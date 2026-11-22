# Burrito stage C step 3: the MCU fanout, stopped at kill line 1

**22 November 2026.** Step 3 of the [stage C and D handoff](burrito-stage-cd-handoff.md), run on Seán's go
(“Go. I believe in you. Do your best”). Kill line 1 was hit, so this is a stop report, not Stop 2. Tags: [O]
measured today, [M] my reasoning. Every count is ordinary nets (Default class, 273) left open by the router at full
effort on six layers, L1, L3 and L6, via in pad: the layer test's 26 is the same measure.

## In one paragraph

Fanning every MCU signal pin inward to a via under the body, step 3 as written, left **34** nets open against **17**
for the same board without it [O]. That's kill line 1 (26), so the step stopped there. The handoff's premise doesn't
survive a correct meter either. About nine of the layer test's 26 were the meter's own doing: it told the router
fire logic keeps 0.5 mm everywhere, so the pins beside U201's fire-logic pins couldn't leave their pads, though the
waiver (D-22Nov.26) makes that 0.2 mm inside U201's courtyard. With the waiver modelled exactly, the board as it
stands leaves 17 [O]. Moving only the plane pins' vias under the body leaves 19 [O], no better. Nothing of step 3
is on the board; the code is kept, switched off, for Seán's call.

## The runs

Board 9d89841f is step 1's: six layers, no scripted copper (step 2 added only a rule area). The trial boards add
step 3's copper. "0.2 everywhere" tells the router fire logic keeps 0.2 mm on the whole board, too little outside
U201: those runs' DRC errors are fire-rule violations. "Waiver" gives U201's fire-logic pads, and their escapes
under the body, 0.2 mm, and keeps 0.5 mm on all other fire-logic copper: the board's real rule.

| Run | Board | Fire logic | Nets open | Of them at U201 / U401 / elsewhere | DRC errors | Router |
| --- | --- | --- | --- | --- | --- | --- |
| r10 (layer test) | 7451d7d4, six-layer copy | 0.5 everywhere | 26 | 17 / 6 / 3 | 4 | 7 min |
| c1 | 9d89841f | 0.2 everywhere | 19 | 9 / 5 / 5 | 50 | 8 min |
| c2 | every MCU pin inward | 0.2 everywhere | **34** | 28 / 1 / 5 | 52 | 10 min |
| c3 | plane and fire-logic pins inward | 0.2 everywhere | 15 | 11 / 2 / 2 | 24 | 7 min |
| c6 | 9d89841f | waiver | **17** | 12 / 2 / 3 | 4 | 6 min |
| c7 | plane and fire-logic pins inward | waiver | 19 | 13 / 3 / 3 | 4 | 8 min |
| c8 | every MCU pin inward | waiver | **34** | 27 / 1 / 6 | 4 | 11 min |
| c9 | 9d89841f, GND at 0.15 mm for the router | waiver | 17 | 10 / 5 / 2 | 116 | 5 min |

The 4 DRC errors in every waiver run are the meter's stand-in plane vias inside the two Tag-Connect keep-outs; c9's
other 112 are the GND tracks it was allowed to bring 0.15 mm close, against the board's 0.2 mm.

## Why the signal fanout lost

- The router crosses under U201's body a lot. Without the fanout it ran 216 mm of track there on L1, 180 mm on L3
  and 157 mm on L6; with the fanout, 54, 66 and 84 mm [O] (fire logic at 0.2 mm everywhere, c1 against c2).
  Through vias block every layer, and the stubs fill L1.
- The router took 35 of the 89 inward signal vias onto L3 or L6 and left the other pins by L1 as before [O]. With
  three router layers its default costs L1 at 1 and L3 and L6 at 3, so an inward via is the dearer start [M].
- A pin whose net keeps 0.2 mm (GND, fire logic) can't have an inward via while its neighbours have theirs at
  0.5 mm pitch: 0.175 mm is left. So 12 of U201's signal pins had to leave outward anyway [O].

## What the code does now

`engine/copper.py` (`mcu_fanout`), switched off by `MCU_FANOUT = {}` in the spec:
- each pin to a via under the body on a short L1 stub in its own lane, two staggered rows 0.5 mm apart, signal vias
  on the router's 0.1 mm grid;
- a GND or fire-logic pin keeps 0.2 mm, so its neighbours leave outward; a supply pin beside it takes a dogleg to
  a via in the next free lane;
- `MCU_FANOUT_SIGNALS = False` leaves the signal pins to the router (c3 and c7).

The meter gains `--waive-fire-logic` (the waiver, modelled as above), `--net-clearance NET=MM` and `--krt-args`
(stage D's knobs), and its plane fanout skips pads that scripted copper already serves.

## Calls for Seán

1. **Step 3.** Recommended: leave it off and let stage D's decoupling fanout serve the MCUs' plane pins as the
   meter does now. Moving them under the body cost two nets (17 → 19); stage D's jitter check will say whether
   that's noise. It's no better electrically than a via at each pin [M]. Alternative: the plane pins under the body
   (c7). 4/5.
2. **L5 (amends D-22Nov.29).** P1's islands can't each sit under the pads they feed: FLIGHT_3V3 has 98 pads across
   the whole board, mixed in with COMMS_3V3's round U401 and BOOT_3V3's round the power stage [O]. Quick meter,
   every class, via in pad, on 9d89841f [O]:
   - every rail a plane: 75 nets open, but not buildable as compact islands;
   - **A, recommended:** L5 is FLIGHT_3V3 fill with islands for COMMS_3V3 (round U401), CAN_3V3 (at its two
     transceivers) and LORA_3V3 (the radio corner), and GND under the armed-rail corridor; BOOT_3V3 as tracks: 83;
   - **B:** FLIGHT_3V3 the only plane, the other four rails as tracks: 90.

   A's downside: L6 references 3V3, not GND, over most of the board, so fast nets stay on L1 and L3. The island
   rule stands. 3/5; stage D's pass on the real outlines settles it.
3. **FLIGHT_HSE_IN.** It can't reach Y201 on L1. Y201's input pad is on its far side; U201's LSE pins leave across
   the way round, and the way between Y201's pads is 0.5 mm, where GND's 0.2 mm leaves no room for a 0.15 mm
   track. Recommended: two vias and about 3 mm on L3, between the GND planes; at 16 MHz two vias cost nothing that
   matters [M]. Alternative: GND at 0.15 mm except pours. The layout brief's table gives GND “0.2 mm (pours)”; the
   spec applies it to every GND pad, track and via. That loosens a rule, and it gains the router nothing
   elsewhere: c9 left 17, as c6.
4. **USB and CAN pairs on L1 only (the layout brief, [J]).** Each pair has to cross itself: on the USB-C
   connector D+ and D− interleave across its two rows, U401's USB pins come in the opposite order to R4405 and
   R4406, and each CAN transceiver's H and L come in the opposite order to its connector's [O]. Recommended: one
   via pair at each crossing, on L3 between the GND planes. Both run at 12 Mbit/s or less.
