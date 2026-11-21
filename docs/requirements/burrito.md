# Burrito requirements

**Frozen 21 November 2026 for capture (D-21Nov.9).** Each row is a requirement:
- the source that asks for it;
- the mechanism that meets it (part, circuit or firmware);
- how we'll verify it.

A change needs a decision row in [decisions.md](../../decisions.md). Values in [brackets] are frozen as open, each with its owner. Nothing here is verified yet: no hardware exists.

Sources:
- OG-01–OG-17 (Notion, "EuRoC 2027 Requirements", draft of 15 October);
- the [rules sweep](2026-11-21-rules-sweep.md) (EuRoC SRD 1.1; IREC 2027 DTEG and R&R REV P1);
- [decisions.md](../../decisions.md).

Status:

| Status | Meaning |
| --- | --- |
| **Met** | Met by the design as decided |
| **Open** | Owner named |

## Recovery and energetics

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| B-01 | Fires a drogue and a main charge, independent of the CATS Vega chain | OG-01; LV-0240; IREC 6.9 | Channels 1 and 2. Each has a high side (TPS1H100, ≈2.0 A limit) and a low side (CSD17318), fed by fuse F6101 → J6101 → external arm → J6601 | EX-07 on inert loads; ground test | Met. Igniter all-fire and no-fire values open (R6310 / R6410 DNP), Recovery |
| B-02 | No single fault fires a channel, or the wrong one | D-2Nov.1; OG-11 | High and low sides driven from different GPIO ports; 100 kΩ pull-downs; arm switch in series; firmware fires one channel at a time | Assertions 1–3, 9, 11, 12; EX-07 fault table | Met |
| B-03 | Energetics stay safe until armed on the rail, by a physical external switch per function | LV-0530 / 0540; IREC 6.14 / 6.15 | J6101 (recovery) and J6102 (staging), each fused; arm sense to PE13 / PE15 | Bench: arms open means no output | Met. Switch parts open, panel subproject |
| B-04 | Continuity checked before arming; a leaking high side is never fired | D-2Nov.14 | 3.9 kΩ continuity legs; ADC; firmware classifies | Bench, inert loads | Met |
| B-05 | All-fire is met at minimum battery through the real panel harness | D-21Nov.5 | The arm switch carries pyro energy (D-6.1); harness gauge sized for it | All-fire test through the real loop | Open: harness length, panel subproject |
| B-06 | Arm, continuity, latch and power state readable remotely once the pad is cleared | OG-08 | 1 Hz pad telemetry over LoRa (D-2Nov.10) | Pad demonstration | Met |
| B-07 | Arming state audible at the panel: at IREC, verifiable from more than 100 mm away, with a face shield, in 76 dBA plus 20 mph wind (a stethoscope is allowed) | D-19Nov.4; IREC 6.16 | Passive piezo driven from PD6 | Behind the skin, at 76 dBA, through a stethoscope | Open: sound level, Seán. A louder sounder is a capture choice |
| B-08 | The drogue fires at or near apogee, never on the transonic spike | OG-02; LV-0350 | Two barometers on separate buses, IMUs, Mach lockout. The lockout uses Burrito's own sensors only, not a payload's | Simulated-flight replays; HIL | Open: D-6.11 lockouts, Anav |
| B-09 | Main at or below 450 m AGL at EuRoC | OG-03; LV-0370; D-18Nov.5 | Per-flight setting; checked at readback | Readback test | Met |
| B-10 | Nothing deploys below 100 m above the pad datum | D-2Nov.13 | Firmware gate; inertial evidence if both barometers fail | HIL; a false launch detect fires nothing | Met |
| B-11 | Staging is inhibited after any reset until cleared on the ground. At IREC, channel 3 never ignites an air-start motor | D-7.2; IREC 5.13 | Reset latch and AND gate; fuse F6102; J6102 | Bench: latch after reset | Met |
| B-12 | The recovery ground test can be driven by simulated conditions | LV-0520; OG-14; IREC 6.13.4 | Ground-test mode: a RAM flag that any reset ends; vacuum chamber | Ground test; signed annex | Met |

