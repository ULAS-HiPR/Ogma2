"""Build a board from its netlist and spec, from nothing (layout plan section 5).

    python3 tools/layout/build.py croi2 --to place

Runs inside the KiCad 9.0.8 chroot with the repository at /work (tools/layout/phase1/README.md).
Stages: setup (outline, holes, fiducials, rules, stackup), parts (every footprint with its nets),
place (fixed parts, anchors, regions). Writes hardware/<board>/<NAME>.kicad_pcb and a JSON report
in hardware/<board>/output/layout/. Same inputs give the same bytes."""
import argparse
import importlib.util
import json
import math
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1].parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import netlist, post                     # noqa: E402
from engine import board as B                        # noqa: E402
from engine import place as P                        # noqa: E402
from engine import silk as SK                        # noqa: E402
from engine import art as A                          # noqa: E402

STAGES = ('setup', 'parts', 'place', 'copper')          # copper: stage C's scripted copper (engine/copper.py)
FIDUCIAL_R = 1.25      # Fiducial_1mm_Mask2mm's courtyard radius: no other courtyard inside


def load_spec(board):
    p = ROOT / 'hardware' / board / 'layout' / 'spec.py'
    s = importlib.util.spec_from_file_location('spec', p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def sheet_key(path):
    parts = [p for p in path.split('/') if p]
    return parts[0] if parts else '/'


def region_of(ref, comps, nets_of, spec):
    if ref in getattr(spec, 'REF_REGIONS', {}):
        return spec.REF_REGIONS[ref], ref
    s = sheet_key(comps[ref].sheet)
    if s == '05-can':
        bus2 = any('CAN2' in n or n.endswith('J502') for n in nets_of.get(ref, ())) or ref == 'J502'
        return spec.REGIONS['CAN2' if bus2 else 'CAN1'], ('CAN2' if bus2 else 'CAN1')
    return spec.REGIONS.get(s), s


def fixed_xy(pl, ref, f, spec):
    """Origin of an edge part so its body sits `inset` from its edge, centred at `at`."""
    if 'xy' in f:
        return f['xy']
    if 'datum' in f:
        return f['datum']
    crt, env, _ = pl.geo[ref][f['rot']]
    cx = lambda lo, hi: (lo + hi) / 2
    if f['edge'] == 'fwd':
        return f['at'] - cx(env[0], env[2]), f['inset'] - env[1]
    if f['edge'] == 'aft':
        return f['at'] - cx(env[0], env[2]), spec.H - f['inset'] - env[3]
    if f['edge'] == 'left':
        return f['inset'] - env[0], f['at'] - cx(env[1], env[3])
    if f['edge'] == 'right':
        return spec.W - f['inset'] - env[2], f['at'] - cx(env[1], env[3])
    raise ValueError(f)


def stretch(spec, L):
    """Spec coordinates for a board L mm long. y maps piecewise-linearly: 12 mm at each end kept as is, and
    each band's span in proportion to the courtyard area it holds (spec.BAND_AREA, measured on the 230 mm
    board). The four hole rows map too, so they stay between the edge parts (rows end up closer than
    D-21Nov.23's 73 mm). Sizes of fixed parts and of J101's reserved block don't change."""
    H0 = spec.H
    if abs(L - H0) < 1e-9:
        return spec
    old = [0.0, 12.0, 45.0, 100.0, 151.0, H0 - 12.0, H0]
    area = getattr(spec, 'BAND_AREA', None) or [b - a for a, b in zip(old[1:5], old[2:6])]
    inner = L - 24.0
    new = [0.0, 12.0]
    for a in area:
        new.append(new[-1] + inner * a / sum(area))
    new.append(L)

    def m(y):
        for a0, a1, b0, b1 in zip(old, old[1:], new, new[1:]):
            if y <= a1:
                return round(b0 + (y - a0) * (b1 - b0) / (a1 - a0), 3)
        return round(y - H0 + L, 3)

    spec.H = L
    spec.HOLES = [(x, m(y)) for x, y in spec.HOLES]      # the rows keep their places between the edge parts
    spec.FIDUCIALS = [(x, m(y)) for x, y in spec.FIDUCIALS]
    for f in spec.FIXED.values():
        for k in ('xy', 'datum'):
            if k in f:
                f[k] = (f[k][0], m(f[k][1]))
        if f.get('edge') in ('left', 'right'):
            f['at'] = m(f['at'])
    spec.RESERVED = {r: (x0, m(y0), x1, m(y0) + (y1 - y0)) for r, (x0, y0, x1, y1) in spec.RESERVED.items()}
    spec.ANCHORS = {r: (x, m(y), a) for r, (x, y, a) in spec.ANCHORS.items()}
    clamp = lambda y: min(max(y, 1.0), L - 1.0)
    spec.REGIONS = {k: (x0, clamp(m(y0)), x1, clamp(m(y1))) for k, (x0, y0, x1, y1) in spec.REGIONS.items()}
    spec.REF_REGIONS = {k: (x0, clamp(m(y0)), x1, clamp(m(y1))) for k, (x0, y0, x1, y1) in getattr(spec, 'REF_REGIONS', {}).items()}
    spec.BANDS = {k: (m(a), m(b)) for k, (a, b) in spec.BANDS.items()}
    return spec


def pack_edges(pl, fixed, spec, gap=1.0):
    """On a stretched board, slide the left- and right-edge parts (and J101's reserved block) along their
    edge, fore to aft in their mapped order, to the first spot at or aft of their mapped place that clears
    the hole keep-outs and the part before. Edits `fixed` and spec.RESERVED; returns the moves (mm)."""
    moves = {}
    keep = [(x, y, spec.HOLE_PART_KEEPOUT_D / 2) for x, y in spec.HOLES] + [(x, y, FIDUCIAL_R) for x, y in spec.FIDUCIALS]
    for side in ('left', 'right'):
        items = []                                         # (top, bottom, ref, x extent)
        for ref, (x, y, a) in fixed.items():
            c = pl.geo[ref][a][0]
            if not 12 < y + (c[1] + c[3]) / 2 < spec.H - 12:
                continue                                   # the end zones keep their parts where they are
            if (side == 'left' and x + c[0] < 12) or (side == 'right' and x + c[2] > spec.W - 12):
                items.append((y + c[1], y + c[3], ref, (x + c[0], x + c[2])))
        if side == 'left':
            for ref, (x0, y0, x1, y1) in spec.RESERVED.items():
                items.append((y0, y1, '@' + ref, (x0, x1)))
        cur = 0.0
        for top, bot, ref, (ex0, ex1) in sorted(items):
            holes = []                                     # each keep-out circle's span in y at this part's x
            for cx, cy, r in keep:
                dx = abs(min(max(cx, ex0), ex1) - cx)
                if dx < r:
                    half = math.sqrt(r * r - dx * dx)
                    holes.append((cy - half - gap, cy + half + gap))
            holes.sort()
            span = bot - top
            y0 = max(top, cur)
            moved = True
            while moved:
                moved = False
                for h0, h1 in holes:
                    if y0 < h1 and y0 + span > h0:
                        y0, moved = h1, True
            if y0 + span > spec.H - 0.5:
                raise RuntimeError(f'{side} edge full: {ref} would end at {y0 + span:.1f} mm on a {spec.H:.0f} mm board')
            dy = y0 - top
            if dy:
                moves[ref] = round(dy, 3)
                if ref.startswith('@'):
                    x0, a0, x1, a1 = spec.RESERVED[ref[1:]]
                    spec.RESERVED[ref[1:]] = (x0, a0 + dy, x1, a1 + dy)
                else:
                    fixed[ref][1] += dy
            cur = y0 + span + gap
    return moves


def silk_names(spec):
    """Function names that replace refs on the silk (D-22Nov.19): {ref: (text, local side, local text angle, gap)}. A
    fixed part's name goes on its inboard side and reads along its edge (side edges) or across the board (fore and aft
    edges); any other part's goes above it, as a ref would. The gap from the courtyard is 0.25 mm, or
    spec.SILK_NAME_GAP's where parts must sit between (D-22Nov.28)."""
    out = {}
    gaps = getattr(spec, 'SILK_NAME_GAP', {})
    for ref, text in getattr(spec, 'SILK_NAMES', {}).items():
        gap = gaps.get(ref, 0.25)
        f = spec.FIXED.get(ref)
        if f is None:
            out[ref] = (text, (0, -1), 0, gap)
            continue
        edge = f.get('edge')
        if edge is None:                                 # xy or datum: the nearest edge
            x, y = f.get('xy') or f.get('datum')
            edge = min((x, 'left'), (spec.W - x, 'right'), (y, 'fwd'), (spec.H - y, 'aft'))[1]
        bx, by = {'left': (1, 0), 'right': (-1, 0), 'fwd': (0, 1), 'aft': (0, -1)}[edge]
        r = math.radians(f['rot'])
        side = (round(bx * math.cos(r) - by * math.sin(r)), round(bx * math.sin(r) + by * math.cos(r)))
        out[ref] = (text, side, ((90 if edge in ('left', 'right') else 0) - f['rot']) % 360, gap)
    return out


def clear_legend(pl, bd, spec, legend, art):
    """The back's test point legend needs a strip clear of exposed copper about 68 mm long on the left of the back
    (the right of the top). A test point loop whose pins block it moves across, in x, to the nearest place clear
    of the strip (Seán, 22 Nov: "move 4 loops, keep layout"); only if there's none does it also move up to 5 mm
    fore or aft. Re-derives D-22Nov.12's PROBE_MOVES at any length. Returns the moves and anything still in the way."""
    moves, block = {}, []
    # x only: the right edge strip (pins at u <= 5.5 on the back, clear of the column's left edge) or left of it
    xs = [spec.W - 2.0 - 0.25 * i for i in range(15)] + [spec.W - 34.0 - 0.25 * i for i in range(int((spec.W - 36.0) / 0.25))]
    dys = [0.0] + [s * d for d in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0) for s in (1, -1)]   # then a little fore or aft
    for _ in range(4):
        block = A.legend_blockers(bd.b, spec.ORIGIN, (spec.W, spec.H), legend, art['logo'], art['place'])
        todo = [r for r in block if r.startswith('TP') and r not in moves]
        if not todo:
            break
        for ref in todo:
            x, y, a = pl.placed[ref]
            to = next(((nx, y + dy) for dy in dys for nx in sorted(xs, key=lambda c: abs(c - x))
                       if pl.move(ref, round(nx, 3), round(y + dy, 3))), None)
            moves[ref] = {'from': [round(x, 3), round(y, 3)], 'to': None if to is None else [round(to[0], 3), round(to[1], 3)]}
        pl.apply(bd)
    return moves, block


