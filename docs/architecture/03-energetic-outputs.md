# Recovery and staging — unresolved output block

**22 September · preserved authority boundary; no new output circuit selected.**

The latest meeting correctly identified that the documents had not delivered a
resolved implementation here. A clearer drawing does not close that gap.

| Boundary retained | Reason |
| --- | --- |
| Flight processor owns event authority | Radio, USB and vehicle peers cannot directly command these outputs |
| Physical energy isolation separate from computer power | Powered logic and software readiness do not establish an armed/disarmed energy path |
| Reset inhibits further sustainer ignition | Unknown history cannot become permission to repeat an event |
| Recovery follows its validated phase-specific policy | Recovery and staging have different consequences |
| Independent vehicle recovery where required | Shared PCB/power/flight MCU are common failure points |

## Disposition of the challenged complexity

| Existing mechanism | Review disposition |
| --- | --- |
| Independent pulse termination | Retain pending the output-specific assessment; nominal load burnout does not settle stuck-request consequences |
| Separate switching conditions | Preserve while their failure cases are reviewed; component count alone is no reliability argument |
| Continuity and current evidence | Keep distinct from physical operation; scope and diagnostic limits remain unresolved |
| Shared servo/energetic enable | Operator-level suggestion, not a selected physical assembly |
| Extra retry machinery | Do not add without a defined operational requirement |

Existing DNP links remain. No newly selected load, pulse setting, diagnostic
energy or physical arm assembly is implied. This block needs its responsible
engineering review; the processor, sensing and service proposal can still be
assessed without pretending it is complete.

[Existing circuit record](implementation-reference/03-energetic-outputs.md) ·
[Flight fault contract](../../interfaces/flight-fault-contract.md) ·
[Reset contract](../../interfaces/reset-recovery-contract.md)

See [connectors and physical arming](09-connectors-arming.md) for the FC battery-enable plug, separate unresolved output-arm assembly and complete connector inventory.

## What exists and what is missing

**There is an existing three-channel draft, not an absent feature. It is not a
finished operational output subsystem.** The preserved design includes command,
termination, sensing and interface provisions, plus deliberate unpopulated
safeguards. The architecture proposal has not closed their suitability as one
installed assembly. Connectivity checks do not establish functional safety.

| Required review result | Present evidence / missing closure |
| --- | --- |
| Approved output requirements | Recovery and staging roles distinguished; load-specific requirements are not closed |
| Complete physical isolation/arming assembly | Computer enable defined; output arm assembly and independent state evidence unresolved |
| Fault and reset behavior for the assembled system | Existing contracts state intent; implementation evidence and responsible review incomplete |
| Diagnostic meaning | Electrical observations do not prove physical actuation; diagnostic validity remains a separate requirement |
| Verification and release | DNP safeguards retained; no qualification or operational release |

This is a **design blocker**, not merely a request to test an otherwise selected
circuit. A qualified responsible engineer must close the output requirements,
assembly and safety case. This audit supplies no firing-circuit design, new
component/value selection or arming wiring. The incomplete subsystem cannot be
counted as accepted because the rest of the review pack is ready.
