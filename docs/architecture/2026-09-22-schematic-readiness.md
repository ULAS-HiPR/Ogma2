# Schematic-readiness evidence — 22 September 2026

**Desk audit and recommendations. No accepted-stack, CAD, firmware or flight
release change.** Start with the [connected review](00-overview.md#can-this-become-schematics).
This is its supporting evidence, not another required sequential reading pack.

## Later synthesis supersedes the recommendations below

The same-day [capture specification](schematic-capture-spec.md) closes ordinary
electronics choices with three regulators, PD10 service recovery, revised domain
allocations, aligned NOR sectors and defined Churro probe/source interfaces.
This audit preserves the earlier findings and two-rail calculations as history;
its numeric recommendations are not the current capture instructions. Native
connectivity evidence remains applicable because CAD has not changed.

## Scope and source confidence

Inspected all ten active chapters, the controlling power/reset/vehicle contracts,
current-system, hardware status and both native netlists. Fresh KiCad exports on
22 September match the tracked exports in **all pin/net assignments and component
reference/value/footprint tuples**: Burrito 2,179 pins / 643 components; Churro
306 pins / 113 components. All 44 Burrito schematic hashes match the stored
check report. Export timestamps and absolute paths differ; raw XML hash equality
is not a connectivity criterion. No new ERC/DRC or hardware pass is implied.

Remote `docs/reliability-review-execution` was fetched; audit started at
`9a8c2a2`, equal to the remote tip. The 19 September proposal and 8 September
CAD remain different authority layers. A complete circuit exists for several
blocks whose engineering suitability remains provisional.

## Findings that changed the active pack

| Finding | Evidence / consequence | Action now in the chapter |
| --- | --- | --- |
| The comms voltage calculation ignored reset-release hysteresis and divider tolerance | Original divider + switch leaves only about 20.5 mV at 300 mA above the conservative supervisor release bound, before layout/transients | [Power](02-power.md#voltage-margin-including-reset-release): propose 31.9 kΩ / 10 kΩ service divider, 3.352 V; calculated margin ~75.8 mV; 50 mV additional loss allocation |
| USB permission was conflated with available local current | U4401's preconfiguration limit can start at 50 mA; configured R4403 gives ~387–491 mA; full-load example requires ~649 mA | [Power](02-power.md#usb-is-a-separate-load-mode): restricted bootstrap and readback modes; inrush and deconfiguration handling |
| The new aggregate limiter has no flight-owned restart | U1501 EN proposed tied to BOOT_3V3; latched fault removes every service | Explicit source-cycle recovery and D1 acceptance, rather than implying a comms reset repairs it |
| Selectivity checked only for a comms fault | NOR's retained 100 kΩ limit can reach ~306 mA | Full local-limiter table; conservative NOR-fault example ~706 mA against ~729 mA aggregate minimum |
| Mission energy and schematic current were different budgets | 600 mA at 4 V is 2.4 W; eight hours is 19.2 Wh before upstream losses/reserve | Separate 8 h + 4 h energy closure from instantaneous rail ratings |
| Readback asked for evidence the MCU cannot directly observe | Buck/core-input/LDO PG nodes do not reach flight GPIO; fault net aggregates sources | [Service](05-service-status-time.md#schematic-handoff): measured, inferred and unavailable states separated |
| Recording slack depended on undefined encoding | 20% allowance included framing/commit; exact packed format not frozen | [Recording](07-sensors-logging.md#schematic-handoff): footer constraint and conservative 6,452,736-byte spare bound; combined-rate queue duration corrected |
| Churro's concise page concealed implementation and unfinished interfaces | Two protected source circuits, monitoring, returned AUX and seven named connector roles already exist | [Churro](08-foinse-can.md#churro-circuit-inventory): inventory, source cascade, ground-return and monitoring-loss consequences |
| Outputs were described as unresolved without distinguishing draft from absence | Existing three-channel draft and DNP safeguards; physical arm assembly and output requirements unfinished | [Output status](03-energetic-outputs.md#what-exists-and-what-is-missing): explicit design blocker, separate responsible review |

Two suspected wiring omissions were **not defects**: sensor ILIM tied to IN
selects the manufacturer's low-current mode; TPSM63603 CBOOT/RBOOT may be left
open to retain its internal resistor/capacitor arrangement. Its EN/SYNC pin 2 is
tied to selected input; pin 22 biases the internal LDO from 4 V. Electrical
roles differ despite collapsed “supply” symbol labels. Preserve the valid
connections. [TPS2553 §9.5](https://www.ti.com/lit/ds/symlink/tps2553.pdf),
[TPSM63603 pin table and §7.3.10](https://www.ti.com/tw/lit/gpn/tpsm63603).

## Dependency closure

| Claimed function | Actual dependencies | Review disposition |
| --- | --- | --- |
| Autonomous flight computation | Source, shared buck, held flight path, flight MCU/clock/supervision and usable sensors | Keep comms/GNSS/USB/recorder/monitor transactions out of essential progress gates |
| Continuous recording | Flight MCU, staging/drain schedule, service LDO, NOR limiter, flash and valid prepared space | Separate failure from flight CPU survival; no final-flush promise from flight-only hold-up |
| Remote control | Flight execution, service rail, CAN branch, harness, peer supply/controller and age/expiry contract | A mission that requires it cannot call the entire service group nonessential |
| Ground visibility | Comms supply/firmware, correct radio mode, antenna path, actual receiver and ground logging | Link loss and vehicle loss differ; local NOR does not help recover data from an unrecovered vehicle |
| GNSS aiding / UTC association | Receiver envelope/reception, comms power/firmware, UART/time mapping | Valid data may be absent while the rest operates; no blocking wait for a fix |
| Source telemetry | AUX power, boundary/buffer, sensor validity and read scheduling | Protection remains autonomous; lost measurement is unknown, not zero current or healthy power |
| USB service | Permitted input current, bootstrap profile, comms and only the required flight/service loads | Cannot inherit the full battery profile; configuration must be withdrawn on USB state change |
| Pack endurance | Mode durations/current, converter losses, cell condition and usable capacity above UVLO | Source ratings and nominal watt-hours alone do not meet the endurance requirement |

Both low-g accelerometers, both pressure sensors, the shared board and the common
source each have correlated limitations. Dissimilar components do not create a
full-envelope measurement or independent recovery system. Keep the provisional
platform envelope for implementation; mission-specific simulation and measured
installation qualify its use. Do not demand final mission firmware before
placing the agreed parts, or describe placement as mission validation.

## Design decisions versus later verification

**Before freezing the affected schematic:** D1–D5 in the overview; exact source/
load interfaces; physical output-arm design; power tolerance and startup paths;
package migration; connector mating/exclusion; monitor lead protection. A load-
dependent power stage cannot be completed by writing “test later.”

**Before ordering:** accepted schematic represented in native CAD; reviewed ERC;
exact land patterns and assembled height; routed returns/decoupling/RF; thermal
and surge/fuse design; connector/mount/vent/antenna installation. Current boards
are unrouted. Burrito's stored ERC has four errors and six warnings; Churro's
has none. Stored PCB reports have 61 and 24 findings respectively, plus unrouted
connections and missing Nano-Fit. Counts are 8 September evidence, not reruns.

**On the first complete PCBA:** scoped power/current/rail tests with inert loads;
source-mode transitions; concurrent acquisition/recording; partial-power and
comms-reset behavior; stale/malformed input; interrupted record/service update;
actual longest CAN harness and RF installation. Continue using the agreed first-
full-PCBA sequence. No new mandatory coupon-board programme is introduced.

**Before mission use:** measured envelope, qualification, independent recovery
where required, responsible output safety review and the actual installed
assembly. This audit does not grant operational release.

## Reproduction and remaining evidence limits

Run [component-proposal-checks.py](../calculations/component-proposal-checks.py)
for current-limit equations, voltage corners, source truth table, pin-map
structure, capacity and energy arithmetic. Results depend on explicitly stated
load and efficiency assumptions; they do not simulate transients or firmware.
Manufacturer sources are linked beside affected calculations.

The Macronix full timing PDF still could not be fetched. Indexed primary text
supports the cited 1.5 ms maximum; exact fitted-revision timing remains an
explicit component-document check. Do not upgrade that source status to a
fully inspected datasheet. No test data, team acceptance or ownership assignment
has been fabricated to make the review appear closed.
