# Ogma 2 block chapters

2 November 2026. Each chapter states the decided or proposed design for one
block. [Decisions](../../decisions.md) say which is which.

| Chapter | Contents |
| --- | --- |
| [System tour](system-tour.md) | Whole system, power and data, connector photos |
| [01 Processors](01-mcus.md) | Flight and comms MCUs, pin maps |
| [02 Power](02-power.md) | Source path, domains, enable hold, USB, hold-up |
| [03 Outputs](03-energetic-outputs.md) | Recovery and staging outputs: two switches per channel, fuses, arms, continuity, pad checks |
| [04 Servos](04-servos.md) | Burrito's servos removed (D-19Nov.2); rules for closed-loop actuator nodes |
| [05 Service](05-service-status-time.md) | Indication, USB readback, time |
| [06 GNSS and radio](06-gnss-radio.md) | Receiver limits, radio, reference assembly |
| [07 Sensors and recording](07-sensors-logging.md) | Sensors, magnetometer, NOR format, recording trigger |
| [08 Churro and CAN](08-foinse-can.md) | Power board, rail umbilical, what CAN carries |
| [09 Connectors](09-connectors-arming.md) | Inventory, FC enable, arm connector |
| [10 Recovery logic](10-recovery-logic.md) | Events, lockouts, after-reset behaviour (draft); pad datum, pad telemetry, ground-test mode |
| [11 Verification](11-verification.md) | Release gates, campaigns, bench and EuRoC tests, capture assertions |
| [Capture specification](schematic-capture-spec.md) | Exact deltas against native CAD |
| [Justifications](justifications/README.md) | Reasons and calculations |

Proposed pin maps: [flight](proposed-flight-pinout.csv), [comms](proposed-comms-pinout.csv)
(22 September nets; the capture specification lists the October and November pad
changes, and the [firmware interface](../firmware-interface.md) has every pin by
function).
