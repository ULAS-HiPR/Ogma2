# Ogma 2 reliability execution plan

Updated: 2026-09-07

Status: all rewritten EX-01–EX-10 recommended answers accepted by Seán,
including qualifications and connector selection. The
[acceptance record](architecture-acceptance-2026-09-07.md) controls parts,
pin maps, current status and sequencing. The accepted
[rewritten packages](../../architecture-review-2026-09-06/02-work-packages.md)
replace the earlier question-first package definitions below.

**Sequence amendment:** no separate mini-PCB/coupon build before ordering the
first full PCBA. Test those blocks on the first PCBA. Retain pre-order library,
schematic, layout, rating, physical-inhibit and assembly checks. Record unresolved
hardware assumptions and their first-board tests; acceptance is not a claim
that the tests passed or that a respin cannot be required.

The original review's coupon-before-order arrows and closure wording are
superseded by that amendment. Its electrical limits and required evidence are
not deleted. G2/G3 remain qualification/release gates. No purchase, live
energetic test or flight is authorised by this document.

Purpose: take the [reliability review](reliability-design-review.md) to measured
engineering decisions without waiting for a mature space-shot vehicle.

Baseline: [current system](../current-system.md), including its accepted
provisional envelope and MCU-less Foinse. The
[owned interface](../interfaces/ogma-foinse-propulsion-boundary.md) remains in
force. New cross-system decisions require the other owner's review.

## Start here

Current checkpoint: accepted complete architecture and full pin maps; no Ogma 2
schematic or hardware yet. Seán reports Anav received the firmware handoff and
can begin coding. Prepare checked project-local libraries and complete the
schematic/layout/PCBA review in parallel with his firmware work. Do not change
the hardware interface silently or implement Anav's application firmware here.

The first full PCBA is the functional-block test article. Inspect it for
assembly errors/shorts before staged current-limited power-up with inert loads;
then measure power transitions, reset and branch containment. Record external
traces, not merely a debugger message that boot succeeded.

Do not start by implementing every diagnostic in the hardening report, buying
every connector family, or building the full operator application.

## Status and closure rules

- **Not started:** no linked implementation or run evidence.
- **In progress:** named owner, bounded scope, and current artifact/run linked.
- **Ready for review:** inputs and results complete; independent review pending.
- **Closed:** stated closure criteria met and decision recorded.
- **Blocked:** name the missing input and the work that can continue without it.
- **Rejected/deferred:** explicit decision, reason, affected claim, and revisit
  condition. Deferment does not establish flight capability.

EX-01–EX-10 have **accepted recommended answers and design artifacts**. No
package is closed by that acceptance. Host checks exist; target builds,
measurements and installed qualification remain open. Seán retains layout and
Anav retains firmware; other role labels are not assignments. Do not infer
implementation progress from delivery of a handoff.

Create linked working documents only when their task starts. Paths listed as
planned outputs are not claims that those files already exist. Use
[the verification-record template](templates/verification-record.md) for runs.
Keep large raw traces outside Git under a controlled evidence location; retain
a manifest, checksums and retrieval instructions. Keep small reproducible
fixtures, parsers, test cases and concise results in this repository.

## Release gates

Accepted by Seán on 6 September 2026 as part of EX-01. Gate adoption does not
mean any gate has passed.

| Gate | Authorises | Evidence needed | Does not establish |
| --- | --- | --- | --- |
| G0: bounded bench work | Identified low-risk inert experiment | Written stimulus and limits, safe supply/loads, instrumentation, expected result, stop conditions | PCB or flight approval |
| G1: engineering PCB order | Rev A prototype manufacture | Exact part/pin map; power/reset feasibility; output hazard review for the prototype; mechanical fit; assembly and test access; named unresolved risks | Qualified recovery, final mission envelope, or operational reliability |
| G2: installed configuration qualification | Claim against a named accepted environment and mission overlay | Controlled hardware/firmware/harness/bay; performance and fault tests; environmental/RF/service evidence; reviewed residual risks | Acceptance of every produced unit or every future mission |
| G3: unit and mission release | Use of that identified configuration on that mission | Unit acceptance, battery and service-life records, profile/readback, recovery/range review, closure manifest, field rehearsal | Uninspected reuse or a changed configuration |

