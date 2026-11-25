"""closes.py ITEMS.json --trial TRIAL [--pcb PCB] [--out COUNT.json]: what copper closes before it's frozen
(D-24Nov.15, rule 1: before a router's route is frozen, count what it closes: plane-pad vias, neighbours' in-pad via
sites, and nets open beside it in its source trial).

    python3 /work/tools/layout/closes.py /cap/x.json --trial /root/layers/d25-e532c976 --pcb /cap/b0/Croi2.kicad_pcb

Run in the KiCad chroot. ITEMS are spec items (dict(net, via, d, drill) and dict(net, layer, w, path), board mm), as
route_scoped.py and freeze_fanout.py write them; PCB the board they're to be frozen on (default the repo's). Counts:
1. plane pads: the trial's fan-out (meter.fan_out, spec.TRIAL_FANOUT) without the items and with them drawn: the
   pads open, and every pad whose via moved, went, or is now joined by the items;
2. in-pad via sites: each connected pad off the planes whose via site (its centre, Ø0.45 mm through every layer)
   clears the board's copper without the items and not with them;
3. the source trial's open nets: for each of their fine-pitch pins, the items in its lane (any layer) or within a
   lane's length of the pin;
and the lane check (engine/metrics.lanes_crossed: L1 tracks and vias) without the items and with them.
"""
import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build                                     # noqa: E402
import meter                                     # noqa: E402
import pcbnew as K                               # noqa: E402
from engine import fanout as FO                  # noqa: E402
from engine import metrics as M                  # noqa: E402
from engine.copper import add_track              # noqa: E402
from shapely.geometry import LineString, Point   # noqa: E402

VR = FO.VIA_D / 2


def draw(b, spec, items):
    """The items on a scratch board, as the build draws spec.POWER_COPPER (engine/copper.pyro)."""
    ox, oy = spec.ORIGIN
    nets = {M.short(str(n)): ni for n, ni in b.GetNetsByName().items()}
    lay = {'F.Cu': K.F_Cu, 'B.Cu': K.B_Cu, 'In2.Cu': K.In2_Cu}
    for it in items:
        if 'via' in it:
            v = K.PCB_VIA(b)
            v.SetPosition(K.VECTOR2I(K.FromMM(float(it['via'][0] + ox)), K.FromMM(float(it['via'][1] + oy))))
            v.SetWidth(K.FromMM(it['d'])); v.SetDrill(K.FromMM(it['drill']))
            v.SetNet(nets[it['net']]); v.SetLocked(True)
            b.Add(v)
        else:
            add_track(b, spec.ORIGIN, LineString(it['path']), it['w'], nets[it['net']], lay[it['layer']])


def shapes(items):
    """[(net, shapely, 'via' or the track's layer)] for the items."""
    out = []
    for it in items:
        if 'via' in it:
            out.append((it['net'], Point(it['via']).buffer(it['d'] / 2), 'via'))
        else:
            out.append((it['net'], LineString(it['path']).buffer(it['w'] / 2), it['layer']))
    return out


