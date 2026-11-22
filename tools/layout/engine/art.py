"""Silkscreen art and legends (Seán, 22 Nov: the board's name and version, and "funny little vector memes ...
sparkles ... both sides"). Everything here is original line art drawn from code: a burrito with a face,
sparkles and steam. Board-local mm, seen from the top; bottom-side items are mirrored so they read from below.
Lines are 0.2 mm or more and text 1.0 mm or more (JLC's silkscreen minimums)."""
import math
import pcbnew as K

MM = K.FromMM
LINE = 0.2


class Pen:
    def __init__(self, board, origin, layer, width=LINE):
        self.b, (self.ox, self.oy), self.layer, self.w = board, origin, layer, width

    def V(self, x, y):
        return K.VECTOR2I(MM(self.ox + x), MM(self.oy + y))

    def _add(self, s, fill=False):
        s.SetLayer(self.layer)
        s.SetWidth(MM(self.w))
        if fill:
            s.SetFilled(True)
        self.b.Add(s)
        return s

    def line(self, pts, closed=False):
        pts = list(pts) + ([pts[0]] if closed else [])
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            s = K.PCB_SHAPE(self.b)
            s.SetShape(K.SHAPE_T_SEGMENT)
            s.SetStart(self.V(ax, ay)); s.SetEnd(self.V(bx, by))
            self._add(s)

    def poly(self, pts):
        s = K.PCB_SHAPE(self.b)
        s.SetShape(K.SHAPE_T_POLY)
        s.SetPolyPoints([self.V(x, y) for x, y in pts])
        return self._add(s, fill=True)

    def circle(self, cx, cy, r, fill=False):
        s = K.PCB_SHAPE(self.b)
        s.SetShape(K.SHAPE_T_CIRCLE)
        s.SetCenter(self.V(cx, cy)); s.SetEnd(self.V(cx + r, cy))
        return self._add(s, fill)

    def arc(self, a, m, b):
        s = K.PCB_SHAPE(self.b)
        s.SetShape(K.SHAPE_T_ARC)
        s.SetArcGeometry(self.V(*a), self.V(*m), self.V(*b))
        return self._add(s)

    def text(self, x, y, txt, h, bold=False, angle=0, justify='center'):
        t = K.PCB_TEXT(self.b)
        t.SetText(txt)
        t.SetLayer(self.layer)
        t.SetTextSize(K.VECTOR2I(MM(h), MM(h)))
        t.SetTextThickness(MM(max(0.15, h * (0.16 if bold else 0.1))))
        t.SetPosition(self.V(x, y))
        t.SetTextAngleDegrees(angle)
        t.SetHorizJustify({'left': K.GR_TEXT_H_ALIGN_LEFT, 'right': K.GR_TEXT_H_ALIGN_RIGHT}.get(justify, K.GR_TEXT_H_ALIGN_CENTER))
        if self.layer == K.B_SilkS:
            t.SetMirrored(True)
        self.b.Add(t)
        return t


def _xf(pts, cx, cy, s=1.0, rot=0.0, mirror=False):
    c, n = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for x, y in pts:
        x, y = x * s, y * s
        x, y = x * c - y * n, x * n + y * c
        out.append((cx - x if mirror else cx + x, cy + y))
    return out


def sparkle(pen, cx, cy, s):
    q = s * 0.26
    pen.poly([(cx, cy - s), (cx + q, cy - q), (cx + s, cy), (cx + q, cy + q),
              (cx, cy + s), (cx - q, cy + q), (cx - s, cy), (cx - q, cy - q)])


