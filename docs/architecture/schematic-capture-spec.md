# Schematic capture and placement specification

22 September 2026, amended 6 October with decisions D-6.1–D-6.10 in
[decisions.md](../../decisions.md). **Proposed capture baseline. No CAD green light yet.**

Seán's intended handoff: approve this specification → **Codex captures the
schematics and places components → Seán routes**. Anav owns firmware. Approval
to capture is not fabrication, energetic-output or mission release.

## Starting point and authority

Use native `hardware/croi2/` and `hardware/foinse2/` at review-branch baseline
**9a8c2a2**, plus any subsequently reviewed manual changes. The September 22
audit exported both native schematics and confirmed pin/net/reference/value/
footprint parity with the stored netlists: 2179/306 connected pins and 643/113
physical components respectively. This is connectivity evidence, not electrical
validation. Preserve UUIDs, DNP states, board-local libraries and mechanical work.

**Retain every baseline connection/value unless the explicit delta below changes
it.** Resolve a conflict against native evidence and this delta before capture;
do not combine an old two-rail sketch with the new three-domain specification.
Both proposed MCU CSVs use exact native electrical net identifiers, including
ADC divider outputs and each side of the partial-power boundaries. `NC` means
leave that pad unconnected; never create a shared net called `NC`. Functional
changes are flight PD10, the comms UART port/package migration and the
6 October decisions in the table below. Other name
corrections preserve native connectivity; the frozen hardware input CSVs contain
functional shorthand and are not the net-name authority.

The [justification index](justifications/README.md) supplies alternatives, sources,
calculations and consequences. Older dated recommendations do not add requirements.

## Burrito capture delta

