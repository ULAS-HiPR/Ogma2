# Ogma 2 hardware

Native KiCad projects are local independent repositories:

| Board | Project | Inspected baseline |
| --- | --- | --- |
| Croí2 | `croi2/Croi2.kicad_pro` | 43 schematic pages, 635 physical symbols, 634 PCB footprints |
| Foinse2 | `foinse2/Foinse2.kicad_pro` | 11 pages, 101 symbols, 100 footprints |

These paths exist in the working workspace but are ignored by the umbrella.
Neither child has a remote or registered submodule. An umbrella clone does
not include the board files. This page documents that boundary; the
[architecture pack](../docs/architecture/README.md) is self-contained.

## Work now

Freeze automatic placement and routing. Turn the existing connectivity into
readable wired circuits, implement the approved installation changes, then
review architecture and drawings together.

Preserve symbol UUIDs, sheet-instance paths, references, footprint assignments,
pin nets and DNP/BOM attributes. This keeps schematic cross-selection linked to
the existing PCB. Pure schematic drawing changes do not justify moving PCB
components. A real electrical delta must update both representations explicitly.

Use each child's AGENTS, README, schematic-status, current pin CSVs and native
check reports. The common `libraries/inputs/` and construction tools are older
snapshots; some still describe two servos and E22. Do not regenerate them over
the working projects. `hardware/Ogma2/` is not the active project.

## Known baseline limits

- Both boards: four copper layers, 1.6 mm, unrouted. Croí 80 × 230 mm and
  Foinse 60 × 80 mm are provisional canvases.
- Croí: 99 recorded placement cells, 68 native groups, 28 rule areas, 28 DNP.
  567 model instances resolved at the inspected checkpoint.
- Foinse: nine groups, 88 model instances resolved.
- Exact Nano-Fit 1053111102 footprint missing on both boards. Its drawn
  reservation is not an approved land pattern. C1403 is also a volume allocation.
- Croí: 2,163 schematic-pin and 346 architecture checks; four ERC errors,
  six warnings; 62 existing DRC findings.
- Foinse: 278 pin and 91 boundary checks; zero ERC findings; 24 existing DRC
  findings. Unrouted connections are additional.
- DRC/check counts describe the saved baseline, not new schematic-revision
  evidence or physical qualification.
- R6310/R6410/R6510/R6804 and unresolved energetic-setting DNPs remain.
  Do not connect initiators.

Each child carries its used symbols, assigned footprints and available models
under local libraries, with provenance. Missing exact models are documented;
a body model is not approval of a footprint.

## Verification after edits

Export a fresh native netlist, ERC report and reading PDF. Compare complete pin
connectivity and symbol/footprint identity, run the board's checker and native
schematic/PCB parity, then inspect every drawing. Preserve existing failure
findings; do not suppress them for a clean-looking result.

The child checkers cover frozen MCU maps, selected fault/power boundaries,
pad-net identity, UUID paths, models, DNP and outlines. These checks do not prove
analog behavior, surge survival, physical arming or routing quality.

First block tests use the first complete engineering PCBA with current-limited
supplies and inert loads. No new mini-PCB gate. Seán owns final layout; Anav
owns firmware; purchasing and flight release remain separate decisions.

## Layout references

The [ordered layout guide](../docs/pcb-layout-guide.md) remains useful after
circuit review. Some detailed rendering and manufacturer-page packs it links
are workspace-local, not clean-clone dependencies. The automatic
99-cell local-routing experiment was not promoted into either live PCB and is
not a released layout.