def labelled(ref, fp):
    """Refs that go on the silkscreen (D-22Nov.9): test points, connectors, ICs, LEDs."""
    return ref.startswith(('TP', 'J', 'U')) or (ref.startswith('D') and 'LED' in fp.GetFPIDAsString())


def near_plan(spec, comps, nets):
    """The parts under a distance rule (spec.NEAR, stage B2 step 6), each with what it is pulled to: placed as soon as
    what they're measured from is down, before the general parts."""
    pins_of = {}
    for n, nodes in nets.items():
        for r, p in nodes:
            pins_of.setdefault(r, {})[p] = n
    short = lambda n: n.rsplit('/', 1)[-1]
    is_cap = lambda r: r.startswith('C') and r[1:].isdigit()
    full = lambda net: next(n for n in nets if short(n) == net)
    plan = {}
    for row in getattr(spec, 'NEAR', []):
        rule = row['rule']
        if rule == 'supply_caps':                      # the IC's own decoupling: placed first, pulled as usual
            ic = row['ic']
            ic_nets = {n for n in pins_of[ic].values() if short(n) != 'GND'}
            for r in sorted(pins_of):
                if (is_cap(r) and comps[r].sheet == comps[ic].sheet and row['value'] in comps[r].value
                        and set(pins_of[r].values()) & ic_nets):
                    plan.setdefault(r, dict(anchor=ic))
        elif rule == 'net_caps':
            ic = row['ic']
            for net in row['nets']:
                caps = [r for r, _ in nets[full(net)] if is_cap(r)]
                for r in [c for c in caps if comps[c].sheet == comps[ic].sheet] or caps:
                    cp = next(p for p, n in pins_of[r].items() if n == full(net))
                    plan[r] = dict(anchor=ic, pulls=[(cp, ic, ip) for x, ip in nets[full(net)] if x == ic])
        elif rule == 'part_to_pins':
            part, ic = row['part'], row['ic']
            plan[part] = dict(anchor=ic, pulls=[(pp, ic, ip) for pp, n in pins_of[part].items() if short(n) != 'GND'
                                                for x, ip in nets[n] if x == ic])
        elif rule == 'on_line':
            n = full(row['net'])
            pp = next(p for p, x in pins_of[row['part']].items() if x == n)
            a = next((r, p) for r, p in nets[n] if r == row['from'])
            z = next((r, p) for r, p in nets[n] if r == row['to'])
            plan[row['part']] = dict(anchor=row['from'], also=row['to'], seg=(pp, a, z))
    return plan


