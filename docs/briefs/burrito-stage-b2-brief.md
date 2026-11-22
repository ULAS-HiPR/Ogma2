# Burrito stage B2: settle the placement before any copper

**22 November 2026.** Claude Fable, for Opus to execute. Seán owns every decision. This stage sits
between Stop 1 and stage C of the [execution brief](burrito-execution-brief.md), and that brief's rules
all hold. It replaces the work order in [burrito-160-calls.md](burrito-160-calls.md).

## Why this stage exists

Stage C scripts copper and freezes it by pad position, so a part that moves afterwards throws its
copper away. Everything that moves parts happens here, gets measured, and stops for Seán.

## Seán's answers, 22 November (stated)

- He agreed with every call in burrito-160-calls.md.
- “Mcu pin swaps are also on the table. Anav is too busy with test stand work rn. Trust.”
- The S/N box: “Please put it on the top face”.
- Surface-mount loops: check them. “why do we have holes going the entire way through”.
- Freerouting: “Yes. Go”.
- J102 keeps -SD and he orders from Mouser. He picks quantities this week.
- Every component stays on top.
- His bet: 160 doesn't route without a re-place, 1/5.

## Measured today (observed, on board f7e9e695)

The script is `/home/claude/capture/survey.py`; step 1 turns it into a kept tool.

