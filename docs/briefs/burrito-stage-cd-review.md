# Burrito stages C and D: review of the 23 November plan, and the plan returned

**23 November 2026.** Written by Claude Fable at Seán's ask: “fable please review this plan and return your own.”
It reviews [Opus's plan](burrito-stage-cd-plan.md) and returns one. Where the two differ, neither stands until
Seán says. The [handoff](burrito-stage-cd-handoff.md)'s stop list and kill line 2 stand. Tags: [O] measured,
[D] decided, [M] my reasoning, to check before it's built on.

## Verdict

The measurements hold and the meter can now be trusted. I agree with step 3 off, 0.5 mm signal vias, two vias for
FLIGHT_HSE_IN, via pairs for USB and CAN, pyro before power, and L5 as one FLIGHT_3V3 plane. The plan misses one
defect and draws copper in the wrong order for it: the MCUs' capacitors aren't at their pins, and fixing that
moves parts, so it comes before any copper.

My own handoff was wrong twice. Its premise was that the plane fanout blocked the MCU escape: moving it changed
nothing (17 against 19). And it assumed each supply pin had its capacitor beside it. The kill line caught the first.

## What the plan misses

1. **The MCUs' capacitors aren't at their pins [O].** Nearest capacitor on the same net, pad centre to pad centre:

   | Pin | U201 | U401 |
   | --- | --- | --- |
   | VCAP | pin 48: 2.0 mm; **pin 98: 19.3 mm** | pin 30: 2.1 mm; **pin 62: 13.8 mm** |
   | VDD | pins 73, 75, 50: 2.3 to 3.8 mm; pin 28: 5.9; pin 11: 6.8; **pin 100: 13.6 mm** | pins 19, 1, 32: 4.2 to 5.6 mm; pin 64: 7.2; **pin 48: 12.4 mm** |
   | VDDA | pins 21, 22: 7.2 and 6.7 mm | **pin 13: 13.2 mm** |

   - The rule is one 100 nF per supply pin, on its side, within 3 mm, and VCAP capacitors within 2 mm (the sweep,
     section 5). The build reports no misses [O]: its check passes if the capacitors are near the part, not near
     each pin [M].
   - VCAP and VDDA are ordinary nets today, so the router would join pin 98 to its capacitor with 19 mm of
     0.15 mm track [O, class; M, consequence]. ST asks for a capacitor at each VCAP pin [M, cite before moving].
   - With L5 as one FLIGHT_3V3 plane, U401's supply arrives by track. That is sound only with each capacitor at
     its pin.
2. **The 9 is a floor, on a board about to change.** Three placement changes lie ahead (the capacitors, U4606,
   the pyro stamp) and each re-rolls the router: the 9 nets left open with 0.5 mm vias share one net with the
   baseline's 17 [O]. None of the hard copper is on the board. Where the router stood in for it, in the quick runs
   of every class, it left open both 6 A nets, 6 of 9 fire-logic nets, 2 of 4 armed rails and 2 of 4 USB nets [O].
   So nothing yet measures the board under its real load.
3. **A difference of two is a re-roll, not an effect.** Two builds of the same placement left 26 and 23 [O]. Equal
   layer costs (16), the 0.05 mm grid (18) and rip-up 5 (19) sit inside that. Only the via result clears it.
4. **Dense vias cost more than the count shows.** Each is a hole of 0.8 to 0.9 mm in L2, L4 and L5 [M]. A field
   of them can cut a plane into strips, and L6's reference with it.
5. **RF.** The trial's fence put 2 vias on the GNSS line's 8.5 mm [O]; D-22Nov.16 asks for 2 mm or less. The
   0.142 mm coplanar width is marked “Not checked” in the layout brief [O].

## Calls

1. **Capacitors to their pins on both MCUs, before any copper.** One 100 nF at each VDD pin, a 2.2 µF at each
   VCAP pin, VDDA's pair at its pin; crystals nudged where they're in the way. VCAP and VDDA are drawn by script at
   rail width. The build's check measures each pin. Why: the rule already says so, and decoupling is the one thing
   a router can't repair. Parts move more than 1 mm: **needs Seán's yes.** 5/5 on VCAP and VDDA, 4/5 on VDD.
2. **Step 3 stays off.** With the capacitors at the pins, the decoupling fanout is what D-22Nov.17 meant: pin to
   its capacitor on L1, the plane vias in the capacitor's pads. 4/5.
3. **Signal vias 0.5 mm with a 0.3 mm hole,** set as the Default class's via in the spec, with teardrops. It
   rewrites the layout brief's via row (0.6 mm), so it wants **Seán's nod.** Not smaller: 0.45 mm is free at JLC
   but leaves a 0.075 mm ring. 4/5.
4. **The other knobs are seeds, not settings.** Stage D runs four to six harmless variants of the Default pass and
   keeps the best valid one. 4/5.
5. **L5: one FLIGHT_3V3 plane, GND under the armed-rail corridor, the other four rails as tracks** (Opus's call
   4). Why: L5's job is to be L6's unbroken reference, and islands spend that for five to seven quick-meter nets.
   GND stays under the corridor so an armed rail's nearest copper, 0.1 mm away, is never a logic rail. Conditional
   on call 1 at U401. Amends D-22Nov.29: **needs Seán's yes.** 4/5.
6. **FLIGHT_HSE_IN by two vias; USB and both CAN pairs by one via pair each, on L3.** As Opus. 4/5 and 5/5.
7. **U4606 turns so its RF pin faces J4601.** Trial 180° as well as 90° and take the shorter line with the fewer
   parts displaced. Parts move more than 1 mm: **needs Seán's yes.** 4/5 that it must turn.
8. **RF lines:** check the coplanar width in JLC's calculator before drawing, not before ordering. Fence coverage
   is an exit check: no gap over 2 mm on either side, outside a part's own footprint.
9. **Budget the hard copper before drawing it.** Lay it out as keep-out rectangles (the corridor on L6, the 6 A
   pours on L1, the fire-logic lanes on L3, the RF keeps, each channel's fire copper), let the router draw the four
   rails, then run the Default class once at full effort. **Gate: above 25 open, stop and bring the lever to
   Seán.** The levers left are 0.127 mm track and space for signals [M: free at JLC, to confirm; it loosens the
   0.15 mm floor] and pin swaps at U201 (Seán allowed those on 22 November, if justified, verified and
   documented). Why: it's the floor plan the drawing needs anyway, and it's the first number for the board under
   load.
10. **Stage D in four moves:** the rails pass frozen; the Default pass by seeds, best one frozen; the router again
    on the open nets alone; then the rungs. Kill line 2 stands.
11. **Planes are checked after fill:** no island, no supply pin fed through a neck narrower than the rail width
    (0.4 mm), and KiCad's own count of unconnected items at zero. That count, not the meter's, is Stop 3's.
12. **Small copper last, not first.** Crystals, USB, CAN and the GNSS line sit beside parts that calls 1 and 7
    move. Opus's plan draws them first; they'd be drawn twice.

## Order of work

0. The build's near check measures each supply pin. *Exit:* it reports today's misses.
1. **Placement, batch 1,** on Seán's yes: capacitors to their pins, U4606 turned. One commit each, DRC clean, two
   builds the same bytes. Then the baseline again (0.5 mm vias), logged.
2. **Placement, batch 2:** channel 1's block, with a picture and its current-path table sent to Seán; then the
   stamp [D: D-22Nov.27]. Baseline again.
3. **The budget run** (call 9), with its gate.
4. **Copper, biggest first:** pyro (fire paths, then fire logic by script from U201); power (L2, L4 and L5 fills,
   the corridor, the 6 A pours, the feeds, pin-to-capacitor fanout, VCAP and VDDA); then the small copper. After
   each: two builds the same bytes, DRC, the rule check, the router once, the count logged.
5. **Stop 2 report.** Not a wait.
6. **Stage D** (call 10).
7. **Finish:** teardrops, stitching, fill, the plane check, DRC, outputs for six layers, Stop 3.

While a router runs, the work that needs none: the six-layer outputs and Stop 2's scaffolding.

## Needs Seán

**Answered, 23 November:** “Yes to 1, 5, 7, I nod at 3 indicating yes.” Calls 1, 5, 7 and 3 are D-23Nov.1 to
D-23Nov.4. The order of work starts at step 0.

- Yes or no: the capacitors to their pins (call 1); L5 (call 5); U4606's turn (call 7).
- A nod: 0.5 mm signal vias as the board's default (call 3).
- Going ahead unless he says no: step 3 off, FLIGHT_HSE_IN's two vias, the USB and CAN via pairs.
- His call, if he wants one: nets open on the budget run, with 1 to 5.

## Where we are

Measured, not yet drawn. The meter is honest at last, and it says the easy nets are 9 short on a board whose MCU
capacitors are in the wrong place. One step back into placement, then the first copper that matters.
