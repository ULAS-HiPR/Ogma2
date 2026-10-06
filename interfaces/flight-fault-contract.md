# Ogma 2 flight fault contract

**Status (6 Oct 2026):** controlling contract. Electrical details describe the
8 September CAD; decided changes are in [decisions.md](../decisions.md) and the
[capture delta](../docs/architecture/schematic-capture-spec.md). Capture waits
for Seán's go-ahead.

Updated: 7 September 2026
Status: EX-01 policy accepted by Seán; timing allocation, implementation and
verification remain open. This is not a completed qualification contract.

Authority: [current system](../current-system.md). Seán accepted all EX-01
recommendations on 6 September and requested that they be recorded before
continuing to EX-02. Acceptance covers the policies below and G0–G3, not every
proposal in the wider reliability study.

## Subsequent accepted implementation — 7 September

Seán accepted the complete integrated review with its qualifications; see the
[decision record](../docs/archive/architecture-acceptance-2026-09-07.md). It supplies
initial timing allocations, not measured passes: 100 ms valid-supply software
reset, 400 ms from watchdog assertion and 550 ms from last earned heartbeat
through recovery. The watchdog has its own 170–230 ms reset assertion.

Channels 1/2 are hardwired into the recovery domain; channel 3 into staging.
Profiles cannot put sustainer ignition on a recovery channel to bypass the
post-reset veto. Stage eligibility uses a supervised asynchronous clear and
hardware disarm qualification on the latch data input, with a raw deliberate
new-flight request on the clock. Reset propagation and inert traces still need
proof. Rev A populates channels 1/2 only; channel 3 and the stage latch stay DNP
until a multistage flight is scheduled (D-6.2). Firmware and a valid checkpoint cannot silently defeat physical inhibits.

The Kármán population has physically unpowered/DNP energetic and servo sections.
It therefore has no primary recovery-actuation claim; the vehicle separately
provides recovery and full-envelope altitude proof. Ordinary active Croí retains
its recovery duties. Independent recovery stays outside the shared Foinse
power-fault boundary. No recovery device or live test is approved here.

The following original fault policies remain; later timing/circuit selections
in the accepted review supersede statements that those are wholly unselected.
Functional-block hardware tests move to the first full PCBA, not pre-order
coupons. G2/G3 qualification and mission-release obligations remain.

## Scope and phase policy

During initial development, an unexplained communications, logger, flight-MCU
reset or flight-power fault stops launch preparation. Diagnose it and repeat
the affected readiness checks. Required local recording must work before launch.
A fault tolerated after launch is not automatically acceptable before launch.

After launch, preserve essential local flight capability where the declared
fault boundary permits it. Report degraded or unavailable functions honestly.
Communications and bulk recording do not gain authority over recovery merely
because they are useful evidence paths.

The flight MCU owns these responses. Neither communications nor an external
system directly commands Ogma's recovery or staged-flight energetic outputs.
The [Ogma/Foinse/propulsion boundary](ogma-foinse-propulsion-boundary.md) is
unchanged. This contract does not select a liquid-engine ignition policy.

## Accepted initial fault allocation

| ID | Fault after launch | Accepted response | Surviving capability and limit | Evidence package |
| --- | --- | --- | --- | --- |
| FF-01 | Communications MCU/link unavailable or malfunctioning | Continue locally owned flight work. A bounded communications-only restart is permitted when electrically safe; persistent failure leaves that branch disabled. Never reset the flight MCU merely to restore telemetry. | Local sensing, flight decisions and local recording continue. GNSS aiding may be lost; estimator accuracy and unaided limits remain explicit. | EX-02 branch-fault traces; EX-05 unaided replay; EX-09 hostile-link and comms-held-reset tests |
| FF-02 | Bulk flight-log device fails | End failed-device transactions within their allocated bound, enter degraded recording, and continue essential work. Preserve minimal evidence only where surviving hardware permits it. Do not enter repeated flight resets to regain the log. | Essential local sensing and flight decisions continue. Full-rate recording is no longer available; a surviving journal is not assumed or equivalent. | EX-02 electrical containment; EX-03 restart without logger; EX-06 busy/full/corrupt/device-loss tests |
| FF-03 | Flight MCU resets while required supplies remain valid | Use a bounded restart. Validate retained flight identity, time and state before restoring any permitted authority. No stationary recalibration, new launch datum, GNSS-acquisition wait or full-log scan. | Recovery may resume only through a validated phase-specific path. Sustainer ignition remains inhibited for the rest of the flight. Insufficient evidence makes the affected primary function unavailable. | EX-03 reset/time/retention campaign; EX-05 state reconstruction; EX-07 inert output traces |
| FF-04 | Complete loss of flight power | Primary Ogma functions are unavailable while unpowered. Independent vehicle recovery covers the allocated recovery hazard. On power return, classify and validate the actual surviving evidence; do not presume a warm reset. | No uninterrupted primary-flight claim. Retained state, clock continuity and any recoverable primary function depend on the actual power-loss class and evidence. | EX-02 power-loss classes; EX-03 retention tests; EX-07/10 independent-recovery coverage review |

