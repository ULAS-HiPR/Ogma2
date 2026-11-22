# Burrito, stop 1

**22 November 2026.** Claude Opus, for Seán, at the end of stages A and B of the
[execution brief](burrito-execution-brief.md). Nothing here is decided until Seán says so; the calls
are at the top.

## Calls for Seán

One line each, all skippable.

1. **Length.** The brief's rule (the shortest length whose densest band is no denser than 0.65, today's at
   180) gives **180 mm**. Every part still places at 175, 170 and 165 mm, at 0.67, 0.69 and 0.72. At 160 the
   S/N box drops out, at 155 two loops, and at 150 the left edge is full. Your call on 22 Nov was 150–170 mm
   at 3/5.
2. **J102.** Samtec makes no right-angle MPT without -SD (D-22Nov.14 can't stand as written). Keep
   MPT-08-01-01-L-RA-SD, whose holes are already on the board, and start the buy on Monday?
3. **A5 proposals.** Add an ESD part on the LoRa port (D4601) and six 1 nF C0G capacitors on the pyro
   outputs, or leave them out?
4. **Test point numbers.** After re-placing, 31 of the 47 are out of fore-to-aft order. Keep the numbers
   (the brief) or renumber once the length is picked (a capture step like step 13)?

## Stage A: parts and footprints

| Item | Result | Commit |
| --- | --- | --- |
| A1 J102 | No change. Samtec's right-angle MPT ordering code always ends in -RA-SD, and Churro's mate is MPS-08-01-01-L-RA-SD, also -SD. The part is orderable: DigiKey SAM9733-ND quotes a 10-week factory lead; RS 767-6994 is back-ordered to 4 Jan 2027. Samtec's own store wasn't checked. Samtec's drawing marks -SD "existing business only" (the sweep's reading). | – |
| A3 J103 | Molex 43650-0215, Micro-Fit 3.0 vertical, single row, 2 circuits, polarizing peg, through-hole, JLC C293740. Harwin's G125 has no 2-contact housing (6 to 50), so D-22Nov.18 stands. Molex lists 43650's mates as 43645 and 171850 only, not the dual-row 43025 that Churro's J701 (raw PROP) takes. | step 14 |
| A2 J101 | `Ogma2:105311-1102`, drawn by script from Molex SD-105311-100 rev H. The peg is on the latch side: the drawing's views and KiCad's footprint for the sister part 105309-xx02 agree. The clips have no net; the peg hole is unplated. Courtyard 7.3 × 9.9 mm, on the left edge with the latch to the edge. The 20 × 22 mm block is gone. | step 15 |
| A4 0402 | 200 of 387 0603 parts (105 R, 95 C), 522 mm² of courtyard, each with its JLC part pinned: 22 types, 15 Basic, 7 Extended. Every part and its reason: [passives-0402.md](../../hardware/croi2/passives-0402.md). The placer already had JLC's 0402 spacing. | step 16 |
| A5 | See below. The checker now asserts the three pyro gate pull-downs (A1b). | checker |

How the A4 rules were read, where the brief left room:

- the whole of the 06 sheets counts as fire path (76 parts stay);
- a capacitor's stated voltage stays a floor, so the fifteen 1 µF X7R 16 V stay: JLC's best 0402 1 µF X7R
  is 10 V;
- 0 Ω links stay: they aren't in the swap list and they carry rail current;
- the six sensor rail links (47 Ω, 22 Ω) were assumed to carry under 20 mA (≤ 19 mW).

### A5: what the sheets show

| Check | Found | Proposal |
| --- | --- | --- |
| LoRa port's static path | `LORA_RF_SUBG` joins J4601 and the Wio-LR2021 only: no ESD part, no DC path | **D4601**, Nexperia PESD5V0F1BL,315 (C45961, 54,327 stocked), at J4601 as D4501 is at J4501. Job: a path for static the antenna collects, before the module's RF pin. Test: transmit power into 50 Ω at 868 MHz with and without it. At 0.4 pF it's 458 Ω at 868 MHz, so expect under 0.1 dB. Open: whether the module has its own path (Seeed's data sheet not read). |
| GNSS antenna supply | Passive antenna; the MAX-M10S's VCC_RF is open | Nothing to limit. An active antenna would need u-blox's current-limited feed. |
| Pyro outputs | No capacitor on any `OUTPUTn_HIGH` or `OUTPUTn_LOW` | **Six 1 nF 50 V C0G, 0603** (C106246, 1.34 M stocked), each output to ground at J6601. Job: RF on the e-match leads returns at the connector, not through the switches. Test: continuity readings and fire timing unchanged on inert loads (3.9 kΩ × 1 nF = 3.9 µs). Open: the TPS1H100's off-state diagnostics with 1 nF on OUT. Checker A3 and A9 change with them. |
| USB ESD | USBLC6-2SC6 on D+, D− and VBUS at J4401; CC1 and CC2 reach only their Rd resistors | – |
| CAN TVS | ESD2CAN24 at J501 and J502 | – |
| Safe with both MCUs in reset | Every pyro switch input and low-side gate has a 100 kΩ pull-down. The checker named 8 of 11 and missed the three gate pull-downs; A1b now names them, and a netlist with R6505 left open is rejected | – |
| BOM variants | J101 and J102 are both fitted on the schematic; KiCad can't mark them exclusive | Stage D writes the two variants |