These gates split evidence obligations. The 7 September amendment allows G1
prototype manufacture without separate pre-order coupon results, with explicit
unverified assumptions and a safe first-PCBA block-test plan. G1 still requires
design inspection and an identified build; it does not grant flight capability.
Available development hardware may support firmware work but is not a new
mandatory board order. Live energetic, propulsion and flight operations require
separate approved procedures and authority.

## Work queue and dependencies

| ID | Work package | Depends on | Roles | Main closure artifact | Gate affected |
| --- | --- | --- | --- | --- | --- |
| EX-01 | Fault allocation and release policy | Current baseline | Systems, firmware, hardware, vehicle reviewer | Fault/phase/capability contract and decision register | All |
| EX-02 | Power and Foinse dependency closure | EX-01 draft | Hardware, Foinse owner, firmware | Source-state/power contract and bench evidence | G0, G1 |
| EX-03 | Reset, time and retained-state semantics | EX-01 draft; EX-02 power classes | Firmware, hardware, vehicle reviewer | Restart contract and reset campaign | G1, G2 |
| EX-04 | Exact MCU, memory and timing spike | EX-02/03 drafts; EX-05 rates | Firmware, hardware, independent pin reviewer | Resource matrix, reproducible build, timing/retention/ECC evidence | G1 |
| EX-05 | Sensor validity and unaided-coast contract | Provisional envelope; EX-01 draft | Estimation, firmware, vehicle | Measurement matrix and replay results | G1, G2 |
| EX-06 | Storage, journal and configuration | EX-03/04; EX-05 data rates | Firmware, host tooling | Byte/endurance/timing budgets and interruption results | G1, G2 |
| EX-07 | Output fault analysis and inert tests | EX-01/02/03; vehicle allocation | Hardware, firmware, recovery reviewer | Channel/function fault matrix and inert evidence | G1, G2 |
| EX-08 | Bay, harness, connectors and environmental path | EX-02/05/07 drafts | Electronics integration, mechanical/structures reviewer | 1:1 service mockup and controlled interface | G1, G2 |
| EX-09 | UART, CAN, USB and operator workflow | EX-01/04/06 | Firmware, host tooling, propulsion interface owner | Versioned contracts and hostile-link/service tests | G1, G2 |
| EX-10 | Integrated fault campaign and flight-readiness allocation | EX-02 through EX-09 | Integration, independent reviewer | Integrated results, residual-risk decisions, release record | G2, G3 |

Draft inputs allow iteration. For G1, distinguish an incomplete/known-invalid
pin, rating or inhibit design from a documented physical assumption to test on
the engineering PCBA. The latter can proceed under the amended prototype
sequence. It must be measured and corrected before its qualified capability
claim; a failed first-board test may require a revision.

## Earlier package definitions — retained test reference

The definitions below preserve the earlier questions, test ideas and closure
criteria. Use the accepted rewritten packages for current answers and the
7 September amendment for test-article sequencing. References below to a
mandatory separate coupon or still-unselected MCU do not override that baseline.

## EX-01 — Fault allocation and release policy

Question: which functions must survive which faults, in which phases?

Policy accepted by Seán on 6 September 2026. The initial
[flight fault contract](../interfaces/flight-fault-contract.md) records the
accepted answers. Timing allocations, mission-specific coverage, named
implementation owners/reviewers and verification remain open; EX-01 is not closed.

Inputs: accepted architecture; Rev 1 flight closure; review sections 1–4 and 8;
the first ordinary-flight and Kármán example mission allocations.

Complete the existing compact contract with:

- function and owning vehicle section;
- phase and physical arm conditions;
- fault being considered, detection method and detection limit;
- accepted response and surviving capability;
- maximum interruption or response time, its rationale and provisional status;
- reset/retention evidence needed;
- independent vehicle coverage and residual common causes;
- test ID and reviewer.

Accepted policy decisions:

1. Contain communications and logger faults in flight; use a bounded validated
   restart for flight-MCU reset; allocate complete flight-power loss to primary
   unavailability and independent recovery. Unexplained faults stop initial
   launch preparation.
2. Essential flight progress earns watchdog feeding. A contained logger fault
   enters supervised degraded recording, not a flight-reset loop.
3. Any in-flight flight-MCU reset inhibits further sustainer ignition for that
   flight. Recovery needs a validated phase-specific path; reboot alone cannot
   authorise it. Exact thresholds and reconstruction mechanisms remain open.
