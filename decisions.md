# Ogma 2 decisions

One row per decision. **Decided** rows override older text anywhere in this
repository; fix the older text when you touch it. **Proposed** rows wait for
acceptance. **Open** rows need an answer and an owner.

Native CAD still holds the 8 September draft. Decided rows change the
[capture specification](docs/architecture/schematic-capture-spec.md), not the CAD, until capture.

## Proposed — new, 13 October (Anav against on first reaction, 14 October)

| ID | Proposal | Why |
| --- | --- | --- |
| D-13.1 | Roll control moves to its own board, **Enchilada**: a third named CAN peer with its own MCU (default STM32H563; H7 only if the sims' controller misses its time budget on an H563). Burrito authorises over CAN (go, stop, boost dormancy expired) and sends slow state (flight stage, velocity, altitude); it never computes roll commands. Fast roll rate comes from a gyro on Enchilada (recommended; replaces "no duplicated sensors") or is streamed from Burrito (gyro alone ≈22–27% of the bus at 1 kHz; ties Enchilada to Burrito's scheduling and restart gap). Actuators go to neutral on stop, abort or stale authorisation, through a path that survives hung Enchilada firmware. The stale timeout is shorter than Burrito's restart, so a Burrito reset always neutralises. Enchilada's CAN IDs rank below Burrito's and Fajita's. It sits on an unterminated stub, so removing it leaves the Burrito–Fajita link intact. Power comes from its own fused Churro output with local bulk, not from Burrito. Actuator, output stage and current follow the requirements: servos for canards or grid fins, valve drivers for cold gas. D-7.1 is unchanged: Burrito's three servos make bounded, event-triggered moves only (e.g. unlatch the payload at booster apogee), never continuous or closed-loop actuation. The Burrito and Churro owners sign off the boundary items. | Roll control has hard sense-to-actuate deadlines and runs an algorithm from sims we haven't seen; it must not share the core that does flight-state estimation and recovery. Ogma1 had too many MCUs, so split only where timing demands it. Same approach as CATS Vega. EuRoC SRD Issue 1.1 RQT-0670 requires actuators to fail safe to neutral. Source: Seán and Arnav, Discord DM, 13 October 20:56–21:39; Seán's review notes, 13 October. |

## Open — Enchilada (D-13.1)

| Question | Proposed answer | Owner |
| --- | --- | --- |
| Fast roll rate: gyro on Enchilada or streamed from Burrito? | Gyro on Enchilada, ranged above the maximum roll rate and aligned to the roll axis; Burrito sends slow state only | Anav |
| Actuator and current | 14 October: RCS with four solenoids and grid fins are EuRoC's closed-loop actuators. If RCS does roll, Enchilada needs four valve drivers, not servos | Sim Systems |
| Neutral path that survives hung firmware | Servos that go to neutral on signal loss (bench-check each model) plus an external watchdog that cuts PWM, not power. Alternative: a hardware stop line from Burrito, which also catches a controller that runs but is wrong | — |
| Churro output for Enchilada | Own fuse and bulk, sized to actuator stall; amends the D2 envelope (AV 3 A, PROP 2 A) and Foinse2 CAD | — |
| Controller compute | Run the sims' controller on a Nucleo-H563 before choosing the MCU; check for double-precision code, since the H563 FPU is single-precision | — |
| Roll data logging | Enchilada status to Burrito's recorder at 100 Hz | — |
| Competition rules | Ask EuRoC what RQT-0690's reference to RQT-0240 requires of one roll board; check this year's EuRoC, the Irish competition and IREC | — |
| Third CAN node | Propulsion owner agrees; IDs, termination and boundary tests go in the boundary contract | Fajita owner |

## Decided — 7 October 2026, Seán

