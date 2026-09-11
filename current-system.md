# Ogma 2 current architecture

Updated: 11 September 2026
Status: requirements and architecture reopened in joint review. Existing CAD
preserved; no schematic/PCB work until Seán authorizes the final stack.

## Direction now

Preserve the 8 September implementation as a reference, not an instruction to
finish it unchanged. The 10 September session with Seán, Anav and Arnav reopened
local output count, remote actuation/control allocation, CAN topology, MCU
selection by role, power-domain purpose and operator indication. Proposals have
not replaced the installed interface contracts. No final stack was authorized.

Start with the [architecture reading pack](docs/architecture/README.md) for the
next joint session. Read the whole pack each pass; questions and misunderstandings
feed back into its explanations and diagrams. The
[joint-review record](docs/architecture/2026-09-10-session-review.md) preserves
supporting observations, alternatives and source evidence. The system/part tables
below describe the preserved draft unless explicitly stated otherwise.

Working names: **Burrito = Croí2 core**, **Churro = Foinse2 power companion**,
**Fajita = separate propulsion controller**. Ogma remains the family name for
now. File, net and CAD names are unchanged.

The [architecture review pack](docs/architecture/README.md) is the reading path:
one overview, eight domain chapters, research and tradeoffs behind the circuitry, and remaining
decisions. Explain the mechanism and its purpose before the component list;
review it together rather than treating unread sections as accepted.
Seán owns final PCB layout; Anav owns firmware implementation.

Authorised installation changes are **implemented in the checked CAD draft**:

- Move GNSS reception outside the carbon airframe. Replace the integrated-antenna
  receiver with MAX-M10S, vertical SMA and low-capacitance RF ESD protection.
  Passive antenna baseline; the actual antenna/coax assembly remains unqualified.
- Provide external power-switch connections for Foinse and standalone Croí.
  Do not put the operational mechanical switch on the vibrating PCB.
- Keep physical energetic arming separate from ordinary computer power.
  A power switch is not proof that every energetic path is safely isolated.

The [installation record](docs/installation-change-record-2026-09-08.md) defines
the exact parts, connector pins, checked scope and remaining hardware tests.

## System

### Open review deltas — not implemented

- Keep standalone core operation and timing/fault separation; two MCUs remain
  a shared-board architecture, not independent recovery.
- Reassess three local servo channels against actual vehicle functions.
  Compare central control with a remote output node against autonomous local
  actuation. No loop-rate/latency result settles that choice yet.
- Linear CAN trunk/short drops and additional named peers were proposed.
  Existing two-node 500 kbit/s Classical CAN remains the unchanged contract;
  no CAN FD, new termination or third endpoint is approved.
- Compare MCU resources by role before retaining or replacing both H563s.
  No replacement, RTOS policy or new pin allocation is selected.
  The [11 September pin audit](docs/mcu-pin-capacity-audit-2026-09-11.md)
  finds flight pin-full but comms with substantial unused I/O. H563 LQFP64
  is a desk-mapped comms candidate, requiring two UART port changes; not approved.
- Explain every power rail and startup dependency before considering deletion.
  Common battery-current sensing remains useful on standalone Burrito.
  Churro regulation/BMS/charging scope still needs actual load requirements.
- Separate operator questions: logic powered, firmware/configuration verified,
  healthy/fresh peers, physical output arm and channel continuity. RGB, rail,
  continuity and CAN LEDs are candidates, not an approved set.
- Shared servo/energetic physical enable is a working direction only. The
  energetic mechanism review was deferred; existing inhibits and DNPs stay.
- Add pre-trigger logging requirements and distinguish interrupted writes,
  physical damage and a lost vehicle. Durations and survival claims remain open.
- Keep experimental expansion on a separately scoped payload carrier rather
  than silently enlarging the flight core. No carrier hardware is selected.

The [11 September power/recording/CAN desk audit](docs/power-recording-can-audit-2026-09-11.md)
adds calculations to the reading pack. Optional power also supplies CAN and
the sounder; held flight power does not hold up NOR. The current 128 KiB staging
budget represents about 1.36 s at 96,672 B/s. Continuous prelaunch recording and
central remote-actuation control are review recommendations, not new requirements.
Candidate bus utilisation is calculated; actuator latency and fault tests remain.

All previous implementation/ordering sequences are subordinate to the explicit
final-stack authorization gate. This documentation pass does not change a
cross-system electrical contract, release hardware or authorize live testing.

Croí2 is the standalone workhorse flight-computer PCB. Foinse2 is a separate,
MCU-less power companion for larger vehicles. Their Samtec connection is
coplanar; supports carry the mechanical loads. Neither board conceals the other.