4. Adopt G0–G3 without waiving any existing flight evidence.
5. Require appropriately independent recovery on initial flights with live
   Ogma recovery authority and on the Kármán mission. Later ordinary-flight
   policy requires explicit vehicle review. Exact equipment, coverage and
   common causes remain open; primary recovery still needs qualification.

Closure: each fault invoked in the first bench campaign has a finite expected
outcome, a timing allocation or an explicit unavailable-function outcome, and
an owner/reviewer. No generic safe-state placeholder remains on those rows.

Smallest next action: use the accepted FF-01–FF-04 rows in EX-02's power review.
Then allocate detection/interruption limits and actual test coverage with
EX-03/05/07. Leave unrelated rows open.

## EX-02 — Power and MCU-less Foinse

Question: can the supply start autonomously and contain the failures it claims
to contain?

Seán accepted the five EX-02 defaults on 6 September, then explicitly retained
switching preregulation followed by a low-noise LDO instead of the model's
direct-buck-first preference. The [power contract](../interfaces/power-contract.md)
records the corrected decision, initial drawings and remaining work. EX-02 is
not closed. Complete it with:

- standalone, integrated, and integrated-with-propulsion diagrams;
- MCU-less Foinse device dependencies and startup defaults;
- every permitted battery/USB/charging/source combination and transition;
- input operating limits, source impedance, harness/return paths and load modes;
- branch peaks, current-limit tolerances, isolation/retry behaviour, and upstream
  protection interaction;
- rail-valid limits, supervisor thresholds and tolerances, and maximum allowed
  disturbance/interruption from EX-01;
- powered/unpowered signal paths and measures against back-power;
- mode-by-mode 8-hour operating plus 4-hour reserve energy calculation;
- exact implementation and validation of the accepted buck/LDO chain;
  direct buck and VIOC remain comparison options, not automatically selected.

The cascade is selected as architecture, not as exact parts or a proven rail.
No source range, fuse, hold-up capacitor, regulator part or VIOC loop is selected.
An unspecified battery is not a blocker to a current-limited emulator test;
it is a blocker to claiming real-battery behaviour or freezing input ratings.

### Experiment PWR-01: source transition and branch containment

Setup:

1. Identify the exact development board/coupon, modifications and wiring.
2. Remove all energetic material. Use isolated inert output loads and a
   current-limited source within established component ratings.
3. Before fault injection, measure normal current and rail limits. Define the
   stimulus envelope and instrument ratings. Do not hard-short an unknown
   battery path; use a rated, controlled load/fault fixture.
4. Capture source input, flight rail, affected branch, reset and an essential
   loop timing marker on a common instrument timebase. Use a differential or
   otherwise suitable probing method so oscilloscope grounds do not bypass the
   fault boundary. Record bandwidth, sample interval, probe points and limits.

Run:

- allowed cold starts, slow ramps and source handovers;
- controlled interruptions above and below the proposed hold-up capability;
- communications branch overload/short and persistent retry condition;
- Foinse auxiliary-branch loss and controlled overload;
- powered/unpowered signal combinations;
- representative actuator-load transients using inert electrical loads;
- hot-plug and contact-interruption stimuli within the approved fixture limits.

Save actual waveforms, not just nominal stimulus settings. First characterise
the fixture: its rise/fall time, impedance and lead inductance affect the result.

Pass criteria:

- Foinse's basic source path starts and maintains its required protection without
  Ogma firmware or returned auxiliary power, as the accepted contract requires.
- Contained branch faults do not violate the flight rail or essential timing
  limits allocated before the run.
- Interruptions outside hold-up cause the specified reset/output behaviour,
  not a claim of uninterrupted operation.
- No unexpected back-power, upstream disconnect, destructive excursion or
  uncontrolled retry occurs within the tested envelope.
- Results identify residual faults requiring a separate vehicle solution.

Stop on unexpected output activity, heating, instrument over-range, insulation
failure, or a transient exceeding the approved component/fixture limit.

Closure: one source-state drawing and measured corner-case set supports the
chosen Rev A power topology. The retained Foinse auxiliary return must have
device-level startup/containment evidence; if it cannot meet the contract,
review a local-supply alternative before dependent layout is frozen.

## EX-03 — Reset, retained state and time

Question: what can the computer legitimately reconstruct after each reset?

