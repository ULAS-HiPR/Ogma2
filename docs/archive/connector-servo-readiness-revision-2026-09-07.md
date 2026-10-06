# Croí2 connector, third-servo and readiness revision

Status: accepted by Seán on 7 September; installed in the working schematic/PCB
after native verification. Exact connector 3D bodies remain unresolved.
This supersedes the two-servo baseline and independently driven red LED. Firmware
implementation remains Anav's. No output-energy population or flight release.

## Readiness indication

PD7 / U201 pad 88 retains `FLIGHT_STATUS_LED1`, now the readiness control:

| Control | Green D9001 | Red D9101 | Meaning |
| --- | --- | --- | --- |
| Low | Off | On | Not ready: read telemetry or connect USB |
| High | On | Off | Selected mission's required preflight checks passed |
| MCU reset / high impedance, valid flight rail | Off | On | 47 kΩ external pull-down selects not ready |

U9101 **SN74LVC1G04DBVR**, SOT-23-5, drives the existing red LED through
R9101 2.2 kΩ. R9102 47 kΩ pulls its input low; C9101 100 nF bypasses its flight
3.3 V supply. Green retains R9001. Comms amber and the hardware power LED remain
independent; the buzzer is unchanged. No scanning, Charlieplexing or I²C LED driver.

Green is neither an armed indication nor independent launch authority. Start low,
assert only after the active profile checks pass, and clear when a required check
fails. Blink/tone details must not redefine steady green as unconditional health.
Both red and green cannot be independently selected or deliberately extinguished.
A hung MCU holding high can leave stale green; this is not a watchdog or safety
monitor. Below valid logic supply voltage the colours are not guaranteed. Hardware
power indication distinguishes an unpowered board from a powered not-ready board.

## Third servo

Only physical MCU allocation **PD10 / pad 57** changes: independent red LED GPIO
becomes `SERVO3_PWM`, **LPTIM2_CH2, AF3**. PD7's electrical net is unchanged.
PC6/PC7 retain TIM3 CH1/2. Recovery/arming pins and the entire comms allocation
remain unchanged. The current CSV is in `hardware/croi2/libraries/inputs/`;
the original architecture-review CSV is historical for PD10.

U6804 TXU0304's unused forward channel is used: pad 4 A3 receives SERVO3_PWM;
pad 11 B3Y drives SERVO3_PWM_ISO; new R6606 100 Ω reaches the connector;
new R6607 100 kΩ pulls the connector signal down. Existing OE/reset qualification,
servo-side bias LDO and shared raw-battery switch remain. R6804 stays DNP.

Anav: reserve LPTIM2 CH2 for servo 3, select and verify its kernel clock, PWM
polarity, period/compare semantics and stop/reset behavior. It is a different
timer from servo 1/2: do not assume frame phase-lock. Initial nominal commands
remain 20 ms frames / 1–2 ms pulses only until actual actuator limits are known.
Extend channel-indexed commands, leases, safe states and logging to three. Keep
all PWM outputs low while the common rail is disabled. Do not alter recovery
authority. Measure all three physical waveforms and rail-off/back-power behavior
on the first PCBA before actuators are connected.

**Three signal channels do not establish grid-fin power capacity.** The existing
nominal shared 2 A limit remains provisional, not 2 A per servo. Qualify the
selected servos' raw-2S voltage range, 3.3 V PWM threshold, simultaneous motion,
stall current, regenerative transients and source-protection selectivity. Do not
raise the current limit without checking the upstream eFuse, traces and harness.

## Connectors

### J6602 servo harness: new ten-contact connector

Board header **Molex 430451000**, Micro-Fit 3.0, right-angle through-hole.
Matching-family ten-cavity housing: **430251000**; retain **430300007** crimp
contact candidate, nine populated contacts. Final housing/contact/drawing and
wire-size review remains part of harness release. No stock or price claim made.

| Channel | Switched battery | PWM | Ground |
| --- | --- | --- | --- |
| Servo 1 | 1 | 2 | 3 |
| Servo 2 | 4 | 5 | 6 |
| Servo 3 | 7 | 8 | 9 |

Contact 10 is NC, with no fitted wire terminal. This is a **new complete pinout**,
not an extension of the old 430450800 eight-contact harness. Use actual moulded
cavity numbers; the symbol drawing is not a physical mating-face diagram. Each
servo gets its own power and return conductors. J6601's pyro pairs are unchanged.

