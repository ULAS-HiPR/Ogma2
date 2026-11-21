# Capture tools

Scripts that apply the [capture specification](../../../../docs/architecture/schematic-capture-spec.md)
to the native sheets, one step at a time, and check each step. Status:
[schematic-status.md](../../schematic-status.md).

- `sexpr.py`: KiCad S-expression reader and writer, from the 7–8 September
  readable-schematics tools (`hardware/libraries/tools/sexpr.py` in the pre-split repository).
- `kicadsch.py`: surgical edits: pin positions, labels, wires, new symbols with
  deterministic uuid5 identities.
- `capture.py`: export the native netlist and ERC, compare against the previous step
  pin by pin, list ERC findings fixed and added, render the changed sheets.
- `steps/sNN_*.py`: one script per step. Each edits sheets in place and refuses to run
  over uncommitted manual edits.

KiCad: `kicad-cli` 9.0.8 from Ubuntu 26.04's official archive, run inside a minimal
26.04 root (`debootstrap`), with the repository bound at `/work` and outputs at `/cap`.
On a machine with KiCad 9 installed, call `kicad-cli` directly instead.
