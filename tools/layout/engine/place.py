"""Constructive placement: fixed parts from the spec, anchors, then every other part pulled to the
pads it serves, inside its region, with courtyards clear and JLC's SMD spacing between bodies.

Board-local mm, y down. Rotations are KiCad's (degrees, counter-clockwise on screen)."""
import math
import re
import pcbnew as K

TOMM = K.ToMM
ROTS = (0, 90, 180, 270)
CELL = 5.0

# JLC's minimum spacing between SMD parts, pad or body edge to pad or body edge, mm
# (https://jlcpcb.com/help/article/minimum-spacing-for-smd-components, updated 9 Sep 2026).
CHIP = {'0201': 0, '0402': 0, '0603': 1, '0805': 1, '1206': 2, '1210': 2, '2512': 2}
JLC = {('QFN', 'QFN'): 1.0, ('QFN', 'QFP'): 1.0, ('QFN', 'SOP'): 1.0, ('QFN', 'SOT'): 1.0,
       ('QFP', 'QFP'): 1.25, ('QFP', 'SOP'): 1.25, ('QFP', 'SOT'): 1.0,
       ('SOP', 'SOP'): 0.5, ('SOP', 'SOT'): 0.4, ('SOT', 'SOT'): 0.4,
       ('chip', 'QFN'): 1.0, ('chip', 'QFP'): 0.5, ('chip', 'SOP'): 0.4, ('chip', 'SOT'): 0.2}
OTHER = 0.3          # anything the table doesn't cover (connectors, modules, cans, crystals) [J]


def pkg_class(fid):
    n = fid.split(':', 1)[-1].upper()
    m = re.match(r'(?:C|R|L|D|LED|FUSE)_(\d{4})_', n)
    if m:
        return 'chip', m.group(1)
    if re.search(r'QFN|DFN|SON|LGA|WQFN|VQFN|S-PDSO-N|DQK|TDSON|RDH|RPW', n) or n.startswith(('TPS2121', 'TPS26630', 'TCAN3413', 'TPS3430', 'TPS7A91', 'LM73100', 'TPSM636', 'CSD173', 'CSD185', 'MMC5983', 'ICM-426', 'LSM6DSV', 'ADXL375', 'BMP390', 'MS5607', 'MS5607')):
        return 'QFN', None
    if 'QFP' in n or n.startswith('STM32'):
        return 'QFP', None
    if re.search(r'SOIC|SSOP|TSSOP|MSOP|VSSOP|HTSSOP|PWP', n) or n.startswith(('TMUX1511', 'TXU0304', 'TXU0202', 'INA228', 'SN74LVC1G74', 'MX66L', 'TPS1H100')):
        return 'SOP', None
    if re.search(r'SOT|SC-70|SC70', n) or n.startswith(('SN74LVC1G97', 'TPS22918', 'TPS2553', 'TPS3700', 'TPS3808', 'TPS70933', 'TXU0101', 'SN74LVC1G08')):
        return 'SOT', None
    return 'other', None


def jlc_gap(a, b):
    (ca, sa), (cb, sb) = a, b
    if ca == 'other' or cb == 'other':
        return OTHER
    if ca == 'chip' and cb == 'chip':
        ga, gb = CHIP.get(sa, 1), CHIP.get(sb, 1)
        if ga == 2 and gb == 2:
            return 0.35
        return (0.15, 0.18, 0.25)[max(ga, gb)]
    key = (ca, cb) if (ca, cb) in JLC else (cb, ca)
    return JLC.get(key, OTHER)


