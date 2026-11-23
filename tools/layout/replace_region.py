"""Re-place the small parts of a region of the board, as edits to placement.json (D-22Nov.30).

    python3 tools/layout/replace_region.py croi2 --box X0,Y0,X1,Y1 [--box ...] [--mcus U201 U401] [--stamp]
        [--plan FILE] [--write]

Every movable part whose courtyard centre lies in a box is lifted: resistors, capacitors, inductors, diodes, FETs,
crystals and test points. ICs, connectors, the spec's fixed parts, anchors and edge-region parts stay, and so do
J6601's output capacitors (D-22Nov.28). Then they go down again in this order:

1. With --stamp, each row of spec.PYRO_STAMP at its offset from its channel's high side (D-22Nov.27).
2. The named MCUs' capacitors to their pins, as caps_to_pins.py does it (D-23Nov.1): crystal lanes kept clear.
3. Their crystals, pulled to their pins as the placer pulls them (spec.NEAR), then each load capacitor at its
   crystal's pad.
4. Everything else in the placer's own order and by its own pulls (engine/place.py), the crystal lanes closed to
   them; a part under a distance rule as soon as what it's measured from is placed, and a test point on a
   sensitive node (spec.PROBES_WITH_CIRCUIT) as soon as its circuit is (stage B2 step 5).
5. The other test points last, each beside its net's route (spec.PROBE_STUB_MAX).
6. A part under a part_to_pins rule that is still out of reach goes to the nearest spot in reach, the other lifted
   parts nudged aside up to 3 mm from where they've just gone.

Nothing outside the boxes moves. Prints every move and anything that found no spot; --plan writes them as JSON;
--write puts the moves in placement.json, and refuses if any part found no spot.
"""
import argparse
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build                               # noqa: E402
import caps_to_pins as CT                  # noqa: E402
from engine import netlist                 # noqa: E402

