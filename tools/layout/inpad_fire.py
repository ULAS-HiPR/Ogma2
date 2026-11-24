"""inpad_fire.py [REF ...]: a part's pins whose in-pad via site lies under L3 fire logic (D-24Nov.13, call 5).

    python3 tools/layout/inpad_fire.py            (U201)

The routing trial's --via-in-pad puts a pin's via at its pad's centre (engine/fanout.plan, in_pad), Ø0.45 mm
(spec.SIGNAL_VIA). The DRU keeps fire copper 0.5 mm from other nets, and fire logic 0.2 mm where its segment lies
inside a fine-pitch part's escape area (D-23Nov.8, D-23Nov.13). This lists each connected pin whose site is closer
than that to another net's fire, fire-logic or pyro-rail copper on L3 (In2.Cu: tracks, and fire vias, which pass
through it), and splits them: drawn whole (no via needed), GND (the plane fan-out's via), and the rest, signals
that need another escape. Read only; prints the count.
"""
import fnmatch
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build                               # noqa: E402
from engine import board as B              # noqa: E402
from engine import metrics as M            # noqa: E402
from shapely.geometry import LineString, Point, Polygon   # noqa: E402

FIRE = ('FIRE', 'FIRE_LOGIC', 'PYRO_RAIL')
VIA_R = 0.225


def main():
    refs = sys.argv[1:] or ['U201']
    spec = build.load_spec('croi2')
    pcb = build.ROOT / 'hardware' / 'croi2' / f'{spec.NAME}.kicad_pcb'
    K = B.K
    b = K.LoadBoard(str(pcb))
    ox, oy = spec.ORIGIN
    mm = lambda v: (K.ToMM(v.x) - ox, K.ToMM(v.y) - oy)
    cls = lambda n: next((c for c, p in spec.PATTERNS if fnmatch.fnmatchcase(M.short(n), p)), 'Default')
    areas = []                                   # the fine-pitch parts' escape areas (rule areas named *_ESCAPE)
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetZoneName().endswith('_ESCAPE'):
            o = z.Outline().Outline(0)
            areas.append(Polygon([mm(o.CPoint(i)) for i in range(o.PointCount())]))
    fire = []                                    # (net, shape, clearance)
    for t in b.GetTracks():
        n = M.short(t.GetNetname())
        if cls(n) not in FIRE:
            continue
        if t.GetClass() == 'PCB_VIA':
            g = Point(mm(t.GetPosition())).buffer(K.ToMM(t.GetWidth(K.F_Cu)) / 2)
        elif t.GetLayer() == K.In2_Cu:
            g = LineString([mm(t.GetStart()), mm(t.GetEnd())]).buffer(K.ToMM(t.GetWidth()) / 2)
        else:
            continue
        inside = cls(n) == 'FIRE_LOGIC' and any(a.contains(g) for a in areas)
        fire.append((n, g, 0.2 if inside else 0.5))
    bd = M.BoardData(b, spec.ORIGIN, (spec.W, spec.H))
    whole = M.nets_drawn_whole(bd)
    for ref in refs:
        fp = b.FindFootprintByReference(ref)
        rows, n_pins = [], 0
        for p in fp.Pads():
            net = M.short(p.GetNetname())
            if not net or net.startswith('unconnected-'):
                continue
            n_pins += 1
            site = Point(mm(p.GetPosition())).buffer(VIA_R)
            hits = sorted((round(site.distance(g), 3), fn, c) for fn, g, c in fire if fn != net and site.distance(g) < c)
            if hits:
                d, fn, c = hits[0]
                kind = 'drawn whole' if net in whole else 'GND' if net == 'GND' else 'signal'
                rows.append((p.GetNumber(), net, fn, d, c, kind))
        rows.sort(key=lambda r: int(r[0]) if r[0].isdigit() else 0)
        print(f'{ref}: {len(rows)} of {n_pins} connected pins have their in-pad via site under L3 fire copper')
        for kind in ('signal', 'GND', 'drawn whole'):
            sel = [r for r in rows if r[5] == kind]
            print(f'  {kind}: {len(sel)}')
            for num, net, fn, d, c, _ in sel:
                print(f'    {ref}.{num} {net}: {fn} {d} mm (needs {c})')


if __name__ == '__main__':
    main()
