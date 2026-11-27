#!/usr/bin/env python3
"""Real pin-1 marks in the footprints (27 Nov 2026, Seán: no loose "1" beside the part).

For every footprint in libraries/Ogma2.pretty and Ogma2_GNSS.pretty with pads and no silkscreen pin-1 mark
(a filled polygon on F.SilkS), draw a filled dot on F.SilkS beside pad 1, outside the pad array, clear of every
pad, and delete the fp_text "1" the footprint carried. Rerunnable: a footprint that already has a mark or a dot
is left alone.

  python3 tools/add_pin1_marks.py                    # libraries (dry run prints; --write saves)
  python3 tools/add_pin1_marks.py --pcb Croi2.kicad_pcb --write
      the same dot on each placed instance of those footprints (B.SilkS on the back), their "1" texts removed,
      and the loose gr_text "1" on the silkscreen removed. Close KiCad first; or use Update Footprints from Library.
"""
import argparse, math, re, uuid
from pathlib import Path

HW = Path(__file__).resolve().parents[1]
R, GAP = 0.25, 0.25            # dot radius (0.15 on packages under 4 mm across), silk-to-pad clearance (mm)
SKIP = {'Fiducial', 'MountingHole', 'TestPoint', 'MARK_AXES',            # no pin 1
        'SMA_Amphenol_132134_Vertical', 'U.FL_Hirose_U.FL-R-SMT-1_Vertical',      # RF: centre and shield, no pin order
        'TestPoint_Keystone_5190TR_ColorKeyed', 'ABS07-32.768KHZ-7-T', 'TPD1E0B04DPYR',  # not polarised
        '105311-1102',                                                           # has its tick outside the housing (s15_j101)
        'CPT-9019S-SMT-TR', 'USB4105-GF-A'}                                      # buzzer polarity: owner to confirm; USB-C has no pin 1
PAD = re.compile(r'\(pad "?([^\s")]+)"?\s+(\w+)\s+(\w+)\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)\s*\(size ([-\d.]+) ([-\d.]+)\)')


def span(s, i):
    d = 0
    for j in range(i, len(s)):
        d += (s[j] == '(') - (s[j] == ')')
        if d == 0:
            return j + 1


def pads(s):
    out = []
    for m in PAD.finditer(s):
        name, x, y, rot, w, h = m.group(1), *map(float, m.group(4, 5)), float(m.group(6) or 0), *map(float, m.group(7, 8))
        if round(rot) % 180 == 90:
            w, h = h, w
        out.append((name, x - w / 2, y - h / 2, x + w / 2, y + h / 2))
    return out


def has_mark(s):
    return any('F.SilkS' in s[m.start():span(s, m.start())] for m in re.finditer(r'\(fp_poly', s)) or \
        any('(fill yes)' in s[m.start():span(s, m.start())] and 'F.SilkS' in s[m.start():span(s, m.start())]
            for m in re.finditer(r'\(fp_circle', s))


def dist(cx, cy, p):
    dx = max(p[1] - cx, 0, cx - p[3]); dy = max(p[2] - cy, 0, cy - p[4])
    return math.hypot(dx, dy)


def place(ps):
    """(x, y, radius) of the dot, or None."""
    one = [p for p in ps if p[0] == '1']
    if not one:
        return None
    x0, y0, x1, y1 = min(p[1] for p in one), min(p[2] for p in one), max(p[3] for p in one), max(p[4] for p in one)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ax0, ay0 = min(p[1] for p in ps), min(p[2] for p in ps)
    ax1, ay1 = max(p[3] for p in ps), max(p[4] for p in ps)
    tol = 0.05
    r = 0.15 if max(ax1 - ax0, ay1 - ay0) < 4 else R
    ex = -1 if x0 <= ax0 + tol else 1 if x1 >= ax1 - tol else 0
    ey = -1 if y0 <= ay0 + tol else 1 if y1 >= ay1 - tol else 0
    row = [p for p in ps if p[0] != '1' and abs((p[2] + p[4]) / 2 - cy) < 0.1 and p not in one]
    col = [p for p in ps if p[0] != '1' and abs((p[1] + p[3]) / 2 - cx) < 0.1 and p not in one]
    if len(row) >= 2 and ex:                     # end of a row: beyond it along the row
        d = (ex, 0)
    elif len(col) >= 2 and ey:                   # end of a column: beyond it along the column
        d = (0, ey)
    elif ex and ey:
        d = (ex, ey)
    else:
        d = (ex, ey) if ex or ey else (-1, -1)
    px, py = (cx + d[0] * ((x1 - x0) / 2 + GAP + r), cy + d[1] * ((y1 - y0) / 2 + GAP + r))
    for _ in range(40):                          # push out until clear of every pad
        if all(dist(px, py, p) >= r + GAP for p in ps):
            return round(px, 3), round(py, 3), r
        px += d[0] * 0.05; py += d[1] * 0.05
    return round(px, 3), round(py, 3), r


