"""Stage C (S4): the copper the router never touches, drawn by script after placement (execution brief, stage C;
stage C and D handoff). Everything here is deterministic and locked, and it is rebuilt from the spec and the
placement on every build, so the board stays the output of scripts (D-21Nov.21).

Board-local mm, y down, as the rest of the engine. Each step takes the Board wrapper, the spec and the placed
footprints, adds its items and returns a short report for build.json.
"""
import fnmatch
import math

import pcbnew as K
from shapely import STRtree
from shapely.geometry import LineString, Point

MM, TOMM = K.FromMM, K.ToMM

VIA_D, DRILL, HOLE_GAP = 0.5, 0.3, 0.25      # the board's smallest via and hole gap (spec.RULES), JLC's default tier
GRID = 0.1                                   # the router's grid: every via it starts from sits on it (handoff step 3)
EPS = 0.01                                   # pad outlines are drawn 0.01 mm inside the true shape
FIRE = ('FIRE', 'FIRE_LOGIC', 'PYRO_RAIL')
ROWS = (0.45, 0.95, 1.45, 1.95)              # via depths under the body, from the pads' inner ends
TIPS = (0.3, 0.4, 0.5, 0.6, 0.8, 1.0)        # depths of a plane via beyond a pad's outer end
STUB_W = {'signal': 0.15, 'plane': 0.25}


def courtyard_poly(fp, origin):
    """A footprint's front courtyard as a list of board-local (x, y) points."""
    fp.BuildCourtyardCaches()
    cy = fp.GetCourtyard(K.F_CrtYd)
    if not cy.OutlineCount():
        bb = fp.GetBoundingBox(False, False)
        x0, y0, x1, y1 = TOMM(bb.GetX()), TOMM(bb.GetY()), TOMM(bb.GetRight()), TOMM(bb.GetBottom())
        return [(x0 - origin[0], y0 - origin[1]), (x1 - origin[0], y0 - origin[1]),
                (x1 - origin[0], y1 - origin[1]), (x0 - origin[0], y1 - origin[1])]
    o = cy.Outline(0)
    return [(TOMM(o.CPoint(i).x) - origin[0], TOMM(o.CPoint(i).y) - origin[1]) for i in range(o.PointCount())]


def escape_areas(bd, spec, fps):
    """Named rule areas with no restrictions of their own, for the custom rules to test against: the fire-logic
    waiver (D-22Nov.26, D-23Nov.8, D-23Nov.13) reads `A.enclosedByArea('<ref>_ESCAPE')`, each area the part's
    courtyard and spec.ESCAPE_MARGIN round it."""
    out = {}
    from shapely.geometry import Polygon
    m = getattr(spec, 'ESCAPE_MARGIN', 0.0)          # D-23Nov.13: the courtyard and this much round it
    for ref in getattr(spec, 'ESCAPE_AREAS', ()):
        poly = courtyard_poly(fps[ref], spec.ORIGIN)
        if m:
            poly = list(Polygon(poly).buffer(m, join_style='mitre').exterior.coords)[:-1]
        bd.rule_area(f'{ref}_ESCAPE', poly, list(bd.b.GetEnabledLayers().CuStack()),
                     tracks=False, vias=False, pads=False, pours=False)
        out[ref] = [[round(x, 3), round(y, 3)] for x, y in poly]
    return out


def clearance(spec, waived=False):
    """pair(n1, n2): the copper clearance KiCad asks between two nets, plus EPS: the larger class clearance, and 0.5 mm
    for fire copper (spec.DRU), except fire logic inside a waived courtyard (D-22Nov.26), which keeps its class's."""
    cl = {c['name']: c['clearance'] for c in spec.NETCLASSES}
    cache = {}

    def cls(n):
        s = (n or '').split('/')[-1]
        if s not in cache:
            cache[s] = next((c for c, pat in spec.PATTERNS if fnmatch.fnmatchcase(s, pat)), 'Default')
        return cache[s]

    def pair(n1, n2):
        if n1 == n2 and n1:
            return 0.0
        a, b = cls(n1), cls(n2)
        c = max(cl.get(a, 0.15), cl.get(b, 0.15))
        fire = {a, b} & set(FIRE)
        if fire and not (waived and fire == {'FIRE_LOGIC'}):
            c = max(c, 0.5)
        return c + EPS
    pair.cls = cls
    return pair


