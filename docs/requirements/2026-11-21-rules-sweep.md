# EuRoC and IREC rules sweep: Burrito, Churro, Salsa, access panel

**21 November 2026. Evidence for the frozen requirements ([Burrito](burrito.md), [Churro](churro.md)); it decides nothing on its own.** The "found on the way" list at the end was fixed in 7e5c57d.

Sources:
- EuRoC System Requirements Document, Issue 1.1 (30 April 2026). This is EuRoC 2026's issue; no 2027 issue is out yet.
- IREC 2027 Design, Test & Evaluation Guide (DTEG), REV P1, effective 15 October 2026.
- IREC 2027 Rules & Requirements (R&R), REV P1, effective 15 October 2026.

Rules are paraphrased, not quoted. Status is judged against the design decided on main (870430c):

| Status | Meaning |
| --- | --- |
| **Pass** | Met by the design as decided; not yet verified. |
| **Open** | Depends on something undecided. |
| **Flag** | A rule that changes hardware or plans, like the battery rule did. |
| **N/A** | Doesn't touch these boards. |

## Flags

1. **IREC DTEG 6.11.6: Burrito has to prove itself before IREC.** Before the competition we need proof of function from ground *and* flight testing. If a flight test isn't feasible, the av-bay must let a COTS flight computer take Burrito's place when ESRA's safety reviewer asks. D-20Nov.3 makes IREC the core's flight test, so either Burrito flies earlier or the bay has to be designed for substitution.
2. **IREC 6.16: arming has to be audible at a distance.** It must be verifiable without anyone's head within 100 mm of the rocket, in at least 76 dBA of background noise plus a 32 km/h wind, wearing a face shield. A stethoscope is allowed. Burrito's sounder is a CPT-9019S passive piezo, and its level through the skin is unverified. The part is fixed at capture.
3. **IREC 7.3.1 and EuRoC LV-0670: control surfaces must go neutral when primary power is lost.** D-2Nov.8 covers stop, abort and stale authorisation, but not loss of power. Nothing in Salsa's rules says what an unpowered servo or canard does.
4. **EuRoC LV-0500: PTFE insulation through the tanks.** N₂O boils at about −88 °C, so safety-critical wiring next to the tank needs cryo-rated (PTFE) insulation. Jay now wants no raceways, with the wiring running straight through the tanks in a downcomer. That catches:
   - the umbilical and charging run;
   - CAN bus 1 and the PROP feed to Fajita, if Fajita sits below the tanks;
   - the USB-C leads.
5. **EuRoC Appendix C: one charging bus to every pack.** The bus runs the length of the vehicle, with mating connectors at every joint and a diode per branch. Appendix C says the benefit is lost if even one battery is left off. Our packs differ in voltage: AV 2S, PROP 6S, Salsa's pack, the CATS cell and any payload pack. LV-0430 also bans modifying the CATS Vega.
6. **IREC DTEG 4.2.1 and 4.2.3: a Primary COTS GPS tracker in every independently recovered section.** It must be switched and powered on its own, unless the flight computer has GPS built in. It is open whether ESRA accepts the CATS Vega for this and whether its 2.4 GHz link reaches from 30,000 ft. If it doesn't, the av-bay gains another device and the access panel another switch.
7. **IREC DTEG 4.3.4–4.4: Burrito's radio rules at IREC.** The radio has to be silent in the pit until ESRA authorises it, off when not in use, and able to change frequency quickly. As SRAD it must stay outside the bands COTS trackers use, under the Student Band Plan; 902–928 MHz is shared with common COTS trackers. No firmware or antenna plan exists for this yet.
8. **EuRoC LV-0880 and IREC R&R-3.4.2: payloads must stay independent.** If the pitot tube feeds Burrito, or a payload draws power from Churro, it is a vehicle subsystem, not a payload.
9. **IREC DTEG 5.13: an SRAD computer may not ignite an air-start motor.** At IREC, Burrito's channel 3 can only do staging.
10. **EuRoC LV-0300 against IREC DTEG 6.17.2: lithium coin cells.** IREC allows lithium primary coin cells; EuRoC doesn't. Keep them off every board, including Salsa, Fajita, the e-reg and the payload. Burrito has none: flight VBAT is held up by 100 µF (D-6.4), and the GNSS has no backup cell.