| ID | Decision | Why | Capture consequence | Still to check |
| --- | --- | --- | --- | --- |
| D-7.1 | Burrito keeps **three pyro channels and three servos**. Core requirement. Channels 1 and 2 are recovery. Channel 3 is staging / air-start, fitted for Rev A, with the hardware reset inhibit. Servo 3 stays on PD10. The service-power enable moves to PE8. Overrides the staging-DNP part of D-6.2 and the two-servo part of D3. | Flights need a third pyro event and a third actuator; leaving them DNP would mean a new board revision. | Fit channel 3: U6504 TPS1H100, R6514 = 1.24 kΩ 1% (≈2.0 A), igniter return to ground, J6601.3 / .6 wired. Fit latch U6001 and divider R6103 / R6104. Keep servo 3 as drawn: PD10 `SERVO3_PWM` (LPTIM2_CH2), R6606 / R6607, U6804 A3, J6602.7 / .8 / .9. PE8 pad 39 → `SERVICE_POWER_EN`. | Latch and staging-arm wiring (D-7.2). Three servos share U6802's 2.0 A limit. Igniter for air-start. |

## Proposed — new, 7 October

| ID | Proposal | Why |
| --- | --- | --- |
| D-7.2 | Staging energy: `ENERGY_TAP` → F6101 (shared with recovery) → new 2-contact staging arm connector J6102 → `STAGING_ARMED_VBAT` → R6510 → U6504. J6102 must not mate J6101, J701 or the GH loops. Reset inhibit: U6001 CLR̄ = `FLIGHT_NRST`, CLK = `NEW_FLIGHT_CLEAR_REQUEST` (PD15), D = `STAGE_ARM_INVALID` (U6103 OUTB, high when staging energy is absent); Q `STAGE_ELIGIBLE` AND `PYRO3_FIRE` (PE12) through a true 2-input AND at U6502 (SN74LVC1G08, or the 1G97 redrawn with IN1 as its own pin; the CAD symbol ties IN1 to GND) → U6504 IN. ~Q `STAGE_INHIBIT_LATCHED` → PD14. Staging arm sense: `STAGE_ARM_INVALID` → R6108 → PC9. Remove U6501, R6511–R6513, U6503, Q6501 and its gate parts; U6104 and the permit gates stay removed; PE13, PE15 → NC. | Any flight-MCU reset clears the latch, so channel 3 can't fire again until someone disarms staging and deliberately sets a new flight. Separate arms let the pad crew arm recovery without arming ignition. Reuses the CAD's own staging rail and sense; one gate instead of the old eight. |

## Decided — 6 October 2026, Seán

