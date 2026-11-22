"""Check for step 16: only the swapped parts' footprints change (0603 -> 0402), each with its pinned MPN and LCSC;
no pin change, no new ERC finding; every part that stays keeps its footprint; the swapped set obeys the rules."""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture as C
import s16_0402 as S

if __name__ == '__main__':
    rows = S.classify(str(C.OUT / 's15' / 'net.xml'))
    sw = {r['ref']: r for r in rows if r['swap']}
    C.export('s16')
    ca, _ = C.load_net('s15')
    changed = {(r, 'fp'): (ca[r]['fp'], S.FP[r[0]]) for r in sw}
    rep = C.check('s15', 's16', {}, expect_added=[], expect_removed=[], expect_changed=changed)
    fixed, new, counts = C.erc_delta('s15', 's16')
    root = ET.parse(C.OUT / 's16' / 'net.xml').getroot()
    got = {c.get('ref'): {f.get('name'): f.text for f in c.findall('fields/field')} for c in root.findall('components/comp')}
    bad = [(r, got[r].get('MPN'), got[r].get('LCSC')) for r, x in sw.items()
           if got[r].get('MPN') != x['part'][1] or got[r].get('LCSC') != x['part'][0]]
    # the rules, re-asserted on the result
    rule = []
    for r, x in sw.items():
        if x['sheet'].startswith('06') or '0.1%' in x['value'] or x['value'].startswith('0R'):
            rule.append((r, 'kept class swapped'))
        if r[0] == 'C':
            farads, _, volts, _ = S.parse_c(x['value'])
            v = float(re.search(r'(?:^|\s)(\d+(?:\.\d+)?)V(?:\s|$)', x['part'][4]).group(1))
            if farads > 1e-6 or x['v'] > 5.0 or v < 2 * x['v'] or (volts and v < volts):
                rule.append((r, 'capacitor rule'))
        elif x.get('p_mw', 0) > 30:
            rule.append((r, 'over 30 mW'))
    print('problems:', rep['problems'] or 'none', '| field mismatches:', bad or 'none', '| rule breaches:', rule or 'none')
    print('ERC fixed:', fixed, 'new:', new)
    assert not rep['problems'] and not new and not fixed and not bad and not rule
    print(f"step 16 ok: {len(sw)} parts to 0402;", rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;", dict(counts))
