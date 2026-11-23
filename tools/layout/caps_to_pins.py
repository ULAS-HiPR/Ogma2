"""Move each MCU's capacitors to their pins (D-23Nov.1), as edits to placement.json (D-22Nov.30).

    python3 tools/layout/caps_to_pins.py croi2 [--refs U201 U401] [--no-room] [--others MM] [--depth N]
        [--plan FILE] [--write [--yes]]

For every `supply_caps` row of spec.NEAR on the named MCUs, tightest distance first, each pin gets its own
capacitor of the row's value on its net, within the row's distance (copper gap, pad edge to pad edge, as the build's
near check measures it). A capacitor already in reach of a pin stays. Each pin left over takes the nearest free
capacitor of its pool (the row's value on the pin's net, drawn on the MCU's sheet in spec.DECOUPLING_SHEETS); one
left over once every pin has one (U401's second VDDA pair: its pin 13 is VDDA and VREF+ in one) goes to the pin with
the fewest, unless it is in reach of one already.

Each capacitor goes to the spot beyond its pin's tip that disturbs least: a free one if there is one, else one whose
occupants can move out of the way, nearest first. Nothing it moves, but the crystals and their load capacitors, may
sit in front of a crystal pin within 2.5 mm of its tip, so the oscillators keep their short lanes on L1; and a
capacitor sits between the lanes either side of its own pin, so the pin reaches it on L1 without crossing one.

What may move, counted from where it stood before the run: the MCU's own capacitors and its crystals with their load
capacitors (D-23Nov.1), up to 4 mm when in the way, a crystal staying within its near rule; the parts in
spec.DECOUPLING_ROOM (D-23Nov.5) up to their allowance, a test point staying beside its net's route
(spec.PROBE_STUB_MAX), unless --no-room; anything else 1 mm at most (the handoff's stop list), or up to --others mm
to draw a plan for Seán. A part keeps its rotation unless it fits nowhere else within 2 mm. Spots are a 0.05 mm
grid, every rotation the placer allows; among equally disturbing spots, the smaller gap to the pin wins, then the
shorter gap from the capacitor's GND pad to one of the MCU's GND pins, then the spot nearer the pin along its row.

Prints every move with its class: `approved` (D-23Nov.1), `room` (D-23Nov.5), `nudge` (1 mm or less) or `needs
Seán` (more than 1 mm, only with --others). --plan writes the moves as JSON. --write puts them in placement.json; a
plan with moves that need Seán is written only with --yes, once he has said so.
"""
import argparse
import json
import math
import re
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pcbnew as K                         # noqa: E402
from shapely.affinity import translate     # noqa: E402
from shapely.geometry import Polygon       # noqa: E402

import build                               # noqa: E402
from engine import netlist, place as P     # noqa: E402

STEP = 0.05
REACH = 3.5                                # how far beyond a pin's tip the search goes, mm
ALONG = 3.0                                # and along its row, either way
APPROVED_MAX = 4.0                         # how far an approved part may go to make room, mm
TURN_MAX = 2.0                             # and turned, only this far
NUDGE = 1.0                                # anything else, without Seán (the handoff's stop list)
GROUPS = 25                                # sets of occupants tried per capacitor
LANE = 2.5                                 # no part this run moves sits in front of a crystal pin, this far out
DEPTH = 2                                  # a part moved to make room may itself move one other set of parts
MOVABLE = re.compile(r'(C|R|L|D|FB|TP|Y)\d+$')
NOTHING = (0, 0.0, 0, 0.0, 0, 0.0)


def pad_poly(pad, layer=K.F_Cu):
    ps = K.SHAPE_POLY_SET()
    pad.TransformShapeToPolygon(ps, layer, 0, K.FromMM(0.005), K.ERROR_INSIDE)
    o = ps.Outline(0)
    return Polygon([(K.ToMM(o.CPoint(i).x), K.ToMM(o.CPoint(i).y)) for i in range(o.PointCount())])


