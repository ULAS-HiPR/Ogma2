# Ogma 2 documents

Start with the [system tour](architecture/system-tour.md) and the
[decisions](../decisions.md).

| Document | Use |
| --- | --- |
| [Block chapters](architecture/README.md) | One page per block |
| [Capture specification](architecture/schematic-capture-spec.md) | Exact changes to the 8 September CAD |
| [Justifications](architecture/justifications/README.md) | Reasons, calculations and sources behind the 22 September proposal |
| [Firmware interface](firmware-interface.md) | Every pin by function, the hardware sequences and the budgets, for both firmware images |
| [Verification](architecture/11-verification.md) | Release gates, test campaigns, EuRoC tests, safety assertions for capture |
| [PCB layout guide](pcb-layout-guide.md) | Routing order and references |
| [Design review procedure](design-review-operating-procedure.md) | Recommendation-first review |
| [Verification template](templates/verification-record.md) | Test record |
| [Proposal checks](calculations/component-proposal-checks.py) | Pin-map and budget calculations |
| [Host checkpoint model](../tests/reset_replay/README.md) | Host tests; not target evidence |
| [Archive](archive/README.md) | Superseded reviews, studies and history |

Owned contracts: [power](../interfaces/power-contract.md),
[flight fault](../interfaces/flight-fault-contract.md),
[reset](../interfaces/reset-recovery-contract.md),
[vehicle boundary](../interfaces/ogma-foinse-propulsion-boundary.md).
