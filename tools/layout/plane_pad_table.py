"""plane_pad_table.py TRIAL_DIR OUT.json: why each open plane pad has no via (D-24Nov.16, step 1).

    python3 tools/layout/plane_pad_table.py /root/layers/<trial> /cap/x.json

Run in the KiCad chroot on a routing trial's folder: its fanned board (fan-out vias in, so the open pads must clear
them) and its meter.json (the open plane pads, meter.plane_pads_open). For each open pad, with true copper shapes
(tracks at their own width, which the fan-out models as 0.3 mm stubs):

- centre: a via in the middle of the pad, and what rejects it (the closest shortfall: what, gap, needed);
- along: the nearest in-pad site along the pad's long axis that clears, as an offset from the centre;
- beside: the fan-out's first site off the pad, straight out of its outer end, and what rejects it;
- at JLC's 0.1: whether the centre or an along site would clear if GND kept JLC's 0.1 mm instead of its class's
  0.2 mm (the layout brief's table gives 0.2 mm for pours; the spec applies it to every GND item);
- its own capacitor: for a chip's pin, the capacitor spec.PASSIVE_PINS ties to that pin, else the chip's capacitor
  whose pad on the same net is nearest; for a capacitor or resistor pad, none (the nearest joined pad is used).

Writes the rows as JSON; the L1 joins to the capacitors are routed after, by l1_route.py (independent)."""
import fnmatch
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build                                     # noqa: E402
import pcbnew as K                               # noqa: E402
from engine import fanout as FO                  # noqa: E402
from engine import metrics as M                  # noqa: E402
from shapely.geometry import LineString, Point   # noqa: E402

VR = FO.VIA_D / 2


