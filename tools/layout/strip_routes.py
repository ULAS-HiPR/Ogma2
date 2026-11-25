"""strip_routes.py BOARD [--out OUT]: every track, arc and via removed except the fire copper, and everything unlocked
(Seán, 25 Nov 2026: "delete all routing now ... and unlock everything"; keep the placement, the rules, the fire copper
and the copper zones).

    python3 tools/layout/strip_routes.py hardware/croi2/Croi2.kicad_pcb

Works on the file's text, so it reads a board saved by KiCad 10 (which KiCad 9's pcbnew can't load) and changes
nothing else in it. Kept: tracks, arcs and vias of the FIRE class (PYRO*_ENERGY, OUTPUT*_HIGH, OUTPUT*_LOW) and the
PYRO_RAIL class (the arm feeds and armed rails), as spec.PATTERNS names them; every zone and rule area. Every
`(locked yes)` goes. The zone fills are left as saved: refill in KiCad (B) after opening.
"""
import argparse
import fnmatch
import re
from collections import Counter

KEEP = ([f'PYRO{i}_ENERGY' for i in (1, 2, 3)] + [f'OUTPUT{i}_{s}' for i in (1, 2, 3) for s in ('HIGH', 'LOW')]
        + ['*RECOVERY_ARM_FEED', '*STAGING_ARM_FEED', 'RECOVERY_ARMED_VBAT', 'STAGING_ARMED_VBAT'])
NET = re.compile(r'\(net "([^"]*)"\)|\(net (\d+)\)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('board')
    ap.add_argument('--out')
    a = ap.parse_args()
    lines = open(a.board, encoding='utf-8').read().split('\n')
    out, kept, gone, unlocked, i = [], Counter(), Counter(), 0, 0
    while i < len(lines):
        l = lines[i]
        kind = next((k for k in ('segment', 'arc', 'via') if l == f'\t({k}'), None)
        if kind:
            j = i
            while lines[j] != '\t)':
                j += 1
            block = lines[i:j + 1]
            m = next((NET.search(b) for b in block if NET.search(b)), None)
            net = (m.group(1) or '') if m else ''
            short = net.rsplit('/', 1)[-1]
            if any(fnmatch.fnmatchcase(short, p) for p in KEEP):
                kept[kind] += 1
                out += [b for b in block if b.strip() != '(locked yes)']
            else:
                gone[kind] += 1
            i = j + 1
            continue
        if l.strip() == '(locked yes)':
            unlocked += 1
        else:
            out.append(l)
        i += 1
    open(a.out or a.board, 'w', encoding='utf-8').write('\n'.join(out))
    print(f'removed {dict(gone)}; kept fire copper {dict(kept)}; (locked yes) removed: {unlocked + 0}')


if __name__ == '__main__':
    main()
