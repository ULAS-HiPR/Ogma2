"""Step 14: J103, the master-enable loop, becomes a Molex Micro-Fit 3.0 header, single row, two circuits (D-22Nov.18).

Harwin's Gecko G125 has no 2-contact housing (Harwin's G125 data sheet lists 6 to 50 contacts; the jlcparts
scrape of 21 Nov has nothing under 6), so D-22Nov.18 stands and D-19Nov.5's 2-contact Gecko is void for J103.

Part: Molex 43650-0215, "Micro-Fit 3.0 Vertical Header, 3.00mm Pitch, Single Row, 2 Circuits, with PCB
Polarizing Peg, Tin" (Molex product page 0436500215). Vertical, as the JST GH it replaces: the side-edge
harness connectors (J501, J502, J6101, J6102) are all vertical. Through-hole with a peg, like the arm
headers. JLC C293740 (Extended, through-hole; 2,209 in stock in the jlcparts scrape of 21 Nov).
Mates 43645 and 171850 only (Molex Micro-Fit 3.0 overview 987650-5984 rev 6; product page): not the
dual-row 43025 plug that Churro's J701 (430450200, raw PROP) takes.
Footprint: KiCad 9.0.7's Molex_Micro-Fit_3.0_43650-0215_1x02_P3.00mm_Vertical, from Molex's drawing
for 436500215, vendored. Same two pins, same nets. Edits the sheet in place (run from a clean checkout).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
SHEET = '44-master-enable.kicad_sch'
FP = 'Molex_Micro-Fit_3.0_43650-0215_1x02_P3.00mm_Vertical'
FIELDS = {
    'Value': '43650-0215',
    'Footprint': f'Connector_Molex:{FP}',
    'Datasheet': 'https://www.molex.com/en-us/products/part-detail/436500215',
    'Description': 'Master-enable loop to the panel switch: Molex Micro-Fit 3.0 vertical header, single row, '
                   '2 circuits, polarizing peg (D-22Nov.18)',
    'ki_keywords': 'connector',
    'ki_fp_filters': 'Connector*:*_1x??_*',
    'MPN': '43650-0215',
    'Manufacturer': 'Molex',
    'LCSC': 'C293740',
    'Library_Check': 'Molex 0436500215: vertical, single row, 2 circuits, PCB polarizing peg; mates 43645 and 171850 '
                     '(987650-5984 rev 6), not the dual-row 43025 of Churro J701; footprint KiCad 9.0.7 from Molex '
                     'drawing 436500215; latch on the footprint +y side',
}


def set_props(sym, kv):
    pr = {p[1]: p for p in K.children(sym, 'property')}
    for k, v in kv.items():
        if k in pr:
            pr[k][2] = v
        else:
            i = next(i for i, x in enumerate(sym) if isinstance(x, list) and x and x[0] == 'instances')
            sym.insert(i, K.prop(k, v, K.xy(sym)))


def build():
    K.vendor_footprint(LIB, 'Connector_Molex', FP)
    t = K.load(BOARD / SHEET)
    set_props(K.symbols(t)['J103'], FIELDS)
    K.save(t, BOARD / SHEET)


if __name__ == '__main__':
    build()
