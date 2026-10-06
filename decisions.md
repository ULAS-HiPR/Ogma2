# Ogma 2 decisions

One row per decision. **Decided** rows override older text anywhere in this
repository; fix the older text when you touch it. **Proposed** rows wait for
acceptance. **Open** rows need an answer and an owner.

Native CAD still holds the 8 September draft. Decided rows change the
[capture specification](docs/architecture/schematic-capture-spec.md), not the CAD, until capture.

## Decided — 6 October 2026, Seán

| ID | Decision | Why | Capture consequence | Still to check |
| --- | --- | --- | --- | --- |
| D-6.1 | Pyro and servo energy tap the battery side, upstream of the Croí eFuse U101, each through its own fuse. Pyro energy then passes an external physical arm switch. Servo energy does not. | An output or servo fault must not pull down or latch off the supply that feeds the flight computer. | New `ENERGY_TAP` node; pyro fuse F6101 → arm connector J6101 → `RECOVERY_ARMED_VBAT`; servo fuse F6801 → `SERVO_ARMED_VBAT`, R6804 fitted. | Tap at `BAT_EFUSE_IN` (after Q101) only if TPS26630 keeps Q101 on through U101 faults and SHDN; otherwise tap `VBAT_CROI_INPUT` with reverse-polarity protection per branch. Fuse and arm-switch parts. |
| D-6.2 | Recovery outputs: one high-side TPS1H100 per channel with a set current limit, igniter return to ground, no low-side switch, no one-shot, no permit logic. Staging channel and its latch stay unpopulated until a multistage flight is scheduled. | The physical arm stops inadvertent firing; the limit protects the board; the removed logic added parts without lowering a flight risk. | Remove U6301/U6401 and their timing parts, U6302/U6303/U6402/U6403, Q6301/Q6401, U6002–U6005, U6101, U6102, U6104. Fit R6314/R6414 = 1.24 kΩ 1% (≈2.0 A). Channel 3, U6001 and the staging divider DNP. | Igniter selection: all-fire must sit well under 2.0 A at minimum battery; continuity values against its no-fire current. |
| D-6.3 | Flight firmware holds the battery enable on in flight. U101 and Churro U1001 use auto-retry instead of latch-off. | A broken J103 wire or plug, or one over-current event, must not switch the flight computer off for the rest of the flight. Rev 1 reset aloft with an intermittent battery connector. | `FC_POWER_HOLD` on flight PE5 (pad 4) → RC stretch → diode → `BAT_SHDN_N`; second diode → Samtec pin 8 → Churro → diode → `AV_SHDN_N`. U101 and U1001 MODE to GND. | SHDN threshold and hysteresis with the stretched edge; retry delay. Churro PROP eFuse U2001 left latch-off for the propulsion owner to decide. |
| D-6.4 | The flight MCU backup domain gets its own hold-up. | Checkpoints in backup SRAM must survive the supply dip most likely to cause an in-flight reset. | U201 VBAT (pad 6) fed from `FLIGHT_3V3` through a Schottky, with 100 µF to ground. | H563 VBAT-mode current (DS14258 Table 37); target ≥1 s retention. |
| D-6.5 | Flight-core power is enabled by source presence, not by USB-compliance logic. | Three extra parts sat in series with flight power to keep USB draw under 100 mA before enumeration. | Remove U1203; LM73100 EN/UVLO from a divider on `4V_PRE`. Remove U4402; U4401 limit fixed by R4403 (387–491 mA) from attach. U1201/U1202/U1204 stay for comms and RF source logic. | USB-only startup current against the 387 mA minimum. Strict hosts may need a powered hub. |
| D-6.6 | Sensors run directly from `FLIGHT_3V3`. No per-sensor switches or isolators. | Guards a rare failure with 13 ICs that each add a way to lose a sensor. | Remove U3101–U3501, U3102/U3202/U3302, U3103/U3203/U3303, U3402/U3502 and their enable/bleed resistors. Keep a 0 Ω link per sensor supply. PE6, PA8, PA9, PA10 become spare. | Firmware: I²C bus recovery and sensor soft reset. |
| D-6.7 | Servo power gets local bulk capacitance; regeneration returns to the battery through its fuse. | Back-driven servos could push the logic input past the TPS2121 over-voltage trip (≈8.6–9.3 V). | ≥220 µF, ≥16 V on `SERVO_VBAT` at J6602. | Back-drive the chosen servo on the bench; scope the battery side. |
| D-6.8 | The 100 km sortie is an overlay, not the workhorse sizing case. | It drove the 8 Ah reference pack, 192 MiB window and 102-min flash preparation for 3–9 km flights. | Workhorse endurance and recording window come from measured first-PCBA loads and the vehicle timeline. | Measure on first PCBA. |
| D-6.9 | Full-rate recording starts at launch detect, with a RAM pre-trigger. Erase-ahead is allowed until launch detect. | Continuous full-rate recording from arming used the ≈58 s spare in about a minute of pad hold. | No hardware change. Pad logging at low rate; ≈1 s full-rate or ≈10 s decimated pre-trigger in RAM. | Firmware design. |
| D-6.10 | At capture, keep netlist parity plus about 20 safety assertions; retire per-pin snapshot checks. | Every per-pin assertion breaks when the board is recaptured. | Rewrite checkers during capture. | — |

