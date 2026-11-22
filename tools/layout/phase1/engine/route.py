"""Scripted copper: an obstacle index, plane fanout (pad -> stub -> via) and simple pad-to-pad routes."""
import math
import pcbnew as K

MM, TOMM = K.FromMM, K.ToMM
CU = (K.F_Cu, K.In1_Cu, K.In2_Cu, K.B_Cu)


class Obstacles:
    def __init__(self, b):
        self.b = b
        self.items = []                         # (bbox, shape-getter, netcode, layers)
        for f in b.GetFootprints():
            for p in f.Pads():
                self.add_item(p)
        for t in b.GetTracks():
            self.add_item(t)
        self.edge = b.GetBoardEdgesBoundingBox()
        self.holes = []                         # (x, y, r) of every drilled hole, any net
        for f in b.GetFootprints():
            for p in f.Pads():
                if p.GetDrillSize().x > 0:
                    q = p.GetPosition(); self.holes.append((q.x, q.y, max(p.GetSize().x, p.GetSize().y) / 2))
        for t in b.GetTracks():
            if t.Type() == K.PCB_VIA_T:
                q = t.GetPosition(); self.holes.append((q.x, q.y, t.GetWidth(K.F_Cu) / 2))

    def hole_ok(self, x, y, r, gap=0.2):
        g = MM(gap)
        return all(math.hypot(x - hx, y - hy) >= r + hr + g for hx, hy, hr in self.holes)

    def add_item(self, it):
        layers = [l for l in CU if it.IsOnLayer(l)]
        if not layers:
            return
        shapes = {l: it.GetEffectiveShape(l) for l in layers}
        bb = it.GetBoundingBox()
        self.items.append((bb, shapes, it.GetNetCode(), layers))

    def clear(self, shapes, bbox, net, clearance):
        """shapes: {layer: SHAPE}. True if nothing of another net is within clearance."""
        c = MM(clearance)
        g = K.BOX2I(bbox.GetPosition(), bbox.GetSize()); g.Inflate(c)
        e = self.edge
        if bbox.GetX() < e.GetX() + MM(0.3) or bbox.GetRight() > e.GetRight() - MM(0.3) or \
           bbox.GetY() < e.GetY() + MM(0.3) or bbox.GetBottom() > e.GetBottom() - MM(0.3):
            return False
        for bb, sh, n, layers in self.items:
            if n == net and net > 0:
                continue
            if not g.Intersects(bb):
                continue
            for l, s in shapes.items():
                if l in sh and s.Collide(sh[l], c):
                    return False
        return True


def via_shapes(b, x, y, d, drill):
    v = K.PCB_VIA(b); v.SetPosition(K.VECTOR2I(x, y)); v.SetWidth(MM(d)); v.SetDrill(MM(drill))
    v.SetViaType(K.VIATYPE_THROUGH)
    return v, {l: v.GetEffectiveShape(l) for l in CU}


def seg(b, a, c, w, layer, net):
    t = K.PCB_TRACK(b); t.SetStart(a); t.SetEnd(c); t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(net)
    return t


def fanout(b, obs, netname, via=(0.45, 0.2), stub_w=0.25, clearance=0.15, lock=True):
    """For each SMD pad of netname on F.Cu: a short stub and a via down to the plane.
    Big pads (exposed pads) get vias inside. Returns (done, failed) pad lists."""
    net = b.FindNet(netname)
    nc = net.GetNetCode()
    done, failed = [], []
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetCode() != nc or not p.IsOnLayer(K.F_Cu) or p.GetAttribute() == K.PAD_ATTRIB_PTH:
                continue
            c = p.GetPosition(); sz = p.GetSize()
            area = TOMM(sz.x) * TOMM(sz.y)
            placed = False
            if area > 2.0:                         # exposed pad: via in the pad
                v, vs = via_shapes(b, c.x, c.y, via[0], via[1])
                if obs.hole_ok(c.x, c.y, MM(via[0]) / 2) and obs.clear(vs, v.GetBoundingBox(), nc, clearance):
                    v.SetNet(net); v.SetLocked(lock); b.Add(v); obs.add_item(v); placed = True
                    obs.holes.append((c.x, c.y, MM(via[0]) / 2))
            else:
                fc = f.GetPosition()
                out = K.VECTOR2I(c.x - fc.x, c.y - fc.y)          # away from the body first
                dirs = []
                if abs(out.x) + abs(out.y) > 0:
                    nrm = math.hypot(out.x, out.y); dirs.append((out.x / nrm, out.y / nrm))
                dirs += [(1, 0), (-1, 0), (0, 1), (0, -1), (.707, .707), (-.707, .707), (.707, -.707), (-.707, -.707)]
                r0 = max(TOMM(sz.x), TOMM(sz.y)) / 2
                for dist in (r0 + 0.45, r0 + 0.6, r0 + 0.8, r0 + 1.1):
                    for dx, dy in dirs:
                        x, y = c.x + MM(dist * dx), c.y + MM(dist * dy)
                        v, vs = via_shapes(b, x, y, via[0], via[1])
                        t = seg(b, c, K.VECTOR2I(int(x), int(y)), stub_w, K.F_Cu, net)
                        ts = {K.F_Cu: t.GetEffectiveShape(K.F_Cu)}
                        bb = v.GetBoundingBox(); bb.Merge(t.GetBoundingBox())
                        allsh = dict(vs); allsh[K.F_Cu] = vs[K.F_Cu]
                        if obs.hole_ok(x, y, MM(via[0]) / 2) and obs.clear(vs, v.GetBoundingBox(), nc, clearance) \
                                and obs.clear(ts, t.GetBoundingBox(), nc, clearance):
                            obs.holes.append((x, y, MM(via[0]) / 2))
                            v.SetNet(net); v.SetLocked(lock); t.SetLocked(lock)
                            b.Add(v); b.Add(t); obs.add_item(v); obs.add_item(t); placed = True
                            break
                    if placed:
                        break
            (done if placed else failed).append(f'{f.GetReference()}.{p.GetNumber()}')
    return done, failed


def route_pts(b, obs, netname, pts_mm, width, layer=K.F_Cu, clearance=0.15, lock=True):
    """A fixed polyline (board mm) for one net, accepted only if it clears everything."""
    net = b.FindNet(netname); nc = net.GetNetCode()
    segs = [seg(b, K.VECTOR2I(MM(a[0]), MM(a[1])), K.VECTOR2I(MM(c[0]), MM(c[1])), width, layer, net)
            for a, c in zip(pts_mm, pts_mm[1:])]
    for t in segs:
        if not obs.clear({layer: t.GetEffectiveShape(layer)}, t.GetBoundingBox(), nc, clearance):
            return False
    for t in segs:
        t.SetLocked(lock); b.Add(t); obs.add_item(t)
    return True


def pad_xy(b, ref, num):
    p = [q for q in b.FindFootprintByReference(ref).Pads() if q.GetNumber() == num][0].GetPosition()
    return TOMM(p.x), TOMM(p.y)


def direct(b, obs, ref1, pin1, ref2, pin2, width, clearance=0.15):
    """Pad to pad: straight, else the two L shapes. Returns the route used or None."""
    a, c = pad_xy(b, ref1, pin1), pad_xy(b, ref2, pin2)
    p1 = [q for q in b.FindFootprintByReference(ref1).Pads() if q.GetNumber() == pin1][0]
    net = p1.GetNetname()
    for pts in ([a, c], [a, (c[0], a[1]), c], [a, (a[0], c[1]), c]):
        if route_pts(b, obs, net, pts, width, clearance=clearance):
            return pts
    return None
