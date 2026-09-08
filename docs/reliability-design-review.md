# Ogma 2 reliability design review

Date: 2026-09-05

Status: source-backed engineering review and proposed design closure. Seán
authorised documenting and deepening the review. This does not accept every
proposed circuit, flight policy, part, or test limit.

Purpose: identify failures that can overturn the architecture, turn broad
reliability requirements into bounded contracts, and define what must be proved
before those contracts can be relied on.

Authority: [current system](../current-system.md) remains the accepted prose
baseline. This review supplements and corrects specific claims in the
[hardening study](karman-line-mission-hardening-report.md). The
[execution plan](reliability-execution-plan.md) owns task status and closure
criteria. Hardware, controlled implementation, selected-part documentation, and
measured evidence outrank this analysis.

No Ogma 2 schematic, firmware implementation, or test article was established
by the original review. Physical tests below remain unperformed; the later
host-model coverage is identified separately below.

Acceptance update, 6 September: Seán accepted the EX-01 recommendations for
communications/logger fault containment, bounded validated restart, primary
unavailability after complete flight-power loss, phase-aware watchdog feeding,
post-reset staging inhibit, independent recovery and G0–G3. The
[flight fault contract](../interfaces/flight-fault-contract.md) supersedes the
initial proposal status for that scope. Remaining study proposals, numerical
limits, implementation and test results are not accepted or proved by it.

Further acceptance, 6 September: EX-02's defaults are accepted in the
[power contract](../interfaces/power-contract.md), including Seán's explicit
retention of switching preregulation followed by a low-noise LDO. The protected
Foinse return remains the starting choice with autonomous source/protection
operation. Part selection, intermediate voltage, VIOC and test evidence remain
open. The [external-review note](rev1-external-review-lessons.md) preserves why
this cascade was chosen rather than treating it as an unexplained extra stage.

EX-03 acceptance, 6 September: Seán accepted the reset-class distinction,
two-slot MCU-retained checkpoint direction, GNSS-independent mission time,
deliberate disarmed new-flight preparation and attempted/observed-action
distinction. The [reset contract](../interfaces/reset-recovery-contract.md)
records scope and the [host checkpoint model](../tests/reset_replay/README.md).
Model tests passed; exact MCU retention, time, ECC and restart timing are not
proved. EX-04's candidate strategy, memory placement, initial 30% reserve and
reversible development provisioning are now accepted in the
[initial MCU allocation](mcu-resource-and-timing-results.md). It contains a
partial simultaneous resource reservation, not a completed fit or target timing
result. EX-05 is the next review.

## 1. Verdict and limits

Keep the basic architecture: one accessible PCB, a flight MCU and a
communications MCU, flight-owned recording, three energetic channels, two
servo signals, bounded external CAN, and vehicle-dependent power on Foinse.

Foinse 2 remains MCU-less. There is no Foinse firmware, software boot sequence,
or third flight-computer processor in this review. Seán reconfirmed that
boundary on 5 September after Anav asked whether it had been understood.
Its analogue and dedicated-function devices can still create power-sequencing
dependencies. Those are the concern in section 5.

The architecture is not fault tolerant merely because it contains protection
parts. Each claimed protection needs a fault it detects, a response it can
complete, a deadline, and a surviving function that benefits.

Three questions dominate:

1. Can an external or nonessential branch fail without removing flight power
   or blocking essential execution?
2. Can the flight computer reset without losing the evidence needed to resume
   a defensible flight state?
3. What can it still know when pressure and GNSS are unavailable together?

These questions apply to ordinary competition flights. The short Kármán sortie
adds a longer unaided sensing interval and different pressure/thermal exposure;
it does not create an orbital-lifetime requirement.

The accepted 3 September provisional envelope stays in force. Do not wait for
final vehicle simulations to build coupons, compare parts, or begin a
schematic. Do not call those provisional values measured loads or guaranteed
qualification margins.

### 1.1 Scope of a survival claim

One flight MCU, one PCB, and a common source cannot honestly promise continued
primary operation after every single fault. A failed flight MCU, broken common
power connection, destroyed PCB, or failed common recovery mechanism needs an
explicit residual-risk allocation.

Separate these claims:

- **Continued flight function:** the fault is contained and essential work
  continues.
- **Bounded restart:** essential work pauses, retained evidence is validated,
  and a defined recovery path completes within its limit.
- **Primary function unavailable:** Ogma cannot fulfil that function; another
  independently qualified vehicle function must cover it if the hazard demands
  coverage.
- **Evidence only:** the event can be reconstructed afterward. Recording the
  failure did not prevent it.