| Owner | Responsibility |
| --- | --- |
| Flight MCU U201 | Acquisition, estimation, mission state, local recording, three energetic channels, three servo commands and vehicle CAN |
| Comms MCU U401 | GNSS, radio, telemetry buffering and USB service |
| Foinse2 | Autonomous source protection, separate vehicle power branches and bounded monitoring |
| Propulsion controller | Local engine state, permissives, redlines, valves, ignition and abort |
| Independent recovery / payloads | Their own qualified function and power; no dependency on Croí logic power |

The two MCUs separate timing and failure domains. They are not redundant flight
computers. Flight must continue with comms held in reset; radio, GNSS, USB and
optional monitoring cannot become boot or deadline prerequisites.

## Selected hardware

| Block | Current selection |
| --- | --- |
| MCUs | Two STM32H563VIT6, non-SMPS LQFP100 |
| Low-g IMUs | ST LSM6DSV16XTR and TDK ICM-42688-P |
| High-g | ADI ADXL375BCCZ; nominal ±200 g, minimum specified range ±180 g |
| Pressure | Bosch BMP390 and TE MS560702BA03-50, separate buses |
| Flight storage | MX66L2G45GMI00, 256 MiB soldered NOR |
| Radio | Wio-LR2021 868/915 MHz, Seeed 100058045; vertical standard SMA 132134 |
| GNSS | MAX-M10S-00B; external passive antenna via vertical SMA 132134 and TPD1E0B04DPYR RF protection; 80 km navigation limit |
| Logic power | 2S battery; TPS2121 battery/USB selection; TPSM63603 4.0 V preregulator; three TPS7A91 3.3 V domains; no boost |
| Supervision | TPS3808 supervisors, TPS3430 earned-heartbeat flight watchdog, LM73100 held-core input |
| Current | Croí INA228 0x40 and 5 mΩ common battery shunt; Foinse propulsion INA228 0x41 |
| Foinse acquisition | ADS1115 0x48, two temperature and two voltage inputs; no MCU/CAN endpoint |
| Indication | Complementary red/green readiness, comms amber, hardware power LED and passive piezo |
| Time | Local monotonic mission time; internal flight RTC with LSE, no external RTC or backup cell |

Support values are engineering starting points unless a reviewed record says
otherwise. Part selection and connectivity checks are not physical qualification.

## Power and output boundaries

Both exclusive Croí battery entries feed the same protected path and common
current shunt. Never attach standalone and Foinse batteries simultaneously.
USB supplies service logic only; no charging or output-energy path through USB.

External maintained contacts control Croí J103 and Foinse J103/J104. Each
two-contact JST GH carries bounded 3 V bias and its branch's SHDN return.
Open/unplug is electronic OFF; closed enables. Foinse-fed Croí requires a
deliberate retained closed enable plug or its own isolated switch pole.
OFF leaves upstream circuits live and is not physical energetic isolation.

Battery logic uses fixed switching preregulation followed by low-noise LDOs.
Flight, comms and optional loads have deliberate supply/signal boundaries.
A failed optional peripheral must not back-power or clamp the essential domain.
Common source, preregulator, board and flight-MCU faults remain.

Croí's three energetic channels and three servos use battery-derived energy,
not the 3.3 V logic rail. Servo power has a common provisional 2 A switch limit;
this is not a validated grid-fin load allocation. Actual servos must tolerate
the source voltage and meet PWM, peak/stall-current and regeneration limits.

The physical arm assembly, group protection and load-specific no-fire,
continuity, pulse and current values remain unfinished. R6310, R6410, R6510
and R6804 stay DNP. Do not connect initiators. Ordinary power switching cannot
replace physical energetic isolation or the independent disarm-proof input.

Foinse keeps 2S avionics and 6S propulsion positives separate. Its protection
starts without Croí, I²C or the returned auxiliary supply. Charging uses matched
external balance chargers and controlled fused service wiring. A regulated
24 V propulsion rail remains conditional on actual coils; no valve count or
finished converter is implied.

## Interfaces

| Interface | Current contract |
| --- | --- |
| Croí ↔ Foinse | Samtec MPT-08-01-01-L-RA-SD / MPS-08-01-01-L-RA-SD: 1 battery, 2 GND, 3 protected auxiliary 3.3 V, 4 GND, 5 SCL, 6 SDA, 7 fault, 8 NC |
| Standalone 2S | Nano-Fit 1053111102; exact footprint unresolved |
| Energetic harness J6601 | Micro-Fit 430450600, three independent channel pairs |
| Servo harness J6602 | Micro-Fit 430451000: PWR/PWM/GND on 1/2/3, 4/5/6, 7/8/9; 10 NC |
| CAN | JST GH: 1 CAN H, 2 CAN L, 3 reference; no power contact |
| Vehicle CAN | 500 kbit/s Classical CAN, one linear two-node Ogma/propulsion link, fixed 120 Ω ends |
| Inter-MCU | Bounded framed UART; 2 Mbaud flight, 20 kB/s routine traffic cap; higher disarmed-service rate requires validation |
| Service | GCT USB4105-GF-A and independent TC2030-NL debug patterns for both MCUs |

