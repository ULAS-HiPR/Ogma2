#!/usr/bin/env python3
"""D-27Nov.3 (proposed, 28 Nov 2026): J102 becomes one 6-pin JST GH (BM06B-GHS-TBT), the external port.
Churro's battery feed moves to J101. Pins: 1 EXT_3V3, 2 EXT_SCL, 3 EXT_SDA, 4 GND, 5 EXT_IO1 (POWER_HOLD to Churro),
6 EXT_IO2 (FAULT_N from Churro). Renames the five nets on every sheet. Run once from hardware/croi2."""
import re
from pathlib import Path
HW = Path(__file__).resolve().parents[1]
REN = {'CHURRO_AUX_3V3': 'EXT_3V3', 'CHURRO_SCL_EXT': 'EXT_SCL', 'CHURRO_SDA_EXT': 'EXT_SDA',
       'BURRITO_POWER_HOLD': 'EXT_IO1', 'CHURRO_FAULT_N_EXT': 'EXT_IO2'}
NEW = 'BM06B-GHS-TBT'
PROPS = {'Value': 'BM06B-GHS-TBT', 'Footprint': 'Connector_JST:JST_GH_BM06B-GHS-TBT_1x06-1MP_P1.25mm_Vertical',
         'Datasheet': 'https://www.jst-mfg.com/product/pdf/eng/eGH.pdf', 'Description': 'External port: I2C, 3.3 V, two IO (D-27Nov.3)',
         'MPN': 'BM06B-GHS-TBT(LF)(SN)', 'Manufacturer': 'JST',
         'Library_Check': 'KiCad standard footprint JST_GH_BM06B-GHS-TBT_1x06-1MP; MP pads unconnected; not yet checked against the JST drawing'}
ROWS = {1: 'EXT_3V3', 2: 'EXT_SCL', 3: 'EXT_SDA', 4: 'GND', 5: 'EXT_IO1', 6: 'EXT_IO2'}   # pin -> label at J102 (row y = 405.13 + 2.54 (n-1))


def span(s, i):
    d = 0
    for k in range(i, len(s)):
        d += (s[k] == '(') - (s[k] == ')')
        if d == 0:
            return k + 1


def cut(s, i):
    a = s.rfind('\n', 0, i) + 1
    e = span(s, i)
    return s[:a] + s[e + (s[e:e + 1] == '\n'):]


def libsym(blk, prefix):
    blk = blk.replace('MPT-08-01-01-L-RA-SD', NEW)
    for n in ('7', '8'):
        m = re.search(r'\(pin \w+ \w+\s+\(at [-\d.]+ [-\d.]+ \d+\)(?:(?!\(pin ).)*?\(number "%s"' % n, blk, re.S)
        blk = cut(blk, m.start())
    for k, v in PROPS.items():
        if k == 'Footprint':
            v = v
        blk = re.sub(r'(\(property "%s" ")[^"]*"' % k, lambda m: m.group(1) + v.replace('\\', '') + '"', blk, count=1)
    return blk


def main():
    for f in sorted(HW.glob('*.kicad_sch')):
        s = f.read_text(); o = s
        for a, b in REN.items():
            s = s.replace(f'"{a}"', f'"{b}"')
        if f.name == '01-power.kicad_sch':
            k = s.find('(symbol "Ogma2:MPT-08-01-01-L-RA-SD"')
            s = s[:k] + libsym(s[k:span(s, k)], 'Ogma2:') + s[span(s, k):]
            i = s.find('(lib_id "Ogma2:MPT-08-01-01-L-RA-SD")'); j = s.rfind('\n\t(symbol\n', 0, i) + 2
            blk = s[j:span(s, j)]
            nb = blk.replace('(lib_id "Ogma2:MPT-08-01-01-L-RA-SD")', f'(lib_id "Ogma2:{NEW}")')
            for n in ('7', '8'):
                nb = cut(nb, nb.find(f'(pin "{n}"'))
            for k2, v in PROPS.items():
                nb = re.sub(r'(\(property "%s" ")[^"]*"' % k2, lambda m: m.group(1) + v + '"', nb, count=1)
            s = s[:j] + nb + s[j + len(blk):]
            # labels at the pins: rows 1-6 relabelled, rows 7-8 (and their wires) removed
            for n in range(1, 9):
                y = f'{405.13 + 2.54 * (n - 1):.2f}'
                m = re.search(r'\(global_label "([^"]+)"\s+\(shape \w+\)\s+\(at 67\.31 %s ' % re.escape(y), s)
                if n <= 6:
                    s = s[:m.start(1)] + ROWS[n] + s[m.end(1):]
                else:
                    s = cut(s, m.start())
                    w = re.search(r'\(wire\s+\(pts\s+\(xy [\d.]+ %s\) \(xy [\d.]+ %s\)' % (re.escape(y), re.escape(y)), s)
                    s = cut(s, w.start())
        if s != o:
            f.write_text(s); print('wrote', f.name)
    p = HW / 'libraries' / 'Ogma2.kicad_sym'; s = p.read_text()
    if f'(symbol "{NEW}"' not in s:
        k = s.find('(symbol "MPT-08-01-01-L-RA-SD"')
        s = s[:k] + libsym(s[k:span(s, k)], '') + s[span(s, k):]
        p.write_text(s); print('wrote Ogma2.kicad_sym (MPT symbol replaced by', NEW + ')')


if __name__ == '__main__':
    main()
