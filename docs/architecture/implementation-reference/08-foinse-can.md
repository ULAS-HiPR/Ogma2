# Preserved reference — not the session reading path

Snapshot retained before the 11 September full-pack rewrite. Detailed component,
pin and calculation evidence follows. Current review status lives in the
[reading pack](../README.md); this snapshot does not authorize implementation.

# 8. Foinse and the vehicle boundary

## Job and current review

**Churro** is the power companion, **Burrito** the standalone core, **Fajita**
the separate local engine controller. Preserve a reusable core while vehicle
power/load requirements change. Monitoring must not be necessary to start
source protection. A BMS, regulator and charger are not interchangeable jobs.

The [joint review](../2026-09-10-session-review.md) reopened servo regulation,
power/charging boundaries and remote CAN actuation. A linear trunk with short
drops and configurable end termination was discussed. **The existing two-node
500 kbit/s Classical CAN interface below is unchanged.** No CAN FD, extra peer
or new connector is approved. A future change must reconcile the propulsion
and stand-emulator interfaces, not just this chapter.

Generic mikroBUS-style experimentation moved toward a **separate payload
carrier** in discussion. It is not a new obligation for Churro or spare buses
on its existing eight-contact interface. Payload work must earn explicit power,
timing and authority boundaries before joining flight-critical infrastructure.

On-rail service and keeping GNSS acquired are useful operating requirements to
develop. Unplugging service is not arming. Preserve separate logic-enable,
charging and physical output-energy meanings; no new charge circuit is chosen.

## Power companion, not another computer

Foinse2 has separate 2S avionics and 6S propulsion inputs. Their positives never
join. TPS26630/CSD18540 source protection starts from its own pack; Croí's
software, I²C and auxiliary supply are not required.

Foinse sends protected 2S to Croí through the coplanar Samtec pair.
Croí returns limited auxiliary 3.3 V for monitoring only. INA228 U5001 measures
propulsion discharge; ADS1115 U6001 reads temperature/voltage. Croí owns the
avionics current monitor, including standalone operation. No duplicate AV shunt,
Foinse MCU or CAN endpoint is needed.

| Samtec contact | Function |
| --- | --- |
| 1 / 2 | Protected 2S to Croí / return |
| 3 / 4 | Croí protected auxiliary 3.3 V / return |
| 5 / 6 | Monitor SCL / SDA |
| 7 / 8 | Aggregated fault / NC |

Both return contacts must individually withstand the full alternative current.
TCA4307 bus recovery does not make monitoring mandatory for source protection.

## Why separate this board

Battery interfaces, high-current paths and propulsion loads change with the
vehicle. Keeping those on Foinse preserves standalone Croí and keeps most
actuator energy away from its logic. The price is connectors, harnesses,
supports and another analog protection board to qualify.

One integrated power/flight board would remove the interconnect but bind the
workhorse computer to each vehicle's power installation. A programmable Foinse
MCU would add a boot/software failure path without a current control job.
Neither alternative is selected.

The installed 8 September draft adds two independent source-enable
loops: J103 avionics, J104 propulsion. Both use vertical two-contact JST GH
`BM02B-GHS-TBT(LF)(SN)` / `GHR-02V-S`. Pin 1 is bounded 3.0 V bias; pin 2
returns to that branch's SHDN. Close to enable; open/unplug to disable.
One maintained two-pole switch may operate both loops, with isolated contacts;
do not join the bias conductors or pack positives. No MCU or Croí AUX needed.

Each pack feeds BAS116, two 4.7k/2010 resistors and LM4040 3.0 V bias clamped
before the connector. Local SHDN has 22.1k pull-down and 100nF filter. OFF
leaves pack entry, sensing and bias live: approximately 0.5 mA bias at nominal
2S and 2.3 mA at nominal 6S, plus existing loads. Unplug packs for storage.

Electronic OFF is not physical energetic or charging isolation. A shorted
contact can force enable; semiconductor faults can defeat shutdown. Contact
bounce can reset a latched fault. Cold startup, bounce/vibration, connector ESD,
clamp failure and thermal/surge behaviour remain installed tests. Native
validation is complete; see the [installed change record](../../installation-change-record-2026-09-08.md).
The external service/charging harness remains pack-specific.

## Source and charging alternatives from the power study

The initial sizing proposed a 2S1P, roughly 4.5 Ah avionics pack and a separate
6S1P propulsion pack of the same provisional capacity class. These were
engineering examples, not purchased or qualified pack assemblies. One 2S pack
must work with standalone Croí; fitting Foinse changes source entry and
distribution, not the basic flight-computer voltage requirement.

| Choice explored | Benefit | Cost / retained boundary |
| --- | --- | --- |
| One common pack for everything | Fewer packs and chargers | Actuator faults/energy demand share more of the avionics source; separate operating packs selected for liquids |
| 2S1P versus 2S2P avionics | 2S2P increases available energy | Doubles cells; start smaller only while measured endurance supports it |
| MCU-less Foinse | Protection can start without Croí, I²C or AUX | Monitoring cannot implement arbitrary autonomous policies; none currently requires a Foinse processor |
| Onboard multi-pack charging | Convenient service integration | Extra conversion, balancing, thermal and fault-control burden; external matched chargers selected |
| Route independent recovery through common protection | Convenient single distribution point | Defeats the claimed power independence; keep its qualified source path separate |

