# Foinse2

Model recovery, 7 September: J201/J701 Micro-Fit bodies added; 88 model instances
resolve. J301 Samtec body and J101 Nano-Fit footprint remain missing. Eleven flat
probes need no physical body. Placement/electrical CAD unchanged.
[Complete gaps and sources](../../docs/model-recovery-2026-09-07.md).

Open **[Foinse2.kicad_pro](Foinse2.kicad_pro)**. Its schematic and PCB use local
symbol, footprint and 3D-model tables; no sibling project is required.

11 schematic pages, 101 physical symbols, 100 imported footprints in 9 movable
functional-sheet groups. **60 × 80 mm**, four copper layers, 1.6 mm. All assigned
footprints are inside the provisional outline. No routing, vias or copper pours.
Select a group to move the block; enter/ungroup it for component-level layout.

Samtec is at the top edge, facing Croí's bottom edge across a nominal 7.39 mm
board-edge gap. The two source blocks are separate, with nearby monitors and
the temperature ADC below. Source/output connector mouths face outward.
Mounting supports, harness access, exact overhang and assembly envelope remain
to be finalised. J101's rectangle reserves space only: it has no invented pads.

Read **[schematic-status.md](schematic-status.md)** before routing. Zero ERC
findings and passing net checks do not qualify battery protection or load
behavior. Pack-specific fusing/charging service, analog/rating checks and the
Nano-Fit land pattern remain open. The regulated 24 V actuator stage is
conditional on actual coils and is not drawn or allocated in this board.

- [Schematic checks](full-checks.json): 278 pins and 91 boundary checks.
- [PCB checks](board-checks.json): 338 numbered pads, identity/model/outline checks.
- [Placement details](placement-report.json).
- [Local-library manifest](libraries/board-library-manifest.json): all used
  symbols and assigned footprints; available models copied locally, absent
  exact models explicitly listed. A model is not footprint approval.

With KiCad 9 and a working Python XML module, from this directory:

```sh
kicad-cli sch export netlist --format kicadxml -o output/full-netlist.xml Foinse2.kicad_sch
kicad-cli sch erc --format json -o output/full-erc.json Foinse2.kicad_sch
python3 tools/check_foinse_schematic.py . output/full-netlist.xml output/full-erc.json --output full-checks.json
kicad-cli pcb drc --schematic-parity --format json -o output/pcb-drc.json Foinse2.kicad_pcb
```

Use KiCad's Python/wx runtime for
`tools/check_board_layout.py . Foinse2 output/full-netlist.xml`. Never run the
floorplan generator over a board with manual placement/routing. Available
models are local; [KiCad-derived assets retain their licence](libraries/KICAD-LICENSE.md).

Independent local Git repo, branch `schematic-layout-draft`. No commits or
remote yet. Not manufacturing or flight release. The umbrella ignores this
directory pending authorised remote/submodule setup.
