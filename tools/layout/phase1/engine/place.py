"""Greedy constructive placement: fixed parts, regions, anchors, then each part
pulled to the pads it connects to, on a spiral, without courtyard overlap."""
import math
import pcbnew as K

MM, TOMM = K.FromMM, K.ToMM
ROTS = (0, 90, 180, 270)


def geometry(fp):
    """Per rotation: courtyard bbox (local mm, relative to the footprint origin) and pad offsets."""
    g = {}
    for a in ROTS:
        fp.SetOrientationDegrees(a)
        fp.SetPosition(K.VECTOR2I(0, 0))
        fp.BuildCourtyardCaches()
        cy = fp.GetCourtyard(K.F_CrtYd)
        bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False, False)
        box = (TOMM(bb.GetX()), TOMM(bb.GetY()), TOMM(bb.GetRight()), TOMM(bb.GetBottom()))
        pads = {}
        for p in fp.Pads():
            q = p.GetPosition()
            pads.setdefault(p.GetNumber(), []).append((TOMM(q.x), TOMM(q.y)))
        g[a] = (box, pads)
    return g


class Placer:
    def __init__(self, fps, nets, origin, size, margin=0.25, power_fanout=12):
        self.fps, self.nets = fps, nets
        self.ox, self.oy = origin
        self.w, self.h = size
        self.margin = margin
        self.geo = {r: geometry(f) for r, f in fps.items()}
        self.placed = {}                      # ref -> (x, y, rot) board-local mm
        self.boxes = []                       # (x0, y0, x1, y1, ref)
        self.keepouts = []
        self.fanout = {n: len(v) for n, v in nets.items()}
        self.power_fanout = power_fanout
        self.pin_nets = {}
        for n, nodes in nets.items():
            for r, p in nodes:
                self.pin_nets.setdefault(r, {}).setdefault(p, n)
        self.cap_used = set()

    # --- geometry helpers
    def box_at(self, ref, x, y, a):
        bx = self.geo[ref][a][0]
        m = self.margin
        return (x + bx[0] - m, y + bx[1] - m, x + bx[2] + m, y + bx[3] + m)

    def pad_pos(self, ref, pin):
        x, y, a = self.placed[ref]
        return [(x + px, y + py) for px, py in self.geo[ref][a][1].get(pin, [])]

    def free(self, box, region):
        x0, y0, x1, y1 = box
        rx0, ry0, rx1, ry1 = region
        if x0 < rx0 or y0 < ry0 or x1 > rx1 or y1 > ry1:
            return False
        for b in self.boxes + self.keepouts:
            if x0 < b[2] and b[0] < x1 and y0 < b[3] and b[1] < y1:
                return False
        return True

    def commit(self, ref, x, y, a):
        self.placed[ref] = (x, y, a)
        self.boxes.append(self.box_at(ref, x, y, a) + (ref,))

    def fix(self, ref, x, y, a=0):
        self.commit(ref, x, y, a)

    # --- targets
    def targets(self, ref):
        """(pin, point, weight) pulls toward pads already placed."""
        out = []
        for pin, net in self.pin_nets.get(ref, {}).items():
            if net.endswith('GND') or net == 'GND':
                continue
            f = self.fanout[net]
            others = [(r, p) for r, p in self.nets[net] if r != ref and r in self.placed]
            if not others:
                continue
            if f > self.power_fanout:
                continue
            pts = [q for r, p in others for q in self.pad_pos(r, p)]
            if pts:
                cx = sum(q[0] for q in pts) / len(pts); cy = sum(q[1] for q in pts) / len(pts)
                out.append((pin, (cx, cy), 1.0 / max(1, f - 1)))
        if not out:                            # decoupling: nearest unused power pin of a placed part
            for pin, net in self.pin_nets.get(ref, {}).items():
                if net.endswith('GND') or net == 'GND' or self.fanout[net] <= self.power_fanout:
                    continue
                cands = [(r, p) for r, p in self.nets[net] if r in self.placed and (r, p) not in self.cap_used
                         and len(self.pin_nets.get(r, {})) > 3]
                if cands:
                    r, p = cands[0]
                    self.cap_used.add((r, p))
                    out.append((pin, self.pad_pos(r, p)[0], 2.0))
                    break
        return out

    def cost(self, ref, x, y, a, tg):
        c = 0.0
        pads = self.geo[ref][a][1]
        for pin, (tx, ty), wgt in tg:
            px, py = pads[pin][0]
            c += wgt * math.hypot(x + px - tx, y + py - ty)
        return c

    def place(self, ref, region, start=None, step=0.25, rmax=60):
        tg = self.targets(ref)
        if start is None:
            if tg:
                tw = sum(t[2] for t in tg)
                start = (sum(t[1][0] * t[2] for t in tg) / tw, sum(t[1][1] * t[2] for t in tg) / tw)
            else:
                start = ((region[0] + region[2]) / 2, (region[1] + region[3]) / 2)
        sx = min(max(start[0], region[0]), region[2])
        sy = min(max(start[1], region[1]), region[3])
        r = 0.0
        while r <= rmax:
            n = max(1, int(2 * math.pi * r / step)) if r else 1
            best = None
            for i in range(n):
                th = 2 * math.pi * i / n
                x, y = round((sx + r * math.cos(th)) / 0.05) * 0.05, round((sy + r * math.sin(th)) / 0.05) * 0.05
                for a in ROTS:
                    if self.free(self.box_at(ref, x, y, a), region):
                        c = self.cost(ref, x, y, a, tg) if tg else r
                        if best is None or c < best[0]:
                            best = (c, x, y, a)
            if best:
                self.commit(ref, best[1], best[2], best[3])
                return True
            r += step
        return False

    def order(self, refs):
        """Big, well-connected parts first, then by connection to what's placed (BFS-like)."""
        left = set(refs)
        seq = []
        def size(r):
            b = self.geo[r][0][0]
            return (b[2] - b[0]) * (b[3] - b[1])
        while left:
            def score(r):
                links = sum(1 for p, n in self.pin_nets.get(r, {}).items()
                            if self.fanout[n] <= self.power_fanout and any(q in self.placed or q in seq for q, _ in self.nets[n] if q != r))
                return (links, size(r))
            r = max(left, key=score)
            seq.append(r); left.discard(r)
        return seq

    def apply(self):
        for ref, (x, y, a) in self.placed.items():
            fp = self.fps[ref]
            fp.SetOrientationDegrees(a)
            fp.SetPosition(K.VECTOR2I(MM(self.ox + x), MM(self.oy + y)))

    def hpwl(self):
        """Half-perimeter wire length of every net, board-local mm (placement quality proxy)."""
        total = 0.0
        for n, nodes in self.nets.items():
            pts = [q for r, p in nodes if r in self.placed for q in self.pad_pos(r, p)[:1]]
            if len(pts) > 1:
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                total += (max(xs) - min(xs)) + (max(ys) - min(ys))
        return total
