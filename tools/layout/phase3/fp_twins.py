"""Footprint audit aid: for each board-local Ogma2* footprint, find KiCad library footprints with the
same copper pads (number, shape type ignored, centre and size within 0.01 mm, rotation-normalised).
Usage: python3 fp_twins.py BOARD_LIB_DIR KICAD_FOOTPRINTS_DIR  -> JSON on stdout.
"""
import sys, os, re, json, math
PAD = re.compile(r'\(pad\s+"([^"]*)"\s+(\w+)\s+(\w+)\s*\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)\s*\(size\s+([-\d.]+)\s+([-\d.]+)\)(.*?)\(layers\s+([^)]*)\)', re.S)

def pads(text):
    out = []
    for m in PAD.finditer(text):
        num, kind, shape, x, y, rot, w, h, mid, layers = m.groups()
        if 'Cu' not in layers or kind == 'np_thru_hole':
            continue
        w, h = float(w), float(h)
        if rot and round(float(rot)) % 180 == 90:
            w, h = h, w
        out.append((num, round(float(x), 2), round(float(y), 2), round(w, 2), round(h, 2), kind))
    return tuple(sorted(out))

def key(p):
    return (len(p), tuple(sorted({q[0] for q in p})))

board, kicad = sys.argv[1], sys.argv[2]
mine = {}
for lib in ('Ogma2.pretty', 'Ogma2_GNSS.pretty'):
    for f in sorted(os.listdir(os.path.join(board, lib))):
        mine[f'{lib[:-7]}:{f[:-10]}'] = pads(open(os.path.join(board, lib, f)).read())
index = {}
for lib in os.listdir(kicad):
    d = os.path.join(kicad, lib)
    if not lib.endswith('.pretty'):
        continue
    for f in os.listdir(d):
        try:
            p = pads(open(os.path.join(d, f)).read())
        except Exception:
            continue
        index.setdefault(key(p), []).append((f'{lib[:-7]}:{f[:-10]}', p))
res = {}
for name, p in mine.items():
    twins = [n for n, q in index.get(key(p), []) if q == p]
    near = []
    if not twins:
        for n, q in index.get(key(p), []):
            if len(q) == len(p) and all(a[0] == b[0] and abs(a[1]-b[1]) < 0.06 and abs(a[2]-b[2]) < 0.06 for a, b in zip(p, q)):
                dw = max(max(abs(a[3]-b[3]), abs(a[4]-b[4])) for a, b in zip(p, q))
                near.append((n, round(dw, 3)))
    res[name] = {'pads': len(p), 'twins': twins[:4], 'near_same_centres': sorted(near, key=lambda t: t[1])[:3]}
json.dump(res, sys.stdout, indent=1)
