"""Plane fanout planner: a via for each surface-mount pad of a plane net (layout brief §7: GND fanout, a via per
GND pad; D-22Nov.15: L3 islands for rails of four loads or more). Each pad gets its own via, never shared.

plan() checks every candidate against the board's copper in board mm and returns what it would add; apply() puts
it on a pcbnew board. Rules: the brief's dense-spot via (0.5 mm pad, 0.3 mm hole), 0.15 mm copper clearance,
0.25 mm hole to hole, 0.3 mm to the edge, nothing within Ø8 mm of a mounting hole (D-22Nov.11), and no via in a
signal pad: a via sits at least 0.1 mm off every pad, except in an exposed pad (2 mm² or more), where it goes in
the middle. A pad with no legal spot within `reach` of its edge is a miss. in_pad=True (the layer test): every pad's
via goes in the pad where its copper clears, as JLC's plated-over filled via allows (free from six layers).
D-24Nov.16: an in-pad via is tried along the pad's long axis, not only at its centre; drawn copper is checked at its
own width; a stub is the pad's width, 0.2 to 0.3 mm.
"""
import math

import numpy as np
from shapely import STRtree
from shapely.geometry import LineString, Point

VIA_D, DRILL = 0.45, 0.2          # spec.SIGNAL_VIA: JLC's smallest via at no extra cost (D-23Nov.17)
CLEAR, HOLE_GAP, EDGE, STUB_W, MASK_WEB = 0.1, 0.2, 0.2, 0.3, 0.1    # JLC's table (spec.JLC): pad to track, hole gap, edge
MIN_STUB = 0.2                    # a stub is the pad's width, 0.2 to 0.3 mm (D-24Nov.16)
BIG_PAD_MM2 = 2.0


FIRE_CLASSES = ('FIRE', 'FIRE_LOGIC', 'PYRO_RAIL')     # the brief's custom rule: 0.5 mm to other nets
FIRE_CLEAR, HOLE_CLEAR = 0.5, 0.2
RF_CLEAR = 1.0                             # other nets to an RF line, ground apart (spec.DRU, D-24Nov.8)
EPS = 0.01


def clearances(spec):
    """pair(n1, n2) -> the copper clearance KiCad will ask between two nets: the larger net-class clearance, 0.5 mm
    if either is fire copper, and 1 mm if either is an RF line and the other isn't GND (spec.DRU, D-24Nov.8)."""
    import fnmatch
    cls_cl = {c['name']: c['clearance'] for c in spec.NETCLASSES} if isinstance(spec.NETCLASSES[0], dict) else \
        {c.name: c.clearance for c in spec.NETCLASSES}
    cache = {}

    def cls(n):
        if n not in cache:
            s = n.split('/')[-1]
            cache[n] = next((c for c, pat in spec.PATTERNS if fnmatch.fnmatchcase(s, pat)), 'Default')
        return cache[n]

    def pair(n1, n2):
        if n1 == n2 and n1:
            return 0.0
        a, b = cls(n1 or ''), cls(n2 or '')
        c = max(cls_cl.get(a, CLEAR), cls_cl.get(b, CLEAR))
        if a in FIRE_CLASSES or b in FIRE_CLASSES:
            c = max(c, FIRE_CLEAR)
        if (a == 'RF50' and b != 'GND') or (b == 'RF50' and a != 'GND'):
            c = max(c, RF_CLEAR)
        return c + EPS                     # the pad outlines are drawn 0.01 mm inside the true shape
    return pair


