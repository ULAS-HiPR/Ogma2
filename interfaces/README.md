# Interfaces and fault contracts

| Contract | Covers | Accepted | Still open |
| --- | --- | --- | --- |
| [Ogma / Foinse / propulsion boundary](ogma-foinse-propulsion-boundary.md) | Who owns what, power ownership, the production CAN link, boundary tests | Controlling; LTS copy points here | Message contract; bonding evidence |
| [Flight fault contract](flight-fault-contract.md) | EX-01: fault responses, watchdog, authority after reset, independent recovery | Policy | Timing allocation, verification |
| [Power contract](power-contract.md) | EX-02: power chain, source enables, branches, source states, first inert test | Policy and defaults | Numbers and hardware closure |
| [Reset, retained state and time](reset-recovery-contract.md) | EX-03: reset classes, checkpoints, clock, host model | Defaults | Retention bank, clock, timing and mechanism evidence |

These are Ogma 2's own interface definitions. They don't give permission to
change a neighbouring system on our own. A real boundary change has to be agreed
with the other owning project and verified at both ends.
