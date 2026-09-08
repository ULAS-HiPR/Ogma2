# 8. Foinse and the vehicle boundary

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

External power-switch connections are authorised. Exact contact arrangement,
connector and safe default need a checked implementation. Ordinary source
switching must not replace independent recovery power or physical energetic
arming. The external service/charging harness remains pack-specific.

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

Evidence: [vehicle boundary](../../interfaces/ogma-foinse-propulsion-boundary.md),
[power contract](../../interfaces/power-contract.md),
[sensing revision](../sensing-indication-time-review-2026-09-07.md).
