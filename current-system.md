# Ogma 2 current system

Updated 2 November 2026. Decisions live in [decisions.md](decisions.md); this
file states what is true now. Native CAD still holds the 8 September draft.
Capture of the [capture specification](docs/architecture/schematic-capture-spec.md)
waits for Seán's go-ahead after the Tuesday 3 November review. No fabrication,
firmware or flight release exists.

## The system

Ogma 2 is HiPR's workhorse flight computer. It owns two boards:

| Board | Name | Job |
| --- | --- | --- |
| Croí2 | Burrito | Flight computer: sensing, estimation, mission state, recording, recovery and staging outputs, servos, CAN; separate comms processor for GNSS, radio and USB |
| Foinse2 | Churro | MCU-less power board: protected 2S avionics and 6S propulsion feeds, from the packs or the rail umbilical; propulsion current, voltage and temperature monitoring |

Fajita, the propulsion controller, is owned by propulsion and governs itself.
Independent vehicle recovery, the groundstation and payloads are external.
Closed-loop actuators (roll control, grid fins) go on their own node under the
D-2Nov.8 rules; which board waits for Sim Systems' requirements. Start with the
[system tour](docs/architecture/system-tour.md).

## Rules that constrain the design

- Two processors (D-6.12): flight and comms. They separate timing from
  communications; they are not redundant. The flight MCU must complete the
  mission with the comms MCU held in reset.
- Only the flight MCU commands recovery and staging outputs. Radio, USB and CAN
  cannot.
- Pyro and servo energy leave before the Croí eFuse U101, at a tap after Q101,
  each through its own fuse: F6101 recovery, F6102 staging, F6801 servos (D-6.1,
  D-2Nov.2, D-2Nov.5). An output fault can't pull down logic power. Pyro energy
  then passes an external physical arm switch: J6101 recovery, J6102 staging.
- Three pyro channels and three servos are a core requirement (D-7.1). Each
  channel has a current-limited TPS1H100 high side (≈2.0 A) and a CSD17318 low
  side, driven from different GPIO ports (D-2Nov.1). One channel fires at a time.
  Channels 1 and 2 are recovery. Channel 3 is staging / air-start, behind its
  own arm and the hardware reset latch (D-7.2).
- Before arming, firmware checks each low side against continuity; after
  arming, a high side that reads as leaking is never fired.
- Burrito's servos make bounded, event-triggered moves only, such as unlatching
  a payload at booster apogee. A closed-loop actuator has its own processor and
  fast sensor, goes to neutral through a path that survives hung firmware, stays
  dormant until Burrito authorises it, and has its own fused Churro feed
  (D-2Nov.8).
- After launch detect, firmware holds the battery enable on (Croí and Churro
  AV). An RC keeps it on for ≥1 s if firmware lets go; after any reset in flight
  firmware re-asserts it within 50 ms; it releases at LANDED plus a delay or at a
  maximum flight time (D-6.3, D-2Nov.4). U101 and Churro U1001 auto-retry.
- Any in-flight flight-MCU reset inhibits further sustainer ignition. Recovery
  resumes only through the [recovery logic](docs/architecture/10-recovery-logic.md).
- CAN is external, linear and two-node (Ogma ↔ Fajita), 500 kbit/s Classical for
  Rev A. It carries permissions and mode, slow state that survives Burrito's
  worst-case 550 ms restart, health, and commands the receiver drops to safe when
  stale; never a loop at loop rate (D-2Nov.9). An actuator node may join only
  under D-2Nov.8, on an unterminated stub, with the propulsion owner's agreement.
- Foinse owns source entry and protection; Ogma is not a power distributor. On
  the rail the vehicle runs from a ground umbilical at Churro, through
  per-source ideal diodes ahead of the eFuses; pulling it hands each feed to its
  pack. Nothing on the vehicle charges a pack (D-2Nov.7).
- Battery, CAN, pyro and servo use keyed, locking board connectors. Bare-wire
  terminals live only on detachable development adapters.
- Never attach standalone and Churro batteries at once. USB powers service logic
  only: no charging, no output energy.
- Every extra component, processor, connector or mode needs a named function,
  failure boundary and test ([11 Verification](docs/architecture/11-verification.md)).

## Power path

