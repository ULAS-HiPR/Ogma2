"""freeze_fanout.py REF [REF ...] --trial TRIAL --out OUT.json: the routing trial's plane vias for these parts, as spec
items to freeze (D-24Nov.17: U201's and U401's, so their escapes are designed against vias that don't move), and
what they close, counted before they're frozen (D-24Nov.15, rule 1).

    python3 /work/tools/layout/freeze_fanout.py U201 U401 --trial /root/layers/d25-e532c976 --out /cap/x.json

Run in the KiCad chroot on the repo's board. meter.fan_out with spec.TRIAL_FANOUT plans the fan-out as the trial
does. The items: each of the parts' plane pads' own via and stub (dict(net, via, d, drill), dict(net, layer, w,
path), board mm), and for a pad the fan-out serves through its drawn group (D-24Nov.16: a supply pin drawn to its
capacitor), the via and stub the fan-out gives that group. What they close:
1. plane pads: the fan-out run again with them drawn; the pads open, and every other pad whose via moved or went;
2. in-pad via sites: each connected pad off the planes whose via site (its centre, Ø0.45 mm) clears the board's
   copper without them and not with them;
3. the source trial's open nets: for each of their fine-pitch pins, the items in its lane or within a lane's length
   of it;
and the lane check with them in (engine/metrics.lanes_crossed), against the board's own.
OUT.json holds the items; OUT-count.json the count.
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('refs', nargs='+')
    ap.add_argument('--trial', required=True, help="the source trial's folder (its meter.json: the open nets)")
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    spec = build.load_spec('croi2')
    pcb = build.ROOT / 'hardware' / 'croi2' / f'{spec.NAME}.kicad_pcb'
    refs = set(a.refs)

    # the trial's fan-out on the repo's board, and the parts' share of it
    f0 = meter.fan_out(K.LoadBoard(str(pcb)), spec, **spec.TRIAL_FANOUT)
    done0 = {(d['ref'], d['num']): d for d in f0['fr']['done']}
    group = f0['existing']['group']
    by_group = {}
    for k, d in done0.items():
        if d.get('via') and k in group:
            by_group[group[k]] = k
    keys, items = [], []
    for k, d in sorted(done0.items()):
        if k[0] not in refs:
            continue
        src = k if d.get('via') else by_group.get(group.get(k))
        if src is None:
            sys.exit(f'{k[0]}.{k[1]}: no via of its own or its group')
        if src in keys:
            continue
        keys.append(src)
        s = done0[src]
        net = M.short(s['net'])
        if s.get('stub'):
            (x0, y0), (x1, y1) = s['stub']
            items.append(dict(net=net, layer='F.Cu', w=round(float(s.get('stub_w', FO.STUB_W)), 3),
                              path=[(round(float(x0), 4), round(float(y0), 4)), (round(float(x1), 4), round(float(y1), 4))],
                              pin=f'{src[0]}.{src[1]}'))
        items.append(dict(net=net, via=(round(float(s['via'][0]), 4), round(float(s['via'][1]), 4)), d=FO.VIA_D, drill=FO.DRILL,
                          pin=f'{src[0]}.{src[1]}'))
    served = {f'{k[0]}.{k[1]}' for k, d in done0.items() if k[0] in refs}

    # 1. plane pads: the fan-out again with the items drawn
    b1 = K.LoadBoard(str(pcb))
    draw(b1, spec, items)
    f1 = meter.fan_out(b1, spec, **spec.TRIAL_FANOUT)
    done1 = {(d['ref'], d['num']): d for d in f1['fr']['done']}
    moved = []
    for k, d in sorted(done0.items()):
        if k in keys or k[0] in refs:
            continue
        e = done1.get(k)
        if e is None:
            moved.append(f'{k[0]}.{k[1]}: now joined by the frozen copper')
        elif (d.get('via') and e.get('via') and math.dist(d['via'], e['via']) > 1e-3) or bool(d.get('via')) != bool(e.get('via')):
            moved.append(f"{k[0]}.{k[1]}: {d.get('via')} -> {e.get('via')}")

    # 2. in-pad via sites, without the items and with them
    b0 = K.LoadBoard(str(pcb))
    bd = M.BoardData(b0, spec.ORIGIN, (spec.W, spec.H))
    pair = FO.clearances(spec)
    ox, oy = spec.ORIGIN
    mm = lambda v: (K.ToMM(v.x) - ox, K.ToMM(v.y) - oy)
    cu = []                                          # (net, shape, layer): the board's copper
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

    def clear(x, y, net, own):
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
    for i, d in enumerate(bd.pads):
        n = d['net']
        if not n or n in planes or M.short(n).startswith('unconnected-') or 'F' not in d['poly'] or d['hole']:
            continue
        c = d['poly']['F'].centroid
        hits = sorted({f"{fn} {'via' if lay == 'via' else 'stub'}" for fn, g, lay in frozen
                       if g.distance(c) < VR + pair(n, fn) - 1e-6})
        if not hits:
            continue
        row = f"{d['ref']}.{d['num']} {M.short(n)}: {', '.join(hits)}"
        (closed if clear(c.x, c.y, n, i) else also).append(row)

    # 3. the source trial's open nets, at their fine-pitch pins
    mj = json.load(open(Path(a.trial) / 'meter.json'))
    open_nets = set(mj['krt'].get('open', []))
    lanes = {(r, num): g for r, num, net, g in M.pin_lanes(bd)}
    beside = {}
    for d in bd.pads:
        if M.short(d['net']) not in open_nets or (d['ref'], d['num']) not in lanes:
            continue
        c = d['poly']['F'].centroid
        lane = lanes[(d['ref'], d['num'])]
        beside[f"{d['ref']}.{d['num']} {M.short(d['net'])}"] = {
            'in_lane': sorted({f'{fn} {lay}' for fn, g, lay in frozen if g.intersects(lane)}),
            'within_1.5_mm': sorted({f'{fn} {lay}' for fn, g, lay in frozen if g.distance(c) < M.LANE_LEN})}

    # the lane check, the board's own and with the items in
    n_l, crossed0 = M.lanes_crossed(bd)
    _, crossed1 = M.lanes_crossed(bd, extra=[(fn, g) for fn, g, lay in frozen if lay in ('via', 'F.Cu')])
    count = {
        'parts': sorted(refs), 'pads_served': len(served), 'vias': sum(1 for it in items if 'via' in it),
        'stubs': sum(1 for it in items if 'path' in it), 'in_pad': sum(1 for k in keys if not done0[k].get('stub')),
        'by_group_vias_at': sorted(f'{k[0]}.{k[1]}' for k in keys if k[0] not in refs),
        '1_plane_pads': {'before': f"{len(f0['plane_pads_open'])} of {f0['plane_pads']} open",
                         'after': f"{len(f1['plane_pads_open'])} of {f1['plane_pads']} open",
                         'open_after': f1['plane_pads_open'], 'other_pads_changed': moved,
                         'fanout_vias': f"{sum(1 for d in f0['fr']['done'] if d.get('via'))} -> "
                                        f"{sum(1 for d in f1['fr']['done'] if d.get('via'))}"},
        '2_in_pad_sites_closed': closed, '2_already_closed_by_other_copper': also,
        '3_open_nets_beside': {'trial': str(a.trial), 'open': sorted(open_nets), 'pins': beside},
        'lanes': {'measured': n_l, 'crossed_before': crossed0, 'crossed_with_items': crossed1,
                  'new': sorted(set(crossed1) - set(crossed0))},
    }
    Path(a.out).write_text(json.dumps(items, indent=1) + '\n')
    Path(a.out).with_name(Path(a.out).stem + '-count.json').write_text(json.dumps(count, indent=1) + '\n')
    print(json.dumps(count, indent=1))


if __name__ == '__main__':
    main()
