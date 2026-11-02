# Schematic capture and placement specification

What to change in the native CAD, block by block. Written 22 September 2026;
amended 6 October with D-6.1–D-6.10, 7 October with D-7.1 (three pyro channels,
three servos) and 2 November with D-2Nov.1–D-2Nov.11 and the acceptance of D1,
D2, D3, D5 and D-7.2, all in [decisions.md](../../decisions.md). D-6.12 (two
processors) needs no capture change.

**Status: proposed baseline. Capture has not been approved; Seán holds it until
after the Tuesday 3 November review.** [Readiness list](#what-ready-for-capture-means).

## Who does what

1. Seán approves this specification.
2. Codex captures the schematics and places components.
3. Seán routes.

Anav owns firmware. Approval to capture is not approval to fabricate, to use the
energetic outputs, or to fly.

## Starting point

- Start from native `hardware/croi2/` and `hardware/foinse2/` at review-branch
  baseline **9a8c2a2**, plus any manual changes reviewed since.
- The 22 September audit exported both native schematics and matched the stored
  netlists on pins, nets, references, values and footprints: 2179 / 306
  connected pins and 643 / 113 physical components (Croí / Foinse). That proves
  connectivity, not electrical correctness.
- Preserve UUIDs, DNP states, board-local libraries and mechanical work.

## Rules for applying the changes

- Keep every baseline connection and value unless a row below changes it.
- If something conflicts, settle it against the native CAD and this document
  before capture. Don't mix the old two-rail sketch with the three-domain design.
- The two proposed pin maps ([flight](proposed-flight-pinout.csv),
  [comms](proposed-comms-pinout.csv)) use the exact native net names, including
  ADC divider outputs and both sides of each partial-power boundary.
- `NC` means leave that pad unconnected. Never create a shared net called `NC`.
- The functional changes are flight PE8 (service-power enable), the comms UART
  port and package, and the 6 October, 7 October and 2 November decisions. Every
  other rename keeps native connectivity. The
  frozen hardware input CSVs use functional shorthand and are not the authority
  for net names.
- Every signal a change leaves unused gets an explicit NC or a defined input
  level. Removing a function must not leave a powered translator input floating.
- The [justification index](justifications/README.md) holds alternatives,
  sources, calculations and consequences. Older dated recommendations add no
  requirements.

## Burrito changes

### Processors

| Block | Instruction | Why |
| --- | --- | --- |
| Flight U201 | Keep STM32H563VIT6 LQFP100. Use the [100-pad map](proposed-flight-pinout.csv), amended by the next row | The CSV still holds 22 September nets so the proposal checker keeps passing; its PD10 `SERVICE_POWER_EN` row is superseded by the next row |
| Flight pad changes | PE5 pad 4 → `FC_POWER_HOLD` with 100 kΩ pull-down. PE7 pad 38 → `PYRO1_FIRE`, PE9 pad 40 → `PYRO2_FIRE`, each driving its TPS1H100 IN directly. PE12 pad 43 → `PYRO3_FIRE`, through the staging latch AND gate (D-7.2). Low-side selects: PA9 pad 68 → `PYRO1_LS_SELECT`, PA10 pad 69 → `PYRO2_LS_SELECT`, PD14 pad 61 → `PYRO3_LS_SELECT` (D-2Nov.1). Magnetometer I²C3: PA8 pad 67 → `MAG_SCL`, PC9 pad 66 → `MAG_SDA`, AF4 (D-2Nov.11). PE14 pad 45 → `STAGE_INHIBIT_LATCHED` through a 1 kΩ series resistor; PE15 pad 46 → staging arm sense (`STAGE_ARM_INVALID` via R6108). PD15 pad 62 stays `NEW_FLIGHT_CLEAR_REQUEST`; PC8 pad 65 stays recovery arm sense. PE8 pad 39 → `SERVICE_POWER_EN`. PD10 pad 57 stays `SERVO3_PWM` (LPTIM2_CH2, AF3), as in the CAD. PE6 pad 5 → `MAG_INT` (optional data-ready input). PE10 pad 41, PE13 pad 44 → NC | D-6.2, D-6.3, D-6.6, D-7.1, D-7.2, D-2Nov.1, D-2Nov.11. The low sides sit on ports A and D, away from the port-E fire pins, so one bad port write can't close both switches of a channel. The 1 kΩ stops a wrongly configured PE14 fighting the latch output |
| Comms U401 | STM32H563RIT6 LQFP64. Use the [64-pad map](proposed-comms-pinout.csv) | [Package choice](01-mcus.md). Supply, VCAP, HSE and SWD follow this package; don't copy 100-pin numbering |
| Inter-MCU link | Comms PC10 TX → `CC_COMMS_TO_FLIGHT` → U4301.1. PC11 RX → `CC_FLIGHT_TO_COMMS` → U4301.8. USART3, AF7 | Flight-side `FLIGHT_TO_COMMS` / `COMMS_TO_FLIGHT` stay on the other side of U4301 |

Also on the processors:

- Comms PA1 / PA2 / PB5 keep `CC_USB_CONFIG_OK` / `CC_BAT_VALID` /
  `CC_BRANCH_FAULT_N` and their boundary circuits.
- Comms VDDA/VREF+ pad 13 takes `COMMS_VDDA` through the existing R401 link.
  Flight VDDA/VREF+ keep `FLIGHT_VDDA`.
- Keep each processor's HSE and SWD nets separate.
- Comms LQFP64 VCAP pads 30 and 62 each need 2.2 µF close by. VDDUSB has no
  external pad in this package.
- Keep the quiet-LSE restriction on flight PC13.

### Power

| Block | Instruction | Why |
| --- | --- | --- |
| Regulators | Keep U1701 / U1801 / U1901 TPS7A9101DSKR and their domains | [Three-domain fault case](justifications/power-domains.md) |
| LDO dividers | R1701 / R1801 / R1901 → 31.9 kΩ 0.1%. Keep the 10 kΩ 0.1% lower legs | 3.352 V nominal on all three; calculated corners 3.310–3.394 V |
| Comms input limiter | U1501 stays before U1801 on `COMMS_BRANCH_EN`. R1504 → 66.5 kΩ 1% | 351–449 mA calculated limit |
| Service input limiter | U1601 stays before U1901. R1604 → 49.9 kΩ 1% | 470–588 mA calculated limit |
| Service restart | Move U1601 EN (pin 3) and the top of R1602 100 kΩ from `FLIGHT_3V3` to `SERVICE_POWER_EN`, driven by PE8 | Low at reset and power-off; a bounded, sequenced restart separate from comms |
| Hold-up capacitor | C1403 → Nichicon PCW0J102MCO1GS, 1000 µF / 6.3 V | Flight hold-up only. Check footprint and body against the maker's drawing |
| Core enable | Remove U1203. Drive U1401 EN/UVLO from a divider on `4V_PRE` (R1204 becomes the lower leg), enabling above ≈3.6 V. Values from the LM73100 threshold | D-6.5 |
| USB limiter | Remove U4402 (TS5A3167). U4401 ILIM fixed by R4403 60.4 kΩ: 387–491 mA from attach. Keep U1201 / U1202 / U1204 | D-6.5 |
| U101 fault mode | MODE pad 11 to GND: auto-retry | D-6.3 |
| Enable hold | `FC_POWER_HOLD` → 330 Ω → 470 µF ≥6.3 V to GND → BAT54-class diode → `BAT_SHDN_N`. A second diode from the same node → J102.8 (`CROI_POWER_HOLD`). The RC must keep SHDN above 2 V (the TPS26630's guaranteed-on level) for ≥1 s after the GPIO lets go, loaded by both 22.1 kΩ pull-downs (Croí R1006, Churro R1006) and both diode drops: these values give ≈1.2 s at Churro's `AV_SHDN_N` with −20% capacitance, ≈1.7 s at Croí's, and ≈0.5 s to charge after launch detect | D-6.3, D-2Nov.4. Covers Burrito's worst-case restart (550 ms) with margin |
| Flight VBAT | U201 pad 6 from `FLIGHT_3V3` through a BAT54-class Schottky. Add 100 µF ≥6.3 V X5R to GND beside the existing 100 nF | D-6.4 |

### Sensors, memory and CAN

| Block | Instruction | Why |
| --- | --- | --- |
| Sensors | Remove U3101–U3501 (TPS2553), U3102 / U3202 / U3302 (TXU0304), U3103 / U3203 / U3303 (TXU0101), U3402 / U3502 (TMUX1511), the R3x02 enable pull-downs and the R3x03 rail bleeders. Feed each sensor from `FLIGHT_3V3` through its link R3101–R3501, now **47 Ω 1% 0603**, with the sensor's decoupling on the sensor side. Join the MCU-side and sensor-side signal nets; keep the 22 Ω damping; move pull-ups to `FLIGHT_3V3` | D-6.6, D-2Nov.3. A shorted sensor draws ≤≈71 mA instead of pulling down the flight rail |
| Magnetometer | New U3701 MEMSIC MMC5983MA, LGA-16 3 × 3 × 1 mm. VDD (2) and CAP (10, tied to VDD inside) on new `MAG_3V3`, fed from `FLIGHT_3V3` through R3701 **22 Ω** 0603; C3701 10 µF low-ESR X5R at CAP, C3702 1 µF and C3703 100 nF at VDD. VDDIO (13) on `MAG_3V3` with C3704 100 nF. SPI_CS (4) tied to VDDIO for I²C; SDO (5) and NC pads unconnected. SCL (1) / SDA (16) → R3704 / R3705 22 Ω → PA8 / PC9; R3702 / R3703 2.7 kΩ pull-ups to `FLIGHT_3V3`. INT (15) → PE6. Address 0x30. Build the footprint from MEMSIC's drawing | D-2Nov.11. 22 Ω, not 47 Ω: VDD's minimum is 2.8 V and measurement pulses come through the link. Placement: [layout guide C09a](../pcb-layout-guide.md#c09a-magnetometer) |
| NOR, CAN, AUX | Keep the devices, buses, local limiters and partial-power boundaries. The service net keeps the name `3V3_OPTIONAL` | [Sensors](07-sensors-logging.md), [CAN](08-foinse-can.md) |

### Output energy and pyro outputs

| Block | Instruction | Why |
| --- | --- | --- |
| Energy tap | New node `ENERGY_TAP` at `BAT_EFUSE_IN`, after Q101 and before U101. When U101 shuts down, Q101 turns off but its body diode still feeds the tap and still blocks a reversed pack. Outputs and servos no longer pass R7101 | D-6.1, D-2Nov.5 |
| Pyro feed and arm | `ENERGY_TAP` → F6101 (≈4 A fast-acting; I²t checked against a 2 A firing pulse) → J6101 → `RECOVERY_ARMED_VBAT`. F6101 feeds recovery only. J6101 is a 2-contact connector to the external arm switch. It must not mate Churro J701 (Micro-Fit 430450200) or the GH enable loops; part chosen at capture. Keep R6101 / R6102 and U6103 arm sense to PC8 | D-6.1, D-2Nov.2 |
| Staging feed and arm | `ENERGY_TAP` → new F6102 (rated like F6101) → J6102 → `STAGING_ARMED_VBAT` → R6510. J6102 is a 2-contact connector to a second external arm switch; it must not mate J6101, J701 or the GH loops. Keep R6103 / R6104 → U6103 INB−; `STAGE_ARM_INVALID` (OUTB, R6106 pull-up) → R6108 → PE15, read inverted in firmware | D-7.2, D-2Nov.2, D-2Nov.11 |
| Recovery channels 1 and 2 | Keep U6304 / U6404 TPS1H100, IN from `PYROn_FIRE` with its 100 kΩ pull-down. Fit R6314 / R6414 = 1.24 kΩ 1% (≈2.0 A). Remove U6301 / U6401 with R6311–R6313 / R6411–R6413, the gates U6302 / U6303 / U6402 / U6403, and U6002–U6005, U6101, U6102, U6104. **Keep the low sides:** Q6301 / Q6401 with R6304 / R6404 (100 Ω) and R6305 / R6405 (100 kΩ gate pull-down); join `PYROn_LS_SELECT` to `PYROn_LS_ENABLE` where the select gate was; keep R6302 / R6402 (100 kΩ); selects on PA9 / PA10. `OUTPUT1_LOW` / `OUTPUT2_LOW` (J6601.4 / .5) stay on the drains. Keep the 06c current diagnostics and the 06e / 06f continuity paths. Size R6911 / R6912 (test current from `3V3_OPTIONAL`) so the current with the low side closed sits well below the igniter's no-fire current, and R6913 / R6914 (return) so a shorted high side with the low side open stays below it too; same for channel 2 | D-6.2, D-2Nov.1 |
| Staging channel 3 | Keep U6504 TPS1H100; fit R6514 = 1.24 kΩ 1% (≈2.0 A). U6502 becomes an **SN74LVC1G08** (SOT-23-5; new footprint), a true 2-input AND: `PYRO3_FIRE` (PE12, keep R6501 pull-down) and `STAGE_ELIGIBLE` → `PYRO3_HS_ENABLE` (keep R6503 pull-down) → U6504 IN. Don't reuse the CAD's SN74LVC1G97 symbol: it ties IN1 to GND, which gives A AND NOT B and would fire whenever the latch is set and the request line sits at its pulled-down default. Remove U6501 with R6511–R6513, and U6503. **Keep the low side:** Q6501 with R6504 / R6505; join `PYRO3_LS_SELECT` to `PYRO3_LS_ENABLE`; keep R6502; select on PD14. `OUTPUT3_LOW` (J6601.6) stays on Q6501's drain; J6601.3 = `OUTPUT3_HIGH`. R6510 DNP until the igniter values close, like R6310 / R6410. Keep the channel-3 current and continuity paths (R6931–R6937) | D-7.1, D-7.2, D-2Nov.1 |
| Staging reset latch | Fit U6001 SN74LVC1G74. CLR̄ = `FLIGHT_NRST`; CLK = `NEW_FLIGHT_CLEAR_REQUEST` (PD15, R6001 pull-down); D = `STAGE_ARM_INVALID` instead of the removed U6002 output; Q = `STAGE_ELIGIBLE` → U6502; Q̄ = `STAGE_INHIBIT_LATCHED` → 1 kΩ → PE14. Any flight reset or power-up leaves channel 3 inhibited until PD15 clocks the latch while staging is disarmed | D-7.2; [FF-03](../../interfaces/flight-fault-contract.md) |

### Servos

| Block | Instruction | Why |
| --- | --- | --- |
| Local PWM | Keep all three servos as drawn: PC6 / PC7 on TIM3, PD10 on LPTIM2_CH2 (its own period). Keep R6606 / R6607, U6804 A3 → B3Y and J6602.7 / .8 / .9. Contact 10 unwired; keep the existing fourth-channel terminations | D-7.1 |
| Servo power | Keep U6802, R6802 1.24 kΩ 1%, U6803 and U6804. `ENERGY_TAP` → F6801 (≈4 A) → `SERVO_ARMED_VBAT`; fit R6804. Add ≥220 µF ≥16 V polymer on `SERVO_VBAT` at J6602. Not behind the pyro arm | D-6.1, D-6.7; [raw-2S interface](justifications/interfaces-and-installation.md#three-local-pwm-interfaces-no-speculative-remote-node). Three servos share the 2.0 A limit |

### Service, radio and source

| Block | Instruction | Why |
| --- | --- | --- |
| Service, status, RF | Keep lamps, sounder, debug, USB, MAX-M10S and Wio-LR2021. No extra display, RTC, flash or remote actuator node | [Service](05-service-status-time.md), [RF](06-gnss-radio.md) |
| Source population | Standalone J101 or Churro J102. Never both in the flight assembly | [Variants](justifications/interfaces-and-installation.md#source-variants-and-harness-construction) |
| J101 footprint | Replace the empty reservation from the exact Molex 1053111102 drawing | Project-local footprint. No guessed pads, no 105309 substitute |

## Churro changes

Keep: autonomous source protection, threshold networks, source controls, the
Samtec pinout (pin 8 is now `CROI_POWER_HOLD`), TCA4307, INA228, ADS1115 and the
voltage-input TMUX1511. Don't add an MCU, charger, BMS, CAN endpoint or 24 V
converter, and don't charge anything through the umbilical. The
[monitoring justification](justifications/churro-monitoring.md) is the
connection authority for the probe and reference additions below; the umbilical
rows come from D-2Nov.7.

| Reference | Part and connection |
| --- | --- |
| U6201 | REF3325AIDBZR, SOT-23-3; `ADC_3V3` → 2.5 V NTC bias |
| C6201 / C6202 | 1 µF each, 16 V X7R 0603, at the reference IN / OUT |
| U6202 | ADG7421FBCPZ-RL7, LFCSP-10 CP-10-16; ten-pin mapping in the justification |
| C6203 | 100 nF 16 V X7R 0603, `ADC_3V3` to GND at U6202 |
| R6211 / R6212 | 2.2 kΩ 0.1% 1206, each J601 probe signal to its protected switch S input |
| R6201 / TP6201 | 10 kΩ 0603 pull-up on FF to `ADC_3V3`; local fault test point only |
| R6202 | 10 kΩ 0603 `ADC_3V3`-to-GND bleeder. Limits floating-rail retention; costs ≈0.34 mA while powered |
| D6201 / D6202 | SMF33CA SOD-123FL, probe connector signals to GND, before the series resistors |
| R6003 / R6004 | Keep 10 kΩ 0.1%. Bias tops move to `NTC_REF_2V5`; bottoms to the protected D1 / D2 nodes |
| R6005 / R6006 | Keep 1 kΩ. Input ends move to the D-side bias nodes; output ends stay on AIN0 / AIN1 |
| C6002 / C6003 | 10 nF → 1 µF 16 V X7R 0603; keep the ADC-input-to-GND connection |
| J101 | Same Nano-Fit footprint fix as Burrito |
| U1001 | MODE pad 11 to GND: auto-retry (D-6.3). U2001 unchanged until the propulsion owner decides |
| J301.8 / AV hold | J301 pin 8 (`CROI_POWER_HOLD`) → BAT54-class diode → `AV_SHDN_N` (D-6.3). Keep R1006 at 22.1 kΩ: Burrito's hold RC is sized against it (D-2Nov.4). PROP enable is not held |
| Umbilical entry (D-2Nov.7) | New 4-way umbilical connector J801: AV+, AV−, PROP+, PROP−; part chosen with the vehicle owner. At the connector, a fuse and a TVS per pair (SMBJ12A AV and SMBJ28A PROP to start, as at the packs). Four ideal-diode stages, LM74700-Q1 class, each with its own N-FET: AV pack (`AV_PACK`) and AV umbilical into a new `AV_SOURCE`; PROP pack (`PROP_PACK`) and PROP umbilical into a new `PROP_SOURCE`. `AV_SOURCE` / `PROP_SOURCE` take over from `AV_PACK` / `PROP_PACK` at Q1001 / Q2001 sources, U1001 / U2001 IN_SYS, the UV / OV dividers R1001 / R1003 and R2001 / R2003, and the enable-bias diodes D1002 / D2002, so the umbilical alone can enable and protection works the same on either source. Pack TVS D1001 / D2001 stay at the pack connectors |
| Pack voltage readout (D-2Nov.7) | Move R6101's top from `VBAT_CROI` to `AV_PACK`, the pack side of its ideal diode, so the ADS1115 reads the pack while the umbilical carries the load. Burrito's INA228 reads the bus; the difference names the source. R6111 (PROP) stays on `PROP_RAW` unless the propulsion owner wants the same |
| External probes | Vishay NTCLE305E4103SB ×2. J601: AV / GND / PROP / GND. Dedicated paired leads, ≤0.5 m |
| Pack service assembly | 0287005.PXCN fuse in an FHAC0001ZXJ holder for each source. Short protected 20 AWG paired harness, properly joined to the holder's 16 AWG leads |

Notes:

- The 6200 references are unused in the inspected native Churro netlist.
- Build new IC symbols and footprints from the makers' drawings. Record where
  each came from. Check pin one, underside and thermal-pad needs, and
  dimensional tolerances.
- The ADC bleeder doesn't guarantee an off-rail voltage under every cable
  fault. Measure rail and ADC transients and leakage before qualification.
- Distribution ceilings: AV 3 A and PROP 2 A continuous, subject to thermal and
  harness qualification.
- Source fuses are assembly parts, not PCB locations.
- Keep both AV protection stages for standalone compatibility. No claim is made
  about which trips first.

## Operating assumptions that shape capture

These are proposals for acceptance. The team hasn't agreed them and no hardware
or firmware has shown them.

| Area | Proposal |
| --- | --- |
| Logic power | 200 / 300 / 200 mA for flight / comms / services; all three at 3.352 V nominal |
| Source endurance | Workhorse: 2S Li-ion, 21700 by default; for EuRoC the pack alone covers ≥6 h on the rail plus the flight (D-2Nov.6); otherwise from measured first-PCBA loads and the vehicle timeline (D-6.8). Kármán overlay keeps 2S 8 Ah, ≥30 Wh, 8 h + 4 h |
| USB only | Flight core and comms boot at reduced clock, services off; ≤387 mA from attach (D-6.5); restricted loads for download |
| Boot and restart | Essential flight work starts on its own. Services are sequenced with PE8; one bounded service restart. Nothing waits for a NOR scan, GNSS or CAN |
| Recording | 15 data pages + footer per 4 KiB sector. Full rate from launch detect with a RAM pre-trigger; erase-ahead only before launch detect (D-6.9). Magnetometer at 100 Hz adds ≈1.6 kB/s (D-2Nov.11). [Format](justifications/recording-and-service.md) |
| CAN | 500 kbit/s Classical for commissioning. Moving to 500 kbit/s / 2 Mbit/s FD needs the other node's owner to agree. Permissions, mode, slow state, health and stale-safe commands only (D-2Nov.9) |
| Pad and rail | The umbilical carries the pad load; the AV pack alone covers ≥6 h on the rail plus the flight (D-2Nov.6, D-2Nov.7). Pad-mode target ≤150 mA from the pack, to be measured. 1 Hz pad telemetry (D-2Nov.10) |
| Monitoring | I2C4 at 100 kHz; addresses 0x40 / 0x41 / 0x48; probe curve, reference and diagnostic windows specified |
| RF | Passive GNSS antenna; a same-variant Wio as the reference peer. Don't assume valid GNSS outside its envelope |
| Observability | Status reports only connected, fresh evidence. No made-up power-good, branch identity or physical-arm state |

## What "ready for capture" means

Processor, power, sensor, service, monitoring and comms blocks each have a
baseline and a change list. Building exact libraries, checking decoupling and
fixing ERC is **Codex capture work**, not more research for Seán.

The output block has a decided topology (D-6.2 with D-2Nov.1, D-7.1, D-7.2) and
energy feed (D-6.1, D-2Nov.2, D-2Nov.5). Nothing here grants authority to fire.
See the [output chapter](03-energetic-outputs.md).

**Capture can start when:**

1. Tuesday's review (3 November) closes, and any change to a Decided row is
   recorded in [decisions.md](../../decisions.md).
2. Seán lifts the capture hold (an Open row).
3. The new parts have checked library entries: MMC5983MA (LGA-16), SN74LVC1G08
   (SOT-23-5), the LM74700-Q1 class controllers and their FETs, fuses F6101 /
   F6102 / F6801, the hold capacitor, and the Nano-Fit footprint.

**These stay open during capture and don't block it:** igniters (all-fire and
no-fire current), so the continuity and return resistor values; the fuse and
arm-switch parts; the J6101 / J6102 and umbilical connector parts (draw them as
reviewed placeholders); where the packs and arm switches sit in the vehicle
(EuRoC access). Pyro energy links R6310 / R6410 / R6510 stay DNP until the
igniter values close.

Once scope is accepted, Codex delivers:

1. Readable native schematics with these changes: exact local libraries;
   where each part, value and footprint came from; BOM and population variants;
   revised pin maps.
2. Fresh exports and ERC, with every finding fixed or justified one by one. A
   comparison against the baseline showing every intended net, pin and DNP change.
3. A placed, unrouted PCB for each board that keeps the reviewed outlines,
   mounts and service access. Courtyard, height, mating, decoupling, RF and
   analog checks.
4. Placement images and routing notes with net classes for Seán, covering
   current returns, RF, clocks, sensor axes and connector access.
5. Updated current-system, affected contracts and
   [firmware interface](../firmware-interface.md), and a project-log entry.
   Changes that cross into another project are agreed with its owner.

Seán routes. Fabrication needs finished routing and DRC, plus land-pattern and
assembly review. Flight needs physical evidence for source changeover, faults,
acquisition, storage, EMC, thermal, environment, installed antennas and loads,
and any separately approved output system. Don't record those later
measurements as if this specification had observed them.
