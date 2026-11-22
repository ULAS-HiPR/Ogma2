# Burrito execution brief

**22 November 2026.** Written by Claude Fable for the next model, at Seán's request. It turns the
[sweep](burrito-sweep.md) and Seán's decisions of 22 November (D-22Nov.13 to D-22Nov.19) into ordered work.
Where this brief and `decisions.md` differ, `decisions.md` wins; say that they differ.

## The job

Take Burrito from "placed at 80 × 180" to "routed, DRC clean, ready for Seán to upload".

| Stage | Work | Ends at |
| --- | --- | --- |
| A | Parts and footprints: J102, J101, J103, the 0402 swap, schematic checks | – |
| B | Re-place: connector labels, a length sweep, Seán's pick, the back refitted | **Stop 1** |
| B2 | Settle the placement before copper: a routability meter, the MCUs turned, surface-mount loops, test points, distance rules, pin swaps ([brief](burrito-stage-b2-brief.md)) | **Stop 1b** |
| C | S4: the critical copper, by script | **Stop 2** |
| D | S5: route the rest, pours, outputs | **Stop 3** |

## Rules

- The board is the output of scripts. No edit that a script can't replay (D-21Nov.21).
- Checked, assumed and unknown stay apart. Never report a check you didn't run.
- Real parts only. No part number, pinout or pad from memory: cite the drawing.
- Every JLC limit you use is cited.
- New parts on the schematic are Seán's decision. Propose them at a stop; don't add them.
- Each stop shows DRC and ERC, the unrouted count, per-layer renders, and decisions and doubts. Renders
  check the work; they don't drive it.
- Ask for Seán's calls only at stops, in one line, skippable.
- One bounded change per commit, on main, then `git push -q origin main`. Decisions, current-system, the
  affected document and a project-log entry go in the same commit as the change.
- Nothing is posted, sent or bought.

## Environment

- KiCad 9.0.8 is in a chroot at `/opt/resolute`, with the repo at `/work`. If the chroot is gone, rebuild it
  from `tools/layout/phase1/README.md`.
- KiCad's Python needs numpy, shapely, Pillow, OpenCV (headless) and fontTools:
  `pip install --break-system-packages` inside the chroot. The host needs CadQuery (for
  `tools/layout/models3d.py`) and `rsvg-convert` (for renders).
- Build: `chroot /opt/resolute env HOME=/tmp python3 /work/tools/layout/build.py croi2 --to place
  [--length L] [--out DIR]`. Two builds must give the same bytes.
- DRC: `kicad-cli pcb drc --format json --severity-all --schematic-parity`, in the chroot with `HOME=/root`.
- Schematic check, from `hardware/croi2`:
  `python3 tools/check_schematic_full.py . output/full-netlist.xml output/full-erc.json`.
- A capture step is a script under `hardware/croi2/tools/capture/steps/` with its own check, one commit,
  and a row in `schematic-status.md`. The next is step 14.
- Renders: `kicad-cli pcb export svg --layers "B.Cu,B.SilkS,Edge.Cuts" --mirror` then `rsvg-convert` for
  the back; `kicad-cli pcb render --side top` or `bottom` for 3D.
- Every y in `layout/spec.py` is in the 230 mm reference frame. `build.py`'s `stretch()` maps it to
  `LENGTH`.

## Stage A: parts and footprints

Each item is one capture step and one commit. After each: ERC unchanged (three recorded exclusions), the
checker passes, the manifest is regenerated.

**A1. J102 without the screw-down (D-22Nov.14)**

1. From Samtec's MPT ordering code and prints, find the right-angle part with the same contacts and no
   -SD that is in stock. Confirm it mates the half Churro uses (`jlc-stock.md`, the Churro interface).
2. Change the part number. Build the footprint from Samtec's print for that part: the two Ø3.56 mm holes
   go if it has none. Update the `mpt` builder in `models3d.py`, which draws the ears.
3. If no such part exists, or its tails move the aft edge, stop and show Seán the options.

**A2. J101 (sweep §10)**

1. Confirm the peg's side against Molex's footprint file or the drawing. Until then nothing is built.
2. Build the footprint in the project library from the drawing's numbers. The clip pads carry no net. The
   peg hole is unplated.
3. Assign it. The checker's `missing_footprints` empties and DRC's parity error goes.
4. In the spec, drop `RESERVED['J101']` and place J101 as a left-edge part with its latch reachable. It
   needs about 11 × 9 mm with its plug.

**A3. J103 (D-22Nov.18)**

1. Check Harwin's catalogue first. If a 2-contact Gecko G125 exists, stop and tell Seán: D-19Nov.5 then
   stands.
2. Otherwise fit a Molex Micro-Fit 3.0, single row, two circuits, from the vendored KiCad library, with the
   entry direction the harness needs.
3. Check that no other Micro-Fit plug on Burrito, Churro or the panel can mate it.

**A4. The 0402 swap (D-22Nov.13)**

