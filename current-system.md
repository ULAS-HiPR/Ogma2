# Ogma 2 current system

Updated 21 November 2026. Decisions live in [decisions.md](decisions.md); this
file states what is true now. Burrito's schematic is captured from the
[capture specification](docs/architecture/schematic-capture-spec.md) (21 November;
[status](hardware/croi2/schematic-status.md)); its PCB still holds the 8 September
draft. Churro's capture waits for its power review. No fabrication,
firmware or flight release exists.

## The system

Ogma 2 is HiPR's workhorse flight computer. It owns two boards:

| Board | Name | Job |
| --- | --- | --- |
| Croí2 | Burrito | Flight computer: sensing, estimation, mission state, recording, recovery and staging outputs, CAN; separate comms processor for GNSS, radio and USB |
| Foinse2 | Churro | MCU-less power board: a protected 2S avionics feed and two protected 6S actuator feeds (PROP to Fajita, ACT to Salsa), from the packs or the rail umbilical; charges every pack on the rail; current, voltage and temperature monitoring (D-21Nov.1, D-21Nov.2) |

Fajita, the propulsion controller, is ours too since 20 November, as its own
project (D-20Nov.2); it governs itself. The e-reg is its own board beside the
valve bay, on its own CAN link to Fajita (D-21Nov.10). The active board, Salsa, runs roll
control and the grid fins in a closed loop, on its
own CAN bus from Burrito, powered through Churro's ACT branch (D-2Nov.8, D-5Nov.3,
D-21Nov.1); at IREC it also drives Ériú's nose canards (D-21Nov.7). It is
designed with the build group from 19 November. The CATS Vega is the
independent COTS recovery set (D-18Nov.2). The groundstation and payloads are
external. Start with the [system tour](docs/architecture/system-tour.md).

## Rules that constrain the design

- Two processors (D-6.12): flight and comms. They separate timing from
  communications; they are not redundant. The flight MCU must complete the
  mission with the comms MCU held in reset.
- Only the flight MCU commands recovery and staging outputs. Radio, USB and CAN
  cannot.
- Pyro energy leaves before the Croí eFuse U101, at a tap after Q101, through
  its own fuses: F6101 recovery, F6102 staging (D-6.1, D-2Nov.2, D-2Nov.5). The
  servo branch is gone (D-19Nov.2). An output fault can't pull down logic power. Pyro energy
  then passes an external physical arm switch: J6101 recovery, J6102 staging.
- Three pyro channels are a core requirement (D-7.1; its servos went in D-19Nov.2). Each
  channel has a current-limited TPS1H100 high side (≈2.0 A) and a CSD17318 low
  side, driven from different GPIO ports (D-2Nov.1). One channel fires at a time.
  Channels 1 and 2 are recovery. Channel 3 is staging / air-start, behind its
  own arm and the hardware reset latch (D-7.2).
- Recovery has two independent chains: Burrito's channels 1 and 2 on the AV
  pack through Churro, and the CATS Vega, COTS, on its own cell, with its own
  e-match for each event wired directly (D-18Nov.2; LV-0240, 0250).
- Before arming, firmware checks each low side against continuity; after
  arming, a high side that reads as leaking is never fired. The continuity legs
  are 3.9 kΩ, safe for any igniter with a no-fire current of 25 mA or more
  (D-2Nov.14).
- Burrito has no servos (D-19Nov.2): a one-off move uses a pyro channel or the
  payload's own electronics. A
  closed-loop actuator has its own processor and fast sensor (the active board
  adds its own magnetometer, D-5Nov.1), goes to neutral through a path that
  survives hung firmware, acts only on a fresh Active from Burrito (D-5Nov.2),
  and takes its actuator power from Churro's ACT branch through its own arm
  key, never from Burrito (D-2Nov.8, D-21Nov.1). Unpowered, its surfaces sit
  neutral by mechanical centring (D-21Nov.7).