Do not combine these into an undifferentiated claim that the system is safe.

## 2. What the evidence actually establishes

The [Rev 1 flight closure](../sources/project/ogma-rev1/ogma-rev1-flight-closure.md)
records an aloft Croí reset at T+14.976 s, approximately 696 m above the launch
datum. It returned to READY at T+51.510 s after recalibration. The cause is
unknown. The earlier inertial event is a possible precursor, not a demonstrated
cause. Recorded voltage and temperature were not usable for diagnosing the
flight power state.

The local log retained 155 committed records with valid checksums and
continuous sequence numbers. That supports the value of local recording. It
does not establish reset-resilient flight control. Pléasc was not flown;
recovery used the conventional system. Ogma's MAIN and LANDED paths were not
qualified by that flight.

The same closure records power-connector trouble, incorrect exact-part/pin
assumptions, rail faults, and a timestamp field that would break the intended
post-landing logger timeout. These are direct reasons to prioritise electrical
integrity, part mapping, time semantics, and recovery tests. No inspected
evidence identifies radiation as the reset cause.

The CATS and Fluctus photographs support serviceability and connector-scale
judgments. They do not establish a measured EMI mechanism, a coating cure, or
the cause of the Fluctus field failure. The
[reference indexes](../sources/README.md) preserve those limits.

## 3. Define flight capability separately from health

A single healthy/faulted flag cannot describe the system usefully. Losing a
radio, losing a barometer during expected high-altitude flight, and losing the
estimator state are different events.

The proposed fault contract records four things together:

- flight phase and the evidence supporting it;
- physical arm state and actuator authority;
- available measurements and their uncertainty/freshness;
- available execution, storage, and communications functions.

This is a design representation, not a proposal for a large new framework or
one UI page per possible combination. Use the smallest explicit state model
that expresses the actual policies and rejects contradictory combinations.

### 3.1 Initial fault allocation for review

| Fault or condition | Before launch | After launch | Evidence required to close the claim |
| --- | --- | --- | --- |
| Communications MCU absent, reset, or flooding UART | Show unavailable functions; readiness follows the mission profile | Flight deadlines and locally owned functions continue; GNSS aiding may be lost | Power and link fault injection, timing trace, local log |
| External flight-log device unavailable | NO-GO if required by the profile | Contain the fault; continue essential work with explicitly reduced recording | Full/busy/corrupt/isolated-device cases; no logger-induced reset loop |
| Pressure or GNSS outside its declared envelope | Cannot substitute invalid data for a readiness measurement | Enter expected invalid-measurement mode; propagate only within the accepted uncertainty policy | Sensor-envelope replay and re-entry tests |
| Correctable ECC event | Diagnose and determine readiness | Correct and continue when the affected path is trustworthy; bounded evidence and escalation | Actual ECC diagnostic test where supported; separate software-integrity tests elsewhere |
| Critical state invalid or uncorrectable memory error | Inhibit launch readiness | Phase-specific reconstruction or primary-function loss; no generic autonomous actuation on an error flag | Corrupt each evidence item; verify allowed transitions and timing |
| Loss of a non-flight power branch | Prevent readiness where that branch is mission-required | Remaining flight rail stays valid and no signal back-power defeats isolation | Rail, current, reset, and output traces during the actual fault |
| Complete loss of the common flight supply | Inactive outputs | Primary flight computer unavailable until power returns; retained capability depends on the real retention supply | Measured power-loss classes and independent vehicle coverage |

The accepted EX-01 contract now governs communications, logger, reset and
complete-power-loss policy. Other rows in this initial review table remain
proposals. Exact mission readiness rules, numerical limits and actuator
implementation still need closure. A closed test for one row does not close
the others.

### 3.2 Watchdog supervision must understand degradation

The hardening study originally made logger progress a prerequisite for the
watchdog heartbeat while also requiring flight to continue after storage
failure. That combination can reset a healthy flight controller repeatedly.

Supervise required progress in the active mode. A contained logger failure
must produce a finite transition into a declared degraded mode, not a permanent
exemption that also hides a dead flight loop. Sensor acquisition, state checks,
and deadline monitoring still have to earn supervision.

Record completion epochs, not just sticky task-alive bits. A bit set once must
not satisfy all later watchdog periods. Supervision cannot depend solely on
the interrupt, timer, or clock whose failure it is intended to catch.

Proposed timing condition for a recoverable fault:

```text
worst detection delay + reset assertion/release + minimum flight restart
    + state validation/reconstruction + required response latency
    < allocated interruption budget for that flight phase
```

