# Phase 1 layout experiments (S1, 21 November 2026)

Throwaway scripts behind [the pipeline report](../../../docs/briefs/layout-pipeline.md).
They are kept so every number in the report can be rerun. Nothing here writes a real board.

Environment: KiCad 9.0.8 in the Ubuntu 26.04 chroot, with `/work` bound to the repo and
`/lab` to a scratch folder holding these scripts (paths in the scripts use `/lab`).
- Java: `openjdk-25-jre-headless` (26.04 archive).
- Freerouting 2.5.0: `freerouting-2.5.0.jar` from the GitHub release, SHA-256
  `f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7`, run with
  `--usage_and_diagnostic_data.disable_analytics=true` (it tries to phone home otherwise).
- kicad-python 0.8.0 (PyPI), `xvfb`, `x11-apps` for the IPC test.
- KiCadRoutingTools: github.com/drandyhaas/KiCadRoutingTools at 1577fa3 (MIT),
  router v0.24.1 built from source with `cargo` (26.04 archive).

| Script | Test |
| --- | --- |
| `engine/` | netlist reader, board builder (pcbnew SWIG), greedy placer, scripted copper (fanout, fixed routes) |
| `tb1.py` | T1: TB1 from Burrito's netlist (flight MCU, CAN, USB sheets), placed, GND zone, filled |
| `t2_sexpr.py` | T2: S-expression round trip and edits (stackup, move, track, via) |
| `fr_route.py` | T4: DSN export, Freerouting headless, SES import |
| `tb1_hybrid.py` | T5: scripted critical nets and GND fanout locked, then Freerouting |
| `tb1_pre.py` | T5b: the same pre-route state, saved for KiCadRoutingTools |
| `t6_ipc.sh` | T6: pcbnew under Xvfb, driven over the IPC API |
| `tb2.py` | TB2: all of Burrito, rough banded placement, for router capacity |
| `stats.py`, `drcsum.py` | track statistics; DRC summary |
