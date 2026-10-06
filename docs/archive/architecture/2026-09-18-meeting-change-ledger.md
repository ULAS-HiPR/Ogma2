# 18 September: full-meeting change audit

## Investigation follow-through

The [review investigation](2026-09-18-review-investigations.md) now supplies the
broader MCU shortlist, per-function rationale, exact PC13 erratum, rail allocation
comparison, source-boundary recommendation, storage alternatives, RSSI/GNSS
answers, proposed FD frame budget, stall calculation, verified buffer behavior,
indicator/net matrix, reset examples and test matrix. The table below records
the earlier audit state, not the completion state of those desk investigations.
Actual prices, new-family pin mappings, actuator/peer inputs and bench results
remain unverified. No final-stack decision is implied.

Status: extraction and documentation correction; technical investigations remain
open below. This supersedes any implication that the 14 September summary
completed the meeting's requested changes. No CAD or firmware change follows.

Sources: complete 13 September preparation (16:37), recording A (59:25),
recording B (95:00, including adjacent LTS discussion), drive reflection (33:19),
and subsequent user/model reflections. Source IDs and recording/capture distinction
are in the [13 September record](2026-09-13-session-review.md). This audit used
independent requested Luna crawls, with parent reconciliation against repository
and source evidence. Automatic transcription and speaker attribution can err;
model narration, participant guesses and accepted decisions are separate.

## Completion audit — mentioning a request does not complete it

| Request | Current disposition after this pass | Remaining concrete deliverable |
| --- | --- | --- |
| Show every power protection function in order, B 00:07 | Corrected supply diagrams in chapter 2 against netlist | Joint comprehension review; physical response/return and fault-path qualification still open |
| Mark understood passages for skipping, A 57:16 | Explicit subsection marker introduced | Extend only where evidence supports comprehension; never mark silent sections accepted |
| Explain each MCU pin-budget box, A 12–25 | Definitions/corrections present; partial | Per-function what/when/why/fixed-state alternative, with exact net and verification |
| Broader MCU comparison, A 25:27 | Earlier narrow recommendation now labelled challenged | Candidate table with real role requirements, memory, peripherals, package, cost and power |
| Correct energetic versus servo pin interpretations | Corrected from actual audit | Recount only after target architecture is accepted |
| Comms-local recording, A 03:41 and 10:25 | Need captured, unresolved | Data/time/reset/loss/readout comparison of shared-flight versus independent storage |
| RSSI both directions, A 04:41 | Unresolved question | Verify which receiver observes each metric and records it |
| GNSS operating limit, A 07:54 | Open research | Exact receiver limits versus remembered altitude/speed restrictions |
| Two- versus three-rail allocation, A 40:54 | Concrete candidate described, comparison incomplete | Side-by-side complete load allocations, switching policy, fault cases, area and losses |
| Define core input range, A 49:49 | Candidate narrow 2S scope retained | Accepted min/max, thresholds/tolerances, Churro adaptation boundary |
| Explain hold-up delta-V, A 47:48 | Corrected explanation/calculation | Actual capacitor, load, dropout and reset measurements |
| Simplify energetic design, A 53:45 | Challenge recorded; stale “deferred” claim removed | Proportionate fault/alternative comparison; no deletion silently approved |
| Explain reset/staging policy, A 56 | Still partial | Concrete phase examples and reason for each inhibit; separate from retries |
| Inert reset/power interruption test, A 32:42 | Proposed only | Bounded fixture/procedure and observed results; no flight experiment performed |
| Two local servos, B 04:26 | Explicit review decision recorded | Final-stack/CAD/interface reconciliation |
| Explain servo buffer, B 02:21 | Concrete powered/unpowered case rewritten | Confirm component behavior and partial-power test |
| Size simultaneous stall demand, B 03:39 | Requirement captured, unresolved | Selected actuators, duration, supply sag/trip and recovery envelope |
| CAN FD redo, B 10:58 | Direction recorded; Classical table labelled baseline | Bitrates, peers, topology, complete frame inventory and end-to-end deadline budget |
| Canards questions, B 10:34–14:02 | Need/volunteer captured | Written answers; no evidence here that contact happened |
| Diagnostic inventory, B 18:18 | Broad candidate questions already listed; incomplete | Every selected indication mapped to driver, electrical connection, reset state and proof |
| Test/flight state and USB readback, B 14:51–16:38 | Requirements present | Operator sequence and verification behavior in implementation |
| Readable diagrams and spoken review | Power split into three readable views | Check normal-scale reading and spoken explanation of every dense table |
| Remove repetitive caveats, A 45:37 | Still partial | One assumptions/status block per calculation, only specific local uncertainties |
| Chapters 6–8 | Explicitly not reached | Full next-session review; side remarks are not coverage |
| Ownership/recruitment reflection | Engineering lesson retained | Named work only becomes assigned when owner accepts scope |

