"""Move every passive to the pin it serves (D-24Nov.1), as edits to placement.json (D-22Nov.30).

    python3 tools/layout/caps_to_chips.py croi2 [--room MM] [--depth N] [--step MM] [--plan FILE] [--write]
    python3 tools/layout/caps_to_chips.py croi2 --apply PLAN    (a saved plan's moves, without searching again)

caps_to_pins.py does it for the two MCUs (D-23Nov.1); this does it for every other passive, from the spec's D-24Nov.1
rows (spec.CAP_PINS and spec.PASSIVE_PINS): each names the part, the chip and the pin it serves, with its distance
(copper gap, pad edge to that pin, as the build's near check measures it). A part already in reach stays. Each one
out of reach, tightest rule first and then the farthest, goes to the spot beyond its pin's tip that disturbs least
(caps_to_pins.Run.to_pin): a free one if there is one, else one whose occupants can move out of the way.

What may move to make room: the other small parts (R, C, L, D, FB, TP) up to --room mm from where they stood (3 by
default), each keeping its own distance rule, a test point staying beside its net's route (spec.PROBE_STUB_MAX).
What never moves: the MCUs' capacitors, the crystals and their load capacitors, the stamped parts (spec.PYRO_PARTS,
spec.POWER_PARTS, spec.PYRO_STAMP) and any part the scripted copper reaches. A part already in reach may be pushed
aside to make room, only within its own rule.
Nothing goes on the scripted copper, within the fire rule of fire copper or 1 mm of an RF line, or in front of a
crystal pin; a part already in an RF line's corridor is placed again, after the --first parts (D-24Nov.8).

Prints every move and each capacitor still out of reach; --plan writes them as JSON; --write puts them in
placement.json.
"""
import argparse
import json
import re
import math
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build                               # noqa: E402
import caps_to_pins as CT                  # noqa: E402
from engine.metrics import rule_pins        # noqa: E402
from shapely.geometry import LineString, Point   # noqa: E402

