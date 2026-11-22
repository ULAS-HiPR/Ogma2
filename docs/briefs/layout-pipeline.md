# Layout pipeline: phase 1 result (S1)

**21 November 2026.** The test of every realistic way to script Burrito's and
Churro's layout, and the pipeline it recommends. Seán picked the recommended hybrid on 22 Nov (D-22Nov.1;
D-21Nov.21; [layout plan](layout-plan.md) section 3).

Each figure below is from a run on this machine, unless marked
*(source)*. The scripts that produced them are in
[tools/layout/phase1](../../tools/layout/phase1/README.md), so
every figure can be rerun.

## Recommendation

**A hybrid pipeline, all in the repo and rerunnable from the netlist:**

1. **`pcbnew` Python (SWIG, KiCad 9.0.8, pinned in the chroot)** builds the board:
   - footprints with their schematic UUID paths, values, DNP and nets;
   - the outline, the holes, the net classes and rules;
   - the placement, from our own placer and a per-board spec;
   - the zones and their fill.
2. **Our S-expression pass** (the repo's `sexpr.py`, already used for capture)
   writes what SWIG can't reach:
   - the stackup;
   - deterministic UUIDs, so each rebuild is byte-identical.
3. **Scripted critical copper**, locked:
   - crystals, RF lines, pairs and power paths;
   - the plane fanout (a via per GND pad).
4. **KiCadRoutingTools** routes everything else. It works on the file and leaves
   locked copper alone. Its output is stored in the repo and replayed, so a
   rebuild doesn't depend on rerunning it.
5. **Our checker, then `kicad-cli`:** DRC (the gate), schematic parity,
   per-layer renders, 3D render and the fab files.

Freerouting 2.5.0 stays wired in as the fallback router.

**Why:** on the same cut of Burrito (TB1, 105 parts):
- KiCadRoutingTools finished every connection, with no KiCad DRC copper error.
- It kept its widths exactly and left the L2 GND plane unbroken when run alone.
- Two runs gave the same board.
- After our scripted critical nets and fanout, it kept all 172 locked items
  unchanged.
- Freerouting either routed signals across the L2 GND plane, or, with L2
  declared a plane, left 50 connections open. In every run it narrowed some
  tracks to 0.075 mm, below JLC's 0.09 mm minimum.

**Downside:**
- KiCadRoutingTools is young: one author, MIT licence, router v0.24.1, commits
  daily. Its behaviour can change between commits. So we pin a commit, store its
  output in the repo, and judge every result with KiCad's own DRC and our checker,
  never its self-report.
- At its default 0.05 mm grid, the whole-board route ran out of memory on this
  8 GB machine, killed at 5–6 GB, twice. At a 0.1 mm grid it fits, at about 3 GB.

**Alternative:** the same hybrid with Freerouting as the router. On TB1 it left
1 connection open and 2 tracks narrowed to 0.075 mm, so it needs a widening and
repair pass after it.

**Confidence:** 3/5. TB1 is a fair test, with its connectors at edges. The whole-board run (TB2) is only a capacity hint, because its placement was crude (below). The real test is the real placement at S4.

**Smallest test that would overturn it:** route the real Burrito placement at S4.
If KiCadRoutingTools can't finish it DRC-clean with only cleanup, the bulk router
becomes Freerouting.

## The approaches

| Approach | What it controls | How reliable it was here | How its output is verified | Time cost |
| --- | --- | --- | --- | --- |
| `pcbnew` Python (SWIG) | Footprints, nets, UUID paths, outline, net classes and rules, placement, tracks, vias, zones and zone fill, DSN export and SES import. **Not the stackup** (the descriptor isn't wrapped) | TB1 built in 1.4 s and TB2 (569 parts) in 35 s. Geometry and nets identical across rebuilds; the file isn't byte-identical, because new UUIDs reorder footprints | `kicad-cli` DRC and schematic parity; our checker | Seconds per build |
| IPC API (`kicad-python` 0.8.0) | Board items in a running KiCad GUI; no export or plot in KiCad 9 and 10 *(source)* | Worked under Xvfb: ready in 5 s, listed 105 footprints, moved U201 (8 ms), saved. A created track didn't reach the saved file. Needs the GUI process; headless only from KiCad 11 *(source)* | Same as SWIG, after saving | Slow to drive; extra moving parts |
| S-expressions (our `sexpr.py`) | Any token in the file. No geometry engine, no zone fill | Not byte-identical, but lossless: `pcbnew` re-saves the original and the round-tripped file identically. Text edits (stackup, a move, a track, a via) load correctly, and the stackup survives a re-save | KiCad loads it; DRC | Seconds |
| kiutils 1.4.8, kicad-skip 0.2.5 | Same, as libraries | kiutils reads KiCad 9 but rewrites settings (plot options flipped to "no"): lossy. kicad-skip fails on the board | — | Ruled out |
| `kicad-cli` 9.0.8 | DRC to JSON, schematic parity, per-layer SVG, 3D render, Gerbers, drill, position files, STEP, IPC-2581. **No zone refill** in DRC | All ran: 3D render in 0.9 s | It is the verifier | Seconds |
| Freerouting 2.5.0 (DSN/SES) | Bulk routing under one width and clearance per class | See tests T4 and T5 | KiCad DRC after the SES import | 1–7 min on TB1 |
| KiCadRoutingTools (1577fa3) | Plane pours, QFN fanout, differential pairs, bulk routing, its own placer; on the file | See tests T5b and T7 | KiCad DRC; its own grading only as a hint | 1.5 min on TB1 |
| DeepPCB, Quilter (cloud ML) | Routing (Quilter also places) | Not run: each needs an account and an upload of our design. DeepPCB's own comparison of the two, a vendor source, averaged 97.3% and 87.7% completion on three open boards; neither finished | DRC after import | Minutes, plus an upload |
| Hybrid (recommended) | Placement and critical copper by us, bulk by a router, cleanup and checks by us | See T5 and T5b | All of the above, and a hash of locked copper before and after | Minutes per run; the per-board spec is the human time |

## Test results

### Bench

- KiCad 9.0.8 with Python 3.14 in the 26.04 chroot.
- OpenJDK 25.0.5.1 (26.04 archive).
- Freerouting 2.5.0 (SHA-256 `f6f51bb0…e3c7`). Run with its analytics switched
  off: by default it tries to reach its server.
- kicad-python 0.8.0.
- KiCadRoutingTools at 1577fa3, router built with cargo.
- The machine has 2 cores and 8 GB of memory.

### Test board TB1

Burrito's sheets `02-flight-mcu`, `02a-flight-support`, `02flight-reset-debug`,
`05-can` and `04c-usb-service`: 105 parts, 138 nets, 243 connections to make.
- 80 × 100 mm, 4 layers, L2 a GND zone.
- Our greedy placer: anchors fixed, each other part pulled to the pads it
  connects to.
- Rules, set for the test (not yet the brief's): 0.15 mm track and clearance,
  0.6 / 0.3 mm vias, minimum track 0.1 mm.

| Run | Open connections (KiCad DRC) | Copper DRC errors | Tracks on L2 (GND plane) | Narrowest track | Vias | Time |
| --- | --- | --- | --- | --- | --- | --- |
| T4 Freerouting, L2 routable, optimiser on | 1 | 0 | 76 | 0.075 mm | 97 | 413 s |
| T4 Freerouting, L2 a plane, optimiser off | 50 (GND not reached) | 6 (track width) | 0 | 0.075 mm | 43 | 68 s |
| T5 Hybrid: scripted critical nets and GND fanout, then Freerouting | 1 | 2 (track width) + 3 hole spacing from the first fanout script (since fixed) | 0 | 0.075 mm | 136 | 56 s |
| T7 KiCadRoutingTools alone | 0 | 0 | 0 | 0.15 mm | 127 | 92 s |
| T5b Hybrid: the same scripted copper, then KiCadRoutingTools | 0 | 0 | 2 (late passes may cross planes; their layer list can forbid it) | 0.15 mm | 180 | 79 s |

Silkscreen overlaps are left out of the table: they are the footprints'
default text, and the silkscreen step sets them.

**Determinism:**
- Freerouting with the optimiser off gave an identical SES twice, apart from the
  file name.
- KiCadRoutingTools gave identical boards twice, apart from UUIDs.

**Locked copper:** the 172 scripted items (critical routes, GND stubs and vias)
hashed the same before and after both routers.

**Freerouting's narrow tracks:** 0.112, 0.09 and 0.075 mm segments at pads and in
gaps, with the class at 0.15 mm. Its `automatic_neckdown` and `neck_width_um`
settings didn't change them.

### T2: S-expressions

- Our round trip is lossless: `pcbnew` re-saves the original and the
  round-tripped file to identical bytes.
- Edits made as text (a stackup with dielectric thicknesses and εr, a footprint
  move, a track, a via) load correctly, and the stackup survives a `pcbnew`
  re-save.
- This is how the stackup gets set: SWIG doesn't expose it.

### T3: `kicad-cli`

- DRC to JSON, per-layer SVG, Gerbers and drill, position file and a 3D render
  all ran on TB1.
- KiCad 9's `kicad-cli` can't refill zones, so the fill is done in `pcbnew`
  before every check.

### T6: IPC API

- Works with KiCad 9.0.8 under a virtual display. It needs a KiCad GUI process
  kept alive, and can't plot, export or write DSN in 9 and 10
  ([KiCad dev docs](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/)).
- It is the future interface. The SWIG module is deprecated and due to be removed
  in KiCad 11 ([KiCad dev docs](https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/)),
  but the IPC API adds nothing this board needs today.

### TB2: all of Burrito (capacity hint only)

**Not a floorplan.** All 569 footprinted parts were placed in 80 × 230 mm by a
crude script that pinned only J102 and the two SMAs, and dropped everything else
into bands by schematic sheet. So most connectors, the USB-C among them, landed
mid-board instead of on an edge facing out, and the SMAs landed on two hole
positions. Seán flagged it on 22 Nov. A route of a placement like that says
little about the real board: the connectors' fan-in is wrong.

- **KiCadRoutingTools:**
  - Its `autoroute` was killed by the out-of-memory guard twice, at 5–6 GB, on
    its 0.05 mm grid.
  - Its route step alone at a 0.1 mm grid finished in 29 min: 310 of 334
    nets routed.
  - KiCad DRC: 38 unconnected, no clearance or short error. The hole and mask
    findings are the SMAs sitting on holes.
  - L2 untouched.
  - It shares GND vias between pads (up to 10 on one via). Our plan gives each
    GND pad its own scripted via instead.
- **Freerouting:** stopped after about 40 CPU-minutes without a result, once the
  placement was flagged. Routing it further proves nothing.
- **Placement time:** 35 s with our placer, after start points were clamped
  inside each part's region (the first version took 465 s and crowded every
  part aft).

## What this means for the pipeline

- **Placement is ours, and connectors come first.** Every connector's place
  and facing is written in the board spec, on an edge and facing out
  (D-21Nov.24, amended 22 Nov), before the placer moves anything. Our greedy
  placer is crude; it was enough to test routers. Phase 3 replaces it with the brief's floorplan, its regions and
  fixed parts, then a local improvement pass. KiCadRoutingTools' own annealing
  placer is worth a look at S3; it would be judged on the same metrics.
- **Planes:**
  - L2 is made a plane layer;
  - every GND pad gets a scripted via;
  - the router's layer list leaves L2 out;
  - the checker fails any track on L2.
- **Byte-identical rebuilds:** deterministic UUIDs, from the S-expression pass.
- **Memory:** a whole-board route runs alone.

## Sources

- [KiCad IPC API for add-on developers](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/)
- [KiCad PCB Python bindings](https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/)
- [Freerouting releases](https://github.com/freerouting/freerouting/releases)
- [KiCadRoutingTools](https://github.com/drandyhaas/KiCadRoutingTools)
- [DeepPCB vs Quilter (vendor comparison, 20 Apr 2026)](https://deeppcb.com/deeppcb-vs-quilter-open-source-routing-compared-2026/)
