"""Routability meter (stage B2, burrito-stage-b2-brief.md step 1): our pipeline in miniature, on a scratch copy.

    python3 tools/layout/meter.py /work/hardware/croi2/Croi2.kicad_pcb --out /cap/meter/base [--freerouting]

1. A via for each surface-mount pad of a plane net (engine/fanout.py): GND to L2, and each rail of four loads or
   more to its L3 island (D-22Nov.15). Each pad its own via.
2. KiCadRoutingTools' route step (pinned at 1577fa3, /krt in the chroot) on L1 and L4 for every other net of two
   pads or more, at a 0.1 mm grid, in its placement-review mode (--quick 1: the main pass, no rescue laps).
   The layer test (decisions.md, Open: four layers or six) adds --layers, --classes, --via-in-pad and
   --krt-minutes; without them a run is the Stop 1b run.
3. Our own connectivity check per signal net, KiCad DRC by type, vias, each net's length against its rectilinear
   spanning tree, time and peak memory.

None of its copper is kept: it answers "will our pipeline route this placement", nothing more. It ignores rule areas
other than the mounting holes' (none are on the board yet), the copper stage C scripts by hand (RF, pairs, fire,
crystals, regulator loops) and the shapes of the L3 islands (a rail's vias count as joined).
With --freerouting it also runs Freerouting 2.5.0, optimiser off, on the same fanned board, for a completion count.
"""
import argparse
import importlib.util
import json
import math
import resource
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pcbnew as K                               # noqa: E402
from engine import fanout as FO                  # noqa: E402
from engine import metrics as M                  # noqa: E402

KRT = Path('/krt')
KRT_PY = '/opt/kipy/bin/python'
FR_JAR = Path('/lab/bin/freerouting-2.5.0.jar')
def cu_keys(b):
    """The board's copper layers, top to bottom, as connectivity keys: F, I1, I2, ..., B."""
    names = [b.GetLayerName(l) for l in b.GetEnabledLayers().CuStack()]
    return {n: ('F' if n == 'F.Cu' else 'B' if n == 'B.Cu' else 'I' + n[2:-3]) for n in names}
# the order the classes route in: power and fire copper first (stage C scripts these; here the router stands in),
# then the pairs, the small rails and last the Default nets, which are the router's in S5 (D-22Nov.17)
PASS_ORDER = ['SRC_6A', 'PYRO_RAIL', 'FIRE', 'LOGIC_FEED', 'FIRE_LOGIC', 'USB_DIFF', 'CAN_DIFF', 'RAIL_3V3', 'Default']


def load_spec(board, length):
    root = HERE.parents[1]
    s = importlib.util.spec_from_file_location('spec', root / 'hardware' / board / 'layout' / 'spec.py')
    spec = importlib.util.module_from_spec(s); s.loader.exec_module(spec)
    from build import stretch
    stretch(spec, length)
    return spec, root / 'hardware' / board


def glob_escape(n):
    return ''.join(f'[{c}]' if c in '[]*?' else c for c in n)


