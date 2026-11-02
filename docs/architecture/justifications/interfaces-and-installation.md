# Interfaces and installation

Proposed board and assembly envelope, 22 September 2026, updated for D-6.1,
D-6.7, D-7.1, D-2Nov.8, D-2Nov.9 and D-2Nov.11. Not qualified vehicle hardware. See [connectors](../09-connectors-arming.md),
[servos](../04-servos.md) and [RF](../06-gnss-radio.md).

## Three local PWM interfaces; no speculative remote node

**What stays.** Three servos are a core requirement (D-7.1): PC6 / PC7 on TIM3,
PD10 on LPTIM2, the TXU0304PWR buffer, a TPS70933DBVR for the buffer-side 3.3 V,
and the ten-contact Micro-Fit. Service power enable moves to PE8.

- Servos 1 and 2 share TIM3, so they share one period; a mechanism profile picks
  compatible pulse limits and rate. Servo 3 on LPTIM2 has its own period.
- Bring up with an inert receiver or load. No pulse width is a universal safe
  position, and none implies the actuator behaves on its own.

**What the interface is.** A **raw-2S, 3.3 V PWM interface** for actuators rated
across the installed source range up to 8.4 V.

- Normal combined motor allocation: **1.5 A**.
- Limit: the existing TPS1H100BQPWPRQ1 with R6802 1.24 kΩ 1%, ≈1.989 A nominal.
  TI's ±14% external-limit accuracy plus resistor tolerance gives about
  1.69–2.29 A under the datasheet overload conditions. That doesn't say exactly
  where limiting starts near a normal load.
- A motor needing more current or another voltage needs a new power interface.
  All three share the limit. The board doesn't promise even two arbitrary
  servos stalled at once.

**Power feed (D-6.1, D-6.7, 6 October).** Servo energy comes from `ENERGY_TAP`
through its own fuse F6801. R6804 is fitted and `SERVO_VBAT` gets ≥220 µF.
Servos are not behind the pyro arm. One motor fault can still take out the
shared motor branch. Churro-fed, regeneration can't return to the pack through
the ideal diodes (D-2Nov.5, D-2Nov.7), so the bulk and the logic load absorb it.
Regeneration, stall, startup and temperature need tests with the installed load.
The switch is not a regulated motor supply and doesn't tolerate every kind of
regeneration. This bounded interface is enough to capture the schematic without
inventing a mechanism.

**No remote node on Burrito.** Local PWM is Burrito's only actuator interface,
for bounded, event-triggered moves. Don't add a remote actuator node,
controller, expander or connector to Burrito. Fajita keeps its own local
control. A mechanism that moves the vehicle in a closed loop (roll control, grid
fins) gets its own node under D-2Nov.8: its own processor and fast sensor, a
neutral path that survives hung firmware, dormant until authorised, an
unterminated CAN stub with IDs that lose arbitration to Burrito's and Fajita's
(numerically higher), and its own fused Churro feed. Its board waits for Sim
Systems' requirements. The 200 Hz traffic example doesn't create that
architecture.

