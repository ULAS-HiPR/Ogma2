"""Helpers for surgical edits to native KiCad 9 schematic sheets (capture, 21 Nov 2026).

Reads and writes through sexpr.py, like the 7-8 September readable-schematics tools.
New objects get deterministic uuid5 identities so a rerun produces the same file.
"""
import copy, math, uuid
from pathlib import Path
from sexpr import Atom as A, parse, emit, children, first, walk

NS = uuid.UUID('5d0b6c1e-21b1-4c3a-9f1e-0a9e1c2a7f00')   # capture namespace, 21 Nov 2026


def ident(*parts):
    return str(uuid.uuid5(NS, '/'.join(map(str, parts))))


def num(v):
    v = round(float(v), 4)
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return A(s if s not in ('-0', '') else '0')


def el(k, *v):
    return [A(k), *v]


def fx(size=1.27, justify=None, hide=False):
    q = el('effects', el('font', el('size', num(size), num(size))))
    if justify:
        q.append(el('justify', *[A(j) for j in justify.split()]))
    if hide:
        q.append(el('hide', A('yes')))
    return q


def load(path):
    return parse(Path(path).read_text())


def save(tree, path):
    Path(path).write_text(emit(tree) + '\n')


def props(sym):
    return {p[1]: p[2] for p in children(sym, 'property')}


def symbols(tree):
    return {props(s)['Reference']: s for s in children(tree, 'symbol')}


def lib_of(tree, sym):
    libs = {s[1]: s for s in children(first(tree, 'lib_symbols'), 'symbol')}
    return libs[first(sym, 'lib_id')[1]]


def pin_positions(tree, ref):
    """Pin number -> (x, y, outward angle) in sheet coordinates (no mirror support)."""
    sym = symbols(tree)[ref]
    assert not first(sym, 'mirror'), f'{ref} is mirrored; extend pin_positions first'
    x, y, ang = map(float, first(sym, 'at')[1:4])
    th = math.radians(ang)
    out = {}
    for p in walk(lib_of(tree, sym), 'pin'):
        number = first(p, 'number')[1]
        px, py, pa = map(float, first(p, 'at')[1:4])
        out[number] = (round(x + px * math.cos(th) - py * math.sin(th), 4),
                       round(y - px * math.sin(th) - py * math.cos(th), 4), (pa + ang) % 360)
    return out


def xy(node):
    a = first(node, 'at')
    return round(float(a[1]), 4), round(float(a[2]), 4)


def wires(tree):
    out = []
    for w in children(tree, 'wire'):
        pts = first(w, 'pts')
        (a, b) = [(round(float(p[1]), 4), round(float(p[2]), 4)) for p in children(pts, 'xy')]
        out.append((w, a, b))
    return out


def on_segment(p, a, b):
    return (a[0] == b[0] == p[0] and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])) or \
           (a[1] == b[1] == p[1] and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]))


def connected_points(tree, start):
    """Every wire point reachable from start through wires (junction-free walk)."""
    ws = wires(tree)
    seen, todo, used = {start}, [start], []
    while todo:
        p = todo.pop()
        for w, a, b in ws:
            if w in used:
                continue
            if on_segment(p, a, b):
                used.append(w)
                for q in (a, b):
                    if q not in seen:
                        seen.add(q); todo.append(q)
    return seen, used


def labels_at(tree, points, kinds=('global_label', 'label', 'hierarchical_label')):
    return [l for k in kinds for l in children(tree, k) if xy(l) in points]


def global_label(text, at, angle=0, sheet='', serial=0, size=0.9):
    justify = 'left' if angle == 180 else 'right' if angle == 0 else None
    return el('global_label', text, el('shape', A('bidirectional')),
              el('at', num(at[0]), num(at[1]), num(angle)), fx(size, justify),
              el('uuid', ident(sheet, 'label', text, serial)),
              el('property', 'Intersheetrefs', '${INTERSHEET_REFS}',
                 el('at', num(at[0]), num(at[1]), num(0)), fx(1.27, hide=True)))


def wire(a, b, sheet='', serial=0):
    return el('wire', el('pts', el('xy', num(a[0]), num(a[1])), el('xy', num(b[0]), num(b[1]))),
              el('stroke', el('width', num(0)), el('type', A('default'))),
              el('uuid', ident(sheet, 'wire', a, b, serial)))


def text(value, at, sheet='', serial=0, size=1.27):
    return el('text', value, el('exclude_from_sim', A('no')), el('at', num(at[0]), num(at[1]), num(0)),
              fx(size, 'left'), el('uuid', ident(sheet, 'text', serial)))


def junction(at, sheet='', serial=0):
    return el('junction', el('at', num(at[0]), num(at[1])), el('diameter', num(0)),
              el('color', num(0), num(0), num(0), num(0)), el('uuid', ident(sheet, 'junction', at, serial)))


def no_connect(at, sheet='', serial=0):
    return el('no_connect', el('at', num(at[0]), num(at[1])), el('uuid', ident(sheet, 'nc', at, serial)))


def new_symbol(tree, template_ref, ref, at, angle=0, value=None, footprint=None, sheet_file='',
               instance_path=None, project='Croi2', extra_props=None, lib_id=None, dnp=False):
    """Copy an existing symbol of the same library part and give it a new identity."""
    src = copy.deepcopy(symbols(tree)[template_ref])
    if lib_id:
        first(src, 'lib_id')[1] = lib_id
    first(src, 'at')[1:4] = [num(at[0]), num(at[1]), num(angle)]
    first(src, 'uuid')[1] = ident(sheet_file, 'symbol', ref)
    d = first(src, 'dnp')
    if d:
        d[1] = A('yes' if dnp else 'no')
    for p in children(src, 'property'):
        if p[1] == 'Reference':
            p[2] = ref
        elif p[1] == 'Value' and value is not None:
            p[2] = value
        elif p[1] == 'Footprint' and footprint is not None:
            p[2] = footprint
        if extra_props and p[1] in extra_props:
            p[2] = extra_props[p[1]]
        first(p, 'at')[1:3] = [num(at[0] + 2.54), num(at[1] + (-1.27 if p[1] == 'Reference' else 1.27))]
    for pin in children(src, 'pin'):
        first(pin, 'uuid')[1] = ident(sheet_file, 'pin', ref, pin[1])
    inst = first(src, 'instances')
    for proj in children(inst, 'project'):
        for path in children(proj, 'path'):
            if instance_path:
                path[1] = instance_path
            first(path, 'reference')[1] = ref
    return src