class Copper:
    """The scripted copper placed so far, with the clearance checks every new item must pass: other nets' pads on
    L1, vias (hole to hole for any net) and L1 tracks."""

    def __init__(self, data):
        self.F = [(d['poly']['F'], d['net']) for d in data.pads if 'F' in d['poly']]
        self.tree = STRtree([g for g, _ in self.F])
        self.vias = []           # (x, y, net)
        self.segs = []           # (LineString, width, net)

    def via_ok(self, x, y, net, pair):
        r, pt = VIA_D / 2, Point(x, y)
        for k in self.tree.query(pt, predicate='dwithin', distance=r + 0.6):
            g, n = self.F[k]
            if n != net and g.distance(pt) < r + pair(net, n):
                return False
        for vx, vy, vn in self.vias:
            d = math.hypot(vx - x, vy - y)
            if d < DRILL + HOLE_GAP or (vn != net and d < VIA_D + pair(net, vn)):
                return False
        return all(sn == net or s.distance(pt) >= r + w / 2 + pair(net, sn) for s, w, sn in self.segs)

    def seg_ok(self, s, w, net, pair):
        for k in self.tree.query(s, predicate='dwithin', distance=w / 2 + 0.6):
            g, n = self.F[k]
            if n != net and g.distance(s) < w / 2 + pair(net, n):
                return False
        for vx, vy, vn in self.vias:
            if vn != net and s.distance(Point(vx, vy)) < VIA_D / 2 + w / 2 + pair(net, vn):
                return False
        return all(tn == net or s.distance(t) >= w / 2 + tw / 2 + pair(net, tn) for t, tw, tn in self.segs)


def _snap(v, toward):
    """v on the grid, rounded toward +1 (up) or -1 (down)."""
    k = v / GRID
    return round((math.ceil(k - 1e-6) if toward > 0 else math.floor(k + 1e-6)) * GRID, 3)


