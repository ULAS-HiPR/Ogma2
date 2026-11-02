# Project Log

Append-only; oldest to newest. Add a dated correction instead of rewriting an
earlier checkpoint. Spelling and broken links may be corrected in place.

[`current-system.md`](current-system.md) is the canonical architecture snapshot.
This log preserves how it changes. If a newer entry changes that snapshot, sync
the accepted change into `current-system.md` before schematic capture.

## 2026-08-28 — Ogma/Foinse power split simplified

### Context

During the Belfast trip, the Ogma 2 discussion returned to the rule of one
workhorse flight computer and one separate power board. The team tested whether
Foinse 2 needed its own MCU, duplicated logic-power conversion, source ORing, or
general-purpose inputs. The aim was to remove another firmware target and every
power stage without a named job.

These are architecture decisions and working directions. No Ogma 2 schematic or
PCB exists yet, and none of the proposed power paths has been electrically
qualified.

### Direct observations

- The existing [`current-system.md`](current-system.md) still describes a Foinse
  MCU as open and has Foinse generate protected logic power. The newer discussion
  narrows both points.
- The saved 19:50, 20:02, and 20:14 stream notes describe Foinse as a directly
  attached, non-load-bearing Ogma mezzanine board with no MCU.
- The stream notes are not speaker-labelled. They attribute the monorepo proposal
  specifically to Anav and record Seán's agreement; the other points are retained
  as team discussion rather than assigned to one speaker.
- Earlier that afternoon, Seán explicitly recorded: “Need one workhorse board and
  then a power board. Mezzanine connector.”

### Explicit statements and proposals

- Ogma 2 must work alone from its own battery input.
- In a larger vehicle, Foinse 2 should be the only board directly connected to
  the vehicle batteries and should pass `VBAT` to Ogma over the board pair.
- Ogma should contain the single `VBAT -> preregulator -> 3.3 V LDO` logic-power
  chain. The intermediate preregulator target remains approximately 3.8 V.
- In the integrated configuration, Ogma should return its regulated 3.3 V rail
  over the mezzanine for Foinse's low-power monitoring devices.
- Foinse should have no MCU. The proposal is a set of bounded I2C monitoring or
  control devices plus the required analogue and power circuitry.
- Ogma's pyro and servo power should come from `VBAT` without another buck or
  boost stage on Ogma. This does not remove channel switching, protection,
  continuity measurement, current limits, or the need to qualify the selected
  loads.
- Vehicle-specific actuator power remains on Foinse. The discussion used a
  roughly 20 V solenoid rail, bulk capacitance, flyback components, inductors,
  and drivers as an example, not a frozen electrical requirement.
- The 12 V barrel-jack idea and a duplicate `7.4 V -> 3.8 V -> 3.3 V` chain on
  Foinse were rejected as unnecessary complexity.
- Ogma and propulsion firmware should live in one monorepo. The saved notes
  attribute this proposal to Anav and record Seán's agreement. The purpose is to
  make changes to the shared CAN contract atomic across both targets.

### Interpretation

- Foinse becomes a vehicle-specific energy and power-interface board, not a
  third computer. Ogma remains the common flight-compute board in both standalone
  and integrated configurations.
- Returning 3.3 V from Ogma removes a second logic regulator, but it also makes
  Foinse's low-power instrumentation part of Ogma's logic-rail load and fault
  budget. Every I2C branch still needs defined power-up behaviour, loading, and
  isolation from a clamped bus or failed peripheral.
- Supplying pyros and servos from `VBAT` deletes an unneeded conversion stage. It
  does not justify an unprotected raw-battery plane or erase the separate
  energetic and actuator safety analysis.
- A monorepo removes cross-repository version skew. It does not merge the two
  firmware targets or their authority boundaries.
- Placing solenoid drivers on a dumb Foinse board is compatible with the existing
  architecture only if the propulsion controller retains local command,
  redlines, safe-state enforcement, abort authority, and loss-of-link behaviour.
  The discussion did not settle that physical/control boundary.

### Decisions

- Baseline Foinse 2 has no MCU.
- Baseline physical pairing is a non-load-bearing Ogma/Foinse mezzanine;
  standoffs and fasteners carry mechanical load.
- Ogma owns the only 3.3 V logic-generation chain used by the pair.
- Standalone Ogma accepts its battery directly. Integrated Foinse passes `VBAT`
  to Ogma; Ogma returns regulated 3.3 V for bounded Foinse instrumentation.
- Ogma's two servo channels and three pyro channels use the defined `VBAT`
  domain without a dedicated buck/boost stage on Ogma.
- No 12 V barrel jack and no duplicated Ogma logic regulator on Foinse.
- Ogma and propulsion firmware will use one monorepo with one versioned CAN
  contract.

### Not decided

- Power ORing is not resolved. A simple BAT54C selector was considered and then
  retracted because the integrated path must also deliver `VBAT` to Ogma's pyro
  and servo domains. “No ORing” is not yet a safe schematic decision.
- The exact source-selection, USB coexistence, hot-plug, reverse-current, and
  backfeed circuit remains open.
- The roughly 20 V solenoid example is not a selected rail voltage.
- The physical owner of liquid-engine driver circuitry and the high-rate
  propulsion-data path remain open.

### Consequences

- Two provisional statements in `current-system.md` now need synchronization:
  Foinse-side logic generation and the possibility of a Foinse MCU.
- The Ogma/Foinse interface now needs one complete two-board power tree rather
  than two independently regulated logic systems.
- The mezzanine must carry `VBAT`, returned 3.3 V, ground, I2C, and any defined
  status/control signals with measured current and fault margins. High-current
  actuator paths may still require separate locking connectors.
- Foinse no longer needs a firmware image, boot process, or release target. Its
  devices, register configuration, power-up defaults, and fault responses still
  require a checked interface specification and HIL tests.
- The monorepo should hold one machine-readable CAN contract or generated shared
  definitions. Hand-maintained duplicate protocol files would preserve the
  failure mode the monorepo is meant to remove.

### Unknowns

- Permitted battery chemistry, voltage range, current, brownout margin, and
  connector for standalone and integrated modes.
- Source priority and safe behaviour for every combination of USB, standalone
  battery, and Foinse-supplied `VBAT`.
- Whether `VBAT` and the returned 3.3 V can use the mezzanine at the required
  current and transient margin, or need separate locking connections.
- Foinse I2C device list, addresses, power-up defaults, interrupt lines, branch
  isolation, and behaviour if a device clamps the bus.
- Pyro and servo peak-current paths, protection, return routing, noise coupling,
  and the loads that define qualification.
- Whether solenoid conversion and drivers belong on Foinse, the propulsion
  controller, or a separately bounded power stage.
- How a dumb Foinse preserves propulsion-controller local authority and a safe
  de-energised state under loss of Ogma, CAN, I2C, or either power domain.
- Required high-rate propulsion output, medium, data rate, and relationship to
  the bounded control/status CAN link.
- Exact mezzanine family, pinout, current rating, stack height, wipe, retention,
  vibration qualification, test access, and serviceability.

### Next checkpoint

Draw one page containing the standalone Ogma, integrated Ogma/Foinse, and
Ogma/Foinse/propulsion power trees. Label every source, conversion, protection
element, connector pin group, current domain, controller, safe state, and data
link. Resolve the solenoid-driver authority boundary on that page. Then sync the
accepted result into `current-system.md` before selecting regulator, connector,
or driver parts.

### Evidence

- [`current-system.md`](current-system.md)
- 2026-08-28 16:30 attributed Seán note in Connective Tissue record
  `rec_443820df07f258acba2a8de9d2a64741ed54ca70bd735e13a6bae186f547e07d`
- 2026-08-28 19:50 stream note:
  `rec_344f5d45ca7942c19ac9dd3aad91e3b7d45dbc55bac5a763d08fd397bb6b44dc`
- 2026-08-28 20:02 stream note:
  `rec_c95f38a847a33ecebbe398bf2fc963661f95ef5401eacc7fa597ce03e7ef65cd`
- 2026-08-28 20:14 stream note:
  `rec_206fee31be7370f41f5d7876d8f2297129a0ea7342b17aa689a846d31c724c63`

## 2026-08-29 — Simplicity, serviceability, and the operator contract

### Context

The last five days of Ogma 2 discussion, the local CATS Vega and Fluctus
photographs, the saved CATS Configurator screens, the earlier Ogma/Fluctus/CATS
UI comparison, and the 29 August field integration were reviewed together.
Seán sharpened the governing principle using Colin's phrase: “the genius is in
the simplicity.” Ogma 2 should contain the complete essential flight computer;
Ogma 3 should mainly correct what real use exposes.

This is an architecture and operating-model checkpoint. No Ogma 2 schematic or
PCB exists. “Space-shot capable” is a target whose mission and environmental
requirements remain undefined.

### Direct observations

- The local CATS Vega photographs show readable functional regions and
  USB-C/debug access. One photographed revision uses large edge lever
  connectors.
- The local Fluctus photographs show two closely spaced boards joined by long
  pin headers. The inner faces are hidden. Inspection or rework requires
  separating the pair. Its battery and pyro field connections use small screw
  terminals.
- The photographs establish geometry and access. They do not measure noise,
  vibration performance, connector resistance, or EMC.
- On 29 August, one Fluctus powered its indicators but did not complete startup,
  light its front display, or enumerate over USB. The battery input measured
  about 8.3 V. Pyro wiring was removed; the battery screws were tug-checked;
  known-good cables and two laptops were tried; the board was cleaned; and the
  suspected screw terminal was bypassed. It did not recover and was swapped.
- The failed unit had been close to a black-powder charge and may have received
  soot. Terminal, stack, contamination, firmware, connector, and board damage
  remained possible. No root cause was established.
- Later that day, Seán recorded the first full CATS Vega/Fluctus integration.
  Anav owned the Fluctus workflow. The replacement hardware and pop tests
  worked.
- The CATS screenshots expose board/app/firmware identity and connection state;
  show event/action sequences; read, export, and compare profiles; make unsaved
  state visible; run a read-only preflight sequence check; and separate normal
  and hardware-test modes.
- One configuration capture reports 0.24 V in its information panel; a later
  preflight capture reports `READY`. The captures do not establish the supply
  context, measurement validity, or whether voltage was part of that check.
- In the 14 July comparison, Seán said the succession goal directly: a future
  team member should be able to plug the flight computer in and have it work.
  The useful CATS ideas were safety fallbacks and legible operating state; the
  Fluctus configuration experience was rejected as operationally poor.
- On 29 August, Seán explicitly set Ogma 2 as the intended space-shot platform,
  preferred factory PCBA, and described Ogma 1 as the project that exposed what
  the team did not know.

### Interpretation

- Simplicity includes interfaces, tools, and service operations. One deleted
  header, connector, VM, configuration path, or hidden PCB face can matter more
  than deleting one small IC.
- A single board removes inter-board joins and makes ownership legible. It does
  not guarantee low noise; return paths, RF, clocks, pyro and servo currents,
  conducted transients, and EMC still require layout review and measurement.
- The Fluctus fault is evidence that opaque hardware and ambiguous indications
  increase diagnosis time. It is not evidence that its screw terminal, stack,
  or soot caused the fault.
- Presentation is insufficient evidence. A large `READY` result must trace to
  current valid checks; unavailable, stale, and unmeasured states remain
  explicit. General `PYRO ON -> DELAY -> PYRO OFF` editing is too permissive for
  Ogma's energetic authority.
- “It just works” can be tested: supported laptop, one ordinary USB-C cable,
  exact identity and configuration readback, typed mission editing, output-safe
  simulation, explicit GO/NO-GO evidence, write/readback comparison, automatic
  telemetry capture, and log extraction without a VM or network.
- Operator delegation worked during the final integration. The design should
  preserve that: one person can own a bounded workflow whose state and result
  are visible to the rest of the team.

### Decisions

- Ogma 2 remains one double-sided flight-computer PCB with no plug-on
  daughterboard or component-obscuring stack.
- The 28 August vertically stacked Ogma/Foinse mezzanine direction is
  superseded. Foinse remains separate and MCU-less, but both boards must be
  visible, independently removable, and probeable. Side-by-side, accessible
  edge, and short locking-harness arrangements remain candidates.
- Exposed pin-header stacking is excluded from the flight interconnect.
- Miniature PCB screw terminals are excluded from battery, arm, pyro, and other
  flight-critical field wiring. Exact connector families remain open pending
  real-wire, current, retention, vibration, contamination, and workflow tests.
- Factory PCBA is the baseline for Ogma 2 assemblies. In-house work is reserved
  for rework, recovery, test coupons, and fixtures.
- Normal configuration, verification, testing, telemetry, and log access use
  USB-C and a maintained Ogma tool on supported macOS and Windows hosts. No VM,
  internet connection, proprietary service adapter, or custom loose lead is
  part of routine field operation.
- The configuration surface is a small typed mission profile. General-purpose
  action scripting is excluded. Pyro firing is a finite one-shot firmware
  action with fixed guards, not an operator-assembled ON/delay/OFF sequence.
- Fixed soldered storage with USB-C extraction is the working baseline.
  Removable storage returns only if measured volume, endurance, retention, or
  extraction requirements force it.
- PMOD and the onboard LCD are removed from the baseline. Neither has a named
  first-mission job that survives the deletion test.
- Ogma 2 is the intended complete platform for the named missions through the
  space-shot target. This does not add speculative hardware: the mission
  envelope must justify every capability before schematic capture.

### Consequences

- Fewer connectors and hidden faces become explicit system requirements rather
  than layout preferences.
- The Ogma/Foinse power tree must be redrawn without assuming a vertical
  mezzanine. Each current and signal path needs a physical connector and return
  path in the avionics-bay CAD.
- Connector selection moves earlier. Pyro, battery, arm, servo, Foinse, CAN,
  antenna, USB-C, and debug access must be reviewed with actual wires and tools.
- Factory assembly shifts effort into DFM, substitution control, incoming
  inspection, first-power checks, serialisation, and fixtures.
- The host tool and firmware contract are part of flight-computer acceptance.
  A board that flies but cannot be configured, verified, diagnosed, or handed
  over simply has not met the product goal.
- CATS remains a reference for legibility, preflight, readback, and profile
  comparison. Its exact connectors, actions, checks, and UI are not copied
  without Ogma-specific requirements and fault analysis.

### Unknowns

- Exact space-shot trajectory, staging, thermal, pressure, vibration, shock,
  RF, logging, recovery, and reliability envelope.
- Root cause of the failed Fluctus unit.
- Final battery, arm, pyro, servo, Ogma/Foinse, and vehicle-CAN connector
  families.
- Side-by-side, accessible edge, or short-harness Ogma/Foinse arrangement.
- Conducted/radiated susceptibility and emissions limits and the tests needed to
  qualify the real avionics assembly.
- Supported host versions, installer/driver packaging, offline update/recovery
  path, and USB ownership between the two MCUs.
- Fixed-storage capacity, endurance, retention, and extraction-time budget.
- Exact minimum LED and buzzer code set.

### Next checkpoint

Draw the revised standalone Ogma, integrated Ogma/Foinse, and
Ogma/Foinse/propulsion power trees without a stacked mezzanine. In parallel,
place 1:1 board outlines, actual candidate wires/connectors, battery, antennas,
and service tools inside the controlled 3-inch envelope. The checkpoint passes
only if every board face and service connection is visible, reachable, retained,
and independently removable. Then freeze the connector shortlist and write the
one-page “plug in and it works” host acceptance script.

### Evidence

- [`current-system.md`](current-system.md)
- [CATS Vega and Fluctus hardware photographs](sources/inspiration/hardware-comparison/README.md)
- [CATS Configurator interaction references](sources/inspiration/cats-configurator/README.md)
- 14 July attributed Seán UI and succession-goal record:
  `rec_71b955b3852b9b61da05ecc03d624d705125a3a1b18c1bd65c3e87c976dada93`
- 29 August Fluctus field-fault and screw-terminal-bypass records:
  `rec_9b6120c76ca276eeaa9ab5aeeab95c5b0d44ecb8963065d593b04d3fcce70603`
  and `rec_a9adbe04a1dee23ce1829a1570bb39636775f7f93c05f01f3e885c753af1248c`
- 29 August attributed Seán simplicity, space-shot, and PCBA record:
  `rec_6476129ca703e2e37ec71f4afdecb5ec708d121f4370a6d85c34feea2c876bdb`
- Seán's 29 August instruction rejecting miniature screw terminals and the
  Fluctus-style header sandwich and requiring the sharpened vision to be made
  durable here.

## 2026-08-29 — Bounded Kármán-line mission and hardening study

### Context

Seán narrowed “space-shot capable” to the actual target: one suborbital sortie
that reaches at least 100 km near apogee and returns through descent and
recovery. This is intentionally different from a spacecraft that must operate
in orbit for six months or years without repair.

The framing came from Seán's 28 August notes while watching Sir Peter Beck. The
notes compare reaching orbit with living there for twelve years and compare the
qualification duration of a single-use engine with a reusable one. “Valley of
death” appears in Seán's note. This record supports Seán's design framing; it is
not a verified verbatim Beck transcript.

Seán also identified live video as a wanted vehicle capability and raised
microSD reliability. The currently available cameras include RunCam Split 4 V3
units; a GoPro was considered as an alternative.

### Decisions

- The Ogma 2 space-shot target is one bounded flight: power up, launch, survive
  ascent and any staging, reach at least 100 km near apogee, descend, execute
  recovery, land, and preserve local evidence.
- Orbital insertion, months/years of autonomous operation, repeated
  radiation-belt exposure, long-term total-dose accumulation, orbital thermal
  cycling, autonomous on-orbit repair, and uninspected reuse are outside the
  baseline.
- Mission duration and phase are first-order requirements. Short transients,
  second-scale resets, minutes near vacuum, hours of pad/recovery operation,
  and years in orbit are not one reliability problem.
- Video remains a separately powered evidence payload. Its storage, RF, camera,
  and power faults cannot enter the Ogma flight-critical tree.
- The mission boundary was added to [`current-system.md`](current-system.md).

### Direct observations from primary sources

- The 1976 US Standard Atmosphere gives near-vacuum pressure at 100 km. Its gas
  temperature does not directly set the board temperature during a short
  transient flight.
- NASA radiation guidance separates cumulative total-ionising-dose and
  displacement-damage effects from prompt single-event effects. Event risk
  depends on trajectory, duration, particle environment, and device response.
- The STM32H573 provides flash ECC and optional ECC on SRAM2, the first 256 KB
  of SRAM3, and backup SRAM. SRAM1 and the remaining 64 KB of SRAM3 are not ECC.
  ST describes one-bit correction and two-bit detection at a 64-bit SRAM
  doubleword. A corrected read does not rewrite the bad cell automatically.
- The TMS570LS1227 provides dual lockstep Cortex-R4F execution, ECC memory,
  BIST, and error signalling, but requires a large LQFP144 package, an
  additional core rail, and a different toolchain. It is not radiation-qualified.
- The u-blox MAX-M10S operational limits are 80,000 m altitude, 500 m/s
  velocity, and 4 g. It cannot be specified as the full-trajectory 100 km
  receiver without contradicting its datasheet.
- Common board-mount barometers have minimum specified pressures many orders
  above the nominal pressure at 100 km. They remain lower-flight instruments.
- The RunCam Split 4 V3 records to microSD and exposes analog video. Live video
  requires a separate transmitter and ground link. GoPro HERO cameras also use
  microSD; changing camera does not remove removable-flash risk.
- Connector manufacturer ratings depend on the exact contact, wire, circuit
  count, temperature, and test configuration. Headline family ratings are not
  installed Ogma ratings.

### Engineering study

[`Kármán-line mission hardening report`](docs/karman-line-mission-hardening-report.md)
was created as a separate pre-schematic design study. It covers:

- mission duration and environment;
- radiation mechanisms and mission-integrated risk;
- MCU selection and the STM32H573/TMS570 comparison;
- SRAM/flash ECC, scrubbing, critical-state encoding, cache/control-flow gaps,
  logging integrity, watchdogs, reset evidence, and fault injection;
- flight, communications, sensor/storage, servo, and pyro power domains;
- input hot-plug, transient, brownout, current-limit, and latch-up containment;
- energetic-output hardware bounds and independent vehicle recovery;
- barometer, GNSS, high-g, inertial, and external altitude-proof roles;
- grounding, CAN/UART/USB protection, galvanic-isolation criteria, ESD, and EMC;
- connector families, crimp workmanship, RF retention, PCB layers, placement,
  coating, staking, and factory PCBA controls;
- separate RunCam/GoPro storage and live-video architecture;
- qualification, environmental, HIL, and fault-injection gates.

### Working recommendations, not decisions

- STM32H573 is the current flight-MCU candidate because it adds real ECC while
  preserving the STM32 development path. It still requires an exact
  pin/memory/DMA/timer/errata and injected-fault audit.
- TMS570LS1227 is the lockstep comparison if fault injection shows that the
  H573's single core leaves unacceptable coverage.
- Rad-hard MCU families remain outside the baseline unless a trajectory and
  device-cross-section calculation shows that system-level containment cannot
  meet the allocated risk.
- Communications/RF should move to a switchable, current-limited branch with
  independent reset and no back-power path.
- An external windowed supervisor should complement the MCU watchdogs.
- Flight-critical objects and stacks should be build-enforced into ECC SRAM;
  corrected SRAM should be read and rewritten by a bounded scrub.
- The vehicle should use a genuinely independent recovery controller rather
  than treating the second or a third on-board MCU as redundancy.
- The direct Ogma-to-Foinse 3.3 V return should be replaced by Foinse local
  regulation or a dedicated current-limited auxiliary branch.
- Micro-Fit-class locking crimp connectors are current-path candidates;
  Harwin Gecko-class parts are high-reliability signal candidates; JST GH is a
  low-current candidate only. Exact parts remain open.
- Four versus six PCB layers should be decided by placement and return-path
  evidence. One board and no hidden stack remain unchanged.
- The permanent 2×3 debug header should be reopened against a no-mass
  Tag-Connect-style footprint.

### Unknowns

- Exact trajectory, duration, acceleration, rotation, vibration, shock,
  thermal, pressure, RF, radiation, and recovery envelopes.
- Quantitative acceptable probability of inadvertent fire, lost recovery,
  lost primary log, and lost telemetry.
- Independent method and uncertainty for proving at least 100 km.
- Exact recovery and staging topology.
- Battery and Foinse power tree.
- Exact MCU, regulator, supervisor, sensors, storage, transceivers, connectors,
  harness, PCB stack-up, antenna, and video assembly.
- Device radiation cross-sections and the resulting mission event probability.
- Qualification and acceptance levels.

### Next checkpoint

Write the one-page trajectory, duration, environment, recovery, and reliability
envelope. In parallel, run a small STM32H573 ECC/watchdog/reset spike and build
the real-harness battery-input/communications-branch power mule. Those results
decide whether the current MCU and power recommendations can enter the
architecture before schematic capture.

### Evidence

- [`current-system.md`](current-system.md)
- [`Kármán-line mission hardening report`](docs/karman-line-mission-hardening-report.md)
- [`ogma-rev1-flight-closure.md`](sources/project/ogma-rev1/ogma-rev1-flight-closure.md)
- 28 August attributed Seán/Peter Beck viewing notes:
  `rec_443820df07f258acba2a8de9d2a64741ed54ca70bd735e13a6bae186f547e07d`
- Seán's 29 August mission-timescale and video clarification.
- Primary manufacturer, NASA, ESA, ECSS, and US Standard Atmosphere sources
  linked at the claims they support in the hardening report.

## 2026-09-02 — Avionics-bay service and contamination boundary

### Context

