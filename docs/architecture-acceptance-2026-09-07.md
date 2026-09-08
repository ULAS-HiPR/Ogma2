# Ogma 2: accepted implementation baseline

7 September 2026. Decision record, not a hardware test or manufacturing release.

Later same-day amendment: Seán accepted the
[six-action review and Wio radio replacement](radio-change-2026-09-07.md).
That record supersedes E22 selection below; all other retained parts, physical
MCU allocations and first-PCBA testing policy remain. Above-80-km work stays
non-binding. The original acceptance is preserved here as chronology.

## Decision and authority

Seán explicitly accepted the complete 6 September architecture review, including
its qualifications and tradeoffs. He separately endorsed the selected connectors.
EX-01–EX-10 now have accepted recommended answers. We do not restart the
question-by-question approval loop. Acceptance does not close unperformed work.

One execution change: **no separate mini-PCB/coupon build before the first full
PCBA order. Test the functional blocks on the first assembled boards.** This
supersedes the review's coupon-before-schematic/order dependencies, not the
electrical claims or their required tests.

Seán states that he sent Anav the firmware handoff and that Anav can start
coding the architecture. This records Seán's report, not independently verified
delivery or Anav's implementation progress. Preserve the accepted hardware
interface; firmware structure and implementation remain with Anav and his
chosen collaborator. Report a demonstrated hardware conflict before changing it.

The accepted detail is the seven integrated chapters in the local
[complete reading copy](../../architecture-review-2026-09-06/READING-COPY.md),
with its linked part tables, full MCU pin maps and source qualifications.
Those chapters take precedence over earlier candidate comparisons. Their
original proposal wording records their status when written; this decision
records subsequent acceptance. Original review files remain unchanged.

Current authority: controlled implementation and measurements, then
`current-system.md` and this decision, then the accepted integrated review,
then its research appendices, then earlier studies. Earlier unanswered
questions are not automatically still open when the accepted review answers them.
An explicitly deferred part or unmeasured value remains deferred or unmeasured.

The detailed review is currently a **local sibling dependency**, not present in
a clean clone of this repository. Curate its implementation tables into the
repository before sharing a self-contained implementation baseline. Do not
import the private source-history dump or publish anything by implication.

## Selected hardware

| Block | Accepted baseline |
| --- | --- |
| Boards | Standalone Croí 2 plus separate MCU-less Foinse 2; coplanar end-to-end mounting with independent supports and connector retention bridge |
| Allocation | Croí 60 × 120 mm; Foinse 60 × 80 mm; four layers, 1.6 mm, double-sided. Provisional placement rectangles, not released outlines |
| Flight and comms MCUs | Two STM32H563VIT6, non-SMPS LQFP100; distinct roles, not redundant flight computers |
| Core operating point | Initial 128 MHz/VOS2; 1 kHz essential loop, 200 Hz estimation/policy; measured timing still required |
| IMUs / high-g | LSM6DSV16XTR; ICM-42688-P; ADXL375BCCZ |
| Pressure | BMP390; MS560702BA03-50; separate buses and validity limits |
| GNSS / radio | SAM-M10Q-00B soldered antenna module; E22-900M22S; Taoglas FXP895.07.0200C external radio antenna |
| Storage | MX66L2G45GMI00, 256 MiB soldered NOR; no flight erase, no flight SD socket |
| Logic source | 2S battery; TPS2121 battery/USB logic-source selection; no logic boost |
| Logic conversion | TPSM63603RDHR at 4.0 V; three TPS7A9101DSKR 3.3 V domains; separate tiny TPS70933DBVR bootstrap bias |
| Supervision | LM73100 core reverse isolation; bounded hold-up; TPS3808G33DBVR supervisor and TPS3430WDRCR earned-heartbeat watchdog |
| Branch containment | Limited sensor, comms, storage, CAN and auxiliary paths with the accepted powered-off signal isolation; component details in the power appendix |
| Foinse | Pack-powered protection independent of Croí; TPS26630RGER/CSD18540Q5B protected source; INA228 and ADS1115 monitoring, no software protection dependency |
| Outputs | Three battery-derived energetic channels and two HV-compatible servo channels; hardware recovery domain on channels 1/2, staging on channel 3 |
| Output circuit | TPS1H100BQPWPRQ1 + CSD17318Q2 + non-retriggerable LTC6993IS6-1; SN74LVC1G74 staging eligibility latch; exact passives/analogue frontends still need completion |
| Vehicle link | 500 kbit/s Classical CAN, TCAN3413DRBR, fixed 120 Ω at each end of the two-node line; CAN and reference only from Croí |
| Liquid power | Separate 2S avionics and 6S propulsion pack domains; exact actuator branch/current and conditional regulated 24 V population depend on real coils |
| Charging | External matched balance charger per pack through controlled service access; physical charge/arm exclusion; no onboard charger or Foinse MCU |

