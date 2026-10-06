# Ogma 2 hardware

The native KiCad projects live in this repository:

| Board | Project | Checked draft, 8 September |
| --- | --- | --- |
| Croí2 (Burrito) | `croi2/Croi2.kicad_pro` | 44 schematic pages, 643 physical symbols, 642 PCB footprints |
| Foinse2 (Churro) | `foinse2/Foinse2.kicad_pro` | 12 pages, 113 symbols, 112 footprints |

A normal clone has both projects with their local symbols, footprints, available
3D models and check reports. No submodules, no second repository. Generated
scratch, backups and editor caches are left out.

- [Croí reading PDF](croi2/output/pdf/Croi2-readable.pdf)
- [Foinse reading PDF](foinse2/output/Foinse2-readable.pdf)
- [Architecture](../docs/architecture/README.md)
- Changes waiting for capture: [decisions](../decisions.md) and the
  [capture specification](../docs/architecture/schematic-capture-spec.md)

## Rules while the CAD is on hold

- Automatic placement and routing stay frozen.
- Readable wired circuits and the approved installation changes are in. Review
  the architecture and the drawings together.
- Eight new Croí parts and twelve new Foinse parts sit outside the board outlines
  for Seán to place. Existing placement is kept.
- Keep symbol UUIDs, sheet-instance paths, references, footprint assignments,
  pin nets and DNP / BOM attributes. That keeps schematic cross-selection linked
  to the PCB.
- A drawing-only schematic change is no reason to move PCB parts. A real
  electrical change must update schematic and PCB explicitly.
- Work from each board's own AGENTS, README, schematic-status, current pin CSVs
  and native check reports.
- `libraries/inputs/` and the construction tools are older snapshots; some
  describe an older servo count and the E22 radio. Don't regenerate them over the
  working projects. `hardware/Ogma2/` is not the active project.

## Where the draft stands

| Item | Croí | Foinse |
| --- | --- | --- |
| Board | 4 layers, 1.6 mm, unrouted; 80 × 230 mm provisional canvas | 4 layers, 1.6 mm, unrouted; 60 × 80 mm provisional canvas |
| Placement data | 99 historical placement cells, 68 native groups, 20 rule areas, 28 DNP; old cell envelopes don't constrain new parts | 9 groups |
| 3D models | 572 instances resolve | 100 instances resolve |
| Checks | 2,179 schematic-pin and 381 architecture checks | 306 pin and 117 boundary checks |
| ERC | 4 errors, 6 warnings | Clean |
| DRC | 61 findings (was 62), plus unrouted | 24 findings, plus unrouted |

- The exact Nano-Fit 1053111102 footprint is missing on both boards. The drawn
  reservation is not an approved land pattern. C1403 is also only a volume
  reservation.
- Check counts describe the draft, not physical qualification.
- R6310 / R6410 / R6510 and the energetic-setting DNPs stay. R6804 becomes
  fitted at capture (D-6.1). Don't connect initiators.
- KiCad 9.0.6 re-check on 30 September matched these counts
  ([archived audit](../docs/archive/architecture/2026-09-30-repository-sanity.md)).

Each board carries its used symbols, assigned footprints and available models in
local libraries, with provenance. Missing exact models are written down. A body
model doesn't approve a footprint.

## After any CAD edit

1. Export a fresh native netlist, ERC report and reading PDF.
2. Compare full pin connectivity and symbol and footprint identity.
3. Run the board's checker and the native schematic/PCB parity check.
4. Look at every drawing.

Keep existing failure findings. Don't suppress them to get a clean result.

The board checkers cover the frozen MCU maps, selected fault and power
boundaries, pad-net identity, UUID paths, models, DNP and outlines. They don't
prove analog behaviour, surge survival, physical arming or routing quality.

First block tests use the first complete engineering PCBA with current-limited
supplies and inert loads. No separate mini-PCB step. Seán owns layout, Anav owns
firmware. Buying parts and releasing for flight are separate decisions.

## Layout references

The [layout guide](../docs/pcb-layout-guide.md) is useful once the circuit is
reviewed. Some rendering and maker-page packs it links exist only in a local
workspace, not in a clean clone. The automatic 99-cell local-routing experiment
was never promoted into either PCB and isn't a released layout.