- After launch detect, firmware holds the battery enable on (Croí and Churro
  AV). An RC keeps it on for about 1 s (≥0.75 s worst case) if firmware lets go;
  after any reset in flight firmware re-asserts it within 50 ms; it releases at
  LANDED plus a delay or at a maximum flight time (D-6.3, D-2Nov.4, D-2Nov.18).
  U101 and Churro U1001 auto-retry.
- Any in-flight flight-MCU reset inhibits further sustainer ignition. Recovery
  resumes only through the [recovery logic](docs/architecture/10-recovery-logic.md).
- CAN is external and linear: two buses of two nodes each, 500 kbit/s Classical
  for Rev A. Bus 1 links Burrito and Fajita (FDCAN1); bus 2 links Burrito and the
  active board (FDCAN2), which Fajita never sees. Both transceivers share one
  standby line and one supply limiter (D-5Nov.3). CAN carries permissions and
  mode, slow state that survives Burrito's worst-case 550 ms restart, health, and
  commands the receiver drops to safe when stale; never a loop at loop rate
  (D-2Nov.9). On bus 2 Burrito sends Safe, Active or Abort with a counter at
  10–20 Hz, and stale means Safe (D-5Nov.2). Connectors are Harwin Gecko
  (D-18Nov.4).
- Foinse owns source entry and protection; Ogma is not a power distributor. On
  the rail the vehicle runs from a ground umbilical at Churro, through
  per-source ideal diodes ahead of the eFuses; pulling it hands each feed to its
  pack. The packs stay in the vehicle and charge through the umbilical: one
  standalone charger per pack voltage, at maintenance rate, temperature-gated
  (D-20Nov.1, D-21Nov.2). Churro has three branches: AV (logic and pyro), PROP
  (Fajita) and ACT (Salsa), the last two from one 6S actuator pack (D-21Nov.1).
  The CATS Vega has its own cell, charged through its own lead (D-18Nov.2,
  D-21Nov.2). Each umbilical pair is damped against hot-plug ringing (D-21Nov.3).
- Battery, CAN, pyro and servo use keyed, locking board connectors. Bare-wire
  terminals live only on detachable development adapters.
- Never attach standalone and Churro batteries at once. USB powers service logic
  only: no charging, no output energy.
- Every extra component, processor, connector or mode needs a named function,
  failure boundary and test ([11 Verification](docs/architecture/11-verification.md)).

## Power path

2S source → Q101 reverse blocking → `ENERGY_TAP` (100 nF + 10 µF, D-2Nov.15),
where the outputs branch off → U101 eFuse (≈6.0 A, auto-retry) →
5 mΩ shunt → TPS2121 battery/USB mux → TPSM63603 4.0 V buck → three TPS7A91
domains (flight, comms, services) at 3.352 V. Flight hold-up: 1000 µF, about
2 ms. Flight VBAT has its own Schottky and 100 µF (D-6.4). Sensors run from
FLIGHT_3V3 through 47 Ω links (D-6.6, D-2Nov.3); the magnetometer through 22 Ω.
The flight-core input enables whenever the buck is up (D-6.5).

The avionics pack is 2S Li-ion in metal-can cylindrical cells, 21700 by default;
no LiPo. It alone covers ≥6 h on the rail plus the flight (D-2Nov.6). Pad-mode
target ≤150 mA, to be measured.

J103 is the FC battery enable: open means off, upstream circuits stay live. It
is not an arm and not physical isolation. It is a Molex Micro-Fit 3.0 header,
single row, two circuits (43650-0215, D-22Nov.18). Churro has separate AV and PROP
enables. Charging is on board, through the umbilical (D-20Nov.1, D-21Nov.2): a BQ25756
per 2S and 6S pack and a BQ25185 for the CATS cell, from a 24 V charge pair,
held off above 45 °C (D-22Nov.5).

## Parts (8 Sep CAD, with decided changes)