def connectivity(b, origin, nets):
    """For each net name: the number of separate copper groups its pads fall into (1 = complete)."""
    from shapely.geometry import LineString, Point, Polygon
    ox, oy = origin
    mm = lambda v: K.ToMM(v)
    items = defaultdict(list)          # net -> [(kind, layers, geom)]
    want = set(nets)
    CU = cu_keys(b)
    inner = [k for k in CU.values() if k.startswith('I')]
    for f in b.GetFootprints():
        for p in f.Pads():
            n = p.GetNetname()
            if n not in want:
                continue
            layers = {}
            for lay, nm in ((K.F_Cu, 'F'), (K.B_Cu, 'B')):
                if p.IsOnLayer(lay):
                    ps = K.SHAPE_POLY_SET()
                    p.TransformShapeToPolygon(ps, lay, 0, K.FromMM(0.01), K.ERROR_INSIDE)
                    if ps.OutlineCount():
                        o = ps.Outline(0)
                        g = Polygon([(mm(o.CPoint(i).x) - ox, mm(o.CPoint(i).y) - oy) for i in range(o.PointCount())]).buffer(0)
                        layers[nm] = g
            if p.GetAttribute() in (K.PAD_ATTRIB_PTH,):
                c = p.GetPosition()
                ring = Point(mm(c.x) - ox, mm(c.y) - oy).buffer(mm(max(p.GetSize().x, p.GetSize().y)) / 2)
                for k in inner:
                    layers.setdefault(k, ring)
            items[n].append(('pad', layers))
    for t in b.GetTracks():
        n = t.GetNetname()
        if n not in want:
            continue
        if t.Type() == K.PCB_VIA_T:
            c = t.GetPosition()
            g = Point(mm(c.x) - ox, mm(c.y) - oy).buffer(mm(t.GetWidth(K.F_Cu)) / 2, 8)
            items[n].append(('via', {l: g for l in CU.values()}))
        else:
            pts = [t.GetStart(), t.GetEnd()]
            if t.Type() == K.PCB_ARC_T:
                pts = [t.GetStart(), t.GetMid(), t.GetEnd()]
            g = LineString([(mm(q.x) - ox, mm(q.y) - oy) for q in pts]).buffer(mm(t.GetWidth()) / 2, 4)
            lay = CU.get(b.GetLayerName(t.GetLayer()))
            if lay:
                items[n].append(('track', {lay: g}))
    out = {}
    for n in nets:
        its = items.get(n, [])
        par = list(range(len(its)))
        def find(i):
            while par[i] != i:
                par[i] = par[par[i]]; i = par[i]
            return i
        for i in range(len(its)):
            for j in range(i + 1, len(its)):
                li, lj = its[i][1], its[j][1]
                if any(l in lj and li[l].distance(lj[l]) < 0.002 for l in li):
                    a, c = find(i), find(j)
                    if a != c:
                        par[a] = c
        pads = {find(i) for i, it in enumerate(its) if it[0] == 'pad'}
        out[n] = len(pads)
    return out


def rect_mst(pts):
    n = len(pts)
    if n < 2:
        return 0.0
    used = [False] * n; used[0] = True
    best = [abs(p[0] - pts[0][0]) + abs(p[1] - pts[0][1]) for p in pts]
    tot = 0.0
    for _ in range(n - 1):
        j = min((i for i in range(n) if not used[i]), key=lambda i: best[i])
        tot += best[j]; used[j] = True
        for i in range(n):
            if not used[i]:
                best[i] = min(best[i], abs(pts[i][0] - pts[j][0]) + abs(pts[i][1] - pts[j][1]))
    return tot


def drc(pcb, out_json):
    subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--severity-error', '--units', 'mm', '-o', str(out_json), str(pcb)],
                   capture_output=True, text=True)
    d = json.loads(Path(out_json).read_text())
    by = defaultdict(int)
    for v in d.get('violations', []):
        by[v['type']] += 1
    return dict(sorted(by.items()))


