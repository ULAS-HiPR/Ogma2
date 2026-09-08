# Croi2

8 September 2026. Readable, connected engineering draft. Not ready for manufacture or flight.

Open [Croi2.kicad_pro](Croi2.kicad_pro), then its schematic and PCB from that project.
Reopen old editors without saving stale in-memory drawings over these files.

44 schematic pages, 643 physical symbols, 642 assigned PCB footprints.
Each circuit explains what it does and what it connects to. Follow the root
index, then trace the local wires. Labels identify connections between sheets.

The external master-enable contacts are implemented in the draft. GNSS now uses
MAX-M10S and an external passive antenna/SMA; MCU pins are unchanged.
Read the [installation change record](installation-change-record.md) for exact
parts, connector pins, limitations and required tests.

Existing component positions, angles, sides and PCB identities are preserved.
8 new footprints are staged outside the provisional outline for Seán to
integrate. No automatic routing or further packing was done. Native identities
and pad nets match the schematic; GUI cross-selection itself was not exercised.
Both editors must use this project for native cross-probing.

- [Current engineering status](schematic-status.md).
- [Schematic checks](full-checks.json), [PCB checks](board-checks.json),
  [independent identity checks](native-identity-checks.json).
- [Local library inventory](libraries/board-library-manifest.json).
- [Architecture reading pack](../../docs/architecture/README.md).
- [Earlier README, preserved as history](history/pre-readable-2026-09-08/README.md).

Current ERC: four errors and six warnings. PCB DRC: 61 findings, plus unrouted
connections and missing J101 Nano-Fit. These are not clean release files.
Exact models remain incomplete. C1403 and physical energetic arming remain unresolved;
all 28 DNP safeguards stay. Do not connect initiators.
