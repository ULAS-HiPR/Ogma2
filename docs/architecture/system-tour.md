# System tour

Start here. Ogma2 is HiPR's workhorse flight computer: two boards we own,
**Burrito** (Croí2) and **Churro** (Foinse2), talking to **Fajita**, the
engine controller, ours too but its own project (D-20Nov.2). Ogma2 exists as
a capture specification and two unrouted KiCad drafts; nothing is built or
flown. What's settled is in [decisions](../../decisions.md).

## The vehicle

```mermaid
flowchart TB
  AV["2S Li-ion avionics pack"] --> C["Churro / Foinse2
battery protection + monitoring
no MCU"]
  PROP["6S propulsion pack"] --> C
  UM["Ground umbilical
on the rail, pulled at Go"] --> C
  C -->|"protected 2S · Samtec"| B["Burrito / Croí2
flight computer"]
  C -->|"protected 6S · Micro-Fit"| F["Fajita
engine control, redlines, abort"]
  B <-->|"CAN bus 1 · 500 kbit/s"| F
  B -.->|"AUX 3.3 V + I²C
monitoring only"| C
  B <-->|"sub-GHz radio"| G["Ground station"]
  A["External GNSS antenna"] --> B
  U["USB-C laptop"] <-->|"service and logs"| B
  B --> O["3 pyro outputs: 2 recovery, 1 staging
behind physical arm switches"]
  I["CATS Vega: independent COTS recovery
own cell, switch and e-matches"]
  N["Active board: RCS, grid fins
ACT feed via its arm key, own IMU and magnetometer"]
  B <-->|"CAN bus 2 · Safe / Active / Abort"| N
```

The dashed AUX line powers and reads Churro's monitors; it never controls
Churro's protection. The two packs keep separate positives and share ground. On
the rail the umbilical feeds them through per-source ideal diodes, and a charger
per pack tops each one up (D-21Nov.2); pulling it hands each feed to its pack
(D-2Nov.7).
Standalone, Burrito takes its own 2S pack on J101 instead of Churro: one or the
other, never both. USB is service power only. The active board follows the
D-2Nov.8 rules on its own CAN bus (D-5Nov.3), powered through Churro's ACT
branch (D-21Nov.1); it
is designed with the build group from 19 November. The CATS Vega is the COTS
recovery set (D-18Nov.2).

## The boards

| Board | Job | State |
| --- | --- | --- |
| **Burrito / Croí2** | Sensing, estimation, flight state, recording, three pyro outputs, a magnetometer, CAN; a comms processor for GNSS, radio and USB | 44 sheets, 643 parts, unrouted, 80 × 230 mm working outline |
| **Churro / Foinse2** | Protected AV, PROP and ACT feeds from the packs or the rail umbilical; charges every pack; current, voltage and temperature (D-21Nov.1, D-21Nov.2) | 12 sheets, 113 parts, unrouted, 60 × 80 mm |
| **Fajita** | Engine-side sensing, valves, permissives, redlines, abort, its own recording | Ours since 20 November, as its own project (D-20Nov.2); this repository sets only the boundary |

Burrito and Churro sit side by side and mate through the 8-contact Samtec pair
(7.39 mm edge gap, 52.63 mm connector envelope); separate supports take the
load. Those are placement references, not fit or vibration evidence.

## Inside Burrito

```mermaid
flowchart LR
  subgraph FLIGHT["Flight MCU · H563VIT6"]
    direction TB
    FS["Sensors: 2 IMUs, high-g, 2 barometers"]
    FM["Magnetometer, non-essential"]
    FN["256 MiB NOR recorder"]
    FO["3 pyro outputs"]
    FC["CAN to Fajita"]
    FS ~~~ FM ~~~ FN ~~~ FO ~~~ FC
  end
  subgraph COMMS["Comms MCU · H563RIT6"]
    direction TB
    CG["GNSS"]
    CR["LoRa radio"]
    CU["USB service"]
    CG ~~~ CR ~~~ CU
  end
  FLIGHT <-->|"UART 2 Mbaud"| COMMS
```

| Block | Parts | Why |
| --- | --- | --- |
| Flight processor | STM32H563VIT6 | Owns deadlines and every vehicle action; runs with comms held in reset |
| Comms processor | STM32H563RIT6 (VIT6 still in CAD; D1) | Keeps GNSS, radio and USB off the flight schedule (two processors decided, D-6.12) |
| Sensors | LSM6DSV16X + ICM-42688-P (±16 g), ADXL375 (±200 g), BMP390 + MS5607 | Independent buses; 47 Ω supply links so one dead short can't pull down the flight rail |
| Magnetometer | MMC5983MA on its own I²C bus, top end of the board | Heading and roll reference for roll control and the grid fins; never gates flight decisions (D-2Nov.11) |
| Recording | 256 MiB NOR, flight-owned | Evidence survives losing the radio |
| GNSS | MAX-M10S, external passive antenna | Position and time when valid; 80 km / 4 g / 500 m/s limits |
| Radio and service | Wio-LR2021 on SMA; USB-C on comms | Telemetry and ground service; ground link not yet tested |
| Supervision | TPS3808 supervisors, TPS3430 watchdog, internal RTC | Reset evidence; not a redundant computer |