def dot(x, y, r, layer):
    return (f'  (fp_circle\n    (center {x} {y})\n    (end {round(x + r, 3)} {y})\n    (stroke\n      (width 0.12)\n'
            f'      (type solid))\n    (fill yes)\n    (layer "{layer}")\n    (uuid "{uuid.uuid4()}"))\n')


def drop_text(s, text='1'):
    n = 0
    for pat in (rf'\(fp_text user "{text}"', rf'\(gr_text "{text}"'):
        while True:
            m = re.search(pat, s)
            if not m:
                break
            blk = s[m.start():span(s, m.start())]
            if 'SilkS' not in blk:
                s = s[:m.start()] + '\0' + s[m.start() + 1:]; continue     # not silk: leave, mark to skip
            a = s.rfind('\n', 0, m.start()) + 1
            e = span(s, m.start())
            e = e + 1 if s[e:e + 1] == '\n' else e
            s = s[:a] + s[e:]; n += 1
    return s.replace('\0', '('), n


def library(write):
    for d in ('Ogma2.pretty', 'Ogma2_GNSS.pretty'):
        for f in sorted((HW / 'libraries' / d).glob('*.kicad_mod')):
            s = f.read_text()
            if f.stem in SKIP or not (ps := pads(s)) or len({p[0] for p in ps}) < 3 and not re.search(r'"1"', s):
                continue
            s2, n = drop_text(s)
            if has_mark(s2) and not n:
                continue
            if has_mark(s2):
                print(f'{d}/{f.stem}: dropped {n} loose "1"; mark already there'); 
            else:
                c = place(ps)
                if c is None or all(p[0] != '1' for p in ps):
                    print(f'{d}/{f.stem}: no pad 1 (left alone)'); continue
                i = s2.index('\n  (pad ') + 1
                s2 = s2[:i] + dot(*c, 'F.SilkS') + s2[i:]
                print(f'{d}/{f.stem}: dot at {c}, dropped {n} loose "1"')
            if write:
                f.write_text(s2)


def pcb(path, write):
    s = Path(path).read_text()
    lib = {}
    for d in ('Ogma2.pretty', 'Ogma2_GNSS.pretty'):
        for f in (HW / 'libraries' / d).glob('*.kicad_mod'):
            t = f.read_text(); ps = pads(t)
            m = re.search(r'\(fp_circle\s+\(center ([-\d.]+) ([-\d.]+)\)\s+\(end ([-\d.]+) [-\d.]+\)(?:(?!\(fp_).)*?\(fill yes\)\s*\(layer "F\.SilkS"', t, re.S)
            lib[f'{d[:-7]}:{f.stem}'] = (float(m.group(1)), float(m.group(2)), round(float(m.group(3)) - float(m.group(1)), 3)) if m else None
    out, i, added = [], 0, 0
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"', s):
        pass
    parts = re.split(r'(?=\n\t\(footprint ")', s)
    res = []
    for blk in parts:
        m = re.match(r'\n\t\(footprint "([^"]+)"', blk)
        if m and lib.get(m.group(1)) and 'F.SilkS' in blk + 'F.SilkS':
            back = bool(re.search(r'\(layer "B\.Cu"\)', blk[:300]))
            blk, n = drop_text(blk)
            if not re.search(r'\(fill yes\)\s*\(layer "[FB]\.SilkS"\)', blk) or n:
                x, y, r = lib[m.group(1)]
                k = blk.index('\n\t\t(pad ') + 1
                g = dot(x, y, r, 'B.SilkS' if back else 'F.SilkS').replace('\n  ', '\n\t\t').replace('\n    ', '\n\t\t\t')
                blk = blk[:k] + '\t' + g.lstrip(' ') + blk[k:] if False else blk[:k] + g.replace('  (fp_circle', '\t\t(fp_circle', 1) + blk[k:]
                added += 1
        res.append(blk)
    s = ''.join(res)
    s, g = drop_text(s)
    print(f'{path}: {added} instances marked, loose gr_text "1" removed: {g}')
    if write:
        Path(path).write_text(s)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--pcb'); ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    pcb(a.pcb, a.write) if a.pcb else library(a.write)
