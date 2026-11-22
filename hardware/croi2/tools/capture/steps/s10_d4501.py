"""Step 10: D4501, the GNSS RF ESD part, moves to a package JLC's Economic PCBA places (D-22Nov.3, D-22Nov.8).

TPD1E0B04DPYR (0.6 x 0.3 mm) is below Economic's 0402 minimum (D-21Nov.27). Its replacement is Nexperia's
PESD5V0F1BL,315: bidirectional, 5.5 V standoff, 0.4 pF typical / 0.55 pF maximum, 10 kV IEC 61000-4-2,
DFN1006-2 (SOD882), 1.0 x 0.6 mm (Nexperia data sheet rev. 4, 14 Apr 2023, pp. 1-4). The two-pin symbol
stays: the part is bidirectional, so pin 1 (IO) and pin 2 (GND) map to either pad. Footprint: KiCad's
Diode_SMD:D_SOD-882, made from Nexperia's SOD882 package drawing, vendored like step 9's.
Edits the sheet in place (run from a clean checkout).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
SHEET = '04d-gnss.kicad_sch'
FIELDS = {
    'Value': 'PESD5V0F1BL,315',
    'Footprint': 'Diode_SMD:D_SOD-882',
    'Datasheet': 'https://assets.nexperia.com/documents/data-sheet/PESD5V0F1BL.pdf',
    'Description': 'GNSS RF ESD at J4501: bidirectional TVS, 0.4 pF typ, 5.5 V standoff (D-22Nov.8)',
    'MPN': 'PESD5V0F1BL,315',
    'Manufacturer': 'Nexperia',
    'Library_Check': 'PESD5V0F1BL (D-22Nov.8): bidirectional, so the kept TPD1E0B04 symbol\'s pin 1 (IO) and pin 2 (GND) '
                     'map to either SOD882 pad; footprint KiCad D_SOD-882 from Nexperia\'s SOD882 drawing',
}
TEXT = ('Same U4504 symbol UUID and hierarchy path. New J4501/D4501 require explicit PCB update; live PCB untouched by this candidate.',
        'Same U4504 symbol UUID and hierarchy path. D4501 is Nexperia PESD5V0F1BL (SOD882), placeable by Economic PCBA (D-22Nov.8).')


def set_props(sym, kv):
    pr = {p[1]: p for p in K.children(sym, 'property')}
    for k, v in kv.items():
        if k in pr:
            pr[k][2] = v
        else:
            i = next(i for i, x in enumerate(sym) if isinstance(x, list) and x and x[0] == 'instances')
            sym.insert(i, K.prop(k, v, K.xy(sym)))


def build():
    (LIB / 'Diode_SMD.pretty').mkdir(exist_ok=True)
    table = BOARD / 'fp-lib-table'
    t = K.load(table)
    if 'Diode_SMD' not in {K.first(l, 'name')[1] for l in K.children(t, 'lib')}:
        t.append(K.el('lib', K.el('name', 'Diode_SMD'), K.el('type', 'KiCad'), K.el('uri', '${KIPRJMOD}/libraries/Diode_SMD.pretty'),
                      K.el('options', ''), K.el('descr', 'KiCad 9.0.7 footprints added during capture')))
        K.save(t, table)
    K.vendor_footprint(LIB, 'Diode_SMD', 'D_SOD-882')
    t = K.load(BOARD / SHEET)
    set_props(K.symbols(t)['D4501'], FIELDS)
    hits = [n for n in K.children(t, 'text') if TEXT[0] in n[1]]
    assert len(hits) == 1, len(hits)
    hits[0][1] = hits[0][1].replace(*TEXT)
    K.save(t, BOARD / SHEET)


if __name__ == '__main__':
    build()
    print('step 10: D4501 ->', FIELDS['Value'], FIELDS['Footprint'])
