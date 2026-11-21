"""Check for step 3: the intended pin and field delta, exactly, and the ERC findings it closes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture as C

GONE = {'U1203': 6, 'C1203': 2, 'U4402': 5}
EXPECT = {('U1601', '3'): 'SERVICE_POWER_EN', ('R1602', '1'): 'SERVICE_POWER_EN',
          ('R1210', '1'): '4V_PRE', ('R1210', '2'): 'CORE_INPUT_EN'}
EXPECT.update({(r, str(p)): None for r, n in GONE.items() for p in range(1, n + 1)})
CHANGED = {('R1701', 'value'): ('31.2k 0.1%', '31.9k 0.1%'), ('R1801', 'value'): ('31.2k 0.1%', '31.9k 0.1%'),
           ('R1901', 'value'): ('31.2k 0.1%', '31.9k 0.1%'), ('R1504', 'value'): ('36.5k 1%', '66.5k 1%'),
           ('R1604', 'value'): ('56.2k 1%', '49.9k 1%'),
           ('C1403', 'value'): ('1000u 10V - MPN OPEN', '1000u 6.3V polymer'),
           ('C1403', 'fp'): ('Capacitor_SMD:CP_Elec_10x10.5', 'Capacitor_SMD:CP_Elec_8x10.5')}
CLOSES = {"Global Label 'SERVICE_POWER_EN'"}

if __name__ == '__main__':
    C.export('s03')
    rep = C.check('s02', 's03', EXPECT, expect_added=['R1210'], expect_removed=list(GONE), expect_changed=CHANGED)
    fixed, new, counts = C.erc_delta('s02', 's03')
    print('problems:', rep['problems'] or 'none')
    print('fixed:', fixed); print('new:', new)
    assert not rep['problems'] and {x[3] for x in fixed} == CLOSES and not new
    print('step 3 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;",
          f'ERC closed {len(fixed)}, added 0;', dict(counts))
