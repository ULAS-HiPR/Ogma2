#!/usr/bin/env python3
"""Rename nets so KiCad detects the CAN and USB differential pairs, and drop the old
board names (Croi, Foinse) from the net names, sheet names and netlists.

    python3 tools/rename_nets.py            # dry run: counts per file, changes nothing
    python3 tools/rename_nets.py --apply    # rewrite the files and git mv the two sheets

Close KiCad first. It is idempotent: running it again changes nothing.
Plain text replacement. It does not run KiCad, so run ERC and DRC afterwards.

Differential pairs (KiCad pairs nets whose names end in + and -):
    CAN_H / CAN_L              -> CAN+ / CAN-
    CAN2_H / CAN2_L            -> CAN2+ / CAN2-
    USB_DP / USB_DM            -> USB_D+ / USB_D-
    USB_DP_CONN / USB_DM_CONN  -> USB_CONN_D+ / USB_CONN_D-

Board names: CROI -> BURRITO and FOINSE -> CHURRO inside identifiers (VBAT_CROI_INPUT,
FOINSE_AUX_3V3, ...), the two sheet names (07-foinse-aux, f03-croi-interface), and, in the
two boards' files (schematics, PCBs, netlists, checks; not the .md notes), the words Croi and Foinse in titles and notes.
"Croi2" and "Foinse2" (project and file names) are left alone.

Never touched: history/, archive/, libraries/ (vendor and library names such as the STM32
USB_DP alternate function), project-log.md, decisions.md, HANDOFF.md (append-only records).
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DIFF = {
    'CAN_H': 'CAN+', 'CAN_L': 'CAN-', 'CAN2_H': 'CAN2+', 'CAN2_L': 'CAN2-',
    'USB_DP': 'USB_D+', 'USB_DM': 'USB_D-',
    'USB_DP_CONN': 'USB_CONN_D+', 'USB_DM_CONN': 'USB_CONN_D-',
}
SHEETS = {'07-foinse-aux': '07-churro-aux', 'f03-croi-interface': 'f03-burrito-interface'}
SHEET_FILES = [('hardware/croi2/07-foinse-aux.kicad_sch', 'hardware/croi2/07-churro-aux.kicad_sch'),
               ('hardware/foinse2/f03-croi-interface.kicad_sch', 'hardware/foinse2/f03-burrito-interface.kicad_sch')]

STRICT = r'(?<![A-Za-z0-9_]){}(?![A-Za-z0-9_])'
RE_DIFF = re.compile('|'.join(STRICT.format(re.escape(k)) for k in sorted(DIFF, key=len, reverse=True)))
RE_SHEET = re.compile('|'.join(re.escape(k) for k in SHEETS))
# identifier words: an upper-case CROI or FOINSE not glued to letters or digits (underscore is a separator)
RE_UP = re.compile(r'(?<![A-Za-z0-9])(CROI|FOINSE)(?![A-Za-z0-9])')
# prose words, schematics and PCBs of the two boards only
RE_PROSE = re.compile(r'(?<![A-Za-z0-9])(Croi|Foinse)(?![A-Za-z0-9í])')
UP = {'CROI': 'BURRITO', 'FOINSE': 'CHURRO'}
PROSE = {'Croi': 'Burrito', 'Foinse': 'Churro'}

SKIP_DIRS = {'.git', 'history', 'archive', 'libraries', '__pycache__', 'node_modules'}
SKIP_FILES = {'project-log.md', 'decisions.md', 'HANDOFF.md', 'rename_nets.py'}
TEXT_EXT = {'.kicad_sch', '.kicad_pcb', '.kicad_pro', '.kicad_dru', '.kicad_prl', '.json', '.md', '.py',
            '.xml', '.dsn', '.csv', '.txt'}
# strings that carry vendor names, not nets: leave them as they are
RE_KEEP = re.compile(r'\((?:alternate|pinfunction)\s+"[^"]*"\)?')


def sub_text(s, prose):
    def one(seg):
        seg = RE_DIFF.sub(lambda m: DIFF[m.group(0)], seg)
        seg = RE_SHEET.sub(lambda m: SHEETS[m.group(0)], seg)
        seg = RE_UP.sub(lambda m: UP[m.group(1)], seg)
        if prose:
            seg = RE_PROSE.sub(lambda m: PROSE[m.group(1)], seg)
        return seg
    # protect (alternate "...") and (pinfunction "...")
    out, last = [], 0
    for m in RE_KEEP.finditer(s):
        out.append(one(s[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(one(s[last:]))
    return ''.join(out)


def strip_lib_symbols(s):
    """Return (before, block, after) around the top-level (lib_symbols ...) block, or None."""
    i = s.find('(lib_symbols')
    if i < 0:
        return None
    depth, j = 0, i
    in_str = False
    while j < len(s):
        c = s[j]
        if in_str:
            if c == '\\':
                j += 1
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    return s[:i], s[i:j + 1], s[j + 1:]
        j += 1
    return None


def transform(path, s):
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    board = rel.startswith(('hardware/croi2/', 'hardware/foinse2/'))
    prose = board and not path.endswith('.md')
    if path.endswith('.kicad_sch'):
        parts = strip_lib_symbols(s)
        if parts:
            b, blk, a = parts
            return sub_text(b, prose) + blk + sub_text(a, prose)
    return sub_text(s, prose)


def files():
    for top in ('hardware/croi2', 'hardware/foinse2', 'tools', 'docs', 'interfaces'):
        base = os.path.join(ROOT, top)
        for dp, dn, fn in os.walk(base):
            dn[:] = [d for d in dn if d not in SKIP_DIRS]
            for f in fn:
                if f in SKIP_FILES or os.path.splitext(f)[1] not in TEXT_EXT:
                    continue
                yield os.path.join(dp, f)
    for f in ('current-system.md', 'README.md', 'AGENTS.md', 'hardware/README.md'):
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    changed = 0
    for p in sorted(set(files())):
        try:
            s = open(p, encoding='utf-8').read()
        except (UnicodeDecodeError, OSError):
            continue
        t = transform(p, s)
        if t != s:
            changed += 1
            n = sum(1 for x, y in zip(re.split(r'\n', s), re.split(r'\n', t)) if x != y) if s.count('\n') == t.count('\n') else -1
            print(f'{"edit" if a.apply else "would edit"}  {os.path.relpath(p, ROOT)}  ({n} lines)')
            if a.apply:
                open(p, 'w', encoding='utf-8').write(t)
    if a.apply:
        for old, new in SHEET_FILES:
            if os.path.exists(os.path.join(ROOT, old)):
                subprocess.check_call(['git', '-C', ROOT, 'mv', old, new])
                print('git mv', old, '->', new)
    print(f'{changed} files {"changed" if a.apply else "would change"}')


if __name__ == '__main__':
    sys.exit(main())