def build(board, upto, length=None, out_dir=None, sets=(), netlist_path=None, replace=False):
    spec = load_spec(board)
    for s in sets:                                    # trials only (--set): a statement run in the spec's namespace
        exec(s, vars(spec))
    length = length or getattr(spec, 'LENGTH', None)
    if length:
        stretch(spec, length)
    hw = ROOT / 'hardware' / board
    out = Path(out_dir) if out_dir else hw / 'output' / 'layout'
    out.mkdir(parents=True, exist_ok=True)
    pcb = (out if out_dir else hw) / f'{spec.NAME}.kicad_pcb'
    lib = hw / 'libraries'
    report = {'board': board, 'length_mm': spec.H, 'stages': []}
    t0 = time.time()

    # stage 0: setup
    bd = B.Board(str(pcb), spec.ORIGIN, copper=getattr(spec, 'COPPER_LAYERS', 4), thickness=spec.THICKNESS)
    bd.outline(spec.W, spec.H)
    holes = []
    for i, (x, y) in enumerate(spec.HOLES, 1):
        holes.append(bd.board_only(str(lib), spec.HOLE_FP, f'H{i}', x, y, value='M3'))
        # under the washer: no track or via; the GND ring and the planes' pours are allowed (D-22Nov.11)
        bd.rule_area(f'HOLE{i}_WASHER', B.circle(x, y, spec.HOLE_TRACK_KEEPOUT_D),
                     list(bd.b.GetEnabledLayers().CuStack()), tracks=True, vias=True, pads=False, pours=False)
    for i, (x, y) in enumerate(spec.FIDUCIALS, 1):
        bd.board_only(str(lib), spec.FIDUCIAL_FP, f'FID{i}', x, y, value='Fiducial')
    report['stages'].append('setup')

    comps, nets = netlist.load(str(netlist_path or hw / 'output' / 'full-netlist.xml'))   # --netlist: trials only
    fps, missing = {}, []
    if STAGES.index(upto) >= 1:
        bd.nets(nets)
        for h in holes:                                  # the exposed ring is GND (D-22Nov.11)
            for pad in h.Pads():
                pad.SetNet(bd.netinfo[spec.HOLE_NET])
        fps, missing = bd.parts(comps, nets, str(lib))
        bd.silk_policy(fps, labelled, silk_names(spec))
        marks = {ref: bd.board_only(str(lib), m, ref, 0, 0) for ref, m in getattr(spec, 'MARKS', {}).items()}
        if getattr(spec, 'ART', None):                # the parts list says the board's real length
            spec.ART = dict(spec.ART, specs=[s.format(W=spec.W, H=spec.H) for s in spec.ART['specs']])
        report['stages'].append('parts')
        report['parts'] = len(fps)
        report['missing_footprint'] = missing

    if STAGES.index(upto) >= 2:
        nets_of = {}
        for n, nodes in nets.items():
            for r, _ in nodes:
                nets_of.setdefault(r, set()).add(n)
        pl = P.Placer({**fps, **marks}, nets, comps, (spec.W, spec.H),     # a name set off its part: a box of its own
                      apart={r: spec.SILK_NAMES[r] for r in getattr(spec, 'SILK_NAME_GAP', {})})
        pl.circles = [(x, y, spec.HOLE_PART_KEEPOUT_D / 2) for x, y in spec.HOLES] + [(x, y, FIDUCIAL_R) for x, y in spec.FIDUCIALS]
        fixed = {ref: [*fixed_xy(pl, ref, f, spec), f['rot']] for ref, f in spec.FIXED.items()}
        if length:
            report['edge_packing'] = pack_edges(pl, fixed, spec)
        for ref, (x, y, a) in fixed.items():
            pl.fix(ref, round(x, 3), round(y, 3), a)
        for ref, box in spec.RESERVED.items():
            pl.rects.append(box)
            bd.note_rect(box, f'{ref} reserved')
        for ref, (x, y, a) in spec.ANCHORS.items():
            pl.fix(ref, x, y, a)
        for ref, fp in fps.items():
            if fp.GetFPIDAsString().startswith(spec.BIG_MLCC):
                pl.rotset[ref] = (0, 180)
            if ref.startswith('TP'):
                pl.rotset[ref] = (0,)                  # TP number reads upright (D-22Nov.9)
        for ref in marks:
            pl.rotset[ref] = (0,)                      # the axes' X points to the nose; S/N reads upright
            own = pl.owner(ref)
            if own:
                for ic, _ in own[1]:
                    pl.exempt.add(frozenset((ref, ic)))
        pl.weights = [(re.compile(rx), w) for rx, w in spec.NET_WEIGHTS]
        if getattr(spec, 'ART', None):                # the back's blocks: no loop pin under them (D-22Nov.12)
            rows_tp = sorted(((r, next(iter(nets_of.get(r, {'?'})))) for r in fps if r.startswith('TP')), key=lambda rn: int(rn[0][2:]))
            rows = A.art_skeleton(bd.b, spec.ORIGIN, (spec.W, spec.H), rows_tp, **dict(
                spec.ART, logo=str(hw / spec.ART['logo']), title_font=str(hw / spec.ART['title_font'])))
            for r, fp in fps.items():
                if r.startswith('TP') and any(pd.GetAttribute() == B.K.PAD_ATTRIB_PTH for pd in fp.Pads()):
                    pl.pad_keepout[r] = rows
        # stage C step 0 (D-22Nov.30): the placement is data. The placer runs only when there's no placement file or
        # --replace asks for it, and then writes the file; otherwise every part goes exactly where the file says
        pfile = (hw / 'layout' / spec.PLACEMENT) if getattr(spec, 'PLACEMENT', None) else None
        frozen = None
        if pfile is not None and pfile.exists() and not replace:
            frozen = {r: tuple(v) for r, v in json.loads(pfile.read_text())['parts'].items()}
        if frozen is None:
            todo = [r for r in fps if r not in pl.placed]
            plan = near_plan(spec, comps, nets)
            pl.near = plan
            pl.step = {r: row['step'] for row in getattr(spec, 'NEAR', []) if 'step' in row for r in [row.get('part')] if r}
            first = [r for r in spec.PRIORITY if r in todo]
            near_wait = [r for r in plan if r in todo and r not in first]      # in the rules' order
            edge = sorted(r for r in todo if r in getattr(spec, 'REF_REGIONS', {}) and r not in first)  # GND loops claim their edge spots
            probes = sorted(r for r in todo if r.startswith('TP') and r not in first + edge)   # last: they fill what's left
            rest = pl.order([r for r in todo if r not in first + edge + probes + near_wait])
            unplaced, noregion = [], []
            def put(ref, rmax=40.0):
                reg, key = region_of(ref, comps, nets_of, spec)
                if reg is None:
                    noregion.append(ref)
                    reg = (1, 1, spec.W - 1, spec.H - 1)
                if not pl.place_grow(ref, reg, rmax=rmax):
                    unplaced.append(ref)
                    return False
                return True
            # the test points on sensitive nodes go in with their circuit, as soon as its parts are down, before the
            # general parts fill the space round it (stage B2 step 5); the rest come last
            net1 = lambda r: next(iter(nets_of.get(r, {''})))
            with_circuit = sorted(r for r in probes if net1(r) in getattr(spec, 'PROBES_WITH_CIRCUIT', ()))
            probes = [r for r in probes if r not in with_circuit]
            pending = list(with_circuit)

            def flush_near():                              # each rule's parts as soon as what they're measured from is down
                for r in list(near_wait):
                    d = plan[r]
                    if d['anchor'] in pl.placed and d.get('also', d['anchor']) in pl.placed:
                        put(r)
                        near_wait.remove(r)
            flush_near()
            for ref in first + edge + rest:
                put(ref)
                flush_near()
                for tp in list(pending):
                    if all(r in pl.placed for r, _ in nets[net1(tp)] if not r.startswith('TP')):
                        pl.probe_look = 20.0               # these search further along their route: 10 mm is their limit
                        put(tp)
                        pl.probe_look = 10.0
                        pending.remove(tp)
            probes = pending + probes
            n_unplaced = len(unplaced)
            for ref in sorted(marks):                      # the axes and the serial box (D-22Nov.19), before the probes
                put(ref)
            marks_unplaced = unplaced[n_unplaced:]
            del unplaced[n_unplaced:]
            # test points last, fore to aft by the circuit each probes: the order doesn't depend on their refs,
            # so renumbering them can't move them
            def probe_key(ref):
                tg = pl.probe_target(ref)
                net = next(iter(pl.pin_nets.get(ref, {}).values()), '')
                return (round(tg[0][1][1], 3), round(tg[0][1][0], 3), net) if tg else (1e9, 1e9, net)
            n_before = len(unplaced)
            for ref in sorted(probes, key=probe_key):
                put(ref)
            # a test point with no room within 40 mm of its circuit: after the others, the nearest spot anywhere on the
            # board (Seán, 22 Nov: no test point is deleted). Reported with its distance, since it's far from what it probes
            far = {}
            for ref in unplaced[n_before:]:
                tg = pl.probe_target(ref)
                unplaced.remove(ref)
                if put(ref, rmax=max(spec.W, spec.H)):
                    x, y, _ = pl.placed[ref]
                    far[ref] = round(math.hypot(x - tg[0][1][0], y - tg[0][1][1]), 1) if tg else None
        else:
            for ref, (x, y, a) in sorted(frozen.items()):
                if ref in pl.placed:                   # fixed parts and anchors: the spec must agree with the file
                    px, py, pa = pl.placed[ref]
                    if abs(px - x) > 1e-6 or abs(py - y) > 1e-6 or pa != a:
                        raise RuntimeError(f'{ref}: the spec puts it at {pl.placed[ref]}, placement.json at {(x, y, a)}')
                    continue
                pl.commit(ref, x, y, a)
            missing = sorted(r for r in {**fps, **marks} if r not in pl.placed)
            extra = sorted(r for r in frozen if r not in fps and r not in marks)
            if missing or extra:
                raise RuntimeError(f'placement.json is out of date (missing {missing[:6]}, extra {extra[:6]}): '
                                   'build with --replace to run the placer')
            unplaced, noregion, marks_unplaced, plan, with_circuit, far = [], [], [], {}, [], {}
        report['probes_far'] = far
        report['probes_with_circuit'] = with_circuit
        report['near_parts'] = sorted(plan, key=lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0)))
        # loops whose pins would land in the back's test point legend: moved after everything else is placed,
        # so no other part sees them, and in x only, so their fore-to-aft numbers hold (Sean, 22 Nov)
        moves = {}
        for ref, mv in getattr(spec, 'PROBE_MOVES', {}).items():
            x, y, a = pl.placed[ref]
            nx = mv['x'] if 'x' in mv else x + mv.get('dx', 0.0)
            moves[ref] = {'from': [round(x, 3), round(y, 3)], 'to': [round(nx, 3), round(y, 3)],
                          'done': pl.move(ref, round(nx, 3), y)}
        report['probe_moves'] = moves
        pl.apply(bd)
        legend, art = None, None
        if getattr(spec, 'ART', None):
            legend = sorted(((r, next(iter(nets_of.get(r, {'?'})))) for r in fps if r.startswith('TP')),
                            key=lambda rn: int(rn[0][2:]))
            art = dict(spec.ART, logo=str(hw / spec.ART['logo']), title_font=str(hw / spec.ART['title_font']))
            report['legend_moves'], report['legend_blockers'] = clear_legend(pl, bd, spec, legend, art)
        moved, stuck = SK.silk_pass(bd.b, spec.ORIGIN, (spec.W, spec.H))
        report['silk_refs_moved'] = {r: list(d) for r, d in sorted(moved.items())}
        report['silk_refs_stuck'] = stuck
        if art:
            try:
                report['art'] = A.board_art(bd.b, spec.ORIGIN, (spec.W, spec.H), legend,
                                            reserved=list(spec.RESERVED.values()), **art)
            except RuntimeError as e:                  # the board is still saved, without its back art
                report['art_error'] = str(e)
        exc, bad = pl.spacing_report()
        per_band = {}
        for name, (y0, y1) in spec.BANDS.items():
            area = sum((pl.crt[r][2] - pl.crt[r][0]) * (pl.crt[r][3] - pl.crt[r][1]) for r in pl.placed
                       if y0 <= (pl.crt[r][1] + pl.crt[r][3]) / 2 < y1)
            area += sum((b[2] - b[0]) * (b[3] - b[1]) for b in pl.apart_rect.values()   # names set off their parts
                        if y0 <= (b[1] + b[3]) / 2 < y1)
            per_band[name] = round(area / (spec.W * (y1 - y0)), 3)
        crit = {k: [n for c, n in spec.PATTERNS if c == k] for k in ('RF50', 'FIRE', 'USB_DIFF', 'SRC_6A', 'PYRO_RAIL')}
        report.update(
            placed=len(pl.placed), unplaced=unplaced, marks_unplaced=marks_unplaced, no_region=noregion,
            spills=[{'ref': r, 'grown_mm': g} for r, g in pl.spills],
            hpwl_mm=round(pl.hpwl(), 1),
            hpwl_by_class_mm={k: round(pl.hpwl(set(v)), 1) for k, v in crit.items()},
            density_by_band=per_band,
            jlc_spacing_violations=[{'a': a, 'b': b, 'gap': g, 'needs': n} for a, b, g, n in bad],
            jlc_spacing_exceptions=[{'a': a, 'b': b, 'gap': g, 'needs': n} for a, b, g, n in exc],
            positions={r: [round(x, 3), round(y, 3), a] for r, (x, y, a) in sorted(pl.placed.items())})
        report['stages'].append('place')
        report['placement'] = 'placer' if frozen is None else f'file {pfile.name}'
        if frozen is None and pfile is not None:      # full precision, so a build from the file gives the same bytes
            dst = (out / pfile.name) if out_dir else pfile
            dst.write_text(json.dumps({'note': 'Written by tools/layout/build.py --replace (D-22Nov.30); x, y in mm on the '
                                               'board, rotation in degrees', 'length_mm': spec.H,
                                       'parts': {r: list(v) for r, v in sorted(pl.placed.items())}}, indent=0) + '\n')

    if STAGES.index(upto) >= 3:                       # stage C (S4): the scripted copper, after the placement
        from engine import copper as CU
        report['copper'] = {'escape_areas': CU.escape_areas(bd, spec, fps)}
        report['stages'].append('copper')

    bd.save(str(pcb))
    if not out_dir:
        post.project_rules(hw / f'{spec.NAME}.kicad_pro', spec.NETCLASSES, spec.PATTERNS, spec.RULES)
        post.dru(hw / f'{spec.NAME}.kicad_dru', spec.DRU)
    report['uuids'] = post.finish(pcb, spec.STACKUP, f'{board}')
    if STAGES.index(upto) >= 2:                       # the stage B2 yardsticks (engine/metrics.py), from the saved board
        from engine import fanout as FO, metrics as M
        bdata = M.BoardData(B.K.LoadBoard(str(pcb)), spec.ORIGIN, (spec.W, spec.H))
        fo = FO.plan(bdata, M.plane_nets(bdata, set(spec.RAILS)), spec)
        m = M.measure(bdata, spec, fo)
        report['metrics'] = m
        lim = getattr(spec, 'PROBE_STUB_MAX', (10.0, 20.0))  # with their circuit / every other (stage B2 step 5)
        report['probe_stub_misses'] = {
            r: v['to_route'] for r, v in sorted(m['tp_stubs'].items(), key=lambda kv: int(kv[0][2:]))
            if v['to_route'] > (lim[0] if v['net'] in getattr(spec, 'PROBES_WITH_CIRCUIT', ()) else lim[1])}
        (out / 'metrics.md').write_text(f'# {spec.NAME} at {spec.H:g} mm: placement yardsticks\n\n'
                                        'Written by tools/layout/build.py from engine/metrics.py. Board mm.\n\n' + M.markdown(m))
    report['seconds'] = round(time.time() - t0, 1)
    (out / 'build.json').write_text(json.dumps(report, indent=1) + '\n')
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('board')
    ap.add_argument('--to', choices=STAGES, default='copper')
    ap.add_argument('--length', type=float, help='board length in mm (default: the spec\'s); see stretch()')
    ap.add_argument('--out', help='write the board and report here instead of the repository (trials)')
    ap.add_argument('--set', action='append', default=[],
                    help="trials: a statement run in the spec's namespace, e.g. \"ANCHORS['U401'] = (40.0, 126.0, 180)\"")
    ap.add_argument('--netlist', help='trials: build from this netlist instead of output/full-netlist.xml')
    ap.add_argument('--replace', action='store_true', help='run the placer and rewrite layout/placement.json (D-22Nov.30)')
    a = ap.parse_args()
    if (a.set or a.netlist) and not a.out:
        ap.error('--set and --netlist are for trials: give --out too')
    r = build(a.board, a.to, a.length, a.out, a.set, a.netlist, a.replace)
    keep = {k: v for k, v in r.items() if k != 'positions'}
    for k in ('jlc_spacing_exceptions',):
        if k in keep:
            keep[k] = len(keep[k])
    print(json.dumps(keep, indent=1))
