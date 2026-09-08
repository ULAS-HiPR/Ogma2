# 3. Energetic outputs

Three channels remain: two recovery events and a distinct sustainer/staging
channel. This page explains the draft; it does not authorise energetic testing.

## Circuit

Each channel has a non-retriggerable LTC6993 one-shot, independently gated
high-side TPS1H100 and low-side CSD17318 paths, current/continuity diagnostics
and reset-default pulls. Channel families are 63xx, 64xx and 65xx.

The staging eligibility latch U6001 and surrounding hardware permissions
separate channel 3 from recovery. A flight reset must clear eligibility.
New-flight eligibility requires deliberate disarmed preparation, not merely a
voltage returning.

J6601 is six-contact Micro-Fit 430450600:

| Channel | High contact | Low contact |
| --- | --- | --- |
| 1 | 1 | 4 |
| 2 | 2 | 5 |
| 3 | 3 | 6 |

Use a retained harness to the replaceable charge assemblies. Raw-wire terminals,
when needed during development, belong on detachable adapters rather than the
flight PCB.

## Why the additional hardware

The physical arm break prevents software alone from supplying energetic power.
A bounded one-shot limits a command duration independently of an application
delay. High- and low-side control provide distinct conditions along the load
path. These choices add circuitry and require a fault analysis; their presence
alone is not proof of single-fault no-fire safety.

A lone low-side FET is smaller, but has a different failed-short and
short-to-structure exposure. It is not the selected simplification.
Optocouplers would not isolate a shared battery-return disturbance by themselves.

## Alternatives and failure cases behind the circuit

The research treated recovery and sustainer ignition as different hazards.
Recovery may need a validated continuation after a reset; an ambiguous reset
must not permit a new sustainer ignition. That is why channel 3 is not merely
another copy of the recovery software event table. The hardware eligibility
state and reset policy must express that difference.

| Approach considered | Attraction | Limitation / current judgement |
| --- | --- | --- |
| MCU GPIO plus one low-side FET | Minimum area and familiar implementation | Firmware duration, stuck request and failed-short paths need other protection; not the chosen boundary |
| Timer peripheral only | Better pulse timing than a software delay | Shares processor configuration/reset fault domain; does not provide the selected independent duration ceiling |
| External non-retriggerable one-shot | Bounds a single accepted request despite software timing failure | Exact suffix, reset behaviour and actual timing tolerances matter; it cannot select a safe pulse width without load data |
| High-side plus low-side control | Distinct conditions along the load path; driver diagnostics | More circuitry and possible sneak paths; not automatically single-fault safe |
| Third onboard recovery MCU | Another application execution path | Still shares installation, board and likely power faults; not a replacement for independent recovery |
| Independent qualified recovery assembly | Separates more common causes | Extra hardware, battery and integration burden; retained for the relevant missions |

The original part work specified the rising-edge non-retriggerable LTC6993
**-1**, not a retriggerable variant. TPS1H100 supplies high-side switching and
diagnostics; CSD17318 supplies the low-side path. These are different jobs,
not three arbitrary layers of the same protection. The physical energy break
is an additional assembly boundary and is still not completed.
[LTC6993](https://www.analog.com/en/products/ltc6993.html),
[TPS1H100-Q1](https://www.ti.com/lit/ds/symlink/tps1h100-q1.pdf),
[CSD17318Q2](https://www.ti.com/lit/ds/symlink/csd17318q2.pdf).

### Why the circuit is not finished by selecting those ICs

The investigation distinguished stuck GPIO, driver failed short, brownout,
wrong-channel selection, shared returns, diagnostic leakage and external
wiring faults. A one-shot can bound its output while a failed semiconductor
still bypasses it. An optocoupler can separate a signal while a shared power
return still couples the disturbance. Every claimed safeguard must be traced
through source, both switching paths, connector, load and return.

Continuity sensing deliberately puts some energy into a load circuit. Its
safe margin depends on the actual initiator's no-fire envelope and worst-case
voltage, resistance and faults. The missing resistor/pulse values are therefore
real engineering gaps, not formatting placeholders. No generic value should
be populated solely to remove ERC errors. The DNP state preserves that boundary.
[Detailed hazard and circuit study](../karman-line-mission-hardening-report.md#energetic-outputs-and-recovery).

### Why the connector leads to a remote replaceable assembly

The six-contact Micro-Fit keeps each channel's high/low pair distinct. A retained
plugged harness can lead to accessible charge terminals away from the computer.
That separates repeatable PCB connection from the field job of changing an
ematch. Screw terminals were attractive for size, but fiddliness, exposed
conductors and loose strands were the objections; ordinary lever terminals
spend more space. Neither belongs on the flight computer merely because the
load is temporary. Development adapters remain possible without changing the
flight PCB connector. [Connector/readiness revision](../connector-servo-readiness-revision-2026-09-07.md).

## What remains unfinished

R6310/R6410/R6510 energy links, pulse/current settings and continuity injection
parts remain DNP. There is no completed physical arm assembly or proven no-fire
margin. Arm-voltage absence is not independent proof that the mechanical
break is open. The ordinary external computer-power switch must not replace it.

Exact initiator limits, harness resistance, arm zones, disarm-proof contacts,
group protection and continuity discrimination remain load/installation work.
Current increase does not prove ignition; absence of a logged increase does not
permit a retry. A storage or telemetry gap is not a safe-action decision.

Review the complete source → arm break → channel → connector → load → return
path visibly in the schematic, with diagnostic branches shown as branches.
Then test defaults, reset classes, wrong-channel faults and pulse behaviour
with inert loads. Keep the Kármán recorder population physically unpowered.

Evidence: [fault contract](../../interfaces/flight-fault-contract.md),
[power contract](../../interfaces/power-contract.md),
[accepted baseline](../architecture-acceptance-2026-09-07.md).
