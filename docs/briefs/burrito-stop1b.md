# Burrito stop 1b: the placement before copper

**22 November 2026.** Stage B2 of the [execution brief](burrito-execution-brief.md), run to the
[B2 brief](burrito-stage-b2-brief.md). 80 × 160 mm, every part on top, nothing routed. Board bbab4a1a,
commits 46385ae to 52cc7f6. Stage C waits for Seán.

## In one paragraph

Every yardstick moved the right way: wire −7%, crossings −24%, wrong-side pins 81 → 52, test point stubs
median 12.5 → 4.2 mm. The router barely noticed: the quick meter leaves 108 of 328 signal nets open,
against 111 on the baseline, and 105 at 165 mm and 103 at 170 mm. What stays open is mostly copper stage C
scripts anyway (the 4 mm and 2 mm power classes, the fire rule at U201's pins) and Default nets in the
flight and power bands. Length isn't the constraint, so 160 stays the call.

## Levers, one by one (fast yardsticks)

| Step | Board | Wire (mm) | Crossings | Wrong-side pins (U201, U401) | Plane pads without a via | Stubs to route: median / >10 / >20 mm | Densest band | Kept |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 Baseline | f7e9e695 | 8032.5 | 3221 | 81 (39/77, 19/28) | 61 | 12.5 / 28 / 8 | 0.735 | — |
| 2 S/N box on top | same placement | — | — | — | — | — | — | yes |
| 4 SMT loops | trial | 7938.3 | 3149 | — | — | 9.2 / 21 / 6 | 0.731 | yes |
| 3 U401 turned, 7 mm left | ba836c8b | 7814.6 | 3015 | 65 (35/76, 9/26) | 58 | 9.2 / 21 / 4 | 0.710 | yes |
| 7 Pin swaps | 18bdb9f9 | 7545.1 | 2633 | 55 (25/78, 6/27) | 61 | 8.4 / 17 / 3 | 0.724 | yes, past the 2% rule on via pads |
| 5 Test points by route | f6f630f0 | 7432.2 | 2494 | 54 (25/78, 6/27) | 62 | 4.7 / 9 / 1 | 0.707 | yes |
| 6 Distance rules | bbab4a1a | 7467.6 | 2437 | 52 (26/77, 6/26) | 59 | 4.2 / 6 / 1 | 0.708 | yes |
| 9 Band equalisation | six trials | 7533–7729 | 2465–2591 | 48–56 | 55–62 | — | 0.705–0.730 | no: spread never under 0.018 |
| 8 Refinement pass | — | | | | | | | not written |

Tried and dropped: U201 at 90°, 180° and 270° (BZ9001 found no room, 2–4% more wire); U401 at x = 30 (densest
band 0.745) and x = 36; the congestion map (its heat didn't sit where the router failed). Builds of the same
swaps from netlists that differ only in net names scatter by about 2% in wire and ±2 via pads, so the 2% rule
sits inside the placer's noise for small counts.

## The meter (KiCadRoutingTools 1577fa3, quick mode, class by class)

| Run | Nets open | Connections open | Router vias | Track (mm) | DRC |
| --- | --- | --- | --- | --- | --- |
| Baseline, f7e9e695, twice | 111 of 328 (33.8%) | 169 | 777 | 7455 | 11 clearance |
| Final, bbab4a1a, twice | 108 (32.9%) | 164 | 748 | 7596 | 9 clearance |
| 165 mm trial | 105 (32.0%) | 156 | 751 | 7491 | 12 clearance |
| 170 mm trial | 103 (31.4%) | 156 | 768 | 7833 | 9 clearance |

Open by class, baseline → final: Default 87 → 84 of 273; SRC_6A 2 → 2 of 2; PYRO_RAIL 4 → 1 of 4; FIRE 5 → 4
of 9; FIRE_LOGIC 7 → 7 of 9; LOGIC_FEED 3 → 4 of 5; USB_DIFF 2 → 2 of 4; CAN_DIFF 0 of 4; RAIL_3V3 1 → 4 of 18.
By band: RF and fire 19 → 20, flight 44 → 42, comms 18 → 15, power and harness 30 → 31. Every DRC error is the
fire rule where a fire track leaves a pad within 0.5 mm of the same part's other pads.

Freerouting gave no count. With 40 passes it ran 40 minutes without a result; with 10 it was stopped after
42 minutes still inside its first routing pass. Its fanout stage escaped 1518 of 1802 SMD pins (84.2%).

## Pin changes (D-22Nov.25)

36 flight and 12 comms nets moved; every one is in the
[firmware interface](../firmware-interface.md#pin-changes-d-22nov25) for Anav. Four moves fix reset-state
faults, verified against ST DS14258, TI SLVS841G and SCDS390B and AN2606: `CHURRO_RETURN_EN` off PA15 (its
pull-up switched Foinse's aux rail on at every power-up) and three outputs off pins the ROM bootloader drives
(PA9, PA11, PA12). The checker now holds the rules as A24–A26.

Class B, apart (fire, low side, arm sense, latch, new-flight request), each a plain I/O, analog at reset:

| Net | Was | Now | Why |
| --- | --- | --- | --- |
| `PYRO2_FIRE` | PE9 | PE15 | Nearer what it connects to |
| `PYRO3_FIRE` | PE12 | PE9 | PE12 sat beside the recovery arm sense (PE13) |
| `PYRO1_LS_SELECT` | PA9 | PD4 | The bootloader drives PA9 |
| `PYRO2_LS_SELECT` | PC8 | PB1 | PC8 carries trace data |
| `PYRO3_LS_SELECT` | PD14 | PC6 | PD14 sat beside the new-flight request (PD15) |
| `STAGING_ARM_SENSE` | PE15 | PD6 | Nearer what it connects to |
| `STAGE_INHIBIT_LATCHED` | PE14 | PE0 | Nearer what it connects to |
| `NEW_FLIGHT_CLEAR_REQUEST` | PD15 | PD7 | Nearer what it connects to |

`PYRO1_FIRE` (PE7) and `RECOVERY_ARM_SENSE` (PE13) stay. No peripheral instance changed.

## The loop pick

Keystone 5194TR, yellow, surface mount (D-22Nov.24, capture step 18): pad 3.0 × 1.5 mm, "most standard
probes, clips and hooks" in Keystone's catalogue, JLC C22388408 (486 in the 21 Nov scrape). Trial against the
through-hole loops on the same placement: stubs median 12.5 → 9.2 mm, wire −1.2%, crossings −2.2%.

## Misses

Distance rules (`metrics.near`): 9 misses among the 30 parts the rules cover.

- U1701's output capacitor: 6.0 mm (rule 2 mm).
- C6601–C6606: 6.7–9.7 mm from their J6601 pins (rule 3 mm). J6601's top row of pins sits 4.3 mm inside its
  courtyard, so the three HIGH capacitors can't make 3 mm with every part on top.
- D4501 and D4601: 2.6 and 2.9 mm off the line from connector to module, at the module end (rule 1 mm).

Test points: TP36 (`BUCK_PG`) at 22.1 mm from its route (limit 20). All seven with their circuit are within
10 mm.

## Doubts

- `FIRE_LOGIC` stays open (7 of 9 every run): a 0.5 mm clearance can't escape U201's 0.5 mm pitch.
- The quick meter may be the wrong judge of placement: the yardsticks moved a lot and it barely did. Full
  mode is untried.
- `STAGE_INHIBIT_LATCHED` sits on PE0, beside VCAP: a solder bridge there would leave its reading
  ambiguous. Not a fire path.
- The flash group still spans three sides of U201; one side would need a bootloader pin.
- RM0481 wasn't reachable (st.com refuses fetchers); DS14258 states the same reset pulls.
- Not done: the pyro stamp (channels 2 and 3 from channel 1), the refinement pass, bands within 0.01.

## Calls for Seán (one line each, skippable)

1. Length: stay at 160 mm (165 and 170 open 105 and 103 nets against 108)? Default: 160.
2. `FIRE_LOGIC`: keep 0.5 mm and script its escape from U201 in stage C? Default: yes.
3. C6601–C6606: as close as J6601's courtyard allows, about 4–5 mm for the top row? Default: yes.
4. Pyro stamp and refinement pass: stamp the channels with the pyro copper in stage C, drop the refinement
   pass? Default: yes.
5. Stage C on this placement? Default: wait for your word.

## Seán's answers (22 November)

“1.yes. 2.yes. 3.yes 4yes. 5.what is stage c?”

1. 160 mm stays (noted on D-22Nov.21).
2. `FIRE_LOGIC` keeps 0.5 mm; stage C scripts its escape from U201, with the rule waived only inside U201's
   courtyard (D-22Nov.26).
3. C6601–C6606 as close as J6601's courtyard allows (D-22Nov.28): now 3.7–3.9 mm on the HIGH pins and 0.9–2.1 mm
   on the LOW, from 6.7–9.7 mm. Distance-rule misses 9 → 3.
4. The pyro channels are stamped in stage C; the refinement pass is dropped (D-22Nov.27).
5. Stage C was explained in chat (the execution brief's stage C: the critical copper by script, ending at
   Stop 2). It waits for his go.
