"""Step 5, sheet 05-can: CAN bus 2, Gecko connectors, and the B-39 reference footprints.

Capture specification rows: CAN bus 2 (D-5Nov.3, D-18Nov.4); CAN references (B-39, D-21Nov.11).
1. J501 becomes a Harwin Gecko-SL 2x3 (G125-MS10605M2P, screw-lok, vertical SMT): 1 CAN H, 2 CAN L,
   3 reference, 4-6 spare. The series is provisional (D-18Nov.4 left it open): Seán confirms.
2. B-39: the reference contact reaches GND through R516 and F501 (resistor and resettable-fuse
   footprints), 0R until the bench sets values.
3. Bus 2 is a copy of bus 1's boundary and transceiver block (U502 / U503 and their parts, including
   the connector and B-39 parts), on FDCAN2, sharing CAN_3V3, CAN_POWER_EN and CAN_STB.
Edits the sheet in place (run from a clean checkout). Vendors Conn_02x03_Top_Bottom, Polyfuse,
Fuse_1206_3216Metric and the Gecko-SL footprint from KiCad 9.0.7.
"""
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
SHEET = '05-can.kicad_sch'
GECKO = 'G125-MS10605M2P'
DY = 165.1                      # bus 2 sits this far below bus 1
BLOCK_Y = (140, 300)            # bus 1's boundary-and-transceiver block
FOOTER_DY = 167.64

REF_MAP = {'U502': 'U504', 'U503': 'U505', 'D501': 'D502', 'R504': 'R511', 'R505': None, 'R506': 'R512',
           'R507': 'R513', 'R508': 'R514', 'R510': 'R515', 'R516': 'R517', 'F501': 'F502',
           'C503': 'C507', 'C504': 'C508', 'C505': 'C509', 'C506': 'C510', 'TP503': 'TP505', 'TP504': 'TP506',
           'J501': 'J502'}
NET_MAP = {'CAN_TX': 'CAN2_TX', 'CAN_RX': 'CAN2_RX', 'CAN_TX_ISO': 'CAN2_TX_ISO', 'CAN_RX_ISO': 'CAN2_RX_ISO',
           'CAN_STB_ISO': 'CAN2_STB_ISO', 'CAN+': 'CAN2+', 'CAN-': 'CAN2-', 'CAN_REF': 'CAN2_REF'}

TEXT = [
    ('CAN / SWITCHED POWER / LOGIC BOUNDARY / TWISTED PAIR', 'CAN / SWITCHED POWER / LOGIC BOUNDARIES / TWO BUSES'),
    ('What this does: Connects the flight MCU to the propulsion controller over a wired CAN pair.',
     'What this does: Connects the flight MCU to the propulsion controller (bus 1, FDCAN1, J501) and to the active board\n'
     '(bus 2, FDCAN2, J502), each over its own wired CAN pair.'),
    ('Connects to: Flight CAN pins -> switched transceiver -> JST GH H/L/reference. The two-node link is 500 kbit/s; this connector supplies no power.',
     'Connects to: Flight CAN pins -> switched transceivers -> Harwin Gecko-SL H / L / reference. Each link is two nodes at\n'
     '500 kbit/s; neither connector supplies power. Both transceivers share CAN_3V3 (PB1) and standby (PE10).'),
    ('the third conductor is the reference return.',
     'the third conductor is the reference return.\n'
     'Each reference contact reaches GND only through R516 / F501 (bus 1) or R517 / F502 (bus 2): footprints for a\n'
     'resistor and a resettable fuse, 0R until the bench sets values inside the TCAN3413 common-mode range (B-39).'),
]