## EuRoC SRD Issue 1.1

| Clause | Asks | Touches | Status | How, or the gap |
| --- | --- | --- | --- | --- |
| LV-0020, 0035 | Air-start electronics meet the recovery redundancy rules; air-start armed only by launch detection | Burrito ch 3 | N/A | EuRoC vehicle is single stage. Ch 3 arms by J6102 on the pad; revisit if ever used for air-start |
| LV-0030 | Ground-start igniter armed and disarmed with nobody within 15 m | Fajita, GSE | Open | Propulsion side ([boundary contract](../../interfaces/ogma-foinse-propulsion-boundary.md)) |
| LV-0100–0160 | Pressurisation, loading, venting | Fajita, GSE | N/A here | — |
| LV-0190 | Remote vent or offload after an abort | Fajita; Burrito may relay | Open | Path not chosen: Fajita's own link, or Burrito's radio relayed over bus 1 (firmware) |
| LV-0240 | Fully redundant recovery electronics, each with its own battery | Burrito, CATS Vega | Pass | D-18Nov.2: Burrito on the AV pack, the CATS Vega on its own cell, each with its own e-matches |
| LV-0250, App B1 | One chain COTS; no SRAD hardware between the COTS computer and its initiators | CATS Vega | Pass | The Vega's leads go straight to its e-matches (D-18Nov.2). Keep its cell's charging (C-04) off its firing path |
| LV-0260–0280 | Manual switches and connectors reachable from outside, from the ground, on the side opposite the rail | Panel | Open | Jay's stack (grid-fin module, then av-bay, then recovery, all above the tanks) puts the av-bay out of reach. Panel low, long runs |
| LV-0290, 0530 | Energetics safe until in launch position | Burrito | Pass | External arm switches J6101 / J6102; arm sense in pad telemetry |
| LV-0300 | No LiPo, no non-rechargeable lithium on board | All packs | Pass for Burrito and Churro; Open for the rest | 2S 21700 Li-ion (D-2Nov.6). Salsa's pack, the CATS cell and payload packs still to choose |
| LV-0310 | Batteries reachable from the ground | All packs | Open | Met by Appendix C option 1 (D-20Nov.1); the charger isn't designed |
| LV-0320 | At least 6 h on the rail | All packs | Pass on paper | AV pack alone covers 6 h plus flight (D-2Nov.6); pad current unmeasured; Salsa and CATS packs separate |
| LV-0340–0380 | Dual deployment: drogue near apogee at 23–46 m/s; main at or below 450 m AGL, under 9 m/s | Burrito firmware; Recovery | Pass | D-18Nov.5, D-2Nov.13; descent rates are Recovery's sizing |
| LV-0430–0470 | Unmodified CATS Vega in each stage, on EuRoC firmware, with call-sign and ground station; its switch accessible like ours | Av-bay, panel | Open | Its switch goes on the panel; its cell's charging mustn't modify the unit |
| LV-0480, 0490 | Safety-critical wiring managed with slack; connectors pass a tug test | Harness | Open | Positive-lock connectors by design; harness drawing not started |
| LV-0500 | Cryo-rated insulation near propellants boiling below −50 °C | Harness | **Flag** | N₂O; see flag 4 |
| LV-0510 | Thermal test, at least one representative temperature monitored, rain tolerance; signed annex | Burrito, Churro | Open | Churro logs the pack temperatures at 2 Hz; no board temperature is specified yet, though the IMUs, barometers and MCU all measure one. Test not run |
| LV-0520 | Recovery ground test with simulated conditions, sensor electronics included; signed annex | Burrito | Pass on paper | Ground-test mode (D-2Nov.10, D-2Nov.16) and a vacuum chamber |
| LV-0540, 0550 | Arming devices reachable like 0260–0280; on the airframe, not at the clock position of what they fire | Panel | Open | Panel position against the recovery hatches |
| LV-0650 | Active control only for pitch or roll augmentation, braking, guided recovery, precision landing or guided deployables | Salsa | Open | Roll control is allowed; any heading hold (Notion open question 4) needs a ruling |
| LV-0660 | Stable with the control system removed or locked | Vehicle | Open | Sim Systems |
| LV-0670 | Fail safe: surfaces neutral, thrusters off on any fault or abort | Salsa | **Flag** | See flag 3 |
| LV-0680, App F1 | Field-adjustable boost dormancy: at least 1500 m AGL with no history; roll-angle control inactive to 1500 m | Burrito, Salsa | Pass | Burrito sends Active only after dormancy (D-5Nov.2) |
| LV-0690 | Control electronics meet 0240 (redundant) and 0260–0280 and §5.4 | Salsa | Open | Officials' ruling (Jay); if it means redundant, a second board |
| LV-0700 | Control energetics (cold-gas RCS) meet §6.1 | Salsa | Open | Arm key in the actuator supply (D-18Nov.1); tank safing is mechanical |
| LV-0710 | Unpressurised bays vented, typically 3–5 mm holes | Av-bay | Open | Placement of the barometers' static vents (OG-02) |
| LV-0780–0820 | Internal antennas behind a 360°, non-carbon RF window at least two calibres long, antenna mid-window; radios inside | Burrito radio, GNSS | Open | RF window or external antennas (Jay) |
| LV-0840–0910 | Payloads independent of vehicle functions; payload energetics meet §6.1; deployables tracked | Payload | **Flag** | See flag 8 |
| SE-0010–0030 | Launch control: 750 m range, single-fault tolerant with an interlock, dead-man switches | Ground side | N/A here | Arnav |
| App C | Charging bus the full length, connectors at every joint, diode per branch, same nominal voltages where possible, linear step-down ahead of balancing, friction pull-release umbilical | Churro, umbilical | **Flag** | See flag 5 |
| App D2–D4 | CATS 2.4 GHz at 100 mW or less; call-sign format | CATS Vega | Pass | COTS; Burrito's LoRa is separate |
| App F2 | Recommended heading 133° to apogee | Salsa | Info | A recommendation, not a requirement |
| App H | Fire-control design | Ground side | N/A here | — |

