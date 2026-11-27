"""Step 15: J101, the standalone 2S input, gets its footprint: Molex Nano-Fit 105311-1102 (D-22Nov.13, sweep section 10).

Source: Molex drawing SD-105311-100 rev H, "Header of Nano-Fit, S/R, vertical, clip, power connector", LCSC's copy
(https://atta.szlcsc.com/upload/public/pdf/source/20240628/E7D92444DA1D193B3483D9BAD77A6611.pdf), read 22 Nov.
Its 105311-1102 row: A 8.66, B 5.94, C 6.84 mm. Recommended PCB, board 1.6 to 2.4 mm:
  - pins: two holes D1.20 +/-0.05 at 2.50 mm pitch;
  - clips: two holes D1.60 +/-0.05 on the pin row, C apart (3.42 mm either side of centre);
  - peg: one hole D1.30 +/-0.05, 1.34 mm off the row, midway between the pins, on the latch side;
  - housing 3.48 mm deep centred on the row, 6.34 mm with the latch; latch 5.20 mm long; 9.06 mm tall
    (10.51 with the latch); tails 3.20 mm.
The peg's side: read off the drawing's views (sweep section 10), and the same in KiCad 9.0.7's footprint for the
non-clip sister part, Molex_Nano-Fit_105309-xx02_1x02_P2.50mm_Vertical (from Molex drawing 1053091203): NPTH D1.3
at 1.34 mm from the row, midway, on the side of its F.Fab latch, whose housing (3.48 / 6.34 / 5.94 / 5.20 mm)
matches this one.

Pads are ours (sweep section 10): pins D1.80 round (0.30 mm ring), so 0.28 mm of copper clears the peg hole;
clips D2.10 (0.25 mm ring) and no net, 0.22 mm from the pins, so no ground sits that close to the pack's
positive pin. The peg hole is unplated. Same layout as KiCad's 105309 footprint: pin 1 at the origin, the row
along +y, the latch toward -x. Edits the sheet in place (run from a clean checkout).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
SHEET = '01-power.kicad_sch'
NAME = '105311-1102'
MODEL = 'Connector_Molex.3dshapes/Molex_Nano-Fit_105311-1102_1x02_P2.50mm_Vertical.step'

P = 2.50                          # pitch
MID = P / 2                       # the row's centre, y
C2 = 6.84 / 2                     # clips, either side of centre
A2 = 8.66 / 2                     # overall, clips included
B2 = 5.94 / 2                     # housing length
D2 = 3.48 / 2                     # housing depth, either side of the row
LATCH_X = -(6.34 - D2)            # the latch's outer face (-x)
LATCH2 = 5.20 / 2                 # latch length
PEG = (-1.34, MID)
PIN_PAD, PIN_DRILL = 1.80, 1.20
CLIP_PAD, CLIP_DRILL = 2.10, 1.60
PEG_DRILL = 1.30
SILK = 0.11                       # silk outside the body
CRT = 0.50                        # courtyard margin

FIELDS = {
    'Footprint': f'Ogma2:{NAME}',
    'Library_Check': 'SD-105311-100 rev H: holes, pitch, clips C apart, peg 1.34 mm off the row on the latch side '
                     '(also so in KiCad 9.0.7\'s 105309-xx02 footprint); pads ours (sweep section 10): clips no net, peg unplated',
    'Implementation_Note': 'Standalone and Churro feeds MUST be mechanically exclusive (J101 or J102 fitted, never both).',
}


def f(v):
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def line(a, b, layer, w):
    return (f'  (fp_line\n    (start {f(a[0])} {f(a[1])})\n    (end {f(b[0])} {f(b[1])})\n'
            f'    (stroke\n      (width {w})\n      (type solid))\n    (layer "{layer}"))\n')


def rect(x0, y0, x1, y1, layer, w):
    return ''.join(line(a, b, layer, w) for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                                                      ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))))


def text(kind, value, at, layer, hide=False):
    head = f'  (property "{value[0]}" "{value[1]}"' if kind == 'property' else f'  (fp_text user "{value}"'
    return (f'{head}\n    (at {f(at[0])} {f(at[1])} 0)\n    (layer "{layer}")\n' + ('    (hide yes)\n' if hide else '')
            + '    (effects\n      (font\n        (size 1 1)\n        (thickness 0.15))))\n')


def pad(num, kind, at, size, drill):
    layers = '"*.Cu" "*.Mask"'
    extra = '    (remove_unused_layers no)\n' if kind == 'thru_hole' else ''
    return (f'  (pad "{num}" {kind} circle\n    (at {f(at[0])} {f(at[1])})\n    (size {f(size)} {f(size)})\n'
            f'    (drill {f(drill)})\n    (layers {layers})\n{extra}  )\n').replace('\n  )\n', ')\n')


def footprint():
    clip_y = (MID - C2, MID + C2)
    y_lo = min(MID - A2, clip_y[0] - CLIP_PAD / 2)
    y_hi = max(MID + A2, clip_y[1] + CLIP_PAD / 2)
    out = [f'(footprint "{NAME}"\n  (version 20241229)\n  (generator "ogma2-capture-step-15")\n  (layer "F.Cu")\n',
           '  (descr "Molex Nano-Fit 105311-1102: vertical header, single row, 2 circuits, 2.50 mm, solder clips; holes and '
           'body from Molex drawing SD-105311-100 rev H; pads ours (Burrito sweep section 10)")\n',
           '  (tags "connector Molex Nano-Fit vertical clip 105311")\n',
           text('property', ('Reference', 'REF**'), (2.8, MID), 'F.SilkS'),
           text('property', ('Value', NAME), (3.5, MID + 2.5), 'F.Fab'),
           '  (attr through_hole)\n']
    # F.Fab: housing, latch, the clips' reach (A wide), pin 1 mark
    out.append(rect(-D2, MID - B2, D2, MID + B2, 'F.Fab', 0.1))
    out.append(rect(LATCH_X, MID - LATCH2, -D2, MID + LATCH2, 'F.Fab', 0.1))
    out.append(line((0, MID - A2), (0, MID - B2), 'F.Fab', 0.1))
    out.append(line((0, MID + B2), (0, MID + A2), 'F.Fab', 0.1))
    out.append(line((-0.5, MID - B2), (0, MID - B2 + 0.7), 'F.Fab', 0.1))
    out.append(line((0, MID - B2 + 0.7), (0.5, MID - B2), 'F.Fab', 0.1))
    # F.SilkS: body plus latch, broken round the clip pads; a pin 1 tick outside the housing
    sx0, sx1, sy0, sy1 = LATCH_X - SILK, D2 + SILK, MID - B2 - SILK, MID + B2 + SILK
    gap = CLIP_PAD / 2 + 0.25
    for y in (sy0, sy1):
        out.append(line((sx0, y), (-gap, y), 'F.SilkS', 0.12))
        out.append(line((gap, y), (sx1, y), 'F.SilkS', 0.12))
    out.append(line((sx0, sy0), (sx0, sy1), 'F.SilkS', 0.12))
    out.append(line((sx1, sy0), (sx1, sy1), 'F.SilkS', 0.12))
    out.append(line((sx1 + 0.3, -0.5), (sx1 + 0.3, 0.5), 'F.SilkS', 0.12))
    # F.CrtYd: body, latch and pads, 0.5 mm round
    out.append(rect(LATCH_X - CRT, y_lo - CRT, D2 + CRT, y_hi - 0 + CRT, 'F.CrtYd', 0.05))
    out.append(text('fp_text', '${REFERENCE}', (0, MID), 'F.Fab'))
    out.append(pad('', 'np_thru_hole', PEG, PEG_DRILL, PEG_DRILL))
    out.append(pad('1', 'thru_hole', (0, 0), PIN_PAD, PIN_DRILL))
    out.append(pad('2', 'thru_hole', (0, P), PIN_PAD, PIN_DRILL))
    out.append(pad('MP', 'thru_hole', (0, clip_y[0]), CLIP_PAD, CLIP_DRILL))
    out.append(pad('MP', 'thru_hole', (0, clip_y[1]), CLIP_PAD, CLIP_DRILL))
    out.append('  (embedded_fonts no)\n')
    out.append(f'  (model "${{KIPRJMOD}}/libraries/3d/{MODEL}"\n    (offset\n      (xyz 0 0 0))\n    (scale\n      (xyz 1 1 1))\n'
               '    (rotate\n      (xyz 0 0 0))))\n')
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
    t = K.load(BOARD / SHEET)
    set_props(K.symbols(t)['J101'], FIELDS)
    K.save(t, BOARD / SHEET)


if __name__ == '__main__':
    build()
