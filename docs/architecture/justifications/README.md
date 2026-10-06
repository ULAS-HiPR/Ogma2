# Why these choices

22 September 2026. Current recommendations; acceptance and physical verification
remain distinct. Start with the relevant block, then follow its reason here.

| Choice | Justification |
| --- | --- |
| Flight/comms H563 100/64-pin pair | [Processor chapter and alternatives](../01-mcus.md#why-these-two), [complete pin-capacity study](../../archive/mcu-pin-capacity-audit-2026-09-11.md) |
| Three LDO domains, restartable services, voltage/current/energy allocation | [Power domains](power-domains.md) |
| Churro source envelope, fuses, exact probes and protected ADC inputs | [Churro monitoring](churro-monitoring.md) |
| Aligned NOR commits, preparation, capacity, truthful USB service | [Recording and service](recording-and-service.md) |
| Bounded PWM/CAN, source variants, connector drawing, RF test assembly and placement | [Interfaces and installation](interfaces-and-installation.md) |
| Retained sensors, receiver, radio and component alternatives | [Preserved component research](../../archive/architecture/implementation-reference/README.md); current chapters identify superseded recommendations |

The [capture specification](../schematic-capture-spec.md) turns these choices into
an implementation delta against the inspected CAD. The [connected overview](../../archive/architecture/00-overview.md)
is the review surface. Dated audits remain evidence of what was found, not an
instruction to restore a superseded proposal.
