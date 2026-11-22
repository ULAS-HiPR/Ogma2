# Burrito layer test: four layers or six

**22 November 2026.** The layer test in the [execution brief](burrito-execution-brief.md), run on Seán's go
(“Ok go. Plus ultra”) before stage C. Board 7451d7d4 (today's placement, after D-22Nov.28), KiCadRoutingTools at
1577fa3 through `tools/layout/meter.py`. Nothing is decided here. Seán's call before the test: six layers, 4/5
(“We need 6 layers. Intuition.”).

## In one paragraph

Six layers leaves about 35–40% fewer ordinary nets open in every like-for-like run:
- 100 → 60 as Stop 1b measured;
- 60 → 41 with the ordinary nets alone;
- 41 → 26 at full effort.

Neither layer count closes the board by autorouting alone. The best case, six layers at full effort, leaves 26
nets, 17 of them in the flight band round U201. A fourth signal layer adds little (60 → 50). Via in pad makes no
difference at full effort (41 → 43 on four layers, 26 → 26 on six).

Six layers on JLC06161H-3313 costs $8.40 more for 5 boards ($59.40 against $51.00) and four more days (7–8 against
3–4). The RF and USB widths stay as they are, and economic assembly still applies.

What six layers really decides is the layer plan. That stackup puts every inner layer close to another, so a
layer of power islands puts one signal layer back over island edges. The alternative is running the rails as
tracks, which costs 14 ordinary nets in the meter (74 against 60).

## The runs

"Ordinary nets" are the Default class: the router's job in S5 (D-22Nov.17), 273 of the board's 328 signal nets.
"As Stop 1b" routes every class in turn, with the router laying its own plain tracks for the power and fire copper
that stage C will script. "Alone" routes the ordinary nets with nothing before them but the plane vias. "Full
effort" turns on the router's rescue laps (`--quick 0`). The six-layer copy gives the router L1, L3 and L6; L3 or
L4 counts the same.

| Ordinary nets open (of 273) | 4 layers | 6 layers |
| --- | --- | --- |
| As Stop 1b | 100 | 60 |
| As Stop 1b, via in pad | 79 | 60 |
| Alone | 60 | 41 |
| Alone, full effort | 41 | 26 |
| Alone, full effort, via in pad | 43 | 26 |

Two more six-layer runs, both as Stop 1b with via in pad:

- **Four signal layers (L1, L3, L4, L6):** 50.
- **GND the only plane, the five island rails routed as tracks:** 74, and 9 of the 23 small rails left open.

Every run:

| Run | What | Nets open | Ordinary open | Other classes open | Connections open | Router vias | Track (m) | Plane pads with no via | Open by band (RF and fire / flight / comms / power) | Router time | DRC errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r1a | 4 layers, as Stop 1b | 121 of 328 | 100 | 21 of 55 | 188 | 705 | 7.58 | 59 | 23 / 46 / 11 / 41 | 9 min | 10 |
| r1b | the same again | 121 of 328 | 100 | 21 of 55 | 188 | 705 | 7.58 | 59 | 23 / 46 / 11 / 41 | 9 min | 10 |
| r2 | 4 layers, alone | 60 of 273 | 60 | – | 73 | 568 | 5.97 | 59 | 5 / 34 / 10 / 11 | 2 min | 0 |
| r3 | 4 layers, alone, full effort | 41 of 273 | 41 | – | 43 | 631 | 6.50 | 59 | 2 / 26 / 8 / 5 | 10 min | 0 |
| r7 | 4 layers, as Stop 1b, via in pad | 102 of 328 | 79 | 23 of 55 | 161 | 719 | 7.27 | 48 | 20 / 39 / 14 / 29 | 8 min | 15 |
| r11 | 4 layers, alone, full effort, via in pad | 43 of 273 | 43 | – | 48 | 612 | 7.10 | 48 | 6 / 27 / 6 / 4 | 12 min | 4 |
| r4a | 6 layers, as Stop 1b | 82 of 328 | 60 | 22 of 55 | 117 | 691 | 7.19 | 59 | 18 / 30 / 11 / 23 | 6 min | 10 |
| r4b | 6 layers, alone | 41 of 273 | 41 | – | 46 | 542 | 6.04 | 59 | 3 / 21 / 6 / 11 | 2 min | 0 |
| r5 | 6 layers, as Stop 1b, via in pad | 80 of 328 | 60 | 20 of 55 | 125 | 675 | 7.38 | 48 | 15 / 26 / 12 / 27 | 8 min | 15 |
| r9 | 6 layers, alone, full effort | 26 of 273 | 26 | – | 27 | 586 | 6.49 | 59 | 1 / 17 / 3 / 5 | 7 min | 0 |
| r10 | 6 layers, alone, full effort, via in pad | 26 of 273 | 26 | – | 26 | 542 | 6.52 | 48 | 2 / 13 / 7 / 4 | 7 min | 4 |
| r6 | 6 layers, four signal layers, as Stop 1b, via in pad | 71 of 328 | 50 | 21 of 55 | 105 | 596 | 7.49 | 48 | 11 / 26 / 10 / 24 | 6 min | 14 |
| r8 | 6 layers, rails as tracks, as Stop 1b, via in pad | 100 of 333 | 74 | 26 of 60 | 148 | 809 | 8.30 | 37 | 23 / 29 / 20 / 28 | 8 min | 11 |
| n1 | 4 layers, as Stop 1b, D-22Nov.28 trial board a | 118 of 328 | 92 | 26 of 55 | 183 | 746 | 7.27 | 57 | 29 / 44 / 14 / 31 | 9 min | 9 |
| n2 | 4 layers, as Stop 1b, D-22Nov.28 trial board b | 114 of 328 | 91 | 23 of 55 | 168 | 705 | 7.33 | 57 | 22 / 42 / 19 / 31 | 9 min | 10 |

What the numbers rest on:

- **The same board meters the same:** r1a and r1b gave identical results, once on the meter as at Stop 1b and once
  on today's version.
- **Placement moves it more than it looks.** Four nearly identical placements left 84, 100, 92 and 91 ordinary
  nets open:
  - Stop 1b's board (bbab4a1a): 84;
  - today's: 100;
  - D-22Nov.28's two trial boards: 92 and 91.

  So gaps under about 10 are noise. Every gap between four and six layers is 15 or more.
- **The router's stand-in copper is costly.** Its plain tracks for the power and fire copper block about 40
  ordinary nets on four layers (100 against 60) and 19 on six (60 against 41). Stage C scripts that copper, so the
  "alone" rows are nearer the real job. That copper has to be compact on either layer count.
- **Run 3 was replanned.** It was meant to route every class at full effort, capped at two hours. Its first ten
  minutes went on the six power nets (the four armed-rail nets alone ran over seven), so it never reached the
  ordinary nets. It was stopped and rerun on
  the ordinary nets alone, which took 10 minutes.
- **Routes are straighter on six layers.** The 90th-percentile net is 1.33–1.41 times its rectilinear spanning
  tree, against 1.49–1.91 on four.
- **The meter ignores L3's island edges, which flatters four layers.** No L4 track may cross an L3 island edge
  (D-22Nov.15), but the islands aren't drawn yet, so the meter routes L4 as if L3 were whole. The same is true of
  L6 over L5 in plan P1 below. Plan P2 (r8) has no such constraint.
- **The DRC column:**
  - the fire rule at the output stage, as at Stop 1b;
  - r10's and r11's 4: plane vias put in the Tag-Connect pads, which their footprints keep clear. That's a meter
    artifact.

## What stays open, and where

At full effort the flight band holds most of what's left on either layer count: 26 of four layers' 41, and 17 of
six layers' 26. That's U201's escape: an LQFP-100 at 0.5 mm pitch inside its ring of decoupling capacitors. Stage C
starts with the MCU fanout and scripts the escapes. That, not a layer count, is what closes those nets.

## JLC's six-layer stackups (quote page, 22 November, nothing ordered)

At 1.6 mm with 1 oz outer and 0.5 oz inner copper, JLC lists 18 named six-layer stackups. Every one except
JLC06161H-3313 is marked "a special stackup", which "doesn't support economic PCB assembly". JLC's assembly
capabilities page agrees: economic assembly takes 2, 4 or 6 layers, "standard stack-up only".

| Stackup | L1–L2 | L2–L3 | L3–L4 | L4–L5 | L5–L6 | Pairs that sit close | Economic assembly |
| --- | --- | --- | --- | --- | --- | --- | --- |
| JLC06161H-3313 | 3313, 0.0994 | core 0.55 | 2116, 0.1088 | core 0.55 | 3313, 0.0994 | 1–2, 3–4, 5–6 | yes |
| JLC06161H-2116A | 2116, 0.1164 | core 0.13 | 2116 + core 0.7 + 2116, 0.93 | core 0.13 | 2116, 0.1164 | 1–2, 2–3, 4–5, 5–6 | no |
| JLC06161H-3313E | 3313, 0.0994 | core 0.1 | 7628 + core 0.7 + 7628, 1.12 | core 0.1 | 3313, 0.0994 | 1–2, 2–3, 4–5, 5–6 | no |

All values are in mm. JLC warns that JLC06161H-3313 finishes at 1.5384 mm, within its ±10%, not 1.6 mm. The
four-layer JLC04161H-3313 is 3313 at 0.0994, a 1.265 core, and 3313 at 0.0994, so L1–L2 is the same prepreg at the
same height in both.

A signal returns in the plane nearest it. On JLC06161H-3313 every inner layer sits about 0.1 mm from another, so a
layer of power islands always has a signal layer 0.1 mm away. That is D-22Nov.15's problem again.

| Plan (L1 to L6) | Signal layers over unbroken ground | Rails |
| --- | --- | --- |
| P1: S, GND, S, GND, PWR, S | L1 and L3. L6 sits 0.1 mm over L5's islands, as L4 does over L3 today. | islands on L5 |
| P2: S, GND, S, GND, GND, S | L1, L3 and L6 | tracks; no power layer |
| JLC's typical "SIG/GND/PWR/SIG/GND/SIG" | L1 and L6. L4 sits 0.11 mm over the power layer. | islands on L3 |
| On 2116A: S, GND, PWR, S, GND, S | L1, L4 and L6. L3's islands sit 0.13 mm over L2's ground and 0.93 mm from L4. | islands on L3 |

The meter's six-layer runs model P1 with its island edges ignored (r4a, r4b, r5, r9, r10) and P2 (r8).

## Impedance

The RF lines and the USB pair run on L1 over L2. In both JLC04161H-3313 and JLC06161H-3313, L1–L2 is 3313 prepreg
at 0.0994 mm, so D-22Nov.2's widths carry over unchanged:
- 50 Ω: 0.151 mm;
- 90 Ω pair: 0.154 mm with a 0.203 mm gap.

On 2116A the prepreg is 2116 at 0.1164 mm, and the widths would need JLC's calculator again.

## Via in pad

JLC's capabilities page says the filled, capped via-in-pad process "is the default for 6-layer and above", for vias
of 0.15–0.55 mm. JLC's six-layer page lists it as free. On four layers the quote adds $18.13 for filled vias and
$3.47 for their plating (5 boards).

The fanout on today's board, with each plane pad's via put in the pad wherever its copper clears:

| Via | Pads with their via in the pad | Plane pads with no via spot |
| --- | --- | --- |
| Beside the pad, 0.5 mm (as at Stop 1b) | 34 (exposed pads) | 59 |
| In the pad, 0.5 mm, 0.3 mm hole (free on six layers) | 498 | 48 |
| In the pad, 0.25 mm, 0.15 mm hole | 582 | 17 |

The 48 are pins where a 0.5 mm via can't keep its clearance to the next pin:
- the MCUs' 0.5 mm-pitch ground and supply pins (GND's class clearance is 0.2 mm);
- the sensors' LGA pins;
- ground pins beside fire copper (0.5 mm).