| What | Number |
| --- | --- |
| Test point stub: distance to the nearest pad on its net | Median 13.7 mm. 31 of 43 are over 10 mm and 11 over 20 mm |
| Worst stubs | TP19 42 mm, TP43 31 mm, TP15 30 mm, TP35 28 mm. TP43 is a pad, so the back's art isn't the only cause: test points are placed last and get what's left |
| U201, the flight MCU | 39 of 77 signal pins leave on the wrong side of the package (over 90° from their partner). Turning it gives 35 to 42. Re-ordering its pins freely would give 0 |
| U401, the comms MCU | 19 of 28 leave on the wrong side. Turned 180°: 9, which is all that re-ordering could give |
| Flash group | `NOR_IO0`, `NOR_IO1` and `NOR_IO3` (pins 58–60) run 24–26 mm to U3602, on the far side of U201 |
| Fire commands | `PYRO2_FIRE` and `PYRO3_FIRE` (pins 40 and 43) leave U201's aft side and run 29–32 mm forward |
| Comms MCU to the radios | 47–50 mm, across the flight band. SWD to J4201 is 48 mm |
| Vias the planes need | 415 surface-mount GND pads, plus 307 on the listed rails (`FLIGHT_3V3` alone has 97) |
| Left for tracks | 698 connections on 312 signal nets |
| Through-hole pads | 185: connectors 82, mounting-hole footprints 72, test loops 22, others 9 |
| Loop courtyards (KiCad's library) | Through-hole 5000 series 3.39 × 3.38 mm. Surface-mount 5015 4.39 × 2.79 mm and 5019 4.79 × 2.99 mm. The area is a wash, not the 60 mm² guessed earlier |
| C6601–C6606 | 14–20 mm from their J6601 pins |
| Routers on hand | KiCadRoutingTools at 1577fa3 (`/home/claude/krt`) and Freerouting 2.5.0 (`/home/claude/layout-lab/bin`). No download is needed. If the container was reclaimed, rebuild both from `tools/layout/phase1/README.md` |

"Wrong side" counts only pins whose nearest partner is more than 4 mm away. The re-ordering figure is a
floor that ignores what each pin can do.

## Calls (a model's; Seán decides)

1. **Placement before copper.** Stage C starts only on a placement that Stop 1b has frozen.
2. **The meter is our own pipeline in miniature:** a via at every plane pad, then KiCadRoutingTools on
   the rest (D-22Nov.1, D-22Nov.17). It answers "will our pipeline route this placement", which another
   router can't. Freerouting cross-checks the first and last runs only.
3. **U401 turns 180°.** Rotation alone gets everything there is.
4. **U201 gets pin swaps.** Rotation can't help it; re-ordering can.
5. **One possible fault (inferred; verify before acting).** `FOINSE_RETURN_EN` is on PA15. An STM32
   pulls PA15 up from reset, as JTDI, at about 40 kΩ. Against R7002's 100 kΩ pull-down that's about
   2.4 V on U7001's EN and U7002's select pins, so the "off by default" in the pin map wouldn't hold
   until firmware runs. Moving the net to a plain GPIO fixes it. `COMMS_RESET_REQUEST` on PB4 idles
   high through R4301, which agrees with PB4's pull-up, so it's fine.
6. **The 18 orange loops go surface-mount. The 4 black GND loops stay through-hole** at the edges,
   where a ground clip pulls hardest. No pins come through the back, so the back's art stops
   constraining the top, and 18 holes stop blocking L4. The orange colour code goes; the silk number
   and the back's legend still identify each one.
7. **A test point aims for its net's route, not its centre,** and the sensitive ones are placed with
   their circuit.
8. **Distance rules and checks before rigid templates.** A template is written only where a rule
   still fails. One exception: the three pyro channels are one placement, stamped three times.
9. **The floorplan stays.** The comms-to-radio bus becomes a scripted L4 corridor in stage C, not the
   router's job.
10. **The S/N box is drawn on top after placement,** like the name tag, in space that's left over.
11. **Length rule.** If the last meter run still leaves over 5% of signal nets open, build and meter
    165 and 170 mm and show all three at the stop. The 5% is a first guess.

## The work order

Each step is one commit with its numbers in the project log. A lever is kept only if the metric it
targets improves and no other gets more than 2% worse. Otherwise revert it and log the numbers.
Every kept step leaves the board building twice to the same bytes, with DRC at 0 errors.

### 0. Records

- `hardware/croi2/AGENTS.md`: J101 has its footprint (`Ogma2:105311-1102`, capture step 15).
- A new decision row: J102 keeps MPT-08-01-01-L-RA-SD, closing D-22Nov.14. Update jlc-stock,
  current-system and the stop 1 addendum.
- Add stage B2 to the execution brief's table, with a link here.
- Read Mouser Ireland's page for the Churro half, MPS-08-01-01-L-RA-SD: stock and price, in one line
  for Seán. Look only.
- The ledger lines for today's bets and decisions are already written.

### 1. Yardsticks, then a baseline on today's board

**Fast, in seconds** (`tools/layout/engine/metrics.py`, written into `build.json` and
`output/layout/metrics.md`):

- signal wire length by class;
- ratsnest crossings: each net's minimum spanning tree, GND and plane-fed rails left out;
- wrong-side pins for every IC of 16 pins or more;
- each test point's stub;
- plane pads with no legal via spot within 1.5 mm;
- a congestion map on a 2 mm grid: each net's bounding box spread over its cells, against the copper
  free on L1 and L4.

**Slow, about half an hour** (`tools/layout/meter.py`, on a scratch copy; none of its copper is kept):

1. GND zones over the whole of L2 and L3.
2. A via and a short track for each surface-mount pad on GND and on each rail with four or more loads
   (D-22Nov.15). Each pad gets its own via. List the pads that find no spot, by band.
3. KiCadRoutingTools' route step at a 0.1 mm grid, on L1 and L4, for every other net.
4. KiCad DRC. Report: nets open, by band; vias; each net's length over its Manhattan length; time;
   peak memory.

Run the baseline twice to prove it repeats. Run Freerouting on the same scratch board with its
optimiser off, and take only its completion count: it narrows tracks below JLC's limit.

Then:

- Write the `out` lines. Seán's bet and the model's first bet settle on this run.
- If the congestion map's hot cells don't sit where the router fails, delete the map.
- Say in the report what the meter ignores: rule areas, scripted critical copper, the L3 islands.

### 2. S/N box to the top

In `art.py`'s top section, after the name tag: "S/N" and a 10 × 3 mm filled box beside the tag, else
the nearest free spot, else an 8 × 3 mm box. It doesn't count as courtyard. Take `serial_box` out of
the back's art, and delete `MARK_SERIAL` from `marks.py` and the library. Report where it went.

### 3. Turn the MCUs

Build with U401 at each of four angles, then U201 at each of four (`ANCHORS`). Pick by wrong-side pins,
then signal wire length. The USB pair must leave U401 on the side facing J4401 with no via. If the
radios and USB disagree, USB wins and the radios take the corridor. Leave the sensors and the radio
modules as they are: their angles are tied to the axes mark and the RF lines.

### 4. Surface-mount loops

- Read Keystone's drawings for 5015 and 5019, and one alternative (Harwin S1751-46R; recalled,
  unread). Compare: the loop's opening against a scope hook tip and a mini-grabber, the pad, JLC stock
  (`tools/layout/phase2/jlc_find.py`), and how JLC charges for through-hole joints. Cite each.
- Pick the smallest that takes both probe tips and that JLC holds 200 or more of.
- Trial on a scratch netlist with the 18 footprints swapped: build and take the fast metrics.
- Capture step 18 only with Seán's yes (the first of the calls for Seán, below): footprint and part fields, no pin changes.
  Same commit: the checker, the manifest, jlc-stock, test-points.md, and a decision row amending
  D-22Nov.9.

### 5. Test point placement

- A test point's cost becomes its distance to the nearest ratsnest segment of its net.
- `TP43` (`BAT_BLOCK_GATE`) and the ADC nodes (`TP5`–`TP7`, `TP9`–`TP11`) go in with their circuit,
  before the general parts: stub of 10 mm or less.
- Every other test point: 20 mm or less. Report any that miss.

### 6. Distance rules

- Put sweep §5's limits in the spec as `NEAR` rows, each with its source: one 100 nF at each MCU supply
  pin; VCAP capacitors within 2 mm; crystals within 5 mm; regulator input and output capacitors within
  2 mm; C6601–C6606 within 3 mm of their J6601 pins; D4601 and D4501 on the line between connector and
  module.
