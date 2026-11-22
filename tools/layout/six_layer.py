"""A six-layer copy of a placed board, for the layer test (decisions.md, Open: four layers or six; execution brief,
"Layer test"). A trial copy only: the real board is never touched.

    python3 tools/layout/six_layer.py IN.kicad_pcb OUT.kicad_pcb

Copper becomes six layers, on JLC's six-layer 1.6 mm stackup as its PCB stackup FAQ gives it
(https://jlcpcb.com/quote/pcbOrderFaq/PCB%20Stackup, read 22 Nov 2026: the "2313" structure; 3313 prepreg replaced
2313 at the same thickness and dielectric constant). Its layers pair up tightly: L1-L2 0.1 mm, L3-L4 0.127 mm,
L5-L6 0.1 mm, with 0.565 mm cores between the pairs. Through-hole pads and through vias reach every layer as they
are; the hole washers' rule areas gain the two new inner layers. The router doesn't read the stackup.
"""
import sys
from pathlib import Path

import pcbnew as K

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import post as P                     # noqa: E402

STACKUP6 = [
    ('F.SilkS', 'Top Silk Screen', None, None, None),
    ('F.Paste', 'Top Solder Paste', None, None, None),
    ('F.Mask', 'Top Solder Mask', 0.01, None, None),
    ('F.Cu', 'copper', 0.035, None, None),
    ('dielectric 1', 'prepreg', 0.0994, 4.05, '3313'),
    ('In1.Cu', 'copper', 0.0152, None, None),
    ('dielectric 2', 'core', 0.565, 4.6, 'FR4'),
    ('In2.Cu', 'copper', 0.0152, None, None),
    ('dielectric 3', 'prepreg', 0.127, 4.25, '2116'),
    ('In3.Cu', 'copper', 0.0152, None, None),
    ('dielectric 4', 'core', 0.565, 4.6, 'FR4'),
    ('In4.Cu', 'copper', 0.0152, None, None),
    ('dielectric 5', 'prepreg', 0.0994, 4.05, '3313'),
    ('B.Cu', 'copper', 0.035, None, None),
    ('B.Mask', 'Bottom Solder Mask', 0.01, None, None),
    ('B.Paste', 'Bottom Solder Paste', None, None, None),
    ('B.SilkS', 'Bottom Silk Screen', None, None, None),
]


def main(src, dst):
    b = K.LoadBoard(src)
    b.SetCopperLayerCount(6)
    for z in b.Zones():
        if z.GetIsRuleArea():
            ls = z.GetLayerSet()
            if ls.Contains(K.In1_Cu):                   # a keep-out on the inner layers covers the new ones too
                ls.AddLayer(K.In3_Cu)
                ls.AddLayer(K.In4_Cu)
                z.SetLayerSet(ls)
    K.SaveBoard(dst, b)
    P.finish(dst, STACKUP6, 'six-layer-trial')
    c = K.LoadBoard(dst)
    print('copper layers', c.GetCopperLayerCount(), [c.GetLayerName(l) for l in c.GetEnabledLayers().CuStack()])


if __name__ == '__main__':
    main(*sys.argv[1:3])
