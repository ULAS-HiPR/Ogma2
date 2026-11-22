# Churro requirements

**Frozen 22 November 2026,** at the accepted power review (D-22Nov.4–7; [review](../briefs/churro-power-review.md)). Changes now go through decisions.md. Values still in [brackets] are open.

Sources: [decisions.md](../../decisions.md) (D2, D-2Nov.7, D-20Nov.1, D-21Nov.1–D-21Nov.3, D-21Nov.10); the [rules sweep](2026-11-21-rules-sweep.md); OG-09.

## Interface rules: what keeps Burrito's order valid

Burrito's side is frozen ([B-36](burrito.md)). Every Churro change keeps to these rules, so no Churro change reaches back into Burrito.

| Rule | Why |
| --- | --- |
| IR-1. Everything new on Churro is read over I²C4, behind Churro's own buffer, at addresses that don't clash. Taken: 0x40 (Burrito's monitor), 0x41, 0x48; added 0x44, 0x49 and 0x20 (D-22Nov.4, D-22Nov.5) | I²C takes any number of devices: Burrito's firmware changes, its hardware doesn't |
| IR-2. New faults wire-OR onto the open-drain fault line (Samtec pin 7); the detail is read over I²C | One line says "something faulted", however much Churro grows |
| IR-3. No new Burrito–Churro signal. The Samtec stays eight contacts with today's pinout and meanings, and Churro's J301 mates Burrito's J102 where it sits now | The one change that would make Burrito's order wrong |
| IR-4. AV at Burrito stays as today: ≤8.4 V nominal from pack, umbilical or charger, with tolerance under Churro's 8.99 V and Burrito's TPS2121 trips; a current limit no lower than today's ≈6 A; auto-retry; a shutdown input that keeps the pin-8 hold's timing (D-2Nov.18) | Burrito's over-voltage trips, all-fire margin (B-05) and reset ride-through (B-14) stay valid |
| IR-5. Churro's monitors stay within AUX's 109–152 mA limit; chargers and actuator branches never run from AUX | AUX is a monitoring supply from Burrito's limiter |
| IR-6. Actuator return current never routes through Burrito: actuator returns go to the actuator pack through Churro's ground | Burrito's CAN references and ground plane aren't sized for it; Burrito limits each reference (B-39) |
| IR-7. Burrito only reads Churro. Any I²C-set output ever added powers up in its safe state and holds it through a Burrito reset | A Burrito reset never switches power on Churro |

## Branches and protection

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| C-01 | Three protected branches. AV (2S) feeds logic and pyro; PROP (6S actuator pack) feeds Fajita; ACT (same pack) feeds Salsa. Each has its own current limit, enable and current measurement | D2; D-21Nov.1 | AV and PROP eFuses as drawn; ACT is new; ratings set at the review | EX-02 branch faults | Decided D-22Nov.4: ACT is an LM5069-2 stage with INA237 0x44 |
| C-02 | PROP and ACT each carry their peak and continuous current at 6S without tripping. Model estimate (21 Nov, 2/5): PROP ≈14 A for tens of ms when three valve servos and the e-reg start together (≈9 A if Fajita staggers starts), ≈2 A averaged over a sequence; ACT ≈15 A (≈10 A staggered), ≈2 A averaged. Both together ≈29 A from the 6S pack | D-21Nov.1; [estimate](../calculations/actuator-branch-estimate.py) | A controller with an external FET on PROP and ACT, since the TPS2663 eFuse limits at 6 A at most. Connectors and copper sized by the averaged figure. A 6S pack of high-drain cells. Fajita and Salsa stagger servo starts, and limit and time out each servo, so a jam trips that servo, not the branch | The worst simultaneous move on the bench, from the pack at its lowest Go voltage: no trip, no under-voltage stop | Limit decided D-22Nov.4 (19.4 A minimum). Open: the servo parts and their stall current; Fajita's and Salsa's start rules; a current probe on a real valve at pressure |
| C-03 | Salsa's arm key is a physical switch in series in ACT | D-21Nov.1; LV-0700; IREC 6.14 | Key on the panel, wired into ACT | Bench: key open means no ACT output | Decided D-22Nov.4: the key in series ahead of ACT's LM5069 |
| C-04 | A short on any branch trips only that branch | D2; D-21Nov.1 | Per-branch protection | EX-02 | Decided D-22Nov.4 |
| C-05 | PROP stays powered through an abort, so Fajita can vent | Concern 4 (21 Nov) | Burrito has no path to switch PROP off | Fault analysis | Open: vent behaviour, James |
| C-06 | Burrito can hold AV on through a reset | D-6.3 | `CROI_POWER_HOLD` → diode → AV shutdown pin; auto-retry eFuse | EX-03 | Met |
| C-07 | Separate external enables for AV and PROP | D-19Nov.5 | Gecko enable loops, each biased from its own pack | Bench | Met |

## The umbilical

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| C-08 | The umbilical carries every load on the rail. Pulled at Go, each feed hands to its pack with no dropout and no Burrito reset | OG-09; D-2Nov.7 | Per-source ideal diodes ahead of the eFuses | EX-02, pulled under load | Met. J801 decided D-22Nov.6 |
| C-09 | Repeated hot-plugging can't overvolt anything | D-21Nov.3 | Fuse and TVS per pair; damping per pair; charger input rated at least twice the bus | 50 plug/pull cycles at full voltage with the real cable | Decided D-22Nov.6 |
| C-10 | J801 carries the AV and actuator power pairs and the charge contacts; it is keyed and can't take the 6S plug; it pulls away at Go | D-21Nov.2; panel brief | Part chosen with the vehicle owner | Mate and pull tests | Decided D-22Nov.6; Jay confirms the harness |

## Charging

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| C-11 | Charges every pack on the rail: AV 2S, the actuator 6S and the CATS Vega's 1S cell, through its own lead without modifying the unit | D-20Nov.1; D-21Nov.2; LV-0310; App C | One standalone CC/CV charger per pack voltage, fed from the umbilical's charge contacts, at maintenance rate (≤0.2 C) | Bench charge of each pack through the real umbilical | Decided D-22Nov.5. Open: EuRoC officials on the CATS cell |
| C-12 | No charging above [45] °C at a pack; resumes below [40] °C | D-21Nov.2; LV-0510 | Existing NTC probes gate each charger | Bench with a heated probe | Decided D-22Nov.5: 45 / 40 °C comparator gate |
| C-13 | Charging stops when the umbilical leaves (Go) | D-20Nov.1 | No charge source once pulled | Bench | Met by topology |
| C-14 | No charger fault can make a firing path | D-21Nov.2 | Firing needs the flight MCU to close both switches of a channel with the arm closed; eFuse overvoltage trips | Fault analysis; bench injection | Open |
| C-15 | Burrito reads charge status over I²C4 and controls nothing in the charge path | D-21Nov.2; B-36 | Each charger's status pins (charging, done, fault) and its temperature hold into an I²C expander on Churro. The voltage trend alone can't tell done from stopped, or why it stopped; firmware keeps it as a cross-check | Bench: force each state, read it over I²C4 | Decided D-22Nov.5: TCA9535 at 0x20 |
| C-16 | Payload packs never charge from our bus | D-21Nov.2; LV-0880 | Not connected | Inspection | Met |
| C-23 | No Churro fault can drain or short the CATS Vega's cell, and the cell's voltage is read | LV-0240, LV-0250 (the COTS chain stays independent); D-21Nov.2 | A fuse at the cell end of its charge lead; reverse blocking in the charger path; a high-value divider behind a series resistor into a second ADS1115 (0x49) | Bench: short the 1S charger output and the divider; the cell holds | Decided D-22Nov.6. Open: the officials' answer on charging the cell (C-11) |

## Monitoring, construction and fit

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| C-17 | Monitors branch current and voltage and both pack temperatures, and shows which source is live | D2; D-2Nov.7 | Current monitors, ADC, NTC probes with a reference bias; AV pack readout on the pack side | Bench readings; probe-lead faults; switchover | Met for AV; ACT decided D-22Nov.4; PROP's pack side (C-22) |
| C-22 | The actuator pack's voltage shows on its pack side while the umbilical carries the load | Seán, 21 Nov (every pack monitored); D-2Nov.7 | PROP's divider (R6111) moves to the pack side of its diode, like AV's | Bench: umbilical connected, pack removed | Open |
| C-18 | No MCU on Churro | Capture spec | MCU-less design | Inspection | Met |
| C-19 | No charger or propulsion current passes through Burrito | Boundary contract | Topology | Assertion | Met |
| C-20 | 80 mm wide; length as needed; held independently of the Samtec mate | D-21Nov.6; D-21Nov.22; layout guide | Outline, 80 × 120 mm working (D-21Nov.22); separate supports | Mockup | Decided D-22Nov.7: 80 × 120 mm until S6; 140 mm if needed |
| C-21 | No LiPo and no lithium primary cell in any pack | LV-0300 | 2S and 6S metal-can cylindrical Li-ion | Inspection | Met |
