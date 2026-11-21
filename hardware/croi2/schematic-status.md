# Croi2 engineering status

Capture started 21 November 2026 (D-21Nov.9), from the [capture specification](../../docs/architecture/schematic-capture-spec.md).
Each step is one commit on main, and Seán reviews each one. The PCB stays untouched
until layout, so schematic/PCB parity is broken until the PCB is updated from this schematic.

## Steps

| Step | Sheets | Status |
| --- | --- | --- |
| 0 | 02-flight-mcu: the amended pad map | Done: 23 pins; alternate functions checked against ST's pin data |
| 1 | 02a-flight-support: VBAT feed, test pads, strobe, reset memory | — |
| 2 | 01-power: auto-retry, power hold, energy tap, J102.8 | — |
| 3 | The other power sheets: core enable, limiters, LDO dividers, C1403, USB limiter | — |
| 4 | Sensor sheets and the new magnetometer sheet | — |
| 5 | 05-can: bus 2, Gecko connectors, B-39 | — |
| 6 | Output sheets and servo removal | — |
| 7 | Comms MCU to LQFP64; inter-MCU link | — |
| 8 | Close-out: root sheet, full ERC, checkers, pin CSVs, J101 footprint | — |

## How each step is checked

- KiCad 9.0.8, from Ubuntu 26.04's archive, reproduces the 8 September baseline
  exactly: 643 parts, 2,179 pins, the same 10 ERC findings.
- The netlist delta against the previous step must equal the step's intended delta,
  pin by pin ([tools/capture](tools/capture/README.md)).
- ERC: a step may add only findings that a named later step closes (below).
- Each changed sheet is rendered and looked at before the commit.

## Open ERC findings and the step that closes each

| Finding | Closes at |
| --- | --- |
| U201 VBAT undriven; `FLIGHT_VBAT`, `RESET_MEMORY`, `TP_STROBE`, `TP_PC6`, `TP_PC7`, `TP_PD10` dangling | 1 |
| `FC_POWER_HOLD` dangling | 2 |
| `SERVICE_POWER_EN` dangling | 3 |
| `MAG_INT`, `MAG_SCL`, `MAG_SDA` dangling; PWR_FLAG pin-to-pin warnings on 03st and 03bmp (baseline) | 4 |
| `CAN2_TX`, `CAN2_RX` dangling | 5 |
| `PYRO1_FIRE`–`PYRO3_FIRE` dangling; pyro VS pins undriven (baseline); the servo block's findings (`SERVO*`, `ADC_SERVO_RAIL`, U6802, U6804) | 6 |
| `LORA_RXEN`, `LORA_TXEN` dangling (baseline) | 7 |

## Checks owed for Burrito

| Check | Where | Status |
| --- | --- | --- |
| JLC stock for every BOM line, with substitutes where something isn't stocked (radio and GNSS modules, Samtec, Gecko, Nano-Fit first) | Early pass during capture; full pass at 8 | Open |
| Flight MCU alternate functions against ST's pin data | 0 | Done: all 29 AF rows match; FDCAN2 = AF9 on PA10/PB5; I²C3 = AF4 on PA8/PC9 |
| Comms MCU alternate functions against ST's pin data | 7 | Open |
| TPS2663 MODE: GND gives auto-retry (D-6.3) | 2 | Done: TI datasheet, section 8.4 |
| Hold capacitor (470 µF) is aluminium electrolytic, leakage ≤30 µA, as D-2Nov.18's hold time assumes. A polymer part's ≈300 µA cuts Churro's hold to 0.33–0.45 s | 2 | Open |
| Sounder level for IREC 6.16 (B-07): a louder sounder is a capture choice | 6 or 8 | Open: Seán's call on the level |
| J6101 / J6102 and umbilical-side parts drawn as reviewed placeholders | 6 | Open |
| Capture assertions 1–22 ([11 Verification](../../docs/architecture/11-verification.md)) | 8 | Open |
| Revised pin maps and [firmware interface](../../docs/firmware-interface.md) | 8 | Open |
| J102 position against Ériú's bay answer (Jay): the Samtec pair only mates end to end | Before layout | Open |
| B-39 series-part values | Bench | Open |
| Footprint, rating and assembly review (G1) | After layout | Open |

## Baseline, 8 September 2026

The status before capture, kept as it stood.

8 September 2026. Current draft; supersedes the historical counts below the
[previous status](history/pre-readable-2026-09-08/schematic-status.md).
That archived document retains earlier support-value rationale and open tests;
its old GNSS/switch descriptions are superseded by the current change record.

### Read and inspect

44 pages explain circuit purpose, interfaces and local connections. The
root index sets the reading order. 643 physical symbols / 642 footprints.
Schematic-to-PCB paths, pad nets, values, DNP and original placements were
checked independently against native KiCad exports.

2,179 schematic pins and 381 architecture assertions pass. All 28 DNP flags
remain; physical output-energy sources are still undefined. Four ERC errors
and six warnings are the existing baseline. PCB DRC has 61 findings (previously
62), with J101 the only missing-footprint parity finding.

80 × 230 mm provisional canvas; four copper layers, 1.6 mm. 501 front and
141 back footprints, 68 original groups, 20 retained rule areas. Eight new
parts are explicitly staged outside the outline. 572 model instances resolve;
this does not mean every physical component has an exact model.

Both boards remain unrouted. Original locations, sides, angles and identities
are retained; U4504 deliberately changes package at its old origin.
These checks do not establish routing capacity, vehicle fit, EMC, thermal
performance, assembly quality or flight reliability.

### Electrical delta and next work

Read [installation-change-record.md](installation-change-record.md). It defines
external maintained source-enable contacts and MAX-M10S external GNSS.
Electronic OFF is not physical battery disconnection or energetic safing.
Firmware remains Anav's responsibility; final placement and routing are Seán's.

Review circuits together, integrate the staged parts, close footprint/rating/
assembly issues before ordering, then test functional blocks on the first
complete PCBA with current-limited supplies and inert loads. No separate
mini-PCB gate was introduced. Earlier unresolved engineering details remain
in the archived status and current architecture contracts.
