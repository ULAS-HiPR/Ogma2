#!/usr/bin/env python3
"""One-off (27 Nov 2026, D-27Nov.2): bring full-expected-pins.json to the squashed sheets without a KiCad netlist.
Takes the committed expected pins (from KiCad's own netlist), drops the removed parts, renames the folded nets and
frees the pins whose far side is gone. Verified against tools/netcheck.py --diff. Replace by
`check_schematic_full.py --write-expected` on a fresh KiCad export when one exists."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import netcheck as N
from apply_power_squash import RELABEL, FREE
HW = Path(__file__).resolve().parents[1]
b, _ = N.named(Path(sys.argv[1])); N.ALLN.clear(); a, _ = N.named(HW)
removed = {p[0] for p in b} - {p[0] for p in a}
exp = json.loads((HW / 'full-expected-pins.json').read_text())
out = {}
for ref, pins in exp.items():
    if ref in removed:
        continue
    out[ref] = {p: (None if n is None or n in FREE else RELABEL.get(n, n)) for p, n in pins.items()}
(HW / 'full-expected-pins.json').write_text(json.dumps(out, indent=1) + '\n')
print('removed', len(removed), sorted(removed, key=lambda r: (r.rstrip('0123456789'), int(''.join(c for c in r if c.isdigit()) or 0))))
print('kept', len(out))