## IREC 2027 (DTEG REV P1, R&R REV P1)

| Clause | Asks | Touches | Status | How, or the gap |
| --- | --- | --- | --- | --- |
| DTEG 4.2.1, 4.2.3 | Primary COTS GPS tracker per independently recovered section; switched and powered independently unless built into the flight computer | Av-bay, panel | **Flag** | See flag 6 |
| DTEG 4.3.4–4.3.7 | No transmitting in the pit without authorisation; transmitters off when not in use; change frequency quickly; Team ID in custom names | Burrito radio | **Flag** | See flag 7 |
| DTEG 4.4; R&R-4.4.10.8 | SRAD GPS optional, outside COTS ranges, per the Student Band Plan; test report required | Burrito GNSS and LoRa | Open | Band at Midland; report |
| DTEG 5.13 | SRAD computers shall not ignite air-start motors | Burrito ch 3 | N/A for IREC | See flag 9 |
| DTEG 6.9 | Completely independent redundant recovery: arming switches, computers, power, initiators; a dual-pole switch doesn't count | Burrito, CATS Vega | Pass | Separate switches, packs and e-matches |
| DTEG 6.10 | At least one chain COTS; a COTS computer is the official altimeter and fires one energetic; kits aren't COTS | CATS Vega | Open | Confirm ESRA treats the CATS Vega as COTS |
| DTEG 6.11.5, 6.11.6 | SRAD computers documented; proof of function by ground and flight test before the competition, or COTS substitution on request | Burrito, av-bay | **Flag** | See flag 1 |
| DTEG 6.11.7 | Sensor filtering, with testing | Burrito firmware | Open | EX-05 replays |
| DTEG 6.12, App B | Safety-critical wiring labelled or colour-coded with strain relief; locked connectors; no connector as a structure; boards on standoffs with daughterboards supported; parts over 7 g staked; no tape insulation | Boards, harness | Pass for connectors and supports; Open for staking and harness | Separate supports behind the Samtec mate are already in the layout guide |
| DTEG 6.13.4 | Recovery ground tests with simulated ambient conditions; videos | Burrito | Pass on paper | Ground-test mode |
| DTEG 6.14 | Energetics safe until launch position; armed only at IREC's direction | Burrito | Pass | External arm switches |
| DTEG 6.15 | Arming features external, reachable with the head kept 100 mm away and a face shield on; shown in OpenRocket | Panel | Open | Panel design |
| DTEG 6.16 | Arming verified in 76 dBA plus wind, from 100 mm or more, wearing a face shield | Burrito sounder | **Flag** | See flag 2 |
| DTEG 6.17 | No LiPo; Li-ion only in cylindrical metal cans; coin cells allowed | Packs | Pass | See flag 10 for EuRoC |
| DTEG 7.1 | Control only for pitch or roll stability augmentation or braking; never guided to a target | Salsa canards | Pass for roll control | — |
| DTEG 7.2 | Naturally stable with controls removed or inert and neutral | Vehicle | Open | — |
| DTEG 7.3 | Neutral on abort or on loss of primary power | Salsa | **Flag** | See flag 3 |
| DTEG 7.4.1, 7.4.2, 7.5 | Control electronics follow 6.12; exempt from COTS redundancy; control energetics follow 6.14 | Salsa | Pass for 7.4.2 | Unlike EuRoC LV-0690, no redundancy question at IREC |
| DTEG App F | The former boost-phase dormancy rule (old 7.4) is removed | Burrito, Salsa | Info | Dormancy is field-adjustable; set it per flight |
| D&T-11.3.5 | Ground power umbilicals permitted | Churro | Pass | — |
| DTEG App B2.0 | Justify any use above 24 V; label 50 V and above | PROP domain | N/A at IREC | Applies if any IREC rail goes above 24 V (item 5) |
| R&R-3.6.1–3.6.8 | COTS barometric altimeter is the official log; telemetry counts only from that sensor; read out without site power; officials may open the bay | CATS, Burrito | Pass | Burrito's data is ours, never official |
| R&R-3.4.1.2, 3.4.2.1, 3.4.2.2 | Payload replaceable by ballast; anything needed for flight or recovery is a vehicle subsystem | Payload | **Flag** | See flag 8 |
| R&R-4.4.10.6, 4.4.10.14–4.4.10.17 | Recovery-electronics test reports, arming verification, a dual-redundancy figure; checklists including off-nominal safing | Docs | Open | — |

## Found on the way: repo text to fix at the freeze

- The capture spec's processor row still says PD10 "stays SERVO3_PWM"; D-19Nov.3 and its own servo section make PD10 a test pad.
- The capture spec still lists fuse F6801, which D-19Nov.2 removed.
- 11 Verification:
  - Assertion 9 still mentions the servo feed.
  - Assertion 20 allows no path from the umbilical to a pack except through an ideal diode, but charging (D-20Nov.1) needs a charger path.
  - The Churro bench test checks for "no current into either pack", which won't hold once charging exists.
- current-system.md:
  - It gives EuRoC as 6 in (152.4 mm); Jay now says 7 in.
  - It keeps the 14 October stack; Jay's order is now grid-fin module, then av-bay, then recovery.
- The access-panel brief runs the USB-C leads "up the raceway"; Jay now says no raceways, with wiring through a downcomer.
- AGENTS.md says main is reviewed truth and changes go through branches and pull requests; since Friday, you push to main directly.
