# Burrito sweep: verdicts and work orders

**22 November 2026.** Claude Fable's reasoning pass, asked for by Seán before S4. It covers: one side or
two, RF shielding and stitching, datasheet layouts, the autorouter, and what may have been missed. It ends
with work orders for the next model.

**Status: recommendations, not decisions.** Nothing here is in `decisions.md`. Each call says how sure it
is (1–5) and what would settle it.

**Grounding.** Each claim is marked:

- **[O]** observed today in the repo or the build;
- **[D]** from a decision row or brief read today;
- **[I]** inferred here from those;
- **[M]** general practice or a datasheet from memory: verify before relying on it;
- **[U]** unknown.

No requirement or interface document was re-read for this pass, and no placed block was compared with its
datasheet figure. Those checks are listed as work, not reported as done.

## 1. Verdicts

| # | Question | Call | Sure | What settles it |
| --- | --- | --- | --- | --- |
| 1 | Parts on a second side? | No for Rev A. It buys about 20 mm, 30 at most (§2) | 4 | Jay's bay length |
| 2 | Shrink Burrito now? | No. Freeze 80 × 180, route it, measure. Cheaper levers exist if needed (§2) | 4 | S5 congestion; bay Rev 2 |
| 3 | Shield cans, or copper walls with solder? | No cans: both radios are shielded modules. Fence the two feed lines (§3) | 4 | First-article GNSS test with LoRa keyed |
| 4 | Stitching vias? | Script them: line fences, a 4 mm grid in the RF zones, 10 mm elsewhere, an edge fence (§3) | 4 | A coverage check after fill |
| 5 | L3? | Make it a second ground plane with power islands. L4 never crosses an L3 gap (§4) | 4 | Seán's yes; a script check |
| 6 | Proper layouts for parts that need them? | Unproven. S3 pulled support parts to their pins; nobody has compared a block with its datasheet (§5) | 5 | S4, block by block |
| 7 | The autorouter? | Keep it, fence it to the non-critical nets, and freeze its output as route files (§6) | 4 | Route metrics; a repeat-build test |
| 8 | J101? | The drawing is read (§10). One feature needs a second look. Its block can shrink | 4 | Molex's own footprint file |
| 9 | J102's screw-down option? | Check it can be bought before anything else: it anchors the aft edge (§7.1) | – | Samtec's page or a quote |
| 10 | J103? | A 2-contact Gecko may not exist. Recommend Micro-Fit 1 × 2 (§7.3) | 3 | Harwin's catalogue; Seán |
| 11 | What sets the order date? | Parts, not routing. Start the long-lead buy now (§7.4) | 3 | JLC sourcing quotes |

## 2. One side or two

### What a second side buys

- 387 of the 559 parts are 0603 resistors and capacitors [O]. Their courtyards come to about 1,670 mm²
  (387 × 4.3 mm²) [I], out of 6,610 mm² for every courtyard [D-21Nov.27]. The parts that could go
  underneath are a quarter of the area.
- The rest can't move: connectors, modules, both MCUs, sensors, electrolytics. The 22 test loops and five
  through-hole connectors already use both sides.
- If 60% of the 0603s went underneath, the top would lose about 1,000 mm². At the placement's packing
  (0.6) that is about 20 mm of length, and 30 mm if every one moved [I].
- S3's sweep put the one-sided floor near 165 mm with no routing room [D-22Nov.10]. Two sides would move
  it to about 140–145 mm [I].

### What it costs

- JLC's Economic assembly is one-sided [D-21Nov.27]. Two sides means Standard assembly: more setup, a
  second stencil, a few more days [M: price it].
- A home second side is harder than it sounds. Order matters: the light side is reflowed first and the
  heavy side second, so heavy parts never hang. JLC would deliver the heavy side done. Reflowing the back
  at home would re-melt the top with the electrolytics, buzzer and radio module hanging [M]. That leaves
  hand-soldering the back. Glue isn't the problem: small parts hold by surface tension [M].
