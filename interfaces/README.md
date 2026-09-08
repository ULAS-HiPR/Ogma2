# System interfaces and fault contracts

| Interface | Use |
| --- | --- |
| [Ogma, Foinse, and propulsion boundary](ogma-foinse-propulsion-boundary.md) | Vehicle authority, power ownership, production CAN boundary, and required fault tests |
| [Flight fault contract](flight-fault-contract.md) | Accepted EX-01 fault, watchdog, post-reset authority and independent-recovery policies; timing allocation and verification remain open |
| [Power contract](power-contract.md) | Accepted EX-02 defaults, source drawings, bounded branches, service/source states, regulator candidates and first inert-test definition; numerical and hardware closure open |
| [Reset, retained state and time](reset-recovery-contract.md) | Accepted EX-03 defaults and host-model scope; exact retention bank, clock, timing and mechanism response evidence remain open |

These documents are owned Ogma 2 interface truth, not permission to change an
adjacent system unilaterally. A real boundary change must be reconciled with the
other owning project and verified at both ends.
