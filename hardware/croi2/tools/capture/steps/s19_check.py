"""Check for step 19: each moved net lands on its new pin and no other pin changes; the three spare pads carry their
new names; every ADC channel and AF number in both maps matches ST's pin data; one interrupt per EXTI line on each
MCU; the reset-state rules (the checker's A24 and A25) fail on step 18's netlist and pass on this one; no new ERC
finding."""
import csv
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture as C
import check_schematic_full as F
import s08_pinmaps as S8
from s19_pin_swaps import MAPS, MOVES, ST, renames

if __name__ == '__main__':
    names = renames()
    C.export('s19')
    ca, p18 = C.load_net('s18')
    expect, changed = {}, {}
    for ref, moves in MOVES.items():
        dest = {b for _, _, b in moves}
        for net, a, b in moves:
            expect[(ref, b)] = names.get(net, net)
            if a not in dest:
                expect[(ref, a)] = 'NC'
    for (r, p), n in p18.items():
        if r.startswith('TP') and n in names:
            expect[(r, p)] = names[n]
            changed[(r, 'value')] = (n, names[n])
    rep = C.check('s18', 's19', expect, expect_added=[], expect_removed=[], expect_changed=changed)
    fixed, new, counts = C.erc_delta('s18', 's19')

    S8.PINDATA = ST                                   # ST's data as kept in the repository
    rows = {ref: list(csv.DictReader(open(MAPS[ref]))) for ref in MAPS}
    af = S8.af_check(rows['U201'], 'STM32H563VITx.xml') + S8.af_check(rows['U401'], 'STM32H563RITx.xml')
    exti = {}
    for ref, rs in rows.items():
        lines = Counter(int(m.group(1)) for r in rs for m in [re.search(r'\bEXTI(\d+)\b', r['notes'])] if m)
        assert all(v == 1 for v in lines.values()), (ref, lines)
        for r in rs:
            m = re.search(r'\bEXTI(\d+)\b', r['notes'])
            assert not m or int(m.group(1)) == int(r['port_or_supply'][2:]), (ref, r['pad'], r['notes'])
        exti[ref] = len(lines)

    before = F.reset_pin_faults(ET.parse(C.OUT / 's18' / 'net.xml').getroot())
    after = F.reset_pin_faults(ET.parse(C.OUT / 's19' / 'net.xml').getroot())
    print('problems:', rep['problems'] or 'none', '| ERC fixed:', fixed, 'new:', new)
    print('A24 / A25 on step 18:', before, '| on step 19:', after)
    assert not rep['problems'] and not new and not fixed
    assert before[0] and before[1] and after == ([], [])
    print('step 19 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;",
          f'{af} AF and ADC rows match ST;', 'EXTI lines', exti, dict(counts))
