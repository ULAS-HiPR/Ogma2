"""Step 9: capture the nine calls decided after close-out (D-21Nov.12 to D-21Nov.20).

- D-21Nov.12 arm connectors: J6101 Molex Mini-Fit Jr. 39281023, J6102 JST B2P-VH (KiCad footprints).
- D-21Nov.14 USB_CONFIG_OK dropped: R1206, R4404 and R4304 go; U4303 channel 4 input (B4, pin 10) tied
  to GND like its unused channel 3, its output (A4, pin 5) and comms PA1 no-connect; PA1 unused in the
  as-captured comms map.
- D-21Nov.15 the doubled pull-ups go: R3106, R3206, R3306, R3407, R3408, R3507, R3508.
- D-21Nov.16 U3104 becomes the LSM6DSV32X (same LGA-14L and pin table, ST DS LSM6DSV32X Table 2).
- D-21Nov.17 bulk capacitors: 47 uF Murata X6S x8, C4613 Taiyo Yuden X5R 16 V, C4504 Samsung X7R 0805.
- D-21Nov.18 R1701 / R1801 / R1901 32k 0.1%, R1103 75k 0.1%.
- D-21Nov.20 (amended at capture) sounder: BZ9001 PUI Audio SMT-1028-T-2-R, Q9001 AO3400A; R9005, the piezo's
  bleed resistor, goes. D9002, the 1N4148W already across the sounder, is the coil's flyback diode.
Edits the sheets in place (run from a clean checkout); vendors KiCad 9.0.7 footprints.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
NEW_LIBS = ('Connector_Molex', 'Buzzer_Beeper')

PROPS = {  # sheet: {ref: {field: value}}
    '06a-arm-boundary.kicad_sch': {
        'J6101': {'Value': '39281023', 'Footprint': 'Connector_Molex:Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical',
                  'MPN': '39281023', 'Manufacturer': 'Molex',
                  'Implementation_Note': 'Recovery arm switch: Mini-Fit Jr. 2-circuit vertical, 4.2 mm, 9 A, positive latch (D-21Nov.12). '
                                         "Can't take J6102's VH plug, J701's Micro-Fit, the GH loops or J101's Nano-Fit"},
        'J6102': {'Value': 'B2P-VH(LF)(SN)', 'Footprint': 'Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical',
                  'MPN': 'B2P-VH(LF)(SN)', 'Manufacturer': 'JST',
                  'Implementation_Note': 'Staging arm switch: JST VH 2-pin vertical, 3.96 mm, 10 A, locking (D-21Nov.12). '
                                         "Can't take J6101's Mini-Fit plug, J701's Micro-Fit, the GH loops or J101's Nano-Fit"}},
    '03st-sensor.kicad_sch': {
        'U3104': {'Value': 'LSM6DSV32XTR', 'MPN': 'LSM6DSV32XTR', 'Datasheet': 'https://www.st.com/resource/en/datasheet/lsm6dsv32x.pdf',
                  'Library_Check': 'LSM6DSV32X (D-21Nov.16): LGA-14L 2.5 x 3.0 mm and Table 2 pin functions match the LSM6DSV16X '
                                   'symbol and footprint kept here (ST LSM6DSV32X datasheet); +-4/8/16/32 g'}},
    '01c-preregulator.kicad_sch': {r: {} for r in ('C1305', 'C1306')},
    '01flight-ldo.kicad_sch': {'C1705': {}, 'C1706': {}, 'R1701': {'Value': '32k 0.1%'}},
    '01comms-ldo.kicad_sch': {'C1805': {}, 'C1806': {}, 'R1801': {'Value': '32k 0.1%'}},
    '01optional-ldo.kicad_sch': {'C1905': {}, 'C1906': {}, 'R1901': {'Value': '32k 0.1%'}},
    '01a-source-mux.kicad_sch': {'R1103': {'Value': '75k 0.1%'}},
    '04f-radio-module.kicad_sch': {'C4613': {'Value': '100u 16V X5R', 'MPN': 'EMK325ABJ107MM-P', 'Manufacturer': 'Taiyo Yuden'}},
    '04d-gnss.kicad_sch': {'C4504': {'Value': '10u 16V X7R', 'Footprint': 'Capacitor_SMD:C_0805_2012Metric',
                                     'MPN': 'CL21B106KOQNNNE', 'Manufacturer': 'Samsung Electro-Mechanics'}},
    '09-indicators.kicad_sch': {
        'BZ9001': {'Value': 'SMT-1028-T-2-R', 'Footprint': 'Buzzer_Beeper:MagneticBuzzer_PUI_SMT-1028-T-2-R',
                   'MPN': 'SMT-1028-T-2-R', 'Manufacturer': 'PUI Audio',
                   'Datasheet': 'https://api.puiaudio.com/filename/SMT-1028-T-2-R.pdf',
                   'Implementation_Note': 'Magnetic transducer, 90 dBA at 10 cm at 3.6 Vpp, 2.83 kHz (KiCad footprint data); '
                                          'pad 1 is +; D9002 is its flyback diode (D-21Nov.20, B-07)'},
        'Q9001': {'Value': 'AO3400A', 'MPN': 'AO3400A', 'Manufacturer': 'Alpha & Omega Semiconductor',
                  'Datasheet': 'http://www.aosmd.com/pdfs/datasheet/AO3400A.pdf',
                  'Library_Check': 'AO3400A (D-21Nov.20): KiCad draws it and the 2N7002 symbol kept here from the same '
                                   'Q_NMOS_GSD base, SOT-23 gate 1, source 2, drain 3',
                  'Implementation_Note': 'Logic-level low-side switch for the sounder coil (D-21Nov.20)'}},
}
X6S = {'Value': '47u 16V X6S', 'MPN': 'GRM32EC81C476KE15L', 'Manufacturer': 'Murata'}
for sheet in ('01c-preregulator.kicad_sch', '01flight-ldo.kicad_sch', '01comms-ldo.kicad_sch', '01optional-ldo.kicad_sch'):
    for ref, kv in PROPS[sheet].items():
        if ref.startswith('C'):
            kv.update(X6S)

REMOVE = {'03st-sensor.kicad_sch': ['R3106'], '03tdk-sensor.kicad_sch': ['R3206'], '03hg-sensor.kicad_sch': ['R3306'],
          '03bmp-pressure.kicad_sch': ['R3407', 'R3408'], '03te-pressure.kicad_sch': ['R3507', 'R3508'],
          '01b-bootstrap.kicad_sch': ['R1206'], '04c-usb-service.kicad_sch': ['R4404'], '04b-uart-boundary.kicad_sch': ['R4304'],
          '09-indicators.kicad_sch': ['R9005']}

LDO_NOTE = ('3.352 V nominal; calculated corners 3.310-3.394 V.', '3.360 V nominal; calculated corners 3.318-3.402 V (D-21Nov.18).')
TEXT = {
    '01flight-ldo.kicad_sch': [LDO_NOTE], '01comms-ldo.kicad_sch': [LDO_NOTE], '01optional-ldo.kicad_sch': [LDO_NOTE],
    '03st-sensor.kicad_sch': [('ST / LSM6DSV16XTR', 'ST / LSM6DSV32XTR')],
    'Croi2.kicad_sch': [('P16  ST / LSM6DSV16XTR', 'P16  ST / LSM6DSV32XTR')],
    '04b-uart-boundary.kicad_sch': [
        ('POWER STATUS: two indications out, USB configuration permission back.',
         'POWER STATUS: two indications out. Channel 4 is unused: USB_CONFIG_OK is dropped (D-21Nov.14).'),
        ('Includes the flight-requested comms reset, battery-valid status and USB permission, not just UART data.',
         'Includes the flight-requested comms reset, battery-valid and USB-present status, not just UART data.')],
    '04c-usb-service.kicad_sch': [('\nUSB_CONFIG_OK keeps only its R4404 pull-down on this sheet.', '')],
    '09-indicators.kicad_sch': [('Flight PD6 -> passive piezo.', 'Flight PD6 -> magnetic sounder (D-21Nov.20).')],
    '06a-arm-boundary.kicad_sch': [
        ('J6101 / J6102: 2-contact connectors to the external arm switches, placeholders until the part is chosen.\n'
         'Neither may mate Churro J701 (Micro-Fit 430450200), the GH enable loops or each other.',
         'J6101: Molex Mini-Fit Jr. 39281023 (4.2 mm, 9 A); J6102: JST VH B2P-VH (3.96 mm, 10 A) (D-21Nov.12).\n'
         "Two families: neither takes the other's plug, Churro J701's Micro-Fit, the GH enable loops or J101's Nano-Fit."),
        ('OPEN: the J6101 / J6102 connector parts and the arm switches; F6101 / F6102 breaking capacity against the pack.',
         'OPEN: the arm switches; F6101 / F6102 breaking capacity against the pack.')],
}


TITLES = {'03st-sensor.kicad_sch': ('ST / LSM6DSV16XTR', 'ST / LSM6DSV32XTR')}
PRO_COMMENT = ('LSM6DSV16X aux pin', 'LSM6DSV32X aux pin')        # the two U3104 ERC exclusion notes


def set_props(sym, kv):
    pr = {p[1]: p for p in K.children(sym, 'property')}
    for k, v in kv.items():
        if k in pr:
            pr[k][2] = v
        else:
            i = next(i for i, x in enumerate(sym) if isinstance(x, list) and x and x[0] == 'instances')
            sym.insert(i, K.prop(k, v, K.xy(sym)))


def retext(t, pairs):
    for old, new in pairs:
        hits = [n for n in K.children(t, 'text') if old in n[1]]
        assert len(hits) == 1, (old[:50], len(hits))
        hits[0][1] = hits[0][1].replace(old, new)


def libraries():
    for name in NEW_LIBS:
        (LIB / f'{name}.pretty').mkdir(exist_ok=True)
    table = BOARD / 'fp-lib-table'
    t = K.load(table)
    have = {K.first(l, 'name')[1] for l in K.children(t, 'lib')}
    for name in NEW_LIBS:
        if name not in have:
            t.append(K.el('lib', K.el('name', name), K.el('type', 'KiCad'), K.el('uri', f'${{KIPRJMOD}}/libraries/{name}.pretty'),
                          K.el('options', ''), K.el('descr', 'KiCad 9.0.7 footprints added during capture')))
    K.save(t, table)
    for lib, fp in (('Connector_Molex', 'Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical'),
                    ('Connector_JST', 'JST_VH_B2P-VH_1x02_P3.96mm_Vertical'),
                    ('Buzzer_Beeper', 'MagneticBuzzer_PUI_SMT-1028-T-2-R'),
                    ('Capacitor_SMD', 'C_0805_2012Metric')):
        K.vendor_footprint(LIB, lib, fp)


def usb_config_ok(log):
    """D-21Nov.14: B4 input to GND (as channel 3's A3 is), A4 output and comms PA1 no-connect."""
    S = '04b-uart-boundary.kicad_sch'
    t = K.load(BOARD / S)
    pins = K.pin_positions(t, 'U4303')
    pts, _ = K.connected_points(t, pins['10'][:2])
    labs = K.labels_at(t, pts)
    assert [l[1] for l in labs] == ['CC_USB_CONFIG_OK'], labs
    labs[0][1] = 'GND'
    log['U4303.5'] = K.strip_branch(t, pins['5'][:2], 'U4303')
    K.add(t, K.no_connect(pins['5'][:2], S, 'u4303.5'))
    K.save(t, BOARD / S)
    S = '04-comms-gnss-radio.kicad_sch'
    t = K.load(BOARD / S)
    at = K.pin_positions(t, 'U401')['15'][:2]
    log['U401.15'] = K.strip_branch(t, at, 'U401')
    K.add(t, K.no_connect(at, S, 'u401.15'))
    K.save(t, BOARD / S)


COMMS_PA1 = ('"comms","STM32H563RIT6","15","PA1","CC_USB_CONFIG_OK","GPIO","","External pulldown"',
             '"comms","STM32H563RIT6","15","PA1","NC","ANALOG","","Unused: USB_CONFIG_OK dropped (D-21Nov.14); no-connect, safe low or analog"')


def pin_map():
    """D-21Nov.14 in the as-captured comms map (step 8b's file): PA1 unused. Safe to rerun."""
    p = LIB / 'inputs/comms-pinout.csv'
    s = p.read_text()
    assert s.count(COMMS_PA1[0]) + s.count(COMMS_PA1[1]) == 1
    p.write_text(s.replace(*COMMS_PA1))


def retitle():
    for sheet, (old, new) in TITLES.items():
        t = K.load(BOARD / sheet)
        title = K.first(K.first(t, 'title_block'), 'title')
        assert title[1] == old, title
        title[1] = new
        K.save(t, BOARD / sheet)
    pro = BOARD / 'Croi2.kicad_pro'
    s = pro.read_text()
    assert s.count(PRO_COMMENT[0]) == 2
    pro.write_text(s.replace(*PRO_COMMENT))


def build():
    log = {}
    libraries()
    for sheet, refs in REMOVE.items():
        t = K.load(BOARD / sheet)
        for r in refs:
            log[r] = K.remove_part(t, r)
        K.save(t, BOARD / sheet)
    usb_config_ok(log)
    pin_map()
    for sheet, refs in PROPS.items():
        t = K.load(BOARD / sheet)
        for r, kv in refs.items():
            set_props(K.symbols(t)[r], kv)
        retext(t, TEXT.get(sheet, []))
        K.save(t, BOARD / sheet)
    for sheet in set(TEXT) - set(PROPS):
        t = K.load(BOARD / sheet)
        retext(t, TEXT[sheet])
        K.save(t, BOARD / sheet)
    retitle()
    return log


if __name__ == '__main__':
    for ref, items in build().items():
        print(ref, len(items))