| Block | Exact instruction | Reason / source |
| --- | --- | --- |
| Flight U201 | Keep STM32H563VIT6 LQFP100; use [proposed 100-pad map](proposed-flight-pinout.csv), amended by the pad changes below | PD10 pad 57 becomes SERVICE_POWER_EN; the CSV still holds 22 Sep nets so the proposal checker keeps passing |
| Flight pad changes (6 Oct) | PE5 pad 4 → `FC_POWER_HOLD` (100 kΩ pull-down). PE6 pad 5, PA8 pad 67, PA9 pad 68, PA10 pad 69 → NC (sensor enables removed). PE7 pad 38 → `PYRO1_FIRE`, PE9 pad 40 → `PYRO2_FIRE`, PE12 pad 43 → `PYRO3_FIRE` (DNP channel), each driving its TPS1H100 IN directly. PE8, PE10, PE13, PE14 → NC (low-side selects and recovery permit removed). PD14/PD15 keep their nets for the DNP staging latch | D-6.2, D-6.3, D-6.6 |
| Comms U401 | STM32H563RIT6 LQFP64; use [complete 64-pad map](proposed-comms-pinout.csv) | [Package justification](01-mcus.md); package-specific supply/VCAP/HSE/SWD connections, not copied 100-pin numbering |
| Inter-MCU link | Comms PC10 TX → CC_COMMS_TO_FLIGHT → U4301.1; PC11 RX → CC_FLIGHT_TO_COMMS → U4301.8; USART3 AF7 | Flight-side FLIGHT_TO_COMMS / COMMS_TO_FLIGHT stay on the opposite side of U4301 |
| Regulators | Retain U1701/U1801/U1901 TPS7A9101DSKR and their domains | [Three-domain fault justification](justifications/power-domains.md) |
| LDO dividers | R1701/R1801/R1901 → 31.9 kΩ 0.1%; lower 10 kΩ 0.1% retained | 3.352 V nominal on all three rails; calculated corners 3.310–3.394 V |
| Comms input limiter | U1501 remains before U1801, existing COMMS_BRANCH_EN; R1504 → 66.5 kΩ 1% | 351–449 mA calculated limit |
| Service input limiter | U1601 remains before U1901; R1604 → 49.9 kΩ 1% | 470–588 mA calculated limit |
| Service recovery | Move U1601 EN (pin 3) and top of R1602 100 kΩ from FLIGHT_3V3 to SERVICE_POWER_EN; drive PD10 | Reset/off default low; bounded sequenced recovery, separate from comms |
| Held input capacitor | C1403 → Nichicon PCW0J102MCO1GS, 1000 µF/6.3 V | Exact manufacturer footprint/body check; flight hold-up only |
| Sensors | Remove U3101–U3501 (TPS2553), U3102/U3202/U3302 (TXU0304), U3103/U3203/U3303 (TXU0101), U3402/U3502 (TMUX1511), R3x02 enable pull-downs and R3x03 rail bleeders. Feed each sensor from FLIGHT_3V3 through its existing 0 Ω link (R3101–R3501). Join MCU-side and sensor-side signal nets; keep 22 Ω damping and re-home pull-ups to FLIGHT_3V3 | D-6.6 |
| NOR/CAN/AUX | Retain devices, buses, local limiters and partial-power boundaries | [Sensors](07-sensors-logging.md), [CAN](08-foinse-can.md); service net identifier remains 3V3_OPTIONAL |
| Core enable | Remove U1203. Drive U1401 EN/UVLO from a divider on 4V_PRE (R1204 becomes its lower leg), enabling above ≈3.6 V; values from the LM73100 threshold | D-6.5 |
| USB limiter | Remove U4402 (TS5A3167). U4401 ILIM fixed by R4403 60.4 kΩ: 387–491 mA from attach. Keep U1201/U1202/U1204 | D-6.5 |
| U101 fault mode | MODE pad 11 to GND: auto-retry | D-6.3 |
| Enable hold | `FC_POWER_HOLD` → series resistor → capacitor to GND → BAT54-class diode → `BAT_SHDN_N`. Second diode from the same node → J102.8 (`CROI_POWER_HOLD`). Size the RC so SHDN stays above threshold ≥300 ms after the GPIO releases (TPS3430 reset 170–230 ms) | D-6.3 |
| Flight VBAT | U201 pad 6 from FLIGHT_3V3 through a BAT54-class Schottky; add 100 µF ≥6.3 V X5R to GND beside the existing 100 nF | D-6.4 |
| Energy tap | New node `ENERGY_TAP` at BAT_EFUSE_IN (after Q101, before U101) if TPS26630 keeps Q101 on through U101 faults and SHDN; otherwise at VBAT_CROI_INPUT with reverse-polarity protection per branch. Outputs and servos no longer pass R7101 | D-6.1 |
| Pyro feed and arm | `ENERGY_TAP` → F6101 (≈4 A fast-acting, I²t checked against a 2 A firing pulse) → J6101 (Molex Micro-Fit 430450200, mate 430250200, to the external arm switch) → `RECOVERY_ARMED_VBAT`. Retain R6101/R6102 and U6103 arm sense to PC8. `STAGING_ARMED_VBAT` stays unsourced | D-6.1 |
| Recovery outputs | Per channel 1 and 2: retain U6304/U6404 TPS1H100 with IN from `PYROn_FIRE` and its 100 kΩ pull-down; fit R6314/R6414 = 1.24 kΩ 1% (≈2.0 A). Remove U6301/U6401 and R6311–R6313/R6411–R6413, U6302/U6303/U6402/U6403, Q6301/Q6401 and their gate parts. Tie OUTPUT1_LOW/OUTPUT2_LOW (J6601.4/.5) to GND. Remove U6002–U6005, U6101, U6102, U6104. Retain 06c current diagnostics and 06e/06f continuity paths; set continuity values against the selected igniter's no-fire current | D-6.2 |
| Staging | Channel 3 (06pyro3), U6001, R6103/R6104 and R6510 DNP; J6601.3/.6 unwired | D-6.2 |
| Local PWM | Keep PC6/PC7 TIM3; remove R6606/R6607; disconnect J6602.7/.8/.9; tie U6804.4 A3 to GND, leave U6804.11 B3Y NC | J6602 contacts 7–10 unused; retain the existing unused fourth-channel terminations |
| Servo power | Retain U6802, R6802 1.24 kΩ 1%, U6803 and U6804. `ENERGY_TAP` → F6801 (≈4 A) → `SERVO_ARMED_VBAT`; fit R6804. Add ≥220 µF ≥16 V polymer on SERVO_VBAT at J6602. Not behind the pyro arm | D-6.1, D-6.7; [bounded raw-2S interface](justifications/interfaces-and-installation.md#two-local-pwm-interfaces-no-speculative-remote-node) |
| Service/status/RF | Retain lamp/sounder/debug/USB, MAX-M10S and Wio-LR2021; no extra display, RTC, flash or remote actuator node | [Service](05-service-status-time.md), [RF](06-gnss-radio.md) |
| Source population | Standalone J101 or Churro J102, never both fitted in the flight assembly | [Variant table](justifications/interfaces-and-installation.md#source-variants-and-harness-construction) |
| J101 footprint | Replace empty reservation using exact Molex 1053111102 drawing | Project-local footprint; no guessed pads or 105309 substitution |

Comms PA1/PA2/PB5 retain CC_USB_CONFIG_OK / CC_BAT_VALID /
CC_BRANCH_FAULT_N and their existing boundary circuits. Comms VDDA/VREF+ pad 13
uses COMMS_VDDA through the retained R401 link; flight VDDA/VREF+ retain
FLIGHT_VDDA. Keep processor-specific HSE/SWD nets distinct.

Comms LQFP64 VCAP pads 30/62 each require 2.2 µF locally; VDDUSB has no external
pad in that package. Preserve flight PC13's quiet LSE restriction. All newly
unused signals need an explicit NC or defined input level; deleting a function
must not leave a powered translator input floating.

## Churro capture delta

Retain autonomous source protection, threshold networks, source controls,
Samtec pinout (except pin 8, now `CROI_POWER_HOLD`), TCA4307, INA228, ADS1115 and voltage-input TMUX1511. No MCU,
charger, BMS, CAN endpoint or 24 V converter. The [monitoring justification](justifications/churro-monitoring.md)
is the connection authority for the following additions.

| Reference | Selection / capture |
| --- | --- |
| U6201 | REF3325AIDBZR, SOT-23-3; ADC_3V3 → 2.5 V NTC bias |
| C6201 / C6202 | 1 µF each, 16 V X7R, 0603, at reference IN/OUT respectively |
| U6202 | ADG7421FBCPZ-RL7, LFCSP-10 CP-10-16; exact ten-pin mapping in rationale |
| C6203 | 100 nF, 16 V X7R, 0603, ADC_3V3 to GND at U6202 |
| R6211/R6212 | 2.2 kΩ 0.1%, 1206, each J601 probe signal to its protected switch S input |
| R6201 / TP6201 | 10 kΩ 0603 pull-up on FF to ADC_3V3; local fault test point only |
| R6202 | 10 kΩ 0603 ADC_3V3-to-GND bleeder; limits floating-rail retention, costs ~0.34 mA while powered |
| D6201/D6202 | SMF33CA, SOD-123FL, probe connector signals to GND before series resistors |
| R6003/R6004 | Retain 10 kΩ 0.1%; move bias tops to NTC_REF_2V5, bottoms to protected D1/D2 nodes |
| R6005/R6006 | Retain 1 kΩ; input ends move to D-side bias nodes, output ends remain AIN0/AIN1 |
| C6002/C6003 | Change 10 nF to 1 µF, 16 V X7R, 0603, retaining ADC-input-to-GND connection |
| J101 | Same exact Nano-Fit footprint correction as Burrito |
| U1001 | MODE pad 11 to GND: auto-retry (D-6.3). U2001 unchanged pending the propulsion owner |
| J301.8 / AV hold | J301 pin 8 (`CROI_POWER_HOLD`) → BAT54-class diode → `AV_SHDN_N` (D-6.3). PROP enable not held |
| External probes | Vishay NTCLE305E4103SB ×2; J601 AV/GND/PROP/GND; ≤0.5 m dedicated paired leads |
| Pack service assembly | 0287005.PXCN fuse in FHAC0001ZXJ holder for each source; protected short 20 AWG paired harness, properly joined to holder's 16 AWG leads |

The 6200 references are unused in the inspected native Churro netlist. Create
new IC symbols/footprints from the exact manufacturer drawings; record provenance
and audit pin-one, underside/thermal-pad requirements and dimensional tolerances.
The ADC bleeder does not establish a guaranteed off-rail voltage under every
cable fault; measure rail/ADC transients and leakage before qualification.

Reference distribution ceilings: AV 3 A and PROP 2 A continuous, subject to
thermal/harness qualification. Source fuses are assembly parts, not invented PCB
locations. Retain both AV protection stages for standalone compatibility; no
selective trip-order claim.

## Operating contracts that constrain capture

| Area | Proposed baseline |
| --- | --- |
| Logic power | 200/300/200 mA flight/comms/services allocation; all three nominal 3.352 V |
| Source endurance | Workhorse: set from measured first-PCBA loads and the vehicle timeline (D-6.8). Kármán overlay keeps 2S 8 Ah, ≥30 Wh, 8 h + 4 h |
| USB only | Flight core and comms boot at reduced clock, services off; ≤387 mA from attach (D-6.5); restricted loads for download |
| Boot/recovery | Essential flight progress starts independently; services sequenced with PD10; one bounded service restart; no waiting for NOR scan/GNSS/CAN |
| Recording | 15 data pages + footer per 4 KiB sector; full rate from launch detect with RAM pre-trigger; erase-ahead only before launch detect (D-6.9); [format](justifications/recording-and-service.md) |
| CAN | Existing 500 kbit/s Classical commissioning; coordinated 500 kbit/s / 2 Mbit/s FD migration requires owning-peer agreement |
| Monitoring | I2C4 100 kHz; addresses 0x40/0x41/0x48; probe curve/reference/diagnostic windows specified |
| RF | Passive GNSS and same-variant Wio reference peer; no assumption of valid GNSS beyond its envelope |
| Observability | Status reports only connected, fresh evidence; no fabricated PG, branch identity or physical-arm state |

These are recommendations offered for acceptance, not claims that the team has
already agreed or that firmware/hardware has demonstrated them.

## What “green for capture” must mean

The ordinary processor, power, sensor, service, monitoring and communications
blocks now have a named baseline and implementation delta. Remaining exact library
construction, decoupling verification and ERC repairs are **Codex capture work**,
not another research task assigned to Seán.

The output block now has a decided topology (D-6.2) and energy feed (D-6.1).
Still open before capture closes it: the igniter (all-fire and no-fire current),
continuity values, the fuse and arm-switch parts, and the energy-tap check in
D-6.1. Pyro energy links R6310/R6410 stay DNP until those close; no operational authority is
supplied. See the [output chapter](03-energetic-outputs.md).

After accepted scope is explicit, Codex delivers:

1. Native readable schematics with the delta applied; exact local libraries,
   part/value/footprint provenance, BOM/population variants and revised pin maps.
2. Fresh exports and ERC, every finding fixed or individually justified; comparison
   against the baseline showing every intentional net/pin/DNP change.
3. A component-placed, unrouted PCB for each board, retaining reviewed outlines,
   mounts and service access; courtyard/height/mating/decoupling/RF/analog checks.
4. Placement review images and routing notes/net classes for Seán, including
   critical current-return, RF, clock, sensor-axis and connector-access constraints.
5. Updated current-system, affected owned contracts/firmware handoff, and append-only
   log. Cross-project contract changes are reconciled with the other owner.

Routing remains Seán's work. Fabrication requires completed routing/DRC, exact
land-pattern and assembly review. Mission release requires physical evidence
for source transitions, faults, acquisition, storage, EMC/thermal/environment,
installed antennas/loads and any separately approved output system. Those later
measurements must not be mislabelled as observations in this specification.
