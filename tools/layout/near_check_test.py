"""Plant one miss per kind of distance rule on Burrito's built board and see the build's check report it (D-24Nov.4:
"Every check says how many things it measured, and is proven on a planted miss").

    python3 tools/layout/near_check_test.py [BOARD]

The board's pads are read once; each test moves one part's pads 30 mm away in memory (the board file is not
touched) or empties a row's measurement, then runs engine/metrics.near_rules and passes when the expected part
appears in the misses. A further test drops one passive's rows and expects it listed without a rule; two take an
accepted written exception's approval, then its mitigation, away and expect a miss; one moves a part off a line its
rule measures as drawn; one plants a track across a fine-pitch pin's lane (D-24Nov.11); one breaks a net drawn
whole, whose pins have no lane, and expects the lane back (D-24Nov.13); and the last takes a plane pin's via away and
expects its lane back (D-24Nov.15).
Prints one line per test and exits non-zero if any fails.
"""
import copy
import sys
from types import SimpleNamespace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build                               # noqa: E402
from engine import board as B              # noqa: E402
from engine import metrics as M            # noqa: E402
from shapely.affinity import translate     # noqa: E402
from shapely.geometry import LineString    # noqa: E402


def moved(bd, ref, dx=30.0):
    """A copy of the board data with `ref`'s pads moved dx mm."""
    b2 = copy.copy(bd)
    pads = []
    for d in bd.pads:
        if d['ref'] == ref:
            d = dict(d, x=d['x'] + dx, poly={l: translate(g, dx, 0) for l, g in d['poly'].items()})
        pads.append(d)
    b2.pads = pads
    b2.by_net = {}
    for d in pads:
        b2.by_net.setdefault(d['net'], []).append(d)
    return b2


def clone(spec):
    return SimpleNamespace(**{k: v for k, v in vars(spec).items() if not k.startswith('__')})


def misses_for(bd, spec, part):
    return [m for r in M.near_rules(bd, spec) if r['what'] == part for m in r['misses']]


