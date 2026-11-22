"""Step 16: the 0402 swap (D-22Nov.13, execution brief A4). Every 0603 resistor and capacitor is classified by its nets
against the brief's rules; the ones that pass move to KiCad's R_0402_1005Metric / C_0402_1005Metric with a pinned JLC
part (MPN and LCSC fields). No pin changes. The full table, with each part's reason, goes to passives-0402.md.

Rules (brief A4, D-22Nov.13): swap pull-ups and pull-downs, series and divider resistors at 1%, and capacitors of
1 uF or less on rails of 5 V or less. Keep anything at 0.1%; sense, limit, shunt and termination resistors; every
part on a fire, arm or continuity net; capacitors of 2.2 uF or more; any capacitor whose 0402 part isn't rated at
twice its rail; any resistor that would dissipate over 30 mW. Same value and tolerance; same dielectric or better;
JLC Basic where one exists, else the best-stocked Extended part. A capacitor's stated voltage stays a floor [J]: it
sets how much of the value survives the rail's bias, and the brief asks for the same value.

How each rule is read here [J]:
  - fire, arm, continuity: every part on the 06-* sheets (outputs, arm boundary, diagnostics, continuity, the pyro
    channels), and anything on a net of the FIRE, FIRE_LOGIC or PYRO_RAIL classes or an arm or pyro sense node;
  - a net's voltage: the rail table below; any other net takes the highest of the rails of the ICs, transistors and
    connectors on it, and of the nets reached through resistors, diodes, inductors and fuses (not capacitors). It
    is an upper bound: a divider's midpoint gets the voltage at its top;
  - a resistor's dissipation: (highest voltage on its nets)^2 / R, except a series resistor between two IC pins
    on nets with no rail, connector or test point (CMOS in to out: no DC path), which is taken as ~0;
  - 0 R links are not in the swap list (they carry rail current) and stay;
  - a capacitor with a part number already pinned (C1006) stays.
"""
import math
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
JLC_DB = Path('/home/claude/capture/jlc.sqlite')        # jlcparts scrape of 21 Nov 2026 (jlc-stock.md)
REPORT = BOARD / 'passives-0402.md'
FP = {'R': 'Resistor_SMD:R_0402_1005Metric', 'C': 'Capacitor_SMD:C_0402_1005Metric'}
P_MAX = 0.030                                            # W (brief A4)
LINK_I = 0.020       # A: a series link between two rails of one voltage carries its load; the sensor rails draw a few mA [J]

VBAT = 9.0           # 2S full is 8.4 V; U101's over-voltage trip is about 9.0 V (D-2Nov.17): the bound used
RAILS = {'GND': 0.0, '4V_PRE': 4.0, 'CORE_HELD_4V': 4.0, 'USB_VBUS': 5.0, 'USB_LIMITED': 5.0,
         'FLIGHT_VDDA': 3.3, 'COMMS_VDDA': 3.3,
         **{n: VBAT for n in ('VBAT_CROI_INPUT', 'VBAT_SHUNT_IN', 'VBAT_PROTECTED', 'ENERGY_TAP', 'LOGIC_SELECTED',
                              'RECOVERY_ARMED_VBAT', 'STAGING_ARMED_VBAT', '/06a-arm-boundary/RECOVERY_ARM_FEED',
                              '/06a-arm-boundary/STAGING_ARM_FEED', 'PYRO1_ENERGY', 'PYRO2_ENERGY', 'PYRO3_ENERGY')}}
FIRE_NET = re.compile(r'PYRO\d_(ENERGY|GATE|FIRE|LS_SELECT|HS_ENABLE|CS|CL)|OUTPUT\d_(HIGH|LOW)|ARMED_VBAT|ARM_FEED|'
                      r'ARM_(VALID|INVALID|SENSE|DIV)|CONT|PYRO_RAIL')
LIMIT_PIN = re.compile(r'ILIM|^CL$|PYRO\d_CL')
SENSE_PIN = re.compile(r'IMON|Vin[+-]|Vbus')
TERMINATION = {'R4401': 'USB-C Rd termination on CC1, open to a cable fault', 'R4402': 'USB-C Rd termination on CC2, open to a cable fault'}
CONDUCT = ('R', 'L', 'D', 'F')                          # parts that carry DC from net to net (FB ferrites are L/FB)