Seán accepted all five EX-03 defaults on 6 September. The
[reset contract](../interfaces/reset-recovery-contract.md) records reset classes,
two alternating MCU-retained checkpoints, local mission time, deliberate
disarmed new-flight preparation and attempted versus observed action. External
FRAM is not the default. Complete the contract with:

- reset classes and actual retention domains from EX-02;
- cold/maintenance and in-flight startup sequences;
- record schema, integrity/age/flight-identity rules, commit protocol and wrap;
- timing source, reset epochs, retained-clock supply and drift allocation;
- data-loss bounds and behaviour when those bounds cannot be established;
- measured restart stages and phase-specific interruption budgets;
- allowed transitions and actuator evidence policy from EX-01/07.

### Experiment RST-01: restart with known evidence

Initial host-only coverage exists in the
[checkpoint replay](../tests/reset_replay/README.md): 12 test methods pass,
including 420 update-cut cases across synthetic phase transitions/generation
wrap, and 264 single-bit slot-corruption cases. A mutation removing slot
invalidation produces 12 expected failed subcases. These are model results,
not MCU ECC injection, firmware phase reconstruction or timing evidence.

Start with a replay-driven non-actuating phase machine. It needs explicit
inputs and output traces, not a complete flight estimator or live actuator.
Establish a reference uninterrupted run and record its accepted profile ID.

Inject software/external/watchdog resets and controlled power-loss classes:

- before and after each phase transition;
- during each persistent-record operation;
- during sensor acquisition and logger activity;
- with one valid record, corrupt newest record, both invalid, stale prior-flight
  record, and mismatched configuration/calibration identity;
- with lost clock continuity, counter wrap, and sensor/comms reset epochs;
- with logger absent and communications disabled;
- repeatedly while already recovering from a prior reset.

At important boundaries, sweep the injection offset across the operation and
add seeded repeat runs. Record the sweep resolution and coverage achieved;
finite tests do not prove every possible instant.

Measure reset assertion/release, first essential execution, first valid sample,
first valid state, and resumption of optional services using an external clock.
Compare retained values before/after startup. Verify debugger attachment does
not change watchdog or low-power/reset behaviour in the claimed flight mode.

Pass criteria:

- no return to a pad-calibration assumption during an established flight;
- no acceptance of old-flight or incompatible-profile state;
- no actuation authority derived solely from a reboot or error flag;
- every tested loss class either meets its accepted reconstruction/time limit
  or produces the explicit unavailable/degraded outcome;
- no boot loop caused solely by a contained logger/comms failure;
- retained state is not erased by generic ECC/startup code;
- where all retention power is lost, missing evidence is reported honestly.

Closure: each implemented reset class has a trace-backed result and a decision
about the capabilities it does and does not preserve. Never relabel a warm-reset
pass as a complete power-loss pass.

## EX-04 — Exact MCU and resource spike

Question: can an exact candidate implement the minimum core with measurable
memory, timing, reset and diagnostic behaviour?

Accepted defaults, 6 September: H563VIT6/LQFP100 is the first allocation
candidate, not the production selection. Start both roles in the same family;
compare a smaller communications part only for a justified saving. Critical
placement must be checked, initial scheduling/critical-memory reserve is 30%,
clock choice requires workload/power measurement, and development provisioning
stays reversible. The [initial resource allocation](mcu-resource-and-timing-results.md)
contains the exact-part comparison, port reservations, memory budget and gaps.
It is not a complete fit or hardware result.

Compare H563 and H573 first unless a concrete requirement eliminates one.
Other families remain comparisons only where a named constraint demands them.
Development-board availability may choose the first spike; it does not select
the production package.

Complete `docs/mcu-resource-and-timing-results.md` with linked reproducible build
inputs and these matrices; its initial source-backed draft already exists:

- exact orderable part, silicon revision, reference/datasheet/errata revision;
- every pin, peripheral, DMA path, timer and debug/boot constraint;
- usable memory, ECC coverage, region owner and retention conditions;
- startup/provisioning/option-byte readback and recovery path;
- cache/MPU/security choice and relevant errata applicability;
- interrupt/loop/scrub/journal timing, stack usage and resource margin.

First implementation should do only the work needed to prove those allocations:
timestamped acquisition or representative input, bounded core loop, fixed
buffers, restart record, inert output observation, and synthetic comms/storage
load. Normal host USB and radio applications are not prerequisites.