Sources: [TI TPS1H100-Q1 Rev D](https://www.ti.com/lit/ds/symlink/tps1h100-q1.pdf)
§6.5 with its accuracy footnotes, and §7.3;
[earlier interface rationale](../../archive/architecture/implementation-reference/04-servos.md).

## CAN: capture the hardware now, change both nodes together

Keep the TCAN3413DRBR, TXU0304PWR, FDCAN pins, the three-contact GH and the
linear trunk terminated only at its two ends.

- **Commission at the existing 500 kbit/s Classical CAN contract.**
- 500 kbit/s arbitration with 2 Mbit/s FD data is a proposed firmware change
  made on both nodes together. Drawing the FD-capable hardware doesn't depend
  on it. No automatic protocol switching, no extra node.
- Peer identity and version, freshness, reboot epoch and bus errors must be
  visible.
- Each node owns its own behaviour when the link drops. A guessed actuator
  command is never the fallback.
- What CAN carries (D-2Nov.9): permissions and mode, slow state that survives
  Burrito's worst-case 550 ms restart, health, and commands the receiver drops
  to safe when stale. No sensor streams or control loops at loop rate.
- Keeping the hardware doesn't make the provisional FD traffic table a
  closed-loop deadline. See the
  [controlled boundary](../../../interfaces/ogma-foinse-propulsion-boundary.md).

## Source variants and harness construction

| Assembly | Fit | Physically absent |
| --- | --- | --- |
| Standalone Burrito | J101 battery, J103 external FC enable | J102 source connector |
| Churro-fed Burrito | J102, with the closed J103 enable plug kept | J101 battery connector |
| Churro | Separate AV and PROP source connectors, maintained source controls | Any link joining the pack positives |

- Keep the schematic pin assignments. Record the variants in the BOM and
  assembly drawing.
- Both source footprints can stay in CAD. Both source connectors can't be fitted
  on one flight assembly.
- A reversible development adapter is its own labelled configuration, not the
  default flight variant.

**Nano-Fit.** Keep Molex 1053111102. Mate: 1053071202 housing with 1053002100
tin female contacts for 20–22 AWG. Use 20 AWG for this harness and check the
insulation fits the contact. The
[105311 sales drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/105/105311/1053111102_sd.pdf)
gives the two-circuit row A / B / C as 8.66 / 5.94 / 6.84 mm. Those aren't pad
coordinates. Build the project-local footprint from the **connector-side PCB
view**: every hole, tolerance, key and pin one. Check it against the drawing and a
1:1 print. Don't substitute the different 105309 family. The current empty
reservation is not a final footprint.

**Other connectors.** Keep the existing
[Micro-Fit and GH mating list](../../archive/connector-servo-readiness-revision-2026-09-07.md#connectors).

- Servo housing 430251000: 1/2/3, 4/5/6 and 7/8/9 PWR/PWM/GND; 10 unwired.
- Temperature housing GHR-04V-S: AV / GND / PROP / GND.
- Pyro arms J6101 (recovery) and J6102 (staging): 2-contact each. They
  must not mate each other, Churro J701 (Micro-Fit 430450200, raw 6S PROP) or the
  GH enable loops. Parts chosen at capture.
- Every drawing says whether it shows the board, the mating face or the wire
  entry. Contacts follow the actual wire gauge; a family name alone isn't a
  harness.

**Leads that could swap.** The repeated GH enables and the two SMA ports can
physically swap. Inside the closed bay, use captured leads, fixed routing and
mechanical retention; only the intended external service end is normally
reachable. Installation acceptance must show each retained lead can't reach the
wrong port without undoing its restraint. Labels help but are not the only
control. Lead lengths follow placement and bay geometry; choosing the electrical
interface needs no invented vehicle dimensions.

## RF reference assembly

Keep **passive GNSS**, 50 Ω SMA ports and no active-antenna bias.

- Board commissioning: **Taoglas TFX125.B** multiband passive GNSS on a short
  50 Ω SMA male-to-male coax, and **Taoglas TI.18.3113** 868 MHz dipole as the
  reference radio antenna.
- These are test assemblies, not vehicle mounts. They're too big to assume they
  fit the flight bay.
- Mount antennas outside carbon. Support antenna and coax weight mechanically,
  not on a PCB SMA.
- A flight antenna must keep impedance and band, the passive bias requirement,
  connector polarity and the measured link budget.

First interoperability peer: a second Wio-LR2021 of the same band and module
variant. That's a concrete target without assuming the existing groundstation
firmware supports the LR2021. Groundstation integration is a separate test. No
permission to radiate on any frequency or power is implied.

Rejected: the FW.86 monopole. Its data assumes a 30 × 30 cm ground plane, which a
small vehicle doesn't have. Choosing a dipole reference says nothing about the
installed radiation pattern.

Sources: [TFX125.B](https://www.taoglas.com/datasheets/TFX125.B.pdf),
[TI.18.3113](https://www.taoglas.com/product/ti-18-868mhz-terminal-antenna-smam-hinged/),
[FW.86 ground-plane data](https://www.taoglas.com/datasheets/FW.86.B.SMA.M.pdf).

## Placement handoff

After Seán approves the schematic, **Codex captures and places; Seán routes.**

- Provisional canvases: Burrito 80 × 230 mm, Churro 60 × 80 mm, four layers,
  1.6 mm thick. Keep existing mechanical constraints and inspect manual
  placements before moving them. An outline or mount change needs a reviewed
  delta, not silent regeneration.
- Connectors placed for access and mating clearance. Separate supports carry the
  Samtec pair's mechanical load.
- Decoupling at its assigned supply pins. Short crystal loops. Flight LSE and
  PC13 kept quiet.
- Regulator and switch thermal pads get usable copper. Keep pressure sensors
  away from heat, board edges, restraints and blocked vents.
- Sensor axes defined in board coordinates.
- RF parts on a short 50 Ω route with continuous reference to their own SMA.
  Switching-current loops kept away from RF, clocks and pressure sensing.
- Magnetometer at the top end of Burrito, ≥20 mm from the GNSS receiver and as
  far as the board allows from power entry, the buck, the outputs and the servo
  connector; no current-carrying copper under it on any layer and no steel
  fasteners nearby ([layout guide](../../pcb-layout-guide.md#c09a-magnetometer)).
  Record its axes in board coordinates like the other sensors.

Deliverable: an unrouted board with every footprint, pad and net mapping
reconciled; courtyards and access checked; keepouts and net classes defined;
BOM variants; and placement notes naming the critical routes. Placement is
reviewed before Seán spends time routing. Routing, fabrication and flight are
separate approvals. See the [layout guide](../../pcb-layout-guide.md) and the
makers' guides it links. An unbuilt placement is not electrically qualified.
