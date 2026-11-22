# Phase 2 scripts (S2, 22 November 2026)

The computed figures in [the routing brief](../../../docs/briefs/layout-brief.md).
None of them writes a board.

| Script | Gives | Runs in |
| --- | --- | --- |
| `inventory.py` | Parts, courtyard areas per sheet, connectors and large parts, from the step-9 netlist and the footprints. Writes JSON (`hardware/croi2/output/layout/inventory.json`, git-ignored) | The KiCad 9.0.8 chroot, with `/work` bound to the repo (see `../phase1/README.md`) |
| `impedance_check.py` | IPC-2141 cross-check of JLC's calculator widths | Plain Python 3 |
| `trace_width.py` | IPC-2152 baseline widths per current (smps.us fit) | Plain Python 3 |
