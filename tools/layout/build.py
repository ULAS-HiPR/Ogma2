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

STAGES = ('setup', 'parts', 'place')


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
    r = spec.HOLE_PART_KEEPOUT_D / 2
    for side, hx in (('left', 4.0), ('right', 76.0)):
        items = []                                         # (top, bottom, ref, nearest x to the hole centre)
        for ref, (x, y, a) in fixed.items():
            c = pl.geo[ref][a][0]
            if not 12 < y + (c[1] + c[3]) / 2 < spec.H - 12:
                continue                                   # the end zones keep their parts where they are
            if (side == 'left' and x + c[0] < 12) or (side == 'right' and x + c[2] > spec.W - 12):
                items.append((y + c[1], y + c[3], ref, min(max(hx, x + c[0]), x + c[2])))
        if side == 'left':
            for ref, (x0, y0, x1, y1) in spec.RESERVED.items():
                items.append((y0, y1, '@' + ref, min(max(hx, x0), x1)))
        cur = 0.0
        for top, bot, ref, nx in sorted(items):
            dx = abs(nx - hx)
            half = math.sqrt(r * r - dx * dx) if dx < r else None   # the keep-out circle's half-height at this part
            holes = [] if half is None else sorted((y - half - gap, y + half + gap) for x, y in spec.HOLES if x == hx)
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


def labelled(ref, fp):
    """Refs that go on the silkscreen (D-22Nov.9): test points, connectors, ICs, LEDs."""
    return ref.startswith(('TP', 'J', 'U')) or (ref.startswith('D') and 'LED' in fp.GetFPIDAsString())