def main():
    board = sys.argv[1] if len(sys.argv) > 1 else 'croi2'
    spec = build.load_spec(board)
    pcb = build.ROOT / 'hardware' / board / f'{spec.NAME}.kicad_pcb'
    bd = M.BoardData(B.K.LoadBoard(str(pcb)), spec.ORIGIN, (spec.W, spec.H))
    base = {r['what']: r for r in M.near_rules(bd, spec)}
    tests = []
    # one row of each kind that passes now, its part moved 30 mm: the check must report it
    for kind in ('part_to_pins', 'supply_caps', 'net_caps', 'on_line'):
        row = next((r for r in spec.NEAR if r['rule'] == kind and not base.get(r.get('part') or r['ic'], {}).get('misses')
                    and not r.get('exception')), None)
        if row is None:
            tests.append((f'{kind}: no passing row to plant a miss in', False))
            continue
        if kind == 'part_to_pins' or kind == 'on_line':
            part, what = row['part'], row['part']
        else:                                   # a cap rule: move the chip, whose pins the rule measures from
            part, what = row['ic'], row['ic']
        got = misses_for(moved(bd, part), spec, what)
        tests.append((f'{kind}: {part} moved 30 mm -> {got[:1] or "no miss"}', bool(got)))
    # a part_to_pins row naming a pin its part doesn't share: measured nothing, so it must miss
    row = next(r for r in spec.NEAR if r['rule'] == 'part_to_pins' and r.get('pin') and r['part'].startswith('C'))
    bad = dict(row, pin='999')
    s2 = clone(spec)
    s2.NEAR = [bad if r is row else r for r in spec.NEAR]
    got = misses_for(bd, s2, row['part'])
    tests.append((f"part_to_pins: {row['part']} named to a pin that doesn't exist -> {got[:1] or 'no miss'}", bool(got)))
    # a passive whose rows are dropped must be listed as without a rule
    s3 = clone(spec)
    s3.NEAR = [r for r in spec.NEAR if r.get('part') != row['part']]
    m = M.measure(bd, s3, None) if hasattr(M, 'measure') else None
    listed = m is not None and row['part'] in m.get('passives_without_rule', [])
    tests.append((f"coverage: {row['part']}'s rows dropped -> {'listed' if listed else 'not listed'}", listed))
    # a written exception is accepted only when approved and its mitigation is in place (D-24Nov.6)
    exr = next((r for r in spec.NEAR if r.get('exception') and base.get(r['part'], {}).get('accepted')), None)
    if exr is None:
        tests.append(('exception: no accepted exception to test', False))
    else:
        for label, change in (('not approved', dict(approved=None)),
                              ('mitigation missing', dict(check=('drawn', 'NO_SUCH_NET')))):
            s4 = clone(spec)
            s4.NEAR = [dict(r, exception=dict(r['exception'], **change)) if r is exr else r for r in spec.NEAR]
            got = misses_for(bd, s4, exr['part'])
            tests.append((f"exception: {exr['part']} {label} -> {got[:1] or 'accepted'}", bool(got)))
    # an on_line row measured from the drawn line (D-24Nov.11): its part moved 30 mm off the line must miss
    drow = next((r for r in spec.NEAR if r['rule'] == 'on_line' and r.get('line') == 'drawn'
                 and not base.get(r['part'], {}).get('misses')), None)
    if drow is None:
        tests.append(('on_line, drawn line: no passing row to plant a miss in', False))
    else:
        got = misses_for(moved(bd, drow['part']), spec, drow['part'])
        tests.append((f"on_line, drawn line: {drow['part']} moved 30 mm -> {got[:1] or 'no miss'}", bool(got)))
    # a fine-pitch pin's lane (D-24Nov.11): a planted track of another net straight across it must be listed
    lanes = M.pin_lanes(bd)
    n0, crossed0 = M.lanes_crossed(bd)
    free = next(((r, q, n, g) for r, q, n, g in lanes if r == 'U201' and not any(c.startswith(f'{r}.{q} ') for c in crossed0)), None)
    if free is None:
        tests.append(('lanes: no uncrossed U201 lane to plant a crossing in', False))
    else:
        r, q, n, g = free
        c = g.centroid
        plant = LineString([(c.x - 0.6, c.y - 0.6), (c.x + 0.6, c.y + 0.6)]).buffer(0.05)
        _, crossed = M.lanes_crossed(bd, extra=[('PLANTED', plant)])
        hit = [x for x in crossed if x.startswith(f'{r}.{q} ')]
        tests.append((f'lanes: a planted track across {r}.{q} ({n}) of {n0} lanes -> {hit[:1] or "not listed"}', bool(hit)))
    # a pin whose own net is drawn whole has no lane (D-24Nov.13): break the net by moving another of its parts 30 mm
    # and the pin's lane must come back
    whole = M.nets_drawn_whole(bd)
    ex = next(((r, q, n) for r, q, n, g in M.pin_lanes(bd, whole=set()) if n in whole), None)
    other = ex and next((d['ref'] for d in bd.pads if d['net'] and M.short(d['net']) == ex[2] and d['ref'] != ex[0]), None)
    if not other:
        tests.append(('lanes, drawn whole: no exempt pin with another part on its net to test', False))
    else:
        r, q, n = ex
        now = any((r2, q2) == (r, q) for r2, q2, _, _ in M.pin_lanes(bd, whole=whole))
        back = any((r2, q2) == (r, q) for r2, q2, _, _ in M.pin_lanes(moved(bd, other)))
        tests.append((f"lanes, drawn whole: {r}.{q} ({n}) has {'a lane' if now else 'none'}; {other} moved 30 mm -> "
                      f"{'its lane back' if back else 'still none'}", back and not now))
    # a plane pin whose via is in place has no lane (D-24Nov.15): with the trial's fan-out a FLIGHT_3V3 pin's lane goes;
    # taken out of the served set, as if its via were missing, it comes back
    import meter
    served = M.served_plane_pins(bd, meter.fan_out(B.K.LoadBoard(str(pcb)), spec, **spec.TRIAL_FANOUT))
    pp = next(((r, q, n) for r, q, n, g in M.pin_lanes(bd, served=set()) if (r, q) in served), None)
    if pp is None:
        tests.append(('lanes, plane pins: no served plane pin with a lane to test', False))
    else:
        r, q, n = pp
        now = any((r2, q2) == (r, q) for r2, q2, _, _ in M.pin_lanes(bd, served=served))
        back = any((r2, q2) == (r, q) for r2, q2, _, _ in M.pin_lanes(bd, served=served - {(r, q)}))
        tests.append((f"lanes, plane pins: {r}.{q} ({n}) has {'a lane' if now else 'none'}; its via taken away -> "
                      f"{'its lane back' if back else 'still none'}", back and not now))
    for t, ok in tests:
        print(('PASS ' if ok else 'FAIL ') + t)
    print(f"{sum(ok for _, ok in tests)} of {len(tests)} pass")
    sys.exit(0 if all(ok for _, ok in tests) else 1)


if __name__ == '__main__':
    main()