### Experiment MCU-01: memory diagnostics and timing

1. Generate a post-link memory-placement check. Deliberately misplace a critical
   section and show that the build check rejects it.
2. Read back option bytes and the fitted device identity. Refuse the claimed
   ECC test if its required configuration is not established.
3. Exercise real single/double-error diagnostic mechanisms only where the exact
   part supports them. The documented H5 RAM3 test is not automatically a RAM2
   or backup-RAM injection method.
4. Separately corrupt application state and stale/invalid buffers through a
   controlled test interface. Label these software-integrity tests, not ECC
   susceptibility measurements.
5. Check scrub removal, bounded handler time, recurring-error handling and
   concurrency with real interrupt/DMA writers.
6. Run the relevant reset-retention tests, startup erase behaviour, and the
   selected flash operation/errata path.
7. Apply maximum permitted acquisition, traffic, storage and diagnostic load.
   Measure deadlines with production-like compiler/optimisation/cache settings.
8. Repeat without debugger assistance; document diagnostic behaviour when the
   fault path or its storage is itself unavailable.

Pass criteria: each selected feature has source-backed applicability and
measured evidence; unsupported injection coverage is explicit; all critical
allocations fit with reviewed margin; required deadlines hold in the tested
corner cases; no new critical dependency on communications is introduced.

Closure: a candidate can be selected for G1, or rejected with the exact failing
constraint. ECC present in a brochure is not a closure artifact.

## EX-05 — Sensor validity, sampling and unaided coast

Question: do the available measurements support the claimed decisions and
altitude evidence over the provisional mission family?

Produce `interfaces/measurement-contract.md`: channel, units, axis/frame,
physical range, overload survival, bandwidth/filter delay, acquisition rate,
timestamp definition, uncertainty/calibration, validity/freshness, bus and power
ownership, failure indication, and degraded policy.

Distinguish low-altitude GNSS use from the full-envelope altitude proof
instrument. Identify the owner of the latter; do not assume it is Ogma, Mu,
the range, or a future receiver without an accepted interface.

### Experiment SNS-01: reference replay and observability limits

Create a small reproducible scenario set with explicit engineering assumptions:

- ordinary flight with pressure and intermittent GNSS aiding;
- high-altitude unaided interval exceeding each candidate's valid envelope;
- low/high-g overlap, clipping and recovery, gyro saturation, bias steps;
- stale plausible samples, FIFO overrun, dropped samples and timing jitter;
- blocked pressure path and measurement re-entry after saturation;
- reset and lost time during unaided coast;
- shortened/aborted trajectory outside the nominal timeline.

Keep reference truth separate from estimator output and inject faults upstream
of the validation logic. Record units, source, random seed and initial state.
Do not validate an estimator solely against synthetic data generated by the
same model and assumptions without identifying that circularity. Supplement
with Rev 1 replay and later independent simulated/measured trajectories.

Measure estimation error and reported uncertainty, sample age, invalidity
detection, recovery latency and policy output. If the estimator cannot support
a claim, the result must expose that limitation rather than tune a threshold
until the desired event appears.

Pass criteria: frame/unit/time checks pass; invalid data never silently becomes
valid evidence; error/latency limits are allocated before claiming performance;
unsupported flight intervals are explicit; re-entry and reset behaviour meet
the accepted contract. No flight deployment thresholds are released from this
engineering replay alone.

Closure: the sensor shortlist and timing requirements support a named bounded
capability, or the required extra measurement/independent coverage is identified
before its PCB/enclosure interface is frozen.

## EX-06 — Storage, restart journal and accepted configuration

Question: can recording fail without removing control, and can retained data
be trusted after interruption?

Produce `docs/storage-and-configuration-results.md` and implement only the
bounded storage/profile paths needed for the tests.

Budget full-rate volume for 30 minutes, pad/recovery modes, metadata, reserve,
largest record, peak byte rate, maximum device busy time and RAM buffering.
Budget endurance for flights, bench sessions, updates and checkpoint frequency.
Select the device using maximum relevant timings, not only typical throughput.

Separate bulk-log failure from restart-journal failure. If they share power,
bus or silicon, record the common failure and resulting capability loss.

### Experiment LOG-01: interruption and saturation

