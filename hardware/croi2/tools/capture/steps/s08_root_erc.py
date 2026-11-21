"""Step 8a, close-out: the root index and the ERC exclusions.

Root: 06d's page is gone (step 6), so the pages after it move up one place in the grid and
renumber 39-44; captions follow the captured design. ERC: the three baseline pin-to-pin warnings
(strap pins tied to GND, a net with a PWR_FLAG) are recorded as exclusions with their reason, in
KiCad 9's serialised form (type|x|y|main|aux|sheet|main sheet|aux sheet, positions in 1e-4 mm).
"""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
COLS = (17.78, 129.54, 241.3, 353.06, 464.82)
ROW0, ROW = 62.23, 35.56

CAPTIONS = {   # page: caption, for pages whose caption changes
    14: 'COMMS MCU / STM32H563RIT6 / LQFP64',
    32: 'Staging reset latch',
    33: 'Arm feeds / arm sense',
    37: 'Output harness / J6601',
    41: 'Vehicle CAN / two buses, Gecko-SL',
}
SUMMARY = ('44 pages. New: external MAX-M10S antenna feed and external master enable. Energetic links remain DNP. No fabrication / flight release.',
           '44 pages, as captured 21 Nov 2026 (capture specification, D-21Nov.9): servos removed, magnetometer and CAN bus 2 added,\n'
           'fused arm feeds, comms MCU in LQFP64. Energy links R6310 / R6410 / R6510 remain DNP. No fabrication / flight release.')

ROOT_ID = 'a9e6a58d-37d4-4c26-836a-c708a8c9d69e'
EXCLUSIONS = [  # (main pin uuid, x, y, sheet uuid, reason)
    ('251173d1-477c-575d-9a5b-e09d2c0af87e', 292.1, 295.91, '12f6be2c-cd81-5c18-a6c2-c9f149762673',
     'U3104 pin 2 (LSM6DSV16X aux pin, unused) strapped to GND as the datasheet allows; GND carries a PWR_FLAG. Correct as drawn (baseline)'),
    ('f4743fb4-d2f8-520d-8f93-80fcb42aa1f6', 292.1, 295.91, '12f6be2c-cd81-5c18-a6c2-c9f149762673',
     'U3104 pin 3 (LSM6DSV16X aux pin, unused) strapped to GND as the datasheet allows; GND carries a PWR_FLAG. Correct as drawn (baseline)'),
    ('9f69283e-cf1e-59f9-a6d6-460f2304b6db', 294.64, 290.83, '92bc9dab-010d-59bf-bfc3-b2b5d70f928e',
     'U3403 pin 5 (BMP390 SDO, I2C address select) tied to GND for address 0x76; GND carries a PWR_FLAG. Correct as drawn (baseline)'),
]
FLAG = ('725c78f9-eaff-5a43-b2c6-e1aecaedd15e', '1ed0d183-0300-4b05-9ff2-c54b7708c528')   # #FLG001 pin on 01-power


def slot(page):
    k = page - 2
    return COLS[k % 5], round(ROW0 + ROW * (k // 5), 4)


def shift(node, dx, dy):
    for a in K.walk(node, 'at'):                                  # the sheet, its fields and any pins
        a[1], a[2] = K.num(float(a[1]) + dx), K.num(float(a[2]) + dy)


def root():
    path = BOARD / 'Croi2.kicad_sch'
    t = K.load(path)
    caps = {}
    for n in K.children(t, 'text'):
        m = re.match(r'P(\d+)  ', n[1])
        if m:
            caps[int(m.group(1))] = n
    for s in K.children(t, 'sheet'):
        page = [p for p in K.walk(s, 'page')]
        assert len(page) == 1
        old = int(page[0][1])
        new = old - 1 if old >= 40 else old
        assert old != 39
        x0, y0 = K.xy(s)
        assert (x0, y0) == slot(old), (old, x0, y0)
        x1, y1 = slot(new)
        if new != old:
            shift(s, x1 - x0, y1 - y0)
            page[0][1] = str(new)
            cap = caps.pop(old)
            title = cap[1].split('  ', 1)[1]
            K.first(cap, 'at')[1:3] = [K.num(x1 + 2.54), K.num(y1 + 4.445)]
            cap[1] = f'P{new}  {CAPTIONS.get(new, title)}'
        elif old in CAPTIONS:
            caps[old][1] = f'P{old}  {CAPTIONS[old]}'
    hits = [n for n in K.children(t, 'text') if n[1] == SUMMARY[0]]
    assert len(hits) == 1
    hits[0][1] = SUMMARY[1]
    K.first(K.first(t, 'title_block'), 'date')[1] = '2026-11-21'
    K.save(t, path)


def exclusions():
    path = BOARD / 'Croi2.kicad_pro'
    text = path.read_text()
    p = json.loads(text)
    assert json.dumps(p, indent=2, ensure_ascii=False) + '\n' == text           # round-trips exactly
    flag_pin, flag_sheet = FLAG
    rows = []
    for pin, x, y, sheet, why in EXCLUSIONS:
        sp = f'/{ROOT_ID}/{sheet}'
        key = f'pin_to_pin|{round(x * 10000)}|{round(y * 10000)}|{pin}|{flag_pin}|{sp}|{sp}|/{ROOT_ID}/{flag_sheet}'
        rows.append([key, why])
    p['erc']['erc_exclusions'] = rows
    path.write_text(json.dumps(p, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    root()
    exclusions()
    print('root and exclusions written')