def vendor():
    K.vendor_symbol(LIB / 'Connector_Generic.kicad_sym', 'Conn_02x03_Top_Bottom', f'{K.KICAD_SYMBOLS}/Connector_Generic.kicad_sym')
    K.vendor_symbol(LIB / 'Device.kicad_sym', 'Polyfuse', f'{K.KICAD_SYMBOLS}/Device.kicad_sym')
    (LIB / 'Fuse.pretty').mkdir(exist_ok=True)
    K.vendor_footprint(LIB, 'Fuse', 'Fuse_1206_3216Metric')
    dst = LIB / 'Ogma2.pretty' / f'{GECKO}.kicad_mod'
    if not dst.exists():
        fp = K.load(f'{K.KICAD_FOOTPRINTS}/Connector_Harwin.pretty/Harwin_Gecko_G125-MS10605M2P_2x03_P1.25mm_Vertical.kicad_mod')
        fp[1] = GECKO
        for p in K.children(fp, 'property'):
            if p[1] == 'Value':
                p[2] = GECKO
        for m in K.children(fp, 'model'):
            m[1] = m[1].replace('${KICAD9_3DMODEL_DIR}', '${KIPRJMOD}/libraries/3d')
        K.save(fp, dst)
    table = BOARD / 'fp-lib-table'
    t = K.load(table)
    if not any(K.first(l, 'name')[1] == 'Fuse' for l in K.children(t, 'lib')):
        t.append(K.el('lib', K.el('name', 'Fuse'), K.el('type', 'KiCad'), K.el('uri', '${KIPRJMOD}/libraries/Fuse.pretty'),
                      K.el('options', ''), K.el('descr', 'KiCad 9.0.7 footprints added during capture')))
        K.save(t, table)


def gecko_and_b39(t):
    """J501 becomes the Gecko-SL 2x3; its reference contact goes through R516 and F501."""
    old = K.pin_positions(t, 'J501')
    assert old['1'][:2] == (365.76, 220.98) and old['2'][:2] == (365.76, 231.14) and old['3'][:2] == (375.92, 241.3), old
    sym = K.symbols(t)['J501']
    K.remove(t, lambda x: x is sym)                              # CAN H / L wires stay for the new J501
    assert K.strip_branch(t, (375.92, 241.3), 'J501') == [('wire', (375.92, 241.3), (375.92, 248.92)), ('label', 'GND', (375.92, 248.92))]
    seg = [w for w, a, b in K.wires(t) if {a, b} == {(330.2, 231.14), (365.76, 231.14)}]
    assert len(seg) == 1
    K.remove(t, lambda x: x is seg[0])
    K.path(t, [(330.2, 231.14), (355.6, 231.14), (355.6, 223.52), (365.76, 223.52)], SHEET, 'canl.jog')
    K.import_lib(t, 'Connector_Generic:Conn_02x03_Top_Bottom', LIB / 'Connector_Generic.kicad_sym')
    K.import_lib(t, 'Device:Polyfuse', LIB / 'Device.kicad_sym')
    j = K.make_symbol(t, 'Connector_Generic:Conn_02x03_Top_Bottom', 'J501', (370.84, 223.52), 0, GECKO, f'Ogma2:{GECKO}', SHEET,
                      extra={'MPN': GECKO, 'Manufacturer': 'Harwin',
                             'Datasheet': 'https://cdn.harwin.com/pdfs/G125-MS1XX05M2P.pdf',
                             'Description': 'Gecko-SL 2x3 male, vertical SMT, screw-lok fixings (D-18Nov.4)',
                             'Library_Check': 'footprint from KiCad 9.0.7 Connector_Harwin (Harwin drawing G125-MS1XX05M2P); '
                                              'series provisional pending Seán and the Fajita owner',
                             'Implementation_Note': '1 CAN H, 2 CAN L, 3 reference, 4-6 spare; no power (D-18Nov.4). '
                                                    'Bus 1 to the propulsion controller (Fajita)'},
                      ref_at=(368.3, 215.9), val_at=(368.3, 217.17))
    assert j['1'][:2] == (365.76, 220.98) and j['2'][:2] == (365.76, 223.52) and j['3'][:2] == (365.76, 226.06), j
    for pin in ('4', '5', '6'):
        K.add(t, K.no_connect(j[pin][:2], SHEET, f'j501.{pin}'))
    # B-39: reference -> R516 -> F501 -> GND.
    K.make_symbol(t, 'Device:R', 'R516', (358.14, 243.84), 0, '0R', 'Resistor_SMD:R_0805_2012Metric', SHEET,
                  extra={'Implementation_Note': 'B-39: CAN reference series resistor; value from the bench, inside the '
                                                'TCAN3413 common-mode range; 0R until then (D-21Nov.11)'})
    K.make_symbol(t, 'Device:Polyfuse', 'F501', (358.14, 256.54), 0, '0R link', 'Fuse:Fuse_1206_3216Metric', SHEET,
                  extra={'Implementation_Note': 'B-39: resettable-fuse footprint on the CAN reference; fitted with a 0R link '
                                                'until the bench picks a part (D-21Nov.11)'})
    K.path(t, [(365.76, 226.06), (358.14, 226.06), (358.14, 240.03)], SHEET, 'ref.a')
    K.path(t, [(358.14, 247.65), (358.14, 252.73)], SHEET, 'ref.b')
    K.path(t, [(358.14, 260.35), (358.14, 264.16)], SHEET, 'ref.c')
    K.add(t, K.local_label('CAN_REF', (358.14, 233.68), 0, SHEET, 'ref'))
    K.add(t, K.global_label('GND', (358.14, 264.16), 0, SHEET, 'ref'))
    # the label sits on the reference run: split the wire there
    seg = [w for w, a, b in K.wires(t) if {a, b} == {(358.14, 226.06), (358.14, 240.03)}]
    K.remove(t, lambda x: x is seg[0])
    K.path(t, [(358.14, 226.06), (358.14, 233.68), (358.14, 240.03)], SHEET, 'ref.a2')