| Block | Selection |
| --- | --- |
| MCUs | STM32H563VIT6 flight; STM32H563RIT6 comms (D1; fitted at capture step 7). Pins: the maps in `hardware/croi2/libraries/inputs`, re-allocated for the placement (D-22Nov.25): no off-by-default output on a pin pulled up from reset or driven by the ROM bootloader, no fire or arm net on a bootloader pin, no fire-chain pin beside another or a supply |
| Low-g IMUs | ST LSM6DSV32XTR (D-21Nov.16), TDK ICM-42688-P |
| High-g | ADI ADXL375BCCZ, ±200 g nominal |
| Pressure | Bosch BMP390, TE MS560702BA03-50, separate buses |
| Magnetometer | MEMSIC MMC5983MA on I²C3, 100 Hz, non-essential (D-2Nov.11) |
| Recording | MX66L2G45GMI00, 256 MiB NOR |
| Radio | Wio-LR2021 (Seeed 100058045), vertical SMA |
| GNSS | MAX-M10S-00B, external passive antenna via SMA; 80 km / 4 g / 500 m/s limits |
| Supervision | TPS3808 supervisors, TPS3430 earned-heartbeat watchdog |
| Current | Croí INA228 0x40 (logic path); Churro: PROP INA228 0x41, ACT INA237 0x44, ADS1115 0x48 and 0x49, charger status TCA9535 0x20 (D-22Nov.4, D-22Nov.5) |
| Outputs | Per channel a TPS1H100 high side and a CSD17318 low side (2 recovery + 1 staging); U6001 staging latch with an SN74LVC1G08 AND; no servo outputs (D-19Nov.2) |
| Churro rail power | Four LM74700-Q1-class ideal-diode stages, fuse and TVS (D-2Nov.7); J801 a Mini-Fit Jr. 2 × 4 with electrolytic damping per pair (D-21Nov.3, D-22Nov.6); PROP and ACT each an LM5069-2 stage, 19.4 A minimum limit (D-22Nov.4); chargers (D-22Nov.5) |
| CAN | Two TCAN3413 transceivers, each behind a TXU0304 boundary: bus 1 on FDCAN1 (PD1 / PD0), bus 2 on FDCAN2 (PA10 TX, PB5 RX); one standby line on PD15 and the PD10 CAN limiter for both (D-5Nov.3, D-22Nov.25) |
| Indication | Red/green readiness, comms amber, hardware power LED, magnetic sounder, PUI SMT-1028-T-2-R at 2.83 kHz (D-21Nov.20) |

## Interfaces

| Interface | Contract |
| --- | --- |
| Croí ↔ Foinse | Samtec MPT/MPS-08-01-01-L-RA-SD: 1 battery, 2 GND, 3 AUX 3.3 V, 4 GND, 5 SCL, 6 SDA, 7 fault, 8 `CROI_POWER_HOLD` |
| Standalone 2S | Molex Nano-Fit 1053111102; footprint from Molex drawing SD-105311-100 (capture step 15) |
| Pyro arms J6101 / J6102 | Recovery / staging (D-7.2), each with its own fuse. 2-contact each, to external arm switches. Must not mate each other, Churro J701 (Micro-Fit 430450200, raw PROP) or the Gecko enable loops (D-19Nov.5). Proposed: single-row Micro-Fit 3.0, recovery 2-way, staging 3-way with one cavity empty |
| Outputs J6601 | Micro-Fit 430450600: 1/2/3 high sides, 4/5/6 returns through each channel's low side |
| Servos J6602 | Removed (D-19Nov.2) |
| CAN J501, bus 1 | Harwin Gecko (D-18Nov.4; was JST GH): 1 CAN H, 2 CAN L, 3 reference; no power. To Fajita, whose end has to match |
| CAN bus 2 | Harwin Gecko, same pinout, to the active board; reference set at capture (D-5Nov.3) |
| Umbilical J801 (Churro) | AV and actuator power pairs plus charge contacts (D-21Nov.2); AV 8.4 V at Churro; part, contact count and mechanism with the vehicle owner |
| Inter-MCU | Framed UART, 2 Mbaud |
| Service | USB-C (USB4105-GF-A) on comms, at the av-bay: nothing is flashed on the rail (D-21Nov.4); TC2030 debug pads for both MCUs |

