# Burrito stages C and D: the plan from 23 November

**23 November 2026.** Opus, at Seán's ask: “assess the situation and provide the plan to move forward please, show
me all the calls you make and why”. It replaces the [handoff](burrito-stage-cd-handoff.md)'s order of work where
they differ; its kill lines and stop list stand. Tags: [O] measured, [M] my reasoning. Counts are ordinary nets
(Default class, 273) left open by the router at full effort on six layers, fire-logic waiver modelled.

## Where it stands

- Stage C steps 0 to 2 are on main: placement frozen as data, six layers, the fire-logic waiver with its rule check.
  Board b507a62c, DRC clean.
- Step 3 stopped at kill line 1 ([report](burrito-stage-c-step3.md)). Every MCU pin fanned inward: 34; nothing
  fanned: 17; plane pins only: 19 [O].
- The layer test's 26 was partly the meter's own error; the real baseline is 17 [O].
- Stage D's knobs, one at a time on step 1's board [O]:

  | Knob | Nets open |
  | --- | --- |
  | none (c6) | 17 |
  | one harmless via added in a corner (jitter) | 17, the same 17 nets |
  | equal layer costs | 16 |
  | 0.05 mm grid | 18 |
  | rip-up 5 | 19 |
  | **router vias 0.5 mm, 0.3 mm hole** | **9** (7 at U201, 2 at U401) |

- RF: the GNSS line routes, 8.5 mm with its ESD stub [O]. The LoRa line has no acceptable path. U4606's RF pin is
  on the side away from the SMA, and the only path the search found ran 30 mm, under the module's body [O]. The
  way round on the right passes within 1 mm of LoRa's own capacitors; the left is H1's keep-out [M].
- Still to draw in stage C: power, pyro, the RF lines, crystals, USB, CAN, the flash group, the sense pair.

## Calls

1. **Step 3 stays off.** The MCUs' plane pins get the ordinary decoupling fanout, a via at each pad, as the meter
   draws it, frozen in step 4. Why: it beat both fanouts (17 against 19 and 34). 4/5.
2. **Router vias 0.5 mm with a 0.3 mm hole for every signal net, not 0.6 mm.** The power classes keep theirs. Why:
   17 → 9, the only knob that moved more than two. It's the board's minimum via and the layout brief's dense-spot
   via, and it stays in JLC's free default (a 0.3 mm hole; the default pad is 0.4 to 0.45 mm). Downside: a 0.1 mm
   annular ring instead of 0.15 mm. 4/5.
3. **The other knobs stay at their defaults.** Why: each moved the count by two or less. 4/5.
4. **L5 is FLIGHT_3V3 over the whole layer, with GND under the armed-rail corridor; COMMS_3V3, CAN_3V3, LORA_3V3
   and BOOT_3V3 run as tracks.** This was option B; overnight I recommended A (islands for COMMS, CAN and LoRa).
   Why the change: the meter doesn't model the island rule, so A's 83 against B's 90 leaves out its cost. A's
   COMMS island would ring U401 and cut L6 through band 3. B's only split lies under the corridor, and the corridor
   is L6 copper that cuts L6 there anyway. The 7-net gap is inside the quick meter's spread. Downside: L6
   references 3V3, not GND, over most of the board, so fast nets stay on L1 and L3; U401 decouples through tracks.
   Amends D-22Nov.29: **needs Seán's yes.** 3/5.
5. **FLIGHT_HSE_IN takes two vias:** one under U201 in pin 12's lane, one in Y201's pad 1 (filled and capped, free
   on six layers), with about 4.5 mm on L3 between the GND planes. Why: the only L1 way is shut (GND's 0.2 mm in
   Y201's pad gap, U201's LSE pins across the way round). GND at 0.15 mm would loosen a rule for no routing gain.
   About 1 pF of stray pulls a 16 MHz crystal a few ppm [M]. 4/5.
6. **USB and both CAN pairs cross with one via pair each, on L3 between the GND planes.** Why: each pair has to
   cross itself (USB-C's rows interleave D+ and D−; pin orders reverse between the ends). Two vias at 12 Mbit/s or
   less cost nothing measurable [M]. 5/5.
7. **U4606 turns 90°, RF pin toward the SMA, and D4601 moves onto the new line.** Why: as placed there's no
   acceptable LoRa line (above). Turned, the pin faces J4601 across open board, about 7 mm away [M, to trial
   first]. Downside: the module's other pads move, so its SPI and supply routes change. Parts move more than
   1 mm: **needs Seán's yes**, after a trial build shows courtyards and DRC clean. 3/5.
8. **RF lines: 0.142 mm, 0.203 mm gap, fence 2 mm or less, other copper 1 mm away**, the last as a custom DRC rule
   (tighter, not looser). The width is the layout brief's coplanar figure; it gets JLC's calculator before the
   order (D-22Nov.16's open item). 3/5 on the width.
9. **Pyro before power.** Channel 1, then the stamp (D-22Nov.27, decided) moves channels 2 and 3's parts. Power
   then routes to where the channels end up.
10. **One router run at a time.** Two full-effort runs hit the container's memory limit and one was killed.

## Order of work

1. Router vias 0.5 mm in the meter and the stage D runner; log the knob runs. *Exit:* the meter repeats 9.
2. Scripted copper that waits on nothing: the GNSS line, the crystals (FLIGHT_HSE_IN as call 5), USB and the two
   CAN pairs (call 6). One commit each, two builds the same bytes, DRC clean, the rule check passing, then the
   router once.
3. U4606's turn as a trial build; on Seán's yes, commit it with the LoRa line.
4. Pyro: channel 1's block, then the stamp. Fire logic from U201 drawn by script to the channels (D-22Nov.26).
5. Power on Seán's yes to call 4: L5 plane and corridor GND, the corridor on L6, the 6 A path as L1 pours, the 1 mm
   feeds, the decoupling fanout frozen.
6. The flash group and the sense pair.
7. Stop 2 report; carry on.
8. Stage D: the passes of D-22Nov.17 frozen under `layout/routes/`, then the rungs for what's left. Kill line 2
   stands: more than 10 nets after rungs 1 and 2, stop and bring the list. Then teardrops, stitching, fill, DRC,
   outputs, Stop 3.

## Needs Seán

- Yes or no on call 4 (L5) and call 7 (U4606's turn).
- Optional: his guess for nets open on stage D's first pass after stage C, with 1 to 5. The model's bet in the
  ledger is 10 or fewer.
