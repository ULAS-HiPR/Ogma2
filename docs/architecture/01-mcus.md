# 1. Processors, timing and restarting

**Retained:** separate flight and communications responsibilities; flight owns
vehicle CAN and recovery authority. **Open:** exact processor choice per role
and firmware scheduling approach.

## Why two processors?

Radio handling, USB transfers and GNSS parsing can take variable amounts of
time. The flight processor must not miss a measurement or decision deadline
because the other processor is busy servicing a laptop.

```mermaid
flowchart LR
  S["Sensors"] --> F["Flight processor<br/>bounded acquisition and decisions"]
  F --> N["Local recording<br/>bounded transactions"]
  F --> O["Permitted local outputs"]
  F <-->|"CAN"| E["Engine peer"]
  F <-->|"Bounded messages"| C["Communications processor"]
  C <--> U["USB service"]
  C <--> G["GNSS receiver"]
  C <--> R["Radio"]
  F -.->|"May request comms restart"| C
```

The dotted arrow is a reset-request relationship, not another data bus.
Communications has no reciprocal authority to reset flight or arm its outputs.
The intended test is simple to state: hold communications in reset and show
that the essential flight functions still work.

There are limits. Both processors share the board, upstream conversion and
installation. Two chips do not protect against all common power, mechanical
or software mistakes.

## Do both jobs need the same chip?

The existing draft uses two STM32H563 devices. Using the same part simplifies
tools, spare parts and bring-up. The meeting correctly reopened whether the
communications role needs the same resources.

| Approach | Gain | Cost / evidence needed |
| --- | --- | --- |
| Keep identical processors | One maintained target and familiar tools | May spend unnecessary area and cost on communications |
| Smaller communications processor | Potential area/cost saving | Check real USB, radio, GNSS, buffering and debug needs; maintain another target |
| One processor for everything | Removes a processor and support circuitry | Must demonstrate timing and fault separation inside one device |

**Recommendation for comparison, not a part decision:** retain the two-role
split while checking resources separately for each role. Start with actual
peripherals, pins, memory and workload. A smaller package is useful only if it
fits those needs. Fewer pins alone do not establish greater reliability.

## Where the pins actually went

The 11 September audit checked both 100-pad allocations against a fresh
schematic netlist. **Flight is pin-full in this draft; comms is not.**
This says nothing about CPU utilisation.

| Of each package's 100 pads | Flight | Comms |
| --- | ---: | ---: |
| Supply, ground, reference, core-capacitor, reset and boot pads | 20 | 20 |
| Connected port pins, including clocks/debug | 79 | 27 |
| Labelled but unused radio reservations | 0 | 2 |
| Unfitted low-speed crystal reservations | 0 | 2 |
| Quiet PC13 reservation | 1 | 1 |
| Other unallocated port pins | 0 | 48 |
| **Total** | **100** | **100** |

The two comms radio reservations are remnants of the earlier radio interface:
their nets contain only the MCU pin. They are not driving the current module.
The low-speed comms crystal pins are also unconnected in the schematic.
These are possible reclamations, not changes made by this audit.

### Flight allocation

Each branch below is a **pin budget**, not a data or power connection.
Counts include peripheral signals, chip selects, enables and diagnostics.

```mermaid
flowchart LR
  F["Flight MCU<br/>100 physical pads"] --> S["Sensors: 24<br/>3 SPI buses: 12<br/>3 data-ready inputs: 3<br/>5 supply enables: 5<br/>2 pressure I2C buses: 4"]
  F --> E["Energetic channels: 19<br/>6 request/select lines<br/>2 permits + 2 latch controls<br/>2 arm inputs<br/>6 current/continuity ADC inputs<br/>1 output-rail ADC input"]
  F --> N["Recording: 8<br/>Quad-SPI: 6<br/>Enable + reset: 2"]
  F --> V["Servos: 5<br/>3 PWM + power enable<br/>1 supply ADC"]
  F --> C["External CAN: 4<br/>RX + TX + power enable + standby"]
  F --> L["Comms boundary: 4<br/>UART TX/RX + power enable + reset"]
  F --> A["Auxiliary monitoring: 3<br/>I2C pair + domain enable"]
  F --> H["Other monitoring/status: 6<br/>Battery + logic ADC: 2<br/>Watchdog + fault input: 2<br/>Buzzer + readiness: 2"]
  F --> D["Clocks/debug: 6<br/>HSE pair + LSE pair + SWD pair"]
  F --> R["Quiet reserve: 1<br/>PC13"]
  F --> P["Dedicated support pads: 20<br/>Supplies, returns, references,<br/>core capacitors, reset and boot"]
```

**The big consumers are sensors and output supervision: 48 pins together.**
Three energetic channels alone use 19, not three. Each independently switched
sensor adds supply control and often a data-ready line on top of its bus.
This is the cost of the current observability and fault-containment choices,
not proof that every choice is necessary.

The early 6 September study reserved only 40 flight port pins and explicitly
left diagnostics and protection controls unallocated. That preliminary count
is not the current design. The later complete allocation consumes 79.

### Communications allocation

```mermaid
flowchart LR
  C["Comms MCU<br/>100 physical pads"] --> R["Radio: 8 connected<br/>SPI: 4<br/>Reset + BUSY + IRQ + power enable: 4"]
  C --> G["GNSS: 5<br/>UART pair + PPS + reset + power enable"]
  C --> U["USB/source status: 5<br/>USB pair + VBUS present<br/>Configuration valid + battery valid"]
  C --> F["Flight link: 2<br/>UART TX/RX"]
  C --> H["Health/status: 2<br/>Fault input + status LED"]
  C --> D["Clock/debug: 5<br/>HSE pair + SWD pair + trace output"]
  C --> L["Unused reservations: 5<br/>Old radio RXEN/TXEN: 2<br/>Unfitted LSE: 2<br/>Quiet PC13: 1"]
  C --> N["Other unallocated port pins: 48"]
  C --> P["Dedicated support pads: 20<br/>Supplies, returns, references,<br/>core capacitors, reset and boot"]
```

