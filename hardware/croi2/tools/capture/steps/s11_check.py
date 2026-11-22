"""Check for step 11: only C1403's footprint changes; no pin change, no new ERC finding."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture as C

if __name__ == '__main__':
    C.export('s11')
    changed = {('C1403', 'fp'): ('Capacitor_SMD:CP_Elec_8x10.5', 'Capacitor_SMD:CP_Elec_8x10')}
    rep = C.check('s10', 's11', {}, expect_added=[], expect_removed=[], expect_changed=changed)
    fixed, new, counts = C.erc_delta('s10', 's11')
    print('problems:', rep['problems'] or 'none')
    print('fixed:', fixed, 'new:', new)
    assert not rep['problems'] and not new and not fixed
    print('step 11 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;", dict(counts))
