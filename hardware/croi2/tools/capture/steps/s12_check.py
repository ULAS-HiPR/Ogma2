"""Check for step 12: 25 test points added, each on its named net; 13 resized (footprint, MPN, LCSC);
36 cut with their wiring; no other pin or footprint change; no new ERC finding."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture as C
from s12_test_points import NEW, RETIER, REMOVE

if __name__ == '__main__':
    C.export('s12')
    ca, _ = C.load_net('s11')
    expect = {**{(ref, '1'): net for ref, net, _ in NEW}, **{(ref, '1'): None for ref in REMOVE}}
    changed = {(r, 'fp'): (ca[r]['fp'], t['Footprint']) for r, t in RETIER.items() if ca[r]['fp'] != t['Footprint']}
    rep = C.check('s11', 's12', expect, expect_added=sorted(r for r, _, _ in NEW), expect_removed=sorted(REMOVE), expect_changed=changed)
    fixed, new, counts = C.erc_delta('s11', 's12')
    root = ET.parse(C.OUT / 's12' / 'net.xml').getroot()
    got = {c.get('ref'): (c.findtext('footprint'), {f.get('name'): f.text for f in c.findall('fields/field')}) for c in root.findall('components/comp')}
    want = {**{r: t for r, _, t in NEW}, **RETIER}
    bad = [(r, got[r][0], got[r][1].get('MPN'), got[r][1].get('LCSC')) for r, t in want.items()
           if got[r][0] != t['Footprint'] or got[r][1].get('MPN') != t.get('MPN') or got[r][1].get('LCSC') != t.get('LCSC')]
    print('problems:', rep['problems'] or 'none', '| field mismatches:', bad or 'none')
    print('footprint changes:', len(changed), '| ERC fixed:', fixed, 'new:', new)
    assert not rep['problems'] and not new and not bad
    print('step 12 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;", dict(counts))
