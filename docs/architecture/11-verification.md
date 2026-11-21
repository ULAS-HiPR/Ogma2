# 11 Verification

**2 November · live again ([D-2Nov.12](../../decisions.md)).** What has to pass
before a board is ordered, before a configuration is qualified, and before a
flight. Nothing has run: there's no Ogma 2 hardware and no target firmware yet.
The full experiment procedures stay in the archived
[execution plan](../archive/reliability-execution-plan.md); this page is the live
list, and it decides nothing on its own.

```mermaid
flowchart LR
  G0["G0
bounded bench work"] --> G1["G1
engineering PCB order"] --> G2["G2
installed configuration
qualified"] --> G3["G3
unit and mission
release"]
```

## Release gates

Accepted by Seán on 6 September as part of EX-01. Adopting a gate passes
nothing.

| Gate | Allows | Needs | Doesn't prove |
| --- | --- | --- | --- |
| G0 · bounded bench work | One identified low-risk, inert experiment | Written stimulus and limits, safe supply and loads, instruments, the expected result, stop conditions | PCB or flight approval |
| G1 · engineering PCB order | Rev A prototype manufacture | Exact part and pin map; power and reset feasibility; an output hazard review for the prototype; mechanical fit; assembly and test access; named open risks | Qualified recovery, the final mission envelope, operational reliability |
| G2 · installed-configuration qualification | A claim against a named environment and mission | Controlled hardware, firmware, harness and bay; performance and fault tests; environmental, RF and service evidence; reviewed residual risks | Every unit, or every future mission |
| G3 · unit and mission release | That configuration on that mission | Unit acceptance; battery and service-life records; profile readback; recovery and range review; a closure manifest; a field rehearsal | Reuse without inspection, or a changed configuration |

G1 can go ahead without separate pre-order coupons (7 September amendment),
with the unproven assumptions listed and a safe block-test plan for the first
PCBA. Live energetic, propulsion and flight operations each need their own
approved procedure.

## Campaigns

| ID | Proves | First run on | Main evidence | Gate | Status |
| --- | --- | --- | --- | --- | --- |
| EX-01 | Which functions survive which faults, in which phase | Policy now; tests through EX-02 to EX-10 | [Flight fault contract](../../interfaces/flight-fault-contract.md) | All | Policy accepted 6 Sep |
| EX-02 · PWR-01 | Power starts on its own and contains the faults it claims, through every source transition, including the umbilical pulled under load and repeatedly hot-plugged (D-21Nov.3) | First PCBA, current-limited supply, inert loads | Source-state drawing; traces on one timebase | G0, G1 | Not started |
| EX-03 · RST-01 | What a restart can rebuild in each reset class; the power hold is back within 50 ms | Target MCU, then first PCBA | Reset and retention traces | G1, G2 | Host model only (12 tests) |
| EX-04 · MCU-01 | The H563 meets the memory, timing, ECC and pin needs | Development board, then target | Build, timing and memory matrix | G1 | Not started |
| EX-05 · SNS-01 | The sensors support the decisions over the envelope; stale or invalid data never becomes valid | Replays, then hardware | Measurement contract; replay results | G1, G2 | Not started |
| EX-06 · LOG-01 | Recording can fail without taking control; retained data can be trusted | First PCBA | Interruption results | G1, G2 | Not started |
| EX-07 · OUT-01 | Each output does exactly its job: no wrong-channel, early, repeated or excessive firing | First PCBA, inert loads | Per-channel fault table; inert traces | G1, G2 | Not started |
| EX-08 · BAY-01 | The bay can be built, serviced and qualified, with EuRoC access from the ground | 1:1 inert mockup | Mockup record | G1, G2 | Not started |
| EX-09 · LINK-01 | Broken or hostile links can't change authority or timing | First PCBA | Protocol fault tests | G1, G2 | Not started |
| EX-10 · SYS-01 | The boundaries still hold together | Integrated assembly | Integrated results; residual-risk record | G2, G3 | Not started |

Owners and independent reviewers aren't assigned yet. Seán owns hardware and
layout; Anav owns firmware.

## Bench tests by block

First PCBA, inert loads, current-limited supplies.

