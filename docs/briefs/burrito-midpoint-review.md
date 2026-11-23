# Burrito at the midpoint: what three days taught, and the method from here

**23 November 2026.** Written by Claude Fable at Seán's ask: “look at everything that we've been doing. And where
are we getting stuck? What approaches are working better?” It changes no decision. The
[stage C/D review](burrito-stage-cd-review.md)'s stop list, its gate (25 nets) and kill line 2 stand. Tags: [O]
measured, or read from the repo, the meter's runs or the taste ledger; [M] my reasoning, to check before it's
built on; [B] a bet, with what settles it.

## Verdict

Placement is right for the first time, and it took a re-placement by rule to get there. No copper is on the board
yet [O: the board file holds 0 tracks]. For two days the number we steered by answered an easier question than the
one that decides the board. The method below changes the order of work, for the rest of Burrito and for every board
after it.

## Scoreboard

| | Before (22 Nov evening, or as first measured) | Now (b2e14f5, board 5b85ff73) |
|---|---|---|
| MCU supply pins with their capacitor | not measured per pin; at least 8 sat 6 to 19 mm away | 22 of 22 |
| Pyro supply capacitor to its pins | 23 to 27 mm | 0.6 mm, all three channels |
| Ordinary nets the router leaves open, no hard copper, full effort | 26 of 273 (17 once the meter was right) | 4 of 273, noise about ±2 |
| The same with the hard copper reserved | never measured | still not measured: one run, void |
| Copper kept on the board | none | none |
| The review's order of work | | steps 0 to 2 of 7 done; step 3 run once, void |

What moved the real number (ordinary nets open, six layers, full effort) [O]:

| Change | Open nets |
|---|---|
| Four layers to six | 41 → 26 |
| The meter models the fire-logic waiver (no board change) | 26 → 17 |
| Router knobs: layer costs, grid, rip-up, a re-roll | 16 to 19 |
| Signal vias 0.6 → 0.5 mm | 17 → 9 |
| Capacitors to their pins, U4606 turned | 9 → 5 |
| The pyro band and both MCUs re-placed | 5 → 4: inside the noise, so “no worse” |
| Every MCU pin fanned inward under the body | 17 → 34: not kept (kill line 1) |
| Stage B2's pin swaps and MCU turns | quick meter 111 → 108 of 328, noise about 10, while U201's wrong-side pins fell 35 → 25 and U401's 19 → 9 |

## Where we got stuck

1. **An easier question stood in for the hard one.** Stage B2 steered by wrong-side pins, wire length and
   crossings; after it we steered by the router's count on a board with no hard copper. The fire paths, the 6 A
   copper, the armed rails and the RF lines were scheduled last and reserved nowhere. The corridor has been in the
   layout brief since 22 November (x ≈ 9–16 mm) and nothing enforced it: U3604 sits astride it and the LoRa supply
   parts stand in its crossing [O: the budget run]. My review of this morning made the same mistake one level up.
   It put the floor plan (step 3) after the placement fixes (steps 1 and 2), so today's re-placement set the pyro
   diagnostics down in the crossing [O].
2. **Instruments failed open, four times.** (a) The near check measured per part, so it passed while eight MCU
   supply pins sat 6 to 19 mm from their capacitors. (b) The meter gave fire logic 0.5 mm at U201's pins, so 9 of
   its 26 open nets were its own. (c) On 22 November two router runs at once ran out of memory; the one
   killed still printed “271 of 273 open”, was set aside by hand, and the fix was a habit: one run at a time.
   (d) Today a single run was killed the same way and read rc 0 with the same 271. (c) to (d) is one mistake made
   twice: the first was handled as an incident, not as a kind.
3. **Differences inside the noise were read as effects.** The quick meter scatters about 10 nets between
   near-identical placements (84, 100, 92, 91); full effort about 2; the placer's wire length 1.5% between equal
   builds. Step 3's first reading was “cost two nets”.
4. **Each stage ran across the whole board, so its defects surfaced one stage later.** The capacitors' defect was
   made in stage B and found in stage C. The pad-exit clearance at the output stage was written down on 22 November
   (D-22Nov.26, still to check) and became a blocking ask a day later.