- The placer, the JLC spacing check, the silk pass and the art are built for one side. All four change,
  and S3 is reviewed again [I].
- Decoupling gets slightly worse. L1 is 0.1 mm above its ground plane, so a capacitor beside its pin on
  top beats one underneath through 1.6 mm of via [I].
- It gives up what Seán named: flat on the bench, one service side, a back free for the sled, the legend
  and staking.

### Does 20–30 mm solve anything?

- The bay is 321 mm between lug faces [D-21Nov.6]. Burrito 180 + 7.4 + Churro 120 is 307 mm before any
  plug, cable bend, pack or the CATS Vega, and Churro may grow to 140 [D-22Nov.7].
- So the bay needs Jay's Rev 2, or boards on both faces of the sled, whether Burrito is 180 or 150 [I].

### Call

**Stay one-sided at 80 × 180 for Rev A (4/5).** What would flip it: a bay limit that Burrito plus Churro
miss by 25 mm or less, with no two-faced sled.

If shorter is ever needed, these come before a second side:

| Lever | Gain (inferred) | Cost |
| --- | --- | --- |
| 0402 for pulls, dividers and small decoupling | ≈ 1,000 mm² (387 × 2.6 mm²), about what a second side buys | Harder hand rework. Economic places 0402 [D] |
| J101's block: 20 × 22 mm reserved, about 11 × 9 mm needed (§10) | ≈ 330 mm² on the left edge | None once the footprint exists |
| Test point labels (each counts as courtyard) | ≈ 300 mm² | Labels sit further from their points |
| Fewer through-hole loops (18 orange) | ≈ 250 mm², and 18 fewer pins in the back's legend | Fewer clip-on points |

### What else could go on the back

Nothing with solder. Free things only: the legend and art (done), a white box for a serial number, and
pads for a pogo-pin jig (not worth it for five boards). The Tag-Connect patterns have no parts, but the
back faces the sled, so they stay on top.

## 3. RF: shielding, fences, stitching

What's there: two radios, both shielded modules (Wio-LR2021, MAX-M10S). Each has one 50 Ω line under
20 mm to a vertical SMA at the forward edge [D-22Nov.2]. D4501 sits on the GNSS line [D-22Nov.8]. The
pyro connector J6601 is between the two jacks [O].

1. **No shield cans (4/5).** The modules carry their own. What's exposed is 20 mm of line and two pins.
2. **Feed lines as grounded coplanar waveguide on L1:**
   - recompute the width for the gap chosen: 0.151 mm is the microstrip figure [D-22Nov.2] [M];
   - a via fence on both sides at 2 mm pitch or less;
   - L2 unbroken under the line and 3 mm either side;
   - no via, stub or test point on the line; D4501's pad sits on the line itself;
   - at each SMA, clear L2–L4 round the centre pin as Amphenol's 132134 drawing shows, and put ground
     vias at the four legs [M].
3. **Stitching, by script after fill:**
   - L1 and L4 ground fill to L2 on a 4 mm grid in the two RF zones (λ/20 at 1.575 GHz in FR-4 is about
     4.5 mm [M]) and 10 mm elsewhere;
   - a fence 1 mm inside the board edge at 5 mm pitch;
   - delete any fill island that has no via.
4. **An exposed ground strip for a later lid: optional.** A 1 mm mask opening over a stitched L1 strip
   round each RF zone is somewhere to solder a can or foil if the bench test asks. ENIG covers it; it
   needs no solder. Add it only where the placement leaves a continuous run. Don't move parts for it.
5. **Fire nets and RF:** fire nets leave J6601 aft, never run within 5 mm of an RF line in parallel, and
   cross one only on L4.
6. **Check on the schematic [U]:**
   - the LoRa port: a DC path to ground or an ESD part? An antenna on a rocket collects static, and only
     the GNSS port has D4501;
   - the GNSS antenna supply, if the antenna is active: current-limited as u-blox's manual shows;
   - each pyro output at J6601: a C0G capacitor to ground (100 pF–1 nF), so RF picked up on the e-match
     leads has a path that isn't the switch [M].