If that inequality cannot be met, increasing the watchdog timeout is not a
solution. Change the fault allocation, recovery path, or independent coverage.
Internal and external watchdogs need coordinated windows so one does not
repeatedly interrupt a legitimate recovery by the other.

## 4. Reset is a loss-of-state problem

### 4.1 Classify the reset before trusting retained information

| Reset class | What may survive | What must be established |
| --- | --- | --- |
| Software, watchdog, external reset with valid supplies | Selected RAM, backup domain, storage, sensor state | Actual reset/option-byte behaviour; startup code did not clear it; data integrity and age |
| Brownout or rail excursion | Some storage and possibly some retained domains | Which domains stayed inside their valid limits; memory contents alone are not proof |
| Main rail lost, separately sustained backup domain valid | Backup state and its clock, plus committed nonvolatile records | Backup energy, minimum voltage, transfer behaviour, and elapsed-time continuity |
| Main and retention power lost | Previously completed nonvolatile records | Record validity and age; lost interval may be unknowable |
| Debug, bootloader, update, or option-byte transition | Device- and mode-dependent | Maintenance-only policy, physical output inhibition, and explicit invalidation of flight readiness |

These are possible retention classes, not verified H573 behaviour. Fill them
from the selected derivative, silicon revision, power wiring, option bytes,
startup implementation, and physical tests.

### 4.2 The retained record needs semantics

Candidate fields for the minimum restart record:

- format/version, board identity, flight/session identity;
- immutable accepted mission-profile and calibration identities;
- record generation, integrity check, and completed-write evidence;
- last validated phase and the evidence that established it;
- launch datum and the time reference used to establish it;
- last valid estimator checkpoint, its acquisition time, and uncertainty;
- sensor validity and reset epochs needed to interpret that checkpoint;
- attempted actuator events and separately recorded observations;
- reset/fault cause when capture is possible.

Not every field belongs in every storage tier. Decide the minimum record that
allows the accepted recovery path; keep high-rate history in the ordinary log.
A CRC proves consistency of bytes under its fault model, not that a record is
recent, belongs to this flight, or describes the true vehicle state.

A new flight must invalidate prior flight authority deliberately. A reset must
not manufacture a new flight/session identity and thereby lose the old one.
Generation counters need wrap and comparison rules. Mission configuration must
not change underneath a retained checkpoint.

### 4.3 Preparation and in-flight restart

EX-03 now accepts separate preparation and bounded in-flight restart semantics.
This does not require duplicated boot code. The actual low-level primitives,
integrity checks and timing remain implementation work on the selected MCU.

The in-flight path needs to:

1. Keep hardware output defaults valid without application software.
2. Capture available reset evidence before code clears it.
3. Establish a known-good execution stack and memory region.
4. Validate retention before initialising or reusing that region.
5. Establish whether time continuity and measurement history are sufficient.
6. Resume only the permitted phase-specific path, or declare the relevant
   primary function unavailable.
7. Restart optional services after essential execution is established.

Do not recalibrate as though stationary, redefine launch altitude, wait for
GNSS acquisition, scan all NOR, or run an unbounded startup diagnostic during
this path. Expensive maintenance diagnostics can remain mandatory before
arming without necessarily running in full during a coast restart.

### 4.4 Retention and ECC must be designed together

Blanket write-before-read initialisation destroys retained history. Conversely,
blindly reading retained ECC RAM after invalid power can trigger a fault before
the application has a usable handler. The reset class, memory partition,
power-valid evidence, and read/initialise order must resolve this conflict.

An ECC handler also cannot assume its current stack, exception frame, logger,
heap, or format strings are healthy. Keep the fault path small and bounded;
test re-entry and failure of the evidence path itself. Some faults may prevent
software handling altogether. Hardware output bounds and external supervision
must not depend on that handler running successfully.

### 4.5 Evidence has a survivability limit

An ADC sample is not a guaranteed capture of a microsecond supply dip. Reset
flags may identify brownout without reconstructing the waveform. A pre-fault
ring buffer may disappear with its power supply.

Allocate separately:

- external instruments for bench diagnosis;
- retained reset classification for recoverable resets;
- a bounded nonvolatile event summary;
- additional minimum-voltage capture or hold-up only if its diagnostic or
  recovery value justifies the hardware.

Do not promise a completed fault record after arbitrary instantaneous loss of
all power. Define the guarantee the actual circuit can support.

## 5. Power: eliminate paths that defeat containment

### 5.1 MCU-less Foinse startup

