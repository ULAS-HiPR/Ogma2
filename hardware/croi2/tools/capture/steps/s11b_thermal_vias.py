"""Step 11b: U101's footprint (TPS26630RGER) thermal vias move to 0.3 mm drill, 22 Nov 2026.

KiCad's generator put nine 0.2 mm vias (0.5 mm pads) in the exposed pad. JLC charges for any via under
0.3 mm (order form, 22 Nov) and D-22Nov.2 fixes 0.3 mm, plugged. Same positions; pads grow to 0.6 mm so
the ring stays 0.15 mm. Library edit only.
"""
from pathlib import Path
FP = Path(__file__).resolve().parents[3] / 'libraries/Ogma2.pretty/TPS26630RGER.kicad_mod'
s = FP.read_text()
old = '(size 0.5 0.5)\n    (drill 0.2)'
n = s.count(old)
if n:
    assert n == 9, n
    FP.write_text(s.replace(old, '(size 0.6 0.6)\n    (drill 0.3)'))
print('step 11b: U101 thermal vias at 0.3 mm:', '(size 0.6 0.6)\n    (drill 0.3)' in FP.read_text())
