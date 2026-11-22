"""Step 17: the two A5 additions Seán accepted on 22 Nov ("Yes absolutely add the esd protect and the 1nf caps").

1. D4601 on the LoRa port, as D4501 is on the GNSS port: Nexperia PESD5V0F1BL,315 (bidirectional, 5.5 V standoff,
   0.4 pF typ, SOD882; data sheet rev. 4), JLC C45961. LORA_RF_SUBG joined only J4601 and the Wio-LR2021, with no
   discharge path for static the antenna collects. 0.4 pF is 458 ohm at 868 MHz, so it barely loads the line.
   Same symbol and footprint as D4501 (step 10): pin 1 IO, pin 2 GND.
2. C6601-C6606, 1 nF 50 V C0G (0603: the fire path stays 0603, step 16), from each pyro output to GND at J6601:
   RF picked up on the e-match leads returns at the connector, not through the switches. On the continuity
   network's 3.9 kohm they add 3.9 us. JLC's matcher picks the part (generic value, like the other 0603s).

Each new part joins its nets by global label, the sheets' house style. Edits the sheets in place.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
RADIO, HARNESS = '04f-radio-module.kicad_sch', '06b-output-harness.kicad_sch'
D_FIELDS = {
    'Datasheet': 'https://assets.nexperia.com/documents/data-sheet/PESD5V0F1BL.pdf',
    'MPN': 'PESD5V0F1BL,315', 'Manufacturer': 'Nexperia', 'LCSC': 'C45961',
    'Library_Check': 'as D4501 (step 10): PESD5V0F1BL is bidirectional, so the TPD1E0B04 symbol\'s pin 1 (IO) and pin 2 (GND) '
                     'map to either SOD882 pad; footprint KiCad D_SOD-882',
}
D_DESC = 'LoRa RF ESD at J4601: bidirectional TVS, 0.4 pF typ, 5.5 V standoff (D-22Nov.20)'
CAPS = [('C6601', 'OUTPUT1_HIGH', 109.22), ('C6602', 'OUTPUT1_LOW', 119.38), ('C6603', 'OUTPUT2_HIGH', 129.54),
        ('C6604', 'OUTPUT2_LOW', 139.7), ('C6605', 'OUTPUT3_HIGH', 149.86), ('C6606', 'OUTPUT3_LOW', 160.02)]
C_VALUE, C_FP = '1n 50V C0G', 'Capacitor_SMD:C_0603_1608Metric'


def text(t, sheet, value, at, tag, size=1.27):
    K.add(t, K.el('text', value, K.el('exclude_from_sim', K.A('no')), K.el('at', K.num(at[0]), K.num(at[1]), K.num(0)),
                  K.fx(size, 'left top'), K.el('uuid', K.ident(sheet, 'text', tag))))


def build():
    # 1. D4601 on the LoRa port
    t = K.load(BOARD / RADIO)
    K.import_lib(t, 'Ogma2_GNSS:TPD1E0B04DPYR', LIB / 'Ogma2_GNSS.kicad_sym')
    x, y = 314.96, 157.48
    pins = K.make_symbol(t, 'Ogma2_GNSS:TPD1E0B04DPYR', 'D4601', (x, y), 270, 'PESD5V0F1BL,315', 'Diode_SMD:D_SOD-882', RADIO,
                         extra=D_FIELDS, ref_at=(x + 2.54, y - 1.27), val_at=(x + 2.54, y + 1.27))
    sym = K.symbols(t)['D4601']
    for p in K.children(sym, 'property'):
        if p[1] == 'Description':
            p[2] = D_DESC
    (x1, y1), (x2, y2) = pins['1'][:2], pins['2'][:2]
    K.add(t, K.global_label('LORA_RF_SUBG', (x1, y1), 90, RADIO, 'D4601'))
    K.add(t, K.global_label('GND', (x2, y2), 270, RADIO, 'D4601'))
    text(t, RADIO, 'D4601: ESD on the LoRa port, as D4501 on GNSS (D-22Nov.20).\nA path for static the antenna collects; 0.4 pF.',
         (x - 12.7, y + 10.16), 'd4601')
    K.save(t, BOARD / RADIO)

    # 2. a 1 nF C0G from each pyro output to GND, beside J6601
    t = K.load(BOARD / HARNESS)
    K.import_lib(t, 'Device:C', LIB / 'Device.kicad_sym')
    cx = 50.8
    for ref, net, yy in CAPS:
        pins = K.make_symbol(t, 'Device:C', ref, (cx, yy), 90, C_VALUE, C_FP, HARNESS,
                             extra={'Implementation_Note': f'RF bypass on {net} at J6601: 1 nF C0G to GND (D-22Nov.20)'},
                             ref_at=(cx - 1.27, yy - 2.54), val_at=(cx - 1.27, yy + 2.54))
        a, b = sorted((pins['1'][:2], pins['2'][:2]))         # left end to the output, right end to GND
        K.add(t, K.global_label(net, a, 180, HARNESS, ref))
        K.add(t, K.global_label('GND', b, 0, HARNESS, ref))
    text(t, HARNESS, 'C6601-C6606: 1 nF C0G from each output to GND at J6601 (D-22Nov.20).\n'
                     'RF picked up on the e-match leads returns here, not through the switches.', (30.48, 167.64), 'c66xx')
    K.save(t, BOARD / HARNESS)


if __name__ == '__main__':
    build()