def mcu_fanout(bd, spec, fps, cu=None, data=None):
    """Stage C step 3 (handoff): MCU pins leave inward, under the body, so no plane via sits in the strip the signal
    pins leave by. Off on Burrito (`MCU_FANOUT = {}`): step 3 stopped at kill line 1 (burrito-stage-c-step3.md).

    Per side, pins in order: a short L1 stub inward to a via under the body, the vias in two staggered rows 0.5 mm
    apart, in line with their pins, signal vias on the router's grid; a stub to the inner row passes between two outer
    vias. That spacing holds only at 0.15 mm, so a pin whose net keeps more (GND, fire logic under the waiver: 0.2 mm)
    takes its via with both neighbours left to leave outward on L1. A neighbour on a plane net takes a dogleg to a via
    in a free lane nearby, or beyond its pad's tip; one on its neighbour's net is joined to that pad on L1. With
    `MCU_FANOUT_SIGNALS = False` only the plane and fire-logic pins are drawn. Pins on the spec's MCU_FANOUT nets are
    left for their own scripted copper (crystals, USB); unconnected pins get nothing."""
    from engine import metrics as M
    data = data or M.BoardData(bd.b, spec.ORIGIN, (spec.W, spec.H))
    planes = set(M.plane_nets(data, set(spec.RAILS)))
    cu = cu or Copper(data)
    b, ox, oy = bd.b, *spec.ORIGIN
    V = lambda x, y: K.VECTOR2I(MM(x + ox), MM(y + oy))
    report = {}
    for ref, later in getattr(spec, 'MCU_FANOUT', {}).items():
        pair = clearance(spec, waived=ref in getattr(spec, 'ESCAPE_AREAS', ()))
        signals = getattr(spec, 'MCU_FANOUT_SIGNALS', True)    # False: plane pins only, signal pins left to the router
        fx, fy = data.fp_xy[ref]
        sides = {'L': [], 'R': [], 'T': [], 'B': []}
        for d in data.pads:
            if d['ref'] == ref and 'F' in d['poly']:
                dx, dy = d['x'] - fx, d['y'] - fy
                sides[('L' if dx < 0 else 'R') if abs(dx) > abs(dy) else ('T' if dy < 0 else 'B')].append(d)
        pins, shift = [], {}                            # (side, index, pad, mode); each side's offset off the grid
        for s, P in sides.items():
            P.sort(key=lambda d: d['y'] if s in 'LR' else d['x'])
            modes = []
            for d in P:
                n = M.short(d['net'])
                modes.append(None if not n or n.startswith('unconnected') else 'later' if n in later
                             else 'fat' if pair(d['net'], '') > 0.15 + EPS + 1e-6
                             else 'in' if signals or d['net'] in planes else 'out')
            for i, m in enumerate(modes):               # a pin that keeps more than 0.15 mm: its neighbours leave outward
                if m != 'fat':
                    continue
                for j in (i - 1, i + 1):
                    if 0 <= j < len(P) and modes[j] in ('in', 'fat') and P[j]['net'] != P[i]['net']:
                        modes[j] = 'out'
            for i, m in enumerate(modes):
                if m != 'out':
                    continue
                if any(0 <= j < len(P) and modes[j] in ('in', 'fat') and P[j]['net'] == P[i]['net'] for j in (i - 1, i + 1)):
                    modes[i] = 'link'
                elif P[i]['net'] in planes:
                    modes[i] = 'tip'
            pins += [(s, i, d, m) for i, (d, m) in enumerate(zip(P, modes))]
            if P:
                a0 = (P[0]['y'] if s in 'LR' else P[0]['x']) / GRID
                shift[s] = (a0 - round(a0)) * GRID

        def geom(s, d):
            """(in sign, the pad's inner and outer ends along that axis, its along coordinate, point maker)"""
            x0, y0, x1, y1 = d['poly']['F'].bounds
            if s in 'LR':
                sg = 1 if s == 'L' else -1
                return sg, (x1, x0) if sg > 0 else (x0, x1), d['y'], lambda a, c: (a, c)
            sg = 1 if s == 'T' else -1
            return sg, (y1, y0) if sg > 0 else (y0, y1), d['x'], lambda a, c: (c, a)

        placed, misses, out, dogleg = {}, [], [], []
        n_vias0 = len(cu.vias)
        fire = lambda n: pair.cls(n) in FIRE
        rank = {'fat': 0, 'in': 1, 'link': 2, 'tip': 3}
        for s, i, d, m in sorted((p for p in pins if p[3] in rank), key=lambda p: (rank[p[3]], 'LTRB'.index(p[0]), p[1])):
            net, num = d['net'], d['num']
            sg, (inner, outer), along, pt = geom(s, d)
            w = STUB_W['plane' if net in planes else 'signal']
            hit = None
            if m == 'link':
                P = sorted((q for q in pins if q[0] == s), key=lambda q: q[1])
                for j in (i - 1, i + 1):
                    q = next((q for q in P if q[1] == j), None)
                    if q and q[2]['net'] == net and q[3] in ('in', 'fat'):
                        seg = LineString([(d['x'], d['y']), (q[2]['x'], q[2]['y'])])
                        if cu.seg_ok(seg, STUB_W['signal'], net, pair):
                            hit = (None, seg, STUB_W['signal'])
                            break
            else:
                mid = d['x'] if s in 'LR' else d['y']
                # the router starts only from signal vias: those sit on its grid. Every pin of a side sits the same
                # distance off it (0.05 mm at most), so one shift per side keeps the rows' stagger exact, and the stub
                # starts inside the pad, in the via's lane. Plane and fire vias stay in their pad's own lane
                routed = net not in planes and not fire(net)
                c = round(along - shift[s], 3) if routed else along
                paths = []
                if m in ('fat', 'in'):
                    pref = ROWS if m == 'fat' else (ROWS[i % 2], ROWS[1 - i % 2]) + ROWS[2:]
                    paths += [[pt(mid, c), pt(a, c)] for a in
                              ((_snap(inner + sg * t, sg) if routed else inner + sg * t) for t in pref)]
                under, beyond = [], []
                if net in planes:
                    # no room in its own lane: a dogleg into a lane nearby, under the body or beyond the tip
                    for da in (0.25, -0.25, 0.5, -0.5, 0.75, -0.75, 1.0, -1.0):
                        under += [[pt(mid, along), pt(inner, along), pt(inner + sg * t, along + da)] for t in ROWS[:2]]
                        beyond += [[pt(mid, along), pt(outer, along), pt(outer - sg * t, along + da)] for t in TIPS[:4]]
                tips = [[pt(mid, c), pt(outer - sg * t, c)] for t in TIPS] if m == 'tip' else []
                # with the signal pins left to the router, the lanes under the body are free and the strip beyond
                # the tips is theirs: a plane pin's dogleg under the body comes first
                paths += (tips + under + beyond) if signals else (under + tips + beyond)
                for path in paths:
                    vx, vy = path[-1]
                    seg = LineString(path)
                    if cu.via_ok(vx, vy, net, pair) and cu.seg_ok(seg, w, net, pair):
                        hit = ((vx, vy), seg, w)
                        if len(path) > 2:
                            dogleg.append(num)
                        break
            if hit is None:
                misses.append(num)
                continue
            (via, seg, w) = hit
            net_item = fps[ref].FindPadByNumber(num).GetNet()
            if via:
                cu.vias.append((via[0], via[1], net))
                v = K.PCB_VIA(b)
                v.SetPosition(V(*via)); v.SetWidth(MM(VIA_D)); v.SetDrill(MM(DRILL))
                v.SetViaType(K.VIATYPE_THROUGH); v.SetNet(net_item); v.SetLocked(True)
                b.Add(v)
            cu.segs.append((seg, w, net))
            pts = list(seg.coords)
            for (ax, ay), (cx, cy) in zip(pts, pts[1:]):
                t = K.PCB_TRACK(b)
                t.SetStart(V(ax, ay)); t.SetEnd(V(cx, cy)); t.SetWidth(MM(w))
                t.SetLayer(K.F_Cu); t.SetNet(net_item); t.SetLocked(True)
                b.Add(t)
            placed[num] = m
        for s, i, d, m in pins:
            if m == 'out':
                out.append(d['num'])
        from shapely.geometry import Polygon
        body = Polygon(courtyard_poly(fps[ref], spec.ORIGIN))
        mine = [(x, y) for x, y, n in cu.vias[n_vias0:]]
        n_under = sum(1 for x, y in mine if body.contains(Point(x, y)))
        report[ref] = {'vias_under_body': n_under, 'vias_beyond_tips': len(mine) - n_under,
                       'links': sum(1 for v in placed.values() if v == 'link'),
                       'leave_outward': sorted(out, key=int),
                       'left_for_later': sorted((d['num'] for s, i, d, m in pins if m == 'later'), key=int),
                       'doglegs': sorted(dogleg, key=int), 'misses': sorted(misses, key=int)}
    return report