- The build places these parts first and reports every miss. Fix a miss by order or region first, and
  by a rigid template only if that fails.
- Stamp pyro channels 2 and 3 from channel 1, matched by position in the sheet.

### 7. Pin swaps

1. **Verify the possible fault first (call 5 above),** against RM0481's GPIO reset values and the TPS2553's and TMUX1511's input
   thresholds. If it holds, `FOINSE_RETURN_EN` moves whatever the routing gain.
2. **Never a destination:** PA13, PA14, PA15, PB3, PB4, PC13–PC15, PH0, PH1, BOOT0, NRST, and any pin
   AN2606 says the H563's ROM bootloader drives.
3. **Tier 1, no new data:** swap nets among pins already used as GPIO, and among ADC inputs of one
   converter. Unused pins are extra GPIO slots. Keep one interrupt per EXTI line number.
4. **Tier 2, with ST's pin data (the third of the calls for Seán):** alternates of the same peripheral signal. Bring the flash
   group to one side of U201, or move U3602 to its pins, whichever leaves its tracks shorter and on
   one layer.
5. **Search:** cost is each pin's distance to its net's nearest partner, weighted as the placer weighs
   nets. Use pairwise swaps until none helps, in a fixed order, so it repeats.
6. **Trial on a scratch netlist,** re-place, measure, twice round. Go on only if U201's wrong-side
   pins fall to 25 or fewer.
7. **Class A** (GPIO, ADC, same-signal alternates): capture step 19. Same commit: both pin maps in
   `libraries/inputs`, `docs/firmware-interface.md` with a table of old and new pins for Anav, the
   checker, and a decision row quoting Seán. Expect pin changes on U201 and U401 only.
8. **Class B** (`PYROn_FIRE`, the arm sense and inhibit nets, and any change of peripheral instance):
   list them with their gain at the stop. Don't apply them.
9. **Two new checker assertions:** no off-by-default enable sits on a JTAG-pull pin; no fire or arm
   net sits on a bootloader pin. Run both against today's maps too.

### 8. Refinement pass

Swap same-footprint parts and flip two-pin parts wherever signal wire length and crossings drop.
Parts under a `NEAR` rule, fixed parts and anchors don't move, and nothing leaves its region. Fixed
order, no random numbers. Keep it only for a gain of 3% or more; otherwise delete the code.

### 9. Equalise the bands

Iterate `BAND_AREA` until the four courtyard densities agree within 0.01.

### 10. Final checks

- Two builds with the same bytes; DRC; schematic parity; ERC; the checker.
- The meter, twice, and the Freerouting cross-check.
- The length rule (call 11 above).
- test-points.md, current-system and the decisions touched.
- Renders: front, back and 3D.

### Stop 1b

Show Seán:

- the metrics table, lever by lever, with what was reverted;
- the meter's runs: baseline, final, and 165 and 170 mm if the length rule fired;
- the renders;
- the pin change table, with class B apart;
- the loop pick and its trial;
- every `NEAR` miss and test point over its limit;
- doubts, and calls in one line each.

Stage C starts on that placement once he says so.

## Not in this stage

Copper, rule areas, pours and outputs. The meter's tracks are thrown away.

## Traps

- The chroot's mounts drop when the container pauses: run `tools/layout/env.sh`. Java's `libjli.so`
  error has the same cause.
- A whole-board route takes about 3 GB and both cores. Run nothing beside it.
- A capture step regenerates the expected pins, the manifest and the PDF in the same commit.
- The pin maps change only through a decision row (hardware/croi2/AGENTS.md). Nothing is sent to Anav.

## Calls for Seán

One line each, skippable. Without an answer Opus takes the default.

1. Surface-mount loops: if the drawing, the probe fit and JLC's stock check out, may Opus make the swap
   without another stop? Default: trial only, proposed at Stop 1b.
2. Pin swaps: “Trust” is read as yes for class A without another stop; fire and arm pins wait for you.
   Default: that reading.
3. OK to clone ST's open pin data (github.com/STMicroelectronics/STM32_open_pin_data; XML, no code)?
   Default: tier 1 only.
4. Your call: after the swaps, how many of U201's 39 wrong-side pins remain, and how sure, 1–5?
5. The S/N box tells built boards apart in bring-up notes, calibration and flight records. Keep it, or
   delete it? Default: keep.

## Seán's answers to the calls, 22 November (stated)

1. Surface-mount loops without another stop: “absolutely”.
2. Pin swaps: “yes you may swap any pin you want so long as it’s justified and verified and documented”.
   This widens the class A and B split above: fire and arm pins may move too, each with its reason, a
   check against the reference manual, and a line in the pin change table.
3. ST's open pin data: “absolutely”.
4. His call on U201's remaining wrong-side pins: “no clue. Let’s rip through and see”. No bet.
5. The S/N box: “keep it. S/N is useful, put it in the free space up top, I’m seeing some in the
   bottom right corner already”.
