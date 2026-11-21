"""Check for step 2: the intended pin delta, exactly, and the ERC findings it closes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture as C

RC = '/01-power/POWER_HOLD_RC'
EXPECT = {('Q101', '5'): 'ENERGY_TAP', ('R7104', '1'): 'ENERGY_TAP', ('U101', '1'): 'ENERGY_TAP', ('U101', '2'): 'ENERGY_TAP',
          ('U101', '11'): 'GND', ('J102', '8'): 'CROI_POWER_HOLD',
          ('R1014', '1'): 'FC_POWER_HOLD', ('R1014', '2'): RC, ('R1015', '1'): 'FC_POWER_HOLD', ('R1015', '2'): 'GND',
          ('C1007', '1'): RC, ('C1007', '2'): 'GND',
          ('D1003', '2'): RC, ('D1003', '1'): 'BAT_SHDN_N', ('D1004', '2'): RC, ('D1004', '1'): 'CROI_POWER_HOLD',
          ('C1004', '1'): 'ENERGY_TAP', ('C1004', '2'): 'GND', ('C1005', '1'): 'ENERGY_TAP', ('C1005', '2'): 'GND'}
ADDED = ['C1004', 'C1005', 'C1007', 'D1003', 'D1004', 'R1014', 'R1015']
CLOSES = {"Global Label 'FC_POWER_HOLD'"}

if __name__ == '__main__':
    C.export('s02')
    rep = C.check('s01', 's02', EXPECT, expect_added=ADDED, expect_changed={})
    fixed, new, counts = C.erc_delta('s01', 's02')
    print('problems:', rep['problems'] or 'none')
    print('fixed:', fixed); print('new:', new)
    assert not rep['problems'] and {x[3] for x in fixed} == CLOSES and not new
    print('step 2 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;",
          f'ERC closed {len(fixed)}, added 0;', dict(counts))