## Flight logic and resilience

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| B-13 | Pad datum tracked on the pad and frozen at launch detect; a reset never creates one | D-2Nov.10 | Firmware; checkpoint every 10 s | Reset injection (EX-03); six-hour pad hold | Met |
| B-14 | Rides through a flight-MCU reset in flight: power held, recovery resumed, staging inhibited | D-6.3; D-2Nov.4; D-2Nov.18; D-19Nov.1 | Hold RC (330 Ω, 470 µF) through diodes; auto-retry eFuses; re-asserted within 50 ms; checkpoint written first at launch detect | EX-03; break the enable loop mid-flight on the bench | Met |
| B-15 | Completes the mission with the comms MCU held in reset | D-6.12 | Two MCUs behind a partial-power boundary; flight never waits on comms | HIL with comms in reset (EX-01, EX-10) | Met |
| B-16 | Only the flight MCU commands outputs | AGENTS.md | No path from comms, CAN, radio or USB to a fire net | Assertions 11, 12; EX-09 | Met |
| B-17 | Measures to ±30 g and ±2000 °/s without clipping | OG-04 | Two low-g IMUs (to ±16 g, gyros to ±4000 / ±2000 °/s) and a ±200 g high-g sensor | Datasheets; shaker or spin rig | Met |
| B-18 | The watchdog is fed only by real progress | Fault policy | Earned-heartbeat watchdog and supervisors | Reset tests | Met |
| B-19 | A shorted sensor doesn't pull down the flight rail | D-6.6; D-2Nov.3 | 47 Ω supply links (magnetometer 22 Ω) | Bench short | Met |
| B-20 | Sensor filtering, with testing | IREC 6.11.7 | Estimator in firmware | EX-05 replays | Open: Anav |

## The active board, and the other CAN peer

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| B-21 | Two CAN buses, two nodes each, terminated at both ends; stale means safe | D-5Nov.3; D-2Nov.9 | Two transceivers behind partial-power boundaries; fixed 120 Ω; one standby line | EX-09; CAN boundary tests | Met |
| B-22 | Salsa acts only on a fresh Active, sent in the phases the phase table allows and only after the field-adjustable dormancy | D-5Nov.2; LV-0680 / F1 | Bus-2 message Safe / Active / Abort at 10–20 Hz with a counter | HIL; readback | Open: the phase table, controls team and Seán |

## Records, links and readout

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| B-23 | Full-rate recording from launch detect to LANDED plus a tail; a recording failure never takes control | D-6.9; EX-06 | 256 MiB NOR; RAM pre-trigger; append-only commits | EX-06 | Met |
| B-24 | Flight data read out after landing without site power | OG-15; IREC R&R-3.6.5 | USB-C on the comms MCU; USB powers logic only | Readout from a laptop on battery | Met |
| B-25 | Telemetry holds to [12] km slant range | OG-12 | LoRa module (868 / 915 MHz) on SMA; antenna behind an RF window or outside | Range test | Open: antenna and RF window, Jay and Arnav |
| B-26 | Position for recovery; at IREC, an SRAD GPS test report | OG-12; IREC 4.4, R&R-4.4.10.8 | GNSS receiver, passive antenna on SMA | GNSS test; report | Open: report, Arnav |
| B-27 | At IREC the radio is silent until authorised, changes channel quickly, and stays outside COTS tracker bands | IREC 4.3.4–4.4 | Firmware, proposed: transmit off by default; on once the recovery arm closes on the pad, or by a flag set over USB; channel set over USB | Bench; pad procedure | Open: Anav and Seán |

