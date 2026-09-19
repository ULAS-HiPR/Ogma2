# Ogma 2 — component design proposal

19 September 2026. **Prepared for joint review; CAD and installed contracts unchanged.**

Open **[the component review](00-overview.md)**. Power, signals, connectors,
operating states and the consequential choices are together there. Use the linked
chapters for a questioned calculation, component or pin; no sequential reread.

| Detail | Contents |
| --- | --- |
| [Processors](01-mcus.md) | Workloads, alternatives, exact comms package map |
| [Power](02-power.md) | Source path, enables, fault comparison, limits/hold-up |
| [Output status](03-energetic-outputs.md) | Explicitly incomplete implementation |
| [Servos](04-servos.md) | Two channels, retained ten-contact 430451000, actuator/control dependencies |
| [Service](05-service-status-time.md) | Indication, readback, reset/time |
| [GNSS/radio](06-gnss-radio.md) | Receiver limits, link directions, interoperability profile |
| [Sensors/recording](07-sensors-logging.md) | Interfaces, rates, storage and comms-record trade |
| [Churro/CAN](08-foinse-can.md) | Source ownership, vehicle timing and peer boundary |
| [Connectors](09-connectors-arming.md) | Inventory and FC-enable versus physical-arm distinction |

The main unresolved implementation is physical output arming/output circuitry.
Desk budgets and component choices are not physical validation. Current CAD and
controlled contracts are preserved until implementation is authorized.

## Evidence

- [Reproducible proposal checks](../calculations/component-proposal-checks.py) — source-enable truth table, comms pin map and numerical budgets.
- [Current system / preserved implementation](../../current-system.md).
- [Detailed component research](implementation-reference/README.md).
- [Pin audit](../mcu-pin-capacity-audit-2026-09-11.md), [power / storage / CAN calculations](../power-recording-can-audit-2026-09-11.md).
- [18 September earlier investigation](2026-09-18-review-investigations.md) — superseded recommendations are marked at its top.
- Historical reviews: [10 September](2026-09-10-session-review.md), [13 September](2026-09-13-session-review.md), [extraction audit](2026-09-18-meeting-change-ledger.md).

Source for this change: 18 September, 19:26 architecture meeting and subsequent
technical reflection; 19 September instruction to prepare a concrete proposal.
Raw recordings and private correspondence are not reproduced here.
