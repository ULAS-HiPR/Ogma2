"""Silkscreen art and legends for the back of the board (Seán, 22 Nov 2026).

The back, top to bottom as seen from below: BURRITO in TeX Gyre Heros Bold (a free Helvetica clone,
vendored under layout/art/fonts with its licence) over its subtitle, the IF FOUND line, HOUSTON, the ULAS
HiPR logo (the team's own, from its website repository), then the test point legend on the left (all of
them, in one column at one pitch) and the board's parts on the right, and the burrito rocket where it fits
best, and an Ogham inscription across the top band. Waves cover the rest. Near any text, graphic or
exposed pin a wave breaks into dashes, then dots, then nothing, like a newspaper dot screen, instead of
stopping at a box. The drawing is original and made here from code; the halftones are dot screens whose
dot size follows a shading function.

Bottom-view coordinates: u across from the left as seen from below, v aft from the forward edge; u = W - x.
Lines are 0.15 mm or more and text 1.0 mm or more (JLC's silkscreen minimums)."""
import math
import re
import numpy as np
import pcbnew as K
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box as sbox
from shapely.ops import unary_union
from shapely.prepared import prep

MM = K.FromMM
LINE = 0.18                     # art lines (mm)
WAVE = 0.2                      # wave lines (mm)
GROW = 0.55                     # silk stays this far from exposed copper (mm)
RES = 0.05                      # raster of the waves' distance field (mm per pixel)


def uv_geom(ps, to_uv):
    """A KiCad SHAPE_POLY_SET as one shapely geometry, through `to_uv`."""
    out = []
    for i in range(ps.OutlineCount()):
        ol = ps.Outline(i)
        ext = [to_uv(ol.CPoint(j)) for j in range(ol.PointCount())]
        holes = []
        for h in range(ps.HoleCount(i)):
            hl = ps.Hole(i, h)
            holes.append([to_uv(hl.CPoint(j)) for j in range(hl.PointCount())])
        if len(ext) >= 3:
            out.append(Polygon(ext, [h for h in holes if len(h) >= 3]).buffer(0))
    return unary_union(out)


class Pen:
    """Draws on one silk layer and keeps what it drew, for the waves to dissolve around.
    Bottom: takes bottom-view (u, v) and mirrors. Top: takes (x, y)."""

    def __init__(self, board, origin, size, layer, width=LINE):
        self.b, (self.ox, self.oy), (self.W, self.H), self.layer, self.w = board, origin, size, layer, width
        self.bottom = layer == K.B_SilkS
        self.n = 0
        self.segs, self.dots, self.polys, self.texts = [], [], [], []
        self.bridges = []                  # not drawn: spans that hold a text row together against the waves

    def V(self, u, v):
        x = self.W - u if self.bottom else u
        return K.VECTOR2I(MM(float(self.ox + x)), MM(float(self.oy + v)))

    def UV(self, p):
        x = K.ToMM(p.x) - self.ox
        return (self.W - x if self.bottom else x, K.ToMM(p.y) - self.oy)

    def _add(self, s, fill=False, width=None):
        s.SetLayer(self.layer)
        s.SetWidth(MM(float(self.w if width is None else width)))
        if fill:
            s.SetFilled(True)
        self.b.Add(s)
        self.n += 1
        return s

    def line(self, pts, width=None):
        w = self.w if width is None else width
        for (a, b), (c, d) in zip(pts, pts[1:]):
            s = K.PCB_SHAPE(self.b)
            s.SetShape(K.SHAPE_T_SEGMENT)
            s.SetStart(self.V(a, b)); s.SetEnd(self.V(c, d))
            self._add(s, width=w)
            self.segs.append((a, b, c, d, w))

    def geom_lines(self, g, width=None):
        """Every line in a shapely geometry, as segments."""
        if g.is_empty:
            return
        for part in getattr(g, 'geoms', [g]):
            if part.geom_type == 'LineString':
                if part.length > 0.3:
                    self.line(list(part.coords), width)
            elif part.geom_type == 'LinearRing':
                self.line(list(part.coords), width)
            elif hasattr(part, 'geoms'):
                self.geom_lines(part, width)

    def polygon(self, poly):
        """A filled shapely polygon (holes allowed), fractured into KiCad's single-outline form."""
        for p in getattr(poly, 'geoms', [poly]):
            if p.is_empty or p.geom_type != 'Polygon' or p.area < 0.02:
                continue
            sps = K.SHAPE_POLY_SET()
            sps.NewOutline()
            for u, v in list(p.exterior.coords)[:-1]:
                q = self.V(u, v)
                sps.Append(q.x, q.y)
            for ring in p.interiors:
                h = sps.NewHole()
                for u, v in list(ring.coords)[:-1]:
                    q = self.V(u, v)
                    sps.Append(q.x, q.y, 0, h)
            sps.Fracture()
            s = K.PCB_SHAPE(self.b)
            s.SetShape(K.SHAPE_T_POLY)
            s.SetPolyShape(sps)
            self._add(s, fill=True, width=0)
            self.polys.append(p)

    def dot(self, u, v, d):
        """A filled circle of diameter d."""
        s = K.PCB_SHAPE(self.b)
        s.SetShape(K.SHAPE_T_CIRCLE)
        u, v, d = float(u), float(v), float(d)
        s.SetCenter(self.V(u, v)); s.SetEnd(self.V(u + d / 2, v))
        self._add(s, fill=True, width=0)
        self.dots.append((u, v, d))

    def text_shape(self, u, v, txt, h, bold=False, justify='left', wfac=1.0):
        """A text item, not yet on the board, and its ink. Bottom: (u, v) is the left end of the line as
        seen from below, or its middle (justify='center'). wfac narrows the letters, never their height."""
        t = K.PCB_TEXT(self.b)
        t.SetText(txt)
        t.SetLayer(self.layer)
        t.SetTextSize(K.VECTOR2I(MM(h * wfac), MM(h)))
        t.SetTextThickness(MM(max(0.15, h * (0.17 if bold else 0.11))))
        t.SetPosition(self.V(u, v))
        t.SetHorizJustify(K.GR_TEXT_H_ALIGN_CENTER if justify == 'center' else K.GR_TEXT_H_ALIGN_LEFT)
        t.SetVertJustify(K.GR_TEXT_V_ALIGN_CENTER)
        if self.bottom:
            t.SetMirrored(True)
        ps = K.SHAPE_POLY_SET()
        t.TransformTextToPolySet(ps, 0, MM(0.01), K.ERROR_INSIDE)
        return t, uv_geom(ps, self.UV)

    def put(self, t, ink, dv=0.0):
        """Put a text from text_shape on the board, dv further aft."""
        if dv:
            p = t.GetPosition()
            t.SetPosition(K.VECTOR2I(p.x, p.y + MM(dv)))
            ink = affinity.translate(ink, 0, dv)
        self.b.Add(t)
        self.n += 1
        self.texts.append(ink)
        return ink

    def text(self, u, v, txt, h, bold=False, justify='left', wfac=1.0):
        return self.put(*self.text_shape(u, v, txt, h, bold, justify, wfac))


