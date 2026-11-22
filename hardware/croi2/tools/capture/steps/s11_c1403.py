"""Step 11: footprint audit fixes before placement (S3), 22 Nov 2026.

- C1403 (Nichicon PCW0J102MCO1GS) is a phi 8 x 10 mm can (Nichicon PCW data, expanded May 2024: D 8.0, L 10.0,
  A 9.0, B / C 8.3, E 3.2), not 8 x 10.5. Its footprint moves from KiCad's CP_Elec_8x10.5 (Vishay 0810) to
  KiCad's CP_Elec_8x10, made for Nichicon's 8 x 10 mm can; both vendored, KiCad 9.0.7.
- U3701 (MMC5983MA): footprint kept. Its pads match MEMSIC's MMC5983MA land pattern (Rev. A, 25 Feb 2019,
  p. 20): 0.45 x 0.30 mm pads, 0.5 mm pitch, pad rows 2.55 mm apart; read from the drawing on 22 Nov.
  Only the footprint's description changes, to record the check.
Edits in place (run from a clean checkout).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
SHEET = '01d-held-core.kicad_sch'
C1403 = {
    'Footprint': 'Capacitor_SMD:CP_Elec_8x10',
    'Datasheet': 'https://www.nichicon.com/getmedia/0a532687-d8ef-4eb6-a434-ae2de5ee9c3a/pcw_e.pdf',
    'Implementation_Note': 'Flight hold-up only. Nichicon PCW, polymer, AEC-Q200, phi 8 x 10 mm (Nichicon PCW data, May 2024); '
                           '>=800 uF effective at -20%. Land: KiCad CP_Elec_8x10, Nichicon 8 x 10 mm (capture step 11)',
}
MAG_OLD = ('(descr "MEMSIC MMC5983MA, LGA-16 3 x 3 x 1 mm. From KiCad 9.0.7 Package_LGA:LGA-16_3x3mm_P0.5mm '
           '(MEMSIC MMC5883MA drawing); check against the MMC5983MA drawing")')
MAG_NEW = ('(descr "MEMSIC MMC5983MA, LGA-16 3 x 3 x 1 mm. From KiCad 9.0.7 Package_LGA:LGA-16_3x3mm_P0.5mm; pads checked '
           'against MEMSIC MMC5983MA Rev. A p. 20 land pattern (0.45 x 0.30 mm, 0.5 mm pitch, rows 2.55 mm apart), 22 Nov 2026")')


def build():
    K.vendor_footprint(LIB, 'Capacitor_SMD', 'CP_Elec_8x10')
    t = K.load(BOARD / SHEET)
    sym = K.symbols(t)['C1403']
    pr = {p[1]: p for p in K.children(sym, 'property')}
    for k, v in C1403.items():
        pr[k][2] = v
    K.save(t, BOARD / SHEET)
    p = LIB / 'Ogma2.pretty' / 'MMC5983MA.kicad_mod'
    s = p.read_text()
    if MAG_NEW not in s:
        assert s.count(MAG_OLD) == 1
        p.write_text(s.replace(MAG_OLD, MAG_NEW))


if __name__ == '__main__':
    build()
    print('step 11: C1403 ->', C1403['Footprint'], '; MMC5983MA footprint checked')
