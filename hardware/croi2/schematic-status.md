# Croi2 engineering status

Capture started 21 November 2026 (D-21Nov.9), from the [capture specification](../../docs/architecture/schematic-capture-spec.md).
Each step is one commit on main, and Seán reviews each one. The PCB stays untouched
until layout, so schematic/PCB parity is broken until the PCB is updated from this schematic.

## Steps

| Step | Sheets | Status |
| --- | --- | --- |
| 0 | 02-flight-mcu: the amended pad map | Done: 23 pins; alternate functions checked against ST's pin data |
| 1 | 02a-flight-support: VBAT feed, test pads, strobe, reset memory | Done: 13 parts, 22 pins; C207 moved to `FLIGHT_VBAT`; 7 findings closed |
| 2 | 01-power: auto-retry, power hold, energy tap, J102.8 | Done: 7 parts, 20 pins; `BAT_EFUSE_IN` renamed `ENERGY_TAP` (also on 07a); 1 finding closed |
| 3 | The other power sheets: core enable, limiters, LDO dividers, C1403, USB limiter | Done: U1203, its bypass C1203 and U4402 removed; R1210 added; 7 values; service restart on PE8; 1 finding closed |
| 4 | Sensor sheets and the new magnetometer sheet | Done: 42 parts out (switches, isolators, their pull-downs, bleeders and bypass caps); links 47R; nets joined; new 03mag sheet, 10 parts; 3 findings closed |
| 5 | 05-can: bus 2, Gecko connectors, B-39 | Done: bus 2 copied from bus 1 (17 parts); J501 / J502 Gecko-SL; B-39 R / F footprints on both references; 2 findings closed |
| 6 | Output sheets and servo removal | Done: 65 parts out (one-shots, gates, their bypass caps, the whole servo block and sheet 06d, J6602, the 08 servo divider); F6101 / F6102 arm feeds, J6101 / J6102 placeholders, R6005, U6502 now SN74LVC1G08; R6x14 1.24k and the twelve continuity resistors 3.9k, fitted; 15 findings closed |
| 7 | Comms MCU to LQFP64; inter-MCU link | Done: U401 redrawn as STM32H563RIT6 from the 64-pad map (same symbol UUID); USART3 on PC10 / PC11; C405 and C408 removed (no such pads); 2 findings closed |
| 8 | Close-out: root sheet, full ERC, checkers, pin CSVs, J101 footprint | Root renumbered; ERC clean with 3 recorded exclusions; checker rewritten with the capture assertions (342 checks pass); as-captured pin maps; fresh exports; library manifest and 5 of 7 missing 3D models. J101 footprint blocked: Molex drawing not obtained |

## How each step is checked

- KiCad 9.0.8, from Ubuntu 26.04's archive, reproduces the 8 September baseline
  exactly: 643 parts, 2,179 pins, the same 10 ERC findings.
- The netlist delta against the previous step must equal the step's intended delta,
  pin by pin ([tools/capture](tools/capture/README.md)).
- ERC: a step may add only findings that a named later step closes (below).
- Each changed sheet is rendered and looked at before the commit.
- Each step's script (`tools/capture/steps/sNN_*.py`) and its check (`sNN_check.py`) are committed with it.

## Open ERC findings and the step that closes each

| Finding | Closes at |
| --- | --- |
| U201 VBAT undriven; `FLIGHT_VBAT`, `RESET_MEMORY`, `TP_STROBE`, `TP_PC6`, `TP_PC7`, `TP_PD10` dangling | 1: closed |
| `FC_POWER_HOLD` dangling | 2: closed |
| `SERVICE_POWER_EN` dangling | 3: closed |
| `MAG_INT`, `MAG_SCL`, `MAG_SDA` dangling | 4: closed |
| Pin-to-pin warnings on 03st and 03bmp (baseline): the IMU's aux pins and the BMP390's SDO are strapped to GND, a net with a PWR_FLAG. Correct as drawn; record as ERC exclusions with that note | 8: excluded, reasons in Croi2.kicad_pro |
| `CAN2_TX`, `CAN2_RX` dangling | 5: closed |
| `PYRO1_FIRE`–`PYRO3_FIRE` dangling; pyro VS pins undriven (baseline); the servo block's findings (`SERVO*`, `ADC_SERVO_RAIL`, U6802, U6804) | 6: closed. VS: a PWR_FLAG on each `PYROn_ENERGY`, fed through its DNP link |
| `LORA_RXEN`, `LORA_TXEN` dangling (baseline) | 7: closed. PC3 / PC4 are the map's "MCU-only reservation, no external connection": no-connect flags and a note on the sheet |

## Checks owed for Burrito

