"""Step 4, the five sensor sheets and the new magnetometer sheet.

Part 1, the five sensor sheets: no switches or isolators; a 47 ohm link per sensor supply.

Capture specification row: Sensors (D-6.6, D-2Nov.3). For each sheet:
- remove the TPS2553 switch, the TXU0304 / TXU0101 translators or the TMUX1511 switch, the enable
  pull-down R3x02, the rail bleeder R3x03, and the local bypass capacitors of those parts;
- the link R3x01 becomes 47R 1% and takes FLIGHT_3V3 where the switch output was;
- join each MCU-side net to its sensor-side twin (labels X_ISO become X), keeping the 22R damping;
- move the sensor-side pull-ups from the sensor rail to FLIGHT_3V3.
Edits the sheets in place (run from a clean checkout).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
SHEETS = {  # sheet: (prefix, link, switch/translator ICs, enable pull-down and bleeder)
    '03st-sensor': ('ST', 'R3101', ['U3101', 'U3102', 'U3103'], ['R3102', 'R3103']),
    '03tdk-sensor': ('TDK', 'R3201', ['U3201', 'U3202', 'U3203'], ['R3202', 'R3203']),
    '03hg-sensor': ('HG', 'R3301', ['U3301', 'U3302', 'U3303'], ['R3302', 'R3303']),
    '03bmp-pressure': ('BMP', 'R3401', ['U3401', 'U3402'], ['R3402', 'R3403']),
    '03te-pressure': ('TE', 'R3501', ['U3501', 'U3502'], ['R3502', 'R3503']),
}
LINK = '47R 1%'
FLAG_NOTE = 'ERC source path through the 47 ohm link from FLIGHT_3V3. Not a qualification claim.'

COMMON_TEXT = [
    ('1  PROTECTED SUPPLY', '1  SUPPLY LINK'),
    ('2  FLIGHT-TO-SENSOR SPI / POWERED-OFF BOUNDARY', '2  FLIGHT-TO-SENSOR SPI'),
    ('2  INDEPENDENT I2C / POWERED-OFF BOUNDARY', '2  INDEPENDENT I2C'),
    ('Local rails remain independently switched. No firmware pin allocations, default pulls, values or DNP states changed by this redraw.',
     'No switches or isolators (D-6.6). Firmware parks a dead sensor\'s bus pins so the MCU cannot back-power it\n'
     'through the 22 ohm damping (D-2Nov.3). Pull-ups go to FLIGHT_3V3.'),
    ('Two independently powered, dissimilar pressure sensors remain selected.',
     'Two dissimilar pressure sensors, each behind its own supply link.'),
]
SHEET_TEXT = {
    '03st-sensor': [('Its own power switch and signal switches separate it from an unpowered or disabled sensor.',
                     'Fed from FLIGHT_3V3 through R3101, a 47 ohm link: a shorted sensor draws <=71 mA (D-6.6, D-2Nov.3).')],
    '03tdk-sensor': [('It has its own switched branch, separate from the ST IMU on 03st-sensor.',
                      'Fed from FLIGHT_3V3 through R3201, a 47 ohm link, like the ST IMU (D-6.6, D-2Nov.3).')],
    '03hg-sensor': [('Its supply and signal switches allow independent shutdown.',
                     'Fed from FLIGHT_3V3 through R3301, a 47 ohm link (D-6.6, D-2Nov.3).')],
    '03bmp-pressure': [('plus independent switched power.', 'supplied through R3401, a 47 ohm link from FLIGHT_3V3 (D-6.6, D-2Nov.3).')],
    '03te-pressure': [('plus independent switched power.', 'supplied through R3501, a 47 ohm link from FLIGHT_3V3 (D-6.6, D-2Nov.3).')],
}


def local(t, ref, pin):
    """Other pins and labels on the wire tree of ref.pin (no label hops)."""
    allpins = {r: K.pin_positions(t, r) for r in K.symbols(t)}
    pts, _ = K.connected_points(t, allpins[ref][pin][:2])
    others = [(r, m) for r, ps in allpins.items() if r != ref for m, v in ps.items() if v[:2] in pts]
    return others, K.labels_at(t, pts)


def set_value(sym, value):
    for p in K.children(sym, 'property'):
        if p[1] == 'Value':
            p[2] = value


def retext(t, pairs, sheet):
    for old, new in pairs:
        hits = [n for n in K.children(t, 'text') if old in n[1]]
        assert len(hits) <= 1, (sheet, old)
        for n in hits:
            n[1] = n[1].replace(old, new)
    return t


def sensor_sheet(sheet, P, link, ics, rs):
    t = K.load(BOARD / f'{sheet}.kicad_sch')
    syms = K.symbols(t)
    # Bypass capacitors that serve only the parts being removed.
    caps = [r for r in syms if r.startswith('C') and (o := local(t, r, '1')[0]) and all(x[0] in ics for x in o)]
    # Sensor-side pull-ups: one end only on the sensor rail's label.
    pulls = []
    for r in syms:
        if r.startswith('R') and r not in rs + [link]:
            o, labs = local(t, r, '1')
            if not o and [l[1] for l in labs] == [f'{P}_3V3']:
                pulls.append((r, labs[0]))
    # 1. Names: sensor-side twins take the MCU-side names; the switch output becomes FLIGHT_3V3.
    renamed = {}
    for lab in K.children(t, 'global_label'):
        if lab[1].endswith('_ISO'):
            renamed[lab[1]] = lab[1][:-4]
            lab[1] = lab[1][:-4]
        elif lab[1] == f'{P}_3V3_PRELINK':
            renamed[lab[1]] = 'FLIGHT_3V3'
            lab[1] = 'FLIGHT_3V3'
    for r, lab in pulls:
        lab[1] = 'FLIGHT_3V3'
    # 2. Remove the switch, translators, their bypass capacitors, the pull-down and the bleeder.
    log = {}
    for r in ics + caps + rs:
        log[r] = K.remove_part(t, r)
    # 3. The link becomes 47 ohm; test points follow their nets; the ERC flag note follows the new source.
    set_value(K.symbols(t)[link], LINK)
    for r, s in K.symbols(t).items():
        p = K.props(s)
        if r.startswith('TP') and p['Value'].endswith('_ISO'):
            set_value(s, p['Value'][:-4])
        if r.startswith('#FLG'):
            for q in K.children(s, 'property'):
                if q[1] == 'Implementation_Note':
                    q[2] = FLAG_NOTE
    retext(t, COMMON_TEXT + SHEET_TEXT[sheet], sheet)
    K.remove(t, lambda x: x[0] == 'text' and x[1] == '3  SENSOR-TO-FLIGHT DATA READY')   # now drawn at the sensor
    K.save(t, BOARD / f'{sheet}.kicad_sch')
    return dict(caps=caps, pulls=[r for r, _ in pulls], renamed=renamed, log=log)


ROOT_UUID = 'a9e6a58d-37d4-4c26-836a-c708a8c9d69e'
MAG = '03mag-magnetometer.kicad_sch'
LIB = BOARD / 'libraries'
R0603, C0603, C1206 = 'Resistor_SMD:R_0603_1608Metric', 'Capacitor_SMD:C_0603_1608Metric', 'Capacitor_SMD:C_1206_3216Metric'
DATASHEET = 'https://mpython-docs-en.readthedocs.io/en/latest/_downloads/904b626be755c6b67b1cbb23966aeee9/MMC5983MA.pdf'
MAG_PINS = [  # number, name, type, side, y
    ('1', 'SCL/SPI_SCK', 'input', 'L', 7.62), ('16', 'SDA/SPI_SDI', 'bidirectional', 'L', 5.08), ('15', 'INT', 'output', 'L', 2.54),
    ('4', 'SPI_CS', 'input', 'L', 0), ('5', 'SPI_SDO', 'output', 'L', -2.54),
    ('3', 'NC', 'no_connect', 'L', -7.62), ('6', 'NC', 'no_connect', 'L', -10.16), ('7', 'NC', 'no_connect', 'L', -12.7),
    ('2', 'VDD', 'power_in', 'R', 7.62), ('10', 'CAP', 'power_in', 'R', 5.08), ('13', 'VDDIO', 'power_in', 'R', 2.54),
    ('8', 'NC', 'no_connect', 'R', -2.54), ('12', 'NC', 'no_connect', 'R', -5.08), ('14', 'NC', 'no_connect', 'R', -7.62),
    ('9', 'GND', 'power_in', 'R', -10.16), ('11', 'GND', 'power_in', 'R', -12.7)]
FP_CHECK = ('pins transcribed from the MMC5983MA pin table (MEMSIC datasheet Rev A); footprint is KiCad 9.0.7 '
            'Package_LGA:LGA-16_3x3mm_P0.5mm, made from MEMSIC\'s MMC5883MA drawing (same 3 x 3 x 1 mm LGA-16): '
            'pads to check against the MMC5983MA drawing before layout')


def mag_library():
    sym = K.ic_symbol('MMC5983MA', MAG_PINS, {
        'Reference': 'U', 'Value': 'MMC5983MA', 'Footprint': 'Ogma2:MMC5983MA', 'Datasheet': DATASHEET,
        'MPN': 'MMC5983MA', 'Manufacturer': 'MEMSIC', 'Description': 'Magnetometer, I2C 0x30 (D-2Nov.11)',
        'Library_Check': FP_CHECK}, top=10.16, bottom=-15.24)
    K.add_lib_symbol(LIB / 'Ogma2.kicad_sym', sym)
    dst = LIB / 'Ogma2.pretty' / 'MMC5983MA.kicad_mod'
    if not dst.exists():
        fp = K.load(f'{K.KICAD_FOOTPRINTS}/Package_LGA.pretty/LGA-16_3x3mm_P0.5mm.kicad_mod')
        fp[1] = 'MMC5983MA'
        for d in K.children(fp, 'descr'):
            d[1] = 'MEMSIC MMC5983MA, LGA-16 3 x 3 x 1 mm. From KiCad 9.0.7 Package_LGA:LGA-16_3x3mm_P0.5mm (MEMSIC MMC5883MA drawing); check against the MMC5983MA drawing'
        for prop in K.children(fp, 'property'):
            if prop[1] == 'Value':
                prop[2] = 'MMC5983MA'
        for m in K.children(fp, 'model'):
            m[1] = m[1].replace('${KICAD9_3DMODEL_DIR}', '${KIPRJMOD}/libraries/3d')
        K.save(fp, dst)


def text(t, value, at, size, tag, justify='left'):
    K.add(t, K.el('text', value, K.el('exclude_from_sim', K.A('no')), K.el('at', K.num(at[0]), K.num(at[1]), K.num(0)),
                  K.fx(size, justify), K.el('uuid', K.ident(MAG, 'text', tag))))


def magnetometer():
    """U3701 MMC5983MA on its own sheet, I2C3 (D-2Nov.11)."""
    mag_library()
    sheet_uuid = K.ident('Croi2.kicad_sch', 'sheet', MAG)
    inst = f'/{ROOT_UUID}/{sheet_uuid}'
    t = K.new_sheet('Magnetometer / MMC5983MA / I2C3', file_id=MAG)
    for lib_id, src in (('Device:R', 'Device'), ('Device:C', 'Device'), ('power:PWR_FLAG', 'power'), ('Ogma2:MMC5983MA', 'Ogma2')):
        K.import_lib(t, lib_id, LIB / f'{src}.kicad_sym')
    S, g = MAG, (lambda *n: [K.add(t, x) for x in n])
    sym = lambda *a, **k: K.make_symbol(t, *a, sheet=S, inst=inst, **k)

    text(t, 'MAGNETOMETER / MMC5983MA / I2C3', (15.24, 15.24), 2.54, 'title')
    text(t, 'What this does: Measures the magnetic field for heading and roll, read at 100 Hz and logged. Non-essential:\n'
            'it never gates the watchdog or the estimator (D-2Nov.11).\n'
            'Connects to: FLIGHT_3V3 through R3701 -> MAG_3V3; I2C3 (PA8 MAG_SCL, PC9 MAG_SDA) and MAG_INT (PE6) on 02-flight-mcu.',
         (15.24, 27.94), 1.4, 'what', 'left top')
    text(t, '1  SUPPLY LINK', (15.24, 52.07), 1.524, 's1')
    text(t, '2  SENSOR, I2C3 AND DATA READY', (15.24, 88.9), 1.524, 's2')

    # Supply link: FLIGHT_3V3 -> R3701 22R -> MAG_3V3.
    r = sym('Device:R', 'R3701', (50.8, 68.58), 90, '22R', R0603,
            extra={'Implementation_Note': 'Magnetometer supply link, 22 ohm not 47: VDD minimum is 2.8 V and the SET/RESET pulses come through it (D-2Nov.11)'},
            ref_at=(50.8, 63.5), val_at=(50.8, 66.04), field_angle=90, justify=None)
    assert r['1'][:2] == (46.99, 68.58) and r['2'][:2] == (54.61, 68.58), r
    sym('power:PWR_FLAG', '#FLG021', (66.04, 68.58), 0, 'PWR_FLAG', '',
        extra={'Implementation_Note': 'ERC source path through the 22 ohm link from FLIGHT_3V3. Not a qualification claim.'},
        ref_at=(66.04, 60.96), val_at=(66.04, 63.5), justify=None)
    g(K.global_label('FLIGHT_3V3', (40.64, 68.58), 0, S, 'link'), K.global_label('MAG_3V3', (78.74, 68.58), 180, S, 'link'),
      K.junction((66.04, 68.58), S, 'link'))
    K.path(t, [(40.64, 68.58), (46.99, 68.58)], S, 'link.in')
    K.path(t, [(54.61, 68.58), (66.04, 68.58), (78.74, 68.58)], S, 'link.out')

    # I2C damping and pull-ups, drawn apart from the sensor and joined by labels.
    for i, (bus, y, rs, rp) in enumerate((('SCL', 116.84, 'R3704', 'R3702'), ('SDA', 139.7, 'R3705', 'R3703'))):
        r = sym('Device:R', rs, (67.31, y), 90, '22R', R0603, extra={'Implementation_Note': f'I2C3 {bus} damping (D-2Nov.11)'},
                ref_at=(67.31, y - 5.08), val_at=(67.31, y - 2.54), field_angle=90, justify=None)
        assert r['1'][:2] == (63.5, y) and r['2'][:2] == (71.12, y), r
        p = sym('Device:R', rp, (55.88, y - 7.62), 0, '2.7k', R0603, extra={'Implementation_Note': f'I2C3 {bus} pull-up to FLIGHT_3V3 (D-2Nov.11)'})
        assert p['2'][:2] == (55.88, y - 3.81), p
        g(K.global_label(f'MAG_{bus}', (40.64, y), 0, S, bus), K.global_label(f'MAG_{bus}_DAMP', (78.74, y), 180, S, bus),
          K.global_label('FLIGHT_3V3', (50.8, y - 15.24), 0, S, bus), K.junction((55.88, y), S, bus))
        K.path(t, [(40.64, y), (55.88, y), (63.5, y)], S, f'{bus}.mcu')
        K.path(t, [(71.12, y), (78.74, y)], S, f'{bus}.dev')
        K.path(t, [(55.88, y - 3.81), (55.88, y)], S, f'{bus}.pu')
        K.path(t, [(55.88, y - 11.43), (55.88, y - 15.24), (50.8, y - 15.24)], S, f'{bus}.top')

    # The sensor.
    u = sym('Ogma2:MMC5983MA', 'U3701', (157.48, 127), 0, 'MMC5983MA', 'Ogma2:MMC5983MA',
            extra={'MPN': 'MMC5983MA', 'Manufacturer': 'MEMSIC', 'Library_Check': FP_CHECK,
                   'Implementation_Note': 'Top end of the board, away from power entry, outputs and GNSS (layout guide C09a)'},
            ref_at=(147.32, 111.76), val_at=(147.32, 114.3))
    for pin, label in (('1', 'MAG_SCL_DAMP'), ('16', 'MAG_SDA_DAMP'), ('15', 'MAG_INT'), ('4', 'MAG_3V3')):
        x, y, _ = u[pin]
        K.path(t, [(x, y), (x - 5.08, y)], S, f'u.{pin}')
        g(K.global_label(label, (x - 5.08, y), 0, S, f'u.{pin}'))
    for pin in ('5', '3', '6', '7', '8', '12', '14'):
        g(K.no_connect(u[pin][:2], S, f'u.{pin}'))
    # VDD, CAP and VDDIO step out to the MAG_3V3 rail; the four capacitors hang from it.
    for pin, x in (('2', 177.8), ('10', 182.88), ('13', 187.96)):
        px, py, _ = u[pin]
        K.path(t, [(px, py), (x, py), (x, 106.68)], S, f'u.{pin}')
    rail = [177.8, 182.88, 187.96, 195.58, 213.36, 231.14, 248.92, 256.54]
    K.path(t, [(x, 106.68) for x in rail], S, 'rail')
    caps = (('C3701', 195.58, '10u 16V X7R', C1206, 'SET/RESET reservoir at CAP (pin 10), low ESR; >=10 uF asked, X7R at 16 V keeps most of it at 3.3 V'),
            ('C3702', 213.36, '1u 16V X7R', C0603, 'At VDD (pin 2)'),
            ('C3703', 231.14, '100n 16V X7R', C0603, 'At VDD (pin 2)'),
            ('C3704', 248.92, '100n 16V X7R', C0603, 'At VDDIO (pin 13)'))
    for ref, x, value, fp, note in caps:
        c = sym('Device:C', ref, (x, 114.3), 0, value, fp, extra={'Implementation_Note': note})
        assert c['1'][:2] == (x, 110.49), c
        K.path(t, [(x, 106.68), (x, 110.49)], S, f'{ref}.t')
        K.path(t, [(x, 118.11), (x, 121.92)], S, f'{ref}.b')
    K.path(t, [(195.58, 121.92), (213.36, 121.92), (231.14, 121.92), (248.92, 121.92), (256.54, 121.92)], S, 'capgnd')
    g(K.global_label('MAG_3V3', (256.54, 106.68), 180, S, 'rail'), K.global_label('GND', (256.54, 121.92), 180, S, 'capgnd'),
      *(K.junction((x, 106.68), S, 'rail') for x in rail[1:-1]),
      *(K.junction((x, 121.92), S, 'capgnd') for x in (213.36, 231.14, 248.92)))
    # Ground pads.
    (x9, y9, _), (x11, y11, _) = u['9'], u['11']
    K.path(t, [(x9, y9), (177.8, y9), (177.8, y11)], S, 'gnd9')
    K.path(t, [(x11, y11), (177.8, y11), (177.8, 142.24), (182.88, 142.24)], S, 'gnd11')
    g(K.global_label('GND', (182.88, 142.24), 180, S, 'gnd'), K.junction((177.8, y11), S, 'gnd'))

    text(t, '22 ohm link, not 47: VDD\'s minimum is 2.8 V and the SET/RESET pulses come through the link (D-2Nov.11).\n'
            'C3701 is the SET/RESET reservoir, at CAP (pin 10); C3702 / C3703 at VDD (pin 2); C3704 at VDDIO (pin 13).\n'
            'I2C only: SPI_CS tied to VDDIO; SDO and the NC pads unconnected. Address 0x30. Pull-ups go to FLIGHT_3V3.',
         (15.24, 165.1), 1.15, 'n1')
    text(t, 'Placement: layout guide C09a. Footprint: KiCad\'s MEMSIC LGA-16 3 x 3 mm pattern (made from the MMC5883MA\n'
            'drawing); check its pads against the MMC5983MA drawing before layout.', (15.24, 182.88), 1.05, 'n2')
    K.save(t, BOARD / MAG)

    # The root sheet gets a sheet symbol in the next free slot, page 45.
    root = K.load(BOARD / 'Croi2.kicad_sch')
    tmpl = [s for s in K.children(root, 'sheet') if any(q[1] == 'Sheetfile' and q[2] == '44-master-enable.kicad_sch'
                                                         for q in K.children(s, 'property'))][0]
    new = K.copy.deepcopy(tmpl)
    K.first(new, 'at')[1:3] = [K.num(353.06), K.num(346.71)]
    K.first(new, 'uuid')[1] = sheet_uuid
    for q in K.children(new, 'property'):
        q[2] = {'Sheetname': '03mag-magnetometer', 'Sheetfile': MAG}[q[1]]
        a = K.first(q, 'at')
        a[1] = K.num(float(a[1]) + 353.06 - 241.3)
    for pg in K.walk(new, 'page'):
        pg[1] = '45'
    K.add(root, new)
    label = [x for x in K.children(root, 'text') if x[1].startswith('P44  ')][0]
    lab = K.copy.deepcopy(label)
    lab[1] = 'P45  Magnetometer / MMC5983MA / I2C3'
    a = K.first(lab, 'at')
    a[1] = K.num(float(a[1]) + 353.06 - 241.3)
    K.first(lab, 'uuid')[1] = K.ident('Croi2.kicad_sch', 'text', 'P45')
    K.add(root, lab)
    K.save(root, BOARD / 'Croi2.kicad_sch')


def build():
    out = {sheet: sensor_sheet(sheet, *spec) for sheet, spec in SHEETS.items()}
    magnetometer()
    return out


if __name__ == '__main__':
    for sheet, r in build().items():
        print(sheet, 'caps', r['caps'], 'pull-ups', r['pulls'], 'renamed', r['renamed'])
