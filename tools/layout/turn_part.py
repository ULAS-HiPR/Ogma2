"""Trial turns of a part whose pin must face a connector (D-23Nov.3: U4606's RF pin toward J4601), as edits to
placement.json (D-22Nov.30).

    python3 tools/layout/turn_part.py croi2 U4606 --pin 10 --toward J4601.1 --esd D4601 [--rots 0 90 270]
        [--reach 5] [--others 4] [--plan FILE] [--write ROT]

For each rotation, the part's centre is tried on a 0.25 mm grid within --reach mm of where it stands, nearest the
connector first: the straight distance from its pin to the connector's pad, then how much of that line runs under
the part's own body, then what's in the way. What's in the way moves out of it, the least distance it can (the
machinery of caps_to_pins.py): passives and test points up to --others mm, nothing else. At each centre the ESD part
must also go on the line, its pad on the pin's net within its on_line row's distance of it (spec.NEAR) and between
the two pads, as near the connector as it fits, moving what's in its way the same way; a centre where it can't is
passed over. Prints, for each rotation, the best centre, the line's straight length, and every part displaced and
how far.
--write ROT puts that rotation's moves in placement.json. The line itself is drawn by the copper stage (rf_lines).
"""
import argparse
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from shapely.geometry import LineString, box   # noqa: E402

import caps_to_pins as CT                  # noqa: E402
from engine import place as P              # noqa: E402

GRID = 0.25
TRIES = 20                                 # centres tried with parts moved, per rotation
ESD_ROOM = 2.4                             # line clear of both bodies, mm: the ESD part's body and JLC's gaps


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('board')
    ap.add_argument('ref')
    ap.add_argument('--pin', required=True)
    ap.add_argument('--toward', required=True, help='REF.PIN of the connector pad')
    ap.add_argument('--esd', help='the ESD part that goes on the line')
    ap.add_argument('--rots', nargs='+', type=int, default=[0, 90, 180, 270])
    ap.add_argument('--reach', type=float, default=5.0)
    ap.add_argument('--others', type=float, default=4.0)
    ap.add_argument('--plan')
    ap.add_argument('--write', type=int, metavar='ROT')
    ap.add_argument('--set', action='append', default=[], help="trials: a statement run in the spec's namespace")
    a = ap.parse_args()
    run = CT.Run(SimpleNamespace(board=a.board, others=a.others, sets=a.set))
    pl, spec = run.pl, run.spec
    ref, pin = a.ref, a.pin
    cref, cpin = a.toward.split('.')
    target = run.board_pads(cref)[cpin].centroid
    row = next((r for r in spec.NEAR if r['rule'] == 'on_line' and r.get('part') == a.esd), None)
    x0, y0, a0 = run.orig[ref]
    results = {}
    for rot in a.rots:
        mark0 = len(run.log)
        run.lift(ref)
        cands = []
        n = int(a.reach / GRID)
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                x, y = round(x0 + i * GRID, 3), round(y0 + j * GRID, 3)
                if math.hypot(x - x0, y - y0) > a.reach:
                    continue
                hits = run.conflicts(ref, x, y, rot)
                if hits is None or any(h not in run.movable for h in hits):
                    continue
                pads = run.pads_at(ref, x, y, rot)
                pp = pads[pin].centroid
                line = LineString([(pp.x, pp.y), (target.x, target.y)])
                crt = pl.boxes_at(ref, x, y, rot)[0]
                under = line.intersection(box(*crt).difference(pads[pin].buffer(0.6))).length
                if a.esd and row:                      # room on the line for the ESD part, outside both bodies
                    free = line.difference(box(*crt).union(box(*pl.crt[cref])))
                    longest = max((g.length for g in getattr(free, 'geoms', [free])), default=0.0)
                    if longest < ESD_ROOM:
                        continue
                area = sum((lambda c: (c[2] - c[0]) * (c[3] - c[1]))(pl.crt[h]) for h in hits)
                cands.append(((round(line.length * 2) / 2, round(under, 1), len(hits), round(area, 1)), x, y, hits))
        cands.sort(key=lambda c: c[0])
        def esd_on_line(x, y):
            """Put the ESD part on the line from the pin (part at x, y) to the connector; its spot, or None."""
            pp = run.pads_at(ref, x, y, rot)[pin].centroid
            line = LineString([(pp.x, pp.y), (target.x, target.y)])
            net = run.net(ref, pin)
            ex, ey, ea = run.orig[a.esd]
            run.lift(a.esd)
            spots = []
            for t in range(1, 40):
                cx_, cy_ = line.interpolate(t / 40, normalized=True).x, line.interpolate(t / 40, normalized=True).y
                for i in range(-20, 21):
                    for j in range(-20, 21):
                        sx, sy = round(round((cx_ + i * CT.STEP) / CT.STEP) * CT.STEP, 3), \
                            round(round((cy_ + j * CT.STEP) / CT.STEP) * CT.STEP, 3)
                        for r2 in pl.rotset.get(a.esd, P.ROTS):
                            ep = run.pads_at(a.esd, sx, sy, r2)
                            q = next((k for k in ep if run.net(a.esd, k) == net), None)
                            if q is None:
                                continue
                            c = ep[q].centroid
                            u = line.project(c, normalized=True)
                            if not 0.0 < u < 1.0 or line.distance(c) > row['mm'] - 0.05:
                                continue
                            hits = run.conflicts(a.esd, sx, sy, r2)
                            if hits is None or any(h in (cref, ref) or h not in run.movable for h in hits):
                                continue
                            spots.append((round(c.distance(target), 2), len(hits), sx, sy, r2))
            for d, _, sx, sy, r2 in sorted(set(spots))[:60]:
                if run.make_room(a.esd, sx, sy, r2, 0, {cref, ref}):
                    return {'at': [sx, sy, r2], 'from_connector_mm': d}
            run.place(a.esd, ex, ey, ea)
            return None

        best = None
        print(f'rot {rot}: {len(cands)} centres clear of fixed parts', file=sys.stderr)
        for key, x, y, hits in cands[:TRIES]:
            mark = len(run.log)
            if not run.make_room(ref, x, y, rot, 0, {cref}):
                print(f'  ({x}, {y}) {key}: no room ({len(hits)} in the way)', file=sys.stderr)
                continue
            esd = esd_on_line(x, y) if a.esd and row else {}
            print(f'  ({x}, {y}) {key}: room; ESD {esd}', file=sys.stderr)
            if esd is not None:
                c = run.cost(mark, ref)
                if best is None or (key[:2], c) < (best[0][:2], best[1]):
                    best = (key, c, x, y)
            run.rollback(mark)
        if best is None:
            results[rot] = {'result': 'no centre fits'}
            run.rollback(mark0)
            continue
        key, c, x, y = best
        assert run.make_room(ref, x, y, rot, 0, {cref})
        res = {'centre': [x, y], 'line_straight_mm': key[0], 'line_under_body_mm': key[1]}
        if a.esd and row:
            res['esd'] = esd_on_line(x, y)
        res['moves'] = run.moves()
        results[rot] = res
        if a.write == rot:
            pfile = run.hw / 'layout' / spec.PLACEMENT
            data = json.loads(pfile.read_text())
            for r, m in res['moves'].items():
                data['parts'][r] = m['to']
            pfile.write_text(json.dumps(data, indent=0) + '\n')
        run.rollback(mark0)
    print('@@' + json.dumps(results))
    if a.plan:
        Path(a.plan).write_text(json.dumps(results, indent=1) + '\n')


if __name__ == '__main__':
    main()
