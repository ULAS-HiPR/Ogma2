# Ogma 2 current system

Updated 15 October 2026. Decisions live in [decisions.md](decisions.md); this
file states what is true now. Native CAD still holds the 8 September draft.
Capture of the [capture specification](docs/architecture/schematic-capture-spec.md)
waits for Seán's go-ahead. No fabrication, firmware or flight release exists.

## The system

Ogma 2 is HiPR's workhorse flight computer. It owns two boards:

| Board | Name | Job |
| --- | --- | --- |
| Croí2 | Burrito | Flight computer: sensing, estimation, mission state, recording, recovery outputs, servos, CAN; separate comms processor for GNSS, radio and USB |
| Foinse2 | Churro | MCU-less power board: protected 2S avionics and 6S propulsion feeds, propulsion-current, voltage and temperature monitoring |

Fajita, the propulsion controller, is owned by propulsion and governs itself.
Independent vehicle recovery, the groundstation and payloads are external.
Start with the [system tour](docs/architecture/system-tour.md).

Proposed, not decided (D-13.1; Anav hasn't reviewed it): roll control moves to
its own board, Enchilada, a third CAN peer with its own MCU, actuators and fused
Churro supply. Burrito would authorise it and send slow flight state, never
compute roll commands. Enchilada's actuators go to neutral on stop, abort or
stale authorisation. Open items are in [decisions.md](decisions.md).

## Rules that constrain the design

- Two processors, decided (D-6.12): flight and comms. They separate timing from
  communications; they are not redundant. The flight MCU must complete the
  mission with the comms MCU held in reset.
- Only the flight MCU commands recovery and staging outputs. Radio, USB and CAN
  cannot.
- Pyro energy passes an external physical arm switch (J6101; staging J6102). Pyro and servo
  energy leave before the Croí eFuse U101 through their own fuses, so an output
  fault can't pull down logic power (D-6.1).
- Three pyro channels and three servos are a core requirement (D-7.1). Each pyro
  channel is a current-limited TPS1H100 high side (≈2.0 A) with the igniter
  return to ground; one channel fires at a time (D-6.2). Channels 1 and 2 are
  recovery. Channel 3 is staging / air-start, behind its own arm and the
  hardware reset latch (D-7.2, proposed).
- Burrito's servos make bounded, event-triggered moves only, such as unlatching
  a payload at booster apogee; no continuous or closed-loop actuation (D-13.1,
  proposed).
- After launch detect, firmware holds the battery enable on (Croí and Churro AV);
  U101 and Churro U1001 auto-retry (D-6.3).
- Any in-flight flight-MCU reset inhibits further sustainer ignition. Recovery
  resumes only through the [recovery logic](docs/architecture/10-recovery-logic.md).
- CAN is external, linear and two-node (Ogma ↔ Fajita), 500 kbit/s Classical
  for Rev A. D-13.1 proposes Enchilada as a third peer on an unterminated stub,
  with IDs below Burrito's and Fajita's. Foinse owns source entry and
  protection; Ogma is not a power distributor.
- Battery, CAN, pyro and servo use keyed, locking board connectors. Bare-wire
  terminals live only on detachable development adapters.
- Never attach standalone and Churro batteries at once. USB powers service logic
  only: no charging, no output energy.
- Every extra component, processor, connector or mode needs a named function,
  failure boundary and test.

## Power path

2S source → Q101 reverse blocking → U101 eFuse (≈6.0 A, auto-retry) → 5 mΩ shunt
→ TPS2121 battery/USB mux → TPSM63603 4.0 V buck → three TPS7A91 domains
(flight, comms, services) at 3.352 V. Flight hold-up: 1000 µF, about 2 ms.
Flight VBAT has its own Schottky and 100 µF (D-6.4). Sensors run from FLIGHT_3V3
directly (D-6.6). The flight-core input enables whenever the buck is up (D-6.5).

J103 is the FC battery enable: open means off, upstream circuits stay live. It
is not an arm and not physical isolation. Churro has separate AV and PROP
enables. Charging uses external balance chargers.

## Parts (8 Sep CAD, with decided changes)

| Block | Selection |
| --- | --- |
| MCUs | Two, decided (D-6.12). STM32H563VIT6 flight; comms H563VIT6 in CAD, H563RIT6 proposed (D1) |
| Low-g IMUs | ST LSM6DSV16XTR, TDK ICM-42688-P |
| High-g | ADI ADXL375BCCZ, ±200 g nominal |
| Pressure | Bosch BMP390, TE MS560702BA03-50, separate buses |
| Recording | MX66L2G45GMI00, 256 MiB NOR |
| Radio | Wio-LR2021 (Seeed 100058045), vertical SMA |
| GNSS | MAX-M10S-00B, external passive antenna via SMA; 80 km / 4 g / 500 m/s limits |
| Supervision | TPS3808 supervisors, TPS3430 earned-heartbeat watchdog |
| Current | Croí INA228 0x40 (logic path); Foinse propulsion INA228 0x41; ADS1115 0x48 |
| Outputs | TPS1H100 per pyro channel (2 recovery + 1 staging), U6001 staging reset latch; one servo TPS1H100 at ≈2.0 A shared by three servos |
| Indication | Red/green readiness, comms amber, hardware power LED, passive piezo |

## Interfaces

| Interface | Contract |
| --- | --- |
| Croí ↔ Foinse | Samtec MPT/MPS-08-01-01-L-RA-SD: 1 battery, 2 GND, 3 AUX 3.3 V, 4 GND, 5 SCL, 6 SDA, 7 fault, 8 `CROI_POWER_HOLD` |
| Standalone 2S | Molex Nano-Fit 1053111102; footprint still to draw |
| Pyro arms J6101 / J6102 | Recovery / staging (J6102 proposed, D-7.2). 2-contact each, to external arm switches. Must not mate each other, Churro J701 (Micro-Fit 430450200, raw PROP) or the GH enable loops; parts chosen at capture |
| Outputs J6601 | Micro-Fit 430450600: 1/2/3 high sides, 4/5/6 returns |
| Servos J6602 | Micro-Fit 430451000: PWR/PWM/GND on 1/2/3, 4/5/6 and 7/8/9; 10 unwired |
| CAN J501 | JST GH: 1 CAN H, 2 CAN L, 3 reference; no power |
| Inter-MCU | Framed UART, 2 Mbaud |
| Service | USB-C (USB4105-GF-A) on comms; TC2030 debug pads for both MCUs |

Full contracts: [power](interfaces/power-contract.md), [flight fault](interfaces/flight-fault-contract.md),
[reset and retained state](interfaces/reset-recovery-contract.md),
[Ogma/Foinse/propulsion boundary](interfaces/ogma-foinse-propulsion-boundary.md).

## Mission envelope

| Item | Workhorse | Kármán overlay |
| --- | --- | --- |
| Missions | 3–9 km; solid, hybrid, liquid | One sortie to ≥100 km and back |
| Endurance | From measured first-PCBA loads and the vehicle timeline | 8 h powered + 4 h recovery reserve |
| Full-rate recording | Launch detect to LANDED + tail | ≥30 min |
| Service life | Inspected after each flight | 5 years, 25 flights |
| Pressure survival | Ambient to 9 km | Toward 0.01 Pa |

Shared provisional targets: powered −20 to +70 °C; 50 g quasi-static; 200 g
shock target; ≥±2000°/s rotation measurement; closed-bay splash only.
Independent recovery is required on early flights where Ogma has live recovery
authority; no backup device is selected yet.

Target vehicles, as said at the 14 October requirements meeting; requirements
not yet written: EuRoC, October 2027, liquid, about 6 m long and 6 in in
diameter, av-bay below the recovery bay; IREC, solid O motor, 152.4 mm, the same
electronics without propulsion control. Croí's 80 mm width fits both. EuRoC SRD
Issue 1.1 adds at least 6 h on the rail on internal power (RQT-0320), no LiPo
on board (0300), a CATS Vega in every stage (0430), and fully redundant recovery
electronics with their own power, one set COTS (0240, 0250); the CATS Vega can
be that set.

## Fault and software policy

- Watchdog feeding requires progress of acquisition, estimation and phase policy.
  Comms and bulk recording never gate it.
- Bound retries; disable persistent optional faults; never reset flight to
  restore telemetry.
- Record reset cause and supply evidence before initialisation clears them.
- Recording is append-only, checked and replayable; full rate from launch detect
  with a RAM pre-trigger (D-6.9). Telemetry is never the only record.
- Initial budgets: 128 MHz, 1 kHz essential loop, 200 Hz estimation/policy,
  30% timing reserve. These are allocations, not measurements.

## State

| Item | State |
| --- | --- |
| Croí CAD | 44 pages, 643 parts, unrouted, 80 × 230 mm working canvas; ERC 4 errors / 6 warnings; DRC 61 + unrouted |
| Foinse CAD | 12 pages, 113 parts, unrouted, 60 × 80 mm; ERC clean; DRC 24 + unrouted |
| Known CAD gaps | Nano-Fit footprints on both boards; Croí USB footprint mismatch; output energy feed (decided, not captured) |
| Firmware | Build-pipeline brief v0.1.0 (Anav); no target code yet |
| Tests | Host checkpoint model only (12 tests); no hardware tests |

## Next

1. Saturday 17 Oct: Seán writes the electronics requirements from EuRoC SRD
   Issue 1.1 and posts them for Jay.
2. Sunday 18 Oct (the 11 Oct meeting didn't run): accept D1–D3, D5, D-6.11 and
   D-7.2; answer the open rows in decisions.md; review Anav's pyro-channel
   circuit against D-6.1 and D-6.2.
3. Enchilada: Anav reviews D-13.1 (first reaction against, 14 Oct). EuRoC's
   closed-loop actuators are RCS with four solenoids and grid fins (said
   14 Oct); Sim Systems writes roll control's requirements. If decided, Churro
   needs a new output before Foinse capture.
4. Capture the specification; independent human review page by page.
5. Place, then Seán routes. Footprint, rating and assembly review before order.
6. First PCBA: functional blocks on inert loads, including the bench tests in
   the [output chapter](docs/architecture/03-energetic-outputs.md#bench-tests-inert-loads-only).

History: [project log](project-log.md) and [archive](docs/archive/README.md).
