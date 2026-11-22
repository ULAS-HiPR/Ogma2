"""Silkscreen marks that aren't parts (D-22Nov.19): the board axes with the nose arrow. (The S/N box is drawn by
art.board_art on the top silk after placing, D-22Nov.23.)
Written as board-only footprints in the project library, so the placer finds them room like any part.

    python3 tools/layout/marks.py      # writes hardware/croi2/libraries/Ogma2.pretty/MARK_*.kicad_mod

Board axes: X to the nose (the forward edge, -y on the board), Y to the left, Z out of the top face: right-handed.
It is the board's frame, not any one chip's: firmware maps each sensor into it."""
from pathlib import Path

LIB = Path(__file__).resolve().parents[2] / 'hardware' / 'croi2' / 'libraries' / 'Ogma2.pretty'
W, TXT, TH = 0.15, 1.0, 0.15          # line width, text height, text stroke (JLC minimums: 1.0 mm, 0.15 mm; spec.RULES)


def f(v):
    s = f'{v:.3f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def line(a, b, layer='F.SilkS', w=W):
    return (f'  (fp_line\n    (start {f(a[0])} {f(a[1])})\n    (end {f(b[0])} {f(b[1])})\n'
            f'    (stroke\n      (width {w})\n      (type solid))\n    (layer "{layer}"))\n')


def rect(x0, y0, x1, y1, layer, w, fill=False):
    return (f'  (fp_rect\n    (start {f(x0)} {f(y0)})\n    (end {f(x1)} {f(y1)})\n    (stroke\n      (width {w})\n'
            f'      (type solid))\n    (fill {"yes" if fill else "no"})\n    (layer "{layer}"))\n')


def circle(c, r, layer='F.SilkS', w=W, fill=False):
    return (f'  (fp_circle\n    (center {f(c[0])} {f(c[1])})\n    (end {f(c[0] + r)} {f(c[1])})\n    (stroke\n      (width {w})\n'
            f'      (type solid))\n    (fill {"yes" if fill else "no"})\n    (layer "{layer}"))\n')


def text(s, at, layer='F.SilkS', justify=None):
    j = f'\n      (justify {justify})' if justify else ''
    return (f'  (fp_text user "{s}"\n    (at {f(at[0])} {f(at[1])} 0)\n    (layer "{layer}")\n    (effects\n      (font\n'
            f'        (size {TXT} {TXT})\n        (thickness {TH})){j}))\n')


def arrow(tip, back):
    """A line from back to tip with a 1.2 mm head."""
    (tx, ty), (bx, by) = tip, back
    dx, dy = tx - bx, ty - by
    n = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    h1 = (tx - 1.2 * ux + 0.6 * px, ty - 1.2 * uy + 0.6 * py)
    h2 = (tx - 1.2 * ux - 0.6 * px, ty - 1.2 * uy - 0.6 * py)
    return line(back, tip) + line(tip, h1) + line(tip, h2)


def footprint(name, descr, body, crt):
    head = (f'(footprint "{name}"\n  (version 20241229)\n  (generator "ogma2-marks")\n  (layer "F.Cu")\n  (descr "{descr}")\n'
            f'  (property "Reference" "MK**"\n    (at 0 0 0)\n    (layer "F.Fab")\n    (hide yes)\n    (effects\n      (font\n'
            f'        (size 0.5 0.5)\n        (thickness 0.08))))\n  (property "Value" "{name}"\n    (at 0 0 0)\n    (layer "F.Fab")\n'
            f'    (hide yes)\n    (effects\n      (font\n        (size 0.5 0.5)\n        (thickness 0.08))))\n'
            f'  (attr board_only exclude_from_pos_files exclude_from_bom allow_missing_courtyard)\n')
    return head + body + rect(*crt, 'F.CrtYd', 0.05) + '  (embedded_fonts no)\n)\n'


def axes():
    L = 6.0
    body = (arrow((0, -L), (0, -1.1)) + arrow((-L, 0), (-1.1, 0)) + circle((0, 0), 0.9) + circle((0, 0), 0.25, fill=True)
            + text('X', (1.9, -L + 1.0), justify='left') + text('NOSE', (0, -L - 1.7))
            + text('Y', (-L + 1.0, 1.9)) + text('Z', (1.9, 1.6), justify='left'))
    return footprint('MARK_AXES', 'Board axes: X to the nose, Y left, Z out of the top (D-22Nov.19)', body, (-L - 0.9, -L - 2.7, 3.1, 2.8))



if __name__ == '__main__':
    for name, txt in (('MARK_AXES', axes()),):
        (LIB / f'{name}.kicad_mod').write_text(txt)
        print(LIB / f'{name}.kicad_mod')