The chronological extraction below preserves detail behind these work items.
Its “current” assessments describe what the agents inspected before the parent
corrections above. Where they differ, the completion table above governs.
“Decision” in an extraction is checked against the source before implementation;
a read-aloud paragraph without objection is not independently approved.

## Recording A: chronological extraction

Source: voice recording A, 2026-09-13 17:08:52 +01:00, 59:25. Anonymous diarization is unreliable; entries below attribute only explicit wording. “Decision” means an explicit group direction; questions and model prose remain open.

## Opening, scope and system map

- 00:00:30: power schematic shown as bulk battery current/input voltage, 5 mOhm shunt, controlled I2C, USB excluded. **Doc action:** show source, measurement location, USB exclusion and what “downstream” means in the power diagram.
- 00:01:15–01:37: review loop is read → explain/question → decide or request rewrite; next pass should retain understood text and expand confusion. **Doc action:** mark reviewed/understood subsections so the next pass can skip them; never infer acceptance from silence.
- 00:01:46–02:03: “reusable” was unclear; explanation meant a non-disposable flight computer. **Doc action:** define reusable in concrete operational terms.
- 02:03–02:24: the CAN bandwidth calculation for active canard control was said to be “not even close”; the recording does not establish whether it was over- or under-estimating capacity. **Doc action:** do not infer a calculation error from this phrase alone; the later CAN FD direction requires a new explicit timing budget.
- 02:24–02:52: names are canonical, not working names: Burrito core, Churro power, Fajita propulsion. **Decision:** preserve canon names in prose while retaining current filenames/legacy labels where required.
- 02:52–03:14: responsibility map was hard to zoom/read. **Doc action:** make the ownership diagram legible at normal review scale; add explicit role labels.
- 03:14–03:41: Churro supplies Burrito in larger vehicles; Burrito standalone, all sensors, flight processing/state estimation, full-rate local recording/black box; separate comms processor on bounded internal link. **Doc action:** show standalone and vehicle-integrated power/data paths distinctly.
- 03:41–04:47: proposal to record GNSS/radio signal strength/USB logs on comms flash so lost-link timing is recoverable. **Status:** open. Need compare shared flash/two devices/partitioning, data value, power/reset/link-loss behavior and actual signal metrics; do not silently add a device.
- 04:41–04:47: whether LoRa signal strength is equal on both ends is unknown. **Action:** verify telemetry direction/RSSI semantics before claiming symmetric evidence.
- 04:59–05:43: flight-to-Fajita interface is unresolved: state request vs active command over CAN; actuator-board framing may support future onboarding. **Status:** open; document interface alternatives and local authority.
- 05:49–06:00: independent payload never connects to Ogma; its own flight computer/telemetry if needed. **Decision:** keep payload outside main Ogma responsibility map.
- 06:00–06:22: Churro has no state machine; Fajita must enforce engine limits locally, especially overpressure, without waiting on CAN. **Decision:** preserve local propulsion safety boundary.
- 06:22–07:05: two processors separate variable comms work from time-critical flight; not redundant recovery. Comms loss may remove GNSS/radio; bulk recording may fail; flight continues with explicit missing evidence. Flight reset requires retained state/phase validation before recovery continuation and must not ignite sustainer blindly. Whole-board power loss means primary functions unavailable. **Doc action:** retain failure table and separate processor reset from complete power loss.
- 07:05–07:55: ordinary 3–9 km flights versus separated bounded 100 km recorder concept; latter has energetic/servo paths physically unpowered and independent recovery. Phrase was confusing/paranoid. **Doc action:** explain mission boundary and avoid implying this is ordinary active configuration.
- 07:54–08:51: GNSS 80 km claim and altitude/speed restriction were challenged; “and” versus “or” was unresolved; unlocked GPS attractive but difficult. **Status:** research exact receiver datasheet/regulatory constraints; do not state 80 km as universal.

## MCU split, pins and resources

