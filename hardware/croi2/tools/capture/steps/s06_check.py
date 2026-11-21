"""Check for step 6: removals derived from the step-5 netlist (every pin of a removed part goes),
renames applied by rule to the pins that stay, the new parts listed pin by pin; ERC closures."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture as C

SHEETS_GONE = {'/06d-servo-power/'}
REMOVED = {'U6002', 'U6003', 'U6004', 'U6005', 'C6002', 'C6003', 'C6004', 'C6005', 'R6002', 'R6003', 'R6004',
           'U6101', 'U6102', 'U6104', 'C6101', 'C6102', 'C6104',
           'J6602', 'R6601', 'R6602', 'R6603', 'R6604', 'R6605', 'R6606', 'R6607',
           'R8010', 'R8011', 'R8012', 'C8004'}
for rr in ('63', '64'):
    REMOVED |= {f'U{rr}01', f'U{rr}02', f'U{rr}03', f'R{rr}01', f'R{rr}11', f'R{rr}12', f'R{rr}13', f'C{rr}01', f'C{rr}02', f'C{rr}03'}
REMOVED |= {'U6501', 'U6503', 'R6511', 'R6512', 'R6513', 'C6501', 'C6503'}
RENAME = {'STAGE_NEW_FLIGHT_ALLOWED': 'STAGE_ARM_INVALID', 'STAGING_ARM_VALID': 'STAGE_ARM_INVALID',
          'PYRO1_HS_ENABLE': 'PYRO1_FIRE', 'PYRO2_HS_ENABLE': 'PYRO2_FIRE', 'PYRO3_HS_REQUEST': 'PYRO3_FIRE',
          'PYRO1_LS_ENABLE': 'PYRO1_LS_SELECT', 'PYRO2_LS_ENABLE': 'PYRO2_LS_SELECT', 'PYRO3_LS_ENABLE': 'PYRO3_LS_SELECT'}
CLOSES = {"Global Label 'PYRO1_FIRE'", "Global Label 'PYRO2_FIRE'", "Global Label 'PYRO3_FIRE'",
          "Global Label 'SERVO_ARMED_VBAT'", "Global Label 'SERVO1_PWM'", "Global Label 'SERVO2_PWM'",
          "Global Label 'SERVO3_PWM'", "Global Label 'ADC_SERVO_RAIL'"}

if __name__ == '__main__':
    C.export('s06')
    ca, pa = C.load_net('s05')
    cb, pb = C.load_net('s06')
    removed = REMOVED | {r for r, c in ca.items() if any(c['sheet'].startswith(s) for s in SHEETS_GONE)}
    assert {r for r in removed if r.startswith(('U68', 'C68', 'R68'))} == \
        {'U6801', 'U6802', 'U6803', 'U6804', 'C6801', 'C6802', 'C6803', 'C6804', 'C6805', 'C6806', 'R6801', 'R6802', 'R6803', 'R6804'}
    state = {}
    for (ref, pin), net in pa.items():
        if ref in removed:
            state[(ref, pin)] = None
        elif net in RENAME:
            state[(ref, pin)] = RENAME[net]
    q = pb[('U6001', '3')]                                       # Q-bar -> R6005: one auto-named two-pin net
    assert q.startswith('Net-') and {k for k, v in pb.items() if v == q} == {('U6001', '3'), ('R6005', '1')}, q
    state.update({('U6001', '3'): q, ('R6005', '1'): q, ('R6005', '2'): 'STAGE_INHIBIT_LATCHED',
                  ('F6101', '1'): 'ENERGY_TAP', ('F6101', '2'): '/06a-arm-boundary/RECOVERY_ARM_FEED',
                  ('J6101', '1'): '/06a-arm-boundary/RECOVERY_ARM_FEED', ('J6101', '2'): 'RECOVERY_ARMED_VBAT',
                  ('F6102', '1'): 'ENERGY_TAP', ('F6102', '2'): '/06a-arm-boundary/STAGING_ARM_FEED',
                  ('J6102', '1'): '/06a-arm-boundary/STAGING_ARM_FEED', ('J6102', '2'): 'STAGING_ARMED_VBAT',
                  ('U6502', '1'): 'PYRO3_FIRE', ('U6502', '2'): 'STAGE_ELIGIBLE', ('U6502', '3'): 'GND',
                  ('U6502', '4'): 'PYRO3_HS_ENABLE', ('U6502', '5'): 'FLIGHT_3V3', ('U6502', '6'): None,
                  ('U8001', '11'): 'NC', ('U8001', '12'): 'NC'})
    expect = {k: v for k, v in state.items() if pa.get(k) != v}
    changed = {('U6502', 'value'): ('SN74LVC1G97DBVR', 'SN74LVC1G08DBVR'),
               ('U6502', 'fp'): ('Ogma2:SN74LVC1G97DBVR', 'Package_TO_SOT_SMD:SOT-23-5')}
    for r in ('R6314', 'R6414', 'R6514'):
        changed[(r, 'value')] = ('TBD load current limit', '1.24k 1%')
        changed[(r, 'dnp')] = (True, False)
    for ch in (1, 2, 3):
        for k, old in ((1, 'TBD no-fire R1'), (2, 'TBD no-fire R2'), (3, 'TBD return R1'), (4, 'TBD return R2')):
            changed[(f'R69{ch}{k}', 'value')] = (old, '3.9k 1%')
            changed[(f'R69{ch}{k}', 'dnp')] = (True, False)
    rep = C.check('s05', 's06', expect, expect_added=['R6005', 'F6101', 'F6102', 'J6101', 'J6102'],
                  expect_removed=sorted(removed), expect_changed=changed)
    fixed, new, counts = C.erc_delta('s05', 's06')
    print('problems:', rep['problems'] or 'none')
    print('fixed:', *fixed, sep='\n  ')
    print('new:', new)
    closed_labels = {x[3] for x in fixed if x[2] == 'global_label_dangling'}
    others = [x for x in fixed if x[2] != 'global_label_dangling']
    assert not rep['problems'] and closed_labels == CLOSES and len(others) == 7 and not new, others
    print('step 6 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;",
          f'ERC closed {len(fixed)}, added 0;', dict(counts))