Supporting implementation tables:
[flight pins](../../architecture-review-2026-09-06/research/flight-pinout.csv),
[comms pins](../../architecture-review-2026-09-06/research/comms-pinout.csv),
[DMA](../../architecture-review-2026-09-06/research/dma-allocation.csv),
[core parts](../../architecture-review-2026-09-06/research/core-parts.csv),
[connector parts](../../architecture-review-2026-09-06/research/connector-parts.csv).
These are design inputs, not a completed netlist or BOM.

## Selected connectors

| Connection | Accepted PCB part / mating harness |
| --- | --- |
| Foinse → Croí | Foinse MPS-08-01-01-L-RA-SD; Croí MPT-08-01-01-L-RA-SD |
| 2S battery | Nano-Fit 1053111102 / 1053071202; 1053002100 contacts; 1053251002 TPA |
| 6S battery | Micro-Fit 430450400 / 430250400; 430300007 contacts |
| Three energetic channels | Micro-Fit 430450600 / 430250600; 430300007 contacts |
| Two servos | Micro-Fit 430450800 / 430250800; 430300007 contacts |
| CAN | JST BM03B-GHS-TBT(LF)(SN) / GHR-03V-S; SSHL-002T-P0.2 contacts |
| USB-C | GCT USB4105-GF-A |
| Debug | Two TC2030-NL-compatible PCB patterns; shared TC2030-CTX-NL bench cable |

Samtec pins: 1 `VBAT_CROI`, 2 `PWR_GND`, 3 protected `3V3_AUX`,
4 `AUX_GND`, 5 SCL, 6 SDA, 7 nFAULT, 8 NC. Each of the two ground
paths must carry the full 6 A fault return if the other opens. Auxiliary
positive-current limiting does not limit that alternate ground current.
Six solder tails per electrical contact must share its pad number correctly.
The screw-down bodies do not latch the halves together. Installed restraint,
wire gauge, mating orientation and exact manufacturer drawings still govern.

## Qualifications retained

- Flight GPIO allocation has no spares. Do not invent expansion or silently
  move the interface Anav received.
- SRAM2/3 provide the selected ECC regions. Two checkpoint slots use the H563
  backup domain with VBAT tied to held flight 3.3 V. No retention after loss of
  that supply is claimed; no independent backup battery is selected.
- Software-reset recovery target is 100 ms. Watchdog reset is different:
  proposed 400 ms from assertion and 550 ms from last earned heartbeat through
  recovery. None is measured timing or a universal vehicle safety limit.
- Core-LDO input/output short remains an uncontained fault in this prototype.
  Shared board, source and flight MCU remain common failure points.
- ADXL375 is nominal ±200 g but minimum specified range is ±180 g. GNSS and
  ordinary pressure sensors do not establish full-envelope altitude at 100 km.
- The Kármán population has physically unpowered/DNP energetic and servo
  sections. It is a recorder/navigation unit, not primary recovery hardware.
  Vehicle-level recovery, actuation and full-envelope altitude proof are separate.
- Independent recovery has its own qualified power/actuation path outside the
  shared Foinse fault boundary. No backup device is selected here.
- The 2S energy budget, USB bootstrap, hold-up, isolation during partial rail
  ramps, sensor validity, storage throughput and installed environmental/RF
  performance still need physical evidence. The parts table is incompletely
  priced; acceptance does not create a PCBA quote.

## Build sequence after the schedule change

1. Prepare project-local KiCad libraries and check exact pin/pad mapping,
   manufacturer land patterns, exposed pads, orientations and mechanical holes.
   Keep provenance and verification status; a downloaded model is not approval.
2. Complete and review the schematic, tolerance/current calculations, source
   defaults, physical inhibits, harness mapping and assembly/test access.
   Design the first full board to support isolated block bring-up: existing
   requested 0 Ω isolation links, rail loops, signal probe pads and defined
   population options. Do not put an under-rated link in a fault-current path.
3. Review layout and PCBA files before ordering. Document unresolved hardware
   assumptions and their first-board tests. No pre-order coupon pass is required.
   This permits prototype iteration; it does not make a known pin/rating fault
   acceptable or establish immunity to a respin.
4. On the first PCBA, inspect and test for shorts, then bring up bounded blocks
   using current-limited supplies and inert loads. Test power/USB, rail faults,
   supervision, memory/sensors, links and output circuitry before integration.
   Use the review's tests with the full PCBA as the test article.
5. Complete integrated and installed qualification before the corresponding
   flight claim. Purchasing, live energetic tests and flight release still need
   their own authority. Nothing is uploaded or ordered by this decision.

## Frozen approval reference

SHA-256 of the reading copy inspected for this record:
`6b07121f37ea01de93b7536ef465294f98238a2e442ed8039301b0d063059b5a`.

Flight pin CSV:
`f69a45c23f0318116bf67103fda75203db77682e943a90b25e7e5590ef464154`.

Comms pin CSV:
`337b0ef4273bdc54a688622e7839c6451717d25940067e2b14664284cae12932`.
