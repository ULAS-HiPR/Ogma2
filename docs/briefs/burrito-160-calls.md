# Burrito at 160 mm: calls before S4

**22 November 2026.** Claude Fable, for Seán, then for Opus to execute. These are a model's calls and
proposals. Nothing here is decided until Seán says so, except the two items marked as his.

## Seán's answers (stated, 22 Nov)

- **J102 keeps -SD** and he orders MPT-08-01-01-L-RA-SD from Mouser. This closes D-22Nov.14.
- **Every component stays on the top face** (D-21Nov.27 stands).
- **His call:** 160 probably doesn't route without a re-place. No confidence given yet.

## 1. Why the S/N box went to the back

Two reasons. His message said to assume it was on the back, and in the stage B sweep the box was the
one thing that didn't place on top at 160 mm (about 105 mm² with its label).

**Call: leave it on the back.** Top area is the scarce thing and the back has room. The cost is that
it can't be read with the board on its sled. If that matters, a 10 × 3 mm box on top costs about
40 mm².

## 2. Test points away from their circuits

**Call: electrically, none of the 13 far ones matters. Don't rearrange the back now.**

- A test point's trace carries no current, so it reads the voltage where it taps. Where the trace
  taps matters; where the loop sits doesn't. Rail loops (TP31, TP34, TP35, TP37, TP40, TP46) are
  fine anywhere if each taps at its regulator's output capacitor.
- TP19 (the strobe) sits behind R203 and R205, so 43 mm of trace adds about 0.3 ns. TP15
  (GNSS_PPS), TP17 (BOOT0) and TP36 (BUCK_PG) are slow or DC.
- The "distance to the net's centre" figure overstates the problem. A net that already travels
  (PPS, a rail, a power-good line to the MCU) can carry its test point anywhere along the route.
  The honest measure is the distance to the nearest pad on the same net.
- **Three to watch** (inferred, sheets not re-read): TP43 `BAT_BLOCK_GATE` is a high-impedance gate
  node; TP5 and TP7 are analogue ADC nodes near the fire band. Keep these within about 10 mm.
- **The real cost is routing room:** thirteen stubs of 20–43 mm on the densest board yet, and each
  through-hole loop pin blocks all four layers, the free bottom layer included.

**Rule proposed for S5:** test point traces route last and thin, tapping at the capacitor. A loop
whose stub can't route cleanly moves then, and the back gives way in this order: HOUSTON, then
parts-list rows.

## 3. Does 160 route without a re-place?

[model] bets, to be graded at S5:

- no parts moved at all: 1/5;
- routes at 160 with local nudges (under about 30 parts) and no length change: 3/5.

Reasons for: all of L4 is free for routing, and L2 and L3 are planes. Reasons against: the power
band is at 0.735, vias need gaps between courtyards, and the LQFP100 needs a fanout ring.

**Smallest test:** a congestion map of the placement (item 4c), run at 160 and 170 with one script.

## 4. Ways to make 160 work with everything on top

a. **Equalise the bands.** Densities are 0.672, 0.662, 0.625 and 0.735. Iterate `BAND_AREA` until
   the four match, at about 0.68, which is 170 mm's worst band. A script change with no downside.

b. **Surface-mount loops (proposal; needs Seán and a capture step).** Swap the 18 orange
   through-hole loops for Keystone's surface-mount test points (5019 miniature or 5015
   micro-miniature; part numbers recalled, drawings not read). No pins on the back, so loops sit
   beside their circuits, the back art stops constraining the top, and 18 holes stop blocking the
   routing layers. Downsides: about 60 mm² more top area, and a pad peels more easily under a
   clipped probe. The black GND loops stay through-hole at the edges. Check first: Keystone's
   drawing, JLC stock, then one sweep.

c. **Measure routing demand, not courtyard density.** After each build, write a congestion map:
   each net's bounding box spread over a 2 mm grid against the tracks that fit, plus a count of
   ratsnest crossings. It replaces the 0.65 proxy and shows where to spend the freed millimetres.

## 5. Placing locally so routing works

Today's placer is greedy: one part at a time, nearest legal spot to its pins' targets. Four changes,
cheapest first:

1. **Templates for critical clusters.** Each cluster is placed as one rigid group, drawn from its
   data sheet's layout: the buck, each LDO, each MCU's decoupling ring and crystal, SMA → ESD →
   module in a straight line, USB, CAN, and one pyro channel stamped three times with C6601–C6606
   at J6601. This is S4's work brought forward.
2. **A refinement pass.** After the greedy pass, swap same-footprint parts and flip rotations
   wherever weighted wire length and crossings drop. Swaps between identical footprints are always
   legal.
3. **Score by the congestion map** (4c), so the pass moves parts out of hot cells.
4. **An autorouter as a meter (needs Seán's OK to download).** Export to Freerouting and read its
   completion rate and unrouted list at 160 and 170. It's a routability gauge only; its tracks are
   thrown away.

Not proposed: swapping MCU pins. It would help most, but the pin maps are a recorded decision and
Anav's firmware depends on them. The crossings count will show whether it's worth asking.

## Work order for Opus

In order; stop after step 5 and report.

0. Fix `hardware/croi2/AGENTS.md`: J101 has its footprint (`Ogma2:105311-1102`, step 15). Record
   Seán's answers: D-22Nov.14 closed (J102 keeps -SD, Mouser), jlc-stock, stop 1, project log.
1. Ledger: Seán's bet "160 doesn't route without a re-place" with the confidence he gives; the two
   [model] bets in section 3.
2. A table of each test point's distance to the nearest pad on its net, at 160.
3. Equalise the band densities (4a). Rebuild, run DRC, compare.
4. The congestion map and crossings count (4c), at 160 and 170.
5. For 4b: read Keystone's drawings and JLC stock for the surface-mount loops; report only, no
   capture step.

**Stop.** Then Seán picks: surface-mount loops or not, Freerouting or not, and whether the cluster
templates start S4.

## Calls for Seán

One line each, skippable.

1. Your confidence, 1–5, that 160 doesn't route without a re-place?
2. S/N box: back, or a 10 × 3 mm one on top?
3. Surface-mount loops: worth Opus checking?
4. Freerouting as a meter: OK to download it?
5. How many J102 and mating parts are you ordering? Mouser's stock of the Churro half (MPS) wasn't
   checked.