- 08:58–09:12: two processors rationale understood: radio, USB and GNSS have variable latency; flight must not miss measurement/decision deadline while comms services laptop. **Decision:** rationale accepted; keep explanation.
- 09:14–09:52: flight owns sensors, bounded acquisition/decisions, local recording, permitted local outputs; comms owns USB/GNSS/radio; flight may request comms restart; comms cannot reset flight. **Decision:** preserve authority asymmetry.
- 09:53–10:09: “local recording” and “bounded transactions” unclear. **Doc action:** define flash record ownership, transaction bound and behavior on stalled logger.
- 10:25–10:58: comms-local recording for GNSS/USB/radio loss evidence accepted as useful idea but open. **Action:** compare storage architecture and evidence value.
- 11:00–12:41: identical H563 devices simplify tools/spares/bring-up but may waste comms area/cost; smaller comms MCU or one MCU are alternatives. Pin count does not prove CPU fit/reliability. Existing 100-pad audit: flight 20 fixed + 79 connected, comms 20 fixed + 27 connected, 48 unused; two radio reservations and LSE pins may be stale schematic remnants. **Action:** correct unexplained counts and distinguish pin, CPU, memory and workload evidence.
- 13:39–14:22: three isolated SPI buses rationale understood (one sensor short should not take all down); “data ready” means sensor interrupt/ready-to-pull, but prior work was disputed. **Doc action:** define DRDY and verify actual interrupt wiring; attribute historical uncertainty.
- 14:44–15:09: five supply enables questioned; if supplies always on, tie appropriately rather than consume MCU pins. **Action:** for every enable state trigger/use/fault benefit and fixed-state alternative; no blanket enables.
- 15:09–15:45: pressure I2C buses were confusing; other sensors/Churro monitoring allocation uncertain. **Action:** map actual I2C1/I2C2 pressure buses versus Churro I2C4 and label vehicle variants.
- 15:46–16:33: energetic count was hard to parse. The six request/select lines are three pyro channels with two control lines per channel; they are not “three pyros plus three servos”. Two permits + two latch controls and two arm inputs are separate; the arm inputs were described as a physical connector/shorting arrangement, not MCU-controlled arming. **Action:** correct diagram and verify each net against the schematic.
- 16:33–17:40: six current/continuity ADCs were interpreted as servo continuity, then challenged: current at idle cannot prove a particular servo is connected; continuity is meaningful for pyros, not automatically servos. **Action:** split pyro current/continuity from any servo telemetry; verify isolation and whether servo continuity is needed.
- 17:50–18:42: recording interface called QuadSPI versus desired OctoSPI; rate requirement unknown; external NOR confirmed; enable/reset need definition. **Action:** compare actual record rate/latency/power and use correct peripheral terminology (OctoSPI peripheral may still use four data lines).
- 18:50–19:21: servo PWM and power enable unclear; “power enable” was repeatedly questioned. **Action:** name exact controlled rail/load and remove unexplained enable.
- 19:33–20:02: CAN power enable/standby looked invented; their necessity was questioned, not disproved. **Action:** audit schematic, define CAN transceiver power/standby need, avoid pin padding.
- 20:09–20:33: auxiliary monitoring/domain enable and battery+logic ADC unclear or duplicated with I2C monitors. **Action:** identify each measurement path and whether independent ADC evidence earns pin/cost.
- 20:44–21:04: external watchdog concept was unclear; watchdog must be fed after actual essential progress, not merely an interrupt. **Action:** explain monitored heartbeat, timeout/fault output and reset authority.
- 21:27–21:55: HSE/LSE/SWD terminology unfamiliar; LSE purpose unclear; request exact reason and silicon errata relevance. **Action:** define each clock/debug pin, mark optional versus required and cite errata only where applicable.
- 21:55–22:57: “quiet reserve”/PC13 was unexplained; diagram should explain every box beside allocation. **Action:** identify actual net/erratum and state why held quiet.
- 23:12–24:15: big consumers are sensors and output supervision; counts are not proof every test is necessary; six September study reservation versus 79 allocation was confusing. **Action:** replace aggregate rhetoric with per-function table: function, signal, purpose, timing/fault benefit, alternative, connected net.
- 24:15–25:25: PPS, fault input and trace output unclear; GNSS PPS should be defined; fault input source/semantics named; SWO trace marked diagnostic optional if so; unused reservations separated from actual unallocated ports.
- 25:27–27:35: H563 LQFP64 same-family candidate versus H503 smaller MCU; request broader MCU comparison table, not only two parts. Mock firmware was proposed then challenged as unnecessary at pin-only stage. **Action:** perform proportional resource study: pins first, then real USB/GNSS/radio buffering, RAM and deadlines; do not treat mock firmware as agreed requirement.
- 27:48–29:29: DMA reservation (flight 11, comms 6) was unexplained and not evidence of fit; DMA is per-MCU and role-specific. **Action:** show actual peripheral/DMA need and arbitration; remove “same package” implication.
- 29:29–30:14: 1 kHz essential schedule/700 us allowance/128 MHz and an estimator rate mistranscribed as “2 Hz” were discussed (the preserved chapter specifies 200 Hz; the transcript is not authority to change it). RTOS/bare-metal choice unresolved. **Action:** state schedule, blocking bounds, failed-peripheral abandonment and watchdog earned-heartbeat behavior; label figures as budgets until measured.
- 30:14–31:42: program memory/RAM/external NOR distinctions, ECC scope and protected/unprotected RAM were read; ECC was explicitly recognized as answering an earlier question. **Action:** keep explanation; specify critical-state placement and interrupted-write behavior without implying radiation qualification.
- 32:09–32:49: reset is not a new flight; preserve output inhibit, reset cause, identity/time/state validation; possible circuit to remove power mid-flight for testing. **Action:** define reset classes and inert reset/power interruption test, no stationary recalibration/event replay.