def l1_path(cu, net, a, b, w, pair, margin=3.0, step=0.025, bend=0.1, tight=False, extra=()):
    """A short L1 route for one scripted net, from point a to point b (board mm), or None: an A* search on a grid
    of `step` mm over the pair's box plus `margin`, eight directions, each 45-degree turn costing `bend` mm, through
    cells where a track of width w keeps its clearance from every other net's pad, track and via. The grid's cells
    are blocked half a diagonal early, and the result is checked against the exact geometry before it's used."""
    import heapq
    import numpy as np
    from shapely import contains_xy
    from shapely.ops import unary_union
    from shapely.geometry import box as sbox
    x0, y0 = min(a[0], b[0]) - margin, min(a[1], b[1]) - margin
    x1, y1 = max(a[0], b[0]) + margin, max(a[1], b[1]) + margin
    area = sbox(x0, y0, x1, y1)
    pad = 0.0 if tight else step * 0.75   # a cell's corner within half a diagonal of its centre; none when tight
    obs = [g.buffer(w / 2 + pair(net, n) + pad, 8) for g, n in cu.F if n != net and g.intersects(area.buffer(1.0))]
    obs += [Point(x, y).buffer(VIA_D / 2 + w / 2 + pair(net, n) + pad, 8) for x, y, n in cu.vias if n != net]
    obs += [s.buffer(sw / 2 + w / 2 + pair(net, n) + pad, 8) for s, sw, n in cu.segs if n != net]
    obs += [g.buffer(w / 2 + pad, 8) for g in extra]          # areas no copper of this net may enter
    blocked_shape = unary_union([o for o in obs if o.intersects(area)])
    nx, ny = int(round((x1 - x0) / step)) + 1, int(round((y1 - y0) / step)) + 1
    xs, ys = x0 + np.arange(nx) * step, y0 + np.arange(ny) * step
    gx, gy = np.meshgrid(xs, ys, indexing='ij')
    blocked = contains_xy(blocked_shape, gx, gy) if not blocked_shape.is_empty else np.zeros_like(gx, bool)
    cell = lambda p: (int(round((p[0] - x0) / step)), int(round((p[1] - y0) / step)))
    s, t = cell(a), cell(b)
    blocked[s] = blocked[t] = False
    dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    h = lambda c: step * (max(abs(c[0] - t[0]), abs(c[1] - t[1])) + (math.sqrt(2) - 1) * min(abs(c[0] - t[0]), abs(c[1] - t[1])))
    best = {(s, -1): 0.0}
    prev = {}
    q = [(h(s), 0.0, s, -1)]
    end = None
    while q:
        f, g, c, d = heapq.heappop(q)
        if c == t:
            end = (c, d)
            break
        if g > best.get((c, d), math.inf):
            continue
        for k, (dx, dy) in enumerate(dirs):
            n_ = (c[0] + dx, c[1] + dy)
            if not (0 <= n_[0] < nx and 0 <= n_[1] < ny) or blocked[n_]:
                continue
            turn = 0 if d < 0 else min((k - d) % 8, (d - k) % 8)
            if turn > 2:
                continue
            g2 = g + step * (math.sqrt(2) if dx and dy else 1.0) + bend * turn
            if g2 < best.get((n_, k), math.inf):
                best[(n_, k)] = g2
                prev[(n_, k)] = (c, d)
                heapq.heappush(q, (g2 + h(n_), g2, n_, k))
    if end is None:
        return None if tight else l1_path(cu, net, a, b, w, pair, margin, step, bend, tight=True, extra=extra)
    cells = [end]
    while cells[-1] in prev:
        cells.append(prev[cells[-1]])
    cells = [c for c, _ in reversed(cells)]
    pts = [(round(x0 + i * step, 4), round(y0 + j * step, 4)) for i, j in cells]
    out = [pts[0]]                       # keep the corners only
    for p, q_ in zip(pts[1:], pts[2:]):
        (ax, ay), (bx, by) = out[-1], p
        if abs((bx - ax) * (q_[1] - by) - (by - ay) * (q_[0] - bx)) > 1e-9:
            out.append(p)
    out.append(pts[-1])
    out[0], out[-1] = a, b
    line = LineString(out)
    if cu.seg_ok(line, w, net, pair) and not any(line.intersects(g) for g in extra):
        return line
    return None if tight else l1_path(cu, net, a, b, w, pair, margin, step, bend, tight=True, extra=extra)


