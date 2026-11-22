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


def measure(bd, spec, fanout_result=None):
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

    # plane pads with no via spot
    if fanout_result is not None:
        done, failed = fanout_result['done'], fanout_result['failed']
        out['plane_pads'] = len(done) + len(failed)
        out['plane_pads_no_via'] = len(failed)
        bands = getattr(spec, 'BANDS', {})
        fb = defaultdict(int)
        for f in failed:
            band = next((k for k, (y0, y1) in bands.items() if y0 <= f['y'] < y1), '?')
            fb[band] += 1
        out['plane_pads_no_via_by_band'] = dict(sorted(fb.items()))
        out['plane_pads_no_via_list'] = [f"{f['ref']}.{f['num']}" for f in failed][:60]

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


def near_rules(bd, spec):
    """The distance rules of stage B2 step 6 (spec.NEAR). Each row: the rule, the limit and its source; a miss lists
    what is too far and by how much. Rules:
      supply_caps  every supply pin of `ic` has its own cap of `value` on its net within `mm` (one to one);
      net_caps     on each of `nets`, a cap pad within `mm` of `ic`'s pad on that net;
      part_to_pins each pad of `part` within `mm` of `ic`'s pad on the same net;
      on_line      `part`'s pad on `net` within `mm` of the line from `from`'s pad to `to`'s pad, between them."""
    out = []
    pads_of = defaultdict(list)
    for d in bd.pads:
        pads_of[d['ref']].append(d)
    is_cap = lambda r: r.startswith('C') and r[1:].isdigit()
    for row in getattr(spec, 'NEAR', []):
        rule, mm, miss = row['rule'], row['mm'], []
        if rule == 'supply_caps':
            pins = [d for d in pads_of[row['ic']] if d['net'] and short(d['net']) != 'GND' and d['pintype'] == 'power_in'
                    and 'VCAP' not in d['pinfn']]
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
                if g is None or g > mm:
                    miss.append(f"{row['ic']} {net}: nearest cap {g:.1f} mm" if g is not None else f"{row['ic']} {net}: no cap")
        elif rule == 'part_to_pins':
            for d in pads_of[row['part']]:
                if not d['net'] or short(d['net']) == 'GND':
                    continue
                ic = [q for q in bd.by_net[d['net']] if q['ref'] == row['ic']]
                if ic:
                    g = min(_gap(d, q) for q in ic)
                    if g > mm:
                        miss.append(f"{row['part']}.{d['num']} to {row['ic']}: {g:.1f} mm")
        elif rule == 'on_line':
            full = next((n for n in bd.by_net if short(n) == row['net']), None)
            on = {d['ref']: d for d in bd.by_net.get(full, [])}
            a, b, d = on.get(row['from']), on.get(row['to']), on.get(row['part'])
            if not (a and b and d):
                miss.append(f"{row['part']}: not on {row['net']} with {row['from']} and {row['to']}")
            else:
                ax, ay, bx, by = a['x'], a['y'], b['x'], b['y']
                L2 = (bx - ax) ** 2 + (by - ay) ** 2
                t = ((d['x'] - ax) * (bx - ax) + (d['y'] - ay) * (by - ay)) / L2 if L2 else 0.0
                off = seg_dist((d['x'], d['y']), (ax, ay), (bx, by))
                if off > mm or not 0.0 <= t <= 1.0:
                    miss.append(f"{row['part']}: {off:.1f} mm off the line, at {t:.2f} along it")
        out.append({'rule': rule, 'what': row.get('part') or row.get('ic'), 'mm': mm, 'source': row['src'], 'misses': miss})
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
    s = m['tp_stub_summary']
    L.append(f"| Test point stubs (median to route / to pad, mm) | {s['median_to_route']} / {s['median_to_pad']} |")
    L.append(f"| Test points over 10 / 20 mm from their route | {s['over_10_to_route']} / {s['over_20_to_route']} |")
    if 'plane_pads' in m:
        L.append(f"| Plane pads without a via spot (of {m['plane_pads']}) | {m['plane_pads_no_via']} |")
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
    from engine import fanout as FO
    fr = FO.plan(bd, plane_nets(bd, set(spec.RAILS)), spec)
    m = measure(bd, spec, fr)
    if a.json:
        Path(a.json).write_text(json.dumps(m, indent=1) + '\n')
    if a.md:
        Path(a.md).write_text(markdown(m))
    print(markdown(m))