A 0.25 mm via fits the MCU pins, leaving the 17 fire-rule and LGA neighbours. On either layer count, the 0.15 mm
hole costs $36.26, plus $17.39 for a four-wire test and $3.63 for TG155 material (5 boards). In the routing runs,
via in pad made no difference at full effort.

## Prices and lead times

From JLC's quote page, 22 November: 80 × 160 mm, 1.6 mm, ENIG, green. Nothing was ordered.

| Board | 5 boards | 10 boards | Build |
| --- | --- | --- | --- |
| Four layers, JLC04161H-3313, plugged vias (today's plan) | $51.00 | $60.40 | 3–4 days |
| Four layers, filled and capped vias | $72.60 | $83.75 | 3–4 days |
| Six layers, JLC06161H-3313, via in pad included | $59.40 | $69.20 | 7–8 days |
| Six layers, JLC06161H-2116A | $161.82 | $174.80 | 7–8 days |

- Getting six layers in 3–4 days adds $132.40.
- Neither 3313 stackup has a stackup fee. The 2116A fee is $102.42.
- Shipping is quoted the same for both ($25.99, UPS, 2–4 business days).
- Assembly isn't priced: JLC's form wants the Gerbers first. The parts don't change with the layer count, and
  JLC06161H-3313 keeps economic assembly.

## What six layers would change

- **Decisions:**
  - D-21Nov.26: four layers;
  - D-22Nov.2: JLC04161H-3313, and plugged vias;
  - D-22Nov.15: L3 as ground with islands, and its L4 check;
  - D-22Nov.3's armed-rail corridor on L4 over L3;
  - D-22Nov.16's L2–L4 clearance round each SMA's centre pin.
- **Code:**
  - `spec.STACKUP`;
  - `spec.DRU`'s no-track rule, which would cover every ground layer;
  - `build.py`'s hole-washer keep-outs, which would cover every inner layer;
  - `metrics.plane_nets` and the fanout's plane map;
  - the meter's default layers;
  - stage C's first check.
- **Churro:** J102 mates edge to edge. Burrito would be 1.54 mm thick (JLC's figure) against Churro's 1.6 mm.
- **Docs:** the layout brief and plan, the PCB layout guide, current-system and the execution brief's stage C.

## Bets

The model's bets were written in the ledger before Seán's call:

- [model] Six layers, as Stop 1b, leaves 42 or fewer ordinary nets open (3/5). **60. Missed.** Four layers left 100
  on today's board, against the 84 the bet was written from.
- [model] Four layers at full effort leaves 20 or more ordinary nets open (3/5). **41. Held.** It was measured on
  the ordinary nets alone; see run 3 above.
- Seán: Burrito needs six layers (4/5). With the model's bet that Burrito ends on six (3/5), this settles on his
  decision.

## Recommendation

**Six layers on JLC06161H-3313, plan P1, the island-edge rule kept on L6.** About 4/5.

- **Why:**
  - At every effort level it closes 15–40 more ordinary nets than four layers. Four layers' numbers are
    flattering, because the meter ignores L3's island edges.
  - It costs $8.40, keeps the RF and USB widths and economic assembly, and makes via in pad free.
  - P1 keeps the rails on a plane and leaves L3 entirely over ground. Only L6 keeps today's island rule.
- **Downside:**
  - Four more days of build.
  - Five decisions and stage C's island scripts need rework.
  - The board is 1.54 mm thick.
  - Even six layers leaves about 26 ordinary nets for stage C's escape scripts.
- **Alternatives:**
  - P2 (rails as tracks): every signal layer over ground, but the router loses 14 more nets.
  - Four layers, putting the effort into stage C's escape scripts and more hand-guided routing: 41 or more open at
    full effort, before the island rule.
- **What settles it further:** meter both plans again after stage C's MCU fanout and scripted copper. That comes
  after this call, because stage C's copper depends on the layer plan.

## Calls for Seán (one line each, skippable)

1. Four or six? Default: six, on JLC06161H-3313.
2. If six, the plan: P1 (L6 keeps the island-edge rule) or P2 (rails as tracks, 14 more nets lost)? Default: P1.
3. Six layers' build time: 7–8 days, or $132.40 for 3–4? Default: 7–8.

Sources: JLC quote page (cart.jlcpcb.com/quote), read 22 November;
[JLC capabilities](https://jlcpcb.com/capabilities/Capabilities);
[JLC six-layer page](https://jlcpcb.com/6-layer-pcb);
[JLC assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities);
[JLC stackup FAQ](https://jlcpcb.com/quote/pcbOrderFaq/PCB%20Stackup).
