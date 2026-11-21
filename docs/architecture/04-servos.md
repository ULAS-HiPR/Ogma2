# 04 Servos

**Burrito has no servo outputs, from 19 November ([D-19Nov.2](../../decisions.md)).**
Nothing on the EuRoC vehicle needs them: closed-loop actuation lives on the
active board, and a one-off move uses a pyro channel or the payload's own
electronics. Removed from the capture: F6801, U6802, U6803, U6804, R6606 /
R6607, R6804, J6602, and the servo bulk with its DNP footprint. The freed pins
PC6, PC7, PD10, PB0 and PA3 become test pads, two of them with jobs: a timing
strobe and a reset memory (D-19Nov.3). The September three-channel design
(D-7.1, D3) stays in the repository history and the
[archive](../archive/connector-servo-readiness-revision-2026-09-07.md).

What went with it: the servo back-drive and regeneration test (D-2Nov.5,
D-2Nov.17), and about 2 A of Churro's AV budget, which leaves room for paired
e-matches (D-19Nov.8).

## Closed-loop actuators go on their own node

Burrito doesn't run actuator loops. Roll control and the grid fins are one
module below the recovery bay (Radion, 8 November; all-hands, 18 November),
driven by one active board (D-19Nov.6): two cold-gas solenoids (Jay), four fin
servos and a lock servo. The board follows the D-2Nov.8 rules:

- its own processor and its own fast sensors: a gyro for roll and its own
  magnetometer (D-5Nov.1);
- goes to neutral on stop, abort or stale authorisation, through a path that
  survives hung firmware: a servo that loses power holds position, and a hung
  timer keeps sending its last pulse, so neither is a neutral path on its own;
- acts only on a fresh Active from Burrito: Safe, Active or Abort with a counter
  at 10–20 Hz, Active only after the field-adjustable boost dormancy (D-5Nov.2,
  EuRoC LV-0680);
- its own CAN bus from Burrito, bus 2 on FDCAN2, so Fajita never sees it
  (D-5Nov.3), with Gecko at both ends (D-18Nov.4);
- actuator power from Churro's ACT branch, through its arm key at the access
  panel, with local bulk and its own conversion to its actuators' voltages
  (D-21Nov.1); never power from Burrito; its own USB-C, at the av-bay
  (D-19Nov.9, D-21Nov.4);
- at IREC, Ériú's nose canards too, their leads crossing the nose joint through
  a breakaway; unpowered surfaces sit neutral by mechanical centring (D-21Nov.7).

Burrito sends it the authority message and slow state, and logs the health it
reports. CAN carries nothing a loop depends on at loop rate (D-2Nov.9). The
board is designed from its requirements with the build group from 19 November.

## Capture

Remove the servo block and add the test pads per the
[capture delta](schematic-capture-spec.md#servos-removed-and-the-freed-pins).
The service-power enable stays on PE8.