FIREISH = ('FIRE', 'FIRE_LOGIC', 'PYRO_RAIL')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('board')
    ap.add_argument('--room', type=float, default=3.0, help='how far another small part may move to make room, mm')
    ap.add_argument('--depth', type=int, default=CT.DEPTH)
    ap.add_argument('--step', type=float, default=CT.STEP, help='the spot grid, mm')
    ap.add_argument('--along', type=float, default=CT.ALONG, help="how far the search runs along a pin's row, mm")
    ap.add_argument('--budget', type=float, default=60.0, help="seconds per part for making room (the cheapest first)")
    ap.add_argument('--only', nargs='*', help='trials: only these parts')
    ap.add_argument('--first', nargs='*', default=[],
                    help='scarce room goes by consequence (D-24Nov.4): these parts, in this order, are placed first, '
                         'even where already in reach')
    ap.add_argument('--free', nargs='*', default=[], help='parts that may move though an earlier pass placed them')
    ap.add_argument('--plan')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--set', action='append', default=[], help="trials: a statement run in the spec's namespace")
    ap.add_argument('--fallback', type=float, default=10.0,
                    help='a ranked part with no spot inside its rule and its old spot taken goes to the nearest spot '
                         'this far from its pin, reported as outside its rule')
    ap.add_argument('--apply', help="write a saved plan's moves to placement.json, each from where it stands now")
    a = ap.parse_args()
    if a.apply:
        spec = build.load_spec(a.board)
        pfile = build.ROOT / 'hardware' / a.board / 'layout' / spec.PLACEMENT
        data, moves = json.loads(pfile.read_text()), json.loads(Path(a.apply).read_text())['moves']
        stale = [r for r, m in moves.items() if [round(v, 3) for v in data['parts'][r]] != [round(v, 3) for v in m['from']]]
        if stale:
            sys.exit(f'the plan is stale for {", ".join(sorted(stale))}: placement.json has moved since')
        for r, m in moves.items():
            data['parts'][r] = m['to']
        pfile.write_text(json.dumps(data, indent=0) + '\n')
        print(f'{len(moves)} moves written to {pfile.name}')
        return
    run = CT.Run(SimpleNamespace(board=a.board, others=None, sets=a.set))
    run.depth = a.depth
    CT.STEP, CT.BUDGET, CT.ALONG = a.step, a.budget, a.along
    pl, spec, comps = run.pl, run.spec, run.comps
    rows = [r for r in spec.NEAR if r['rule'] == 'part_to_pins' and re.match(r'^(R|C|L|FB|F)\d', r['part'])]
    small = {r for r in run.movable if not r.startswith('Y')}
    run.room = {r: a.room for r in small}
    CT.prepare(run, ['U201', 'U401'])                     # the crystals' lanes, the MCUs' own parts, probe routes
    why = {}
    for r in run.approved:
        why[r] = "an MCU's own part (D-23Nov.1)"
    for r in run.xtal:
        why[r] = 'a crystal or its load capacitor, placed with the crystal'
    for r in list(spec.PYRO_PARTS) + list(getattr(spec, 'POWER_PARTS', {})) + \
            [r for _, refs, _, _ in spec.PYRO_STAMP['rows'] for r in refs]:
        why[r] = 'stamped'
    for r in a.free:
        why.pop(r, None)
    keep = set(why)
    block = spec.PYRO_COPPER + getattr(spec, 'POWER_COPPER', [])
    cls = {}
    import fnmatch
    for n in {it['net'] for it in block}:
        cls[n] = next((c for c, p in spec.PATTERNS if fnmatch.fnmatchcase(n, p)), 'Default')
    cu = []                                    # one piece per via and per straight run, so a bend's box stays small
    for it in block:
        if 'via' in it:
            cu.append((it['net'], Point(*it['via']).buffer(it.get('d', 0.6) / 2)))
        elif it.get('layer') == 'F.Cu':
            pts = it['path']
            cu += [(it['net'], (LineString(pts[i:i + 2]) if len(pts) > 1 else Point(pts[0])).buffer(it['w'] / 2))
                   for i in range(max(1, len(pts) - 1))]
    for r in sorted(small):                                # the scripted copper's own parts stay
        if any(run.net(r, p) == n and g.intersects(cg) for p, g in run.board_pads(r).items() for n, cg in cu):
            keep.add(r)
            why.setdefault(r, 'the scripted copper reaches it')
    run.approved = set()
    run.movable -= keep
    run.room = {r: a.room for r in run.movable}
    rf_rects = []
    for n, g in cu:                                        # the scripted copper, closed to every part placed now
        m = 0.5 if cls.get(n) in FIREISH else 1.0 if cls.get(n) == 'RF50' else 0.0   # RF: 1 mm clear (D-24Nov.8)
        x0, y0, x1, y1 = g.bounds
        pl.rects.append((x0 - m, y0 - m, x1 + m, y1 + m, 'scripted copper'))
        if cls.get(n) == 'RF50':
            rf_rects.append(pl.rects[-1])
    settled, report = set(keep), []         # what may not be pushed aside: a part in reach may, keeping its own rule
    evict = sorted(r for r in run.movable if r in pl.placed and r not in keep and any(
        CT.P.overlap(pl.boxes_at(r, *pl.placed[r])[0], k) for k in rf_rects))
    if evict:                                              # a part in an RF line's corridor is placed again, first
        report.append(f"in an RF line's corridor, placed again: {', '.join(evict)}")
        a.first = a.first + [r for r in evict if r not in a.first]     # after the ranked ones, in their order

    def gap(r, ic, only):
        x, y, rot = pl.placed[r]
        pads, ips = run.pads_at(r, x, y, rot), run.board_pads(ic)
        gs = [(g.distance(h), q, k) for q, g in pads.items() if run.net(r, q) not in ('', 'GND')
              for k, h in ips.items() if run.net(ic, k) == run.net(r, q) and (only is None or k in only)]
        return min(gs) if gs else (None, None, None)
    todo = []
    for row in rows:
        r, ic = row['part'], row['ic']
        if r not in pl.placed or ic not in pl.placed:
            continue
        g, q, k = gap(r, ic, rule_pins(row))
        if g is None:
            continue
        if (g > row['mm'] or r in a.first) and (not a.only or r in a.only or r in a.first):
            todo.append((row['mm'], -g, r, ic, k))
    rank = {r: i for i, r in enumerate(a.first)}
    for r in a.first:                                      # lifted first, so the ranked parts choose before the rest
        if r in pl.placed and r not in keep:
            run.lift(r)
    for mm, ng, r, ic, k in sorted(todo, key=lambda t: (rank.get(t[2], len(rank)), t)):
        if r in keep:
            report.append(f'{r}: {-ng:.1f} mm from {ic}.{k} (rule {mm}), kept: {why[r]}')
        elif run.to_pin(r, ic, k, mm, settled, 'its pin', report):
            pass
        else:
            report.append(f'{r}: still {-ng:.1f} mm from {ic}.{k} (rule {mm}), no spot in reach')
            if r in rank and r not in pl.placed:           # lifted for the ranking: the nearest spot it can have
                lim = min(a.fallback, -ng - 0.1)
                x, y, ang = run.orig[r]
                if lim > mm and run.to_pin(r, ic, k, lim, settled, 'nearer than before, outside its rule', report):
                    report.append(f'{r}: outside its rule ({mm} mm), at the nearest spot it could have')
                elif run.conflicts(r, x, y, ang) == set():
                    run.place(r, x, y, ang)
                elif run.to_pin(r, ic, k, a.fallback, settled, f'outside its rule, within {a.fallback} mm', report):
                    report.append(f'{r}: outside its rule ({mm} mm): its old spot was taken by a part ranked before it')
        if a.plan:                                         # as it goes, so a stopped run keeps what it found
            Path(a.plan).write_text(json.dumps({'moves': run.moves(), 'report': report, 'partial': True}, indent=1))
    for r in a.first:                                      # a ranked part that found no spot goes back where it was
        if r not in pl.placed and r in run.orig:
            x, y, ang = run.orig[r]
            if run.conflicts(r, x, y, ang) == set():
                run.place(r, x, y, ang)
            else:
                report.append(f'{r}: found no spot and its old one is taken: do not apply this plan')
    moves = run.moves()
    out = {'moves': moves, 'report': report}
    print('@@' + json.dumps(out))
    if a.plan:
        Path(a.plan).write_text(json.dumps(out, indent=1) + '\n')
    if a.write and moves:
        CT.write_moves(run, moves)


if __name__ == '__main__':
    main()