def in_block(node):
    if node[0] == 'wire':
        ys = [float(q[2]) for q in K.walk(node, 'xy')]
    elif node[0] == 'symbol':
        ys = [float(K.first(node, 'at')[2])]
    else:
        ys = [float(K.first(node, 'at')[2])]
    return all(BLOCK_Y[0] <= y <= BLOCK_Y[1] for y in ys)


def renew_uuids(node, salt):
    for u in K.walk(node, 'uuid'):
        u[1] = K.ident(SHEET, 'bus2', salt, u[1])


def copy_bus(t):
    """Bus 2: bus 1's block, moved down DY, with references and nets renamed."""
    kinds = ('symbol', 'wire', 'junction', 'global_label', 'label', 'no_connect')
    block = [n for n in t if isinstance(n, list) and n and n[0] in kinds and in_block(n)]
    refs = {K.props(n)['Reference'] for n in block if n[0] == 'symbol'}
    assert refs == set(REF_MAP), (sorted(refs - set(REF_MAP)), sorted(set(REF_MAP) - refs))
    for n in block:
        c = copy.deepcopy(n)
        if c[0] == 'symbol':
            ref = K.props(c)['Reference']
            K.move_symbol(c, (float(K.first(c, 'at')[1]), float(K.first(c, 'at')[2]) + DY))
            new = REF_MAP[ref] or f'{ref}_DROP'
            for p in K.children(c, 'property'):
                if p[1] == 'Reference':
                    p[2] = new
                if p[1] == 'Value' and new.startswith('TP'):
                    p[2] = NET_MAP.get(p[2], p[2])
            for path in K.walk(c, 'path'):
                K.first(path, 'reference')[1] = new
            renew_uuids(c, new)
        elif c[0] == 'wire':
            for q in K.walk(c, 'xy'):
                q[2] = K.num(float(q[2]) + DY)
            renew_uuids(c, 'w')
        else:
            a = K.first(c, 'at')
            a[2] = K.num(float(a[2]) + DY)
            if c[0] in ('global_label', 'label'):
                c[1] = NET_MAP.get(c[1], c[1])
                for p in K.children(c, 'property'):
                    pa = K.first(p, 'at')
                    pa[2] = K.num(float(pa[2]) + DY)
            renew_uuids(c, c[0])
        K.add(t, c)
    return K.remove_part(t, 'R505_DROP')                  # CAN_STB is shared: bus 1's pull-up serves both


def build():
    vendor()
    t = K.load(BOARD / SHEET)
    gecko_and_b39(t)
    # make room: the footer moves below bus 2, the page grows
    for n in K.children(t, 'text'):
        a = K.first(n, 'at')
        if float(a[2]) > 300:
            a[2] = K.num(float(a[2]) + FOOTER_DY)
    paper = K.first(t, 'paper')
    paper[3] = K.num(float(paper[3]) + FOOTER_DY + 2.54)
    log = copy_bus(t)
    for old, new in TEXT:
        hits = [n for n in K.children(t, 'text') if old in n[1]]
        assert len(hits) == 1, old
        hits[0][1] = hits[0][1].replace(old, new)
    for y, title in ((144.78, 'BUS 1 / FDCAN1 / PROPULSION CONTROLLER (FAJITA) / J501'),
                     (144.78 + DY, 'BUS 2 / FDCAN2 / ACTIVE BOARD / J502')):
        K.add(t, K.text(title, (15.24, y), SHEET, title, 1.524))
    K.save(t, BOARD / SHEET)
    return log


if __name__ == '__main__':
    print(build())