| Block | Tests | Detail |
| --- | --- | --- |
| Outputs | Arms open means no output; low-side self-test; a high side on alone stays below no-fire; all-fire at minimum battery with one body-diode drop; shorts during a pulse; a staging short leaves recovery working; the latch after a reset | [03 Outputs](03-energetic-outputs.md#bench-tests-inert-loads-only) |
| Power | Cold start with Churro's return absent; branch faults; break the enable loop during a simulated flight and reset the flight MCU: the board stays up; the hold releases at LANDED and at the time cap; servo back-drive at 8.4 V, standalone and Churro-fed at the lowest logic load, against the TPS2121 trip and U101's over-voltage | [02 Power](02-power.md), [power contract](../../interfaces/power-contract.md#first-test-and-closure) |
| Sensors | Short one sensor's supply: the flight rail stays in regulation and the other sensors keep running; the link's drop at each sensor's peak; dead-sensor pin parking | [07 Sensors](07-sensors-logging.md) |
| Magnetometer | Noise and heading error in the assembled bay, with servos moving and current in the pyro and battery leads | [Layout guide C09a](../pcb-layout-guide.md#c09a-magnetometer) |
| Churro | Umbilical pulled under load on every branch; no current into a pack except through its charger; 50 plug/pull cycles at full voltage with the real cable (D-21Nov.3); each charger charges, stops when hot and stops at Go (D-21Nov.2); the source report; startup with AUX absent | [08 Churro](08-foinse-can.md) |
| Recovery logic | Rev 1 replay; hardware-in-the-loop trajectories; reset injection in every phase; a six-hour pad hold with pressure drift; the ground-test mode; a false launch detect on the pad fires nothing | [10 Recovery logic](10-recovery-logic.md#tests) |
| CAN boundary | Peer in reset, missing, corrupt, bus-off; stale and illegal requests | [Boundary contract](../../interfaces/ogma-foinse-propulsion-boundary.md#boundary-tests) |

## EuRoC tests and checks

From the EuRoC SRD. These feed G2 and G3 for a EuRoC flight.

| Rule | What it asks | How we show it |
| --- | --- | --- |
| LV-0510 | Thermally test the electronics to know their reliable operating range | Thermal-chamber run of the flight assembly, powered and logging the MCU, IMU and barometer temperatures; then six hours closed in sun on a rail, charging |
| LV-0520 | Test every recovery mechanism successfully before EuRoC, with simulated triggers, recorded in a signed annex | Ground-test mode (D-2Nov.10): a vacuum chamber drives both barometers; inert loads first, then the procedure EuRoC accepts |
| LV-0320 | At least six hours of battery life on the launch rail | Measured pad current × 6 h against cold pack capacity, then a six-hour powered hold on the bench without the umbilical; for every onboard pack: AV, the 6S actuator pack and the CATS Vega's cell |
| LV-0300 | No LiPo or lithium primary cells on board | Inspection of every pack: AV, the 6S actuator pack and the CATS Vega's cell (Li-ion only in metal-can cylindrical cells, Appendix C) |
| LV-0260–0280, 0310, 0540–0550 | Manually operated switches, connectors, batteries and arming features on the airframe, reachable from the ground without ladders, opposite the rail | Bay mockup, then the integrated vehicle on a rail |
| LV-0480–0500 | Safety-critical wiring: cable management, secure connections, cryogenic-rated insulation near the N₂O | Harness inspection |
| LV-0530 | Energetics safed until the rocket is in launch position | Arming procedure; arm sense in the pad telemetry |
| LV-0240, 0250, 0430 | Fully redundant recovery electronics with their own power, one set COTS; a CATS Vega in each stage | Vehicle review: the CATS Vega on its own cell beside Burrito, each with its own e-match per event, and no SRAD hardware between the Vega and its e-matches (D-18Nov.2, Appendix B1) |
| LV-0440–0470 | The CATS Vega's call-sign, EuRoC's mandated firmware, the CATS ground station, and its switch reachable like ours | Every CATS link shown at the FRR; firmware version read back before the flight |
| LV-0340–0380 | Dual deployment: drogue at or near apogee, 23–46 m/s; main at or below 450 m AGL, under 9 m/s | Recovery's sizing; the main-altitude limit checked at readback (D-18Nov.5) |
| LV-0650–0700 | Active control: allowed uses, stable without it, fails safe, boost dormancy, electronics rules | The active board's review under D-2Nov.8 and D-5Nov.2, after the LV-0690 ruling: dormant until at least 1500 m AGL without flight history (Appendix F1), Safe on a stale message, its arm key in Churro's ACT branch (D-21Nov.1), neutral when unpowered (D-21Nov.7) |
| LV-0780–0820 | RF windows: 360°, at least two calibres long, not carbon; antennas centred in them, away from wiring and metal; no radio outside the skin | Bay mockup, then the integrated vehicle |
| LV-0030, 0190, Appendix E1, SE-0010–0030 | Remote igniter arming; remote vent after an abort; a manual disconnect for valve power; launch-control range, interlock and dead-man switches | Propulsion's evidence, listed in the [boundary contract](../../interfaces/ogma-foinse-propulsion-boundary.md#euroc-items-on-the-propulsion-side) |

## Safety assertions at capture

D-6.10 replaces per-pin snapshot checks with netlist parity plus about 20
assertions. Write them as a checker during capture. Each must hold in every
population variant.

1. Each `PYROn_FIRE` and `PYROn_LS_SELECT` net has a 100 kΩ pull-down and no
   driver except its own MCU pin.
2. Each channel's fire pin and low-side select sit on different GPIO ports.
3. Each `OUTPUTn_LOW` connects only to its low-side drain, its continuity
   network and J6601; never straight to GND.
4. `ENERGY_TAP` (`BAT_EFUSE_IN`) connects only to Q101's drain, U101's IN pins,
   F6101, F6102, its sense tap and local decoupling.
5. F6101 feeds only J6101; F6102 only J6102.
6. `RECOVERY_ARMED_VBAT` reaches only channels 1 and 2 (through R6310 / R6410),
   the recovery arm sense (R6101) and its rail-ADC divider (R8007, to PA2);
   `STAGING_ARMED_VBAT` only channel 3 (through R6510) and the staging sense
   (R6103).
7. U6504's IN comes only from U6502, whose inputs are `PYRO3_FIRE` and
   `STAGE_ELIGIBLE`.
8. U6001's CLR̄ is `FLIGHT_NRST`, its D is `STAGE_ARM_INVALID`, and its CLK is
   PD15 with a pull-down.
9. No logic-rail net connects to an armed rail. The only
   logic-rail paths to J6601 are the continuity resistors R69x1 / R69x2.
10. R6310, R6410 and R6510 are DNP until the igniter values close.
11. The comms MCU has no path to any pyro, servo or arm net.
12. CAN, radio and USB nets have no path to an output enable.
13. J6101, J6102 and Churro's J701 can't mate one another: different families or keying.
14. `FC_POWER_HOLD` reaches `BAT_SHDN_N` and J102.8 only through diodes, with
    the D-2Nov.4 RC values.
15. Each of the five flight sensors is fed through its 47 Ω link and the
    magnetometer through 22 Ω; their I²C pull-ups sit on `FLIGHT_3V3`.
16. The magnetometer's nets land on PA8, PC9 and PE6 and nowhere else.
17. J101 and J102 sit in mutually exclusive BOM variants.
18. USB VBUS reaches only its connector's ESD diode (D4401) and decoupling, the
    logic mux through U4401, the USB-present divider R1208 / R1209 into the
    source logic, and the protected VBUS sense on the comms MCU: never an armed
    rail, the servo feed or a pack.
19. Each TPS7A91 divider is 31.9 kΩ over 10 kΩ; U101 and U1001 MODE are tied to GND.
20. Churro: every source has its own ideal-diode stage, and the only path from
    the umbilical connector to a pack connector is through that pack's charger
    (D-21Nov.2).
21. Churro: R6101's top is on `AV_PACK`; R1006 stays 22.1 kΩ.
22. Burrito: each CAN connector's reference contact reaches board GND only
    through its series parts (B-39).

## Records

Use the [verification record template](../templates/verification-record.md) for
every run. Keep large raw traces outside Git, with a manifest, checksums and
retrieval instructions; keep small fixtures, parsers and concise results here.
Declare pass limits before a run, not after it.
