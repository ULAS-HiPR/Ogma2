# Ogma 2 flight fault contract

**Status, 6 October 2026, amended 2 November: controlling contract.** Electrical
detail describes the 8 September CAD. Decided changes are in
[decisions.md](../decisions.md) and the
[capture specification](../docs/architecture/schematic-capture-spec.md). Capture
waits for Seán's go-ahead.

**What is accepted.** Seán accepted all EX-01 recommendations on 6 September and
asked for them to be recorded before EX-02. That covers the policies below and
gates G0–G3, not every proposal in the wider reliability study. Timing
allocation, implementation and verification are still open. This is not a
finished qualification contract. Authority: [current system](../current-system.md).

On 7 September Seán accepted the integrated review with its qualifications
([decision record](../docs/archive/architecture-acceptance-2026-09-07.md)). It
set starting timing allocations, which are not measured passes:

| Allocation | Value |
| --- | --- |
| Software reset with a valid supply | 100 ms |
| From watchdog assertion through recovery | 400 ms |
| From the last earned heartbeat through recovery | 550 ms |
| Watchdog's own reset assertion | 170–230 ms |

Where those later timing and circuit choices exist, they replace statements
below that nothing is selected. Functional-block hardware tests happen on the
first full PCBA, not on pre-order coupons. G2 / G3 qualification and
mission-release obligations stand.

## Before and after launch

**Before launch**, during early development: an unexplained comms, logger,
flight-MCU reset or flight-power fault stops launch preparation. Diagnose it and
repeat the affected readiness checks. Required local recording must work before
launch. A fault that's tolerable after launch isn't automatically acceptable
before it.

**After launch:** keep essential local flight capability wherever the declared
fault boundary allows, and report degraded or unavailable functions honestly.
Comms and bulk recording gain no authority over recovery just because they're
useful evidence.

**Who decides.** The flight MCU owns these responses. Neither comms nor any
external system directly commands Ogma's recovery or staging outputs. The
[Ogma / Foinse / propulsion boundary](ogma-foinse-propulsion-boundary.md) is
unchanged. This contract doesn't choose a liquid-engine ignition policy.

## Fault responses

| ID | Fault after launch | Response | What survives, and its limit | Evidence |
| --- | --- | --- | --- | --- |
| FF-01 | Comms MCU or link unavailable or misbehaving | Carry on with local flight work. One bounded comms-only restart is allowed when electrically safe; if it keeps failing, leave that branch off. Never reset flight just to get telemetry back | Local sensing, flight decisions and local recording carry on. GNSS aiding may be lost; estimator accuracy and unaided limits stay explicit | EX-02 branch-fault traces; EX-05 unaided replay; EX-09 hostile-link and comms-held-in-reset tests |
| FF-02 | Bulk flight-log device fails | End its transactions within their allotted time, go to degraded recording, carry on with essential work. Keep minimal evidence only where surviving hardware allows. No repeated flight resets to get the log back | Essential sensing and decisions carry on. Full-rate recording is gone; a surviving journal isn't assumed and isn't equivalent | EX-02 electrical containment; EX-03 restart without logger; EX-06 busy, full, corrupt and device-loss tests |
| FF-03 | Flight MCU resets while required supplies stay valid | Bounded restart. Validate the retained flight identity, time and state before restoring any permitted authority. No stationary recalibration, new launch datum, GNSS wait or full-log scan | Recovery may resume only through a validated phase-specific path ([recovery logic](../docs/architecture/10-recovery-logic.md)). Sustainer ignition stays inhibited for the rest of the flight. Not enough evidence makes that primary function unavailable | EX-03 reset, time and retention campaign; EX-05 state reconstruction; EX-07 inert output traces |
| FF-04 | Flight power lost completely | Primary Ogma functions are unavailable while unpowered; independent vehicle recovery covers that hazard. When power returns, classify and validate whatever evidence actually survived. Don't presume a warm reset | No claim of uninterrupted primary flight. Retained state, clock continuity and any recoverable function depend on the actual power-loss class and evidence | EX-02 power-loss classes; EX-03 retention tests; EX-07/10 independent-recovery coverage review |

FF-01 and FF-02 need electrical containment as well as software. A timeout
doesn't disconnect a shorted supply, free a physically clamped shared bus or stop
back-power through signals. The chosen circuits and bus ownership must support
the claimed surviving functions.

The common input, the flight MCU and the PCB stay common failure points. The two
processors (D-6.12) are not redundant flight computers.

## Watchdog

Only essential progress earns the heartbeat: acquisition and validation,
estimation and phase policy, each within its deadline. Bulk logging, radio and
the magnetometer are not in-flight prerequisites (D-2Nov.11).

