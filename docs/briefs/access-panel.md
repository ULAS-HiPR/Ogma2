# Access panel brief

**Status, 19 November 2026, amended 20 and 21 November: requirements for the access-panel subproject.**
Decided items cite their decision; the rest is proposed.

One panel, low on the vehicle and opposite the rail, reachable from the ground
without a ladder: everything the pad crew touches (EuRoC LV-0260–0280, 0310,
0540–0550). On Ériú (IREC) it sits on the av-bay itself, reached from ESRA's
stepladders (DTEG 6.15.6, D-24Nov.17).

## What it holds

| Item | Requirement |
| --- | --- |
| Recovery and staging arm switches | Maintained, rated above their fuses at 8.4 V DC, operable from outside the airframe. Proposed: screw or key switches, not toggles, so vibration can't move them. Burrito reports each arm sense |
| Their plugs at Burrito (J6101, J6102) | Decided D-21Nov.12: recovery Molex Mini-Fit Jr. 2-circuit (39281023 header), staging JST VH 2-pin (B2P-VH header), two families so they can't swap. Neither mates J701 (Micro-Fit, raw 6S), the Micro-Fit enable loops or J101's Nano-Fit; confirm with real housings |
| The active board's arm key | In Churro's ACT branch, in series (D-21Nov.1) |
| The CATS Vega's switch, and its cell if batteries must be reachable | EuRoC LV-0310, 0470 |
| Enable loops for Burrito and Churro (AV, PROP) | Micro-Fit 3.0 2-circuit (D-22Nov.18; was Gecko, D-19Nov.5) |
| The umbilical | A keyed positive-lock plug on Churro that can't take the 6S plug (proposed: Nano-Fit 4-way), and at the skin a pull-away that releases at Go (proposed: a magnetic breakaway or a lanyard-pulled power connector). Part chosen with propulsion once the pad currents and who pulls it are known (D-2Nov.7) |
| USB-C service | Burrito's, by an extension from J4401, for the configurator and test mode (D-24Nov.18). Salsa's and Fajita's stay at the av-bay. Nothing is flashed on the rail: the running firmware's USB writes settings only (D-21Nov.4, D-24Nov.18). Capped in flight |
| Cornstar's screw switch (IREC) | Not on our panel: it sits at the nose with its own access hole, and Cornstar has no wires to Ogma |
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