LIFTABLE = ('C', 'R', 'L', 'D', 'FB', 'Q', 'Y', 'TP')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('board')
    ap.add_argument('--box', action='append', required=True, help='X0,Y0,X1,Y1 in board mm')
    ap.add_argument('--mcus', nargs='*', default=[])
    ap.add_argument('--stamp', action='store_true')
    ap.add_argument('--also', nargs='*', default=[], help='lift these parts too, whatever their kind or place')
    ap.add_argument('--closed', action='append', default=[], help='X0,Y0,X1,Y1: no re-placed part in this box '
                    '(an area the hard copper takes, where a pad would need a via it can\'t have)')
    ap.add_argument('--block', action='store_true', help="spec.PYRO_PARTS at their spots first, and spec.PYRO_COPPER's "
                    'L1 copper, with the fire rule round it, closed to every other part')
    ap.add_argument('--plan')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--set', action='append', default=[], help="trials: a statement run in the spec's namespace")
    a = ap.parse_args()
    run = CT.Run(SimpleNamespace(board=a.board, others=None, sets=a.set))
    run.anywhere = True                                    # a lifted part may go anywhere its search finds
    pl, spec, comps = run.pl, run.spec, run.comps
    boxes = [tuple(float(v) for v in b.split(',')) for b in a.box]
    _, full_nets = netlist.load(str(run.hw / 'output' / 'full-netlist.xml'))
    nets_of = {}
    for n, nodes in full_nets.items():
        for r, _ in nodes:
            nets_of.setdefault(r, set()).add(n)
    keep = set(spec.FIXED) | set(getattr(spec, 'ANCHORS', {})) | set(getattr(spec, 'REF_REGIONS', {}))
    keep |= {r for r in pl.placed if comps.get(r) and comps[r].sheet == '/06b-output-harness/'}

    def liftable(r):
        head = r.rstrip('0123456789')
        return head in LIFTABLE and r[len(head):].isdigit() and r not in keep

    def inside(r):
        c = pl.crt[r]
        x, y = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
        return any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in boxes)
    lifted = sorted(r for r in list(pl.placed) if liftable(r) and inside(r))
    lifted = sorted(set(lifted) | {r for r in a.also if r in pl.placed})
    if a.block:                                           # the output stage's own parts, wherever they stand
        lifted = sorted(set(lifted) | {r for r in spec.PYRO_PARTS if r in pl.placed})
    for r in lifted:
        run.lift(r)
    run.movable = set()                                    # nothing outside the boxes is pushed
    report, unplaced, settled = [f'lifted {len(lifted)} parts'], [], set()

    # 1. the stamp
    if a.stamp:
        st = spec.PYRO_STAMP
        for role, refs, (dx, dy), rot in st['rows']:
            for anchor, r in zip(st['anchors'], refs):
                if r in pl.placed:
                    continue
                ax, ay, _ = pl.placed[anchor]
                x, y = round(ax + dx, 3), round(ay + dy, 3)
                if run.fits(r, x, y, rot):
                    run.place(r, x, y, rot)
                    settled.add(r)
                    report.append(f'stamp: {r} ({role}) at ({x}, {y}, {rot})')
                else:
                    hits = run.conflicts(r, x, y, rot)
                    report.append(f'stamp: {r} ({role}) blocked at ({x}, {y}): {sorted(hits) if hits else "board"}')

    # a closed box takes no pad of a part with a plane-net pad (GND, FLIGHT_3V3: D-23Nov.2): every such pad needs a via,
    # and the box is the hard copper's, where no via may go. A part on signal nets alone may sit there.
    boxes = [tuple(float(v) for v in c.split(',')) for c in a.closed]
    closed = []
    if boxes:
        for r in lifted:
            if any(n in ('GND', 'FLIGHT_3V3') for n in (run.net(r, q) for q in pl.pin_nets.get(r, {}))):
                pl.pad_keepout[r] = list(pl.pad_keepout.get(r, [])) + boxes

    # 1b. the output stage (D-22Nov.27, D-23Nov.9): its parts at their spots, then its L1 copper closed to the rest,
    # sampled along each track as squares of the track's half width plus the fire rule's 0.5 mm
    copper_rects = []
    if a.block:
        for r, (x, y, rot) in spec.PYRO_PARTS.items():
            hits = run.conflicts(r, x, y, rot)
            run.place(r, x, y, rot)
            settled.add(r)
            report.append(f'block: {r} at ({x}, {y}, {rot})' + (f', over {sorted(hits)}' if hits else ''))
        for it in spec.PYRO_COPPER:
            if it.get('layer') != 'F.Cu' or 'path' not in it:
                continue
            h = it['w'] / 2 + 0.5
            for (x0, y0), (x1, y1) in zip(it['path'], it['path'][1:]):
                n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 0.25))
                for i in range(n + 1):
                    x, y = x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n
                    copper_rects.append((x - h, y - h, x + h, y + h, 'pyro copper'))
        pl.rects.extend(copper_rects)

    # 2. the MCUs' capacitors
    if a.mcus:
        rows = CT.prepare(run, a.mcus)
        CT.serve_caps(run, rows, report, settled)

    # 3. crystals, then their load capacitors
    pl.near = build.near_plan(spec, comps, full_nets)
    region = lambda r: build.region_of(r, comps, nets_of, spec)[0] or (1, 1, spec.W - 1, spec.H - 1)

    def put(r):
        if r in pl.placed:                                # already down (a list can name a part twice)
            return True
        if pl.place_grow(r, region(r)):
            return True
        unplaced.append(r)
        return False
    for r in [r for r in lifted if r.startswith('Y') and r not in pl.placed]:
        put(r)
    for r in [r for r in lifted if r in run.xtal and not r.startswith('Y') and r not in pl.placed]:
        n = next(run.net(r, q) for q in ('1', '2') if run.net(r, q) != 'GND')
        near = None
        for y in (y for y in run.xtal if y.startswith('Y') and y in pl.placed):
            x0, y0, rot = pl.placed[y]
            for q, g in run.pads_at(y, x0, y0, rot).items():
                if run.net(y, q) == n:
                    near = (g.centroid.x, g.centroid.y)
        if not run.relocate(r, run.depth, set(settled), near=near):
            unplaced.append(r)

    # 4. the rest, in the placer's order, the crystal lanes closed to them; a test point on a sensitive node goes
    # down as soon as its circuit is (stage B2 step 5), every other test point last
    lane_rects = [(*k, 'crystal lane') for k in run.lanes]
    pl.rects.extend(lane_rects)
    rest = [r for r in lifted if r not in pl.placed and r not in unplaced and not r.startswith('TP')]
    wait = {r: d for r, d in pl.near.items() if r in rest}
    probes = [r for r in lifted if r.startswith('TP') and r not in pl.placed]
    net1 = lambda r: next(iter(pl.pin_nets.get(r, {'1': ''}).values()))
    sens = [r for r in probes if net1(r).rsplit('/', 1)[-1] in getattr(spec, 'PROBES_WITH_CIRCUIT', ())]

    def flush():
        for w in [w for w, d in wait.items() if d['anchor'] in pl.placed and d.get('also', d['anchor']) in pl.placed]:
            put(w)
            del wait[w]
        for tp in list(sens):
            if all(q in pl.placed for q, _ in pl.nets[net1(tp)] if not q.startswith('TP')):
                pl.probe_look = 20.0
                put(tp)
                pl.probe_look = 10.0
                sens.remove(tp)
    flush()
    for r in pl.order([r for r in rest if r not in wait]):
        put(r)
        flush()
    for w in list(wait):
        put(w)

    # 5. the other test points
    for r in sorted(r for r in probes if r not in pl.placed and r not in unplaced):
        pl.probe_look = 20.0 if r in sens else 10.0
        put(r)
    pl.probe_look = 10.0

    # 6. a distance rule the placer missed: the part goes to the nearest spot in reach of its pin, lifted parts
    # nudged aside up to 3 mm from where they now are
    orig0, run.orig = run.orig, dict(pl.placed)
    run.anywhere = False
    run.movable, run.room = set(lifted), {r: 3.0 for r in lifted}
    now = lambda r: run.pads_at(r, *pl.placed[r])
    for row in getattr(spec, 'NEAR', []):
        part, ic = row.get('part'), row.get('ic')
        if row['rule'] != 'part_to_pins' or part not in lifted or part not in pl.placed or ic not in pl.placed:
            continue

        def gap(pads):
            gs = [g.distance(h) for q, g in pads.items() if run.net(part, q) not in ('', 'GND')
                  for k, h in now(ic).items() if run.net(ic, k) == run.net(part, q)]
            return min(gs) if gs else None
        g0 = gap(now(part))
        if g0 is None or g0 <= row['mm']:
            continue
        tx, ty = next(h.centroid.coords[0] for q, g in now(part).items() if run.net(part, q) not in ('', 'GND')
                      for k, h in now(ic).items() if run.net(ic, k) == run.net(part, q))
        mark = len(run.log)
        run.lift(part)
        spots = []
        n = int((row['mm'] + 2.0) / CT.STEP)
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                x, y = round(tx + i * CT.STEP, 3), round(ty + j * CT.STEP, 3)
                for rot in pl.rotset.get(part, CT.P.ROTS):
                    g = gap(run.pads_at(part, x, y, rot))
                    if g is not None and g <= row['mm'] - 0.02:
                        spots.append((round(g, 2), round(math.hypot(x - tx, y - ty), 2), x, y, rot))
        done = False
        for g, _, x, y, rot in sorted(spots)[:200]:
            if run.make_room(part, x, y, rot, 0, set(settled) | {ic}):
                report.append(f'near: {part} to ({x}, {y}, {rot}), {g} mm from {ic} (was {g0:.1f})')
                done = True
                break
        if not done:
            run.rollback(mark)
            report.append(f'near: {part} still {g0:.1f} mm from {ic}, no spot in reach')
    run.orig = orig0
    for k in lane_rects + copper_rects + closed:
        pl.rects.remove(k)

    moves = run.moves()
    for m in moves.values():
        m['class'] = 'region'
    far = sorted(((m['mm'], r) for r, m in moves.items()), reverse=True)[:12]
    report.append('farthest: ' + ', '.join(f'{r} {d} mm' for d, r in far))
    if unplaced:
        report.append(f'NO SPOT: {", ".join(sorted(set(unplaced)))}')
    out = {'lifted': lifted, 'moves': moves, 'unplaced': sorted(set(unplaced)), 'report': report}
    print('@@' + json.dumps(out))
    if a.plan:
        Path(a.plan).write_text(json.dumps(out, indent=1) + '\n')
    if a.write:
        if unplaced:
            sys.exit(f'not written: {", ".join(sorted(set(unplaced)))} found no spot')
        CT.write_moves(run, moves)


if __name__ == '__main__':
    main()