Two processors on one board still share the battery, buck, ground and PCB.
Independent backup recovery is a separate vehicle job.

## Power

```mermaid
flowchart LR
  BAT["2S pack
or umbilical via Churro"] --> Q["Q101"] --> TAP(("ENERGY_TAP"))
  TAP --> E["U101 eFuse
auto-retry"] --> BUCK["4.0 V buck"] --> LDO["3 LDOs
flight · comms · services"]
  TAP --> PF["F6101 recovery fuse"] --> ARM["J6101 arm"] --> PY["Channels 1, 2
high + low side"]
  TAP --> PF3["F6102 staging fuse"] --> ARM3["J6102 arm"] --> PY3["Channel 3
+ reset latch"]
  EN["J103 enable"] -.-> E
  HOLD["Firmware hold
in flight, ≈1 s RC"] -.-> E
```

Logic goes through U101, a 4.0 V buck and three LDOs: flight, comms and
services (NOR, CAN, monitors), so a comms fault can't take the recorder.
Pyro energy leaves before U101 through its own fuses, so a shorted
igniter can't switch the computer off, and a staging fault
can't blow recovery's fuse. In flight, firmware holds the enable on, and an RC
carries it through a restart; the eFuses restart after an over-current instead
of latching off; the flight MCU's backup memory has its own hold-up. Detail in
[02 Power](02-power.md).

Churro protects the raw packs and charges them through the umbilical
(D-21Nov.2); it doesn't regulate: Fajita and Salsa convert at the load
(D-21Nov.1). AV's continuous ceiling is 3 A (D2); PROP and ACT are rated at the
Churro review. On the rail it runs the vehicle from
the umbilical. Its protection works without Burrito; its monitoring doesn't.

## Switching on and arming

| Action | Connector | What it does | What it doesn't |
| --- | --- | --- | --- |
| Switch on | J103 enable loop | Turns on Burrito's battery entry | Disarm anything; isolate the pack |
| Arm recovery | J6101 external switch | Connects energy to pyro channels 1 and 2 | Switch the computer on |
| Arm staging | J6102 external switch | Connects energy to channel 3, which also needs the reset latch set | Arm recovery |
| On the rail | Ground umbilical at Churro | Powers the vehicle; pulling it switches to the packs. It will charge them too (D-20Nov.1) | Charge a pack yet: the chargers are drawn at the Churro power review (D-21Nov.2) |
| In flight | Firmware hold | Keeps the computer on if J103's wire breaks, through a restart | Override a pulled battery |

The arm switch parts aren't chosen yet, and for EuRoC they must be reachable
from the ground with the rocket on the rail. Arm state, continuity and the
staging latch come over USB and 1 Hz pad telemetry; no lamp shows them.
[09 Connectors](09-connectors-arming.md).

## What changes from the 8 September CAD

| Topic | CAD now | At capture |
| --- | --- | --- |
| Comms MCU | H563VIT6, 100 pins | H563RIT6, 64 pins (D1) |
| Rails | Three 3.3 V domains | Three at 3.352 V; services restartable from flight |
| Servos | Three channels | None (D-19Nov.2): the active board runs the loops |
| Outputs | Three channels with one-shots, gates, high and low sides; no energy source | Three channels, each a TPS1H100 high side (≈2.0 A) and a CSD17318 low side on another GPIO port. Recovery fuse and arm; staging fuse, arm and reset latch. No one-shots or permit gates |
| Power path | Outputs after U101; latch-off eFuses; enable open = off | Energy tapped after Q101, before U101; auto-retry; firmware hold with a ≈1 s RC; VBAT hold-up |
| Sensors | Per-sensor switches and isolators | 47 Ω link per sensor; a magnetometer on I²C3 |
| Recording | Earlier format | 15 data pages + footer per sector; full rate from launch detect |
| Battery entries | Both provisions; J101 footprint missing | Fit one; draw the Nano-Fit footprint |
| Churro | Pack feeds only | Umbilical entry with four ideal-diode stages and damping; AV pack readout; an ACT branch beside PROP from one 6S actuator pack; a charger per pack (D-21Nov.1–D-21Nov.3; drawn at the power review) |
| CAN | 500 kbit/s Classical, two nodes | Unchanged for Rev A; what it may carry is now a rule (D-2Nov.9) |

No target firmware exists yet; the 12 host checkpoint tests are a model, not
firmware. A full 256 MiB download over the inter-MCU UART takes at least
22.4 minutes. Pins and sequences for firmware:
[firmware interface](../firmware-interface.md).

## Connectors

Manufacturer photos and renders, not our hardware. Part numbers and cavity
drawings govern the harness.