def geometry(fp, label=False, label_text=None, apart=None):
    """Per rotation: courtyard box, body+pad envelope box (local mm) and pad offsets.
    label: a reference visible on the silkscreen counts as courtyard, so no part covers it (D-22Nov.9).
    label_text: size that box for this text instead of the ref (test points: 'TP00', so renumbering them
    can't change their boxes, and so can't move them).
    apart: a silk text left out of the box (a name set further off than usual, with room for parts between; or a
    ref whose box would otherwise span the part's whole side: the MCUs', D-23Nov.1); the Placer keeps it clear as a
    box of its own."""
    g = {}
    ref_text = fp.Reference().GetText()
    if label_text:
        fp.Reference().SetText(label_text)
    for a in ROTS:
        fp.SetOrientationDegrees(a)
        fp.SetPosition(K.VECTOR2I(0, 0))
        fp.BuildCourtyardCaches()
        cy = fp.GetCourtyard(K.F_CrtYd)
        bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False, False)
        crt = (TOMM(bb.GetX()), TOMM(bb.GetY()), TOMM(bb.GetRight()), TOMM(bb.GetBottom()))
        texts = [f for f in fp.GetFields() if f.IsVisible() and f.GetLayer() == K.F_SilkS and f.GetText() != apart]
        texts += [g for g in fp.GraphicalItems() if g.GetClass() == 'PCB_TEXT' and g.GetLayer() == K.F_SilkS
                  and g.GetText() != apart]
        for tx in texts if label else []:              # the ref and any pin-1 mark printed on silk
            tb = tx.GetBoundingBox()
            crt = (min(crt[0], TOMM(tb.GetX())), min(crt[1], TOMM(tb.GetY())),
                   max(crt[2], TOMM(tb.GetRight())), max(crt[3], TOMM(tb.GetBottom())))
        xs, ys = [], []
        for p in fp.Pads():
            pb = p.GetBoundingBox()
            xs += [TOMM(pb.GetX()), TOMM(pb.GetRight())]; ys += [TOMM(pb.GetY()), TOMM(pb.GetBottom())]
        for gi in fp.GraphicalItems():
            if gi.GetLayer() == K.F_Fab and gi.GetClass() != 'PCB_TEXT':
                gb = gi.GetBoundingBox()
                xs += [TOMM(gb.GetX()), TOMM(gb.GetRight())]; ys += [TOMM(gb.GetY()), TOMM(gb.GetBottom())]
        env = (min(xs), min(ys), max(xs), max(ys)) if xs else crt
        pads = {}
        for p in fp.Pads():
            q = p.GetPosition()
            pads.setdefault(p.GetNumber(), []).append((TOMM(q.x), TOMM(q.y)))
        g[a] = (crt, env, pads)
    fp.SetOrientationDegrees(0)
    fp.Reference().SetText(ref_text)
    return g


def text_boxes(fp, text):
    """Per rotation: the local box of the footprint's top silk text `text` (a text, or a field such as its ref)."""
    g = {}
    for a in ROTS:
        fp.SetOrientationDegrees(a)
        fp.SetPosition(K.VECTOR2I(0, 0))
        tb = next(t for t in [*fp.GetFields(), *fp.GraphicalItems()] if t.GetClass() in ('PCB_TEXT', 'PCB_FIELD')
                  and t.GetLayer() == K.F_SilkS and t.GetText() == text).GetBoundingBox()
        g[a] = (TOMM(tb.GetX()), TOMM(tb.GetY()), TOMM(tb.GetRight()), TOMM(tb.GetBottom()))
    fp.SetOrientationDegrees(0)
    return g


def overlap(a, b, gap=0.0):
    return a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap


def box_gap(a, b):
    dx = max(b[0] - a[2], a[0] - b[2], 0.0)
    dy = max(b[1] - a[3], a[1] - b[3], 0.0)
    return math.hypot(dx, dy) if dx and dy else max(dx, dy)


def _mst(pts):
    """Prim's spanning tree over points: [(i, j)]."""
    n = len(pts)
    if n < 2:
        return []
    inside, best, par, out = {0}, {}, {}, []
    for j in range(1, n):
        best[j] = math.hypot(pts[j][0] - pts[0][0], pts[j][1] - pts[0][1]); par[j] = 0
    while best:
        j = min(best, key=lambda k: (best[k], k))
        out.append((par[j], j)); inside.add(j); del best[j]
        for k in best:
            d = math.hypot(pts[k][0] - pts[j][0], pts[k][1] - pts[j][1])
            if d < best[k]:
                best[k], par[k] = d, j
    return out