def main():
    trial, out = Path(sys.argv[1]), sys.argv[2]
    spec = build.load_spec('croi2')
    b = K.LoadBoard(str(trial / 'fanned.kicad_pcb'))
    opened = json.load(open(trial / 'meter.json'))['plane_pads']['open']
    bd = M.BoardData(b, spec.ORIGIN, (spec.W, spec.H))
    ox, oy = spec.ORIGIN
    mm = lambda v: (K.ToMM(v.x) - ox, K.ToMM(v.y) - oy)
    pair = FO.clearances(spec)
    cls_cl = {c['name']: c['clearance'] for c in spec.NETCLASSES}

    def pair_jlc(n1, n2):                       # GND at JLC's 0.1 instead of its class's 0.2
        c = pair(n1, n2)
        if M.short(n1) == 'GND' or M.short(n2) == 'GND':
            other = n2 if M.short(n1) == 'GND' else n1
            if abs(c - (cls_cl['GND'] + FO.EPS)) < 1e-9:
                oc = next((cls_cl[c_] for c_, p in spec.PATTERNS if fnmatch.fnmatchcase(M.short(other), p)), 0.1)
                c = max(0.1, oc) + FO.EPS
        return c
    # copper, true shapes: (shape, net, what, layers) ; layers: 'F', 'B' or 'in' (inner) or 'all'
    cu = []
    for i, d in enumerate(bd.pads):
        for side in ('F', 'B'):
            if side in d['poly']:
                cu.append((d['poly'][side], d['net'], f"pad {d['ref']}.{d['num']}", side, i))
    for t in b.GetTracks():
        n = t.GetNetname()
        if t.Type() == K.PCB_VIA_T:
            cu.append((Point(mm(t.GetPosition())).buffer(K.ToMM(t.GetWidth(K.F_Cu)) / 2), n,
                       f'via {M.short(n)}', 'all', None))
        else:
            lay = b.GetLayerName(t.GetLayer())
            cu.append((LineString([mm(t.GetStart()), mm(t.GetEnd())]).buffer(K.ToMM(t.GetWidth()) / 2), n,
                       f'{lay} {M.short(n)}', 'F' if lay == 'F.Cu' else ('B' if lay == 'B.Cu' else 'in'), None))
    holes = [(d['x'], d['y'], d['hole'], d['net']) for d in bd.pads if d['hole']]
    washers = [(x, y) for x, y in spec.HOLES]
    from shapely import STRtree
    tree = STRtree([g for g, *_ in cu])

    def check(x, y, net, own, in_pad, pr=pair):
        """Shortfalls [(short, what, gap, need)] for a via at (x, y), worst first."""
        v = Point(x, y)
        out = []
        if not (VR + FO.EDGE <= x <= spec.W - VR - FO.EDGE and VR + FO.EDGE <= y <= spec.H - VR - FO.EDGE):
            out.append((1.0, 'board edge', 0, FO.EDGE))
        for wx, wy in washers:
            dd = math.hypot(x - wx, y - wy) - VR
            if dd < spec.HOLE_TRACK_KEEPOUT_D / 2:
                out.append((spec.HOLE_TRACK_KEEPOUT_D / 2 - dd, 'mounting hole', round(dd, 3), spec.HOLE_TRACK_KEEPOUT_D / 2))
        for hx, hy, hr, hn in holes:
            dd = math.hypot(x - hx, y - hy) - hr - FO.DRILL / 2
            if dd < FO.HOLE_GAP:
                out.append((FO.HOLE_GAP - dd, 'hole', round(dd, 3), FO.HOLE_GAP))
        for k in tree.query(v, predicate='dwithin', distance=VR + 1.1):
            g, n, what, lay, i = cu[k]
            gap = g.distance(v) - VR
            if what.startswith('via') and n == net:
                dd = g.centroid.distance(v)
                if dd < FO.DRILL + FO.HOLE_GAP:
                    out.append((FO.DRILL + FO.HOLE_GAP - dd, what + ' (holes)', round(dd, 3), FO.DRILL + FO.HOLE_GAP))
                continue
            if n == net and not what.startswith('pad'):
                continue
            if what.startswith('pad'):
                if in_pad:                                 # in the pad: other nets' pads at their clearance
                    if n == net:
                        continue
                    need = pr(net, n)
                else:                                      # beside: off every pad (fanout.copper_ok)
                    if i == own:
                        continue
                    need = max(pr(net, n), FO.MASK_WEB) if n != net else FO.MASK_WEB
                if gap < need - 1e-6:
                    out.append((need - gap, what, round(gap, 3), round(need, 3)))
                continue
            need = pr(net, n)
            if gap < need - 1e-6:
                out.append((need - gap, what, round(gap, 3), round(need, 3)))
        return sorted(out, reverse=True)

    def fmt(sf):
        return '; '.join(f'{w} {g} < {n}' for _, w, g, n in sf[:2]) if sf else 'clears'
    idx = {(d['ref'], d['num']): i for i, d in enumerate(bd.pads)}
    PP = {}
    for cap, chip, pin, dist, kind in spec.PASSIVE_PINS:
        PP.setdefault((chip, pin), []).append(cap)
    caps_of = {}
    for cap, chip, pin, dist, kind in spec.PASSIVE_PINS:
        caps_of.setdefault(chip, set()).add(cap)
    rows = []
    for name in opened:
        ref, num = name.split('.', 1)
        i = idx[(ref, num)]
        d = bd.pads[i]
        g, net = d['poly']['F'], d['net']
        c = g.centroid
        # the pad's long axis: its minimum rotated rectangle's longer side
        mrr = list(g.minimum_rotated_rectangle.exterior.coords)[:4]
        e1, e2 = (mrr[1][0] - mrr[0][0], mrr[1][1] - mrr[0][1]), (mrr[2][0] - mrr[1][0], mrr[2][1] - mrr[1][1])
        ax = e1 if math.hypot(*e1) >= math.hypot(*e2) else e2
        L = math.hypot(*ax)
        ux, uy = ax[0] / L, ax[1] / L
        sides = sorted((math.hypot(*e1), math.hypot(*e2)))
        fx, fy = bd.fp_xy[ref]
        if (c.x - fx) * ux + (c.y - fy) * uy < 0:              # point the axis away from the part's centre
            ux, uy = -ux, -uy
        centre = check(c.x, c.y, net, i, True)
        along, along_jlc = None, None
        for k in range(1, int(L / 0.025) + 1):
            for sgn in (1, -1):
                t = sgn * k * 0.025
                x, y = c.x + t * ux, c.y + t * uy
                if not g.contains(Point(x, y)):
                    continue
                if along is None and not check(x, y, net, i, True):
                    along = round(t, 3)
                if along_jlc is None and not check(x, y, net, i, True, pr=pair_jlc):
                    along_jlc = round(t, 3)
        r = 0.0
        while Point(c.x + r * ux, c.y + r * uy).distance(g) < VR + FO.MASK_WEB:
            r += 0.05
        beside = check(c.x + r * ux, c.y + r * uy, net, i, False)
        jlc_ok = (not check(c.x, c.y, net, i, True, pr=pair_jlc)) or along_jlc is not None
        own = None
        if ref[0] == 'U':
            cands = PP.get((ref, num), [])
            if not cands:                                       # the chip's capacitor with a pad on this net nearest
                best = None
                for cap in caps_of.get(ref, ()):
                    for j, q in enumerate(bd.pads):
                        if q['ref'] == cap and q['net'] == net and 'F' in q['poly']:
                            dd = q['poly']['F'].distance(g)
                            if best is None or dd < best[0]:
                                best = (dd, cap, q['num'])
                own = best and [best[1], best[2]]
            else:
                cap = cands[0]
                q = next((q for q in bd.pads if q['ref'] == cap and q['net'] == net), None)
                own = q and [cap, q['num']]
        rows.append(dict(pad=name, net=M.short(net), value=b.FindFootprintByReference(ref).GetValue(),
                         size=[round(s, 2) for s in sides], centre=fmt(centre), along=along,
                         beside=fmt(beside), jlc=jlc_ok if M.short(net) == 'GND' else None, along_jlc=along_jlc,
                         own=own))
    json.dump(rows, open(out, 'w'), indent=1)
    for r in rows:
        print(r)


if __name__ == '__main__':
    main()
