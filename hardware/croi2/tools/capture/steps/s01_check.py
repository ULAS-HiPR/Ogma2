"""Check for step 1: the intended pin delta, exactly, and the ERC findings it closes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture as C

AUTO = 'Net-(D202-K)'                       # D202 cathode to R204, no label needed
PAD = '/02a-flight-support/TP_STROBE_PAD'   # local label: KiCad prefixes the sheet path
EXPECT = {('C207', '1'): 'FLIGHT_VBAT',
          ('D201', '1'): 'FLIGHT_VBAT', ('D201', '2'): 'FLIGHT_3V3',
          ('C219', '1'): 'FLIGHT_VBAT', ('C219', '2'): 'GND',
          ('R202', '1'): 'FLIGHT_3V3', ('R202', '2'): 'RESET_MEMORY',
          ('C220', '1'): 'RESET_MEMORY', ('C220', '2'): 'GND',
          ('D202', '2'): 'RESET_MEMORY', ('D202', '1'): AUTO,
          ('R204', '1'): AUTO, ('R204', '2'): 'FLIGHT_MR_N',
          ('TP205', '1'): 'RESET_MEMORY',
          ('R203', '1'): 'TP_STROBE', ('R203', '2'): PAD,
          ('R205', '1'): PAD, ('R205', '2'): 'GND',
          ('TP201', '1'): PAD,
          ('TP202', '1'): 'TP_PC6', ('TP203', '1'): 'TP_PC7', ('TP204', '1'): 'TP_PD10'}
ADDED = ['C219', 'C220', 'D201', 'D202', 'R202', 'R203', 'R204', 'R205', 'TP201', 'TP202', 'TP203', 'TP204', 'TP205']
CLOSES = {"Global Label 'FLIGHT_VBAT'", "Global Label 'RESET_MEMORY'", "Global Label 'TP_PC6'", "Global Label 'TP_PC7'",
          "Global Label 'TP_PD10'", "Global Label 'TP_STROBE'", 'Symbol U201 Pin 6 [VBAT, Power input, Line]'}

if __name__ == '__main__':
    C.export('s01')
    rep = C.check('s00', 's01', EXPECT, expect_added=ADDED, expect_changed={})
    fixed, new, counts = C.erc_delta('s00', 's01')
    assert not rep['problems'], rep['problems']
    assert {x[3] for x in fixed} == CLOSES and not new, (fixed, new)
    print('step 1 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;",
          f'ERC closed {len(fixed)}, added 0;', dict(counts))
