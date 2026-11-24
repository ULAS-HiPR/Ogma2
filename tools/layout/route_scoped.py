"""route_scoped.py FANNED NET [NET ...] --out OUT.json: route a few nets by KiCadRoutingTools, to be frozen as data in
spec.py (D-24Nov.13, call 3: FLIGHT_NRST, GNSS_TX and COMMS_SWDIO drawn round the frozen fire logic).

    python3 /work/tools/layout/route_scoped.py /root/layers/<trial>/fanned.kicad_pcb GNSS_TX ... --out /cap/x.json

Run in the KiCad chroot. FANNED is a routing trial's board after its plane fan-out (meter.py), so the scripted nets
keep clear of the fan-out's vias; its net-clearances.json (beside it) gives the router the trial's clearances, fire
copper's 0.5 mm among them. Every other net's fine-pitch pin lanes (engine/metrics.pin_lanes, D-24Nov.11) become L1
keep-outs, so a net leaves its own pins square and crosses no other pin's lane. The router runs as the trial's
does (meter.py), on L1, L3 and L6 unless --layers says otherwise, at the trial's half grid (0.05 mm). Works on a
copy in /root/scoped; writes the nets' new copper as spec items: dict(net, layer, w, path) and dict(net, via, d,
drill), board mm.
"""
import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build                               # noqa: E402
from engine import metrics as M            # noqa: E402
import pcbnew as K                         # noqa: E402

KRT, KRT_PY = Path('/krt'), '/opt/kipy/bin/python'
WORK = Path('/root/scoped')


def glob_escape(n):
    return ''.join(f'[{c}]' if c in '[]*?' else c for c in n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fanned')
    ap.add_argument('nets', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--grid', default='0.05')
    ap.add_argument('--layers', nargs='+', default=['F.Cu', 'In2.Cu', 'B.Cu'])
    a = ap.parse_args()
    spec = build.load_spec('croi2')
    ox, oy = spec.ORIGIN
    src = Path(a.fanned)
    WORK.mkdir(exist_ok=True)
    for ext in ('kicad_pro', 'kicad_dru'):
        if src.with_suffix('.' + ext).exists():
            shutil.copy(src.with_suffix('.' + ext), WORK / f'in.{ext}')
    b = K.LoadBoard(str(src))
    full = {M.short(str(n)): str(n) for n in b.GetNetsByName().keys() if str(n)}
    want = set(a.nets)
    before = {(M.short(t.GetNetname()), t.GetClass(), t.GetLayer(), t.GetStart().x, t.GetStart().y, t.GetEnd().x,
               t.GetEnd().y) for t in b.GetTracks() if M.short(t.GetNetname()) in want}
    # other nets' lanes as L1 keep-outs (no tracks, no vias)
    bd = M.BoardData(b, spec.ORIGIN, (spec.W, spec.H))
    n_ko = 0
    for ref, num, net, g in M.pin_lanes(bd):
        if net in want:
            continue
        z = K.ZONE(b)
        z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowFootprints(False)
        z.SetLayer(K.F_Cu); z.SetZoneName(f'LANE_{ref}_{num}')
        o = z.Outline(); o.NewOutline()
        for x, y in list(g.exterior.coords)[:-1]:
            o.Append(K.FromMM(x + ox), K.FromMM(y + oy))
        b.Add(z)
        n_ko += 1
    b.Save(str(WORK / 'in.kicad_pcb'))
    netcl = src.parent / 'net-clearances.json'
    cmd = [KRT_PY, 'py_router/route.py', str(WORK / 'in.kicad_pcb'), str(WORK / 'out.kicad_pcb'),
           '--nets'] + [glob_escape(full[n]) for n in a.nets] + \
          ['--layers', *a.layers, '--grid-step', a.grid, '--no-bga-zones', '--escalation', 'off',
           '--json-out', str(WORK / 'krt.json')] + (['--net-clearances', str(netcl)] if netcl.exists() else [])
    with open(WORK / 'krt.log', 'w') as log:
        rc = subprocess.run(cmd, cwd=KRT, stdout=log, stderr=subprocess.STDOUT).returncode
    print(f'lanes as keep-outs: {n_ko}; router rc {rc}; log {WORK / "krt.log"}')
    if rc:
        sys.exit(rc)
    r = K.LoadBoard(str(WORK / 'out.kicad_pcb'))
    mm = lambda v: (round(K.ToMM(v.x) - ox, 4), round(K.ToMM(v.y) - oy, 4))
    segs, items = {}, []
    for t in r.GetTracks():
        n = M.short(t.GetNetname())
        if n not in want:
            continue
        key = (n, t.GetClass(), t.GetLayer(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y)
        if key in before:
            continue
        if t.GetClass() == 'PCB_VIA':
            items.append(dict(net=n, via=mm(t.GetPosition()), d=round(K.ToMM(t.GetWidth(K.F_Cu)), 3),
                              drill=round(K.ToMM(t.GetDrillValue()), 3)))
        elif t.GetClass() == 'PCB_ARC':
            sys.exit(f'{n}: an arc on {r.GetLayerName(t.GetLayer())}; the spec draws straight runs')
        else:
            segs.setdefault((n, r.GetLayerName(t.GetLayer()), round(K.ToMM(t.GetWidth()), 4)), []).append(
                (mm(t.GetStart()), mm(t.GetEnd())))
    for (n, lay, w), ss in sorted(segs.items()):      # chain each net's segments on a layer into runs
        ss = list(ss)
        while ss:
            run = list(ss.pop(0))
            grew = True
            while grew:
                grew = False
                for i, (p, q) in enumerate(ss):
                    if math.dist(p, run[-1]) < 1e-4:
                        run.append(q)
                    elif math.dist(q, run[-1]) < 1e-4:
                        run.append(p)
                    elif math.dist(q, run[0]) < 1e-4:
                        run.insert(0, p)
                    elif math.dist(p, run[0]) < 1e-4:
                        run.insert(0, q)
                    else:
                        continue
                    ss.pop(i); grew = True
                    break
            items.append(dict(net=n, layer=lay, w=w, path=run))
    js = json.load(open(WORK / 'krt.json'))
    print('routed', js.get('routed_single'), 'failed', js.get('failed_single'),
          'multipoint failed', [f.get('net_name') for f in js.get('failed_multipoint', [])])
    json.dump(items, open(a.out, 'w'), indent=1)
    print(len(items), 'items to', a.out)


if __name__ == '__main__':
    main()
