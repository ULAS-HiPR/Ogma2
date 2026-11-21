"""Step 3, the other power sheets: core enable, limiters, LDO dividers, C1403, service restart, USB limiter.

Capture specification rows: LDO dividers; Comms input limiter; Service input limiter; Service restart;
Hold-up capacitor; Core enable (D-6.5); USB limiter (D-6.5).
Edits the sheets in place (run from a clean checkout). Vendors KiCad 9.0.7's CP_Elec_8x10.5.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
R0603 = 'Resistor_SMD:R_0603_1608Metric'

VALUES = {  # sheet: {ref: (old value, new value)}
    '01flight-ldo.kicad_sch': {'R1701': ('31.2k 0.1%', '31.9k 0.1%')},
    '01comms-ldo.kicad_sch': {'R1801': ('31.2k 0.1%', '31.9k 0.1%')},
    '01optional-ldo.kicad_sch': {'R1901': ('31.2k 0.1%', '31.9k 0.1%')},
    '01comms-limit.kicad_sch': {'R1504': ('36.5k 1%', '66.5k 1%')},
    '01optional-limit.kicad_sch': {'R1604': ('56.2k 1%', '49.9k 1%')},
}
LDO_NOTE = ('3.296 V nominal.', '3.352 V nominal; calculated corners 3.310-3.394 V.')
TEXT = {
    '01flight-ldo.kicad_sch': [LDO_NOTE], '01comms-ldo.kicad_sch': [LDO_NOTE], '01optional-ldo.kicad_sch': [LDO_NOTE],
    '01comms-limit.kicad_sch': [('Current-limit resistor is a provisional selected value.',
                                 'Current limit set by R1504 66.5k: 351-449 mA calculated.')],
    '01optional-limit.kicad_sch': [
        ('Current-limit resistor is a provisional selected value.',
         'Current limit set by R1604 49.9k: 470-588 mA calculated. EN on SERVICE_POWER_EN (PE8), held low by R1602\n'
         'at reset and power-off: a bounded, sequenced restart separate from comms.'),
        ('Connects to: 01c 4 V supply and flight control ->', 'Connects to: 01c 4 V supply and SERVICE_POWER_EN from the flight MCU ->')],
    '01b-bootstrap.kicad_sch': [
        ('Core input = BAT_VALID OR USB_CONFIG_OK.',
         'Core input enable: R1210 / R1204 from 4V_PRE into U1401 EN/UVLO (1.2 V): on above ~3.6 V, off below ~3.3 V,\n'
         'whatever the source (D-6.5).'),
        ('Connects to: Battery/USB status -> core and comms power enables.',
         'Connects to: Battery/USB status -> comms power enable; 4V_PRE level -> core input enable.')],
    '01d-held-core.kicad_sch': [
        ('C1403 remains a 1000 uF volume reservation, not an approved capacitor/footprint. Effective capacitance, ESR and retention remain open.',
         'C1403: Nichicon PCW0J102MCO1GS, 1000 uF 6.3 V polymer, 8 x 10.5 mm, flight hold-up only.\n'
         'Land pattern to check against Nichicon\'s drawing; hold-up time not proved.'),
        ('Connects to: 01c 4 V supply and 01b permission -> 01flight-ldo. C1403 is still an unselected capacitor allocation; hold-up time is not proved.',
         'Connects to: 01c 4 V supply, enabled by its own level (01b) -> 01flight-ldo. Hold-up time is not proved.')],
    '04c-usb-service.kicad_sch': [
        ('USB_CONFIG_OK controls the selected current-limit configuration. Reset / floating control returns through R4404 to the default state.',
         'U4401 limit fixed by R4403 60.4k: 387-491 mA from attach (D-6.5); strict hosts may need a powered hub.\n'
         'USB_CONFIG_OK keeps only its R4404 pull-down on this sheet.')],
}


def retext(t, sheet):
    for old, new in TEXT.get(sheet, []):
        hits = [n for n in K.children(t, 'text') if old in n[1]]
        assert len(hits) == 1, (sheet, old)
        hits[0][1] = hits[0][1].replace(old, new)


def set_props(sym, **kv):
    pr = {p[1]: p for p in K.children(sym, 'property')}
    at = K.xy(sym)
    for k, v in kv.items():
        if k in pr:
            pr[k][2] = v
        else:
            i = next(i for i, x in enumerate(sym) if isinstance(x, list) and x and x[0] == 'instances')
            sym.insert(i, K.prop(k, v, at))


def build():
    K.vendor_footprint(LIB, 'Capacitor_SMD', 'CP_Elec_8x10.5')
    log = {}

    for sheet, vals in VALUES.items():
        t = K.load(BOARD / sheet)
        for ref, (old, new) in vals.items():
            sym = K.symbols(t)[ref]
            assert K.props(sym)['Value'] == old, (ref, K.props(sym)['Value'])
            set_props(sym, Value=new)
        if sheet == '01optional-limit.kicad_sch':      # service restart: EN and R1602's top move to PE8
            en = K.pin_positions(t, 'U1601')['3'][:2]
            pts, _ = K.connected_points(t, en)
            labs = K.labels_at(t, pts)
            assert [l[1] for l in labs] == ['FLIGHT_3V3'], labs
            labs[0][1] = 'SERVICE_POWER_EN'
        retext(t, sheet)
        K.save(t, BOARD / sheet)

    # ---- 01b: core enable from a 4V_PRE divider; U1203 (and its own bypass C1203) go (D-6.5).
    sheet = '01b-bootstrap.kicad_sch'
    t = K.load(BOARD / sheet)
    log['U1203'] = K.remove_part(t, 'U1203')
    log['C1203'] = K.remove_part(t, 'C1203')
    K.make_symbol(t, 'Device:R', 'R1210', (420.37, 138.43), 0, '200k 1%', R0603, sheet,
                  extra={'Implementation_Note': 'Core-enable divider top over R1204 100k: U1401 EN/UVLO 1.183-1.223 V rising, '
                                                '1.076-1.116 V falling, so on at 3.5-3.7 V and off at 3.2-3.4 V of 4V_PRE (D-6.5)'})
    K.path(t, [(420.37, 142.24), (420.37, 146.05)], sheet, 'en.lo')
    K.path(t, [(420.37, 134.62), (420.37, 130.81), (412.75, 130.81)], sheet, 'en.hi')
    K.add(t, K.global_label('4V_PRE', (412.75, 130.81), 0, sheet, 'en'))
    K.add(t, K.junction((420.37, 146.05), sheet, 'en'))
    retext(t, sheet)
    K.save(t, BOARD / sheet)

    # ---- 01d: C1403 becomes the Nichicon PCW polymer part, 8 x 10.5 mm.
    sheet = '01d-held-core.kicad_sch'
    t = K.load(BOARD / sheet)
    set_props(K.symbols(t)['C1403'], Value='1000u 6.3V polymer', Footprint='Capacitor_SMD:CP_Elec_8x10.5',
              MPN='PCW0J102MCO1GS', Manufacturer='Nichicon',
              Implementation_Note='Flight hold-up only. Nichicon PCW, polymer, AEC-Q200, 8 x 10.5 mm max; '
                                  '>=800 uF effective at -20%. Land pattern to check against Nichicon\'s drawing')
    retext(t, sheet)
    K.save(t, BOARD / sheet)

    # ---- 04c: U4402 goes; U4401's limit is R4403 alone (D-6.5).
    sheet = '04c-usb-service.kicad_sch'
    t = K.load(BOARD / sheet)
    log['U4402'] = K.remove_part(t, 'U4402')
    retext(t, sheet)
    K.save(t, BOARD / sheet)
    return log


if __name__ == '__main__':
    for ref, items in build().items():
        print(ref, items)
