# Access panel brief

**Status, 19 November 2026, amended 20 and 21 November: requirements for the access-panel subproject.**
Decided items cite their decision; the rest is proposed.

One panel, low on the vehicle and opposite the rail, reachable from the ground
without a ladder: everything the pad crew touches (EuRoC LV-0260–0280, 0310,
0540–0550).

## What it holds

| Item | Requirement |
| --- | --- |
| Recovery and staging arm switches | Maintained, rated above their fuses at 8.4 V DC, operable from outside the airframe. Proposed: screw or key switches, not toggles, so vibration can't move them. Burrito reports each arm sense |
| Their plugs at Burrito (J6101, J6102) | Proposed: single-row Micro-Fit 3.0, recovery 2-way, staging 3-way with one empty cavity, so they can't swap. Must not mate J701 (Micro-Fit 2-way, raw 6S) or the Gecko enable loops; confirm with real housings |
| The active board's arm key | In Churro's ACT branch, in series (D-21Nov.1) |
| The CATS Vega's switch, and its cell if batteries must be reachable | EuRoC LV-0310, 0470 |
| Enable loops for Burrito and Churro (AV, PROP) | Gecko 2-contact (D-19Nov.5) |
| The umbilical | A keyed positive-lock plug on Churro that can't take the 6S plug (proposed: Nano-Fit 4-way), and at the skin a pull-away that releases at Go (proposed: a magnetic breakaway or a lanyard-pulled power connector). Part chosen with propulsion once the pad currents and who pulls it are known (D-2Nov.7) |
| USB-C service | Not on the panel. The ports stay at the av-bay; nothing is flashed on the rail (D-21Nov.4) |
| The COTS GPS tracker's switch (IREC) | Switched and powered on its own (IREC DTEG 4.2.3), unless the CATS Vega counts as the tracker |
| Labels | On every switch, plug and port. Burrito's two SMA antenna plugs are identical: label or key them in the av-bay |

## Rules

- Keyed, shrouded, positive-lock connectors; the skin pull-away is the one
  release by design.
- Every harness: a cavity-numbered drawing, wire and contact, retention, strain
  relief, and a tug test (LV-0490). The panel is low and the av-bay sits above
  the tanks, and Jay wants no raceways, so the panel runs go through the tank
  downcomer: PTFE wire (LV-0500), with a connector at every joint they cross.
- The arm switches carry pyro energy (D-6.1). All-fire is checked at minimum
  battery through the real panel loop (D-21Nov.5).
- The packs stay inside and charge through the umbilical (D-20Nov.1); no battery hatch.
- The sounder beeps continuity and state at arming (D-19Nov.4), so the crew hears
  go or no-go at the panel.

## Open

Switch and plug parts; the panel's position and height; the downcomer route and
harness length; how the umbilical is pulled; its charging contacts (D-21Nov.2).
