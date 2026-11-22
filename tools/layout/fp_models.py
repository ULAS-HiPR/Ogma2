"""Point Burrito's footprints that had no 3D model at one (22 Nov 2026). Library edit: adds a (model ...)
to each footprint below if it has none; copper untouched. The models are KiCad 9.0.7's (from Ubuntu's
kicad-packages3d 9.0.7-1) or drawn by tools/layout/models3d.py; see libraries/3d/GENERATED.md."""
from pathlib import Path

LIB = Path(__file__).resolve().parents[2] / 'hardware' / 'croi2' / 'libraries'
MODELS = {
    'Ogma2.pretty/ABS07-32.768KHZ-7-T.kicad_mod': 'Crystal.3dshapes/Crystal_SMD_3215-2Pin_3.2x1.5mm.step',
    'Ogma2.pretty/ECS-160-10-36Q-ES-TR.kicad_mod': 'Crystal.3dshapes/Crystal_SMD_2016-4Pin_2.0x1.6mm.step',
    'Ogma2.pretty/BMP390.kicad_mod': 'Package_LGA.3dshapes/ST_HLGA-10_2x2mm_P0.5mm_LayoutBorder3x2y.step',
    'Ogma2.pretty/TPS1H100BQPWPRQ1.kicad_mod': 'Package_SO.3dshapes/Texas_HTSSOP-14-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3.155x3.255mm.step',
    'Ogma2.pretty/TPS7A9101DSKR.kicad_mod': 'Package_SON.3dshapes/WSON-10-1EP_2.5x2.5mm_P0.5mm_EP1.2x2mm.step',
    'Ogma2.pretty/SMA_Amphenol_132134_Vertical.kicad_mod': 'Connector_Coaxial.3dshapes/SMA_Amphenol_132291_Vertical.step',
    'Ogma2.pretty/TPSM63603RDHR.kicad_mod': 'Package_DFN_QFN.3dshapes/Texas_RDH0030A_TPSM63603.step',
    'Ogma2.pretty/MPT-08-01-01-L-RA-SD.kicad_mod': 'Connector_Samtec.3dshapes/Samtec_MPT-08-01-01-L-RA-SD.step',
    'Ogma2_GNSS.pretty/MAX-M10S-00B.kicad_mod': 'RF_GPS.3dshapes/ublox_MAX-M10S.step',
    'TestPoint.pretty/TestPoint_Keystone_5000-5004_Miniature.kicad_mod': 'TestPoint.3dshapes/TestPoint_Keystone_5000-5004_Miniature.step',
}
BLOCK = ('  (model "${{KIPRJMOD}}/libraries/3d/{m}"\n    (offset\n      (xyz 0 0 0))\n    (scale\n      (xyz 1 1 1))\n'
         '    (rotate\n      (xyz 0 0 0))))\n')

if __name__ == '__main__':
    for fp, m in MODELS.items():
        p = LIB / fp
        t = p.read_text()
        assert (LIB / '3d' / m).exists(), m
        if '(model ' in t:
            print('has a model already:', fp)
            continue
        t = t.rstrip()
        assert t.endswith(')')
        p.write_text(t[:-1].rstrip() + '\n' + BLOCK.format(m=m))
        print('model ->', fp)