def add_track(b, origin, line, w, net_item, layer=K.F_Cu):
    """A locked track along each segment of a board-mm LineString."""
    ox, oy = origin
    V = lambda x, y: K.VECTOR2I(MM(x + ox), MM(y + oy))
    pts = list(line.coords)
    for (ax, ay), (cx, cy) in zip(pts, pts[1:]):
        t = K.PCB_TRACK(b)
        t.SetStart(V(ax, ay)); t.SetEnd(V(cx, cy)); t.SetWidth(MM(w))
        t.SetLayer(layer); t.SetNet(net_item); t.SetLocked(True)
        b.Add(t)


def crystals(bd, spec, fps, cu, data):
    """Stage C step 6, the crystals (D-22Nov.17; ST AN2867): each oscillator net as short L1 tracks, no via, from the
    MCU pin to the crystal's pad and on to its load capacitor, over L2's unbroken ground. Each net's pads in that
    order; a hop that finds no path is reported, not forced."""
    from engine import metrics as M
    pair = clearance(spec)
    out, todo = {}, []
    for net_s in getattr(spec, 'CRYSTAL_NETS', ()):
        pads = [d for d in data.pads if M.short(d['net']) == net_s and 'F' in d['poly']]
        out[net_s] = [] if len(pads) >= 2 else 'no pads'
        key = lambda d: (0 if d['ref'].startswith('U') else 1 if d['ref'].startswith('Y') else 2, d['ref'])
        pads.sort(key=key)
        todo += [(p, q) for p, q in zip(pads, pads[1:])]
    # shortest hop first: the pin-to-crystal hops are the tight ones
    for p, q in sorted(todo, key=lambda pq: (math.hypot(pq[0]['x'] - pq[1]['x'], pq[0]['y'] - pq[1]['y']), pq[0]['ref'], pq[0]['num'])):
        net, w = p['net'], STUB_W['signal']
        line = l1_path(cu, net, (p['x'], p['y']), (q['x'], q['y']), w, pair)
        tag = f"{p['ref']}.{p['num']}-{q['ref']}.{q['num']}"
        if line is None:
            out[M.short(net)].append(f'{tag}: no path')
            continue
        cu.segs.append((line, w, net))
        add_track(bd.b, spec.ORIGIN, line, w, fps[p['ref']].FindPadByNumber(p['num']).GetNet())
        out[M.short(net)].append(f'{tag}: {line.length:.2f} mm')
    return out