## Power path, rails and display

- 33:00–34:07: power diagram was detailed but hard to follow. It shows standalone 2S or Churro feed → input protection → common battery measurement → physical output boundary and logic path; USB is service source only. **Doc action (extraction suggestion, orientation not mandated by the speaker):** draw in a consistent energy-flow direction; label what is source, measurement, protection, permission, regulator and load; distinguish control relationships from energy arrows.
- 34:07–34:52: Burrito current measurement was defended as standalone evidence of servo/pyro electrical response. Physical output energy boundary was mistaken for optical isolation. **Action:** define actual physical arm/current-limit/isolation mechanism; never claim optical isolation without circuit evidence. Current pulse proves electrical response, not actuation.
- 34:58–35:09: “startup bias” and battery/USB source selection were unclear. **Action:** define bootstrap/startup bias as source-control startup power; distinguish it from MOSFET-driver bootstrap and battery enable bias; show USB exclusion from battery/energetic/servo loads.
- 35:09–35:49: three downstream branches were described as flight, comms and optional; purpose is containment of failed nonessential load. **Action:** name actual branch limiter/switch/regulator and loads rather than generic labels.
- 38:07–39:08: optional branch explanation failed: sounder, continuity test, CAN logging, AUX and Churro monitoring were mixed; continuity test supply path made no sense; “AUX” undefined. **Action:** trace each actual schematic load and its return, identify Churro monitoring versus Churro source power, remove proposed/unpopulated feeds from claimed design.
- 39:08–40:54: mechanism definitions (buck, LDO, current limit, reverse blocking, hold-up) were read aloud, but the diagram must show where each sits and its failure boundary. NOR, CAN translator, battery/Churro monitor, sounder and proposed continuity paths need per-load consequence. **Action:** maintain actual load table and branch-fault trace.
- 40:54–42:22: optional rail removal discussion was circular: deleting a rail makes its assigned loads disappear; no reason was given why NOR/CAN must be separate from flight. **Action:** compare three-branch versus two-rail architecture concretely: load current/transients, fault containment, startup, back-power, area and recovery behavior. Do not preserve a rail merely because it sounds cautious.
- 42:22–43:56: current draft recommendation to retain optional rail was not accepted as final. Moving loads onto flight may weaken fault boundary; moving onto comms couples logging/CAN to deliberate comms shutdown; merged rail with equivalent local protection may work. **Status:** open; current three-rail electrical baseline remains until measured comparison.
- 43:56–44:48: explicit challenge: why optional rail at all, and why continuity tests are treated as essential/separate when non-flight-essential. **Action:** state whether continuity is prelaunch flight readiness only, its required timing, energy and fault containment; consider local protection or deletion.
- 44:56–45:36: USB service needs firmware to negotiate/configure after a startup bias begins source control. **Decision:** explanation understood; do not claim bias sets exact negotiated power without USB implementation evidence.
- 45:37–46:38: 2S nominal 7.4 V/8.4 V full charge; power arithmetic and 1.98 W estimate were recognized as estimates, not measurements. **Action:** label all current/efficiency/endurance numbers with input range, load, converter losses and measurement status.
- 46:38–48:38: “usable voltage fall” unclear; capacitor equation is t=C·ΔV/I. 10 ms at 0.25 V needs ~8,000 uF effective; existing ~800 uF is brief dip provision, not loose-connector protection. Capacitor holds flight rail, not NOR/CAN; does not guarantee final log write/message. **Action:** define ΔV as rail drop from starting capacitor voltage to minimum valid LDO input including dropout/path loss; verify C/ESR/leakage/load/reset threshold; use continuous committed recording, no emergency-flush assumption.
- 48:38–49:49: duplicate Burrito/Churro current measurement may add shunt drop, dissipation and little information; the measured battery path excludes USB-only service current. **Action:** keep one measurement where it answers a decision; state the USB exclusion explicitly; separate electrical response from servo movement and propulsion actuation.
- 49:49–51:26: Core input range was missing; nominal 2S is not min/max. Proposal: narrow Burrito input to defined 2S range and let Churro handle higher vehicle battery voltages. **Status:** candidate direction, not accepted. **Action:** specify min/max, UVLO/OVP/ESD/reverse-polarity requirements and source ownership.