Budget rule from D-6.1/D-6.2: with Churro feeding the board, its AV eFuse
(≈6.0 A) carries logic (≈0.6 A), servo (2.0 A limit) and pyro (2.0 A per
channel). Fire one channel at a time.

## Proposed — accept on 8 October

| ID | Proposal | Change since 22 September |
| --- | --- | --- |
| D1 | STM32H563VIT6 flight, H563RIT6 comms; three TPS7A91 domains at 3.352 V; PD10 service restart | Sensor and core-enable changes in D-6.5/D-6.6 |
| D2 | Churro source, probes, fuses and AV 3 A / PROP 2 A envelope | U1001 auto-retry and pin-8 hold (D-6.3) |
| D3 | Two local PWM interfaces; 500 kbit/s Classical CAN for Rev A | Servo feed and bulk (D-6.1, D-6.7) |
| D5 | Sector-aligned NOR recording, bounded USB service, source variants | Recording trigger (D-6.9); 100 km overlay (D-6.8) |
| D-6.11 | [Recovery logic specification](docs/architecture/10-recovery-logic.md) | New draft for Anav's review |

D4 (outputs excluded) is replaced by D-6.2.

## Open — 8 October

| Question | Proposed answer | Owner |
| --- | --- | --- |
| Lift the capture hold? | Yes, for everything above | Seán |
| One MCU or two? | Two only if firmware can staff two images, the inter-MCU protocol and two update paths | Anav |
| Where does firmware live; how are tags split? | `firmware/` in Ogma2; `fw-v0.1.0` and `hw-revA` | Anav, Seán |
| Backup altimeter for first flights | Pick model and buyer this week | — |
| Ground radio and link test | Name the receiver; range-test two Wio-LR2021 before PCB order | Arnav |
| Igniter | Select; record all-fire and no-fire current | — |
| Arm switch | Select a maintained switch rated above the pyro fuse at 8.4 V, operable from outside the airframe | — |
| Bay envelope | Airframe inner diameter and bay length Croí must fit | — |
| Capture review | Arnav: power and connectors. Anav: MCU and sensors | Arnav, Anav |
| Recovery parameters | Main altitude, lockouts and timers per vehicle (D-6.11) | Anav, vehicle lead |
| Propulsion eFuse U2001 fault mode | Propulsion owner decides latch-off vs retry | Fajita owner |
| Foinse "dumb driver" allowance in the LTS boundary copy | Accept or remove in the controlling copy | Seán, LTS |
