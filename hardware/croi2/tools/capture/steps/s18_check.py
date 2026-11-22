"""Check for step 18: the 18 orange loops now carry the surface-mount footprint and Keystone 5194TR's fields; no
part added or removed, no pin moves to another net, no new ERC finding."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture as C
from s18_smt_loops import FIELDS, OLD_FP

if __name__ == '__main__':
    ca, _ = C.load_net('s17')
    loops = sorted((r for r, c in ca.items() if c['fp'] == OLD_FP), key=lambda r: int(r[2:]))
    assert len(loops) == 18, loops
    C.export('s18')
    changed = {(r, 'fp'): (OLD_FP, FIELDS['Footprint']) for r in loops}
    rep = C.check('s17', 's18', {}, expect_added=[], expect_removed=[], expect_changed=changed)
    fixed, new, counts = C.erc_delta('s17', 's18')
    root = ET.parse(C.OUT / 's18' / 'net.xml').getroot()
    bad = []
    for comp in root.findall('components/comp'):
        if comp.get('ref') in loops:
            f = {x.get('name'): x.text for x in comp.findall('fields/field')}
            for k in ('MPN', 'Manufacturer', 'LCSC', 'Datasheet'):
                if f.get(k) != FIELDS[k]:
                    bad.append((comp.get('ref'), k, f.get(k)))
    left = [c.get('ref') for c in root.findall('components/comp') if c.findtext('footprint') == OLD_FP]
    print('problems:', rep['problems'] or 'none', '| field mismatches:', bad or 'none', '| old footprint left:', left or 'none',
          '| ERC fixed:', fixed, 'new:', new)
    assert not rep['problems'] and not bad and not left and not new and not fixed
    print('step 18 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;", len(loops), 'loops;', dict(counts))
