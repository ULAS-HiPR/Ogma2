# Ogma 2 current architecture

Updated: 2026-09-05
Status: architecture checkpoint before schematic capture
Scope: Ogma 2 as HiPR's workhorse competition flight computer, its bounded Kármán-line mission, its power boundary with Foinse 2, and its interface to a future liquid-propulsion controller

This is the current working picture assembled from the Ogma Rev 1 evidence, the portfolio closure, the design references in this directory, the Seán/Anav discussions from 17 August–3 September 2026, and the 29 August CATS Vega/Fluctus field-integration evidence. No Ogma 2 schematic or PCB exists yet. Where the discussion moved faster than the evidence, this document says so.

The 5 September update reconciles only the test-stand relationship with the LTS
decisions of 3–4 September. Ogma's flight architecture, power authority and
full-rate flight-recording requirements are unchanged.

Ogma 2 is intended to be HiPR's workhorse flight computer: the same maintained board for ordinary competition and development launches across solid, hybrid, liquid, single-stage, and multistage vehicles, through the eventual space-shot mission. Ogma 3 should be a corrective refinement, not the release that finally adds an essential Ogma 2 function. This is a design target, not a present capability claim. Here, “space shot” means one bounded suborbital sortie that reaches at least 100 km near apogee, returns through descent and recovery, and preserves local evidence. It does not mean orbital insertion or unattended operation for months or years. Rev A uses the accepted provisional platform envelope below. Exact vehicle trajectories and environments arrive later from simulation and measurement; they replace provisional values before mission qualification but do not block initial component selection or schematic work.

Status words used below:

- **Decided**: explicitly chosen for the current architecture.
- **Required**: follows from Rev 1 evidence, safety, or the reason for an architectural split.
- **Working direction**: strongly favoured, but still needs a part, circuit, interface, or test decision.
- **Open**: not settled.
- **Rejected or superseded**: considered and removed from the baseline.

A separate [5 September reliability review](docs/reliability-design-review.md)
and [execution plan](docs/reliability-execution-plan.md) deepen the unresolved
design and provide bounded work packages, proposed gates, and test criteria.
Their creation is authorised; their new circuit and flight-policy proposals
are not automatically accepted architecture. No Ogma 2 bench result is claimed.
The existing provisional envelope and MCU-less Foinse boundary are unchanged.

## The current design in one paragraph

Ogma 2 is one compact, four-layer, double-sided workhorse flight-computer PCB. A change of rocket should normally change the typed mission profile, harness, Foinse configuration, and qualification evidence rather than the Ogma PCB. It has two MCUs connected over UART. The flight MCU owns sensing, estimation, flight state, local logging, three pyro channels, and two servo channels. The communications MCU owns GNSS, LoRa, telemetry buffering, and normal USB-C access. The second MCU provides timing and failure containment; it is not compute redundancy. CAN leaves the board only for named independent vehicle systems. The only current example is the liquid-propulsion controller. Ogma does not become a general power distributor. Foinse 2 is a separate, MCU-less, vehicle-specific power interface. A payload such as Mu remains separate and independently powered. The liquid-propulsion controller is a self-governing peer with local sensing, actuation, redline logic, abort authority, power protection, and logging. Electronics owns the functional integration of the complete avionics bay. The installed assembly is qualified, closed, and then left undisturbed; routine e-match replacement, configuration, readback, log extraction, and charging use deliberate external service boundaries.

## Governing rule

“The genius is in the simplicity” is the governing acceptance principle. Delete every repeated function and speculative interface unless it buys a named capability, measurable safety boundary, or testable form of fault containment. Simplicity does not remove required protection or evidence; it removes ways for the system to be ambiguous, fragile, or difficult to operate.

Rev 1 was electrically parallel on shared power and CAN, but functionally serial. Each board performed a unique required job. Losing a required node removed that function. Splitting the system across five MCUs, five firmware targets, repeated regulators, repeated CAN interfaces, repeated connectors, and repeated configuration did not create useful redundancy. It created more integration surfaces.

Consolidation removes those surfaces. It also removes some physical isolation, so the electrical boundaries that matter must be designed deliberately inside the new system: separate power domains, bounded interfaces, safe output states, branch isolation, layout separation, current limiting, and direct observability.

The deletion test for every proposed part, connector, board, MCU, protocol, and software layer is:

1. Which named mission needs it?
2. What fails if it is absent?
3. Does it need local autonomy or hard local timing?
4. Can the requirement be met with a simpler local peripheral or a bounded signal?
5. Does adding it create another power path, firmware target, protocol contract, programming step, or mechanical interface?
6. How will it be isolated, measured, tested, and removed if it fails?
7. Can the installed system still be seen, reached, disconnected, and diagnosed without dismantling unrelated hardware?
8. Does normal use require a special cable, virtual machine, network account, or undocumented operator knowledge?

If those questions do not produce a concrete answer, delete it.

## Workhorse platform and bounded Kármán-line mission

**Decided.** Ogma 2 is the default HiPR flight-computer platform for ordinary competition and development launches. The baseline covers 3–9 km competition flights and solid, hybrid, liquid, single-stage, and multistage vehicles. This does not create a generic expansion platform: every populated interface still needs a named mission function and failure boundary.

**Decided.** The Ogma 2 space-shot target is one suborbital flight: power up, wait for a bounded period, launch, survive ascent and any staging, reach at least 100 km near apogee, descend, execute recovery, land, and retain enough local data to establish what happened.

The baseline does not include orbital insertion, six-month or multi-year autonomy, repeated radiation-belt passage, long-term total-dose accumulation, orbital thermal cycling, autonomous on-orbit repair, or reuse without post-flight inspection. Those are different reliability problems and would reopen the architecture.

**Required.** Mission duration is a first-order design input. Nanosecond transients, second-scale resets, a minutes-long near-vacuum coast, hours of pad/recovery operation, and years in orbit require different protection and qualification. Reaching the Kármán line is a geometry target; it is not itself an electronic qualification class.

**Decided provisional envelope.** These are design budgets for Rev A, not predictions of a particular rocket:

| Dimension | Provisional platform value |
| --- | --- |
| Normal mission set | 3–9 km competition flights; solid, hybrid, liquid; single-stage or multistage |
| Extreme mission | One short-duration flight to at least 100 km followed by recovery |
| Powered operation | 8 hours through bench/pad wait and flight |
| Recovery reserve | A further 4 hours of reduced-duty beacon and log protection |
| Full-rate flight record | At least 30 minutes |
| Supported service period | 5 years, subject to inspection, maintenance, and storage controls |
| Reuse | 25 inspected flight cycles; acceptance test after every flight |
| Powered electronics temperature | −20 to +70 °C |
| Component temperature grade | Prefer at least −40 to +85 °C |
| Ambient-pressure survival | Sea-level pressure down to approximately 0.01 Pa; sensor validity is separate |
| Acceleration measurement | Separate ±200 g channel |
| Board structural design case | 50 g quasi-static |
| Angular-rate measurement | At least ±2000°/s, with saturation detected and handled |
| Shock screening | 200 g short-duration provisional target; waveform remains open |
| Vibration | No invented qualification spectrum; begin with exploratory sine/random testing, then replace it with vehicle measurement |
| Moisture | Closed-bay rain and splash survival; no exposed-wet-PCB requirement |

These values may select architecture, part classes, sensor ranges, storage size, energy reserve, connector construction, and mechanical margins now. Exact pad wait, trajectory, boost, coast, descent, speed, rotation, temperature, vibration spectrum, shock waveform, RF environment, and recovery duration remain later mission overlays. Simulation and measured flights must replace the provisional values before final mission qualification. A change is recorded explicitly; it does not silently invalidate the platform.

No numerical reliability probability is invented yet. The fault-containment requirements still apply. Whether independent recovery is required for each mission, and the exact coverage it provides, remain open decisions; the hardening study's recommendation must not be read as an accepted blanket requirement. Probability targets may be allocated when vehicle hazards, range rules, and evidence support them.

The separate [`Kármán-line mission hardening report`](docs/karman-line-mission-hardening-report.md) analyses the required changes and candidates. Its technical proposals remain a design study until accepted here.

## Architecture boundary

| System | Owns | Does not own | Current interface |
| --- | --- | --- | --- |
| **Ogma 2 flight MCU** | Sensors, state estimation, flight-state machine, local flight log, three pyro outputs, two servo signals, flight-safe decisions, external vehicle coordination | LoRa stack, GNSS parsing, payload computation, liquid-engine protection, general power distribution | UART to communications MCU; CAN to named independent vehicle systems |
| **Ogma 2 communications MCU** | GNSS, LoRa, telemetry framing and buffering, radio health, USB-facing configuration and log transfer | Recovery decisions, pyro authority, servo policy, liquid-engine authority | UART to flight MCU; RF and GNSS hardware; USB-C |
| **Foinse 2** | Vehicle battery/source interface, charging or rail-charging functions, protected distribution, bounded monitoring, and named actuator-power generation | Flight state, recovery logic, payload logic, propulsion state machine, general computation | Passes `VBAT` to Ogma; receives a protected bounded 3.3 V return for its low-power devices; exact physical and monitoring interface open |
| **Liquid-propulsion controller** | Engine-critical sensing, local control, redlines, main engine actuators, ignition authority, local abort, local full-rate logging | General GSE sequencing, research-only DAQ, Ogma recovery, operator UI | Narrow versioned CAN interface to Ogma; separate power domain |
| **GSE controller** | Fill, drain, purge, vent, pressurisation, facility isolation, stand sequencing | Flight recovery and engine-local protection that must survive loss of GSE | Independent stand network; interface still open |
| **Stand DAQ** | Research-only high-rate acquisition and analysis channels | Safety authority and hard-real-time valve control | High-bandwidth test path and time synchronisation still open |
| **Payloads** | Their own experiment, storage, processing, and normally their own power | Flight-critical decisions | None by default; a narrow data or trigger interface only when a named payload needs it |
| **Avionics-bay integration** | Electronics layout and service boundary for Ogma, Foinse, batteries, harnesses, antennas, connectorised charge assemblies, access, venting, and flight-configuration evidence | Primary airframe structural substantiation or authority belonging to an independent recovery system | Controlled mechanical interface with structures; exact panel, flight-harness connector/feedthrough, vent, and service connectors open |