Full contracts: [power](interfaces/power-contract.md), [flight fault](interfaces/flight-fault-contract.md),
[reset and retained state](interfaces/reset-recovery-contract.md),
[Ogma/Foinse/propulsion boundary](interfaces/ogma-foinse-propulsion-boundary.md).
Firmware: [firmware interface](docs/firmware-interface.md).

## 19 November changes (D-19Nov.1–9)

- Vehicle, since 8 November: the grid fins sit below the recovery bay, merged
  with the RCS (two cold-gas solenoids) into one module that one active board
  drives (D-19Nov.6). The 14 October stack above is kept as history.
- Burrito has no servo outputs (D-19Nov.2). The freed pins are test pads: a
  timing strobe on PE10 and a reset memory on PA4 (D-19Nov.3; pins D-22Nov.25).
- No external pyro board (D-19Nov.7). Paired e-matches, if Recovery wants two
  from Burrito, share one channel (D-19Nov.8).
- The sounder beeps continuity and state at arming (D-19Nov.4).
- JST GH leaves the vehicle harness for Gecko (D-19Nov.5); Burrito's J103 is a
  Micro-Fit instead, since no 2-contact Gecko exists (D-22Nov.18). Batteries and
  connectors get particular attention: they are where student vehicles fail.
- One USB-C per programmable board; no firmware over CAN (D-19Nov.9). The ports
  stay at the av-bay (D-21Nov.4).
- Firmware writes the in-flight checkpoint first at launch detect, and PAD
  catches a missed launch (D-19Nov.1).

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
authority; for EuRoC the mandatory CATS Vega is that set (D-18Nov.2).

Target vehicles, as said at the 14 October requirements meeting:

- **EuRoC, October 2027.** Liquid, about 6 m long, 7 in (178 mm; James, 22 Oct;
  Aerostructures AER-07, AER-11). Bottom up (Jay, 20 Nov): engine, tanks and
  COPVs, valve bay (e-reg, burst discs, relief valves, vent), grid-fin and RCS
  module, av-bay, recovery, nose and payload. Harness runs through a downcomer
  in the tanks, with no raceways; pad-touched items sit in the lowest ≈1.8 m
  (AER-18). The 14 October stack is history. Armed on the pad before filling; nobody within 600 m once anything is
  pressurised; the umbilical powers the rocket until it disconnects remotely at
  Go. EuRoC SRD Issue 1.1: ≥6 h on the rail (LV-0320); no LiPo (0300); a CATS
  Vega in every stage (0430); fully redundant recovery electronics with their own
  power, one set COTS (0240, 0250); switches, connectors and batteries touched
  on the pad reachable from the ground, no ladders, opposite the rail
  (0260–0280, 0310, 0540–0550). Drogue at or near apogee, main at or below
  450 m AGL (0350, 0370; D-18Nov.5). Antennas inside the skin need a 360°
  non-carbon RF window at least two calibres long (0780–0820). Active control
  stays dormant until at least 1500 m AGL without flight history (0680). Open:
  where the packs and arm switches go (the av-bay is above the tanks), how far
  the charges sit from Burrito (Seán, 18 Nov: the recovery bay may be well above
  the av-bay; James to confirm), and whether LV-0690 makes roll control
  redundant.
- **IREC: Ériú.** SRAD solid O motor to 30,000 ft; tubes 156.4 mm outside,
  152.4 mm bore. The recovery bay sits above the av-bay; the nose carries the
  canards and Cornstar. The av-bay's contents must pass a Ø111 opening at the
  RADAX lugs, so they fit Ø109 (Ø104 inside the sheath), and the bay is 321 mm
  between lug faces today (Notion, Ériú av-bay requirements, Rev 1.3, measured
  from the CAD). Flies Burrito, Churro and Salsa without Fajita, as the flight
  test of our core before EuRoC (D-20Nov.3); Salsa drives the nose canards
  (D-21Nov.7). IREC 2027 DTEG REV P1 (15 Oct 2026) applies. Cornstar, the
  heated payload in the nose, is independent: its own pack, launch detect,
  switch and logging, and no wires to Ogma. The canard servos and their leads
  keep clear of its hot module.