def rf_lines(bd, spec, fps, cu, data):
    """Stage C step 6, the RF feed lines (D-21Nov.25, D-22Nov.16, the layout brief's RF50 row): each a grounded
    coplanar line on L1 with no via, pad to pad along the spec's chain (module pin, ESD part, connector), keeping its
    gap from GND and `keep` mm from every other net's copper and out from under any part's body, then a fence of GND
    vias each side at `pitch` mm or less. A hop with no path is reported, not forced. Off on Burrito until the
    LoRa line has a way (the plan of 23 November, call 7): spec.RF_LINES is unset."""
    from engine import metrics as M
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    base = clearance(spec)
    courts = {r: Polygon(courtyard_poly(f, spec.ORIGIN)) for r, f in fps.items()}
    gnd = next((d['net'] for d in data.pads if M.short(d['net']) == 'GND'), None)
    gnd_item = bd.b.FindNet(gnd) if gnd else None
    out = {}
    for net_s, c in getattr(spec, 'RF_LINES', {}).items():
        w, gap, keep, pitch = c['width'], c['gap'], c.get('keep', 1.0), c.get('pitch', 2.0)
        pads = [next(d for d in data.pads if d['ref'] == r and d['num'] == n and 'F' in d['poly']) for r, n in c['chain']]
        net = pads[0]['net']
        item = fps[pads[0]['ref']].FindPadByNumber(pads[0]['num']).GetNet()

        def pair(n1, n2, net=net, gap=gap, keep=keep):
            if n1 == n2 and n1:
                return 0.0
            other = n2 if n1 == net else n1
            return (gap if M.short(other) == 'GND' else keep) + EPS

        # no line under a part's body: every other part's courtyard blocks it, and so does the module's (the chain's
        # first part) less a 0.6 mm reach round its RF pad; the ESD part and the connector are the line's own
        chain = {r for r, n in c['chain']}
        bodies = [cp for r, cp in courts.items() if r not in chain]
        bodies.append(courts[c['chain'][0][0]].difference(pads[0]['poly']['F'].buffer(0.6)))
        rep, lines = [], []
        for p, q in zip(pads, pads[1:]):
            line = l1_path(cu, net, (p['x'], p['y']), (q['x'], q['y']), w, pair, margin=8.0, step=0.05, bend=0.2,
                           extra=[g for g in bodies if not g.is_empty])
            tag = f"{p['ref']}.{p['num']}-{q['ref']}.{q['num']}"
            if line is None:
                rep.append(f'{tag}: no path')
                continue
            cu.segs.append((line, w, net))
            add_track(bd.b, spec.ORIGIN, line, w, item)
            lines.append(line)
            rep.append(f'{tag}: {line.length:.2f} mm')
        # the fence: GND vias each side, the via's edge 0.15 mm beyond the gap, every pitch along the line or as near
        # as the copper allows; none in a part's courtyard
        d_off = w / 2 + gap + 0.15 + VIA_D / 2
        fence = 0
        if gnd_item is not None:
            for line in lines:
                n_steps = max(1, int(math.ceil(line.length / pitch)))
                for side in (1, -1):
                    off = line.offset_curve(side * d_off, join_style=2)
                    if off.is_empty or off.length == 0:
                        continue
                    for k in range(n_steps + 1):
                        for nudge in (0.0, 0.3, -0.3, 0.6, -0.6):
                            s_ = min(max(k * off.length / n_steps + nudge, 0.0), off.length)
                            pt_ = off.interpolate(s_)
                            x, y = round(pt_.x, 3), round(pt_.y, 3)
                            if any(cp.contains(Point(x, y)) for cp in courts.values()):
                                continue
                            if cu.via_ok(x, y, gnd, base) and Point(x, y).distance(line) >= d_off - 0.01:
                                cu.vias.append((x, y, gnd))
                                v = K.PCB_VIA(bd.b)
                                v.SetPosition(K.VECTOR2I(MM(x + spec.ORIGIN[0]), MM(y + spec.ORIGIN[1])))
                                v.SetWidth(MM(VIA_D)); v.SetDrill(MM(DRILL)); v.SetViaType(K.VIATYPE_THROUGH)
                                v.SetNet(gnd_item); v.SetLocked(True)
                                bd.b.Add(v)
                                fence += 1
                                break
        out[net_s] = {'hops': rep, 'length_mm': round(sum(l.length for l in lines), 2), 'fence_vias': fence}
    return out