Degraded mode is still supervised. A logger fault never justifies feeding the
watchdog while the essential loop is dead. Losing required core progress still
triggers the accepted reset or unavailable-function policy. Exact windows and
coordination with external supervision are EX-03/04 work.

## Outputs after a reset

- An in-flight flight-MCU reset inhibits further sustainer ignition for the rest
  of that flight. Only a separate design review can reopen this. Comms coming
  back, or state that looks valid, doesn't lift it.
- Recovery authority resumes only through the accepted phase-specific path,
  backed by trustworthy retained and current evidence.
- A reset or error flag alone never authorises deployment. Missing evidence is
  not permission to fire; the gap needs independent recovery coverage.
- Still in force: the physical arm in the pyro feed, outputs off by default at
  reset, a high side and a low side per channel (D-2Nov.1), firmware-bounded
  pulses with a per-channel current limit, and the staging inhibit (D-6.1,
  D-6.2, D-7.2).
- The power hold is re-asserted within 50 ms of a reset in flight (D-2Nov.4), so
  a restart doesn't also lose the battery enable.

Accepted cost: a recoverable processor reset can end the staging objective.
Reconstruction logic, interruption budgets, actuator-event evidence and how
inhibits persist across power-loss classes still need design and test. No firing
threshold or circuit is chosen here.

## Output hardware this relies on

- Channels 1 and 2 are wired to the recovery domain; channel 3 to staging.
  Profiles can't put sustainer ignition on a recovery channel to dodge the
  post-reset veto.
- Rev A fits all three channels and the stage latch (D-7.1). Channel 3 has its
  own fuse and staging arm (D-7.2, D-2Nov.2).
- Each igniter sits between a high side and a low side on different GPIO ports
  (D-2Nov.1): one stuck pin or one shorted switch can't fire it once armed, and
  the pad checks can see both failures.
- The stage latch: any flight reset clears it asynchronously; its data input is
  the hardware staging-disarmed signal; a deliberate new-flight request (PD15)
  clocks it. Channel 3 fires only while it is set. Reset propagation and inert
  traces still need proof.
- Firmware and a valid checkpoint can't silently defeat physical inhibits.

**Kármán population.** Its energetic and servo sections are unpowered or DNP, so
it makes no primary recovery-actuation claim; the vehicle provides recovery and
full-envelope altitude proof separately. An ordinary active Croí keeps its
recovery duties. Independent recovery stays outside the shared Foinse power-fault
boundary. Nothing here approves a recovery device or a live test.

## Independent recovery

- Required on the first flights where Ogma has live recovery authority, and on
  the Kármán mission. Ogma's own recovery must still be qualified; a backup
  isn't permission to leave it unproven.
- Only an explicit vehicle review can change this for later competition flights.
  A count of good flights doesn't remove it. It adds no third MCU to Ogma.
- No commercial device is chosen. The vehicle review must show sensing and
  deployment across the real mission envelope, its own power and actuation, and
  independent wiring, arming, installation and mechanisms. Shared batteries,
  protection, harnesses, pressure paths or deployment hardware are common causes
  to assess; naming them separately doesn't make them independent.
- A normal barometric backup isn't presumed valid near 100 km.

## Release gates

[G0–G3](../docs/architecture/11-verification.md#release-gates): inert bench
work, engineering-PCB order, installed-configuration qualification, then unit
and mission release (live again from 2 November, D-2Nov.12). Each gate needs its
own evidence and approval. No existing flight obligation is waived. Accepting
the policy doesn't authorise a purchase, a live energetic test or a flight.

## To close EX-01

Seán approves policy. Implementation owners and independent reviewers aren't
assigned yet, and no test has run.

For each exercised row add: the actual phase and arm conditions; how the fault is
detected and the coverage limit; a numerical response and interruption budget
with its reasoning; the supported reset and retention class; mission-specific
independent coverage; a named owner and reviewer; and a linked test result. The
campaigns are in [11 Verification](../docs/architecture/11-verification.md#campaigns);
the full EX-01 closure criteria stay in the archived
[execution plan](../docs/archive/reliability-execution-plan.md#ex-01--fault-allocation-and-release-policy).

Don't invent millisecond limits before the power, sensing and restart work
supports them. Characterisation can go ahead within known fixture and part
ratings, but a pass against a survival or timing claim needs limits declared
before the run. Until then these are accepted requirements, not demonstrated
capabilities.

The [EX-02 power contract](power-contract.md) and the
[EX-03 reset contract](reset-recovery-contract.md) are accepted at policy level.
Their numbers and target-hardware evidence still feed this contract's closure.
Every rewritten EX recommendation is now accepted. Next is library and schematic
work and target evidence, not another round of policy approval.
