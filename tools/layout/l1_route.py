"""l1_route.py BOARD CONNS.json OUT.json: short pad-to-pad connections on L1 (crystal traces: AN2867 7.1, no via).

Run in the KiCad chroot: python3 /work/tools/layout/l1_route.py BOARD CONNS OUT. Other nets' fine-pitch pin lanes
(engine/metrics.pin_lanes, D-24Nov.11) are obstacles, so a line leaves its own pin square and crosses no other.

CONNS.json: [{"net": N, "a": [ref, pin], "b": [ref, pin], "w": 0.1}, ...] in order, then optional
{"gnd_via": [ref, pin]} entries: a GND via by that pad on a short stub (kept 0.1 mm off every pad, clear of all
copper). Each connection is a grid A* (0.025 mm, 8-connected) from pad centre to pad centre round every other net's
F.Cu copper: pads at 0.1 mm (DRC's JLC rule), tracks and vias at their class clearance (0.5 fire, 1.0 RF, 0.2 GND),
earlier connections included; zone fills are ignored (they refill). Writes spec-style items (board mm)."""
import sys, json, math, fnmatch, heapq
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build                                      # noqa: E402
import pcbnew as K                                # noqa: E402
from engine import metrics as M                   # noqa: E402
from shapely.geometry import LineString, Point, Polygon, box   # noqa: E402
from shapely.ops import unary_union               # noqa: E402

spec = build.load_spec('croi2')
OX, OY = spec.ORIGIN
TM = K.ToMM
CL = {c['name']: c['clearance'] for c in spec.NETCLASSES} if isinstance(spec.NETCLASSES[0], dict) else \
    {c.name: c.clearance for c in spec.NETCLASSES}
short = lambda n: n.rsplit('/', 1)[-1]
cls = lambda n: next((c for c, p in spec.PATTERNS if fnmatch.fnmatchcase(short(n), p)), 'Default')


def clear(n, mine):
    c = max(CL.get(cls(n), 0.1), CL.get(cls(mine), 0.1))
    if cls(n) in ('FIRE', 'FIRE_LOGIC', 'PYRO_RAIL'):
        c = max(c, 0.5)
    if cls(n) == 'RF50' and cls(mine) != 'GND':
        c = max(c, 1.0)
    return c


b = K.LoadBoard(sys.argv[1])
CONNS = json.load(open(sys.argv[2]))
DROP = set(CONNS[0]['drop']) if CONNS and 'drop' in CONNS[0] else set()   # nets whose drawn copper is redrawn
obs, pads = [], {}                          # (geom, net, kind)
for fp in b.GetFootprints():
    for p in fp.Pads():
        if not p.IsOnLayer(K.F_Cu):
            continue
        ps = K.SHAPE_POLY_SET()
        p.TransformShapeToPolygon(ps, K.F_Cu, 0, K.FromMM(0.005), K.ERROR_INSIDE)
        polys = []
        for i in range(ps.OutlineCount()):
            o = ps.Outline(i)
            pts = [(TM(o.CPoint(j).x) - OX, TM(o.CPoint(j).y) - OY) for j in range(o.PointCount())]
            if len(pts) >= 3:
                polys.append(Polygon(pts).buffer(0))
        g = unary_union(polys)
        obs.append((g, short(p.GetNetname()), 'pad'))
        pads[(fp.GetReference(), p.GetNumber())] = (g, short(p.GetNetname()))
for t in b.GetTracks():
    n = short(t.GetNetname())
    if n in DROP:
        continue
    if t.GetClass() == 'PCB_VIA':
        obs.append((Point(TM(t.GetPosition().x) - OX, TM(t.GetPosition().y) - OY).buffer(TM(t.GetWidth(K.F_Cu)) / 2), n, 'via'))
    elif t.GetLayer() == K.F_Cu:
        a, e = t.GetStart(), t.GetEnd()
        obs.append((LineString([(TM(a.x) - OX, TM(a.y) - OY), (TM(e.x) - OX, TM(e.y) - OY)]).buffer(TM(t.GetWidth()) / 2), n, 'cu'))
items, report = [], []
LANES = M.pin_lanes(M.BoardData(b, spec.ORIGIN, (spec.W, spec.H)))   # D-24Nov.11: other pins' lanes are closed


PAD = 0.11                                   # DRC's 0.1 mm, past the pad outlines' 0.005 mm approximation
EDGE = 0.2                                   # copper to the board edge (cucheck2, JLC)


def blocked_union(net, w, region, avoid=(), exempt=()):
    near = [(g, n, k) for g, n, k in obs if n != net and g.intersects(region)]
    parts = [g.buffer((PAD if k == 'pad' else clear(n, net)) + w / 2 - 1e-4) for g, n, k in near]
    for ref, num, n, g in LANES:                  # other nets' fine-pitch pin lanes (D-24Nov.11)
        if n != net and n not in exempt and g.intersects(region):   # exempt: a net drawn whole earlier in this run
            parts.append(g.buffer(w / 2))
    for r in avoid:                              # a part whose pads the line must not pass between: its courtyard
        c = b.FindFootprintByReference(r).GetCourtyard(K.F_Cu).BBox()
        parts.append(box(TM(c.GetX()) - OX, TM(c.GetY()) - OY, TM(c.GetRight()) - OX, TM(c.GetBottom()) - OY).buffer(w / 2))
    return unary_union(parts) if parts else None


