"""pockets.py BOARD REF.PIN [REF.PIN ...] [--netcl FILE] [--grid 0.1] [--win 3]: the region a 0.09 mm track of the
pin's net can reach from it on L1, L3 and L6, changing layer where a 0.45 mm via fits, and the copper that bounds it,
by net and layer (Fable's fifth review: judge pins by whether they're boxed in, not by the open count).

    python3 /work/tools/layout/pockets.py /root/layers/<trial>/routed.kicad_pcb U201.4 --netcl .../net-clearances.json

Run in the KiCad chroot. A grid (the router's 0.1 mm by default, on the board's absolute grid) in a window of +/- WIN
mm round the pin; each cell is free on a layer if no other net's copper there (pads, tracks, vias) or a keep-out
comes nearer than the pair's clearance plus the track's half width; a via fits where it clears every layer. The pair's
clearance is the larger of the two nets' values: a trial's net-clearances.json, or the spec's classes. Zones are left
out, as the trial leaves them (the planes are modelled by vias). Read only. closes.py uses pocket() for its fourth
count: a neighbour's pin that loses its last via site, or its way out of the window, to copper about to be frozen.
"""
import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pcbnew as K                               # noqa: E402
from engine import fanout as FO                  # noqa: E402
from engine import metrics as M                  # noqa: E402
from shapely import STRtree                      # noqa: E402
from shapely.geometry import LineString, Point, Polygon   # noqa: E402

HW, VR = 0.045, 0.225
LAYERS = ('L1', 'L3', 'L6')
LAY = {'F.Cu': 'L1', 'In2.Cu': 'L3', 'B.Cu': 'L6'}


class Copper:
    """A board's copper on L1, L3 and L6 as shapes, with spatial indexes; `extra` adds items (closes.shapes form:
    (net, shape, 'via' or a layer name))."""

    def __init__(self, b, spec, extra=(), netcl=None):
        ox, oy = spec.ORIGIN
        mm = lambda v: (K.ToMM(v.x) - ox, K.ToMM(v.y) - oy)
        self.items = {l: [] for l in LAYERS}
        self.keep = {l: [] for l in LAYERS}
        self.pads = {}
        for f in b.GetFootprints():
            for p in f.Pads():
                for lname, lid in (('L1', K.F_Cu), ('L6', K.B_Cu), ('L3', K.In2_Cu)):
                    if not p.IsOnLayer(lid) or (lname == 'L3' and p.GetAttribute() != K.PAD_ATTRIB_PTH):
                        continue
                    ps = K.SHAPE_POLY_SET()
                    p.TransformShapeToPolygon(ps, lid, 0, K.FromMM(0.005), K.ERROR_INSIDE)
                    for i in range(ps.OutlineCount()):
                        o = ps.Outline(i)
                        g = Polygon([mm(o.CPoint(j)) for j in range(o.PointCount())])
                        self.items[lname].append((p.GetNetname(), g, f'pad {f.GetReference()}.{p.GetNumber()}'))
                        if lname == 'L1':
                            self.pads[f'{f.GetReference()}.{p.GetNumber()}'] = (p.GetNetname(), g, mm(p.GetPosition()))
        for t in b.GetTracks():
            n = t.GetNetname()
            if t.Type() == K.PCB_VIA_T:
                g = Point(mm(t.GetPosition())).buffer(K.ToMM(t.GetWidth(K.F_Cu)) / 2)
                for l in LAYERS:
                    self.items[l].append((n, g, 'via'))
            elif b.GetLayerName(t.GetLayer()) in LAY:
                self.items[LAY[b.GetLayerName(t.GetLayer())]].append(
                    (n, LineString([mm(t.GetStart()), mm(t.GetEnd())]).buffer(K.ToMM(t.GetWidth()) / 2), 'track'))
        for n, g, kind in extra:
            for l in (LAYERS if kind == 'via' else (LAY.get(kind),)):
                if l:
                    self.items[l].append((n, g, 'frozen ' + ('via' if kind == 'via' else 'track')))
        for z in b.Zones():
            if z.GetIsRuleArea() and z.GetDoNotAllowTracks():
                o = z.Outline().Outline(0)
                P = Polygon([mm(o.CPoint(i)) for i in range(o.PointCount())])
                for lname, lid in (('L1', K.F_Cu), ('L3', K.In2_Cu), ('L6', K.B_Cu)):
                    if z.IsOnLayer(lid):
                        self.keep[lname].append((z.GetZoneName(), P))
        self.trees = {l: STRtree([g for _, g, _ in self.items[l]]) for l in LAYERS}
        pair = FO.clearances(spec)
        if netcl:
            cl = json.load(open(netcl))
            c = lambda n: cl.get(n, cl.get(M.short(n), 0.1))
            self.pair = lambda a, b_: max(c(a), c(b_))
        else:
            self.pair = pair

    def blockers(self, net, l, P, r):
        out = []
        for k in self.trees[l].query(P, predicate='dwithin', distance=r + 0.6):
            n, g, what = self.items[l][k]
            if n == net:
                continue
            if g.distance(P) < self.pair(net, n) + r - 1e-6:
                out.append((M.short(n) or '(no net)', l, what))
        for name, P2 in self.keep[l]:
            if P2.contains(P):
                out.append((name, l, 'keep-out'))
        return out