def existing(board, origin):
    """The copper on the board before the fanout (stage C's scripted copper, D-22Nov.17): its vias [(x, y, net)], its
    L1 tracks [(LineString, width, net)], its tracks on every other layer ('under': a via passes through them), the
    board's and the footprints' rule areas that forbid vias or L1 tracks ('areas'), and the (ref, num) of each pad one
    of them already joins (a track end in the pad, or a via touching it): those pads need no fanout via of their own."""
    import pcbnew as K
    from shapely.geometry import Polygon
    ox, oy = origin
    mm = lambda v: K.ToMM(v)
    vias, tracks, under, areas = [], [], [], []
    for t in board.GetTracks():
        n = t.GetNetname()
        if t.Type() == K.PCB_VIA_T:
            c = t.GetPosition()
            vias.append((mm(c.x) - ox, mm(c.y) - oy, n))
        else:
            a, e = t.GetStart(), t.GetEnd()
            ls = LineString([(mm(a.x) - ox, mm(a.y) - oy), (mm(e.x) - ox, mm(e.y) - oy)])
            (tracks if t.GetLayer() == K.F_Cu else under).append((ls, mm(t.GetWidth()), n))
    for z in list(board.Zones()) + [z for f in board.GetFootprints() for z in f.Zones()]:
        if not z.GetIsRuleArea() or not (z.GetDoNotAllowVias() or z.GetDoNotAllowTracks()):
            continue
        o = z.Outline()
        for i in range(o.OutlineCount()):
            ol = o.Outline(i)
            g = Polygon([(mm(ol.CPoint(j).x) - ox, mm(ol.CPoint(j).y) - oy) for j in range(ol.PointCount())]).buffer(0)
            areas.append({'poly': g, 'no_via': bool(z.GetDoNotAllowVias()),
                          'no_track_f': bool(z.GetDoNotAllowTracks()) and z.IsOnLayer(K.F_Cu)})
    # D-24Nov.16: drawn copper joins pads into groups; a pad is 'joined' (needs no via of its own) only if its group
    # holds a via or a through-hole pad. 'group' maps each pad in a group to its id, so the first via the plan gives
    # one of a group's pads serves them all (a supply pin drawn to its capacitor: the capacitor's pad takes the via)
    joined, group = set(), {}
    if vias or tracks:
        items = []                                  # (shape, net, pad key or None, reaches the plane)
        for f in board.GetFootprints():
            for p in f.Pads():
                n = p.GetNetname()
                if not n or not p.IsOnLayer(K.F_Cu):
                    continue
                ps = K.SHAPE_POLY_SET()
                p.TransformShapeToPolygon(ps, K.F_Cu, 0, K.FromMM(0.01), K.ERROR_INSIDE)
                if not ps.OutlineCount():
                    continue
                o = ps.Outline(0)
                g = Polygon([(mm(o.CPoint(i).x) - ox, mm(o.CPoint(i).y) - oy) for i in range(o.PointCount())]).buffer(0.002)
                items.append((g, n, (f.GetReference(), p.GetNumber()), p.GetAttribute() == K.PAD_ATTRIB_PTH))
        items += [(t.buffer(w / 2), n, None, False) for t, w, n in tracks]
        items += [(Point(x, y).buffer(VIA_D / 2), n, None, True) for x, y, n in vias]
        parent = list(range(len(items)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        tree = STRtree([g for g, *_ in items])
        for i, (g, n, _, _) in enumerate(items):
            for j in tree.query(g, predicate='intersects'):
                if j > i and items[j][1] == n:
                    parent[find(i)] = find(j)
        reach = {find(i) for i, it in enumerate(items) if it[3]}
        sizes = {}
        for i, it in enumerate(items):
            sizes[find(i)] = sizes.get(find(i), 0) + 1
        for i, (g, n, key, _) in enumerate(items):
            if key is None:
                continue
            r = find(i)
            if r in reach:
                joined.add(key)
            elif sizes[r] > 1:
                group[key] = r
    return {'vias': vias, 'tracks': tracks, 'under': under, 'areas': areas, 'joined': joined, 'group': group}


def plan(bd, planes, spec, reach=1.5, step=0.1, in_pad=False, existing=None, no_via=()):
    """existing: from existing(); its pads are skipped and its copper is kept clear of. no_via: shapely polygons
    (board mm) no via may touch, the keep-outs of the budget run (meter.py --budget)."""
    vr = VIA_D / 2
    ex = existing or {'vias': [], 'tracks': [], 'joined': set()}
    pair = clearances(spec)
    F = [(d['poly']['F'], d['net'], i) for i, d in enumerate(bd.pads) if 'F' in d['poly']]
    Bk = [(d['poly']['B'], d['net'], i) for i, d in enumerate(bd.pads) if 'B' in d['poly']]
    trees = {}
    for name, items in (('F', F), ('B', Bk)):
        trees[name] = (STRtree([g for g, _, _ in items]), items)
    holes = np.array([(d['x'], d['y'], d['hole']) for d in bd.pads if d['hole']] or np.zeros((0, 3)))
    hole_net = [d['net'] for d in bd.pads if d['hole']]
    washers = [(x, y) for x, y in spec.HOLES]
    washer_r = spec.HOLE_TRACK_KEEPOUT_D / 2
    vias = []            # (x, y, net)
    stubs = []           # (LineString, net)
    old_vias = ex['vias']
    # drawn copper at its own width (D-24Nov.16: it was modelled as 0.3 mm stubs, which turned away legal sites)
    old_tracks = [(t.buffer(w / 2), n) for t, w, n in ex['tracks']]
    # scripted copper on the other layers: a via passes through it, an L1 stub doesn't
    old_under = [(t.buffer(w / 2), n) for t, w, n in ex.get('under', [])]
    area_via = [a['poly'] for a in ex.get('areas', []) if a['no_via']]
    area_trk = [a['poly'] for a in ex.get('areas', []) if a['no_track_f']]

    def copper_ok(pt, net, own):
        """Other-net copper at its pair clearance from the via on F and B; every pad at least vr + MASK_WEB
        (no via in pad)."""
        for name in ('F', 'B'):
            tree, items = trees[name]
            for k in tree.query(pt, predicate='dwithin', distance=vr + FIRE_CLEAR):
                g, n, i = items[k]
                d = g.distance(pt)
                if n != net and d < vr + pair(net, n):
                    return False
                if i != own and d < vr + MASK_WEB:
                    return False
        return True

    def via_ok(x, y, net, own, in_pad=False):
        if not (vr + EDGE <= x <= bd.W - vr - EDGE and vr + EDGE <= y <= bd.H - vr - EDGE):
            return False
        if any(math.hypot(x - wx, y - wy) < washer_r + vr for wx, wy in washers):
            return False
        if no_via and any(k.distance(Point(x, y)) < vr for k in no_via):
            return False
        if any(k.distance(Point(x, y)) < vr for k in area_via):          # the board's own keep-outs
            return False
        if len(holes) and (np.hypot(holes[:, 0] - x, holes[:, 1] - y) < holes[:, 2] + DRILL / 2 + HOLE_GAP).any():
            return False
        for vx, vy, vn in vias + old_vias:
            dd = math.hypot(vx - x, vy - y)
            if dd < DRILL + HOLE_GAP or (vn != net and dd < VIA_D + pair(net, vn)):
                return False
        pt = Point(x, y)
        for s, sn in stubs + old_tracks + old_under:
            if sn != net and s.distance(pt) < vr + pair(net, sn):
                return False
        if in_pad:
            # copper clearance only: the via is meant to sit in its own pad
            for name in ('F', 'B'):
                tree, items = trees[name]
                for k in tree.query(pt, predicate='dwithin', distance=vr + FIRE_CLEAR):
                    g, n, i = items[k]
                    if n != net and g.distance(pt) < vr + pair(net, n):
                        return False
            return True
        return copper_ok(pt, net, own)

    def stub_ok(a, b, net, own, sw=STUB_W):
        s = LineString([a, b])
        if any(k.distance(s) < sw / 2 for k in area_trk):
            return False
        for name in ('F',):
            tree, items = trees[name]
            for k in tree.query(s, predicate='dwithin', distance=sw / 2 + FIRE_CLEAR):
                g, n, i = items[k]
                if n != net and g.distance(s) < sw / 2 + pair(net, n):
                    return False
        for (hx, hy, hr), hn in zip(holes, hole_net):
            if hn != net and s.distance(Point(hx, hy)) < hr + HOLE_CLEAR + sw / 2 + EPS:
                return False
        for vx, vy, vn in vias + old_vias:
            if vn != net and s.distance(Point(vx, vy)) < vr + sw / 2 + pair(net, vn):
                return False
        for t, tn in stubs + old_tracks:
            if tn != net and s.distance(t) < sw / 2 + pair(net, tn):
                return False
        return True

    done, failed = [], []
    order = sorted((i for i, d in enumerate(bd.pads)
                    if d['net'] in planes and 'F' in d['poly'] and not d['tht'] and (d['ref'], d['num']) not in ex['joined']),
                   key=lambda i: (bd.pads[i]['ref'], bd.pads[i]['num']))
    group, served = ex.get('group', {}), set()
    for i in order:
        d = bd.pads[i]
        if group.get((d['ref'], d['num'])) in served:      # its drawn group got a via already (D-24Nov.16)
            done.append(dict(d, via=None, stub=None, by_group=True)); continue
        net, g = d['net'], d['poly']['F']
        cx, cy = g.centroid.x, g.centroid.y
        mrr = list(g.minimum_rotated_rectangle.exterior.coords)[:3]
        e1 = (mrr[1][0] - mrr[0][0], mrr[1][1] - mrr[0][1])
        e2 = (mrr[2][0] - mrr[1][0], mrr[2][1] - mrr[1][1])
        long_, short_ = (e1, e2) if math.hypot(*e1) >= math.hypot(*e2) else (e2, e1)
        sw = min(STUB_W, max(MIN_STUB, math.hypot(*short_)))     # the pad's width, 0.2 to 0.3 mm (D-24Nov.16)
        if g.area >= BIG_PAD_MM2 or in_pad:
            site = None
            if via_ok(cx, cy, net, i, in_pad=True):
                site = (cx, cy)
            else:                                   # D-24Nov.16: along the pad's long axis, nearest the centre first
                L = math.hypot(*long_)
                ux, uy = long_[0] / L, long_[1] / L
                for k in range(1, int(L / 0.05) + 1):
                    for sg in (1, -1):
                        x, y = round(cx + sg * k * 0.025 * ux, 3), round(cy + sg * k * 0.025 * uy, 3)
                        if g.contains(Point(x, y)) and via_ok(x, y, net, i, in_pad=True):
                            site = (x, y)
                            break
                    if site:
                        break
            if site:
                vias.append((site[0], site[1], net)); done.append(dict(d, via=site, stub=None))
                if (d['ref'], d['num']) in group:
                    served.add(group[(d['ref'], d['num'])])
                continue
        fx, fy = bd.fp_xy[d['ref']]
        away = math.atan2(cy - fy, cx - fx) if (cx, cy) != (fx, fy) else 0.0
        dirs = sorted((math.radians(22.5 * k) for k in range(16)),
                      key=lambda t: (abs((t - away + math.pi) % (2 * math.pi) - math.pi), t))
        hit = None
        for t in np.arange(0.0, reach + 1e-9, step):
            for th in dirs:
                ux, uy = math.cos(th), math.sin(th)
                # the first distance from the centre where the via clears its own pad by MASK_WEB, then t further
                r = 0.0
                while Point(cx + r * ux, cy + r * uy).distance(g) < vr + MASK_WEB:
                    r += 0.05
                r += t
                x, y = round(cx + r * ux, 3), round(cy + r * uy, 3)
                if via_ok(x, y, net, i):
                    w_ok = next((w for w in (sw, MIN_STUB) if stub_ok((cx, cy), (x, y), net, i, w)), None)
                    if w_ok:                        # the pad's width where there's room, else 0.2 mm
                        hit, sw = (x, y), w_ok
                        break
            if hit:
                break
        if hit:
            vias.append((hit[0], hit[1], net))
            stubs.append((LineString([(cx, cy), hit]).buffer(sw / 2), net))
            done.append(dict(d, via=hit, stub=((cx, cy), hit), stub_w=sw))
            if (d['ref'], d['num']) in group:
                served.add(group[(d['ref'], d['num'])])
        else:
            failed.append(d)
    late = [d for d in failed if group.get((d['ref'], d['num'])) in served]   # its group got a via after it was tried
    failed = [d for d in failed if d not in late]
    done += [dict(d, via=None, stub=None, by_group=True) for d in late]
    copper = {'F': [Point(x, y).buffer(vr, 8) for x, y, _ in vias] + [s for s, _ in stubs],
              'B': [Point(x, y).buffer(vr, 8) for x, y, _ in vias]}
    return {'done': done, 'failed': failed, 'vias': vias, 'copper': copper}


def apply(board, origin, result, lock=True):
    """Put a plan's vias and stubs on a pcbnew board."""
    import pcbnew as K
    ox, oy = origin
    V = lambda x, y: K.VECTOR2I(K.FromMM(float(x + ox)), K.FromMM(float(y + oy)))
    nets = {}
    for d in result['done']:
        if d.get('via') is None:                    # served through its drawn group's via
            continue
        net = nets.get(d['net']) or board.FindNet(d['net'])
        nets[d['net']] = net
        v = K.PCB_VIA(board)
        v.SetPosition(V(*d['via'])); v.SetWidth(K.FromMM(VIA_D)); v.SetDrill(K.FromMM(DRILL))
        v.SetViaType(K.VIATYPE_THROUGH); v.SetNet(net); v.SetLocked(lock)
        board.Add(v)
        if d['stub']:
            t = K.PCB_TRACK(board)
            t.SetStart(V(*d['stub'][0])); t.SetEnd(V(*d['stub'][1])); t.SetWidth(K.FromMM(d.get('stub_w', STUB_W)))
            t.SetLayer(K.F_Cu); t.SetNet(net); t.SetLocked(lock)
            board.Add(t)
