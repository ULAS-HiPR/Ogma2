"""The RF lines' fence and keep-aways on Burrito's built board (D-22Nov.16, stage C/D review call 8, D-24Nov.8).

    python3 tools/layout/rf_check.py [BOARD]

Fence: walking each RF line of spec._rf_lines() every 0.05 mm, the point 0.6 mm to each side is either inside a
part's courtyard (exempt: "outside a part's own footprint") or within 1.0 mm of a GND via or GND pad, so no gap along
a side exceeds 2 mm. Keep-aways (Seeed Wio-LR2021 PCB guide; u-blox UBX-20053088 3.3): each line to the buck module
and any inductor (20 mm), the crystals (15 mm), the USB parts (10 mm), and the other radio (5 mm).
Then the planted miss (D-24Nov.4): the same fence check with one fence via taken away must report a gap.
Prints what it measured and exits non-zero on a gap, a keep-away under its distance, or a planted miss not caught.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build                                 # noqa: E402
import pcbnew as K                           # noqa: E402
from shapely.geometry import LineString, Point, box   # noqa: E402
from shapely.ops import unary_union          # noqa: E402

OFFSET, REACH, STEP = 0.6, 1.0, 0.05


def main():
    board = sys.argv[1] if len(sys.argv) > 1 else 'croi2'
    spec = build.load_spec(board)
    b = K.LoadBoard(str(build.ROOT / 'hardware' / board / f'{spec.NAME}.kicad_pcb'))
    ox, oy = spec.ORIGIN
    M = lambda v: (K.ToMM(v.x) - ox, K.ToMM(v.y) - oy)
    short = lambda n: n.rsplit('/', 1)[-1]
    crt, gnd_pads, vias = {}, [], []
    for fp in b.GetFootprints():
        c = fp.GetCourtyard(K.F_Cu)
        if c.OutlineCount():
            bb = c.BBox()
            crt[fp.GetReference()] = box(*M(bb.GetPosition()), *M(bb.GetEnd()))
        for p in fp.Pads():
            if short(p.GetNetname()) == 'GND' and p.IsOnLayer(K.F_Cu):
                bb = p.GetBoundingBox()
                gnd_pads.append(box(*M(bb.GetPosition()), *M(bb.GetEnd())))
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA' and short(t.GetNetname()) == 'GND':
            vias.append(Point(*M(t.GetPosition())).buffer(K.ToMM(t.GetWidth(K.F_Cu)) / 2))
    crt_u = unary_union(list(crt.values()))
    lines = [(it['net'], it['path']) for it in spec._rf_lines() if 'path' in it and it['net'] != 'GND']

    def fence(vs, quiet=False):
        g, worst_all, n_all = unary_union(gnd_pads + vs), 0.0, 0
        for net, pts in lines:
            for side in (1, -1):
                n = ex = 0
                worst = (0.0, None)
                for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                    L = math.dist((x0, y0), (x1, y1))
                    ux, uy = (x1 - x0) / L, (y1 - y0) / L
                    for k in range(int(L / STEP) + 1):
                        px, py = x0 + ux * k * STEP, y0 + uy * k * STEP
                        q = Point(px - side * uy * OFFSET, py + side * ux * OFFSET)
                        n += 1
                        if crt_u.contains(q):
                            ex += 1
                            continue
                        d = q.distance(g)
                        if d > worst[0]:
                            worst = (d, (round(q.x, 2), round(q.y, 2)))
                worst_all, n_all = max(worst_all, worst[0]), n_all + n
                if not quiet:
                    print(f"fence {net} side {'+' if side > 0 else '-'}: {n} points, {ex} inside a courtyard, worst "
                          f"{worst[0]:.2f} mm from ground at {worst[1]}: {'ok' if worst[0] <= REACH else 'GAP'}")
        return worst_all <= REACH, n_all

    ok, n = fence(vias)
    print(f'fence: {n} points measured, {"no gap over 2 mm" if ok else "a gap over 2 mm"}')
    fails = 0 if ok else 1
    refs = list(crt)
    keep = [('the buck module and inductors', [r for r in refs if r[0] == 'L' and r[1:].isdigit()] + ['U1301'], 20.0),
            ('the crystals', [r for r in refs if r.startswith('Y')], 15.0),
            ('the USB parts', ['J4401', 'D4401', 'R4405', 'R4406'], 10.0)]
    shapes = {net: LineString(pts) for net, pts in lines}
    other = {'GNSS_RF': 'U4606', 'LORA_RF_SUBG': 'U4504'}
    for net, ln in shapes.items():
        rows = keep + [(f'the other radio, {other[net]}', [other[net]], 5.0)]
        for what, rs, mm in rows:
            d, r = min((ln.distance(crt[r]), r) for r in rs if r in crt)
            print(f'keep-away {net} to {what}: {d:.1f} mm ({r}), at least {mm}: {"ok" if d >= mm else "SHORT"}')
            fails += d < mm
    # the planted miss: the fence via nearest the middle of the LoRa line's run below D4601, taken away
    mid = Point(12.9, 10.4)
    drop = min(range(len(vias)), key=lambda i: vias[i].centroid.distance(mid))
    caught = not fence(vias[:drop] + vias[drop + 1:], quiet=True)[0]
    c = vias[drop].centroid
    print(f'planted miss: fence via at ({c.x:.2f}, {c.y:.2f}) taken away -> {"gap reported" if caught else "NOT caught"}')
    fails += not caught
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