## Energetic outputs, reset and mission variants

- 51:29–52:30: energetic section was too abstract: “permission”, “energy path”, “validated phase”, “hardware permissions”, “bounded request” unclear. **Action:** rewrite in plain wiring/state terms and show complete supply/return path, arm boundary, switches, diagnostics and fault paths.
- 52:30–53:07: three existing channels (two recovery, one sustainer) have different hazards; recovery after reset is not sustainer ignition. **Preserved draft policy read aloud:** distinct hazard treatment; the subsequent reset discussion questioned its rationale.
- 53:07–53:45: high-side supply switch and low-side return switch are distinct conditions with different wiring exposures; solid arrows energy, dashed arrows controls. **Action:** diagram legend and truth table must be explicit.
- 53:45–55:42: independent one-shot pulse limiter/non-retriggerable circuit was challenged as unnecessary for dumb set-and-forget e-match firing; no duration requirement or retry need was identified. **Decision/direction:** investigate deletion/simplification; no approval to remove protection yet. For every layer name the fault and test that justify it.
- 55:05–55:38: physical energy isolation likely external arm connector/switch; software cannot make energy available while physically disarmed. **Action:** define physical assembly and proof of disarm.
- 55:42–57:16: reset/staging policy unclear; reset can inhibit further sustainer ignition, but recovery continuation requires validated phase/time/state. A missing request/current pulse cannot prove no physical event. No retry policy was decided or apparently needed for ordinary flights. **Action:** distinguish event repetition, reset-state validation and pulse termination; do not invent retry machinery.
- 57:16–58:13: review method explicitly requested: preserve liked/understood text, mark it for skipping, expand questioned text. Ordinary launch pyro may be simple set-and-forget; space-shot configuration omits pyro circuitry. **Decision:** ordinary and space-shot configurations remain separate.
- 58:35–59:04: servo/CO2 actuation for space shot may use a separate actuator board; board is called actuator board, not CAN board. **Status:** candidate architecture; document as mission-specific follow-up, not ordinary Ogma requirement.

## Cross-cutting doc changes

1. Add a dated source review record linking each chapter/subsection to “understood”, “direction”, “open”, or “not reached”; only material actually read in this recording is marked reviewed.
2. Replace unexplained Mermaid labels with adjacent plain-language rationale boxes or a companion table. Draw power diagrams as energy flow plus dashed control/permission flow, with legends.
3. For every pin/rail/protection part: function, actual net/load, failure addressed, fixed-state/deletion alternative, and verification method.
4. Preserve current electrical/CAD baseline until a decision is explicitly accepted and backed by schematic, calculation or inert test. Do not convert discussion, laughter, or silence into approval.
5. Carry forward unresolved items to next pass: chapters not reached, GNSS restriction evidence, comms storage, CAN FD/latency, MCU/resource comparison, rail comparison, energetic simplification, reset tests.

## Coverage / disposition key