def load(netlist):
    root = ET.parse(netlist).getroot()
    pins, members = defaultdict(dict), defaultdict(list)
    for n in root.findall('nets/net'):
        for x in n.findall('node'):
            pins[x.get('ref')][x.get('pin')] = n.get('name')
            members[n.get('name')].append((x.get('ref'), x.get('pin'), x.get('pinfunction') or ''))
    comps = {}
    for c in root.findall('components/comp'):
        f = {x.get('name'): x.text for x in c.findall('fields/field')}
        comps[c.get('ref')] = dict(value=c.findtext('value') or '', fp=c.findtext('footprint') or '',
                                   sheet=c.find('sheetpath').get('names'), mpn=f.get('MPN'))
    return comps, pins, members


def rail_of(net):
    if net in RAILS:
        return RAILS[net]
    if re.search(r'3V3', net) and not net.endswith('_ILIM') and 'SCALED' not in net and 'MID' not in net:
        return 3.3
    return None


def bounds(comps, pins, members):
    """Upper bound on each net's voltage (see the module notes)."""
    V = {n: rail_of(n) for n in members}
    dev_rails = {}
    for ref, pp in pins.items():
        if ref[:1] in ('U', 'Q', 'J', 'Y'):
            known = [rail_of(n) for n in pp.values() if rail_of(n) is not None]
            dev_rails[ref] = max(known) if known else None
    for n, mem in members.items():
        if V[n] is None:
            got = [dev_rails[r] for r, _, _ in mem if dev_rails.get(r) is not None]
            V[n] = max(got) if got else None
    changed = True
    while changed:                                       # through resistors, diodes, inductors, fuses
        changed = False
        for ref, pp in pins.items():
            if not ref.startswith(CONDUCT) or ref.startswith(('LED',)) or len(pp) != 2:
                continue
            a, b = pp.values()
            for x, y in ((a, b), (b, a)):
                if rail_of(x) is None and V[y] is not None and (V[x] is None or V[y] > V[x]):
                    V[x] = V[y]
                    changed = True
    return V


def parse_r(value):
    tok = value.split()
    m = re.fullmatch(r'(\d+(?:\.\d+)?)([RkM]?)', tok[0])
    if not m:
        return None, None
    ohms = float(m.group(1)) * {'R': 1, '': 1, 'k': 1e3, 'M': 1e6}[m.group(2)]
    tol = next((t for t in tok[1:] if t.endswith('%')), None)
    return ohms, tol


def parse_c(value):
    tok = value.split()
    m = re.fullmatch(r'(\d+(?:\.\d+)?)([pnu])', tok[0])
    farads = float(m.group(1)) * {'p': 1e-12, 'n': 1e-9, 'u': 1e-6}[m.group(2)]
    volts = next((float(t[:-1]) for t in tok[1:] if re.fullmatch(r'\d+(\.\d+)?V', t)), None)
    diel = next((t for t in tok[1:] if t in ('X5R', 'X7R', 'C0G', 'NP0')), None)
    return farads, m.group(1) + {'p': 'pF', 'n': 'nF', 'u': 'uF'}[m.group(2)], volts, diel


DIEL_OK = {'X5R': ('X5R', 'X7R', 'C0G', 'NP0'), 'X7R': ('X7R', 'C0G', 'NP0'), 'C0G': ('C0G', 'NP0'), 'NP0': ('C0G', 'NP0'), None: None}


def pick(con, kind, value, need_v=None):
    """The 0402 JLC part: same value and tolerance (resistors; 1% where none is stated, as jlc_passives.py does),
    same dielectric or better and at least need_v (capacitors); Basic first, then stock. Returns (row, note)."""
    if kind == 'R':
        ohms, tol = parse_r(value)
        tol = tol or '1%'
        num = value.split()[0]
        jlc = f"{num[:-1] if num.endswith('R') else num}Ω"
        rows = con.execute("select lcsc, mfr, class, stock, descr from parts where category like '%chip_resistor%' and "
                           "package = '0402' and descr like ? and descr like ? and stock > 0",
                           (f'%{jlc}%', f'%±{tol}%')).fetchall()
        rows = [r for r in rows if re.search(rf'(^|\s){re.escape(jlc)}(\s|$)', r[4]) and re.search(rf'±{re.escape(tol)}(\s|$)', r[4])]
    else:
        farads, jlc, volts, diel = parse_c(value)
        rows = con.execute("select lcsc, mfr, class, stock, descr from parts where category like '%multilayer_ceramic%' "
                           "and package = '0402' and descr like ? and stock > 0", (f'%{jlc}%',)).fetchall()
        out = []
        for r in rows:
            if not re.search(rf'(^|\s){re.escape(jlc)}(\s|$)', r[4]):
                continue
            v = re.search(r'(?:^|\s)(\d+(?:\.\d+)?)V(?:\s|$)', r[4])
            if not v or float(v.group(1)) < max(volts or 0, need_v or 0):
                continue
            if DIEL_OK[diel] and not any(d in r[4].split() for d in DIEL_OK[diel]):
                continue
            out.append(r)
        rows = out
    rows.sort(key=lambda r: (r[2] != 'Basic', -r[3]))
    return (rows[0] if rows else None)


