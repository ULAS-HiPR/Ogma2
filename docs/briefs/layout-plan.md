# Layout plan: Burrito and Churro

**21 November 2026, v1.** How Claude lays out both boards by script, from the
phase 1 test to the order files. Seán owns both boards and every stop below.
It rests on D-21Nov.21–27 (layout by script, placed fresh, holes, connector ends,
RF, stackup, top-side assembly) and on Burrito's frozen requirements (B-01–B-39).
Each line is tagged:
- *(observed)*: checked;
- *(source)*: read in a cited document;
- *(plan)*: what will be done;
- *(J)*: an engineering judgement Seán can challenge.

## 0. Ground rules

From Seán, 21 Nov:
- The requirements, the schematics and the decided outline are the truth. A gap
  or contradiction goes to Seán; nothing is guessed.
- The board is the output of scripts in the repo, rerunnable from a clean state.
  No hand edit of a `.kicad_pcb`.
- JLC's current capabilities set the stackup and rules, each number cited with
  its page and the date it was read.
- Checked, assumed and unknown stay separate. No check is reported as passed
  unless it ran.
- When a script can't do something well, say so and propose the smallest manual
  step for Seán.

How the grind runs:

| Claude decides alone, and lists it at the next stop | Claude stops and asks |
| --- | --- |
| Placement inside the brief's floorplan | Anything that contradicts a requirement or decision |
| Rule values at or above JLC's minimums | Any schematic change (a part swap is a decision row, then a scripted capture step) |
| Routing order, widths within a net class, via use | A frozen interface (B-36, IR-1–IR-7, J102's place) |
| Cleanup, stitching, silkscreen | Any upload of design data, purchase or message |
| Which tool does a step, inside the chosen pipeline | A check that fails and can't be fixed within the rules |

- Calls (rule 6) are asked only at the stops, batched in one line and skippable.
- Each stop gets a commit on main, a project-log entry and the decisions it made,
  rows in decisions.md once Seán accepts them.
- Bets go to the taste ledger as `dec` lines, and their results as `out` lines.

## 1. Where we start

- **Burrito schematic:** 570 parts, ERC clean with 3 recorded exclusions, and 347
  checks pass (capture step 9, f602a72) *(observed)*.
- **Burrito PCB:** still the 8 September draft: 642 footprints, 141 on the back,
  no tracks and no holes *(observed)*. It is archived, not reused (D-21Nov.21).
- **Churro:** no captured schematic. Its power review comes first (D-21Nov.22).
- **Tools here** *(observed)*:
  - KiCad 9.0.8 from Ubuntu 26.04, in a chroot (`/opt/resolute`), with
    the SWIG `pcbnew` module working on Python 3.14.
  - `kicad-cli` runs DRC, exports (Gerbers, drill, position files, SVG, PDF,
    STEP, IPC-2581, ODB++) and 3D renders.
  - The 26.04 archive has `openjdk-25-jre-headless`, `xvfb` and `cargo`.
- **Facts that shape the choice of pipeline** *(source)*:
  - KiCad's IPC API needs a running KiCad GUI in 9 and 10; headless use
    through `kicad-cli` arrives in KiCad 11. In 9 and 10 it can't plot or export
    ([KiCad dev docs](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/)).
    A CI user ran it under Xvfb
    ([adamws, 2025](https://adamws.github.io/using-the-new-kicad-ipc-api-in-a-ci-environment)).
  - The SWIG `pcbnew` bindings are deprecated as of 9.0, and their removal is
    planned for KiCad 11 ([KiCad dev docs](https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/)).
  - Freerouting is at v2.5.0. It needs Java 25 and runs headless, with a
    DRC report in JSON and a deterministic optimiser. On its own corpus, the
    share of boards it finishes with no DRC violation rose from 30.9% to 75.0%
    ([releases](https://github.com/freerouting/freerouting/releases)).
  - KiCadRoutingTools is an A* router for KiCad 9 and 10 with
    differential pairs, length matching and QFN fanout. It works on the file
    ([repo](https://github.com/drandyhaas/KiCadRoutingTools)).
  - DeepPCB and Quilter are cloud services that take an upload of the design.

## 2. Stops and timeline

Targets assume each stop is reviewed the same day. While one board waits at a
stop, work continues on the other track.

| Stop | What Seán gets | Target |
| --- | --- | --- |
| S1 | Phase 1: the approaches compared on test boards; one recommended pipeline | Sun 22 Nov |
| S2 | Phase 2: the routing brief for both boards; Churro's power review draft | Tue 24 Nov |
| S3 | Burrito: stackup, rules, placement (no routing) | Thu 26 Nov |
| S4 | Burrito: critical nets routed | Sat 28 Nov |
| S5 | Burrito: full route, pours, DRC clean, fab outputs | Mon 30 Nov |
| S6 | Churro: stackup, rules, placement | Sun 29 Nov |
| S7 | Churro: critical nets | Tue 1 Dec |
| S8 | Churro: full route, pours, DRC clean, fab outputs | Thu 3 Dec |
| S9 | Both: sign-off gates (section 7), order files, STEP for Jay's fit check | Fri 4 Dec |
| Order | Seán places both orders | ≈ Sat 5 Dec |

If Churro's review isn't accepted by Wed 25 Nov, Churro moves a week later, as
D-21Nov.9 allows. Burrito keeps its dates.

## 3. Phase 1: pick the pipeline (no layout yet)

### 3.1 Candidates

| Approach | What it controls | How its output is verified |
| --- | --- | --- |
| `pcbnew` Python (SWIG), headless | Everything in the board: setup, stackup, net classes, footprints, placement, tracks, vias, zones and their fill, DSN export and SES import | `kicad-cli` DRC with schematic parity; our own geometric checks |
| IPC API (`kicad-python`) | Board items in a running KiCad GUI; no plotting or export in 9 | The same checks, after saving |
| S-expressions direct (our `sexpr.py`; kiutils or kicad-skip if they read KiCad 9) | Any token in the file; no zone fill, no geometry engine | KiCad loads it; DRC |
| `kicad-cli` | DRC, renders, fab outputs; no editing | It is the verifier |
| Freerouting (DSN/SES) | Bulk routing under net-class widths and clearances | DRC after the SES import; unrouted count |
| KiCadRoutingTools | Bulk routing, differential pairs, fanout, on the file | DRC; unrouted count |
| DeepPCB, Quilter (cloud ML) | Routing (Quilter also places) | DRC after the import; needs an account and an upload |
| Hybrid | Scripted placement and critical nets, router for the bulk, scripted cleanup | All of the above; locked tracks hashed before and after |

### 3.2 Test bench *(plan)*

- **Lab:** `/home/claude/layout-lab`, bound into the chroot at `/lab`. It's
  scratch: the code that survives moves into the repo at phase 3.
- **Versions pinned and recorded:**
  - KiCad 9.0.8;
  - `openjdk-25-jre-headless`;
  - the Freerouting 2.5.0 jar, with its SHA-256;
  - `kicad-python` from PyPI, for the IPC test;
  - `cargo`, if KiCadRoutingTools is tested.
- **Remount:** the chroot's bind mounts drop after a pause. A remount step goes
  into `tools/layout/env.sh`, with a rebuild recipe in case the
  container is replaced.

### 3.3 Test boards *(plan)*

- **TB1, cut from Burrito:** sheets `02-flight-mcu`, `02a-flight-support`,
  `02flight-reset-debug`, `05-can` and `04c-usb-service`.
  - About 80 × 100 mm, 4 layers as D-21Nov.26, with JLC rules.
  - A first scripted placement: ICs anchored, then decoupling and support
    parts pulled to their pins.
  - Nets that leave the cut end at their pad and are dropped from routing.
- **TB2, all of Burrito:** a quick automatic placement in 80 × 230 mm, to test
  router capacity at full size. Its placement is not the final one.

### 3.4 Tests *(plan)*

| Test | Procedure | Measured |
| --- | --- | --- |
| T1 `pcbnew` | Build TB1 from the netlist: footprints from the repo's libraries, references and UUID paths, nets, outline, stackup, net classes, custom rules, placement, GND zones, zone fill. Build it twice | Build time; DRC; the two builds byte-identical or not |
| T2 S-expressions | Round-trip TB1 through `sexpr.py`; move a part, add a track, a via and a zone by text; check whether kiutils and kicad-skip read KiCad 9 | Byte-identical round trip; KiCad loads it; DRC |
| T3 `kicad-cli` | DRC to JSON; SVG of each layer; 3D render; Gerbers, drill, position files; a JLC BOM and CPL by script | Each runs; time; output readable |
| T4 Freerouting | DSN export, a headless run with a pass limit, SES import, DRC. Run twice | Completion; DRC by type; vias; length; time; determinism; whether net-class widths and clearances hold |
| T5 Hybrid | Script and lock TB1's critical nets (HSE crystal, USB pair, CAN pairs, VCAP, supplies); Freerouting for the rest; a cleanup script | Locked tracks unchanged (hash); completion; DRC |
| T6 IPC API | `pcbnew` GUI under Xvfb with the API server on; open TB1, list footprints, move one, add a track, save | Works or not; time per operation; popups and crashes |
| T7 KiCadRoutingTools | Build its router; route TB1 | The T4 metrics, side by side |
| T8 Cloud ML | Not run without Seán's OK: it needs an account and an upload of design data. Survey from their own documents; a trial would use a synthetic board, not ours | Published claims only, marked as such |

TB2 then runs the router or routers that come out of T4–T7 best.

### 3.5 How the pipeline is chosen (*J*, in this order)

1. **Verifiable and replayable** from the repo, from a clean state.
2. **Control** over critical geometry: exact widths, lengths, layers, via fences.
3. **Completion and DRC** on TB1 and TB2.
4. **Time** to Burrito's S5.
5. **Maintenance risk:** SWIG is removed in KiCad 11; IPC needs a GUI until then;
   external services can change.
6. **Cost and data sharing.**

### 3.6 S1 deliverable

`docs/briefs/layout-pipeline.md`:
- the comparison table with the test evidence;
- the recommended pipeline, with its reason, downside, one real alternative,
  confidence and the smallest test that would overturn it.

Claude stops for Seán's pick.

## 4. Phase 2: the routing brief

### 4.1 Inputs to collect *(plan)*

- **JLC stackup:** the exact order name, thicknesses and Dk for the 0.1 mm-prepreg
  stackup. Then 50 Ω single-ended and coplanar widths and the 90 Ω USB pair,
  from JLC's impedance calculator, read in the browser, with page and date.
  A closed-form estimate cross-checks each width.
- **JLC fabrication rules, read 21 Nov 2026**
  ([PCB capabilities](https://jlcpcb.com/capabilities/PCB-capabilities)):
  - 1 oz track and space 0.09 / 0.09 mm;
  - via hole 0.15 mm minimum (0.2 mm preferred), via pad 0.25 mm minimum;
  - annular ring 0.15 mm minimum, 0.20 mm recommended;
  - hole-to-track 0.2 mm (via), 0.28 mm (PTH);
  - mask bridge 0.10 mm;
  - silkscreen line 0.15 mm, text 1.0 mm;
  - copper to a routed edge 0.2 mm.

  Rules are set above these minimums wherever the board allows *(J)*.
- **JLC assembly** ([assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)):
  - Economic vs Standard;
  - component spacing and edge clearance, fiducials and THT rules, from JLC's
    help articles;
  - whether Economic takes an impedance stackup.
- **Currents per net:**
  - from the schematic and `interfaces/power-contract.md`: the 6 A
    source path at J102, the ≈2 A pyro pulses, each 3.3 V rail's sum, and
    USB's 387 mA;
  - widths from IPC-2152 charts at a stated temperature rise, cited.
- **Layout pages of the datasheets:** TPSM63603, TPS26630, LM73100, TPS7A91,
  TPS2121, STM32H563 (HSE, VCAP, VDDA), TCAN3413, TPS1H100, CSD18540,
  INA228, Wio-LR2021, MAX-M10S, LSM6DSV32X, ICM-42688-P, ADXL375, BMP390,
  MS5607, MMC5983MA, USBLC6 and Samtec MPT.
- **Mechanical:**
  - holes (D-21Nov.23), connector ends (D-21Nov.24), J102's edge datum (IR-3);
  - plug heights within the ≈33 mm each side (D-21Nov.6);
  - parts over 7 g to stake (B-33).
- **Footprint audit before placement**, on every custom `Ogma2:*` footprint
  against its datasheet. First the known ones:
  - the USB-C mismatch (current-system);
  - the MMC5983MA pads;
  - C1403's land pattern;
  - J101 (Molex's drawing, read in the browser).

### 4.2 The brief: `docs/briefs/layout-brief.md`

Seán's nine points, for each board:
1. outline, holes, keep-outs and fixed connectors;
2. stackup, layer use and the return path of each signal class;
3. floorplan by subsystem, and why each group sits where it does;
4. power: protection, regulator loops, copper per rail, thermal relief, planes;
5. net classes and rules: widths, clearances, pairs, impedance, length,
   high-current nets;
6. routing order;
7. flight concerns: vibration, shock, thermal, EMI between radio, switchers
   and sensors;
8. DFM and DFA for JLC;
9. what must pass before sign-off.

Every point is tagged:
- **[R]**, fixed by a requirement or decision, cited;
- or **[J]**, Claude's judgement, with its reason.

Churro's section is written against its accepted review.

### 4.3 Churro's power review, in parallel

`docs/briefs/churro-power-review.md`. It gives a recommended answer for each open
item, in the design-review format (recommendation, reason, downside, alternative,
uncertainty, smallest test):
- ACT and PROP at ≈15 A peaks (controller and FET);
- the three chargers (2S, 6S, 1S) and their temperature gate;
- damping at J801, and the J801 part;
- the CATS cell lead;
- the I²C additions (an expander, a second ADS1115 at 0x49);
- the outline length.

C-02's branch ratings stay Seán's call unless he hands them over.

### 4.4 S2

The brief and the review go together. The accepted points become decision rows.

## 5. Phase 3: Burrito by script

### 5.1 Where the code lives *(J)*

- `tools/layout/` holds the engine (`/hardware/tools/` is ignored as old scratch), shared by both boards:
  - `build.py` is the entry point;
  - `board.py`, `place.py`, `route.py`, `pours.py`, `checks.py`, `outputs.py`;
  - `env.sh` sets up the environment.
- `hardware/croi2/layout/` holds Burrito's spec, which is data:
  - outline and holes, fixed parts, floorplan regions, net classes, rules;
  - the critical routes;
  - stored router results, such as an SES file.
- `python3 tools/layout/build.py croi2 --to <stage>` writes
  `Croi2.kicad_pcb` from the netlist and the spec, from nothing.
- Reports go to `hardware/croi2/output/layout/`.
- A router's result is stored in the repo and replayed by the build. Running the
  router again is an explicit flag, so every rebuild gives the same board.
- The 8 September PCB moves to `history/` before the first generated board.

### 5.2 Build stages

| Stage | Does | Check before going on |
| --- | --- | --- |
| 0 Setup | 80 × 230 outline; eight M3 holes as board-only footprints; 3 fiducials; stackup; design settings; net classes; custom rules (`.kicad_dru`) | Board loads; rules parse |
| 1 Parts | Every footprint from the netlist, with UUID paths, fields, DNP and nets | Parity 0 |
| 2 Placement | Section 5.3 | Courtyard overlaps 0; keep-outs clear; all on top → **S3** |
| 3 Critical nets | Section 5.4, scripted, then locked | DRC on those nets → **S4** |
| 4 Bulk | The S1 pipeline, under the net classes | Unrouted 0 |
| 5 Pours | L2 solid GND; L3 rail pours; L1 and L4 GND fill; stitching and via fences | DRC; zones filled |
| 6 Silkscreen | Polarity and pin-1 marks on every polarised part: JLC reads polarity from the silkscreen, emails if it can't, and follows the silkscreen over the CPL when they disagree ([JLC assembly FAQ 2](https://jlcpcb.com/help/article/pcb-assembly-faqs-part-2), updated 9 Sep 2026). References where they fit at JLC's 1.0 mm minimum, an assembly drawing (F.Fab) with every reference, connector labels, board name, revision and date | Every polarised part has a mark that matches its pad 1; text ≥ 1.0 mm |
| 7 Outputs | DRC, per-layer renders, 3D render, Gerbers, drill, JLC BOM and CPL, STEP | Section 7 → **S5** |

### 5.3 Placement method *(plan; the floorplan itself is in the brief)*

1. **Fix what is fixed, before anything else moves.** Every connector sits on a
   board edge, facing out (D-21Nov.24): right-angle ones (J102, J4401, J6601)
   open past their edge; vertical ones stand at the edge with latch and cable
   toward it. Their coordinates are written in the board spec, never chosen by
   the optimiser:
   - the holes;
   - J102 centred on the aft edge, datum at the edge (IR-3);
   - the aft-third connectors (J101, J6101, J6102, J103, J501);
   - J6601 forward;
   - both SMAs in the forward corners beside their modules.
2. **Regions:** each subsystem gets a region from the brief's floorplan.
3. **Anchor parts** go first: the MCUs, regulators, eFuse, modules, sensors and
   connectors.
4. **Support parts:** each decoupling capacitor goes to the pin it serves, and
   each passive chain to its pins. A legaliser keeps courtyards apart, with JLC's
   spacing, then improves wire length inside each region.
5. **Rotation:** large MLCCs lie across the board's long axis, against bending
   strain (B-33) *(J)*. Polarised parts share an orientation where they can.
6. **Measured:** wire length, density per region, overlaps, keep-out hits.

### 5.4 Critical nets on Burrito *(plan; widths come from the brief)*

- **RF:** U4606 → J4601 and U4504 → J4501. 50 Ω on L1, no vias, a via fence
  each side, D4501 at its SMA.
- **Clocks:** both HSE crystals (Y201, Y401) and the 32.768 kHz crystal. Short,
  symmetric, ground-guarded, nothing routed under them.
- **TPSM63603 (U1301):** input and output capacitor loops, per TI's layout page.
- **High current:**
  - J102 pins 1, 2 and 4 → U101 → Q101 at the 6 A path;
  - `ENERGY_TAP` → F6101 / F6102 → J6101 / J6102 → the armed rails → TPS1H100 →
    J6601 for the 2 A pulses;
  - and their returns.
- **Sense:** a Kelvin connection from R7101 to the INA228 (U7101).
- **Pairs:**
  - USB D+ / D− at 90 Ω;
  - CAN bus 1 and bus 2 H / L, coupled;
  - the B-39 series footprints, in each CAN reference.
- **MCUs:** VCAP, VDDA / VREF+, decoupling, NRST, BOOT0, SWD.
- **Sensors:** SPI through the damping resistors, I²C, interrupts. No current
  carrying copper under or near the MMC5983MA.
- **Fire nets:** kept apart from each other and from noisy nets (B-02's intent)
  *(J)*.

### 5.5 Bulk route, cleanup, pours

- **Bulk:** the S1 pipeline with the net classes.
- **Cleanup script:**
  - removes dangling stubs;
  - checks that no acute angles were added;
  - re-hashes the locked tracks.
- **Stitching vias** *(J; final pitch in the brief)*:
  - about every 5 mm along the board edges and the RF lines;
  - about a 10 mm grid elsewhere.

### 5.6 What each stop shows

- DRC (`kicad-cli`, JSON, summarised by type) and the unrouted count.
- A render of each layer: F.Cu, In1, In2, B.Cu, F.Silk, F.Mask, Edge.Cuts.
- A 3D render.
- The metrics.
- The decisions made, and the ones Claude is unsure of.

### 5.7 Order package

- **Gerbers and drill** from `kicad-cli`.
- **The JLC BOM and CPL**, by script:
  - LCSC numbers from `jlc-stock.md`;
  - a table of JLC rotation offsets, checked against JLC's own preview at
    upload (Seán's step).
- **Two BOMs** for the source variants (D-21Nov.9): J101 fitted on the
  standalone boards, J102 on the rest.
- **A STEP export** for Jay's Onshape fit check (EX-08). The missing models
  are flagged in it.

## 6. Churro track

1. Seán accepts the power review at S2. Its points become decision rows, and
   `churro.md` freezes.
2. A capture specification for Churro, then scripted capture steps, as Burrito
   had:
   - `kicadsch.py`, step scripts and checks;
   - exact netlist deltas, ERC clean;
   - its own checker.
3. JLC stock for Churro's BOM.
4. Layout with the same engine: Churro's spec in `hardware/foinse2/layout/`,
   stops S6–S8, then sign-off at S9.

## 7. Gates before sign-off (both boards)

Each gate is checked by a script or tool, and its output kept.

1. **DRC:** 0 errors and 0 unconnected; each warning listed with its reason.
2. **Schematic parity:** 0 (DRC with parity).
3. **Board checker assertions:**
   - no copper or part in the hole keep-outs;
   - RF widths and no vias on RF;
   - high-current widths at least those computed;
   - net-class compliance;
   - the magnetometer keep-out;
   - no part on the bottom;
   - fiducials present;
   - JLC component spacing and edge clearance;
   - test points reachable;
   - courtyard overlaps 0.
4. **Fabrication and assembly files:**
   - the Gerbers render back;
   - every BOM line has an LCSC number or a sourcing route;
   - every CPL line matches the board.
5. **Footprint audit complete;** G1's footprint, rating and assembly review done.
6. **STEP exported** for the fit check.
7. **Seán's own visual pass** of the renders, then JLC's online DFM at upload
   (his step).

## 8. Risks

| Risk | Mitigation |
| --- | --- |
| The router struggles with the 0.5 mm-pitch LQFPs and the QFN thermal pads | Scripted fanout before the bulk route; TB1 measures it in phase 1 |
| Autorouted tracks need heavy cleanup | Hybrid: what matters is scripted and locked; the router only does the bulk |
| SWIG is gone in KiCad 11 | Pin KiCad 9.0.8 in the chroot. Keep the engine's KiCad calls in one module, so an IPC port is contained |
| Zone fill or DSN export loses rules (keep-outs, edge clearance) | Freerouting's copper-to-edge flag; DRC after every import; rule areas re-checked by our own checker |
| Custom footprints are wrong (the USB-C mismatch is known) | The footprint audit before S3 |
| JLC rotation offsets wrong in the CPL | Offset table, plus JLC's own preview at upload |
| The container is replaced and the chroot lost | Rebuild recipe in `env.sh`; versions recorded |
| The context is compacted mid-grind | This plan's progress list and the project log are the state; each stop is committed |
| Churro slips | Burrito's dates don't depend on it (D-21Nov.22) |
| Two weeks is tight | Stops are reviewed the same day; Burrito and Churro alternate while one waits |

## 9. What others hold, and when it's needed

| Who | What | Needed by |
| --- | --- | --- |
| Seán | S1 pick; S2 brief and review; S3–S8 stops; JLC upload, DFM and the orders; the MCU buy (D-21Nov.19) | Each stop |
| Seán | Molex 1053111102's PDF, only if the browser can't read it | S3 |
| Seán | OK for any cloud-router trial (T8) | Only if wanted |
| Jay | The bay length or a two-sided sled (D-21Nov.24); the sled and its standoffs (D-21Nov.23); the STEP fit check (EX-08) | Before the order, ideally by S5 |
| Jay and Arnav | Antennas and RF window (B-25): coax lengths only; the board doesn't wait | Before integration |

## 10. Doc fixes found on the way

- `docs/briefs/access-panel.md` still proposes Micro-Fit 3.0 for J6101 / J6102.
  D-21Nov.12 decided Mini-Fit Jr. and JST VH.
- Foinse2's README and AGENTS still describe the 60 × 80 mm draft
  (D-21Nov.6, D-21Nov.22).
- `docs/pcb-layout-guide.md` describes the 8 September placement. It is kept for
  its circuit notes (C04–C14) and is superseded by the brief at S2.

## 11. Progress

- [x] Open points decided (D-21Nov.21–27, 65512f1)
- [x] S1 phase 1: bench, TB1, T1–T7, TB2, report (docs/briefs/layout-pipeline.md); Seán picked the KiCadRoutingTools hybrid (D-22Nov.1)
- [x] access-panel brief's J6101 / J6102 line fixed
- [ ] S2: Burrito's half of the routing brief drafted (docs/briefs/layout-brief.md, 22 Nov); Churro review and footprint audit next
- [ ] Burrito D4501 swap (decision row and capture step), if Economic assembly is kept
- [ ] S3 Burrito placement
- [ ] S4 Burrito critical nets
- [ ] S5 Burrito full route, outputs
- [ ] Churro capture
- [ ] S6 Churro placement
- [ ] S7 Churro critical nets
- [ ] S8 Churro full route, outputs
- [ ] S9 sign-off gates, order files, STEP
