# 1. MCUs and execution

## Circuit

U201 and U401 are STM32H563VIT6, non-SMPS LQFP100. U201 owns acquisition,
estimation, mission state, NOR recording, three energetic outputs, three servo
commands and CAN. U401 owns GNSS, radio and normal USB service.

The UART crosses U4301 TXU0202 with distinct supplies. Reset/source-status
crossings are separate. Flight may request a comms reset; comms has no direct
flight-reset, arm or energetic authority. Each MCU has its own oscillator,
decoupling, supervised reset and SWD access.

Initial operating budgets: 128 MHz CPU, 1 kHz essential schedule and 200 Hz
estimation/policy. Essential execution/blocking initially gets 700 µs of each
millisecond, leaving 300 µs reserve. These are allocations, not measurements.

## Why keep this

Radio stacks, GNSS parsing and USB transfers have variable latency. Separating
them allows a simpler bounded flight loop and independent comms recovery.
Using the same MCU reduces toolchain, spare-part and bring-up differences.
It does not provide dissimilar-computer redundancy.

A single larger MCU could save its neighbour's support circuitry, but it would
need demonstrated timing and fault separation inside one processor. A smaller
comms MCU could save cost/area, but adds another maintained target. Neither
alternative is selected for this pass.

## Failure handling

The flight loop never waits indefinitely for UART, NOR, GNSS or optional I²C.
Frames need bounded size, integrity, sequence and age. Dropping telemetry is
preferable to missing a required flight deadline.

The external flight watchdog is fed only after required tasks progress.
Comms failure does not justify resetting flight. Following an in-flight flight
reset, staging is inhibited; recovery needs validated phase/time/state.
Neither reset nor restored power is evidence that a new flight has begun.

Critical memory placement must follow the H563 ECC/retention regions actually
configured by the firmware. Two checkpoint slots do not survive loss of their
common supply and do not protect against a common corrupt writer.

## Freeze and review

Keep all existing physical pads. The approved exception already installed is
PD10/pad57: servo3 on LPTIM2_CH2 AF3. PD7/pad88 controls complementary readiness.
No free flight GPIO should be invented. External GNSS must retain the existing
logical UART/PPS/reset boundary unless a concrete conflict is reviewed.

Anav owns the scheduler, HAL/driver structure and firmware implementation.
Next evidence: compiled clock/peripheral allocation, measured worst-case timing,
comms-held-reset test, corrupted/flooded UART, reset-class retention and staging
inhibit checks on the first PCBA.

Evidence: [firmware handoff](../firmware-handoff-2026-09-07.md),
[fault contract](../../interfaces/flight-fault-contract.md),
[reset contract](../../interfaces/reset-recovery-contract.md).
