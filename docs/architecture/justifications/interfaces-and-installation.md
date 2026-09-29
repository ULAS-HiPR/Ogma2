# Interfaces and installation — recommendation

22 September 2026. Proposed board/assembly envelope; not qualified vehicle hardware.
[Connectors](../09-connectors-arming.md) · [Servos](../04-servos.md) · [RF](../06-gnss-radio.md).

## Two local PWM interfaces; no speculative remote node

Retain PC6/PC7 TIM3, TXU0304PWR, TPS70933DBVR for buffer-side 3.3 V and the
ten-contact Micro-Fit. Remove channel 3; allocate PD10 to service power enable.
The two timer channels share a period. A mechanism profile chooses compatible
pulse limits/rate; software cannot independently set two periods on TIM3.
Use an inert receiver/load for electrical bring-up; no universal safe position
or autonomous actuator behavior is asserted by a pulse width.

Define this board revision as a **raw-2S, 3.3 V PWM interface**, accepting only
actuators specified across the installed source range up to 8.4 V. The normal
combined motor allocation is **1.5 A**, with the retained TPS1H100BQPWPRQ1 and
R6802 1.24 kΩ, 1% (~1.989 A nominal limit). TI's ±14% external-limit accuracy
and resistor tolerance imply ~1.69–2.29 A under the specified overload conditions;
they do not guarantee the exact onset of limiting near a normal load. A motor
requiring more current or a different voltage needs a separate power-interface
revision. The board does not promise two arbitrary servos at simultaneous stall.

R6804 remains DNP. No motor energy or shared energetic-arm arrangement is enabled
by this recommendation. One motor fault can remove the common motor branch.
Motor regeneration, stall/startup and temperature require installed-load tests;
the switch is not a regulated or universally regeneration-tolerant motor supply.
This bounded interface permits schematic capture without inventing a mechanism.

Retain **local PWM as the board baseline**. Do not add a remote actuator node,
controller, expander or connector. Fajita retains its independent local control.
If a future mechanism requires a remote loop, its command age, local feedback
and loss behavior become a separate peer contract; the 200 Hz traffic example
does not silently establish that architecture.

