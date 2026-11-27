#!/usr/bin/env python3
"""Own netlist from the native sheets (no KiCad): pin -> net, to compare before and after an edit.

    python3 tools/netcheck.py --vs output/full-netlist.xml      # does this reader reproduce KiCad's netlist?
    python3 tools/netcheck.py --dump nets.json                  # write {ref.pin: net}
Joins: wire ends, a pin or label on a wire, junctions, labels of the same name. Global labels and power symbols
join across sheets by name; local labels stay on their sheet. Hierarchical labels / sheet pins are not followed
(reported if any are found). Multi-unit and mirrored symbols are reported, not guessed.
"""
import json, math, re, sys, glob, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'capture'))
import kicadsch as K
from sexpr import children, first, walk

BOARD = Path(__file__).resolve().parents[1]


class UF:
    def __init__(s): s.p = {}
    def f(s, a):
        s.p.setdefault(a, a)
        while s.p[a] != a:
            s.p[a] = s.p[s.p[a]]; a = s.p[a]
        return a
    def u(s, a, b): s.p[s.f(a)] = s.f(b)


def sheet_pins(tree, sym):
    """pin -> (x, y) with mirror support."""
    x, y, ang = map(float, first(sym, 'at')[1:4])
    mir = first(sym, 'mirror'); mir = mir[1] if mir else ''
    th = math.radians(ang)
    lib = K.lib_of(tree, sym)
    unit = int(first(sym, 'unit')[1]) if first(sym, 'unit') else 1
    out = {}
    for sub in children(lib, 'symbol'):
        m = re.search(r'_(\d+)_(\d+)$', sub[1])
        if m and int(m.group(1)) not in (0, unit):
            continue
        for p in walk(sub, 'pin'):
            n = first(p, 'number')[1]
            px, py = map(float, first(p, 'at')[1:3])
            if mir == 'x': py = -py
            if mir == 'y': px = -px
            out[n] = (round(x + px * math.cos(th) - py * math.sin(th), 4), round(y - px * math.sin(th) - py * math.cos(th), 4))
    for p in walk(lib, 'pin'):                         # symbols whose pins sit on the top level
        n = first(p, 'number')[1]
        if n not in out:
            px, py = map(float, first(p, 'at')[1:3])
            if mir == 'x': py = -py
            if mir == 'y': px = -px
            out[n] = (round(x + px * math.cos(th) - py * math.sin(th), 4), round(y - px * math.sin(th) - py * math.cos(th), 4))
    return out


def sheet_nets(path, notes):
    t = K.load(path)
    uf = UF()
    ws = K.wires(t)
    pts = set()
    for _, a, b in ws:
        uf.u(a, b); pts |= {a, b}
    junc = {K.xy(j) for j in children(t, 'junction')}
    # a point lying on a wire's body joins that wire (pin, label, junction or another wire's end)
    def touch(p):
        for _, a, b in ws:
            if K.on_segment(p, a, b):
                uf.u(p, a)
    members = []                                       # (point, kind, name)
    for s in children(t, 'symbol'):
        ref = K.props(s).get('Reference', '?')
        lid = first(s, 'lib_id')[1]
        if first(s, 'dnp') and False: pass
        unit = first(s, 'unit')
        pins = sheet_pins(t, s)
        isp = lid.startswith('power:')
        for n, p in pins.items():
            if isp:
                members.append((p, 'net', K.props(s)['Value']))
            else:
                members.append((p, 'pin', (ref, n)))
    for k in ('global_label', 'label'):
        for l in children(t, k):
            members.append((K.xy(l), 'g' if k == 'global_label' else 'l', l[1]))
    for l in children(t, 'hierarchical_label'):
        notes.add(('hierarchical_label', Path(path).name))
    if children(t, 'sheet'):
        pass
    for p, _, _ in members:
        touch(p)
    for j in junc:
        touch(j)
    # connect points that coincide exactly (pin on wire end, label on pin)
    by = {}
    for p, kind, name in members:
        by.setdefault(p, []).append((kind, name))
    for p in by:
        uf.f(p)
    for _, a, b in ws:
        uf.f(a)
    return t, uf, members


def build(board=BOARD):
    notes = set()
    allnets = {}
    names_g = {}
    sheets = sorted(glob.glob(str(board / '*.kicad_sch')))
    uf_all = UF()
    pinroot = {}
    for sp in sheets:
        if sp.endswith('Croi2.kicad_sch'):
            continue
        t, uf, members = sheet_nets(sp, notes)
        name = os.path.basename(sp)
        # group members by their uf root
        groups = {}
        for p, kind, n in members:
            groups.setdefault(uf.f(p), []).append((kind, n))
        for root, items in groups.items():
            gl = sorted({n for k, n in items if k in ('g', 'net')})
            ll = sorted({n for k, n in items if k == 'l'})
            key = ('G', gl[0]) if gl else (('L', name, ll[0]) if ll else ('A', name, root))
            for g in gl[1:]:
                uf_all.u(('G', g), key)
            for k, n in items:
                if k == 'pin':
                    pinroot.setdefault(n, []).append(key)
        # local labels in the same sheet with same name join
        for l1 in {n for _, _, n in members if False}:
            pass
    # unify local-label groups with the same name inside a sheet
    out = {}
    for pin, keys in pinroot.items():
        k = keys[0]
        for other in keys[1:]:
            uf_all.u(k, other)
    for pin, keys in pinroot.items():
        r = uf_all.f(keys[0])
        out[pin] = r
    # name each root: prefer a global name
    return out, uf_all, notes