| Check | Where | Status |
| --- | --- | --- |
| JLC stock for every BOM line, with substitutes where something isn't stocked (radio and GNSS modules, Samtec, Gecko, Nano-Fit first) | Early pass during capture; full pass at 8 | Early pass done ([jlc-stock.md](jlc-stock.md)): 21 lines not in stock, alternatives listed; Seán's calls owed on the sensor, monitor and flash swaps |
| Flight MCU alternate functions against ST's pin data | 0 | Done: all 29 AF rows match; FDCAN2 = AF9 on PA10/PB5; I²C3 = AF4 on PA8/PC9 |
| Comms MCU alternate functions against ST's pin data | 7 | Done: all 64 pads and 11 AF rows match ST's open pin data (STM32H563RITx.xml, H56x GPIO modes); USART3 = AF7 on PC10 / PC11 (`s07_check.py`) |
| TPS2663 MODE: GND gives auto-retry (D-6.3) | 2 | Done: TI datasheet, section 8.4 |
| VBAT retention ≥1 s (D-6.4). C219 (100 µF 6.3 V X5R) keeps roughly a third of its value at 3.3 V, and BAT54 leakage rises steeply when hot. Fallback if short: 100 µF 10 V 1206, stocked | Bench, at temperature | Open |
| Hold capacitor (470 µF) is aluminium electrolytic, leakage ≤30 µA, as D-2Nov.18's hold time assumes. A polymer part's ≈300 µA cuts Churro's hold to 0.33–0.45 s | 2 | Chosen: C1007 Panasonic EEEFKJ471XSP, 6.3 V; the standard 0.01CV limit gives 29.6 µA. Confirm on Panasonic's FK datasheet at G1 |
| Sounder level for IREC 6.16 (B-07): a louder sounder is a capture choice | 6 or 8 | Open: Seán's call on the level |
| J6101 / J6102 and umbilical-side parts drawn as reviewed placeholders | 6 | J6101 / J6102 drawn: `Conn_01x02`, no footprint. Part open: Seán's call on the family. Each must not mate Churro J701 (Micro-Fit 430450200), the GH enable loops or the other. Umbilical parts: Churro |
| F6101 / F6102 (Littelfuse 0451004.MRL, 4 A fast NANO2): pulse checked (a 2 A pulse is half the rating; both recovery channels together are 4 A, at the rating, 4 h minimum to open). Breaking capacity is 50 A (JLC's listing; Littelfuse's table, as read, is blank on this row) against the pack's fault current, which depends on the pack and harness | Pack chosen | Open |
| D-19Nov.2 names F6801, U6802, U6803, U6804, J6602 and the bulk. The CAD had no F6801 or bulk: the servo feed was R6804 (DNP link). Capture removed the whole servo block: sheet 06d (with U6801, its caps and R6801–R6804), R6601–R6607 on 06b, and the 08 servo divider (TMUX1511 channel 4 left unused, pins NC) | 6 | Done |
| Board AGENTS.md, README and `libraries/connector-servo-revision.md` still describe J6602 and the servos | 8 | Open |
| Library provenance for parts added during capture (step 1: `Device:D_Schottky`; steps 2 and 3: `CP_Elec_6.3x7.7` and `CP_Elec_8x10.5`; step 4: `Ogma2:MMC5983MA` symbol and footprint; step 5: `Conn_02x03_Top_Bottom`, `Polyfuse`, `Fuse_1206_3216Metric` (new `Fuse` library) and `Ogma2:G125-MS10605M2P`; step 6: `Device:Fuse`, `Fuse_Littelfuse-NANO2-451_453` and `Ogma2:SN74LVC1G08DBVR` (from 74xGxx:74LVC1G08); step 7: `Ogma2:STM32H563RIT6` (from MCU_ST_STM32H5:STM32H563RITx; VCAP pad 62 set passive, see its ERC_Model) and `LQFP-64_10x10mm_P0.5mm` (new `Package_QFP` library); 3D models still to collect; all from KiCad 9.0.7). Ogma2.kicad_sym also holds three copies each of `430451000` and `SN74LVC1G04DBVR` and the board library manifest | 8 | Manifest regenerated with each source; 5 KiCad models fetched. Still open: no 3D model for the NANO2 fuse or the Gecko (KiCad ships neither), and the duplicate symbols in Ogma2.kicad_sym |
| J101 footprint (Molex Nano-Fit 1053111102) from Molex's drawing: no guessed pads, no 105309 substitute | 8 | Blocked: this session can't reach Molex or the distributors' PDFs, and the text layer doesn't carry the land pattern. Needs the sales drawing attached (PDF) |
| C1403 (Nichicon PCW0J102MCO1GS, 8 × 10.5 mm) land pattern against Nichicon's drawing; `CP_Elec_8x10.5` is KiCad's generic 8 mm can | G1 | Open |
| `USB_CONFIG_OK` now drives nothing: its two loads (U1203, U4402) are gone, and the spec keeps comms PA1 and its boundary. Keep it, or drop the signal and its parts | 7 | Open: Seán's call |
| Docs that still say the core input follows `BAT_VALID OR USB_CONFIG_OK` (pcb-layout-guide.md) | 8 | Open |
| MMC5983MA footprint: KiCad's MEMSIC LGA-16 3 × 3 mm pattern was made from the MMC5883MA drawing; check its pads against the MMC5983MA drawing | Before layout | Open |
| Doubled pull-ups after the join: each SPI chip select has two 47k (R3x05 moved, R3x06 kept); each pressure-sensor I²C line has 4.7k ∥ 10k ≈ 3.2k. Both work; dropping the MCU-side R3x06 / R3407–R3408 / R3507–R3508 would simplify | 8 | Open: Seán's call |
| Capture assertions 1–22 ([11 Verification](../../docs/architecture/11-verification.md)) | 8 | Done in `tools/check_schematic_full.py` (A1–A12, A14–A16, A18, A19, A22). A13 (J6101 / J6102 / J701 mating) waits on the connector parts; A17 (J101 / J102 variants) can't be checked in a KiCad 9 schematic, so it's an assembly rule; A20 / A21 are Churro's |
| Revised pin maps and [firmware interface](../../docs/firmware-interface.md) | 8 | Open |
| J102 position against Ériú's bay answer (Jay): the Samtec pair only mates end to end | Before layout | Open |
| B-39 series-part values (R516 / F501 bus 1, R517 / F502 bus 2; 0R until then) | Bench | Open |
| CAN connector series (D-18Nov.4 left it open): drawn as Gecko-SL G125-MS10605M2P, 2×3 vertical SMT with screw-lok fixings; pins 1–3 H / L / reference, 4–6 spare. The latched through-hole G125-MV10605L1 is the alternative. Fajita's end of J501 has to match | Before layout | Open: Seán's call |
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