| Ledger area | Recording coverage | Current-document disposition at inspection |
|---|---|---|
| System map, ownership, failure boundaries | Read in full | Mostly represented; improve diagram legibility and standalone/integrated power distinction |
| MCU split and pin allocation | Read in full | Current docs record many corrections; schematic/net verification still missing for disputed counts and enables |
| Power path and rail display | Read in full | Current docs acknowledge open three-versus-two rail question; detailed energy/control diagram and per-load fault trace remain the main rewrite need |
| Energetic outputs and reset | Read in full | Current docs preserve protection as baseline and record simplification as unapproved; one-shot necessity, retry semantics and reset test remain open |
| GNSS altitude restriction | Briefly discussed only | Current docs must retain uncertainty until exact receiver/regulatory evidence is checked |
| Chapters 6–8 of the architecture pack | Not reached in this recording | Do not mark understood or accepted from this source |

## Ogma review (00:00–21:39)

| Time | Evidence | Required change / status | Decision class |
|---|---|---|---|
| 00:00–00:45 | Seán says the power Mermaid is still a simplification: it names branches but does not show the actual electrical path, reverse-polarity protection, current limiting, and what each branch passes through. | **Critical miss:** redraw `02-power.md` as a branch-by-branch electrical path, including source, polarity protection, current limit/switch, regulator, load, return, and fault boundary. The current diagram remains ownership-level only. Add explicit distinction between asserted protection and unselected/unknown parts. | Explicit request; not implemented by the existing pack. |
| 01:44–02:38 | Servo draft says three channels share a battery-derived supply; buffer prevents a live control pin back-powering an unpowered output domain. Room cannot understand “signal buffer” and asks what it means. | Rewrite `04-servos.md` with a concrete powered/unpowered signal-isolation explanation and a small circuit/function diagram. Say explicitly that the buffer is not the servo regulator. | Comprehension failure; required rewrite. |
| 03:21–04:24 | Shared protection/supply means a stalled servo can affect others; group debates stall current and bulk capacitance. | Add aggregate simultaneous stall current, duration/duty, voltage sag, protection trip, capacitor ESR/energy, and recovery requirements. State that bulk capacitance does not substitute for a qualified supply. | Requirement raised; no numeric qualification agreed. |
| 04:26–05:46 | Third local channel challenged. Seán explicitly proposes two Burrito channels; two are enough for canards; grid fins need separate controller; larger rockets use actuator board over CAN and Burrito servo connectors may be unused. | Update `04-servos.md`/overview to record two local channels as agreed review direction, separate grid-fin/remote use, and retain CAD as unreconciled draft until final-stack authorization. Current `04-servos.md` partly records target; CAD still three. | **Decision:** two local channels. Remote/grid-fin allocation remains open. |
| 05:46–07:23 | Central estimate/control versus autonomous local sensing/control. Room says neither wins without actual task. | Preserve both options and add a comparison table keyed to mechanism, loop rate, allowable age/jitter, sensing, reset/link-loss behavior, and bus payload. Include hybrid only as a review option. | Open; no architecture selected. |
| 07:24–09:39 | Model gives Classical-CAN arithmetic and suggests central control with local stale-command response; Seán says select nothing until actuator allowable age/jitter/flight phase are known. | Keep Classical arithmetic explicitly baseline only; add full end-to-end age chain and stale-command behavior. Do not present “central” as accepted design. Obtain canard requirements. | Recommendation only; selection deferred. |
| 10:34–11:24 | Need canard loop frequency and maximum request-to-motion latency. Participant states CAN FD is settled; Seán asks for recalculation and another requirements document. | Update protocol status: CAN FD is an explicit direction, but bitrate, frame contract, peers, topology, compatibility, and qualification remain open. Add a canards requirements request and FD timing budget. Current pack records direction but not the needed concrete contract. | **Direction stated/settled in room; implementation contract open.** |
| 11:57–12:47 | Discussion of future canard sensors (potentiometer, magnetometer) and objection to processing outside flight computer due to complexity. | Add bounded-interface rule: remote actuator may generate PWM and enforce stale-command safety; sensor estimation/vehicle processing ownership must be explicit. Do not add magnetometer/potentiometer to Ogma without vehicle requirement. | Open suggestion; no new sensor decision. |
| 12:50–14:17 | Power follows actuator. High-voltage servo on raw 2S is only an assumption; regulated supply needs conversion, thermal, peak/stall, returned-energy checks. Loaded tests need travel/stall/reconnect/reset/deceleration, not desk motion. | Expand servo chapter with actuator envelope and test matrix. Keep local servo energy links unpopulated. Current coverage is good prose but lacks actual selected actuator values/tests. | Requirement/review direction; no regulator selected. |
| 14:28–15:37 | Five operator questions: main power; identity/build/config; valid progress/CAN; physical output-energy availability; bounded continuity/external circuit. A voltage LED answers only one. | Retain five-question diagnostic model in `05-service-status-time.md`; map every indicator to source, proof, reset default, and failure ambiguity. | Working direction; final inventory open. |
| 15:37–16:38 | USB configurator readback preferred over fragile display; read board identity, running build, profile/config, and verify update outcome. | Current `05` covers this. Add explicit update verification/readback acceptance and keep SWD per-processor boundary. | Reaffirmed requirement. |
| 16:38–18:18 | USB on communications processor; SWD independent. RGB proposed via I2C rather than three PWM pins. Need smart vs dumb LEDs: dumb electrically driven, smart GPIO/driver driven. | Current `05` mentions smart/dumb but still needs an explicit per-indicator table and wiring/driver ownership. Current flight pin budget has no casual GPIO. | Interface selection open. |
| 18:18–19:51 | Request: exhaustive day-of-board diagnostic list, grouped by LED, smart/dumb, connection; CAN should be smart, power/continuity likely dumb, RGB does much of status work; do not merely repeat this meeting—review prior session too. | **Concrete outstanding deliverable:** produce broad inventory then narrow it; add to `05` and implementation reference. Current pack only states the inventory principle, no exhaustive list or grouping. | Explicit request; unfulfilled. |
| 19:51–21:18 | Connectivity and peer health differ; activity light cannot quantify loss. Piezo must be silent in flight; RTC vs monotonic timer; 20 ppm ≈18 ms/15 min; retention/temp/elapsed accuracy need tests. | Current `05` covers these points. Add actual operator sequence and stale/reset/unpowered cases; retain as evidence-pending tests. | Requirements/review directions, no hardware choice. |
| 21:18–21:39 | Ogma review stops because of meeting logistics; next section is LTS. | Architecture README correctly says chapters 0–5 discussed and 6–8 unreached. Do not mark 6–8 accepted. | Coverage boundary. |