def astar(a, c, net, w, step=0.025, margin=2.0, avoid=(), exempt=()):
    x0, x1 = min(a[0], c[0]) - margin, max(a[0], c[0]) + margin
    y0, y1 = min(a[1], c[1]) - margin, max(a[1], c[1]) + margin
    region = box(x0, y0, x1, y1)
    blk = blocked_union(net, w, region, avoid, exempt)
    own = unary_union([g for (r, p), (g, n) in pads.items() if n == net and g.intersects(region)])
    nx, ny = int((x1 - x0) / step) + 1, int((y1 - y0) / step) + 1
    memo = {}

    e = EDGE + w / 2

    def free(i, j):
        k = (i, j)
        if k not in memo:
            q = Point(x0 + i * step, y0 + j * step)
            inside = e <= q.x <= spec.W - e and e <= q.y <= spec.H - e        # the board edge's 0.2 mm
            memo[k] = inside and (blk is None or not blk.contains(q) or own.contains(q))
        return memo[k]
    si, sj = round((a[0] - x0) / step), round((a[1] - y0) / step)
    ti, tj = round((c[0] - x0) / step), round((c[1] - y0) / step)
    h = lambda i, j: math.hypot(i - ti, j - tj)
    openq, came, cost = [(h(si, sj), 0.0, (si, sj), None)], {}, {(si, sj): 0.0}
    while openq:
        f, g, cur, par = heapq.heappop(openq)
        if cur in came:
            continue
        came[cur] = par
        if cur == (ti, tj):
            break
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if not di and not dj:
                    continue
                nb = (cur[0] + di, cur[1] + dj)
                if not (0 <= nb[0] < nx and 0 <= nb[1] < ny) or nb in came or not free(*nb):
                    continue
                turn = 0.0 if par is None or (cur[0] - par[0], cur[1] - par[1]) == (di, dj) else 0.3
                ng = g + math.hypot(di, dj) + turn
                if ng < cost.get(nb, 1e9):
                    cost[nb] = ng
                    heapq.heappush(openq, (ng + h(*nb), ng, nb, cur))
    if (ti, tj) not in came:
        return None
    path, cur = [], (ti, tj)
    while cur is not None:
        path.append((round(x0 + cur[0] * step, 4), round(y0 + cur[1] * step, 4)))
        cur = came[cur]
    path.reverse()
    path[0], path[-1] = tuple(a), tuple(c)
    ok = lambda p, q: blk is None or not LineString([p, q]).difference(own).intersects(blk) if LineString([p, q]).difference(own).length else True
    simp, i = [path[0]], 0                      # straighten what stays clear
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1 and not ok(path[i], path[j]):
            j -= 1
        simp.append(path[j]); i = j
    return [(round(x, 3), round(y, 3)) for x, y in simp]


def via_near(pad, reach=1.5, step=0.05, d=0.45):
    g, net = pads[pad]
    c = g.centroid
    region = c.buffer(reach + 1)
    near = [(gg, n, k) for gg, n, k in obs if gg.intersects(region)]
    best, n = None, int(reach / step)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = round(c.x + i * step, 3), round(c.y + j * step, 3)
            dd = math.hypot(x - c.x, y - c.y)
            if dd > reach or (best and dd >= best[0]):
                continue
            v = Point(x, y).buffer(d / 2)
            if any(k == 'pad' and v.distance(gg) < PAD for gg, nn, k in near):          # off every pad, its own too
                continue
            if any(nn != net and v.distance(gg) < (0.2 if k != 'pad' else 0.2) + 1e-6 for gg, nn, k in near if k != 'pad'):
                continue
            if any(nn != net and k == 'pad' and v.distance(gg) < 0.2 for gg, nn, k in near):
                continue
            stub = LineString([(c.x, c.y), (x, y)]).buffer(0.15)
            if any(nn != net and stub.distance(gg) < (PAD if k == 'pad' else clear(nn, net)) for gg, nn, k in near):
                continue
            if any(k == 'via' and v.distance(gg) < 0.25 for gg, nn, k in near):
                continue
            best = (dd, x, y)
    return best


for cn in CONNS:
    if 'drop' in cn:
        continue
    if 'gnd_via' in cn:
        pad = tuple(cn['gnd_via'])
        v = via_near(pad)
        if v is None:
            report.append(f'no GND via spot by {pad}'); continue
        _, x, y = v
        c = pads[pad][0].centroid
        items.append(dict(net='GND', via=(x, y), d=0.45, drill=0.2))
        items.append(dict(net='GND', layer='F.Cu', w=0.3, path=[(round(c.x, 3), round(c.y, 3)), (x, y)]))
        obs.append((Point(x, y).buffer(0.225), 'GND', 'via'))
        obs.append((LineString([(c.x, c.y), (x, y)]).buffer(0.15), 'GND', 'cu'))
        report.append(f'GND via by {pad} at ({x}, {y})')
        continue
    net, w = cn['net'], cn.get('w', 0.1)
    A, B = pads[tuple(cn['a'])][0].centroid, pads[tuple(cn['b'])][0].centroid
    path = astar((round(A.x, 3), round(A.y, 3)), (round(B.x, 3), round(B.y, 3)), net, w, avoid=cn.get('avoid', ()), exempt=cn.get('exempt', ()))
    if path is None:
        report.append(f"{net}: no L1 path {cn['a']} -> {cn['b']}"); continue
    items.append(dict(net=net, layer='F.Cu', w=w, path=path))
    obs.append((LineString(path).buffer(w / 2), net, 'cu'))
    L = sum(math.dist(p, q) for p, q in zip(path, path[1:]))
    report.append(f"{net}: {cn['a']} -> {cn['b']} {L:.2f} mm, {len(path) - 1} runs")
json.dump(items, open(sys.argv[3], 'w'), indent=1)
print('\n'.join(report)); print(len(items), 'items')