def pyro(bd, spec, fps, cu, data):
    """Stage C, the pyro output stage (D-22Nov.27, D-23Nov.9): spec.PYRO_COPPER's tracks and vias, locked, each on
    its net. Fire vias take the FIRE class's 0.6 mm with a 0.3 mm hole."""
    by_short = {}
    for n, item in bd.b.GetNetsByName().items():
        by_short.setdefault(str(n).rsplit('/', 1)[-1], []).append(item)
    lay = {'F.Cu': K.F_Cu, 'B.Cu': K.B_Cu, 'In2.Cu': K.In2_Cu}
    ox, oy = spec.ORIGIN
    rep = {'tracks': 0, 'vias': 0, 'mm': 0.0}
    for it in spec.PYRO_COPPER:
        items = by_short.get(it['net'], [])
        assert len(items) == 1, f"net {it['net']}: {len(items)} matches"
        net = items[0]
        if 'via' in it:
            x, y = it['via']
            v = K.PCB_VIA(bd.b)
            v.SetPosition(K.VECTOR2I(MM(x + ox), MM(y + oy)))
            v.SetWidth(MM(it.get('d', 0.6))); v.SetDrill(MM(it.get('drill', 0.3)))
            v.SetNet(net); v.SetLocked(True)
            bd.b.Add(v)
            rep['vias'] += 1
            continue
        line = LineString(it['path'])
        add_track(bd.b, spec.ORIGIN, line, it['w'], net, lay[it['layer']])
        rep['tracks'] += len(it['path']) - 1
        rep['mm'] = round(rep['mm'] + line.length, 1)
    return rep