## Power, environment and fit

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| B-28 | At least 6 h on the rail plus the flight on the AV pack alone (OG-06 adds a 50% margin); pad mode ≤[150] mA | LV-0320; D-2Nov.6; OG-06 | 2S 21700 Li-ion; firmware pad mode | Measured pad current × 6 h against cold capacity; 6 h hold without the umbilical | Open: measurement on the first board |
| B-29 | No LiPo and no lithium primary cell anywhere on the board | LV-0300 | Flight VBAT held up by 100 µF (D-6.4); no GNSS backup cell | Inspection | Met |
| B-30 | Known operating temperature range, with board temperature logged | LV-0510; OG-13 | Parts rated −20 to +70 °C powered (provisional). Firmware logs the flight MCU die, one IMU and one barometer temperature at 1 Hz on the pad (in pad telemetry) and 10 Hz in flight; pad telemetry warns above [60] °C | Thermal chamber, then six hours closed in sun on a rail; signed annex | Open: the tests |
| B-31 | USB powers service logic only, ≤387 mA; never output energy, never charging | D-6.5; assertion 18 | USB current limit; battery/USB mux | USB-only boot | Met |
| B-32 | Flashed only at the av-bay, never on the rail | D-19Nov.9; D-21Nov.4 | USB-C on the comms MCU at the av-bay | Procedure | Met |
| B-33 | Survives 50 g quasi-static and a 200 g shock target; parts over 7 g staked; nothing hangs off the Samtec mate | Mission envelope; IREC App B3.6 | Mounting, staking, separate supports behind the mate | Vibration, shock, thermal cycling and vacuum (G2) | Open: qualification plan, the test-campaign owner |
| B-34 | Keyed, locking connectors; the arm plugs can't cross-mate; everything passes the tug test | AGENTS.md; LV-0490; IREC 6.12 / B3.3; assertion 13 | Gecko (CAN, enables); Micro-Fit (outputs, arms, PROP); Nano-Fit (2S) | Tug test; mate checks | Open: J6101 / J6102 parts |
| B-35 | 80 mm wide, 80 × 230 mm | D-21Nov.6; OG-17 | Outline | Fit check in Ériú Rev 2 and the EuRoC bay (EX-08) | Met for the outline; bay lengths open, Jay |
| B-36 | The interface to Churro is the eight Samtec contacts and I²C4; no further Burrito–Churro signal is added. Churro's new status rides on I²C4, and Churro keeps the [interface rules](churro.md#interface-rules-what-keeps-burritos-order-valid) | D-21Nov.9 | Samtec pair: 1 battery, 2 GND, 3 AUX 3.3 V, 4 GND, 5 SCL, 6 SDA, 7 fault, 8 `CROI_POWER_HOLD` | Netlist parity; mate check | Met |
| B-37 | Proof of function before IREC: ground and flight test, or a COTS computer can take Burrito's place when ESRA asks | IREC 6.11.6; D-21Nov.8 | Test campaign, then a named proof flight; Ériú keeps a second CATS Vega mount as the swap-in | Proof flight; ESRA review | Open: vehicle and date, Seán |
| B-38 | Assembled by JLC from its parts library | D-21Nov.9 | BOM check before order, with substitutes for what isn't stocked | BOM availability check | Open: capture |

## Proposed, not yet frozen

Added 21 November, before the order sign-off. A row joins the frozen list only through a decision row.

| ID | Requirement | Source | Mechanism | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| B-39 | Actuator return current stays off Burrito: a broken actuator return can't push current through Burrito's CAN reference, and in normal running a servo move's return current stays on its own wire | Boundary contract: "An open propulsion return must not push actuator current through the CAN reference." D-21Nov.1 puts Fajita and Salsa on Churro's common ground, so each CAN reference parallels an actuator return | A series part in the reference contact of each CAN connector (J501 and bus 2's): footprints for a resistor or a resettable fuse, value set on the bench inside the TCAN3413's common-mode range. Today the reference is bonded straight to GND | Bench: reference current during a servo stall; open the actuator return under load | **Proposed: Seán's OK** |