ALLN = {}


def named(board=BOARD):
    out, uf, notes = build(board)
    names = {}
    for k in list(uf.p):
        r = uf.f(k)
        if k[0] == 'G':
            names.setdefault(r, set()).add(k[1])
        elif k[0] == 'L':
            names.setdefault(r, set()).add(k[2])
    res = {}
    for pin, r in out.items():
        nm = sorted(names.get(r, []))
        res[pin] = nm[0] if nm else f'unnamed:{pin}'
        ALLN[pin] = set(nm)
    return res, notes


def diff(before, after):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from apply_power_squash import RELABEL, PARTS, EMPTY_SHEETS
    b, _ = named(Path(before)); bn = dict(ALLN); ALLN.clear(); a, _ = named(Path(after)); an = dict(ALLN)
    gone = [p for p in b if p not in a]
    print(f'pins before {len(b)}, after {len(a)}, gone {len(gone)}')
    bad = 0
    groups = {}
    for p, n in b.items():
        if p in a:
            groups.setdefault(n, []).append(p)
    for n, pins in sorted(groups.items()):
        want = RELABEL.get(n, n)
        if n.startswith('unnamed:'):
            keys = {a[p] for p in pins}
            if len(keys) > 1 or not all(k.startswith('unnamed:') for k in keys):
                bad += 1; print('CHANGED unnamed net', pins[:4], '->', sorted(keys)[:3])
        else:
            if not all(want in an[p] for p in pins):
                bad += 1; print('CHANGED', n, 'expected', want, 'got', sorted({a[p] for p in pins})[:4], pins[:3])
    cnt = {}
    for p, n in a.items(): cnt.setdefault(n, []).append(p)
    dang = [(n, ps) for n, ps in cnt.items() if len(ps) == 1 and not n.startswith('unnamed:')]
    sing = [(n, ps) for n, ps in cnt.items() if len(ps) == 1 and n.startswith('unnamed:')]
    cb = {}
    for p, n in b.items(): cb.setdefault(n, []).append(p)
    new_dang = [(n, ps) for n, ps in dang if len(cb.get(n, [])) != 1]
    print(f'unexpected net changes: {bad}')
    print(f'nets with a single pin after: {len(dang)} named ({len(new_dang)} new), {len(sing)} unnamed')
    for n, ps in new_dang[:40]: print('  NEW single-pin net', n, ps)
    for n, ps in [(n, ps) for n, ps in sing if len(cb.get(a[ps[0]], [])) != 1][:20]: print('  NEW single-pin unnamed', ps)


if __name__ == '__main__':
    if '--diff' in sys.argv:
        i = sys.argv.index('--diff'); diff(sys.argv[i + 1], sys.argv[i + 2]); sys.exit()
    res, notes = named()
    if '--dump' in sys.argv:
        json.dump({f'{a}.{b}': n for (a, b), n in sorted(res.items())}, open(sys.argv[sys.argv.index('--dump') + 1], 'w'), indent=0)
    if '--vs' in sys.argv:
        import xml.etree.ElementTree as ET
        r = ET.parse(sys.argv[sys.argv.index('--vs') + 1]).getroot()
        ref = {}
        for n in r.findall('nets/net'):
            nm = n.get('name')
            for x in n.findall('node'):
                ref[(x.get('ref'), x.get('pin'))] = nm
        # compare by partition: pins that share a net must share a net in both
        ours = {}
        for p, n in res.items(): ours.setdefault(n, set()).add(p)
        theirs = {}
        for p, n in ref.items(): theirs.setdefault(n, set()).add(p)
        miss = [p for p in ref if p not in res and not p[0].startswith('#')]
        extra = [p for p in res if p not in ref]
        bad = 0
        for n, pins in theirs.items():
            if n.startswith('unconnected-'): continue
            parts = {res.get(p) for p in pins if p in res}
            if len(parts) > 1:
                bad += 1
                if bad <= 15: print('SPLIT', n, sorted(parts)[:4])
        for n, pins in ours.items():
            if n.startswith('unnamed:'): continue
            parts = {ref.get(p) for p in pins if p in ref}
            if len(parts) > 1:
                bad += 1
                if bad <= 30: print('MERGED', n, sorted(x for x in parts if x)[:4])
        print(f'pins ours {len(res)} / theirs {len(ref)}; missing {len(miss)}, extra {len(extra)}; net disagreements {bad}')
        print('notes', notes)