def build(board, upto, length=None, out_dir=None):
    spec = load_spec(board)
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
    bd = B.Board(str(pcb), spec.ORIGIN, thickness=spec.THICKNESS)
    bd.outline(spec.W, spec.H)
    holes = []
    for i, (x, y) in enumerate(spec.HOLES, 1):
        holes.append(bd.board_only(str(lib), spec.HOLE_FP, f'H{i}', x, y, value='M3'))
        # under the washer: no track or via; the GND ring and the planes' pours are allowed (D-22Nov.11)
        bd.rule_area(f'HOLE{i}_WASHER', B.circle(x, y, spec.HOLE_TRACK_KEEPOUT_D),
                     [B.K.F_Cu, B.K.In1_Cu, B.K.In2_Cu, B.K.B_Cu], tracks=True, vias=True, pads=False, pours=False)
    for i, (x, y) in enumerate(spec.FIDUCIALS, 1):
        bd.board_only(str(lib), spec.FIDUCIAL_FP, f'FID{i}', x, y, value='Fiducial')
    report['stages'].append('setup')

    comps, nets = netlist.load(str(hw / 'output' / 'full-netlist.xml'))
    fps, missing = {}, []
    if STAGES.index(upto) >= 1:
        bd.nets(nets)
        for h in holes:                                  # the exposed ring is GND (D-22Nov.11)
            for pad in h.Pads():
                pad.SetNet(bd.netinfo[spec.HOLE_NET])
        fps, missing = bd.parts(comps, nets, str(lib))
        bd.silk_policy(fps, labelled)
        report['stages'].append('parts')
        report['parts'] = len(fps)
        report['missing_footprint'] = missing

    if STAGES.index(upto) >= 2:
        nets_of = {}
        for n, nodes in nets.items():
            for r, _ in nodes:
                nets_of.setdefault(r, set()).add(n)
        pl = P.Placer(fps, nets, comps, (spec.W, spec.H))
        pl.circles = [(x, y, spec.HOLE_PART_KEEPOUT_D / 2) for x, y in spec.HOLES]
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
            own = pl.owner(ref)
            if own:
                for ic, _ in own[1]:
                    pl.exempt.add(frozenset((ref, ic)))
        pl.weights = [(re.compile(rx), w) for rx, w in spec.NET_WEIGHTS]
        todo = [r for r in fps if r not in pl.placed]
        first = [r for r in spec.PRIORITY if r in todo]
        edge = sorted(r for r in todo if r in getattr(spec, 'REF_REGIONS', {}) and r not in first)  # GND loops claim their edge spots
        probes = sorted(r for r in todo if r.startswith('TP') and r not in first + edge)   # last: they fill what's left
        rest = pl.order([r for r in todo if r not in first + edge + probes])
        unplaced, noregion = [], []
        def put(ref):
            reg, key = region_of(ref, comps, nets_of, spec)
            if reg is None:
                noregion.append(ref)
                reg = (1, 1, spec.W - 1, spec.H - 1)
            if not pl.place_grow(ref, reg):
                unplaced.append(ref)
        for ref in first + edge + rest:
            put(ref)
        # test points last, fore to aft by the circuit each probes: the order doesn't depend on their refs,
        # so renumbering them can't move them
        def probe_key(ref):
            tg = pl.probe_target(ref)
            net = next(iter(pl.pin_nets.get(ref, {}).values()), '')
            return (round(tg[0][1][1], 3), round(tg[0][1][0], 3), net) if tg else (1e9, 1e9, net)
        for ref in sorted(probes, key=probe_key):
            put(ref)
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
        moved, stuck = SK.silk_pass(bd.b, spec.ORIGIN, (spec.W, spec.H))
        report['silk_refs_moved'] = {r: list(d) for r, d in sorted(moved.items())}
        report['silk_refs_stuck'] = stuck
        if getattr(spec, 'ART', None):
            legend = sorted(((r, next(iter(nets_of.get(r, {'?'})))) for r in fps if r.startswith('TP')),
                            key=lambda rn: int(rn[0][2:]))
            art = dict(spec.ART, logo=str(hw / spec.ART['logo']), title_font=str(hw / spec.ART['title_font']))
            report['art'] = A.board_art(bd.b, spec.ORIGIN, (spec.W, spec.H), legend,
                                        reserved=list(spec.RESERVED.values()), **art)
        exc, bad = pl.spacing_report()
        per_band = {}
        for name, (y0, y1) in spec.BANDS.items():
            area = sum((pl.crt[r][2] - pl.crt[r][0]) * (pl.crt[r][3] - pl.crt[r][1]) for r in pl.placed
                       if y0 <= (pl.crt[r][1] + pl.crt[r][3]) / 2 < y1)
            per_band[name] = round(area / (spec.W * (y1 - y0)), 3)
        crit = {k: [n for c, n in spec.PATTERNS if c == k] for k in ('RF50', 'FIRE', 'USB_DIFF', 'SRC_6A', 'PYRO_RAIL')}
        report.update(
            placed=len(pl.placed), unplaced=unplaced, no_region=noregion,
            spills=[{'ref': r, 'grown_mm': g} for r, g in pl.spills],
            hpwl_mm=round(pl.hpwl(), 1),
            hpwl_by_class_mm={k: round(pl.hpwl(set(v)), 1) for k, v in crit.items()},
            density_by_band=per_band,
            jlc_spacing_violations=[{'a': a, 'b': b, 'gap': g, 'needs': n} for a, b, g, n in bad],
            jlc_spacing_exceptions=[{'a': a, 'b': b, 'gap': g, 'needs': n} for a, b, g, n in exc],
            positions={r: [round(x, 3), round(y, 3), a] for r, (x, y, a) in sorted(pl.placed.items())})
        report['stages'].append('place')

    bd.save(str(pcb))
    if not out_dir:
        post.project_rules(hw / f'{spec.NAME}.kicad_pro', spec.NETCLASSES, spec.PATTERNS, spec.RULES)
        post.dru(hw / f'{spec.NAME}.kicad_dru', spec.DRU)
    report['uuids'] = post.finish(pcb, spec.STACKUP, f'{board}')
    report['seconds'] = round(time.time() - t0, 1)
    (out / 'build.json').write_text(json.dumps(report, indent=1) + '\n')
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('board')
    ap.add_argument('--to', choices=STAGES, default='place')
    ap.add_argument('--length', type=float, help='board length in mm (default: the spec\'s); see stretch()')
    ap.add_argument('--out', help='write the board and report here instead of the repository (trials)')
    a = ap.parse_args()
    r = build(a.board, a.to, a.length, a.out)
    keep = {k: v for k, v in r.items() if k != 'positions'}
    for k in ('jlc_spacing_exceptions',):
        if k in keep:
            keep[k] = len(keep[k])
    print(json.dumps(keep, indent=1))
