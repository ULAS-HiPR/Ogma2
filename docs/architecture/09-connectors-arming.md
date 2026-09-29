# Connectors and physical arming

**22 September · installed connector inventory; unresolved arm assembly explicit.**

Two distinct operator functions: **enable computer battery power**, then
**separately establish the physical output-arm state**. Neither a powered FC nor
software readiness proves output energy is isolated or armed.

## Justification and deeper detail

| Question | Follow through | Source status |
| --- | --- | --- |
| Which assembly decisions are now proposed? | [Source variants, mates, exact Nano-Fit drawing and retained leads](justifications/interfaces-and-installation.md#source-variants-and-harness-construction) | Current capture/placement baseline; physical output-arm block excluded |
| Where is FC enable defined? | [Source-enable contract](../../interfaces/power-contract.md#8-september-source-enable-implementation) | Installed connector/contact behavior |
| Why these connector families? | [Connector and service revision](../connector-servo-readiness-revision-2026-09-07.md#connectors) | Preserved parts/harness rationale; output-arm assembly remains incomplete |

## Computer enable — defined in the preserved CAD

| Item | Existing definition |
| --- | --- |
| Croí J103 | JST GH BM02B-GHS-TBT(LF)(SN), GHR-02V-S housing; wire-matched crimp |
| Contact 1 / 2 | BAT_SWITCH_3V / BAT_SHDN_N |
| Maintained contact closed | Enables the battery entry electronically |
| Contact open / plug absent | Battery entry commanded off; upstream circuitry remains live |
| USB connected | Logic can remain powered with J103 open |
| Churro/Foinse-fed installation | Retained closed enable plug at Croí J103; source switching at the distribution board |

Call this **FC battery enable**, not “flight armed.” It carries control current,
not the board supply current. The existing [power contract](../../interfaces/power-contract.md#8-september-source-enable-implementation)
owns this definition and the separate distribution-board source enables.

## Physical output arm — required, assembly unresolved

| Review item | Current status |
| --- | --- |
| Removable shorting plug / maintained arm connection | Requested operator function; exact assembly, connector and contact assignment are not selected |
| Physical isolation | Separate from J103 and software permission; no completed assembly in the present CAD |
| Recovery versus staging | Existing separate arm-sense inputs describe evidence; they do not establish the physical assembly or imply one shared plug |
| Servo sharing | Shared servo/energetic enable was discussed, not accepted |
| Indication | FC power lamp and software “ready” cannot substitute for independently established physical arm state |
| Unplugged state | Must be established for the complete installed assembly; an absent sense voltage alone is insufficient evidence |

The energetic output harness **J6601 is not an arming connector**. No jumper
across its output contacts is specified here. Existing DNP energy links are not
operator arm plugs and remain unchanged.

The review must settle the physical assembly, whether recovery/staging share an
operator control, how its state is independently established, and its accessible
mounting, retention and labelling. Until then, no selected short-to-arm pinout or
completed physical isolation claim belongs in this pack.

## Operator boundaries

```mermaid
flowchart TB
  A["FC battery-enable contact · J103\nDefined in preserved CAD"] --> B["Electronic battery-source enable\nNot physical battery isolation"]
  U["USB service power"] --> C["Computer powered"]
  B --> C
  C --> D["Software readiness\nSeparate evidence"]
  E["Physical output-arm assembly\nConnector / arrangement unresolved"] --> F["Physical arm-state evidence\nSeparate from power and readiness"]
```

This is a boundary diagram, not an energetic wiring diagram. The unresolved
assembly remains visible beside the defined computer-enable connection.

## Connector inventory — review together

| Connector | Preserved part / function | Review status |
| --- | --- | --- |
| J101 | 1053111102 · standalone battery | Alternative to J102; source exclusion required |
| J102 | Samtec MPT-08-01-01-L-RA-SD · distribution-board connection | Power + monitoring; [power/CAN page](08-foinse-can.md) |
| J103 | Two-contact JST GH · FC battery enable | Defined above; retained external contact |
| Physical output arm | No selected connector | Open assembly decision; not J6601 |
| J6601 | Molex 430450600 · output harness | Preserved; service-end assembly unresolved |
| J6602 | Molex 430451000 · three-servo harness | [Proposal](04-servos.md): retain ten-contact connector, use two servo groups |
| J501 | Three-contact JST GH · CAN H/L/reference | [Vehicle link](08-foinse-can.md); no power contact |
| J4401 | USB4105-GF-A · USB-C service | Logic service, not output arming |
| J4501 / J4601 | Amphenol 132134 · GNSS / radio SMA | Distinct labels and retained antenna leads |
| J2301 / J4201 | TC2030-NL-FP · flight / comms debug | Development access; not arm connections |

**Mating review:** retain the ten-contact servo connector; withdraw the
six-contact substitution that would match J6601. Distinguish the two SMA ports
and externally accessible enable plugs in the installation drawing.

For every external harness, release the mating part, cavity-numbered drawing,
wire/contact selection, retention, strain relief and accessible mounting together.
The table is an inventory, not a released harness drawing.

Evidence: [native netlist](../../hardware/croi2/output/full-netlist.xml),
[power contract](../../interfaces/power-contract.md),
[connector revision](../connector-servo-readiness-revision-2026-09-07.md),
[meeting extraction](2026-09-18-meeting-change-ledger.md),
[output boundary](03-energetic-outputs.md).

## Schematic handoff

**Burrito's board-side inventory is defined; the complete vehicle harness is not.**
Churro also requires J101 (2S), J201 (6S), J103/J104 (source enables), J301
(board pair), J601 (temperature probes) and J701 (protected propulsion output).
The [Churro chapter](08-foinse-can.md#churro-circuit-inventory) now inventories
these together with their actual source roles.

Two sources cannot be made mutually exclusive by a note beside two populated
connectors. Recommend an assembly variant: standalone J101 or Churro-fed J102,
with the unused source connection physically unavailable. Preserve power-pin
assignments. The exact [Nano-Fit drawing is located](justifications/interfaces-and-installation.md#source-variants-and-harness-construction);
create and independently check that footprint during capture. A rectangular
reservation is not a land pattern. Codex owns this library/placement work after
the green light; Seán owns routing.

SMA GNSS/radio and the repeated two-contact GH enable connectors remain
misconnection cases despite the ten-contact servo fix. Resolve them with
installation access, physical differentiation where necessary, retained leads
and cavity-numbered harness drawings. A label alone is not proof against every
credible cross-connection. Include ground-return faults and USB attached in the
installed assembly review. Physical output-arm wiring remains outside this
completed connector inventory.