## Stage B: re-place

- **Top silk (D-22Nov.19).** Function names replace the connector refs: PYRO 1 2 3 with the pin polarity,
  CAN 1, CAN 2, RECOVERY ARM, STAGING ARM, ENABLE, 2S PACK, USB, GNSS, LORA, SWD FLIGHT, SWD COMMS. The
  LEDs read CHECKS OK, NOT READY, COMMS, POWER. There's a board-axes mark (X to the nose, Y left, Z out of
  the top) and a white S/N box. Each counts as courtyard while placing.
- **Band areas, re-measured on the 230 mm board:** 2002, 1847, 1460, 3891 mm² (were 1880, 2083, 1443,
  3846). The total barely moved (9200 against 9252 mm²): the 522 mm² the 0402s freed went to the names, the
  marks and the real J101 and J103. J101's old block wasn't counted, so what was freed there helps the
  placement but not this sum.
- **The back follows the length.** The legend's window and IF FOUND move with the aft end. No test point
  loop's pin goes under the back's fixed blocks, so the loop moves are re-derived by the build and
  `PROBE_MOVES` is empty. At 180 the parts list's head now sits level with the legend's (102.95 mm, was
  115 mm).
- **A fiducial moved:** FID3 to x = 12 mm, inboard of the left-edge connectors, which it was colliding with.

### The sweep

| Length (mm) | Unplaced parts | Unplaced marks | Density per band (1 RF and fire, 2 Flight, 3 Comms, 4 Power and harness) | Densest | JLC spacing breaches | Grown out of region | Back art |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 180 | 0 | - | 0.597 / 0.614 / 0.591 / 0.648 | **0.648** | 0 | 17 | fits |
| 175 | 0 | - | 0.611 / 0.603 / 0.619 / 0.671 | **0.671** | 0 | 21 | fits |
| 170 | 0 | - | 0.632 / 0.623 / 0.638 / 0.691 | **0.691** | 0 | 23 | fits |
| 165 | 0 | - | 0.651 / 0.637 / 0.654 / 0.718 | **0.718** | 0 | 25 | fits |
| 160 | 0 | MK2 | 0.674 / 0.688 / 0.623 / 0.735 | **0.735** | 0 | 34 | fits |
| 155 | 2: TP19, TP39 | MK2 | 0.691 / 0.662 / 0.682 / 0.758 | **0.758** | 0 | 39 | fits |
| 150 | build stopped: RuntimeError: left edge full: J101 would end at 160.0 mm on a 150 mm board | | | | | |
| 145 | build stopped: RuntimeError: left edge full: J101 would end at 155.0 mm on a 145 mm board | | | | | |
| 140 | build stopped: RuntimeError: left edge full: J101 would end at 150.0 mm on a 140 mm board | | | | | |

From `tools/layout/sweep.py` ([table](../../hardware/croi2/output/layout/length-sweep.md)). MK2 is the S/N box.

The back keeps every block at every length that builds, down to 155 mm (renders at 180, 170 and 165 mm).
Below 165 mm the board starts losing what it carries: at 160 the S/N box, at 155 two loops. At 150 mm and
under, the left edge can't hold its six connectors and the holes.

## Checks run

- ERC after each step: the 3 recorded exclusions, nothing new.
- Schematic checker: 357 checks pass; no part without a footprint.
- Board at 180 mm (the repository's): two builds give the same bytes; DRC 0 errors, 2 warnings (J6601's silk
  at the forward edge, accepted before); schematic parity clean; 499 connections unrouted (no copper yet).
- Renders: top and 3D at 180 mm, the back at 180, 170 and 165 mm.

## Doubts

- J103 against J701's plug: Molex's mating list only. Nobody has tried a 43025 plug in a 43650 header.
- J101's peg side: two sources agree. The first part to arrive settles it, laid on a footprint print.
- J103's model height (9.9 mm) is an unlabelled JLC figure.
- The 0.65 rule is a proxy for routing room; nothing is routed until S4/S5.
- Thirteen silk refs at 180 found no clear spot and kept their default places. DRC shows no silk overlap.
- Seven new Extended part types, each with JLC's loading fee.
- The axes mark is the board's frame, not each chip's.

## After stop 1, 22 November

Seán's answers:

1. **Length:** “Let’s try get 80x160”. Done: [D-22Nov.21](../../decisions.md). Every part and all 47
   test points place; the densest band is 0.735. The S/N box moved to the back, under the parts list;
   the rocket keeps its size.
2. **J102:** he had an agent look for earlier stock. Mouser Ireland holds 706 of
   MPT-08-01-01-L-RA-SD and Arrow 32 in the Netherlands (22 Nov,
   [jlc-stock.md](../../hardware/croi2/jlc-stock.md)). Whether J102 keeps -SD is still his call.
   Later the same day: “Yes keep it and we’ll order from mouser.” (D-22Nov.22.)
3. **A5:** “Yes absolutely add the esd protect and the 1nf caps.” Capture step 17 (D-22Nov.20).
4. **Test point numbers:** kept.

At 160 mm, TP19 sits at the left edge, 43 mm from its circuit, and the loops sit further from what they
probe than at 180.

Correction: the checks above say 499 connections are unrouted. That is where DRC's report stops; the
netlist has about 1,376 connections, none routed.
