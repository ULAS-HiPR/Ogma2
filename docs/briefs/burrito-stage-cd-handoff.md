# Burrito stages C and D: handoff

**22 November 2026.** Written by Claude Fable for Opus, at Seán's request: “please look at Opus’ plan and write
the handoff. I agree with its general direction. Let’s go phase C 6 layers and then run phase D full effort.”
It sits on top of the [execution brief](burrito-execution-brief.md), the [layer test](burrito-layer-test.md) and
D-22Nov.29. Where they differ this is newer; `decisions.md` wins over all of them. Tags: [O] measured today,
[D] decided, [M] my reasoning or memory, to check before it's built on.

## The job

Stage C on six layers, then stage D at full effort, to Stop 3: nothing unrouted, DRC clean, outputs ready.

**Stop 2 is a report, not a wait.** That's my reading of “and then run phase D”. Send Stop 2's set when stage C is
done and carry on into D. Nothing is irreversible before Stop 3, and a change to stage C's copper only costs router
time. Stop and ask only for the cases under "When to stop".

## What the layer test says about the work

- On six layers at full effort the router left 26 ordinary nets open [O]. 20 of them touch U201 and 2 touch U401.
  In that run the router logged 23 "boxed in by static copper" verdicts, and 21 of its blocker reports name copper
  that was there before it started [O].
- That copper is the meter's own plane fanout: a via and stub beside every supply and ground pad, in the same strip
  the signal pins need to leave by.
- So the job is the MCU escape. The plan below takes it away from the router entirely.

## Order of work

One bounded change per commit, as before. After every step from 3 on, run the router once on the Default class at
full effort and log the count: it takes about 7 minutes [O], and on an unchanged board it repeats exactly [O].

**0. Freeze the placement as data. Do this first.**
- The placer reshuffles the whole board on any small change: four near-identical placements metered 84 to 100 [O].
  Scripted copper and frozen routes can't sit on that.
- Write `positions` from `build.json` to `hardware/croi2/layout/placement.json`. `build.py` places from it and
  runs the placer only when asked.
- Exit: a build from the file gives the same bytes as 7451d7d4.
- A later nudge is one edited entry, checked by `Placer.ok`, and it moves nothing else.

**1. Six layers in the spec (D-22Nov.29).** As the execution brief's stage C now lists. Exit: every part where it
was, two builds the same bytes, DRC as today.

**2. Rules before copper.**
- Draw each L5 island's outline as a track keep-out ring on L6. The router and KiCad's DRC then both enforce the
  island rule, and no separate checker is needed. Check that the router honours rule areas: its JSON has a
  `rule_area_keepouts` key [O].
- Keep each island under the pads it feeds. L5 under the armed-rail corridor stays GND.
- The fire rule's waiver inside U201's courtyard (D-22Nov.26) ends at the courtyard edge. By there a fire-logic
  track needs 0.5 mm to its neighbours on whatever layer it's on, so reserve the channel each side of it.
- Plant one violation per custom rule and see DRC report it. The router's log calls two of our rules unparseable
  [O]; KiCad does enforce the fire rule [O], but the others haven't been seen to fire.

**3. MCU fanout: inward, under the body.**
- Supply and ground pins: an L1 track to their own capacitor. The capacitor's two pads carry the plane vias, in
  the pad. No plane via beside an MCU pad.
- Every signal pin without scripted L1 copper: a short L1 stub inward to a via under the body, in two staggered
  rows. At 1.0 mm between vias in a row, one 0.15 mm track passes between two 0.45–0.5 mm vias [M]. JLC's default
  tier is a 0.3 mm hole in a 0.4–0.45 mm pad [O].
- Put every via the router will start from on its 0.1 mm grid. U201 sits 0.012 mm off the grid in y [O], and the
  router blames off-grid pads for some failures [O].
- Each inner-row via must be able to leave between the outer row on L3 or L6. If the router can't find the gap,
  script that short breakout too.
- After a pass is frozen, delete fanout vias and stubs the routes didn't use.
- Exit: no net fails as "boxed in" at an MCU. The count after this step alone settles a bet in the ledger (26
  today).
- **If the count is still above 26, stop and report.** The premise would be wrong, and more scripting on it would
  be sunk cost.

**4. Power.** Islands on L5; the armed-rail corridor on L6 over L5's GND; the 6 A path as L1 pours; the 1.0 mm
feeds. Draw them compactly: the router's stand-in for this copper cost 19 ordinary nets on six layers [O]. Report
each path's narrowest neck against IPC-2152.

**5. Pyro.** Channel 1, then the stamp (D-22Nov.27). C6603: a via in its pad and a stub of 0.5 mm or less on L3 or
L6 round pin 5's barrel. The stub carries no fire current, so it needn't be 1.0 mm; it does keep 0.5 mm clearance.
Check that nothing in the rules enforces the class width on it.

**6. The rest of sweep §8's list:** RF lines and fences, USB, CAN, crystals, the flash group, the sense pair.

**7. Stop 2 report.** The execution brief's set, with the L5 map. Send it and go on.

**8. Stage D.**
- First, one knob at a time on the frozen board, Default class, full effort: grid 0.05 mm; layer costs (the
  default for three layers makes L3 and L6 three times L1's cost [O]); `--max-ripup`. Keep what wins.
- Measure the router's own jitter once: add one harmless via in an empty corner and rerun. Smaller differences
  than that mean nothing.
- Then the passes of D-22Nov.17, each frozen under `layout/routes/` and replayed by `build.py`.
- For what's left, read each net's blocker in the router's JSON, then take the cheapest fix that fits:
  1. Clear unused fanout and reroute.
  2. Nudge a two-pin part by 1 mm or less in `placement.json`.
  3. A scripted route for that net, as a route file.
  4. A pin swap: capture step, checker, the firmware interface table. Seán pre-approved these on 22 Nov if
     justified, verified and documented.
- **If more than 10 nets are left after rungs 1 and 2, stop and bring the list.**
- Then teardrops, stitching, fill, DRC, outputs for six layers, and Stop 3.

## Two cautions on via in pad

- It's free, but it isn't always right. A 0402 with one pad on a plane via and the other on a thin track heats
  unevenly in reflow and can stand up [M]. Use the in-pad via where both pads go to planes or pours, as on a
  decoupling capacitor. On a pull-up or pull-down, keep the via beside the pad on a short neck.
- A plane pad with no via spot isn't a miss if it reaches its capacitor's via on L1. Count the pads with neither.
  The target is 0.

## When to stop

Stop and ask for any of these. Otherwise decide, log it, and carry on.

- Any schematic change or new part.
- Any rule made looser: the 0.15 mm floor, the island rule, the fire waiver beyond a courtyard.
- Moving a connector, an anchor or a mounting hole, or any part by more than 1 mm.
- Anything that changes JLC's price or tier, such as a smaller via.
- Either kill line above.

## Traps found today

- Run `tools/layout/env.sh` with bash, never `source` it: sourced, it bind-mounts `/` over the repo's mount.
- The chroot's bind mounts drop mid-session. Long runs go from a copy of the repo inside the chroot.
- The unrouted count means nothing until the plane zones are filled. Check that a filled board still builds to the
  same bytes twice.
- The board file is four layers until step 1.
- Nothing has been sent to Anav. Any pin swap adds to the table he hasn't seen.
- Burrito will be 1.54 mm against Churro's 1.6 mm. J102 mates in the plane of the boards, so 0.06 mm should be
  inside its float [M]. Note it in the interface; no action expected.