Every board is 80 mm wide (D-21Nov.6). Burrito is 80 × 160 mm (D-22Nov.21).
Ériú's av-bay must grow to hold the stack: about 400–420 mm between lug faces, or
a two-sided sled. Burrito's mounting holes have GND rings; the sled mounts it on
insulating standoffs or washers (D-22Nov.11).

## Fault and software policy

- Watchdog feeding requires progress of acquisition, estimation and phase policy.
  Comms, bulk recording and the magnetometer never gate it.
- Bound retries; disable persistent optional faults; never reset flight to
  restore telemetry. A sensor given up on has its bus pins parked.
- Record reset cause and supply evidence before initialisation clears them.
- Recording is append-only, checked and replayable; full rate from launch detect
  with a RAM pre-trigger (D-6.9). Telemetry is never the only record.
- The pad datum is tracked on the pad and frozen at launch detect; a reset never
  creates one. Nothing deploys before the barometric altitude has passed 100 m
  above it, or inertial evidence shows flight if both barometers are invalid
  (D-2Nov.13). Pad telemetry at 1 Hz shows arm, continuity, latch and power
  state. A ground-test mode serves EuRoC's recovery ground test (D-2Nov.10); it
  lives in RAM and any reset ends it (D-2Nov.16). The in-flight checkpoint is
  written first at launch detect, and PAD catches a missed launch (D-19Nov.1).
- Initial budgets: 128 MHz, 1 kHz essential loop, 200 Hz estimation/policy,
  30% timing reserve. These are allocations, not measurements.

## State

| Item | State |
| --- | --- |
| Croí CAD | Schematic: 44 pages, 566 parts, captured 21–22 Nov (steps 0–19; 200 passives in 0402 since step 16; the LoRa ESD part and pyro RF bypass capacitors since step 17, D-22Nov.20; the MCU pins re-allocated for the placement at step 19, D-22Nov.25); ERC clean with 3 recorded exclusions; 369 checks incl. the capture assertions and the reset-state pin rules (A24–A26). PCB: built and placed by script at 80 × 160 mm, the placement frozen as data since D-22Nov.30 (S3, D-21Nov.21, D-22Nov.21; rebuilt in stage B with steps 14–17, the function names and the axes mark): every part placed, J101 on the left edge, nothing routed (the netlist has about 1,376 connections; DRC's report stops at 499), DRC 0 errors and schematic parity clean; six layers on JLC06161H-3313, plan P1, 1.6 mm ordered (1.54 mm by JLC's figure), named, without paid impedance control (D-22Nov.29, D-22Nov.2; four layers until stage C step 1), the routing brief's rules (D-22Nov.3), every part on top (D-21Nov.27), eight plated M3 holes with GND rings on insulated mounts (D-22Nov.11), J102's end aft (D-21Nov.24), both SMAs forward (D-21Nov.25), 47 test points (D-22Nov.9; the 18 rail loops surface-mount, D-22Nov.24), the back silkscreen (D-22Nov.12). Built in stage B: 0402 passives and J101's footprint (D-22Nov.13), J103 as a Micro-Fit (D-22Nov.18), function names, LED meanings, the board axes and the S/N box on the top silk (D-22Nov.19, D-22Nov.23). J102 keeps its screw-down part, bought from Mouser (D-22Nov.22). Not yet built: L3 as ground with power islands (D-22Nov.15). Stage B2 settled the placement before any copper ([brief](docs/briefs/burrito-stage-b2-brief.md)): MCU pins swapped (D-22Nov.25), test points beside their routes, the sweep's distance rules placed first; the quick meter leaves 108 of 328 signal nets open. At [Stop 1b](docs/briefs/burrito-stop1b.md) Seán kept 160 mm, kept `FIRE_LOGIC` at 0.5 mm with its escape from U201 scripted in stage C (D-22Nov.26), and had the pyro channels stamped in stage C instead of a refinement pass (D-22Nov.27); C6601–C6606 now sit at J6601's courtyard edge, 0.9–3.9 mm from their pins (D-22Nov.28). After the [layer test](docs/briefs/burrito-layer-test.md), Burrito is six layers on JLC06161H-3313, plan P1 (D-22Nov.29). Since 23 Nov: L5 is one FLIGHT_3V3 plane with GND under the armed-rail corridor and the other four 3V3 rails as tracks (D-23Nov.2); signal vias are 0.5 mm (D-23Nov.4); U4606 is turned 90° to face its SMA with D4601 on the new line (D-23Nov.3), and 19 of the MCUs' 22 capacitor slots are at their pins, with test points and pull resistors moved up to 8 mm to make room (D-23Nov.1, D-23Nov.5; three slots open). Stage C's steps 0 to 2 are built; the [review](docs/briefs/burrito-stage-cd-review.md) orders the rest |
| Foinse CAD | 12 pages, 113 parts, unrouted, 60 × 80 mm; ERC clean; DRC 24 + unrouted |
| Known CAD gaps | Churro's Nano-Fit footprint (Burrito's J101 drawn in capture step 15); ten of Burrito's 3D models are drawn stand-ins and two are borrowed, several heights unverified ([list](hardware/croi2/libraries/3d/GENERATED.md)); Burrito's routing (S4, S5); Churro's capture |
| Firmware | [Firmware interface](docs/firmware-interface.md); build-pipeline brief v0.1.0 (Anav); no target code yet |
| Tests | Host checkpoint model only (12 tests); no hardware tests. Gates and campaigns in [11 Verification](docs/architecture/11-verification.md) |

