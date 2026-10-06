# Ogma 2 reset, retained state and time contract

**Status, 6 October 2026: controlling contract.** Electrical detail describes the
8 September CAD. Decided changes are in [decisions.md](../decisions.md) and the
[capture specification](../docs/architecture/schematic-capture-spec.md).
Capture waits for Seán's go-ahead.

**What is accepted.** Seán accepted all five EX-03 recommendations (defaults
below). A host model exists. MCU-specific implementation, timing, power and
retention evidence, and qualification are open. Authority:
[current system](../current-system.md), [flight fault contract](flight-fault-contract.md),
[power contract](power-contract.md). The firmware rules that use this contract
are drafted in the [recovery logic](../docs/architecture/10-recovery-logic.md)
(D-6.11, proposed). Anav owns the firmware work.

## Hardware this assumes

From the 7 September [batch acceptance](../docs/archive/architecture-acceptance-2026-09-07.md)
and later decisions:

- Flight is an STM32H563VIT6 (comms is a separate H563, D-6.12; package in D1).
- Flight keeps two 1 KiB checkpoint slots in the H563 backup domain.
- Flight VBAT is fed from `FLIGHT_3V3` through a Schottky, with its own 100 µF
  (D-6.4), so retention outlasts a short supply dip. There is still no backup
  cell.
- An LSE / RTC is the proposed retained time base.
- Nothing retained survives the loss of its real supply just by assumption.
- Still needed: SRAM2/3 ECC placement, reset-aware initialisation and evidence
  for the checkpoint port. Host-model passes are not hardware proof.

Timing targets, unmeasured:

| Case | Target |
| --- | --- |
| Software reset with valid supplies | 100 ms |
| Watchdog recovery, from assertion | 400 ms |
| Watchdog recovery, from last earned heartbeat | 550 ms |
| TPS3430 reset assertion alone, as configured | 170–230 ms |

These are engineering targets, not mission-wide guarantees. Real behaviour and
the firmware encoding still have to be proved.

## Accepted defaults

1. **Separate the reset classes.** A processor reset with valid supplies, main
   power lost with retention surviving, and all retention power lost are
   different classes. Passing one proves nothing about another.
2. **Two small checkpoint slots.** They alternate, sit in a verified MCU
   retention domain and are independent of bulk logging. Each holds flight and
   profile identity, generation, integrity, time, validated state and relevant
   action history. The previous valid checkpoint stays intact while the next is
   written. No external FRAM by default; reconsider if the MCU can't meet this.
3. **Mission time without GNSS.** Use a retained clock where the real hardware
   supports the claimed reset classes. Never read a restarted counter as time
   since launch. Unknown age stays unknown, even with a valid CRC.
4. **Resets never start a new flight.** Creating a new flight and clearing the
   previous flight's authority are deliberate, disarmed preparation steps. Full
   calibration belongs to preparation. An in-flight restart brings back
   validated essential functions before optional comms or bulk-log recovery.
5. **Attempted is not observed.** Keep "we commanded it" apart from "it
   physically happened". Neither replaying commands automatically nor suppressing
   every attempted recovery action is good enough. EX-07 settles each mechanism's
   evidence and allowed response. No re-fire policy is chosen here.

The EX-01 staging inhibit stands: an in-flight flight-MCU reset stops any
further sustainer ignition that flight. Recovery still needs a validated
phase-specific path. No reset, checkpoint or error flag alone grants authority
to actuate.

## Reset classes

| Class | Evidence needed | What may be claimed before qualification |
| --- | --- | --- |
| Processor, software, watchdog or external reset with supplies valid | Exact bank and reset behaviour, option bytes, startup preservation, clock continuity, checkpoint integrity, identity and age | A candidate for bounded restart. No assumed timing pass |
| Main supply lost, retention domain stayed valid | Independent evidence of the retention supply and clock window, and where state was actually saved | Only state and time in domains that really survived can support reconstruction |
| Brownout, or unsure which domains stayed valid | Work out which domains stayed valid. A CRC alone isn't enough | Unknown retention is never promoted to a valid warm reset |
| All retention power lost | Any completed non-volatile records and their known limits | Primary was unavailable. No claim that volatile checkpoints or elapsed time survived |
| Maintenance, debug or update | Physical disarm, controlled preparation, identity readback, affected rechecks | No retained flight authority carried into a new flight by accident |

Two slots protect the update protocol under its stated fault model. They don't
protect against a common power loss, a corrupt writer, a destroyed bank or the
PCB. If both slots are invalid, incompatible or their order is ambiguous, report
unavailable and follow the fault allocation.

## Checkpoint and clock work still to do

**Schema.** Keep only what the permitted restart path needs. Close the production
schema against: format and version; board, flight, profile and calibration
identity; generation and wrap rules; evidence the write completed; phase;
launch datum; estimator state, uncertainty and acquisition age; sensor reset
epochs; attempted events, kept apart from observations.

**Open:** the production bank, binary format, CRC, write granularity, cache,
barrier and DMA rules, writer ownership, update rate and maximum checkpoint
age.

- An update isn't atomic just because the C assignment is small.
- Retained ECC memory needs a read-and-initialise sequence that knows the reset
  class. Generic startup clearing must not wipe good state, and RAM from an
  invalid-power case must not be read blindly before a usable fault path exists.

**Clock.** Record mission time separately from boot and reset epochs. Establish
drift, resolution, wrap, reset behaviour, loss detection and how any retained
clock maps to a restarted high-resolution counter. This policy chooses no RTC
part or backup battery; the only added hold-up is D-6.4's 100 µF on VBAT. A
surviving clock doesn't mean the estimator checkpoint survived, or the other way
round.

## Startup and outputs

Preparation and restart both keep the hardware output inhibits.

- **Preparation:** explicit disarm, deliberate creation of a flight identity,
  full calibration and readiness work.
- **In-flight restart:** capture reset evidence, get known-good execution,
  validate whatever state and time are available, reacquire required
  measurements, and allow only the supported phase-specific continuation.

During a restart, don't recalibrate as if stationary, create a new launch datum,
wait for GNSS, scan the whole bulk log or start optional services before
required flight work. A previously written fire command is not proof of
deployment. When evidence is short, the affected primary function stays
unavailable; independent recovery covers only its own separately agreed
allocation.

## Host model

The [host checkpoint replay](../tests/reset_replay/README.md) covers ordered
byte-write interruption at every update boundary, four synthetic phase changes,
generation wrap, bit corruption, identity and freshness checks, and gating by
retention class. It returns a checkpoint candidate, never an actuator command.

Its byte-write assumptions, synthetic times and identities, and simplified state
are model-only. It isn't a flight estimator, a chosen firmware encoding, ECC
injection, an MCU timing measurement or a physical reset test. Passing it says
nothing about hardware survival or flight readiness.

## To close EX-03

Use [RST-01](../docs/archive/reliability-execution-plan.md#experiment-rst-01-restart-with-known-evidence)
to carry the model onto the real device.

1. Declare per-phase limits for interruption, state age and uncertainty before
   claiming a pass.
2. Measure reset release, first essential execution, first valid sample and
   state, and optional-service return on an external timebase.
3. Repeat without a debugger attached, and with the logger and comms
   unavailable.

Seán approves policy. Hardware and firmware owners and an independent reviewer
aren't assigned. Exact memory, clock and power behaviour and each mechanism's
EX-07 response are open; EX-03 is not closed. Carry on against the accepted pin
maps and firmware handoff, and run the reset campaign on available target
hardware and then the first PCBA.
