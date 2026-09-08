# Ogma 2

HiPR's workhorse flight computer: standalone Croí2, with MCU-less Foinse2 power
distribution when the vehicle needs it. Engineering draft; no fabrication or
flight release.

## Read

1. [Current system](current-system.md) — selected architecture, boundaries and next work.
2. [Architecture review pack](docs/architecture/README.md) — overview and eight chapters with research, alternatives and tradeoffs.
3. [Firmware handoff](docs/firmware-handoff-2026-09-07.md) — detailed Anav interface; dated revisions at its top control older text.
4. [Document index](docs/README.md) — decision records, interfaces and deeper studies.
5. [Project log](project-log.md) — append-only history.

The current review keeps the accepted design. External GNSS reception and
external power-switch connections are implemented in the checked CAD draft.
[Exact changes and remaining tests](docs/installation-change-record-2026-09-08.md).
Physical energetic arming remains separate. Readable schematics are installed;
automatic PCB packing and routing remain paused for human review.

Read the architecture pack separately, then review it together. Seán owns final layout;
Anav owns firmware. The model prepares the drawings, comparisons and checks.

## Hardware and repository boundary

[Hardware entrypoint](hardware/README.md) explains the local Croí/Foinse projects,
dependencies and verification. The umbrella contains architecture, interfaces,
curated evidence and common library/tool sources. Active CAD lives in independent
local repositories at:

- `hardware/croi2/` — Croi2.kicad_pro
- `hardware/foinse2/` — Foinse2.kicad_pro

These child repositories are ignored, not registered submodules. A clean
umbrella clone does **not** contain their CAD. Read the architecture pack without
them; obtain the reviewed board projects separately for implementation.

The earlier long current-system is [preserved verbatim](docs/history/README.md).
Historical alternatives are not additional current requirements. Native CAD,
controlled contracts and measured evidence outrank prose; discrepancies require
a recorded correction, not silent regeneration.

Use review branches and bounded pull requests. Do not publish raw transcripts,
private correspondence, generated research dumps or temporary render trees.
No repository licence has been selected; Rev 1 remains a separate project.
