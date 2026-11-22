"""Check for step 17: seven parts added, each pin on its intended net; nothing else changes; no new ERC finding."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture as C
from s17_rf_guards import CAPS, C_VALUE, C_FP, D_FIELDS

if __name__ == '__main__':
    C.export('s17')
    expect = {('D4601', '1'): 'LORA_RF_SUBG', ('D4601', '2'): 'GND'}
    for ref, net, _ in CAPS:
        expect[(ref, '1')], expect[(ref, '2')] = None, None          # filled below: which pin is which is the symbol's
    _, pb = C.load_net('s17')
    for ref, net, _ in CAPS:
        got = {pb.get((ref, '1')), pb.get((ref, '2'))}
        assert got == {net, 'GND'}, (ref, got)
        expect[(ref, '1')], expect[(ref, '2')] = pb[(ref, '1')], pb[(ref, '2')]
    added = ['D4601'] + [r for r, _, _ in CAPS]
    rep = C.check('s16', 's17', expect, expect_added=added, expect_removed=[], expect_changed={})
    fixed, new, counts = C.erc_delta('s16', 's17')
    root = ET.parse(C.OUT / 's17' / 'net.xml').getroot()
    comp = {c.get('ref'): c for c in root.findall('components/comp')}
    bad = []
    d = comp['D4601']
    f = {x.get('name'): x.text for x in d.findall('fields/field')}
    if d.findtext('footprint') != 'Diode_SMD:D_SOD-882' or f.get('MPN') != D_FIELDS['MPN'] or f.get('LCSC') != D_FIELDS['LCSC']:
        bad.append('D4601 fields')
    for ref, _, _ in CAPS:
        if comp[ref].findtext('value') != C_VALUE or comp[ref].findtext('footprint') != C_FP:
            bad.append(ref)
    print('problems:', rep['problems'] or 'none', '| field mismatches:', bad or 'none', '| ERC fixed:', fixed, 'new:', new)
    assert not rep['problems'] and not new and not fixed and not bad
    print('step 17 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;", dict(counts))
