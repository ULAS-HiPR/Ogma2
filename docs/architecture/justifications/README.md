# Why these choices

Each block in the [capture specification](../schematic-capture-spec.md) points
here for its reasons, alternatives, sources and sums. Written 22 September 2026
and kept current with [decisions.md](../../../decisions.md). A recommendation
here is not acceptance, and neither is physical verification.

| Choice | Where the reasons are |
| --- | --- |
| Two processors, H563 100-pin flight and 64-pin comms | [Processor chapter](../01-mcus.md#why-two-and-why-these) (D-6.12); [pin-capacity study](../../archive/mcu-pin-capacity-audit-2026-09-11.md) |
| Three regulated domains, restartable services, current and energy budget | [Power domains](power-domains.md) |
| Churro source envelope, fuses, temperature probes, protected ADC inputs | [Churro monitoring](churro-monitoring.md) |
| Sector-aligned NOR commits, preparation, capacity, honest USB service | [Recording and service](recording-and-service.md) |
| PWM and CAN limits, source variants, connector drawings, RF test assembly, placement | [Interfaces and installation](interfaces-and-installation.md) |
| Sensors, receiver, radio and component alternatives | [Preserved component research](../../archive/architecture/implementation-reference/README.md); the current chapters say which recommendations it superseded |

The [system tour](../system-tour.md) is the overview. Dated audits in the
archive record what was found at the time. They are not instructions to bring
back a superseded proposal.