Port-by-port allocation, including actual pad numbers and net names, is in the
[pin audit](../mcu-pin-capacity-audit-2026-09-11.md). The diagrams deliberately
group by job so the reason for each allocation is visible.

## The investigation result

**Keep the flight part for now; compare a smaller package of the same H563 for
comms before changing MCU families.** That recommendation follows the actual
asymmetry above, rather than assuming both roles need identical packages.

The H563 LQFP64 candidate keeps the same processor and memory class in a smaller
package. The current comms signals can be mapped at the desk-check level:
keep the existing functional port choices except move the flight-link UART
from PD8/PD9 to PC10/PC11, both USART3 AF7. Those current pins are unallocated
on comms. The exact candidate allocation is in the audit.
This is a proposal, not a drop-in footprint or an approved remap.
[ST package and alternate-function tables](https://www.st.com/resource/en/datasheet/stm32h563vi.pdf).

A genuinely smaller device such as H503 also has USB, but its 32 KiB main RAM
makes the current 32 KiB service-block contract an immediate design question.
Streaming may avoid buffering a whole block; that would need an explicit
implementation, not an assumed fit. Start with package reduction unless a
measured cost/power benefit justifies tighter memory and another target.
[ST H503 datasheet](https://www.st.com/resource/en/datasheet/stm32h503cb.pdf).

For flight, reclaim pins by reviewing functions, not weakening protection merely
to make a count fit:

- Removing an unnecessary third local PWM would recover **one** pin.
- SPI rather than quad-SPI recording could recover **two**, but needs throughput
  and NOR-mode validation.
- Sharing sensor buses could recover pins, at the cost of shared fault and timing
  dependencies. It is not a free simplification.
- Comms can own noncritical display work, but moving flight-owned authority to
  exploit spare comms pins would contradict the intended failure boundary.

These savings are alternatives, not additive approved changes. PC13 remains
reserved; spare comms pins cannot be used as flight-local pins without a new
interface and dependency.

### What can be settled without hardware?

The pin count, proposed package mapping and resource budget can be investigated
now; this audit does that. Firmware size, stack usage, execution time and actual
power need a build or measurement. No Ogma2 target firmware build is present in
this repository, so there is no evidence yet that either CPU is compute-full
or that a slower part meets the deadlines.

The draft reserves 11 DMA channels for flight and six for comms, but a reservation
is not a tested request/arbitration configuration. The H563 same-peripheral
package change avoids inventing a new DMA architecture; it still needs target
configuration and bring-up.

## What makes the execution predictable?

The draft budgets a 1 kHz essential schedule and 200 Hz estimation/policy at
128 MHz. A 700 microsecond essential-work allowance leaves 300 microseconds of
each millisecond reserved. These are **unmeasured allocations**, not proof the
code fits.

An RTOS schedules tasks; bare-metal firmware schedules work without that layer.
Neither is automatically faster or safer. Anav's architecture needs to show
which work runs when, how long it can block, and how failed peripherals are
abandoned without stalling flight.

The watchdog is an independent timer that can force a reset if required
execution stops progressing. It should be fed because essential tasks actually
completed, not merely because an interrupt still runs. Losing a nonessential
logger after launch must not create an endless reset cycle.

## Three kinds of memory

| Memory | What it does | What not to assume |
| --- | --- | --- |
| Program memory | Holds executable firmware | Correct storage does not make the program correct |
| Working RAM | Holds current estimates, buffers and execution state | Contents need not survive power loss |
| External nonvolatile NOR | Holds the flight record | A write interrupted by power loss may be incomplete |

ECC is error-correcting coding for specified memory regions and error patterns.
It does not correct arbitrary software decisions or make a processor
radiation-qualified. The existing device has both protected and unprotected
RAM regions; placement of critical state and buffers must follow that map.
Two retained checkpoint copies help with interrupted updates, not loss of
their common supply or a writer corrupting both.

## Reset is not a new flight

```mermaid
flowchart TD
  R["Flight processor restarts"] --> D["Keep output inhibits<br/>capture reset cause"]
  D --> V{"Trustworthy retained identity,<br/>time and state?"}
  V -->|"No"| U["Primary continuation unavailable<br/>independent recovery allocation applies"]
  V -->|"Yes"| P["Validate current measurements and phase"]
  P --> C["Only the permitted phase-specific recovery path"]
  D --> I["Further sustainer ignition inhibited<br/>for this flight"]
```

“Staging” here means igniting a subsequent rocket stage. It does not mean boot
calibration. An in-flight reset must not declare the rocket stationary,
recalibrate its launch height or replay every event. Recovery continuation and
sustainer ignition have different hazards.

A surviving clock does not prove that the estimate survived. A valid checksum
does not prove that its timestamp is recent. Complete power loss is different
from a processor-only reset with valid supplies.

## Next pass through this chapter

Can everyone explain why the two roles exist and what each failure loses?
Then compare the processor resources and scheduling options. Close the choice
with compiled allocations and measured timing, including unavailable peripherals
and communications held in reset—not a headline clock speed.

[Next: power](02-power.md) · [Detailed devices, memory and timing evidence](implementation-reference/01-mcus.md) · [Reset contract](../../interfaces/reset-recovery-contract.md)
