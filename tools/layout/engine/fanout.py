"""Plane fanout planner: a via for each surface-mount pad of a plane net (layout brief §7: GND fanout, a via per
GND pad; D-22Nov.15: L3 islands for rails of four loads or more). Each pad gets its own via, never shared.

plan() checks every candidate against the board's copper in board mm and returns what it would add; apply() puts
it on a pcbnew board. Rules: the brief's dense-spot via (0.5 mm pad, 0.3 mm hole), 0.15 mm copper clearance,
0.25 mm hole to hole, 0.3 mm to the edge, nothing within Ø8 mm of a mounting hole (D-22Nov.11), and no via in a
signal pad: a via sits at least 0.1 mm off every pad, except in an exposed pad (2 mm² or more), where it goes in
the middle. A pad with no legal spot within `reach` of its edge is a miss.
"""
import math

import numpy as np
from shapely import STRtree
from shapely.geometry import LineString, Point

VIA_D, DRILL = 0.5, 0.3
CLEAR, HOLE_GAP, EDGE, STUB_W, MASK_WEB = 0.15, 0.25, 0.3, 0.3, 0.1
BIG_PAD_MM2 = 2.0


FIRE_CLASSES = ('FIRE', 'FIRE_LOGIC', 'PYRO_RAIL')     # the brief's custom rule: 0.5 mm to other nets
FIRE_CLEAR, HOLE_CLEAR = 0.5, 0.25
EPS = 0.01


def clearances(spec):
    """pair(n1, n2) -> the copper clearance KiCad will ask between two nets: the larger net-class clearance, and
    0.5 mm if either is fire copper (spec.DRU)."""
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
        return c + EPS                     # the pad outlines are drawn 0.01 mm inside the true shape
    return pair


def plan(bd, planes, spec, reach=1.5, step=0.1):
    vr = VIA_D / 2
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
        if len(holes) and (np.hypot(holes[:, 0] - x, holes[:, 1] - y) < holes[:, 2] + DRILL / 2 + HOLE_GAP).any():
            return False
        for vx, vy, vn in vias:
            dd = math.hypot(vx - x, vy - y)
            if dd < DRILL + HOLE_GAP or (vn != net and dd < VIA_D + pair(net, vn)):
                return False
        pt = Point(x, y)
        for s, sn in stubs:
            if sn != net and s.distance(pt) < vr + STUB_W / 2 + pair(net, sn):
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

    def stub_ok(a, b, net, own):
        s = LineString([a, b])
        for name in ('F',):
            tree, items = trees[name]
            for k in tree.query(s, predicate='dwithin', distance=STUB_W / 2 + FIRE_CLEAR):
                g, n, i = items[k]
                if n != net and g.distance(s) < STUB_W / 2 + pair(net, n):
                    return False
        for (hx, hy, hr), hn in zip(holes, hole_net):
            if hn != net and s.distance(Point(hx, hy)) < hr + HOLE_CLEAR + STUB_W / 2 + EPS:
                return False
        for vx, vy, vn in vias:
            if vn != net and s.distance(Point(vx, vy)) < vr + STUB_W / 2 + pair(net, vn):
                return False
        for t, tn in stubs:
            if tn != net and s.distance(t) < STUB_W + pair(net, tn):
                return False
        return True

    done, failed = [], []
    order = sorted((i for i, d in enumerate(bd.pads)
                    if d['net'] in planes and 'F' in d['poly'] and not d['tht']),
                   key=lambda i: (bd.pads[i]['ref'], bd.pads[i]['num']))
    for i in order:
        d = bd.pads[i]
        net, g = d['net'], d['poly']['F']
        cx, cy = g.centroid.x, g.centroid.y
        if g.area >= BIG_PAD_MM2:
            if via_ok(cx, cy, net, i, in_pad=True):
                vias.append((cx, cy, net)); done.append(dict(d, via=(cx, cy), stub=None)); continue
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
                if via_ok(x, y, net, i) and stub_ok((cx, cy), (x, y), net, i):
                    hit = (x, y)
                    break
            if hit:
                break
        if hit:
            vias.append((hit[0], hit[1], net))
            stubs.append((LineString([(cx, cy), hit]), net))
            done.append(dict(d, via=hit, stub=((cx, cy), hit)))
        else:
            failed.append(d)
    copper = {'F': [Point(x, y).buffer(vr, 8) for x, y, _ in vias] + [s.buffer(STUB_W / 2, 4) for s, _ in stubs],
              'B': [Point(x, y).buffer(vr, 8) for x, y, _ in vias]}
    return {'done': done, 'failed': failed, 'vias': vias, 'copper': copper}


def apply(board, origin, result, lock=True):
    """Put a plan's vias and stubs on a pcbnew board."""
    import pcbnew as K
    ox, oy = origin
    V = lambda x, y: K.VECTOR2I(K.FromMM(float(x + ox)), K.FromMM(float(y + oy)))
    nets = {}
    for d in result['done']:
        net = nets.get(d['net']) or board.FindNet(d['net'])
        nets[d['net']] = net
        v = K.PCB_VIA(board)
        v.SetPosition(V(*d['via'])); v.SetWidth(K.FromMM(VIA_D)); v.SetDrill(K.FromMM(DRILL))
        v.SetViaType(K.VIATYPE_THROUGH); v.SetNet(net); v.SetLocked(lock)
        board.Add(v)
        if d['stub']:
            t = K.PCB_TRACK(board)
            t.SetStart(V(*d['stub'][0])); t.SetEnd(V(*d['stub'][1])); t.SetWidth(K.FromMM(STUB_W))
            t.SetLayer(K.F_Cu); t.SetNet(net); t.SetLocked(lock)
            board.Add(t)
