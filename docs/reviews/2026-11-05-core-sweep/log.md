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
