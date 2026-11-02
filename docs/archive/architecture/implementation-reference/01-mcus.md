# Preserved reference — not the session reading path

Snapshot retained before the 11 September full-pack rewrite. Detailed component,
pin and calculation evidence follows. Current review status lives in the
[reading pack](../../../architecture/README.md); this snapshot does not authorize implementation.

# 1. MCUs and execution

## Job and current review

One processor must keep sensing and making timely flight decisions while the
other handles variable-latency radio, GNSS and USB work. Separating those jobs
does not make two independent flight computers: PCB and upstream power remain
shared. Comms failure containment must be tested, not inferred from chip count.

The [10 September review](../2026-09-10-session-review.md#3-processor-selection-and-firmware-structure)
reopens **which MCU each role needs**, not the right to silently replace them.
Compare exact peripherals/pins, memory protection, timing, area/cost and the
burden of two maintained targets. A smaller comms MCU is a candidate; no part
or RTOS/bare-metal policy was selected. Current CAN ownership was checked in
the meeting: flight MCU, not comms.

ECC means error detection/correction in specified memory regions. It is not
radiation qualification or protection against all wrong values. External NOR
stores the flight record; MCU RAM holds live working state. Keep those distinct.
The resource figures below are allocations awaiting measured execution times.

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

## What the earlier MCU comparison actually found

The hardening study initially led with H573. The accepted resource work then
used H563VIT6 first, keeping H573 as the direct comparator. That sequence matters:
the old table is research history, not an instruction to replace the installed
H563. Selection followed the required peripherals, memory placement, package
and support burden rather than maximum headline clock speed.

| Researched option | What it offers | Tradeoff and disposition |
| --- | --- | --- |
| H563VIT6, current | STM32 toolchain, inspectable LQFP100, required peripheral allocation and partly ECC-protected memory | No core lockstep; unequal RAM protection; tight flight pin budget. Exact allocation passed desk/native checks, not target timing qualification |
| H573 | Closely related M33 safety/resource comparator; initial study leader | Also lacks lockstep and has unprotected RAM regions. No recorded mission benefit justified changing the accepted H563 allocation |
| TI TMS570LS1227 | Lockstep R4F cores, ECC, BIST and error-signalling hardware | Larger 144-pin package, separate 1.2 V core rail, different tools and smaller memory budget. Reopen if a demonstrated core-fault requirement earns that burden |
| NXP S32K3 family | Automotive safety architecture, ECC and lockstep options | Exact derivative selection, new tools and safety framework were not closed. Family capability is not a selected board |
| SAMRH71 / VA41630 / TMS570LC4357-SEP class | Radiation-oriented devices and supporting evidence | Cost, procurement, package/rail and integration burden aimed at a different mission class. No quantified short-sortie need justified them |

Source trail: [dated hardening comparison](../../karman-line-mission-hardening-report.md#candidate-comparison),
[accepted EX-04 resource work](../../reliability-execution-plan.md),
[ST exact H563 datasheet](https://www.st.com/resource/en/datasheet/stm32h563vi.pdf),
[TI TMS570LS1227](https://www.ti.com/lit/ds/symlink/tms570ls1227.pdf).

The comparison is not a measured failure-rate ranking. Automotive safety
features do not establish radiation qualification, and commodity parts do not
become space-qualified because they have ECC. The mission is a short sortie
and return, not years in orbit. The installed power, software and recovery
architecture still decide what a fault does to the vehicle.

### ECC means a memory map, not a checkbox

The exact-device study allocated the H563 memory as follows. These are planned
uses; the actual linker and option-byte configuration must enforce them.

| Region | Available role with the studied ECC configuration | Consequence |
| --- | --- | --- |
| SRAM1, 256 KiB | No ECC; disposable logger/USB staging | Never the sole authoritative estimator or flight-state copy |
| SRAM2, 64 KiB | ECC-protected critical stacks/control | Include interrupt nesting and bank-specific headroom |
| SRAM3, 256 KiB usable with ECC | Protected acquisition/estimator buffers | Upper 64 KiB of the physical bank is consumed by ECC storage, not application capacity |
| Backup SRAM, 4 KiB | Protected checkpoint slots if configured and powered | Two slots share supply and writer; not independent recovery |

The initial protected-RAM spending cap was 223 KiB, preserving roughly 30%
reserve across the 320 KiB main protected capacity, with per-bank limits too.
DMA accessibility, ownership and cache behaviour need explicit checks. A map
file checker should fail a build that puts critical state in disposable RAM.
[ST RAM configuration training](https://www.st.com/content/ccc/resource/training/technical/product_training/group1/9d/5c/38/7e/32/71/41/e0/STM32H5-RAM-configuration-RAMCFG/files/stm32h5-ram-configuration-ramcfg.pdf/jcr:content/translations/en.stm32h5-ram-configuration-ramcfg.pdf).

ECC corrects specified memory errors; it does not stop software writing the
wrong valid value, repair a failed clock or independently validate a control
decision. The H5 study also found that a corrected read is not automatically
written back. Scrubbing needs controlled read/correct/rewrite ownership so it
does not overwrite a concurrent DMA update. Supported diagnostic injection
coverage and ordinary software corruption tests must remain separately named.
[ST safety manual](https://www.st.com/resource/en/user_manual/um3150-stm32h5-series-safety-manual-stmicroelectronics.pdf).

### Package and timing evidence

The pin audit used the non-SMPS LQFP100 table, not the family feature list.
PB11 and PE1 are not bonded on this variant. Both VCAP pads, supplies, ADC
channels, alternate functions and interrupt numbers were checked. The flight
allocation had no spare general GPIO; the later third servo reclaimed PD10,
and complementary readiness retained red/green with PD7. A larger LQFP144
remains a real fallback if a necessary boundary cannot fit, not the current part.

Three SPI buses let the IMUs and high-g part transfer independently. The
960/1000/800 Hz streams are still asynchronous. DMA removes CPU copying, not
all bus contention or scheduling work. The 128 MHz / 700 µs essential-budget
choice was a resource allocation; no measured worst-case runtime supports it
yet. Use the [current handoff](../../firmware-handoff-2026-09-07.md) for clocks,
DMA requests and final physical pins, rather than an old research CSV.

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

Evidence: [firmware handoff](../../firmware-handoff-2026-09-07.md),
[fault contract](../../../../interfaces/flight-fault-contract.md),
[reset contract](../../../../interfaces/reset-recovery-contract.md).