| ID | Decision | Why | Capture consequence | Still to check |
| --- | --- | --- | --- | --- |
| D-6.1 | Pyro and servo energy tap the battery side, upstream of the Croí eFuse U101, each through its own fuse. Pyro energy then passes an external physical arm switch. Servo energy does not. | An output or servo fault must not pull down or latch off the supply that feeds the flight computer. | New `ENERGY_TAP` node; pyro fuse F6101 → arm connector J6101 → `RECOVERY_ARMED_VBAT`; servo fuse F6801 → `SERVO_ARMED_VBAT`, R6804 fitted. | Tap at `BAT_EFUSE_IN` (after Q101) only if TPS26630 keeps Q101 on through U101 faults and SHDN; otherwise tap `VBAT_CROI_INPUT` with reverse-polarity protection per branch. Fuse and arm-switch parts. Arm connector J6101 must not mate Churro J701 (Micro-Fit 430450200) or the GH enable loops. |
| D-6.2 | Recovery outputs: one high-side TPS1H100 per channel with a set current limit, igniter return to ground, no low-side switch, no one-shot, no permit logic. Staging channel and its latch stay unpopulated until a multistage flight is scheduled (staging part superseded by D-7.1). | The physical arm stops inadvertent firing; the limit protects the board; the removed logic added parts without lowering a flight risk. | Remove U6301/U6401 and their timing parts, U6302/U6303/U6402/U6403, Q6301/Q6401, U6002–U6005, U6101, U6102, U6104. Fit R6314/R6414 = 1.24 kΩ 1% (≈2.0 A). Channel 3, U6001 and the staging divider DNP. | Igniter selection: all-fire must sit well under 2.0 A at minimum battery; continuity values against its no-fire current. |
| D-6.3 | Flight firmware holds the battery enable on in flight. U101 and Churro U1001 use auto-retry instead of latch-off. | A broken J103 wire or plug, or one over-current event, must not switch the flight computer off for the rest of the flight. Rev 1 reset aloft with an intermittent battery connector. | `FC_POWER_HOLD` on flight PE5 (pad 4) → RC stretch → diode → `BAT_SHDN_N`; second diode → Samtec pin 8 → Churro → diode → `AV_SHDN_N`. U101 and U1001 MODE to GND. | SHDN threshold and hysteresis with the stretched edge; retry delay. Churro PROP eFuse U2001 left latch-off for the propulsion owner to decide. |
| D-6.4 | The flight MCU backup domain gets its own hold-up. | Checkpoints in backup SRAM must survive the supply dip most likely to cause an in-flight reset. | U201 VBAT (pad 6) fed from `FLIGHT_3V3` through a Schottky, with 100 µF to ground. | H563 VBAT-mode current (DS14258 Table 37); target ≥1 s retention. |
| D-6.5 | Flight-core power is enabled by source presence, not by USB-compliance logic. | Three extra parts sat in series with flight power to keep USB draw under 100 mA before enumeration. | Remove U1203; LM73100 EN/UVLO from a divider on `4V_PRE`. Remove U4402; U4401 limit fixed by R4403 (387–491 mA) from attach. U1201/U1202/U1204 stay for comms and RF source logic. | USB-only startup current against the 387 mA minimum. Strict hosts may need a powered hub. |
| D-6.6 | Sensors run directly from `FLIGHT_3V3`. No per-sensor switches or isolators. | Guards a rare failure with 13 ICs that each add a way to lose a sensor. | Remove U3101–U3501, U3102/U3202/U3302, U3103/U3203/U3303, U3402/U3502 and their enable/bleed resistors. Keep a 0 Ω link per sensor supply. PE6, PA8, PA9, PA10 become spare. | Firmware: I²C bus recovery and sensor soft reset. |
| D-6.7 | Servo power gets local bulk capacitance; regeneration returns to the battery through its fuse. | Back-driven servos could push the logic input past the TPS2121 over-voltage trip (≈8.6–9.3 V). | ≥220 µF, ≥16 V on `SERVO_VBAT` at J6602. | Back-drive the chosen servo on the bench; scope the battery side. |
| D-6.8 | The 100 km sortie is an overlay, not the workhorse sizing case. | It drove the 8 Ah reference pack, 192 MiB window and 102-min flash preparation for 3–9 km flights. | Workhorse endurance and recording window come from measured first-PCBA loads and the vehicle timeline. | Measure on first PCBA. |
| D-6.9 | Full-rate recording starts at launch detect, with a RAM pre-trigger. Erase-ahead is allowed until launch detect. | Continuous full-rate recording from arming used the ≈58 s spare in about a minute of pad hold. | No hardware change. Pad logging at low rate; ≈1 s full-rate or ≈10 s decimated pre-trigger in RAM. | Firmware design. |
| D-6.10 | At capture, keep netlist parity plus about 20 safety assertions; retire per-pin snapshot checks. | Every per-pin assertion breaks when the board is recaptured. | Rewrite checkers during capture. | — |
| D-6.12 | Keep two processors: flight and comms. | Flight must keep flying with comms held in reset; USB, radio and GNSS stalls stay off the flight schedule. | None; both are in the CAD. | Comms package (D1). |

Budget rule from D-6.1/D-6.2/D-7.1: with Churro feeding the board, its AV eFuse
(≈6.0 A) carries logic (≈0.6 A), servos (2.0 A limit shared by three) and pyro
(2.0 A per channel, three channels). Fire one channel at a time.

## Proposed — accept on Sunday 18 October

