"""Text passes over a saved board and its project: the stackup SWIG can't set, deterministic UUIDs,
net classes and board rules in the .kicad_pro, custom rules in the .kicad_dru."""
import json
import uuid
from pathlib import Path
from . import sexpr as S

A = S.Atom
NS = uuid.UUID('6f1d2a6e-0b6b-4a43-9a1e-0a4b8f3c2d11')      # fixed namespace for board item UUIDs


def stackup_layers(spec):
    """spec: list of (name, type, thickness_mm, epsilon_r or None, material or None)."""
    out = [A('stackup')]
    for name, typ, th, er, mat in spec:
        lay = [A('layer'), name, [A('type'), typ]]
        if th is not None:
            lay.append([A('thickness'), A(f'{th:g}')])
        if mat:
            lay += [[A('material'), mat], [A('epsilon_r'), A(f'{er:g}')], [A('loss_tangent'), A('0.02')]]
        out.append(lay)
    out += [[A('copper_finish'), 'ENIG'], [A('dielectric_constraints'), A('no')]]
    return out


def finish(path, stack, tag):
    """Insert the stackup and renumber every (uuid ...) in document order, so a rebuild is byte-identical."""
    p = Path(path)
    tree = S.parse(p.read_text())
    setup = S.first(tree, 'setup')
    for old in S.children(setup, 'stackup'):
        setup.remove(old)
    setup.insert(1, stackup_layers(stack))
    canonical(tree)
    n = 0
    for node in S.walk(tree, 'uuid'):
        node[1] = str(uuid.uuid5(NS, f'{tag}:{n}'))
        n += 1
    p.write_text(S.emit(tree) + '\n')
    return n


TOP = ('footprint', 'zone', 'gr_line', 'gr_arc', 'gr_circle', 'gr_rect', 'gr_poly', 'gr_text', 'segment', 'arc', 'via')
INNER = ('fp_line', 'fp_arc', 'fp_circle', 'fp_rect', 'fp_poly', 'fp_text')   # pads keep the library's order


def _key(node):
    """Sort key: the node's text without its uuids (footprints by reference first)."""
    def strip(n):
        return [strip(x) if isinstance(x, list) else x for x in n if not (isinstance(x, list) and x and x[0] == 'uuid')]
    ref = ''
    if node[0] == 'footprint':
        ref = next((p[2] for p in S.children(node, 'property') if p[1] == 'Reference'), '')
    return (node[0], ref, S.emit(strip(node)))


def _resort(parent, kinds):
    slots = [i for i, x in enumerate(parent) if isinstance(x, list) and x and x[0] in kinds]
    items = sorted((parent[i] for i in slots), key=_key)
    for i, item in zip(slots, items):
        parent[i] = item


def canonical(tree):
    """KiCad orders items by their random UUIDs on save; put them in a fixed order before renumbering."""
    for fp in S.children(tree, 'footprint'):
        _resort(fp, INNER)
    _resort(tree, TOP)


def project_rules(pro_path, classes, patterns, rules):
    """Write net classes, their pattern assignments and the board minimums into the .kicad_pro (JSON)."""
    p = Path(pro_path)
    d = json.loads(p.read_text())
    ns = d['net_settings']
    base = dict(ns['classes'][0])
    out = []
    for c in classes:
        e = dict(base)
        e.update(c)
        out.append(e)
    ns['classes'] = out
    ns['netclass_patterns'] = [{'netclass': c, 'pattern': pat} for c, pat in patterns]
    ns['netclass_assignments'] = None
    d['board']['design_settings']['rules'].update(rules)
    p.write_text(json.dumps(d, indent=2) + '\n')


def dru(path, text):
    Path(path).write_text(text)