The accepted integrated direction is Foinse protected VBAT to Ogma, then an
Ogma protected low-power 3.3 V return to Foinse. A monitoring IC, gate driver,
enable pull network, or protection controller can still need a supply before
it works. No microcontroller is needed to create a circular dependency.

Write a dependency graph for the actual devices:

```text
vehicle source -> Foinse autonomous source/protection path -> Ogma VBAT
Ogma VBAT -> Ogma logic conversion -> optional protected Foinse auxiliary supply
```

The second line must not be a prerequisite for the first unless a separately
proved startup and maintenance path resolves that dependency. Loss of Ogma
software must not make an otherwise healthy Foinse source path chatter.

EX-02 now retains the protected auxiliary return with autonomous source-path
operation and demonstrable containment. Local regulation is the review fallback
if actual device dependencies cannot satisfy that contract cleanly. Feasibility
is not yet demonstrated. Foinse remains MCU-less in either case.

### 5.2 Complete the source-state table

For standalone and integrated operation, enumerate: battery absent/present,
USB absent/present, charging absent/present, permitted maintenance connections,
and all allowed source transitions. Physically exclude invalid combinations
or protect them. Include the return conductor; a broken return can reroute
current through a signal, cable shield, or host ground.

For every powered/unpowered boundary, inspect signal-pin injection limits,
pull-ups, transceiver fail-silent behaviour, and whether a disabled load switch
actually discharges and isolates the downstream node. A chip that remains
partly powered through UART may never reset as intended.

### 5.3 Coordinate protection against the actual source

Current limiting must be evaluated as a system:

- normal peak load, startup/inrush, and pulse load;
- branch short current and interruption delay;
- upstream source impedance and battery protection response;
- source/connector/harness voltage drop;
- stored energy and where it can discharge;
- upstream fuse and branch-protection selectivity;
- thermal or repeated-retry behaviour after a persistent fault.

If the battery protection disconnects everything before the communications
branch isolates, the branch boundary has failed its purpose. If an automatic
retry repeatedly sags the flight rail, a recovered branch is not necessary for
continued failure. Try-later policy needs a bounded retry count and energy
budget; those values remain open.

### 5.4 The proposed 3.8 V to 3.3 V chain needs a reason

The buck/LDO cascade is now the accepted baseline, following Seán's
6 September clarification of the prior external review. The approximately
3.8 V value and exact devices remain provisional, not a universal solution.
The available headroom must include buck tolerance/ripple/droop, LDO dropout at
load and temperature, wiring loss, and startup. Dissipation is approximately
`(Vin - Vout) × I`, before quiescent consumption.

