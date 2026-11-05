# Log: core-board sweep, 5 November 2026

Questions and decisions as they happen, newest last. Append only. Each entry
names its section from the [README](README.md). **Decided tonight** means Seán
decided it here; it goes into `decisions.md` and the docs at the end of the
evening. **Open** and **Proposed** stay as they are until he decides.

## Before pass 1: decided in chat on 5 November

1. §6 **Decided tonight (Seán):** keep three pyro channels, one e-match each,
   with separate recovery and staging arm switches. Confirms D-7.1 and
   D-2Nov.1; no change. The "flight computer just needs one" remark is dropped.
2. §5 **Decided tonight (Seán):** the flash stays on the flight MCU. No change.
3. §5, §9 **Decided tonight (Seán):** the magnetometer stays on Burrito
   (D-2Nov.11), and the active board carries its own as well. Adds a
   magnetometer to the D-2Nov.8 node rules.
4. §9 **Decided tonight (Seán), 4a:** Burrito sends the active board one
   message at a fixed rate (10–20 Hz): Safe (default, neutral), Active (allowed
   to steer, sent only after Burrito's field-adjustable dormancy, LV-0680) or
   Abort (neutral until power-cycled on the ground), with a counter. Stale
   counts as Safe. The board has its own hardware path to neutral (D-2Nov.8).
5. §9, §4 **Decided tonight (Seán), 4b:** the active board gets its own CAN bus,
   Burrito–active board only, on the flight MCU's FDCAN2. Amends D-2Nov.8's
   unterminated stub on the Fajita bus; Fajita's owner no longer has to agree to
   a third node. Cost: a second transceiver, level shifter, ESD part and
   connector. **Proposed pins** (to confirm in §4): FDCAN2 RX PB5, TX PA10; CAN
   standby to PE10, shared by both transceivers; recovery arm sense PC8 to PE13;
   channel-2 low side PA10 to PC8. Uses the last two spare flight pins.
6. §2 **Decided tonight (Seán), 4c:** the active board's servos run from a third
   Churro branch off the AV source, with its own eFuse and its own enable loop
   at the bottom of the raceway, not after U1001, sized for two servos stalling.
   Cost accepted: one more eFuse stage, connector and enable on Churro, and the
   AV pack and harness limit (3 A today, 5 A pack fuse) has to cover it.
7. §9 **Open, 5:** CAN connectors. Seán unsure; may change later. On the table:
   Micro-Fit 3.0, 3-way single row, for bus 2 (a pin count nothing else on the
   vehicle uses; the 6S pack is a 4-way Micro-Fit); J501 stays JST GH until a
   hand tug test; Harwin Gecko-MT as the high-reliability alternative (what
   Waterloo Rocketry flies). DroneCAN calls GH unsuitable for safety-critical
   hardware.
8. §2, §6, §9 **Open (Seán):** we may need an external pyro board, probably on
   the same CAN bus as the active board. Which Churro supply would it use?
   Unsure. Notes for the sweep:
   - Supply, if it happens: its own Churro branch off the AV source, fused,
     with its own physical arm switch in series at the bottom of the raceway
     (LV-0530, 0550, 0270, 0280). Not the active board's servo branch, not
     Burrito (Ogma doesn't distribute power), not the 6S PROP feed. The AV
     pack is fine for the SRAD chain; the CATS Vega stays the chain with its
     own battery (LV-0240).
   - It reopens a core rule: only the flight MCU commands recovery and staging
     outputs, and CAN can't (AGENTS.md, current-system, D-2Nov.9; the "pyro
     over CAN" Open row, Jay's 14 Oct ask, says "not for recovery").
   - On bus 2 it would share wires with the experimental board that bus 2
     exists to isolate, and that harness would become safety-critical
     deployment wiring (SRD §5.4, LV-0490 tug test) inside the ground test
     (LV-0520).
   - Burrito has no room for wired extras: after the FDCAN2 move no flight
     pins are spare, and the H563's two CAN controllers are both used.
   - What decides it: what the board would fire, and where.
9. §2, §10, §11 **Proposed (Seán):** one access panel on the side of the
   rocket, reachable from the ground, holding the arm switches, the umbilical
   and a service port for programming. Notes:
   - The panel sits low with the packs and switches (Jay, 2 Nov), so USB runs up
     the raceway to Burrito's J4401. Full-speed USB over that length and
     through two connectors needs a bench test.
   - Programming through it is USB to the comms MCU; the flight MCU takes its
     new build over the inter-MCU UART and checks it after reboot (05's
     "two-MCU update"). Comms never gets a path to flight reset (firmware
     interface). SWD (TC2030) stays bench-only.
   - The umbilical plug at the panel matches D-2Nov.7's pull-away plug on the
     skin. The active board's enable and any external pyro arm would join the
     switches there.
10. §2 **Open (Jay and Seán):** is the umbilical needed? Jay: switch on, walk
    away, launch. Seán: hours pass between switch-on and launch, and GNSS lock
    should come early. In the repo, the avionics pack alone covers ≥6 h on the
    rail plus flight (D-2Nov.6), so for avionics the umbilical is margin and
    GNSS can stay on through the hold either way. Its stronger case is the
    propulsion side during filling (PROP ≈24–25 V, set with the propulsion
    owner) and packs that launch full.
11. §10 **Confirmed (already in the repo):** the GNSS antenna is external on
    SMA (J4501); the radio has its own SMA (J4601). The av-bay design has to
    take both antennas and their cables. The GNSS antenna is passive and
    Burrito has no bias circuit for an active one, so keep that coax short. The
    two SMA ports are identical and can be swapped: label or key the cables.
12. §7 **Open:** do Burrito's three event servos need position evidence too? No
    flight pins are spare after the FDCAN2 move.
13. §13 **Context (Seán):** a Waterloo-style design sheet, every number in one
    place with one owner per value; its avionics tab gives the av-bay designer
    board models, mounting holes, orientation and battery sizes. For Ogma2:
    the sheet owns the vehicle-interface numbers (outlines, holes, masses, pack
    sizes, panel layout) and the repo links to it, so no value lives in two
    places.
14. §7, §5 **Proposed (Seán), answers 12 if needed:** expose the monitor I²C
    (I²C4, PB8/PB9, 100 kHz, already carrying Churro's INA228 0x41 and ADS1115
    0x48 and Croí's INA228 0x40) at a connector on Burrito, and plug angle
    sensors into it. Notes:
    - Costs no MCU pins, and the bus already leaves the board to Churro through
      a TCA4307, designed so a stuck bus leaves readings unknown and protection
      unaffected.
    - Shared fate: a shorted or stuck sensor harness would also blind Churro's
      monitoring (pack voltage, live source, PROP current), which pad telemetry
      depends on. So the port gets its own TCA4307, ESD protection and a
      current-limited 3.3 V feed.
    - Three sensors need three addresses other than 0x40, 0x41 and 0x48: pick a
      sensor with selectable addresses and a PWM output too (AS5048B to check),
      so one angle board also serves Fajita and the active board on plain pins.
    - I²C is a board-level bus: fine inside the av-bay, wrong for a run to the
      fins or the nose.
    - Serves Burrito's own servos only. The active board still reads its fin
      angles locally, at loop rate.
    - Decides it: whether Burrito's servos need evidence (12), and where they
      sit.

## Parked for other boards

Not for tonight; kept so nothing is lost.

- **Servo position sensing on Fajita and the active board (Seán):** without it
  there's no evidence of actual servo position. Proposed: one tiny Hall-effect
  angle board reused on both, with no MCU: a magnetic angle sensor IC and a
  diametric magnet on the driven shaft (valve stem or fin, not the servo horn),
  PWM or analogue out on three wires to the board that drives that servo, read
  on a timer or ADC pin. Not a CAN node per sensor: the active board's loop
  needs fin angle at loop rate (D-2Nov.9 keeps that off CAN), and each node
  would add an MCU, regulator, transceiver, firmware and ID for a three-wire
  signal. Candidates to check: AS5048A, AS5600. Fajita's requirements capture
  is a couple of months out.

Context, stated by Seán on 5 November: close Burrito and Churro first, made and
tested as soon as possible (agreed with Jay, Anav and Arnav). The other boards
start from scratch with the team, using Ogma2 as the template.

## Pass 1

## Pass 2

## Pass 3

## To record at the end

- [ ] `decisions.md`: rows for every **Decided tonight** entry; close or update
      the Open rows they answer (third CAN node, pyro over CAN if closed).
- [ ] `current-system.md`, the affected chapters, the capture spec, the
      firmware interface, the power contract and the propulsion boundary.
- [ ] `project-log.md` entry for the sweep.
- [ ] One commit on PR #2 after Seán's go-ahead; then `python3 render.py`.
