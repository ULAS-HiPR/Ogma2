"""Capture step runner: export, compare against the previous step, render.

Each step edits sheets in the working tree, then:
  export(tag)                      native netlist + ERC from KiCad 9.0.8
  check(prev, tag, expect)         the pin-net delta must equal the intended delta exactly
  erc_delta(prev, tag)             findings fixed and added since the previous step
  render(tag, sheets)              PNGs of the changed sheets for review

KiCad runs as `kc` (kicad-cli 9.0.8 inside an Ubuntu 26.04 root, repo bound at /work,
outputs at /cap). See README.md.
"""
import json, subprocess, sys, hashlib
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

REPO = Path('/home/claude/ogma2')
BOARD = REPO / 'hardware/croi2'
OUT = Path('/home/claude/capture/steps')          # bound at /cap/steps
REVIEW = Path('/mnt/user-data/outputs')


def kc(*args):
    r = subprocess.run(['kc', *args], capture_output=True, text=True)
    if r.returncode not in (0, 5):                   # 5: ERC ran and found violations
        sys.exit(f'kicad-cli failed: {args}\n{r.stdout}\n{r.stderr}')
    return r


def export(tag):
    d = OUT / tag
    d.mkdir(parents=True, exist_ok=True)
    kc('sch', 'export', 'netlist', '--format', 'kicadxml', '-o', f'/cap/steps/{tag}/net.xml', '/work/hardware/croi2/Croi2.kicad_sch')
    kc('sch', 'erc', '--format', 'json', '--severity-all', '-o', f'/cap/steps/{tag}/erc.json', '/work/hardware/croi2/Croi2.kicad_sch')
    return d


def load_net(tag):
    r = ET.parse(OUT / tag / 'net.xml').getroot()
    comps, pins = {}, {}
    for c in r.findall('components/comp'):
        p = {x.get('name'): x.get('value') for x in c.findall('property')}
        comps[c.get('ref')] = dict(value=c.findtext('value') or '', fp=c.findtext('footprint') or '',
                                   dnp='dnp' in p, sheet=c.find('sheetpath').get('names'))
    for n in r.findall('nets/net'):
        name = n.get('name')
        name = 'NC' if name.startswith('unconnected-') else name
        for x in n.findall('node'):
            pins[(x.get('ref'), x.get('pin'))] = name
    return comps, pins


def check(prev, tag, expect_pins, expect_added=(), expect_removed=(), expect_changed=None):
    """expect_pins: {(ref, pin): net or None (pin gone)}; every other pin must be unchanged."""
    ca, pa = load_net(prev)
    cb, pb = load_net(tag)
    phys = lambda c: {k for k in c if not k.startswith('#')}
    added, removed = phys(cb) - phys(ca), phys(ca) - phys(cb)
    problems = []
    if added != set(expect_added):
        problems.append(f'added {sorted(added)} != expected {sorted(expect_added)}')
    if removed != set(expect_removed):
        problems.append(f'removed {sorted(removed)} != expected {sorted(expect_removed)}')
    changed = {}
    for k in phys(ca) & phys(cb):
        for f in ('value', 'fp', 'dnp'):
            if ca[k][f] != cb[k][f]:
                changed[(k, f)] = (ca[k][f], cb[k][f])
    if expect_changed is not None and changed != expect_changed:
        problems.append(f'field changes {changed} != expected {expect_changed}')
    diff = {k: pb.get(k) for k in set(pa) | set(pb) if not k[0].startswith('#') and pa.get(k) != pb.get(k)}
    if diff != expect_pins:
        extra = {k: (pa.get(k), v) for k, v in diff.items() if expect_pins.get(k, '<unexpected>') != v}
        missing = {k: v for k, v in expect_pins.items() if diff.get(k, '<absent>') != v}
        problems.append(f'pin delta mismatch.\n  unexpected: {sorted(extra.items())[:40]}\n  missing: {sorted(missing.items())[:40]}')
    report = dict(prev=prev, tag=tag, components=(len(phys(ca)), len(phys(cb))), pins=(len(pa), len(pb)),
                  added=sorted(added), removed=sorted(removed), changed={f'{k[0]}.{k[1]}': v for k, v in changed.items()},
                  pin_changes=len(diff), problems=problems)
    (OUT / tag / 'delta.json').write_text(json.dumps(report, indent=1, default=str) + '\n')
    return report


def erc_items(tag):
    d = json.loads((OUT / tag / 'erc.json').read_text())
    return {(s['path'], v['severity'], v['type'], '; '.join(i.get('description', '') for i in v.get('items', [])))
            for s in d['sheets'] for v in s['violations']}


def erc_delta(prev, tag):
    a, b = erc_items(prev), erc_items(tag)
    return sorted(a - b), sorted(b - a), Counter(f'{x[1]}/{x[2]}' for x in b)


def render(tag, sheets, width=3000):
    svg = OUT / tag / 'svg'
    svg.mkdir(parents=True, exist_ok=True)
    kc('sch', 'export', 'svg', '--exclude-drawing-sheet', '-o', f'/cap/steps/{tag}/svg', '/work/hardware/croi2/Croi2.kicad_sch')
    out = []
    for s in sheets:
        src = svg / f'Croi2-{s}.svg'
        dst = REVIEW / f'capture-{tag}-{s}.png'
        subprocess.run(['rsvg-convert', '-w', str(width), '-b', 'white', str(src), '-o', str(dst)], check=True)
        out.append(dst)
    return out


def head_unchanged(*sheets):
    """Guard: the sheets in the working tree equal git HEAD (no manual edits pending)."""
    for s in sheets:
        p = f'hardware/croi2/{s}'
        r = subprocess.run(['git', '-C', str(REPO), 'diff', '--quiet', 'HEAD', '--', p])
        if r.returncode:
            sys.exit(f'{p} differs from HEAD; refusing to overwrite')