1. Swap to 0402:
   - pull-ups and pull-downs;
   - series and divider resistors at 1%;
   - capacitors of 1 µF or less on rails of 5 V or less.
2. Keep as they are:
   - anything at 0.1%;
   - sense, limit, shunt and termination resistors;
   - every part on a fire, arm or continuity net;
   - capacitors of 2.2 µF or more;
   - any capacitor whose 0402 part isn't rated at twice its rail;
   - any resistor that would dissipate over 30 mW.
3. Pick each value's part from JLC's library, Basic where one exists. Record its C-number. Same value and
   tolerance; the same dielectric or better.
4. One capture step changes footprint, MPN and LCSC fields. No pin changes, so the netlist's connections
   must come back identical.
5. Teach the placer the 0402 class (`pkg_class` and JLC's spacing table in `engine/place.py`).
6. Report how many parts swapped and the courtyard area saved.

**A5. Schematic checks (sweep §7.5–7.9)**

Verify each on the sheets and report what's there. Anything missing goes to Stop 1 as a proposal, with its
part, its job and its test.

## Stage B: re-place

1. Connector function names (D-22Nov.19) go in before the sweep, since a label counts as courtyard.
2. Re-measure `BAND_AREA`: the 0402s change each band's share.
3. Sweep the length from 180 down to 140 mm in 5 mm steps. For each: unplaced parts, density per band,
   JLC spacing breaches.
4. Refit the back. `ART['place']` holds positions for 180 mm; make them follow the length. Re-derive
   `PROBE_MOVES`: the legend needs a pin-free strip about 68 mm long. If the back runs short, keep things
   in this order (Seán, 22 Nov):
   - the test point legend in one column, and the parts list;
   - BURRITO with its subtitle, and the logo;
   - the IF FOUND and HOUSTON lines;
   - then the rocket, the Ogham line, and the waves last.
5. **Stop 1.** Show the sweep table, the back at two or three candidate lengths, and A5's findings.
   Recommend the shortest length whose densest band is no denser than today's at 180 (0.65). Seán picks.
   His call on 22 November was 150–170 mm at 3/5.
6. After his pick: set `LENGTH`, build twice (same bytes), run DRC, and update `test-points.md`,
   `decisions.md` (the length) and `current-system.md`. Test point numbers don't change.

## Stage C: S4, the critical copper

Follow sweep §8 steps 3 to 5, with these fixed:

- L2 is never routed or cut.
- L3 is ground with power islands, and no L4 track crosses an island's edge (D-22Nov.15). Write that
  check before any copper.
- RF as D-22Nov.16 and sweep §3. No shield cans.
- Thermal reliefs on every passive pad that meets a pour; solid on regulators, FETs and connectors.
- `FIRE_LOGIC` keeps 0.5 mm. Draw its escape from U201 by script, with the fire rule waived only inside U201's
  courtyard (D-22Nov.26).
- Pyro: draw channel 1's parts and copper, then stamp the block for channels 2 and 3 (D-22Nov.27).
- **Stop 2.** The usual set, plus each block's copper beside its datasheet's layout figure (the table in
  sweep §5), the L3 map, and the list of nets left for the router.

## Stage D: S5, the rest

Follow sweep §6:

- Router passes in order. Each accepted pass is frozen under `hardware/croi2/layout/routes/` and replayed
  by `build.py` (D-22Nov.17).
- The metrics table, then teardrops, stitching and fill. DRC clean with nothing unrouted.
- Outputs: gerbers, drill, BOM and CPL.
  - The CPL carries JLC's rotation corrections.
  - The 25 test pads, the Tag-Connects, fiducials and holes are left out.
  - Two BOM variants: J101 fitted, or J102 fitted.
- **Stop 3.** Seán reviews, uploads and orders.

## Traps found on 22 November

- pcbnew rejects numpy numbers. Cast to `float` before `FromMM`.
- SWIG objects fail `is` tests. Compare by name.
- Silk text is either KiCad's stroke font or polygons. A named font won't be on Seán's machine.
- Anything exposed on the back must reach the art as copper at its real shape. `board_art` raises if the
  legend can't fit.
- The manifest hashes every library file. Regenerate it in any commit that touches a footprint or model.
- The built-in browser shows a PDF at 100% only if the tab loads in a 4000 × 2750 viewport and is then
  shrunk to 800 × 550. Clicks don't reach the viewer; scrolling does.

## Outside this brief

- Seán starts the parts buy on Monday 23 November: sweep §7.4, plus whatever A1 to A3 choose.
- For Jay: insulated antenna mounts, non-magnetic screws by the magnetometer, the J102 datum, bay vents
  and RF windows (sweep §7.19–21).
- The taste ledger wasn't written today. Append sweep §11's bets and this line:

```text
dec  2026-11-22  ogma2  scope  chose one side with 0402s and a smaller J101 block over a second side, because "Let’s do this {let’s keep it one sided plus this: If you ever need it shorter, 0402 passives and a smaller J101 block buy about the same without a second side.}", betting the board gets shorter without one  ?/5  settles: the Stage B sweep
```