def pocket(cu, pin, grid=0.1, win=3.0):
    """The region from `pin` ('REF.NUM'): cells per layer, via sites, whether it reaches the window's edge, the net's
    own copper it touches, and what bounds it and its via sites, by (net, layer, what) and cell count."""
    net, padg, (cx, cy) = cu.pads[pin]
    n = int(round(2 * win / grid)) + 1
    x0, y0 = round(round((cx - win) / grid) * grid, 4), round(round((cy - win) / grid) * grid, 4)
    xy = lambda i, j: (round(x0 + i * grid, 4), round(y0 + j * grid, 4))
    memo, vmemo = {}, {}

    def blocked(l, i, j):
        k = (l, i, j)
        if k not in memo:
            memo[k] = cu.blockers(net, l, Point(xy(i, j)), HW)
        return memo[k]

    def via_blocked(i, j):
        if (i, j) not in vmemo:
            P = Point(xy(i, j))
            vmemo[(i, j)] = [x for l in LAYERS for x in cu.blockers(net, l, P, VR)]
        return vmemo[(i, j)]
    seen, q = set(), deque()
    for i in range(n):
        for j in range(n):
            if padg.contains(Point(xy(i, j))):
                seen.add(('L1', i, j))
                q.append(('L1', i, j))
    if not q:                                   # a pad narrower than the grid: its nearest cell
        i, j = int(round((cx - x0) / grid)), int(round((cy - y0) / grid))
        seen.add(('L1', i, j))
        q.append(('L1', i, j))
    bound, vbound, edge, vias = defaultdict(int), defaultdict(int), False, 0
    while q:
        l, i, j = q.popleft()
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if not (di or dj):
                    continue
                a, c = i + di, j + dj
                if not (0 <= a < n and 0 <= c < n):
                    edge = True
                    continue
                if (l, a, c) in seen:
                    continue
                bl = blocked(l, a, c)
                if bl:
                    for x in set(bl):
                        bound[x] += 1
                    continue
                seen.add((l, a, c))
                q.append((l, a, c))
        vb = via_blocked(i, j)
        if vb:
            for x in set(vb):
                vbound[x] += 1
            continue
        vias += 1
        for l2 in LAYERS:
            if (l2, i, j) not in seen and not blocked(l2, i, j):
                seen.add((l2, i, j))
                q.append((l2, i, j))
    per = defaultdict(int)
    for l, i, j in seen:
        per[l] += 1
    top = lambda d: sorted(([a, b, w, c] for (a, b, w), c in d.items()), key=lambda r: -r[3])
    return dict(cells=dict(per), via_sites=vias, reaches_edge=edge, bounded_by=top(bound)[:12],
                via_blocked_by=top(vbound)[:8])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('board')
    ap.add_argument('pins', nargs='+')
    ap.add_argument('--netcl')
    ap.add_argument('--grid', type=float, default=0.1)
    ap.add_argument('--win', type=float, default=3.0)
    a = ap.parse_args()
    import build
    spec = build.load_spec('croi2')
    cu = Copper(K.LoadBoard(a.board), spec, netcl=a.netcl)
    print(json.dumps({p: pocket(cu, p, a.grid, a.win) for p in a.pins}, indent=1))


if __name__ == '__main__':
    main()
