"""Check for step 20: the six nets land on their new U201 pins and no other pin changes; the pin map matches ST's pin
data; one interrupt per EXTI line; the reset-state rules (A24, A25) still pass; A26's fire-pin rules hold on the new
pins, with channel 3's low side on U201's top row (the side facing the output stage) and no fire pin there; no new ERC
finding. The full checker (A26 with D-22Nov.25's whole neighbour rule) runs on the exported netlist after this."""
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
from s19_pin_swaps import ST
from s20_pin_swaps import MAP, MOVES

if __name__ == '__main__':
    C.export('s20')
    expect = {('U201', b): net for net, _, b in MOVES}
    rep = C.check('s19', 's20', expect, expect_added=[], expect_removed=[], expect_changed={})
    fixed, new, counts = C.erc_delta('s19', 's20')

    S8.PINDATA = ST
    rows = list(csv.DictReader(open(MAP)))
    af = S8.af_check(rows, 'STM32H563VITx.xml')
    lines = Counter(int(m.group(1)) for r in rows for m in [re.search(r'\bEXTI(\d+)\b', r['notes'])] if m)
    assert all(v == 1 for v in lines.values()), lines

    root = ET.parse(C.OUT / 's20' / 'net.xml').getroot()
    a24, a25 = F.reset_pin_faults(root)
    pad_of = {n.get('name'): x.get('pin') for n in root.iter('net') for x in n.iter('node') if x.get('ref') == 'U201'}
    func = {(x.get('ref'), x.get('pin')): x.get('pinfunction') or '' for x in root.iter('node')}
    fire = {k: int(pad_of[f'PYRO{k}_FIRE']) for k in (1, 2, 3)}
    low = {k: int(pad_of[f'PYRO{k}_LS_SELECT']) for k in (1, 2, 3)}
    port = lambda p: re.match(r'P([A-K])\d+', func[('U201', str(p))]).group(1)
    side = lambda p: (p - 1) // 25                      # 0 west, 1 bottom, 2 east, 3 top (north, the output stage)
    beside = [(a, b) for a in [*fire.values(), *low.values()] for b in [*fire.values(), *low.values()]
              if abs(a - b) == 1 and side(a) == side(b)]
    print('problems:', rep['problems'] or 'none', '| ERC fixed:', fixed, 'new:', new)
    print('A24 / A25:', a24, a25, '| fire pads', fire, 'low-side pads', low, '| beside:', beside)
    assert not rep['problems'] and not new and not fixed
    assert a24 == [] and a25 == []
    assert all(port(p) == 'E' for p in fire.values()) and len({port(p) for p in low.values()}) == 3 \
        and 'E' not in {port(p) for p in low.values()} and not beside
    assert [k for k, p in fire.items() if side(p) == 3] == [], fire
    assert [k for k, p in low.items() if side(p) == 3] == [3], low
    print('step 20 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;",
          f'{af} AF and ADC rows match ST;', 'EXTI lines', len(lines), dict(counts))