## Adjacent LTS recording: covered, kept outside Ogma scope

B 22:19–35:25: preparation proposed unified sensing/control, USB-C recording,
CAN coordination and local physical inhibits; sensor/valve inventory, redline
responses and response-time requirements remained missing. Responsibility for
those inputs was unclear. This does not assign LTS work to Burrito.

B 46:01–1:32:31: full meeting included stand structure/layout, feed diagram,
valve-type corrections, sensor purpose, tank dependencies, controls architecture,
redline/response-time requests and a stated 11 October review date. The floated
10 kHz rate had no established requirement. None of those numbers transfers to
Ogma. B 1:32:34–1:34:53 considered schedule feasibility and a commercial DAQ
alternative; no component selection resulted.

Transferable lesson: request the mechanism, operating envelope, protective
response and maximum delay before selecting sample rates or board partitions.
Keep responsibility with the owning project and record absent inputs explicitly.
No adjacent project was edited.

## Preparation and subsequent reflections: corrections to the earlier read

The preparation discussed distributing ownership and several possible small
projects. They were proposals, not staffed commitments. The later user correction
on 14 September at 00:34 explicitly rejected equating interested recruits with
independent capacity: supervision can increase the existing owner's workload.
The earlier model's optimistic interpretation therefore needs qualification.
Participation, technical contribution, delivery ownership and ongoing coordination
are different commitments; none implies the others.

The drive reflection also contains evidence of collaborators making concrete
progress, including solid-stand instrumentation. Do not flatten the lesson into
“others cannot work.” The project-relevant issue is accepted scope and the cost
of sustaining momentum. Personal/family/career reflections and judgments are not
reproduced here.

Presentation lesson: models must supply explanations that survive questioning,
not force the reviewer to invent the purpose of unexplained generated circuitry.
Use one explicit design recommendation with reasons and a real alternative;
show what remains unknown. Preserve useful text, expand actual confusion, and
keep understanding status independent of acceptance and measured verification.

## Next pass closure rule

For each row, link the resulting diagram/table/calculation/test and mark it
completed, partial, open research, awaiting external input or deliberately
rejected with a reason. A summary is evidence of capture, not evidence that the
requested work happened. Start the next session with changed material and the
remaining 6–8 chapters, keeping a brief whole-system consistency check.
