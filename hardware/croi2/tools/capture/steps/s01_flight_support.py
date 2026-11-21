"""Step 1, sheet 02a-flight-support: VBAT feed, reset memory, timing strobe and spare pads.

Capture specification rows: Flight VBAT (D-6.4); Timing strobe, Reset memory, Spare pads (D-19Nov.3).
Edits the sheet in place (run from a clean checkout). Also vendors KiCad 9.0.7's Device:D_Schottky
into libraries/Device.kicad_sym, so the embedded copy matches the project library.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
SHEET = '02a-flight-support.kicad_sch'
LIB = BOARD / 'libraries'

# Parts. MPNs only where the part matters; generic passives follow the sheet's value-string style.
SCHOTTKY = dict(value='BAT54T1G', mpn='BAT54T1G', mfr='onsemi')            # SOD-123; JLC C152458, stocked 21 Nov
SOD123 = 'Diode_SMD:D_SOD-123'
R0603, C0603, C1206 = 'Resistor_SMD:R_0603_1608Metric', 'Capacitor_SMD:C_0603_1608Metric', 'Capacitor_SMD:C_1206_3216Metric'
PAD = 'TestPoint:TestPoint_Pad_D1.0mm'

TEXT = {
    'What this does: Gives the flight MCU stable local supplies and its two clock sources.':
        'What this does: Gives the flight MCU stable local supplies, its two clock sources, the backup-domain feed,\n'
        'the watchdog-reset memory, the timing strobe and the spare test pads.',
    'Connects to: FLIGHT_3V3 -> U201 on 02-flight-mcu.':
        'Connects to: FLIGHT_3V3 -> U201 on 02-flight-mcu; FLIGHT_MR_N from the watchdog on 02flight-reset-debug.',
}


def g(t, *nodes):
    for n in nodes:
        K.add(t, n)


def build():
    K.vendor_symbol(LIB / 'Device.kicad_sym', 'D_Schottky', f'{K.KICAD_SYMBOLS}/Device.kicad_sym')
    t = K.load(BOARD / SHEET)
    K.import_lib(t, 'Device:D_Schottky', LIB / 'Device.kicad_sym')
    K.import_lib(t, 'Connector:TestPoint', LIB / 'Connector.kicad_sym')
    S = SHEET

    # ---- C207 (100 nF at VBAT pad 6) leaves the FLIGHT_3V3 row for FLIGHT_VBAT.
    p = K.pin_positions(t, 'C207')
    stubs = [(w, a, b) for w, a, b in K.wires(t) if p['1'][:2] in (a, b) or p['2'][:2] in (a, b)]
    assert len(stubs) == 2, stubs
    taps = [a if b in (p['1'][:2], p['2'][:2]) else b for _, a, b in stubs]
    for tap in taps:
        segs = [(w, a, b) for w, a, b in K.wires(t) if tap in (a, b) and all(w is not s[0] for s in stubs)]
        assert len(segs) == 2 and all(a[1] == b[1] == tap[1] for _, a, b in segs), (tap, segs)
        ends = sorted(a if b == tap else b for _, a, b in segs)
        K.remove(t, lambda x: any(x is s[0] for s in segs))
        assert K.remove(t, lambda x: x[0] == 'junction' and K.xy(x) == tap) == 1, tap
        K.add(t, K.wire(ends[0], ends[1], S, 'rail-merge'))
    K.remove(t, lambda x: any(x is s[0] for s in stubs))
    K.move_symbol(K.symbols(t)['C207'], (190.5, 132.08))

    # ---- A. FLIGHT_VBAT: FLIGHT_3V3 -> D201 -> pad 6, with C207 and C219 hold-up (D-6.4).
    g(t, K.text('FLIGHT_VBAT / BACKUP-DOMAIN FEED', (149.86, 111.76), S, 'tA', 1.524))
    d = K.make_symbol(t, 'Device:D_Schottky', 'D201', (166.37, 124.46), 180, SCHOTTKY['value'], SOD123, S,
                      extra={'MPN': SCHOTTKY['mpn'], 'Manufacturer': SCHOTTKY['mfr'],
                             'Implementation_Note': 'VBAT feed from FLIGHT_3V3 (D-6.4); place at pad 6 with C207 and C219'},
                      ref_at=(166.37, 120.65), val_at=(166.37, 128.27), justify=None)
    assert d['2'][:2] == (162.56, 124.46) and d['1'][:2] == (170.18, 124.46), d
    c = K.make_symbol(t, 'Device:C', 'C219', (210.82, 132.08), 0, '100u 6.3V X5R', C1206, S,
                      extra={'Implementation_Note': 'VBAT hold-up beside C207 at pad 6 (D-6.4)'})
    assert c['1'][:2] == (210.82, 128.27)
    g(t, K.global_label('FLIGHT_3V3', (157.48, 124.46), 0, S, 'A'),
         K.global_label('FLIGHT_VBAT', (226.06, 124.46), 180, S, 'A'),
         K.global_label('GND', (182.88, 140.97), 0, S, 'A'))
    K.path(t, [(157.48, 124.46), (162.56, 124.46)], S, 'A.in')
    K.path(t, [(170.18, 124.46), (190.5, 124.46), (210.82, 124.46), (218.44, 124.46), (226.06, 124.46)], S, 'A.rail')
    for x in (190.5, 210.82):
        K.path(t, [(x, 124.46), (x, 128.27)], S, f'A.top{x}')
        K.path(t, [(x, 135.89), (x, 140.97)], S, f'A.bot{x}')
    K.path(t, [(182.88, 140.97), (190.5, 140.97), (210.82, 140.97)], S, 'A.gnd')
    K.clone_symbol(t, '#FLG009', '#FLG020', (218.44, 124.46), S,
                   {'Implementation_Note': 'ERC source path through D201 from FLIGHT_3V3. Not a qualification claim.'})
    g(t, *(K.junction(j, S, 'A') for j in ((190.5, 124.46), (210.82, 124.46), (218.44, 124.46), (190.5, 140.97))))
    g(t, K.text('BAT54-class Schottky, so VBAT never back-feeds FLIGHT_3V3. C219 holds the backup domain\n'
                '(RTC, backup registers) through supply dips (D-6.4).', (149.86, 148.59), S, 'nA', 1.016))

    # ---- C. RESET_MEMORY on PA3 (D-19Nov.3).
    g(t, K.text('RESET_MEMORY / WATCHDOG-RESET MEMORY', (149.86, 160.02), S, 'tC', 1.524))
    r = K.make_symbol(t, 'Device:R', 'R202', (175.26, 175.26), 0, '470k', R0603, S,
                      extra={'Implementation_Note': 'Recharge, ~1 s with C220 (D-19Nov.3); value set on the bench'})
    assert r['1'][:2] == (175.26, 171.45) and r['2'][:2] == (175.26, 179.07), r
    K.make_symbol(t, 'Device:C', 'C220', (187.96, 190.5), 0, '2.2u 10V X7R', C0603, S,
                  extra={'Implementation_Note': 'Reset memory (D-19Nov.3)'})
    d = K.make_symbol(t, 'Device:D_Schottky', 'D202', (210.82, 190.5), 90, SCHOTTKY['value'], SOD123, S,
                      extra={'MPN': SCHOTTKY['mpn'], 'Manufacturer': SCHOTTKY['mfr'],
                             'Implementation_Note': 'Reset memory discharge, anode at the node (D-19Nov.3)'},
                      ref_at=(216.535, 189.23), val_at=(216.535, 191.77), field_angle=90, justify=None)
    assert d['2'][:2] == (210.82, 186.69) and d['1'][:2] == (210.82, 194.31), d
    K.make_symbol(t, 'Device:R', 'R204', (210.82, 201.93), 0, '1k', R0603, S,
                  extra={'Implementation_Note': 'Limits the watchdog output sink current (D-19Nov.3)'})
    K.make_symbol(t, 'Connector:TestPoint', 'TP205', (223.52, 182.88), 0, 'RESET_MEMORY', PAD, S,
                  ref_at=(227.33, 179.07), val_at=(227.33, 179.07), hide_value=True)
    g(t, K.global_label('FLIGHT_3V3', (162.56, 167.64), 0, S, 'C'),
         K.global_label('RESET_MEMORY', (233.68, 182.88), 180, S, 'C'),
         K.global_label('GND', (182.88, 198.12), 0, S, 'C'),
         K.global_label('FLIGHT_MR_N', (215.9, 209.55), 180, S, 'C'))
    K.path(t, [(162.56, 167.64), (175.26, 167.64), (175.26, 171.45)], S, 'C.3v3')
    K.path(t, [(175.26, 179.07), (175.26, 182.88), (187.96, 182.88), (210.82, 182.88), (223.52, 182.88), (233.68, 182.88)], S, 'C.node')
    K.path(t, [(187.96, 182.88), (187.96, 186.69)], S, 'C.c1')
    K.path(t, [(182.88, 198.12), (187.96, 198.12), (187.96, 194.31)], S, 'C.c2')
    K.path(t, [(210.82, 182.88), (210.82, 186.69)], S, 'C.d1')
    K.path(t, [(210.82, 194.31), (210.82, 198.12)], S, 'C.d2')
    K.path(t, [(210.82, 205.74), (210.82, 209.55), (215.9, 209.55)], S, 'C.mr')
    g(t, *(K.junction(j, S, 'C') for j in ((187.96, 182.88), (210.82, 182.88), (223.52, 182.88))))
    g(t, K.text('A watchdog reset (FLIGHT_MR_N low) empties C220 through D202 and R204 in a few ms; R202 refills it\n'
                'in about a second, so PA3 reads low just after a watchdog reset. Values confirmed on the bench (D-19Nov.3).',
                (149.86, 215.9), S, 'nC', 1.016))

    # ---- B. Timing strobe and spare pads (D-19Nov.3).
    g(t, K.text('TEST PADS / TIMING STROBE AND SPARE PADS', (149.86, 228.6), S, 'tB', 1.524))
    r = K.make_symbol(t, 'Device:R', 'R203', (166.37, 240.03), 90, '330R', R0603, S,
                      extra={'Implementation_Note': 'Strobe series resistor: a probe or short at TP201 cannot load PB0 (D-19Nov.3)'},
                      ref_at=(166.37, 234.95), val_at=(166.37, 237.49), field_angle=90, justify=None)
    assert r['1'][:2] == (162.56, 240.03) and r['2'][:2] == (170.18, 240.03), r
    K.make_symbol(t, 'Device:R', 'R205', (177.8, 247.65), 0, '100k', R0603, S,
                  extra={'Implementation_Note': 'Holds the strobe pad low at reset (D-19Nov.3)'})
    K.make_symbol(t, 'Connector:TestPoint', 'TP201', (200.66, 240.03), 0, 'TP_STROBE', PAD, S,
                  ref_at=(204.47, 236.22), val_at=(204.47, 236.22), hide_value=True)
    g(t, K.global_label('TP_STROBE', (157.48, 240.03), 0, S, 'B'),
         K.global_label('GND', (172.72, 255.27), 0, S, 'B'),
         K.local_label('TP_STROBE_PAD', (180.34, 240.03), 0, S, 'B'))
    K.path(t, [(157.48, 240.03), (162.56, 240.03)], S, 'B.in')
    K.path(t, [(170.18, 240.03), (177.8, 240.03), (180.34, 240.03), (200.66, 240.03)], S, 'B.pad')
    K.path(t, [(177.8, 240.03), (177.8, 243.84)], S, 'B.pd1')
    K.path(t, [(177.8, 251.46), (177.8, 255.27), (172.72, 255.27)], S, 'B.pd2')
    g(t, K.junction((177.8, 240.03), S, 'B'))
    for i, (net, ref, x) in enumerate((('TP_PC6', 'TP202', 165.1), ('TP_PC7', 'TP203', 195.58), ('TP_PD10', 'TP204', 226.06))):
        K.make_symbol(t, 'Connector:TestPoint', ref, (x, 270.51), 0, net, PAD, S,
                      ref_at=(x + 3.81, 266.7), val_at=(x + 3.81, 266.7), hide_value=True)
        g(t, K.global_label(net, (x - 7.62, 270.51), 0, S, 'B'))
        K.path(t, [(x - 7.62, 270.51), (x, 270.51)], S, f'B.{net}')
    g(t, K.text('PB0 strobe to TP201 through R203; R205 holds it low at reset. PC6, PC7 and PD10 are spare pads:\n'
                'inputs with pull-downs in firmware. PC7 never drives: it neighbours PC8, channel 2\'s low side (D-19Nov.3).',
                (149.86, 279.4), S, 'nB', 1.016))

    for node in K.children(t, 'text'):
        for old, new in TEXT.items():
            if old in node[1]:
                node[1] = node[1].replace(old, new)
    K.save(t, BOARD / SHEET)


if __name__ == '__main__':
    build()
    print('written:', BOARD / SHEET)
