# Ogma 2 documents

**Start next review here:** [Investigated answers and decision table](architecture/2026-09-18-review-investigations.md).

[18 September full-meeting change audit](architecture/2026-09-18-meeting-change-ledger.md) — requested changes, misses and completion status.

Latest: [13 September architecture review and learnings](architecture/2026-09-13-session-review.md).
Two local servos and CAN FD are review directions; CAD remains preserved.

## Current reading path

- [Architecture review pack](architecture/README.md): the next session's complete nine-chapter walkthrough, mechanism diagrams and open decisions.
- [Current system](../current-system.md): concise controlling architecture.
- [Implementation reference](architecture/implementation-reference/README.md): preserved detailed part comparisons and calculations; optional lookup.
- [10 September joint review](architecture/2026-09-10-session-review.md): supporting source-backed extraction, not required first reading.
- [Firmware handoff](firmware-handoff-2026-09-07.md): detailed hardware/driver contract.
- [Hardware entrypoint](../hardware/README.md): local CAD boundary and checks.
- [Project log](../project-log.md): dated decisions and observed results.

The architecture pack is self-contained. Older detailed records may reference
workspace-local CAD or research; those links are not promised in a clean clone.
Read current truth first. A dated selection or failed experiment remains history,
not an instruction to restore it.

## Owned interfaces

- [Flight fault contract](../interfaces/flight-fault-contract.md)
- [Power contract](../interfaces/power-contract.md)
- [Reset/recovery contract](../interfaces/reset-recovery-contract.md)
- [Ogma/Foinse/propulsion boundary](../interfaces/ogma-foinse-propulsion-boundary.md)

## Accepted changes and rationale

| Record | Purpose |
| --- | --- |
| [External installation and readable schematics](installation-change-record-2026-09-08.md) | MAX-M10S external antenna, maintained enable contacts, installed CAD checks and remaining tests |
| [Architecture acceptance](architecture-acceptance-2026-09-07.md) | Batch acceptance and first-full-PCBA testing sequence |
| [Three servos, readiness and SMA](connector-servo-readiness-revision-2026-09-07.md) | Third timer channel, complete new servo pinout and complementary LEDs |
| [Radio revision](radio-change-2026-09-07.md) | Wio-LR2021 replaces E22; exact signal/driver delta |
| [Sensing, indication and time](sensing-indication-time-review-2026-09-07.md) | Croí bulk-current monitor, passive piezo and internal RTC |
| [Sensor configuration](sensor-configuration-review-2026-09-07.md) | Rates, range/validity and independent sensor branches |
| [Rev 1 external-review lessons](rev1-external-review-lessons.md) | Preregulator/LDO and serviceable packaging rationale |

## Deeper reference, not the first read

- [MCU pin-capacity audit](mcu-pin-capacity-audit-2026-09-11.md): fresh 200-pad
  connectivity check, complete allocation and smaller comms-package comparison.
- [Power, recording and CAN audit](power-recording-can-audit-2026-09-11.md):
  traced optional loads, hold-up sensitivity, history/storage budgets and
  candidate actuation traffic. Recommendations, not accepted changes.

| Record | Purpose |
| --- | --- |
| [Reliability execution plan](reliability-execution-plan.md) | Tests, dependencies and release gates |
| [Reliability review](reliability-design-review.md) | Power/reset/sensing/storage/output failure analysis |
| [Kármán hardening report](karman-line-mission-hardening-report.md) | Bounded suborbital environment; not orbital lifetime |
| [Avionics options review](avionics-options-review-2026-09-07.md) | Dated radio/GNSS/CAN/sensor comparison |
| [Above-80-km height study](height-estimation-above-80km-2026-09-07.md) | Non-binding receiver/inertial/tracking comparison |
| [PCB layout guide](pcb-layout-guide.md) | Layout order and local manufacturer-page references |
| [Placement history](croi2-functional-placement-2026-09-07.md) | Provisional placement, not final routing |
| [Library preparation](kicad-library-preparation.md) | Historical feasibility and provenance |
| [Model gaps](model-recovery-2026-09-07.md) | Remaining bodies/footprint distinctions |
| [MCU allocation study](mcu-resource-and-timing-results.md) | Earlier reservation rationale; current exact pins are in the handoff |
| [Host checkpoint model](../tests/reset_replay/README.md) | Non-actuating host tests; not target reset evidence |
| [Verification template](templates/verification-record.md) | Repeatable result record |
| [Design review procedure](design-review-operating-procedure.md) | Recommendation-first collaboration |
| [History](history/README.md) | Verbatim earlier current-system snapshot |

Keep raw transcripts and private source dumps outside this repository.