def local_pads(fp, rot):
    """{pin: polygon} of a footprint's front pads with the part at (0, 0) and rotation rot, board mm."""
    pos, ang = fp.GetPosition(), fp.GetOrientationDegrees()
    fp.SetPosition(K.VECTOR2I(0, 0))
    fp.SetOrientationDegrees(rot)
    out = {p.GetNumber(): pad_poly(p) for p in fp.Pads() if p.IsOnLayer(K.F_Cu)}
    fp.SetOrientationDegrees(ang)
    fp.SetPosition(pos)
    return out


def offsets(rmax):
    """Grid offsets within rmax, nearest first: 0.05 mm steps to 1 mm, 0.1 mm beyond."""
    out = set()
    for step, lim in ((STEP, NUDGE), (0.1, rmax)):
        n = int(round(lim / step))
        out |= {(round(i * step, 3), round(j * step, 3)) for i in range(-n, n + 1) for j in range(-n, n + 1) if i or j}
    out = [(dx, dy, math.hypot(dx, dy)) for dx, dy in out] + [(0.0, 0.0, 0.0)]
    return sorted((o for o in out if o[2] <= rmax + 1e-9), key=lambda o: (round(o[2], 4), o[1], o[0]))


class Run:
    def __init__(self, a):
        captured = {}
        orig_apply = P.Placer.apply

        def grab(self, board):
            captured['pl'] = self
            return orig_apply(self, board)
        P.Placer.apply = grab
        with tempfile.TemporaryDirectory() as tmp:
            build.build(a.board, 'place', out_dir=tmp, sets=getattr(a, 'sets', ()))
        P.Placer.apply = orig_apply
        self.pl = pl = captured['pl']
        self.spec = spec = build.load_spec(a.board)
        for st in getattr(a, 'sets', ()):                              # trials: as the build ran them
            exec(st, vars(spec))
        build.stretch(spec, spec.LENGTH) if getattr(spec, 'LENGTH', None) else None
        self.hw = build.ROOT / 'hardware' / a.board
        self.comps, nets = netlist.load(str(self.hw / 'output' / 'full-netlist.xml'))
        self.ox, self.oy = spec.ORIGIN
        self.pin_net = {(r, p): n.rsplit('/', 1)[-1] for n, nodes in nets.items() for r, p in nodes}
        self.orig = dict(pl.placed)                                    # where everything stood before the run
        self.others = a.others
        far = max([APPROVED_MAX, a.others or 0.0] + list(getattr(spec, 'DECOUPLING_ROOM', {}).values()))
        self.offs = offsets(far + 4.0)
        self.t0 = time.time()
        self.shapes = {}
        self.log = []                                                  # ('lift' | 'place', ref, position)
        fixed = set(spec.FIXED) | set(getattr(spec, 'ANCHORS', {})) | set(getattr(spec, 'REF_REGIONS', {}))
        self.movable = {r for r in pl.placed if MOVABLE.match(r) and r not in fixed}
        self.approved = set()
        self.near_rows = [r for r in getattr(spec, 'NEAR', []) if r['rule'] == 'part_to_pins']
        self.ic_pads = {}
        self.lanes, self.xtal = [], set()                             # set by main()
        self.room = dict(getattr(spec, 'DECOUPLING_ROOM', {}))          # parts Seán let move further (D-23Nov.5)
        self.stub = {}
        self.depth = DEPTH
        self.lane_side = []                    # (ic, outward direction, along-span) of each lane

    # --- geometry
    def net(self, r, p):
        return self.pin_net.get((r, p), '')

    def board_pads(self, ref):
        """{pin: polygon} of a part as the build placed it, board-local mm: for parts this run doesn't move."""
        if ref not in self.ic_pads:
            self.ic_pads[ref] = {p: translate(g, -self.ox, -self.oy) for p, g in
                                 ((pd.GetNumber(), pad_poly(pd)) for pd in self.pl.fps[ref].Pads()
                                  if pd.IsOnLayer(K.F_Cu))}
        return self.ic_pads[ref]

    def pads_at(self, ref, x, y, rot):
        if (ref, rot) not in self.shapes:
            self.shapes[(ref, rot)] = local_pads(self.pl.fps[ref], rot)
        return {p: translate(g, x, y) for p, g in self.shapes[(ref, rot)].items()}

    def conflicts(self, ref, x, y, a):
        """The placed parts in the way of `ref` at (x, y, a), or None if the board itself is (edge, hole, keep-out)."""
        pl = self.pl
        crt, env = pl.boxes_at(ref, x, y, a)
        m = pl.edge_margin
        if crt[0] < m or crt[1] < m or crt[2] > pl.w - m or crt[3] > pl.h - m:
            return None
        for cx, cy, r in pl.circles:
            nx, ny = min(max(cx, crt[0]), crt[2]), min(max(cy, crt[1]), crt[3])
            if (nx - cx) ** 2 + (ny - cy) ** 2 < r * r:
                return None
        if any(P.overlap(crt, k) for k in pl.rects):
            return None
        if ref not in self.xtal and any(P.overlap(crt, k) for k in self.lanes):
            return None
        for b in pl.pad_keepout.get(ref, ()):
            for pts in pl.geo[ref][a][2].values():
                if any(b[0] < x + px < b[2] and b[1] < y + py < b[3] for px, py in pts):
                    return None
        hits = set()
        for o in pl._near(crt):
            if P.overlap(crt, pl.crt[o]):
                hits.add(o)
            elif frozenset((ref, o)) not in pl.exempt and \
                    P.box_gap(env, pl.env[o]) < P.jlc_gap(pl.cls[ref], pl.cls[o]) - 1e-6:
                hits.add(o)
        return hits

    def near_ok(self, ref, x, y, rot):
        """A moved part's own near rules (a crystal within 5 mm of its pins) still hold."""
        rows = [r for r in self.near_rows if r['part'] == ref]
        if not rows:
            return True
        pads = self.pads_at(ref, x, y, rot)
        for row in rows:
            ic = self.board_pads(row['ic'])
            for p, g in pads.items():
                n = self.net(ref, p)
                if not n or n == 'GND':
                    continue
                mine = [h for q, h in ic.items() if self.net(row['ic'], q) == n]
                if mine and min(g.distance(h) for h in mine) > row['mm']:
                    return False
        return True

    # --- moves, undoable
    def _lift(self, ref):
        pl = self.pl
        for c in pl._cells(pl.crt[ref]):
            pl.grid[c].remove(ref)
        if ref in pl.apart_rect:
            pl.rects.remove(pl.apart_rect.pop(ref))
        old = pl.placed.pop(ref)
        del pl.crt[ref], pl.env[ref]
        return old

    def lift(self, ref):
        self.log.append(('lift', ref, self._lift(ref)))

    def place(self, ref, x, y, a):
        self.pl.commit(ref, x, y, a)
        self.log.append(('place', ref, (x, y, a)))

    def rollback(self, mark):
        while len(self.log) > mark:
            op, ref, pos = self.log.pop()
            if op == 'place':
                self._lift(ref)
            else:
                self.pl.commit(ref, *pos)

    def allowance(self, ref):
        if ref in self.approved:
            return APPROVED_MAX
        if ref in self.room:
            return self.room[ref]
        return max(NUDGE, self.others or 0.0)

    def fits(self, ref, x, y, rot):
        """`ref` may stand at (x, y, rot): nothing in its way, its own near rules and probe stub kept."""
        hits = self.conflicts(ref, x, y, rot)
        return hits == set() and self.rules_ok(ref, x, y, rot)

    def rules_ok(self, ref, x, y, rot):
        if not self.near_ok(ref, x, y, rot):
            return False
        if ref in self.stub:                                           # a test point stays beside its net's route
            pin, segs, lim = self.stub[ref]
            px, py = self.pl.geo[ref][rot][2][pin][0]
            q = (x + px, y + py)
            if min(math.hypot(*(lambda c: (q[0] - c[0], q[1] - c[1]))(P._closest(q, a, b))) for a, b in segs) > lim:
                return False
        return True

    def make_room(self, ref, x, y, a, depth, frozen):
        """Put the lifted `ref` at (x, y, a), moving what's in the way. True if done, else nothing changed."""
        hits = self.conflicts(ref, x, y, a)
        if hits is None or any(h in frozen or h not in self.movable for h in hits):
            return False
        if hits and depth >= self.depth:
            return False
        mark = len(self.log)
        for h in sorted(hits):
            self.lift(h)
        self.place(ref, x, y, a)
        area = lambda r: (lambda c: (c[2] - c[0]) * (c[3] - c[1]))(self.pl.geo[r][self.orig[r][2]][0])
        for h in sorted(hits, key=lambda r: (-area(r), r)):
            if not self.relocate(h, depth + 1, frozen | {ref}):
                self.rollback(mark)
                return False
        return True

    def relocate(self, ref, depth, frozen, near=None):
        """Set the lifted `ref` down at the nearest spot within its allowance of where it stood before the run, or
        nearest the point `near` within that allowance."""
        ox, oy, a0 = self.orig[ref]
        x0, y0 = near or (ox, oy)
        maxd = self.allowance(ref)
        reach = maxd + math.hypot(x0 - ox, y0 - oy)
        rots = [a0] + [r for r in self.pl.rotset.get(ref, P.ROTS) if r != a0]
        for rot in rots:                                               # a free spot, same rotation first
            for dx, dy, d in self.offs:
                if d > (reach if rot == a0 else min(reach, TURN_MAX)):
                    break
                x, y = round(x0 + dx, 3), round(y0 + dy, 3)
                if math.hypot(x - ox, y - oy) > (maxd if rot == a0 else min(maxd, TURN_MAX)) + 1e-9:
                    continue
                if self.fits(ref, x, y, rot):
                    self.place(ref, x, y, rot)
                    return True
        if depth >= self.depth:
            return False
        tried = 0
        for dx, dy, d in self.offs:                                    # else one whose occupants move in turn
            if d > reach or tried >= 30:
                break
            x, y = round(x0 + dx, 3), round(y0 + dy, 3)
            if math.hypot(x - ox, y - oy) > maxd + 1e-9:
                continue
            hits = self.conflicts(ref, x, y, a0)
            if not hits or any(h in frozen or h not in self.movable for h in hits) or not self.rules_ok(ref, x, y, a0):
                continue
            tried += 1
            if self.make_room(ref, x, y, a0, depth, frozen):
                return True
        return False

    def cost(self, mark, cap):
        """How much the moves since `mark` disturb: parts needing Seán and their travel, then nudges, then the rest."""
        moved = {ref for op, ref, _ in self.log[mark:] if op == 'place' and ref != cap}
        ask = nudge = appr = 0.0
        n_ask = n_other = 0
        for r in moved:
            x, y, _ = self.pl.placed[r]
            d = math.hypot(x - self.orig[r][0], y - self.orig[r][1])
            if r in self.approved or r in self.room:
                appr += d
            elif d > NUDGE + 1e-9:
                n_ask += 1
                ask += d
            else:
                n_other += 1
                nudge += d
        return (n_ask, round(ask, 2), n_other, round(nudge, 2), len(moved), round(appr, 2))

    # --- one capacitor to one pin
    def to_pin(self, cap, ic, pin, limit, frozen, why, report):
        pl = self.pl
        ic_pads = self.board_pads(ic)
        pg = ic_pads[pin]
        cx, cy, _ = pl.placed[ic]
        px, py = pg.centroid.x, pg.centroid.y
        dx, dy = px - cx, py - cy
        out = (1 if dx > 0 else -1, 0) if abs(dx) > abs(dy) else (0, 1 if dy > 0 else -1)
        along = (out[1], out[0])
        x0, y0, x1, y1 = pg.bounds
        tip = (x1 if out[0] > 0 else x0 if out[0] < 0 else px, y1 if out[1] > 0 else y0 if out[1] < 0 else py)
        net = self.net(ic, pin)
        npin = next(q for q in ('1', '2') if self.net(cap, q) == net)
        gnd_pins = [g for q, g in ic_pads.items() if self.net(ic, q) == 'GND']
        # between the crystal lanes either side of its pin, so the pin reaches it on L1 without crossing one
        p_al = py if along[0] == 0 else px
        spans = [sp for i, o, sp in self.lane_side if i == ic and o == out]
        lo = max((sp[1] for sp in spans if sp[1] <= p_al), default=-1e9)
        hi = min((sp[0] for sp in spans if sp[0] >= p_al), default=1e9)
        start = len(self.log)
        if cap in pl.placed:
            self.lift(cap)
        groups = {}
        n_out, n_al = int(REACH / STEP), int(ALONG / STEP)
        for i in range(0, n_out + 1):
            for j in range(-n_al, n_al + 1):
                x = round(tip[0] + out[0] * i * STEP + along[0] * j * STEP, 3)
                y = round(tip[1] + out[1] * i * STEP + along[1] * j * STEP, 3)
                for rot in pl.rotset.get(cap, P.ROTS):
                    pads = self.pads_at(cap, x, y, rot)
                    g = pads[npin].distance(pg)
                    if g > limit - 0.02:
                        continue
                    crt = pl.boxes_at(cap, x, y, rot)[0]
                    c_lo, c_hi = (crt[1], crt[3]) if along[0] == 0 else (crt[0], crt[2])
                    if c_lo < lo - 1e-6 or c_hi > hi + 1e-6:
                        continue
                    hits = self.conflicts(cap, x, y, rot)
                    if hits is None or any(h in frozen or h == ic or h not in self.movable for h in hits):
                        continue
                    other = next(q for q in pads if q != npin)
                    gg = min((pads[other].distance(h) for h in gnd_pins), default=9.0)
                    score = (round(g, 2), round(gg, 2), round(abs(j * STEP), 2), rot)
                    groups.setdefault(frozenset(hits), []).append((score, x, y, rot))
        order = sorted(groups, key=lambda k: (sum(h not in self.approved for h in k), len(k), min(groups[k])[0]))
        best = None
        for k in order[:GROUPS]:
            for score, x, y, rot in sorted(groups[k])[:2]:
                mark = len(self.log)
                if not self.make_room(cap, x, y, rot, 0, frozen | {ic}):
                    continue
                c = self.cost(mark, cap)
                if best is None or (c, score) < (best[0], best[1]):
                    best = (c, score, x, y, rot)
                self.rollback(mark)
            if best is not None and best[0] == NOTHING:
                break
        if best is None:
            self.rollback(start)
            report.append(f'{ic}.{pin} {net}: no spot for {cap} within {limit} mm ({why})')
            return False
        c, score, x, y, rot = best
        assert self.make_room(cap, x, y, rot, 0, frozen | {ic})
        moved = sorted({ref for op, ref, _ in self.log[start:] if op == 'place' and ref != cap})
        print(f'{time.time() - self.t0:.0f} s: {ic}.{pin} {cap}', file=sys.stderr)
        report.append(f'{ic}.{pin} {net}: {cap} to ({x}, {y}, {rot}), gap {score[0]} mm, GND pad {score[1]} mm from '
                      f'a GND pin ({why})' + (f'; moved for it: {", ".join(moved)}' if moved else ''))
        return True

    def moves(self):
        out = {}
        for r, (x, y, a) in sorted(self.pl.placed.items()):
            if r not in self.orig:
                continue
            o = self.orig[r]
            if (x, y, a) != tuple(o):
                d = math.hypot(x - o[0], y - o[1])
                cls = ('approved' if r in self.approved else 'room' if r in self.room else
                       'nudge' if d <= NUDGE + 1e-9 else 'needs Seán')
                out[r] = {'from': list(o), 'to': [x, y, a], 'mm': round(d, 2), 'class': cls}
        return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('board')
    ap.add_argument('--refs', nargs='+', default=['U201', 'U401'])
    ap.add_argument('--others', type=float, default=None, help='let other parts move up to this far, mm (a plan)')
    ap.add_argument('--plan', help='write the moves here as JSON')
    ap.add_argument('--depth', type=int, default=DEPTH, help='how many sets of parts deep a move may push (2)')
    ap.add_argument('--no-room', action='store_true', help="leave spec.DECOUPLING_ROOM's parts to the 1 mm nudge")
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--yes', action='store_true', help="Seán has said yes to the moves that need him")
    a = ap.parse_args()
    run = Run(a)
    run.depth = a.depth
    if a.no_room:
        run.room = {}
    pl, spec, comps = run.pl, run.spec, run.comps
    sheets = getattr(spec, 'DECOUPLING_SHEETS', {})
    rows = [r for r in getattr(spec, 'NEAR', []) if r['rule'] == 'supply_caps' and r['ic'] in a.refs and 'nets' in r]
    is_cap = lambda r: r.startswith('C') and r[1:].isdigit()

    def pool(ic, net, value):
        return sorted(r for r in pl.placed if is_cap(r) and comps[r].sheet in sheets.get(ic, ())
                      and value in comps[r].value and any(run.net(r, q) == net for q in ('1', '2')))
    # approved to move (D-23Nov.1): each MCU's own capacitors on its supply nets, its crystals and their load caps
    for ic in a.refs:
        nets = {n for row in rows if row['ic'] == ic for n in row['nets']}
        run.approved |= {r for r in pl.placed if is_cap(r) and comps[r].sheet in sheets.get(ic, ())
                         and any(run.net(r, q) in nets for q in ('1', '2'))}
        for row in run.near_rows:
            if row['ic'] == ic and row['part'].startswith('Y'):
                y = row['part']
                xnets = {run.net(y, p) for p in run.board_pads(y)} - {'', 'GND'}
                run.approved |= {y} | {r for r in pl.placed
                                       if is_cap(r) and any(run.net(r, q) in xnets for q in ('1', '2'))}
    # the crystals' lanes: in front of each MCU pin on a crystal's net, nothing this run moves but the crystal parts
    for ic in a.refs:
        ic_pads = run.board_pads(ic)
        cx, cy, _ = pl.placed[ic]
        for row in run.near_rows:
            if row['ic'] != ic or not row['part'].startswith('Y'):
                continue
            y = row['part']
            xnets = {run.net(y, p) for p in run.board_pads(y)} - {'', 'GND'}
            run.xtal |= {y} | {r for r in pl.placed if is_cap(r) and any(run.net(r, q) in xnets for q in ('1', '2'))}
            for p, g in ic_pads.items():
                if run.net(ic, p) not in xnets:
                    continue
                px, py = g.centroid.x, g.centroid.y
                x0, y0, x1, y1 = g.bounds
                if abs(px - cx) > abs(py - cy):
                    t = x1 if px > cx else x0
                    run.lanes.append((min(t, t + LANE * (1 if px > cx else -1)), py - 0.25,
                                      max(t, t + LANE * (1 if px > cx else -1)), py + 0.25))
                    run.lane_side.append((ic, (1 if px > cx else -1, 0), (py - 0.25, py + 0.25)))
                else:
                    t = y1 if py > cy else y0
                    run.lanes.append((px - 0.25, min(t, t + LANE * (1 if py > cy else -1)),
                                      px + 0.25, max(t, t + LANE * (1 if py > cy else -1))))
                    run.lane_side.append((ic, (0, 1 if py > cy else -1), (px - 0.25, px + 0.25)))
    report, settled = [], set()
    lim = getattr(spec, 'PROBE_STUB_MAX', (10.0, 20.0))
    for r in run.room:                                     # test points stay beside their nets' routes
        route = pl.probe_route(r) if r.startswith('TP') and r in pl.placed else None
        if route:
            pin, segs, _ = route
            run.stub[r] = (pin, segs, lim[0] if run.net(r, pin) in getattr(spec, 'PROBES_WITH_CIRCUIT', ()) else lim[1])
    where = lambda r: pl.placed[r] if r in pl.placed else run.orig[r]
    have = {}

    def serve(row):
        ic, limit = row['ic'], row['mm']
        ic_pads = run.board_pads(ic)
        for net in row['nets']:
            pins = sorted((p for p in ic_pads if run.net(ic, p) == net), key=int)
            key = lambda p: (ic, row['value'], p)
            caps = pool(ic, net, row['value'])

            def gap(r, p):
                x, y, rot = pl.placed[r]
                q = next(q for q in ('1', '2') if run.net(r, q) == net)
                return run.pads_at(r, x, y, rot)[q].distance(ic_pads[p])
            owner = {}                                     # keep what's in reach, one capacitor to one pin

            def take(p, seen):
                for r in caps:
                    if r not in seen and r not in settled and r in pl.placed and gap(r, p) <= limit:
                        seen.add(r)
                        if r not in owner or take(owner[r], seen):
                            owner[r] = p
                            return True
                return False
            for p in pins:
                if not have.get(key(p)):
                    take(p, set())
            for r, p in sorted(owner.items(), key=lambda rp: int(rp[1])):
                settled.add(r)
                have[key(p)] = have.get(key(p), 0) + 1
                report.append(f'{ic}.{p} {net}: {r} stays, gap {gap(r, p):.2f} mm')
            free = [r for r in caps if r not in settled]
            for p in [p for p in pins if not have.get(key(p))]:
                if not free:
                    report.append(f'{ic}.{p} {net}: no free {row["value"]} on its sheet')
                    continue
                px, py = ic_pads[p].centroid.x, ic_pads[p].centroid.y
                r = min(free, key=lambda r: (math.hypot(where(r)[0] - px, where(r)[1] - py), r))
                if run.to_pin(r, ic, p, limit, settled, 'its pin', report):
                    free.remove(r)
                    settled.add(r)
                    have[key(p)] = have.get(key(p), 0) + 1
            for r in list(free):                           # left over: to the pin with fewest
                if r in pl.placed and any(gap(r, p) <= limit for p in pins):
                    report.append(f'{ic} {net}: {r} spare, in reach already')
                    settled.add(r)
                    continue
                p = min(pins, key=lambda p: (have.get(key(p), 0), math.hypot(where(r)[0] - ic_pads[p].centroid.x,
                                                                             where(r)[1] - ic_pads[p].centroid.y)))
                if run.to_pin(r, ic, p, limit, settled, 'spare, to the pin with fewest', report):
                    settled.add(r)
                    have[key(p)] = have.get(key(p), 0) + 1

    ordered = sorted(rows, key=lambda r: (a.refs.index(r['ic']), r['mm']))
    for row in ordered:
        serve(row)
    moves = run.moves()
    print('@@' + json.dumps({'moves': moves, 'report': report}))
    if a.plan:
        Path(a.plan).write_text(json.dumps({'moves': moves, 'report': report}, indent=1) + '\n')
    if a.write and moves:
        ask = sorted(r for r, m in moves.items() if m['class'] == 'needs Seán')
        if ask and not a.yes:
            sys.exit(f'not written: {", ".join(ask)} move more than {NUDGE} mm and need Seán\'s yes (--yes)')
        pfile = run.hw / 'layout' / spec.PLACEMENT
        data = json.loads(pfile.read_text())
        for r, m in moves.items():
            data['parts'][r] = m['to']
        pfile.write_text(json.dumps(data, indent=0) + '\n')


if __name__ == '__main__':
    main()