| ID | Proposal | Change since 22 September |
| --- | --- | --- |
| D1 | STM32H563VIT6 flight, H563RIT6 comms package; three TPS7A91 domains at 3.352 V; PE8 service restart (D-7.1) | Two processors decided (D-6.12); sensor and core-enable changes in D-6.5/D-6.6 |
| D2 | Churro source, probes, fuses and AV 3 A / PROP 2 A envelope | U1001 auto-retry and pin-8 hold (D-6.3) |
| D3 | Three local PWM interfaces (D-7.1); 500 kbit/s Classical CAN for Rev A | Servo feed and bulk (D-6.1, D-6.7) |
| D5 | Sector-aligned NOR recording, bounded USB service, source variants | Recording trigger (D-6.9); 100 km overlay (D-6.8) |
| D-6.11 | [Recovery logic specification](docs/architecture/10-recovery-logic.md) | New draft for Anav's review |

D4 (outputs excluded) is replaced by D-6.2.

## Open — Sunday 18 October

| Question | Proposed answer | Owner |
| --- | --- | --- |
| Lift the capture hold? | Yes, for everything above | Seán |
| Where does firmware live; how are tags split? | `firmware/` in Ogma2; `fw-v0.1.0` and `hw-revA` | Anav, Seán |
| Backup recovery electronics | For EuRoC, the mandatory CATS Vega (RQT-0430) flies as the COTS redundant set with its own power (0240, 0250). Pick the buyer | — |
| Ground radio and link test | Check whether the SX1272 Ogma cartridge hears the Wio-LR2021 at our settings or a new cartridge is needed; range-test before PCB order | Arnav |
| Igniters | Select for recovery and for air-start; record all-fire and no-fire current | — |
| Arm switches and J6101 / J6102 connectors | Select maintained switches rated above the pyro fuse at 8.4 V, operable from outside the airframe, and 2-contact connectors that can't mate each other, J701 or the GH loops. EuRoC: on the airframe, reachable from the ground with the rocket vertical, opposite the rail (RQT-0260–0280, 0540–0550); a key switch is the candidate | — |
| Bay envelope | EuRoC and IREC are 6 in (152.4 mm); Croí's 80 mm fits. IRRC boosters are 54 or 76 mm (unconfirmed) and carry a CATS Vega or Eggtimer. Hold the 65–70 mm, longer Croí until IRRC's diameter is confirmed and something there must carry Ogma. Bay length still open | Seán, Elgan |
| Capture review | Arnav: power and connectors. Anav: MCU and sensors | Arnav, Anav |
| Recovery parameters | Main altitude, lockouts and timers per vehicle (D-6.11); drogue descent at most 46 m/s (James, to check) | Anav, vehicle lead |
| Propulsion eFuse U2001 fault mode | Propulsion owner decides latch-off vs retry | Fajita owner |
| Foinse "dumb driver" allowance in the LTS boundary copy | Accept or remove in the controlling copy | Seán, LTS |
| Electronics requirements | Seán writes them from EuRoC SRD Issue 1.1 on Saturday 17 October and posts them for Jay. IREC application 25 October; IRRC rules not out | Seán, James |
| Pyro over CAN (Jay's ask, 14 October) | Not for recovery: only the flight MCU commands recovery and staging outputs. EuRoC's charges sit in the recovery bay directly above the av-bay and wire from Burrito; redundancy comes from the CATS Vega on its own power | Seán, Jay |
| Anav's pyro-channel circuit (Sunday) | Review against D-6.1 and D-6.2: the arm switch sits in the battery-side feed ahead of each high-side switch, not on the low side; the igniter returns to ground. A different topology needs a case against D-6.2 | Anav |
| Pad power and pack | At least 6 h on the rail on internal power (RQT-0320); no LiPo on board (0300); the umbilical powers the rocket during filling. The umbilical enters at Churro, which owns source entry; a 2S Li-ion pack keeps the 8.4 V design point; charging through the umbilical stays out until a need is named | Seán |
| Pad state after arming | Armed before filling, then nobody within 600 m: arm and continuity state must be readable remotely, by Ogma telemetry or the umbilical | — |
| Magnetometer (Radu: hopper, maybe grid fins) | Not on Burrito until Radu says what heading he needs and how accurately; put it on the board that runs that loop, away from batteries and servos | Radu, Seán |
| Grid fins (EuRoC, closed loop under drogue) | Their own CAN node at the top of the rocket, on Enchilada's design with a servo stage, powered from Churro through the raceway; Burrito authorises after deployment | Radu (placement) |