def burrito(pen, cx, cy, s=1.0, rot=-12.0, mirror=False):
    """A wrapped burrito, foil on one end, with a face; about 22 x 11 mm at s = 1. Steam above."""
    X = lambda pts: _xf(pts, cx, cy, s, rot, mirror)
    body = [(-5, -5), (5, -5)] + [(5 + 5 * math.cos(math.radians(a)), 5 * math.sin(math.radians(a))) for a in range(-80, 81, 10)] \
        + [(5, 5), (-5, 5)] + [(-5 - 5 * math.cos(math.radians(a)), -5 * math.sin(math.radians(a))) for a in range(-80, 81, 10)]
    pen.line(X(body), closed=True)
    zig = [(3.2 + (0.6 if i % 2 else 0), -5 + i * 1.0) for i in range(11)]       # the foil's crinkled edge
    pen.line(X(zig))
    for y0 in (-3.0, -0.5, 2.0):                                                   # foil shine
        pen.line(X([(5.6, y0), (7.2, y0 - 1.2)]))
    pen.line(X([(-9.3, -1.8), (-7.6, -0.2), (-9.0, 2.4)]))                        # the tortilla's fold
    for ex in (-3.6, -0.2):                                                        # eyes
        (x, y), = X([(ex, -1.3)])
        pen.circle(x, y, 0.5 * s, fill=True)
    pen.line(X([(-2.9 + 0.25 * i, 0.6 + 0.9 * math.sin(math.pi * i / 10)) for i in range(11)]))  # smile
    for bx in (-5.2, 1.4):                                                         # blush
        pen.line(X([(bx, 0.9), (bx + 0.5, 0.4)]))
        pen.line(X([(bx + 0.5, 0.9), (bx + 1.0, 0.4)]))
    for sx in (-4.0, -1.0, 2.0):                                                   # steam
        pen.line(X([(sx + 0.6 * math.sin(i * math.pi / 3), -6.5 - i * 0.6) for i in range(7)]))


def find_spot(obstacles, w, h, size, prefer, margin=1.5, step=0.5):
    """Nearest free w x h box (centre) to `prefer` that clears every obstacle box and the board edge."""
    W, H = size
    px, py = prefer
    best = None
    for i in range(int((W - w - 2 * margin) / step) + 1):
        for j in range(int((H - h - 2 * margin) / step) + 1):
            x0, y0 = margin + i * step, margin + j * step
            box = (x0, y0, x0 + w, y0 + h)
            if any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] for b in obstacles):
                continue
            d = math.hypot(x0 + w / 2 - px, y0 + h / 2 - py)
            if best is None or d < best[0]:
                best = (d, x0 + w / 2, y0 + h / 2)
    return best[1:] if best else None