Seán requested a review of the previous five days of Stream material before
continuing the Ogma section-by-section design review. Most of the 1 September
work concerned the liquid-test-stand controller, GSE, and DAQ. It was kept out
of Ogma except where an already accepted interface principle applied.

The Ogma-specific material added one missing system boundary: the flight
computer cannot be designed independently of how a tested avionics assembly is
closed, serviced, connected to e-matches, vented, and protected from energetic
residue. Seán reviewed the proposed document scope and authorised these changes.

### Direct observations and evidence

- A voice memo recorded on 1 September and transcribed on 2 September contains
  one speaker saying, “Anav was saying” that pop tests should not require the
  whole avionics bay to be disassembled. The proposal was to connect permanent
  internal pyro wiring to service connections in the bay wall, attach
  replaceable e-matches outside, keep soot out of the closed bay, test the
  assembly in advance, and then stop disturbing it.
- The same memo discusses removable side access for programming and battery
  charging and prefers it to loose USB extension wiring. It explicitly
  describes the immediate terminal retrofit as a Multistage measure and says a
  future Ogma bay should receive a better purpose-designed solution.
- The voice transcription uses anonymous speaker labels. Recognition and
  diarisation may contain errors. Attribution to Anav is indirect through the
  speaker's words rather than provider identity metadata.
- An explicitly attributed Anav/Seán conversation on 31 August raised
  conformal coating, high-g sensing, GNSS valid through the real trajectory,
  battery and MCU thermal behaviour, extensive error checking, and measured
  software timing. Anav did not see a present need for FreeRTOS. BPS.space was
  suggested as a possible external review contact.
- “Conformal coating could have saved Fluctus” was Anav's hypothesis. No
  Fluctus root cause has been established. Acrylic and parylene material saved
  nearby was model-authored guidance, not a component or process decision.
- In an explicitly attributed 1 September exchange about ownership of payload
  structures and avionics bays, Seán stated: “This must be a part of
  electronics.”
- A saved model launch-process debrief proposed one manifest, an early complete
  rehearsal, and a configuration freeze. Seán's direct follow-up recalled the
  Anav/Ashen pyro test matrix marked “Test v2,” “Seal everything!” and
  “Pins = Flight.” The saved model analysis is not treated as raw launch
  evidence; the attributed follow-up is treated as Seán's recollection.
- The live Ogma documents already covered high-g measurement, full-envelope
  GNSS limits, low-pressure thermal testing, ECC and state protection,
  execution monitoring, selective post-test coating, locking harnesses, and
  the complete avionics bay as the qualification article. They did not define
  the closed-bay service workflow or clean/dirty interface.

### Interpretation

- The important idea is not a screw terminal. It is a system state: integrate,
  inspect, test, close, and stop disturbing the flight assembly.
- E-match leads are consumable and repeatedly handled. Ogma, Foinse, batteries,
  internal harnesses, and mounts are qualified flight hardware. Their service
  boundaries should reflect that difference.
- “Sealed” cannot silently mean hermetic. Near 100 km, an unvented sea-level
  cavity approaches a one-atmosphere pressure differential. Unless qualified
  as a pressure vessel, the bay needs controlled pressure equalisation that
  does not use the dirty energetic opening as the barometer reference.
- A removable maintenance panel and externally available routine interfaces are
  different things. E-match replacement, normal USB work, and charging should
  not open the electronics volume. Raw debug, rework, board removal, or internal
  harness changes may use the maintenance panel, but they invalidate the
  flight-ready state.
- Electronics ownership means ownership of functional layout, electrical
  integration, service procedure, and acceptance evidence. Structures still
  reviews and accepts primary load paths, pressure loads, retention, and any
  airframe cut-out.

### Decisions

- Electronics owns the functional integration of the Ogma avionics bay.
- The complete avionics assembly must have a recorded closed flight-ready
  state. Opening it or disturbing an internal item triggers the defined
  inspection and regression path.
- Replaceable e-matches connect outside the protected electronics volume.
  Ogma connects through a retained internal harness and mechanically supported
  bay-wall interface. Continuity and firing-current evidence cover the whole
  installed path.
- Routine identity/configuration readback, log extraction, and the defined
  Foinse charging operation must be possible without opening or moving the
  flight assembly.
- Raw SWD, invasive probing, rework, and internal changes are maintenance
  operations rather than ordinary closed-bay service.
- The bay needs a deliberate pressure-equalisation path unless later designed
  and qualified as a pressure vessel. The barometer port and contamination path
  are separate design subjects.
- Miniature PCB screw terminals remain excluded. The voice memo's screw
  terminal/WAGO examples do not select an Ogma connector.
- LTS common-board, GSE, DAQ, Linux-host, valve-control, and E-stop decisions do
  not enter the Ogma architecture. The existing rule remains: safety-critical
  decisions stay local; CAN carries bounded coordination and summaries.

### Working directions, not decisions

- A retained removable side or service panel is the current maintenance-access
  direction. Geometry, fasteners, sealing, structural role, RF effect, and
  vent relationship remain open.
- Selective conformal coating and staking remain candidates only after
  manufacture, cleaning, inspection, bring-up, rework, and development tests.
  Acrylic is a development candidate; no chemistry or process has been chosen.
- BPS.space remains a possible benchmarking or external-review contact.
  No outreach is recorded or authorised by this checkpoint.
- The current cyclic executive remains the software baseline. Measured deadline
  evidence, not preference, decides whether an RTOS returns.

### Consequences

- Board connectors cannot be selected in isolation. The board connector,
  internal harness, bay-wall interface, external lead, e-match, strain relief,
  contamination cover, and operator procedure form one qualified current path.
- Avionics-bay CAD must include routine service operations, clean/dirty
  boundaries, pressure paths, insertion/removal paths, witness marks, and
  actual hands, tools, wires, and connector envelopes.
- Qualification gains closed-bay e-match replacement, short/miswire/partial-
  mate/pull tests, external contamination exposure, pressure cycling,
  service-panel cycling, and a closure/reopening record.
- Software qualification gains target-hardware deadline and execution-time
  tests under simultaneous worst-case traffic, storage, ECC, timeout, and
  output conditions.
- [`current-system.md`](current-system.md) now records the accepted boundary.
  [`Kármán-line mission hardening report`](docs/karman-line-mission-hardening-report.md)
  now carries its engineering and qualification consequences.

### Unknowns

- Exact external e-match connector or terminal family, pinout, cover, wire,
  feedthrough construction, and mounting.
- Exact service-panel geometry and whether it carries structural load.
- Bay volume, vent area, pressure history, contamination barrier, and separate
  barometer-port geometry.
- Exact external USB-C and Foinse charging implementation.
- Closure authority, checklist, witness method, and exact regression depth after
  each class of disturbance.
- Coating chemistry, masking, thickness, supplier, rework process, and
  qualification article.
- Whether BPS.space or another external reviewer will be contacted.
- Independent recovery architecture, which remains the unresolved subject of
  Ogma design review Section 2.

### Next checkpoint

Resume Ogma design review Section 2 and decide the independent recovery
architecture. Then review the avionics-bay boundary directly: make a 1:1
service mock-up with the actual candidate boards, battery, e-match leads,
feedthroughs, USB-C, charging lead, vent path, removable panel, hands, and tools.
The mock-up passes only when every routine operation occurs without disturbing
the closed flight assembly.

### Evidence

- [`current-system.md`](current-system.md)
- [`Kármán-line mission hardening report`](docs/karman-line-mission-hardening-report.md)
- 31 August attributed Anav/Seán space-shot and coating discussion:
  `rec_75acf8afac76014b1eadade505eb0de9dec1ec3c9cc25e8ee824cbb31b154ae4`
- 1 September attributed Seán avionics-bay ownership statement:
  `rec_9a8411aad8ba4018258da2e2aaa77bf172014f20561de31095004834a2906cdc`
- 1 September voice memo, transcribed 2 September:
  `rec_b94e2f6e4e8e8225a37a366d267af763114dea3afbd970cddb1eed1f4bad5d26`
- 1 September saved model debrief and attributed Seán pyro-matrix recollection:
  `rec_282f3ba5050e5b35a0fd9db774b446a937fc09b46364eacc8e0e093919d4d110`
- Seán's 2 September authorisation of the proposed three-document update, with
  connector, coating, panel geometry, and independent recovery left open.

## 2026-09-03 — Proper flight connectors and detachable raw-wire adapters

### Context

Seán clarified the connector discussion after the avionics-bay boundary was
recorded. The earlier wording still allowed screw, WAGO, or another terminal to
be read as a possible Kármán e-match interface. That is not the intended
architecture.

There are two different jobs:

1. Ogma and its flight harness need compact, keyed, retained, protected
   connectors.
2. Development and some earlier vehicle work may need repeated connection of
   bare servo or e-match leads.

The second job does not justify putting a raw-wire terminal on Ogma or carrying
one into the space-shot configuration.

### Explicit statements and acceptance

- Anav likes screw terminals because they are small.
- Seán dislikes them because they are fiddly, permit shorts, and leave the
  electrical connection exposed.
- Seán considers WAGO-style terminals better for temporary bare-wire work but
  generally too large.
- Seán stated that such terminals are temporary connections for later servo and
  pyro work and will not be used for the space-shot launch.
- Seán stated that Ogma will use proper battery and CAN connectors from the
  start.
- The model proposed extending that rule to pyro and servo: proper locking
  connectors on Ogma from Rev A, detachable WAGO/raw-wire adapters for
  development, and connectorised servo or charge assemblies for Kármán flight.
- Seán answered, “fantastic. write all of this shit down. thank you so much. and
  also the strong candidates.” This checkpoint treats the complete proposed
  lifecycle as accepted and the named families as candidates, not selected
  parts.

### Decisions

- Ogma Rev A uses proper shrouded, polarised, positive-lock connectors for
  battery, CAN, pyro, and servo.
- No bare-wire screw, spring, push-button, or lever terminal is mounted on
  Ogma.
- Screw terminals are rejected. Their board-area saving does not compensate for
  tool use, exposed conductors, loose-strand/short risk, poor insertion
  visibility, or operator difficulty at energetic interfaces.
- When bare servo or e-match leads are useful during development, pop tests, or
  an earlier vehicle, a detachable harness or breakout converts the proper Ogma
  connector to a tool-free terminal.
- The raw-wire adapter is replaceable, visibly non-flight hardware, and absent
  from the Kármán manifest and physical configuration.
- The Kármán connection is:

  ```text
  Ogma locking connector -> qualified retained harness -> keyed connectorised servo or charge assembly
  ```

- A bare-lead e-match is terminated into its controlled replaceable charge
  assembly away from the vehicle, then inspected and tested before installation.
  Exact termination workmanship remains open.
- Battery, CAN, pyro, servo, and charge-module connectors may use different
  families or mechanical keys. Nothing may cross-mate with battery or the wrong
  energetic channel.

### Strong candidates

#### Battery and higher-current paths

- **Molex Nano-Fit:** strongest small candidate. The family uses 2.50 mm pitch,
  26–20 AWG wire, positive locking, isolated contacts, optional TPA/CPA, and
  mechanical/colour keying. Molex states up to 8 A at family level; the real
  Ogma value depends on the exact contact, loaded circuits, wire, PCB copper,
  temperature, and duty.
- **Molex Micro-Fit 3.0:** slightly larger established comparison. Positive
  latch, polarised housing, isolated contacts, TPA/secondary-lock options, and
  an 8.5 A family-level maximum. Exact parts and derating remain open.

These are the primary battery, Ogma/Foinse, pyro-power, and high-current servo
candidates. Neither is selected.

#### CAN and compact low-current harnesses

- **Molex Micro-Lock Plus 2.0:** strongest compact CAN candidate. Positive
  latch, board-retention solder tabs, 22–26 AWG support, and a stated maximum up
  to 4.7 A depending on configuration.
- **JST GH:** smallest current comparison. Secure lock, 1.25 mm pitch, 1 A with
  AWG 26, and AWG 30–26 wire. Its wire size and installed harness retention may
  be too delicate for the final vehicle.
- **Harwin Gecko:** Kármán high-reliability comparison. 1.25 mm pitch, locking
  options, published shock/vibration performance, 2 A per contact with all
  contacts loaded, and available cable assemblies. Cost, tooling, procurement,
  and assembly burden may make it excessive outside the highest-consequence
  links.

#### Pyro and servo flight connectors

- **Nano-Fit or Micro-Fit 3.0:** primary candidates where measured pulse/stall
  current and wire size require a power connector.
- **Micro-Lock Plus 2.0:** candidate where the measured servo or pyro path stays
  inside its exact contact, wire, temperature, and pulse limits.
- A standard friction-fit RC servo plug is not accepted as the Ogma board
  interface. It may remain beyond a retained development adapter or be replaced
  on the controlled flight assembly.

#### Temporary bare-wire adapters

- **WAGO MCS MICRO 2712:** strongest compact tool-free candidate. Pluggable
  lever connection, 2.54 mm pitch, 28–20 AWG, optional locking, gold contacts,
  and inverse coding. WAGO positions it for low-current/low-voltage use. It
  requires pyro pulse testing and remains adapter-only.
- **WAGO 2601:** larger-wire alternative. Fixed 3.5 mm-pitch lever PCB terminal
  accepting 26–16 AWG. It belongs on a detachable breakout board, not Ogma.

### Interpretation

- The useful modularity is in the harness, not on the flight PCB. Ogma keeps one
  stable qualified connector surface while cheap adapters absorb changing
  servos, e-matches, wire sizes, and test procedures.
- A small screw terminal optimises PCB area while making the human operation
  worse. The detachable adapter permits a physically larger, clearer terminal
  without consuming flight-board area or entering the flight failure tree.
- The connectorised charge module preserves Anav's underlying goal: e-matches
  can be replaced without opening or disturbing the avionics bay. It removes the
  exposed field terminal from the Kármán implementation.
- “Proper connector” is still a requirement category, not a part number.
  Manufacturer headline current and shock/vibration claims do not qualify the
  installed Ogma harness.

### Consequences

- The schematic reserves proper connector footprints for battery, CAN, pyro,
  and servo; it does not reserve space for screw or WAGO terminals.
- Development hardware includes one or more separately controlled adapter
  drawings/BOMs. An adapter cannot silently become flight hardware.
- The flight manifest and visual inspection include an explicit check that no
  raw-wire adapter is installed.
- Pyro qualification covers board connector, internal harness, external
  connector, pre-terminated charge assembly, e-match, and physical retention as
  one path.
- CAD and service testing use the real connector bodies, latches, wire bend
  radii, strain relief, hands, and tools rather than nominal pitch alone.

### Unknowns

- Exact family and part number for battery, Ogma/Foinse, CAN, each pyro channel,
  servo, arm, and charge-module interfaces.
- Actual battery, pyro pulse, servo stall, and combined connector current.
- Exact wire gauges, insulation diameters, contact plating, contact count,
  keying, TPA/CPA, strain relief, and backshells.
- Whether Micro-Lock Plus 2.0 is mechanically preferable to JST GH for CAN after
  real-harness vibration.
- Whether Gecko's extra reliability is justified by the Kármán fault allocation.
- Whether MCS MICRO 2712 can carry any intended pyro-development pulse without
  unacceptable resistance, heating, damage, or state ambiguity.
- Exact off-vehicle process for turning a bare-lead e-match into a controlled
  connectorised charge assembly.

### Next checkpoint

Buy or request samples rather than selecting from drawings. Build one small
comparison fixture using the intended wires and test:

1. gloved mating and clear latch/lever-state inspection;
2. deliberate wrong-interface and wrong-channel attempts;
3. crimp/termination inspection and wire pull;
4. four-wire contact/path resistance before and after repeated mating;
5. battery continuous current, servo stall, and instrumented pyro pulse;
6. harness-supported vibration and shock disturbance;
7. contamination, partial-mate, open, short, and conductor-pull faults;
8. 1:1 bay access, bend radius, strain relief, and removal;
9. manifest check that rejects the temporary adapter from the Kármán article.

The result freezes connector families. Until then, the shortlist remains open.

### Evidence

- [`current-system.md`](current-system.md)
- [`Kármán-line mission hardening report`](docs/karman-line-mission-hardening-report.md)
- Seán's 3 September connector clarification and authorisation in the current
  conversation.
