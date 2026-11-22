"""Check for step 10: only D4501's value and footprint change; no pin change, no new ERC finding."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture as C

if __name__ == '__main__':
    C.export('s10')
    changed = {('D4501', 'value'): ('TPD1E0B04DPYR', 'PESD5V0F1BL,315'),
               ('D4501', 'fp'): ('Ogma2_GNSS:TPD1E0B04DPYR', 'Diode_SMD:D_SOD-882')}
    rep = C.check('s09', 's10', {}, expect_added=[], expect_removed=[], expect_changed=changed)
    fixed, new, counts = C.erc_delta('s09', 's10')
    print('problems:', rep['problems'] or 'none')
    print('fixed:', fixed, 'new:', new)
    assert not rep['problems'] and not new and not fixed
    print('step 10 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;", dict(counts))