## Next

1. Burrito: schematic captured (steps 0–16); what's still open (the MCU buy) is in [schematic-status.md](hardware/croi2/schematic-status.md). Next: the scripted
   layout (D-21Nov.21), then the JLC assembly files. Burrito limits each CAN
   reference (B-39, D-21Nov.11).
2. Churro: the power review was accepted on 22 Nov (D-22Nov.4–7). Next: its
   scripted capture and layout, working to 80 × 120 mm (D-22Nov.7).
3. Anav: the recovery logic (D-6.11) and his pyro-channel circuit against
   D-2Nov.1.
4. Jay and James: Ériú av-bay Rev 2 length (end-to-end mating, or an adapter at
   J102 on a two-sided sled; J102 stays where it sits, aft, D-21Nov.24); the sled
   and its insulating standoffs or washers for Burrito's eight M3 holes (D-22Nov.11); the e-reg's
   readings and PTs (D-21Nov.10); actuator and valve specs, and each
   valve's unpowered state; where the panel, packs, switches, Churro and the CATS Vega
   sit; the run length; how far the charges are from Burrito (the external pyro
   board row); the RF window. LV-0690: Jay reads it as covering only
   independently controlled bodies; the SRD's Section 7 text points the other
   way, so the officials' answer still decides one active board or two.
5. The active board, with the build group from 19 November: its phase table
   and its requirements from Radion and Sim Systems (controls' plan, as
   reported: LQR on the RCS, two solenoids, four fin servos and a lock servo),
   the IREC canards included (D-21Nov.7); its loads, which set the ACT branch
   rating; what the magnetometer has to deliver.
6. Place and route by script (D-21Nov.21), with review stops at placement, the
   critical nets and the full route; DRC; JLC files from its parts library.
   Footprint, rating and assembly review before order (G1). Burrito first, then
   Churro (D-21Nov.9, D-21Nov.22).
7. First PCBA: functional blocks on inert loads, per
   [11 Verification](docs/architecture/11-verification.md#bench-tests-by-block).

History: [project log](project-log.md) and [archive](docs/archive/README.md).