5. **Exceptions went to Seán one instance at a time.** About ten yes-or-no rounds in two days, each a wait. The one
   batched round, this morning's review, got four decisions in one line. The waiver granted for U201 now returns
   for seven more parts.
6. **The router's memory is the pipeline's hard limit, and nothing manages it.** Finished full-effort runs peaked
   at 3.1 to 4.8 GB on a board with no hard copper; the container ends a process at about 6 GB [O]. Stage D runs the
   same router on a fuller board. [M] It will be hit again unless the work is split.
7. **My predictions of the router are poor.** Three count bets at 3/5: one held, two missed, the inward fanout by
   three times and in the wrong direction. Seán's two calls on this board (six layers; 160 mm doesn't route without
   a re-place) both held [O: taste ledger].

## What worked

- **The board is the output of scripts.** Every change is a scratch build that passes its gates (DRC, the near
  check, the meter no worse, two builds the same bytes) before it's committed. 148 parts moved in one commit with
  DRC at 0.
- **Kill lines set in advance.** The inward fanout cost one trial, not a day.
- **Placement by rule, most constrained first, one region at a time** (`replace_region.py`): the stamp, capacitors
  to their pins, crystals, the rest, test points with their circuits. It fixed in an afternoon what the whole-board
  placer had left wrong since stage B.
- **Decisions batched at a review.**
- **Planted-violation checks** (`rules_check.py`): the one instrument that hasn't misled us.
- **The gains came from measuring, not tuning:** layers, via size, parts where the datasheet puts them. The
  router's knobs moved nothing.

## The method, for the rest of Burrito and for the next board

1. **Interfaces fix the edges:** connectors, holes, datums.
2. **The floor plan comes before placement.** Every path that carries real current, RF or a fire command is drawn
   as areas: which layer, how wide with its clearance, where it changes layer. Each area says what it forbids above
   and below (an L6 rail forbids any via through it, so no plane-net pad sits over it). The placer treats the plan
   as fixed.
3. **Distance rules are written per pin, before placing,** with a check that fails when one is missed. A repeated
   circuit is one block, stamped.
4. **Parts go down in order of constraint,** a region at a time: fixed parts, stamps, parts under a pin rule,
   crystals and RF, the rest, test points.
5. **One steering number from the first placement: the budget run.** The router on the ordinary nets with the hard
   copper reserved, in the router's quick mode (main pass only: minutes, and bounded memory). A quick count is
   never below the full-effort one, so a quick count under a gate passes it. The same board is run three times
   first; that spread is the noise, and nothing inside it is an effect.
6. **A region is finished before the next starts:** placement, hard copper, DRC, budget run, frozen. Hardest region
   first. The whole-board router runs once, when the hard copper is all down.
7. **Instruments fail closed.** Each check has a planted failure it must catch. Each run says valid or void, and a
   void run prints no count. When one breaks, the kind is fixed before the next run.
8. **A lever gets a trial and a kill line, never a prediction.**
9. **Exceptions go to the owner as rules, in one batch, at the stage boundary.** Every “still to check” the next
   stage needs is settled before that stage starts.

Earned by what worked [O]: 3, 4, 8, and 7 in part. Bets [B]: 2, 5 and 6. They settle on whether Burrito's pyro band
reaches frozen copper in one working session once its calls are answered, and on whether Churro reaches a placed
and budgeted board with no region placed twice.

**Churro** has no MCU: two packs, the umbilical and an eFuse on each branch. Almost all of it is step 2. Its first
artefact is the current-path floor plan, not a placement.

## From here on Burrito

1. **Meter.** `--budget` runs in quick mode with `--krt-minutes`, and prints peak memory. The plain baseline in
   quick mode three times, for the spread.
2. **Floor plan to the copper's real size,** and the placer keeps plane-net pads off L6 keep-outs. Re-place the
   crossing, the corridor's neighbours and the low side (FETs behind J6601's LOW pins) with `replace_region.py`.
   Budget run. The gate is 25.
3. **Pyro band to frozen copper:** channel 1's block, its picture and current-path table to Seán, the stamp, fire
   logic from U201, DRC, budget run.