def count(spec, pcb, items, trial, skip=()):
    """The count, as a dict. `skip`: (ref, num) of pads the items are meant to serve, left out of 'other pads'."""
    f0 = meter.fan_out(K.LoadBoard(str(pcb)), spec, **spec.TRIAL_FANOUT)
    done0 = {(d['ref'], d['num']): d for d in f0['fr']['done']}
    b1 = K.LoadBoard(str(pcb))
    draw(b1, spec, items)
    f1 = meter.fan_out(b1, spec, **spec.TRIAL_FANOUT)
    done1 = {(d['ref'], d['num']): d for d in f1['fr']['done']}
    moved = []
    for k, d in sorted(done0.items()):
        if k in skip:
            continue
        e = done1.get(k)
        if e is None:
            moved.append(f'{k[0]}.{k[1]}: now joined by the items')
        elif (d.get('via') and e.get('via') and math.dist(d['via'], e['via']) > 1e-3) or bool(d.get('via')) != bool(e.get('via')):
            moved.append(f"{k[0]}.{k[1]}: {d.get('via')} -> {e.get('via')}")
    moved += [f'{k[0]}.{k[1]}: a via now, none before' for k in sorted(set(done1) - set(done0)) if k not in skip]

    b0 = K.LoadBoard(str(pcb))
    bd = M.BoardData(b0, spec.ORIGIN, (spec.W, spec.H))
    pair = FO.clearances(spec)
    ox, oy = spec.ORIGIN
    mm = lambda v: (K.ToMM(v.x) - ox, K.ToMM(v.y) - oy)
    cu = []                                          # (net, shape, layer, pad index): the board's copper
    for i, d in enumerate(bd.pads):
        for side in ('F', 'B'):
            if side in d['poly']:
                cu.append((d['net'], d['poly'][side], side, i))
    for t in b0.GetTracks():
        if t.Type() == K.PCB_VIA_T:
            cu.append((t.GetNetname(), Point(mm(t.GetPosition())).buffer(K.ToMM(t.GetWidth(K.F_Cu)) / 2), 'via', None))
        else:
            cu.append((t.GetNetname(), LineString([mm(t.GetStart()), mm(t.GetEnd())]).buffer(K.ToMM(t.GetWidth()) / 2),
                       b0.GetLayerName(t.GetLayer()), None))
    holes = [(d['x'], d['y'], d['hole']) for d in bd.pads if d['hole']]
    from shapely import STRtree
    tree = STRtree([g for _, g, _, _ in cu])
    frozen = shapes(items)
    planes = f0['planes']

    def clear(x, y, net):
        v = Point(x, y)
        if not (VR + FO.EDGE <= x <= spec.W - VR - FO.EDGE and VR + FO.EDGE <= y <= spec.H - VR - FO.EDGE):
            return False
        if any(math.hypot(x - hx, y - hy) < hr + FO.DRILL / 2 + FO.HOLE_GAP for hx, hy, hr in holes):
            return False
        for k in tree.query(v, predicate='dwithin', distance=VR + 1.1):
            n, g, lay, i = cu[k]
            if n != net and g.distance(v) < VR + pair(net, n) - 1e-6:
                return False
        return True
    closed, also = [], []
    for d in bd.pads:
        n = d['net']
        if not n or n in planes or M.short(n).startswith('unconnected-') or 'F' not in d['poly'] or d['hole']:
            continue
        c = d['poly']['F'].centroid
        hits = sorted({f"{fn} {lay}" for fn, g, lay in frozen if M.short(n) != fn and g.distance(c) < VR + pair(n, fn) - 1e-6})
        if not hits:
            continue
        row = f"{d['ref']}.{d['num']} {M.short(n)}: {', '.join(hits)}"
        (closed if clear(c.x, c.y, n) else also).append(row)

    mj = json.load(open(Path(trial) / 'meter.json'))
    open_nets = set(mj['krt'].get('open', []))
    lanes = {(r, num): g for r, num, net, g in M.pin_lanes(bd)}
    beside = {}
    for d in bd.pads:
        if M.short(d['net']) not in open_nets or (d['ref'], d['num']) not in lanes:
            continue
        c = d['poly']['F'].centroid
        lane = lanes[(d['ref'], d['num'])]
        beside[f"{d['ref']}.{d['num']} {M.short(d['net'])}"] = {
            'in_lane': sorted({f'{fn} {lay}' for fn, g, lay in frozen if fn != M.short(d['net']) and g.intersects(lane)}),
            'within_1.5_mm': sorted({f'{fn} {lay}' for fn, g, lay in frozen if g.distance(c) < M.LANE_LEN})}

    n_l, crossed0 = M.lanes_crossed(bd)
    _, crossed1 = M.lanes_crossed(bd, extra=[(fn, g) for fn, g, lay in frozen if lay in ('via', 'F.Cu')])
    return {
        '1_plane_pads': {'before': f"{len(f0['plane_pads_open'])} of {f0['plane_pads']} open",
                         'after': f"{len(f1['plane_pads_open'])} of {f1['plane_pads']} open",
                         'open_after': f1['plane_pads_open'], 'other_pads_changed': moved,
                         'fanout_vias': f"{sum(1 for d in f0['fr']['done'] if d.get('via'))} -> "
                                        f"{sum(1 for d in f1['fr']['done'] if d.get('via'))}"},
        '2_in_pad_sites_closed': closed, '2_already_closed_by_other_copper': also,
        '3_open_nets_beside': {'trial': str(trial), 'open': sorted(open_nets), 'pins': beside},
        'lanes': {'measured': n_l, 'crossed_before': crossed0, 'crossed_with_items': crossed1,
                  'new': sorted(set(crossed1) - set(crossed0)), 'gone': sorted(set(crossed0) - set(crossed1))},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('items')
    ap.add_argument('--trial', required=True, help="the source trial's folder (its meter.json: the open nets)")
    ap.add_argument('--pcb', help="the board they're to be frozen on (default the repo's)")
    ap.add_argument('--out')
    a = ap.parse_args()
    spec = build.load_spec('croi2')
    pcb = a.pcb or build.ROOT / 'hardware' / 'croi2' / f'{spec.NAME}.kicad_pcb'
    c = count(spec, pcb, json.load(open(a.items)), a.trial)
    if a.out:
        Path(a.out).write_text(json.dumps(c, indent=1) + '\n')
    print(json.dumps(c, indent=1))


if __name__ == '__main__':
    main()