| Visual | Selected part and use |
| --- | --- |
| ![Molex Nano-Fit 1053111102](https://www.molex.com/content/dam/molex/molex-dot-com/products/manual/en-us/images/105/105311/1053111102_hires.jpg?wid=480&hei=327) | **Nano-Fit, 2.5 mm, two contacts.** Burrito J101 standalone 2S and Churro J101 AV pack. Board **1053111102**, mate **1053071202**. Exact footprint missing on both boards. [Molex](https://www.molex.com/en-us/products/part-detail/1053111102) |
| ![Samtec MPT eight-contact header](https://suddendocs.samtec.com/kineticimages/images/product/parts/mpt/mpt-08-01-01-l-ra-sd.png) ![Samtec MPS eight-contact receptacle](https://suddendocs.samtec.com/kineticimages/images/product/parts/mps/mps-08-01-01-l-ra-sd.png) | **Samtec, 5 mm, eight contacts.** Burrito J102 **MPT-08-01-01-L-RA-SD** ↔ Churro J301 **MPS-08-01-01-L-RA-SD**. Protected 2S, two grounds, returned AUX 3.3 V, I²C, fault and `CROI_POWER_HOLD` on pin 8. [Header](https://www.samtec.com/products/mpt-08-01-01-l-ra-sd) / [receptacle](https://www.samtec.com/products/mps-08-01-01-l-ra-sd) |
| ![JST GH connector family](https://www.jst-mfg.com/product/images/pict/GH.jpg) | **JST GH, 1.25 mm.** Two-contact **BM02B-GHS-TBT(LF)(SN)** / **GHR-02V-S**: Burrito J103 and Churro J103/J104 source enables. Burrito J501 (CAN) leaves the GH family for Harwin Gecko, like bus 2's connector (D-18Nov.4); series chosen at capture. Four-contact **BM04B-GHS-TBT(LF)(SN)** / **GHR-04V-S**: Churro J601 probes. [JST family and exact variants](https://www.jst-mfg.com/product/index.php?series=105) |
| ![Molex Micro-Fit 430451000 ten-contact header](https://www.molex.com/content/dam/molex/molex-dot-com/products/manual/en-us/images/430/43045/0430451000_hires.jpg?wid=480&hei=327) | **Micro-Fit 3.0.** Photo: the ten-contact **430451000**, the family's look (Burrito's J6602 was removed, D-19Nov.2). Exact variants in use: J6601 six-contact **430450600 / 430250600**, three-pyro output harness; Churro J201 four-contact **430450400 / 430250400**, PROP input; J701 two-contact **430450200 / 430250200**, protected PROP output. The pyro arms J6101 / J6102 must not use this same two-contact part. [Ten-contact part](https://www.molex.com/en-us/products/part-detail/430451000) |
| ![GCT USB4105 render](https://cdn.gct.co/products/USB/USB4105/USB4105_0_3D-Render.png) | **GCT USB4105-GF-A**, USB-C USB 2.0 service socket, Burrito J4401. Logic/data service, no pack charging. Current PCB/library footprint mismatch needs reconciliation. [GCT](https://gct.co/connector/usb4105) |
| ![Amphenol 132134 SMA jack](https://s3.us-west-2.amazonaws.com/catsy.582/132134.jpg) | **Amphenol 132134**, vertical through-hole, 50 Ω standard SMA jack. Burrito J4501 GNSS and J4601 radio. Passive GNSS baseline; identical sockets need distinct retained leads. [Amphenol](https://www.amphenolrf.com/en-us/part/132134/662/) |
| ![Tag-Connect TC2030-CTX-NL programming cable](https://www.tag-connect.com/wp-content/uploads/2018/03/tc2030-ctx-nl-programming-cable-380x253.jpg) | **TC2030-NL-FP** six-pad/locating-hole patterns at J2301/J4201, separate MCU debug. No mounted header. Shown **TC2030-CTX-NL** cable connects six spring contacts to Cortex ten-contact debug. [Tag-Connect](https://www.tag-connect.com/product/tc2030-ctx-nl-6-pin-no-legs-cable-with-10-pin-micro-connector-for-cortex-processors) |

Same family isn't a safety key: the three 2-contact GH enable plugs and the two
SMA sockets can be swapped, and the pyro arm connectors must not mate with
Churro's J701 or each other. Churro's umbilical connector J801 is chosen with the
vehicle owner. Harnesses need cavity-numbered drawings, wire-matched contacts
and strain relief. [Connector inventory](09-connectors-arming.md) ·
[assembly notes](justifications/interfaces-and-installation.md).

## What's next

1. Anav reviews the recovery logic and his pyro-channel circuit.
2. Answer the open rows in [decisions.md](../../decisions.md): EuRoC access for
   packs and arm switches, the RF window, LV-0690, the external pyro board, the
   umbilical, igniters, arm-switch parts, the CATS Vega's buyer.
3. The active board, from its requirements, with the build group.
4. Capture the [specification](schematic-capture-spec.md) once Seán lifts the
   hold, with a human reviewer per page; place; Seán routes.
5. First board on inert loads, per [11 Verification](11-verification.md);
   firmware bring-up; radio range test.