Source: [TI TPS1H100-Q1 Rev D](https://www.ti.com/lit/ds/symlink/tps1h100-q1.pdf),
§6.5 including accuracy footnotes and §7.3; [existing interface rationale](../implementation-reference/04-servos.md).

## CAN: capture hardware now, migrate both peers together

Retain TCAN3413DRBR, TXU0304PWR, FDCAN pins, three-contact GH and the linear
trunk with termination only at its two ends. **Commission at the existing
500 kbit/s Classical CAN contract.** The 500 kbit/s arbitration / 2 Mbit/s FD
profile is a proposed coordinated firmware migration, not a condition for drawing
this FD-capable physical interface. No automatic protocol switching or extra node.

Peer identity/version, freshness, reboot epoch and bus errors must be observable.
Each peer owns behavior through link loss; no guessed actuator command is a
substitute. Retaining hardware does not accept the provisional FD traffic table
as a closed-loop deadline. [Controlled boundary](../../../interfaces/ogma-foinse-propulsion-boundary.md).

## Source variants and harness construction

| Assembly | Populate | Physically unavailable |
| --- | --- | --- |
| Standalone Burrito | J101 battery, J103 external FC enable | J102 source connector |
| Churro-fed Burrito | J102, retained closed J103 enable plug | J101 battery connector |
| Churro | Both distinct AV/PROP source connectors, maintained source controls | Any link joining pack positives |

Keep schematic pin assignments; record population variants in the BOM and
assembly drawing. Both source footprints may remain in CAD, but both source
connectors may not be installed on one flight assembly. A reversible development
adapter is a separately labelled configuration, not the default flight variant.

**Nano-Fit:** retain Molex 1053111102; mate 1053071202 with 1053002100 tin female
contacts for 20–22 AWG. Select 20 AWG for this source harness; verify insulation
fits the contact. The exact [105311 sales drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/105/105311/1053111102_sd.pdf)
has now been located: two-circuit row A/B/C = 8.66/5.94/6.84 mm. Those dimensions
are not pad coordinates. Create the project-local footprint from the **connector-side
PCB view**, all holes, tolerances, keying and pin-one; independently check it against
the drawing and a 1:1 print. Do not substitute the different 105309 family.
The existing empty reservation is not an acceptable final footprint.

Keep existing [Micro-Fit/GH mating inventory](../../connector-servo-readiness-revision-2026-09-07.md#connectors).
Servo housing 430251000: 1/2/3 PWR/PWM/GND, 4/5/6 PWR/PWM/GND; 7–10 unwired.
Temperature housing GHR-04V-S: AV/GND/PROP/GND. Every drawing states whether it
shows the board, mating face or wire-entry view. Contact selection follows actual
wire gauge; a family name alone is not a complete harness.

Repeated GH enables and the two SMA ports remain physically interchangeable.
Use captured leads, fixed routing and mechanical retention inside the closed bay;
only the intended external service end is routinely accessible. Installation
acceptance must demonstrate each retained lead cannot reach the wrong port without
undoing its restraint. Labels are additional evidence, not the sole control.
Exact lead lengths follow placement and bay geometry; no fabricated vehicle
dimensions are needed to choose the electrical interface.

## RF reference assembly

Keep **passive GNSS**, 50 Ω SMA ports and no active-antenna bias supply. For
board commissioning, use **Taoglas TFX125.B** multiband passive GNSS with a short
50 Ω SMA-male/male coax, and **Taoglas TI.18.3113** 868 MHz dipole as a supported
reference radio antenna. These are reference test assemblies, not selected
vehicle mounts. Their size alone precludes assuming they fit the flight bay.
Mount antennas outside carbon; support antenna/coax mass mechanically rather
than loading a PCB SMA. Flight antenna substitution preserves impedance/band,
passive bias requirement, connector polarity and the measured link budget.

Use a second Wio-LR2021 of the same band/module variant as the first controlled
interoperability peer. That gives a concrete test target without assuming the
existing groundstation firmware supports LR2021. Groundstation integration is a
separate compatibility test. No radiated frequency/power permission is inferred.

The alternative FW.86 monopole specifies a 30 × 30 cm reference ground plane;
that makes its advertised performance a poor unqualified assumption for a small
vehicle. Choosing a dipole reference does not establish installed radiation pattern.

Sources: [TFX125.B](https://www.taoglas.com/datasheets/TFX125.B.pdf),
[TI.18.3113](https://www.taoglas.com/product/ti-18-868mhz-terminal-antenna-smam-hinged/),
[FW.86 reference-plane data](https://www.taoglas.com/datasheets/FW.86.B.SMA.M.pdf).

## Placement handoff

After Seán's schematic green light, **Codex captures and places; Seán routes**.
Use the retained Burrito 80 × 230 mm and Churro 60 × 80 mm outlines, four layers,
1.6 mm board thickness as provisional canvases. Preserve existing mechanical
constraints and inspect manual placements before changing them. A necessary
outline/mount change needs an explicit reviewed delta, not silent regeneration.

Place connectors for access and mating clearance; independent supports carry
the Samtec pair's mechanical load. Keep decoupling at its assigned supply pins,
crystal loops short and flight LSE/PC13 quiet. Give regulator/switch thermal pads
usable copper access; don't crowd pressure sensors against heat sources, board
edges, restraints or blocked vents. Establish sensor axes in board coordinates.
Place RF parts along a short continuous-reference 50 Ω route to their own SMA;
keep switching-current loops away from RF, clocks and pressure measurement.

Deliver an unrouted board with all footprint/pad/net mappings reconciled,
courtyards/access checked, keepouts and net classes defined, BOM variants, and
placement notes identifying the critical routing paths. Placement is reviewed
before Seán invests in routing. Routing/fabrication/mission release are separate.
See the [existing layout guide](../../pcb-layout-guide.md) and linked manufacturer
guides; this document does not claim an unbuilt placement is electrically qualified.