2S source → Q101 reverse blocking → `ENERGY_TAP`, where the outputs and servos
branch off → U101 eFuse (≈6.0 A, auto-retry) → 5 mΩ shunt → TPS2121 battery/USB
mux → TPSM63603 4.0 V buck → three TPS7A91 domains (flight, comms, services) at
3.352 V. Flight hold-up: 1000 µF, about 2 ms. Flight VBAT has its own Schottky
and 100 µF (D-6.4). Sensors run from FLIGHT_3V3 through 47 Ω links (D-6.6,
D-2Nov.3); the magnetometer through 22 Ω. The flight-core input enables whenever
the buck is up (D-6.5).

The avionics pack is 2S Li-ion in metal-can cylindrical cells, 21700 by default;
no LiPo. It alone covers ≥6 h on the rail plus the flight (D-2Nov.6). Pad-mode
target ≤150 mA, to be measured.

J103 is the FC battery enable: open means off, upstream circuits stay live. It
is not an arm and not physical isolation. Churro has separate AV and PROP
enables. Charging uses external balance chargers with the packs off the vehicle.

## Parts (8 Sep CAD, with decided changes)

| Block | Selection |
| --- | --- |
| MCUs | STM32H563VIT6 flight; STM32H563RIT6 comms (D1; the CAD still has a VIT6) |
| Low-g IMUs | ST LSM6DSV16XTR, TDK ICM-42688-P |
| High-g | ADI ADXL375BCCZ, ±200 g nominal |
| Pressure | Bosch BMP390, TE MS560702BA03-50, separate buses |
| Magnetometer | MEMSIC MMC5983MA on I²C3, 100 Hz, non-essential (D-2Nov.11) |
| Recording | MX66L2G45GMI00, 256 MiB NOR |
| Radio | Wio-LR2021 (Seeed 100058045), vertical SMA |
| GNSS | MAX-M10S-00B, external passive antenna via SMA; 80 km / 4 g / 500 m/s limits |
| Supervision | TPS3808 supervisors, TPS3430 earned-heartbeat watchdog |
| Current | Croí INA228 0x40 (logic path); Foinse propulsion INA228 0x41; ADS1115 0x48 |
| Outputs | Per channel a TPS1H100 high side and a CSD17318 low side (2 recovery + 1 staging); U6001 staging latch with an SN74LVC1G08 AND; one servo TPS1H100 at ≈2.0 A shared by three servos |
| Churro rail power | Four LM74700-Q1-class ideal-diode stages, umbilical connector J801, fuse and TVS (D-2Nov.7) |
| Indication | Red/green readiness, comms amber, hardware power LED, passive piezo |

## Interfaces

| Interface | Contract |
| --- | --- |
| Croí ↔ Foinse | Samtec MPT/MPS-08-01-01-L-RA-SD: 1 battery, 2 GND, 3 AUX 3.3 V, 4 GND, 5 SCL, 6 SDA, 7 fault, 8 `CROI_POWER_HOLD` |
| Standalone 2S | Molex Nano-Fit 1053111102; footprint still to draw |
| Pyro arms J6101 / J6102 | Recovery / staging (D-7.2), each with its own fuse. 2-contact each, to external arm switches. Must not mate each other, Churro J701 (Micro-Fit 430450200, raw PROP) or the GH enable loops; parts chosen at capture |
| Outputs J6601 | Micro-Fit 430450600: 1/2/3 high sides, 4/5/6 returns through each channel's low side |
| Servos J6602 | Micro-Fit 430451000: PWR/PWM/GND on 1/2/3, 4/5/6 and 7/8/9; 10 unwired |
| CAN J501 | JST GH: 1 CAN H, 2 CAN L, 3 reference; no power |
| Umbilical J801 (Churro) | AV+ / AV− / PROP+ / PROP−; AV 8.4 V, PROP ≈24–25 V at Churro; part and mechanism with the vehicle owner |
| Inter-MCU | Framed UART, 2 Mbaud |
| Service | USB-C (USB4105-GF-A) on comms; TC2030 debug pads for both MCUs |

Full contracts: [power](interfaces/power-contract.md), [flight fault](interfaces/flight-fault-contract.md),
[reset and retained state](interfaces/reset-recovery-contract.md),
[Ogma/Foinse/propulsion boundary](interfaces/ogma-foinse-propulsion-boundary.md).
Firmware: [firmware interface](docs/firmware-interface.md).

## Mission envelope