7. **Antenna shields and the insulated mounts.** The SMA shells are Burrito's GND. If an antenna or its
   bulkhead connector bolts to conductive structure, GND reaches the airframe there. That's what
   D-22Nov.11's insulated mounts avoid. Ask Jay for insulated antenna mounts.
8. **The test that settles it (first article):** GNSS C/N0 with LoRa transmitting at full power and USB
   active, against both idle. Then the same in the assembled bay, watching the CATS Vega's GNSS and
   telemetry too.

## 4. L3 as ground

- L4 is 0.1 mm from L3 and 1.3 mm from L2 [D-21Nov.26]. A signal on L4 returns in L3.
- D-21Nov.26 makes L3 power pours. Burrito has more than ten rails [O: the test point list]. Cut into
  that many pours, L3 leaves most L4 tracks crossing a gap, with no return path beneath them [M].

**Call: L3 is ground, with power islands (4/5).** It amends D-21Nov.26, so it needs Seán's yes.

1. L3 is GND by default.
2. A rail gets an L3 island only if it feeds four or more loads. Smaller rails run as 0.4–0.6 mm tracks
   on L1 or L4.
3. No L4 track crosses an island's edge. Check it by script: the L3 zone under a track's whole length is
   one zone.
4. The armed-rail corridor on L4 stays over L3 ground [D-22Nov.3].

## 5. Datasheet layouts, keep-outs and pours

State: the placer pulls each two-pin support part toward its IC's pin [O], and the brief's §3a holds the
sensor, crystal and Tag-Connect notes [D]. No placed block has been compared with its datasheet's layout
figure. The only rule areas are the hole keep-outs [O]. S4 does each block as scripted copper and shows
it beside the datasheet figure.

| Block | Hold to ([M] unless marked) | S4 action |
| --- | --- | --- |
| U1301 TPSM63603 | Input capacitors hard against VIN and PGND, output capacitors next, the feedback divider at FB and off the output pour, vias in the ground pads | Compare with TI's figure; script the pours |
| U101 TPS26630, U1101 TPS2121, LM73100 | The 6 A path as L1 pours at IPC-2152 widths [D-22Nov.3]; limit and timing parts at their pins on a quiet ground | Script; report the path's narrowest neck |
| 3× TPS7A91, TPS70933 | Input and output capacitors within 2 mm; noise and feedback parts on the quiet side | Script |
| Pyro: 3× TPS1H100, 3× CSD17318, F6101, F6102, J6601 | 0.5 mm round fire nets [D-22Nov.3]; sense and limit resistors Kelvin at their pins; outputs short and direct | Script every fire, arm and sense net. None goes to the router |
| INA228 and its shunt | Two sense tracks from inside the shunt's pads, run as a pair, filter at the pins | Script |
| U201, U401 | One 100 nF per supply pin on that pin's side; VCAP capacitors within 2 mm; the VDDA filter; reset and BOOT0 parts at the pins | Fanout first: every decoupling via pair before any routing |
| Crystals (2× 16 MHz, 32.768 kHz) | Within 5 mm of the pins, load capacitors at the crystal, a stitched guard ring, nothing under on L1 | Rule area and script |
| USB: J4401, TMUX1511, TPS2553 | 90 Ω pair at 0.154 / 0.203 mm [D-22Nov.2]; CC resistors and any ESD part at the connector | Script the pair |
| CAN: 2× TCAN3413, J501, J502 | CANH and CANL as a pair; termination and any TVS at the connector; the B-39 parts in the reference [D-21Nov.11] | Script the pairs |
| MX66L2G45G | Clock and data as one group: one layer, lengths within 3 mm, ground beneath | Script, or route first as a group |
| LSM6DSV32X, ICM-42688-P, ADXL375 | Nothing under the package on L1; clear of heat, the buzzer, edges and screws [D: §3a] | Rule areas; mark the axes on top silk |
| BMP390, MS5607 | Clear of heat and light; no flux, wash or coating in the vents | Rule areas; "no washing" on the assembly notes |
| MMC5983MA | Far from currents and magnets [D-22Nov.3]. BZ9001 is a magnetic buzzer about 40–50 mm away [O, I]. Its magnet's field there is the size of Earth's (tens of µT) [I: magnet unknown]. The nearest screws are 10–15 mm away [I] | Calibrate in the assembled bay regardless. Ask for brass or nylon screws at the two nearest holes. Move BZ9001 aft only if it's free |
| Wio-LR2021, MAX-M10S | Ground on L1 beneath, no routing under | Rule areas; §3 |
| C1403, C1007, BZ9001 (tall) | They sit in the longest span, between the hole rows at 104 and 175 mm [O] | Stake at assembly; put it on the assembly drawing |
| J102 | Six tails per contact need copper for current and heat to solder | Wide spokes (4 × 0.5 mm), not solid |
| Every 0603 on a pour | Unequal copper on its two pads tombstones a small part | Thermal reliefs on passives; solid on regulators, FETs, connectors |

