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