## Decisions already made

### One main PCB

**Decided.** Croí, Teachtaire, Lámh, and Pléasc do not remain separate flight boards in the baseline. Their flight-computer functions move onto one Ogma 2 PCB. Foinse 2 remains separate because power conversion, charging, and high-current distribution change with the vehicle and deserve their own electrical and physical domain. Ogma itself has no plug-on daughterboard or component-obscuring PCB stack.

This reverses the earlier instinct that a large number of tiny Imperial College London-style boards was the more mature architecture. Our current judgement is that this produces a difficult-to-maintain system with too many connectors, repeated support circuits, programming targets, and hidden dependencies. Imperial's implementation has not been freshly audited for this document, so it is recorded as the team's design conclusion, not as a new external finding.

### Two MCUs on Ogma 2

**Decided.** There are two MCUs on the one PCB:

- **Flight MCU:** sensors, estimation, flight state, local recording, pyro, and servo control.
- **Communications MCU:** LoRa, GNSS, telemetry, and other bursty or third-party protocol work.

They communicate over UART.

The split exists because radio transmission, GNSS acquisition, parsing, and USB-facing work have variable latency. Those tasks should not set the worst-case timing of the flight loop. The two MCUs are not redundant. The communications MCU can fail while the flight MCU continues the mission. The reverse is not true.

Consequences of the split:

- The flight MCU must never wait for the communications MCU.
- Flight-to-comms traffic is bounded, fire-and-forget telemetry.
- Comms-to-flight traffic is a request or configuration proposal. It cannot directly command a recovery action.
- Holding the communications MCU in reset must not interrupt locally owned flight sensing, logging, or essential flight/recovery operation. Loss of GNSS aiding may change estimator accuracy; the permitted degraded capability, uncertainty, and timing bounds must be defined and tested. Numerically identical estimates with and without aiding are not required.
- The UART contract must be versioned, checksummed, generated from one source, and tested at both ends.
- A third MCU for CAN cleanup, recovery, or generic expansion is rejected. Spend the board area and verification effort on sensors, power integrity, observability, and test access instead.

### Three pyro channels

**Decided.** Ogma 2 has three energetic channels:

1. first event in dual deployment;
2. second event in dual deployment;
3. sustainer ignition for a future staged vehicle.

The third channel has a different hazard and permissive set from recovery deployment. The electrical channel may be similar, but the state-machine rules, arming conditions, and test evidence cannot be treated as identical by default.

### Two servo channels

**Decided.** Ogma 2 has two direct servo channels. Three was considered for speculative grid-fin work and dropped from the baseline.

The current direction is to generate servo PWM directly with MCU hardware timers and delete the PCA9685 unless the timer and pin audit proves that impossible. The nominal RC-servo frame is 20 ms, with a nominal 1–2 ms pulse width. Actual endpoints, safe positions, update behaviour, and supply voltage must come from the selected actuators and be measured under load.

### CAN is external and bounded

**Decided.** CAN no longer exists to decompose the flight computer internally. The currently named external peer is the propulsion controller. No CAN expander is planned. CAN cannot be wired as a star. If the vehicle has only Ogma and one propulsion controller, build and terminate a clean two-node line.

Additional CAN nodes require an actual use case and a revised topology and bandwidth budget. A hypothetical future node is not enough reason to add connectors, transceivers, or routing now.

### USB-C and compact physical debug

**Decided.** Ogma 2 uses USB-C for normal configuration, identity/readback, log extraction, and firmware update or recovery where safely supported. Routine field work must not require a virtual machine, internet connection, proprietary adapter, or loose custom lead. The supported host matrix and packaging remain to be specified, but it must include the actual macOS and Windows machines used by the team.

USB does not replace hardware recovery and breakpoints. The physical debug connector will use the compact vertical 2×3 SWD/JTAG-style form factor discussed at Analog, roughly 6 mm × 4 mm, rather than the large 10-pin Cortex header. The required signal set is currently SWD. The exact manufacturer part, mate, pinout, height, and whether each MCU receives its own connector remain open. Independent access to SWDIO, SWCLK, NRST, reference voltage, and ground is required for each MCU, whether that is achieved with two connectors or a fully reviewed selection scheme.

### Double-sided assembly

**Decided.** The PCB will use full double-sided placement. Board area, routing, signal integrity, and the 3-inch vehicle envelope justify it.

**Decided.** Ogma 2 assemblies are ordered as factory PCBAs. Team time goes into architecture, review, fixtures, bring-up, measurement, and qualification rather than routine placement and reflow. In-house work remains useful for rework, bodges, test coupons, and recovery. Every unit still needs serialisation, incoming inspection, first-power checks, and a repeatable fixture.

### Field-wiring connectors

**Decided.** Ogma uses proper shrouded, polarised, positive-lock connectors for battery, CAN, pyro, and servo connections from its first hardware revision. Bare-wire screw, spring, push-button, or lever terminals are not mounted on Ogma. Miniature PCB screw terminals are excluded: their small footprint is a false saving when the operator must manipulate a tool beside exposed conductors and adjacent energetic channels.

**Decided.** Temporary raw-wire connection is a tooling problem. When development, pop tests, or an earlier vehicle require bare servo or e-match leads, a detachable harness or breakout converts the proper Ogma connector to a tool-free terminal. That adapter is replaceable and visibly non-flight hardware. It does not determine the Ogma PCB footprint and is absent from the Kármán flight configuration.

The Kármán path is:

```text
Ogma locking connector -> qualified retained harness -> keyed connectorised servo or charge assembly
```

No raw-wire field terminal is part of that flight path. If an e-match arrives with bare leads, it is terminated away from the vehicle into a controlled replaceable charge assembly, then inspected and tested before installation. Exact termination workmanship and charge-module geometry remain open.

**Working shortlist:**

