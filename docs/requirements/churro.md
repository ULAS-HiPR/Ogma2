# Churro requirements

**Draft, 21 November 2026. Not frozen.** These freeze at the Churro power review (D-21Nov.9). Until then, only the interface to Burrito ([B-36](burrito.md)) is fixed. Values in [brackets] are open.

Sources: [decisions.md](../../decisions.md) (D2, D-2Nov.7, D-20Nov.1, D-21Nov.1–D-21Nov.3); the [rules sweep](2026-11-21-rules-sweep.md); OG-09.

## Branches and protection

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| C-01 | Three protected branches. AV (2S) feeds logic and pyro; PROP (6S actuator pack) feeds Fajita; ACT (same pack) feeds Salsa. Each has its own current limit, enable and current measurement | D2; D-21Nov.1 | AV and PROP eFuses as drawn; ACT is new; ratings set at the review | EX-02 branch faults | Open: ACT drawn at the review |
| C-02 | PROP and ACT each carry [peak] A and [continuous] A at 6S | D-21Nov.1 | eFuse or hot-swap controller and FET sized to the rating; connectors and copper to match | Worst simultaneous move on the bench | **Open: Seán's call, then Jay's actuator specs** |
| C-03 | Salsa's arm key is a physical switch in series in ACT | D-21Nov.1; LV-0700; IREC 6.14 | Key on the panel, wired into ACT | Bench: key open means no ACT output | Open |
| C-04 | A short on any branch trips only that branch | D2; D-21Nov.1 | Per-branch protection | EX-02 | Open for ACT |
| C-05 | PROP stays powered through an abort, so Fajita can vent | Concern 4 (21 Nov) | Burrito has no path to switch PROP off | Fault analysis | Open: vent behaviour, James |
| C-06 | Burrito can hold AV on through a reset | D-6.3 | `CROI_POWER_HOLD` → diode → AV shutdown pin; auto-retry eFuse | EX-03 | Met |
| C-07 | Separate external enables for AV and PROP | D-19Nov.5 | Gecko enable loops, each biased from its own pack | Bench | Met |

## The umbilical

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| C-08 | The umbilical carries every load on the rail. Pulled at Go, each feed hands to its pack with no dropout and no Burrito reset | OG-09; D-2Nov.7 | Per-source ideal diodes ahead of the eFuses | EX-02, pulled under load | Met. J801 part open |
| C-09 | Repeated hot-plugging can't overvolt anything | D-21Nov.3 | Fuse and TVS per pair; damping per pair; charger input rated at least twice the bus | 50 plug/pull cycles at full voltage with the real cable | Open: damping drawn at the review |
| C-10 | J801 carries the AV and actuator power pairs and the charge contacts; it is keyed and can't take the 6S plug; it pulls away at Go | D-21Nov.2; panel brief | Part chosen with the vehicle owner | Mate and pull tests | Open |

## Charging

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| C-11 | Charges every pack on the rail: AV 2S, the actuator 6S and the CATS Vega's 1S cell, through its own lead without modifying the unit | D-20Nov.1; D-21Nov.2; LV-0310; App C | One standalone CC/CV charger per pack voltage, fed from the umbilical's charge contacts, at maintenance rate (≤0.2 C) | Bench charge of each pack through the real umbilical | Open: chargers drawn at the review; EuRoC officials on the CATS cell |
| C-12 | No charging above [45] °C at a pack; resumes below [40] °C | D-21Nov.2; LV-0510 | Existing NTC probes gate each charger | Bench with a heated probe | Open |
| C-13 | Charging stops when the umbilical leaves (Go) | D-20Nov.1 | No charge source once pulled | Bench | Met by topology |
| C-14 | No charger fault can make a firing path | D-21Nov.2 | Firing needs the flight MCU to close both switches of a channel with the arm closed; eFuse overvoltage trips | Fault analysis; bench injection | Open |
| C-15 | Burrito reads charge status over I²C4 and controls nothing in the charge path | D-21Nov.2; B-36 | Status into Churro's I²C devices | Bench | Open |
| C-16 | Payload packs never charge from our bus | D-21Nov.2; LV-0880 | Not connected | Inspection | Met |

## Monitoring, construction and fit

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| C-17 | Monitors branch current and voltage and both pack temperatures, and shows which source is live | D2; D-2Nov.7 | Current monitors, ADC, NTC probes with a reference bias; AV pack readout on the pack side | Bench readings; probe-lead faults; switchover | Met for AV and PROP; ACT at the review |
| C-18 | No MCU on Churro | Capture spec | MCU-less design | Inspection | Met |
| C-19 | No charger or propulsion current passes through Burrito | Boundary contract | Topology | Assertion | Met |
| C-20 | 80 mm wide; length as needed; held independently of the Samtec mate | D-21Nov.6; layout guide | Outline; separate supports | Mockup | Open |
| C-21 | No LiPo and no lithium primary cell in any pack | LV-0300 | 2S and 6S metal-can cylindrical Li-ion | Inspection | Met |
