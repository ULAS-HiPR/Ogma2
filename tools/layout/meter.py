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

None of its copper is kept: it answers "will our pipeline route this placement", nothing more. The fanout keeps
clear of the board's scripted copper on every layer and of its rule areas; the fanned board must pass DRC before the
router starts, or the run is void (23 Nov). It ignores the shapes of the L3 islands (a rail's vias count as joined).
With --freerouting it also runs Freerouting 2.5.0, optimiser off, on the same fanned board, for a completion count.
"""
import argparse
import importlib.util
import json
import math
import os
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


def budget_keepouts(b, spec):
    """spec.BUDGET's areas as keep-out rule areas on the board (no tracks, no vias on their layers; pads and pours
    allowed), for the router; returns them as shapely polygons for the fanout, which places no via in any."""
    from shapely.geometry import LineString, box
    ox, oy = spec.ORIGIN
    polys = []
    for it in spec.BUDGET:
        g = box(*it['box']) if 'box' in it else LineString(it['path']).buffer(it['w'] / 2, quad_segs=4)
        z = K.ZONE(b)
        z.SetIsRuleArea(True)
        z.SetZoneName('BUDGET ' + it['name'])
        ls = K.LSET()
        for l in it['layers']:
            ls.AddLayer(b.GetLayerID(l))
        z.SetLayerSet(ls)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False)
        z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowFootprints(False)
        o = z.Outline(); o.NewOutline()
        for x, y in list(g.exterior.coords)[:-1]:
            o.Append(K.FromMM(x + ox), K.FromMM(y + oy))
        b.Add(z)
        polys.append(g)
    return polys


def plane_pads_open(b, origin, planes, fills):
    """The plane pads with no via and no drawn join to one (D-24Nov.15: a trial's result includes them). Per plane
    net, its pads, tracks, vias and the board's own outer-layer fills (`fills`: [(net, layer, polygon)], kept from
    before the planes go, such as the RF lines' ground pours) are joined where they touch on a shared layer; a group
    reaches the plane if it holds a via or a through-hole pad. Returns (pads counted, ['REF.PIN' open])."""
    import pcbnew as K
    from shapely import STRtree
    from shapely.geometry import LineString, Point, Polygon
    ox, oy = origin
    mm = lambda v: (K.ToMM(v.x) - ox, K.ToMM(v.y) - oy)
    ALL = None
    items = defaultdict(list)                       # net -> [(layers or ALL, shape, pad name or None, reaches)]
    for f in b.GetFootprints():
        for p in f.Pads():
            n = p.GetNetname()
            if n not in planes:
                continue
            tht = p.GetAttribute() in (K.PAD_ATTRIB_PTH,)
            for lid, lname in ((K.F_Cu, 'F.Cu'), (K.B_Cu, 'B.Cu')):
                if not p.IsOnLayer(lid):
                    continue
                ps = K.SHAPE_POLY_SET()
                p.TransformShapeToPolygon(ps, lid, 0, K.FromMM(0.005), K.ERROR_INSIDE)
                if not ps.OutlineCount():
                    continue
                o = ps.Outline(0)
                g = Polygon([mm(o.CPoint(i)) for i in range(o.PointCount())]).buffer(0.002)
                items[n].append((ALL if tht else (lname,), g, f'{f.GetReference()}.{p.GetNumber()}', tht))
                if tht:
                    break
    for t in b.GetTracks():
        n = t.GetNetname()
        if n not in planes:
            continue
        if t.Type() == K.PCB_VIA_T:
            items[n].append((ALL, Point(mm(t.GetPosition())).buffer(K.ToMM(t.GetWidth(K.F_Cu)) / 2), None, True))
        else:
            items[n].append(((b.GetLayerName(t.GetLayer()),),
                             LineString([mm(t.GetStart()), mm(t.GetEnd())]).buffer(K.ToMM(t.GetWidth()) / 2), None, False))
    for n, lname, g in fills:
        if n in planes:
            items[n].append(((lname,), g, None, False))
    counted, open_ = 0, []
    for n, its in items.items():
        parent = list(range(len(its)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        tree = STRtree([g for _, g, _, _ in its])
        for i, (li, gi, _, _) in enumerate(its):
            for j in tree.query(gi, predicate='intersects'):
                if j <= i:
                    continue
                lj = its[j][0]
                if li is ALL or lj is ALL or set(li) & set(lj):
                    parent[find(i)] = find(j)
        reach = {find(i) for i, it in enumerate(its) if it[3]}
        for i, (_, _, name, _) in enumerate(its):
            if name:
                counted += 1
                if find(i) not in reach:
                    open_.append(name)
    return counted, sorted(set(open_))


def _tree_rss_mb(pid):
    """Resident memory of a process and all its descendants, MB, from /proc."""
    kids, rss = {}, 0
    for d in os.listdir('/proc'):
        if d.isdigit():
            try:
                with open(f'/proc/{d}/stat') as f:
                    kids.setdefault(int(f.read().rsplit(')', 1)[1].split()[1]), []).append(int(d))
            except OSError:
                pass
    todo = [pid]
    while todo:
        q = todo.pop()
        try:
            with open(f'/proc/{q}/status') as f:
                rss += next((int(l.split()[1]) for l in f if l.startswith('VmRSS:')), 0)
        except OSError:
            pass
        todo += kids.get(q, [])
    return round(rss / 1024)


STEP = ('Loading ', 'Routing ', '[', 'MPS', 'Building ', 'Pre-computing', '  Reconciliation', '  Finer-grid',
        'Writing ', 'Phase ', 'Final ')


def run_traced(cmd, cwd, log_path, trace_path, timeout=None):
    """Run a router pass with its resident memory (the process and its children) sampled each second against the
    number of lines its log has reached (D-24Nov.15). Writes the samples to trace_path (seconds, MB, log line) and
    returns (rc, peak): peak is {mb, at_s, log_line, step}, step the last line before it that starts a router step."""
    t0, peak, nlines, off = time.time(), (0, 0.0, 0), 0, 0
    with open(log_path, 'w') as log, open(trace_path, 'w') as tr:
        tr.write('seconds\trss_mb\tlog_line\n')
        p = subprocess.Popen(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        rc = None
        while rc is None:
            try:
                rc = p.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                if timeout is not None and time.time() - t0 > timeout:
                    p.kill()
                    p.wait()
                    rc = 'timeout'
            mb = _tree_rss_mb(p.pid) if rc is None else 0
            with open(log_path, 'rb') as f:              # count the log's new lines since the last sample
                f.seek(off)
                chunk = f.read()
            off += len(chunk)
            nlines += chunk.count(b'\n')
            if rc is None:
                tr.write(f'{time.time() - t0:.0f}\t{mb}\t{nlines}\n')
                tr.flush()
                if mb > peak[0]:
                    peak = (mb, round(time.time() - t0), nlines)
    lines = open(log_path, errors='replace').read().splitlines()
    step = next((l.strip()[:160] for l in reversed(lines[:peak[2]]) if l.startswith(STEP)), '')
    return rc, {'mb': peak[0], 'at_s': peak[1], 'log_line': peak[2], 'step': step}


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


def drc(pcb, out_json, twin_of=None):
    """KiCad DRC's errors by type, less those between a fire-logic net and its own twin (the waiver's model, main())."""
    import re
    subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--severity-error', '--units', 'mm', '-o', str(out_json), str(pcb)],
                   capture_output=True, text=True)
    d = json.loads(Path(out_json).read_text())
    by = defaultdict(int)
    for v in d.get('violations', []):
        if twin_of:
            nets = {M.short(m.group(1)) for i in v['items'] for m in [re.search(r'\[([^\]]*)\]', i['description'])] if m}
            if nets and any(n in twin_of for n in nets) and len({twin_of.get(n, n) for n in nets}) == 1:
                by['(the waiver model: a net against its twin, dropped)'] += 1
                continue
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
    ap.add_argument('--layers', nargs='+', help='the router\'s layers (default the spec\'s ROUTER_LAYERS, else F.Cu and B.Cu)')
    ap.add_argument('--classes', nargs='+', help='route only these net classes, in PASS_ORDER (default all)')
    ap.add_argument('--via-in-pad', action='store_true',
                    help='each plane pad\'s via in the pad itself where it fits (JLC\'s plated-over filled via)')
    ap.add_argument('--krt-minutes', type=float, help='stop the router after this long; a pass cut off leaves its nets open')
    ap.add_argument('--rails-as-tracks', action='store_true',
                    help='GND is the only plane: the rails are routed as tracks (a six-layer plan with no power layer)')
    ap.add_argument('--waive-fire-logic', action='store_true',
                    help='model the fire-logic waiver (D-22Nov.26, D-23Nov.8, D-23Nov.13) as DRC applies it: on the scratch '
                         "copy, fire logic wholly inside a part's escape area moves to a twin net at the class's 0.2 mm, "
                         'the rest keeps 0.5 mm (those nets are not routed here)')
    ap.add_argument('--net-clearance', action='append', default=[], metavar='NET=MM',
                    help="trial: tell the router this net's clearance instead of its class's (e.g. GND=0.15)")
    ap.add_argument('--krt-args', default='',
                    help="extra router flags for every pass, one string (stage D's knobs), e.g. '--layer-costs 1 1 1'")
    ap.add_argument('--plane-rails', nargs='+', default=[],
                    help='with --rails-as-tracks: these rails stay planes (e.g. FLIGHT_3V3 as a whole L5 plane)')
    ap.add_argument('--no-finer-lap', action='store_true',
                    help="skip the router's final whole-board lap at half the grid (krt_wrap.py; D-24Nov.15)")
    ap.add_argument('--budget', action='store_true',
                    help="the budget run (stage C/D review, call 9): spec.BUDGET's areas become keep-outs for tracks and "
                         'vias on their layers, for the fanout and the router alike')
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    b = K.LoadBoard(a.pcb)
    # the board's copper planes go (D-23Nov.30): the meter models a plane as before, a plane pad's via counting as
    # joined, and a fill saved before the fanout's vias would clash with them
    fills = []                                     # outer-layer fills, kept for the plane-pad count (D-24Nov.15)
    for z in b.Zones():
        if z.GetIsRuleArea():
            continue
        for lid, lname in ((K.F_Cu, 'F.Cu'), (K.B_Cu, 'B.Cu')):
            if z.IsOnLayer(lid) and z.HasFilledPolysForLayer(lid):
                from shapely.geometry import Polygon as _P
                ps = z.GetFilledPolysList(lid)
                for i in range(ps.OutlineCount()):
                    o = ps.Outline(i)
                    pts = [(K.ToMM(o.CPoint(j).x), K.ToMM(o.CPoint(j).y)) for j in range(o.PointCount())]
                    if len(pts) >= 3:
                        fills.append((z.GetNetname(), lname, pts))
    for z in [z for z in b.Zones() if not z.GetIsRuleArea()]:
        b.RemoveNative(z)                          # Remove() leaves a dead object in Zones(): a later read crashes
    length = a.length or float(round(K.ToMM(b.GetBoardEdgesBoundingBox().GetHeight())))
    spec, hw = load_spec(a.board, length)
    a.layers = a.layers or getattr(spec, 'ROUTER_LAYERS', ['F.Cu', 'B.Cu'])
    waived, twin_of = {}, {}
    if a.waive_fire_logic:
        # the waiver as DRC applies it (D-22Nov.26, D-23Nov.8, D-23Nov.13): fire logic wholly inside a part's escape
        # area keeps 0.2 mm, elsewhere 0.5. Each fire-logic net's pads, tracks and vias that sit wholly inside an area
        # move to a twin net at the class's 0.2 mm, so the router keeps 0.2 mm from them and 0.5 mm from the rest of
        # the net. A twin touches its own net where the copper leaves the area; DRC's errors between a net and its own
        # twin are the model's, and drc() drops them.
        from shapely.geometry import LineString, Point, Polygon
        fl_cl = next(c['clearance'] for c in spec.NETCLASSES if c['name'] == 'FIRE_LOGIC')
        mm_ = K.ToMM
        areas = []
        for z in b.Zones():
            if z.GetIsRuleArea() and z.GetZoneName().endswith('_ESCAPE'):
                o = z.Outline()
                for k in range(o.OutlineCount()):
                    ol = o.Outline(k)
                    areas.append(Polygon([(mm_(ol.CPoint(q).x), mm_(ol.CPoint(q).y)) for q in range(ol.PointCount())]).buffer(1e-4))
        twins, moved = {}, defaultdict(list)

        def to_twin(item):
            n = item.GetNetname()
            if n not in twins:
                name = f'{M.short(n)}_WAIVED'
                ni = K.NETINFO_ITEM(b, name)
                b.Add(ni)
                twins[n], waived[name], twin_of[name] = ni, fl_cl, M.short(n)
            moved[n].append((item, item.GetNet()))
            item.SetNet(twins[n])
        is_fl = lambda n: M.net_class(n, spec.PATTERNS) == 'FIRE_LOGIC'
        for f in b.GetFootprints():
            for p in f.Pads():
                if is_fl(p.GetNetname()):
                    ps = K.SHAPE_POLY_SET()
                    p.TransformShapeToPolygon(ps, K.F_Cu if p.IsOnLayer(K.F_Cu) else K.B_Cu, 0, K.FromMM(0.005), K.ERROR_INSIDE)
                    if ps.OutlineCount():
                        ol = ps.Outline(0)
                        g = Polygon([(mm_(ol.CPoint(q).x), mm_(ol.CPoint(q).y)) for q in range(ol.PointCount())])
                        if any(ar.contains(g) for ar in areas):
                            to_twin(p)
        for t in list(b.GetTracks()):
            if is_fl(t.GetNetname()):
                if t.Type() == K.PCB_VIA_T:
                    c = t.GetPosition()
                    g = Point(mm_(c.x), mm_(c.y)).buffer(mm_(t.GetWidth(K.F_Cu)) / 2, 16)
                else:
                    g = LineString([(mm_(t.GetStart().x), mm_(t.GetStart().y)), (mm_(t.GetEnd().x), mm_(t.GetEnd().y))]).buffer(mm_(t.GetWidth()) / 2, 16)
                if any(ar.contains(g) for ar in areas):
                    to_twin(t)
        # a net with every pad inside an area keeps its own name throughout: KiCad would give the copper between the
        # areas the twin's net when it saves the board (STAGE_ELIGIBLE, U6001 to U6502), so it keeps 0.5 mm there too
        for n, items in moved.items():
            if not any(p.GetNetname() == n for f in b.GetFootprints() for p in f.Pads()):
                for item, ni in items:
                    item.SetNet(ni)
                name = twins[n].GetNetname()
                waived.pop(name, None); twin_of.pop(name, None)
    bd = M.BoardData(b, spec.ORIGIN, (spec.W, spec.H))
    planes = M.plane_nets(bd, set(spec.RAILS))
    if a.rails_as_tracks:
        planes = {n: l for n, l in planes.items() if M.short(n) == 'GND' or M.short(n) in a.plane_rails}
    allsig = sorted(M.signal_nets(bd, planes))
    # RF lines are scripted in stage C on L1 with no via (D-21Nov.25, D-22Nov.16): left out of the route
    rf = [n for n in allsig if M.net_class(n, spec.PATTERNS) == 'RF50']
    sig = [n for n in allsig if n not in rf and M.short(n) not in twin_of]     # fire logic's twins are drawn, not routed
    # each net's clearance as KiCad will check it: its class's, and 0.5 mm for fire copper (spec.DRU), which the
    # router can't read from the custom rule
    pair = FO.clearances(spec)
    net_cl = {n: round(pair(n, '') - FO.EPS, 3) for n in bd.by_net if n}
    net_cl.update(waived)
    for kv in a.net_clearance:                 # trial overrides, by short net name
        k_, v_ = kv.split('=')
        for n in net_cl:
            if M.short(n) == k_:
                net_cl[n] = float(v_)
    if a.fire_logic_clearance is not None:      # trial: the fire rule on the logic class relaxed to this
        for n in net_cl:
            if M.net_class(n, spec.PATTERNS) == 'FIRE_LOGIC':
                net_cl[n] = a.fire_logic_clearance
    no_via = budget_keepouts(b, spec) if a.budget else []
    t0 = time.time()
    ex = FO.existing(b, spec.ORIGIN)            # stage C's scripted copper: its pads need no fanout via
    fr = FO.plan(bd, planes, spec, in_pad=a.via_in_pad, existing=ex, no_via=no_via)
    FO.apply(b, spec.ORIGIN, fr)
    from shapely.geometry import Polygon as _P
    ox_, oy_ = spec.ORIGIN
    pp_n, pp_open = plane_pads_open(b, spec.ORIGIN, planes,
                                    [(n, l, _P([(x - ox_, y - oy_) for x, y in pts]).buffer(0)) for n, l, pts in fills])
    fan = out / 'fanned.kicad_pcb'
    K.SaveBoard(str(fan), b)
    for ext in ('kicad_pro', 'kicad_dru'):
        src = hw / f'{spec.NAME}.{ext}'
        if src.exists():
            shutil.copy(src, out / f'fanned.{ext}')
    if twin_of:                                  # the twins stay FIRE_LOGIC for DRC, so its waiver rule reads them
        pro = json.loads((out / 'fanned.kicad_pro').read_text())
        pro['net_settings'].setdefault('netclass_patterns', []).append({'netclass': 'FIRE_LOGIC', 'pattern': '*_WAIVED'})
        (out / 'fanned.kicad_pro').write_text(json.dumps(pro, indent=2) + '\n')
    # the input board and the meter's own steps (the waiver, the keep-outs, the fanout) must leave a board DRC passes
    # before any routing; an error here is the input's or the instrument's, so the run is void and the router never
    # starts. Planted test (23 Nov): a GND via 0.15 mm from OUTPUT1_LOW on L6 voids the run. (A via planted on the
    # track itself doesn't test it: KiCad gives a free via the net of the track it sits on when it saves the board.)
    fan_drc = drc(fan, out / 'fanned-drc.json', twin_of)
    dropped_fan = fan_drc.pop('(the waiver model: a net against its twin, dropped)', 0)
    rep = {'board': a.pcb, 'length_mm': length, 'copper_layers': b.GetCopperLayerCount(), 'router_layers': a.layers,
           'classes': a.classes or 'all', 'via_in_pad': a.via_in_pad, 'krt_minutes': a.krt_minutes,
           'no_finer_lap': a.no_finer_lap,
           'rails_as_tracks': a.rails_as_tracks, 'plane_rails': a.plane_rails, 'krt_args': a.krt_args,
           'fire_logic_twins': sorted(waived), 'net_clearance_overrides': a.net_clearance,
           'plane_nets': {M.short(n): l for n, l in sorted(planes.items())},
           'left_out': {'rf_scripted_in_stage_c': [M.short(n) for n in rf]},
           'fire_logic_clearance': a.fire_logic_clearance if a.fire_logic_clearance is not None else 'the 0.5 mm fire rule',
           'scripted': {'vias': len(ex['vias']), 'tracks': len(ex['tracks']), 'pads_joined': len(ex['joined'])},
           'fanout': {'pads': len(fr['done']) + len(fr['failed']), 'vias': sum(1 for d in fr['done'] if d.get('via')),
                      'by_group': sum(1 for d in fr['done'] if d.get('by_group')),
                      'misses': [f"{d['ref']}.{d['num']}" for d in fr['failed']],
                      'in_pad': sum(1 for d in fr['done'] if d.get('via') and d['stub'] is None),
                      'seconds': round(time.time() - t0, 1)},
           'plane_pads': {'pads': pp_n, 'open': pp_open},
           'ignores': 'the L3 islands\' shapes',
           'budget': [it['name'] for it in spec.BUDGET] if a.budget else None,
           'fanned_drc_errors': fan_drc, 'fanned_drc_twin_errors_dropped': dropped_fan}
    if fan_drc:
        rep['VOID'] = 'the board fails DRC after the fanout, before routing (%s): an input or instrument error; no count' % fan_drc
        (out / 'meter.json').write_text(json.dumps(rep, indent=1) + '\n')
        print(json.dumps({'VOID': rep['VOID'], 'fanout': {kk: rep['fanout'][kk] for kk in ('pads', 'vias', 'seconds')}}, indent=1))
        sys.exit(3)
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
                     '--json-out', str(out / f'krt-pass{k}.json')] + (['--quick', a.quick] if a.quick != '0' else []) \
                + a.krt_args.split()
            cmd = [KRT_PY] + ([str(HERE / 'krt_wrap.py')] if a.no_finer_lap else []) + \
                ['py_router/route.py', str(src), str(dst), '--nets'] + [glob_escape(n) for n in nets] + flags
            tp = time.time()
            left = None if a.krt_minutes is None else a.krt_minutes * 60 - (tp - t1)
            if left is not None and left <= 0:
                runs.append({'class': cls, 'nets': len(nets), 'rc': 'not started: out of time', 'seconds': 0})
                continue
            rc, mem = run_traced(cmd, str(KRT), out / f'krt-pass{k}.log', out / f'mem-pass{k}.tsv', timeout=left)
            runs.append({'class': cls, 'nets': len(nets), 'rc': rc, 'seconds': round(time.time() - tp, 1),
                         'memory_peak': mem})
            if rc == 0 and dst.exists():
                src = dst
        routed = out / 'routed.kicad_pcb'
        shutil.copy(src, routed)
        for ext in ('kicad_pro', 'kicad_dru'):
            if (out / f'fanned.{ext}').exists():
                shutil.copy(out / f'fanned.{ext}', out / f'routed.{ext}')
        rcs = [x['rc'] for x in runs]
        # the first pass that didn't finish cleanly: a timeout, an error, or a kill (negative, e.g. -9 when the kernel
        # ends it for memory); its nets stay open, so the count is void, not a result
        rep['krt'] = {'rc': next((x for x in rcs if x != 0), 0), 'seconds': round(time.time() - t1, 1),
                      'peak_rss_mb': round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024),
                      'passes': runs, 'cmd_flags': flags}
        routed_sig = {n for n in sig if not a.classes or M.net_class(n, spec.PATTERNS) in a.classes}
        rep['krt'].update(summarise(routed, spec, routed_sig, sum(1 for d in fr['done'] if d.get('via')) + len(ex['vias']), 'krt'))
        rep['krt']['drc_errors'] = drc(routed, out / 'routed-drc.json', twin_of)
        by = defaultdict(lambda: [0, 0])
        for n in sig:
            if a.classes and M.net_class(n, spec.PATTERNS) not in a.classes:
                continue
            c = M.net_class(n, spec.PATTERNS)
            by[c][1] += 1
            if M.short(n) in rep['krt']['open']:
                by[c][0] += 1
        rep['krt']['open_by_class'] = {c: f'{o} of {n}' for c, (o, n) in by.items()}
        rep['krt']['open_by_class']['PLANE_PADS'] = f'{len(pp_open)} of {pp_n}'   # D-24Nov.15: no via, no drawn join
        rep['krt']['plane_pads_open'] = pp_open
        if rep['krt']['rc']:     # a pass that didn't finish: its nets were never tried, so the counts mean nothing
            for x in ('nets_open', 'nets_open_pct', 'connections_open', 'open', 'open_by_class', 'nets_open_by_band'):
                rep['krt'].pop(x, None)
            rep['krt']['VOID'] = 'a router pass did not finish (rc %s); no count is a result' % rep['krt']['rc']
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
            frrep.update(summarise(frb, spec, set(sig), sum(1 for d in fr['done'] if d.get('via')), 'freerouting'))
            widths = [K.ToMM(t.GetWidth()) for t in bf.GetTracks() if t.Type() == K.PCB_TRACE_T]
            frrep['min_track_mm'] = round(min(widths), 3) if widths else None
        rep['freerouting'] = frrep
    (out / 'meter.json').write_text(json.dumps(rep, indent=1) + '\n')
    k = rep.get('krt', {})
    print(json.dumps({x: k.get(x) for x in ('rc', 'VOID', 'seconds', 'peak_rss_mb', 'signal_nets', 'nets_open', 'nets_open_pct',
                                           'connections_open', 'router_vias', 'track_mm', 'length_ratio', 'drc_errors',
                                           'open_by_class', 'nets_open_by_band')}
                     | {'fanout': {kk: rep['fanout'][kk] for kk in ('pads', 'vias', 'seconds')},
                        'freerouting': {kk: v for kk, v in rep.get('freerouting', {}).items() if kk not in ('open',)}}, indent=1))


if __name__ == '__main__':
    main()
