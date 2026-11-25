"""freeze_fanout.py REF [REF ...] --trial TRIAL --out OUT.json: the routing trial's plane vias for these parts, as spec
items to freeze (D-24Nov.17: U201's and U401's, so their escapes are designed against vias that don't move), and
what they close, counted before they're frozen (D-24Nov.15, rule 1).

    python3 /work/tools/layout/freeze_fanout.py U201 U401 --trial /root/layers/d25-e532c976 --out /cap/x.json

Run in the KiCad chroot on the repo's board (or --pcb). meter.fan_out with spec.TRIAL_FANOUT plans the fan-out as the trial
does. The items: each of the parts' plane pads' own via and stub (dict(net, via, d, drill), dict(net, layer, w,
path), board mm), and for a pad the fan-out serves through its drawn group (D-24Nov.16: a supply pin drawn to its
capacitor), the via and stub the fan-out gives that group. What they close: closes.py's count.
OUT.json holds the items; OUT-count.json the count.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build                                     # noqa: E402
import closes                                    # noqa: E402
import meter                                     # noqa: E402
import pcbnew as K                               # noqa: E402
from engine import fanout as FO                  # noqa: E402
from engine import metrics as M                  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('refs', nargs='+')
    ap.add_argument('--trial', required=True, help="the source trial's folder (its meter.json: the open nets)")
    ap.add_argument('--out', required=True)
    ap.add_argument('--pcb', help="the board (default the repo's)")
    a = ap.parse_args()
    spec = build.load_spec('croi2')
    pcb = a.pcb or build.ROOT / 'hardware' / 'croi2' / f'{spec.NAME}.kicad_pcb'
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
    skip = set(keys) | {k for k in done0 if k[0] in refs}
    count = {'parts': sorted(refs), 'pads_served': len(served), 'vias': sum(1 for it in items if 'via' in it),
             'stubs': sum(1 for it in items if 'path' in it),
             'in_pad': sum(1 for k in keys if not done0[k].get('stub')),
             'by_group_vias_at': sorted(f'{k[0]}.{k[1]}' for k in keys if k[0] not in refs)}
    count.update(closes.count(spec, pcb, items, a.trial, skip))
    Path(a.out).write_text(json.dumps(items, indent=1) + '\n')
    Path(a.out).with_name(Path(a.out).stem + '-count.json').write_text(json.dumps(count, indent=1) + '\n')
    print(json.dumps(count, indent=1))


if __name__ == '__main__':
    main()