LDO rejection depends on frequency, load, headroom, and the fitted capacitors.
Compare it at the converter switching spectrum and sensitive sensor bandwidth,
not only at a favourable low-frequency datasheet point. [ADI AN-1120](https://www.analog.com/en/resources/app-notes/an-1120.html)

Measure the chain's actual noise and measurement performance. A direct buck
or sensor-only post-regulator can remain a comparison if evidence justifies
reopening the choice; neither is the default implementation. Retaining the
chosen chain does not close headroom, thermal, transient or fault checks.

### 5.5 Hold-up is an energy budget

For a constant-current first estimate:

```text
C >= I_load × interruption_time / allowable_voltage_drop
```

For an approximately constant-power load, available capacitor energy is:

```text
E_usable = 0.5 × C × (V_start² - V_min²)
E_required >= P_load × interruption_time / conversion_efficiency
```

These are screening calculations. Include capacitance tolerance, DC-bias and
temperature effects, ESR droop, converter limits, and the current of every
load that remains attached. Hold-up intended for the flight core should not
quietly discharge into a failed radio or external harness.

Hot plugging a low-loss ceramic input through an inductive lead can produce
large overshoot. More ceramic capacitance alone is not a damping design.
The real cable/source and input network need a captured transient. [ADI AN88](https://www.analog.com/media/en/technical-documentation/application-notes/an88f.pdf)

### 5.6 Grounding, isolation, and ESD

Start with current loops and permitted reference differences. Separate power
branches do not automatically require split ground planes or galvanic
isolation. Do not route a sensitive signal over a break in its reference merely
to make the drawing look isolated.

For each accessible connector, document:

- reference/return and possible host/chassis connection;
- working voltage, transient envelope, and unpowered-pin behaviour;
- protection placement and discharge path;
- clamp voltage at the relevant current, pulse energy, and series impedance;
- allowable signal capacitance and common-mode range;
- fault response and test observables.

An IC's component-level ESD rating does not establish installed-bay immunity.
Formal ESD/EMC levels remain a qualification decision. Early development uses
controlled tests with the actual enclosure and inert outputs, not improvised
unmeasured sparks. Isolation is justified where a named ground/hazard boundary
requires it; adding an isolator without isolated power or with a bypassing
shield/return does not establish galvanic separation.

## 6. MCU, memory, and execution

### 6.1 Source corrections for the H563/H573 candidate path

The H573 memory discussion contained two consequential problems. ST AN5342
Rev 8, table 4, describes H5 SRAM ECC on 32-bit data words. SRAM3's upper 64 KiB
is reserved for ECC check storage when its ECC is enabled. It is not available
for disposable buffers. For H573, the main-RAM allocation is 64 KiB protected
SRAM2 plus 256 KiB protected SRAM3, with 256 KiB unprotected SRAM1; backup SRAM
is separate. [ST AN5342](https://www.st.com/resource/en/application_note/an5342-error-correction-code-ecc-management-for-internal-memories-protection-on-stm32h7-series-stmicroelectronics.pdf)

ST's RAM training corroborates the 32-bit organisation and SRAM3 reservation.
Do not extrapolate this allocation to every newly released H5 derivative.
[ST H5 RAMCFG training](https://www.st.com/content/ccc/resource/training/technical/product_training/group1/9d/5c/38/7e/32/71/41/e0/STM32H5-RAM-configuration-RAMCFG/files/stm32h5-ram-configuration-ramcfg.pdf/jcr:content/translations/en.stm32h5-ram-configuration-ramcfg.pdf)

UM3150 Rev 2 table 22 contains conflicting 64-bit wording; the earlier report
followed an actual ST statement. Its table 24 limits the documented ECC-disable
test mechanism to RAM3, with other measures identified for RAM2/BKPSRAM.
Do not claim identical hardware injection coverage for every bank.
[ST UM3150](https://www.st.com/resource/en/user_manual/um3150-stm32h5-series-safety-manual-stmicroelectronics.pdf)

Close this with the selected part's reference manual, revision-specific errata,
and executable evidence. A source conflict is not resolved by repeating the
more convenient table.

H563 belongs beside H573 in the candidate comparison: H573 adds cryptographic
and security facilities that need a named requirement. Exact package, memory,
peripherals, availability, and provisioning behaviour still decide suitability.
[ST family comparison](https://www.st.com/en/microcontrollers-microprocessors/stm32h563-573.html)

### 6.2 Make the resource matrix enforceable

Close all of these for an exact orderable part:

- pin/alternate-function allocation, boot/debug constraints, package and
  footprint;
- sensor buses, logger bus, CAN, UART, two PWM channels, capture inputs, ADC,
  interrupt lines, clock sources, and test access;
- DMA routing, transfer bounds, bus contention, and buffer ownership;
- stack, estimator, sensor history, restart record, event evidence, and log
  buffers within the usable protected-memory budget;
- cache policy, MPU regions, executable memory, privilege/security setup;
- startup files, option bytes, boot/security provisioning, and debug recovery;
- interrupt nesting, worst observed latency, and the remaining execution margin.

Do not assume a different H5 package has the same usable pins or a family
peripheral list is a realizable simultaneous allocation. A post-link check
should reject critical symbols outside their allowed memory classes.

### 6.3 Protect against valid but wrong writes

ECC handles codeword corruption; a buffer overrun or wrong DMA destination can
write bad application state with valid ECC. Use ownership, bounds checks,
restricted writable regions, legal state transitions, and freshness checks.
MPU coverage and DMA coverage must be assessed separately for the device; do
not assume CPU access restrictions constrain every bus master.

Adding inverse copies, CRCs, redundant computations, and periodic register
checks everywhere can create more code and timing failure modes than it removes.
For each diagnostic record: target fault, independent evidence, response,
execution cost, and a test that distinguishes working from broken protection.

### 6.4 Scrubbing is a concurrent memory operation

A read/correct/write sequence can overwrite a legitimate update made by an
interrupt or DMA between its read and write. `volatile` does not resolve
ownership. Use a bank/region-specific scheme and prove it against the actual
writers and cache policy. An old snapshot copied back is not a safe scrub.

Exercise rarely read memory and the diagnostic path itself. Rate-limit fault
recording so a stream of correctable events cannot consume all execution or
storage. A corrected value that is not rewritten can remain a latent error;
verify removal through the supported mechanism. [ST UM3150, RAM_SM_7](https://www.st.com/resource/en/user_manual/um3150-stm32h5-series-safety-manual-stmicroelectronics.pdf)

### 6.5 Boot and flash errata affect retained evidence

ES0565 Rev 8 §2.2.33 describes an approximately 120 µs flash-access stall on the
first erase/program after power-on or Standby exit, including cross-bank
read-while-write. Budget or work around it using the documented SRAM execution
path. This is not a claim that every watchdog reset causes the same stall.

The same errata includes SRAM2 erasure on backup-domain reset (§2.2.14) and a
conditional STiRoT/clock-related backup-domain erasure issue (§2.2.39).
Applicability depends on configuration, silicon and system-flash package
version. Record those before relying on retention. [ST ES0565](https://www.st.com.cn/resource/en/errata_sheet/es0565-stm32h562xx563xx573xx-device-errata-stmicroelectronics.pdf)

A two-slot journal must respect the selected memory's real program and erase
units. A commit marker is not permission to rewrite a previously programmed
ECC word. Test interrupted writes at each actual operation boundary, both
slots invalid, generation wrap, and inaccessible storage.

### 6.6 Scheduling: measure the maximum, preserve the bound

Average CPU utilisation does not establish deadline behaviour. Instrument
sample-ready, acquisition completion, estimator completion, policy evaluation,
and output update. Include interrupts, DMA contention, flash activity, fault
handlers, scrub slices, and maximum permitted incoming traffic.

Busy waits and library calls need bounded failure paths. A timeout driven by a
stopped scheduler tick can become infinite. Avoid dynamic allocation in the
flight path after initialisation; this still leaves stack growth and fixed
buffer overflow to test.

A minimal flight-core scheduler can be evaluated before choosing or migrating
an RTOS. The decision should follow the timing/ownership contract and team
maintenance cost, not a claim that an RTOS automatically provides determinism.

## 7. Sensing, uncertainty, and the unaided interval

### 7.1 Separate measurement validity from device health

MAX-M10S R08 specifies 80,000 m altitude, 500 m/s velocity, and dynamics up to
4 g under its stated platform assumption. It is a lower-envelope candidate,
not a full-flight 100 km instrument. A powered receiver and valid packet CRC do
not override those limits. [u-blox MAX-M10S datasheet](https://beta-content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf)

A barometer may be healthy while pressure lies outside its usable range. A
blocked vent may yield plausible stale pressure. A sensor can also resume
plausible output after saturation before its reading is trustworthy again.
Define validity, saturation recovery, re-entry checks, and stale-data limits
for each measurement.

### 7.2 What inertial propagation needs

Near free fall, an accelerometer measures approximately zero specific force;
it does not supply an instantaneous apogee marker or a gravity direction.
[Analog Devices free-fall explanation](https://www.analog.com/en/resources/analog-dialogue/articles/using-accelerometers-to-protect-hard-drives.html)

The estimator therefore depends on prior state, frame conventions, attitude,
the gravity model, calibration, acquisition timing, and the duration of lost
external aiding. State uncertainty must grow when information is lost.

Illustration only: a constant 1 mg acceleration error integrated for 120 s
contributes approximately 1.18 m/s velocity error and 70.6 m position error.
This is not an Ogma error prediction or an allocated acceptable error. It
omits attitude, launch-state, timing, vibration, and model errors. It shows why
an unaided-duration budget is necessary even for a short mission.

Start with a small family of provisional profiles: ordinary lower-altitude
flight, prolonged unaided coast, fast/spinning boost, and aborted or shortened
flight. Mature simulation later replaces these engineering scenarios.

### 7.3 Acquisition time is not packet arrival time

Define time at the sensor sample, FIFO, DMA completion, UART transfer, and log
record. Preserve sequence and reset epochs so data from before a sensor or
communications restart cannot masquerade as new data.

GNSS time or PPS may improve synchronisation while valid; neither can be the
sole clock for the interval where that source is unavailable. A retained clock
needs its own power and drift budget. A timer restarted at zero needs an
explicit mapping or loss-of-time indication.

### 7.4 Sensor range does not establish bandwidth

The accepted ±2000°/s gyro target is approximately 5.56 revolutions/s. That
conversion does not prove adequate spin measurement. Include sample rate,
analogue/digital filtering, aliasing, sensor group delay, cross-axis response,
mounting, overload recovery, and timestamp jitter.

The high-g channel and low-g IMU need a defined overlap region and calibration
relationship. Switching between them must not introduce an unrecorded step.
Two sensors on one PCB can share supply, clock, mounting and bus faults;
different part numbers alone do not establish independent evidence.

### 7.5 Claim altitude separately from controlling recovery

Name the proof instrument, its owner, operating envelope, data availability,
time/datum conventions, and uncertainty needed to substantiate the altitude
claim. If a full-envelope receiver changes the RF, connector, power or package
requirements, resolve that before freezing those interfaces.

The recovery-policy output of this work is a reviewed sensor/phase validity
contract. This review deliberately does not invent launch-specific deployment
or staging thresholds.

## 8. Actuation, independence, and vehicle sections

### 8.1 Software state and physical action are not atomic

Writing an event-complete flag before physical actuation can record an event
that never occurred. Writing it afterward leaves a possible gap in which the
action occurred but the record did not survive.

Distinguish command intent, attempted actuation, measured electrical response,
and observed mechanical outcome. Define how each ambiguous case is handled
after reset. No universal exactly-once physical-actuation guarantee follows
from a CRC-protected flag.

Finite pulses address excessive duration. They do not prove correct channel,
correct phase, sufficient actuation, or absence of a premature pulse. Two
enables driven by the same faulty decision path are not independent decisions.
The actual circuit needs a fault analysis for each named hazardous outcome.

Routine development uses inert loads. This document does not authorise live
energetic testing or select firing parameters.

### 8.2 Servo failure policy is mechanical

PWM absent, power absent, commanded home, and physically home are different
states. An airbrake and a servo-triggered recovery mechanism can require
different responses. Measure motion under the intended load and interruption
conditions before claiming that an electrical safe state is mechanically safe.

### 8.3 Independent recovery is still open

The baseline has an open per-mission independent-recovery decision. Some study
paragraphs already relied on that recommendation as though accepted. That
status leakage is corrected by keeping the recommendation explicit.

Review recommendation: provide suitably independent recovery coverage for
development flight risk and the Kármán mission, subject to a vehicle hazard and
range review. Do not infer a blanket mandate for every competition launch.

The selected system must cover its intended altitude/velocity/pressure/time
envelope. Examine common battery, return, harness, sensor, mounting, pressure
port, and deployment-mechanism failures. A backup may cover non-deployment
without covering a premature primary event or a jammed shared mechanism.
Commercial provenance alone does not close those hazards.

### 8.4 One board does not own every separated stage

Allocate the three channels and two servo signals to a named vehicle section.
A separately recovered booster needs its own surviving recovery capability.
Separation must not leave a required power, reference, antenna, or command path
on the discarded section.

For liquid staging, reconcile Ogma's staged-flight authority with the propulsion
controller's local engine ignition authority. No channel acquires two owners
because both documents use the word ignition. The
[existing interface](../interfaces/ogma-foinse-propulsion-boundary.md) remains
in force pending a jointly accepted clarification.

## 9. Recording, configuration, and service

### 9.1 Three data jobs

Treat the restart record, event evidence, and bulk sensor log separately in
their requirements. They may share a device only if the common failure is
accepted. A minimal journal on the same failed NOR is not a storage fallback.

Budget:

```text
flight_bytes = full_rate_bytes_per_second × 1800 seconds
total_bytes = flight_bytes + pad_log + recovery_log + metadata + reserve
buffer_bytes >= peak_production_rate × maximum_supported_storage_stall
```

The buffer relation assumes no service during the stall and needs extra space
for records already queued and implementation overhead. It does not handle
an indefinitely failed device; that requires the degraded policy.

Example only: 1000 records/s × 64 bytes × 1800 s is 115.2 MB before overhead.
No record rate, width, or device capacity is selected by that example.

Account for write amplification, erase/program granularity, maximum busy time,
temperature, endurance, interrupted writes, address wrap, and flight extraction
time. Pre-erasure is a candidate for simplifying flight timing; it must never
erase unexported evidence silently. Boot recovery cannot scale without bound
with the size of the full log.

### 9.2 Typed configuration needs a commit contract

The host proposes a profile; the flight MCU validates and accepts it. Readback
must describe the accepted bytes, identity, schema, hardware compatibility and
activation status. A successful USB transfer is not proof of activation.

Define how an interrupted update, incompatible communications firmware, wrong
board identity, stale upload, and invalid calibration are rejected. A CRC detects
accidental corruption under its assumptions; it does not establish sender
authority. No incoming radio or USB packet directly acquires energetic output
authority. Firmware recovery and factory provisioning remain maintenance
operations with physical inhibition.

Preserve the configuration and calibration used for a flight even if the host
tool later changes defaults. Logs need enough schema and version information
to be decoded without reconstructing the original laptop installation.

### 9.3 A useful operator interface is a small set of truthful states

Build the minimum workflow first: connect, identify, inspect faults, select a
compatible profile, validate, transfer, read back, compare, and extract evidence.
Distinguish displayed intent from board acceptance and physical arm readback.

Test unplugging, suspended hosts, wrong device, incompatible versions and
interrupted transfers on the actual supported macOS and Windows versions.
Do not build a general action editor to compensate for an undefined flight
policy. The CATS references inform the workflow, not actuator authority.

## 10. The installed bay is part of the circuit

### 10.1 Connectors and workmanship

The existing shortlist is sufficient for the next experiment. Evaluate the
actual header/contact/wire/tool combination, not a family current headline.
Record contact population, neighbouring loaded pins, temperature derating,
wire insulation, crimp inspection, retention, mating cycles and strain relief.

The smallest housing can lose its size advantage through tool access, latch
clearance, bend radius and strain relief. Different functions must not be
dangerously cross-matable merely because one family is convenient. Colour and
labels help operators; they are not equivalent to mechanical keying.

Mock up the complete 3-inch assembly with inert charge-module stand-ins.
Structural mounts carry board/harness loads. Normal service must not tug a
flight connector or disturb another accepted assembly. Keep direct test access
for both MCUs and the important current/return paths.

### 10.2 Pressure, heat, and contamination have different paths

The enclosure needs controlled pressure equalisation and a characterised
barometer path while excluding energetic residue. A vent or membrane can
change pressure lag; a shared obstruction can invalidate two barometers.

Low ambient pressure changes cooling. Qualify the actual power profile and
thermal path through PCB, mounts and enclosure. Component ambient grade alone
does not establish junction or battery temperature. Include the long powered
pad period, short low-pressure interval, and descent/recovery conditions.

Coating, staking and cleanliness solve different problems. Coating does not
repair a marginal joint, prevent all shorts, prove radiation tolerance, or
establish a thermal path. Select it after inspection/cleaning and test the
actual process; keep pressure ports, contacts and service areas appropriately
controlled. Parylene is a candidate process, not a default requirement.

### 10.3 RF and video remain system loads

Measure radio operation with final antennas, cables, enclosure and installed
orientation. Include telemetry loss from tumbling/nulls, deployment changes,
and ground-station geometry. A packet received on the bench is not a link
margin measurement.

Camera and video transmission remain separate payload functions and normally
separately powered. Test their interference and heat in the installed bay.
Changing RunCam to GoPro does not remove microSD. No inspected evidence proves
that an SD card inevitably fails merely because apogee reaches 100 km.

## 11. Radiation: bound the mission claim

Time reduces accumulated exposure; it does not make every instantaneous upset
impossible. Conversely, a successful software fault-injection campaign is not
a measurement of radiation susceptibility.

An event-rate estimate needs a mission/environment model and relevant device
cross-section data. Symbolically, expected events integrate flux times
susceptibility over particle energy and exposure time. No such qualified H573
mission estimate was established here. Do not invent an upset probability or
claim that industrial temperature grade supplies radiation qualification.

Use ECC and fault containment for their named benefits while keeping the
residual radiation uncertainty explicit. Before a Kármán release, obtain an
appropriate parts/radiation review of the exact candidate set and the bounded
mission. NASA's parts guidance likewise treats radiation suitability as an
application-specific assessment, not a property inferred from generic parts
selection. [NASA NPSL guidance](https://nepp.nasa.gov/npsl/npsl_UsePolicy.htm)

Do not make months of irradiation testing a default prerequisite to the first
inert engineering board. Do not label that board radiation-qualified afterward.

## 12. Release gates and review closure

The current pre-PCB evidence list includes useful requirements whose complete
proof needs an assembled board and bay. Split readiness by what is actually
being released:

- permission to run a bounded inert bench experiment;
- permission to order an engineering PCB with explicit limitations;
- qualification of a controlled installed configuration for a named envelope;
- acceptance and flight release of a particular unit and mission.

This is proposed gate allocation. It does not waive any existing flight
requirement. The [execution plan](reliability-execution-plan.md) provides the
deliverables and decision points.

Review closure is not agreement with every paragraph. Close each finding with
an accepted decision and evidence, a rejected recommendation with rationale,
or an explicit residual risk owned at the appropriate vehicle/release level.
Do not mark an unknown resolved because a component was bought or a test was
run without a pass criterion.

Start with EX-01 through EX-04: fault allocation, power dependencies, restart
semantics, and exact MCU resource/retention evidence. EX-05 develops the sensing
contract alongside them. These define the first useful integrated bench test.