def classify(netlist, db=JLC_DB):
    comps, pins, members = load(netlist)
    V = bounds(comps, pins, members)
    con = sqlite3.connect(db)
    out = []
    for ref, c in sorted(comps.items()):
        kind = ref[0]
        if kind not in 'RC' or not re.search(r':(R|C)_0603_1608Metric$', c['fp']):
            continue
        nets = [pins[ref].get('1'), pins[ref].get('2')]
        funcs = [f for n in nets for r, _, f in members[n] if r[0] in 'UQ']
        vmax = None if any(V[n] is None for n in nets) else max(V[n] for n in nets)
        row = dict(ref=ref, value=c['value'], sheet=c['sheet'].strip('/'), nets=nets, v=vmax, swap=False, part=None)
        def keep(why, cls=None):
            row['why'], row['cls'] = why, cls or why
            out.append(row)
        if c['sheet'].startswith('/06'):
            keep('fire path (06 sheets)'); continue
        if any(FIRE_NET.search(n) for n in nets):
            keep('on a fire, arm or continuity net'); continue
        if kind == 'R':
            ohms, tol = parse_r(c['value'])
            if c['value'].startswith('0R'):
                keep('0 R link: not in the swap list, carries rail current'); continue
            if tol == '0.1%':
                keep('0.1%'); continue
            if ref in TERMINATION:
                keep(TERMINATION[ref], 'USB-C Rd termination (CC), open to a cable fault'); continue
            if any(LIMIT_PIN.search(f) for f in funcs) or any(n.endswith('_ILIM') for n in nets):
                keep('current limit set'); continue
            if any(SENSE_PIN.search(f) for f in funcs):
                keep('sense'); continue
            if vmax is None:
                keep('net voltage not bounded'); continue
            others = [(r, n) for n in nets for r, _, _ in members[n] if r != ref]
            rails = [rail_of(n) for n in nets]
            if all(v is not None for v in rails) and rails[0] == rails[1] and rails[0] > 0:
                p, how = LINK_I ** 2 * ohms, f'rail link, I <= {LINK_I * 1000:.0f} mA assumed: <= {LINK_I ** 2 * ohms * 1000:.1f} mW'
            elif all(v is None for v in rails) and not any(r[0] in 'JDQYT' or r.startswith(('TP', 'LED')) for r, _ in others) \
                    and all(any(r[0] == 'U' for r, _, _ in members[n]) for n in nets):
                pull_i = sum(rail_of(pins[r][q]) / parse_r(comps[r]['value'])[0] for r, n in others if r[0] == 'R'
                             for q in pins[r] if pins[r][q] != n and rail_of(pins[r][q]))
                p, how = pull_i ** 2 * ohms, f'series between IC pins; DC only from pulls: <= {pull_i ** 2 * ohms * 1000:.2f} mW'
            else:
                p, how = vmax ** 2 / ohms, f'<= {vmax ** 2 / ohms * 1000:.1f} mW at {vmax:g} V'
            row['p_mw'] = round(p * 1000, 2)
            if p > P_MAX:
                keep(f'up to {p * 1000:.0f} mW ({vmax:g} V across)', 'would dissipate over 30 mW'); continue
            part = pick(con, 'R', c['value'])
            if not part:
                keep('no 0402 part at JLC with this value and tolerance'); continue
            row.update(swap=True, part=part, why=how)
            out.append(row)
        else:
            if c['mpn']:
                keep('part number already pinned'); continue
            farads, _, volts, diel = parse_c(c['value'])
            if farads >= 2.2e-6:
                keep('2.2 uF or more'); continue
            if farads > 1e-6:
                keep('over 1 uF'); continue
            if vmax is None:
                keep('net voltage not bounded'); continue
            if vmax > 5.0:
                keep(f'rail above 5 V ({vmax:g} V)', 'rail above 5 V'); continue
            part = pick(con, 'C', c['value'], need_v=2 * vmax)
            if not part:
                keep(f'no 0402 part at JLC with this value and dielectric at {max(volts or 0, 2 * vmax):g} V or more',
                     'no 0402 part at JLC with the value, dielectric and stated voltage (1 uF X7R: 10 V at most)'); continue
            row.update(swap=True, part=part, why=f'{c["value"].split()[0]} on {vmax:g} V; 0402 part rated >= {2 * vmax:g} V')
            out.append(row)
    return out