Rule areas to add at S4: under each MEMS sensor, both radios and each crystal (L1); the two RF line
corridors; J101's real outline; the Tag-Connect clip areas on the back; staking room beside the tall parts.

## 6. Routing and the autorouter

Known: KiCadRoutingTools at 1577fa3 routed TB1 fully, with exact widths, no copper DRC error, the ground
plane unbroken and 172 locked items kept [D-22Nov.1]. Its memory at full size and its repeatability are
untested [U].

1. **Keep it (4/5).** The alternative tested worse, and no new test is wanted.
2. **It finds a path, not a good one [M].** It knows nothing of return paths, crosstalk, Kelvin pairs or
   crystals. So fence what it may touch.
3. **Never autoroute:** RF, USB, CAN pairs, crystals, the flash group, fire, arm and sense nets, shunt
   pairs, regulator loops and feedback, the 6 A path, decoupling fanout, sensor analog pins. Script and
   lock these at S4. That's about 30% of the copper [I].
4. **Autoroute in passes, each locked before the next:** sensor buses, then inter-MCU and GPIO, then
   status and LEDs. L2 is closed to routing. L3 is closed outside allowed areas.
5. **Freeze each accepted pass as data.** Write its tracks and vias to
   `hardware/croi2/layout/routes/<pass>.json`, commit it, and have `build.py` replay it. Then:
   - the build stays byte-identical without trusting the router's own repeatability;
   - a routed net can be diffed and reviewed;
   - a placement change invalidates only nets whose pads moved (hash the pad positions per net);
   - the router isn't needed to rebuild the board;
   - a hand-drawn fix can enter the same way: draw on a scratch copy, capture, replay. D-21Nov.21 holds.
6. **Earn trust with numbers.** Nobody can eyeball 499 connections.
   - Per net: length over Manhattan distance, via count, layers used. Look at any net over 2.5× or over
     four vias.
   - Per board, all zero: L2 cuts, L4 tracks over an L3 gap, tracks in keep-outs.
   - Longest parallel run between an aggressor class (switch nodes, USB, clocks, fire) and a victim
     class (sense, crystal, RF, sensor analog).
7. **After routing, by script:** teardrops at pad and via exits, stitching (§3), fill, DRC.
8. **If it stalls at full size:** route one band at a time with the others locked.

## 7. What may have been missed

Each is a concern to check, not a finding, unless marked [O]. The owner is in brackets.

**Before S4, because they can move parts**

1. **J102.** Samtec's drawing lists the screw-down (-SD) option for existing business only [O: read on
   the drawing today]. If it can't be bought, the footprint and the aft edge change. [next model: check;
   Seán: decide]
2. **J101.** Build it from §10, shrink the reserved block, and the parity error goes. [next model]
3. **J103** is still a JST GH [O], against D-19Nov.5 (Gecko, two contacts). Harwin's G125 range starts
   at six contacts [M], so a 2-contact Gecko may not exist. Recommend Micro-Fit 3.0, 1 × 2: positive
   lock, and the same crimps and tool as J6601 (3/5). [Seán]
