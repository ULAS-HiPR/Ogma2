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


# ---------------------------------------------------------------- new parts

KICAD_SYMBOLS = '/opt/resolute/usr/share/kicad/symbols'      # official KiCad 9.0.7 libraries


def import_lib(tree, lib_id, source):
    """Embed lib_id in the sheet's lib_symbols (no-op if present).

    source: the .kicad_sym library the project's sym-lib-table resolves lib_id to,
    so the embedded copy matches it (ERC lib_symbol_mismatch)."""
    libs = first(tree, 'lib_symbols')
    if any(s[1] == lib_id for s in children(libs, 'symbol')):
        return
    name = lib_id.split(':', 1)[1]
    found = [s for s in children(load(source), 'symbol') if s[1] == name]
    assert found, f'{lib_id} not in {source}'
    sym = copy.deepcopy(found[0])
    assert not first(sym, 'extends'), f'{lib_id} is derived; flatten it first'
    sym[1] = lib_id
    libs.append(sym)


def vendor_symbol(lib_path, name, source):
    """Copy symbol `name` from an official library into a vendored .kicad_sym (no-op if present)."""
    lib = load(lib_path)
    if any(s[1] == name for s in children(lib, 'symbol')):
        return False
    sym = copy.deepcopy([s for s in children(load(source), 'symbol') if s[1] == name][0])
    tail = [i for i, x in enumerate(lib) if isinstance(x, list) and x and x[0] == 'symbol'][-1]
    lib.insert(tail + 1, sym)
    save(lib, lib_path)
    return True


def lib_symbol(tree, lib_id):
    return {s[1]: s for s in children(first(tree, 'lib_symbols'), 'symbol')}[lib_id]


def lib_pins(tree, lib_id):
    return [first(p, 'number')[1] for p in walk(lib_symbol(tree, lib_id), 'pin')]


def prop(name, value, at, angle=0, hide=True, justify=None, size=1.27):
    return el('property', name, value, el('at', num(at[0]), num(at[1]), num(angle)), fx(size, justify, hide))


def sheet_path(tree):
    """The sheet's instance path, read from an existing symbol on it."""
    for s in children(tree, 'symbol'):
        for p in walk(s, 'path'):
            return p[1]


def add(tree, node):
    """Insert before the trailing embedded_fonts / sheet_instances, if any."""
    tail = [i for i, x in enumerate(tree) if isinstance(x, list) and x and x[0] in ('embedded_fonts', 'sheet_instances')]
    tree.insert(tail[0] if tail else len(tree), node)
    return node


def make_symbol(tree, lib_id, ref, at, angle=0, value='', footprint='', sheet='', extra=None,
                dnp=False, ref_at=None, val_at=None, field_angle=0, justify='left', hide_value=False,
                project='Croi2'):
    """Place a new symbol in the house style of the readable sheets; returns its pin positions."""
    x, y = at
    lp = {p[1]: p[2] for p in children(lib_symbol(tree, lib_id), 'property')}
    ref_at = ref_at or (x + 3.81, y - 1.27)
    val_at = val_at or (x + 3.81, y + 1.27)
    s = el('symbol', el('lib_id', lib_id), el('at', num(x), num(y), num(angle)), el('unit', num(1)),
           el('in_bom', A('yes')), el('on_board', A('yes')), el('dnp', A('yes' if dnp else 'no')),
           el('uuid', ident(sheet, 'symbol', ref)),
           prop('Reference', ref, ref_at, field_angle, hide=False, justify=justify, size=1.016),
           prop('Value', value, val_at, field_angle, hide=hide_value, justify=justify, size=1.016),
           prop('Footprint', footprint, at), prop('Datasheet', lp.get('Datasheet', '~'), at),
           prop('Description', lp.get('Description', ''), at))
    for k in ('ki_keywords', 'ki_fp_filters'):
        if k in lp:
            s.append(prop(k, lp[k], at))
    for k, v in (extra or {}).items():
        s.append(prop(k, v, at))
    s.append(el('instances', el('project', project, el('path', sheet_path(tree), el('reference', ref), el('unit', num(1))))))
    for p in lib_pins(tree, lib_id):
        s.append(el('pin', p, el('uuid', ident(sheet, 'pin', ref, p))))
    add(tree, s)
    return pin_positions(tree, ref)


def local_label(text_, at, angle=0, sheet='', serial=0):
    justify = 'right bottom' if angle in (180, 270) else 'left bottom'
    return el('label', text_, el('at', num(at[0]), num(at[1]), num(angle)), fx(1.016, justify),
              el('uuid', ident(sheet, 'llabel', text_, serial)))


def path(tree, pts, sheet, tag):
    """Wires along a polyline of points (each consecutive pair one segment)."""
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        add(tree, wire(a, b, sheet, f'{tag}.{i}'))


def remove(tree, pred):
    """Drop top-level nodes matching pred; returns how many."""
    before = len(tree)
    tree[:] = [x for x in tree if not (isinstance(x, list) and x and pred(x))]
    return before - len(tree)


def move_symbol(sym, at, angle=None):
    """Translate a placed symbol and its fields to `at` (fields keep their offsets)."""
    a = first(sym, 'at')
    dx, dy = at[0] - float(a[1]), at[1] - float(a[2])
    a[1:3] = [num(at[0]), num(at[1])]
    if angle is not None:
        a[3] = num(angle)
    for p in children(sym, 'property'):
        pa = first(p, 'at')
        pa[1:3] = [num(float(pa[1]) + dx), num(float(pa[2]) + dy)]
    return sym


def clone_symbol(tree, template_ref, ref, at, sheet='', props_=None):
    """Copy a placed symbol (same sheet) to a new reference and position; props_ sets or adds fields."""
    s = move_symbol(copy.deepcopy(symbols(tree)[template_ref]), at)
    first(s, 'uuid')[1] = ident(sheet, 'symbol', ref)
    pr = {p[1]: p for p in children(s, 'property')}
    pr['Reference'][2] = ref
    for k, v in (props_ or {}).items():
        if k in pr:
            pr[k][2] = v
        else:
            pins_at = len(s) - sum(1 for x in s if isinstance(x, list) and x and x[0] in ('instances', 'pin'))
            s.insert(pins_at, prop(k, v, at))
    for p in walk(s, 'path'):
        first(p, 'reference')[1] = ref
    for pin in children(s, 'pin'):
        first(pin, 'uuid')[1] = ident(sheet, 'pin', ref, pin[1])
    add(tree, s)
    return pin_positions(tree, ref)
