# Architecture sign-off, 19 November 2026

Seán signed off the Ogma 2 architecture part by part, by voice and text, before
the first build session (19 November, 18:00). His words are quoted; the rest is
the reviewed summary. Decisions are D-19Nov.1–9 in [decisions.md](../../../decisions.md).

## 1. Philosophy: signed

"I sign off 100%." In short: simplex and fail-safe, prevention by deleting
everything that doesn't earn its place, and the CATS Vega as the dissimilar
redundancy.

In standard terms: a fail-safe simplex core with containment and supervised
restart, backed by an independent, dissimilar COTS recovery chain. Disarmed, each
output has three independent inhibits (the NSTS 1700.7B pattern for
catastrophic hazards); armed, two, both in the flight MCU. The weight sits on
fault prevention and removal; fault forecasting (FMEA, numbers) is thin. The
long exposure is the pad, six hours armed, not the flight.

## 2. The vehicle: signed with its open items

"I sign off on that vehicle with those open items."

Bottom up: engine; tanks and COPVs; the av-bay, with Burrito bolted edge to edge
to Churro; the active module (RCS and grid fins, merged, D-19Nov.6), just above
or below the av-bay; the recovery bay; the nose and payloads. Fajita on CAN bus
1, the active board on bus 2 with its own pack and arm key and permission only
from Burrito, the CATS Vega and payloads independent. The ground station works
(LoRa and CATS); launch control is propulsion's.

Open: the drogue joint above the active module and the charge distance (James);
where the packs and the CATS Vega sit; the RF window (Jay); Fajita's owner and
the propulsion items; whether the umbilical is fitted; LV-0690 (officials).

## 3. Burrito and Churro: all ten subsystems signed

| Subsystem | Signed | Decided or noted | Open |
| --- | --- | --- | --- |
| Power | "Okay, I approve this." | No second 4 V buck: the repo already rejected one per domain, and the flight core's input has an over-voltage cut-off (U1401 OVLO, R1401/R1402). Batteries and connectors get particular attention. | OVLO threshold against the datasheet; 5 A source fuse and 3 A ceiling heat; two eFuses in series; pack location; pad current, back-drive (now gone with D-19Nov.2), umbilical switchover |
| Supervision and resets | "That all seems fair" | D-19Nov.1, a must before first flight | Watchdog window; reset injection in every phase |
| Processors | "I sign off on the processors." | The UCPD dead-battery pins pull down the TDK IMU's SPI lines until boot step 2; the same on the active board if it uses an H5 | Measured clock and memory budgets |
| Sensors and recording | "I sign off on all of the above there." | No black box board: the NOR is the black box. Proposed: the in-flight downlink carries supply voltages, reset count and phase | One vent feeds both barometers, and the CATS Vega if it shares the bay; magnetometer calibration in the bay |
| Outputs and arming | "I sign off on everything else." | Paired e-matches (D-19Nov.8). Proposed: one e-match make for both chains, a few test-fired from every batch | E-match make and numbers; arm switches and fuses; the inert bench tests, written but not run |
| Servos | "I sign off 7 to 9." | Removed (D-19Nov.2); freed pins (D-19Nov.3) | Reset-memory values on the bench |
| CAN | as above | Two buses kept; Gecko on both ends of both | Bus 2 frames and stale timeout (tonight); the Fajita message contract |
| GNSS, radio, USB | as above | One USB-C per board at the panel (D-19Nov.9) | Radio link test with the ground station before ordering; antenna parts; labels |
| Connectors and harness | "I sign off on literally everything you have said here." | JST to Gecko (D-19Nov.5); sounder at arming (D-19Nov.4) | Arm-switch and umbilical parts ([access panel brief](../../briefs/access-panel.md)) |

## Testing

No shock or vibration test is written yet, only targets: −20 to +70 °C powered,
50 g quasi-static, 200 g shock. Proposed: run it powered and logging, on the
whole bay with real packs and harnesses and the supply on a scope, hunting
intermittent opens like the Rev 1 suspect. Found on 19 November: Resonate
Testing in Newry (vibration, shock including pyroshock, thermal vacuum), the
CREDIT Technology Gateway at DkIT (vibration, HALT), and Mbryonics' in-house
shakers and TVAC. Seán's call was 3/5; half right.

## Subprojects

Burrito and Churro (Seán); the active board; the access panel and harness;
Fajita; e-reg, an avionics and propulsion collaboration. Proposed for e-reg:
inside propulsion's boundary, on Fajita or propulsion's own bus, never a third
node on bus 1.

## Before capture

James (joint, charge distance); Recovery (what two e-matches per system means);
the e-match make; the arm-switch and umbilical parts; the OVLO threshold; the
reset-memory values; the records follow-up listed in the project log; Seán lifts
the capture hold.