- Cut power/reset at each real program/erase/commit boundary using controlled
  offsets; verify which completed record is recoverable.
- Exercise full, busy, corrupt, absent/unpowered and bus-clamped storage.
- Corrupt record length/header/payload, address and generation metadata.
- Exercise both configuration slots invalid, incompatible schema, stale upload,
  wrong board/profile identity and interrupted activation.
- Attempt extraction while writing under supported service conditions; check
  that maintenance is not accidentally permitted during armed operation.
- Repeat first-boot access with an empty device and a full device; measure
  restart time versus occupied capacity.
- Run the complete accepted operating/logging duty cycle before claiming
  duration capability. Short accelerated runs are preliminary evidence only.

Pass criteria: bounded parser and driver behaviour; intact prior committed
records remain recoverable within the stated failure model; explicit loss/drop
counters; no silent erase of unexported flights; contained logger failure does
not create watchdog loops; accepted configuration readback matches the active
flight configuration; restart remains within EX-03 bounds.

Closure: a selected storage scheme, capacity/endurance/timing budget and
interruption evidence support the exact claims. All-power-loss evidence limits
remain stated.

## EX-07 — Output hazards and inert actuation

Question: does each electrical output implement the intended physical function
without wrong-channel, premature, repeated or excessive actuation within the
accepted fault model?

First allocate channels to vehicle sections and functions. Reconcile liquid
engine ignition ownership with the propulsion owner before assigning a pin.

Produce `docs/output-fault-analysis-and-inert-results.md`:

- event/function, owning controller and physical mechanism;
- energy source and physical arming boundary;
- evidence for intent, attempted actuation, electrical response and physical
  outcome;
- reset/brownout/invalid-state policy, with recovery and staging separate;
- circuit single faults, cross-channel faults, connector faults and shared
  causes;
- independent coverage, residual risks and reviewer decision.

### Experiment OUT-01: one channel and one direct-timer path

Use a reviewed current-limited fixture and inert loads. Observe the actual
output nodes and load response independently of firmware status. Exercise
power-up/down, programming/reset/watchdog, unpowered logic, broken arm sense,
stale commands, controlled opens/shorts and partial connection in the fixture.
Inject reset around command and evidence-record boundaries.

For servo motion, start unloaded or safely restrained with a bounded mechanism;
then use a separately reviewed intended load. Record physical position or a
witnessed endpoint when making a motion claim. PWM-off alone is not a pass.

Pass criteria are the reviewed per-function truth/fault table, not generic
GPIO correctness. Verify permitted pulse bounds and no unpermitted neighbour
output within the tested cases. Exact energetic electrical limits come from
the selected initiator and approved hazard process, not this plan.

Closure: one reviewed topology and the direct-timer feasibility have inert
evidence adequate for G1. Live energetic qualification remains separate.

## EX-08 — Bay, harness, connectors and environment

Question: can the actual installed assembly be built, inspected, serviced and
qualified without defeating its electrical or contamination boundaries?

Produce `interfaces/avionics-bay-interface.md` when work starts. Include the
envelope, mounts, source/return paths, connector matrix, strain relief, antenna
locations, vents, thermal paths, service access and closure-invalidating work.

Choose a small physical comparison from the existing shortlist. Start with one
credible power family and one signal family plus a justified alternative; do
not buy or populate every listed family by default. Include exact contacts,
wires, crimp tools and housing variants.

### Experiment BAY-01: 1:1 inert service mockup

Install real connectors/cables and representative boards, battery mass,
antennas, inert charge-module stand-ins and service tools. Verify latch/tool
access, wrong-mate prevention, strain relief and independent board removal.
Demonstrate external routine module replacement, USB service and charging
without disturbing internal accepted items.

Record inspection access on both PCB faces, required maintenance openings,
pressure/contamination paths and possible wiring interference with sensors/RF.
Structures reviews load-bearing attachments; electronics owns the functional
integration. Neither review substitutes for the other.

Develop the environmental test specification from the accepted provisional
values. State temperature measurement location, dwell/duty cycle, pressure
profile, shock waveform/duration/axes and vibration method before using a
numerical level as a pass criterion. Early screening is not mission
qualification. Replace provisional profiles with mission evidence before G2.

Closure for G1: representative fit/service evidence and controlled electrical,
mechanical, RF and vent interfaces. Closure for G2 additionally requires the
installed-environment campaign and recorded post-test inspection.

