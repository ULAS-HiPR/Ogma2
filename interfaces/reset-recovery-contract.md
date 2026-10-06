# Ogma 2 reset, retained state and time contract

**Status (6 Oct 2026):** controlling contract. Electrical details describe the
8 September CAD; decided changes are in [decisions.md](../decisions.md) and the
[capture delta](../docs/architecture/schematic-capture-spec.md). Capture waits
for Seán's go-ahead.

Updated: 7 September 2026
Status: EX-03 defaults accepted by Seán. Initial host model exists; MCU-specific
implementation, timing, power/retention evidence and qualification remain open.

Authority: [current system](../current-system.md),
[flight fault contract](flight-fault-contract.md) and [power contract](power-contract.md).
Seán accepted all five EX-03 recommendations before requesting the next review.

The subsequent [batch acceptance](../docs/archive/architecture-acceptance-2026-09-07.md)
selects STM32H563VIT6 for both roles. Flight uses the H563 backup domain for two
1 KiB checkpoint slots. VBAT is fed from flight 3.3 V through a Schottky with
100 µF of its own (D-6.4), so retention outlives a short supply dip; there is
still no backup cell. An LSE/RTC provides the proposed retained time base.
No retained state/time survives loss of its actual supply by assumption.
SRAM2/3 ECC placement, reset-aware initialisation and checkpoint-port evidence
remain required; host-model passes are not hardware proof.

Initial accepted timing targets distinguish 100 ms valid-supply software-reset
recovery from watchdog recovery: 400 ms from watchdog assertion, 550 ms from
the last earned heartbeat. TPS3430's reset assertion alone is 170–230 ms in
the selected configuration. These are unmeasured engineering targets, not
mission-wide guarantees. Earlier statements below leaving the bank, clock or
supply wholly unselected are superseded; actual behaviour and firmware encoding
remain to be proved. Anav owns the firmware work, not a new model implementation
in this documentation task.

## Accepted defaults

1. Classify a processor reset with valid supplies separately from main-power
   loss with surviving retention, and from loss of all retention power. A
   successful result for one class does not establish another.
2. Start with two alternating small checkpoint slots in a verified MCU
   retention domain, independent of bulk logging. Each carries flight/profile
   identity, generation, integrity, time, validated state and relevant action
   history. Preserve the prior valid checkpoint while writing its replacement.
   No external FRAM by default; reconsider if the MCU cannot meet the contract.
3. Preserve local mission elapsed time without depending on GNSS. Use a retained
   clock where the actual hardware supports the claimed reset classes. Never
   silently interpret a restarted counter as time since launch. Unknown age
   remains unknown, even when the checkpoint's CRC is valid.
4. Creating a new flight and clearing prior-flight authority are deliberate,
   explicitly disarmed preparation operations. A reset does neither. Full
   calibration belongs to preparation; in-flight restart restores validated
   essential functions before optional communications or bulk-log recovery.
5. Keep attempted action separate from observed physical result. Neither
   automatic command replay nor blanket suppression of all attempted recovery
   actions is an adequate policy. EX-07 must resolve each mechanism's evidence
   and permitted response. No re-fire policy is selected here.

The accepted EX-01 staging inhibit remains: an in-flight flight-MCU reset
prevents further sustainer ignition for that flight. Recovery still needs a
validated phase-specific path. No reset, checkpoint or error flag alone grants
actuation authority.

## Reset classes and claims

| Class | Required evidence | Permitted claim before qualification |
| --- | --- | --- |
| Processor/software/watchdog/external reset, relevant supplies valid | Exact bank/reset behaviour, option bytes, startup preservation, clock continuity, checkpoint integrity/identity/age | Candidate for bounded restart; no assumed timing pass |
| Main supply lost, selected retention domain remained valid | Independent evidence of the retention supply/clock window and actual saved-state location | Only the state/time actually in surviving domains can support reconstruction |
| Brownout or uncertain domain validity | Determine which domains stayed valid; CRC alone is insufficient | Unknown retention is not promoted to a valid warm-reset class |
| All retention power lost | Any completed nonvolatile records and their known limitations | Primary was unavailable; no claim that volatile checkpoints or elapsed time survived |
| Maintenance/debug/update | Physical disarm, controlled preparation, identity/readback and affected rechecks | No retained flight authority carried into a new flight by accident |

Two slots protect an update protocol under its stated fault model. They do not
protect against a common power loss, corrupt writer, destroyed bank or PCB.
If both slots are invalid, incompatible or ambiguously ordered, return explicit
unavailability and follow the accepted fault allocation.

## Checkpoint and clock implementation work

Keep only the evidence necessary for the permitted restart path. Close the
production schema against required format/version, board/flight/profile and
calibration identity, generation/wrap rules, completed-write evidence, phase,
launch datum, estimator state/uncertainty and acquisition age, sensor reset
epochs, attempted events and separate observations.

The production bank, binary format, CRC, write granularity, cache/barrier/DMA
rules, writer ownership, update frequency and maximum checkpoint age are open.
Do not claim an update is atomic merely because a C assignment is small.
Retained ECC memory needs a reset-class-aware read/initialise sequence: generic
startup clearing must not erase good state, and invalid-power RAM must not be
read blindly before a usable fault path exists.

Record mission time separately from boot/reset epochs. Establish clock drift,
resolution, wrap, reset behaviour, loss detection and the mapping between any
retained clock and a restarted high-resolution counter. No RTC part, backup
battery or hold-up capacitor is selected by this policy. A surviving clock
does not imply that the estimator checkpoint survived, or vice versa.

## Startup and output boundary

Both preparation and restart preserve hardware output inhibits. Preparation
requires explicit disarm, deliberate flight-identity creation and full relevant
calibration/readiness work. In-flight restart captures reset evidence, establishes
known-good execution, validates available state/time, reacquires required
measurements and permits only the supported phase-specific continuation.

Do not recalibrate as stationary, create a new launch datum, wait for GNSS,
scan the complete bulk log or restart optional services before required flight
work. Do not treat a previously written firing command as proof of deployment.
When evidence is insufficient, the affected primary function remains unavailable;
independent recovery covers only its separately established mission allocation.

## Initial executable check

The [host checkpoint replay](../tests/reset_replay/README.md) exercises ordered
byte-write interruption at every update boundary, four synthetic phase changes,
generation wrap, bit corruption, identity/freshness checks and retention-class
gating. It returns only a checkpoint candidate, never an actuator command.

Its byte-write assumptions, synthetic times/identities and simplified state
are explicitly model-only. This is not a flight estimator, selected firmware
encoding, ECC injection, MCU timing measurement or physical reset test. No
hardware survival or flight-readiness claim follows from passing it.

## Closure and next checkpoint

Use [RST-01](../docs/archive/reliability-execution-plan.md#experiment-rst-01-restart-with-known-evidence)
to extend the model onto the selected device. Declare per-phase interruption,
state-age and uncertainty limits before claiming a pass. Measure reset release,
first essential execution, first valid sample/state and optional-service return
using an external timebase. Repeat without debugger assistance and with logger
and communications unavailable.

Seán is the policy approver. Hardware/firmware implementation owners and an
independent reviewer remain unassigned. Exact memory/clock/power behaviour and
the mechanism-specific EX-07 responses remain open; EX-03 is not closed.
Continue implementation against the accepted full pin maps and firmware handoff;
run the target reset campaign on available target hardware and the first PCBA.
