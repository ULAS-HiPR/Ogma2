# Schematic capture and placement specification

What to change in the native CAD, block by block. Written 22 September 2026;
amended 6 October with D-6.1–D-6.10 and 7 October with D-7.1 (three pyro
channels, three servos) in [decisions.md](../../decisions.md). D-6.12 (two
processors) needs no capture change. D-7.2 (staging arm and reset latch) is
proposed.

**Status: proposed baseline. Capture has not been approved.**

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
  port and package, and the 6 and 7 October decisions. Every other rename keeps native connectivity. The
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
| Flight pad changes | PE5 pad 4 → `FC_POWER_HOLD` with 100 kΩ pull-down. PE6 pad 5, PA8 pad 67, PA9 pad 68, PA10 pad 69 → NC (sensor enables gone). PE7 pad 38 → `PYRO1_FIRE`, PE9 pad 40 → `PYRO2_FIRE`, each driving its TPS1H100 IN directly. PE12 pad 43 → `PYRO3_FIRE`, gated by the staging latch (D-7.2). PE8 pad 39 → `SERVICE_POWER_EN`. PD10 pad 57 stays `SERVO3_PWM` (LPTIM2_CH2, AF3), as in the CAD. PE10, PE13, PE14, PE15 → NC (low-side selects and permits gone). PD14 / PD15 keep `STAGE_INHIBIT_LATCHED` / `NEW_FLIGHT_CLEAR_REQUEST`; PC9 keeps staging arm sense | D-6.2, D-6.3, D-6.6, D-7.1 |
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
| Enable hold | `FC_POWER_HOLD` → series resistor → capacitor to GND → BAT54-class diode → `BAT_SHDN_N`. A second diode from the same node → J102.8 (`CROI_POWER_HOLD`). Size the RC so SHDN stays above threshold for ≥300 ms after the GPIO lets go (TPS3430 reset is 170–230 ms) | D-6.3 |
| Flight VBAT | U201 pad 6 from `FLIGHT_3V3` through a BAT54-class Schottky. Add 100 µF ≥6.3 V X5R to GND beside the existing 100 nF | D-6.4 |

### Sensors, memory and CAN

| Block | Instruction | Why |
| --- | --- | --- |
| Sensors | Remove U3101–U3501 (TPS2553), U3102 / U3202 / U3302 (TXU0304), U3103 / U3203 / U3303 (TXU0101), U3402 / U3502 (TMUX1511), the R3x02 enable pull-downs and the R3x03 rail bleeders. Feed each sensor from `FLIGHT_3V3` through its existing 0 Ω link (R3101–R3501). Join the MCU-side and sensor-side signal nets; keep the 22 Ω damping; move pull-ups to `FLIGHT_3V3` | D-6.6 |
| NOR, CAN, AUX | Keep the devices, buses, local limiters and partial-power boundaries. The service net keeps the name `3V3_OPTIONAL` | [Sensors](07-sensors-logging.md), [CAN](08-foinse-can.md) |

### Output energy and pyro outputs

