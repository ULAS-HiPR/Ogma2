"""Yardsticks for a placement, in seconds (stage B2, burrito-stage-b2-brief.md step 1).

    python3 tools/layout/engine/metrics.py hardware/croi2/Croi2.kicad_pcb [--spec croi2] [--md out.md]

Reads a placed board and returns, all in board mm (x across from the left edge, y aft from the forward edge):

- wire length: each signal net's minimum spanning tree over its pads, summed by net class;
- crossings: pairs of those spanning-tree segments, of different nets, that cross;
- wrong-side pins: for each IC of 16 pins or more, signal pins whose nearest partner on the net (another part,
  not a test point) is over 4 mm away and lies over 90 degrees round the package from the pin;
- test point stubs: the distance from each test point (not GND) to the nearest pad on its net, and to the
  nearest segment of the spanning tree of its net's other pads;
- plane pads without a via: the fanout planner's misses (fanout.py), within 1.5 mm of each pad.

A congestion map (RUDY on a 2 mm grid) was here until the meter's baseline: its heat did not sit where the router
failed (project log, 22 Nov 2026), so the brief's rule deleted it.

Signal nets are every net of two pads or more except the plane nets: GND (L2) and each rail that feeds four ICs
or more (L3 islands, D-22Nov.15). A rail that feeds fewer is a signal net here, as it is routed as tracks.
"""
import fnmatch
import re
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

WRONG_SIDE_MIN_MM = 4.0       # a partner this close is reached whatever the side
IC_MIN_PINS = 16
ISLAND_MIN_LOADS = 4          # D-22Nov.15: a rail gets an L3 island if it feeds four or more loads (ICs here)


def short(n):
    return n.split('/')[-1] if n else ''


def net_class(name, patterns):
    s = short(name)
    for cls, pat in patterns:
        if fnmatch.fnmatchcase(s, pat):
            return cls
    return 'Default'


def mst(pts):
    """Prim's minimum spanning tree over points; returns [(i, j, length)]."""
    n = len(pts)
    if n < 2:
        return []
    P = np.asarray(pts, float)
    used = np.zeros(n, bool); used[0] = True
    best = np.hypot(*(P - P[0]).T); par = np.zeros(n, int)
    out = []
    for _ in range(n - 1):
        d = np.where(used, np.inf, best)
        j = int(np.argmin(d))
        out.append((int(par[j]), j, float(d[j])))
        used[j] = True
        nd = np.hypot(*(P - P[j]).T)
        upd = (~used) & (nd < best)
        best[upd] = nd[upd]; par[upd] = j
    return out


def seg_dist(p, a, b):
    a, b, p = np.asarray(a, float), np.asarray(b, float), np.asarray(p, float)
    ab = b - a
    t = 0.0 if not ab.any() else max(0.0, min(1.0, float(np.dot(p - a, ab) / np.dot(ab, ab))))
    return float(np.hypot(*(a + t * ab - p)))


def count_crossings(segs):
    """segs: [(net, (x1, y1), (x2, y2))]. Proper crossings between segments of different nets."""
    if len(segs) < 2:
        return 0, {}
    A = np.array([s[1] for s in segs], float); B = np.array([s[2] for s in segs], float)
    net = np.array([hash(s[0]) for s in segs])
    def orient(p, q, r):          # sign of (q - p) x (r - p), broadcast
        return np.sign((q[..., 0] - p[..., 0]) * (r[..., 1] - p[..., 1]) - (q[..., 1] - p[..., 1]) * (r[..., 0] - p[..., 0]))
    n = len(segs)
    total, per = 0, defaultdict(int)
    for i in range(n - 1):
        a, b = A[i], B[i]
        c, d = A[i + 1:], B[i + 1:]
        o1 = orient(a[None], b[None], c); o2 = orient(a[None], b[None], d)
        o3 = orient(c, d, a[None]); o4 = orient(c, d, b[None])
        hit = (o1 * o2 < 0) & (o3 * o4 < 0) & (net[i + 1:] != net[i])
        k = int(hit.sum())
        if k:
            total += k
            per[segs[i][0]] += k
            for j in np.nonzero(hit)[0]:
                per[segs[i + 1 + j][0]] += 1
    return total, per


