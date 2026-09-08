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