| Item | Workhorse | Kármán overlay |
| --- | --- | --- |
| Missions | 3–9 km; solid, hybrid, liquid | One sortie to ≥100 km and back |
| Endurance | ≥6 h on the rail plus flight (EuRoC); otherwise from measured loads and the vehicle timeline | 8 h powered + 4 h recovery reserve |
| Full-rate recording | Launch detect to LANDED + tail | ≥30 min |
| Service life | Inspected after each flight | 5 years, 25 flights |
| Pressure survival | Ambient to 9 km | Toward 0.01 Pa |

Shared provisional targets: powered −20 to +70 °C; 50 g quasi-static; 200 g
shock target; ≥±2000°/s rotation measurement; closed-bay splash only.
Independent recovery is required on early flights where Ogma has live recovery
authority; for EuRoC the mandatory CATS Vega is that set.

Target vehicles, as said at the 14 October requirements meeting:

- **EuRoC, October 2027.** Liquid, about 6 m long, 6 in diameter. Bottom up:
  engine, tanks and COPVs, av-bay (RCS at its bottom), recovery bay, grid fins,
  nose. Armed on the pad before filling; nobody within 600 m once anything is
  pressurised; the umbilical powers the rocket until it disconnects remotely at
  Go. EuRoC SRD Issue 1.1: ≥6 h on the rail (LV-0320); no LiPo (0300); a CATS
  Vega in every stage (0430); fully redundant recovery electronics with their own
  power, one set COTS (0240, 0250); switches, connectors and batteries touched
  on the pad reachable from the ground, no ladders, opposite the rail
  (0260–0280, 0310, 0540–0550). Open: where the packs and arm switches go (the
  av-bay is above the tanks), and whether LV-0690 makes roll control redundant.
- **IREC.** Solid O motor, 152.4 mm, the same electronics without propulsion
  control.

Croí's 80 mm width fits both.

## Fault and software policy

- Watchdog feeding requires progress of acquisition, estimation and phase policy.
  Comms, bulk recording and the magnetometer never gate it.
- Bound retries; disable persistent optional faults; never reset flight to
  restore telemetry. A sensor given up on has its bus pins parked.
- Record reset cause and supply evidence before initialisation clears them.
- Recording is append-only, checked and replayable; full rate from launch detect
  with a RAM pre-trigger (D-6.9). Telemetry is never the only record.
- The pad datum is tracked on the pad and frozen at launch detect; a reset never
  creates one. Pad telemetry at 1 Hz shows arm, continuity, latch and power
  state. A ground-test mode serves EuRoC's recovery ground test (D-2Nov.10).
- Initial budgets: 128 MHz, 1 kHz essential loop, 200 Hz estimation/policy,
  30% timing reserve. These are allocations, not measurements.

## State

| Item | State |
| --- | --- |
| Croí CAD | 44 pages, 643 parts, unrouted, 80 × 230 mm working canvas; ERC 4 errors / 6 warnings; DRC 61 + unrouted |
| Foinse CAD | 12 pages, 113 parts, unrouted, 60 × 80 mm; ERC clean; DRC 24 + unrouted |
| Known CAD gaps | Nano-Fit footprints on both boards; Croí USB footprint mismatch; every decided change since 6 October (capture specification) |
| Firmware | [Firmware interface](docs/firmware-interface.md); build-pipeline brief v0.1.0 (Anav); no target code yet |
| Tests | Host checkpoint model only (12 tests); no hardware tests. Gates and campaigns in [11 Verification](docs/architecture/11-verification.md) |

## Next

1. Tuesday 3 November, after the firmware meeting: Anav, Arnav and Seán review
   PR #2 and the 2 November decisions; Anav reviews the recovery logic (D-6.11)
   and his pyro-channel circuit against D-2Nov.1.
2. Jay: where the packs and arm switches go for EuRoC access, the umbilical,
   and the LV-0690 question to the EuRoC officials (through #euroc-electronics).
3. Radion and Sim Systems: roll-control and grid-fin requirements, then the
   actuator node's board (D-2Nov.8); what the magnetometer has to deliver.
4. Seán lifts the capture hold; capture the specification with an independent
   human review page by page.
5. Place, then Seán routes. Footprint, rating and assembly review before order (G1).
6. First PCBA: functional blocks on inert loads, per
   [11 Verification](docs/architecture/11-verification.md#bench-tests-by-block).

History: [project log](project-log.md) and [archive](docs/archive/README.md).
