"""Step 2, sheet 01-power: auto-retry, the enable hold, the energy tap and J102.8.

Capture specification rows: U101 fault mode (D-6.3); Enable hold (D-6.3, D-2Nov.4, D-2Nov.18);
Energy tap (D-6.1, D-2Nov.5, D-2Nov.15). The energy-tap rename also touches 07a (R7104, VBUS).
Edits the sheets in place (run from a clean checkout). Vendors KiCad 9.0.7's CP_Elec_6.3x7.7.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
SHEET, MONITOR = '01-power.kicad_sch', '07a-battery-monitor.kicad_sch'

SCHOTTKY = dict(value='BAT54T1G', mpn='BAT54T1G', mfr='onsemi')            # as step 1; JLC C152458
HOLD_CAP = dict(value='470u 6.3V Al', mpn='EEEFKJ471XSP', mfr='Panasonic')  # FK, 6.3 x 7.7 mm; JLC C401736
SOD123, CP63 = 'Diode_SMD:D_SOD-123', 'Capacitor_SMD:CP_Elec_6.3x7.7'
R0603, C0603, C1206 = 'Resistor_SMD:R_0603_1608Metric', 'Capacitor_SMD:C_0603_1608Metric', 'Capacitor_SMD:C_1206_3216Metric'

TEXT = {
    SHEET: {
        'SOURCE ENTRY -> REVERSE BLOCKING -> LATCH-OFF EFUSE -> SHUNT ON BATTERY MONITOR SHEET':
            'SOURCE ENTRY -> REVERSE BLOCKING -> ENERGY_TAP -> AUTO-RETRY EFUSE -> SHUNT ON BATTERY MONITOR SHEET',
        'What this does: Accepts one 2S battery source, blocks reverse connection and shuts down a faulty input.':
            'What this does: Accepts one 2S battery source, blocks reverse connection, shuts down a faulty input and retries,\n'
            'and holds the battery enable on through a flight-computer reset aloft (FC_POWER_HOLD).',
        'The external switch is on 44-master-enable.':
            'The external switch is on 44-master-enable.\n'
            'ENERGY_TAP (Q101 drain, ahead of the eFuse) -> output arm feeds on 06*, battery-monitor VBUS on 07a.',
    },
    MONITOR: {
        'VBUS measures BAT_EFUSE_IN, upstream of the load shunt.':
            'VBUS measures ENERGY_TAP, upstream of the eFuse and the load shunt.',
    },
}


def g(t, *nodes):
    for n in nodes:
        K.add(t, n)


def rename_labels(t, old, new):
    n = 0
    for lab in K.children(t, 'global_label'):
        if lab[1] == old:
            lab[1] = new
            n += 1
    return n


DONE = set()


def retext(t, sheet):
    for node in K.children(t, 'text'):
        for old, new in TEXT[sheet].items():
            if old in node[1]:
                node[1] = node[1].replace(old, new)
                DONE.add(old)


def build():
    K.vendor_footprint(LIB, 'Capacitor_SMD', 'CP_Elec_6.3x7.7')
    t = K.load(BOARD / SHEET)
    K.import_lib(t, 'Device:D_Schottky', LIB / 'Device.kicad_sym')
    K.import_lib(t, 'Device:C_Polarized', LIB / 'Device.kicad_sym')
    S = SHEET

    # ---- U101 fault mode: MODE pad 11 to GND, auto-retry (D-6.3).
    mode = K.pin_positions(t, 'U101')['11'][:2]
    assert K.remove(t, lambda x: x[0] == 'no_connect' and K.xy(x) == mode) == 1
    K.path(t, [mode, (330.2, 181.61)], S, 'mode')
    g(t, K.global_label('GND', (330.2, 181.61), 180, S, 'mode'))

    # ---- Energy tap: BAT_EFUSE_IN becomes ENERGY_TAP; 100 nF and 10 uF at Q101's drain.
    assert rename_labels(t, 'BAT_EFUSE_IN', 'ENERGY_TAP') == 2
    drain, u_in = K.pin_positions(t, 'Q101')['5'][:2], K.pin_positions(t, 'U101')['1'][:2]
    seg = [w for w, a, b in K.wires(t) if {a, b} == {drain, u_in}]
    assert len(seg) == 1, seg
    K.remove(t, lambda x: x is seg[0])
    K.path(t, [drain, (187.96, 85.09), (208.28, 85.09), u_in], S, 'tap')
    K.make_symbol(t, 'Device:C', 'C1004', (187.96, 92.71), 0, '100n 50V X7R', C0603, S,
                  extra={'Implementation_Note': 'ENERGY_TAP decoupling at Q101 drain (D-2Nov.15)'})
    K.make_symbol(t, 'Device:C', 'C1005', (208.28, 92.71), 0, '10u 16V X7R', C1206, S,
                  extra={'Implementation_Note': 'ENERGY_TAP decoupling at Q101 drain, for pulsed output loads (D-2Nov.15)'})
    for x in (187.96, 208.28):
        K.path(t, [(x, 85.09), (x, 88.9)], S, f'tap.t{x}')
        K.path(t, [(x, 96.52), (x, 100.33)], S, f'tap.b{x}')
    K.path(t, [(182.88, 100.33), (187.96, 100.33), (208.28, 100.33)], S, 'tap.gnd')
    g(t, K.global_label('GND', (182.88, 100.33), 0, S, 'tap'),
         *(K.junction(j, S, 'tap') for j in ((187.96, 85.09), (208.28, 85.09), (187.96, 100.33))))

    # ---- J102.8 becomes CROI_POWER_HOLD (Churro's hold input).
    p8 = K.pin_positions(t, 'J102')['8'][:2]
    assert K.remove(t, lambda x: x[0] == 'no_connect' and K.xy(x) == p8) == 1
    K.path(t, [p8, (67.31, 422.91)], S, 'j102.8')
    g(t, K.global_label('CROI_POWER_HOLD', (67.31, 422.91), 0, S, 'j102'))

    # ---- Enable hold: FC_POWER_HOLD -> R1014 -> C1007 -> D1003 / D1004 (D-6.3, D-2Nov.4, D-2Nov.18).
    g(t, K.text('ENABLE HOLD / FC_POWER_HOLD', (139.7, 368.3), S, 'tH', 1.524))
    r = K.make_symbol(t, 'Device:R', 'R1014', (167.64, 389.89), 90, '330R', R0603, S,
                      extra={'Implementation_Note': 'Enable-hold charge: about 0.5 s into C1007 (D-2Nov.18)'},
                      ref_at=(167.64, 384.81), val_at=(167.64, 387.35), field_angle=90, justify=None)
    assert r['1'][:2] == (163.83, 389.89) and r['2'][:2] == (171.45, 389.89), r
    K.make_symbol(t, 'Device:R', 'R1015', (160.02, 397.51), 0, '1M', R0603, S,
                  extra={'Implementation_Note': 'Holds PE5 low at reset without draining the hold (D-2Nov.18)'})
    c = K.make_symbol(t, 'Device:C_Polarized', 'C1007', (177.8, 397.51), 0, HOLD_CAP['value'], CP63, S,
                      extra={'MPN': HOLD_CAP['mpn'], 'Manufacturer': HOLD_CAP['mfr'],
                             'Implementation_Note': 'Enable hold (D-2Nov.18). Aluminium electrolytic, catalogue leakage <=30 uA: '
                                                    'a polymer part (~300 uA) cuts the hold below the 0.6 s it must cover'})
    assert c['1'][:2] == (177.8, 393.7) and c['2'][:2] == (177.8, 401.32), c
    for ref, y, net, note in (('D1003', 389.89, 'BAT_SHDN_N', 'Enable hold into BAT_SHDN_N (D-6.3)'),
                              ('D1004', 400.05, 'CROI_POWER_HOLD', 'Enable hold to Churro over J102.8 (D-6.3)')):
        d = K.make_symbol(t, 'Device:D_Schottky', ref, (205.74, y), 180, SCHOTTKY['value'], SOD123, S,
                          extra={'MPN': SCHOTTKY['mpn'], 'Manufacturer': SCHOTTKY['mfr'], 'Implementation_Note': note},
                          ref_at=(205.74, y - 3.81), val_at=(205.74, y + 3.81), justify=None)
        assert d['2'][:2] == (201.93, y) and d['1'][:2] == (209.55, y), d
        K.path(t, [(209.55, y), (217.17, y)], S, f'hold.{ref}')
        g(t, K.global_label(net, (217.17, y), 180, S, 'hold'))
    g(t, K.global_label('FC_POWER_HOLD', (154.94, 389.89), 0, S, 'hold'),
         K.global_label('GND', (154.94, 405.13), 0, S, 'hold'),
         K.local_label('POWER_HOLD_RC', (182.88, 389.89), 0, S, 'hold'))
    K.path(t, [(154.94, 389.89), (160.02, 389.89), (163.83, 389.89)], S, 'hold.in')
    K.path(t, [(160.02, 389.89), (160.02, 393.7)], S, 'hold.pd')
    K.path(t, [(171.45, 389.89), (177.8, 389.89), (182.88, 389.89), (198.12, 389.89), (201.93, 389.89)], S, 'hold.rc')
    K.path(t, [(177.8, 389.89), (177.8, 393.7)], S, 'hold.c')
    K.path(t, [(198.12, 389.89), (198.12, 400.05), (201.93, 400.05)], S, 'hold.d2')
    K.path(t, [(154.94, 405.13), (160.02, 405.13), (177.8, 405.13)], S, 'hold.gnd')
    K.path(t, [(160.02, 401.32), (160.02, 405.13)], S, 'hold.pd2')
    K.path(t, [(177.8, 401.32), (177.8, 405.13)], S, 'hold.c2')
    g(t, *(K.junction(j, S, 'hold') for j in ((160.02, 389.89), (177.8, 389.89), (198.12, 389.89), (160.02, 405.13))))
    g(t, K.text('Firmware drives PE5 high after launch detect; R1014 charges C1007 in about 0.5 s. If PE5 lets go\n'
                '(a reset aloft), C1007 keeps BAT_SHDN_N and, through J102.8, Churro\'s AV_SHDN_N above 2 V for\n'
                '>=0.75 s at the worst corner, against the ~0.6 s a restart and re-assert take (D-2Nov.4, D-2Nov.18).\n'
                'R1015 keeps PE5 low at reset. U101 MODE to GND: auto-retry after an overload (D-6.3).',
                (139.7, 416.56), S, 'nH', 1.016))
    retext(t, SHEET)
    K.save(t, BOARD / SHEET)

    m = K.load(BOARD / MONITOR)
    assert rename_labels(m, 'BAT_EFUSE_IN', 'ENERGY_TAP') == 1
    retext(m, MONITOR)
    K.save(m, BOARD / MONITOR)
    missed = [o for s in TEXT.values() for o in s if o not in DONE]
    assert not missed, missed


if __name__ == '__main__':
    build()
    print('written:', BOARD / SHEET, BOARD / MONITOR)
