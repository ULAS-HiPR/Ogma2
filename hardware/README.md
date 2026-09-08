# Ogma 2 hardware

Native KiCad projects are tracked directly in this monorepo:

| Board | Project | Installed checked draft, 8 September |
| --- | --- | --- |
| Croí2 | `croi2/Croi2.kicad_pro` | 44 schematic pages, 643 physical symbols, 642 PCB footprints |
| Foinse2 | `foinse2/Foinse2.kicad_pro` | 12 pages, 113 symbols, 112 footprints |

Both projects are included in a normal clone, with local symbols, footprints,
available models and check reports. No submodule initialisation or separate
repository is needed. Generated scratch, backups and editor caches are excluded.

- [Croí reading PDF](croi2/output/pdf/Croi2-readable.pdf)
- [Foinse reading PDF](foinse2/output/Foinse2-readable.pdf)
- [Architecture pack](../docs/architecture/README.md)

## Work now

Automatic placement and routing remain frozen. Readable wired circuits and the
approved installation changes are installed. Review architecture and drawings
together. Eight new Croí and twelve new Foinse parts are staged outside the
outlines for Seán to integrate; existing placement is preserved.

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
- Croí: 99 historical placement cells, 68 native groups, 20 rule areas, 28 DNP.
  572 model instances resolve. Old cell envelopes do not constrain new parts.
- Foinse: nine groups, 100 model instances resolve.
- Exact Nano-Fit 1053111102 footprint missing on both boards. Its drawn
  reservation is not an approved land pattern. C1403 is also a volume allocation.
- Croí: 2,179 schematic-pin and 381 architecture checks; four ERC errors,
  six warnings; 61 DRC findings, previously 62.
- Foinse: 306 pin and 117 boundary checks; zero ERC findings; 24 existing DRC
  findings. Unrouted connections are additional.
- DRC/check counts describe the installed draft, not physical qualification.
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
