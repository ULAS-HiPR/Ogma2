"""JLC full pass for generic passives: match each resistor / capacitor value line of the exported BOM
to a stocked JLC part (jlcparts data, in-stock only), Basic first, then by stock.

A resistor matches on value, package, and tolerance (the stated one exactly, or 1% where none is
stated), plus power where one is stated. A capacitor matches on value and package, with a rated
voltage at least the stated one and the stated dielectric (X7R also covers X5R; NP0 equals C0G).
Usage: python3 jlc_passives.py <netlist.xml> <jlc.sqlite>  -> markdown table on stdout
"""
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

UNITS = {'p': 'pF', 'n': 'nF', 'u': 'uF'}
DIELECTRIC_OK = {'X5R': ('X5R', 'X7R'), 'X7R': ('X7R',), 'C0G': ('C0G', 'NP0')}


def bom_lines(netlist):
    lines = defaultdict(list)
    for c in ET.parse(netlist).getroot().findall('components/comp'):
        fp = c.findtext('footprint') or ''
        if c.findtext("fields/field[@name='MPN']") or not re.match(r'(Resistor_SMD|Capacitor_SMD):', fp):
            continue
        dnp = any(p.get('name') == 'dnp' for p in c.findall('property'))
        lines[(fp.split(':')[0][0], c.findtext('value'), fp.split(':')[1].split('_')[1])].append((c.get('ref'), dnp))
    return lines


def resistor(con, value, package):
    tok = value.split()
    m = re.fullmatch(r'(\d+(?:\.\d+)?)([RkMm]?)', tok[0])
    if not m:
        return None, 'value not parsed'
    num, mult = m.groups()
    jlc = f"{num}{'' if mult in ('R', '') else mult}Ω"
    tol = next((t for t in tok[1:] if t.endswith('%')), '1%')
    power = next((t for t in tok[1:] if t.endswith('W')), None)
    rows = con.execute("select lcsc, mfr, class, stock, descr from parts where category like '%chip_resistor%' and package = ? "
                       "and descr like ? and descr like ?", (package, f'%{jlc}%', f'%±{tol}%')).fetchall()
    rows = [r for r in rows if re.search(rf'(^|\s){re.escape(jlc)}(\s|$)', r[4])]
    if power:
        mw = round(float(power[:-1]) * 1000)
        rows = [r for r in rows if any(int(x) >= mw for x in re.findall(r'(\d+)mW', r[4])) or
                any(float(x) * 1000 >= mw for x in re.findall(r'(\d+(?:\.\d+)?)W(?!\w)', r[4]))]
    note = '' if any(t.endswith('%') for t in tok[1:]) else 'no tolerance stated: 1% chosen'
    return rows, note


def capacitor(con, value, package):
    tok = value.split()
    m = re.fullmatch(r'(\d+(?:\.\d+)?)([pnu])', tok[0])
    if not m:
        return None, 'value not parsed'
    jlc = m.group(1) + UNITS[m.group(2)]
    volts = next((float(t[:-1]) for t in tok[1:] if re.fullmatch(r'\d+(\.\d+)?V', t)), None)
    diel = next((t for t in tok[1:] if t in DIELECTRIC_OK), None)
    rows = con.execute("select lcsc, mfr, class, stock, descr from parts where category like '%multilayer_ceramic%' and package = ? "
                       "and descr like ?", (package, f'%{jlc}%')).fetchall()
    out = []
    for r in rows:
        if not re.search(rf'(^|\s){re.escape(jlc)}(\s|$)', r[4]):
            continue
        v = re.search(r'(?:^|\s)(\d+(?:\.\d+)?)V\s', r[4])
        if volts and (not v or float(v.group(1)) < volts):
            continue
        if diel and not any(d in r[4] for d in DIELECTRIC_OK[diel]):
            continue
        out.append(r)
    return out, ''


def main(netlist, db):
    con = sqlite3.connect(db)
    print('| Value | Package | Qty | LCSC | Part | Class | Stock | Note |')
    print('| --- | --- | --- | --- | --- | --- | --- | --- |')
    misses = 0
    for (kind, value, package), refs in sorted(bom_lines(netlist).items(), key=lambda x: (x[0][0], x[0][2], x[0][1])):
        rows, note = (resistor if kind == 'R' else capacitor)(con, value, package)
        n_dnp = sum(d for _, d in refs)
        qty = f'{len(refs)}' + (f' ({n_dnp} DNP)' if n_dnp else '')
        if not rows:
            misses += 1
            print(f'| {value} | {package} | {qty} | none | | | | **not matched**{"; " + note if note else ""} |')
            continue
        best = sorted(rows, key=lambda r: (r[2] != 'Basic', -r[3]))[0]
        print(f'| {value} | {package} | {qty} | {best[0]} | {best[1]} | {best[2]} | {best[3]:,} | {note} |')
    return misses


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1], sys.argv[2]) < 0 else 0)