def summarise(pcb, spec, sig, fan_vias, tag):
    b = K.LoadBoard(str(pcb))
    groups = connectivity(b, spec.ORIGIN, sig)
    open_nets = sorted(M.short(n) for n, g in groups.items() if g > 1)
    open_conn = sum(g - 1 for g in groups.values() if g > 1)
    vias = sum(1 for t in b.GetTracks() if t.Type() == K.PCB_VIA_T) - fan_vias
    ln = defaultdict(float)
    for t in b.GetTracks():
        if t.Type() != K.PCB_VIA_T and t.GetNetname() in sig:
            ln[t.GetNetname()] += K.ToMM(t.GetLength())
    ox, oy = spec.ORIGIN
    pads = defaultdict(list)
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() in sig:
                c = p.GetPosition(); pads[p.GetNetname()].append((K.ToMM(c.x) - ox, K.ToMM(c.y) - oy))
    ratios = []
    for n, L in ln.items():
        base = rect_mst(pads[n])
        if base > 0.5 and groups.get(n, 2) == 1:
            ratios.append((L / base, M.short(n)))
    ratios.sort()
    r = [x for x, _ in ratios]
    bands = getattr(spec, 'BANDS', {})
    ob = defaultdict(int)
    for n in sig:
        if groups.get(n, 1) > 1:
            ys = [y for _, y in pads[n]]
            yc = sum(ys) / len(ys)
            ob[next((k for k, (y0, y1) in bands.items() if y0 <= yc < y1), '?')] += 1
    return {'tag': tag, 'signal_nets': len(sig), 'nets_open': len(open_nets), 'connections_open': open_conn,
            'nets_open_pct': round(100.0 * len(open_nets) / max(1, len(sig)), 1),
            'nets_open_by_band': dict(sorted(ob.items())), 'open': open_nets,
            'router_vias': vias, 'track_mm': round(sum(ln.values()), 1),
            'length_ratio': {'median': round(r[len(r) // 2], 2) if r else None,
                             'p90': round(r[int(len(r) * 0.9)], 2) if r else None,
                             'over_2_5': [n for x, n in ratios if x > 2.5]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pcb')
    ap.add_argument('--out', required=True)
    ap.add_argument('--board', default='croi2')
    ap.add_argument('--length', type=float)
    ap.add_argument('--quick', default='1')
    ap.add_argument('--freerouting', action='store_true')
    ap.add_argument('--fr-minutes', type=float, default=40)
    ap.add_argument('--fr-passes', type=int, default=40, help='Freerouting autorouter passes (it writes its result only at the end)')
    ap.add_argument('--skip-krt', action='store_true')
    ap.add_argument('--fire-logic-clearance', type=float,
                    help='route the FIRE_LOGIC class at this clearance instead of the 0.5 mm fire rule (a trial)')
    ap.add_argument('--layers', nargs='+', default=['F.Cu', 'B.Cu'], help='the router\'s layers (default L1 and L4)')
    ap.add_argument('--classes', nargs='+', help='route only these net classes, in PASS_ORDER (default all)')
    ap.add_argument('--via-in-pad', action='store_true',
                    help='each plane pad\'s via in the pad itself where it fits (JLC\'s plated-over filled via)')
    ap.add_argument('--krt-minutes', type=float, help='stop the router after this long; a pass cut off leaves its nets open')
    ap.add_argument('--rails-as-tracks', action='store_true',
                    help='GND is the only plane: the rails are routed as tracks (a six-layer plan with no power layer)')
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    b = K.LoadBoard(a.pcb)
    length = a.length or float(round(K.ToMM(b.GetBoardEdgesBoundingBox().GetHeight())))
    spec, hw = load_spec(a.board, length)
    bd = M.BoardData(b, spec.ORIGIN, (spec.W, spec.H))
    planes = M.plane_nets(bd, set(spec.RAILS))
    if a.rails_as_tracks:
        planes = {n: l for n, l in planes.items() if M.short(n) == 'GND'}
    allsig = sorted(M.signal_nets(bd, planes))
    # RF lines are scripted in stage C on L1 with no via (D-21Nov.25, D-22Nov.16): left out of the route
    rf = [n for n in allsig if M.net_class(n, spec.PATTERNS) == 'RF50']
    sig = [n for n in allsig if n not in rf]
    # each net's clearance as KiCad will check it: its class's, and 0.5 mm for fire copper (spec.DRU), which the
    # router can't read from the custom rule
    pair = FO.clearances(spec)
    net_cl = {n: round(pair(n, '') - FO.EPS, 3) for n in bd.by_net if n}
    if a.fire_logic_clearance is not None:      # trial: the fire rule on the logic class relaxed to this
        for n in net_cl:
            if M.net_class(n, spec.PATTERNS) == 'FIRE_LOGIC':
                net_cl[n] = a.fire_logic_clearance
    t0 = time.time()
    fr = FO.plan(bd, planes, spec, in_pad=a.via_in_pad)
    FO.apply(b, spec.ORIGIN, fr)
    fan = out / 'fanned.kicad_pcb'
    K.SaveBoard(str(fan), b)
    for ext in ('kicad_pro', 'kicad_dru'):
        src = hw / f'{spec.NAME}.{ext}'
        if src.exists():
            shutil.copy(src, out / f'fanned.{ext}')
    rep = {'board': a.pcb, 'length_mm': length, 'copper_layers': b.GetCopperLayerCount(), 'router_layers': a.layers,
           'classes': a.classes or 'all', 'via_in_pad': a.via_in_pad, 'krt_minutes': a.krt_minutes,
           'rails_as_tracks': a.rails_as_tracks,
           'plane_nets': {M.short(n): l for n, l in sorted(planes.items())},
           'left_out': {'rf_scripted_in_stage_c': [M.short(n) for n in rf]},
           'fire_logic_clearance': a.fire_logic_clearance if a.fire_logic_clearance is not None else 'the 0.5 mm fire rule',
           'fanout': {'pads': len(fr['done']) + len(fr['failed']), 'vias': len(fr['done']),
                      'misses': [f"{d['ref']}.{d['num']}" for d in fr['failed']], 'in_pad': sum(1 for d in fr['done'] if d['stub'] is None),
                      'seconds': round(time.time() - t0, 1)},
           'ignores': 'rule areas other than the mounting holes; the copper stage C scripts by hand; the L3 islands\' shapes'}
    if not a.skip_krt:
        # the router's clearance floor is the widest class in a call (KiCadRoutingTools' routing_config), so the
        # classes route in passes, widest copper first, each on top of the last, as D-22Nov.17 routes in passes
        (out / 'net-clearances.json').write_text(json.dumps(net_cl, indent=0))
        passes = []
        for cls in PASS_ORDER:
            if a.classes and cls not in a.classes:
                continue
            nets = [n for n in sig if M.net_class(n, spec.PATTERNS) == cls]
            if nets:
                passes.append((cls, nets))
        src, t1, runs = fan, time.time(), []
        for k, (cls, nets) in enumerate(passes, 1):
            dst = out / f'pass{k}.kicad_pcb'
            for ext in ('kicad_pro', 'kicad_dru'):
                if (out / f'fanned.{ext}').exists():
                    shutil.copy(out / f'fanned.{ext}', out / f'pass{k}.{ext}')
            flags = ['--layers', *a.layers, '--grid-step', '0.1', '--no-bga-zones', '--escalation', 'off',
                     '--net-clearances', str(out / 'net-clearances.json'),
                     '--json-out', str(out / f'krt-pass{k}.json')] + (['--quick', a.quick] if a.quick != '0' else [])
            cmd = [KRT_PY, 'py_router/route.py', str(src), str(dst), '--nets'] + [glob_escape(n) for n in nets] + flags
            tp = time.time()
            left = None if a.krt_minutes is None else a.krt_minutes * 60 - (tp - t1)
            if left is not None and left <= 0:
                runs.append({'class': cls, 'nets': len(nets), 'rc': 'not started: out of time', 'seconds': 0})
                continue
            try:
                with open(out / f'krt-pass{k}.log', 'w') as log:
                    r = subprocess.run(cmd, cwd=str(KRT), stdout=log, stderr=subprocess.STDOUT, timeout=left)
                rc = r.returncode
            except subprocess.TimeoutExpired:
                rc = 'timeout'
            runs.append({'class': cls, 'nets': len(nets), 'rc': rc, 'seconds': round(time.time() - tp, 1)})
            if rc == 0 and dst.exists():
                src = dst
        routed = out / 'routed.kicad_pcb'
        shutil.copy(src, routed)
        for ext in ('kicad_pro', 'kicad_dru'):
            if (out / f'fanned.{ext}').exists():
                shutil.copy(out / f'fanned.{ext}', out / f'routed.{ext}')
        rcs = [x['rc'] for x in runs]
        rep['krt'] = {'rc': next((x for x in rcs if not isinstance(x, int)), max(rcs, default=0)), 'seconds': round(time.time() - t1, 1),
                      'peak_rss_mb': round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024),
                      'passes': runs, 'cmd_flags': flags}
        routed_sig = {n for n in sig if not a.classes or M.net_class(n, spec.PATTERNS) in a.classes}
        rep['krt'].update(summarise(routed, spec, routed_sig, len(fr['done']), 'krt'))
        rep['krt']['drc_errors'] = drc(routed, out / 'routed-drc.json')
        by = defaultdict(lambda: [0, 0])
        for n in sig:
            if a.classes and M.net_class(n, spec.PATTERNS) not in a.classes:
                continue
            c = M.net_class(n, spec.PATTERNS)
            by[c][1] += 1
            if M.short(n) in rep['krt']['open']:
                by[c][0] += 1
        rep['krt']['open_by_class'] = {c: f'{o} of {n}' for c, (o, n) in by.items()}
    if a.freerouting:
        bf = K.LoadBoard(str(fan))
        bf.SetLayerType(K.In1_Cu, K.LT_POWER); bf.SetLayerType(K.In2_Cu, K.LT_POWER)
        dsn, ses = out / 'fr.dsn', out / 'fr.ses'
        assert K.ExportSpecctraDSN(bf, str(dsn))
        t2 = time.time()
        try:
            with open(out / 'fr.log', 'w') as log:              # streamed, so a run cut off by the timeout still shows its passes
                r = subprocess.run(['java', '-Xmx3g', '-jar', str(FR_JAR), '-de', str(dsn), '-do', str(ses),
                                    '--gui.enabled=false', '--usage_and_diagnostic_data.disable_analytics=true',
                                    '--router.optimizer.enabled=false', f'--router.autorouter.max_passes={a.fr_passes}'],
                                   stdout=log, stderr=subprocess.STDOUT, timeout=a.fr_minutes * 60)
            frrep = {'rc': r.returncode, 'seconds': round(time.time() - t2, 1), 'passes': a.fr_passes}
        except subprocess.TimeoutExpired:
            frrep = {'rc': 'timeout', 'seconds': round(time.time() - t2, 1), 'passes': a.fr_passes}
        if ses.exists():
            K.ImportSpecctraSES(bf, str(ses))
            frb = out / 'fr-routed.kicad_pcb'
            K.SaveBoard(str(frb), bf)
            frrep.update(summarise(frb, spec, set(sig), len(fr['done']), 'freerouting'))
            widths = [K.ToMM(t.GetWidth()) for t in bf.GetTracks() if t.Type() == K.PCB_TRACE_T]
            frrep['min_track_mm'] = round(min(widths), 3) if widths else None
        rep['freerouting'] = frrep
    (out / 'meter.json').write_text(json.dumps(rep, indent=1) + '\n')
    k = rep.get('krt', {})
    print(json.dumps({x: k.get(x) for x in ('rc', 'seconds', 'peak_rss_mb', 'signal_nets', 'nets_open', 'nets_open_pct',
                                           'connections_open', 'router_vias', 'track_mm', 'length_ratio', 'drc_errors',
                                           'open_by_class', 'nets_open_by_band')}
                     | {'fanout': {kk: rep['fanout'][kk] for kk in ('pads', 'vias', 'seconds')},
                        'freerouting': {kk: v for kk, v in rep.get('freerouting', {}).items() if kk not in ('open',)}}, indent=1))


if __name__ == '__main__':
    main()
