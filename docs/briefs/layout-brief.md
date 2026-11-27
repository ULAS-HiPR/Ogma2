# Routing brief: Burrito and Churro (S2)

**Accepted 22 November 2026** (D-22Nov.2, D-22Nov.3). **Drafted 22 November for S2.** The layout rules both boards are built to, by
the KiCadRoutingTools hybrid (D-22Nov.1). Burrito's half is complete. Churro's half
waits for its [power review](churro-power-review.md) (D-21Nov.22), drafted alongside. Seán's nine
points come in his order.

Every line is tagged:
- **[R]**: fixed by a requirement or a decision, cited;
- **[J]**: Claude's judgement, with its reason. Seán can change any [J] at S2.

Numbers carry their source. "Read" dates are when the page was read. The scripts
behind the computed figures are in [tools/layout/phase2](../../tools/layout/phase2).

## What S2 asks Seán to accept

1. **Order the board on JLC04161H-3313, without paid impedance control.**
   - It is D-21Nov.26's 0.1 mm-prepreg stackup, named. JLC's order form charges it
     no stackup fee, like 7628 and 1080. 3313A and 7628G each added a $50.45
     stackup fee (quote form, 22 Nov; the other variants weren't tried).
   - Economic PCBA takes "Standard stack-up only, special stack-up is not
     supported" ([assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities),
     read 22 Nov). The fee-free stackups look like the standard ones. The
     impedance calculator labels 7628 "Standard", 3313A and most suffixed ones
     "Special", and 3313 neither. So 3313 should be allowed. *Not proven:* the
     form shows the PCBA tier only after a Gerber upload. Checked at upload
     (Seán's step).
   - JLC's tested impedance control is a paid option ($33.08 on the form for
     5 boards at its default size, and it drops the fastest build). Both RF lines
     are under 20 mm, and the USB pair runs at full speed (12 Mbit/s). So the
     widths come from JLC's calculator for this stackup, and the test isn't
     bought *[J]*. That amends D-21Nov.26's "impedance control".
2. **Keep Economic PCBA** (D-21Nov.27). D4501 still needs its swap: a decision
   row and a capture step before S3.
3. **The floorplan in section 3**, with a pyro corridor on L4 along one edge and
   the magnetometer on the far side.
4. **The net classes and widths in section 5.** They are sized from IPC-2152,
   with a 0.5 mm clearance around every fire net.
5. **The 0.3 mm via.** It is JLC's free option, plugged by default. A smaller
   via costs extra (section 8). Thermal vias go in exposed pads only where the
   part's datasheet asks.
6. **ENIG surface finish** *[J]*: flat pads for the LGA sensors and the 0.5 mm
   LQFPs. It is a paid option, his call at order.

## Burrito

### 1. Outline, holes, keep-outs and fixed connectors

**Coordinates** (used throughout): seen from the top, forward end up.
- x runs across, from 0 to 80 mm.
- y runs along, from 0 at the forward edge to 230 at the aft edge.

| Item | Rule | Tag |
| --- | --- | --- |
| Outline | 80 × 160 mm, 1.6 mm thick. The y values in this brief and in `spec.py` are written for the 230 mm reference board; `build.py` maps them to 160 | [R] B-35, D-22Nov.21 |
| Holes | Eight Ø3.2 mm unplated holes at x = 4 and 76, y = 6, 79, 152 and 225. No copper within Ø7 mm on any layer, no part within Ø8 mm | [R] D-21Nov.23 |
| J102 | Origin at (40, 230), 0°, top side: where it sits on the 8 September draft, read from that file. Its mating face overhangs the aft edge; its courtyard spans x 13.2–66.9 | [R] IR-3, D-21Nov.24 |
| Other connectors | On an edge, facing out. The right-angle ones open past their edge. The vertical ones stand at the edge, with latch and cable toward it | [R] D-21Nov.24 |
| Forward edge (y = 0) | J6601 centred, opening forward. J4601 (LoRa SMA) in the left corner, J4501 (GNSS SMA) in the right, each inboard of its hole | [R] D-21Nov.24, D-21Nov.25. Left and right *[J]* |
| Aft third, left edge | J6101 (recovery arm), J6102 (staging arm), J101 (2S, standalone variant), between y ≈ 160 and 212 | [R] aft third. Left *[J]*, beside the energy tap and fuses |
| Aft third, right edge | J501 (CAN bus 1, Fajita) and J103 (master-enable loop) | [R] aft third. Right *[J]*, away from the pyro feed |
| J4401 (USB-C) | Left edge, about y = 120, opening left: reachable with the bay open | [R] D-21Nov.4. Place *[J]* |
| J502 (CAN bus 2, Salsa) | Right edge, about y = 110 | [R] "where the floorplan suits". Place *[J]* |
| Tag-Connect pads J2301, J4201 | Within 10 mm of an edge beside their MCU, and near a hole, so the board is supported while a plug is pressed on | *[J]* |
| Fiducials | Three, 1 mm copper, 2 mm mask opening, at least 3.35 mm from the edge, on the edges ([JLC](https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order), updated 9 Sep 2026) | Economic doesn't need them. *[J]*: they cost only area and keep Standard open |
| Plug heights | Within the ≈33 mm each side of the board | [R] D-21Nov.6 |