FF-01 and FF-02 require electrical as well as software containment. A timeout
does not disconnect a shorted supply, release a physically clamped shared bus
or prevent back-power through signals. The selected circuits and bus ownership
must support the claimed surviving functions.

The common input, flight MCU and PCB remain common failure points. Two Ogma
MCUs are not redundant flight computers.

## Watchdog policy

Essential acquisition/validation, estimation and phase-policy progress within
their deadlines earn the heartbeat. Bulk logging and radio progress are not
unconditional in-flight prerequisites.

Degraded mode remains supervised. A logger fault cannot justify feeding the
watchdog while the essential flight loop is dead. Loss of required core
progress still invokes the accepted reset/unavailable-function policy; exact
windows and coordination with external supervision remain EX-03/04 work.

## Output authority after reset

- An in-flight flight-MCU reset inhibits further sustainer ignition for the
  remainder of that flight. Reopening this rule requires a separate design
  review; restoring communications or apparently valid state does not lift it.
- Recovery authority may resume only through the accepted phase-specific path
  supported by trustworthy retained and current evidence.
- A reset or error flag alone never authorises deployment. Insufficient
  evidence does not become permission to fire; the declared gap requires
  independent recovery coverage.
- The physical arm in the pyro feed, output-off reset defaults, firmware-bounded
  pulses with a per-channel switch current limit, and the staging inhibit remain
  in force (D-6.1, D-6.2).

Accepted cost: a recoverable processor reset may end the staging objective.
Exact reconstruction logic, interruption budgets, actuator-event evidence and
inhibit persistence across power-loss classes remain to be designed and tested.
No firing threshold or circuit is selected here.

## Independent recovery

Require appropriately independent recovery on the initial flights where Ogma
has live recovery authority and on the Kármán mission. Primary Ogma recovery
must still be qualified; backup coverage is not permission to leave it unproved.

Later ordinary-competition policy can change only through an explicit vehicle
review. A count of successful flights does not automatically remove the
requirement. This adds no third MCU to Ogma.

No commercial device is selected. The vehicle review must establish suitable
sensing and deployment capability across the actual mission envelope, its own
power and actuation path, and the independence of wiring, arming, installation
and mechanisms. Shared batteries, protection, harnesses, pressure paths or
deployment hardware are common causes to assess, not independence by naming.
A conventional barometric backup is not presumed valid near 100 km.

## Release policy

Adopt [G0–G3](../docs/archive/reliability-execution-plan.md#release-gates): inert bench
work, engineering-PCB order, installed-configuration qualification, then unit
and mission release. Each gate needs its own evidence and approval. No existing
flight obligation is waived. Policy acceptance does not authorise a purchase,
live energetic test or flight.

## What remains before EX-01 closes

Seán is the policy approver. Implementation owners and independent reviewers
remain unassigned; no test has run.

For each exercised row, add the actual phase/arm conditions, detection method
and coverage limit, numerical response/interruption budget and rationale,
supported reset/retention class, mission-specific independent coverage, named
owner/reviewer and linked test result. Use the EX-01 closure criteria in the
[execution plan](../docs/archive/reliability-execution-plan.md#ex-01--fault-allocation-and-release-policy).

Do not invent millisecond limits before the dependent power, sensing and restart
work supports them. Characterisation can proceed within known fixture and
component ratings; a pass against a survival or timing claim requires limits
declared before the run. Until then these are accepted design requirements,
not demonstrated capabilities.

Follow-on decisions: the [EX-02 power contract](power-contract.md) and
[EX-03 reset contract](reset-recovery-contract.md) are accepted at policy level.
Their numerical and target-hardware evidence still feed this contract's closure.
All rewritten EX recommendations are now accepted; library/schematic work and
target evidence are next, not another EX policy-approval round.
