"""Step 11c: J4401's footprint (Ogma2:USB4105-GF-A) writes its two NPTH locating holes on "*.Cu", as
KiCad 9 saves an unplated hole on a four-layer board. The library said "F&B.Cu", so every board copy
differed from it (DRC lib_footprint_mismatch, 22 Nov). An unplated hole has no copper; nothing physical changes.
"""
from pathlib import Path

FP = Path(__file__).resolve().parents[3] / 'libraries' / 'Ogma2.pretty' / 'USB4105-GF-A.kicad_mod'

if __name__ == '__main__':
    t = FP.read_text()
    old = '(layers "F&B.Cu" "*.Mask")'
    n = t.count(old)
    assert n in (0, 2), n
    FP.write_text(t.replace(old, '(layers "*.Cu" "*.Mask")'))
    print('step 11c:', n, 'NPTH pads ->', '"*.Cu" "*.Mask"')