def halftone(pen, region, shade, pitch=0.62, angle=45.0, dmin=0.24, dmax=0.56):
    """A newspaper dot screen over `region`: at each lattice point a dot whose area follows shade(u, v),
    0..1. Dots smaller than JLC prints (dmin) are left out."""
    if region.is_empty:
        return 0
    u0, v0, u1, v1 = region.bounds
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
    k = int((math.hypot(u1 - u0, v1 - v0) / 2 + pitch) / pitch) + 1
    pr = prep(region)
    n = 0
    for i in range(-k, k + 1):
        for j in range(-k, k + 1):
            a, b = i * pitch, j * pitch
            u, v = cu + a * c - b * s, cv + a * s + b * c
            if not pr.contains(Point(u, v)):
                continue
            d = dmax * math.sqrt(max(0.0, min(1.0, shade(u, v))))
            if d >= dmin:
                pen.dot(u, v, d)
                n += 1
    return n


def tongue(base, tip, w, n=32):
    """A flame tongue: round at `base`, `w` mm at its widest, tapering to a point at `tip`."""
    (x0, y0), (x1, y1) = base, tip
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    side = [[], []]
    for i in range(n + 1):
        t = i / n
        hw = w * (1 - t) ** 0.9 * min(1.0, (t + 0.08) / 0.25) ** 0.5
        cx, cy = x0 + t * (x1 - x0), y0 + t * (y1 - y0)
        side[0].append((cx - uy * hw, cy + ux * hw))
        side[1].append((cx + uy * hw, cy - ux * hw))
    leaf = Polygon(side[0] + side[1][::-1]).buffer(0)
    return leaf.union(Point(base).buffer(w * 0.566, resolution=16))


def capsule(cx, cy, length, r, n=24):
    pts = [(cx + length / 2 + r * math.cos(-math.pi / 2 + math.pi * i / n), cy + r * math.sin(-math.pi / 2 + math.pi * i / n))
           for i in range(n + 1)]
    pts += [(cx - length / 2 + r * math.cos(math.pi / 2 + math.pi * i / n), cy + r * math.sin(math.pi / 2 + math.pi * i / n))
            for i in range(n + 1)]
    return Polygon(pts)