- **Battery and higher-current paths:** Molex [Nano-Fit](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/nano-fit-connectors) or [Micro-Fit 3.0](https://www.content.molex.com/dxdam/literature/987650-5984.pdf), with the exact header, contacts, wire, TPA/CPA, keying, current derating, and strain relief selected from measured loads.
- **Compact CAN and other low-current harnesses:** Molex [Micro-Lock Plus 2.0](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/micro-lock-plus-connectors) is the strongest current compact candidate. [JST GH](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf) is a smaller signal-only alternative if its AWG 26 wire and installed vibration result are acceptable. [Harwin Gecko](https://www.harwin.com/hri-range/gecko) is the high-reliability Kármán comparison where its cost, tooling, and assembly burden are justified.
- **Temporary raw-wire adapters:** WAGO [MCS MICRO 2712](https://www.wago.com/us/pluggable-pcb-connectors/mcs-micro-2712) is the strongest compact tool-free candidate. WAGO [2601](https://www.wago.com/global/products/electrical-interconnections/discover-pcb-connection/pcb-terminal-blocks-with-levers-2601-series) is the larger-wire alternative on a detachable breakout board.

These are candidates, not selected parts or rocket qualification. Selection must use the real conductor type and gauge, continuous and pulse current, no-fire/all-fire limits, insertion visibility, contact protection, cross-mating prevention, strain relief, vibration, contamination, mating cycle, tooling, and gloved-field workflow. Connector convenience and manufacturer headline ratings do not replace installed testing.

### Avionics-bay service boundary

**Required.** The complete avionics assembly must reach a closed, verified flight-ready state. After its final representative test and configuration readback, routine field work must not require removing either board, unplugging an internal harness, separating bulkheads, or disturbing a qualified mount. Opening the electronics volume or changing an internal item invalidates that state and requires the affected inspection and tests to be repeated.

**Required.** Replaceable e-matches connect at an external service boundary. Ogma's proper board connector feeds a retained internal harness and a mechanically supported bay-wall or external harness connector; the connectorised charge assembly is the replaceable part. Continuity and firing-current evidence must cover the complete installed path. The external interface must prevent casual cross-mating, shorts, conductor pull-out, unobserved partial insertion, and mechanical load reaching the PCB. The exact locking connector remains open. Bare screw, spring, push-button, and lever terminals are excluded from the Kármán flight configuration.

**Required.** The electronics volume is protected from black-powder soot, loose conductive debris, and repeated handling. “Closed” does not mean hermetically sealed. Unless the bay is deliberately qualified as a pressure vessel, it needs a controlled pressure-equalisation path for ascent and descent. Barometer ports and the bay vent must be designed so the pressure measurement remains useful without giving energetic residue a direct path to the electronics.

**Required.** Normal USB-C identity, configuration readback, log extraction, and the Foinse charging interface must remain usable without opening or moving the flight assembly. Raw SWD, invasive probing, component rework, and internal harness changes are maintenance operations; using them invalidates flight-ready closure. A retained removable side or service panel is the working mechanical direction for exceptional access. Its geometry, fasteners, structural role, contamination control, RF effect, and relationship to the vent remain open.

The closure record must identify the bay, boards, batteries, harnesses, firmware, configuration, calibration, connector map, continuity/resistance results, inspection state, and the people who assembled and independently checked it. A witness mark or seal can expose later disturbance, but it does not replace the recorded checks.

### No general payload power from Ogma

**Decided.** Ogma 2 does not expose its logic supply as a general vehicle power bus.

If a subsystem has its own purpose, processor, storage, and failure modes, it is a payload or an independent computer. Mu is the concrete example. Giving it Ogma's logic power would couple a non-flight experiment into the flight computer without making it part of the flight computer.

There are two narrow exceptions worth keeping distinct:

- A directly supported dumb actuator, such as one of the two servos, may receive a dedicated actuator rail through the Ogma connector area. That rail must not come from the 3.3 V logic supply.
- A low-current dumb peripheral may be powered through a deliberately budgeted and protected local interface if a named use case survives design review.

No generic powered-peripheral connector is part of the baseline. The second exception requires a named later use case and a new review.

## Ogma 2 functional breakdown

### Flight MCU

The flight MCU owns the minimum complete flight computer:

- acquire and timestamp the flight-critical sensors;
- validate sensor health and freshness;
- estimate altitude, velocity, orientation, and other required state;
- run the flight-state machine;
- log raw and derived data locally;
- enforce pyro arming, continuity, pulse, and one-shot rules;
- generate two servo signals and enforce their leases and safe states;
- monitor its own rails, reset cause, watchdog, execution timing, and storage health;
- publish a bounded telemetry stream to the communications MCU;
- coordinate with the propulsion controller over a narrow vehicle protocol where required.

It must remain useful with the communications MCU held in reset, the radio absent, GNSS absent, USB disconnected, the display absent, and every optional external interface unused.

### Communications MCU

The communications MCU owns:

- GNSS configuration, parsing, fix state, PPS handling, and health;
- LoRa configuration, packet framing, transmit scheduling, and radio health;
- buffering and down-selection of telemetry supplied by the flight MCU;
- sequence numbers, CRCs, link statistics, and groundstation compatibility;
- USB configuration, profile transfer, identity/readback, firmware service, and post-flight data access.

It does not consume raw unbounded CAN traffic, run the flight-state machine, or decide when to deploy recovery. If propulsion summaries need to reach the ground, the flight MCU should publish an explicitly bounded summary over UART. A third gateway MCU is not justified.

### UART boundary

**Required.** The UART link needs a small generated contract with:

- protocol and message version;
- length and message type;
- monotonic sequence number;
- timestamp source and age;
- CRC;
- bounded maximum frame size;
- defined behaviour on corruption, overflow, reset, stale data, and version mismatch;
- explicit rate budgets for each message;
- no dynamic allocation in the flight-side implementation.

The flight MCU must be able to drop telemetry rather than miss a hard deadline. The communications MCU must expose drop and corruption counters so telemetry loss is visible.

## Sensors and measurement

The early list mixed measurements with component categories: accelerometer, IMU, gyro, barometer, voltage, current, temperature, and air quality. The schematic should begin from measurements and flight decisions instead.

| Measurement | Current status | Notes |
| --- | --- | --- |
| Low-g acceleration and angular rate | **Required** | Usually one IMU. Do not list a separate gyro unless it has an independent role. |
| High-g acceleration | **Working direction** | A separate high-g device is more useful than a third MCU and preserves boost/shock evidence beyond the low-g IMU range. |
| Barometric pressure | **Required for lower flight** | Ordinary board barometers are far outside range near 100 km. The exact part, pressure-port arrangement, transonic strategy, and upper validity limit remain open. Two dissimilar barometers are a candidate only if their failure modes and placement are genuinely independent. |
| GNSS position, velocity, time, PPS | **Required where the selected receiver is valid** | Owned by the communications MCU. PPS activity is not proof of a position fix. Published altitude, velocity, acceleration, and simultaneous operating limits must cover each claimed use. |
| Battery and critical rail voltage | **Required** | Ownership between Ogma and Foinse 2 must be explicit. Ogma still needs enough local evidence to explain its own reset. |
| Current | **Required where diagnostic value is clear** | At minimum logic and actuator domains need useful current evidence. Do not add channels without a fault or decision they can diagnose. |
| Temperature | **Required where it protects or calibrates hardware** | MCU/board, battery, regulator, or sensor temperature may matter. A generic ambient-temperature channel is not automatically useful. |
| Air quality or gas sensing | **Rejected from the baseline** | No flight-state, recovery, or control requirement currently needs it. Rev 1's BME680 also demonstrated the cost of a non-essential device clamping a shared bus. It can return only as a named payload requirement. |

Sensor requirements before part selection:

- physical range and overload survival;
- useful bandwidth and sample rate;
- required accuracy and uncertainty;
- behaviour through boost, transonic flight, descent, shock, and recovery;
- bus ownership and failure isolation;
- startup and self-test evidence;
- calibration method and retained calibration record;
- whether loss causes degraded operation, a state veto, or no mission effect.

Every shared sensor bus needs per-device 0 Ω links or series footprints, labelled test access, and a way to prove which device is holding the bus. A failed optional sensor must not hide the primary IMU, barometer, or logger.

## Logging and reset evidence

Local flight logging remains on the flight side. Telemetry is never the only record.

**Required from Rev 1:**

- append-only records with per-record integrity checks;
- sequence continuity and explicit drop counters;
- valid timestamps in every record;
- reset flags copied before normal startup clears them;
- a short pre-reset fault and power record;
- firmware identity, configuration identity, calibration identity, and board serial in the log header;
- automatic raw groundstation capture from the first received byte;
- host replay of the complete state machine, including reset recovery;
- storage-full, corrupt-record, interrupted-write, and brownout tests.

**Working baseline:** soldered non-volatile storage with USB-C extraction. This deletes a socket, removable medium, retention problem, and field-handling step. Required log volume, write rate, flight duration, retention, endurance, and extraction time must still be calculated before selecting the device. Removable storage returns only if those numbers show that fixed storage cannot meet the mission. USB servicing must not share a path that can stall the flight logger.

## Pyro architecture

Three channels are fixed. Their circuit is not.

### Requirements already supported by Rev 1 evidence

- A physical arming break must interrupt the energetic path. Software alone cannot make a channel armed.
- Firmware must read the real arm state.
- Each channel needs continuity measurement through a hardware-current-limited path.
- All outputs must default off through reset, brownout, watchdog, assert, bootloader entry, and uninitialised GPIO time.
- Firing pulses are finite and one-shot, with an event record.
- The energetic current loop, return path, connector, and local energy storage need deliberate layout and transient control.
- Harness transients must be caught at the connector.
- Continuity and output nodes need direct test access.
- Channel state must remain interpretable without trusting one application-level status bit.

### Circuits considered

- **Rev 1 LTV-817-heavy isolation:** rejected as the default. If pyro and logic share a battery return, phototransistor optocouplers do not isolate the dominant shared-return and harness-transient paths. They add area and an ageing transfer characteristic. If the batteries are truly galvanically separate, isolation remains necessary, but the isolator should be selected for that topology rather than copied from Rev 1.
- **Single low-side FET:** small and common, but a shorted device or one short to structure can have poor single-fault behaviour depending on the rest of the circuit.
- **Two-sided switching:** favoured candidate because the match can float until commanded and one failed-short device need not fire the channel. The high-side implementation, diagnostics, voltage headroom, and failure analysis remain open.
- **Photovoltaic high-side MOSFET drive:** proposed as a compact slow-switching option. It has not been selected or tested.
- **One shared arm/fire circuit with channel selection:** floated during the deletion discussion and not accepted. It needs a fault-tree and must not allow one selector fault to energise the wrong channel.

The power topology must be chosen before the isolation topology. Questions about star return, separate batteries, high-side drive, and galvanic isolation cannot be answered honestly until that is fixed.

Continuity LEDs should be driven by interpreted MCU state rather than placed in the sensing path. If a hardware-only continuity indication is required, specify it separately. Visual status never replaces the physical arm break.

The third channel, intended for sustainer ignition, needs its own staging permissives, inhibit conditions, timing evidence, and range-rule review. Reusing a recovery-channel schematic does not settle those system requirements.

## Servo architecture

Two channels are fixed. The PCA9685 is not.

**Working direction:** remove the PCA9685 and drive both outputs from flight-MCU hardware timers. This deletes an I2C device, a scarce part, a driver, an output-enable failure mode, and another shared-bus dependency.

Before locking that decision:

- audit timer channels, alternate-function pins, DMA/interrupt interactions, and debug-pin conflicts on the selected MCU;
- define the exact output frame, pulse limits, boot state, command timeout, and safe position;
- define how output is physically inhibited during reset and before arming;
- separate servo power from flight logic power;
- measure stalled, startup, and manoeuvre current with the intended actuators;
- qualify motion with the actual mechanism and load;
- add position or witnessed end-state sensing whenever physical movement is a qualification claim.

The flight event system should command an action, not pretend that every deployment is electrically a pyro. A CO₂ deployment mechanism may be triggered at the same logical event as a drogue charge while using a servo output. Event, policy, and electrical actuator should remain separate concepts.

## GNSS and LoRa

### GNSS

GNSS remains on the communications side.

Rev 1's active-antenna path accumulated Q3 pinout trouble, a bodge, and diagnostic complexity that was ultimately bypassed. Ogma 2 should begin with the simplest reviewed u-blox reference path that meets the selected antenna requirement. Keep:

- a reviewed 50 Ω RF path and ground transition;
- antenna-supply test access;
- GNSS UART, reset, and PPS access;
- ESD and protection justified by the connector and installation;
- firmware-visible fix, satellite, signal, parser, and overrun state.

Delete the Rev 1 antenna switching or diagnostic circuit unless a written requirement explains what fault it detects and what the system does with that result. TIMEPULSE blinking must not be presented as a position-fix indication.

The likely MAX-M10S path cannot be the full Kármán-line navigation or proof instrument. Its published operational limits are 80,000 m altitude, 500 m/s velocity, and 4 g. It may remain useful on the pad, in the lower permitted flight envelope, and during recovery. Flight state must tolerate its loss, and proof of at least 100 km needs external range tracking or a receiver explicitly valid for the complete trajectory.

The antenna connector, active antenna, cable length, mounting, and location in the avionics bay remain open. They must be designed with the enclosure rather than after PCB layout.

### LoRa

The radio implementation remains open:

- retain a castellated module;
- place the RF IC and matching network directly on Ogma 2;
- retain SX1272 compatibility or select a newer part.

The decision needs a real comparison of availability, RF review burden, board area, firmware maturity, output power, current, certification constraints, and groundstation compatibility. Rev 1 proved the value of recording the actual fitted radio identity and one checked-in radio profile. That becomes mandatory regardless of the part.

## Power architecture and Foinse 2

### Boundary

Ogma owns flight logic. Foinse 2 owns vehicle power. Keeping those concerns separate does not recreate Rev 1's arbitrary board split because Foinse 2 has a distinct current domain, vehicle-dependent topology, connector set, and qualification campaign.

Current Foinse 2 direction:

- no MCU and no firmware image;
- be the only board directly connected to the vehicle batteries in the integrated configuration;
- pass protected `VBAT` to Ogma;
- use the protected, current-limited 3.3 V returned by Ogma for bounded low-power monitoring or control devices;
- perform only named battery/source management, charging, protection, measurement, and distribution functions;
- generate a vehicle-specific actuator rail only for selected loads with a written voltage and current requirement;
- control inrush, reverse current, source handover, and backfeed where the selected topology requires them;
- expose direct rail, enable, fault, and source-path test access;
- use retained locking connections for high-current outputs;
- keep every monitoring branch isolatable so a failed device cannot clamp an Ogma bus or collapse its flight rail.

Foinse must not become a propulsion controller implemented as analogue glue. Main-engine command authority, redlines, loss-of-link behaviour, and local safe-state enforcement remain on the propulsion controller even when a driver or power stage is physically close to Foinse.

### Standalone and integrated modes

The current concept has two modes:

1. **Standalone Ogma 2:** local battery input, switching preregulation to roughly 3.8 V, then a low-noise 3.3 V LDO for logic.
2. **Integrated vehicle:** Foinse 2 is the battery/source entry, passes `VBAT` to Ogma, and receives a protected bounded 3.3 V return for its low-power devices. Ogma uses the same logic-generation chain in both modes.

Ogma's three pyro channels and two servo channels use the defined `VBAT` domain without another dedicated buck or boost stage on Ogma, subject to the selected loads' voltage and current qualification. The figures above are a working concept, not a finished power specification. Input range, brownout margin, efficiency, dissipation, source priority, reverse current, and regulator parts remain open. Permitted source combinations must be made physically exclusive or protected against contention and backfeed.

### Ogma/Foinse physical connection

The 28 August direction toward a vertically stacked Ogma/Foinse mezzanine is superseded. The Fluctus photographs make the service cost concrete: the upper PCB and two rows of headers conceal the inner faces, constrain probing and rework, and turn separation of one board into disturbance of both. A stacked parallel-board geometry also adds an interconnect and complicates return paths, coupling, power integrity, and EMC analysis. The photographs do not prove that this caused a measured Fluctus fault or noise problem.

Current physical requirements:

- no component-obscuring face-to-face PCB sandwich;
- no exposed 2.54 mm pin-header stack as the flight interconnect;
- both boards remain visible, independently removable, and probeable in the installed avionics fixture;
- USB-C, debug, arm, antenna, and test points remain accessible;
- structural fasteners carry mechanical loads;
- every connector or harness has rated current, return conductors, keying, retention, strain relief, wipe/mating-cycle data, and disturbance tests;
- high-current actuator wiring stays on a separately qualified locking path where appropriate;
- the complete assembly fits the controlled 3-inch envelope.

The exact choice between a side-by-side arrangement, edge connection, and short locking harness remains open. Choose it from the complete power tree, signal-integrity needs, and avionics-bay CAD rather than compact appearance.

## External peripherals, PMOD, and payloads

Several expansion models were considered:

- male GPIO headers;
- ribbon cables carrying logic, power, ground, and CAN;
- one cable for a powered CAN device and another for a simple trigger;
- Arduino-style shields;
- pyro and servo expansion boards;
- camera or image-processing modules;
- PMOD.

None is part of the baseline today.

The current rule is:

- If it is always required for normal flight, integrate it.
- If it needs autonomous control or hard local timing, make it an independent computer with a narrow vehicle interface.
- If it is an experiment, keep it out of the flight-critical memory, buses, and power unless a bounded interface is justified.
- If it only needs a trigger, expose the smallest safe trigger and ground-reference interface.
- If it only needs power, it is not an Ogma module. Power it from the vehicle power system as a separate load.

A RunCam start/stop signal is a plausible example of a bounded dumb interface. The RunCam Split 4 V3 records locally to microSD and exposes analog video; live video still requires a separate transmitter, antenna, receiver, and link budget. A GoPro also records to microSD, so changing camera does not remove the removable-flash failure mode. Video remains a separately powered evidence payload. Its camera, card, supply, transmitter, mount, pressure, temperature, vibration, and sudden-power-loss behaviour must be qualified without coupling failure into Ogma.

PMOD is **rejected from the baseline**. No named first-mission peripheral justifies its area, power path, shared signals, connector, and fault coupling. A later revision can add one bounded interface after a real consumer supplies its protocol, current, failure behaviour, and flight purpose.

## Displays, LEDs, buzzer, and diagnostics

### Tiny display

**Rejected from the baseline.** No named flight or field operation requires an onboard LCD. A small deliberate LED set, buzzer codes, and the USB-C tool cover the current jobs with fewer parts, less firmware, no display bus, and clearer failure behaviour. A display can return only if a later operator study identifies a specific task that cannot be met more simply. It can never be the sole indication of physical arm state, rail presence, logging, or a safety-relevant fault.

### LEDs

The idea of replacing every LED with a screen is rejected. Rev 1 needed direct rail and state observability. Retain a small deliberate set, likely including:

- critical rail present;
- physical arm state;
- flight MCU health or fault;
- logging state;
- communications or link state where useful.

The final set and disable behaviour remain open. Avoid decorative duplication.

### Buzzer

A buzzer is a strong working requirement for bench fault codes, armed-state warnings, recovery location, and LANDED indication. Rev 1 placed the buzzer on a rail that was absent in common bench use. Ogma 2 must power and test it in every mode where its indication is expected. Audible patterns need a documented meaning and must not be the only safety indication.

### Debug and test access

Rev 1 repeatedly required package-pin surgery and loose SWD leads. Ogma 2 needs:

- compact dedicated debug access for both MCUs;
- NRST and boot/recovery control;
- a debug UART or equivalent console path;
- labelled pads for every rail, enable, reset, chip select, UART, SPI, I2C, CAN TX/RX, CANH/CANL, pyro state, and actuator state;
- per-device isolation links;
- a fixture strategy that does not require probing tiny package pins.

## Mechanical and manufacturing direction

### Packaging

The board must fit a 3-inch vehicle and remain serviceable in the complete avionics bay. Layout and av-bay CAD must be developed together.

The local hardware photographs establish the design contrast:

- The CATS Vega references present one readable PCB with visible processing, GNSS, RF, power, energetic-output, connector, and service regions. One photographed revision uses large edge lever connectors that are easy to operate and inspect, although Ogma's exact connector still needs its own qualification.
- Fluctus uses two closely spaced PCBs joined by long pin headers. The inner faces are hidden, the boards must be separated for inspection or rework, and the photographed battery/pyro screw terminals are small relative to the field wiring task.

During the 29 August integration, one Fluctus showed power indication but did not complete startup or enumerate over USB. It had possible soot exposure near a black-powder charge. Removing the pyro wiring, checking 8.3 V at the battery input, using known-good cables and two laptops, cleaning it, and bypassing the suspected screw terminal did not recover it. The board was swapped. The root cause remains unknown; this is serviceability and diagnostic evidence, not proof that the terminal, stack, soot, or electrical noise caused the failure. The replacement Fluctus and CATS Vega completed the later integration and pop tests.

Electronics owns the avionics bay's functional definition, electrical integration, service workflow, and acceptance evidence. Structures must review and accept its load-bearing airframe interface, retention, pressure loads, and any service-panel cut-out. Ashen remains the intended CAD owner once the controlled envelopes and interfaces are ready. His input package should include:

- Ogma and Foinse outlines, stack height, mounting holes, and keep-outs;
- battery and harness envelopes;
- antenna locations and cable bend radius;
- USB-C, debug, arm, connectors, antennas, and test access;
- insertion and removal path;
- connector retention and strain relief;
- the proper board-to-harness-to-connectorised-charge-assembly path;
- external USB-C, charging, and ordinary service access;
- clean/dirty contamination boundaries;
- bay and barometer pressure-equalisation paths;
- service-panel removal and board/harness keep-outs;
- the flight-ready closure and witness-mark locations;
- tolerance for a future propulsion-CAN harness;
- representative acceleration, rotation, and recovery loads.

### Double-sided layout

Double-sided placement must not turn the board into an unprobeable slab. Keep functional blocks legible, place references and pin-1 marks where they can be seen, leave rework access around high-risk parts, and make both sides inspectable in the intended fixture. No plug-on board may cover a flight-critical block.

One PCB removes board-to-board joins; it does not automatically solve noise. Layout must still control pyro and servo current loops, RF return paths, clocks, sensor grounds, antenna separation, and access for conducted/radiated and connector-disturbance tests. The CATS lesson is block clarity, not component-for-component copying.

### Cleanliness, coating, and staking

**Working direction.** Selective conformal coating and staking may be used after the design and rework state are stable. Manufacture, clean, inspect, bring up, rework, and complete the relevant development tests before coating; then apply a qualified masking and cure process, inspect it, and repeat acceptance. Connectors, USB and RF contacts, physical arm contacts, test/debug pads, barometer and other sensor ports, and every prohibited device area remain uncoated.

The exact chemistry, thickness, masking method, staking material, supplier, rework process, and coated qualification article remain open. Acrylic is a development candidate, not a decision. Parylene is not the baseline. Coating does not replace the external contamination boundary, connector protection, cleanliness, strain relief, or fault containment, and the evidence does not establish that coating would have prevented the Fluctus failure.

## Software direction

### Layers

Rev 1's post-flight review identified four required boundaries:

1. STM32 HAL and interrupts.
2. Peripheral drivers with explicit errors, health, and counters.
3. Per-board pin, bus, and device configuration.
4. Flight and node logic that does not call hardware registers or HAL directly.

The existing shared-library intent remains useful: `comheadan` for transport and contracts, `braiteoiri` for reusable peripheral drivers. Ogma 2 should live in one reproducible project/repository boundary rather than reintroducing drift through many independent application repositories.

### Scheduler

A small time-triggered cyclic executive is the current working direction for the flight MCU. FreeRTOS returns only if measured timing or concurrency requires it.

The flight-side rule is simple: bounded run-to-completion work, no dynamic allocation, no blocking radio or GNSS calls, measured task budgets, and explicit overrun evidence. Every task and interrupt needs a deadline, worst-case activation rate, measured execution-time distribution, accepted upper bound, and defined response to overrun. The timing campaign must include maximum sensor traffic, storage delay, ECC handling, communication flood, timeouts, and simultaneous output activity on the target MCU. DMA and interrupts may service I/O, but the control flow must remain readable enough to audit in one sitting.

The communications MCU can use a different scheduling strategy if its libraries require it. Its failure must remain contained by the UART boundary.

### Development sequence

The staged plan discussed with Anav remains a strong working direction:

1. **Foundations:** one contract source, generated C/Python definitions, CI, clock assertions, console, reproducible binary.
2. **Flight recorder:** barometer and IMU acquisition, watchdog, timestamps, append-only flash. Fly it as a passive recorder.
3. **Estimation and state:** scheduler, state estimation, state machine, host replay, outputs disabled.
4. **Actuation:** three pyro channels, continuity, physical arming, two servo channels, safe-state and HIL tests.
5. **Communications:** second MCU, UART contract, GNSS and LoRa, including the comms-held-reset test.
6. **Health and operations:** reset capture, configuration integrity, preflight self-test, release identity, and field readback.
7. **RTOS only if evidence requires it.**

Every stage ends in an observed result. No stage exists solely to add abstraction.

### Configuration and ground tools

**Required operating promise:** plug in USB-C and it works on a supported team laptop. Normal configuration, verification, testing, telemetry, and log retrieval must use one maintained Ogma tool with no virtual machine, internet dependency, or undocumented recovery ritual.

The July Ogma UI discussion and the CATS Configurator screenshots establish the useful interaction model:

1. Detect the connected board and show board serial, hardware revision, firmware identity, configuration identity, connection state, and data age.
2. Read the actual on-board profile before offering a change. Export it and compare a proposed profile setting by setting.
3. Edit a small typed mission profile with constrained event, fallback, logging, radio, and actuator parameters. Do not expose a general-purpose action language.
4. Preview the complete flight sequence and run firmware-backed replay or simulation with all physical outputs suppressed.
5. Present a timestamped GO/NO-GO report. Missing, stale, invalid, or unmeasured evidence is not a pass. A large `READY` label must be traceable to the checks beneath it.
6. Keep normal, simulation, and hardware-test modes visibly distinct. Entering a test mode must be deliberate; it never bypasses physical arming or hardware output inhibits.
7. Upload once, read the device back, compare every field and identity, and report verified success or a precise mismatch.
8. Capture raw telemetry automatically and package the manifest, identities, events, faults, and local log for each flight.

CATS' clear event sequence, profile readback/comparison, preflight view, and separated test mode are useful references. Its arbitrary `PYRO ON -> DELAY -> PYRO OFF` construction is not the Ogma safety model. A pyro firing is one typed, finite, one-shot firmware action with fixed safety guards. The Fluctus full-configuration workflow's Windows-only dependency is explicitly rejected for Ogma.

The safety authority remains in firmware and hardware. The tool cannot hide an armed output, silently change a profile, declare unavailable evidence healthy, or become the only copy of flight data.

The ordinary USB-C workflow must work with the avionics assembly closed. Raw SWD and invasive recovery remain available, but they are maintenance operations: using them after closure voids the recorded flight-ready state and forces the affected checks to be repeated.

Release requirements carried from Rev 1:

- clean source tag for every flight image and tool;
- binary hashes and compiler/library versions;
- generated protocol and mission manifest version;
- calibration and board serials;
- dirty-tree rejection;
- flashed-image verification;
- configuration upload followed by readback and comparison;
- automatic raw telemetry capture.

## Liquid-propulsion controller

### Architectural position

The propulsion controller is a separate self-governing computer. Calling it an Ogma module obscures the authority boundary. It is an equal vehicle system that exchanges a narrow set of state and coordination messages with Ogma.

Ogma can request or report vehicle-level actions. It cannot be the only place that notices an engine redline or closes a valve. The propulsion controller must remain capable of safe local operation while Ogma is reset, the CAN link is absent, and the operator UI is disconnected.

Its power must be electrically independent of Ogma's logic rail. That does not yet decide whether the vehicle uses a separate physical battery or a centrally distributed protected source. It means an Ogma brownout or connector failure cannot be allowed to hold the engine in an unsafe state.

### Likely propulsion-controller responsibilities

**Working direction:**

- acquire sensors used for local engine control and engine protection;
- run deterministic state, redline, fault, throttle, or sequencing logic required in flight;
- own main fuel and oxidiser valves;
- own throttle actuators if present;
- own ignition enable or igniter output if it is part of the engine subsystem;
- own flight-relevant pressurisation actuators if the vehicle architecture uses them;
- command the defined local safe state without waiting for Ogma, a Pi, a laptop, or GSE;
- retain full-rate local data and fault history;
- publish bounded engine state, health, key pressures, and abort status to Ogma;
- accept only requests that its own state machine considers safe.

### Functions that stay off the flight propulsion controller by default

- tank fill and drain;
- purge;
- ground vent;
- ground pressurant-bottle management;
- facility isolation and preparation;
- operator UI;
- research-only thermocouples, flow, load, or pressure channels;
- general stand data acquisition.

Those belong to GSE, DAQ, or an independent protection layer unless a channel-by-channel requirement proves otherwise.

### Test-stand relationship

The first idea was one broad board that could become both the liquid-test-stand controller and the flight propulsion board. Discussion with Anav, Jay, David, and Dylan exposed the problem: the stand has many more sensors, valves, research channels, operator functions, and facility states than the flight article.

The current LTS working route, decided on 4 September, is one unified stand
controller PCB with one primary MCU. Propulsion and GSE remain explicit logical
responsibilities sharing local acquisition and one output arbiter. The Linux
stand computer handles supervision, aggregation and bulk recording; no required
sensor-to-action path round-trips through it. Separate GSE/DAQ controller boxes
are no longer the stand baseline.

CAN A exercises the production two-node Ogma/propulsion contract. A host adapter
temporarily occupies Ogma's position and is removed when real Ogma is installed.
The stand controller's separate, unbridged CAN B serves GSE requests from the
host. Both LTS software partitions stop on a shared primary-MCU reset; their
separate names do not provide independent protection.

The LTS PCB is not required to fly. A later flight propulsion board is selected
against vehicle requirements and may reuse proven circuits, software, interfaces
and tests. This changes the test implementation, not Ogma's vehicle authority or
the self-governing propulsion boundary.

LTS Revision A keeps a bounded local pre/post-event incident record; the stand
PC owns the complete run. That decision does not reduce the vehicle's local
full-rate recording direction or Ogma's flight-recording requirements. Flight
cannot rely on a stand PC. Incident duration and reset/power-loss coverage on the
LTS remain implementation questions, not completed qualifications.

Local measurement implies local authority. If the propulsion controller reads a pressure for a safety-critical decision, it needs enough local actuator authority to perform the corresponding protective action. If a measurement exists only for research, the stand DAQ can own it.

Do not duplicate pressure ports or transducers by default. Start with one sensor and one clearly owned acquisition path. Add a second transducer only when independent measurement is physically and metrologically justified. If both control and research need the same signal, assess a deliberate conditioned fanout, a digital publisher, or a local high-rate log.

### Data and CAN

Control and abort stay local. CAN carries coordination and summaries.

The earlier estimate showed why full-rate engine acquisition does not belong on a 500 kbit/s vehicle bus. Sixteen 1 kHz 16-bit channels already consume 256 kbit/s before identifiers, timestamps, framing, arbitration, retries, and all other vehicle traffic. Full-rate data should stay in local storage or use a separate test-only interface.

Before selecting Classical CAN, CAN FD, Ethernet, or another test path, write:

- a channel matrix;
- an actuator and safe-state matrix;
- a timing budget;
- a data-volume budget;
- a fault and hazard list;
- a time-synchronisation requirement.

### Propulsion gate tests

The controller is not ready for a hot-fire campaign until it can demonstrate:

- correct local safe action with Ogma held in reset;
- correct local safe action with CAN removed or corrupted;
- bounded response to every defined redline;
- deterministic behaviour at measured worst-case execution load;
- output-safe reset, watchdog, brownout, and loss-of-sensor behaviour;
- local log continuity through faults and power interruption;
- independent hardwired E-stop or protection action as required by the stand hazard analysis;
- flight-like controller qualification separated from research-data ambitions where one test cannot honestly do both.

Exact valve fail states, energise/de-energise policy, ignition interlocks, abort deadlines, sensor rates, and competition/range requirements remain open. They must come from the actual plumbing, valves, sensors, vehicle, stand, and rules.

## Ideas rejected or superseded

| Idea | Current status | Reason |
| --- | --- | --- |
| Five separate Croí/Teachtaire/Foinse/Lámh/Pléasc flight boards | **Superseded** | Repeated MCUs, CAN, regulators, connectors, releases, and integration faults without useful redundancy. Foinse remains separate for a different reason. |
| Many tiny boards because that looks modular | **Rejected** | Maintenance, probing, repair, programming, mechanical integration, and protocol drift dominate. Imperial is now treated as a warning, not the template. |
| Third recovery or CAN-gateway MCU | **Rejected** | More firmware and protocol surfaces. Two MCU roles are enough. |
| CAN as Ogma's internal backplane | **Rejected** | UART connects the two on-board roles. CAN is reserved for independent vehicle systems. |
| CAN star or speculative expander | **Rejected** | No current topology needs it; CAN is a line bus. |
| Generic powered module ecosystem | **Rejected** | No named modules justify unknown current, connectors, protocols, and fault coupling. |
| Mu or another payload powered from Ogma logic | **Rejected** | Couples experiment faults into flight logic. Payload stays separate. |
| Propulsion controller as an Ogma slave module | **Rejected** | It needs local authority, its own safety lifecycle, and independent power. |
| Arduino-style shields | **Rejected from baseline** | No named flight requirement; mechanically and electrically expensive. |
| Male GPIO forest | **Rejected from baseline** | Poor packaging and serviceability. Use a small named interface if one is justified. |
| PMOD or generic expansion connector | **Rejected from baseline** | No named first-mission consumer justifies the power, pins, area, and fault coupling. |
| Separate servo and pyro boards by default | **Superseded** | Two servo and three pyro channels are integrated on Ogma 2. |
| PCA9685 by default | **Working toward deletion** | Two channels fit MCU timers; delete a scarce part, driver, bus dependency, and OE failure mode. |
| Large 10-pin SWD header | **Superseded** | Compact vertical 2×3 connector selected. |
| USB-C with no physical debug | **Rejected** | Breakpoints, recovery, and independent MCU access remain necessary. |
| Screen replaces all LEDs | **Rejected** | Rail and arm observability cannot depend on display firmware. |
| Onboard LCD in the baseline | **Rejected** | No named operation needs it; LEDs, buzzer, and the USB-C tool cover the current jobs with fewer failure modes. |
| Miniature PCB screw terminals for field wiring | **Rejected** | Too small and tool-dependent for the battery, arm, and energetic-output workflow. Select against actual wire, current, retention, and vibration requirements. |
| Rev 1 GNSS antenna diagnostic/switch network | **Rejected from baseline** | It added faults and was bypassed. Start from the simplest justified reference path. |
| Fluctus-style opaque multi-board stack | **Rejected** | Headers obscure the inner faces, couple service operations, add an electrical/mechanical interface, and complicate diagnosis and EMC work. |
| Vertically stacked Ogma/Foinse mezzanine | **Superseded** | It recreates the access problem. Use a visible, independently removable physical arrangement. |
| Windows-only or VM-dependent normal field workflow | **Rejected** | Normal configuration, verification, and log access must work directly on supported team laptops. |
| Routine in-house placement and reflow of Ogma 2 units | **Superseded** | Factory PCBA preserves team time for review, bring-up, fixtures, measurement, and qualification. |
| Embedded controller also owns the operator UI/host workload | **Rejected** | LTS now combines propulsion, GSE and selected acquisition on one MCU, but keeps Linux/UI outside every required real-time protection path. This is not a prohibition on that unified LTS controller. |
| Pi or laptop as sole liquid safety authority | **Rejected** | Loss of the host or link must not remove local safe-state action. |
| Duplicate every stand sensor | **Rejected as default** | Adds ports, leak paths, calibration, packaging, and cost without proving independent value. |
| Maximum possible sample rate for every channel | **Rejected** | Sample rate follows physical bandwidth and the decision or research question. |
| Full-rate engine data over vehicle CAN | **Rejected** | Bus load and timing interference are unacceptable. Log locally or use a test-only path. |
| Image processing on the flight MCU | **Rejected from baseline** | It is payload work. Use a separate subsystem and exchange only a bounded result if needed. |
| One shared selector/fire circuit for all pyro channels | **Not accepted** | Area saving is unproven against wrong-channel and single-fault risks. Needs a fault analysis before reconsideration. |

## Benchmarking plan

### References already inspected locally

- **CATS Vega hardware:** useful example of two MCUs on one readable board, compact debug access, USB-C, clear functional placement, integrated energetic outputs, and field-scale edge connectors.
- **CATS Configurator:** useful reference for visible identity/state, profile comparison, device readback, preflight checks, sequence preview, explicit save state, and separated test mode. Its general action builder is not a template for pyro authority.
- **Silicdyne Fluctus:** useful counterexample for a component-obscuring header stack, miniature field terminals, and a Windows-only full-configuration path. The 29 August failure did not establish which of several possible causes was responsible.

### References still to inspect from primary sources

1. ASTG flight electronics and avionics-bay architecture.
2. Imperial College London, with attention to whether the small boards are actually independent, replaceable, and maintained in practice.
3. CATS repositories and hardware documentation, beyond the photos and configurator screens already saved.
4. Altus Metrum hardware and flight-software architecture.
5. Cornell Rocketry and UBC Rocket avionics.
6. Other teams with public flight evidence, schematics, layout files, release processes, and failure reports.

The comparison should score:

- number of flight-critical PCBs and connectors;
- number of MCUs and firmware releases;
- power-domain isolation;
- sensor and actuation topology;
- debug and production-test access;
- mechanical access and repair;
- configuration and readback;
- logging and reset evidence;
- flight history and published failures;
- whether the design is maintainable by a student team after the original author leaves.

Do not copy a board count or aesthetic. Copy only a choice whose requirement and failure behaviour match ours.

## Design questions and later qualification gates

### P0: architecture and safety

1. Which first vehicle supplies the first mission-specific overlay, and when must its simulated and measured trajectory, staging, environment, RF, recovery, logging, and reliability values replace the provisional workhorse envelope before qualification?
2. What is the authoritative system block diagram for standalone, solid-stack, and liquid-vehicle modes?
3. Which physical source powers Ogma, Foinse, servos, pyros, and propulsion in each mode?
4. Are pyro logic and energetic rails on one battery domain or genuinely galvanically separate?
5. Which pyro switching topology meets the agreed single-fault and wrong-channel requirements?
6. What physical arming and remove-before-flight arrangement is required by each range and competition?
7. What extra interlocks distinguish sustainer ignition from recovery deployment?
8. Is an independent commercial backup deployment altimeter required or strongly preferred for each mission?
9. What is the local safe state for every output after reset, watchdog, brownout, assert, sensor loss, stale command, and power-domain loss?
10. What exact responsibilities and authority are exchanged between Ogma and the propulsion controller?

### P0: MCU and interface selection

11. Which flight MCU has enough timers, ADCs, DMA channels, buses, memory, USB capability if needed, CAN, and debug access without pin conflicts?
12. Which communications MCU supports GNSS, LoRa, UART, USB, and buffering with a stable toolchain and supply path?
13. Should both MCUs use the same family to reduce tools and spare parts, or does the role split justify different parts?
14. What UART bitrate, framing, maximum message size, rate budget, and recovery behaviour are required?
15. Which MCU owns vehicle CAN? The default should be the flight MCU unless a measured requirement proves otherwise.
16. What are the exact CAN endpoints, cable length, bitrate, termination positions, connector, and ground/reference scheme?
17. Does any ground umbilical share vehicle CAN, or use USB, Ethernet, RS-485, or another path?
18. Does each MCU receive its own compact 2×3 debug connector? If not, how is selection achieved without creating another recovery failure?
19. What is the exact 2×3 connector part number, mating cable/tool, pinout, keying, and vertical clearance?
20. What exact USB-C architecture lets the communications MCU own normal access while preserving independent flight-MCU recovery, log extraction, and safe firmware update?

### P0: sensors and actuation

21. What are the actual measurement requirements and ranges for acceleration, angular rate, pressure, voltage, current, and temperature?
22. Which low-g IMU, high-g accelerometer, and barometer set gives useful independent failure modes?
23. Are two dissimilar barometers justified, and how will transonic trust or fusion be handled?
24. Which sensors are flight-critical, health-only, calibration-only, or payload-only?
25. Which buses and chip selects do they use, and how is each branch isolated?
26. Can two servo channels be driven entirely from hardware timers with all other pin and DMA requirements satisfied?
27. What servo supply voltage and peak/stall current must Foinse 2 support?
28. Does the board need servo position feedback, a witnessed endpoint input, or neither for its first mission?
29. What real e-matches or igniters define continuity current, no-fire margin, pulse energy, conductor type and gauge, proper board/harness connector, connectorised charge assembly, temporary adapter, retention, and transient requirements?
30. What output test loads and fixtures will qualify each pyro channel without energetic material during routine HIL?

### P1: power

31. What is the valid standalone input-voltage range and brownout margin?
32. Is the provisional preregulator-to-3.8 V then 3.3 V LDO path thermally and electrically justified?
33. What exactly does Foinse 2 charge or manage on the rail, and under what connector, isolation, and operator procedure?
34. Which Foinse functions survive the deletion test: charger, BMS/protection, fuel gauge, source selector, ideal diode, e-fuse, rail monitor, or actuator conversion?
35. What programmable actuator-voltage range and current are tied to real actuators rather than hypothetical future loads?
36. Which bounded Foinse monitoring/control devices are needed, and what happens if any one powers up incorrectly, clamps the bus, shorts the returned 3.3 V rail, or reports nonsense?
37. How are USB, standalone battery, Foinse power, and any alternate source prevented from backfeeding one another?
38. Which exact power, return, status, measurement, and control signals cross the Ogma/Foinse connection?
39. Which visible, independently removable connection carries each current domain with margin, and which high-current paths require a separate locking harness?
40. Which rail transients, cold starts, hot plugs, source handovers, servo stalls, and radio bursts form the qualification campaign?

### P1: storage, diagnostics, and RF

41. What fixed soldered storage device meets the measured data-rate, endurance, retention, capacity, and USB-C extraction-time requirement? If none does, what evidence justifies removable storage?
42. How quickly must a field operator retrieve and inspect a flight log?
43. Does any named later operation invalidate the baseline decision to omit an LCD?
44. What is the minimum LED set that preserves rail, arm, log, fault, and communications observability?
45. What buzzer part, rail, drive, acoustic output, and code set work in every required mode?
46. Does the GNSS use an active antenna, which connector, and which minimal bias/protection network?
47. Where do the GNSS and LoRa antennas sit in the real avionics bay, with what cable lengths and separation?
48. Castellated LoRa module or on-board RF design?
49. Which radio family and groundstation profile are supported for the first flight?
50. Which RF, GNSS, UART, and PPS nodes need fixture and scope access?

### P1: mechanics and manufacture

51. What are the controlled board outline, mounting-hole pattern, keep-outs, and maximum component heights for the 3-inch envelope?
52. Side-by-side boards, an accessible edge connection, or a short locking harness between Ogma 2 and Foinse 2?
53. How are both sides inspected, reworked, cleaned, and probed in the actual avionics fixture without disturbing unrelated wiring?
54. Which PCBA supplier, stack-up, assembly class, substitutions policy, cleanliness requirement, and inspection evidence apply to prototypes and flight units?
55. What incoming inspection, first-power, boundary-scan/debug, fixture, and acceptance process makes factory-assembled units repeatable?
56. How are battery, antenna cables, USB, debug, arm, proper pyro/servo connectors, connectorised charge assemblies, and high-current harnesses retained against vibration and recovery impact, and how is every temporary raw-wire adapter kept out of the flight configuration?
57. Can either board be removed without disturbing e-matches, antennas, batteries, the other board, or structural joints, and can routine e-match replacement, USB service, and charging occur without opening the electronics volume?
58. What exactly constitutes the closed flight-ready state; which service interfaces remain exposed; how are the bay and barometer pressure paths separated from energetic residue; and which changes invalidate sign-off?

### P2: expansion and usability

59. Does any named first-mission peripheral provide enough evidence to reverse the decision to omit PMOD or another generic expansion port?
60. Is a simple protected camera trigger worth a dedicated connector?
61. Does any payload need a bounded telemetry summary, and if so why must it reach Ogma rather than its own radio or logger?
62. What exact host versions, packaging, USB drivers, offline behaviour, timing, and acceptance tests define “plug in and it just works” on the team's macOS and Windows laptops?
63. What remains field-configurable inside the typed mission profile, what is locked at build time, and what forces a new verified firmware release?

### Liquid-propulsion open questions

64. Which engine sensors are required for local control, local redline protection, development logging, or stand research?
65. What are their ranges, output types, bandwidths, sample rates, accuracy, and failure indications?
66. Which main valves, ignition devices, throttle actuators, and pressurisation actuators must the propulsion controller own?
67. What is the defined safe state for every actuator, and is de-energised hardware consistent with it?
68. What are the worst-case control and abort deadlines?
69. What independent action remains after loss of UI, Ethernet, Pi, Ogma, CAN, controller, one sensor, or one power domain?
70. Is the reusable propulsion controller exactly the flight board, or will flight use a qualified subset after test-stand learning?
71. Which full-rate data stay local, which summaries cross CAN, and which test-only data use a separate link?
72. How are propulsion, GSE, DAQ, valve command, thrust, pressure, and abort logs time-aligned?
73. Which rulesets and range requirements constrain arming, ignition, abort, recovery, and independent safety layers?

## Required evidence before PCB release

The reliability review identifies a sequencing problem in this list: complete
operator and closed-bay proofs require representative assembled hardware.
The [proposed G0–G3 gates](docs/reliability-execution-plan.md#proposed-release-gates)
allocate bounded bench work, engineering-PCB release, installed qualification,
and unit/mission release separately. Gate adoption remains a review decision;
no flight evidence below is waived or claimed complete.

1. Mission and system block diagrams for every supported mode.
2. Sensor/channel matrix with ownership, purpose, rate, accuracy, and fault action.
3. Actuator matrix with power source, normal state, safe state, feedback, and authority.
4. Power tree with every source combination, backfeed path, fuse/protection element, and measured current budget.
5. MCU pin, timer, DMA, ADC, bus, clock, memory, and debug allocation.
6. UART and CAN contracts generated from one machine-readable source.
7. Pyro fault analysis and one-channel bench prototype into inert loads.
8. Servo timer and power test with the intended actuator and load.
9. GNSS and LoRa architecture review using the selected parts and antenna installation.
10. Independent symbol, footprint, exact orderable-part, pin-1, net, and alternate-function audit.
11. Mechanical envelope and serviceability review with the actual connectors, cables, battery, antennas, and visible independently removable Foinse arrangement.
12. Factory-PCBA fabrication/assembly package, substitutions policy, incoming inspection, and test-fixture plan.
13. Software release and acceptance plan with flight-recorder-first staging.
14. Current rules and hazard review for any pyro, staging, or liquid use.
15. End-to-end operator proof on supported macOS and Windows hosts: connect, identify, read, edit, simulate, upload, read back, compare, capture telemetry, and extract a log without a VM or network.
16. Closed-avionics-bay service proof: replace every connectorised charge assembly externally, exercise configuration/readback/log extraction and charging, verify the complete energetic path, inspect the clean volume after representative contamination exposure, confirm pressure equalisation, prove that no temporary raw-wire adapter is installed, and demonstrate that no board, internal harness, mount, or structural joint was disturbed.

## Acceptance direction

The board is not ready because it boots or because every peripheral answers once. The eventual acceptance campaign must include:

- flight MCU operating correctly with communications MCU held in reset;
- independent reset and programming of both MCUs;
- repeated cold start, brownout, source handover, hot plug, and connector disturbance;
- repeated field connection with the actual wire gauges, strain relief, gloves/tools, contamination controls, and access constraints;
- sensor open, short, stuck, stale, saturated, and bus-clamp faults;
- storage interruption and full/corrupt log recovery;
- pyro continuity, arm, wrong-channel, reset, watchdog, and inert-load firing tests;
- open, short, cross-wire, partial-mate, pull, contamination, and repeated replacement tests at every connectorised charge-module interface, with the bay closed;
- servo startup, stall, command loss, MCU reset, and real-mechanism tests;
- CAN loss, corruption, missing termination, and peer reset;
- LoRa range and GNSS acquisition in the final antenna installation;
- exact configuration upload, readback, compare, and release verification;
- normal host workflow on every supported platform without network, VM, or special adapter;
- routine configuration, identity/readback, log extraction, and charging with the electronics volume closed;
- repeated service-panel cycles, pressure equalisation, external contamination exposure, and inspection that the protected electronics volume remained clean;
- a recorded closure manifest and a demonstrated rule that reopening or disturbing an internal item invalidates flight-ready sign-off;
- closed-avionics-bay vibration, acceleration, rotation, shock, and recovery-impact testing;
- a full field rehearsal using the exact battery, harnesses, groundstation, configuration, and binaries intended for flight.

## Immediate next sequence

Use [EX-01–EX-10](docs/reliability-execution-plan.md#work-queue-and-dependencies)
to execute the reliability review. Begin with the fault allocation, MCU-less
Foinse power dependencies, reset/retention contract, and exact MCU resource
spike. The sequence below remains the wider architecture checklist; it is not
a requirement to finish every comparison before a bounded bench experiment.

1. Use the accepted provisional workhorse envelope for Rev A architecture, component comparison, and schematic work. Open a mission-specific overlay for the first vehicle and replace provisional values with simulation and measurement before qualification.
2. Draw the three system block diagrams: standalone Ogma, Ogma plus Foinse, and Ogma plus Foinse plus propulsion controller.
3. Define the avionics-bay clean/dirty, maintenance, and routine-service boundaries. Mock them up at 1:1 with the real e-match leads, connectorised charge assemblies, Nano-Fit/Micro-Fit/Micro-Lock/JST GH/Gecko samples, detachable WAGO MCS MICRO 2712 and 2601 adapters, USB-C, charging lead, battery, boards, tools, vent route, and removable panel.
4. Close the power-domain and pyro-topology questions first. They determine layout and safety boundaries.
5. Build the MCU resource matrix and choose the two MCUs.
6. Write the sensor and actuator matrices.
7. Inspect ASTG, CATS, Imperial, Altus Metrum, Cornell, and UBC from primary sources against the same comparison table.
8. Prototype one pyro channel and the proposed direct-timer servo path before committing the full schematic.
9. Freeze field-connector families, the accessible Ogma/Foinse arrangement, and controlled envelopes; then hand the electronics-owned functional package to Ashen for av-bay CAD and structures review.
10. Create the schematic and factory-PCBA/fixture strategy around named requirements only.
11. Begin firmware as a reproducible passive flight recorder and build the minimal USB-C identity/readback path before adding state, actuation, or radio.

## Evidence basis and authority

Current technical authority:

- [`ogma-rev1-flight-closure.md`](sources/project/ogma-rev1/ogma-rev1-flight-closure.md)
- [`rev1-unified-learnings.md`](sources/project/ogma-rev1/rev1-unified-learnings.md)
- [`rev2-requirements.md`](sources/project/ogma-rev1/rev2-requirements.md), with its distributed-CAN and 10-pin-SWD requirements superseded by the decisions recorded here
- [`rev1-current-system.md`](sources/project/ogma-rev1/rev1-current-system.md)

Local design references:

- [CATS Vega and Fluctus hardware photographs](sources/inspiration/hardware-comparison/README.md)
- [CATS Configurator interaction references](sources/inspiration/cats-configurator/README.md)

Connective Tissue records used to reconstruct the design discussion:

- 17 August: initial consolidation specification and aggressive redundancy deletion, `rec_a75107efc435f3676e4b2511fa50cc18f04c72fb05b3ff075ec7cfaba5d5efd9`.
- 17 August: Anav/Seán discussion of cameras, GPIO, ribbon interfaces, payloads, extra pyro/servo boards, and flight-computer scope, `rec_4d79ab54f6779755a092e31528178b5628e81efc08622bf2781495117f51cb53`.
- 17–19 August: saved external architecture analysis and the subsequent Anav/Seán responses, `rec_00a7185cb30331d699072f7f973da99ce83d78f7dac2bbfe1004715424209c82`. The long analysis is model-authored; the later attributed replies establish which parts Anav and Seán accepted, corrected, or kept open.
- 20 August: saved model analysis of the separate propulsion controller, `rec_59d607fd080bdf2843020fd8bf553446387d234f174c15aec33593dd0d090016`. It is a design input, not a ratified safety specification.
- 24–26 August: liquid-test-stand and propulsion-controller discussion and probe, including speaker-attribution uncertainty where the transcript merged voices, `rec_a9ecab1ebfc7d15411eb0238ce97629f34bb74614760fb9858f6f51bd6ea5fa2`, `rec_7604d79e30132aecadb20f4003ce265cae54a8dc4b1a3cf8c90b979b70695a54`, `rec_c43e7026599d4a55cb420cf23d26cccbe30a6cdd374001197767587a2fa37015`, and `rec_7c539f634c5523ecf8c2061833b1f43ef2ea3ae769636fa642922e89b5d317c6`.
- 27 August: pyro-circuit analysis, display/diagnostic discussion, USB-C, removable storage, and compact debug connector, `rec_d9c76bc7219879780b20cb28b6b30add000bdc271d0f1d8191b21fe04dfda889` and `rec_ff17627ba6cf283b49d22d1aba1e03c07e920594e6472c53d34ad05b3c667263`.
- 27 August: Anav/Seán discussion that separated payloads, generic modules, power, and the self-governing propulsion controller, `rec_2f261b1147e5d596a48dc4ca11c8230719a70608c0acbe8682568f665a6862ac`.
- 28 August: Foinse 2, actuator rail, standalone power, CAN, mezzanine, and packaging discussion, `rec_bc96e7a8b0e93a7f953914df7e568f71fd365865ddd4449c5768545204d9da5c` and `rec_380c35cc9b065dd953f7b28943c28d5db3853966797ca1c809c7db6b3a12919f`.
- 28 August: Seán's explicit current requirements and corrections in the request that produced this document.
- 14 July: attributed Seán record comparing the Ogma, Fluctus, and CATS operating experiences and stating the “plug in and it just works” succession goal, `rec_71b955b3852b9b61da05ecc03d624d705125a3a1b18c1bd65c3e87c976dada93`.
- 29 August: Fluctus field-fault observations and the later correction that bypassing the screw terminal did not recover it, `rec_9b6120c76ca276eeaa9ab5aeeab95c5b0d44ecb8963065d593b04d3fcce70603` and `rec_a9adbe04a1dee23ce1829a1570bb39636775f7f93c05f01f3e885c753af1248c`.
- 29 August: attributed Seán note recording simplicity, Ogma 2 as the intended space-shot platform, and factory PCBA as the preferred assembly route, `rec_6476129ca703e2e37ec71f4afdecb5ec708d121f4370a6d85c34feea2c876bdb`.
- 29 August: Seán's current instruction rejecting miniature screw terminals and the Fluctus-style header sandwich and sharpening the “genius in simplicity” rule.
- 31 August: explicitly attributed Anav/Seán discussion of conformal coating, high-g sensing, full-envelope GNSS, low-pressure thermal concerns, error checking, execution-time tests, and BPS.space as a possible external reviewer, `rec_75acf8afac76014b1eadade505eb0de9dec1ec3c9cc25e8ee824cbb31b154ae4`. Suggestions in that discussion remain suggestions unless marked otherwise here.
- 1 September: attributed Seán statement that avionics-bay work belongs within electronics, `rec_9a8411aad8ba4018258da2e2aaa77bf172014f20561de31095004834a2906cdc`.
- 1 September: voice memo transcribed on 2 September describing Anav's proposal for external replaceable e-match connections, a closed tested avionics assembly, contamination separation, and removable service access, `rec_b94e2f6e4e8e8225a37a366d267af763114dea3afbd970cddb1eed1f4bad5d26`. The transcription uses anonymous speaker labels; attribution to Anav is indirect through the words “Anav was saying,” and recognition or diarisation may contain errors.
- 1 September: saved model launch-process analysis followed by Seán's direct recollection of the Anav/Ashen pyro matrix marked “Test v2,” “Seal everything!” and “Pins = Flight,” `rec_282f3ba5050e5b35a0fd9db774b446a937fc09b46364eacc8e0e093919d4d110`. The model analysis is not treated as raw launch evidence.
- 3 September: Seán clarified that screw and WAGO-style terminals are temporary interfaces for later servo and pyro connection, not Kármán flight hardware; battery and CAN use proper connectors from the start. He then accepted the resulting architecture: proper Ogma connectors for battery, CAN, pyro, and servo, with terminal access only through detachable adapters and connectorised charge/servo assemblies for the space shot.

The local Rev 1 documents and hardware evidence outrank old proposals. Direct attributed Seán/Anav decisions outrank saved model suggestions. Anything still marked open must not silently become a schematic requirement.