## EX-09 — Bounded communications and operator service

Question: can hostile or broken communications change authority or timing?

Produce one machine-readable source for each implemented link contract when
implementation starts. Generated parsers/definitions share a schema, while
validation and acceptance remain on the owning controller.

Define frame bounds, units, sequence/reset epochs, acquisition versus arrival
time, CRC, freshness, rate limits, timeout and incompatible-version behaviour.
Distinguish configuration proposals from accepted active configuration. Keep
CAN as the named two-node vehicle interface; no production GSE third node.

### Experiment LINK-01: malformed traffic and service interruption

- Flood UART within physical link limits; corrupt lengths, checksums and types.
- Replay old valid data and restart either endpoint independently.
- Hold lines or endpoint power in the permitted fault states.
- Test CAN loss/bus-off and peer failure without importing live propulsion
  authority into the fixture.
- Interrupt configuration and log transfer; suspend/disconnect the host.
- Use wrong device, incompatible firmware/schema and stale host state.
- Verify the minimum offline identify/readback/extract workflow on named macOS
  and Windows configurations.

Pass criteria: essential flight timing remains valid, input buffers and parser
time remain bounded, rejected requests do not change accepted configuration,
and no external message directly authorises recovery/staging. Readback comes
from the responsible device. Electrical endpoint faults also satisfy EX-02.

Closure: protocol, implementation and fault tests agree; the operator sees
actual acceptance/fault state without an expanded UI or undocumented procedure.

## EX-10 — Integrated campaign and flight readiness

Question: do individually working boundaries remain valid together?

Build one identified integrated engineering assembly with the actual power
chain, flight core, chosen sensors/storage, communications load or emulator,
and inert outputs. Record the complete configuration and deviations from the
intended PCB/bay before comparing results.

### Experiment SYS-01: compound mission rehearsal

Run the reference profile and selected fault combinations chosen from shared
causes, not every mathematically possible combination:

- radio peak load while storage is busy;
- communications loss during the pressure/GNSS invalid interval;
- reset during a journal write with a failed bulk logger;
- actuator-load transient with the cold/low-source operating corner;
- sensor restart and stale buffered messages while flight time advances;
- persistent branch fault across several attempted recovery cycles.

Measure rails, input validity, loop deadlines, phase/health, output nodes and
retained evidence on aligned timebases. A pass of separate component tests is
not evidence for these interactions.

Before G2/G3, close mission overlays, recovery/range decisions, RF, installed
environment, actual actuator qualification, camera coexistence if fitted,
manufacturing acceptance, calibration and service-life policy. Obtain an
appropriate exact-part radiation review for the bounded Kármán claim. Software
fault injection does not supply radiation cross-section data.

Pass criteria: every required mission capability has evidence against the
accepted contract; limitations and residual common failures are reviewed;
no unresolved finding invalidates the release claim; the unit configuration
matches what was qualified and rehearsed.

Closure: the appropriate G2 or G3 review is signed. No flight authorisation is
created by completion of this documentation task.

## Numerical closure sheet

Unknown numerical limits must be resolved before a test claims a pass. They do
not block initial characterisation within known equipment/component ratings.

| Quantity | Source of first value | Closes in |
| --- | --- | --- |
| Input range and source impedance | Candidate battery/source plus measured harness; emulator labelled provisional | EX-02 |
| Flight rail validity and branch disturbance | Selected device operating requirements, regulator/supervisor tolerances | EX-02 |
| Branch current and disconnect/retry bounds | Load measurements and protection coordination | EX-02 |
| Mission energy reserve | Measured operating modes against accepted 8 h + 4 h envelope | EX-02, EX-10 |
| Essential loop and response deadlines | Sensor bandwidth and function/phase allocation; provisional rationale recorded | EX-01, EX-05 |
| Maximum restart interruption | Phase/function hazard allocation and measured boot stages | EX-03 |
| Maximum unaided interval and state error | Provisional trajectory family, then mature mission overlay | EX-05 |
| Retained-clock drift and data age | Actual clock/supply configuration and recovery tolerance | EX-03, EX-05 |
| Log capacity, stalls, buffer and endurance | Explicit record schema/rates and selected memory maxima | EX-06 |
| Actuator electrical and physical limits | Selected device/mechanism and approved hazard review | EX-07 |
| Shock/vibration/thermal/pressure test profile | Defined provisional screening profile; later measured vehicle environment | EX-08, EX-10 |