| Block | Instruction | Why |
| --- | --- | --- |
| Energy tap | New node `ENERGY_TAP`. Put it at `BAT_EFUSE_IN` (after Q101, before U101) if the TPS26630 keeps Q101 on through U101 faults and SHDN. Otherwise put it at `VBAT_CROI_INPUT` with reverse-polarity protection on each branch. Outputs and servos no longer pass R7101 | D-6.1 |
| Pyro feed and arm | `ENERGY_TAP` → F6101 (≈4 A fast-acting; I²t checked against a 2 A firing pulse) → J6101 → `RECOVERY_ARMED_VBAT`. J6101 is a 2-contact connector to the external arm switch. It must not mate Churro J701 (Micro-Fit 430450200) or the GH enable loops; part chosen at capture. Keep R6101 / R6102 and U6103 arm sense to PC8 | D-6.1 |
| Staging feed and arm (proposed) | F6101 output → J6102 → `STAGING_ARMED_VBAT` → R6510. J6102 is a 2-contact connector to a second external arm switch; it must not mate J6101, J701 or the GH loops. Keep R6103 / R6104 → U6103 INB−; `STAGE_ARM_INVALID` (OUTB, R6106 pull-up) → R6108 → PC9, read inverted in firmware | D-7.2 |
| Recovery channels 1 and 2 | Keep U6304 / U6404 TPS1H100, IN from `PYROn_FIRE` with its 100 kΩ pull-down. Fit R6314 / R6414 = 1.24 kΩ 1% (≈2.0 A). Remove U6301 / U6401 with R6311–R6313 / R6411–R6413, U6302 / U6303 / U6402 / U6403, Q6301 / Q6401 and their gate parts. Tie `OUTPUT1_LOW` / `OUTPUT2_LOW` (J6601.4 / .5) to GND. Remove U6002–U6005, U6101, U6102, U6104. Keep the 06c current diagnostics and the 06e / 06f continuity paths; set continuity values against the chosen igniter's no-fire current | D-6.2 |
| Staging channel 3 | Keep U6504 TPS1H100; fit R6514 = 1.24 kΩ 1% (≈2.0 A). U6502 becomes a true 2-input AND: `PYRO3_FIRE` (PE12, keep R6501 pull-down) and `STAGE_ELIGIBLE` → `PYRO3_HS_ENABLE` (keep R6503 pull-down) → U6504 IN. Use an SN74LVC1G08, or redraw the SN74LVC1G97 symbol so IN1 is its own pin: the CAD symbol ties IN1 to GND, which only gives A AND NOT B, and that form would fire whenever the latch is set and the request line sits at its pulled-down default. Remove U6501 and R6511–R6513, U6503, Q6501 and its gate parts. Tie `OUTPUT3_LOW` (J6601.6) to GND; J6601.3 = `OUTPUT3_HIGH`. R6510 DNP until the igniter values close, like R6310 / R6410. Keep the channel-3 current and continuity paths | D-7.1, D-7.2 |
| Staging reset latch | Fit U6001 SN74LVC1G74. CLR̄ = `FLIGHT_NRST`; CLK = `NEW_FLIGHT_CLEAR_REQUEST` (PD15, R6001 pull-down); D = `STAGE_ARM_INVALID` instead of the removed U6002 output; Q = `STAGE_ELIGIBLE` → U6502; Q̄ = `STAGE_INHIBIT_LATCHED` → PD14. Any flight reset or power-up leaves channel 3 inhibited until PD15 clocks the latch while staging is disarmed | D-7.2; [FF-03](../../interfaces/flight-fault-contract.md) |

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
converter. The [monitoring justification](justifications/churro-monitoring.md)
is the connection authority for the additions below.

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
| J301.8 / AV hold | J301 pin 8 (`CROI_POWER_HOLD`) → BAT54-class diode → `AV_SHDN_N` (D-6.3). PROP enable is not held |
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
| Source endurance | Workhorse: from measured first-PCBA loads and the vehicle timeline (D-6.8). Kármán overlay keeps 2S 8 Ah, ≥30 Wh, 8 h + 4 h |
| USB only | Flight core and comms boot at reduced clock, services off; ≤387 mA from attach (D-6.5); restricted loads for download |
| Boot and restart | Essential flight work starts on its own. Services are sequenced with PE8; one bounded service restart. Nothing waits for a NOR scan, GNSS or CAN |
| Recording | 15 data pages + footer per 4 KiB sector. Full rate from launch detect with a RAM pre-trigger; erase-ahead only before launch detect (D-6.9). [Format](justifications/recording-and-service.md) |
| CAN | 500 kbit/s Classical for commissioning. Moving to 500 kbit/s / 2 Mbit/s FD needs the other node's owner to agree |
| Monitoring | I2C4 at 100 kHz; addresses 0x40 / 0x41 / 0x48; probe curve, reference and diagnostic windows specified |
| RF | Passive GNSS antenna; a same-variant Wio as the reference peer. Don't assume valid GNSS outside its envelope |
| Observability | Status reports only connected, fresh evidence. No made-up power-good, branch identity or physical-arm state |

## What "ready for capture" means

Processor, power, sensor, service, monitoring and comms blocks each have a
baseline and a change list. Building exact libraries, checking decoupling and
fixing ERC is **Codex capture work**, not more research for Seán.

The output block has a decided topology (D-6.2, D-7.1) and energy feed (D-6.1).
Still open: the staging arm and latch wiring (D-7.2), the igniters (all-fire and
no-fire current), continuity values, the fuse, arm-switch and J6101 / J6102
connector parts, and the energy-tap check in D-6.1. Pyro energy links R6310 /
R6410 / R6510 stay DNP until those close. Nothing here grants
authority to fire. See the [output chapter](03-energetic-outputs.md).

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
5. Updated current-system, affected contracts and firmware handoff, and a
   project-log entry. Changes that cross into another project are agreed with
   its owner.

Seán routes. Fabrication needs finished routing and DRC, plus land-pattern and
assembly review. Flight needs physical evidence for source changeover, faults,
acquisition, storage, EMC, thermal, environment, installed antennas and loads,
and any separately approved output system. Don't record those later
measurements as if this specification had observed them.