def burrito_rocket(pen, cu, cv, s=1.0, tilt=0.0):
    """The burrito as a rocket: a halftone-shaded tortilla with grill marks and a wrap seam, crinkled foil
    with highlight streaks at the nose, sunglasses with glints over a wide grin, a three-tongued flame with
    a solid core fading out in halftone, and speed lines trailing it. About
    62 x 15 mm at s = 1. With pen=None it only returns the outline (grown 1.2 mm) for fitting; drawn, it
    returns the same outline."""
    T = lambda g: affinity.translate(affinity.rotate(affinity.scale(g, s, s, origin=(0, 0)), tilt, origin=(0, 0)), cu, cv)
    r, L = 7.5, 22.0
    body = capsule(3.0, 0.0, L, r)
    plume = unary_union([tongue((-12.5, 0.0), (-35.0, 0.0), 5.2), tongue((-13.0, -2.6), (-29.5, -6.8), 2.9),
                         tongue((-13.0, 2.6), (-29.5, 6.8), 2.9)]).difference(body)
    core = tongue((-12.5, 0.0), (-27.0, 0.0), 2.6).difference(body)
    speed = [(-7.2, -36.5, -29.6), (7.2, -36.5, -29.6), (-3.9, -40.0, -35.4), (3.9, -40.0, -35.4)]
    outline = T(unary_union([body, plume, sbox(-40.0, -7.5, -29.0, 7.5)]).buffer(1.2))
    if pen is None:
        return outline
    zig = LineString([(10.5 + (0.9 if i % 2 else 0.0), -8.0 + i * 1.6) for i in range(11)])
    foil = body.intersection(Polygon(list(zig.coords) + [(30, 8.0), (30, -8.0)]))
    tort = body.difference(foil)

    pen.geom_lines(T(body.exterior), 0.26)
    pen.geom_lines(T(zig.intersection(body)), 0.22)

    def tshade(u, v):                                   # a cylinder lit from above, with a highlight band
        p = affinity.rotate(Point(u - cu, v - cv), -tilt, origin=(0, 0))
        y = max(-1.0, min(1.0, p.y / s / r))
        band = math.exp(-((y + 0.42) / 0.16) ** 2)
        return 0.10 + 0.62 * ((y + 1) / 2) ** 1.7 - 0.18 * band
    face = sbox(-11.8, -4.4, 0.9, 3.6)
    halftone(pen, T(tort.buffer(-0.45).difference(face)), tshade)
    for xc in (3.4, 7.4):                               # toasted grill marks, between the face and the foil
        g = Polygon([(xc + 1.1, -6.4), (xc + 2.0, -6.4), (xc - 1.1, 6.4), (xc - 2.0, 6.4)])
        pen.polygon(T(g.intersection(tort.buffer(-1.0)).difference(face.buffer(0.4))))
    pen.geom_lines(T(LineString([(-12.6, -7.0), (-11.2, -3.0), (-11.0, 1.0), (-12.4, 7.0)]).intersection(body)), 0.2)
    hatch = unary_union([LineString([(8.0 + k * 0.9, -10), (14.0 + k * 0.9, 10)]) for k in range(-14, 22)])
    streaks = unary_union([LineString([(13.0, -7), (17.5, 7)]).buffer(0.55), LineString([(16.2, -7), (20.0, 5)]).buffer(0.35)])
    pen.geom_lines(T(hatch.intersection(foil.buffer(-0.5)).difference(streaks)), 0.18)
    for lx in (-8.4, -3.0):                             # sunglasses
        lens = Polygon([(lx - 2.3, -3.3), (lx + 2.3, -3.3), (lx + 1.9, -0.6), (lx - 1.6, -0.6)]).buffer(0.35)
        glint = LineString([(lx - 1.2, -2.6), (lx - 0.2, -1.4)]).buffer(0.22)
        pen.polygon(T(lens.difference(glint)))
    pen.polygon(T(sbox(-10.7, -3.75, -0.7, -3.2)))
    pen.polygon(T(sbox(-6.0, -2.9, -5.4, -2.4)))
    arc = lambda a: (-5.7 + 3.3 * math.cos(math.radians(a)), -0.9 + 3.3 * math.sin(math.radians(a)))
    pen.polygon(T(LineString([arc(a) for a in range(38, 143, 5)]).buffer(0.3)))      # a wide grin
    for a, d in ((38, 1), (142, -1)):                   # its dimples
        x, y = arc(a)
        pen.line([tuple(T(Point(x + 0.1 * d, y - 0.5)).coords[0]), tuple(T(Point(x + 0.45 * d, y + 0.35)).coords[0])], 0.2)
    pen.geom_lines(T(plume.exterior), 0.2)              # the flame: solid core, halftone glow fading out
    pen.polygon(T(core))
    nozzle = T(Point(-13.0, 0))
    halftone(pen, T(plume.difference(core.buffer(0.45)).buffer(-0.35)),
             lambda u, v: 0.95 - 0.75 * min(1.0, Point(u, v).distance(nozzle) / (21.0 * s)), pitch=0.58, angle=15.0)
    for y0, x0, x1 in speed:
        pen.geom_lines(T(LineString([(x0, y0), (x1, y0)])), 0.22)
    return outline


