# Croi2

21 November 2026. Schematic captured from the [capture specification](../../docs/architecture/schematic-capture-spec.md)
(D-21Nov.9). Engineering draft: not ready for manufacture or flight.

Open [Croi2.kicad_pro](Croi2.kicad_pro), then its schematic and PCB from that project.
Reopen old editors without saving stale in-memory drawings over these files.

44 schematic pages, 581 physical symbols. Each circuit explains what it does and
what it connects to. Follow the root index, then trace the local wires. Labels
identify connections between sheets. The capture steps, their checks and what is
still owed are in [schematic-status.md](schematic-status.md).

The PCB has not been updated from this schematic yet: it still holds the
8 September parts and placements, so schematic/PCB parity is broken until layout.
[board-checks.json](board-checks.json), [native-identity-checks.json](native-identity-checks.json)
and [placement-report.json](placement-report.json) describe that older PCB.

- [Current engineering status](schematic-status.md).
- [Schematic checks](full-checks.json): netlist parity, the as-captured pin maps
  ([flight](libraries/inputs/flight-pinout.csv), [comms](libraries/inputs/comms-pinout.csv))
  and the capture safety assertions, from [tools/check_schematic_full.py](tools/check_schematic_full.py).
- [Local library inventory](libraries/board-library-manifest.json).
- [JLC stock](jlc-stock.md).
- [Architecture reading pack](../../docs/architecture/README.md).
- [8 September exports and pin maps](history/baseline-2026-09-08/), and the
  [earlier README](history/pre-readable-2026-09-08/README.md), preserved as history.

ERC: no finding, with three recorded exclusions (strap pins tied to GND; reasons in
the project file). J101 still has no footprint (Molex Nano-Fit drawing not yet
obtained) and J6101 / J6102 are placeholders until their parts are chosen. Energy
links R6310 / R6410 / R6510 stay DNP. Do not connect initiators.
