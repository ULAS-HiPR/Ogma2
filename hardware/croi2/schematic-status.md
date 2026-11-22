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
| 9 | The nine calls decided after close-out (D-21Nov.12–20), on 18 sheets and the root index | Done: 11 parts out (the seven doubled pull-ups; R1206, R4404 and R4304 with `USB_CONFIG_OK`; R9005, the piezo's bleed resistor, with D9002 kept as the coil's flyback diode); U4303 channel 4 input tied to GND, its output and comms PA1 no-connect; J6101 / J6102, U3104, BZ9001, Q9001, the bulk capacitors and the 0.1% resistors set (19 parts); 25 pins; ERC unchanged; A13 and the sounder added to the checker (347 checks pass). Sounder amended at capture to PUI SMT-1028-T-2-R (D-21Nov.20) |
| 10 | D4501 to a part Economic PCBA places (D-22Nov.3, D-22Nov.8) | Done: Nexperia PESD5V0F1BL,315, SOD882 (KiCad D_SOD-882, vendored); symbol kept, bidirectional; 0 pin changes; ERC unchanged; 347 checks pass |
| 11 | Footprint audit before placement | Done: C1403 to `CP_Elec_8x10` (φ8 × 10 mm part); MMC5983MA pads checked against MEMSIC's drawing; J4401's footprint is pad for pad KiCad's GCT USB4105 footprint (the mismatch that came back on the regenerated board was its NPTH layers, 11c); U4302's TXU0101DCKR lands moved to TI's DCK0006A pattern (11a: the old lands barely passed the lead tips); every custom footprint's basis in [footprint-audit.md](footprint-audit.md); J101 still waits for Molex's drawing (SD-105311-100) |
| 11b | U101 (TPS26630RGER) thermal vias | Done: nine 0.2 mm vias to 0.3 mm drill, 0.6 mm pads, same positions (JLC charges below 0.3 mm; D-22Nov.2); library only |
| 11c | J4401 (USB4105-GF-A) NPTH layers | Done: the two locating holes on `*.Cu`, as KiCad 9 writes them, so the board copy matches the library (DRC lib_footprint_mismatch); no copper changes |
| 12 | Test points in three sizes, the lean set (D-22Nov.9) | Done: new sheet `10-test-points` (P45), TP9501–TP9525 by global label: 7 orange 5003 loops (6 rails, GNSS PPS), 2 black 5011 GND loops, 16 pads; 13 resized (10 rail loops 5000 → 5003, TP2304 / TP4204 5001 → 5011, TP201 pad → 5003 loop); 36 cut with their wiring (sensor rails and buses, LoRa SPI, CAN logic, NRST, duplicate rail loops, TP502); 47 test points; every loop has its LCSC number; 559 parts, 1820 pins, 61 pin changes; ERC unchanged; checker TP1–TP5 new, all pass |
| 13 | Test points renumbered TP1–TP47 fore to aft (D-22Nov.9) | Done: the order is from the 80 × 180 placement (D-22Nov.10), in 2.5 mm rows of y, then x; refs, instance paths and notes renamed; 94 pin changes (47 out, 47 in, same nets); ERC unchanged; checker passes; the rebuild moved no test point |
| 14 | J103 to a Molex Micro-Fit 3.0, single row, two circuits (D-22Nov.18) | Done: 43650-0215, vertical through-hole with a polarizing peg, JLC C293740; KiCad 9.0.7 footprint vendored, model drawn (`models3d.py`); stray resistor fields from the old symbol fixed; 0 pin changes; ERC unchanged; checker A13b: J103 is single-row (43650), whose listed mates exclude J701's dual-row 43025 plug; 353 checks pass |
| 15 | J101's footprint: Molex Nano-Fit 105311-1102 (D-22Nov.13, sweep §10) | Done: `Ogma2:105311-1102` drawn by the step from SD-105311-100 rev H: pins Ø1.2 at 2.5 mm, clips Ø1.6 C = 6.84 mm apart with no net, peg Ø1.3 unplated 1.34 mm off the row on the latch side; pads ours (pin Ø1.8, clip Ø2.1); model drawn; the spec's reserved block replaced by a left-edge place; 0 pin changes; ERC unchanged; checker: no part without a footprint, 354 checks pass |
| 16 | The 0402 swap (D-22Nov.13, execution brief A4) | Done: 200 of 387 0603 parts to 0402 (105 R, 95 C), each with its JLC part pinned (MPN, LCSC); 522 mm² of courtyard saved. Kept: the fire-path sheets (76), 0.1% (34), rails above 5 V (13), 0 R links (12), ≥ 2.2 µF (11), limit / sense / termination (15), over 30 mW (6), and 15 × 1 µF X7R 16 V with no 0402 part at the stated rating. Every part and reason in [passives-0402.md](passives-0402.md). 0 pin changes; ERC unchanged; checker 354 pass |
| 17 | The A5 additions (D-22Nov.20) | Done: D4601 (PESD5V0F1BL,315) on `LORA_RF_SUBG` at J4601, as D4501 on GNSS; C6601–C6606, 1 nF 50 V C0G 0603, each pyro output to GND at J6601; global labels; 566 parts, 1834 pins, 14 pin changes; ERC unchanged; checker A3, A9 amended, A23 added, 364 checks pass |
| 18 | The rail and strobe loops to surface mount (D-22Nov.24) | Done: 18 loops from Keystone 5003 through-hole (orange) to 5194TR surface-mount (yellow, C22388408); footprint `Ogma2:TestPoint_Keystone_5190TR_ColorKeyed` drawn by the step from Keystone's SMT catalogue page, model drawn (`models3d.py`); footprint and part fields only, 0 pin changes; ERC unchanged; checker TP3 follows, 364 checks pass |
| 19 | MCU pin swaps for the placement (D-22Nov.25) | Done: 36 flight and 12 comms nets moved (labels traded on sheet 02; on sheet 04 five pins gain a no-connect and five lose one); the spare pads renamed `TP_PA9`, `TP_PA11`, `TP_PA12` with their labels and values; both pin maps with ADC channels and AF numbers from ST's pin data (51 rows match, `libraries/inputs/st-open-pin-data`); 56 pin changes; ERC unchanged; checker A8, A16 and the USART3 and CAN standby checks follow the pins, A24–A26 added (A24 and A25 fail on step 18's netlist), 369 checks pass |

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
| JLC stock for every BOM line, with substitutes where something isn't stocked (radio and GNSS modules, Samtec, Gecko, Nano-Fit first) | Early pass during capture; full pass at 8 | Done ([jlc-stock.md](jlc-stock.md)). Parts with an MPN: 21 lines not in JLC's library, alternatives listed; the LSM6DSV32X swap captured at step 9 (D-21Nov.16; BMP390, INA228 and NOR stay, through Global Sourcing). Generic passives, rerun after step 9: all 70 lines match (34 Basic), the bulk capacitors and 0.1% values settled (D-21Nov.17, D-21Nov.18). Still open: the MCUs to buy into the private library (D-21Nov.19, Seán) |
| Flight MCU alternate functions against ST's pin data | 0 | Done: all 29 AF rows match; FDCAN2 = AF9 on PA10/PB5; I²C3 = AF4 on PA8/PC9 |
| Comms MCU alternate functions against ST's pin data | 7 | Done: all 64 pads and 11 AF rows match ST's open pin data (STM32H563RITx.xml, H56x GPIO modes); USART3 = AF7 on PC10 / PC11 (`s07_check.py`) |
| TPS2663 MODE: GND gives auto-retry (D-6.3) | 2 | Done: TI datasheet, section 8.4 |
| VBAT retention ≥1 s (D-6.4). C219 (100 µF 6.3 V X5R) keeps roughly a third of its value at 3.3 V, and BAT54 leakage rises steeply when hot. Fallback if short: 100 µF 10 V 1206, stocked | Bench, at temperature | Open |
| Hold capacitor (470 µF) is aluminium electrolytic, leakage ≤30 µA, as D-2Nov.18's hold time assumes. A polymer part's ≈300 µA cuts Churro's hold to 0.33–0.45 s | 2 | Chosen: C1007 Panasonic EEEFKJ471XSP, 6.3 V; the standard 0.01CV limit gives 29.6 µA. Confirm on Panasonic's FK datasheet at G1 |
| Sounder level for IREC 6.16 (B-07): a louder sounder is a capture choice | 9 | Captured (D-21Nov.20): PUI SMT-1028-T-2-R at 2.83 kHz, Q9001 AO3400A, D9002 (already fitted) as its flyback diode, R9005 removed. Amended at capture from CUI's CMT-8504, whose four pads couldn't be matched to its coil without CUI's datasheet. Open: level at 3.3 V drive and the panel test (B-07) |
| J6101 / J6102 and umbilical-side parts drawn as reviewed placeholders | 9 | Captured (D-21Nov.12): Mini-Fit Jr. 39281023 (J6101), JST B2P-VH (J6102), KiCad footprints; A13 checks the families. Umbilical parts: Churro |
| F6101 / F6102 (Littelfuse 0451004.MRL, 4 A fast NANO2): pulse checked (a 2 A pulse is half the rating; both recovery channels together are 4 A, at the rating, 4 h minimum to open). Breaking capacity is 50 A (JLC's listing; Littelfuse's table, as read, is blank on this row) against the pack's fault current, which depends on the pack and harness | Pack chosen | Open |
| D-19Nov.2 names F6801, U6802, U6803, U6804, J6602 and the bulk. The CAD had no F6801 or bulk: the servo feed was R6804 (DNP link). Capture removed the whole servo block: sheet 06d (with U6801, its caps and R6801–R6804), R6601–R6607 on 06b, and the 08 servo divider (TMUX1511 channel 4 left unused, pins NC) | 6 | Done |
| Board AGENTS.md, README and `libraries/connector-servo-revision.md` still describe J6602 and the servos | 8 | Done |
| Library provenance for parts added during capture (step 1: `Device:D_Schottky`; steps 2 and 3: `CP_Elec_6.3x7.7` and `CP_Elec_8x10.5`; step 4: `Ogma2:MMC5983MA` symbol and footprint; step 5: `Conn_02x03_Top_Bottom`, `Polyfuse`, `Fuse_1206_3216Metric` (new `Fuse` library) and `Ogma2:G125-MS10605M2P`; step 6: `Device:Fuse`, `Fuse_Littelfuse-NANO2-451_453` and `Ogma2:SN74LVC1G08DBVR` (from 74xGxx:74LVC1G08); step 7: `Ogma2:STM32H563RIT6` (from MCU_ST_STM32H5:STM32H563RITx; VCAP pad 62 set passive, see its ERC_Model) and `LQFP-64_10x10mm_P0.5mm` (new `Package_QFP` library); step 9: `Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical` (new `Connector_Molex` library), `JST_VH_B2P-VH_1x02_P3.96mm_Vertical`, `MagneticBuzzer_PUI_SMT-1028-T-2-R` (new `Buzzer_Beeper` library) and `C_0805_2012Metric`; all from KiCad 9.0.7). Ogma2.kicad_sym also holds three copies each of `430451000` and `SN74LVC1G04DBVR` and the board library manifest | 8, 9 | Manifest regenerated with each source; 6 KiCad models fetched (C_0805 at step 9). Still open: no 3D model for the NANO2 fuse or the Gecko (KiCad ships neither), nor for the Mini-Fit, VH or PUI footprints (not on kicad-packages3D's master), and the duplicate symbols in Ogma2.kicad_sym |
| J101 footprint (Molex Nano-Fit 1053111102) from Molex's drawing: no guessed pads, no 105309 substitute | Placement stop | Blocked at step 8: the shell can't reach Molex, and the PDF's text layer doesn't carry the land pattern. Next: Claude reads the drawing in the browser before the placement stop; Seán attaches the PDF only if it can't be read reliably |
| C1403 (Nichicon PCW0J102MCO1GS) land pattern against Nichicon's drawing | 11 | Done 22 Nov: the part is φ8 × 10 mm (Nichicon PCW data, May 2024), not 8 × 10.5; footprint now KiCad `CP_Elec_8x10` (Nichicon 8 × 10) |
| `USB_CONFIG_OK` now drives nothing: its two loads (U1203, U4402) are gone, and the spec keeps comms PA1 and its boundary. Keep it, or drop the signal and its parts | 9 | Captured (D-21Nov.14): R1206, R4404 and R4304 out; U4303 channel 4 input tied to GND like channel 3, its output and comms PA1 no-connect |
| Docs that still say the core input follows `BAT_VALID OR USB_CONFIG_OK` (pcb-layout-guide.md) | 8 | Done |
| MMC5983MA footprint: KiCad's MEMSIC LGA-16 3 × 3 mm pattern was made from the MMC5883MA drawing; check its pads against the MMC5983MA drawing | 11 | Done 22 Nov: pads match MEMSIC's MMC5983MA land pattern (Rev. A p. 20: 0.45 × 0.30 mm, 0.5 mm pitch, rows 2.55 mm apart) |
| Doubled pull-ups after the join: each SPI chip select has two 47k (R3x05 moved, R3x06 kept); each pressure-sensor I²C line has 4.7k ∥ 10k ≈ 3.2k. Both work; dropping the MCU-side R3x06 / R3407–R3408 / R3507–R3508 would simplify | 9 | Captured (D-21Nov.15): the seven MCU-side resistors removed |
| Capture assertions 1–22 ([11 Verification](../../docs/architecture/11-verification.md)) | 8 | Done in `tools/check_schematic_full.py` (A1–A16, A18, A19, A22; A13, the arm connector families, added at step 9); A17 (J101 / J102 variants) can't be checked in a KiCad 9 schematic, so it's an assembly rule; A20 / A21 are Churro's |
| Revised pin maps and [firmware interface](../../docs/firmware-interface.md) | 8 | Done: as-captured maps in libraries/inputs, linked from the firmware interface |
| J102 position against Ériú's bay answer (Jay): the Samtec pair only mates end to end | Before layout | Open |
| B-39 series-part values (R516 / F501 bus 1, R517 / F502 bus 2; 0R until then) | Bench | Open |
| CAN connector series (D-18Nov.4 left it open): drawn as Gecko-SL G125-MS10605M2P, 2×3 vertical SMT with screw-lok fixings; pins 1–3 H / L / reference, 4–6 spare. The latched through-hole G125-MV10605L1 is the alternative. Fajita's end of J501 has to match | Before layout | Decided D-21Nov.13: Gecko-SL stays |
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