def set_props(sym, kv):
    pr = {p[1]: p for p in K.children(sym, 'property')}
    for k, v in kv.items():
        if k in pr:
            pr[k][2] = v
        else:
            i = next(i for i, x in enumerate(sym) if isinstance(x, list) and x and x[0] == 'instances')
            sym.insert(i, K.prop(k, v, K.xy(sym)))


def courtyard(fid):
    lib, name = fid.split(':')
    tree = K.load(LIB / f'{lib}.pretty' / f'{name}.kicad_mod')
    xs, ys = [], []
    for kind in ('fp_line', 'fp_rect'):
        for g in K.children(tree, kind):
            if K.first(g, 'layer')[1] == 'F.CrtYd':
                for tag in ('start', 'end'):
                    n = K.first(g, tag)
                    xs.append(float(n[1])); ys.append(float(n[2]))
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


def report(rows):
    sw = [r for r in rows if r['swap']]
    a = {(k, s): courtyard(f'{"Resistor_SMD" if k == "R" else "Capacitor_SMD"}:{k}_{s}') for k in 'RC'
         for s in ('0603_1608Metric', '0402_1005Metric')}
    saved = sum(a[(r['ref'][0], '0603_1608Metric')] - a[(r['ref'][0], '0402_1005Metric')] for r in sw)
    lines = ['# Burrito passives: the 0402 swap (capture step 16, D-22Nov.13)', '',
             'Generated by `tools/capture/steps/s16_0402.py` from the step-15 netlist and the jlcparts scrape of 21 Nov 2026. '
             'The rules and how each is read are in the script\'s header. Each swapped part has its JLC part pinned (MPN and LCSC '
             'fields); the parts that stay keep their generic values for `jlc_passives.py`.', '',
             f'**{len(sw)} of {len(rows)} 0603 parts move to 0402** ({sum(r["ref"][0] == "R" for r in sw)} resistors, '
             f'{sum(r["ref"][0] == "C" for r in sw)} capacitors). Courtyard area saved: **{saved:.0f} mm²** '
             f'(KiCad courtyards: R 0603 {a[("R", "0603_1608Metric")]:.2f}, 0402 {a[("R", "0402_1005Metric")]:.2f}; '
             f'C 0603 {a[("C", "0603_1608Metric")]:.2f}, 0402 {a[("C", "0402_1005Metric")]:.2f} mm²).', '']
    why = defaultdict(int)
    for r in rows:
        if not r['swap']:
            why[r['cls']] += 1
    lines += ['| Stays 0603 because | Parts |', '| --- | --- |'] + [f'| {k} | {v} |' for k, v in sorted(why.items(), key=lambda x: -x[1])] + ['']
    lines += ['## Swapped', '', '| Ref | Value | Sheet | Nets | Bound | Why it may move | LCSC | Part | Class | Stock |',
              '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in sw:
        p = r['part']
        lines.append(f"| {r['ref']} | {r['value']} | {r['sheet']} | {' / '.join(r['nets'])} | {r['v']:g} V | {r['why']} | {p[0]} | "
                     f"{p[1]} | {p[2]} | {p[3]:,} |")
    lines += ['', '## Staying', '', '| Ref | Value | Sheet | Nets | Bound | Why |', '| --- | --- | --- | --- | --- | --- |']
    for r in rows:
        if not r['swap']:
            b = '?' if r['v'] is None else f"{r['v']:g} V"
            lines.append(f"| {r['ref']} | {r['value']} | {r['sheet']} | {' / '.join(n or '' for n in r['nets'])} | {b} | {r['why']} |")
    REPORT.write_text('\n'.join(lines) + '\n')
    return len(sw), saved


def build(netlist):
    rows = classify(netlist)
    sw = {r['ref']: r for r in rows if r['swap']}
    for kind, fid in FP.items():
        K.vendor_footprint(LIB, fid.split(':')[0], fid.split(':')[1])
    found = defaultdict(list)
    for f in sorted(BOARD.glob('*.kicad_sch')):
        t = K.load(f)
        syms = K.symbols(t)
        hit = [r for r in sw if r in syms]
        for r in hit:
            p = sw[r]['part']
            set_props(syms[r], {'Footprint': FP[r[0]], 'MPN': p[1], 'LCSC': p[0]})
            found[r].append(f.name)
        if hit:
            K.save(t, f)
    assert all(len(found[r]) == 1 for r in sw) and len(found) == len(sw), [r for r in sw if len(found[r]) != 1]
    return report(rows)


if __name__ == '__main__':
    n, saved = build(sys.argv[1] if len(sys.argv) > 1 else str(BOARD / 'output' / 'full-netlist.xml'))
    print(f'{n} parts to 0402; {saved:.0f} mm2 of courtyard saved; table in {REPORT.name}')