### J4601 radio antenna

**Amphenol RF 132134**, standard SMA female, vertical/top-entry through-hole,
50 Ω; not RP-SMA and not right-angle. Signal contact 1 retains LORA_RF_SUBG,
connected only to Wio pad 10. All four contact-2 legs are GND. The former U.FL
antenna lead does not mate directly: select a standard SMA-male antenna/lead.

Use the local exact-named KiCad land pattern. Reserve antenna/coupling access
above the board and support the cable/antenna against torque and vibration.
Route a short controlled-impedance RF line over uninterrupted ground; the
collision-free starting position is not a validated RF launch or enclosure fit.
No ground void has been added beneath the connector.

### J6601 pyro connector and charge service

The symbol already exists on `06b-output-harness.kicad_sch`; footprint
**430450600**, six-contact Micro-Fit, remains unchanged. Output pairs are
1/4, 2/5, 3/6. LOW is a switched output return, not chassis ground.
Board plug to strain-relieved harness to a deliberate accessible charge-service
boundary is the architecture. Bare-wire terminals belong to removable development
adapters; retained connectorised charge assemblies remain the space-shot direction.
The exact service-end assembly and physical arm hardware remain unresolved.

## Library and layout limits

SMA and ten-contact servo footprints are stock KiCad exact-named imports, not
freshly hand-drawn patterns. The inverter uses the existing local SOT-23-5 STEP.
Exact 3D bodies for J6601, new J6602 and J4601 are **still missing**. KiCad public
model URL attempts returned 404, Molex download attempts failed, and Amphenol's
STEP requires login. Browser control was not used; no similar-part model was
substituted. Missing 3D geometry is not usable physical space.

USB-C J4401 and its schematic remain untouched, as explicitly requested. Only
the two replaced connectors, five added support parts and two nearby PWM
resistors require placement changes. Preserve all other layout and rule areas.
No routing, enclosure clearance, load qualification or manufacturing release is
implied. Nano-Fit J101 remains the known missing footprint.

## Evidence and review

- [ST H563 datasheet](https://www.st.com/resource/en/datasheet/stm32h563ai.pdf),
  table 15, page 109: PD10 LPTIM2_CH2 AF3.
- [TI inverter datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf),
  page 3 DBV: 1 NC, 2 A, 3 GND, 4 Y, 5 VCC; page 12 bypass/layout.
- [TI TXU0304 datasheet](https://www.ti.com/lit/ds/symlink/txu0304.pdf),
  page 4: A3 pin 4 and B3Y pin 11; existing switched-domain/OE behavior retained.
- [Amphenol 132134](https://www.amphenolrf.com/en-us/part/132134/662/).
- [Molex 430451000](https://www.molex.com/en-us/products/part-detail/430451000).
- Current native checks: `hardware/croi2/full-checks.json`, `board-checks.json`
  and `output/connector-servo-delta-checks.json`.
- Recovery snapshot and bounded scripts: sibling
  `../../connector-servo-2026-09-07/` outside the umbrella repository.

First PCBA: verify readiness colours at boot/reset/brownout, profile pass/fail
and deliberate firmware stall; three servo PWM waveforms and disabled-domain
behavior with inert loads; RF launch and retained-antenna performance. Existing
output-energy DNP safeguards remain until their separate release conditions close.

## Installed verification checkpoint

635 physical symbols, 634 footprints, 2,163 pin checks and 346 architecture
checks. 556 model instances resolve; all linked model paths are local and valid.
Four existing ERC errors and six warnings remain; no new native DRC finding
by type and implicated-item identity. Zero courtyard/drill-reservation overlaps.
All 629 existing footprint UUIDs retained, 622 unaffected footprint states
identical, 38 unrelated sheets byte-identical, all 28 rule areas unchanged.
Only flight allocation row PD10/pad57 changed. Foinse PCB is unchanged.

J6602 moved 3 mm upward to (169.535, 229), keeping its edge-facing orientation;
R6602/R6603 moved locally to clear it. SMA J4601 is at (146.5126, 180.54),
vertical. Five new support footprints are placed. Native board SHA-256:
`03bb9ba5b0731cf31ad1bf958eeb063147fd269cf90446388e2afe51e2bcaf7c`.
These checks prove the stated CAD delta, not electrical or mechanical qualification.