def board_art(board, origin, size, legend, name, version, lines):
    """Bottom: the name, version and team, a burrito with sparkles and steam, and the test point legend
    (TP number to net). Top: the name and version, small, and one sparkle. Each block goes to the free spot
    nearest its preferred place: clear of every pad that reaches that side (and, on top, of every courtyard
    and silk item). Returns {block: (x, y)} or None for a block with no room."""
    ox, oy = origin
    W, H = size
    box = lambda bb, g=0.0: (K.ToMM(bb.GetX()) - ox - g, K.ToMM(bb.GetY()) - oy - g,
                              K.ToMM(bb.GetRight()) - ox + g, K.ToMM(bb.GetBottom()) - oy + g)
    bottom, top = [], []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(K.B_Cu) or p.GetAttribute() == K.PAD_ATTRIB_NPTH:
                bottom.append(box(p.GetBoundingBox(), 0.6))
            top.append(box(p.GetBoundingBox(), 0.4))
        fp.BuildCourtyardCaches()
        cy = fp.GetCourtyard(K.F_CrtYd)
        if cy.OutlineCount():
            top.append(box(cy.BBox(), 0.2))
        for g in list(fp.GraphicalItems()) + list(fp.GetFields()):
            if g.GetLayer() == K.F_SilkS and (g.GetClass() == 'PCB_SHAPE' or g.IsVisible()):
                top.append(box(g.GetBoundingBox(), 0.3))
    for d in board.GetDrawings():
        if d.GetLayer() == K.Edge_Cuts:
            continue
    where = {}
    B = Pen(board, origin, K.B_SilkS)
    # title block, about 46 x 15 mm
    spot = find_spot(bottom, 46, 15, size, (W / 2, H * 0.38))
    where['title'] = spot
    if spot:
        x, y = spot
        B.text(x, y - 3.5, name, 6.0, bold=True)
        for i, l in enumerate(lines):
            B.text(x, y + 2.6 + 1.9 * i, l, 1.2)
        bottom.append((x - 23, y - 7.5, x + 23, y + 7.5))
    # the burrito, sparkles and steam, about 30 x 22 mm
    spot = find_spot(bottom, 30, 22, size, (W / 2, H * 0.2))
    where['burrito'] = spot
    if spot:
        x, y = spot
        burrito(B, x, y + 2.5, 1.05, rot=-12, mirror=True)
        for dx, dy, s in ((-12.5, -6.5, 1.6), (12.0, -7.5, 1.1), (13.0, 6.5, 1.8), (-13.0, 7.0, 1.0), (9.0, -9.5, 0.7)):
            sparkle(B, x + dx, y + dy, s)
        B.text(x, y + 10.2, 'PLUS ULTRA', 1.2, bold=True)
        bottom.append((x - 15, y - 11, x + 15, y + 11))
    # test point legend, TP number to net, in reading order seen from below: column 1 (TP1 on) on the left,
    # column 2 on the right; a column splits into two blocks if it doesn't fit whole
    lh, cw = 1.55, 27.0
    half = (len(legend) + 1) // 2
    cols = [legend[:half], legend[half:]]
    where['legend'] = []
    for c, entries in enumerate(cols):
        want = (W / 2 + (13.5 if c == 0 else -13.5), H * 0.70)      # mirrored: +x is the left seen from below
        for parts in (1, 2, 3):
            n = -(-len(entries) // parts)
            chunks = [entries[i:i + n] for i in range(0, len(entries), n)]
            trial, spots, w0 = list(bottom), [], want
            for k, blk in enumerate(chunks):
                h = (2.2 if c == 0 and k == 0 else 0.0) + len(blk) * lh + 0.4
                spot = find_spot(trial, cw, h, size, w0)
                if not spot:
                    break
                spots.append((spot, h, blk, c == 0 and k == 0))
                trial.append((spot[0] - cw / 2 - 0.5, spot[1] - h / 2 - 0.5, spot[0] + cw / 2 + 0.5, spot[1] + h / 2 + 0.5))
                w0 = (spot[0], spot[1] + h / 2 + 3)
            if len(spots) == len(chunks):
                break
        for (x, y), h, blk, head in spots:
            y0 = y - h / 2 + 0.2
            if head:
                B.text(x + cw / 2 - 0.5, y0 + 0.6, 'TEST POINTS', 1.2, bold=True, justify='left')
                y0 += 2.2
            for i, (tp, net) in enumerate(blk):
                B.text(x + cw / 2 - 0.5, y0 + i * lh + 0.6, f'{tp} {net.rsplit("/", 1)[-1]}', 1.0, justify='left')
            bottom.append((x - cw / 2 - 0.5, y - h / 2 - 0.5, x + cw / 2 + 0.5, y + h / 2 + 0.5))
            where['legend'].append([round(x, 1), round(y, 1), blk[0][0], blk[-1][0]])
    # top: name and version, small, and a sparkle
    T = Pen(board, origin, K.F_SilkS)
    tag = f'{name} {version}'
    w = 1.0 * 0.95 * len(tag) + 4.0
    spot = find_spot(top, w, 2.6, size, (W * 0.8, H * 0.82))
    where['top_tag'] = spot
    if spot:
        x, y = spot
        T.text(x - 1.2, y, tag, 1.2, bold=True)
        sparkle(T, x + w / 2 - 1.2, y, 1.0)
    return where