def logo_polys(png, width):
    """The ULAS HiPR logo from its PNG: every opaque pixel that isn't black is ink, so it reads as the logo
    does on a dark background. Traced with OpenCV, `width` mm wide, centred on (0, 0). Returns it and its
    height."""
    import cv2
    im = cv2.imread(png, cv2.IMREAD_UNCHANGED)
    rgb, a = im[:, :, :3].astype(float), im[:, :, 3]
    lum = 0.299 * rgb[:, :, 2] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 0]
    ink = ((a > 127) & (lum > 60)).astype(np.uint8) * 255
    cs, hier = cv2.findContours(ink, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    k = width / im.shape[1]
    h0, w0 = im.shape[0] / 2, im.shape[1] / 2
    pts = lambda c: [((p[0][0] - w0) * k, (p[0][1] - h0) * k) for p in cv2.approxPolyDP(c, 0.8, True)]
    polys = []
    for i, c in enumerate(cs):
        if hier[0][i][3] >= 0 or len(c) < 3:
            continue
        holes = [pts(cs[j]) for j in range(len(cs)) if hier[0][j][3] == i and len(cs[j]) >= 3]
        p = Polygon(pts(c), [h for h in holes if len(h) >= 3]).buffer(0)
        if not p.is_empty:
            polys.append(p)
    return unary_union(polys), im.shape[0] * k


def word_polys(font, text, cap_h):
    """`text` set in an OpenType font as filled polygons, cap height `cap_h` mm, centred on (0, 0), v down.
    Curves are flattened finely; contours combine even-odd, so counters stay open."""
    from fontTools.pens.basePen import BasePen
    from fontTools.ttLib import TTFont
    f = TTFont(font)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f['hmtx']
    k = cap_h / f['OS/2'].sCapHeight

    class Flat(BasePen):
        def __init__(self, glyphs):
            super().__init__(glyphs)
            self.rings, self.cur = [], []

        def _moveTo(self, p):
            self.cur = [p]

        def _lineTo(self, p):
            self.cur.append(p)

        def _curveToOne(self, p1, p2, p3):
            x0, y0 = self.cur[-1]
            for i in range(1, 17):
                t = i / 16
                q = 1 - t
                self.cur.append((q ** 3 * x0 + 3 * q * q * t * p1[0] + 3 * q * t * t * p2[0] + t ** 3 * p3[0],
                                 q ** 3 * y0 + 3 * q * q * t * p1[1] + 3 * q * t * t * p2[1] + t ** 3 * p3[1]))

        def _qCurveToOne(self, p1, p2):
            x0, y0 = self.cur[-1]
            for i in range(1, 13):
                t = i / 12
                q = 1 - t
                self.cur.append((q * q * x0 + 2 * q * t * p1[0] + t * t * p2[0], q * q * y0 + 2 * q * t * p1[1] + t * t * p2[1]))

        def _closePath(self):
            if len(self.cur) >= 3:
                self.rings.append(self.cur)
            self.cur = []

        def _endPath(self):
            self._closePath()

    x, parts = 0.0, []
    for ch in text:
        g = cmap[ord(ch)]
        pen = Flat(gs)
        gs[g].draw(pen)
        shape = Polygon()
        for ring in pen.rings:
            shape = shape.symmetric_difference(Polygon([(x + a, b) for a, b in ring]).buffer(0))
        parts.append(shape)
        x += hmtx[g][0]
    word = affinity.scale(unary_union(parts), k, -k, origin=(0, 0))
    b = word.bounds
    return affinity.translate(word, -(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2)


OGHAM = {   # letter: (group, strokes). Reading up the stem: b = strokes to its right, h = to its left,
            # m = oblique strokes across it, a = short strokes across it (the vowels)
    'B': ('b', 1), 'L': ('b', 2), 'F': ('b', 3), 'S': ('b', 4), 'N': ('b', 5),
    'H': ('h', 1), 'D': ('h', 2), 'T': ('h', 3), 'C': ('h', 4), 'Q': ('h', 5),
    'M': ('m', 1), 'G': ('m', 2), 'Z': ('m', 4), 'R': ('m', 5),
    'A': ('a', 1), 'O': ('a', 2), 'U': ('a', 3), 'E': ('a', 4), 'I': ('a', 5)}


def ogham(text, pitch=1.0, reach=2.3, notch=0.9, slant=1.0, gap=1.5, space=3.4, tail=2.2):
    """`text` in Ogham, the script the Ogam Tract credits to Ogma, as strokes about a stem: a list of
    ((n0, t0), (n1, t1)), t along the reading direction and n across it, and the stem's length. +n is
    below the line when it's written left to right, and the right-hand side when it runs up a stone's
    edge. Four groups of five letters, one to five strokes each; a space is a bare stretch of stem."""
    segs, t = [], tail
    for wi, word in enumerate(text.split()):
        t += (space - gap) if wi else 0.0
        for ch in word:
            grp, n = OGHAM[ch]
            e = slant if grp == 'm' else 0.0
            t += e
            for i in range(n):
                ti = t + i * pitch
                segs.append({'b': ((0.0, ti), (reach, ti)), 'h': ((-reach, ti), (0.0, ti)),
                             'm': ((reach, ti - slant), (-reach, ti + slant)), 'a': ((-notch, ti), (notch, ti))}[grp])
            t += (n - 1) * pitch + e + gap
    return segs, t - gap + tail


def raster(pen, hard, size, res, close=0.0, close_text=1.6):
    """Everything the pen drew, and the copper, as a 0/1 mask (rows v, columns u). Art is closed by `close`
    mm and text by `close_text` mm, so the gaps between letters, words and lines fill in."""
    import cv2
    W, H = size
    S = 1.0 / res
    shape = (int(H * S) + 2, int(W * S) + 2)

    def fill(m, g):
        for p in getattr(g, 'geoms', [g]):
            if p.is_empty or p.geom_type != 'Polygon':
                continue
            cv2.fillPoly(m, [np.round(np.asarray(p.exterior.coords) * S).astype(np.int32)], 1)

    def closed(m, r):
        if not r:
            return m
        k = 2 * round(r * S) + 1
        return cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    art, txt = np.zeros(shape, np.uint8), np.zeros(shape, np.uint8)
    for g in pen.polys:
        fill(art, g)
    for a, b, c, d, w in pen.segs:
        cv2.line(art, (round(a * S), round(b * S)), (round(c * S), round(d * S)), 1, max(1, round(w * S)))
    for u, v, d in pen.dots:
        cv2.circle(art, (round(u * S), round(v * S)), max(1, round(d / 2 * S)), 1, -1)
    for g in pen.texts + pen.bridges:
        fill(txt, g)
    m = closed(art, close) | closed(txt, close_text)
    fill(m, hard)
    return m


def fit_shape(block, res, shape, window, anchor):
    """The centre nearest `anchor`, inside `window` (u0, v0, u1, v1), where `shape` (drawn about 0, 0) misses
    every set cell of `block` (a res-mm mask, rows v). FFT cross-correlation of the mask with the shape."""
    import cv2
    b = shape.bounds
    kh, kw = int((b[3] - b[1]) / res) + 3, int((b[2] - b[0]) / res) + 3
    ker = np.zeros((kh, kw), np.float32)
    for p in getattr(shape, 'geoms', [shape]):
        pts = (np.asarray(p.exterior.coords) - (b[0] - res, b[1] - res)) / res
        cv2.fillPoly(ker, [np.round(pts).astype(np.int32)], 1.0)
    Hh, Ww = block.shape
    F = np.fft.rfft2(block.astype(np.float32), s=(Hh, Ww))
    G = np.fft.rfft2(ker, s=(Hh, Ww))
    hit = np.fft.irfft2(F * np.conj(G), s=(Hh, Ww))
    ci, cj = (0 - (b[1] - res)) / res, (0 - (b[0] - res)) / res      # the shape's (0, 0) in the kernel
    ii, jj = np.mgrid[0:Hh - kh, 0:Ww - kw]
    u, v = (jj + cj) * res, (ii + ci) * res
    ok = (hit[:Hh - kh, :Ww - kw] < 0.5) & (u >= window[0]) & (u <= window[2]) & (v >= window[1]) & (v <= window[3])
    if not ok.any():
        return None
    d = np.where(ok, np.hypot(u - anchor[0], v - anchor[1]), np.inf)
    i, j = np.unravel_index(np.argmin(d), d.shape)
    return round(float(u[i, j]), 2), round(float(v[i, j]), 2)


def wave_v(u, v0):
    return v0 + 2.3 * np.sin(2 * np.pi * u / 27 + v0 / 8.5) + 1.1 * np.sin(2 * np.pi * u / 9.4 + v0 / 3.7)


def waves(pen, hard, size, d0=0.45, d1=2.1, period=0.62, pitch=1.7, edge=1.0, close=1.0):
    """The wave field. Where a wave nears ink or copper (closer than d1 mm) it breaks into dashes that
    shorten, then dots that shrink, and it stops d0 mm short; it never just ends at a box. The dashes sit
    on a staggered grid, so the breakup reads as a dot screen. Returns the number of items drawn."""
    import cv2
    W, H = size
    m = raster(pen, hard, size, RES, close)
    dist = cv2.distanceTransform((1 - m).astype(np.uint8), cv2.DIST_L2, 5) * RES - WAVE / 2
    nr, nc = dist.shape
    frame = prep(sbox(edge, edge, W - edge, H - edge))
    n0 = pen.n
    for n, v0 in enumerate(np.arange(-4.0, H + 4.0, pitch)):
        us = (np.arange(-1, int(W / period) + 2) + 0.5 * (n % 2)) * period
        vs = wave_v(us, v0)
        inside = (us >= edge) & (us <= W - edge) & (vs >= edge) & (vs <= H - edge)
        dd = dist[np.clip(np.round(vs / RES).astype(int), 0, nr - 1), np.clip(np.round(us / RES).astype(int), 0, nc - 1)]
        t = np.where(inside, np.clip((dd - d0) / (d1 - d0), 0.0, 1.0), 0.0)
        k = 0
        while k < len(us):
            if t[k] >= 1.0:                             # a solid run, to half a period past its ends
                j = k
                while j + 1 < len(us) and t[j + 1] >= 1.0:
                    j += 1
                uu = np.append(np.arange(us[k] - period / 2, us[j] + period / 2, 0.15), us[j] + period / 2)
                run = LineString(np.column_stack([uu, wave_v(uu, v0)])).simplify(0.02)
                cut = run.intersection(sbox(edge, edge, W - edge, H - edge))
                pen.geom_lines(cut, WAVE)
                k = j + 1
                continue
            if t[k] > 0.25:                             # a dash, shorter the closer it is
                half = (period - WAVE) * t[k] ** 1.3 / 2
                uu = np.array([us[k] - half, us[k], us[k] + half])
                pts = list(zip(uu, wave_v(uu, v0)))
                if all(frame.contains(Point(p)) for p in pts):
                    pen.line(pts, WAVE)
            elif t[k] > 0.04:                           # then a dot, smaller the closer it is
                pen.dot(us[k], vs[k], 0.2 + 0.15 * t[k])
            k += 1
    return pen.n - n0


def board_art(board, origin, size, legend, name, version, lines, specs, logo, found, title_font, place,
              ogham_text=None, reserved=()):
    """Draw the back and the top tag. Returns where each block went (bottom-view mm) and counts."""
    ox, oy = origin
    W, H = size
    B = Pen(board, origin, size, K.B_SilkS)
    where = {}

    # exposed copper on the back, at its real shape: pads, rings and holes, grown by GROW
    cu = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(K.B_Cu) or p.GetAttribute() == K.PAD_ATTRIB_NPTH:
                cu.append(uv_geom(p.GetEffectivePolygon(K.B_Cu, K.ERROR_INSIDE), B.UV))
                dr = p.GetDrillSize()
                if max(dr.x, dr.y) > 0:
                    cu.append(Point(B.UV(p.GetPosition())).buffer(K.ToMM(max(dr.x, dr.y)) / 2))
    copper = unary_union(cu).buffer(GROW)
    rsv = [sbox(W - x1, y0, W - x0, y1) for x0, y0, x1, y1 in reserved]          # J101: its pins come later
    hard = unary_union([copper] + rsv)
    hp = prep(hard)
    clear = lambda g: not hp.intersects(g)
    misses = []

    # 1. BURRITO and its subtitle, where Seán saw them on 22 Nov, the name in Helvetica-style bold
    word = word_polys(title_font, name, place['cap'])
    tv = place['title']
    wd = affinity.translate(word, W / 2, tv)
    B.polygon(wd)
    B.bridges.append(wd.buffer(2.0).buffer(-2.0))
    sub = [B.text(W / 2, place['lines'] + 2.1 * i, l, 1.3, justify='center') for i, l in enumerate(lines)]
    where['title'] = {'v': tv, 'width': round(word.bounds[2] - word.bounds[0], 2), 'cap': place['cap']}
    if not clear(wd) or not all(clear(g) for g in sub):
        misses.append('title')

    # 2. IF FOUND, where Seán liked it
    fi = B.text(W / 2, place['found'], found, 1.0, justify='center')
    where['found'] = [W / 2, place['found']]
    if not clear(fi):
        misses.append('found')

    # 3. the test point legend: all of it, one column, one pitch; the pitch and the start are the biggest
    # and lowest that clear every pin, so the logo above moves up as little as it can
    u0, gap_head, gap_logo, lw = 7.8, 2.2, 4.0, 0.95       # lw: the legend's letters 5% narrower, same height
    labels = [B.text_shape(u0, 0.0, t, 1.0, wfac=lw) for t, _ in legend]
    tab = max(g.bounds[2] for _, g in labels) - u0 + 0.85  # every net starts in one column
    names = [B.text_shape(u0 + tab, 0.0, n.rsplit('/', 1)[-1], 1.0, wfac=lw) for _, n in legend]
    head = B.text_shape(u0, 0.0, 'TEST POINTS', 1.3, bold=True)
    boxes = [(a[1].bounds[0], min(a[1].bounds[1], b[1].bounds[1]), b[1].bounds[2], max(a[1].bounds[3], b[1].bounds[3]))
             for a, b in zip(labels, names)]               # a row's box runs from its label to its net's end
    hb = head[1].bounds
    lp, lh = logo_polys(logo, 58.0)
    lt, lb = lp.bounds[1], lp.bounds[3]                # the logo's ink above and below its centre
    logo_was = place['logo']
    cands = []
    for p in np.arange(1.50, 1.355, -0.01):
        p = round(float(p), 2)
        for v1 in np.arange(115.0, 100.0, -0.05):
            v1 = round(float(v1), 2)
            if v1 + (len(boxes) - 1) * p + boxes[-1][3] > H - 9.0:        # stays above J102's row
                continue
            if not clear(sbox(hb[0], hb[1] + v1 - gap_head, hb[2], hb[3] + v1 - gap_head)):
                continue
            if all(clear(sbox(b[0], b[1] + v1 + k * p, b[2], b[3] + v1 + k * p)) for k, b in enumerate(boxes)):
                cands.append((p, v1, min(logo_was - 2.0, v1 - gap_head + hb[1] - gap_logo - lb)))
                break
    if not cands:
        raise RuntimeError('the test point legend fits nowhere on the back: check PROBE_MOVES')
    near = [c for c in cands if logo_was - c[2] <= 3.6]     # Sean: the logo up "a couple of millimetres"
    pitch, v1, logo_v = max(near, key=lambda c: c[0]) if near else max(cands, key=lambda c: c[2])
    where['legend_options'] = [list(c) for c in cands[:6]]
    B.put(*head, dv=v1 - gap_head)
    legend_ink = []
    for k, (a, b) in enumerate(zip(labels, names)):
        ga, gb = B.put(*a, dv=v1 + k * pitch), B.put(*b, dv=v1 + k * pitch)
        B.bridges.append(sbox(ga.bounds[2] - 0.2, min(ga.bounds[1], gb.bounds[1]), gb.bounds[0] + 0.2, max(ga.bounds[3], gb.bounds[3])))
        legend_ink += [ga, gb]
    where['legend'] = {'pitch': pitch, 'first': v1, 'last': round(v1 + (len(labels) - 1) * pitch, 2), 'lines': len(labels),
                       'net_column': round(u0 + tab, 2)}

    # 4. the logo, centred, as near where Seán saw it as the waves above the column heads allow
    for dv in np.arange(0.0, 3.0, 0.1):
        g = affinity.translate(lp, W / 2, logo_v - dv)
        if clear(g.buffer(0.3)):
            logo_v = round(float(logo_v - dv), 2)
            break
    else:
        misses.append('logo')
    B.polygon(affinity.translate(lp, W / 2, logo_v))
    B.bridges.append(affinity.translate(lp, W / 2, logo_v).buffer(3.0).buffer(-3.0))   # no waves inside its letters
    where['logo'] = {'v': logo_v, 'up_mm': round(logo_was - logo_v, 2), 'width': 58.0}

    # 5. HOUSTON: centred across the board, and midway between IF FOUND and the logo
    mid = (fi.bounds[3] + logo_v + lt) / 2
    for wfac in (1.0, 0.97, 0.94):
        t, g = B.text_shape(W / 2, 0.0, 'HOUSTON, WE HAVE A BURRITO', 1.0, bold=True, justify='center', wfac=wfac)
        gb = g.bounds
        dv = mid - (gb[1] + gb[3]) / 2
        if clear(affinity.translate(g, 0, dv)):
            B.put(t, g, dv=dv)
            where['houston'] = {'v': round(mid, 2), 'width_factor': wfac}
            break
    else:
        misses.append('houston')

    # 6. the board's parts: one block on the right, at the first place below the column heads where all of
    # it clears the pins and the legend
    su, sv = 32.0, 40.7                                # labels, and the values in their own column
    shead = B.text_shape(su, 0.0, 'THIS BOARD', 1.3, bold=True)
    srows = []
    for s in specs:
        parts = re.split(r'\s{2,}', s.strip(), maxsplit=1) if s else []
        if not parts:
            srows.append(None)
            continue
        ts = [B.text_shape(su, 0.0, parts[0], 1.0)] + ([B.text_shape(sv, 0.0, parts[1], 1.0)] if len(parts) > 1 else [])
        srows.append((ts, unary_union([g for _, g in ts])))
    used = unary_union(legend_ink).buffer(0.6)
    placed_specs, spec_ink = None, []
    for sp in (1.4, 1.35, 1.3):
        offs, v = [], gap_head
        for r in srows:
            offs.append(None if r is None else v)
            v += 0.9 if r is None else sp
        for v0 in np.arange(v1 - gap_head, H - 10.0, 0.25):
            v0 = float(v0)
            gs = [affinity.translate(shead[1], 0, v0)] + [affinity.translate(r[1], 0, v0 + o)
                                                          for r, o in zip(srows, offs) if r is not None]
            if all(clear(g) and not used.intersects(g) for g in gs):
                placed_specs = (sp, v0, offs)
                break
        if placed_specs:
            break
    if placed_specs:
        sp, v0, offs = placed_specs
        spec_ink.append(B.put(*shead, dv=v0))
        for r, o in zip(srows, offs):
            if r is not None:
                gs = [B.put(tt, g, dv=v0 + o) for tt, g in r[0]]
                spec_ink += gs
                if len(gs) == 2:                       # no waves between a label and its value
                    a, b = gs[0].bounds, gs[1].bounds
                    B.bridges.append(sbox(a[2] - 0.2, min(a[1], b[1]), b[0] + 0.2, max(a[3], b[3])))
        where['specs'] = {'pitch': sp, 'head': round(v0, 2), 'end': round(v0 + offs[-1], 2)}
    else:
        misses.append('specs')

    # 6b. an inscription in Ogham across the top band, over the name: written along a line as in the
    # manuscripts, left to right, between feather marks (Claude's addition, 22 Nov, at Seán's invitation;
    # ogham_text=None drops it). The right-hand side, where a stone's edge would run, is J101's.
    if ogham_text:
        segs, length = ogham(ogham_text)
        reach = max(abs(a[0]) for a, _ in segs)
        top_of_name = wd.bounds[1]
        spot = None
        for sv_ in np.arange(20.6, 17.4, -0.2):
            for du in (0.0, -1.0, 1.0, -2.0, 2.0, -3.0, 3.0):
                sv_, us_ = round(float(sv_), 2), round(W / 2 - length / 2 + du, 2)
                strokes = [LineString([(us_ + a[1], sv_ + a[0]), (us_ + b[1], sv_ + b[0])]) for a, b in segs]
                stem = LineString([(us_ + 0.9, sv_), (us_ + length - 0.9, sv_)])
                marks = [LineString([(us_, sv_ - 1.2), (us_ + 0.9, sv_), (us_, sv_ + 1.2)]),
                         LineString([(us_ + length, sv_ - 1.2), (us_ + length - 0.9, sv_), (us_ + length, sv_ + 1.2)])]
                g = unary_union(strokes + marks + [stem]).buffer(0.5)
                if clear(g) and sv_ + reach + 3.5 <= top_of_name:
                    spot = (us_, sv_, strokes, stem, marks)
                    break
            if spot:
                break
        if spot:
            us_, sv_, strokes, stem, marks = spot
            for g in [stem] + marks + strokes:
                B.geom_lines(g, 0.3)
            B.bridges.append(sbox(us_ - 0.3, sv_ - reach, us_ + length + 0.3, sv_ + reach))   # one band to the waves
            where['ogham'] = {'text': ogham_text, 'stem_v': sv_, 'from_u': us_, 'to_u': round(us_ + length, 2),
                              'strokes': len(strokes)}
        else:
            misses.append('ogham')

    # 7. the burrito rocket: as big as fits clear of everything with room for waves, between the title and
    # IF FOUND first, then the lower right, then the top band
    rb = 0.25
    import cv2
    blk = raster(B, hard, size, rb, close=1.0)
    k = 2 * round(1.6 / rb) + 1                        # 1.6 mm, plus the rocket's own 1.2: room for dots
    blk = cv2.dilate(blk, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    e = round(1.5 / rb)
    blk[:e, :] = blk[-e:, :] = 1
    blk[:, :e] = blk[:, -e:] = 1
    band = (wd.bounds[3] if not sub else max(g.bounds[3] for g in sub), fi.bounds[1])   # under the subtitle, over IF FOUND
    windows = [('under the title', (1, 42, W - 1, 58), (W / 2, (band[0] + band[1]) / 2)),
               ('lower right', (30, 112, W - 1, H - 1), (56, 158)), ('top band', (1, 10, W - 1, 28), (W / 2, 18))]
    found_at = {}
    for nm, win, anc in windows:
        for s in np.arange(0.95, 0.38, -0.05):
            hit = None
            for tilt in (0, -4, 4, -8):
                shape = burrito_rocket(None, 0, 0, float(s), tilt)
                b = shape.bounds                        # centre the whole rocket, flame and all, on the anchor
                a = (anc[0] - (b[0] + b[2]) / 2, anc[1] - (b[1] + b[3]) / 2)
                c = fit_shape(blk, rb, shape, win, a)
                if c and (nm != 'under the title' or abs(c[0] - a[0]) <= 3.0):
                    hit = (round(float(s), 2), tilt, c)
                    break
            if hit:
                found_at[nm] = hit
                break
    where['burrito_options'] = found_at
    pick = found_at.get('under the title') or max(found_at.values(), key=lambda h: h[0], default=None)
    if pick:
        s, tilt, (bu, bv) = pick
        out = burrito_rocket(None, bu, bv, s, tilt)
        if clear(out):
            burrito_rocket(B, bu, bv, s, tilt)
            where['burrito'] = {'at': [bu, bv], 'scale': s, 'tilt': tilt}
        else:
            misses.append('burrito')
    else:
        misses.append('burrito')

    # 8. the waves, dissolving around everything above
    where['wave_items'] = waves(B, copper, size)           # over J101's reservation too: rebuilt round its pins

    # top: name and version, small, clear of everything on the top side
    T = Pen(board, origin, size, K.F_SilkS)
    tag = f'{name} {version}'
    tv = lambda bb, g: sbox(K.ToMM(bb.GetX()) - ox - g, K.ToMM(bb.GetY()) - oy - g, K.ToMM(bb.GetRight()) - ox + g, K.ToMM(bb.GetBottom()) - oy + g)
    tops = []
    for fp in board.GetFootprints():
        tops += [tv(pd.GetBoundingBox(), 0.4) for pd in fp.Pads()]
        fp.BuildCourtyardCaches()
        cy = fp.GetCourtyard(K.F_CrtYd)
        if cy.OutlineCount():
            tops.append(tv(cy.BBox(), 0.2))
        tops += [tv(g.GetBoundingBox(), 0.3) for g in list(fp.GraphicalItems()) + list(fp.GetFields())
                 if g.GetLayer() == K.F_SilkS and (g.GetClass() == 'PCB_SHAPE' or g.IsVisible())]
    topu = prep(unary_union(tops))
    w = 1.2 * 0.95 * len(tag)
    best = None
    for i in range(int((W - w - 2) / 0.5) + 1):
        for j in range(int((H - 4) / 0.5) + 1):
            r = sbox(1 + i * 0.5, 1 + j * 0.5, 1 + i * 0.5 + w, 3.4 + j * 0.5)
            d = math.hypot(r.centroid.x - W * 0.8, r.centroid.y - H * 0.82)
            if (best is None or d < best[0]) and not topu.intersects(r):
                best = (d, r.centroid.x, r.centroid.y)
    where['top_tag'] = best and [round(best[1], 1), round(best[2], 1)]
    if best:
        T.text(best[1], best[2], tag, 1.2, bold=True, justify='center')
    where['misses'] = misses
    where['items'] = B.n + T.n
    return where
