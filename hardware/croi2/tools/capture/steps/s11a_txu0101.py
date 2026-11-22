"""Step 11a: U4302's footprint (TXU0101DCKR, SC-70-6) gets TI's DCK0006A land pattern, 22 Nov 2026.

The local pattern had 0.65 x 0.40 mm pads centred at +-0.95 mm, so its lands ended at +-1.275 mm: barely past
the leads' tips (2.4 mm tip to tip at most). TI's land pattern example for DCK0006A (drawing 4214835/D,
11/2024, in the TXU0101 data sheet) is 6X (0.9) x 6X (0.4) at 4X (0.65) pitch, rows (2.2) apart: pads centred at
+-1.1 mm, ending at +-1.55 mm. Pin numbering unchanged. The courtyard grows to +-1.8 x +-1.35 mm. Library
edit only: the netlist doesn't change.
"""
import re
from pathlib import Path

FP = Path(__file__).resolve().parents[3] / 'libraries/Ogma2.pretty/TXU0101DCKR.kicad_mod'
s = FP.read_text()
if '(size 0.9 0.4)' not in s:
    for x in ('-0.95', '0.95'):
        nx = '-1.1' if x.startswith('-') else '1.1'
        s, n = re.subn(rf'\(at {re.escape(x)} (-?0\.65|0)\)\n(\s*)\(size 0\.65 0\.4\)', rf'(at {nx} \1)\n\2(size 0.9 0.4)', s)
        assert n == 3, (x, n)
    for old, new in (('(start -1.6 -1.4)\n    (end -1.6 1.4)', '(start -1.8 -1.4)\n    (end -1.8 1.4)'),
                     ('(start -1.6 -1.4)\n    (end 1.6 -1.4)', '(start -1.8 -1.4)\n    (end 1.8 -1.4)'),
                     ('(start -1.6 1.4)\n    (end 1.6 1.4)', '(start -1.8 1.4)\n    (end 1.8 1.4)'),
                     ('(start 1.6 1.4)\n    (end 1.6 -1.4)', '(start 1.8 1.4)\n    (end 1.8 -1.4)')):
        assert s.count(old) == 1, old
        s = s.replace(old, new)
    s = s.replace('(descr "SOT-363, SC-70-6, SC-88', '(descr "TI DCK0006A land pattern (4214835/D): 0.9 x 0.4 mm pads, rows 2.2 mm apart, 0.65 mm pitch; SOT-363, SC-70-6, SC-88', 1)
    FP.write_text(s)
print('step 11a: TXU0101DCKR footprint ->', 'TI DCK0006A lands' if '(size 0.9 0.4)' in FP.read_text() else 'unchanged')