The original P45B cell example used minimum nominal energy and a **70% planning
factor**, not measured cold-pack discharge data. That gave about 21.7 Wh for
2S1P against a 19 Wh example mission. Continuous 3 W operation did not fit the
same allowance. Pack temperature limits can also be narrower than board limits.
Endurance closes with the assembled pack, wiring and real mode profile, not the
cell's advertised amp-hours. No loose spring cell holder is proposed for flight.
[Power contract](../../../interfaces/power-contract.md),
[cell datasheet used by the study](https://www.molicel.com/wp-content/uploads/INR21700P45B_1.4_Product-Data-Sheet-of-INR-21700-P45B-80109.pdf).

### “24 V solenoid” does not mean direct 6S is valid

The power study used a representative 24 V ±10% coil class to test the idea,
not to select a propulsion valve. A 6S pack spans about 25.2 V full to 18 V
at the provisional lower source bound. It starts inside that example coil's
21.6–26.4 V band and then leaves it. More cells can violate the upper end.
Nominal battery voltage is not actuator compatibility.

| Explored conversion route | Finding |
| --- | --- |
| TRACO THN 30-2415WI | Convenient 9–36 V to 24 V / 30 W proof candidate; reviewed altitude/convection conditions prevented calling it flight-qualified |
| Pololu S18V20F24 | Lower-cost nonflight experimental option; thermally dependent output capability, not a qualified flight rail |
| TI LM5176 converter circuit | Could regulate across the 6S window without an MCU; requires magnetics/FET/compensation/thermal design for actual loads |
| TI TPS552882 | Rejected for this job: reviewed output limit was 22 V despite a higher input rating |

None is a populated Foinse 24 V stage. Raw propulsion power and its paired
return are drawn; actual coil demand must decide whether and where conversion
is needed. Coil suppression and recirculation belong at the local driver/load
loop, not at a remote converter in the bay.
[TRACO datasheet](https://www.tracopower.com/thn30wi-datasheet),
[LM5176](https://www.ti.com/lit/ds/symlink/lm5176.pdf),
[TPS552882](https://www.ti.com/lit/ds/symlink/tps552882.pdf).

### Why the interboard connector is larger than a signal header

The original Micro-Fit BMI candidate had unresolved availability, geometry and
parallel-contact current assumptions. The Samtec MPT/MPS coplanar pair trades
width and through-hole assembly for an inspectable single mating interface.
One electrical contact carries the complete provisional feed; the design does
not depend on equal sharing between nominally parallel contacts.

Each electrical contact has six solder tails. The 48 holes are eight contacts,
not 48 independently assignable pins. The drawing audit recorded a 52.63 mm
footprint envelope and 7.39 mm nominal board-edge gap. Screw-down features
secure each body to its PCB; they do not by themselves hold the mating halves
together. Supports and engagement retention remain mechanical work.
[Samtec MPT](https://www.samtec.com/products/mpt-08-01-01-l-ra-sd),
[Samtec MPS](https://www.samtec.com/products/mps-08-01-01-l-ra-sd).

Contacts 2 and 4 share board ground. If the main return opens, the auxiliary
reference may carry unintended load current. Its copper/bonding must support
that fault; it is not extra normal current-capacity credit. A connector's
catalogue rating never replaces the complete return-path audit.

## Propulsion and CAN

Croí carries CAN and reference only: JST GH contacts 1 H, 2 L, 3 reference.
Use twisted H/L conductors up to the connector, with a short untwisted breakout.
The connector does not need to twist the contacts internally.

TCAN3413, 500 kbit/s Classical CAN and fixed 120 Ω ends serve the two-node
Ogma/propulsion line. No star, powered bus or speculative expander.
The controller owns local engine sensing, permissives, valves, redlines and
abort. It must act safely if Ogma, CAN or the operator disappears.

Foinse supplies paired propulsion power independently of Croí logic.
An open power return must not divert actuator current into CAN reference.
Common ground and signal protection do not prove isolation.

## Remaining choices

The present raw 6S branch is roughly 3 A nominal; it is not a frozen solenoid
budget. Coil count/current/duty, clamps and whether regulated 24 V is needed
remain propulsion inputs. External matched balance chargers use protected,
segregated service wiring; no onboard charger or invented balance pinout.

Next tests: autonomous startup with AUX absent, bounded monitor-bus faults,
source short/brownout selectivity, actual return faults, CAN loss/bus-off and
peer resets. Do not expand this review into designing unspecified valves.

Evidence: [vehicle boundary](../../../interfaces/ogma-foinse-propulsion-boundary.md),
[power contract](../../../interfaces/power-contract.md),
[sensing revision](../../sensing-indication-time-review-2026-09-07.md).