class BoardData:
    """Pads and copper of a placed board, in board mm."""

    def __init__(self, board, origin, size):
        import pcbnew as K
        self.K = K
        self.b = board
        self.ox, self.oy = origin
        self.W, self.H = size
        self.pads = []            # dicts: ref, num, x, y, net, tht, fp, layers, poly {layer: shapely}, hole
        self.fp_xy = {}
        self.fp_lib = {}
        self.value = {}
        from shapely.geometry import Polygon
        for f in board.GetFootprints():
            ref = f.GetReference()
            p0 = f.GetPosition()
            self.fp_xy[ref] = (K.ToMM(p0.x) - self.ox, K.ToMM(p0.y) - self.oy)
            self.fp_lib[ref] = f.GetFPID().GetLibItemName().wx_str()
            self.value[ref] = f.GetValue()
            for p in f.Pads():
                c = p.GetPosition()
                d = dict(ref=ref, num=p.GetNumber(), x=K.ToMM(c.x) - self.ox, y=K.ToMM(c.y) - self.oy,
                         net=p.GetNetname(), tht=p.GetAttribute() in (K.PAD_ATTRIB_PTH, K.PAD_ATTRIB_NPTH),
                         layers=[], poly={}, hole=None, pinfn=p.GetPinFunction(), pintype=p.GetPinType())
                for lay, name in ((K.F_Cu, 'F'), (K.B_Cu, 'B')):
                    if not p.IsOnLayer(lay):
                        continue
                    ps = K.SHAPE_POLY_SET()
                    p.TransformShapeToPolygon(ps, lay, 0, K.FromMM(0.01), K.ERROR_INSIDE)
                    if ps.OutlineCount() == 0:
                        continue
                    o = ps.Outline(0)
                    pts = [(K.ToMM(o.CPoint(i).x) - self.ox, K.ToMM(o.CPoint(i).y) - self.oy) for i in range(o.PointCount())]
                    if len(pts) >= 3:
                        d['poly'][name] = Polygon(pts).buffer(0)
                        d['layers'].append(name)
                ds = p.GetDrillSize()
                if ds.x > 0:
                    d['hole'] = max(K.ToMM(ds.x), K.ToMM(ds.y)) / 2
                self.pads.append(d)
        self.by_net = defaultdict(list)
        for d in self.pads:
            if d['net']:
                self.by_net[d['net']].append(d)

    def ic_refs(self):
        n = defaultdict(int)
        for d in self.pads:
            n[d['ref']] += 1
        return {r for r, k in n.items() if r.startswith('U') and k >= IC_MIN_PINS}


def plane_nets(bd, rails):
    """GND, and each listed rail that feeds ISLAND_MIN_LOADS ICs or more (D-22Nov.15)."""
    out = {}
    for net, ps in bd.by_net.items():
        s = short(net)
        if s == 'GND':
            out[net] = 'GND planes'
        elif s in rails:
            loads = {d['ref'] for d in ps if d['ref'].startswith('U')}
            if len(loads) >= ISLAND_MIN_LOADS:
                out[net] = 'island'
    return out


def signal_nets(bd, planes):
    return {n: ps for n, ps in bd.by_net.items() if n not in planes and len(ps) >= 2}


