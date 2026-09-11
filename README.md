# Ogma 2

HiPR's workhorse flight computer: standalone Croí2, with MCU-less Foinse2 power
distribution when the vehicle needs it. Engineering draft; no fabrication or
flight release.

**11 September review hold:** requirements and architecture are in flux after
the joint session. No schematic or PCB changes until Seán authorizes the final
stack. [Complete session extraction](docs/architecture/2026-09-10-session-review.md).
Working names: Burrito (Croí2), Churro (Foinse2), Fajita (propulsion controller).
Existing CAD/file names and cross-system contracts have not changed.

## Read

1. [Current system](current-system.md) — selected architecture, boundaries and next work.
2. [Architecture review pack](docs/architecture/README.md) — overview and eight chapters with research, alternatives and tradeoffs.
3. [Firmware handoff](docs/firmware-handoff-2026-09-07.md) — detailed Anav interface; dated revisions at its top control older text.
4. [Document index](docs/README.md) — decision records, interfaces and deeper studies.
5. [Project log](project-log.md) — append-only history.

The existing CAD preserves the previously accepted design. External GNSS reception and
external power-switch connections are implemented in the checked CAD draft.
[Exact changes and remaining tests](docs/installation-change-record-2026-09-08.md).
Physical energetic arming remains separate. Readable schematics are installed;
all schematic and PCB implementation remains paused pending final-stack approval.

For the next session, start at the architecture pack's overview and review all
nine chapters together. Each session's questions must improve that same text
and its diagrams; the extraction record is optional supporting evidence.
Seán owns final layout;
Anav owns firmware. The model prepares the drawings, comparisons and checks.

## Hardware and repository boundary

[Hardware entrypoint](hardware/README.md) explains the local Croí/Foinse projects,
dependencies and verification. This monorepo contains architecture, interfaces,
curated evidence and both active CAD projects:

- `hardware/croi2/` — Croi2.kicad_pro
- `hardware/foinse2/` — Foinse2.kicad_pro

Both are ordinary tracked directories, not submodules or separate repositories.
A clean clone includes their native projects, symbols, footprints, available
3D models, reading PDFs and check reports. Open the corresponding `.kicad_pro`.

The earlier long current-system is [preserved verbatim](docs/history/README.md).
Historical alternatives are not additional current requirements. Native CAD,
controlled contracts and measured evidence outrank prose; discrepancies require
a recorded correction, not silent regeneration.

Use review branches and bounded pull requests. Do not publish raw transcripts,
private correspondence, generated research dumps or temporary render trees.
No repository licence has been selected; Rev 1 remains a separate project.