- Molex [Nano-Fit](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/nano-fit-connectors)
- Molex [Micro-Fit 3.0](https://www.content.molex.com/dxdam/literature/987650-5984.pdf)
- Molex [Micro-Lock Plus](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/micro-lock-plus-connectors)
- [JST GH](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf)
- [Harwin Gecko](https://www.harwin.com/hri-range/gecko)
- WAGO [MCS MICRO 2712](https://www.wago.com/us/pluggable-pcb-connectors/mcs-micro-2712)
- WAGO [2601](https://www.wago.com/global/products/electrical-interconnections/discover-pcb-connection/pcb-terminal-blocks-with-levers-2601-series)

## 2026-09-03 — Ogma 2 separated into its own collaboration repository

### Context

Seán asked for the same boundary used by the LTS workspace: one small active
Git repository for current design decisions and planning, surrounded by a local
archive for raw, duplicate, generated, and superseded material. He then made the
repository boundary explicit: Ogma 2 must be a new project and repository; the
original Ogma repository remains the Rev 1 project.

### Observed

- `ULAS-HiPR/Ogma` already exists as a private repository for the first Ogma
  project. No remote change was made to it during this restructure.
- The pre-split Ogma 2 directory contained three current Markdown documents,
  four CATS Vega/Fluctus hardware photographs, eleven CATS Configurator
  screenshots, and two `.DS_Store` files.
- All three documents are active. The photographs and Configurator screens are
  cited by current architecture decisions about serviceability, connector scale,
  identity/readback, preflight, event visibility, and test mode.
- Several Configurator screens are alternate or collapsed views of the same
  state. The full capture is useful provenance but not required in every clone.

### Decisions

- The new private `ULAS-HiPR/Ogma2` repository is the canonical Ogma 2
  collaboration repository.
- `current-system.md` and `project-log.md` remain at repository root.
- The Kármán hardening study lives under `docs/`.
- The owned Ogma/Foinse/propulsion authority, power, and CAN boundary lives
  under `interfaces/`; downstream projects may carry explicit snapshots.
- Four unique hardware photographs and seven non-redundant Configurator screens
  are kept under `sources/` with descriptive filenames, scope limits,
  provenance notes, and SHA-256 hashes.
- The complete original four-photo and eleven-screen capture, original
  filenames, macOS metadata, and future bulky/superseded material remain in the
  local sibling `archive/` outside Git.
- Ogma Rev 1 evidence remains in the original Ogma workspace and repositories.
  It may be cited; it is not moved or merged into Ogma 2.

### Consequences

- A clean clone now contains the current architecture, deep design study,
  chronology, controlled cross-system boundary, and the visual evidence needed
  to review them.
- Raw model runs, duplicate captures, temporary output, personal material, and
  stale working files do not enter collaborator review by default.
- Future Ogma 2 hardware, firmware, host tooling, fixtures, tests, requirements,
  and qualification evidence have one repository boundary instead of reviving
  the Rev 1 multi-repository split.
- The reference images remain internal. Repository privacy does not resolve
  their unknown reuse rights.

### Unknowns

- The new repository's software, hardware, and documentation licences. The Ogma
  Rev 1 GPL-2.0 file was deliberately not copied into the separate Ogma 2
  project without an explicit licensing decision.
- Creator, source URL, and publication rights for the hardware photographs and
  CATS Configurator screenshots.

### Next checkpoint

Review the initial repository pull request. Then add the first mission-envelope
artifact and begin implementation only after its decision-critical ranges and
fault allocations are accepted.

### Evidence

- [`README.md`](README.md)
- [`current-system.md`](current-system.md)
- [`docs/karman-line-mission-hardening-report.md`](docs/karman-line-mission-hardening-report.md)
- [`sources/README.md`](sources/README.md)
- [`interfaces/ogma-foinse-propulsion-boundary.md`](interfaces/ogma-foinse-propulsion-boundary.md)
- Local sibling `archive/README.md`
- Seán's 3 September instruction to mirror the LTS active-repository/archive
  split while keeping Ogma 2 separate from the first Ogma repository.

## 2026-09-03 — Workhorse role and provisional platform envelope accepted

### Context

The hardening report initially treated the missing final trajectory and
environment as blockers to part selection. Seán corrected that framing. Ogma 2
must be a workhorse flight computer for the team's competition launches. Exact
vehicle values will not exist until each rocket is mature enough for simulation
and instrumented testing; Rev A needs provisional values now.

### Observed evidence

- The public 2025 EuRoC rules define 3 km and 9 km solid, hybrid, and liquid
  categories and permit multistage vehicles.
- The public 2024 EuRoC Design, Test & Evaluation Guide warns that a vehicle may
  remain on the rail for several hours.
- No current Ogma 2 vehicle simulation or measured environment exists. The
  numerical values below are engineering budgets, not observed vehicle loads.

### Decisions

- Ogma 2 is HiPR's default workhorse flight computer for ordinary competition
  and development launches across solid, hybrid, liquid, single-stage, and
  multistage vehicles.
- A new rocket should normally change the typed mission profile, harness,
  Foinse configuration, external assemblies, and qualification evidence rather
  than force a new Ogma PCB.
- The bounded flight to at least 100 km remains the short-duration extreme case.
  Orbital lifetime remains out of scope.
- The following values are locked as the provisional Rev A platform envelope:

| Dimension | Provisional value |
| --- | --- |
| Normal mission set | 3–9 km competition flights; solid, hybrid, liquid; single-stage or multistage |
| Extreme mission | One short-duration flight to at least 100 km followed by recovery |
| Powered operation | 8 hours through bench/pad wait and flight |
| Recovery reserve | A further 4 hours of reduced-duty beacon and log protection |
| Full-rate flight record | At least 30 minutes |
| Supported service period | 5 years |
| Reuse | 25 inspected flight cycles; acceptance test after every flight |
| Powered electronics temperature | −20 to +70 °C |
| Component temperature grade | Prefer at least −40 to +85 °C |
| Ambient-pressure survival | Sea-level pressure down to approximately 0.01 Pa; sensor validity separate |
| Acceleration measurement | Separate ±200 g channel |
| Board structural design case | 50 g quasi-static |
| Angular-rate measurement | At least ±2000°/s with saturation handling |
| Shock screening | 200 g short-duration provisional target; waveform open |
| Vibration | Exploratory sine/random testing, replaced later by measured vehicle spectra |
| Moisture | Closed-bay rain and splash survival; no exposed-wet-PCB requirement |

### Interpretation

- “Provisional” means accepted for present design use and explicitly replaceable
  by better evidence. It does not mean optional or undefined.
- Exact mission values block final qualification, mission thresholds, and
  release—not initial architecture, component comparison, or schematic work.
- The workhorse role does not reverse the deletion rule or justify generic
  expansion. Every interface still needs a named function and fault boundary.
- The 100 km case should select short-duration pressure, thermal, sensing, upset,
  and evidence controls. It must not import orbital-lifetime architecture.

### Consequences

- MCU, sensor, storage, power, connector, and mechanical comparisons can proceed
  against one stated envelope.
- Battery budgeting must support eight powered hours plus four hours of reduced
  recovery duty.
- Logging design must distinguish long low-rate ground operation from at least
  thirty minutes of full-rate flight evidence.
- Part selection targets industrial temperature margin, while board-level test
  covers the narrower accepted powered range.
- Reuse requires cycle records, post-flight inspection, acceptance testing, and
  retirement criteria; it is not uninspected indefinite reuse.
- The first mature vehicle creates a mission-overlay artifact. Simulation and
  measured environments replace affected provisional values before release.

### Unknowns

- First vehicle and date for the first mission-specific overlay.
- Actual vibration power spectral density and shock waveform.
- Quantitative reliability targets and vehicle-level hazard allocation.
- Exact low-rate/full-rate log schedule needed to meet the energy and storage
  budgets.

### Next checkpoint

Use the provisional envelope in the MCU and sensor resource matrix. Record which
candidate passes each value, where it depends on an external sensor or power
domain, and which later mission evidence could overturn the choice.

### Evidence

- [`current-system.md`](current-system.md)
- [`Kármán-line mission hardening report`](docs/karman-line-mission-hardening-report.md)
- [2025 EuRoC Competition Rules](https://euroc.pt/wp-content/uploads/2025/03/PTS_EDU_EuRoC_ST_001905_CR_v01-1.pdf)
- [2024 EuRoC Design, Test & Evaluation Guide](https://euroc.pt/wp-content/uploads/2024/04/PTS_EDU_EuRoC_ST_000455_DTEG_v05.pdf)
- Seán's 3 September acceptance of the proposed workhorse role and provisional
  values.

## 2026-09-05 — Reconcile LTS implementation without changing flight requirements

**Context:** Seán authorised document updates after the LTS engineering review.
The Ogma description still placed separate propulsion, GSE and DAQ controllers
on the stand, whereas LTS decisions of 3–4 September now use one unified stand
PCB/primary MCU and no longer require that PCB to fly.

**Correction:** Updated only the test-stand relationship in
[`current-system.md`](current-system.md) and the
[owned interface](interfaces/ogma-foinse-propulsion-boundary.md). CAN A retains
the two-node production Ogma/propulsion boundary; separate unbridged CAN B serves
GSE. Both LTS partitions stop on a shared primary-MCU reset. Linux remains
outside the required local measurement/decision/action path.

**Scope retained:** Ogma flight architecture, Foinse power authority, the
self-governing vehicle propulsion peer, and full-rate local flight-recording
requirements are unchanged. LTS incident-only local recording is a stand
decision, not permission to remove flight evidence. Later flight hardware
requires its own qualification and cannot depend on the stand PC.

**Still proposed/open:** The LTS end-to-end expiring operator-permission scheme,
its timeout and integration with real Ogma need joint review. No such timeout
was adopted for autonomous flight. Exact LTS incident reset/power-loss coverage
is also unproven.

**Next checkpoint:** Review the two interface snapshots together when the CAN
contracts and flight/stand test modes are implemented. No firmware, circuit,
physical test, component choice, commit, push or external message resulted from
this documentation correction.

## 2026-09-05 — Reliability review made executable; source corrections recorded

### Context and authority

Seán requested a deeper independent review, then authorised writing the
findings into project documentation in an executable form. This authorises the
review, work breakdown and evidence templates. It does not accept every new
circuit, exact part, reset policy, recovery allocation or release-gate proposal.

Seán also reconfirmed that Foinse has no microcontroller after Anav asked
whether that boundary had been understood. The power review concerns analogue
and dedicated-function device dependencies. It adds no Foinse MCU or firmware.
No private correspondence was imported into the repository.

### Observed evidence

- The repository has architecture, studies and curated predecessor evidence;
  no Ogma 2 hardware or firmware test result was established by this work.
- The Rev 1 closure records the unexplained aloft reset, subsequent
  recalibration, missing voltage evidence, and valid recovered flash records.
  It does not qualify Ogma's own energetic recovery path.
- ST AN5342 Rev 8 and H5 RAM configuration material describe 32-bit SRAM ECC
  words and reserved SRAM3 check storage. The earlier 64-bit wording came from
  a conflicting statement in ST UM3150 Rev 2, not a measured Ogma result.
- UM3150 limits its documented H5 ECC diagnostic injection method to RAM3.
  The earlier plan for the same injection in every protected bank was not
  supported by that source.
- The study coupled watchdog feeding to logger progress while requiring
  continued flight under a storage fault. It needed an explicit degraded-mode
  policy rather than contradictory unconditional requirements.
- An LTS reconciliation appeared in current-system, the owned interface and
  this log during the work. Its changes were preserved; this review does not
  reverse the unified stand-controller or stand-recording decisions.

### Documentation changes

- Added the indexed reliability review covering fault allocation, reset/time
  semantics, retention/ECC interaction, MCU-less Foinse startup, protection
  coordination, power budgets, sensor validity, physical actuation evidence,
  storage/configuration, installed-bay behaviour and bounded radiation claims.
- Added EX-01–EX-10 with dependencies, required roles, planned outputs,
  controlled bench procedures, measurable closure criteria, numerical inputs
  still needed, and a decision register. All tasks remain not started and
  personnel unassigned.
- Added a reusable verification record for exact configuration, instruments,
  stimulus, limits, raw evidence, failures, interpretation and disposition.
- Corrected the active study's SRAM geometry, unavailable-memory assumption,
  bank-specific ECC test coverage and unsafe blanket retention initialisation
  wording. Marked the watchdog/degraded-logger correction as proposed policy.
- Clarified that communications failure must preserve essential local flight
  functions; losing GNSS aiding need not leave numerical estimates unchanged.
- Corrected the independent-recovery status leak: mission-specific need and
  coverage remain open. No commercial backup was selected or mandated here.
- Indexed the new work from README, docs index and current-system. Flagged the
  mixed prototype/qualification evidence list and proposed separate G0–G3 gates
  without waiving existing flight evidence.

### Interpretation and unresolved decisions

The basic single-board/two-MCU architecture remains coherent. Its main open
reliability work is closing power containment, supported reset/restart classes,
and the available sensing through the unaided flight interval. The accepted
provisional workhorse envelope is unchanged and supports present bench work.

Exact MCU/package, Foinse auxiliary supply topology, memory/time retention,
degraded flight policy, output fault allocation, independent recovery and gate
adoption remain explicit decisions. Tests in the plan are unperformed. No
radiation susceptibility, numerical reliability probability, environmental
qualification or flight readiness is claimed.

### Next checkpoint

Review EX-01's communications-loss, logger-failure, warm-reset and total-power-
loss rows with their actual surviving capabilities. Draw EX-02's MCU-less
Foinse source dependency and EX-03's retention classes. Use those to run the
first externally instrumented, current-limited power interruption and restart
on an identified development assembly with inert outputs.

### Evidence

- [Reliability design review](docs/reliability-design-review.md)
- [Reliability execution plan](docs/reliability-execution-plan.md)
- [Verification-record template](docs/templates/verification-record.md)
- [Corrected hardening study](docs/karman-line-mission-hardening-report.md)
- [Rev 1 flight closure](sources/project/ogma-rev1/ogma-rev1-flight-closure.md)
- Primary manufacturer links and exact source-conflict notes are retained in
  the review and corrected study.

### Documentation verification

- Checked nine changed/new Markdown files: 81 relative links and referenced
  heading anchors resolved; code fences were balanced.
- Verified that the pre-existing project log remains an unchanged prefix.
- Verified preservation of all added lines from the concurrent LTS changes in
  current-system, the owned interface and the log.
- `git diff --check` passed. Changes remain local on
  `docs/reliability-review-execution`; no commit, push or pull request was made
  by this review task. No hardware/firmware test was run.

## 2026-09-06 — Recommendation-first design-review procedure

### Context and decision

Seán asked the model to propose potential answers to each section's questions
using engineering judgment, then let the team guide the choices. He requested
a formal operating procedure in Ogma 2 and the saved text verbatim in chat for
his own Stream record.

The active collaboration procedure is recommendation-first: concrete default,
reason, cost, material alternative, uncertainty, validation and next action.
Review one coherent section at a time unless a batch is requested. Distinguish
what needs reading, an external wait or bounded model work; do not hand the
team a blank requirements questionnaire when a defensible proposal is possible.

### Changes and boundaries

- Added [the operating procedure](docs/design-review-operating-procedure.md),
  linked from AGENTS, README and the document index.
- Kept recommendations, accepted architecture and chronological evidence
  separate. No EX-01 fault response, independent-recovery policy, staging
  inhibit or release gate was accepted by documenting this working method.
- Included coordination of overlapping repository work and a single writer
  for shared staging/commit/push operations, following the prior coordination
  issue. No other task was messaged or assigned by this update.
- Preserved the pre-existing execution-plan edit. No hardware, firmware,
  architecture, test result, commit or push changed in this documentation task.
- The procedure is returned verbatim for Seán to capture if he chooses. No
  Stream or Connective Tissue write is performed.

### Next checkpoint

Continue the EX-01 conversation from the proposed answers already presented.
Resolve the consequential technical choices explicitly, then prepare the
bounded contracts and tests required by those choices.

## 2026-09-06 — EX-01 policy accepted

### Decision and authority

After reading EX-01, Seán explicitly agreed with all recommendations, had no
notes, and requested that the agreement be recorded before moving on. This
accepts the EX-01 policies already presented. It does not accept every proposal
in the broader reliability study or close unperformed engineering work.

### Accepted policies

- Unexplained communications, logger, flight-MCU reset or flight-power faults
  stop initial launch preparation. Required recording must work before launch.
- In flight, contain communications failure and continue local flight work;
  allow only bounded electrically safe communications-only recovery. Persistent
  failure leaves the branch disabled; telemetry loss does not justify a flight
  MCU reset.
- Contain bulk logger failure, end failed transactions within their bound and
  enter supervised degraded recording. Preserve minimal evidence where hardware
  allows it; do not reset the flight controller repeatedly to regain a log.
- Essential acquisition/validation, estimation and phase-policy progress earn
  watchdog feeding. A degraded logger/radio is not an unconditional in-flight
  reset trigger, nor an excuse to conceal a stalled core.
- Use a bounded validated in-flight restart without pad recalibration, a new
  launch datum, a GNSS-acquisition wait or a full-log scan. Complete power loss
  means primary unavailability; power return is not presumed a warm restart.
- Any in-flight flight-MCU reset inhibits further sustainer ignition for that
  flight. Recovery may resume only from a validated phase-specific path; reboot
  alone grants no actuation authority. The accepted cost is possible loss of
  the staging objective after a recoverable reset.
- Require appropriately independent recovery on initial flights with live Ogma
  recovery authority and on the Kármán mission. Later ordinary-flight changes
  require vehicle review, not an automatic successful-flight-count rule.
  Primary Ogma recovery still requires its own qualification.
- Adopt G0 inert bench, G1 engineering PCB, G2 installed qualification and G3
  unit/mission release. No existing flight obligation is waived.

### Documentation and evidence status

Created the [initial fault contract](interfaces/flight-fault-contract.md) with
FF-01–FF-04 and explicit remaining closure work. Updated current-system, the
execution plan/decision register, discovery links and current review position.
Added dated acceptance notices to the studies; previous log entries remain
unchanged. The operating procedure now points to EX-02.

EX-01 policy is accepted, but the package is not closed. Numerical detection,
interruption and restart limits, mission-specific independent coverage, exact
hardware/software, implementation owners, independent reviewers and tests
remain open. No commercial recovery device, Foinse supply topology, MCU, circuit
or firing threshold was selected. No physical test, flight release, purchase,
cross-project authority change, commit or push occurred.

### Next checkpoint

Present EX-02's recommended source dependencies, protected branches and source
handling for review. Its recommendations remain proposals. After acceptance,
produce the bounded power contract and first inert, externally instrumented
source-transition/branch-containment experiment definition. Exact component and
fixture limits must precede fault injection; final vehicle simulations need not
block initial characterisation.

## 2026-09-06 — EX-02 accepted; preregulator and low-noise LDO retained

### Decision and correction

Seán accepted the five EX-02 recommendations, then clarified that switching
preregulation followed by a low-noise LDO is wanted because it came from the
first external Ogma 1 review. That explicit correction supersedes the model's
direct-buck-first recommendation. No direct-buck implementation or hardware
change had occurred.

Accepted: autonomous MCU-less Foinse source/protection without Ogma software or
returned 3.3 V; retain the protected auxiliary return subject to device-level
feasibility; bound communications/RF, bulk storage and auxiliary-branch faults;
keep USB servicing free of actuator-power/backfeed/unintended-charge paths;
allocate bounded core hold-up and the existing 8 h + 4 h energy budget.
The preregulator/low-noise LDO cascade remains the logic baseline. Exact devices,
intermediate voltage, module versus IC and VIOC use remain open.

### Source evidence and its limits

Seán supplied the first reviewer's power/mechanical comments and a second
reviewer's packaging feedback. The first recommended compact switchers and
low-noise LDO post-regulation where noise matters, and warned about unsupported
TO-220s and heavy components. The second discussed assembly order, captive
metal spacers/nuts, harness restraint and realistic printed-material/load
assumptions. Seán's supplied reply clarified that the sled was a visual mock-up
without modelled flight loads. These are attributed reviews and replies, not
measurements or proof of implementation.

ADI's primary documentation confirms that LT3045-1 has VIOC whereas LT3045 does
not. LT3045-1's documented VIOC differential starts at 1 V, so the approximately
3.8 V to 3.3 V placeholder cannot be assumed to implement that configuration.
The cited TI SNVA935A body was not retrievable in this pass. No detailed claim
from it is presented as independently checked.

The [external-review note](docs/rev1-external-review-lessons.md) preserves source
roles, available links and unknown dates. XT30 with a cable tie remains
historical candidate advice; it does not replace the current connector rule.
The packaging questions feed EX-08 without making every comment architecture.

### Documentation and remaining engineering

Created the [initial power contract](interfaces/power-contract.md): three
functional source drawings, branch requirements, source-state table, numerical
budget framework, candidate constraints and first inert PWR-01 definition.
Updated current-system, the owned interface, execution status/decision register,
studies, indexes and the review procedure. Existing edits and prior log entries
remain intact. Foinse/propulsion ownership and LTS behaviour are unchanged; exact
Foinse device feasibility still needs its owner's review.

EX-02 defaults are accepted, but the work package is not closed. No real pack,
current, noise, hold-up, startup or fault result exists from this work. No part
purchase, physical test, firmware change, commit, push, Stream write or flight
release occurred.

### Next checkpoint

Continue with EX-03's proposed reset, retained-state and time semantics. In
engineering, fill the power contract with exact candidate-device limits and
mode currents, then define the rated inert fixture before applying faults.
Retain the preregulator/LDO chain while testing its implementation; bring back
contradictory evidence rather than silently deleting it.

## 2026-09-06 — EX-03 accepted; first host checkpoint replay

### Decision

Seán accepted all five EX-03 recommendations and requested the next section.
Accepted: distinguish reset/power-loss classes; use two alternating small
checkpoints in verified MCU retention independently of bulk logging; preserve
local mission time without depending on GNSS; make new-flight preparation and
clearing prior authority deliberate and disarmed; retain attempted action
separately from observed physical result. External FRAM is not the default.
Mechanism-specific replay/suppression policy remains open under EX-07.

The [reset contract](interfaces/reset-recovery-contract.md) records those
decisions and remaining implementation work. Current-system, the execution
plan/decision register, indexes, studies and review procedure now point to
EX-04. EX-01's staging inhibit and EX-02's preregulator/LDO direction remain
unchanged. No adjacent project's authority changed.

### Executed model and observed result

Added and ran the [non-actuating host checkpoint model](tests/reset_replay/README.md)
using Python 3 with no external dependencies or device access. All 12 test
methods passed. Coverage includes 420 interrupted-update cases across four
synthetic phase transitions and sequence wrap, 35 interrupted first-checkpoint
cases, 264 single-bit slot-corruption cases, identity/time validation,
reset-class gating and preservation of attempted versus observed action.

Removed slot invalidation temporarily in memory and reran the interruption
test: 12 expected failed subcases, no execution errors. This demonstrates that
the test detects early publication through a reused valid marker. The source
remains unmutated. Commands and model assumptions are in the test README.

### Limits and unresolved work

The model assumes ordered atomic byte writes and supplies power validity and
mission time as test inputs. Its encoding, generation arithmetic, synthetic
times and phase labels are fixture choices, not selected flight firmware.
It returns a data candidate and has no actuator API. It does not establish
actual RAM/ECC behaviour, clock survival, cache/DMA ordering, MCU startup,
estimator reconstruction, restart latency or physical deployment.

EX-03 is not closed. Actual bank/clock/supply, production schema, checkpoint
frequency, interruption/age/error limits, implementation owners and independent
review remain open. No firmware was flashed, physical test run, part purchased,
commit/push made, Stream record written or flight authorised. Existing edits
and previous log entries were preserved.

### Next checkpoint

Review EX-04's recommended MCU family/package, memory placement, timing margin
and provisioning approach. Its exact-part resource work must establish whether
the accepted reset and power contracts can be implemented. Port the model's
tested invariants onto actual firmware and hardware without presenting the
host result as proof of the port.

## 2026-09-06 — EX-04 accepted; initial MCU resource reservation

### Decision

Seán accepted all EX-04 recommendations. Start with STM32H563VIT6/LQFP100
as the first exact allocation candidate and compare H573 directly. Start flight
and communications in the same MCU family; a smaller communications device
needs a justified saving. Require simultaneous resource allocation, checked
critical-state/stack/checkpoint placement in verified ECC regions, an initial
30% scheduling and critical-memory reserve, workload/power-based clock choice,
and reversible development provisioning with exact configuration and errata
records. Production MCU selection remains open. Neither MCU is redundant.

### Work and evidence

Created [MCU resource and timing results](docs/mcu-resource-and-timing-results.md).
It compares exact candidates using ST DS14258 Rev 6 and DS14121 Rev 5,
distinguishes the H563VIT6 non-SMPS core-supply pinout from Q-suffix variants,
reserves digital resources for both roles, and records the protected-memory
budget and first ES0565 Rev 8 applicability items. The external
preregulator/low-noise-LDO decision remains unchanged.

The initial map proposes buses and GPIO reservations, not final circuits or
released physical pin numbers. A local consistency check found 40 distinct
flight port pins and 20 distinct communications port pins with no duplicates
within either table. Per-bank and combined memory-reserve arithmetic passed.
Checked 104 local Markdown link targets across eight updated documents; all
resolved. The existing 12 checkpoint-model test methods still pass.
Whitespace checks passed. The prior 73,118-byte log prefix was unchanged.

Manufacturer PDFs were readable through web extraction. Direct downloads and
the screenshot attempt failed; no visual symbol/footprint audit was performed.
There was no target build, fitted-part inspection or hardware measurement.

### Limits and next checkpoint

EX-04 is not closed. ADC and circuit-level output/control needs, DMA routing,
physical pin/symbol audit, full errata applicability, memory placement,
retention, clocks, power and timing remain open. Host checks establish only
table consistency, arithmetic and the previously scoped checkpoint semantics.
They do not establish whole-board fit, schedulability or flight reliability.

Current-system, active indexes, review status and the hardening study now
record EX-04 acceptance. H563-first supersedes the study's H573-leading ranking;
extra security hardware is not presumed to provide better flight reliability.
Previous log entries and unrelated edits were preserved. No commit, push,
purchase, physical test, Stream write or flight release occurred.

Continue the conversational review with EX-05: measurement validity, sampling
and unaided coast. Its rates and limits feed the MCU timing/resource work;
EX-07 supplies the remaining output-circuit allocation. Those recommendations
remain proposals until explicitly accepted.

## 2026-09-07 — Complete architecture accepted; first-PCBA block tests; library feasibility

### Explicit decisions

Seán read and accepted the complete 6 September architecture review, including
its qualifications and tradeoffs. He separately endorsed the connectors. All
rewritten EX-01–EX-10 recommended answers now form the implementation baseline;
there is no remaining sequential approval round merely because the older
checklist stops at EX-04. Explicitly deferred questions and unmeasured claims
remain deferred and unmeasured.

Seán changed the build sequence: no separate mini-PCBs/coupons before the first
full PCBA order. Functional-block tests move to that first assembled hardware.
Pre-order pin/footprint/rating, inhibit, schematic/layout, mechanical and
assembly checks remain. The first PCBA is an engineering test article, not a
qualified flight assembly. Tests are moved, not silently counted as passed.

Seán states he sent Anav the firmware handoff and Anav can start coding the
architecture. This records that statement, not independently observed delivery
or coding progress. Preserve the hardware interface and leave firmware
implementation to Anav and his chosen collaborator.

### Current authority and files

Added the [acceptance record](docs/architecture-acceptance-2026-09-07.md), including
exact major parts/connectors, source hashes, amended sequence and retained
qualifications. Updated current-system, reader indexes, affected fault/power/
reset/vehicle interfaces, execution status and the review procedure. Earlier
candidate discussions and test ideas remain explicitly labelled as preceding
material where superseded, rather than erased or presented as current choices.

The original seven-chapter review, full MCU CSVs and research remain unchanged
under local `../architecture-review-2026-09-06/`. This is a declared local
dependency; curate its implementation inputs before a self-contained repository
handoff. No private source-history dump was imported into the repository.

### Library feasibility: observed, not imported

Seán asked whether the Ultra Librarian-to-KiCad work can be handled for him.
Read-only audit found KiCad 9.0.6, 11 stock symbol/family matches against 40
unique MPNs in the partial core table, and six stock matches for nine distinct
PCB connector footprint requirements. The selected H563 symbol is the non-Q
100-pin variant. Native parsing confirmed its 100-pad footprint and the six
connector footprints. This is availability/parse evidence, not completed
datasheet or land-pattern validation.

The exact Samtec pair and Nano-Fit 1053111102 footprints are missing. Old Croí
contains reusable MS5607 assets and embedded ADXL375 data; reuse still needs
checking. Its old library tables contain another computer's absolute Windows
paths and must not be copied. Three stock Micro-Fit STEP references are absent.
The old-board parse emitted a wxApp assertion while returning the expected
objects; that limitation is retained in the audit.

The [library preparation note](docs/kicad-library-preparation.md) records exact
native identifiers, gaps, verification and portable project-local workflow.
No library files or global configuration were changed. The next bounded model
deliverable is checked project-local symbols, footprints and available models,
with exact MPNs and explicit per-part verification status.

No schematic/PCB routing, firmware implementation, hardware test, purchase,
commit, push, upload, external message, Stream write or flight release occurred.
Earlier log entries and unrelated working-tree changes were preserved.

Documentation checks: 101 local link targets resolved across 12 changed/new
documents (only this entry checked in the log). Whitespace checks passed.
The preceding 76,087-byte log prefix retained its exact SHA-256. No hardware
or firmware test was rerun for this documentation-only change.

## 2026-09-07 — Project-local KiCad library build, draft handoff

Seán's “GO” authorised the library implementation after the feasibility and
effort-level discussion. Architecture, exact selected parts, firmware ownership
and the first-full-PCBA test sequence remain unchanged.

Created `hardware/` with portable project-local symbol/footprint tables,
`Ogma2.kicad_sym`, `Ogma2.pretty`, available local models, source/verification
manifest, inventory, deterministic generators and structural/native checks.
Curated unchanged copies of the four accepted parts/connector/MCU CSV inputs;
did not import private context dumps. Stock assets retain KiCad licensing and
attribution. Public PDFs and temporary renders remain outside this repository.

Observed result: **46 selected PCB symbols, 44 assigned footprints, 27 parts
with resolved local models**, plus 11 off-board inventory entries. This is the
major-parts inventory, not a finished schematic BOM. Exact MPNs are retained;
no easier-to-import component was substituted.

Drawing-derived footprints include both Samtec halves, BMP390, SAM-M10Q,
E22-900M22S, two crystals, CSD17318Q2, LM73100 and TPS1H100B. The latter's
candidate stock mask opening differed from current TI PWP0014K; replaced it
with drawing-derived copper/mask/paste geometry. Samtec contact groups have six
tails each and opposite pin-1 orientations. The GNSS land pattern includes its
four-per-pad paste apertures. Radio host-land dimensions are explicitly a
design choice because the source gives module pads, not a host-land drawing.

**Unfinished:** TPSM63603RDHR stepped-corner/stencil geometry and the exact
Nano-Fit 1053111102 footprint are deliberately unassigned. TPSM source drawings
were obtained; transcription/audit remains work. Nano-Fit direct PDF/visual
retrieval repeatedly failed although source text was accessible. No retention
coordinates were invented. Stock-family dimensional/pin audits, stated custom
geometry qualifications, 3D coverage, support-part selection and manufacturing
checks remain open. [Review notes](hardware/libraries/review-notes.md) identify
the exact next work. This is a draft library, not fabrication approval.

Verification observed: KiCad 9.0.6 exported all 46 symbols and 44 footprints.
All 1,149 structural checks passed; both accepted 100-pin allocations match
the H563 non-Q package after GPIO/debug-name normalisation. No alternate-function
or firmware-timing validation is implied. Native KiCad loaded 44 footprints
and found no unexpected differently numbered front-copper overlaps. USB's
four common VBUS/GND pairs are explicit checked exceptions. Initial testing
emitted a wxApp assertion; framework initialisation and an allowed rerun gave
a clean native result. Native/structural tests do not replace schematic ERC,
board DRC, manufacturer drawing review or physical measurements.

No schematic/PCB routing, global KiCad configuration change, firmware work,
hardware test, purchase, commit, push, upload, external message or Stream write
occurred. Existing unrelated changes and all preceding log text were preserved.
The preceding 79,992-byte log prefix has SHA-256
`fb5fd18e2ae5a0480e6c4d6cd87b612a67d118e1c6d91a7b84a6bfeda8d5f6a6`.

### Same build — regulator footprint added after final geometry pass

Completed the TPSM63603RDHR draft footprint after cross-checking the annotated
RDH0030A land pattern against vector coordinates in TI's PDF. Added nonuniform
pad placement, stepped corners and the specified reduced exposed-pad paste
apertures. Same-number primitives approximate the corner fillets; final
stencil/assembly review remains explicitly open. No architecture changed.

Current coverage is **46 symbols, 45 assigned footprints and 27 parts with local
models**. Nano-Fit 1053111102 is the sole blank footprint assignment. All 1,194
structural checks pass. KiCad exported the additional footprint; the clean
native geometry run now covers 45 footprints. Earlier 44-footprint checkpoint
and its unfinished-work record remain above as history.

## 2026-09-07 — Native schematic pilot after GUI-control experiment

Seán created `hardware/Ogma2/Ogma2.kicad_pro`. Initial GUI work saved its
title block and one blank power sheet; canvas/keyboard control proved unreliable.
Seán then explicitly approved direct native schematic-file authoring and review.
No further GUI navigation was used for this implementation.

Built seven editable sheets, 26 footprint-assigned symbols, a detailed CAN block
and five accepted CAN-related flight-MCU connections. The power, sensors/storage,
communications and output sheets remain explicit placeholders. Other 95 MCU pads
remain unfinished. No architecture/pin-allocation or firmware-ownership change.
Foinse2 remains separate; the project PCB remains the original empty file.

CAN includes the accepted TPS2553DBVR-1 limiter, TXU0304 boundary, TCAN3413,
fixed 120 Ω termination and JST GH mapping. Added draft support values, one
ESD2CAN24DBZRQ1 TVS proposal, rail/ground loops, signal pads and a removable
positive supply link. The 210 kΩ resistor's tolerance-inclusive estimate is
109.2–152.3 mA, not an exact 110–150 mA assembly guarantee. Aggregate fault
pull-up, supply/ramp containment, installed grounding and final part/drawing
audits remain open. These are circuits to review/test, not hardware results.

Observed checks: KiCad 9.0.6 parses and exports all seven sheets; 79 independent
expectation checks pass on its exported netlist. A negative test deliberately
swapping connector H/L is rejected. Full-board ERC reports 108 errors, zero
warnings: 104 on the unfinished MCU sheet and four undriven-power checks on CAN.
CAN has no dangling-pin, library or footprint-link warnings. Nothing was excluded
or falsely driven to make ERC green. All PDF pages were visually inspected.

Early native checks caught missing T-junction segmentation, then an accidental
CAN termination connection to the other line; both were corrected and exact H/L
node sets retested. The checker was corrected to recognise the stock MCU's five
stacked VSS pads as a floating internal node, not external ground wiring.
System Python's XML loader failed; bundled Python completed the checks.
Local font-configuration warnings did not prevent native exports.

[Pilot status](hardware/Ogma2/schematic-status.md) records source citations,
remaining work, reproduction and editing boundaries. The builder refuses the
live project directory; future generation must be reviewed before installation.
The nested project has local library tables plus a relative model-path symlink.
Project-memory updates distinguish this implementation checkpoint from the
unchanged accepted architecture. Original GUI drawings and full native reports
remain in local `../schematic-work-2026-09-07/`; rendered output is Git-ignored.

Next: source/regulation/supervision and flight-MCU support circuitry. No PCB
layout, hardware test, firmware work, purchase, commit, upload or flight release.
The preceding 84,039-byte log prefix has SHA-256
`a2f129708f93e2d3abb4bf865a8786f339da6ea546d6e28350adc876f4c9501a`.

## 2026-09-07 — Croí2 full engineering schematic draft

Seán authorised the remaining schematics after the CAN pilot. Expanded the
existing native project to **42 pages**: root index and 41 functional sheets.
Both complete MCU allocations/support networks, source protection/mux/bootstrap,
4 V preregulation, held core and three main LDO domains, five sensor branches,
NOR, reset/watchdog/debug, MCU crossing, USB/GNSS/radio, CAN, auxiliary monitoring,
rail ADCs, indicators and energetic/servo topologies are drawn. Foinse2 itself
remains a separate future CAD project. No GPIO allocation or firmware work changed.

The installed draft contains 612 physical symbols, including 29 DNP components
and 51 test points, plus 19 ERC power annotations. These are schematic counts,
not an orderable BOM. Local Croí protection for standalone operation, extra
powered-off boundaries, comms supervision and the servo switch/buffer supply are
circuit-level implementation proposals. Support values, cost and physical area
still need review; authorisation to draw them is not another team-approved freeze.

Physical arm hardware, source contacts/proof contact and group protection remain
unspecified. No power source is connected to the recovery, staging or servo arm
rails. All four output-energy links, pulse/current-setting resistors and twelve
continuity injection/return resistors are DNP. No operative firing, continuity,
single-fault no-fire or servo-load capability is claimed. Exact load/arm choices
need team input. Nano-Fit and the DNP transducer still lack exact footprints;
C1403 has only a volume reservation pending a real hold-up capacitor selection.
Input transient/fuse coordination, LDO shutdown reverse-voltage protection,
USB CC/service behavior and comms local fault-pin semantics remain explicit gaps.

Observed verification from the **installed project**: KiCad 9.0.6 exports all
42 sheets; **2,116 physical pin checks and 275 architecture checks pass**.
Generated pin expectations verify drawing connectivity; separate assertions
verify both accepted MCU CSVs with documented physical-net aliases, CAN node
sets, source-policy truth tables, reset/staging connections and DNP states.
Negative tests reject a swapped CAN contact and a short bypassing the MCU VDDA
link. They are regression checks, not independent proof of all circuit behavior.

Native ERC: **four errors and four warnings**, no exclusions. Errors identify
the four deliberately unsupplied output domains. Warnings identify ST's two
grounded mode-1 auxiliary pins, BMP's grounded address strap and the unresolved
servo arm-source label. No other dangling-pin, off-grid, library-link or
footprint-link findings remain. Nineteen legitimate external/component-mediated
source annotations let ERC traverse modeled supply paths; none pretends the
missing output source exists. Four support-symbol views retain physical
pin/name/footprint maps while marking repeated internally common output contacts
passive, leaving one power-output pin for ERC. The canonical major library is
unchanged. All pages were visually inspected, including re-rendered corrections.

Construction exposed and corrected a TPS26630 MODE strap which would have
selected retry instead of latch-off, a generated VDD bus bypassing the VDDA
link, incomplete inherited-symbol graphics/pins, label alignment and page-frame
collisions. The VDDA fault now has a negative test. System Python's XML loader
failed; bundled Python ran the checks. Local font warnings did not prevent
exports. No analogue simulation, target timing, thermal, ESD, inrush or hardware
test was performed, and no such success is inferred from native parsing/ERC.

[Current schematic status](hardware/Ogma2/schematic-status.md) records the page
map, circuit proposals, primary sources, remaining closures and reproduction.
[Native check report](hardware/Ogma2/full-checks.json) records the schematic
hashes and installed netlist hash. The previous
[pilot status](hardware/Ogma2/pilot-status-2026-09-07.md) is preserved as history;
the older log's pilot-status link now leads to the superseding current status.
The complete pre-install project is recoverable from local
`../schematic-work-2026-09-07/pre-full.99GULg/`. Native reports and the reading
PDF are under `hardware/Ogma2/output/`, ignored by Git. Builders refuse the live
project directory: regeneration must be reviewed before applying any delta.

The original project settings, library tables and empty PCB are byte-for-byte
unchanged. PCB SHA-256:
`3e491cd8085eff0d6c95f0a11a135421cbcfce4c5620e6356c3896e122f1772b`.
No GUI control, PCB layout, firmware changes, purchase, Git staging/commit/push,
upload or external message occurred. Current-system and reader entrypoints now
describe the engineering draft without promoting provisional support choices.

Next: review the power-entry circuit and collect the concrete arm/load choices;
close the named schematic/library gaps before manufacturing release. Functional
block qualification remains on the first full engineering PCBA with current
limiting and inert loads, not separate pre-order mini-PCBs.
The preceding 87,107-byte log prefix is unchanged, SHA-256
`9876d277e698df5451fb44f691cf5f336b77be882b281b35a66eb3318a4ec293`.

## 2026-09-07 — Foinse2 schematic, independent board repos and PCB floorplans

Seán authorised Foinse schematics, a Croí/Foinse subrepo split inside the existing
Ogma2 umbrella, portable symbol/footprint/model linkage, basic board outlines
and scripted functional-block placement. He was asleep; the stated unattended
interpretation was local-only repositories, no invented remotes or uploads,
and the accepted report's provisional 60 × 120 mm / 60 × 80 mm outlines.

Active projects are now `hardware/croi2/Croi2.kicad_pro` and
`hardware/foinse2/Foinse2.kicad_pro`. Each is an independent Git repo on
`schematic-layout-draft`, with no commits or remote. The umbrella ignores both;
they are not yet registered submodules and a parent clone does not fetch CAD.
Remote creation and reviewed submodule registration remain for later authorised
publication. No old Ogma/Rev 1 repository was touched.

Foinse's new 11-page, 110-symbol engineering draft draws two autonomous source
paths: 2S avionics and separate 6S propulsion, each TPS26630/CSD18540 reverse
protection, source-powered enable, open MODE for latch-off, input TVS, protected
discharge shunt and probes. INA228 monitors are 0x40/0x41; ADS1115 is 0x48;
TMUX1511 isolates voltage inputs with the monitor rail absent. TCA4307 and all
monitoring use Croí's protected auxiliary supply. No Foinse MCU, CAN endpoint
or monitoring prerequisite for source startup was added. The accepted Samtec
contact map is preserved. Pack-positive branches never join.

New draft connector proposals are a two-way Micro-Fit 430450200 raw propulsion
output and four-way JST GH dedicated thermistor connector. They are recorded
as model-authored implementation proposals, not silently promoted to another
team-approved inventory. Nominal thresholds, current limits, shunts and TVS
choices likewise need circuit/rating review. The 3 A-class 6S source is not an
allocation for unspecified valves. Regulated 24 V conversion remains conditional
on the coil schedule; charging remains external matched balance chargers and
a passive pack-specific harness. No unspecified converter, charger, balance
connector or independent-recovery source was invented.

Croí retains its 42-sheet connectivity and frozen MCU allocations. Its native
project was renamed from Ogma2 to Croi2, instance project names updated, and
overlong title-block titles shortened without changing full sheet headings or
electrical intent. Both board repos vendor embedded symbols, every assigned
footprint and all available existing 3D models. All active library/model paths
are project-relative, without a parent-library symlink. Board manifests retain
hashes, source roles, licences and explicit model gaps. Some exact 3D models
remain absent; no decorative substitute was called an exact model.

Both PCBs have closed rectangular Edge.Cuts outlines, four copper layers and
1.6 mm thickness. Samtec origins are at Croí's bottom / Foinse's top board edges,
opposite orientations, for a nominal 7.39 mm board-edge gap. No mounting-hole
pattern, tracks, vias or copper pours were added. Functional-sheet PCB groups
retain each part's schematic UUID path and all repeated-pad net assignments.
Croí imports 610 footprints in 41 groups: 529 inside, 81 explicitly staged
beside the outline. Foinse imports 109 in ten groups, all inside. The coarse
packing is not proof of fit impossibility or of routing/assembly feasibility.
The GNSS reference rectangle is on Dwgs.User, never a ground split or cutout.

Molex 1053111102 remains footprint-blocked on both boards. Bounded attempts to
obtain a visually readable exact manufacturer drawing failed; extracted text
does not establish retention-hole geometry. No 105309 lookalike was substituted.
Both layouts reserve visibly labelled, unverified space without electrical pads.
Croí BZ9001 remains unselected DNP; C1403 remains a volume allocation rather
than a fully selected hold-up capacitor. Those gaps survive this folder change.

Observed native checks: Croí 2,116 physical schematic pins / 275 architecture
checks, four ERC errors and four warnings unchanged; Foinse 304 pins / 102
boundary checks, zero ERC findings and no exclusions. Foinse's negative test
rejects merging the two battery-positive rails. Saved-PCB checks verify 2,183
Croí and 364 Foinse numbered pads, UUID/value/DNP/BOM linkage, local model paths,
library hashes, group membership, outlines/layers and courtyard/drill
reservations. Model references resolve locally: 554 Croí and 95 Foinse instances.
Native schematic parity reports only the known missing footprints.

Initial native checks caught stock test-pad BOM attributes differing from the
schematic, backside parts beneath debug-hole footprints, and long title-block
text crossing the page frame. Those were corrected. DRC findings were not
hidden: fine-pitch pad clearance against default rules, 0.2 mm thermal-via
drilling versus default 0.3 mm constraints, and Croí USB/library/cosmetic issues
remain. Unrouted-item report counts can be capped. There is no clean DRC,
thermal, analog, RF, ESD, surge, fuse, charging, vibration or hardware claim.

The complete original `hardware/Ogma2` directory, including its original empty
PCB, user settings, pilot records and native reports, is recoverable under
`../schematic-work-2026-09-07/two-board.8O7gAe/original-Ogma2/`, with the matching
library tree beside it. Original PCB SHA-256 remains
`3e491cd8085eff0d6c95f0a11a135421cbcfce4c5620e6356c3896e122f1772b`;
project-settings SHA-256 remains
`e9510236e90b16fbaff736efb2cee26e6dd0fdc9b23da60fe85bd298b6f4c48a`.
Older log links naming `hardware/Ogma2` refer to that archived location; the
[current hardware entrypoint](hardware/README.md) routes to the active repos.

Seán can begin detailed placement from the grouped files, while the named
electrical/library/mechanical gaps close before ordering. Functional testing
still uses the first full engineering PCBA, not new pre-order mini-PCBs. No
firmware, purchase, GUI automation, Git staging/commit/push, upload or external
communication occurred. Project-memory work updated active routing/status;
it did not convert draft implementation details into new approved requirements.
The preceding 92,363-byte log prefix is unchanged, SHA-256
`7846e53cc9e0ab387084a42a7a2da4d7eb348758a1ab3e48895e534daae17238`.

Final readback addition: the native Samtec pair check passes all eight opposing
contact positions and net assignments, including all six tails per contact.
Comparing Croí's 42 schematic trees against the recovery snapshot finds only
the intended project-name and presentation-title changes. An exact project-file
comparison exposed that native `SaveBoard` had rewritten the project settings,
dropping the schematic/ERC sections while populating board defaults. The
original schematic/ERC and other non-board settings were restored; only the
new project filename, current 42-sheet index and native board defaults differ.
The builder now sets `aSkipSettings=True` and asserts that saving a PCB leaves
the project file byte-for-byte unchanged. The original archived settings and
the 92,363-byte pre-turn log prefix remain intact.

The corrected save call passed an isolated native regression test: the complete
project file remained byte-identical. Croí ERC was rerun with its restored
settings and still returned the same four errors and four warnings. Final
schematic PDFs were visually inspected across all 42/11 pages. Front/back
placement previews use the final saved boards; older exports and placement
attempts remain outside the active repos in the recovery work directory.

## 7 September 2026 — standalone current evidence, indication, time and layout references

Seán asked for an ordered PCB-layout reference pack, original manufacturer
layout pages, a sensing/indication/RTC judgement carried through the documents
and CAD, and a new self-contained firmware handoff for Anav. He explicitly
authorised reasonable implementation decisions while away. This is model-authored
engineering work under that authority, not a claim of Anav's review or hardware
qualification. No MCU allocation or accepted connector pinout changed.

Native inspection found the existing Croí protected-battery ADC, three status
LEDs, an unselected buzzer/transistor circuit and flight LSE/internal RTC.
Ogma 1 Foinse firmware identifies ACS71240 sensing, with 132 mV/A, 1650 mV zero
and eight-sample averaging; this establishes the design precedent, not installed
calibration. Seán's reported current/servo/reset observation remains attributed
to him, not a new bench measurement.

Implemented recommendation: move the AV INA228 and 5 mΩ shunt from Foinse to
Croí. U7101 is INA228AIDGSR at 0x40; R7101 proposes WSLP2512R0050FEA. Both
mechanically exclusive source inputs feed the common reverse blocker/eFuse,
then this shunt, then VBAT_PROTECTED. Future arm feeds must originate after the
shunt, but their physical source/arm circuits remain unfinished and all four
output-energy DNP links remain. Foinse's 2S output now reaches its Croí connector
without a duplicate shunt. Propulsion R2011/U5001 at 0x41 and ADS1115 at 0x48
remain on Foinse. Source protection stays autonomous and MCU-less.

The Croí monitor uses the protected AUX side of the existing optional I²C bus.
Firmware must enable historical FOINSE_RETURN_EN even standalone. External bus
failure can also lose this local measurement; it is bounded diagnostic evidence,
not an essential flight or firing dependency. INA VBUS measures reverse-protected
pre-eFuse input; PA0 measures post-shunt protected voltage. USB, charging,
propulsion and upstream protection quiescent/leakage currents are outside Croí's
measurement. Local capacitors can delay the battery response to load events.
Current is electrical corroboration, never proof of motion/ignition or permission
to retry an energetic action. Preserve sample gaps after AUX loss/reset.

Retained three direct GPIO LEDs, proposed green/red/amber, and added hardware
green PWR D9301/R9301. LED MPNs/brightness remain open. Selected passive
CPT-9019S-SMT-TR for pitch-controlled ground tones, using existing PD6/Q9001
with R9005 discharge and D9002 clamp. No NeoPixel or display. PD6 is a frozen
GPIO, not a hardware PWM allocation; bounded timer-driven ground chirps only,
silence before flight acquisition/calibration. The exact manufacturer-derived
9 mm piezo footprint is local to Croí; no exact 3D model was invented. Its
−30 to +70 °C operating grade is an explicit nonessential-indication exception.

No external RTC or backup cell added. Keep flight internal RTC/LSE for qualified
reset continuity, HSE-derived monotonic fast time for acquisition/deadlines, and
optional GNSS time mapping. The held-3.3-V backup domain cannot preserve time
after complete source loss. Illustrative HSE 100 ppm gives 90 ms/15 minutes;
provisional LSE 200 ppm allows 180 ms/15 minutes pending measured temperature,
load and startup evidence. Room-temperature ±20 ppm is not a full-temperature
bound. Neither timing allowance is a tested guarantee.

Current-logging starting proposal: range 0, 100 µA current LSB, calibration
register 6554, 150 µs shunt/bus conversions with averaging 16, 100 Hz records.
Optional 500 Hz bursts remain bus-budgeted, bounded and nonblocking. Independent
arithmetic gives 96,672 B/s normal recorder allocation and 180,587,776 bytes
for the retained mission budget before bursts; 30 seconds aggregate extra burst
capture adds 230,400 bytes. These fit the 256 MiB NOR minus 64 MiB reserve.
[Calculation results](hardware/sensing-revision-calculations.json) are arithmetic,
not throughput or measurement evidence. Anav retains firmware implementation.

Updated [decision/reasoning](docs/sensing-indication-time-review-2026-09-07.md),
[ordered layout guide](docs/pcb-layout-guide.md), current-system and power/module
contracts, hardware status and [standalone handoff](docs/firmware-handoff-2026-09-07.md).
The handoff embeds both actual native 100-pad MCU tables and DMA allocation;
the original allocation CSVs are byte-identical. Its new revision has not been
sent to or reviewed by Anav. Earlier acceptance and historical logs are preserved.
Project-memory work kept current truth, durable reasoning and append-only history
separate; it did not rewrite prior enthusiasm into new decisions.

The local [reading pack](../layout-reference-2026-09-07/START-HERE.md) contains
31 component-named PDFs comprising 50 original manufacturer pages. Original
URLs, source/extract SHA-256 and original page numbers are indexed. Every
extracted page was checked for preserved text/page geometry and rendered for
visual inspection. ST H563/AN5711, LSM6DSV16X, TDK ICM-42688-P and LTC6993
layout-page downloads remain unavailable after bounded manufacturer/mirror
attempts; the cached TDK file was not a PDF and was rejected. Nano-Fit's exact
drawing and C1403's exact selection remain open. These gaps are explicit in the
index, not silently substituted. ADXL375 uses the original ADI document from
Adafruit's mirror. Different-package TI layout examples are marked as routing
guidance, not our pad geometry.

The guide starts with the Samtec datums and carrier, then GNSS reservation,
source/shunt/regulation, MCUs/clocks, sensing/storage/comms, indication and outputs;
Foinse has its own ordered sequence. A material finding: Croí's initial GNSS
support row does not establish the manufacturer's 10 mm component clearance.
The guide gives a first rearrangement and the no-under-module-signal/20 mm
layer-change rules. The PCB now labels this placement unqualified. Its old
Dwgs.User ground rectangle is not a keepout or performance proof.

Observed checks: Croí 43 PDF pages, 625 physical symbols, 28 DNP, 2,150 pins and
283 assertions; ERC remains four deliberate unpowered-output errors and four
warnings. Foinse 11 pages, 101 symbols, 278 pins and 91 assertions; ERC zero.
All 54 schematic pages were rendered/reviewed, with updated monitor/indicator
pages inspected individually. Native PCB checks pass 2,219/338 numbered pads,
schematic UUID/value/DNP/BOM identity, local models and no courtyard collisions.
There are 624/100 footprints, 567/86 resolved model instances, 43/9 groups;
Croí stages 95 parts, Foinse none. All 610 retained Croí and 100 retained Foinse
footprint placements/identities match the recovery snapshot. Fourteen new Croí
footprints are separately staged; no existing placement, routing or outline was
silently regenerated. Samtec opposing contact checks pass. DRC remains non-clean
with documented clearance/drill/library/cosmetic findings and expected unrouted
connections; schematic parity reports the missing J101 footprint on each board.

Nine obsolete Foinse components were removed from active schematic/PCB:
R1011, U4001, R4001–R4004 and C4001–C4003. They are recoverable with the complete
pre-change projects at
`../schematic-work-2026-09-07/sensing-status.KvNwHP/{croi2,foinse2}-before/`.
Croí project settings changed only by adding the correct new sheet-instance
metadata; existing settings and sheet records remain intact. Final PCB SHA-256:
Croí `a3df196d67a5ed6f4f9b1219034f13065ebd5106c40f0a4185680f30cbe1e34f`;
Foinse `fc07b76b59e4e3215bef99b6c6b5430871171db650c8b9c8f3e587383f996e93`.

Mac GUI work hit the locked-session boundary. Markdown Preview's normal open
requests also failed in this session despite its executable being present;
no security setting or app installation was changed. Finder accepted the handoff
reveal request, but the selected window cannot be verified while locked. The
guide was requested in Codex's right-hand file panel as a fallback. Do not claim
that Markdown Preview was successfully left open. No external message, upload,
Git staging/commit/push, purchase, charging or live-load test occurred. First
functional tests still use the first full engineering PCBA with inert loads.

The preceding 99,988-byte log prefix remains unchanged, SHA-256
`1e4408090b6e9373c8a5c717d6046928009ff5e8c0c22d6d1c2bd93e643a3805`.

## 2026-09-07 — Circuit clusters before board packing

Seán authorised building every Croí subcircuit locally, choosing preferred
faces, and accounting for copper/keepout space before determining the final
outline. He proposed 80 mm width from avionics-bay constraints and authorised
adjusting length. This is the next packing budget, not measured vehicle fit.

Created a separate [portable placement study](../cluster-layout-2026-09-07/START-HERE.md)
outside the Git-tracked umbrella. The live Croí/Foinse CAD, schematics, settings,
libraries, pin allocations and output safeguards were not changed. All 624
assigned Croí footprints are in 25 physical review groups containing the original
43 sheet groups. There are 483 front and 141 back footprints. The source-entry
and INA228 shunt sheets share one physical group because they form one current
path. MCU support/reset/debug sheets now move with their actual processor.

Critical placements use explicit IC anchors and native pad-net assignments for
bypass, oscillator, feedback, Kelvin-filter and selected damping parts. Remaining
local support uses net-aware positioning and is labelled as a review suggestion.
All recorded pin-distance checks pass; these distances are placement heuristics,
not routed loop/EMI validation. Ground-reference rectangles and thermal/quiet
reservations travel with their physical groups. The study has no Edge.Cuts,
tracks, vias or filled pours. No board packing or final length is claimed.

Front: power conversion, MCU/high-frequency support, sensor bodies, NOR, RF,
CAN/USB and drivers. Back: slow permission/timing/observation logic and six MCU
bulk capacitors. The latter are an explicit layout tradeoff; AN5711 recommends
same-side non-BGA decoupling, and equally short front placements remain preferable
if final packing allows them. Inertial bodies are front/unmirrored, but their
body-to-board transforms still require visual source and physical sign checks.

GNSS planning preserves the separate 50 mm ground, 10 mm component-clearance and
20 mm signal-layer-change concepts. Native rule areas exclude centre/buried
tracks and unsuitable component placements while retaining ground. A custom
non-GND-via rule leaves ground stitching possible. Positive-control tests on an
isolated, deliberately invalid copy verify rejection of a signal via, buried
trace, rear component and wrong-net filled pour, and acceptance of a ground via.
The test copy's synthetic outline/filled copper are not present in the study.

Observed checks: unchanged source-board hash; identical copied schematics,
project settings and libraries; preserved footprint identities/pad nets/DNPs and
original group membership; no courtyard collisions; no newly introduced native
clearance, drill, hole-clearance or keepout findings. Full DRC remains non-clean:
36 existing clearance findings, four hole-clearance, nine drill, one library
mismatch, twelve text-height, two silk-overlap findings, the deliberate missing
outline, 499 unconnected items and missing J101 parity warning. The source had
one silk-overlap finding; this study has two. No rule was weakened to hide them.
[Validation details](../cluster-layout-2026-09-07/croi2/validation.json).

The [reading views](../cluster-layout-2026-09-07/preview/index.html) provide native
front/back geometry for each cluster; duplicate fabrication-reference text is
simplified only in the reading renders. The study notes identify fixed geometry,
movable satellites, copper intent, source status and unresolved work. Project
memory links distinguish this candidate from the active CAD and preserve the
earlier starter's history. The REV-B label denotes the sensing/status update;
those parts are intended for the first engineering PCBA, not a later board order.

Next: review critical local circuits, then pack within 80 mm and let length
follow routing/service/mechanical needs. Exact J101/C1403, sensor axes/assembly
audits, thermal sizing, output/arm closure and hardware proof remain open. No
firmware implementation, Git staging/commit/push, external publication, purchase
or live-load test occurred.

Pre-entry log prefix: 108,432 bytes, SHA-256
`3ffd0fa89a4da2e936b08dc35f4294cd8b9015b3faf3f4c7d176333fb8b3ad80`.

Final visual review also moved the monitor's R7105 supply-isolation link from
the connector rail to the local U7101 supply node. All electrical identities
remain unchanged. Opening the study in KiCad stopped at the computer-use
locked-Mac boundary; no unlock bypass was attempted. The guide-open request in
this task's file panel was queued, not visually confirmed.

## 2026-09-07 — Functional blocks installed in the working Croí PCB

Seán authorised placing components from the reviews and guides, accepting
group-level placement for his fine-arrangement pass. He then explicitly kept
board dimensions provisional: arrange the functional blocks first, let him
bring them together, then establish how compact the board can be. This
supersedes treating 80 mm as a hard packing constraint for this pass.

Installed the reviewed local circuit geometry into
`hardware/croi2/Croi2.kicad_pcb`: 624 assigned footprints, 25 physical groups
containing the 43 original schematic-sheet groups, 483 front and 141 back.
The 130 × 300 mm Edge.Cuts rectangle is an oversized working canvas only,
not a minimum-area claim, a proposed production envelope or vehicle-fit proof.
There are no remaining old staging banks, routes or filled pours. Twenty-eight
native rule areas and the project-local GNSS custom rules are installed.
The original separate cluster catalogue remains intact.

Kept each circuit's local geometry while translating blocks. Turned the two
Micro-Fit connectors and their local resistor networks together toward the
right edge. Moved Samtec and its input test point together to the provisional
bottom datum. All connector nets, physical MCU pins, DNP safeguards and
schematics remain unchanged. Interblock spacing is deliberately unfinished:
NOR/flight, LoRa/comms, LDO/load and the source-power path must be brought
together before routing. The updated placement notes name these moves.

Observed candidate checks: all 624 footprint identities, 2,219 numbered pad
nets, 567 model instances, 28 DNP flags and 43 sheet groups preserved; all 499
local pin-distance checks pass; zero courtyard collisions and no new critical
native DRC geometry/keepout findings. After promotion, the native working-board
checker passed against the schematic netlist, including its in-memory negative
pad-net test. Movement and reversal of every outer physical group was tested
in memory: all nested components/drawings/rule areas followed, with no saved
CAD change. The Samtec pair check passes using relative connector datums,
independent of the two provisional board widths.

Existing native DRC remains visible: 36 clearance findings, four hole-clearance,
nine drill, one footprint-library mismatch, twelve text-height, two silk-overlap,
499 unconnected items and one missing-J101 parity finding. No invalid outline
or keepout violation. No rule was weakened. J101's exact land pattern, C1403's
part/retention, sensor body-axis transforms, routed return paths, mechanical
integration, thermal design and circuit/arm/load qualification remain open.

Before replacement, saved the old board, reports and changed documentation in
`../placement-work-2026-09-07/pre-placement/`, with file hashes. All 145 Croí
schematic/settings/library files remain byte-identical; Foinse PCB hash remains
`fc07b76b59e4e3215bef99b6c6b5430871171db650c8b9c8f3e587383f996e93`.
New Croí PCB hash:
`c71bf80a7355fd493af4a1c1be892ab49174b6575cf855ea1a7896f1c753bcb3`.
The guide, hardware entrypoints and current-system now identify the working
PCB and distinguish local circuit placement from final packing. Native
front/back and reservation views are retained with the scratch candidate.

Next: Seán's fine placement and compaction; then final outline and routing.
Anav retains firmware ownership. No Git staging/commit/push, publication,
purchase, charging or live-load test occurred.

Pre-entry log prefix: 113,036 bytes, SHA-256
`e7579c4cc6d35d85527c0c5491406c6af3b155545371575ab493adb9f7c5bdcf`.

## 2026-09-07 — Local rigid-block compaction

Seán authorised treating the functional groups as Tetris pieces: consider their
nearest neighbours and bring them together, without rearranging group internals.
Performed bounded local translation sweeps and neighbouring contact-chain moves.
No group or component was rotated, flipped, split or internally rearranged.

The working Croí outline is now **123.75 × 269.75 mm**, reduced from 130 × 300:
33,381.5625 versus 39,000 mm², **14.40625% less area**. This is an observed local
compaction result, not a packing optimum, final production size or vehicle-fit
claim. The earlier 80 mm width target is not reached. The source-entry/mate
group's roughly 90 mm envelope and the output bank's roughly 74 × 118 mm
envelope remain coarse rigid pieces; they were not silently split to force fit.

Saved-CAD checks verify rigid translation of all 624 footprint origins and
2,353 pad positions, including mechanical/unnumbered pads. All 2,219 numbered
pad nets, 28 DNP flags, 43 sheet groups, 483 front/141 back choices and local
models are preserved. All 499 recorded circuit-distance checks still pass.
All 28 rule areas travel with their groups. The unassigned J101 reservation
drawings now belong to the source group too. No routed copper or filled pours.

Native working-board/netlist checks pass, including the negative pad-net test;
no courtyard collision or added critical DRC finding. Existing DRC counts remain
36 clearance, four hole-clearance, nine drill, one library mismatch, twelve
text-height, two silk-overlap, 499 unrouted items and one missing-J101 parity
finding. No invalid outline or keepout violation. No rule was weakened.
Samtec contact-order/edge-datum checks pass; Croí's provisional local mate
coordinate is now (68.5, 269.75), 0°. Alignment uses connector datums rather
than assuming the different-width boards have coincident left edges or centres.

The prior working board and reports are recoverable at
`../compaction-work-2026-09-07/pre-compaction/`. All 146 schematic, project,
custom-rule and library files remain byte-identical; Foinse is unchanged.
Current Croí PCB SHA-256:
`e1357bbf100452989d1a231f6549416bdaacb066c4df0b9b5788b2832d58b9e0`.
The [placement notes](docs/croi2-functional-placement-2026-09-07.md), current
system and hardware guide reflect the new geometry. Native front/back views
and the movement history are retained in the compaction scratch directory.

Further compaction, routing, exact J101/C1403 closure, mechanical integration
and qualification remain open. Firmware, schematics and electrical architecture
were not changed. No Git staging/commit/push, publication or live-load testing.

Pre-entry log prefix: 116,640 bytes, SHA-256
`134f166c89a94bc17639edcfda29f1378bddb24ea8acc573606182b2b1a6e6c6`.

## 2026-09-07 — Second compaction; insulated rail test points

Seán requested another rigid-group compaction pass and raised rail test points
with a small cylindrical plastic body and short exposed loop, replacing the
bare-loop style. Scope was Croí2; Foinse and firmware were left unchanged.

The working outline is now **123.75 × 260.75 mm**, from 123.75 × 269.75:
another **9 mm shorter / 3.3364% less area**. Area is 32,267.8125 mm²; total
reduction from the original 130 × 300 canvas is 17.2620%. This is a bounded
local packing result, not a minimum, final dimension or vehicle-fit claim.
The 80 mm width target remains unmet. Translation sweeps followed by a bounded
local shuffle/settle search moved the same 25 rigid groups. No group was split,
rotated or flipped; no internal circuit geometry was rearranged.

Replaced all 20 generic raised loops: 17 supply points now specify **Keystone
5000 red**, and TP2304/TP4204/TP502 specify **5001 black ground**. The 31 flat
signal-probe pads are unchanged. Selected the stock miniature Keystone footprint:
nominal 2.5 mm body diameter, 4.6 mm installed height, 3.3 mm courtyard, one
1 mm plated hole and 2 mm pad. The former pad, hole, centre, net and UUID remain.
Fifteen schematic sheets and PCB metadata now name the MPN/manufacturer;
rail-name values are retained. The library snapshot records provenance.

The manufacturer catalogue was downloaded and visually checked. The exact STEP
named by KiCad is absent locally and from direct upstream lookups; the vendor's
STEP download requests contact details, which were not submitted. Removed the
broken model reference rather than attaching the wrong bare-wire shape. Thus
547 model instances resolve, down from 567. These twenty parts have footprints
and procurement identities but no exact 3D bodies. Installed-height/probe-access
checks and finished-hole fit remain necessary. See
[test-point selection](hardware/croi2/libraries/testpoint-selection.md).

Saved-CAD checks passed for all 2,353 translated pad positions, 2,219 numbered
pad nets, 28 DNP flags, all 43 sheet groups and all 28 rule areas. All 499 local
pin-distance checks pass. Full native netlist comparison found all 2,150 nodes
unchanged; the 283 architecture checks pass. ERC remains four errors and four
warnings. Native DRC adds no finding in any category; one old silk overlap
disappeared. Remaining: 36 clearance, four hole-clearance, nine drill, one USB
library mismatch, twelve text-height, one silk-overlap, 499 reported unconnected
items and one missing-J101 parity finding. No routing, vias or filled pours.
No design rule was weakened.

Samtec edge/contact checks pass. Croí's datum is now (68.75, 260.75), 0°;
Foinse remains (30, 0), 180°, with the nominal 7.39 mm edge gap. Final supports,
connector access, J101/C1403 closure, routed returns, thermal/RF/assembly review
and hardware qualification remain open. Anav's MCU allocations are untouched.

The previous board and full local dependencies are recoverable in
`../compaction-2-2026-09-07/pre-pass/croi2/`; source hashes, exact movements,
native reports and inspected previews are in the same scratch work directory.
Working PCB SHA-256:
`3759817698e843a1d42adc1c0167675bfe845fdbe8febee37de9198df8d63586`.
Foinse remains SHA-256
`fc07b76b59e4e3215bef99b6c6b5430871171db650c8b9c8f3e587383f996e93`.
The current-system, layout guide, hardware entrypoints and placement notes now
match the saved CAD. No Git staging/commit/push, publication, procurement,
charging or live-load test occurred.

Pre-entry log prefix: 119,451 bytes, SHA-256
`639ed7941a6f32a426362a84ae27cc76e2983c0f75e7dd3e8de7c6207737785f`.

## 2026-09-07 — Release subsystem rigidity; 80 mm placement width

Seán paused the new keepout/polygon request after inspecting the 2D and 3D
PCB views. He explicitly asked to stop treating groups as rigid because many
contain multiple widely spaced circuits. This supersedes the earlier instruction
to preserve each whole subsystem internally. No additional rule area or copper
polygon was created for the paused request.

Inspection: the old compactor already used individual footprint occupancy, not
solid subsystem bounding boxes. The restrictive assumption was frozen internal
spacing across 25 groups. The output group contained 121 footprints; source
entry was tied to its distant Samtec and blank battery connector reservation.
The 3D image also omits several real footprints whose exact models are missing.
Both PCB faces and the native reservation overlay were used for review.

Built 97 small placement cells from all 499 recorded local distance constraints,
plus explicit clock/regulator/shunt/MOSFET relationships. Independently moved
debug, interfaces, sensor support, source stages, output channels and connectors.
All 43 original sheet groups and the 25 outer groups remain; the latter are
logical selection aids, not placement constraints. The 97 cells are recorded
relationships, not native KiCad groups. A moved local circuit needs its own
named rule area/drawing moved with it; an IC-only mouse move does not do that.

The saved working outline is now **80 × 230 mm**, from 123.75 × 260.75 mm:
18,400 mm², **42.98% less area**. An 80 × 220 trial fit geometrically but
scattered several connected circuits; it was not promoted. The selected trial
keeps extra height and prioritises the source/shunt, power chain and CAN region.
This is a provisional placement result, not routing capacity or assembled fit.

Footprint-origin distances, before → after: flight/NOR 33.3 → 30.2 mm;
comms/radio 73.6 → 47.5; entry/mux 26.3 → 17.7; mux/buck 19.8 → 14.1;
CAN boundary/transceiver 12.0 → 7.6. Not every connection improves: channel 3
driver/J6601 grows 44.2 → 50.9 mm and remains a refinement target. These
distances are neither routed lengths nor an electrical-performance result.

Native readback checks preserve 624 footprint identities, all 2,353 pad
translations, 2,219 numbered pad nets, 28 DNP flags, 43 sheet memberships and
28 rule areas. All 499 local pin-distance checks pass. Component rotations,
483 front/141 back allocation, schematic UUID paths, libraries, MCU pin maps,
project settings and custom rules are unchanged. No courtyard/drill-reservation
collision or newly added native DRC finding in any category. Remaining DRC:
36 clearance, four hole-clearance, nine drill, one USB library mismatch,
twelve text-height and one silk-overlap. There are 499 reported unconnected
items and the known missing-J101 parity finding. No rule was weakened.

The conservative 56 × 56 GNSS packing reservation remains, in addition to
the existing native rules; it is broader than the native via-only restriction
and is not presented as a new manufacturer component-clearance requirement.
All existing thermal/quiet areas follow their actual owner. No routing,
routing vias or copper pours. Insulated Keystone test points are unchanged.

Samtec opposing contact/edge checks pass. Croí J102 is (40, 230), 0°; Foinse
J301 remains (30, 0), 180°, with nominal 7.39 mm edge gap. Foinse itself is
unchanged. Native source hashes were checked before promotion to avoid
overwriting concurrent edits. Live PCB SHA-256:
`eae51e3f801186ac5857a22d812e96d1ab95990acc33babfe17ce6266ac29f10`.

The previous project is recoverable in
`../flex-placement-2026-09-07/source/`; previous notes, source hashes, circuit
membership, final plan and native previews are beside it. The
[layout notes](docs/croi2-functional-placement-2026-09-07.md), current-system,
hardware entrypoints and ordered guide now replace the old rigid-group advice.
Next: visually review the tighter board, refine actual signal/power paths,
close J101/C1403 and mechanical constraints, then route. Do not save an old
open editor over the disk update. No firmware work, Git staging/commit/push,
publication, procurement or live-load testing occurred.

Pre-entry log prefix: 123,107 bytes, SHA-256
`65f2728b915d94271d994ddafdf27c871778490f819b9192713d697d48c79223`.

## 2026-09-07 — Six-action avionics review; above-80-km study non-binding

Seán authorised the follow-up research from his discussion with Anav and added
an explicitly exploratory sixth action: what accurate height estimation above
80 km would require. This authorises research and review documents, not a new
parts freeze, CAD change or mission requirement.

The [review](docs/avionics-options-review-2026-09-07.md) covers radio modules,
GNSS alternatives, sensors, a CAN harness drawing and the actual CATS comparison.
The leading proposed radio upgrade is Seeed Wio-LR2021: a small solder-down SPI
module with official CAD assets and a listed US$6.99 price/in-stock indication
on the review date. E22 remains accepted. Exact revision, host RF launch,
TCXO/BUSY treatment, current-table ambiguity and driver limitations need closure
before substitution. Faster PHYs trade away sensitivity; no live-video promise
or full-rate flight-data radio requirement was added.

The selected ST/TDK IMUs already provide dissimilar low-g sensing. No sixth
sensor is proposed. The [Anav supplement](docs/sensor-configuration-review-2026-09-07.md)
preserves allocations and asks for explicit range/filter/validity/timing checks.
SAM-M10Q four-constellation 10 Hz requires the high-performance configuration
in the R05 table; TE's MS5607 extended ADC range is not its full-accuracy range.
These qualifications do not silently revise the accepted firmware contract.
Anav has not been messaged or assigned a new implementation schedule.

The CAN drawing preserves J501 pin 1 H / 2 L / 3 reference, two-node fixed
termination and no power contact. It proposes short untwist and chassis strain
relief. It is not a mating-face drawing or fabrication release: compatible
120 Ω cable part, installed length, propulsion cavity numbering and bonding
remain open. The CATS product page's 10 km flight-tested radio range does not
establish the discussed 100 km altitude rating; that claim remains unverified.

The [height study](docs/height-estimation-above-80km-2026-09-07.md) separates
real-time navigation, telemetry and post-flight altitude proof. It covers
supported high-dynamic GNSS, installed antennas, inertial propagation, ground
tracking, height reference and error budgets. DLR's published 309 km sounding-
rocket result is relevant evidence, with documented outages and specialised
configuration; it is not a qualification of an arbitrary retail receiver.
Full-envelope altitude proof remains outside ordinary Croí in the accepted
Kármán configuration. No receiver, accuracy requirement or extra PCB selected.

Executed the small standard-library calculation accompanying the reports.
Golden LoRa airtimes, distance scaling, inverse-square coast energy and
half-step convergence checks pass. In the deliberately idealised 100 km radial
coast, speed at 80 km is 617.6 m/s and time above 80 km is 129.67 s. This exposes
why a valid SAM fix at exactly 80 km cannot be assumed. It is not a HiPR flight
simulation, calibrated error bound or hardware test. Existing first-full-PCBA
testing policy remains; no separate custom evaluation-board gate was introduced.

Indexed the new documents and added a proposal-status pointer to current-system.
Corrected stale discovery text that still described Croí staging banks/rigid
groups; it now matches the already-saved placement. No CAD, symbols, footprints,
pin maps or firmware changed. No staging, commit, push, publication, procurement,
supplier contact or live-load test occurred.

Pre-entry log prefix: 127,463 bytes, SHA-256
`22c260bd8bc1eb552bbe8fd9779dc8ff073f12f6a3c6d920e54c2ce3bf453f0a`.

## 2026-09-07 — Six recommendations accepted; Wio radio installed

Seán accepted the recommendations and instructed continuation. Wio-LR2021
868/915 MHz, Seeed SKU 100058045, replaces E22. SAM-M10Q, the five sensors,
CAN connector/pinout, MCU physical allocations and Croí/Foinse boundary remain.
The sensor checklist and CAN harness recommendation are accepted; cable part,
length and propulsion cavity numbering remain open. Above-80-km work stays
explicitly non-binding. No pre-order custom evaluation-board gate was added.

Downloaded Seeed's official KiCad assets and STEP. The assets used KiCad 10
syntax; adapted them to KiCad 9 and independently checked all 22 pad locations,
numbers and sizes. Removed the supplied footprint's DNP/net-tie flags and
replaced its incomplete courtyard and pad-crossing silk. Original source and
checksums remain in `../radio-upgrade-2026-09-07/sources/` and its audit JSON.
The official STEP is retained but deliberately not linked: its compound
assembly origin has not been verified. No guessed model alignment was installed.

Replaced U4606 in the two radio sheets and PCB. Removed U4605, C4605, R4606
and R4607; disabled the unused U4604 channel. Added seven 470 Ω digital series
resistors, a 10 kΩ switched-rail BUSY pull-up and J4601 U.FL host connector.
Pad 10 is the single sub-GHz RF path; pad 13 is NC. Historical LORA_DIO1 reaches
Wio DIO5. MCU PC3/PC4 remain named/reserved but no longer drive external RF
switches. Radio bypass placement follows the changed supply contact.

Source-to-candidate checks: all 41 unrelated schematic files and both frozen
MCU CSVs byte-identical; 617 unaffected footprint states identical; module
board UUID and schematic paths preserved; all 28 rule areas unchanged.
Native results: 630 symbols, 629 footprints, 2,148 schematic pin checks,
322 architecture checks, 2,218 numbered PCB pads, 552 resolved model instances,
28 DNP parts, 488 front/141 back, 96 recorded cells, 68 native groups. The
80 × 230 mm provisional outline and unrouted state remain. No new native DRC
finding by type and implicated-item identity. Existing DRC categories remain:
36 clearance, four hole-clearance, nine drill, one USB library mismatch,
eleven text-height and one silk-overlap; 499 reported unconnected items and
the known missing-J101 parity finding. ERC has four existing errors and six
warnings: two additions identify the intentionally unused RXEN/TXEN labels.
No rule was suppressed. Radio sheet renders and the PCB export were inspected.

Promoted only 22 explicitly allowed files after verifying the live source had
not changed. Live PCB SHA-256:
`ec3b7997d8969aac0a2e591dc0dc63d387548b5474217be8d06733e34ee11dd8`.
The prior complete Croí draft remains at
`../radio-upgrade-2026-09-07/before/`; candidate, scripts, read-back checks and
promotion manifest are beside it. Foinse PCB hash is unchanged. Previous
PDF/PNG/SVG exports are explicitly marked stale for the radio revision.

Updated [Anav's handoff](docs/firmware-handoff-2026-09-07.md),
[radio contract](docs/radio-change-2026-09-07.md), ordered layout guide,
current-system and discovery records. Preserved earlier acceptance/research
records with supersession notes. Anav retains firmware implementation.
The radio still needs exact revision/clock-startup confirmation, final SPI
timing and installed RF/power tests on the first PCBA. Wio STEP alignment and
existing board release gaps remain open. This is not fabrication/flight release.
No firmware, external message, purchase, Git staging/commit/push or publication.

Pre-entry log prefix: 131,098 bytes, SHA-256
`88bb1d554cd488c6d7e290868376f3e0956c72d04fc09f1c11159a56e64ef4da`.

## 2026-09-07 — Third servo, complementary readiness and vertical SMA

Seán explicitly withdrew the USB-C placement request: the current connector was
correct and the observed issue belonged to an older version. USB schematic and
footprint remain unchanged. He accepted Jay's third servo requirement and the
one-GPIO complementary red/green readiness proposal, then authorised implementation.

Installed flight PD10/pad57 as SERVO3_PWM, LPTIM2_CH2 AF3. All other flight
allocations and the complete comms CSV remain unchanged. Existing TXU0304 A3/B3Y
now carries the third PWM; R6606 100 ohm and R6607 100k complete its boundary.
J6602 is now ten-contact Micro-Fit 430451000 with three PWR/PWM/GND triplets
1/2/3, 4/5/6, 7/8/9 and contact10 NC. This intentionally supersedes the entire
old eight-contact harness pinout. Its common 2A limit remains provisional, not
a grid-fin load qualification. All four output-energy links remain DNP.

PD7 retains its existing green LED and now drives U9101 SN74LVC1G04DBVR for
complementary red indication. Added 47k pull-down and 100n bypass. Low/reset
with valid flight supply means red/not ready; high means green/selected-profile
preflight checks passed. No armed/launch authority is implied; a stuck-high
MCU can leave stale green. Comms amber, hardware power LED and buzzer are unchanged.

J4601 is now vertical standard SMA female Amphenol 132134, preserving Wio pad10
RF connectivity and GND. J6601 pyro symbol and footprint already existed and
remain unchanged. Exact 3D bodies for pyro, new servo and SMA connectors remain
unavailable: public model attempts failed/returned404, Amphenol STEP needs login.
No browser control or substitute model was used. This is an explicit remaining
library gap, not completed model acquisition.

Native verification: 635 symbols, 634 footprints, 2163 pin checks, 346 independent
architecture checks, 2235 numbered PCB pads, 556 resolved model instances,
493 front/141 back, 99 recorded cells, 68 native groups, 28 rule areas and 28 DNP.
Four existing ERC errors/six warnings remain. No new DRC finding by type and
implicated-item identity; existing clearance/drill/library/text findings persist.
All 629 existing footprint UUIDs retained, 622 unaffected states identical and
38 unrelated sheets byte-identical. J6602 moved 3 mm upward; R6602/R6603 moved
locally to clear it; five new parts placed. Outline remains 80 x 230 mm, unrouted.
Foinse PCB hash is unchanged. Schematic and PCB previews were inspected.

Promoted only checked files after verifying live originals matched the snapshot.
Current PCB SHA256: `03bb9ba5b0731cf31ad1bf958eeb063147fd269cf90446388e2afe51e2bcaf7c`.
Recovery snapshot, bounded scripts and promotion record:
`../connector-servo-2026-09-07/`. Current-system, power contract, layout guide,
connector inputs, library manifest, checks and Anav handoff were reconciled.
The original shared-library/architecture-review input snapshots are historical;
current physical MCU CSV authority is inside the Croí board repository.
See [full revision](docs/connector-servo-readiness-revision-2026-09-07.md).
No firmware, hardware/energetic test, purchase, commit/push or external message.
Next: layout review and first-PCBA waveform/indicator/load/RF checks; exact
connector bodies and existing Nano-Fit land-pattern gap remain open.

Pre-entry log prefix: 134,777 bytes, SHA-256
`a76bce3dfeef146b194f9aefa6b89984942df742c68b350a979564f72e2d8ed0`.

## 2026-09-07 — Model recovery; remaining gaps counted explicitly

Seán flagged SMA solder/rework access beside an IMU and requested all missing
models/parts, explicitly including Foinse, LoRa, GNSS and the power module.

Installed eight model instances: Croí U4606 Wio, U4504 SAM-M10Q, BZ9001 sounder,
J6601/J6602 Micro-Fit and U503 DRB-package CAD; Foinse J201/J701 Micro-Fit.
Seeed's original radio STEP needed coordinate alignment. The buzzer came from
Same Sky's public download service. GNSS was extracted as an explicitly named
SAM-M10Q-00B from Vimdrones' public assembly and checked against u-blox geometry;
no carrier board was imported. Rejected a Boardoza download whose internal
identities say SAM-M8Q, and mismatched local generic package/crystal models.
Micro-Fit sources are manufacturer-derived community CAD, not vendor-certified
geometry. Exact source roles, transformations and limitations are recorded in
each board's library and the [recovery register](docs/model-recovery-2026-09-07.md).

Observed remaining gaps: 39 Croí and one Foinse placed physical bodies, covering
14 part numbers. Another 44 footprints are intentionally bodyless flat probes/
Tag-Connect patterns. Both J101 Nano-Fit footprints remain absent, outside those
placed-footprint counts. C1403 is still an unselected volume reservation. No
separate L-reference exists in the inspected Croí PCB; the user's inductor may
mean the TPSM63603 integrated-inductor module, but that identification is inferred.

Both native checks pass, 2235/338 numbered pads and 562/88 model instances.
DRC remains 62/24 findings with identical violation types/item identities.
Parsed boards excluding model entries are exactly unchanged: no pad/net,
placement, outline, group, rule-area, DNP or schematic change. Original PCB
hashes were checked immediately before promotion. Current hashes:
Croí `582f1b38f3ab7e2cf222722da714037cafcb8ad4c533f6b8f975dd45f24489bc`;
Foinse `fcaa39f752b3da5e984106606e324e95a72784e351fe7e7c0d5ab15a697c0698`.

SMA edge positions beside CAN were checked but collided with other cells on
one/both faces. Nothing moved. Its soldering/mating access needs a coordinated
local placement pass, not a claimed universal thermal clearance. USB stays put.

Next acquisition checkpoint: exact gated STEP downloads for the 14 remaining
part numbers, and Nano-Fit vendor land pattern, followed by geometry checks.
No browser control, registration, personal-data submission, purchase, firmware,
Git staging/commit/push or public redistribution. Recovery snapshots, downloaded
sources, hashes and scripts: `../model-recovery-2026-09-07/`.

## 2026-09-07 — Public-library model follow-up

Seán asked to find the rest. Public EasyEDA records yielded eight STEP candidates.
Installed three package models on five Croí instances: U1101 TPS2121, U1401
LM73100, Q6301/Q6401/Q6501 CSD17318Q2. Measured package/terminal geometry and
native preview checked; library CAD provenance and geometric simplifications
are explicit. No EasyEDA footprint/symbol was imported. Rejected five candidates
for height or part-identity mismatches; no generic substitute silently installed.

Croí now has 567 resolved model instances and 34 remaining physical body gaps;
Foinse remains unchanged with one gap. Eleven part numbers remain, plus the
separate missing Nano-Fit footprint on both boards. Public Samtec records and
TPSM63603 model lookup did not recover assets. Keystone contribution searches
did not locate the announced source; Nano-Fit distributor fetch failed.

Parsed board excluding model nodes is identical. Native checks pass 2235 pad
identities; all 62 DRC finding types/item identities and 499 unconnected entries
remain unchanged. Snapshot hashes checked before promoting 12 bounded files.
Croí PCB SHA256: `8357ca46c3ddcf8ff5011edf37fa0c08195efcf52d30ef2584a49ffc17b1aa87`.
No placement, routing, schematic, Foinse, firmware or external account change.
Sources, dimensions, rejected candidates and next acquisition pointers:
[follow-up register](hardware/croi2/libraries/model-recovery-easyeda-2026-09-07.md).
Recovery snapshot/check evidence: `../model-recovery-2026-09-07/easyeda-pass/`.
Next: obtain exact remaining vendor/account downloads, then validate geometry.

## 2026-09-07 — 99-cell local-routing study checkpoint

Seán requested pin-aware placement and real cell-local traces/vias across all
current Croí cells, without inter-cell wiring. Created a separate recoverable
study outside the live hardware repository; no live PCB promotion.

Observed in the saved candidate: 99 cells, 634 footprints, 2,993 trace segments,
122 vias; 78 footprints moved or rotated. Native copper connectivity finds no
open local pad groups in 86 cells (including three single-resistor cells with
no internal wiring). Thirteen cells remain partially routed. Every cell has an
illustrated before/current view and exact open-net register. This is a partial
checkpoint, not completion of every circuit's layout.

Native DRC adds zero findings over the existing 62. All 2,235 numbered pad
identities/nets, 28 DNP flags, original groups and custom clearance rules remain.
No copper connection spans different cells. Live Croí PCB SHA remains
`8357ca46c3ddcf8ff5011edf37fa0c08195efcf52d30ef2584a49ffc17b1aa87`.
Foinse, schematics, firmware and external services were not changed.

Pin-order corrections cover U6802 support, three LDO support networks, buck
support, INA differential filtering, HSE load-capacitor corridors and three TXU
input bypass capacitors. Native connectivity is not electrical-layout approval:
power/return paths and 0.125/0.2 mm study widths remain provisional; RF/USB,
Kelvin geometry, quiet returns, thermal implementation and manufacturing review
remain open. No claim of 99 manufacturer-reviewed or production-ready cells.

Next: close the 13 listed partial cells, then perform the per-family electrical
layout review. Do not promote this candidate as a finished board.
[Study inventory, diagrams and native evidence](../local-routing-2026-09-07/START-HERE.md).

## 2026-09-08 — evening review: readable architecture first

Authority: Seán's instruction in this task after the evening team discussion.
Reviewed all 74 stream records in the rolling eight-hour window ending
2026-09-08 00:58:44 Europe/Dublin, including complete recording transcripts.
Private recordings and unrelated personal material are not copied here.

The 7 September 22:34 recording establishes the relevant sequence: external
GNSS and external switches at 00:30–00:33; short domain explanations at
00:56–01:14; connected schematics and schematic/PCB cross-selection at
01:15–01:31; independent reading before joint review at 01:32–01:33.
Quoted BPS hardware is a comparison, not authority to duplicate its design.

Decided:

- Publish the readable documentation baseline to the existing HiPR review
  branch. Retain the earlier research; remove contradictory repetition from
  the current entrypoint.
- Add a short architecture layer explaining the actual circuit, rationale,
  alternatives, drawbacks and remaining questions for each domain. Seán and
  Anav read independently before discussing it; Arnav can test its readability.
- Implement an external GNSS antenna arrangement for the carbon airframe,
  external power-switch connections on Foinse and standalone Croí, and explicit
  separation between ordinary power control and physical energetic arming.
  Exact circuit changes require a checked implementation record.
- Make schematics genuinely wired and readable. Retain symbol UUIDs, MCU pins,
  footprint assignments and PCB paths; prove any electrical delta separately.
- Freeze automatic PCB arrangement and routing. This supersedes the previous
  routing-study entry's immediate next step. Seán owns final layout; Anav owns
  firmware. Do not restart all requirements or impose a weekly review gate.

Observed documentation checkpoint: current-system reduced from 1,303 to 185
lines; its previous body is preserved verbatim in `docs/history/`. Added one
overview and eight short domain chapters under `docs/architecture/`. The new
reading path is self-contained; older records may retain clearly labelled
workspace-local CAD/research links. Publication excludes child hardware repos,
raw transcripts, third-party PDF/image dumps and private correspondence.

At this checkpoint the new electrical changes are still pending. Baseline CAD
is Croí 43 sheets / 635 physical symbols and Foinse 11 sheets / 101 symbols.
Equivalent redraws are being checked in scratch before any live promotion.
The shared preregulator remains a common failure point to discuss; no extra
processor, display, boost converter or generic exposed I²C connector was
authorised by the BPS comparison.

## 2026-09-08 — readable CAD and installation changes installed

The preceding documentation baseline was pushed as `bd3c28d` to
`docs/reliability-review-execution`. No child hardware repository was published.

Installed the checked readable schematics in both local board projects: Croí
44 pages / 643 physical symbols / 642 footprints; Foinse 12 / 113 / 112.
Circuit pages now explain purpose and connections and show local wiring.
The 56-page export set was rasterised and visually checked for clipping;
detailed circuit views were inspected during redraw. Digital zoom is needed
on large sheets. This is not a claim of manufacturing-ready drawing polish.

The explicit electrical delta is MAX-M10S external passive GNSS reception with
vertical SMA/RF protection, and independent external maintained source-enable
contacts on standalone Croí and Foinse's two branches. Exact parts, pins,
limitations and tests are in the
[installation record](docs/installation-change-record-2026-09-08.md).
Anav's handoff and the power contract carry the same change. The PPS/SAFEBOOT
startup constraint remains; no MCU allocation or firmware ownership changed.

Native exports were rechecked after installation. Croí: 2,179 schematic pins,
381 architecture checks, the original four ERC errors/six warnings. Foinse:
306 pins, 117 boundary checks, zero ERC findings. Independent symbol/path/net
checks and saved-board library/geometry checks pass. Native schematic/PCB
parity reports only the existing unassigned Nano-Fit J101 on each board.
GUI cross-selection itself was not exercised. Host replay tests: all 12 pass.

All original PCB positions, angles, sides, UUIDs and existing copper remain.
U4504 intentionally changes package at its previous origin. Eight Croí and
twelve Foinse additions are staged outside the outlines, deliberately ungrouped
for manual integration. The original groups are retained. Eight SAM-specific
rule areas and two obsolete custom rules were retired; 20 Croí rule areas
remain. Native DRC: Croí 61 findings, previously 62; Foinse 24 unchanged,
plus unrouted connections. No DRC exclusions were added to disguise findings.

Scratch redraw checks caught and corrected passive-orientation/connection
mistakes before promotion. Readability and connectivity are separate checks;
neither proves analog performance. Full pre-promotion working-file recovery
copies and an exact changed-file/hash ledger remain in the workspace-only
`readable-schematics-2026-09-08` study directory. Child READMEs/status pages are
current; their earlier complete text remains in each child's history folder.

Open: physical energetic arm assembly, all 28 Croí DNP safeguards, Nano-Fit
lands, C1403 selection, remaining models, existing DRC findings, switch/cable
fault tests and installed antenna/RF/power qualification. No initiators, live
load testing, purchases or hardware publication were performed. Next: independent
reading and joint circuit review, then Seán's layout and Anav's firmware work.

## 2026-09-08 — restore research depth to the architecture chapters

Seán found the GitHub architecture chapters too sparse for the flight-computer
team review. Expanded the overview and all eight domain chapters using the
6 September architecture research and 7 September follow-ups, reconciled with
the 8 September installed changes. The concise current-system remains the
orientation; the architecture pack now carries the substantive design argument.

Recovered material includes the H563/H573/lockstep/radiation-oriented comparison,
ECC memory consequences, buck/LDO and hold-up tradeoffs, output fault boundaries,
servo supply alternatives, Hall/shunt/IMON comparison, indication and timekeeping,
radio/GNSS shortlists, airtime/sensitivity calculations, each sensor's range and
timing limits, NOR capacity/commit throughput, battery-energy assumptions,
conditional propulsion conversion and the interboard connector audit.

This is evidence curation, not a new component-selection decision or live market
survey. Dated prices stay dated; desk calculations are not measurements. The
original sensor study checked a selected suite and meaningful architectural
alternatives but did not exhaustively benchmark every competing sensor. That
coverage limit is explicit. Historical SAM/E22/two-servo/coupon-first language
does not override the installed MAX/Wio/three-servo/first-full-PCBA baseline.

Manufacturer references are placed beside the claims they support; the pack
indexes deeper records already in the umbrella. No raw research/transcript dump,
private correspondence or child hardware was added. Checked 121 local links and
section anchors across the pack and entrypoints; no missing targets found.
No CAD, pin allocation, firmware, tests or qualification status changed.

Next: Seán, Anav and Arnav can review the reasoning within the same GitHub reading
path, then raise specific circuit or evidence questions rather than reconstructing
the design rationale from old workspace reports.

## 2026-09-08 — track both board projects in the monorepo

Seán explicitly clarified that Croí2 and Foinse2 are directories in the Ogma2
monorepo and asked to publish the updated schematics. This supersedes the
earlier independent-local-repository arrangement; no submodules are used.

Both nested repositories had no commits or remotes. Their Git metadata was
moved intact to a workspace-only recovery directory, not deleted. Active CAD
stays at `hardware/croi2/` and `hardware/foinse2/`. The monorepo now includes
their native projects, schematic sheets, PCB files, local symbol/footprint/model
dependencies, provenance/licence files, reading PDFs and verification reports.
Editor state, caches, backups and scratch output remain excluded.

Source paths in provenance/export metadata were made workspace-relative for
publication. Electrical CAD and vendor model bytes were not changed. The
existing manufacturing/qualification limitations remain; publication does not
make either board ready for PCBA or flight. Root and board instructions now
describe the monorepo. Earlier log entries retain the old arrangement as history.

A clean checkout of the staged tree resolved both local library tables and all
160 recorded library asset hashes. Fresh KiCad netlist/ERC exports and each
board's schematic checker passed with the existing documented ERC baseline.
No Git submodule entries were present. Vendor model bytes are preserved and
treated as binary for review; about 36.7 MB of files is included in this import.

## 2026-09-11 — extract the 10 September joint architecture sessions

Seán requested a complete ten-hour Stream read and maximal extraction of the
Ogma2 discussions, explicitly prohibiting schematic/PCB changes until the
final stack is authorized. Read the naming discussions and both complete
technical recordings with Seán, Anav and Arnav. Created the
[source-backed session review](docs/architecture/2026-09-10-session-review.md)
with recording timestamps, source locators, observations, changing positions,
clarifications, candidate learning projects and unresolved review gates.

Recorded Burrito/Croí2, Churro/Foinse2 and Fajita/propulsion as working spoken
names. No CAD/file/net renaming. Reopened requirements include local servo
count, central versus autonomous remote actuation, CAN trunk/peers/termination,
MCU sizing by role, optional-rail purpose, operator indications and pre-trigger
logging. Existing hardware and interface contracts remain the preserved draft,
not final-stack approval. The energetic mechanism discussion was deferred,
not accepted; existing inhibits, DNPs and qualification limits remain.

Updated current-system, entrypoints, every architecture chapter and the review
procedure to expose the new review state and explain jobs/mechanisms before
part inventories. Added responsibility, power and recording diagrams. Retained
the earlier detailed research and dated implementation facts. Distinguished
reported ground-recording capability from verified implementation, current
draw from physical outcome, and interrupted-write recovery from mechanical
crash survival. Captured the separate experimental payload-carrier direction
without enlarging the flight core or assigning new people to flight-critical work.

No schematic, PCB, firmware or controlled electrical contract was changed.
No fabrication, energetic testing, flight, purchase, commit or publication was
authorized by this pass. The pre-existing AGENTS.md edit is unrelated and
preserved. Validation of the documentation is recorded in the task handoff;
the earlier CAD/ERC/DRC results were not rerun or represented as new results.

Documentation checks: whitespace/diff check passed; 170 current/new local links
and anchors resolved across the 20 touched documentation files. No hardware
diff. A wider history scan found four pre-existing broken links under
`hardware/Ogma2/`; historical entries were left untouched rather than rewritten.

## 2026-09-11 — rebuild the reading pack for iterative whole-system sessions

Seán clarified that extraction and annotations were insufficient: the next
session must read the improved whole architecture, with earlier confusion
resolved in the text and diagrams themselves. Rewrote all nine main chapters
around functions, mechanisms, ownership, failure boundaries, retained choices
and unresolved alternatives. Removed component designators from the main
reading text. Preserved complete earlier chapters, calculations and detailed
part references in the linked implementation-reference directory.

The pack now starts at its overview, not the session extraction. Updated the
entrypoints and review procedure: read the whole system, capture discussion,
rewrite the affected explanation and diagram, reconcile the whole pack, repeat.
The operating procedure distinguishes this mode from a bounded single-section
review. No technical proposal became accepted merely through this rewrite.

Checks: all 14 Mermaid diagrams rendered in a local browser preview; inspected
the power and remote-actuation comparison layouts, then improved the latter
to stack the alternatives readably. Checked 266 resolving local Markdown links
across changed/new documents; the same four pre-existing historical broken
links remain. Main chapters contain no component designators. Diff whitespace
checks pass. No hardware or firmware edits; pre-existing AGENTS.md changes
preserved. No commit or push.

Next checkpoint: begin the next joint session at chapter 0 and work through
chapter 8. Capture both architecture decisions and presentation failures for
the next revision. Final-stack authorization remains required before CAD work.

## 2026-09-11 — investigate MCU pin pressure rather than defer the question

Seán requested the actual resource investigation and visible allocations in
the MCU chapter. Exported a fresh KiCad XML netlist without changing CAD;
checked all 200 allocated physical pads against their CSV logical-to-physical
net mappings. All passed. Added a read-only audit utility, grouped source-backed
tables and two inline Mermaid allocation diagrams.

Flight uses 79 of 80 port pads, with PC13 deliberately quiet; the other 20 pads
serve supply/reference/core-capacitor/reset/boot functions. Comms has 27
externally connected port pads, two labelled-but-unused legacy radio pins,
two unfitted LSE reservations, one quiet reservation and 48 other unused ports.
The initial “29 connected” reading counted the legacy radio labels; inspecting
their single-node nets corrected that distinction before final documentation.

Recommendation, not acceptance: compare H563 LQFP64 for comms, retaining the
same peripheral choices except USART3 TX/RX moves to PC10/PC11. Desk-checked
package availability and AF mapping against ST's tables. A smaller H503-class
device raises a concrete RAM/service-buffer question. Price, actual power,
target firmware fit and timing remain unmeasured. No target firmware build was
found in this repo; no synthetic empty build substituted for the actual work.

The [audit](docs/mcu-pin-capacity-audit-2026-09-11.md) records counts, port groups,
candidate mapping, savings and remaining checks. The main reading chapter now
explains why sensor isolation and output supervision consume so many pins.
No pin CSV, schematic, PCB or firmware was edited. No commit or push in this pass.

Validation: all 16 reading-pack Mermaid diagrams render; inspected both new
allocation diagrams locally. The read-only audit passes all 200 pads and rejects
an intentionally mismatched mapping in an in-memory negative test. Local links
and diff whitespace checks pass.

## 2026-09-11 — power, recording and CAN desk analysis

Seán authorized the three follow-on analyses after the MCU audit. Updated the
same reading chapters rather than leaving the findings solely in an appendix.
The [supporting audit](docs/power-recording-can-audit-2026-09-11.md) and read-only
budget script preserve inputs, calculations, source status and limits.

Observed in the unchanged schematic/netlist: optional power also feeds CAN,
the sounder and DNP continuity-test paths. The prior simplified picture omitted
these. Local current monitoring shares AUX. NOR/CAN are not on held flight
power; processor hold-up cannot establish emergency-flush capability.

Calculated: 800 µF effective, 204 mA and an assumed 0.25 V usable fall gives
0.98 ms; actual margins remain unmeasured. At 96,672 B/s, 128 KiB is 1.356 s,
not the older ~1.38 s. After the existing mission budget and 64 MiB reserve,
20,738,816 bytes remain, roughly 214.5 full-rate seconds. Single-lane NOR
transfer is not ruled out by the simplified program/transfer budget.

Recommendations only: retain the optional rail; use continuous full-rate
prelaunch recording with a proposed ten-second lead-in and bounded pad duration;
compare central control first for a 100–200 Hz remote-actuator scenario. CAN
traffic tables explicitly assume message counts/background traffic. No average
occupancy is presented as a latency proof or accepted actuator requirement.

Checks: arithmetic assertions pass; 66 local links resolve; all 16 Mermaid
diagrams render, with revised power/recording drawings inspected locally.
Main chapters retain no component designators. Diff whitespace passes. Croí
schematic and PCB hashes match their checked native snapshot. Macronix direct
PDF retrieval failed; indexed manufacturer timing text matched the prior study,
and that evidence limitation is recorded. No hardware, firmware or interface
contract edits; existing AGENTS.md changes preserved. No commit or push.

Next checkpoint: review these recommendations during the next whole-pack pass.
Actuator age/jitter and message inventory, actual load/hold-up measurements and
implemented recording format remain the discriminating evidence. Final-stack
authorization remains a separate gate.


## 14 September 2026 — integrate 13 September architecture review

Fetched origin successfully using a clean shell and fast-forward checked
`docs/reliability-review-execution`; local and remote both at
`695b6779faa45ee62949164e82c375551da11e83`. No incoming changes were missing.
Seán authorized documentation updates after remote retrieval.

Added the [13 September source-backed review](docs/architecture/2026-09-13-session-review.md)
from preparation, both complete meeting recordings, the drive reflection and
subsequent corrections to the earlier model response. Preserved source roles,
recording times, decision status and the distinction between interest and
accepted work ownership. No raw personal transcript was copied into the repo.

Updated the reading pack, current-system, review procedure and indexes. Recorded
two local servo channels and CAN FD as review directions while preserving CAD
and electrical definitions. Corrected pin-role explanations, rail alternatives,
hold-up terminology and diagnostic inventory. Marked chapters 6–8 unreached.
Added interface reconciliation notices without changing electrical contracts.

Validation: relative file targets resolve and Markdown fences balance across
changed documentation; diff whitespace checked. Existing Mermaid bodies are
unchanged, so no new diagram render was required. No hardware or firmware test
was run: those files were not changed. Existing AGENTS.md edits preserved.
No commit or push. Next checkpoint: resolve open choices and complete chapters
6–8 before final-stack authorization and CAD/interface reconciliation.


## 18 September 2026 — correct incomplete meeting extraction

Seán identified that the prior integration missed explicit meeting requests and
requested Luna crawls of the full meeting and subsequent reflections. Completed
independent crawls of A, B (including adjacent LTS), preparation and reflections;
reconciled transcript guesses against existing pin/netlist evidence. Added the
[full change ledger](docs/architecture/2026-09-18-meeting-change-ledger.md), with
chronological findings and completed/partial/open deliverables. The previous
summary captured themes but did not complete the requested transformations.

Concrete correction: B 00:07 requested actual ordered protection elements.
Replaced chapter 2's abstract power diagram with source-entry, regulator and
load paths traced through the preserved netlist. Corrected startup-bias source,
made load switches distinct from current limiters, and showed the hold-up
capacitor as a side connection. Clarified servo back-power and local recording;
marked the narrow MCU recommendation challenged and removed the stale claim
that the energetic review was deferred. Added an evidenced understanding marker.

Validation: all three new Mermaid diagrams parse. Browser rendering was not
completed because the expected browser executable was unavailable; no visual
render claim is made. Relative file targets and Markdown fences checked in edited docs and new log
entries; `git diff --check` passed. A pre-existing historical log link to
`hardware/Ogma2/schematic-status.md` is broken and remains outside this edit. Hardware, firmware and existing AGENTS.md edits were
not changed. No commit or push. Outstanding research, external requirements,
operator-indicator mapping and physical tests remain explicitly open in the
ledger rather than being counted as completed by summarization.

## 18 September 2026 — remaining desk investigations for next design review

Seán requested remaining investigations before the next afternoon review and
asked to conserve usage. Reused retrieved meeting evidence and pin/netlist audits;
batched manufacturer research without additional agents.

Added [review investigations](docs/architecture/2026-09-18-review-investigations.md)
and linked the answers from each relevant chapter, indexes and the change ledger.
Includes MCU shortlist and selection rationale, per-function pin justification,
PC13 erratum, rail alternatives, source thresholds versus proposed operating
acceptance points, bounded comms logging, RSSI direction, GNSS limits, proposed FD
traffic/timing envelope, servo power example, partial-power behavior, indicator
connections, reset examples and a discriminating test matrix.

Material new evidence: manufacturer MAX-M10S specification includes ≤4 g and
500 m/s limits as well as 80 km; low altitude alone does not qualify boost aiding.
ST ES0565 confirms PC13/LSE crystal limitation on LQFP. TI TXU0304 supports the
stated powered-off boundary under specified conditions. Recommendations remain
proposals; no part, pin, bus rate, supply or output-circuit change was implemented.

Checked FD planning arithmetic (13.3%, 29.2%, 55.7% for declared scenarios),
logging-capacity subtraction, hold-up and stall-capacitance arithmetic. Checked
74 relative file targets in current-system/architecture documents, balanced
Markdown fences and diff whitespace. No physical tests claimed. Manufacturer
price table lacked comparable quotes; U575 direct page retrieval failed, so its
headline shortlist data uses the official indexed summary. New-family AF maps,
actual actuator/peer inputs and bench validation remain open and named.

Next review: use the decision table, resolve mission/interface assumptions,
assign accepted owners for external inputs/tests, then continue chapters 6–8.
Existing AGENTS edits and all CAD/firmware preserved. No commit or push.


## 19 September 2026 — connected component proposal for joint review

Seán authorized turning the latest architecture review into a concrete, concise
component proposal. Reworked the existing architecture index and nine chapters
in place: connected diagrams, exact retained/proposed parts, short reasons,
alternatives and named remaining checks. Updated entry points and review
procedure; marked the earlier three-rail recommendation superseded by this
proposal. These recommendations are not accepted architecture or CAD changes.

Proposed H563VIT6 flight / H563RIT6 comms, with a complete 64-pad comms map;
two 3.3 V LDO domains with the independently switched comms branch downstream;
two local servo interfaces; continuous prepared recording and streamed service
transfer; a bounded CAN FD proposal and first radio interoperability settings.
Retained the existing sensor and recorder parts. Selected a specific hold-up
capacitor candidate with explicit footprint/environment checks still outstanding.

Native-netlist tracing corrected an important detail: the comms enable gate is
a battery-dependent selector, not a simple OR. Battery operation retains flight
control even with USB connected; USB-only service forces comms power on. Checked
that the 64-pin MCU internally bonds VDDUSB to VDD. Numerical checks cover
current-limit selectivity, the downstream switch's DC voltage budget, LDO loss,
hold-up, logging capacity and ideal service-download time. Static budgets do not
prove fault-transient behavior or physical qualification.

Validation: manufacturer-source and native-netlist review; all 11 Mermaid
diagrams rendered in the local browser, with overview and power layouts visually
inspected. Added reproducible source-enable, pin-map and budget checks in
`docs/calculations/component-proposal-checks.py`; they pass. Checked edited
Markdown file targets, fences and diff whitespace. The pre-existing broken
historical log link remains outside this change.

Remaining: the recovery/staging output implementation is unresolved; actual
actuator, antenna/harness and vehicle peer inputs still constrain final choices.
Board layout, dynamic power/fault behavior, throughput and environmental
qualification require implementation and measurement. CAD, firmware, installed
interface contracts and pre-existing AGENTS.md edits preserved. No commit/push.


## 19 September 2026 — connector and arming review restored

Seán identified missing explicit treatment of FC and energetic short-to-arm
connections. Added a dedicated connector inventory and operator-boundary diagram,
linked from the review index, overview, power, output, status and servo pages.
Native netlist and power contract confirm J103 is a maintained electronic battery
enable, with USB service possible when open. The physical output-arm assembly
remains unresolved; neither arm-sense inputs nor J6601 define that assembly.
No new energetic wiring or jumper assignment introduced.

Flagged that the proposed six-contact servo connector matches the output-harness
family/contact count: mis-mating prevention must precede acceptance. CAD and
interface contracts unchanged. Markdown links/fences and diff whitespace checked.


## 19 September 2026 — review-surface and reasoning correction

Seán rejected another partial documentation fix and requested a full pass against
the actual meeting criticisms. Replaced the overview with one review surface
containing source and branch power drawings, signal map, connector inventory,
operating states and consequential choices. Supporting chapters retain pin maps,
calculations and sources. No new summary/report added to the reading path.

Corrected recommendations: withdrew the six-contact servo-harness substitution;
retain ten-contact 430451000 with two used groups. Restored remote control split
to undecided pending mechanism timing. Replaced generic power-reliability claims
with one/two/three-rail consequences for named faults, acknowledging the absence
of comparative failure-rate evidence. Corrected monitoring I2C3 label to I2C4
from the flight pin CSV. Comms cycling preserves already-enabled NOR/CAN branches.

Brought MCU workload/headroom/alternatives and control-pin purposes, receiver-owned
RSSI in both directions, shared-versus-independent comms-recording consequences,
and operator indication/readback into the active chapters. Existing understood
material remains available; no new team acceptance/comprehension is inferred.

Output circuitry and physical energetic arming remain incomplete; this revision
does not claim to have designed that assembly. Actuator/peer/antenna inputs and
physical validation remain distinct from completed desk checks.

Validation: source/pin and arithmetic checks; current Markdown target/anchor and
whitespace checks. Browser render checks recorded below after final inspection.
CAD, firmware, installed contracts and existing AGENTS edits untouched. No push.

Final validation: all 14 diagram instances render across 11 preview pages;
overview source-path layout visually inspected. 141 current file/anchor references
pass, as do proposal arithmetic/pin checks and diff whitespace.


## 19 September 2026 — visible justification links

Added opening question-to-source maps to MCU, power, servo, service, RF, sensor,
vehicle-link and connector chapters. MCU package and control-pin arguments also
link directly to the relevant audit sections beside the claims. Links distinguish
current proposals/calculations from dated rationale; the older MCU audit now
links back and flags its superseded whole-block buffering assumption. No new
technical selections. Local file/anchor validation and diff checks pass.


## 22 September 2026 — whole-system schematic-readiness audit

Seán requested a comprehensive pass intended to make the next review a closing
architecture review: test every section against schematic handoff, with special
attention to energetic outputs, Churro and whole-system dependencies. Fetched
`docs/reliability-review-execution`; HEAD and remote were both `9a8c2a2` at audit
start. No team acceptance or final-stack authorization inferred.

Updated every active chapter with handoff status and closure requirements. The
overview now joins those statuses, named failure consequences and five closing
decisions. Added linked supporting evidence in
`docs/architecture/2026-09-22-schematic-readiness.md`; it is optional supporting
material, not another sequential reading assignment.

Concrete changes:

- Included LDO/divider/leakage/switch corners and supervisor release hysteresis.
  Proposed 31.9 kΩ / 10 kΩ service divider, both 0.1%, for 3.352 V: calculated
  comms release margin at 300 mA improves from 20.5 to 75.8 mV before further
  wiring/transient loss. Flight remains 3.296 V. Added a proposed 50 mV loss
  allocation; neither load allocation nor dynamic margin is measured.
- Separated USB bootstrap/readback budgets from battery operation. Native
  preconfiguration limit is 50–100 mA; configured range about 387–491 mA.
  The full 2.4 W allocation would need about 649 mA in the stated USB example.
  Defined restricted proposed load modes, startup/inrush and permission withdrawal.
- Audited every local limiter against aggregate service protection. Conservative
  NOR-fault allocation leaves only about 23 mA against aggregate minimum. Made
  source-cycle-only aggregate recovery and simultaneous loss of comms/NOR/CAN/
  monitoring explicit. Separate regulators still share the upstream converter.
- Expanded Churro's actual two-source circuitry, protections, monitoring and
  connectors. Distinguished autonomous protection from AUX-powered telemetry;
  identified series-protection, common-return, pack/fuse/load and NTC-lead gaps.
- Bounded recording-format/footer overhead and combined-rate staging duration.
  Conservative spare beyond the 64 MiB reserve is 6,452,736 bytes; the larger
  17,918,656-byte figure requires footers to fit the original framing allowance.
- Separated directly observable rail/status signals from unavailable or inferred
  state; added package, clock/reset, service, RF and installed-harness handoffs.
- Distinguished the existing three-channel output draft from a completed
  operational subsystem. Output requirements, physical arm assembly and responsible
  engineering assessment remain a design blocker. Preserved DNP safeguards;
  supplied no firing-circuit design, component values or arming wiring.

Validation: fresh native KiCad exports match all tracked pin/net assignments and
reference/value/footprint tuples for both boards (Burrito 2,179 pins / 643
components; Churro 306 / 113). All 44 Burrito schematic hashes match the saved
check report. Updated component/pin/calculation checks pass; 188 current Markdown
file/heading references and fences pass; all 14 diagrams render across 11 preview
pages. Overview and revised voltage-margin table visually inspected. Diff
whitespace passes. Existing ERC/DRC counts are dated evidence, not rerun results.

Remaining: D1–D5 acceptance; actual output/actuator/source/installed-interface
inputs; implementation, layout and first-full-PCBA measurements. Full Macronix
PDF retrieval remained unsuccessful; indexed primary timing evidence stays
labelled as such. CAD, firmware and controlled interfaces unchanged. Pre-existing
AGENTS.md changes preserved. No commit or push.

## 22 September 2026 — concrete capture baseline and placement handoff

Seán asked the model to synthesize the remaining choices, with justification,
rather than return another list of team research tasks. He clarified the target:
after his future green light, Codex captures schematics and places components;
Seán routes. Anav retains firmware implementation. That division of work is now
explicit in the capture specification, current-system and review procedure.
It does not lift the present CAD hold.

Added `docs/architecture/schematic-capture-spec.md`, a proposed flight pin map
and a discoverable justification index with power, Churro, recording/service and
interface/installation rationale. Reconciled all active chapters and drawings.
Preserved the earlier same-day audit with an explicit supersession notice.

Recommendations and their reasons:

- Retain three LDOs. The two-rail candidate shared a comms-regulator fault with
  loss of logging/CAN, contrary to the useful FF-01 boundary. Keep U1501/U1601
  upstream of their original regulators; use 66.5 kΩ / 49.9 kΩ limits respectively.
  Reallocate only flight PD10 to SERVICE_POWER_EN, including the off-default
  pulldown; give service recovery a bounded, sequenced restart.
- Set all three TPS7A91 dividers to 31.9 kΩ / 10 kΩ, 0.1%, nominal 3.352 V.
  Calculated 3.310–3.394 V corners leave ~116 mV static supervisor release margin,
  ~66 mV after the proposed 50 mV healthy-loss allowance. Upstream switch drop
  belongs in LDO input-headroom analysis, not another output-voltage subtraction.
- Allocate 200/300/200 mA flight/comms/services. The documented conservative
  logic endurance calculation gives 29.69 Wh for 8 h + 4 h. Propose a 2S 8 Ah
  reference source with ≥30 Wh usable; usable fraction, efficiency and recovery
  load are explicit assumptions. Actuator energy is additional. USB retains
  distinct restricted bootstrap/configured/suspend behavior.
- Define Churro's AV 3 A / PROP 2 A continuous interface envelope and exact
  source-fuse/holder assembly. Select Vishay probes, REF3325 bias, ADG7421F
  protected external leads, connector TVS, filters and diagnostic windows.
  These are proposed electrical boundaries, not qualified pack/thermal/fault
  results. Protection remains autonomous and monitor loss remains observable.
- Keep two bounded raw-2S, 3.3 V PWM interfaces, 1.5 A combined normal allocation;
  retain local control, add no remote actuator node. Keep existing Classical CAN
  commissioning while documenting a coordinated FD migration separately.
- Replace the cross-sector NOR commit candidate with 15 data pages plus one
  footer per 4 KiB sector. Define footer/CRC/epoch, recording region, preparation
  and throughput target. Conservative storage leaves 5,689,344 bytes within the
  192 MiB region; its last 64 MiB remains reserved. Worst-case block-erase
  preparation is 102.4 minutes plus verification, explicitly outside flight boot.
- Define exclusive source population variants, retained harness controls, passive
  RF reference test assemblies and placement delivery criteria. Located the exact
  Molex 1053111102 sales drawing; footprint construction is now an assigned
  implementation task, not an unanswered request for the team to find the source.

Evidence: native netlists checked for divider values, limiter EN connectivity,
existing ADC filter nodes and unused 6200-series references. Primary TI, ADI,
Vishay, Molex, Littelfuse and Taoglas documents support the new choices; sources
are linked beside the rationale. The complete manufacturer-authored Macronix
Rev 1.0 mirror was inspected, while the exact Rev 1.1 source remains limited to
indexed manufacturer text; that distinction is explicit. No bench result is
inferred from component ratings or desk calculations.

Validation: proposal calculation script passes, including both complete MCU maps
and the single changed flight pad, rail/limiter/energy corners, storage/CRC and
probe-transfer checks. All 266 relative file/anchor references across 22 active
or supporting pages pass. Seventeen preview pages render, with all 15 diagrams
valid; updated three-domain power and Churro temperature drawings visually
inspected. Diff whitespace passes. Native CAD, frozen hardware pin CSVs, firmware
and controlled interfaces remain unchanged; no new ERC/DRC or hardware run.
Pre-existing AGENTS.md edits preserved. No commit or push.

Remaining boundary: the energetic-output/physical-arm design is incomplete and
excluded; DNP safeguards remain and no firing-circuit design or arming wiring
was supplied. Ordinary electronics choices now have a concrete proposal for
acceptance. Later physical qualification, owning-peer agreement and routing/
manufacturing release remain distinct from authorizing capture and placement.

## 22 September 2026 — capture-specification sanity check

Seán requested one sanity pass. Corrected documentation and checks; no capture
or placement was authorized or performed.

Found a material weakness in the previous map validation: it checked allocation
and CSV structure but retained functional shorthand from the frozen input CSVs.
That shorthand was not an exact electrical net list. Following it literally
could bypass partial-power boundaries or connect ADC pins to raw measured rails.
Corrected both proposed maps against the native Burrito netlist:

- Comms UART retains CC_COMMS_TO_FLIGHT / CC_FLIGHT_TO_COMMS at U4301;
  USB configuration, battery-valid and fault reporting retain their CC_ nodes.
- Flight ADC pins retain the actual ADC_ front-end nodes. Both processors retain
  their separate VDDA, clock, debug and status nets. Unused pads use NC as an
  instruction, never a shared electrical net.
- Only flight PD10 changes functional allocation; the comms UART migrates from
  PD8/PD9 to PC10/PC11 with the package change. Other corrected names preserve
  existing connectivity. Frozen hardware CSVs remain unchanged.

Extended the calculation checker to compare every proposed MCU connection to
native electrical nodes, including the migration and combined analog-supply
pads. The earlier log's successful map check must not be read as proof that its
old net-name aliases were safe to use directly for capture.

Other corrections:

- ADG7421FBCPZ-RL7 package is CP-10-16, not CP-10-17. Verified the official ADI
  Rev 0 ordering guide and outline, p. 30; ten signal-pin assignments unchanged.
- REF3325 input C6201 becomes 1 µF, matching TI REF33 Rev I §8.1/§8.4 bypass
  guidance. Output C6202 remains 1 µF. Both capture and rationale tables agree.
- Made third-servo removal explicit: remove R6606/R6607, disconnect the third
  connector group, ground unused U6804 A3 and leave B3Y unconnected. Other
  terminations and DNP safeguards remain as before.
- The proposed 100 ms service-off interval is a bench starting value, not proof
  of peripheral reset. Released timing requires measured discharge and restart.
- Logger extraction preserves valid sectors after gaps; restart cannot trust a
  lost RAM cursor or overwrite data speculatively. Cursor recovery is bounded
  background work; flight proceeds with recording unavailable until safe.

Validation: all 164 proposed MCU pads pass native-node comparison; the existing
rail, limiter, energy, recording and probe calculations pass. All 267 relative
file/heading references across 22 pages pass. Regenerated 17 preview pages;
inspected revised capture, MCU and Churro pages, including MCU diagram rendering.
Whitespace checks pass. Native CAD, firmware and controlled interfaces unchanged;
no new ERC/DRC or bench result. Pre-existing AGENTS.md changes preserved. No commit
or push. The separate incomplete energetic-output/physical-arm scope remains
excluded; this pass does not grant a full-platform capture green light.

## 29 September 2026 — private review-branch publication

Seán authorized pushing the latest documentation to the existing private review
branch for the departmental introduction. Repository visibility and access remain
unchanged; he will grant access individually. This is publication of a proposed
review baseline, not acceptance of its architecture or authorization to change CAD.

Included the 22 September readiness audit, concrete capture specification,
justifications, corrected proposed MCU maps, numerical checks and reconciled
reading entrypoints. Preserve the pre-existing AGENTS.md working-tree edit outside
this documentation commit. No hardware, firmware or controlled interfaces changed.

Pre-push checks: all 164 proposed MCU pads agree with native electrical nodes;
rail, current, energy, recording and probe calculations pass; all 267 active
file/heading links pass. Four broken links in older log entries already existed
at the parent commit and are retained as history. Their former hardware/Ogma2
paths refer to files now under hardware/croi2; no new active-document link uses
those old locations. No credentials, raw transcripts, private correspondence,
temporary previews or machine paths were found in the intended changes.

The branch-relative docs/architecture/00-overview.md remains the intended QR
entrypoint. Access requires permission to the private repository. Energetic-output
and physical-arm design remains incomplete and excluded from the capture proposal.


## 30 September 2026 — full-repository sanity pass and illustrated system tour

Seán requested a full sanity audit and a digestible picture of the boards, power/
data topology and connector families. He reported Anav's proposed shared low-side
switch with one high-side switch per energetic output, explicitly as a
recommendation. Recorded it as reported/unreviewed/unaccepted; no primary design
note was inspected. Existing DNP safeguards and unresolved arm assembly remain.

Fetched remote state. Review branch HEAD f18141e equals origin; main remains the
older f81e6a6 baseline. Inspected the full tracked tree, controlling documents,
interfaces, both native CAD projects, local dependencies and verification tools.
Added docs/architecture/system-tour.md and 2026-09-30-repository-sanity.md, indexed
from the current entrypoints. The tour separates September 22 proposals from
September 8 CAD, includes source-backed manufacturer connector images and makes
external Fajita/groundstation/recovery ownership explicit. Clarified the dated
firmware handoff and its nonportable historical research references.

Fixed the obsolete Foinse check_schematic_full.py copied-MCU body by delegating
to the canonical MCU-less checker while preserving native pin helpers/CLI. Both
entrypoints now return the same 113 components, 306 pins and 117 assertions;
negative merged-branch detection remains. Corrected two active manifest links.
Labelled the older budget tool's September 11 scenarios as historical rather
than silently changing their ledger.

Fresh KiCad 9.0.6 netlist/ERC/DRC exports were written to temporary audit paths,
not tracked evidence. Ref/pin/net maps equal saved native outputs. Croí: 643
components, 2,179 pins, 381 assertions, 28 DNP preserved; ERC four errors/six
warnings, DRC 61 violations plus 499 unconnected items and missing J101. Foinse:
113 components, 306 pins, 117 assertions, zero ERC; DRC 24 violations plus 262
unconnected items and missing J101. Fresh DRC categories match saved reports.
Both board identity/pad/geometry checks complete, including in-memory negative
mate-disconnection tests; headless wx emitted an initialization diagnostic, so
no interactive GUI validation is claimed. All 160 manifest-hashed dependency
files match and are tracked. All 12 tracked Python scripts parse; current
proposal checks pass 164 MCU pads and desk budgets; 12 host replay tests pass.
None is target or hardware qualification.

Material outstanding work: incomplete output/physical-arm design; absent exact
Nano-Fit footprints on both boards; Burrito USB board/library geometry mismatch;
native ERC/DRC/routing/manufacturing review; physical capacitor/source/harness
assembly; target firmware and measured source/USB/recording/RF/peer/mission tests.
CAD, frozen pin maps, controlled contracts and saved native reports unchanged.
Pre-existing AGENTS.md changes preserved. This pass grants no capture/placement,
manufacture or flight authorization; no commit or push.


## 6 October 2026 — flight-loss fixes decided; capture specification amended

Seán decided D-6.1–D-6.10 after a review of over- and under-protection
(`decisions.md`). Pyro and servo energy now tap the battery side before U101
through their own fuses; pyro passes an external arm switch (J6101). Recovery
outputs are current-limited TPS1H100 high sides (≈2.0 A); one-shots, low-side
switches and permit gates are removed; staging is DNP. Firmware holds the
battery enable on in flight (Croí, and Churro AV over Samtec pin 8); U101 and
U1001 auto-retry. Flight VBAT gets its own hold-up. Sensors run directly from
FLIGHT_3V3; the USB-compliance gate on core power is removed. The 100 km sortie
becomes an overlay. Recording starts full rate at launch detect.

Evidence: netlist values checked against TI TPS26630, TPS1H100-Q1, TPS2121 and
TPS3700 data sheets; Rev 1 closure (unexplained aloft reset, intermittent
battery connector). Not checked: H563 VBAT-mode current, TPS26630 behaviour of
Q101 under faults, servo regeneration in practice. Added a draft recovery-logic
chapter for Anav's review. CAD unchanged; the proposal pin CSVs keep 22 Sep nets.


## 6 October 2026 — documents archived; one entry path

Moved superseded reviews, audits, studies, dated decision records,
implementation reference and the earlier current-system snapshot to
`docs/archive/`, with an index. Live links were updated; the verbatim history
snapshot and older log entries keep their original paths. README, the docs
index and the chapter index now start at the system tour and `decisions.md`.
The old budget script moved to `docs/archive/tools/`. No content in archived
files changed beyond link paths.


## 6 October 2026 — two processors decided; live docs rewritten for reading

Seán decided to keep two processors, flight and comms (D-6.12). Recorded in
`decisions.md`, `current-system.md`, the processor chapter and the firmware
handoff; the "one MCU or two" open question is closed.

Found and fixed an error from the earlier 6 October commit: J6101, the pyro arm
connector, had been specified as Micro-Fit 430450200, the same part as Churro
J701 (raw 6S PROP output). A crossed harness could then put propulsion voltage on
the pyro rail. J6101 is now a 2-contact connector that must not mate J701 or the
GH enable loops, part chosen at capture; added to D-6.1's checks and the open
arm-switch row.

Rewrote the live architecture chapters, system tour, capture specification,
justifications, the four interface contracts and the hardware README in plain
language. Facts, numbers and decisions are unchanged except where a decided row
superseded older text (power-contract numbers table, servo count, 192 MiB window
now the Kármán overlay). Every Mermaid diagram rendered with mermaid-cli
(17 diagrams); long left-to-right chains were turned top-to-bottom so they stay
legible at page width. The boundary contract changed wording only; authority
and content are unchanged. Link and anchor checks
clean; proposal checks, reset replay (12 tests), MCU pin audit and both board
checkers pass. CAD unchanged.


## 7 October 2026 — three pyro channels and three servos are a core requirement

Seán: Burrito needs three pyro channels and three servos (D-7.1). This reverses
the staging-DNP part of D-6.2 and the two-servo part of D3. Channel 3 is the
staging / air-start channel and keeps the hardware reset inhibit. Servo 3 stays
on PD10 (LPTIM2, its own period) as drawn in the CAD, and the service-power
enable moves from PD10 to PE8 (freed by D-6.2).

Proposed for Sunday (D-7.2): staging energy through its own 2-contact arm
connector J6102 from F6101; latch U6001 cleared by `FLIGHT_NRST`, clocked by PD15,
D = `STAGE_ARM_INVALID` so a new flight can only be set with staging disarmed;
one gate (U6502) ANDs the latch with `PYRO3_FIRE`. Found while checking the CAD:
the native latch's disarm qualification (`STAGING_DISARM_PROOF` into U6002) has
only a pull-down, so the drawn latch could be set with staging armed;
`STAGING_ARMED_VBAT` has no source; and the SN74LVC1G97 symbol ties IN1 to GND,
so it can only make A AND NOT B. The proposal fixes all three (D = staging
disarmed; J6102 feed; a true AND gate), not the CAD.

Updated decisions, current-system, the capture specification, chapters 01–04
and 09, the system tour, the power and interface justifications, the flight
fault and power contracts and the firmware handoff. The proposal pin CSV still
holds 22 September nets; the capture specification's pad table supersedes its
PD10 row. CAD unchanged.


## 13 October 2026 — Enchilada roll-control board proposed, not decided

Seán and Arnav (Discord DM, 13 October 20:56–21:39 Irish) proposed moving roll
control to its own board, now named Enchilada, as a third CAN peer. Recorded as
Proposed D-13.1 with an Open table, revised after Seán's review notes the same
evening. Anav hasn't reviewed it. D-7.1 stands: Burrito's three servos make
bounded, event-triggered moves only. Interfaces and chapters change only if
D-13.1 is decided.

Observed:

- 500 kbit/s Classical CAN, 11-bit IDs, worst-case stuffing: streaming at 1 kHz
  takes 57–69% of the bus for the full IMU as 3 × 6 B frames, 44–54% for gyro
  and accelerometer as 2 × 8 B, and 22–27% for gyro alone. Fixed traffic (slow
  state, authorisation, roll status, Fajita reservation) is ≈7–8%.
- Burrito has no magnetometer.
- Burrito's restart targets are 100–550 ms (flight-fault contract; unmeasured).
- Croí's CAN end has fixed 120 Ω termination; the boundary contract names a
  two-node link.
- Churro's envelopes are AV 3 A and PROP 2 A (D2).
- J6602 carries all three Burrito servo triplets on contacts 1–9; contact 10 is
  unwired. Dropping to two servos would free contacts 7–9, not the connector.
- EuRoC System Requirements Document Issue 1.1 (30 April 2026), §7: active
  control only for stability augmentation, braking or guided recovery, landing
  or deployables (RQT-0650); vehicle stable with actuators removed or locked
  (0660); fail safe, surfaces to neutral and thrusters disabled (0670); boost
  dormancy to at least 1500 m AGL without flight history, 500 m default with
  limited history (0680); control electronics meet the recovery redundancy rule
  RQT-0240 and §5.4 wiring (0690); stored energy meets §6.1 (0700).
- EuRoC 2024 Rules & Requirements v05, now superseded: control algorithms
  submitted with the RocketPy simulation (§9.5); active control makes a vehicle
  eligible for selection for a design review (§8.2).
- UKRA allows active surfaces for roll control and stability; surfaces that
  guide to a specific point are prohibited.

Recommended, not decided:

- Gyro on Enchilada for the fast loop, slow state from Burrito. It costs one
  driver; Anav's call.
- STM32H563 by default; H7 only if the sims' controller misses its budget on an
  H563.
- Neutral through a path that survives hung firmware. A hung MCU's timer keeps
  sending the last pulse, and a servo that loses power holds position, so
  neither firmware centring nor a Churro fuse trip is enough.
- Enchilada CAN IDs below Burrito's and Fajita's, on an unterminated stub.
- Its own fused Churro output with local bulk. Three servos at stall may exceed
  either existing envelope.

Unknown: actuator and current (requirements meeting 14 October); what RQT-0690
requires of one roll board; which competitions apply this year (the Irish
competition and IREC unchecked); the sims' controller and its compute cost; the
propulsion owner's agreement to a third node.

Updated `decisions.md` and `current-system.md`, where D-13.1 is marked proposed
and the two-node CAN rule stands. CAD unchanged.


## 15 October 2026 — avionics inputs from the 14 October requirements meeting

Source: the HiPR requirements meeting, 14 October evening, from Seán's
recordings. Items are as said unless marked verified; only what affects the
avionics is recorded. The 11 October flight computer meeting didn't run (Seán to
Arnav, 12 October), so D1–D3, D5, D-6.11 and D-7.2 move to Sunday 18 October.

Said:

- EuRoC, October 2027: liquid, about 6 m long, 6 in diameter, may grow. Bottom
  up: engine, tanks and COPVs, av-bay (RCS at its bottom), recovery bay, grid
  fins, nose cone. Four charges, two drogue and two main, in the recovery bay.
  Every system tested by May.
- IREC: solid O motor, 152.4 mm, the same electronics without propulsion
  control. Application due 25 October.
- IRRC: a centre booster and two side boosters that separate mid-flight. The
  boosters were given as 54 mm with a 75 mm centre, then as 76 mm. They carry a
  CATS Vega or an Eggtimer. Rules not out.
- Closed loop: roll control and the grid fins (an experiment). RCS has four
  solenoids. The grid fins use servos or steppers, work under drogue and sit on
  their own board with power and CAN through a raceway. Sim Systems writes roll
  control's requirements.
- The rocket is armed on the pad before filling. Nobody is within 600 m once
  anything is pressurised. The electronics umbilical powers the rocket during
  filling and disconnects remotely at Go.
- Drogue descent at most 46 m/s (James, to check).
- Radu wants a magnetometer for the hopper, maybe the grid fins. Seán asked him
  what heading and accuracy he needs (#canards, 14 October 21:26); no answer yet.
- Jay's ask, as Seán described it: a pyro-over-CAN board for recovery. That
  conflicts with the rule that only the flight MCU commands recovery and staging
  outputs.
- Anav, first reaction to D-13.1: roll control is flight-critical, so it goes
  on the flight computer or is a separate payload; no new board. He'll bring a
  pyro-channel circuit on Sunday. He reads the docs as putting the arm switch on
  the low side; D-6.1 puts it in the battery-side feed.
- The electronics sub-team requirements in Notion are not to be relied on
  (James).

Verified, EuRoC SRD Issue 1.1 (30 April 2026): at least 6 h of battery life on
the rail (RQT-0320); no LiPo on board (0300); a CATS Vega in every stage, for
tracking (0430); fully redundant recovery electronics with their own power, one
set COTS (0240, 0250); arming features on the airframe, reachable from the
ground with the rocket vertical, opposite the rail (0260–0280, 0540–0550);
energetics safed until the rocket is in launch position (0530).

Recorded as Open rows in `decisions.md`; `current-system.md` gains the target
vehicles and next steps. Nothing decided. CAD unchanged.

## 2 November 2026 — review answers recorded: D-2Nov.1–D-2Nov.12

Seán answered the fifteen review recommendations (R1–R15) in chat on 2 November,
ahead of the Tuesday 3 November review with Anav and Arnav. All accepted as
recommended except R12, the magnetometer, where he chose to add one ("I
committed to Radion that we will"). Radion is the control-systems lead, written
"Radu" in the 15 October entry. The answers are in `decisions.md`:

- D-2Nov.1 (R1): a low-side CSD17318 per pyro channel again, on PA9 / PA10 /
  PD14, away from the port-E fire pins; four-step firing sequence; pre-arm
  low-side self-test. Continuity sensing works again.
- D-2Nov.2 (R2): staging gets F6102; F6101 is recovery only.
- D-2Nov.3 (R3): sensor supply links 0 Ω → 47 Ω; firmware parks a dead
  sensor's pins.
- D-2Nov.4 (R4): the power-hold RC holds SHDN above 2 V for ≥1 s with both
  22.1 kΩ pull-downs; assert at launch detect, re-assert within 50 ms of a reset
  in flight, release at LANDED plus a delay or a maximum flight time.
- D-2Nov.5 (R5): the energy tap stays after Q101; D-6.1's check closed with the
  netlist and TPS2663 §9.3.13 / §9.3.6. Servo regeneration still reaches the
  pack standalone; Churro-fed, the new ideal diodes block it, so the logic load
  and the servo bulk absorb it.
- D-2Nov.6 (R6): 2S Li-ion, metal-can cylindrical cells, 21700 by default;
  pad-mode target ≤150 mA; the pack alone covers six hours on the rail.
- D-2Nov.7 (R7): rail power from a ground umbilical at Churro, per-source ideal
  diodes ahead of the eFuses, no charging on the vehicle. Seán: "the whole point
  of the umbilical is that when on rail it just is alive through the umbilical,
  and then when we unplug it switches."
- R8: D1, D2, D3, D5 and D-7.2 accepted, D-7.2 amended by D-2Nov.1, D-2Nov.2 and
  the pin moves, with U6502 fixed as an SN74LVC1G08.
- D-2Nov.8 (R9): rules for closed-loop actuator nodes replace D-13.1
  (Enchilada); the board waits for Sim Systems' requirements.
- D-2Nov.9 (R10): what CAN may carry. Seán: "can should be for permissions and
  mode; slow state that survives Burrito's worst-case 550 ms restart; health;
  commands the receiver drops to safe when they go stale.. not high rate control
  loops."
- D-2Nov.10 (R11): pad datum tracked and frozen at launch detect; ground-test
  mode for EuRoC LV-0520; 1 Hz pad telemetry. D-6.11 stays proposed for Anav.
- D-2Nov.11 (R12): MMC5983MA magnetometer on I²C3 (PA8 / PC9).
- D-2Nov.12 (R13): release gates and test campaigns live again in
  `docs/architecture/11-verification.md`, with EuRoC's tests and the D-6.10
  capture assertions.
- R14 and R15 are documentation: `docs/firmware-interface.md` replaces the
  7 September handoff (moved to `docs/archive/`), and `decisions.md` now has one
  newest-first table per status with dates.

Judgment calls made while writing these up, for Tuesday's review:

- R1 first put the low sides on PA8 / PA9 / PA10. The magnetometer needs PA8
  for I²C3, so they went to PA9 / PA10 / PD14; the latch readback moved to PE14
  (with a 1 kΩ series resistor) and staging arm sense to PE15. PE10 and PE13 are
  spare.
- R7 said two ideal-diode controllers. It's four: each pack needs its own so the
  umbilical can't charge it.
- PA9 and PC9 (not PA10) are the H563's UCPD dead-battery pins, gating
  pull-downs on PB13 / PB14, the TDK IMU's SPI. Firmware sets `UCPD_DBDIS` at
  boot. Found in the KiCad symbol and confirmed against an ST community thread.
- TI gives the TPS26630 SHDN levels as 2 V rising and 0.8 V falling, with no
  guaranteed band between, so the hold RC is sized to stay above 2 V: 330 Ω and
  470 µF, ≈1.2 s at Churro's `AV_SHDN_N` with −20% capacitance.
- The magnetometer's link is 22 Ω because its minimum supply is 2.8 V; its INT
  goes to the spare PE6.
- Churro's AV divider moves to the pack side so the pack stays readable on the
  umbilical, and the live source comes from bus minus pack.
- After arming, a channel whose return node reads near the armed rail has a
  leaking high side and is never fired; the low-side self-test runs only with
  the arms open.

Also on 2 November: the EuRoC rule texts behind the open rows were checked
against the published SRD (LV-0240, 0260–0280, 0300–0320, 0480–0560,
0650–0700). The note under LV-0270 rules out ladders and stools. LV-0500
applies to N₂O, which boils below −50 °C. The pack and arm-switch access
question and the LV-0690 question go to Jay through #euroc-electronics.

The PR #2 description was corrected the same day: D-6.5 was not a brownout
weakening, and EX-10 is still cited by the flight fault contract.

CAD unchanged. Capture stays on hold until after Tuesday's review.

## 2 November 2026 — overnight check of the 2 November write-up

Every page changed in PR #2 read again end to end, with the link, table and
calculation checks re-run and the new parts checked against data. Fixed:

- Actuator-node CAN IDs. "Below Burrito's and Fajita's" could be read as
  numerically lower, which wins arbitration; D-13.1 meant lower priority. Every
  copy now says the IDs lose arbitration (numerically higher).
- Churro-fed regeneration. The sink is the logic load at the time, under 150 mA
  in pad mode, not the ≈0.6 A budget. The back-drive test runs at the lowest
  logic load and also watches U101's 8.99 V over-voltage, which is sensed at
  `VBAT_CROI_INPUT` (R1003 / R1004).
- Leak check after arming. A conducting high side shows as any rise above the
  disarmed continuity reading, not only a reading near the rail: a partial leak
  can grow once the low side takes R69x3 / R69x4 out of the path. 03 and the
  firmware interface say so.
- Recording budget with the magnetometer for the whole Kármán window:
  186,303,936 B, 198,725,632 B sector-rounded, 2,600,960 B spare in the 192 MiB
  region; staging 1.320 s. Added to `component-proposal-checks.py`.
- The capture spec's endurance row still gave only the D-6.8 path; it now
  carries D-2Nov.6. J6102's connector is rated above F6102, not F6101. The
  all-fire margin includes the low side's on-resistance.

Proposed for Anav's review of D-6.11 (not decided):

- No drogue, primary or backup timer, until the barometric altitude has passed
  100 m above the pad datum (or inertial evidence of flight with both barometers
  invalid). As written, a false launch detect on the pad with the arms closed
  would let the backup timer fire.
- A reset between launch detect and the first in-flight checkpoint boots as
  PAD, and after burnout nothing detects launch again. Write that checkpoint
  first, and consider a missed-launch backup.
- Any reset clears ground-test mode, and its checkpoint never reads as in
  flight.
- Write PE5 high every essential-loop cycle in flight. Set the hold-release
  delay knowing that, with J103's loop broken, release ends the GNSS beacon.
- Before the umbilical is pulled, the AV pack voltage is a go/no-go item. With
  R6111 still on Churro's protected PROP output, a missing PROP pack is
  invisible on the umbilical.

Checked, no change:

- PA8 / PC9 are I2C3 AF4, PB8 / PB9 I2C4 AF6, PD10 LPTIM2_CH2 AF3, PD0 / PD1
  FDCAN1 AF9; PA9 / PC9 are UCPD1 DB1 / DB2 with CC1 / CC2 on PB13 / PB14.
  Source: ST's CubeMX pin data as packaged in embassy's stm32-data. Every flight
  pad number in the docs matches.
- TPS3700 (TI SBVS187 §7.3.1): OUTA releases when INA+ rises past the
  threshold, OUTB pulls low when INB− does. So `RECOVERY_ARM_VALID` high means
  armed and `STAGE_ARM_INVALID` high means staging disarmed, as documented, and
  the latch can be set only with staging disarmed. U6001 PRE̅ is tied high and
  CLR̄ is on `FLIGHT_NRST`.
- CSD17318Q2: ≤30 mΩ at a 2.5 V gate, 0.9 V typical threshold.
- Hold RC, simulated with a BAT54-class diode model: ≈1.24 s at Churro's
  `AV_SHDN_N` and ≈1.69 s at `BAT_SHDN_N` with −20% capacitance and 15 µA of
  capacitor leakage; still ≈1.0 s at −30% and 30 µA. It has to cover about
  600 ms (550 ms restart plus 50 ms to re-assert).

CAD unchanged.

Later the same night, from three quick models kept outside the repo for now
(assumptions stated with them; models, not evidence):

- The events table as a state machine, fed a 3.6 g, 150 ms knock on the pad:
  launch detect passes, there's no burnout, and the backup timer fires the
  drogue about 25 s later. The main follows at once, since 0 m counts as at or
  below the main altitude. With the proposed 100 m gate nothing fires, and a
  modelled flight gives the same events either way. EuRoC arms before filling,
  so the crew is still at the rocket in that window.
- Pad datum over 2,000 modelled six-hour holds: captured at arming, the main
  would be 20 m off on a typical hold and 59 m at the 95th percentile; tracked
  with τ ≈ 3 min, under 1 m. Measuring the hold rate on 30 s means rather than
  single samples keeps gusts from holding the filter half the time.
- Regeneration, order of magnitude: about 1 mJ lifts 220 µF from 8.4 V to the
  8.99 V trips; a small servo rotor at speed holds 37–343 mJ. The bench test
  decides. Added to the Open table: standalone, nothing keeps a wrong (3S) pack
  off the servos since D-6.1.
- Continuity values, proposed for review: 3.9 kΩ 1% for each of R69x1–R69x4.
  Every E24 pair was checked with 1% parts, 8.4 V armed and one resistor of a
  leg shorted: ≤0.9 mA through the igniter on the self-test, ≤2.3 mA with a
  shorted high side, ≤1.3 mA back into the services rail. That keeps a tenfold
  margin for any igniter whose no-fire current is 25 mA or more. In 03 and the
  capture spec as a proposed start; the igniter choice still decides.
- MMC5983MA against MEMSIC's Rev A datasheet: VDD and CAP are shorted inside the
  part, 10 µF at CAP, VDDIO and SPI_CS as captured, address 0x30, 2.7 kΩ
  pull-ups in its application circuit, BW = 01 gives 100 Hz at 0.6 mG rms, and
  3.6 V is the absolute maximum. The capture row stands.
- Firing sequence: if a channel's current sense hasn't fallen to zero after the
  high side is switched off, opening the low side stops it; firmware reports
  the channel and doesn't use it again. Added to 03 and the firmware interface.
- Pad telemetry frame, estimated: about 28 bytes packed with sequence, time and
  CRC, inside the 64-byte 1 Hz packet the radio chapter budgets. The
  ground-test flag is held in RAM and never stored with the configuration.
- Open row added: nothing protects J6601's six pyro lines or the J6602 servo
  lines against ESD or induced transients on their harnesses; decide at capture
  between a TVS per pyro line and a written check of the part ratings.
- The continuity divider is ÷5.86, not ÷5.42: R6714 / R6724 / R6734 (100 kΩ,
  on the ADC side of U6901) sit across the 10 kΩ foot while the switch is on.
  The rail dividers have no such resistor and stay ÷5.42. Fixed in 03 and the
  firmware interface, with a sampling-time note for the unfiltered ~8 kΩ
  continuity inputs.
- Both pin maps checked against ST's CubeMX pin data (as packaged in embassy's
  stm32-data): every pad number on the LQFP64 and LQFP100, and every
  alternate-function row (11 comms, 29 flight), match. The only rows the data
  doesn't list are the AF0 debug pins (PA13, PA14, PB3), which are standard.
- PA2 measures `RECOVERY_ARMED_VBAT` only; the staging armed rail has no ADC,
  just its arm sense. The firmware interface now says so.
- Hold RC, recounted: PE5's own 100 kΩ pull-down (capture spec, flight pad
  changes) also drains the 470 µF once the pin lets go. With it, −20%
  capacitance and 15 µA of leakage: ≈1.1 s at Churro's `AV_SHDN_N` (was quoted
  as ≈1.2 s) and ≈1.5 s at Croí's; ≈0.9 s at −30% and 30 µA. Still well over the
  ≈600 ms it must cover. D-2Nov.4 and the capture row now give these figures and
  note that a 1 MΩ pull-down would win back ≈0.15 s.