def measure(bd, spec, fan=None):
    planes = plane_nets(bd, set(spec.RAILS))
    sig = signal_nets(bd, planes)
    out = {'plane_nets': {short(n): l for n, l in sorted(planes.items())}}

    # wire length and crossings over spanning trees
    by_class = defaultdict(float)
    segs, net_len = [], {}
    for n, ps in sig.items():
        pts = [(d['x'], d['y']) for d in ps]
        t = mst(pts)
        L = sum(e[2] for e in t)
        net_len[n] = L
        by_class[net_class(n, spec.PATTERNS)] += L
        segs += [(n, pts[i], pts[j]) for i, j, _ in t]
    cross, per = count_crossings(segs)
    out['signal_nets'] = len(sig)
    out['wire_mm'] = round(sum(net_len.values()), 1)
    out['wire_by_class_mm'] = {k: round(v, 1) for k, v in sorted(by_class.items())}
    out['crossings'] = cross
    out['crossings_worst_nets'] = [[short(n), k] for n, k in sorted(per.items(), key=lambda t: (-t[1], t[0]))[:10]]

    # wrong-side pins
    ics = bd.ic_refs()
    ws = {}
    for u in sorted(ics):
        cx, cy = bd.fp_xy[u]
        n_far, bad, worst = 0, 0, []
        for d in [d for d in bd.pads if d['ref'] == u]:
            if not d['net'] or d['net'] in planes or d['net'] not in sig:
                continue
            others = [q for q in sig[d['net']] if q['ref'] != u and not q['ref'].startswith('TP')]
            if not others:
                continue
            q = min(others, key=lambda q: (math.hypot(q['x'] - d['x'], q['y'] - d['y']), q['ref'], q['num']))
            dist = math.hypot(q['x'] - d['x'], q['y'] - d['y'])
            if dist <= WRONG_SIDE_MIN_MM:
                continue
            n_far += 1
            a1 = math.atan2(d['y'] - cy, d['x'] - cx); a2 = math.atan2(q['y'] - cy, q['x'] - cx)
            e = math.degrees(abs((a2 - a1 + math.pi) % (2 * math.pi) - math.pi))
            if e > 90:
                bad += 1
                worst.append([d['num'], short(d['net']), q['ref'], round(dist, 1), round(e)])
        ws[u] = {'far_pins': n_far, 'wrong_side': bad,
                 'worst': sorted(worst, key=lambda w: (-w[4], w[0]))[:6]}
    out['wrong_side'] = ws
    out['wrong_side_total'] = sum(v['wrong_side'] for v in ws.values())

    # test point stubs
    stubs = {}
    for d in bd.pads:
        if not d['ref'].startswith('TP') or short(d['net']) == 'GND' or not d['net']:
            continue
        others = [q for q in bd.by_net[d['net']] if not q['ref'].startswith('TP')]
        if not others:
            continue
        near = min(math.hypot(q['x'] - d['x'], q['y'] - d['y']) for q in others)
        pts = [(q['x'], q['y']) for q in others]
        t = mst(pts)
        route = min((seg_dist((d['x'], d['y']), pts[i], pts[j]) for i, j, _ in t), default=near)
        stubs[d['ref']] = {'net': short(d['net']), 'to_pad': round(near, 1), 'to_route': round(route, 1)}
    out['tp_stubs'] = stubs
    rt = sorted(v['to_route'] for v in stubs.values())
    pd_ = sorted(v['to_pad'] for v in stubs.values())
    out['tp_stub_summary'] = {'n': len(rt), 'median_to_route': rt[len(rt) // 2] if rt else None,
                              'median_to_pad': pd_[len(pd_) // 2] if pd_ else None,
                              'over_10_to_route': sum(1 for v in rt if v > 10), 'over_20_to_route': sum(1 for v in rt if v > 20)}

    out['near'] = near_rules(bd, spec)
    out['near_misses'] = sum(len(r['misses']) for r in out['near'])
    out['near_accepted'] = sum(len(r['accepted']) for r in out['near'])
    out['near_measured'] = f"{sum(r['measured'] for r in out['near'])} distances in {len(out['near'])} rows" 
    # D-24Nov.1: every passive has a rule of its own, naming the part and the pin it serves
    named = {r['part'] for r in getattr(spec, 'NEAR', []) if r.get('part') and r['rule'] in ('part_to_pins', 'on_line')}
    out['passives_without_rule'] = sorted({d['ref'] for d in bd.pads if re.match(r'^(R|C|L|FB|F)\d+$', d['ref'])} - named)
    # D-24Nov.4: each chip a rule serves has its maker's layout section read and cited (spec.LAYOUT_REFS)
    served = {r['ic'] for r in getattr(spec, 'NEAR', []) if r.get('ic', '').startswith('U') and r.get('part')}
    out['chips_without_layout_ref'] = sorted(served - set(getattr(spec, 'LAYOUT_REFS', {})))
    # D-24Nov.11: scripted copper stays out of other fine-pitch pins' lanes
    n_lanes, crossed = lanes_crossed(bd)
    out['lanes_measured'] = n_lanes
    out['lanes_crossed'] = crossed

    # the plane pads still open after the routing trial's own fan-out (D-24Nov.17): `fan` is meter.fan_out's result
    # with spec.TRIAL_FANOUT, so the build reports the trial's number
    if fan is not None:
        fr = fan['fr']
        out['plane_pads'] = fan['plane_pads']
        out['plane_pads_open'] = len(fan['plane_pads_open'])
        bands = getattr(spec, 'BANDS', {})
        at = {f"{d['ref']}.{d['num']}": d['y'] for d in bd.pads}
        fb = defaultdict(int)
        for name in fan['plane_pads_open']:
            y = at.get(name)
            band = next((k for k, (y0, y1) in bands.items() if y is not None and y0 <= y < y1), '?')
            fb[band] += 1
        out['plane_pads_open_by_band'] = dict(sorted(fb.items()))
        out['plane_pads_open_list'] = fan['plane_pads_open'][:60]
        out['plane_fanout'] = {'settings': fan['settings'], 'vias': sum(1 for d in fr['done'] if d.get('via')),
                               'in_pad': sum(1 for d in fr['done'] if d.get('via') and d['stub'] is None),
                               'by_group': sum(1 for d in fr['done'] if d.get('by_group')),
                               'scripted_joined': len(fan['existing']['joined'])}

    return out


def _gap(a, b):
    """Copper gap between two pads (edge to edge on a shared layer), else centre to centre."""
    shared = [l for l in a['poly'] if l in b['poly']]
    if shared:
        return min(a['poly'][l].distance(b['poly'][l]) for l in shared)
    return math.hypot(a['x'] - b['x'], a['y'] - b['y'])


def _match(pins, caps, limit):
    """Pins matched one to one to caps within limit (augmenting paths); returns the unmatched pins."""
    edges = {i: [j for j, c in enumerate(caps) if _gap(p, c) <= limit] for i, p in enumerate(pins)}
    owner = {}

    def take(i, seen):
        for j in edges[i]:
            if j not in seen:
                seen.add(j)
                if j not in owner or take(owner[j], seen):
                    owner[j] = i
                    return True
        return False
    return [pins[i] for i in edges if not take(i, set())]


def rule_pins(row):
    """The pins a part_to_pins row names (D-24Nov.1): a set of pin numbers, or None when any pin on the net counts."""
    p = row.get('pin')
    return None if p is None else {str(p)} if isinstance(p, (str, int)) else {str(q) for q in p}


def near_rules(bd, spec):
    """The distance rules of stage B2 step 6 (spec.NEAR). Each row: the rule, the limit and its source; a miss lists
    what is too far and by how much. Rules:
      supply_caps  every supply pin of `ic` has its own cap of `value` on its net within `mm` (one to one). The pins
                   are `ic`'s pads on `nets` when the row names them: the board's pads carry no pin types, so a row
                   without `nets` finds no pins and can't miss (it measured nothing before 23 November);
      net_caps     on each of `nets`, a cap pad within `mm` of `ic`'s pad on that net;
      part_to_pins each pad of `part` within `mm` of `ic`'s pad on the same net; with `pin` (a pin number or a tuple
                   of them, D-24Nov.1), only that pin counts, so the part must sit at the pin it serves;
      on_line      `part`'s pad on `net` within `mm` of the line from `from`'s pad to `to`'s pad, between them; with
                   line='drawn' (D-24Nov.11), within `mm` of `net`'s drawn L1 copper instead, once the line is drawn."""
    out = []
    pads_of = defaultdict(list)
    for d in bd.pads:
        pads_of[d['ref']].append(d)
    is_cap = lambda r: r.startswith('C') and r[1:].isdigit()
    for row in getattr(spec, 'NEAR', []):
        rule, mm, miss, n = row['rule'], row['mm'], [], 0          # n: how many distances this row measured
        if rule == 'supply_caps':
            if 'nets' in row:
                pins = [d for d in pads_of[row['ic']] if d['net'] and short(d['net']) in row['nets']]
            else:
                pins = [d for d in pads_of[row['ic']] if d['net'] and short(d['net']) != 'GND'
                        and d['pintype'] == 'power_in' and 'VCAP' not in d['pinfn']]
            n = len(pins)
            for net in sorted({d['net'] for d in pins}):
                caps = [d for d in bd.by_net[net] if is_cap(d['ref']) and row['value'] in bd.value.get(d['ref'], '')]
                for d in _match([q for q in pins if q['net'] == net], caps, mm):
                    near_c = min((_gap(d, c) for c in caps), default=None)
                    miss.append(f"{row['ic']}.{d['num']} {short(net)}: nearest {row['value']} {near_c:.1f} mm" if near_c is not None
                                else f"{row['ic']}.{d['num']} {short(net)}: no {row['value']}")
        elif rule == 'net_caps':
            for net in row['nets']:
                full = next((n for n in bd.by_net if short(n) == net), None)
                ic = [d for d in bd.by_net.get(full, []) if d['ref'] == row['ic']]
                caps = [d for d in bd.by_net.get(full, []) if is_cap(d['ref'])]
                g = min((_gap(a, c) for a in ic for c in caps), default=None)
                n += g is not None
                if g is None or g > mm:
                    miss.append(f"{row['ic']} {net}: nearest cap {g:.1f} mm" if g is not None else f"{row['ic']} {net}: no cap")
        elif rule == 'part_to_pins':
            pins, hit = rule_pins(row), False
            for d in pads_of[row['part']]:
                if not d['net'] or short(d['net']) == 'GND':
                    continue
                ic = [q for q in bd.by_net[d['net']] if q['ref'] == row['ic'] and (pins is None or q['num'] in pins)]
                if ic:
                    hit, n = True, n + 1
                    g = min(_gap(d, q) for q in ic)
                    if g > mm:
                        at = '/'.join(sorted({q['num'] for q in ic}, key=lambda n: (len(n), n))) if pins else ''
                        miss.append(f"{row['part']}.{d['num']} to {row['ic']}{'.' + at if at else ''}: {g:.1f} mm")
            if pins is not None and not hit:
                miss.append(f"{row['part']}: shares no net with {row['ic']}.{'/'.join(sorted(pins))}")
        elif rule == 'on_line':
            full = next((n for n in bd.by_net if short(n) == row['net']), None)
            on = {d['ref']: d for d in bd.by_net.get(full, [])}
            a, b, d = on.get(row['from']), on.get(row['to']), on.get(row['part'])
            if not (a and b and d):
                miss.append(f"{row['part']}: not on {row['net']} with {row['from']} and {row['to']}")
            elif row.get('line') == 'drawn':           # the drawn line, not the chord (D-24Nov.11)
                cu = _net_l1_copper(bd, row['net'])
                if not cu or 'F' not in d['poly']:
                    miss.append(f"{row['part']}: {row['net']} has no drawn L1 line to measure from")
                else:
                    n = 1
                    off = min(g.distance(d['poly']['F']) for g in cu)
                    if off > mm:
                        miss.append(f"{row['part']}: {off:.1f} mm off the drawn {row['net']} line")
            else:
                n = 1
                ax, ay, bx, by = a['x'], a['y'], b['x'], b['y']
                L2 = (bx - ax) ** 2 + (by - ay) ** 2
                t = ((d['x'] - ax) * (bx - ax) + (d['y'] - ay) * (by - ay)) / L2 if L2 else 0.0
                off = seg_dist((d['x'], d['y']), (ax, ay), (bx, by))
                if off > mm or not 0.0 <= t <= 1.0:
                    miss.append(f"{row['part']}: {off:.1f} mm off the line, at {t:.2f} along it")
        if n == 0 and not miss:                       # zero misses out of zero measured is a failure (D-24Nov.4)
            miss.append(f"{row.get('part') or row.get('ic')}: measured nothing")
        out.append({'rule': rule, 'what': row.get('part') or row.get('ic'), 'mm': mm, 'source': row['src'],
                    'measured': n, 'misses': miss, 'accepted': []})
    # written exceptions (D-24Nov.2, D-24Nov.6): a miss is accepted only once Seán has approved the exception and its
    # mitigation is drawn or checked; until then it stays a miss, saying what is missing
    first = {r['what']: r for r in out}
    for row, r in zip(getattr(spec, 'NEAR', []), out):
        ex = row.get('exception')
        if not ex or not r['misses']:
            continue
        ex = ex if isinstance(ex, dict) else {'why': ex}
        lack = [] if ex.get('approved') else ['not approved by Seán']
        chk = ex.get('check')
        if chk and not _mitigated(bd, first, chk):
            lack.append(f'mitigation not in place: {chk[0]} {chk[1]}')
        if lack:
            r['misses'] = [f"{m} (exception: {'; '.join(lack)})" for m in r['misses']]
        else:
            r['accepted'], r['misses'] = [f"{m} ({ex['why']}; {ex['approved']})" for m in r['misses']], []
    return out


def _mitigated(bd, rows, chk):
    """An exception's mitigation, checked on the board: ('drawn', net) the net's copper is drawn, on In2.Cu among
    other layers, and touches every one of its pads; ('passes', part) that part's own rule holds; ('within', part, ic,
    pins, mm) that part sits within mm of one of those pins."""
    kind = chk[0]
    if kind == 'passes':
        r = rows.get(chk[1])
        return bool(r and r['measured'] and not r['misses'])
    if kind == 'within':
        _, part, ic, pins, mm = chk
        pins = {pins} if isinstance(pins, str) else set(pins)
        mine = [d for d in bd.pads if d['ref'] == part and d['net'] and short(d['net']) != 'GND']
        theirs = [d for d in bd.pads if d['ref'] == ic and d['num'] in pins]
        gs = [_gap(a, b) for a in mine for b in theirs if a['net'] == b['net']]
        return bool(gs) and min(gs) <= mm
    if kind == 'drawn':
        from shapely.geometry import LineString, Point
        net, K = chk[1], bd.K
        cu, layers = [], set()
        for t in bd.b.GetTracks():
            if short(t.GetNetname()) != net:
                continue
            if t.GetClass() == 'PCB_VIA':
                c = t.GetPosition()
                cu.append(Point(K.ToMM(c.x) - bd.ox, K.ToMM(c.y) - bd.oy).buffer(K.ToMM(t.GetWidth(K.F_Cu)) / 2))
                continue
            layers.add(bd.b.GetLayerName(t.GetLayer()))
            if t.GetLayer() == K.F_Cu:
                a, e = t.GetStart(), t.GetEnd()
                cu.append(LineString([(K.ToMM(a.x) - bd.ox, K.ToMM(a.y) - bd.oy),
                                      (K.ToMM(e.x) - bd.ox, K.ToMM(e.y) - bd.oy)]).buffer(K.ToMM(t.GetWidth()) / 2))
        pads = [d for d in bd.pads if d['net'] and short(d['net']) == net and 'F' in d['poly']]
        return 'In2.Cu' in layers and bool(pads) and all(any(g.intersects(d['poly']['F']) for g in cu) for d in pads)
    return False


LANE_LEN, FINE_PITCH = 1.5, 0.65              # D-24Nov.11: the strip straight out from a pin's end; pin pitch, mm


def nets_drawn_whole(bd):
    """The nets whose pads all join through drawn copper (tracks, vias and pads; zones aside): such a pin needs no
    lane (D-24Nov.13). A track joins what it touches on its layer; a via, and a through-hole pad, every layer."""
    from shapely.geometry import LineString, Point
    K = bd.K
    items = defaultdict(list)                         # net -> [(layers or None for all, shape, is_pad)]
    for d in bd.pads:
        if not d['net']:
            continue
        if d['tht']:
            g = d['poly'].get('F') or d['poly'].get('B')
            if g is not None:
                items[short(d['net'])].append((None, g, True))
        else:
            for lay in d['layers']:
                items[short(d['net'])].append((({'F': 'F.Cu', 'B': 'B.Cu'}[lay],), d['poly'][lay], True))
    for t in bd.b.GetTracks():
        n = short(t.GetNetname())
        if n not in items:
            continue
        if t.GetClass() == 'PCB_VIA':
            c = t.GetPosition()
            items[n].append((None, Point(K.ToMM(c.x) - bd.ox, K.ToMM(c.y) - bd.oy).buffer(K.ToMM(t.GetWidth(K.F_Cu)) / 2), False))
        else:
            a, e = t.GetStart(), t.GetEnd()
            items[n].append(((bd.b.GetLayerName(t.GetLayer()),),
                             LineString([(K.ToMM(a.x) - bd.ox, K.ToMM(a.y) - bd.oy),
                                         (K.ToMM(e.x) - bd.ox, K.ToMM(e.y) - bd.oy)]).buffer(K.ToMM(t.GetWidth()) / 2), False))
    whole = set()
    for net, its in items.items():
        pads = [i for i, it in enumerate(its) if it[2]]
        if len(pads) < 2 or len(its) == len(pads):
            continue                                  # one pad, or no drawn copper on the net
        parent = list(range(len(its)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for i in range(len(its)):
            for j in range(i + 1, len(its)):
                li, gi, _ = its[i]
                lj, gj, _ = its[j]
                if (li is None or lj is None or set(li) & set(lj)) and gi.distance(gj) < 1e-4:
                    parent[find(i)] = find(j)
        if len({find(i) for i in pads}) == 1:
            whole.add(net)
    return whole


def pin_lanes(bd, whole=None):
    """Each fine-pitch pin's lane (D-24Nov.11): the strip straight out from its outer end, as wide as the pad and
    LANE_LEN long, for every L1 pad of a part whose neighbouring pin along the row sits FINE_PITCH or closer.
    Pins with no net, GND pins (a via in the pad serves them), and pins whose own net is already drawn whole
    (D-24Nov.13) have none. Returns [(ref, num, net, polygon)]."""
    from shapely.geometry import Polygon
    whole = nets_drawn_whole(bd) if whole is None else whole
    by_ref = defaultdict(list)
    for d in bd.pads:
        g = d['poly'].get('F')
        if g is None or g.is_empty:
            continue
        r = g.minimum_rotated_rectangle
        xy = list(r.exterior.coords)[:4]
        e1 = (xy[1][0] - xy[0][0], xy[1][1] - xy[0][1])
        e2 = (xy[2][0] - xy[1][0], xy[2][1] - xy[1][1])
        l1, l2 = math.hypot(*e1), math.hypot(*e2)
        if min(l1, l2) < 1e-6 or max(l1, l2) / min(l1, l2) < 1.5:
            continue                                  # square or round: not a pin with a direction
        u = e1 if l1 >= l2 else e2
        L = max(l1, l2)
        u = (u[0] / L, u[1] / L)
        by_ref[d['ref']].append((d, g.centroid, u, L, min(l1, l2)))
    out = []
    for ref, ps in by_ref.items():
        if len(ps) < 4:
            continue
        cx = sum(c.x for _, c, *_ in ps) / len(ps)
        cy = sum(c.y for _, c, *_ in ps) / len(ps)
        for d, c, u, L, w in ps:
            net = short(d['net']) if d['net'] else ''
            if not net or net == 'GND' or net.startswith('unconnected-') or net in whole:
                continue
            pitch = min((math.hypot(c.x - c2.x, c.y - c2.y) for d2, c2, u2, *_ in ps
                         if d2 is not d and abs(u[0] * u2[0] + u[1] * u2[1]) > 0.99), default=9.0)
            if pitch > FINE_PITCH + 1e-6:
                continue
            if (c.x - cx) * u[0] + (c.y - cy) * u[1] < 0:
                u = (-u[0], -u[1])                    # outward, away from the part's centre
            nx, ny = -u[1], u[0]
            ex, ey = c.x + u[0] * L / 2, c.y + u[1] * L / 2
            fx, fy = ex + u[0] * LANE_LEN, ey + u[1] * LANE_LEN
            h = w / 2
            out.append((ref, d['num'], net, Polygon([(ex + nx * h, ey + ny * h), (fx + nx * h, fy + ny * h),
                                                     (fx - nx * h, fy - ny * h), (ex - nx * h, ey - ny * h)])))
    return out


def lanes_crossed(bd, extra=()):
    """How many fine-pitch pin lanes there are, and each one another net's L1 track or via crosses (D-24Nov.11).
    `extra`: [(net, shapely)] copper to add, for the planted test."""
    from shapely.geometry import LineString, Point
    K = bd.K
    cu = list(extra)
    for t in bd.b.GetTracks():
        n = short(t.GetNetname())
        if t.GetClass() == 'PCB_VIA':
            c = t.GetPosition()
            cu.append((n, Point(K.ToMM(c.x) - bd.ox, K.ToMM(c.y) - bd.oy).buffer(K.ToMM(t.GetWidth(K.F_Cu)) / 2)))
        elif t.GetLayer() == K.F_Cu:
            a, e = t.GetStart(), t.GetEnd()
            cu.append((n, LineString([(K.ToMM(a.x) - bd.ox, K.ToMM(a.y) - bd.oy),
                                      (K.ToMM(e.x) - bd.ox, K.ToMM(e.y) - bd.oy)]).buffer(K.ToMM(t.GetWidth()) / 2)))
    lanes = pin_lanes(bd)
    crossed = []
    for ref, num, net, lane in lanes:
        hit = sorted({n for n, g in cu if n != net and g.intersects(lane)})
        if hit:
            crossed.append(f"{ref}.{num} {net}: {', '.join(hit)}")
    return len(lanes), crossed


def _net_l1_copper(bd, net):
    """The net's L1 tracks as shapely shapes, board mm."""
    from shapely.geometry import LineString
    K, out = bd.K, []
    for t in bd.b.GetTracks():
        if short(t.GetNetname()) == net and t.GetClass() != 'PCB_VIA' and t.GetLayer() == K.F_Cu:
            a, e = t.GetStart(), t.GetEnd()
            out.append(LineString([(K.ToMM(a.x) - bd.ox, K.ToMM(a.y) - bd.oy),
                                   (K.ToMM(e.x) - bd.ox, K.ToMM(e.y) - bd.oy)]).buffer(K.ToMM(t.GetWidth()) / 2))
    return out


def markdown(m):
    L = ['| Metric | Value |', '| --- | --- |',
         f"| Signal nets | {m['signal_nets']} |",
         f"| Plane nets | {', '.join(f'{k} ({v})' for k, v in m['plane_nets'].items())} |",
         f"| Signal wire, spanning trees (mm) | {m['wire_mm']} |",
         f"| Crossings | {m['crossings']} |",
         f"| Wrong-side pins, all ICs | {m['wrong_side_total']} |"]
    for u, v in m['wrong_side'].items():
        if v['far_pins']:
            L.append(f"| Wrong-side pins, {u} | {v['wrong_side']} of {v['far_pins']} |")
    if 'passives_without_rule' in m:
        L.append(f"| Distance rules: measured | {m.get('near_measured', '')} |")
        L.append(f"| Distance-rule misses / written exceptions / passives without a rule of their own | "
                 f"{m['near_misses']} / {m.get('near_accepted', 0)} / {len(m['passives_without_rule'])} |")
        L.append(f"| Chips served by a rule without their layout section cited | "
                 f"{len(m.get('chips_without_layout_ref', []))} |")
    if 'lanes_measured' in m:
        L.append(f"| Fine-pitch pin lanes crossed by another net's copper (of lanes measured) | "
                 f"{len(m['lanes_crossed'])} of {m['lanes_measured']} |")
    s = m['tp_stub_summary']
    L.append(f"| Test point stubs (median to route / to pad, mm) | {s['median_to_route']} / {s['median_to_pad']} |")
    L.append(f"| Test points over 10 / 20 mm from their route | {s['over_10_to_route']} / {s['over_20_to_route']} |")
    if 'plane_pads' in m:
        L.append(f"| Plane pads open after the routing trial's fan-out (of {m['plane_pads']}) | {m['plane_pads_open']} |")
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    import argparse
    import importlib.util
    import pcbnew as K
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    ap = argparse.ArgumentParser()
    ap.add_argument('pcb')
    ap.add_argument('--spec', default='croi2')
    ap.add_argument('--length', type=float)
    ap.add_argument('--json')
    ap.add_argument('--md')
    a = ap.parse_args()
    root = Path(__file__).resolve().parents[3]
    s = importlib.util.spec_from_file_location('spec', root / 'hardware' / a.spec / 'layout' / 'spec.py')
    spec = importlib.util.module_from_spec(s); s.loader.exec_module(spec)
    from build import stretch
    b = K.LoadBoard(a.pcb)
    bb = b.GetBoardEdgesBoundingBox()
    H = a.length or float(round(K.ToMM(bb.GetHeight())))
    stretch(spec, H)
    bd = BoardData(b, spec.ORIGIN, (spec.W, spec.H))
    import meter                                    # the trial's fan-out and plane-pad count (D-24Nov.17)
    m = measure(bd, spec, meter.fan_out(K.LoadBoard(a.pcb), spec, **spec.TRIAL_FANOUT))
    if a.json:
        Path(a.json).write_text(json.dumps(m, indent=1) + '\n')
    if a.md:
        Path(a.md).write_text(markdown(m))
    print(markdown(m))