*J101's footprint was drawn in capture step 15* from Molex's drawing SD-105311-100 (D-22Nov.13).
It sits on the left edge with its latch to the edge; the reserved block is gone.

### 2. Stackup, layer use and return paths

**Stackup** (JLC impedance calculator and order form, read 22 Nov) [R] D-21Nov.26:

| Layer | Material | Thickness |
| --- | --- | --- |
| L1 | Copper, 1 oz | 0.035 mm |
| | Prepreg 3313 × 1 | 0.0994 mm |
| L2 | Copper, 0.5 oz | 0.0152 mm |
| | Core | 1.265 mm |
| L3 | Copper, 0.5 oz | 0.0152 mm |
| | Prepreg 3313 × 1 | 0.0994 mm |
| L4 | Copper, 1 oz | 0.035 mm |

Finished 1.56 mm ± 10%. Dk of the 0.1 mm prepreg: 4.05
([JLC stackups](https://jlcpcb.com/quote/pcbOrderFaq/PCB%20Stackup), read 21 Nov).

**Controlled widths** (JLC impedance calculator, JLC04161H-3313, L1 over L2, read
22 Nov):

| Line | Width | Gap | Closed-form check (IPC-2141, no mask) |
| --- | --- | --- | --- |
| 50 Ω microstrip | 0.151 mm (5.94 mil) | — | 49.9 Ω |
| 50 Ω coplanar, grounded | 0.142 mm (5.59 mil) | 0.203 mm to ground | Not checked |
| 90 Ω pair | 0.154 mm (6.05 mil) | 0.203 mm between | 92.0 Ω |

- `impedance_check.py` reruns the checks.
- For comparison, JLC04161H-7628 needs 0.359, 0.306 and 0.291 mm.
- Seeed's Wio-LR2021 guide shows 0.190 mm on "0.1 mm FR4"
  ([Seeed](https://wiki.seeedstudio.com/wio_lr2021_pcb_design_guide/), updated
  3 Jun 2026). Its material differs. The fab's calculator for the stackup we order wins.

**Layer use** [R] D-21Nov.26:
- L1: every part, RF, fast and critical signals.
- L2: unbroken GND. No track, no split. The checker fails any L2 track.
- L3: power pours, GND fill between them, slow signals.
- L4: slow signals, the pyro corridor (section 4), GND fill.

**Return paths** *[J]* (the core is 1.27 mm thick, so L2 and L3 barely couple):
- **L1 signals** return on L2, 0.1 mm below. Everything fast stays on L1: QSPI,
  SPI clocks, crystals, USB and RF.
- **L4 signals** return on L3, also 0.1 mm away. So a fast or long L4 track
  runs over L3 GND fill, never over a power pour and never across a pour edge.
  The checker flags any L4 track crossing an L3 pour boundary.
- **A layer change** puts a GND via within 1 mm of the signal via (an L1–L4
  change), so the return can follow.
- **Power** flows on L3 pours and returns on L2. Each pour's decoupling ties it
  to GND at its loads.
- **Pyro pulses** (≈2 A) run out on the L4 corridor, over L3 GND fill. They
  return through the GND layers, with J102's GND pins as the battery return.

### 3. Floorplan

Four bands, forward to aft *[J]*. Parts and areas come from `inventory.py` on the
step-9 netlist:
- 569 parts with footprints, plus J101.
- 7,186 mm² of courtyard bounding boxes: 39% of the top side.
  D-21Nov.27's 36% was counted from the courtyard outlines.

| Band | y (mm) | Holds | Area (mm²) | Why here |
| --- | --- | --- | --- | --- |
| 1 RF and fire | 0–42 | LoRa block, left corner. GNSS block, right corner. J6601 centred, with the three output channels and their diagnostics behind it | 877 RF, 781 outputs | D-21Nov.24/25 fix the forward edge. The fire nets stay a few mm long next to J6601 (B-02's intent). Both RF lines stay under 20 mm. |
| 2 Flight | 42–100 | U201 near the centre line (about 40, 68). Its crystals and support. NOR flash and switches on the left. IMUs and high-g as a cluster right of U201. Barometers right. Magnetometer at the right edge, about (68, 52) | 630 MCU, 731 sensors | Short SPI to the sensors. Far from the regulators' heat and from J102's 6 A. The magnetometer is ≥ 50 mm from the pyro corridor, ≥ 150 mm from J102 and ≥ 60 mm from the buzzer |
| 3 Comms | 100–150 | U401 near the centre line. USB-C and its protection, left edge. CAN bus 2 and J502, right edge. UART boundary, indicators. Buzzer at the right edge | 872 comms, ≈ 290 CAN2 | USB ≥ 10 mm from RF (Seeed's rule) and next to the comms MCU. The radios' control lines run forward to band 1 |
| 4 Power and harness | 150–230 | J102. Source path (Q101, U101, R7101 with U7101) just forward of it. Then the mux, bootstrap, buck, held core with C1403, the three LDOs and the branch limiters. Arms and fuses, left edge. CAN bus 1 with J501 and J103, right edge. Churro-facing monitors (`07`, `08`, `44`) | 2,446 power (857 of it J102), 277 arms, ≈ 290 CAN1 | Power enters here (IR-3). The heat and the 6 A stay aft, away from the sensors and the GNSS input. The arm plugs face the panel harness |

**Placement inside a band** *[J]*:
- Anchors first:
  - the MCUs;
  - the modules, with their RF line from pad to SMA pin drawn first;
  - U1301 with its input loop;
  - U101 and Q101;
  - the three TPS1H100 with their low sides;
  - the crystals at their MCU pins.
- Then each support part goes to the pin it serves, as in phase 1.
- **Sensors** sit ≥ 10 mm from any hole and from the board edges (flexure), and
  ≥ 15 mm from the regulators and LDOs (heat).
- **IMUs** share one orientation, axes square to the board edges.
- **Heavy and tall parts** sit near a hole row: C1403, C1007, BZ9001, the vertical
  plugs.
- **Test points** (D-22Nov.9):
  - The four black GND loops claim edge spots first, spread fore to aft.
  - The 18 yellow loops and 25 pads each aim for their net's route, the spanning tree of its other pads,
    upright (stage B2 step 5). The pads on the six pyro ADC nodes and `BAT_BLOCK_GATE` go in with their
    circuit, as soon as its parts are down, stub 10 mm at most; the rest come last, 20 mm at most.
  - They're numbered TP1 to TP47 fore to aft once the length is fixed.
- **Silkscreen** (D-22Nov.9):
  - Refs go on silk only for test points, connectors, ICs and LEDs.
  - Each of those refs counts as courtyard while placing, so no part covers it.
  - Every other ref goes on F.Fab (the assembly drawing). Polarity marks stay on silk.
  - A pass after placement moves any visible ref to the nearest spot clear of pads, other parts' courtyards, other silk and the edge.
  - The bottom (D-22Nov.12) carries the name, subtitle, a burrito rocket, two lines of text, the team's logo, the TP-to-net legend in one column and the board's parts, with waves over the rest. The top carries the name and version, small.
- **Mounting holes** (D-22Nov.11): plated, with an exposed GND ring and stitching vias. No track or via within Ø8 mm; the sled mounts Burrito on insulating standoffs or washers.

*Unknown until S3:* whether band 3's ≈ 1,160 mm² and band 1's ≈ 1,660 mm² fit
their bands with routing room. The S3 metrics (density per band, wire length)
test it. The bands may shift by a few mm; the order doesn't change.

### 3a. Placement rules from the datasheets (read 22 Nov)

| Parts | Rule | Source |
| --- | --- | --- |
| All six LGA sensors (U3104, U3204, U3304, U3403, U3503, U3701) | No track or via on L1 under the package: a keep-out. Traces to the pads symmetric; GND reaches the pads by trace, not by pour. ≥ 2 mm from screw holes (ours ≥ 10 mm), between fasteners, ≥ 10 mm from where a force lands (mated plugs, the Tag-Connect pads), away from heat sources | ST TN0018 Rev 8 (Mar 2025), §3.1–3.11, §6.1–6.5 |
| U3701 (MMC5983MA) | No current-carrying track under it or on the far side of the board; nothing magnetic nearby; 10 µF at CAP (pin 10), close | MEMSIC MMC5983MA Rev. A, pp. 11–12 |
| U3304 (ADXL375) | Close to a hard mounting point: within ≈ 15 mm of a hole *[J]*, still ≥ 2 mm per ST. 1 µF at VS and 0.1 µF at VDD I/O, close | ADI ADXL375 Rev. B, p. 26 |
| U3403 (BMP390) | 100 nF at each supply; ≥ 0.1 mm clear above the lid; out of strong light (the bay is dark) | Bosch BST-BMP390-DS002 Rev 1.7, pp. 47–52 |
| Y201, Y401 (16 MHz), Y202 (32.768 kHz) | As close to the MCU pins as possible; GND under the oscillator tied to the nearest MCU VSS; a GND guard ring round crystal and load capacitors; load capacitors symmetric; fast signals routed away. AN2867 also recommends conformal coating over the oscillator | ST AN2867 Rev 25 (Oct 2026), §7.1–7.2 |
| J2301, J4201 (TC2030-NL) | The footprint's 7 × 4 mm courtyard stays clear (Tag-Connect's keep-out, in KiCad's footprint), with its three Ø0.99 mm locating holes | KiCad 9.0.7 `Tag-Connect_TC2030-IDC-NL` |

*Not read:* TDK's own layout section for the ICM-42688-P (its URL returned an index page) and TE's MS5607 data sheet (the site refuses fetches). ST's LGA rules above cover both packages.

### 4. Power

**The paths** (netlist, step 9):
- **Source:** J102.1 / J101.1 → `VBAT_BURRITO_INPUT` → Q101 (CSD18540, the blocking
  FET) → `ENERGY_TAP` → U101 (TPS26630) → `VBAT_SHUNT_IN` → R7101 (5 mΩ) →
  `VBAT_PROTECTED` → U1101 (TPS2121 mux) → `LOGIC_SELECTED` → U1301 (TPSM63603).
- **Logic rails:** U1301 → `4V_PRE`. Then U1401 (LM73100) → `CORE_HELD_4V` →
  U1701 → `FLIGHT_3V3`. And U1501 / U1601 → the comms and optional LDOs.
- **Pyro:** `ENERGY_TAP` → F6101 / F6102 → J6101 / J6102 → the arm switch →
  `RECOVERY_ARMED_VBAT` / `STAGING_ARMED_VBAT` → 0 Ω links → `PYROx_ENERGY` →
  TPS1H100 → `OUTPUTx_HIGH` → J6601. The return is `OUTPUTx_LOW` → CSD17318 →
  GND.

**Currents:**
- The source path has a 6 A aggregate ceiling, and each Samtec ground path must
  carry the full 6 A
  ([power contract](../../interfaces/power-contract.md)) [R].
- Each pyro channel is ≈ 2.0 A, limited by its TPS1H100 (B-01), and F6101 /
  F6102 are 4 A fuses [R]. Firmware fires one channel at a time (B-02).
- The logic needs ≈ 1.24 A at 4.0 V at most (static bound, power appendix).
- USB is limited to 387–491 mA (D-6.5) [R].

**Block templates.** Each is coded from the part's layout section (datasheets read
21–22 Nov), then locked before the router runs (D-22Nov.1):

| Block | Template | Source |
| --- | --- | --- |
| Source path: J102 → Q101 → U101 | `VBAT_BURRITO_INPUT` and `ENERGY_TAP` as pours ≥ 4 mm wide on L1 and again on L4, joined by ≥ 12 vias. Q101's drain sits close to U101's input through the pour. 0.1 µF (C1002) at IN_SYS. R_ILIM (`BAT_ILIM`) short and away from the switching path, with its own short GND. Nothing on IMON. PowerPAD to GND with vias. J102's GND pins (2, 4) into L1, L2 and L4 copper | [TPS2663](https://www.ti.com/lit/ds/symlink/tps2663.pdf) pp. 38–40 |
| Shunt: R7101 with U7101 | Kelvin lines from the inner edges of R7101's pads, through R7102 / R7103 and C7101, as a pair to U7101. 0.1 µF bypass at the INA228 | [INA228](https://www.ti.com/lit/ds/symlink/ina228.pdf) p. 39 |
| Mux: U1101 | Short wide copper. Vias under the input and output pins. Caps close | [TPS2121](https://www.ti.com/lit/ds/symlink/tps2121.pdf) p. 33 |
| Buck: U1301 | Input caps (C1303, C1304) tight between VIN and PGND. Large VIN, VOUT and PGND copper. AGND to PGND at one point. RFBT and RFBB (R1301 and its partner) at FB. 1 µF on VCC close. SW pin left as minimal copper, nothing routed by it. Pads 27–30 soldered, with GND vias | [TPSM63603](https://www.ti.com/lit/ds/symlink/tpsm63603.pdf) p. 36 |
| Held core: U1401 with C1403 | 0.1 µF at IN, ≥ 1 µF at OUT. Copper ≥ 2× the current. Thermal vias. Quiet GND island for its set resistors, star-tied. R_IMON close | [LM73100](https://www.ti.com/lit/ds/symlink/lm73100.pdf) p. 41 |
| LDOs: U1701, U1801, U1901 | Input and output caps grounded together at the GND pin. FB divider top sensed at the output cap. CNR/SS and the lower divider return to the thermal pad. A via array in the pad. GND pin to the pad | [TPS7A91](https://www.ti.com/lit/ds/symlink/tps7a91.pdf) p. 25 |
| Output channels: U6304 / U6404 / U6504 with Q6301 / Q6401 / Q6501 | As many plugged thermal vias in the pad as fit. ≥ 85% solder coverage. As much copper on the pad as the area allows. R_CL to device GND. The schematic has no GND network, so the pad goes straight to GND. Each channel's high and low side sit beside J6601's pins | [TPS1H100-Q1](https://www.ti.com/lit/ds/symlink/tps1h100-q1.pdf) pp. 37–38 |
| CAN transceivers | Protection and filter in line, at the connector. 100 nF at VCC and VIO, ≥ 2 vias per cap. Thermal pad with vias | [TCAN3413](https://www.ti.com/lit/ds/symlink/tcan3413.pdf) p. 29 |

**The pyro corridor** *[J]*:
- The two armed rails run on L4, from the arm plugs on the left aft edge to
  band 1:
  - each ≥ 2.0 mm wide;
  - x ≈ 9–16 mm, just inside the hole keep-outs;
  - over an L3 strip of GND fill.
- **Cross-arming:** a GND strip ≥ 1 mm wide separates the two rails. A short
  between them would let the recovery arm feed staging.
- **Fire nets** stay on L1 inside band 1.

**Copper per rail** *[J]*:
- **L3 pours:** `FLIGHT_3V3` (99 pins) over bands 1–2, `COMMS_3V3` (38) over
  band 3, `4V_PRE` and `CORE_HELD_4V` in band 4.
- **The smaller branch rails** (`CAN_3V3`, `NOR_3V3`, `LORA_3V3`, `GNSS_3V3` and
  the others) are 0.4 mm tracks.
- **Under the magnetometer** there is no pour on L3: only GND fill.

**Thermal** *[J]*:
- The heat sources are U1301 (≈ 0.5 W), the three LDOs (up to ≈ 0.4 W each)
  and the TPS1H100s during a pulse.
- None needs more than its datasheet's via array and the planes.
- No thermal relief on the high-current pads. Thermal relief on the rest, so
  hand rework stays possible.

### 5. Net classes and rules

**Widths** come from the IPC-2152 baseline fit published by
[smps.us](https://smps.us/pcb-calculator.html) (read 22 Nov; `trace_width.py`).
It assumes no nearby plane, so it is conservative here. For 1 oz outer copper:

| Current | 10 °C rise | 20 °C rise |
| --- | --- | --- |
| 1 A | 0.29 mm | 0.16 mm |
| 2 A | 1.01 mm | 0.55 mm |
| 4 A | 3.54 mm | 1.87 mm |
| 6 A | 7.38 mm | 3.84 mm |

The 0.5 oz inner layers need twice these widths. Altium's IPC-2152 table is less
conservative (1 A at 10 mil, 4 A at 80 mil, 6 A at 150 mil, at 10 °C;
[Altium](https://resources.altium.com/p/pcb-trace-width-vs-current-table-high-voltage-design),
updated 27 Jun 2025).

| Class | Nets | Current | Width | Clearance | Layers |
| --- | --- | --- | --- | --- | --- |
| `SRC_6A` | `VBAT_BURRITO_INPUT`, `ENERGY_TAP` | 6 A ceiling [R] | Pours ≥ 4.0 mm on L1 and on L4 in parallel: each alone meets 20 °C *[J]* | 0.2 mm | L1, L4 |
| `PYRO_RAIL` | `RECOVERY_ARM_FEED`, `STAGING_ARM_FEED`, `RECOVERY_ARMED_VBAT`, `STAGING_ARMED_VBAT` | 4 A fuse rating [R] | ≥ 2.0 mm *[J]* | 0.5 mm to any other net *[J]* | L1 at the parts, L4 in the corridor |
| `FIRE` | `PYROx_ENERGY`, `OUTPUTx_HIGH`, `OUTPUTx_LOW`, `PYROx_GATE`, `PYROx_FIRE`, `PYROx_LS_SELECT` | ≈ 2 A pulses on the power nets [R] | ≥ 1.0 mm on the power nets, 0.15 mm on the logic ones *[J]* | 0.5 mm to any other net; channels apart, with GND between *[J]* | L1 |
| `LOGIC_FEED` | `VBAT_SHUNT_IN`, `VBAT_PROTECTED`, `LOGIC_SELECTED`, `4V_PRE`, `CORE_HELD_4V` | ≤ 1.24 A at 4.0 V | ≥ 1.0 mm, or pours *[J]* | 0.2 mm | L1, L3 |
| `RAIL_3V3` | `FLIGHT_3V3`, `COMMS_3V3`, the branch rails, `BOOT_3V3`, `USB_VBUS`, `USB_LIMITED` | Branch limits up to 588 mA; USB 491 mA [R] | ≥ 0.4 mm, or L3 pours *[J]* | 0.15 mm | Any but L2 |
| `RF50` | `GNSS_RF`, `LORA_RF_SUBG` | — | 0.151 mm, or 0.142 mm coplanar with a 0.203 mm gap | GND fill set back to the gap. Other copper ≥ 1 mm (Seeed: 3W or 1 mm) | L1 only, no via [R] D-21Nov.25 |
| `USB_DIFF` | `USB_D+`/`USB_D-` and their `_CONN` nets | 12 Mbit/s | Pair 0.154 mm, gap 0.203 mm; matched to 1 mm *[J]* | 0.2 mm | L1 only |
| `CAN_DIFF` | `CAN+`/`CAN-`, `CAN2+`/`CAN2-` | Not impedance-controlled: on-board runs are short *[J]* | Coupled pair 0.2 mm, gap 0.2 mm | 0.2 mm | L1 |
| `GND` | `GND` | Returns | L2 plane, pours, a via per pad | 0.2 mm (pours) | All |
| Default | Everything else | ≤ 50 mA | 0.15 mm | 0.15 mm | L1, L4; L3 at a cost |

**Board-wide rules** (JLC [PCB capabilities](https://jlcpcb.com/capabilities/PCB-capabilities),
read 21 Nov; ours set above them *[J]*):

| Rule | JLC minimum | Ours |
| --- | --- | --- |
| Track and space, 1 oz | 0.09 / 0.09 mm | 0.15 / 0.15 mm |
| Via | 0.15 mm hole, 0.25 mm pad | 0.3 mm hole, 0.5 mm pad for signals, with teardrops (D-23Nov.4; 0.6 mm until then). 0.6 mm pad for the power classes |
| Annular ring (PTH) | 0.15 mm (0.20 recommended) | 0.20 mm |
| Hole to track | 0.2 mm via, 0.28 mm PTH | 0.25 / 0.3 mm |
| Copper to edge | 0.2 mm | 0.3 mm. Pours 0.5 mm |
| Mask bridge | 0.10 mm | Footprint default |
| Silkscreen | 0.15 mm line, 1.0 mm text | 0.15 mm, 1.0 mm |

**Hole keep-outs** are rule areas: no copper inside Ø7, no courtyard inside Ø8 [R].

**Length:** no length matching beyond the USB pair. Nothing on Burrito is fast
enough to need it *[J]*.

### 6. Routing order

1. Outline, holes, rule areas, fiducials.
2. **RF:** both lines from pad to SMA pin, with their GND fences:
   - two staggered rows within 0.3 mm of the edge;
   - pitch ≤ 5 mm at 868/915 MHz (Seeed), 2 mm *[J]* for both;
   - ≤ 2 bends, radius ≥ 3W (Seeed);
   - D4501 in line at J4501.
3. **Power templates** (section 4), the source-path pours and the pyro corridor.
4. **Crystals** Y201, Y202, Y401: at their pins, nothing under them on L1 or L4,
   a GND guard *[J]*. AN5711 (§3.1) asks for them as close as possible; it
   defers routing to AN2867, not yet read.
5. **Pairs:** USB, then CAN at their connectors through the protection, in line.
6. **MCU supplies:**
   - VCAP: AN5711 §2.2 asks for 2.2 µF per pin when there are two;
   - VDDA;
   - 100 nF per VDD pin plus one ≥ 4.7 µF (AN5711 §7.4);
   - then NRST, BOOT0 and SWD.
7. **GND fanout:** a via per GND pad, scripted.
8. **Lock and hash** everything above.
9. **KiCadRoutingTools:**
   - L1 and L4 first; L3 at a cost; L2 never;
   - 0.1 mm grid (phase 1's memory limit);
   - one board at a time.
10. **Pours:**
    - L2 solid;
    - L3 rail pours and GND fill;
    - L1 and L4 GND fill;
    - stitching vias every 5 mm along the edges and on a 10 mm grid elsewhere
      *[J]*.
11. **Cleanup** (stubs, acute angles), DRC, the checker, re-hash of the locked
    copper.

### 7. Flight concerns

**Vibration and shock** (B-33: 50 g quasi-static, 200 g shock target; parts over
7 g staked [R]):
- D-21Nov.23's beam estimate puts the first mode near 300 Hz on eight standoffs.
- *[J]* MLCCs of 1206 and larger lie across the long axis, ≥ 5 mm from holes and
  plug footprints.
- C1403 (φ8 × 10 mm can), C1007, BZ9001, the SMAs and the vertical plugs get
  staking or adhesive whatever their mass. Their masses aren't read yet; any
  over 7 g is staked by rule.
- Nothing is supported by the Samtec mate (B-33): the y = 225 hole pair takes it.

**Thermal** (B-30: −20 to +70 °C):
- The dissipation is small and stays aft (section 4).
- The barometers sit ≥ 15 mm from any regulator.
- Barometer, IMU and MCU temperatures are logged (B-30).

**EMI between radio, switcher and sensors** *[J]*, from the sources cited:
- **Buck to GNSS:** U1301 (the only switcher) sits ≥ 150 mm from the GNSS input.
  Seeed asks for ≥ 20 mm between RF and a DC-DC inductor.
- **LoRa to GNSS:** the two feeds sit in opposite forward corners (D-21Nov.25).
  The MAX-M10S integration manual recommends a SAW filter where radios share a
  board; whether one is fitted is a schematic question for G1.
- **RF keep-clear distances:** ≥ 10 mm to USB lines and ≥ 15 mm to crystals
  (Seeed). ≥ 5 mm from the GNSS module to other RF parts (u-blox).
- **Module grounds:** GND under both modules, on L1 and L2, and no signals under
  them (u-blox integration manual, pp. 30–31; the LoRa module the same).
- **Radio decoupling:** 470 Ω series resistors on the LoRa SPI lines, at the
  module. 10 µF and 100 nF at the module's VCC_IN (Seeed).
- **Magnetometer:** no current over ≈ 100 mA within 20 mm, no L3 pour beneath,
  and the buzzer's magnet ≥ 40 mm away.
- **Pyro pulses** run in the corridor, away from the sensors. A pulse may glitch
  the magnetometer for its few ms. It isn't used to decide a deployment.

### 8. DFM and DFA for JLC

**Assembly** [R] D-21Nov.27, B-38:
- Economic PCBA, every part on top.
- Economic covers single-sided SMT and through-hole, 2–6 layers, 0.8–1.6 mm, a
  single board up to 470 × 500 mm, packages down to 0402. Rails and fiducials
  aren't needed. Castellations and SPI aren't offered
  ([assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities),
  read 22 Nov).
- **D4501** (0.6 × 0.3 mm) was below 0402. It is now Nexperia's PESD5V0F1BL in SOD882 (D-22Nov.8, capture step 10).

**Spacing:** JLC's recommended minimums between parts, measured between the
nearest pad or body edges (updated 9 Sep 2026,
[SMD spacing](https://jlcpcb.com/help/article/minimum-spacing-for-smd-components)):

| Pair | Minimum |
| --- | --- |
| 0402 to 0402 | 0.15 mm |
| 0603 or 0805 to a chip part | 0.18 mm |
| 1206 to 1206 | 0.35 mm |
| Chip to SOT | 0.2 mm |
| Chip to SOIC | 0.4 mm |
| Chip to QFP | 0.5 mm |
| Chip to QFN | 1.0 mm |
| QFN to QFN, SOIC or SOT | 1.0 mm |
| QFP to QFP | 1.25 mm |

*[J]:* the placer enforces the table. Decoupling and loop parts whose datasheet
layout puts them closer to a QFN are allowed down to touching courtyards (0.5 mm).
Each such exception is listed in the S3 report.

**Edges:** the edge clearance JLC wants without rails isn't stated. Ours: SMD
courtyards ≥ 1 mm from the edge, except the edge plugs *[J]*. JLC's DFM at upload
checks it.

**Vias** (quote form, 22 Nov, 5 boards at its default size):
- 0.3 mm with 0.4 / 0.45 mm pads is the free default, plugged.
- 0.2 mm added $17.78 and switched on a $17.20 Kelvin test. 0.15 mm added $35.56.
- Epoxy-filled and capped vias added $17.78.
- So we use 0.3 mm, plugged. Via-in-pad only for thermal arrays, where the
  datasheets ask for plugged vias.

**Silkscreen:** polarity and pin-1 marks on every polarised part. JLC reads
polarity from the silkscreen, and follows it over the CPL when they disagree
([FAQ 2](https://jlcpcb.com/help/article/pcb-assembly-faqs-part-2), updated
9 Sep 2026). References where they fit at 1.0 mm. Every reference on F.Fab.

**Files:**
- Gerbers, drill, BOM and CPL with LCSC numbers.
- Two BOMs for the source variants (D-21Nov.9).
- JLC's rotation offsets, checked in their preview at upload (Seán's step).

### 9. What must pass before sign-off

All by script, each output kept:

1. KiCad DRC: 0 errors, 0 unconnected. Each warning listed with its reason.
2. Schematic parity: 0.
3. The checker:
   - nothing in the hole keep-outs;
   - RF widths, no via on RF, its fence present;
   - every class at or above its width;
   - 0.5 mm around fire nets;
   - no L2 track, no L4 track across an L3 pour edge;
   - magnetometer keep-out;
   - every part on top;
   - fiducials;
   - JLC spacing, exceptions listed;
   - courtyards clear;
   - test points reachable;
   - the locked copper's hash unchanged.
4. Gerbers render back. Every BOM line has an LCSC number or a route. Every CPL
   line matches the board.
5. Footprint audit complete (J101, the USB-C mismatch, MMC5983MA, C1403).
6. STEP exported for Jay's fit check (EX-08).
7. Seán's visual pass, then JLC's DFM and the tier check at upload.

## Churro (after its power review)

**Fixed already:**
- 80 mm wide, 80 × 120 mm working (D-21Nov.6, D-21Nov.22, C-20).
- MCU-less (C-18).
- J301 mates J102 where it sits (IR-3).
- Held independently of the mate (C-20).
- The same pipeline, JLC rules and gates as Burrito.

**Waits for the review:**
- ACT and PROP's ≈ 15 A peaks will set the copper weight, the pours and possibly
  a 2 oz outer layer.
- The chargers.
- The J801 umbilical and its damping.
- The floorplan.

This half of the brief is written once Seán accepts the review.

## Open and unknown

| Item | Who | By |
| --- | --- | --- |
| JLC offers Economic with JLC04161H-3313 | Seán, at upload | Order |
| D4501's swap | Done 22 Nov: PESD5V0F1BL (D-22Nov.8) | — |
| J101's footprint from Molex's drawing (the rest of the audit done 22 Nov, capture step 11) | Done 22 Nov: capture step 15, from SD-105311-100 rev H | — |
| Sensor datasheets' layout notes (LSM6DSV32X, ICM-42688-P, ADXL375, BMP390, MS5607, MMC5983MA), ST's AN2867, Tag-Connect's keep-out | Claude | Before S3's placement freezes |
| Part masses for staking (B-33) | Claude | S3 |
| ENIG, impedance control, via options: the money | Seán | Order |

## Sources

- [JLC PCB capabilities](https://jlcpcb.com/capabilities/PCB-capabilities) (read 21 Nov 2026)
- [JLC assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) (read 22 Nov 2026)
- [JLC impedance calculator](https://jlcpcb.com/pcb-impedance-calculator) and [order form](https://cart.jlcpcb.com/quote) (read 22 Nov 2026)
- [JLC stackups](https://jlcpcb.com/quote/pcbOrderFaq/PCB%20Stackup) (read 21 Nov 2026)
- [JLC SMD spacing](https://jlcpcb.com/help/article/minimum-spacing-for-smd-components) (updated 9 Sep 2026)
- [JLC rails and fiducials](https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order) (updated 9 Sep 2026)
- [JLC assembly FAQ 2](https://jlcpcb.com/help/article/pcb-assembly-faqs-part-2) (updated 9 Sep 2026)
- [IPC-2152 fit, smps.us](https://smps.us/pcb-calculator.html); [Altium width table](https://resources.altium.com/p/pcb-trace-width-vs-current-table-high-voltage-design)
- [Seeed Wio-LR2021 PCB design guide](https://wiki.seeedstudio.com/wio_lr2021_pcb_design_guide/) (updated 3 Jun 2026)
- [u-blox MAX-M10S integration manual, UBX-20053088](https://cdn.sparkfun.com/assets/5/c/a/0/b/MAX-M10S_IntegrationManual_UBX-20053088.pdf)
- [ST AN5711, STM32H5 hardware development](https://www.st.com/resource/en/application_note/an5711-getting-started-with-stm32h5-mcu-hardware-development-stmicroelectronics.pdf) (Rev 5, July 2026)
- TI datasheets: [TPS2663](https://www.ti.com/lit/ds/symlink/tps2663.pdf), [TPSM63603](https://www.ti.com/lit/ds/symlink/tpsm63603.pdf), [LM73100](https://www.ti.com/lit/ds/symlink/lm73100.pdf), [TPS2121](https://www.ti.com/lit/ds/symlink/tps2121.pdf), [TPS7A91](https://www.ti.com/lit/ds/symlink/tps7a91.pdf), [TPS1H100-Q1](https://www.ti.com/lit/ds/symlink/tps1h100-q1.pdf), [INA228](https://www.ti.com/lit/ds/symlink/ina228.pdf), [TCAN3413](https://www.ti.com/lit/ds/symlink/tcan3413.pdf)