4. **Long-lead parts.** The Samtec pair and the SMA jacks are global-sourcing or consigned
   [O: jlc-stock.md]; the Wio-LR2021 and the PUI buzzer aren't in JLC's library [D-21Nov.27,
   D-21Nov.20]. Sourcing takes weeks [M]. Start the buy now, with the MCUs (D-21Nov.19). [Seán]

**Schematic: verify, then fix or record**

5. The LoRa port's static path, the GNSS antenna supply limit, a capacitor on each pyro output (§3.6).
6. USB: an ESD part on D+, D− and VBUS at the connector?
7. CAN: a TVS at each connector?
8. Every fire gate and switch enable safe with both MCUs in reset. The checker asserts the architecture
   (352 checks [O]); confirm its list names each pull-down.
9. J101 and J102 are exclusive by an assembly rule the checker can't see (A17 [O]). Write both BOM
   variants down before ordering.

**Assembly and files**

10. JLC's placement rotations differ from KiCad's for many packages [M]. Build the CPL with a correction
    table, and check every polarised part in JLC's preview before paying.
11. Leave the 25 test pads, the Tag-Connects, fiducials and holes out of the BOM and CPL [O].
12. Thermal pads: paste in windows at 50–80% cover on the custom footprints (TPSM63603, TPS1H100,
    TPS7A91, TPS26630) [M]. Confirm JLC plugs the nine vias under U101 [D-22Nov.2].
13. Mask between 0.5 mm-pitch pins: JLC's smallest bridge is about 0.1 mm [M]. Check the LQFP and VQFN
    mask expansion.
14. J102, USB, the SMAs and J6601 overhang the edge. Tell JLC where the assembly rails' tabs can't go.
15. Ask JLC not to wash the boards (the baros).

**Top silkscreen: cheap, and useful at 6 a.m. in a field**

16. Function names at connectors, not only refs [O: refs only now]: PYRO 1–3 with polarity, CAN 1,
    CAN 2, ARM, ENABLE, USB, GNSS, LORA, SWD FLIGHT, SWD COMMS, 2S PACK.
17. What each LED means; an arrow to the nose; the IMU axes; a white box for a serial number.

**Mechanical and system**

18. Stake the tall parts (§5).
19. J102 mates Churro edge to edge on one sled. The holes' position from the connector datum must match
    on both boards, or one board needs slots. Put the datum in the interface before Churro is placed.
    [next model, Jay]
20. Insulated antenna mounts (§3.7); non-magnetic screws by the magnetometer (§5). [Jay]
21. Bay vent holes set how fast the baros follow the outside pressure, which apogee detection rests on.
    If the airframe is carbon, both antennas need an RF window. [Jay, firmware]
22. The radio check with the CATS Vega in the bay (§3.8).
23. USB is the only way in once the bay is closed. Confirm the panel reaches J4401, and how a bricked
    board is recovered in the bay: the BOOT0 pads are on the board, not the panel [U].
24. Bench tests written before the boards arrive, with inert loads only.

## 8. Work orders for the next model

Do them in order. Stop and show Seán after step 5, with what the ground rules ask: DRC, the unrouted
count, per-layer renders, decisions and doubts.

0. Read this file, `layout-brief.md`, `layout-plan.md` and D-22Nov.1 to D-22Nov.12.
1. Close the blockers: J102's lifecycle (a web check), J101 from §10. J103 waits for Seán.
2. Get Seán's yes or no on: L3 as ground (§4), the Ogham line, the top-silk labels (§7.16–17).
3. Put the rule areas (§5), the net classes and the L3 / L4 plan in the spec.
4. S4 copper by script, in this order: decoupling fanout, RF lines and fences, USB, crystals, the flash
   group, power blocks, pyro channels and the arm corridor, sense pairs, CAN. For each block, a render
   beside its datasheet figure.
