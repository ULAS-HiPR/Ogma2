# Croí2

## Latest accepted revision — 7 September

Three servo channels; J6602 ten-contact Micro-Fit 430451000 with a new complete
pinout; J4601 vertical standard SMA 132134. USB stays unchanged. Flight PD10
is servo3 LPTIM2_CH2 AF3; PD7 drives complementary green/red readiness through
U9101. Green is profile checks passed, not armed or launch authority.
Current totals: 635 symbols, 634 footprints, 493 front/141 back, 99 placement
cells, 68 native groups, 28 rule areas, 28 DNP. 2,163 pin / 346 architecture
checks pass; existing four ERC errors/six warnings and DRC findings remain.
567 model instances resolve after the additional power-package recovery.
34 physical component bodies still lack models; 33 further bodyless patterns are
flat probes/Tag-Connect. SMA remains unmoved. [Complete gaps and sources](../../docs/model-recovery-2026-09-07.md).
Earlier counts/pin statements below describe prior checkpoints.
[Full delta and verification](../../docs/connector-servo-readiness-revision-2026-09-07.md).


Open **[Croi2.kicad_pro](Croi2.kicad_pro)**. Use the schematic and PCB editors
from this project so `${KIPRJMOD}` resolves here. Close any old `Ogma2` editor
without saving over the new project, then reopen this one.

43 schematic pages; 630 physical symbols; **629 placed PCB footprints**.
The latest placement separates the 25 coarse subsystems into **97 small circuit
cells** at the compaction checkpoint; **96 remain after the Wio radio revision**.
The 25 native outer groups remain logical selection aids, containing
all 43 original sheet groups; they are no longer rigid placement units.
488 front, 141 back. Four copper layers, 1.6 mm. The outline is now
**80 × 230 mm**, down **42.98% in area** from 123.75 × 260.75 mm.
This reaches the provisional width target; vehicle fit and routing capacity
remain unverified. Critical local geometry, component angles and sides are
preserved. Independently spaced circuits within each subsystem have moved.
No parts remain in the old staging banks. No tracks, routing vias or filled pours.

The reviewed local circuit geometry, 28 native rule areas and GNSS custom rules
are now in this working PCB. Enter the logical groups to adjust local circuits.
Do not use the old subsystem envelope as a packing constraint. Keep actual
IC support together across sheet boundaries, and move each relevant rule area
and reference drawing with its owning circuit. The 96 cells are recorded in
the placement report, not 97 new native KiCad groups.

The 50 × 50 mm GNSS rectangle on User.1 is a continuous ground-reference
reservation, not a cutout or ground split. Separate rules preserve its component,
signal-route and signal-via restrictions while permitting GND. Samtec sits at
local (40, 230), rotation 0°, on the provisional bottom edge. Its
counterpart remains Foinse2's top edge, with a nominal 7.39 mm board-edge gap.
Connector access, supports, mounting holes and installed RF performance remain
mechanical/layout work. The J101 rectangle is an unverified space reservation,
not a land pattern.

## Read before routing

Read the [current ordered guide](../../docs/pcb-layout-guide.md) and
[placement/compaction notes](../../docs/croi2-functional-placement-2026-09-07.md).
The source shunt/INA and passive piezo are included in their functional groups;
REV-B was a change label, not a later manufacturing population.

- [Electrical status and open circuit work](schematic-status.md).
- [Exact schematic checks](full-checks.json) and [saved-PCB checks](board-checks.json).
- [Placement coordinates and circuit-distance checks](placement-report.json).
- [Portable library manifest](libraries/board-library-manifest.json).
- [Insulated rail test points](libraries/testpoint-selection.md): 17 red
  Keystone 5000s and three black 5001 grounds replace the old bare loops.
  Exact footprints/MPNs installed; their exact 3D model remains unavailable.
  The 31 flat signal-probe pads are unchanged.

Start refinement here; do not order from this draft. The interblock spacing is
not a routing proposal or routing-capacity proof. Four known ERC errors and four warnings remain, chiefly
the deliberately unpowered output domains. The radio revision adds two warnings
for reserved, unused RXEN/TXEN labels: four errors and six warnings now.
Arm hardware, load-dependent values,
no-fire limits, exact hold-up capacitor, Nano-Fit land pattern and DNP transducer
selection remain open. See the electrical status for the full list. Existing
fabrication-rule and library findings remain visible in `output/pcb-drc.json`;
none were suppressed to obtain a clean-looking report.

## Local dependencies and checks

`sym-lib-table` and `fp-lib-table` use only this repo's `libraries/`. Existing
3D models are also local. **Not every footprint has an exact 3D model**: the
manifest lists missing models, including major custom connector/RF parts.
Opening the project does not require the umbrella or global KiCad libraries.
KiCad stock-derived assets retain [their licence](libraries/KICAD-LICENSE.md).

With KiCad 9 and a Python whose XML module works, from this directory:

```sh
kicad-cli sch export netlist --format kicadxml -o output/full-netlist.xml Croi2.kicad_sch
kicad-cli sch erc --format json -o output/full-erc.json Croi2.kicad_sch
python3 tools/check_schematic_full.py . output/full-netlist.xml output/full-erc.json --output full-checks.json
kicad-cli pcb drc --schematic-parity --format json -o output/pcb-drc.json Croi2.kicad_pcb
```

Use KiCad's Python/wx runtime for
`tools/check_board_layout.py . Croi2 output/full-netlist.xml`. The PCB checks
cover pads, references, UUID linkage, library hashes, local model paths,
outline/layers, DNP/BOM flags and courtyard/drill reservations. Native DRC is
still required. Its unrouted-item list may be report-limited; it is not an
exact work estimate. Regeneration is only for a separate scratch copy; never
rerun a floorplan generator over your developing layout.

The pre-placement board, reports and changed notes are recoverable under
`../../../placement-work-2026-09-07/pre-placement/`. The earlier separate
cluster catalogue remains intact. The 130 × 300 pre-compaction board is saved
under `../../../compaction-work-2026-09-07/pre-compaction/`.
The previous 123.75 × 269.75 board and libraries are saved under
`../../../compaction-2-2026-09-07/pre-pass/croi2/`.
The immediately preceding 123.75 × 260.75 board and dependencies are saved
under `../../../flex-placement-2026-09-07/source/`.
If KiCad still shows an older placement,
reload from disk; do not save a stale editor over this placement.

Independent local Git repo, branch `schematic-layout-draft`. No commits or
remote yet. The umbrella intentionally ignores this directory until the team
chooses remotes and registers reviewed submodule commits.