## Earlier decision register — through 6 September

Current selections are in the [7 September acceptance record](architecture-acceptance-2026-09-07.md).
The table below preserves the preceding decision checkpoint; its open/candidate
labels are not the current selection status.

| ID | Decision | Current status | Evidence owner/package |
| --- | --- | --- | --- |
| DR-01 | Phase-aware watchdog and logger-degradation policy | Accepted by Seán, 6 September; essential progress earns heartbeat, contained logger loss enters supervised degraded operation; timing and tests open | EX-01/03/06 |
| DR-02 | Foinse auxiliary return versus local low-power regulation | Accepted by Seán, 6 September: retain protected return; basic source/protection independent of return and Ogma software; local regulation only if reviewed device dependencies require it; tests open | EX-02 |
| DR-03 | Retention supply, time source and supported reset classes | EX-03 defaults accepted by Seán, 6 September; separate reset classes, two-slot MCU checkpoint, local time and deliberate new-flight reset of authority; exact bank/clock/supply/timing and hardware proof open | EX-02/03/04 |
| DR-04 | Exact flight/comms MCU, package and provisioning path | EX-04 strategy accepted by Seán, 6 September: H563VIT6/LQFP100 first candidate, H573 comparator, same-family starting point, checked ECC placement, 30% initial reserve and reversible development provisioning; production selection and target evidence open | EX-04 |
| DR-05 | Sensor validity/error budget and full-envelope altitude proof owner | Open | EX-05 |
| DR-06 | Independent recovery by mission and residual common failures | Policy accepted by Seán, 6 September: required on initial flights with live Ogma recovery authority and Kármán; later ordinary-flight change needs vehicle review; exact coverage open | EX-01/07/10 |
| DR-07 | Per-section output allocation and liquid ignition authority clarification | Open where vehicle-specific; current interface still governs | EX-01/07/09 |
| DR-08 | G0–G3 release-gate allocation | Accepted by Seán, 6 September; no existing flight evidence waived and no gate passed by policy adoption | EX-01/10 |
| DR-09 | Post-reset staging and recovery authority | Accepted by Seán, 6 September: inhibit further sustainer ignition for that flight; recovery only from validated phase evidence; mechanisms and tests open | EX-01/03/07 |
| DR-10 | Initial communications/logger/reset/power-loss allocation | FF-01–FF-04 accepted by Seán, 6 September; numerical limits, mission coverage and evidence open | EX-01/02/03/05/06/09/10 |
| DR-11 | Logic regulator cascade | Accepted by Seán, 6 September correction: switching preregulator then low-noise LDO; direct buck comparison only; exact parts, intermediate voltage and VIOC open | EX-02/04/05 |
| DR-12 | Power branches, USB service and reserve | EX-02 defaults accepted by Seán, 6 September: contain optional branches, USB service without actuator power/backfeed, bounded core hold-up and measured 8 h + 4 h budget; numerical limits/tests open | EX-02/03/07/09/10 |
| DR-13 | Attempted action versus observed result | EX-03 distinction accepted by Seán, 6 September; no blanket replay or blanket suppression policy; mechanism-specific evidence and responses remain open | EX-03/07 |

The [flight fault contract](../interfaces/flight-fault-contract.md) and
[6 September acceptance log](../project-log.md#2026-09-06--ex-01-policy-accepted)
record the accepted choices, rationale, limits and authority. Decisions left
open above are not accepted merely because EX-01 policy is accepted.
EX-02's acceptance and subsequent regulator correction are recorded in the
[power contract](../interfaces/power-contract.md) and
[power acceptance log](../project-log.md#2026-09-06--ex-02-accepted-preregulator-and-low-noise-ldo-retained).
EX-03's defaults and model evidence are recorded in the
[reset contract](../interfaces/reset-recovery-contract.md) and
[reset acceptance log](../project-log.md#2026-09-06--ex-03-accepted-first-host-checkpoint-replay).

When a decision closes, record the actual choice, approving owner, date,
evidence, affected baseline/interface, and reason. Update current-system and
append the project log for real architectural changes. Do not rewrite old log
entries or convert a successful test into broader authority than it supports.