5. Checks: DRC; L2 cuts 0; L4 over an L3 gap 0; IPC-2152 width for each power net; keep-outs clean.
   **S4 stop.**
6. S5: router passes, each frozen as route files (§6.5); the metrics (§6.6); teardrops, stitching, fill;
   DRC clean; outputs with a rotation-corrected CPL.
7. After any placement change, rebuild: the back's art re-fits itself round the pins.

## 9. The back

- One side stays (this file's call): keep the back as built. The Ogham line waits for Seán's yes;
  `ogham_text=None` in the spec drops it.
- If a second side were ever used: keep the legend, the parts list, BURRITO with its subtitle, the logo
  and the two lines. Drop the rocket and the Ogham first, then thin the waves.

## 10. J101: what Molex's drawing says

Source: Molex product customer drawing **SD-105311-100, revision H**, "Header of Nano-Fit, S/R, vertical,
clip, power connector", read on LCSC's copy:
`https://atta.szlcsc.com/upload/public/pdf/source/20240628/E7D92444DA1D193B3483D9BAD77A6611.pdf`.
The title, hole sizes and table came out as text; the geometry was read off the drawing at 100% zoom.

- Table row for 105311-1102: A = 8.66, B = 5.94, C = 6.84 mm, 2 circuits, tin.
- "Recommended PCB (connector side view)", board 1.6 to 2.4 mm:
  - two pin holes, Ø1.20 ± 0.05, at 2.50 mm pitch; circuit 1 is the left one in this view;
  - two clip holes, Ø1.60 ± 0.05, on the pin row's centreline, C apart: 3.42 mm either side of centre,
    2.17 mm outboard of each pin;
  - one peg hole, Ø1.30 ± 0.05, 1.34 mm off the row, midway between the pins. A second view, marked
    for 3, 5 and 7 circuits only, shows the odd-count offset;
  - keep-out zone: A wide, 1.74 mm either side of the row.
- Body: housing 3.48 mm deep, centred on the row; 6.34 mm deep with the latch; 9.06 mm tall, 10.51 mm
  with the latch; tails 3.20 mm below the board.
- **Peg side: on the latch side (3.5/5).** The peg hole is drawn below the row with circuit 1 at left,
  the top view above it has the latch toward the bottom of the sheet, and the side view shows a short
  post under the latch side. Confirm it against Molex's footprint file (SYM-105311-XX02) or the drawing
  before the footprint goes in. Everything else above: 4.5/5.
- Footprint notes [I]:
  - a clip pad sits 2.17 mm from a pack pin, so keep the pads small (pin Ø1.8 on a 1.2 mm hole, clip
    Ø2.1 on a 1.6 mm hole leaves 0.22 mm) and give the clips no net. A grounded clip would put GND
    0.2 mm from the pack's positive pin;
  - the peg hole is unplated;
  - the block needs about 11 × 9 mm with the plug, not 20 × 22.
- To see the drawing again: the built-in browser shows it at 100% only if the tab loads in a large
  viewport (4000 × 2750) and is then shrunk to 800 × 550. Clicks don't reach the PDF viewer; scrolling
  does.

## 11. Bets for the taste ledger

Not written to the ledger: the Mac wasn't touched for this. Append them if wanted.

```text
bet  2026-11-22  ogma2  scope  [model] a second side would shorten Burrito by 30 mm at most  4/5  settles: a two-sided placement run, if one is ever made
bet  2026-11-22  ogma2  mech   [model] no shield cans needed: GNSS C/N0 drops under 2 dB with LoRa keyed at full power  3/5  settles: first-article bench test
bet  2026-11-22  ogma2  cost   [model] parts lead time, not layout, sets Burrito's order date  3/5  settles: JLC sourcing dates against the S5 finish
bet  2026-11-22  ogma2  field  [model] Harwin sells no 2-contact Gecko G125  3/5  settles: Harwin's catalogue
bet  2026-11-22  ogma2  form   [model] Seán keeps the Ogham line  3/5  settles: his next look at the back
```
