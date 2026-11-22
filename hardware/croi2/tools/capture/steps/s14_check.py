"""Check for step 14: only J103's value and footprint change (and its MPN, LCSC fields); no pin change, no new ERC finding."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture as C
from s14_j103 import FIELDS

if __name__ == '__main__':
    C.export('s14')
    ca, _ = C.load_net('s13')
    changed = {('J103', 'value'): (ca['J103']['value'], FIELDS['Value']), ('J103', 'fp'): (ca['J103']['fp'], FIELDS['Footprint'])}
    rep = C.check('s13', 's14', {}, expect_added=[], expect_removed=[], expect_changed=changed)
    fixed, new, counts = C.erc_delta('s13', 's14')
    root = ET.parse(C.OUT / 's14' / 'net.xml').getroot()
    j = next(c for c in root.findall('components/comp') if c.get('ref') == 'J103')
    f = {x.get('name'): x.text for x in j.findall('fields/field')}
    bad = {k: f.get(k) for k in ('MPN', 'LCSC', 'Manufacturer') if f.get(k) != FIELDS[k]}
    print('problems:', rep['problems'] or 'none', '| field mismatches:', bad or 'none')
    print('ERC fixed:', fixed, 'new:', new)
    assert not rep['problems'] and not new and not fixed and not bad
    print('step 14 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;", dict(counts))