Each Samtec ground path must carry the full alternative fault return.
Propulsion power returns must not migrate into the thin CAN reference if a
power conductor opens. Common ground is not galvanic isolation.

Flight PC6/PC7 use TIM3 for servo 1/2; PD10 uses LPTIM2_CH2 AF3 for servo 3.
PD7 controls complementary readiness. These physical allocations are frozen.
The child board's current pin CSVs control, not older shared-library copies.

## Mission envelope

These are provisional design budgets, replaced by vehicle simulation and
measurement before mission qualification. They do not override the current
explicit hold on schematic and PCB work.

| Item | Provisional baseline |
| --- | --- |
| Workhorse missions | 3–9 km; solid, hybrid, liquid, single-stage and multistage |
| Extreme mission | One short sortie to at least 100 km and back; no orbital-lifetime claim |
| Operation | 8 h powered plus 4 h reduced-duty recovery reserve |
| Full-rate recording | At least 30 minutes |
| Service / reuse | 5 years; 25 inspected flights; acceptance after each flight |
| Powered temperature | −20 to +70 °C; prefer components rated at least −40 to +85 °C |
| Ambient pressure | Survival toward 0.01 Pa; sensor validity is separate |
| Mechanical screening | 50 g quasi-static; 200 g provisional shock target, waveform unresolved |
| Rotation measurement | At least ±2000°/s; detect saturation |
| Vibration / moisture | Measured vehicle spectrum required; closed-bay rain/splash, not exposed wet PCB |

Kármán population has physically unpowered/DNP energetic and servo sections.
It is not the primary recovery/actuation system. Independent vehicle recovery,
power and full-envelope altitude proof are separate responsibilities.
Initial flights with live Ogma recovery also require appropriately independent
recovery. No commercial backup device is selected by this document.

## Fault and software policy

- Watchdog feeding requires progress of essential acquisition, estimation and
  phase policy. Comms and bulk recording are not unconditional in-flight gates.
- Bound retries and disable persistent optional faults; never reset flight just
  to restore telemetry.
- Preserve reset cause, identities, time validity and fault evidence.
  Two checkpoint slots do not provide independent power or writer redundancy.
- Any in-flight flight-MCU reset inhibits further sustainer ignition.
  Recovery resumes only through a validated phase-specific path.
- Local logging is append-only, checked and replayable. Telemetry is not the
  only record. Current is electrical evidence, not proof of motion or ignition.
- Initial budgets: 128 MHz CPU, 1 kHz essential schedule, 200 Hz estimator/policy,
  30% timing reserve. These are allocations, not measured execution limits.
- Normal USB operation is offline, readable and verifiable: identify, read,
  change, read back, compare and extract logs without disturbing the closed bay.

The [fault](interfaces/flight-fault-contract.md),
[power](interfaces/power-contract.md) and
[reset](interfaces/reset-recovery-contract.md) contracts retain detailed obligations.

## Engineering state and next sequence

Installed checked CAD: Croí 44 pages / 643 physical symbols / 642 footprints;
Foinse 12 pages / 113 symbols / 112 footprints. Both are four-layer, 1.6 mm,
unrouted engineering drafts. Croí's 80 × 230 mm and Foinse's 60 × 80 mm are
provisional canvases, not final dimensions. These are the previous checked
snapshot, not checks rerun for the 11 September documentation update. All
schematic and PCB work remains frozen until final-stack authorization.
New installation parts are staged outside the outlines: eight Croí, twelve
Foinse. Circuit pages now explain purpose and connections with local wiring.

Existing Croí ERC: four errors, six warnings; Foinse: zero.
Current PCB DRC: 61 / 24 findings, plus unrouted connections and missing
Nano-Fit footprints. No exclusions were added to call either board clean.
C1403 is an unresolved hold-up-capacitor volume allocation.

1. Readable documentation baseline published on the review branch.
2. GNSS and external-switch implementation recorded and installed in draft.
3. Connected schematics installed; native identity/pad-net checks pass.
4. Review the 10 September deltas and actual mechanisms together. Resolve
   function/output allocation, remote control/CAN, processor roles, power,
   indication and logging requirements with explicit dispositions.
5. Obtain Seán's final-stack authorization before any schematic/PCB changes.
   Then reconcile affected interfaces and firmware assumptions before layout.
6. Review pins, footprints, ratings, inhibits and assembly before the first PCBA.
7. Test functional blocks on that first full PCBA using inert loads.
   No separate pre-order mini-PCB/coupon gate. Installed qualification follows.

History remains in the [project log](project-log.md), dated decision records and
the [verbatim earlier current-system snapshot](docs/history/README.md).