def _closest(p, a, b):
    """The point of segment a-b nearest p."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = 0.0 if not (dx or dy) else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return (a[0] + t * dx, a[1] + t * dy)


class Placer:
    def __init__(self, fps, nets, comps, size, edge_margin=1.0, power_fanout=12, apart=None, bare=()):
        self.fps, self.nets, self.comps = fps, nets, comps
        self.w, self.h = size
        self.edge_margin = edge_margin
        apart = apart or {}                    # ref -> its silk name, kept clear as a box of its own
        # a visible silk ref counts as courtyard, except for the parts in `bare`, whose own parts ring their pins:
        # the silk pass sets those refs where there's room (D-23Nov.29)
        self.geo = {r: geometry(f, label=r not in bare, label_text='TP00' if r.startswith('TP') else None,
                                apart=apart.get(r)) for r, f in fps.items()}
        self.apart = {r: text_boxes(fps[r], t) for r, t in apart.items() if r in fps}
        self.apart_rect = {}                   # ref -> its name's placed box, in self.rects
        self.cls = {r: pkg_class(f.GetFPIDAsString()) for r, f in fps.items()}
        self.placed = {}                       # ref -> (x, y, rot)
        self.crt, self.env = {}, {}            # ref -> placed boxes
        self.grid = {}
        self.circles = []                      # (cx, cy, r): no courtyard inside
        self.rects = []                        # (x0, y0, x1, y1, name): no courtyard inside
        self.pad_keepout = {}                  # ref -> boxes where none of its pad centres may fall
        self.fanout = {n: len(v) for n, v in nets.items()}
        self.power_fanout = power_fanout
        self.pin_nets = {}
        for n, nodes in nets.items():
            for r, p in nodes:
                self.pin_nets.setdefault(r, {}).setdefault(p, n)
        self.cap_used = set()
        self.exempt = set()                    # frozenset({a, b}) pairs allowed under the JLC table
        self.exceptions = []                   # (a, b, gap, required) actually used
        self.rotset = {}                       # ref -> allowed rotations
        self.spills = []
        self.weights = []                      # (compiled regex, multiplier) on net names
        self.routes = {}                       # test point -> the segments of its net's route (stage B2 step 5)
        self.probe_look = 10.0                 # how far past its first fitting ring a test point's search goes
        self.near = {}                         # part -> its distance rule's pulls (stage B2 step 6)
        self.step = {}                         # part -> a finer search step than 0.25 mm, where its spot is a thin strip

    # --- spatial index
    def _cells(self, box):
        for i in range(int(box[0] // CELL) - 1, int(box[2] // CELL) + 2):
            for j in range(int(box[1] // CELL) - 1, int(box[3] // CELL) + 2):
                yield (i, j)

    def _near(self, box):
        seen = set()
        for c in self._cells(box):
            for r in self.grid.get(c, ()):
                if r not in seen:
                    seen.add(r)
                    yield r

    def boxes_at(self, ref, x, y, a):
        c, e, _ = self.geo[ref][a]
        return (x + c[0], y + c[1], x + c[2], y + c[3]), (x + e[0], y + e[1], x + e[2], y + e[3])

    def pad_pos(self, ref, pin):
        x, y, a = self.placed[ref]
        return [(x + px, y + py) for px, py in self.geo[ref][a][2].get(pin, [])]

    def ok(self, ref, x, y, a, region, fixed=False):
        crt, env = self.boxes_at(ref, x, y, a)
        if not fixed:
            m = self.edge_margin
            if crt[0] < m or crt[1] < m or crt[2] > self.w - m or crt[3] > self.h - m:
                return False
            if region and (crt[0] < region[0] or crt[1] < region[1] or crt[2] > region[2] or crt[3] > region[3]):
                return False
        for cx, cy, r in self.circles:
            nx, ny = min(max(cx, crt[0]), crt[2]), min(max(cy, crt[1]), crt[3])
            if (nx - cx) ** 2 + (ny - cy) ** 2 < r * r:
                return False
        for k in self.rects:
            if overlap(crt, k):
                return False
        for b in self.pad_keepout.get(ref, ()):
            for pts in self.geo[ref][a][2].values():
                if any(b[0] < x + px < b[2] and b[1] < y + py < b[3] for px, py in pts):
                    return False
        for o in self._near(crt):
            if overlap(crt, self.crt[o]):
                return False
            if frozenset((ref, o)) in self.exempt:
                continue
            if box_gap(env, self.env[o]) < jlc_gap(self.cls[ref], self.cls[o]) - 1e-6:
                return False
        return True

    def commit(self, ref, x, y, a):
        self.placed[ref] = (x, y, a)
        self.crt[ref], self.env[ref] = self.boxes_at(ref, x, y, a)
        for c in self._cells(self.crt[ref]):
            self.grid.setdefault(c, []).append(ref)
        if ref in self.apart:                  # its name: no other courtyard on it
            if ref in self.apart_rect:
                self.rects.remove(self.apart_rect[ref])
            t = self.apart[ref][a]
            self.apart_rect[ref] = (x + t[0], y + t[1], x + t[2], y + t[3], f'{ref} name')
            self.rects.append(self.apart_rect[ref])

    def fix(self, ref, x, y, a=0):
        if not self.ok(ref, x, y, a, None, fixed=True):
            raise RuntimeError(f'fixed part {ref} at ({x}, {y}, {a}) collides')
        self.commit(ref, x, y, a)

    def move(self, ref, x, y):
        """Lift a placed part and set it down at (x, y), same rotation, if it fits there; else leave it."""
        old = self.placed[ref]
        for c in self._cells(self.crt[ref]):
            self.grid[c].remove(ref)
        del self.placed[ref], self.crt[ref], self.env[ref]
        fits = self.ok(ref, x, y, old[2], None)
        self.commit(ref, *((x, y, old[2]) if fits else old))
        return fits

    # --- what a part is pulled toward
    def owner(self, ref):
        """For a two-pin support part: the multi-pin part it serves, and the pin(s), on its non-GND net."""
        pins = self.pin_nets.get(ref, {})
        if len(pins) != 2:
            return None
        for pin, net in pins.items():
            if net == 'GND':
                continue
            ics = [(r, p) for r, p in self.nets[net] if r != ref and len(self.pin_nets.get(r, {})) > 3]
            if ics:
                return net, ics
        return None

    def weight(self, net):
        for rx, w in self.weights:
            if rx.fullmatch(net):
                return w
        return 1.0

    def targets(self, ref):
        d = self.near.get(ref)
        if d and d.get('seg'):                 # on the line from one pad to another (an RF line's ESD part)
            pin, a, b = d['seg']
            if a[0] in self.placed and b[0] in self.placed:
                pa, pb = self.pad_pos(*a)[0], self.pad_pos(*b)[0]
                self.routes[ref] = [(pa, pb)]
                return [(pin, ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2), 1.0)]
        if d and d.get('pulls'):               # pins pulled hard to the pads the rule names
            out = [(pp, self.pad_pos(ic, ip)[0], 10.0) for pp, ic, ip in d['pulls'] if ic in self.placed]
            if out:
                return out
        if ref.startswith('TP'):
            rt = self.probe_route(ref)
            if rt is None:
                return self.probe_target(ref)
            pin, segs, start = rt
            self.routes[ref] = segs
            return [(pin, start, 1.0)]
        out = []
        for pin, net in self.pin_nets.get(ref, {}).items():
            if net == 'GND':
                continue
            others = [(r, p) for r, p in self.nets[net] if r != ref and r in self.placed]
            if not others:
                continue
            if self.fanout[net] > self.power_fanout:
                cands = [(r, p) for r, p in others if len(self.pin_nets.get(r, {})) > 3 and (r, p) not in self.cap_used]
                if cands:
                    sheet = self.comps[ref].sheet
                    best = min(cands, key=lambda rp: (self.comps[rp[0]].sheet != sheet, rp[0], len(rp[1]), rp[1]))
                    self.cap_used.add(best)
                    out.append((pin, self.pad_pos(*best)[0], 3.0))
                continue
            pts = [q for r, p in others for q in self.pad_pos(r, p)]
            if pts:
                cx = sum(q[0] for q in pts) / len(pts); cy = sum(q[1] for q in pts) / len(pts)
                out.append((pin, (cx, cy), self.weight(net) / max(1, self.fanout[net] - 1)))
        return out

    def probe_target(self, ref):
        """A test point goes beside the circuit it probes: the centre of its net's pads on its own sheet,
        else of all its net's pads. It never takes a decoupling slot. GND loops have no pull (their region
        puts them at an edge)."""
        pin, net = next(iter(self.pin_nets.get(ref, {}).items()), (None, None))
        if net is None or net == 'GND':
            return []
        others = [(r, p) for r, p in self.nets[net] if r != ref and r in self.placed and not r.startswith('TP')]
        same = [(r, p) for r, p in others if self.comps[r].sheet == self.comps[ref].sheet]
        pts = [q for r, p in (same or others) for q in self.pad_pos(r, p)]
        if not pts:
            return []
        return [(pin, (sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)), 1.0)]

    def probe_route(self, ref):
        """A test point sits beside its net's route (stage B2 step 5): the spanning tree over the placed pads of the
        net's other parts, as the yardstick draws it. Returns its pin, the tree's segments and the point on them
        nearest the circuit it probes (its sheet's pads, else all), where the search starts."""
        pin, net = next(iter(self.pin_nets.get(ref, {}).items()), (None, None))
        if net is None or net == 'GND':
            return None
        others = [(r, p) for r, p in self.nets[net] if r != ref and r in self.placed and not r.startswith('TP')]
        pts = [q for r, p in others for q in self.pad_pos(r, p)]
        if not pts:
            return None
        same = [q for r, p in others if self.comps[r].sheet == self.comps[ref].sheet for q in self.pad_pos(r, p)] or pts
        c = (sum(q[0] for q in same) / len(same), sum(q[1] for q in same) / len(same))
        segs = [(pts[i], pts[j]) for i, j in _mst(pts)] or [(pts[0], pts[0])]
        start = min((_closest(c, a, b) for a, b in segs), key=lambda q: math.hypot(q[0] - c[0], q[1] - c[1]))
        return pin, segs, start

    def cost(self, ref, x, y, a, tg):
        if ref in self.routes:                 # a test point: its pad's distance to the nearest segment of the route
            pin = tg[0][0]
            px, py = self.geo[ref][a][2][pin][0]
            q = (x + px, y + py)
            best = math.inf
            for s0, s1 in self.routes[ref]:
                cx, cy = _closest(q, s0, s1)
                best = min(best, math.hypot(cx - q[0], cy - q[1]))
            return best
        c = 0.0
        pads = self.geo[ref][a][2]
        for pin, (tx, ty), wgt in tg:
            px, py = pads[pin][0]
            c += wgt * math.hypot(x + px - tx, y + py - ty)
        return c

    def place(self, ref, region, start=None, step=0.25, rmax=40.0, look=2.0):
        step = self.step.get(ref, step)
        tg = self.targets(ref)
        if ref in self.routes:
            look = self.probe_look                 # the route runs away from the start: look further along it
        if start is None:
            if tg:
                tw = sum(t[2] for t in tg)
                start = (sum(t[1][0] * t[2] for t in tg) / tw, sum(t[1][1] * t[2] for t in tg) / tw)
            else:
                start = ((region[0] + region[2]) / 2, (region[1] + region[3]) / 2)
        sx = min(max(start[0], region[0]), region[2])
        sy = min(max(start[1], region[1]), region[3])
        rots = self.rotset.get(ref, ROTS)
        r, best, found = 0.0, None, None
        while r <= rmax:
            n = max(1, int(2 * math.pi * r / step)) if r else 1
            for i in range(n):
                th = 2 * math.pi * i / n
                x = round((sx + r * math.cos(th)) / 0.05) * 0.05
                y = round((sy + r * math.sin(th)) / 0.05) * 0.05
                for a in rots:
                    if self.ok(ref, x, y, a, region):
                        c = self.cost(ref, x, y, a, tg) if tg else r
                        if best is None or c < best[0]:
                            best = (c, x, y, a)
            if best is not None:
                found = found if found is not None else r
                if r >= found + look:
                    break                  # look this far past the first ring that fits, then take the cheapest
            r += step
        if best is None:
            return False
        self.commit(ref, best[1], best[2], best[3])
        return True

    def place_grow(self, ref, region, grow=(0, 4, 8, 16), rmax=40.0):
        for g in grow:
            reg = (max(0, region[0] - g), max(0, region[1] - g), min(self.w, region[2] + g), min(self.h, region[3] + g))
            if self.place(ref, reg, rmax=rmax):
                if g:
                    self.spills.append((ref, g))
                return True
        return False

    def order(self, refs):
        """Parts with the most connections to what's placed first; ties by size."""
        left, seq, done = set(refs), [], set(self.placed)
        def size(r):
            b = self.geo[r][0][0]
            return (b[2] - b[0]) * (b[3] - b[1])
        while left:
            def score(r):
                links = sum(1 for p, n in self.pin_nets.get(r, {}).items()
                            if n != 'GND' and any(q in done for q, _ in self.nets[n] if q != r))
                return (links, size(r), r)
            r = max(left, key=score)
            seq.append(r); left.discard(r); done.add(r)
        return seq

    def apply(self, board):
        for ref, (x, y, a) in self.placed.items():
            fp = self.fps[ref]
            fp.SetOrientationDegrees(a)
            fp.SetPosition(board.V(x, y))

    # --- metrics
    def hpwl(self, names=None):
        total = 0.0
        for n, nodes in self.nets.items():
            if names is not None and n not in names:
                continue
            pts = [q for r, p in nodes if r in self.placed for q in self.pad_pos(r, p)[:1]]
            if len(pts) > 1:
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                total += (max(xs) - min(xs)) + (max(ys) - min(ys))
        return total

    def spacing_report(self):
        """Every placed pair under JLC's table: exempt ones listed as exceptions, others as violations."""
        exc, bad = [], []
        for r in self.placed:
            for o in self._near(self.crt[r]):
                if o <= r:
                    continue
                need = jlc_gap(self.cls[r], self.cls[o])
                g = box_gap(self.env[r], self.env[o])
                if g < need - 1e-6:
                    (exc if frozenset((r, o)) in self.exempt else bad).append((r, o, round(g, 2), need))
        return exc, bad
