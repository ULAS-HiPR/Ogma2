"""Step 18: the 18 orange through-hole loops become yellow surface-mount loops (stage B2, D-22Nov.24).

Seán, 22 Nov, on the B2 calls: surface-mount loops, "absolutely" ("why do we have holes going the entire way
through"). A loop's pin went through all four layers, and the back's art had to keep clear of it. The four black
GND loops (Keystone 5011) stay through-hole at the edges, where a ground clip pulls hardest.

Source: Keystone's catalogue page "SMT Test Points" (Mouser's copy, https://www.mouser.com/pdfDocs/
KeystoneSMTTestPoints.pdf), read 22 Nov 2026. Of the families there:
  - 5015/5017 micro-miniature: "Ideal for use with miniature probes, clips and hooks"; pad 3.4 x 1.8 mm.
  - 5019/5029 miniature: "most standard probes, clips and hooks"; pad 3.0 x 1.6 mm; not in JLC's library
    (jlcparts scrape of 21 Nov 2026).
  - 5190TR-5199TR colour keyed: "most standard probes, clips and hooks"; phosphor bronze .008 (0.20) on an LCP
    base, base .094 x .118 (2.4 x 3.0 mm), .098 (2.5 mm) tall; pad layout .118 x .059 (3.0 x 1.5 mm).
  - 5016/5018 compact: "standard probes, clips and hooks"; pad 4.7 x 3.4 mm.
The pick (brief B2 step 4: the smallest that takes a standard scope hook and a mini-grabber, of which JLC holds
200 or more): 5194TR, yellow, JLC C22388408 (486 in stock in the 21 Nov scrape; Extended). Orange, 5193TR, isn't
in JLC's library. Black stays for GND.

The footprint is ours, from that page: one SMD pad 3.0 x 1.5 mm, the base 3.0 x 2.4 mm centred on it (F.Fab),
courtyard 0.25 mm round the base. Footprint field and part fields only: no pin changes. Edits the sheets in place.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
NAME = 'TestPoint_Keystone_5190TR_ColorKeyed'
MODEL = 'TestPoint.3dshapes/TestPoint_Keystone_5190TR_ColorKeyed.step'
OLD_FP = 'TestPoint:TestPoint_Keystone_5000-5004_Miniature'
SRC = 'https://www.mouser.com/pdfDocs/KeystoneSMTTestPoints.pdf'
FIELDS = {
    'Footprint': f'Ogma2:{NAME}',
    'Datasheet': SRC,
    'MPN': '5194TR',
    'Manufacturer': 'Keystone Electronics',
    'LCSC': 'C22388408',
    'Library_Check': 'Keystone SMT Test Points catalogue page (5190TR-5199TR colour keyed): pad .118 x .059 in '
                     '(3.0 x 1.5 mm), base 3.0 x 2.4 mm; footprint ours (capture step 18)',
}
PAD_W, PAD_H = 3.0, 1.5           # the pad layout
BASE_W, BASE_H = 3.0, 2.4         # the LCP base, centred on the pad
CRT = 0.25
OLD_NOTE, NEW_NOTE = 'orange loop, Keystone 5003 (D-22Nov.9)', 'yellow surface-mount loop, Keystone 5194TR (D-22Nov.24)'
TEXTS = [
    ('Black Keystone 5011 loops on GND at the board edges; orange Keystone 5003 loops where a probe stays clipped on',
     'Black Keystone 5011 loops on GND at the board edges; yellow Keystone 5194TR surface-mount loops where a probe stays clipped on'),
    ('ORANGE LOOPS: RAILS, PPS', 'YELLOW LOOPS: RAILS, PPS'),
]


def f(v):
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def rect(x0, y0, x1, y1, layer, w):
    pts = ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0))
    return ''.join(f'  (fp_line\n    (start {f(a[0])} {f(a[1])})\n    (end {f(b[0])} {f(b[1])})\n'
                   f'    (stroke\n      (width {w})\n      (type solid))\n    (layer "{layer}"))\n' for a, b in zip(pts, pts[1:]))


def text(kind, value, at, layer):
    head = f'  (property "{value[0]}" "{value[1]}"' if kind == 'property' else f'  (fp_text user "{value}"'
    return (f'{head}\n    (at {f(at[0])} {f(at[1])} 0)\n    (layer "{layer}")\n'
            '    (effects\n      (font\n        (size 1 1)\n        (thickness 0.15))))\n')


def footprint():
    bw, bh = BASE_W / 2, BASE_H / 2
    out = [f'(footprint "{NAME}"\n  (version 20241229)\n  (generator "ogma2-capture-step-18")\n  (layer "F.Cu")\n',
           '  (descr "Keystone 5190TR-5199TR colour-keyed SMT test point: pad and base from Keystone\'s SMT Test Points '
           'catalogue page; footprint ours (Burrito capture step 18)")\n',
           '  (tags "test point Keystone SMT 5194TR")\n',
           text('property', ('Reference', 'REF**'), (0, -bh - 1.0), 'F.SilkS'),
           text('property', ('Value', NAME), (0, bh + 1.0), 'F.Fab'),
           '  (attr smd)\n',
           rect(-bw, -bh, bw, bh, 'F.Fab', 0.1),
           rect(-bw - CRT, -bh - CRT, bw + CRT, bh + CRT, 'F.CrtYd', 0.05),
           text('fp_text', '${REFERENCE}', (0, 0), 'F.Fab'),
           f'  (pad "1" smd rect\n    (at 0 0)\n    (size {f(PAD_W)} {f(PAD_H)})\n    (layers "F.Cu" "F.Paste" "F.Mask"))\n',
           '  (embedded_fonts no)\n',
           f'  (model "${{KIPRJMOD}}/libraries/3d/{MODEL}"\n    (offset\n      (xyz 0 0 0))\n    (scale\n      (xyz 1 1 1))\n'
           '    (rotate\n      (xyz 0 0 0))))\n']
    return ''.join(out)


def set_props(sym, kv):
    pr = {p[1]: p for p in K.children(sym, 'property')}
    for k, v in kv.items():
        if k in pr:
            pr[k][2] = v
        else:
            i = next(i for i, x in enumerate(sym) if isinstance(x, list) and x and x[0] == 'instances')
            sym.insert(i, K.prop(k, v, K.xy(sym)))


def build():
    (LIB / 'Ogma2.pretty' / f'{NAME}.kicad_mod').write_text(footprint())
    done = {}
    for fn in sorted(BOARD.glob('*.kicad_sch')):
        t = K.load(fn)
        hit = False
        for ref, sym in K.symbols(t).items():
            pr = {p[1]: p for p in K.children(sym, 'property')}
            if 'Footprint' in pr and pr['Footprint'][2] == OLD_FP:
                set_props(sym, FIELDS)
                if 'Implementation_Note' in pr and OLD_NOTE in pr['Implementation_Note'][2]:
                    pr['Implementation_Note'][2] = pr['Implementation_Note'][2].replace(OLD_NOTE, NEW_NOTE)
                done[ref] = fn.name
                hit = True
        for x in K.children(t, 'text'):
            for old, new in TEXTS:
                if old in x[1]:
                    x[1] = x[1].replace(old, new)
                    hit = True
        if hit:
            K.save(t, fn)
    return done


if __name__ == '__main__':
    done = build()
    print('step 18:', len(done), 'loops ->', FIELDS['Footprint'], ':', ' '.join(sorted(done, key=lambda r: int(r[2:]) if r[2:].isdigit() else 0)))