4. **Power the same way** (the 6 A copper, the feeds, L5's plane, the corridor); then the RF lines, the crystals,
   the pairs.
5. **Before stage D, one trial of routing by band:** each band's own nets, then the nets that cross, with count and
   peak memory against a whole-board run. [M] It is the cheap answer to the 6 GB limit.
   Seán asked whether the router could run on his Mac instead. It wouldn't lift the limit: the laptop has no more
   memory than the container, and the sandbox reachable on it has 3.9 GB and 4 cores [O], less than a finished
   full-effort run needs. It would be faster per core, but the router ran for 33 minutes of 23 November [O].
6. Stage D, the finish, Stop 3.

## Calls for Seán

**Answered, 23 November:** “A. Yes.” “B. Your option fable, i prefer it:” “C, yes.” “D, yup. Assuming the edge
connectors remain at edges and the holes remain lying on a rectangle”. They are D-23Nov.8 to D-23Nov.11. His yes on A
covers the courtyard; an area past it goes back to him.

**A. One rule for fire logic leaving a fine-pitch part.** D-22Nov.26 waives the 0.5 mm fire rule for fire logic
inside U201's courtyard. The same geometry holds at U6304, U6404 and U6504 (IN pin 0.2 mm from its neighbours [O]),
at Q6301, Q6401 and Q6501 (gate 0.35 mm from the drain pad [O]) and at U6502, channel 3's gate ([M], not measured).
Proposed: *inside the courtyard of a part whose own pads sit closer than the fire rule allows, fire logic keeps
0.2 mm; everywhere else 0.5 mm.* It lowers no minimum the land patterns don't already set. [M] The area may need to
reach up to 0.25 mm past the courtyard for a track to be 0.5 mm from the neighbouring pads' corners where it
leaves; a planted test settles the extent. No alternative keeps the parts.

**B. HIGH 2 and C6603.** J6601's pin 2 sits behind the LOW row; the gap between LOW pads is 1.5 mm and a 1.0 mm fire
track needs 2.0.
1. HIGH 2 on L3 round the LOW row; C6603 on a 0.25 mm stub between pins 4 and 5. Exception: FIRE's width, on the
   stub.
2. HIGH 2 on L3; C6603 on that loop, about 9 mm from the pin. No exception.
3. **Recommended, 4/5:** HIGH 2 stays on L1 and passes between LOW pins 4 and 5 through a neck 0.5 mm wide and about
   2 mm long, 0.5 mm from both pins. C6603 sits on the trace just before the neck, 4 to 5 mm from pin 2. Exception:
   FIRE's 1.0 mm width, for the neck only. Channel 2 then has the shape of channels 1 and 3, so the block stamps;
   no via sits in a fire path; the run is about 13 mm against about 22 [M]. The neck's copper (0.5 × 0.035 mm) is
   about one 0.3 mm via barrel's, and the L3 route would put two or three barrels in the same path. About 2 mΩ:
   8 mW at the ≈2 A pulse (layout brief), 58 mW at D-19Nov.8's 5.4 A ceiling [M]. Downside: HIGH 2 runs between two
   FETs if the low side moves behind J6601. If the block doesn't fit, 2 is the fallback. Test: one scratch build
   with DRC.

**C. PYRO3_HS_ENABLE is in class Default.** It runs from U6502 to U6504's IN pin: the staging channel's fire command
after its inhibit gate, the same part PYRO1_FIRE and PYRO2_FIRE play at their high sides. `spec.PATTERNS` lists
only `PYROn_GATE`, `_FIRE` and `_LS_SELECT` as fire logic [O], so this net gets 0.15 mm and the router. Proposed: add
it to FIRE_LOGIC. It tightens a rule.

**D. D-23Nov.7's reach.** Read as: any part may move, except those other decisions hold in place (the edge
connectors of D-21Nov.24, the mounting holes, J102's datum).

## Bets

- [B] Standing in the ledger: with the hard copper reserved, the ordinary nets at full effort leave 15 to 30 open.
  3/5. Settles: the budget run, once one finishes.
- [B] Call B's option 3 builds DRC-clean as one block on all three channels. 3/5. Settles: the scratch build.
- [B] Routing by band keeps the router's peak under 4 GB and costs 3 nets or fewer against a whole-board run. 3/5.
  Settles: the trial before stage D.
