"""Check for step 9: every pin change listed, value / footprint changes listed, no new ERC finding."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture as C

REMOVED = ['R3106', 'R3206', 'R3306', 'R3407', 'R3408', 'R3507', 'R3508', 'R1206', 'R4404', 'R4304', 'R9005']
X6S = ('47u 16V X7R', '47u 16V X6S')

if __name__ == '__main__':
    C.export('s09')
    ca, pa = C.load_net('s08a')
    cb, pb = C.load_net('s09')
    state = {(r, p): None for (r, p) in pa if r in REMOVED}
    state.update({('U401', '15'): 'NC', ('U4303', '5'): 'NC', ('U4303', '10'): 'GND'})
    expect = {k: v for k, v in state.items() if pa.get(k) != v}
    changed = {('J6101', 'value'): ('Recovery arm switch (part open)', '39281023'),
               ('J6101', 'fp'): ('', 'Connector_Molex:Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical'),
               ('J6102', 'value'): ('Staging arm switch (part open)', 'B2P-VH(LF)(SN)'),
               ('J6102', 'fp'): ('', 'Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical'),
               ('U3104', 'value'): ('LSM6DSV16XTR', 'LSM6DSV32XTR'),
               ('C4613', 'value'): ('100u 10V X7R', '100u 16V X5R'),
               ('C4504', 'value'): ('10u 16V X7R', '10u 16V X7R'),
               ('C4504', 'fp'): ('Capacitor_SMD:C_0603_1608Metric', 'Capacitor_SMD:C_0805_2012Metric'),
               ('R1103', 'value'): ('74.9k 0.1%', '75k 0.1%'),
               ('BZ9001', 'value'): ('CPT-9019S-SMT-TR', 'SMT-1028-T-2-R'),
               ('BZ9001', 'fp'): ('Ogma2:CPT-9019S-SMT-TR', 'Buzzer_Beeper:MagneticBuzzer_PUI_SMT-1028-T-2-R'),
               ('Q9001', 'value'): ('2N7002', 'AO3400A')}
    del changed[('C4504', 'value')]
    for r in ('C1305', 'C1306', 'C1705', 'C1706', 'C1805', 'C1806', 'C1905', 'C1906'):
        changed[(r, 'value')] = X6S
    for r in ('R1701', 'R1801', 'R1901'):
        changed[(r, 'value')] = ('31.9k 0.1%', '32k 0.1%')
    rep = C.check('s08a', 's09', expect, expect_added=[], expect_removed=sorted(REMOVED), expect_changed=changed)
    fixed, new, counts = C.erc_delta('s08a', 's09')
    print('problems:', rep['problems'] or 'none')
    print('fixed:', fixed, 'new:', new)
    assert not rep['problems'] and not new and not fixed
    assert not [k for k, v in pb.items() if v in ('USB_CONFIG_OK', 'CC_USB_CONFIG_OK')]
    print('step 9 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;", dict(counts))
