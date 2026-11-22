# Ogma 2 Kármán-line mission hardening report

Date: 2026-09-05

Status: design study before schematic capture; the workhorse role, provisional platform envelope, bounded Kármán mission, avionics-bay service boundary, and connector lifecycle are accepted, while exact connector parts and remaining proposals are not yet Ogma 2 architecture decisions

Scope: a reusable workhorse flight computer for ordinary HiPR competition launches, with one suborbital flight to at least 100 km and recovery as its short-duration extreme case

Authority: [`current-system.md`](../../current-system.md) is the current architecture; only report items explicitly accepted there are architecture decisions

Review update, 5 September: the [reliability design review](reliability-design-review.md)
and [execution plan](reliability-execution-plan.md) deepen this study and own the
new review work queue. Source corrections below cover H573 SRAM geometry and
ECC test coverage. Reset/retention, logger/watchdog interaction, and gate
sequencing need explicit closure. References to independent recovery describe
the study's proposed safety architecture, not a blanket per-mission decision
already accepted by the team. Foinse remains MCU-less in every candidate.

Acceptance update, 6 September: the [EX-01 flight fault contract](../../interfaces/flight-fault-contract.md)
now records accepted fault responses, phase-aware watchdog feeding, post-reset
staging inhibit and G0–G3. Independent recovery is required for initial flights
with live Ogma recovery authority and the Kármán mission; later ordinary-flight
policy needs explicit vehicle review. That bounded decision supersedes the
earlier open/proposed status for those policies, not the whole study. Exact
coverage, timing, components, circuits and all test evidence remain open.

EX-02 update, 6 September: the [power contract](../../interfaces/power-contract.md)
records accepted source independence, protected branches, USB service and
bounded hold-up/energy defaults. Seán explicitly retained the switching
preregulator followed by low-noise LDO, citing the earlier external review.
Exact regulator, intermediate voltage, VIOC use and measurements remain open.

EX-03 update, 6 September: accepted reset-class, checkpoint, local-time,
new-flight preparation and action-evidence defaults are in the
[reset contract](../../interfaces/reset-recovery-contract.md). The initial host
model tests selected semantics; it does not establish MCU retention, physical
power/reset behaviour, clock survival or qualification.

EX-04 update, 6 September: the [initial MCU allocation](mcu-resource-and-timing-results.md)
records accepted H563VIT6-first selection strategy, critical-memory placement,
30% initial reserve and reversible development provisioning. This supersedes
the study's H573-leading ranking: H573 remains the direct comparator, not a
presumed reliability upgrade. Complete resource fit and target proof remain
open. EX-05 is the next review.

## The result in one page

Ogma 2 is HiPR's workhorse flight computer for ordinary solid, hybrid, liquid, single-stage, and multistage competition and development launches. Its extreme design case is one bounded sortie: power up, wait on the pad, launch, survive ascent, reach the Kármán line near apogee, descend, deploy recovery, land, and preserve enough local data to prove what happened. It does not need to operate unattended in orbit for six months, survive years of accumulated radiation, recover from an arbitrary sequence of faults, or be reusable without inspection.

That boundary removes a great deal of false complexity. It does not permit an ordinary hobby flight computer with the word “space” attached to it.

The changes with the highest value are:

1. Use the accepted provisional platform envelope to select architecture and part classes now. Replace it with vehicle simulation and measured environments before final qualification; do not block schematic work waiting for a mature rocket.
2. Select a flight MCU with actual flash and SRAM ECC, an MPU, independent watchdog support, clock and voltage monitoring, adequate timers, and a package that can be inspected. EX-04 now starts with STM32H563VIT6 and compares H573 directly. Their unprotected SRAM regions, ECC capacity cost and errata must be treated explicitly. Neither is radiation-qualified by this study.
3. Keep the two-MCU split, but put the communications MCU and its radio/GNSS loads on a separately switchable and current-limited power branch. It must be possible for that entire branch to fail short, latch up, reset repeatedly, or flood UART without pulling down the flight computer.
4. Add an independent external supervisor/windowed watchdog. Use internal watchdogs as a second layer. Reset cause, ECC events, rail minima, watchdog state, and the last valid flight state must survive reset well enough to explain it.
5. Use ECC where the MCU supplies it, and design the software around what ECC does not cover. Put flight state, stacks, estimator state, command state, and critical buffers only in ECC SRAM. Initialise ECC memory before use. Scrub by reading and rewriting. Detect and handle uncorrectable errors. Protect critical state with explicit encodings, CRCs, range checks, freshness, and reconstruction. Do not apply triple modular redundancy to the whole computer.
6. Redraw power as fault-containment branches: flight core, communications/RF, sensors/storage, servo, and pyro. Pyro and servo current must return directly to the source domain without sharing a narrow logic return. The Foinse low-power return must not be an unprotected extension of the flight 3.3 V rail.
7. Replace the provisional battery input with a measured front end: keyed locking connector, fuse, reverse-polarity protection, controlled inrush, transient clamp and damping, under/over-voltage behaviour, bulk energy storage, rail monitoring, and tested brownout semantics. Hot-plug ringing must be captured on the real harness.
8. Make energetic outputs safe against one software error or transient: physical arm interruption, boot-safe biasing, high- and low-side isolation where justified, continuity measurement, current measurement, hardware-bounded pulse energy, and one-shot firmware semantics. An independent recovery controller with its own battery and initiator path is more credible vehicle redundancy than a third MCU on Ogma.
9. Stop treating the current barometer and likely u-blox M10 GNSS path as Kármán-line instruments. Ordinary barometers are far outside range near 100 km. The MAX-M10S operational altitude limit is 80 km and its velocity limit is 500 m/s. It can support lower-flight telemetry and recovery, but it cannot prove a 100 km apogee. Apogee state needs high-g and low-noise inertial sensing, bounded propagation through the pressure/GNSS dead region, and external range tracking or a receiver explicitly qualified for the trajectory.
10. Treat the avionics bay as a qualified service boundary. Integrate, test, record, close, and then stop disturbing the flight assembly. Replace connectorised charge assemblies outside the protected electronics volume. Keep routine USB-C service and Foinse charging externally accessible. “Closed” means contamination-controlled, not hermetic: provide a deliberate pressure-equalisation path and a separately characterised barometer port.
11. Keep one PCB. Move from four to six layers only if the placement and return-path study shows four layers forces broken references or mixes RF, clocks, sensor, servo, and pyro currents. Layer count is a layout result, not a space badge.
12. Put proper keyed, shrouded, positive-lock connectors on Ogma for battery, CAN, pyro, and servo from the first revision. Bare-wire terminals belong only on detachable development adapters and are absent from the Kármán flight configuration. Nano-Fit/Micro-Fit are the strongest battery and high-current candidates; Micro-Lock Plus 2.0 is the strongest compact CAN candidate; JST GH is the smaller signal-only comparison; Harwin Gecko is the high-reliability comparison. WAGO MCS MICRO 2712 is the strongest compact lever-terminal adapter candidate, with WAGO 2601 for larger wire. Exact parts still follow measured current, wire, keying, retention, contamination, and vibration evidence.
13. Add interface protection at every external connector: correctly selected TVS parts, current limiting, series impedance where allowed, and explicit return paths. ESD protection is for handling and harness transients. It is not radiation protection. Galvanic isolation is added only across a real power/ground or hazard boundary.
14. Keep video completely outside the flight-computer power and failure tree. A RunCam Split 4 V3 records to microSD and produces analog video; live video still needs a separate transmitter. A GoPro also records to microSD. The choice is packaging, thermal, power, mass, and evidence quality, not “SD versus no SD.” Qualify the exact camera, card, supply, mount, pressure, temperature, vibration, and sudden power-loss behaviour.
15. Build qualification around the real failure mechanisms: rail interruption, hot plug, brownout, bit and state corruption, bus lockup, radio transmission, pyro and servo current, pressure, temperature, vibration, shock, ESD, harness disturbance, reset at every flight phase, and full mission playback. A generic “space rated” component cannot replace these tests.

The governing distinction is time. A system that works for several minutes above the atmosphere and then returns has a different fault budget from a system that must live in orbit for months or years. Seán recorded this point on 28 August while listening to Sir Peter Beck discuss the “valley of death”: reaching orbit, operating there for twelve years, qualifying a single-use engine for minutes, and qualifying a reusable engine for an hour and repeated starts are different propositions. This is Seán's contemporaneous summary, not a verified verbatim Beck quotation. The Ogma requirement is the short proposition.

## Status words

- **Observed:** directly supported by inspected Ogma evidence, a manufacturer document, or a named standard.
- **Required for the stated mission:** follows from the mission boundary or a hazardous failure.
- **Working recommendation:** the best current technical direction, still awaiting schematic, part, packaging, or test evidence.
- **Open:** must be measured, selected, or decided.
- **Out of scope:** belongs to a materially longer or different mission.

## Mission boundary

### Workhorse role

Ogma 2 is the default maintained HiPR flight computer for ordinary competition and development flights. It must support 3–9 km solid, hybrid, and liquid vehicles, including single-stage and multistage configurations, without redesigning the main PCB for each rocket. Vehicle changes should normally be carried by the typed mission profile, harness, Foinse configuration, actuator or charge assemblies, and mission-specific qualification evidence.

“All competition launches” does not make Ogma a generic modular computer. A connector, interface, sensor, or software mode still needs a named function and bounded failure behaviour.

The public 2025 EuRoC rules define 3 km and 9 km categories across solid, hybrid, and liquid propulsion and permit multistage vehicles. The public 2024 Design, Test & Evaluation Guide warns that a vehicle may remain on the rail for several hours. These are useful anchors for the workhorse role and powered-duration budget; annual competition rules still require a mission-specific review. Sources: [2025 EuRoC Competition Rules](https://euroc.pt/wp-content/uploads/2025/03/PTS_EDU_EuRoC_ST_001905_CR_v01-1.pdf) and [2024 EuRoC Design, Test & Evaluation Guide](https://euroc.pt/wp-content/uploads/2024/04/PTS_EDU_EuRoC_ST_000455_DTEG_v05.pdf).

### Required mission statement

Ogma 2 shall support one launch in which the vehicle:

1. is configured and verified on the ground;
2. remains powered for a bounded pre-launch interval;
3. survives launch, powered ascent, staging if present, coast, and apogee at or above 100 km;
4. remains capable of performing its required recovery actions through descent;
5. preserves a local record through landing;
6. supports a bounded post-landing recovery/beacon interval;
7. may be inspected and serviced before any later use.

The mission is complete when the vehicle returns and the required evidence can be recovered. Long-term operation above the atmosphere is not part of the mission.

### Accepted provisional platform envelope

The following values are accepted Rev A engineering budgets. They are deliberately conservative and provisional. They may select architecture and components now; they are not claims about an unsimulated vehicle.

| Dimension | Provisional platform value | Design consequence |
| --- | --- | --- |
| Normal mission set | 3–9 km; solid, hybrid, liquid; single-stage or multistage | Core board and software remain common across normal competition vehicles |
| Extreme mission | One short-duration flight to at least 100 km followed by recovery | Near-vacuum, high-dynamic-range sensing, upset handling, and evidence retention remain in scope |
| Powered operation | 8 hours through bench/pad wait and flight | Energy, regulator heating, logging modes, and radio duty cycle |
| Recovery reserve | A further 4 hours of reduced-duty beacon and log protection | Battery reserve and post-landing load shedding |
| Full-rate flight record | At least 30 minutes | Storage capacity, write rate, incident windows, and extraction time |
| Supported service period | 5 years | Retention, calibration, battery ageing, support, and obsolescence planning |
| Reuse | 25 inspected flight cycles; acceptance test after every flight | Cycle records, connector/service life, inspection, and retirement criteria |
| Powered electronics temperature | −20 to +70 °C | Board-level operational thermal test |
| Component temperature grade | Prefer at least −40 to +85 °C | Part-screening margin; not proof of installed thermal performance |
| Ambient-pressure survival | Sea-level pressure down to approximately 0.01 Pa | Venting, thermal-vacuum function, materials, and pressure-sensitive parts; barometer validity remains separate |
| Acceleration measurement | Separate ±200 g channel | Boost/shock evidence beyond low-g IMU range |
| Board structural design case | 50 g quasi-static | Mounting, connector, component, and PCB mechanical margin |
| Angular-rate measurement | At least ±2000°/s, with saturation detected and handled | Sensor selection and estimator/state-machine degraded behaviour |
| Shock screening | 200 g short-duration target; waveform open | Early board, mount, connector, and harness screen only |
| Vibration | Exploratory sine/random work first; measured vehicle spectrum later | Avoid a fictional PSD while still testing workmanship and resonances |
| Moisture | Closed-bay rain and splash survival | Enclosure, service interface, vent, and contamination design; no exposed-wet-PCB requirement |

Exact trajectory, speed, acceleration history, rotation, powered coast, pressure-time history, temperature-time history, vibration spectrum, shock waveform, RF environment, and recovery duration arrive later from vehicle simulation and instrumented flights. Those values replace the platform assumptions before mission qualification. They do not block initial MCU, regulator, sensor, storage, connector, and schematic work.

No numerical probability of mission success is assigned provisionally. Fault containment, phase-aware recovery, safe energetic outputs, local evidence, and an independent recovery path remain requirements. Quantitative probability targets wait for the vehicle hazard allocation, range rules, and defensible evidence.

### Explicitly out of scope

- orbital insertion;
- six-month or multi-year autonomous operation;
- repeated radiation-belt passages;
- long-term total-ionising-dose or displacement-damage accumulation;
- orbital thermal equilibrium and repeated eclipse cycles;
- long-duration vacuum ageing;
- autonomous on-orbit repair, reconfiguration, or redundant-string management;
- remote flight-software update while airborne;
- indefinite reuse without inspection and acceptance test;
- satellite-grade parts procurement as a goal in itself.

If one of these returns, this report is no longer the right reliability case.

## Time scale selects the architecture

| Time scale | Dominant examples | Appropriate response |
| --- | --- | --- |
| Nanoseconds to microseconds | ESD edge, switching transient, single-event transient, clock glitch | placement, return path, clamp, filtering, synchronisers, pulse rejection |
| Microseconds to milliseconds | SRAM upset, peripheral upset, brief rail dip, bus collision | ECC, CRC, hardware timer bounds, brownout threshold, bus recovery |
| Milliseconds to seconds | watchdog expiry, SEFI, sensor lockup, MCU reset, communications latch-up | independent supervisor, branch power-cycle, state reconstruction, safe output hardware |
| Minutes | boost, coast, near-vacuum apogee, descent | transient thermal design, inertial propagation, energy reserve, local logging |
| Hours | pad wait and post-landing search | battery capacity, cold operation, radio duty cycle, storage budget |
| Months to years | orbital dose, wear, thermal cycling, autonomous degradation | rad-hard parts, redundant strings, shielding analysis, long-life fault management; out of scope |

The time-scale distinction is not language around the requirement. It changes the part class, number of power strings, amount of autonomy, software recovery strategy, qualification campaign, and acceptable failure probability.

## Reliability claim

### What “survive” must mean

The board does not need every peripheral to remain alive. It needs required vehicle functions to remain available or fail into a bounded state.

The proposed minimum claim is:

- no single failure of the communications MCU, LoRa radio, GNSS receiver, USB interface, display, or video payload prevents the flight MCU from sensing, logging, and executing recovery;
- no single corrupt UART or CAN frame directly fires an energetic output;
- no single software variable or ordinary GPIO default state can deliver an unbounded pyro pulse;
- a short or latch-up on a switchable non-critical branch cannot collapse the flight rail;
- a recoverable single-bit error in protected MCU memory is corrected and recorded;
- an uncorrectable memory or control-flow fault is detected and forces a defined, phase-aware response;
- a reset preserves enough evidence and state to resume or enter the safest available recovery policy;
- loss of GNSS or pressure validity above their operating envelopes is an expected mode, not a surprise fault;
- local recording remains the evidence source when telemetry is absent;
- the complete vehicle has an independent recovery path commensurate with the hazard and range rules.

The reliability number remains open. “Cannot fail” cannot be verified. The team needs explicit allowable probabilities for loss of recovery, inadvertent ignition, loss of primary log, and loss of telemetry. Those targets can then be allocated across architecture, parts, software, harnesses, and tests.

### Common-cause failures remain

Two MCUs on one PCB still share:

- battery and input connector;
- enclosure and mounting;
- much of the PCB fabrication and assembly;
- physical temperature, vibration, contamination, and radiation environment;
- potentially a regulator, reference ground, clock source, reset line, or software toolchain;
- design errors and operator configuration.

The communications MCU is a containment boundary, not a backup flight computer. A third MCU on the same board would not solve the most important common causes. A separate recovery controller, battery, harness, and initiator path can.

## Environment at 100 km

### Pressure and thermal behaviour

The 1976 US Standard Atmosphere gives approximately `3.2011 × 10^-4 mbar` pressure and `5.604 × 10^-10 g/cm³` density at 100 km. This is near vacuum for board cooling and venting purposes. Its tabulated gas temperature is about 195 K, but the PCB does not instantly become 195 K. During a short flight, component temperature is governed mainly by starting temperature, internal dissipation, thermal mass, conduction into the assembly, radiation, and the duration of each phase.

Consequences:

- convection disappears as an assumed cooling path near apogee;
- switching regulator, radio, processor, battery, camera, and pyro-driver dissipation need transient thermal models and low-pressure tests;
- the enclosure must vent without creating a pressure load or trapping the barometer behind an uncontrolled pneumatic filter;
- pressure ports need contamination control and a measured time constant;
- adhesives, coatings, tapes, foam, batteries, and capacitors need inspection for low-pressure behaviour;
- coating or potting must not block pressure sensors, connectors, test pads, RF grounds, or rework access;
- the short mission reduces the importance of months-long outgassing and thermal cycling, but it does not remove local heating or trapped-volume problems.

Primary basis: [US Standard Atmosphere 1976](https://ntrs.nasa.gov/api/citations/19910021306/downloads/19910021306.pdf) and its [100 km property table](https://ntrs.nasa.gov/api/citations/20070022273/downloads/20070022273.pdf).

### Acceleration, vibration, shock, and acoustics

No useful qualification level can be copied from the altitude target. The vehicle supplies the mechanical environment.

Required inputs:

- axial and lateral acceleration histories, including staging and recovery opening;
- angular rate and coning estimates;
- random and sine vibration spectra at the avionics mount;
- shock response spectrum for ignition, staging, charge events, deployment, and landing;
- acoustic environment and fairing/airframe coupling;
- board mounting points, fastener preload, enclosure modes, harness mass, and connector support;
- measured data from the closest previous vehicle.

NASA GEVS is useful as a source of methods and test thinking, not a level to claim by default. The actual rocket environment must tailor the campaign. Source: [GSFC-STD-7000](https://standards.nasa.gov/standard/gsfc/gsfc-std-7000).

### Radiation

Radiation effects divide into different mechanisms:

- **Total ionising dose:** cumulative threshold and leakage changes.
- **Displacement damage:** cumulative lattice damage, important for some sensors and optoelectronics.
- **Single-event effects:** prompt events from one particle. These include recoverable data upset, multiple-bit upset, transients, functional interrupts, and potentially destructive latch-up or power-device failure.

TID and displacement damage scale with integrated environment. They are unlikely to drive a minutes-long ascent through 100 km in the way they drive a multi-year spacecraft. That statement is a design direction, not a numerical risk result. A solar-particle event and a device with poor single-event behaviour can still create a prompt fault during a short flight.

The correct calculation is device and trajectory specific:

```text
expected_events = integral(flux(particle, energy, position, time)
                           × device_cross_section(particle, energy)
                           × susceptible_bits_or_devices)

P(at least one event) = 1 - exp(-expected_events)
```

Required work:

1. Export the actual altitude, latitude, longitude, and time profile.
2. Model atmospheric radiation to the highest supported altitude and use a compatible space-environment model above it. NASA NAIRAS currently covers the surface through 90 km; the final 90–100 km interval needs an explicitly compatible source rather than extrapolation by hand.
3. Include nominal galactic-cosmic-ray conditions and a defined solar-particle-event case.
4. Obtain SEE cross-section or radiation test data for the selected MCU, memories, regulators, supervisors, sensors, transceivers, radio, and power switches where available.
5. Sum the mission integral. State the missing data rather than replacing it with a guessed upset rate.
6. Compare the result with the allocated probability of lost recovery, lost data, and lost telemetry.

NASA NEPP makes the relevant distinction: TID and displacement damage are cumulative; SEE are prompt and probabilistic; the mission environment and duration must be defined before part-level risk can be evaluated. Sources: [NASA Radiation Effects 101](https://nepp.nasa.gov/DocUploads/392333B0-7A48-4A04-A3A72B0B1DD73343/Rad_Effects_101_WebEx.pdf), [NASA system-level radiation hardening](https://nepp.nasa.gov/files/27385/2014-561-Ladbury-Pres-Turkey-SysRH-TN14471_v4.pdf), [NASA architecture reliability report](https://ntrs.nasa.gov/citations/20190002742), [NAIRAS 2](https://ccmc.gsfc.nasa.gov/models/NAIRAS~2.0/), and [ESA SPENVIS](https://swe.ssa.esa.int/scd_arv).

### Radiation design consequence

**Working recommendation:** do not begin with a rad-hard MCU. Begin with a COTS MCU whose error-detection features can be exercised, then design the system so a detected fault has a bounded consequence. Escalate to radiation-characterised or rad-hard parts only if the mission integral and device data show that system-level mitigation cannot meet the allocated risk.

This keeps the design aligned with a short sortie. Rad-hard parts such as the Microchip SAMRH71 and VORAGO VA41630 are built for a different reliability and duration class. They bring large packages, unfamiliar tools, unusual supply needs, long procurement paths, and their own qualification burden. Their existence is useful evidence of what long-life space operation requires; it does not make them the default answer here.

Do not count an aluminium enclosure as SEE protection without transport analysis. Shielding can reduce some dose components and can also create secondaries. The mechanical enclosure should be designed for mechanics, thermal conduction, RF, debris, and handling first. Radiation shielding needs its own calculation if later justified.

A launch-day space-weather constraint may buy more reliability than a radically more complex computer for a single short mission. It needs a quantitative no-go threshold tied to the radiation model before becoming an operating rule.

## MCU selection

### Required flight-MCU properties

The part-selection table must score at least:

- ECC coverage for embedded flash and every SRAM bank;
- exact ECC word size, correction/detection capability, error address capture, interrupts, and test injection;
- lockstep or other core-error detection;
- independent watchdog clock and external watchdog compatibility;
- brownout, power-on reset, clock-failure detection, and reset-cause evidence;
- MPU and privilege separation;
- timers that can own servo and bounded pyro timing without software bit-banging;
- ADC channels for rails, continuity, current, battery, and temperature;
- DMA access to the selected ECC memories;
- sufficient UART, SPI, I²C, CAN FD, USB ownership, and interrupt priority resources;
- LQFP or another package that the team and assembler can inspect and rework;
- current consumption and thermal dissipation at the real clock rate;
- active lifecycle, errata quality, toolchain, debugger, and team familiarity;
- radiation data if it exists, with no substitution of automotive safety certification for radiation qualification.

### Candidate comparison

| Candidate | Useful properties | Costs and gaps | Current judgement |
| --- | --- | --- | --- |
| **STM32H573** | Cortex-M33; 250 MHz; 2 MB flash with SEC/DED ECC; 640 KB SRAM with ECC on SRAM2, most of SRAM3, and backup SRAM; MPU; CAN FD; timers; ADC; USB; LQFP options; familiar STM32 path | SRAM1 is not ECC; part is not radiation-qualified; no dual-core lockstep; DMA/memory placement and silicon errata require audit | **Best current flight-MCU candidate.** Proceed to a pin, memory, timer, DMA, power, and errata audit |
| **TMS570LS1227** | Dual Cortex-R4F lockstep; ECC flash and RAM; BIST; error-signalling module; voltage/clock monitoring; MPU; CRC; CAN; LQFP144 option | 22 mm package; separate 1.2 V core rail; older and less familiar ecosystem; 1.25 MB flash and 192 KB RAM; safety features still do not make it radiation-qualified | **Comparison/fallback.** Select only if injected core/control faults show that lockstep is worth the size, rail, and verification cost |
| **NXP S32K3 family** | Single, dual, and lockstep variants; ECC memories; modern automotive safety architecture; CAN-rich | Large family-selection and safety-framework burden; new tools and reference manuals; no inherent radiation qualification | **Possible, not currently simplest.** Review only if H573 or TMS570 resource/safety gaps remain |
| **Microchip SAMRH71 / VORAGO VA41630 / TI TMS570LC4357-SEP** | Radiation-characterised or rad-hard class; ECC/EDAC and, depending on part, latch-up and dose evidence | Large or BGA/CQFP packages, multiple rails, cost, procurement, unfamiliar tools, board area, and long-life feature burden | **Out of scope by default.** Reopen only after a quantified radiation case or mission-duration change |

Primary part sources: [STM32H573 datasheet](https://www.st.com/resource/en/datasheet/stm32h573ii.pdf), [STM32H5 safety manual](https://www.st.com/resource/en/user_manual/um3150-stm32h5-series-safety-manual-stmicroelectronics.pdf), [STM32H5 errata](https://www.st.com/resource/en/errata_sheet/es0565-stm32h562xx563xx573xx-device-errata-stmicroelectronics.pdf), [TMS570LS1227 datasheet](https://www.ti.com/lit/ds/symlink/tms570ls1227.pdf), [NXP S32K3 family](https://www.nxp.com/products/S32K3), [Microchip SAMRH71](https://www.microchip.com/en-us/product/SAMRH71), [VORAGO VA41630](https://www.voragotech.com/products/microcontrollers/arm-cortex-m4-family/va41630), and [TMS570LC4357-SEP](https://www.ti.com/product/TMS570LC4357-SEP).

### STM32H573 memory consequence

The H573 is only a good choice if its unequal memory coverage becomes an enforced software rule.

The part provides:

- flash ECC with single-error correction, double-error detection, and failing-address reporting;
- ECC on SRAM2 when its ECC option is enabled;
- ECC on the first 256 KB of SRAM3 when its ECC option is enabled;
- ECC on backup SRAM when its ECC option is enabled;
- no ECC on SRAM1; with SRAM3 ECC enabled, its upper 64 KiB is reserved for check storage and unavailable to application code.

Source correction, 5 September: [ST AN5342 Rev 8, table 4](https://www.st.com/resource/en/application_note/an5342-error-correction-code-ecc-management-for-internal-memories-protection-on-stm32h7-series-stmicroelectronics.pdf) describes H5 SRAM ECC on 32-bit data words. UM3150 Rev 2 table 22 contains conflicting 64-bit wording, which the earlier report followed. Use the exact-part RAM documentation and verify implementation in EX-04; do not silently generalise across H5 derivatives. H573 main RAM with SRAM2/SRAM3 ECC enabled provides 320 KiB protected and 256 KiB unprotected application space, plus separate backup SRAM. The production fixture must program and read back the relevant ECC option bytes. Firmware must verify the loaded configuration; ECC capability with ECC disabled is not protection.

The linker script must therefore create named memory classes:

```text
FLIGHT_ECC_RAM     estimator, flight state, stacks, scheduler, pyro state,
                   sensor samples used for decisions, persistent reset journal

NONCRITICAL_RAM    radio/USB staging, diagnostic formatting, disposable caches,
                   buffers whose loss cannot alter flight authority

DMA_RAM            only regions proven accessible by the selected DMA engines;
                   split into critical and disposable classes
```

The build must fail when a critical section, task stack, heap, or interrupt stack lands in non-ECC RAM. A map-file review done by eye is insufficient. Generate a post-link check against symbol ranges. Disable dynamic allocation on the flight MCU after initialisation, or remove it entirely.

The exact H573 derivative and package remain open until the pin/timer/DMA/ADC matrix closes. Selecting “STM32H5” without that matrix would repeat the Rev 1 part/footprint class of error.

## Error detection and correction

### The fault classes are different

“Bit flip” is useful shorthand but insufficient for a design.

| Fault | Example consequence | Detection/containment |
| --- | --- | --- |
| Single-bit SRAM upset | one estimator value or pointer changes | SEC/DED ECC, range checks, MPU, state encoding |
| Multiple-bit SRAM upset | ECC word becomes uncorrectable or aliases | double-error indication, reconstruction/reset; general SEC/DED cannot correct it |
| Flash upset/read fault | instruction or constant changes | flash ECC, boot image CRC/hash, control-flow monitor |
| CPU register or execution upset | wrong branch, instruction, address, or arithmetic result | lockstep if fitted; otherwise control-flow, plausibility, deadline, MPU, watchdog |
| Peripheral-register upset | timer, GPIO, DMA, ADC, or clock configuration changes | periodic configuration readback, hardware output bounds, independent measurement |
| Single-event functional interrupt | peripheral or MCU stops operating until reset | timeout, watchdog, local branch reset or power-cycle |
| Single-event latch-up | abnormal current, heating, rail collapse, possible damage | fast current limit, overcurrent detection, switchable branch, independent recovery |
| Power/EMI transient | several registers or interfaces fail together | input protection, rail supervisor, reset, local decoupling, interface protection |
| Software defect | valid but wrong state or output | review, tests, invariants, state-machine restrictions; ECC does nothing |
| Stale or corrupt sensor data | estimator consumes a plausible old sample | sensor CRC where available, sequence, freshness, range/rate/phase checks |

ECC protects memory codewords. It does not protect the CPU core, GPIO pad, timer, power supply, sensor, bus transceiver, clock, algorithm, or connector. Automotive lockstep protects more of CPU execution but still shares power, clocks, peripherals, memories, package, PCB, and software.

The H573 instruction-cache and data-cache logic/RAM also need treatment. ST's safety manual does not present their fault coverage as ordinary SRAM ECC. It calls for configuration readback, application control-flow monitoring, static-data protection where applicable, and fault-exception handling. Cache enablement and configuration therefore belong in the MCU safety audit; flash ECC alone does not prove that every fetched instruction remains protected through the complete path.

### Required ECC bring-up

For the H573 candidate:

1. Hold all energetic enables inactive in hardware.
2. Start on the internal safe clock and establish reset cause.
3. Follow the selected reset-class retention sequence. Initialise fresh or invalidated ECC regions before use; do not blanket-clear the flight record that a warm restart must validate and retain. Establish a known-good execution region before accessing suspect retained memory.
4. Enable and clear ECC status in the order required by the reference and safety manuals.
5. Install correctable and uncorrectable error handlers before general interrupts begin.
6. Run the supported controlled ECC self-test on reserved locations. UM3150 Rev 2 RAM_SM_10 limits its documented H5 mechanism to RAM3; it identifies other protection measures for RAM2/BKPSRAM. Test software integrity separately and do not claim unsupported hardware injection coverage.
7. Initialise stacks and critical structures in protected banks.
8. Verify the application image and immutable configuration.
9. Start sensors and storage in an output-safe state.
10. Start the internal watchdog, then the external windowed watchdog only after the scheduler health path is running.
11. Permit transition from `SAFE` only after rail, arm, configuration, sensor, and output readback pass.

The exact write-before-read and retention sequence must be checked against the selected option-byte and reset configuration. No uninitialised SRAM content may be treated as valid. Cold/maintenance startup and bounded in-flight restart may require different diagnostic work; neither path may destroy the evidence needed by the other. Boot time is a flight requirement and must be measured across the supported supply and temperature envelope. EX-03 and EX-04 close these paths before they are relied on for recovery.

ST provides fixed flash locations containing one- and two-bit error patterns for testing the flash ECC diagnostic. The startup test should verify returned data, error reporting, failing address, and interrupt/NMI path. Use the documented RAM ECC test mechanism or reserved test words for the exact silicon; do not corrupt live flight memory to prove the handler.

### SRAM scrubbing

The STM32H5 safety manual states that a corrected SRAM read is not automatically written back. A single error can remain resident until software rewrites the word. A real scrub is therefore:

```text
read protected word -> ECC corrects returned data -> write corrected value back
```

Requirements:

- scrub every used protected SRAM region on a bounded schedule;
- explicitly read and write; do not assume a DMA copy or cache operation exercises ECC until verified for the exact part and memory path;
- divide the scan into small slices so it cannot break flight-loop deadlines;
- avoid scrubbing memory while a producer or interrupt can mutate it; use region ownership, brief critical sections, or snapshot methods;
- count corrected events by bank and address;
- clear flags promptly in the manufacturer-required order;
- treat repeated correction at one address as a developing hard fault;
- test that the scrub really removes an injected error rather than repeatedly reporting it;
- include rarely read memory. Those regions gain the most from scrubbing.

The scrub period cannot be selected from intuition. It depends on the calculated upset rate, ECC word geometry, use of each region, and acceptable chance of a second error accumulating in the same codeword. A mission lasting minutes will likely permit a modest periodic scan. The calculation and measured CPU cost still belong in the evidence set.

SEC/DED normally corrects one bit and detects two bits within its protected word. It does not guarantee detection of every larger corruption. A particle-induced multiple-cell upset can place more than one bad bit in one word. Memory interleaving and physical bit placement are device properties; do not assume logical neighbouring bits are physically separated without manufacturer evidence.

### Correctable-error policy

A corrected single-bit memory error should not immediately reset the board during flight. Proposed policy:

- correct and continue;
- record bank, address, syndrome/status, flight phase, timestamp, supply minima, and reset history;
- increase a saturating per-bank counter;
- rewrite the corrected word through the verified scrub path;
- raise a degraded-health flag for telemetry;
- enter a defined escalation if events repeat at one address or exceed a mission threshold.

Thresholds remain open until normal electrical-noise and fault-injection testing establish the false-trigger and recovery behaviour.

### Uncorrectable-error policy

An uncorrectable ECC event cannot be handled by “continue and hope.” The response depends on what was corrupted and which flight phase is active.

Minimum handler:

1. Hardware keeps pyro and servo energy bounded while software is compromised.
2. Capture the smallest reliable fault record without using the suspect memory region.
3. Stop new non-critical bus and storage transactions.
4. Select either state reconstruction, immediate controlled reset, or a phase-specific recovery-safe action.
5. Let the independent recovery controller retain ultimate deployment capability if Ogma cannot recover.

Examples:

- On the pad while disarmed: latch `NO-GO`, keep all outputs safe, require power cycle and inspection.
- During boost: reset/reconstruct if the verified boot time and state evidence permit it; do not fire recovery solely because an ECC flag appeared.
- During coast near the expected apogee window: preserve the independent recovery path and use a narrowly specified fail-safe policy based on time and already validated state.
- After deployment: prevent any repeated energetic command and continue logging if possible.

The final table must come from the vehicle hazard analysis. A universal “reset on double error” is too crude because the consequence of a reset changes across the flight.

### Critical state representation

Flight-critical state needs defence beyond hardware ECC:

- encode finite states with values having large Hamming distance rather than sequential integers;
- store the state with its bitwise inverse and a CRC or other independent check;
- require legal monotonic transitions; no arbitrary state assignment;
- maintain a transition sequence number and timestamp;
- reconstruct from immutable configuration, validated sensor history, and the last committed transition after reset;
- duplicate only the small state needed for recovery across two independently checked storage locations;
- reject stale command/state records even when their CRC is valid;
- range-check every enum, index, length, timestamp delta, and physical value before use;
- use an MPU so parser or communications buffers cannot overwrite flight-state memory;
- place stack guards at every interrupt and task stack boundary;
- make arithmetic overflow and NaN handling explicit in the estimator.

Two identical copies plus a comparison only detect disagreement. They do not identify the correct copy. For configuration and short state records, use generation counters, CRCs, commit markers, and a known default/reconstruction path. Three copies and majority voting are justified only for a tiny value whose loss cannot otherwise be reconstructed. General software TMR would triple state, transitions, and verification work while preserving common software faults.

### Peripheral and register protection

Peripheral configuration is outside normal SRAM ECC. The flight firmware should maintain a compact table of safety-relevant register masks and expected values for:

- clock tree and clock security;
- GPIO mode, pull, alternate function, and output enable for pyro/servo pins;
- timer prescalers, periods, channels, one-pulse settings, and break inputs;
- DMA source, destination, length, and enable state;
- ADC reference/channel configuration;
- watchdog configuration;
- MPU regions;
- CAN/UART baud and mode;
- power-switch and sensor-enable GPIOs.

Read back the stable subset on a bounded schedule. Mask volatile/status bits. A mismatch does not mean blindly rewriting a live peripheral: first force the associated output or transaction into its defined safe state, then reinitialise or reset that domain. Verify that register readback returns the actual hardware state rather than a write-only shadow.

### Control-flow and deadline protection

The H573 does not provide lockstep execution. Compensating controls should remain small:

- a static cyclic executive or tightly bounded scheduler on the flight MCU;
- independent deadline counters for acquisition, estimation, logging, and safety evaluation;
- a program-flow signature updated at required checkpoints;
- the external watchdog heartbeat generated only when all required checkpoints complete in order and within time;
- no watchdog feed from an interrupt that can continue while the main loop is dead;
- MPU separation between communications/parser-facing buffers and flight authority;
- compile-time stack sizing plus measured high-water marks;
- no unbounded recursion, heap use, format parsing, or logging paths on the flight core;
- explicit handling for hard fault, memory fault, bus fault, usage fault, NMI, clock failure, and watchdog reset.

Lockstep remains an architectural option if fault injection demonstrates unacceptable undetected control-flow failures. It is not a substitute for the hardware output bounds or external recovery path.

### Configuration integrity

The typed mission profile should use an atomic two-slot format:

```text
magic
schema_version
vehicle/profile identity
monotonic generation
payload length
payload
CRC32C over header and payload
commit marker written last
```

On boot:

- validate both slots;
- choose the newest valid compatible generation;
- reject an unknown schema or vehicle identity;
- expose the selected generation and hash over USB and telemetry;
- compare host write, device readback, and expected flight profile before arming;
- retain a safe immutable default that cannot fire an energetic output;
- never accept an in-flight profile write.

A CRC detects accidental corruption. It does not authenticate the source. Signed firmware and configuration may be added if protection from wrong or unauthorised images becomes a real requirement. They are not radiation mitigations.

### Local log integrity

Fixed soldered storage remains the right baseline. The flight logger should avoid a general-purpose filesystem during flight.

Recommended format:

- pre-erased fixed-size segments;
- segment header with format version, board identity, firmware hash, mission profile hash, generation, and start time;
- fixed or self-delimiting records with type, length, monotonic sequence, timestamp, and CRC32C;
- commit marker or footer written after record content;
- no in-place metadata rewrite required for continued append;
- independent segment CRC/index written after flight when possible;
- scanner that skips an incomplete final record and recovers every earlier valid record;
- a small event/reset journal in internal ECC-protected flash or another independent fixed store;
- full-rate data in external NOR, with capacity and endurance margin based on the accepted mission duration.

CRC provides detection, not correction. That is sufficient when one damaged record can be dropped and the surrounding sequence remains useful. If storage testing shows burst corruption that would destroy required evidence, compare three specific remedies:

1. duplicate only critical event summaries into internal flash;
2. interleave duplicated records in separate NOR regions or devices;
3. add block-level erasure/error correction such as Reed–Solomon across independent pages.

Do not add a large software ECC layer without measured error patterns. It can increase RAM, CPU time, and power-fail states while solving a failure that record CRC and a second event journal already contain.

Required storage tests:

- reset and hard power removal at every byte/page/program phase;
- operation at minimum and maximum voltage and temperature;
- full-log endurance and extraction-time measurement;
- injected single-bit, multi-bit, page, and address faults;
- corrupted header, length, sequence, and commit marker;
- read while radio transmits and while servo/pyro loads switch;
- complete recovery with the ordinary supported USB-C host tool.

### Telemetry and bus error detection

Each application frame on UART and CAN needs its own:

- protocol version;
- message type and bounded length;
- source identity;
- monotonic sequence number;
- source timestamp and freshness limit;
- CRC independent of the link layer;
- range and state checks;
- defined behaviour for loss, replay, duplication, reordering, corruption, and version mismatch.

UART parity is insufficient. CAN's frame CRC protects the transmission, but it does not prove that the source application assembled the right message or that the receiver is using fresh data. LoRa physical-layer coding improves the radio link; it does not remove the need for application sequence, CRC, identity, and age.

Telemetry is one-way mission evidence by default. Recovery authority must not depend on receiving an acknowledgement. Commands from ground need a separately justified, authenticated, state-bounded path; they are not implied by having a radio.

## Reset, boot, and supervision

### External supervisor

**Required for the stated mission.** Add a supervisor independent of the MCU clock and software.

Required properties:

- threshold above the lowest voltage at which the MCU, flash, and outputs can behave correctly;
- controlled reset assertion and release for slow ramps and brownouts;
- windowed watchdog or challenge/response behaviour that detects a stuck-fast as well as stuck-slow heartbeat;
- independent oscillator;
- reset output that cannot be defeated by a normal GPIO state;
- reset-cause/readback indication where practical;
- package and temperature range suitable for the assembly;
- deterministic behaviour if its own supply ramps or chatters.

The heartbeat is an aggregate progress claim for the accepted operating mode. Proposed correction, 5 September: acquisition, estimation, state and deadline checks must progress; a contained logger failure must enter an explicit degraded-recording mode rather than force repeated resets of a healthy flight loop. A required logger fault can still prevent pre-launch readiness. The transition and watchdog rules require EX-01/03/06 acceptance and tests. A free-running timer or a sticky task-alive flag can continue while required work is dead and is inadequate supervision.

### Internal watchdogs

Use the independent MCU watchdog as a second layer, with a different timeout path from the external supervisor. Use a window watchdog only if its clock and failure coverage add something distinct. Measure the watchdog clocks over voltage and temperature; low-accuracy oscillators turn nominal timeout values into ranges.

### Reset evidence

Rev 1 lost the evidence needed to explain its T+14.976 s reset. Ogma 2 should capture, before normal initialisation clears anything:

- MCU reset flags;
- external supervisor reset indication;
- brownout and power-good history;
- ECC and bus-fault status;
- watchdog status;
- last stored flight phase and transition sequence;
- rail minimum/maximum latches if provided;
- overcurrent or branch-trip state;
- firmware and configuration identity;
- boot count and time since arm where recoverable.

Write a compact record using a power-fail-safe method before verbose logging starts. Then clear flags only after their state has been committed. Test every reset source physically.

### Boot and update policy

- No firmware update in flight.
- Program and verify both MCUs before vehicle integration.
- Expose firmware hash, build identity, bootloader version, MCU identity, and silicon revision through the normal host tool.
- Protect the recovery bootloader against accidental overwrite.
- Check the complete application image at boot. Perform background chunk checks only if their timing and flash-access effects are measured.
- Audit the exact silicon errata and record every applied workaround in the build.
- A/B images are optional. Add them only if field update recovery justifies the second slot and boot-selection state. SWD plus a protected small bootloader may be the simpler recovery mechanism.
- Both MCUs require independent reset and debug access. Resetting or programming communications must not glitch flight outputs.

## Power architecture

### Required domain split

The accepted conversion chain is `VBAT -> switching preregulator -> low-noise
3.3 V LDO`. The earlier approximately 3.8 V intermediate voltage remains
provisional. This selects a topology, not a qualified power architecture;
the complete source, branch, startup and protection behaviour still needs proof.

The board should be redrawn as these functional domains:

```text
vehicle battery / Foinse VBAT
    |
    +-- input fuse, reverse protection, inrush control, TVS/damping, UV/OV policy
    |
    +-- FLIGHT CORE
    |     flight MCU, supervisor, required clocks, minimum recovery sensing
    |
    +-- SENSOR / STORAGE branches
    |     individually current-bounded or disconnectable where useful
    |
    +-- COMMS / RF branch
    |     comms MCU, GNSS, LoRa; switchable and current-limited
    |
    +-- SERVO VBAT / regulated actuator branch
    |     direct paired power and return; no logic-rail path
    |
    +-- PYRO VBAT branch
          arm interruption, drivers, current sense; direct paired return
```

The ground/reference scheme stays deliberate and continuous. “Separate domain” does not automatically mean split ground or galvanic isolation. It means faults, current paths, enabling, monitoring, and reset are bounded.

### Input protection

Required input functions:

- keyed connector and polarity that cannot be confused with pyro or servo connectors;
- fuse or other irreversible protection sized around harness fault energy;
- reverse-polarity/ideal-diode function;
- controlled inrush and a defined maximum input capacitance;
- TVS clamp selected from battery maximum, source impedance, transient energy, and downstream absolute maximum;
- damping for harness inductance and low-ESR ceramic input capacitance;
- under-voltage lockout above loss of correct operation;
- over-voltage response;
- local bulk sized from measured pulse load and allowed droop;
- voltage, current, and minimum-voltage evidence;
- test access on both sides of every protection stage.

Analog Devices AN88 demonstrates that a cable inductance and low-ESR ceramic input can ring to damaging voltage during hot plug. The fix is not “add a TVS” by reflex. Capture the real battery, harness, connector, switch, and PCB with a high-bandwidth probe, then tune input capacitance, damping, inrush, and clamp. Source: [AN88, Ceramic Input Capacitors Can Cause Overvoltage Transients](https://www.analog.com/media/en/technical-documentation/application-notes/an88f.pdf).

### Battery

The battery is part of the flight computer's reliability case even when Foinse owns it.

Required evidence for the exact cell and assembled pack:

- chemistry, series/parallel arrangement, capacity, protection circuit, connector, wire, fuse, and manufacturing traceability;
- open-circuit voltage and source impedance across state of charge and temperature;
- delivered capacity for the maximum pad, flight, deployment, and recovery profile with reserve;
- pulse droop during radio transmit, servo stall/movement, and each credible pyro event;
- cold-start and cold-discharge behaviour;
- self-heating and enclosure temperature in low pressure;
- pressure/venting, pouch expansion, restraint, and failure containment;
- storage age, charge-state policy, preflight acceptance, and retirement criteria;
- behaviour of any pack protection/BMS during pulse load, transient, undervoltage, and reconnect.

Do not use a percentage state-of-charge display as the launch criterion unless it is validated against voltage, temperature, age, and load. Use a measured loaded-voltage/internal-resistance acceptance test and a conservative energy budget.

The pack must be restrained without point-loading, abrasion, puncture risk, or blocking intended vent/expansion behaviour. Its leads need independent strain relief. A recovery controller's independent battery must not share the Ogma connector, fuse, protection IC, or return bottleneck.

### Regulator selection

Select each regulator from a written rail budget:

- nominal, minimum, startup, and maximum current;
- radio transmit and GNSS acquisition pulses;
- processor frequency and peripheral state;
- sensor and storage program current;
- input voltage from fresh battery through end-of-life and transient droop;
- efficiency across the mission load profile;
- switch frequency, spectral content, and synchronisation options;
- dropout and headroom;
- startup monotonicity, pre-bias behaviour, soft start, power-good, discharge, and current-limit mode;
- thermal resistance through the actual copper, enclosure, and low-pressure environment;
- control-loop stability for the selected capacitors over voltage and temperature;
- radiation/SEE data if the risk calculation requires it;
- package inspectability, lifecycle, and manufacturer errata.

Accepted starting point and retained comparisons:

- switching preregulator plus low-noise 3.3 V LDO is the baseline; choose the
  intermediate voltage from actual headroom, noise and thermal requirements;
- direct buck or sensor-only post-regulation remains a comparison that would
  require evidence and a recorded decision to replace that baseline;
- fixed preregulation versus a compatible VIOC-controlled pair remains open.

The [external-review note](rev1-external-review-lessons.md) records the chosen
chain's rationale and LT3045/LT3045-1 distinction. Verify startup ordering, loop
stability, dissipation, headroom, measurement noise and fault behaviour. A
manufacturer's low-noise claim does not establish installed Ogma performance.

### Flight versus communications power

**Required:** the communications branch must have:

- a load switch or regulator enable controlled outside the communications MCU;
- current limit low enough to prevent a short/latch-up from pulling down the source, but above measured startup/transmit current;
- discharge so a commanded power-cycle actually removes charge;
- independent reset;
- no back-power through UART, USB, GNSS, RF control, or protection diodes;
- current and power-good observation by the flight MCU or supervisor;
- a tested automatic policy for one restart and then isolation, with no endless rail cycling.

Holding the communications MCU in reset and physically shorting its branch are required bench tests. Flight sensing, logging, state progression, and recovery outputs must continue.

### Sensor and storage branches

Use separate current-limited switches where they contain a credible short or SEFI. Do not give every sensor its own elaborate supply merely for symmetry.

Candidate grouping:

- minimum inertial/recovery sensors on the flight core or one protected always-on branch;
- secondary/high-range sensors on a restartable branch;
- external NOR on a branch whose short cannot stop the MCU, while retaining a minimal internal event journal;
- pressure sensor on a quiet filtered branch if measurements require it.

Every switch creates leakage and voltage drop. Verify sensor back-power through I²C/SPI pins when its rail is off. Series resistors or bus switches may be required. Firmware must put interface pins into a domain-safe state before removing power.

### Foinse boundary

The current architecture says Foinse receives a protected bounded 3.3 V return from Ogma for low-power devices. For the Kármán mission, that return cannot be the flight-core rail exposed through a connector.

Accepted EX-02 direction: retain Ogma's protected bounded auxiliary return.
Foinse's basic source/protection path must work without it or Ogma software.
An auxiliary-branch fault must not move the flight rail outside its allocated
limits. Actual switches, monitoring, discharge and current budgets remain open.

If the Foinse device dependencies cannot meet this cleanly, review local
low-power regulation before freezing the dependent layout. It is an explicit
fallback, not the presently selected topology. Foinse remains MCU-less.

### Pyro and servo power

- Route outgoing power and return as pairs from their source point.
- Do not let servo stall or pyro fire current traverse the flight MCU ground neck, regulator return, ADC reference path, or sensor connector ground.
- Size copper, connector contacts, switches, sense elements, and bulk capacitance from measured cold and hot loads.
- Test the worst credible simultaneous load even if software intends to sequence events.
- Monitor voltage at the driver, not only at battery entry.
- Define whether actuator supply collapse is allowed to reset only that branch or the complete board.
- Prevent a powered servo or igniter harness from back-powering an unpowered Ogma through signal or sense pins.
- Qualify the selected servo electronics, motor, gears, lubricant, position feedback, and mechanism at the actual cold, low-pressure, load, and duty profile. The PCB surviving does not prove the actuator moves.

### Rail supervision and brownout

“MCU did not reset” is not evidence of a valid rail. Instrument:

- battery at the board connector;
- protected input after inrush/reverse protection;
- flight regulator input and output;
- communications branch;
- servo and pyro source at the driver;
- MCU internal supply monitor where available;
- minimum-voltage latches sampled faster than normal telemetry.

Set external reset above the lowest voltage for correct flash, SRAM, clock, peripheral, and output operation, with margin and hysteresis. Test slow ramps, repeated threshold crossing, millisecond dips, microsecond transients, battery bounce, and abrupt disconnect. There must be no half-alive interval where software runs below its valid supply.

Hold-up capacitance should ride through specified source transients. It should not conceal a physically open battery connection long enough to create an ambiguous dying state. Connector and harness integrity must solve disconnection.

### Latch-up containment

For switchable branches, detect sustained overcurrent and remove power. A restart policy may recover a functional interrupt or latch-up, but repeated cycling can overheat a damaged part and inject rail transients. One bounded retry followed by isolation is the default working direction.

The flight core is harder. An automatic flight-core power cut removes the computer responsible for recovery. Use regulator current limiting, external reset, thermal/current evidence, and the independent recovery controller. If radiation data later shows a material destructive-latch-up risk in the selected flight MCU, change the MCU or introduce a genuinely independent power/recovery architecture. Do not pretend a self-controlled load switch is independent.

## Energetic outputs and recovery

### Required fault model

For each pyro channel, analyse at least:

- MCU pin high, low, floating, and damaged;
- pin mode corrupted from input to output;
- timer or DMA configuration corrupted;
- driver MOSFET shorted drain-to-source or gate-to-drain;
- high-side or low-side control stuck active;
- continuity circuit short or excessive test current;
- arm connector partially mated, reversed, contaminated, or bouncing;
- external ESD/EFT event on either igniter lead;
- cable short to battery, chassis/reference, or another pyro channel;
- regulator or ground transient during fire;
- reset immediately before, during, and after command;
- repeated software command after an apparent misfire;
- one channel firing while another is being measured;
- storage or telemetry delay while the fire window is active.

The safe design goal is not that any single fault leaves the whole channel functional. It is that one credible fault cannot create an unintended or unlimited energetic event, and that the vehicle retains an independently justified recovery path.

### Proposed electrical structure

Each channel should have:

- a physical arm interruption in the energetic supply, outside normal MCU authority;
- positive arm-state readback that proves electrical state rather than only switch-handle position;
- a common armed high-side energy gate and a channel-specific low-side or equivalent series switch, so one ordinary semiconductor short does not by itself complete the circuit;
- hardware gate bias that is off through power-up, reset, programming, unpowered-MCU, and broken-wire states;
- current-limited continuity injection many times below the characterised no-fire current across voltage and temperature;
- continuity voltage/current measurement that can distinguish open, plausible igniter, short, and measurement fault;
- fire-current measurement and a latched fired/result indication;
- a hardware pulse limiter outside the main MCU's normal execution path that removes gate drive after the maximum allowed pulse even if software, DMA, or an interrupt stalls; an MCU timer may request the pulse but must not be the only maximum-energy bound;
- transient protection at the connector selected so leakage, capacitance, clamp current, and failure mode cannot fire the initiator;
- direct paired power and return paths sized for the measured initiator and harness;
- an irreversible per-flight software latch after a completed command unless the exact mission hazard analysis permits a second attempt;
- a dummy-load test mode that cannot energise a real initiator connector.

A useful logical model is:

```text
energy delivered = physical arm closed
                   AND valid vehicle/phase permissive
                   AND channel command
                   AND independent bounded hardware pulse window
```

The physical arm boundary and hardware pulse limit must remain effective if the MCU is executing nonsense.

### Recovery versus staging

The third pyro channel for sustainer ignition cannot inherit recovery rules merely because the output circuit looks similar.

Recovery deployment may need a phase-aware fail-safe response after loss of estimation. Sustainer ignition must normally fail closed and requires stronger permissives, such as validated stage separation, attitude/rotation envelope, timing window, vehicle state, and any external range rule. A reset or uncertainty must not turn into “fire because we might be late.”

Keep separate:

- connector keying and labelling;
- firmware state and command type;
- continuity result;
- pulse limits;
- arm/permissive chain;
- host-tool workflow;
- test fixtures and dummy loads;
- event log and post-flight interpretation.

### Independent recovery controller

**Working recommendation:** a Kármán-line vehicle should carry an independent recovery controller/altimeter with:

- its own battery;
- its own sensors and deployment logic;
- its own arm boundary;
- its own initiator or independently wired deployment path;
- no dependence on Ogma power, UART, CAN, firmware, connector, or PCB;
- a physically separate installation sufficient to avoid the dominant common causes.

This is vehicle-level redundancy, not a demand for a third Ogma MCU. Its exact topology depends on the recovery system, range requirements, vehicle size, and whether two initiators can safely actuate the same event. Those are open. The fault tree must include common mechanical failure of the deployment hardware; two computers do not correct a jammed parachute or severed shared harness.

### Bench and flight workflow

- Real initiators remain physically disconnected during firmware and host-tool development.
- Output tests use instrumented dummy loads with known resistance and pulse-energy capture.
- The host tool shows physical arm, electrical arm readback, continuity class, branch voltage, and profile identity separately.
- “Ready” requires fresh evidence. Missing, stale, out-of-range, or unmeasured states cannot collapse into green.
- Software cannot expose a general `output on / wait / output off` editor.
- Arming requires a written two-person workflow if the vehicle hazard assessment calls for it.
- Every connector and channel is keyed and labelled so battery, recovery, and staging cannot be cross-mated.
- The board stores command time, measured current trace/summary, pulse duration, rail minimum, and result.

## Sensors, estimation, and proof of altitude

### Pressure sensing has a ceiling

The current barometer direction cannot measure the complete mission.

- TE MS5607: specified pressure range starts at 10 mbar.
- TE MS5611: specified pressure range starts at 10 mbar.
- Bosch BMP390: full-accuracy pressure range starts at 300 hPa, or 300 mbar.
- Standard-atmosphere pressure near 100 km is about `0.00032011 mbar`.

Even the 10 mbar lower limit is more than 30,000 times the nominal pressure at 100 km. The pressure sensor will reach its floor long before apogee. It remains useful during lower ascent and descent, where it can supply altitude trend, deployment conditions, and landing evidence. It cannot prove 100 km or directly locate high-altitude apogee.

Sources: [TE board-mount pressure selection guide](https://www.te.com/content/dam/te-com/documents/sensors/global/te-sensors-board-mount-pressure-selection-guide.pdf) and [Bosch BMP390 product specification](https://www.bosch-sensortec.com/en/products/environmental-sensors/pressure-sensors/pressure-sensors-bmp390.html).

### The current likely GNSS path also has a ceiling

The u-blox MAX-M10S datasheet gives operational limits of:

- altitude: 80,000 m;
- velocity: 500 m/s;
- dynamic acceleration: 4 g.

All three must be compared with the trajectory. A Kármán-line vehicle may exceed the velocity and acceleration limit well before it reaches the altitude limit. The receiver may still be valuable on the pad, during permitted flight portions, after deceleration, and for recovery. It cannot be specified as the instrument that proves 100 km. Source: [u-blox MAX-M10S datasheet](https://beta-content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf).

The GNSS selection must include the exact manufacturer's simultaneous altitude/velocity/dynamics restrictions and all applicable legal/export restrictions. “High-altitude mode” is not evidence.

### Required sensing roles

| Role | Required characteristic | Notes |
| --- | --- | --- |
| Boost acceleration | range above maximum axial/lateral load with margin, adequate bandwidth, clipping indication | A high-g accelerometer earns its place by range, not redundancy |
| Coast/navigation acceleration | low bias, noise, temperature characterisation, stable timing | May be part of the main IMU; bias becomes dominant during propagation |
| Angular motion | gyro range above worst credible rotation, clipping/status, temperature model | Saturation must be observable |
| Lower-atmosphere altitude/trend | pressure range, low-temperature operation, port time constant, transonic placement error | Not valid near Kármán apogee |
| Absolute time/lower-flight position | GNSS with explicit trajectory envelope and PPS | Loss is expected outside envelope |
| Board health | rail voltage/current, temperatures, reset/ECC/watchdog state | Needed to distinguish environment from logic failure |
| Proof of apogee | external range tracking or a receiver/instrument explicitly valid for full trajectory | Cannot be inferred from an out-of-range barometer |

The high-g and low-noise accelerometers may be two different devices because one device may not provide both range and resolution. This is complementary measurement, not duplicated identical sensing.

### Estimation through the dead region

Above the pressure sensor range and outside GNSS limits, the flight computer must propagate inertial state. Accelerometer bias produces velocity error approximately proportional to time and position error approximately proportional to time squared. The short coast interval makes this tractable, but only after the actual sensor bias, temperature drift, alignment, vibration rectification, saturation recovery, and integration timing are measured.

The estimator should:

- use pressure and GNSS only while their data are fresh and inside specified operating envelopes;
- latch and report the reason each source became invalid;
- switch to inertial propagation without a discontinuous state jump;
- carry uncertainty that grows through the unobserved interval;
- use burnout and known vehicle dynamics as phase constraints without forcing the expected result;
- detect accelerometer and gyro saturation;
- avoid interpreting transonic pressure disturbance as vertical acceleration or apogee;
- reacquire pressure/GNSS on descent only after validity and innovation checks pass;
- never require communications MCU progress for recovery state.

The flight-state machine needs a bounded apogee/recovery window built from validated burnout time, inertial vertical velocity, elapsed time, attitude/rotation state, and the independent recovery architecture. The exact logic is a safety decision and requires trajectory simulation plus HIL injection. This report does not invent a deployment algorithm.

### External proof

If the mission claim is “reached at least 100 km,” proof should not rest on the same computer being qualified. Plan an independent measurement path:

- range radar or optical tracking where available;
- a trajectory-qualified GNSS/range receiver;
- calibrated ground tracking with documented uncertainty;
- post-flight inertial reconstruction with uncertainty as supporting evidence, not the only absolute reference.

Record raw high-rate IMU, pressure, GNSS status/raw measurements where licensed and available, PPS, flight state, and calibration data. Preserve calibration and coordinate-frame definitions with the log.

## Interfaces, grounding, ESD, and EMC

### Grounding is a system decision

The rocket structure, battery return, propulsion controller, Foinse, antennas, cable shields, pyrotechnic returns, and ground-support equipment form one electrical system. Decide before layout:

- whether the airframe is conductive, carbon composite, metal, or mixed;
- where battery negative bonds to structure, if anywhere;
- where cable shields terminate;
- the maximum DC and transient offset between Ogma and every external peer;
- how USB-connected ground equipment changes the reference on the pad;
- how ignition, servo, radio, and pyro currents return;
- which paths remain connected when armed, disconnected, or attached to GSE.

Use a continuous reference plane on the PCB. Do not cut “analog” and “digital” ground islands under signal paths. Control noise by placement, current-loop geometry, filtering, differential interfaces, and deliberate connection points. NASA's grounding handbook is useful method guidance: [NASA-HDBK-4001A](https://standards.nasa.gov/system/files/tmp/NASA-HDBK-4001A_Final_07152025_0.pdf).

### ESD is not radiation

ESD is most likely during manufacture, handling, harness mating, USB service, and access to exposed vehicle parts. It couples through connectors and enclosure openings. Cosmic-particle upsets occur inside semiconductor volume and are not solved by a connector TVS.

For every external pin:

1. identify normal voltage/current and signal bandwidth;
2. identify possible shorts to battery, ground, neighbouring pins, and structure;
3. select a clamp whose working voltage exceeds normal operation;
4. verify its clamp voltage at the relevant pulse current is below the protected device limit;
5. verify capacitance, leakage, dynamic resistance, pulse rating, and failure mode;
6. place it at the connector before the trace branches or approaches the protected IC;
7. give discharge current a short, wide path to the intended return/chassis point;
8. add series impedance or common-mode filtering only where signal integrity and DC error permit;
9. test the assembled board and harness. A diode datasheet rating is not system immunity.

TI's CAN material shows the relevant design sequence and system-level IEC methods: [CAN bus ESD protection](https://www.ti.com/lit/an/slvafc1/slvafc1.pdf), [isolated CAN protection](https://www.ti.com/lit/pdf/slla419), and [TIDA-00629](https://www.ti.com/tool/TIDA-00629). ST's [ESD protection FAQ](https://www.st.com/resource/en/technical_note/dm00670774-faq-esd-protection-stmicroelectronics.pdf) is useful for clamp placement and selection questions.

### CAN

For the current two-node Ogma/propulsion link:

- use one linear twisted pair with fixed termination at the two physical ends;
- include a defined reference conductor or shield scheme based on the ground-offset analysis;
- select a fault-protected CAN FD transceiver with standby behaviour, bus-fault range, dominant-timeout, and temperature range matched to the vehicle;
- place CAN TVS protection at the connector;
- consider split termination and common-mode choke only after emissions/immunity and signal-integrity testing;
- keep stubs short and measure the real harness;
- make bus-off recovery bounded and observable;
- prevent propulsion traffic from consuming unbounded flight CPU time;
- keep application CRC, identity, sequence, freshness, and state validation above CAN's link CRC.

Fixed termination is preferable to a field jumper when the topology is fixed. A jumper can silently turn the same harness into three configurations.

### When CAN isolation is justified

Galvanic isolation is justified if the propulsion controller:

- uses a genuinely separate battery/return whose offset can exceed the transceiver common-mode range;
- sits across a hazardous-energy or ground-fault boundary that must remain separated;
- has a cable/environment whose conducted transient cannot be contained by a non-isolated interface;
- is required to remain functional through a defined fault on the other side.

If isolated, the design also needs:

- an isolated DC/DC supply or independently available isolated-side power;
- creepage/clearance appropriate to the actual voltage and contamination, not the word “isolation”;
- common-mode transient immunity;
- defined startup and unpowered-side bus state;
- shield/reference strategy;
- propagation-delay and CAN-FD timing analysis;
- fault tests for isolation-supply collapse and capacitive transient coupling.

If both boards deliberately share battery and reference and the measured ground offset stays inside a robust transceiver range, non-isolated CAN is simpler and can be more reliable. Isolation is not a general noise filter.

### Internal UART

The two MCUs are centimetres apart on one PCB. Galvanic isolation is not justified.

Required details:

- point-to-point traces over a continuous reference;
- source series resistors sized after edge-rate measurement;
- explicit idle/default levels;
- application framing, CRC, sequence, freshness, and flow bounds;
- separate reset and power branches;
- pins selected or buffered so one unpowered MCU cannot be back-powered by the other;
- stuck-high, stuck-low, shorted, flooded, corrupt, and version-mismatch tests;
- no blocking request/response on the flight MCU.

### USB-C

USB-C is service-only. No USB cable is part of flight configuration.

- define the board as the correct source/sink/data role; do not leave USB-C policy implicit;
- protect D+/D− and CC pins with low-capacitance ESD parts at the connector;
- use a connector with through-hole shell stakes or equivalent mechanical retention;
- keep shell/chassis/reference connection deliberate;
- protect against an attached, unpowered, or incorrectly powered host;
- make USB ownership between MCUs explicit;
- test plug/unplug, ESD, wrong cable, suspended host, enumeration failure, and host ground offset;
- energetic outputs remain hardware-safe during enumeration, firmware recovery, and debugger access.

### Sensor buses and external discrete inputs

- Keep flight sensors local to the board where practical.
- Add sensor-provided CRC to SPI/I²C transactions when supported.
- Use bounded bus timeouts. Recover a stuck I²C bus with clocking/reset/power-cycle that cannot stall the flight loop.
- Put series resistors near the source on fast local clocks if edge measurement supports them.
- Clamp every harness-borne discrete at the connector, then add input filtering and Schmitt hysteresis appropriate to its timing.
- Synchronise asynchronous inputs before state logic.
- Read physical arm and continuity through independent channels where a single ADC/reference failure would create a dangerous false result.

### EMC test boundary

No generic compliance label has been selected. The useful programme is self-compatibility plus tailored immunity:

- emissions with MCU clocks, storage writes, GNSS, and maximum LoRa transmit duty;
- sensor noise with radio transmit, servo movement/stall, and dummy pyro pulses;
- conducted transient injection on battery, CAN, arm, servo, pyro, and external discrete harnesses;
- IEC 61000-4-2-style contact and air discharge at accessible connector shells, panels, and enclosure points, with levels selected by the handling environment;
- cable bulk/current or equivalent RF immunity where the vehicle/transmitter environment justifies it;
- reset, false-fire, corrupted-log, and degraded-sensor criteria monitored during every test.

Passing means the required function and evidence survive, not merely that the board does not suffer visible damage.

## Connectors and harnesses

### Selection rules

Every connector needs a one-line ownership statement and an exact fault/qualification record. Select from:

- maximum continuous and pulse current at the actual contact count, wire gauge, temperature, housing, and PCB copper;
- contact resistance and allowed rail drop;
- keyed polarisation and prevention of cross-mating with every nearby interface;
- positive latch and secondary contact retention/TPA;
- touch safety and whether a live source can expose pins;
- conductor type, insulation diameter, crimp tooling, pull strength, and bend radius;
- vibration and shock with the actual harness mass and strain relief;
- mating cycle and field replacement needs;
- connector height and access inside the 3-inch vehicle;
- visual/tactile confirmation while gloved;
- contamination and cleaning;
- availability of genuine contacts, housings, headers, tools, and inspection gauges.

### Candidate allocation

| Interface | Working candidate | Reason and limit |
| --- | --- | --- |
| Battery input | Molex Nano-Fit or Micro-Fit 3.0 | Both provide proper polarisation and positive locking with assurance/keying options. Select exact series, contact, wire, circuit count, and derating from the real current and temperature test |
| Pyro board-to-bay harness | individually keyed Nano-Fit or Micro-Fit 3.0; Micro-Lock Plus 2.0 only if wire and pulse tests support it | Proper connector from Ogma Rev A. Each channel needs distinct physical/visual identity, complete-path resistance, real pulse testing, and no cross-mating with battery or servo |
| Kármán charge assembly | open: current-qualified keyed two-pin connector on a pre-terminated replaceable charge module | No bare-wire terminal in flight. The raw e-match termination is made and inspected away from the vehicle; the complete module then survives short, miswire, partial-mate, pull, contamination, pulse-current, and vibration tests |
| Servo power/signal | Micro-Lock Plus 2.0 where measured stall current permits; Nano-Fit or Micro-Fit if power requires it | Proper locking board and harness connection from Rev A. Standard friction-fit RC plugs may appear only beyond a retained adapter or be replaced on the flight assembly |
| Physical arm/RBF | panel- or harness-borne positive-retention connector/switch, with separate electrical readback | Must not lever the PCB or be confused with power/pyro; exact family open |
| Ogma/Foinse power | Nano-Fit, Micro-Fit 3.0, or larger locking crimp if the current/temperature result requires it | Keep boards visible and independently removable; no exposed pin-header stack |
| CAN/low-current vehicle signals | Micro-Lock Plus 2.0 primary compact candidate; JST GH smallest comparison; Harwin Gecko high-reliability comparison | All are locking families. JST GH's AWG 26 limit is restrictive; Gecko adds cost/tooling. Qualify the exact twisted-pair harness and board retention |
| Temporary raw-wire servo/pyro adapter | WAGO MCS MICRO 2712 primary compact candidate; WAGO 2601 for larger conductors | Detachable breakout or harness only. Tool-free access for development/pop tests; visibly excluded from the Kármán manifest. Neither family is accepted for pyro pulse or rocket vibration without installed tests |
| USB-C | mechanically staked receptacle | Service-only; shell retention and ESD required |
| RF | threaded/bulkhead SMA-class interface or internally mated micro-coax with independent strain relief | Do not use an exposed U.FL as a repeated field connector |
| Debug | Tag-Connect footprint or very low-mass keyed connector | Reopen the current permanent 2×3 header choice; both MCUs still need independent SWD/reset access |

The shortlist is grounded in current manufacturer information:

- Molex [Nano-Fit](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/nano-fit-connectors) is a 2.50 mm family for 26–20 AWG wire with positive locking, isolated contacts, TPA/CPA options, and mechanical/colour keying. Molex states up to 8 A at family level. That is not the installed Ogma rating.
- Molex [Micro-Fit 3.0](https://www.content.molex.com/dxdam/literature/987650-5984.pdf) is a 3.00 mm family with positive latching, polarised housings, isolated contacts, and TPA/secondary-lock options. Molex states an 8.5 A family maximum and documents higher-current terminal variants. Exact contact, wire, loaded circuits, copper, pulse, and temperature control the usable value.
- Molex [Micro-Lock Plus 2.0](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/micro-lock-plus-connectors) provides a positive latch, board-retention solder tabs, 22–26 AWG support, and a stated maximum of 4.7 A depending on configuration. It is the strongest compact CAN/servo candidate, not an automatic power-connector selection.
- [JST GH](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf) is a 1.25 mm secure-lock family rated 1 A with AWG 30–26 wire. It is a small signal connector, not a battery or untested pyro connector.
- [Harwin Gecko](https://www.harwin.com/hri-range/gecko) is a 1.25 mm high-reliability family with latching/screw-lock options, 2 A per contact with all contacts loaded, published shock/vibration testing, and ready-made cable assemblies. It is the Kármán high-reliability comparison; cost, tooling, size, and assembly burden still count.
- WAGO [MCS MICRO 2712](https://www.wago.com/us/pluggable-pcb-connectors/mcs-micro-2712) is a pluggable lever connector at 2.54 mm pitch for 28–20 AWG, with optional locking, gold contacts, and inverse coding. WAGO positions it for low-current/low-voltage work. It is the strongest compact temporary-adapter candidate, not qualified flight pyro hardware.
- WAGO [2601](https://www.wago.com/global/products/electrical-interconnections/discover-pcb-connection/pcb-terminal-blocks-with-levers-2601-series) is a fixed 3.5 mm-pitch lever PCB terminal for 26–16 AWG. It accepts larger conductors but stays on a detachable breakout board.

Manufacturer ratings describe product families and prescribed tests. They do not establish Ogma current capacity, vibration survival, contact resistance after handling, or suitability beside energetic circuits.

### Harness workmanship

- Use the manufacturer crimp tool or a validated production equivalent.
- Record wire part, gauge, strip length, contact, housing, cavity, tool, die, and operator/assembler.
- Inspect crimp geometry and conductor/insulation support.
- Pull-test samples from each build lot to a written acceptance value.
- Apply strain relief to the harness, not to solder joints or connector latches.
- Support heavy harnesses close to the board.
- Label both ends and enforce cavity-level continuity checks.
- Hi-pot is unnecessary at these low voltages unless another vehicle subsystem introduces a real requirement; continuity, isolation resistance, four-wire resistance, and current-pulse tests are more useful.
- Qualify connectors after vibration, then disturb and re-mate them as the field workflow actually does.

The connector current printed on a family webpage is not the installed rating. Contact count, ambient temperature, adjacent loaded contacts, wire, copper, and pulse duration all matter.

## Avionics-bay service and contamination boundary

### Closed means controlled, not hermetic

The useful boundary is a flight assembly that can be integrated, tested, closed, and left undisturbed. It keeps black-powder soot, loose conductive debris, repeated charge-assembly replacement, temporary raw-wire adapters, and routine operator handling away from Ogma, Foinse, batteries, and their internal harnesses.

It is not automatically a pressure seal. A sea-level cavity carried toward 100 km approaches a one-atmosphere differential unless it vents or is deliberately designed as a pressure vessel. The baseline is a controlled pressure-equalisation path sized from the ascent/descent pressure rate and bay volume. It must be protected from direct energetic residue. The barometer needs its own characterised port geometry; neither a dirty e-match opening nor an arbitrary enclosure leak is an acceptable pressure reference.

### Interface hierarchy

Treat the energetic connection as four inspectable elements:

1. proper locking Ogma board connector and channel protection;
2. retained internal harness with known wire, cavities, length, resistance, and strain relief;
3. mechanically supported bay-wall or retained external harness connector whose loads do not reach the PCB;
4. externally replaceable, pre-terminated, connectorised charge assembly containing the e-match.

Continuity and fire-current evidence must include all four. Each channel needs visible identity at both ends, protection against cross-mating and partial insertion, an inspectable conductor termination, and a safe unmated state. The exterior must not expose a live source pin or a geometry that a dropped tool can bridge. The physical arm break must interrupt energetic power before e-matches are connected, removed, or resistance-tested by the field procedure.

No exact external connector has been selected. A WAGO or screw terminal mentioned during the Multistage discussion was an example of removability, not Kármán flight architecture. Screw terminals remain rejected. WAGO lever or push-button terminals may appear only on a detachable development/pop-test adapter. An internal PCB connector, protected bay-wall or inline flight connector, connectorised charge module, and temporary ground-test adapter do not need to be the same product family.

The two configurations must be visibly different:

```text
development: Ogma locking connector -> detachable adapter -> WAGO terminal -> bare servo/e-match lead
Kármán:      Ogma locking connector -> qualified harness -> keyed connectorised servo/charge assembly
```

The Kármán manifest rejects the temporary adapter. If the chosen e-match is supplied with bare leads, the one-time termination into the charge assembly is completed away from the vehicle under a controlled workmanship and inspection process. It is not a launch-pad wiring operation.

### Routine service and maintenance access

The following operations must be possible with the qualified electronics volume closed and without moving a board or internal harness:

- connect and replace each connectorised charge assembly;
- confirm identity and configuration, upload an allowed profile, read it back, and extract logs over USB-C;
- use the defined Foinse charging interface;
- inspect physical arm state and the accessible connector map.

Raw SWD, invasive probing, rework, battery or internal-harness replacement, and board removal are maintenance operations. They remain possible through a retained removable panel or disassembly path, but they invalidate flight-ready closure and force the affected inspection and tests to be repeated. Do not default to an unterminated USB extension loose inside the bay. Any panel-mounted USB path must be electrically and mechanically qualified as part of the real cable assembly.

The removable panel and its opening need retention, repeated-cycle, vibration, pressure, contamination, RF, cable-clearance, and tool-access review. If the panel or cut-out carries primary load, structures must substantiate it. Electronics owns the functional layout, interface definition, service procedure, and acceptance evidence; structures owns or accepts the load-bearing airframe consequences.

### Closure record

The flight-ready record must identify:

- bay and vehicle identity;
- Ogma, Foinse, recovery-controller, battery, harness, and camera serials or controlled identities;
- firmware, configuration, calibration, and host-tool versions and hashes;
- connector cavity/channel map and installed harness revision;
- internal inspection and cleanliness result;
- rail, continuity, isolation, and path-resistance results;
- external service-interface condition and protective covers;
- closure fastener state and witness marks;
- assembler and independent reviewer;
- every change after closure and the tests repeated because of it.

A witness mark detects disturbance. It does not prove correct assembly.

## PCB, mechanical, and manufacture

### One board remains the right baseline

The Kármán mission does not justify returning to a hidden PCB stack. One board removes inter-board headers, inaccessible components, extra regulators, and repeated programming targets. It also concentrates faults, so the domains on that board must be physically legible and electrically bounded.

### Four versus six layers

**Open, with six layers as a serious working candidate.** Use the placement and current-return study to decide.

Six layers are justified if they enable:

- uninterrupted reference planes under all high-speed and RF paths;
- a clean power-distribution layer without cutting signal returns;
- physical separation of pyro/servo loops from sensors and clocks;
- controlled-impedance USB/CAN/RF routes;
- lower spreading inductance for decoupling and branch transients;
- route completion without hidden necks in ground or high-current copper.

Four layers remain acceptable if the actual layout demonstrates these properties. More layers do not correct poor placement or a broken return path.

### Functional placement

Place in a visible sequence:

1. battery/Foinse entry and input protection;
2. power conversion and branch switches;
3. flight MCU, supervisor, clock, and local decoupling;
4. inertial and pressure sensors away from hot, flexing, magnetic, RF, and high-current regions;
5. fixed storage close to its controller with bounded current loop;
6. communications MCU, GNSS, radio, RF matching, and antenna edge;
7. servo and pyro drivers at their connectors with short paired current paths;
8. USB and debug at accessible edges;
9. test points visible with the board installed where possible.

Do not route:

- RF or fast clocks under inertial/pressure sensors;
- pyro/servo current through sensor or MCU reference copper;
- USB/CAN over plane gaps;
- switch-node copper near pressure, GNSS, crystal, or antenna nodes;
- sensitive traces along connector ESD discharge paths;
- critical vias or small passives beneath heavy unsupported harnesses.

### Components and mounting

- Put heavy components and connectors near board supports.
- Use enough mounting points to control board modes; do not clamp over sensors whose package stress changes bias.
- Keep IMU alignment datums and coordinate frames explicit in PCB and mechanical drawings.
- Prefer inspectable packages for critical parts where performance permits.
- Record polarity, pin 1, connector cavity numbering, and test-point names visibly.
- Use manufacturer-recommended crystal layouts and prove startup across pressure, voltage, and temperature.
- Provide thermal copper and conduction paths for regulators, radio, switches, and current shunts.
- Retain the RF feed and antenna mechanically independent of the tiny board connector.
- Keep every board face inspectable after enclosure opening. No Foinse board may hide it.

### Electrical derating

Derating should follow the actual stress and failure mode, not a single blanket percentage.

- Capacitors: account for DC-bias capacitance loss, temperature, tolerance, ripple current, voltage transients, and ageing. The nominal printed capacitance of an MLCC is not the installed value.
- MOSFETs: check steady and pulsed current, `RDS(on)` at the real gate voltage and temperature, safe operating area, avalanche/inductive energy, body-diode path, and short-circuit duration.
- TVS parts: check working voltage, leakage, dynamic clamp at the selected pulse, repetitive exposure, and what happens when they fail short or open.
- Resistors and shunts: check continuous power, pulse energy, temperature coefficient, Kelvin routing, and overload/fusing behaviour.
- Regulators and switches: check absolute maximum, current limit, dropout, switching-node overshoot, thermal shutdown, and restart mode with margin from qualified worst case.
- Connectors and copper: check temperature rise and voltage drop after vibration and mating-cycle exposure, not only when new.
- Oscillators and sensors: stay inside the manufacturer's voltage, temperature, acceleration, and pressure limits with an explicit margin or qualify the excursion.

Record the worst-case stress ratio in the design review. A part outside its published envelope needs test evidence and a conscious risk acceptance; it cannot be rescued by a generic “space-shot” label.

### Coating, staking, and cleanliness

Selective conformal coating and staking may improve resistance to contamination, fretting, and vibration. They are not automatic.

Sequence:

1. manufacture and clean;
2. inspect, including X-ray where package/hidden-joint risk requires it;
3. bring up and rework;
4. complete electrical, pressure, and environmental development tests;
5. mask connectors, pressure ports, sensors, RF contacts, test pads, arm contacts, and other prohibited areas;
6. apply qualified staking/coating process;
7. inspect cure, coverage, bubbles, wicking, contamination, and clearance;
8. rerun acceptance test.

Coating before the design is stable traps contamination and makes diagnosis harder. NASA workmanship guidance provides process controls, but the Ogma process must be tailored: [NASA-STD-8739.1](https://standards.nasa.gov/node/280), [GSFC-STD-6001A](https://standards.nasa.gov/sites/default/files/standards/GSFC/A/0/gsfc-std-6001a_approved.pdf), and [ECSS-Q-ST-70-12C Rev.1 PCB design rules](https://ecss.nl/standard/ecss-q-st-70-12c-rev-1-design-rules-for-printed-circuit-boards-30-april-2025/).

### Factory PCBA consequence

Factory assembly remains correct. It adds required controls:

- approved manufacturer part numbers and allowed substitutions;
- date/lot traceability for MCU, memory, regulators, sensors, and pyrotechnic switches;
- PCB impedance, stack-up, material, copper, finish, cleanliness, and coupon requirements;
- stencil and assembly notes for thermal pads, void-sensitive parts, and double-sided heavy parts;
- AOI and X-ray requirements;
- board serial number and hardware revision in copper/marking and readable in firmware;
- incoming visual inspection and dimensional check;
- current-limited first power with rail sequencing captured;
- boundary scan/SWD programming, memory self-test, and fixture report saved per serial;
- no component substitution without electrical, mechanical, firmware, and qualification review.

## RF and telemetry

### Mission role

LoRa is useful but non-critical. The mission must complete with no ground packets received. Local fixed storage is the source of truth.

Required radio work:

- accepted frequency, bandwidth, power, duty cycle, licensing, and range coordination;
- transmitter and oscillator operation over pressure, voltage, and temperature;
- complete line-of-sight link budget at maximum slant range, not only vertical altitude;
- free-space loss, connector/cable loss, antenna gain and pattern, polarisation, airframe shadowing, ground antenna, receiver noise/sensitivity, and at least a defined fade/orientation margin;
- Doppler from maximum radial velocity and oscillator error;
- packet airtime and channel occupancy;
- tumble and null behaviour;
- ground-station antenna tracking/diversity;
- coexistence with GNSS and every flight sensor;
- no high-rate retry loop that starves the flight UART or power branch.

At 868 MHz and 100 km, free-space path loss is about 131 dB before antenna, airframe, cable, polarisation, or fade losses. Doppler is about 2.9 kHz per 1 km/s of radial velocity at that frequency. These are orientation numbers only; use the accepted trajectory and frequency for the actual budget.

Application telemetry should favour bounded repeated summaries over acknowledgements and retransmission queues. Critical events can be sent several times with unique sequence and time. A receiver can reconstruct loss from gaps. Ground commands remain out of the baseline unless separately justified.

### Antennas

- Do not bury an antenna behind carbon fibre or an unmodelled metal structure.
- Keep GNSS and LoRa antennas separated and test simultaneous operation.
- Use a threaded/bulkhead connection where the field cable is mated repeatedly.
- If U.FL/I-PEX is used internally, mate it during assembly, strain-relieve the coax, and do not expose it as the service interface.
- Verify connector torque and cable bend radius.
- Vibration-test the complete antenna, cable, bulkhead, and ground-plane arrangement.

## Video payload

### Architecture boundary

Video is a separate evidence payload. It must not share:

- Ogma's flight-core regulator;
- Ogma's flight-core battery path unless a separately fused and proven branch is deliberately allocated upstream;
- flight UART, CAN, USB, or storage;
- a mounting failure that can damage Ogma or its antennas;
- a fault path through trigger, ground, or shielding.

The simplest baseline is its own battery, power switch, camera, storage, transmitter if required, antenna, and mount. Power it before launch and let it run. Ogma does not need to manage it.

If synchronisation is valuable, use a one-way bounded indication: a visible timed LED in frame, an acoustical marker, or a protected one-way trigger whose unpowered and shorted states cannot back-power either system. Do not add a bidirectional protocol merely to align timestamps.

### RunCam Split 4 V3

The RunCam Split 4 V3 manufacturer page specifies:

- 4K/30 recording;
- analog TV output;
- microSD storage up to 128 GB;
- nominal 5–20 V input;
- about 450 mA at 5 V;
- a 29 mm × 29 mm main board and 10.2 g stated weight.

RunCam separately warns that supply quality, loose interconnects, and the card are causes to check when the Split blacks out during flight, and warns against assuming raw battery input is clean merely because it falls inside the voltage headline.

Consequences:

- local 4K recording goes to microSD;
- analog video output is not a ground link;
- live video requires a separate video transmitter, RF power design, antenna, ground receiver, link budget, and legal frequency/power allocation;
- the camera board and its small camera interconnect need independent strain relief;
- its regulator must survive the real battery surge and transmitter load;
- a camera crash or card short must only lose video.

Sources: [RunCam Split 4 V3](https://shop.runcam.com/runcam-split-4-v3/) and [RunCam in-flight blackout guidance](https://support.runcam.com/hc/en-us/articles/115013874488-Split-blacks-out-power-off-during-flight).

### GoPro does not remove microSD

GoPro HERO cameras also require microSD. GoPro's own setup material for HERO13 and manual for HERO10 specify removable microSD and note card-care/retention concerns. A GoPro may give a more integrated enclosure, battery, camera, and recording stack. It may also add mass, frontal area, heat, a consumer battery, closed power-management behaviour, and less convenient live-video output.

The real comparison is:

| Question | RunCam Split | GoPro |
| --- | --- | --- |
| Local storage | microSD | microSD |
| Live video | analog output plus separate VTX | requires a separate supported output/link; consumer wireless is not a 100 km link |
| Power | external protected supply required | internal/removable battery depending model, still needs environmental proof |
| Packaging | exposed board/camera cable needs enclosure and restraint | integrated consumer enclosure, heavier |
| Thermal control | system designer owns it | closed internal behaviour, still must be tested at low pressure |
| Failure containment | easy to make fully independent | easy if left self-contained |

Sources: [GoPro HERO13 setup](https://gopro.com/en/gi/out-of-the-box-experience/hero-13-black) and [GoPro HERO10 manual](https://gopro.com/content/dam/help/hero10-black/manuals/HERO10Black_UM_ENG_REVB.pdf).

### microSD risk

The card does not “likely die” merely because apogee is 100 km. The credible failure paths are:

- camera or card power interruption while metadata is being updated;
- connector/contact movement under vibration;
- temperature outside the camera/card operating envelope;
- camera thermal shutdown in low pressure;
- controller/firmware crash;
- card incompatibility, wear, counterfeit media, or insufficient write rate;
- fractured board, slot, or card retention;
- filesystem damage that hides otherwise intact video segments.

Mitigation is empirical because the camera firmware and filesystem behaviour are closed:

- use genuine manufacturer-supported high-endurance cards from controlled supply;
- qualify the exact card capacity and firmware, not only the product family;
- fill and verify each card before the campaign, then perform the manufacturer's recommended format in the camera;
- record in bounded file segments if the camera supports it, limiting the loss from the final interrupted file;
- physically retain the card without blocking service or distorting the slot;
- test hard power removal repeatedly at random recording times;
- verify file recovery on the actual host tools;
- keep local recording and live downlink independent when both are required;
- if video is important evidence, use two independent cameras rather than coupling one camera into Ogma.

### Video qualification

For the exact camera/card/VTX assembly:

- record at full resolution for the maximum pad plus flight plus recovery duration;
- cold-soak and hot-soak, then start and record;
- run at representative low pressure while monitoring camera, card, battery, and regulator temperature;
- vibrate the powered recording assembly and inspect for dropped frames, reboot, cable movement, focus shift, rolling-shutter artefact, and corrupted files;
- test sudden power loss, brownout, and reconnection;
- transmit at maximum duty while checking Ogma GNSS, LoRa, sensors, and ground links;
- inspect lens/window fogging, contamination, reflection, and pressure loading;
- verify the mount and field of view after vehicle assembly;
- confirm that a hard short at every video connector does not affect Ogma.

## Software architecture consequences

### Flight MCU

Keep the flight software smaller than the current hardware capability tempts it to become.

- one deterministic scheduler/cyclic executive;
- no radio stack, USB host behaviour, dynamic protocol discovery, or general scripting;
- no heap after startup;
- fixed-size queues with explicit drop counters;
- acquisition and output timing owned by hardware timers/DMA only where the memory path is proven;
- all external data treated as untrusted, bounded, versioned input;
- estimator validity and uncertainty explicit;
- flight-state transitions centralised and append-only in the log;
- output drivers accept typed one-shot commands, not arbitrary levels;
- reset, fault, and degraded states designed as normal state-machine paths;
- watchdog health earned from independent progress tokens;
- every cyclic task and interrupt has a deadline, maximum activation rate, measured execution-time distribution, accepted upper bound, and specified overrun response;
- timing is measured on the selected MCU with maximum sensor traffic, storage delay, ECC correction/fault handling, communication flood, bus timeouts, and simultaneous output activity;
- compiler, linker, optimisation, startup, and device pack versions pinned in the build record.

### Communications MCU

The communications side may carry more third-party code, but its resource use and failure rate are contained.

- bounded flight-to-comms queue; flight drops telemetry instead of waiting;
- no comms-to-flight message can directly command pyro or servo action;
- parse into a disposable non-authoritative representation before proposing configuration/service operations;
- USB and radio queues have fixed maxima;
- GNSS loss, malformed packets, RF timeout, and host disconnect are ordinary modes;
- watchdog reset and branch power-cycle are safe;
- firmware identity and protocol compatibility are visible to the flight MCU and host;
- no shared mutable memory between the MCUs.

### State-aware reset recovery

For every reset point in every phase, specify:

| Phase | Evidence available after reset | Allowed reconstruction | Output policy |
| --- | --- | --- | --- |
| Disarmed/pad | profile, arm readback, sensor state, last log | return to `SAFE/NO-GO` | all energetic outputs inhibited |
| Armed/pre-launch | profile, arm, elapsed time, launch evidence | require revalidation; no assumption of launch | remain inhibited unless launch becomes independently valid |
| Boost | recent committed phase/time, high-g evidence, sensor state | resume only through a bounded boost/coast recovery path | no staging/recovery solely on boot |
| Coast/apogee window | committed burnout/coast evidence, elapsed-time source, sensor validity | phase-specific reconstruction with uncertainty | preserve narrow recovery safety path; staging fails closed |
| Descent/deployed | fired latches, current evidence, descent sensors | restore deployed state and logging | no repeated fire unless explicitly justified |
| Landed | landing evidence, elapsed time | beacon/log mode | energetic outputs permanently inhibited |

The elapsed-time source itself must survive or be reconstructable. GNSS time cannot be the only source during the invalid region. A reset test must cover loss or corruption of each evidence item.

### Development controls

Proportionate controls for this mission:

- generated register/pin/peripheral ownership table from the schematic source where possible;
- compiler warnings as errors for the flight target;
- static analysis and a small adopted C/C++ safety subset;
- unit tests for framing, CRC, configuration selection, state encoding, numerical bounds, and log recovery;
- fuzzing of UART/CAN/USB/configuration parsers;
- host-compiled simulation of state machine and estimator against recorded and generated trajectories;
- hardware-in-the-loop with real timers, reset, storage, sensors, and dummy output loads;
- target-hardware deadline tests with high-water marks and forced worst-case interrupt, DMA, storage, parser, timeout, and ECC paths;
- reproducible build with firmware hash and source revision;
- reviewed disassembly/map evidence for startup, vector table, critical memory placement, and watchdog path;
- no test-only bypass compiled into the flight image unless it is physically and cryptographically impossible to invoke in flight, with simpler removal preferred.

This is not a claim of DO-178C, IEC 61508, ISO 26262, or another certification. Borrow useful methods without pretending the project has completed their assurance process.

FreeRTOS remains outside the baseline. Add it only if measured concurrency or timing evidence shows that the cyclic executive cannot meet a named requirement and the RTOS path makes that requirement easier to verify.

## Verification and qualification

### Requirements before tests

Every test needs:

- requirement ID;
- exact article serial/revision and firmware/configuration hash;
- setup and calibrated instrumentation;
- input level/profile and uncertainty;
- pass/fail criteria tied to required function;
- raw data location;
- anomalies and disposition;
- whether the test is development, qualification, or acceptance evidence.

“It booted afterward” is insufficient where a test could corrupt state, fire an output, lose data, or silently degrade a sensor.

### Development sequence

#### 1. Mission and hazard closure

- accepted trajectory and all durations;
- acceleration, rotation, vibration, shock, pressure, thermal, and RF envelopes;
- recovery and staging hazard analysis;
- required probability allocations;
- independent altitude-proof method;
- range and regulatory constraints;
- accepted independent recovery architecture.

#### 2. Part and resource closure

- exact MCU/package and memory map;
- ECC/errata test on development hardware;
- pin, timer, ADC, DMA, interrupt, bus, and debug matrix;
- exact sensors and their valid envelopes;
- regulator and branch-switch shortlist;
- exact storage and radio;
- connector/harness shortlist using actual wire and contacts.

#### 3. Circuit coupons and power mule

Before committing the whole board, build or fixture the dangerous unknowns:

- battery hot-plug/inrush/transient front end with real harness;
- regulator chain and communications branch short/latch-up emulation;
- pyro driver, arm/readback, continuity, one-shot, current sensing, and dummy loads;
- servo load and return-path behaviour;
- CAN protection/termination with propulsion harness;
- connector retention/pull/vibration samples;
- proper pyro connector, connectorised charge-module, detachable WAGO adapter, and service-panel samples using the intended wall thickness, wire, strain relief, covers, and tools;
- pressure-port time constant and sensor placement coupon if needed.

#### 4. Engineering board bring-up

- verify every rail and startup sequence before fitting initiators or actuators;
- execute MCU ECC, watchdog, reset, clock, MPU, and memory-placement tests;
- exercise branch isolation and back-power;
- characterise sensor noise in every load state;
- run storage interruption and recovery tests;
- close thermal behaviour at atmosphere and low pressure;
- validate host workflow on supported macOS and Windows;
- capture all results per board serial.

#### 5. Integrated qualification article

Test the complete representative avionics bay: batteries, Ogma, Foinse, recovery controller, propulsion peer or emulator, harnesses, antennas, enclosure, camera, mounts, connectorised charge assemblies, pressure paths, and removable panels. Close it in the representative flight-ready state. Perform routine configuration, readback, logging, charging, and charge-module replacement only through the intended external interfaces. Verify against the manifest that no raw-wire adapter is installed. Qualification levels and durations must include margin over the accepted flight environment. Do not improvise them from generic NASA tables.

#### 6. Flight-unit acceptance

Acceptance should screen workmanship without consuming the flight unit's life through destructive over-test. Exact acceptance levels follow the qualified design and part limits.

### Fault-injection matrix

At minimum, inject:

| Injection | Required observed result |
| --- | --- |
| One-bit ECC diagnostic fault where the selected bank supports injection | correction/reporting/scrub verified, deadlines maintained; unsupported banks require separately identified evidence rather than an invented injection method |
| Two-bit ECC diagnostic fault where supported | uncorrectable path and bounded evidence handling verified against the accepted phase policy |
| Corrupt critical state/inverse/CRC | rejected and reconstructed or safe reset; no arbitrary transition |
| Corrupt each configuration slot and commit marker | newest valid compatible slot selected or safe default/no-go |
| Corrupt log record/header/address | surrounding valid records recover; no parser overrun |
| Reset at every state transition | outputs bounded; state recovers or safely degrades; no duplicate energetic event |
| External watchdog early/late/stuck heartbeat | reset and cause evidence as specified |
| Clock failure or wrong clock status | failover/reset path and timing bounds verified |
| Slow brownout, fast dip, repeated threshold crossing | no half-alive outputs; reset evidence retained |
| Battery contact bounce/hot plug | no damaging overshoot, false fire, storage corruption, or ambiguous boot |
| Communications branch hard short | flight rail and required loop remain within limits |
| Communications MCU UART flood/stuck lines | flight loop deadlines maintained; link isolated/degraded |
| GNSS absent/stale/corrupt/out of envelope | expected invalid mode; flight/recovery continues |
| Pressure sensor saturation/floor/blocked port | invalidity detected; no false apogee claim |
| IMU/high-g clipping and bias step | clipping/status recorded; estimator uncertainty/degraded path correct |
| SPI/I²C stuck lines and sensor back-power | bounded recovery/isolation; flight loop does not hang |
| Storage busy/short/full/corrupt | minimal event journal and flight functions continue |
| Maximum LoRa transmit | sensor, GNSS, regulator, storage, and reset criteria remain valid |
| Servo stall and rapid motion | no flight-rail reset or sensor corruption; harness/driver temperature valid |
| Dummy pyro fire/misfire/open/short | bounded pulse, current evidence, no repeat or neighbour-channel event |
| Charge-module connector open/short/cross-wire/partial-mate/pull/contamination | no false fire or wrong-channel path; fault is visible; internal harness and electronics remain undisturbed |
| ESD/transient at every accessible interface | no false energetic output; defined recovery and evidence |
| Video payload short/transmit/reboot | no Ogma effect |

Fault injection does not provide the probability of a cosmic event. It establishes whether the consequence is contained.

### Environmental sequence

An effective development sequence is:

1. baseline functional/performance test;
2. powered thermal and low-pressure mapping;
3. vibration and shock with operation/logging where safe;
4. post-mechanical inspection and functional test;
5. ESD/conducted/RF susceptibility;
6. combined worst-case load and mission HIL;
7. approved representative energetic test or non-energetic contamination surrogate outside the closed bay, followed by inspection of the protected volume and pressure paths;
8. final inspection, memory/log extraction, calibration comparison, and connector resistance check.

Order may change to isolate mechanisms. At least one representative article should experience the combined lifecycle in flight order because coating cracks, connector fretting, solder damage, and calibration shifts can be sequence-dependent.

### Full mission rehearsal

The release gate is an end-to-end rehearsal using flight-like hardware:

- cold vehicle and maximum pad wait;
- supported laptop, ordinary USB-C cable, offline host tool;
- identity/profile write-readback and independent review;
- all real harnesses and connectors installed;
- closure manifest completed and the electronics volume closed before connectorised charge assemblies are installed;
- each charge assembly replaced and its complete path rechecked without opening or moving the flight assembly;
- temporary WAGO/raw-wire adapters explicitly absent from the Kármán manifest and physical inspection;
- configuration/readback, log extraction, and charging performed through the intended closed-bay service interfaces;
- GNSS and telemetry groundstation active;
- communications faults injected without stopping flight operation;
- trajectory and sensor HIL through boost, GNSS loss, pressure floor, coast, apogee, descent, recovery, and landing;
- instrumented dummy pyro loads and representative servos;
- local logs and telemetry captured automatically;
- abrupt post-landing power loss at the worst logging time;
- log and video recovered using the documented field procedure;
- pass/fail report generated from immutable raw evidence.

Any reopening, internal re-mate, battery or board change, invasive debug access, or disturbed witness mark returns the article to the defined inspection and regression point. “We only changed one thing” is not a release state.

## Changes this would make to the current system description

This table maps the report back to [`current-system.md`](../../current-system.md). The workhorse role, provisional platform envelope, bounded Kármán mission, avionics-bay service boundary, and connector lifecycle have been accepted into the current architecture. Exact connector parts and every other row remain proposals unless the current-system document explicitly marks them otherwise.

| Current-system area | Required change |
| --- | --- |
| Scope and opening | Define Ogma 2 as the common 3–9 km competition workhorse, use the provisional Rev A envelope now, treat one bounded Kármán-line sortie as the extreme case, and require later mission overlays before qualification |
| Architecture boundary | Add an independent vehicle recovery controller as a separate power, sensor, logic, and initiator boundary; add video as a separate evidence payload |
| Two MCUs | Keep roles; require separate current-limited/switchable communications power, independent reset, no back-power, and corrupt-link containment |
| MCU selection | Add STM32H573 as working flight candidate and TMS570LS1227 as lockstep comparison; keep exact derivative open pending the resource/errata audit |
| Memory/logging | Require ECC memory placement, initialise/scrub/error policies, external supervisor, reset journal, atomic configuration, append-only record CRC, and internal event summary |
| Sensors | State that ordinary barometers are lower-atmosphere instruments; MAX-M10S cannot cover 100 km/likely dynamics; require high-g plus low-noise inertial roles and an independent apogee proof path |
| Pyro | Add physical energy interruption/readback, two-series-fault thinking, hardware pulse bound, fire-current evidence, phase-aware fault policy, and separate staging permissives |
| Power | Replace the provisional single logic chain with flight, sensor/storage, communications/RF, servo, and pyro fault-containment domains; resolve input hot-plug and supervisor behaviour |
| Foinse return | Prohibit direct exposure of flight-core 3.3 V; choose local Foinse regulation or a dedicated current-limited auxiliary branch |
| CAN | Add grounding/offset decision, protection, fixed two-node termination, application integrity, and explicit isolation criteria |
| Connectors | Put proper locking battery, CAN, pyro, and servo connectors on Ogma from Rev A; confine bare-wire terminals to detachable development adapters; exclude those adapters from Kármán flight; compare Nano-Fit, Micro-Fit, Micro-Lock Plus, JST GH, Gecko, and WAGO adapter candidates using real-wire qualification |
| Avionics bay | Make electronics responsible for functional integration; add a closed flight-ready state, replaceable connectorised charge assemblies, closed-bay USB/charging workflow, controlled vent and barometer paths, retained maintenance access, closure evidence, and reopening rules |
| USB/debug | Keep USB-C service-only; reopen the permanent 2×3 header in favour of a no-mass contact footprint if access remains adequate |
| PCB | Keep one double-sided board; reopen four versus six layers as a return-path/layout gate |
| Mechanical/manufacture | Add transient low-pressure thermal test, connector/harness vibration, selective coating/staking process, substitution control, and serialised factory evidence |
| Software | Add phase-aware reset recovery, build-enforced ECC placement, fault handlers, register readback, watchdog health path, and fault injection |
| Acceptance | Add the mission/hazard, power, ECC, HIL, thermal-vacuum, mechanical, EMC/ESD, harness, video-isolation, and full-rehearsal gates in this report |

## What does not change

- one visible, serviceable, double-sided main PCB;
- no hidden header-connected PCB sandwich;
- flight and communications work on separate MCUs;
- communications MCU is not a redundant flight computer;
- flight MCU does not wait for communications;
- CAN only leaves the board for named independent systems;
- no general payload power;
- Foinse remains separate and MCU-less;
- fixed soldered local storage and USB-C extraction;
- no PMOD, onboard display, speculative third MCU, or general action scripting;
- factory PCBA;
- small typed mission profile and legible readback;
- proper locking connectors are present for battery, CAN, pyro, and servo from Rev A;
- screw terminals remain rejected; WAGO/raw-wire terminals exist only on detachable development adapters and never in the Kármán flight configuration;
- simplicity and serviceability remain governing acceptance criteria.

## Rejected directions

### Rad-hard everything

Rejected for the bounded baseline. It spends board area, money, power, procurement time, and verification effort before the mission radiation integral exists. Reopen only with evidence.

### General triple modular redundancy

Rejected. It does not remove shared power, clock, PCB, software, connector, or mechanical failure and makes state management harder. Use ECC, invariants, small duplicated journals, and an independent vehicle recovery controller.

### A third Ogma MCU as backup recovery

Rejected. It remains on the same board and power/mechanical domain. Put genuinely independent recovery outside Ogma.

### Galvanic isolation on every interface

Rejected. Each isolator adds supplies, propagation, startup states, capacitance, and failure modes. Use it only at a measured ground/hazard boundary.

### Designing to orbital life

Rejected for this mission. Months/years of dose, thermal cycling, autonomous maintenance, redundant strings, and long-term ageing need a separate architecture and qualification case.

### Barometer or MAX-M10S as proof of 100 km

Rejected by their published operating envelopes.

### GoPro as a cure for microSD risk

Rejected. It also uses microSD. Select on tested system behaviour.

### Video powered from flight logic

Rejected. A camera or VTX fault must not affect recovery.

### A six-layer board merely because the flight reaches space

Rejected. Use six layers only if the actual layout and return paths need them.

### Coating or potting before inspection and qualification

Rejected. It can hide contamination, block sensors and contacts, change thermal behaviour, and prevent useful rework.

## Open design questions and later qualification gates

### P0: mission and safety

1. First vehicle and the point at which its simulated and measured trajectory, speed, acceleration, rotation, coast, descent, and powered duration replace the provisional platform envelope before qualification.
2. Accepted recovery topology, deployment events, initiators, independent controller, and range rules.
3. Staging architecture and the exact permissives for the third pyro channel.
4. Quantitative allowable probability of inadvertent fire, loss of recovery, loss of primary log, and loss of telemetry.
5. Independent method and uncertainty requirement for proving at least 100 km.
6. Battery chemistry, voltage, capacity, temperature, source impedance, location, and Foinse relationship.
7. Later measured vibration/shock/acoustic environment at the avionics mount and the qualification profile derived from it; exploratory screening proceeds now.
8. Later mission-specific launch, pad, bay, and component temperatures, enclosure venting, and pressure history; the provisional range governs Rev A.
9. Radio frequencies, powers, licences/range approvals, antennas, and groundstation.

### P0: compute and state

1. Exact H573 derivative/package resource matrix and errata disposition.
2. Measured ECC injection, correction, scrub, double-error, and reset behaviour.
3. Whether fault-injection evidence leaves a justified need for lockstep/TMS570.
4. Exact critical/non-critical memory allocation and DMA accessibility.
5. External supervisor part and state-aware watchdog/reset policy.
6. Boot time and reconstruction evidence in every flight phase.
7. Firmware/configuration update and recovery mechanism.

### P0: power and energetic outputs

1. Complete current budget and transient profiles.
2. Input protection, inrush, clamp, damping, UV/OV, and hot-plug measurements on the real harness.
3. Flight-core regulator topology and low-pressure thermal result.
4. Communications, sensor, and storage branch switches/current limits/back-power paths.
5. Foinse low-power supply ownership.
6. Pyro circuit, initiator no-fire/all-fire data, pulse energy, continuity current, arm boundary, and fault tree.
7. Servo models, voltage, stall current, transient current, endpoints, and mechanical loads.

### P1: sensing, storage, interfaces, and mechanics

1. High-g and low-noise IMU parts, ranges, bandwidth, alignment, temperature calibration, and saturation behaviour.
2. Pressure sensor/port placement and valid lower-flight envelope.
3. GNSS role and a full-trajectory receiver or external proof system.
4. Fixed NOR capacity, endurance, temperature, program-interruption behaviour, and log extraction time.
5. CAN ground/isolation choice and propulsion-controller power relationship.
6. Exact battery, pyro, servo, arm, Foinse, CAN, RF, USB-C, and debug connector parts; connectorised charge/servo assemblies; detachable raw-wire adapters; and harness drawings.
7. Four- versus six-layer placement/return-path result.
8. Enclosure, board mounts, thermal conduction, venting, coating, staking, and antenna geometry.
9. Exact clean/dirty boundary, flight-harness connector or feedthrough, connectorised charge module, service-panel geometry, pressure-equalisation path, barometer-port relationship, closed-bay USB/charging path, closure record, and reopening rule.
10. Exact video camera/card/VTX/battery/mount and whether live downlink is a real mission requirement.

## Immediate next sequence

1. Translate the accepted provisional envelope into rail-energy, storage, sensor-range, temperature, pressure, and mechanical-screening budgets. Open a mission-overlay template for the first vehicle; do not wait for mature simulation before beginning Rev A.
2. Execute EX-04's exact-part resource/ECC spike, comparing H563/H573 where relevant: linker classes, supported diagnostic injection, separate application-corruption tests, scrub, watchdog, retention, boot time, and bounded fault handlers.
3. Draw the complete standalone and Ogma/Foinse power trees with branch fault currents and return paths. Build the input/regulator/comms-branch mule against the real battery and harness.
4. Close the recovery and staging energetic-output fault trees before selecting MOSFETs or connectors.
5. Put actual Nano-Fit, Micro-Fit, Micro-Lock Plus, JST GH, Gecko, WAGO MCS MICRO 2712, and WAGO 2601 samples beside the real wires, boards, batteries, antennas, camera, e-match leads, connectorised charge assemblies, removable panel, vent route, and service tools in the 1:1 avionics-bay layout. Demonstrate charge-module replacement, USB service, and charging with the flight assembly closed; verify the temporary adapter is absent; then pull, disturb, vibrate, contaminate externally, pressure-cycle, and inspect it.
6. Exercise the provisional 100 km case through candidate sensor limits. Decide how apogee is proved and how recovery state survives the pressure/GNSS dead region. Replace the provisional profile when the first mature vehicle simulation exists.
7. Freeze Rev A MCU, power, sensor, storage, connector, layer-count, and schematic choices against the provisional envelope while recording the later mission evidence that could overturn each choice.

## Evidence basis

### Current Ogma authority

- [`current-system.md`](../../current-system.md): current architecture checkpoint, updated 2026-09-03.
- [`project-log.md`](../../project-log.md): chronological Ogma 2 record.
- [`ogma-rev1-flight-closure.md`](../../sources/project/ogma-rev1/ogma-rev1-flight-closure.md): Rev 1 flight evidence, including the unexplained T+14.976 s reset.
- [`rev1-unified-learnings.md`](../../sources/project/ogma-rev1/rev1-unified-learnings.md): consolidated Rev 1 electrical, software, integration, and workflow evidence.
- [`rev2-requirements.md`](../../sources/project/ogma-rev1/rev2-requirements.md): earlier requirements inherited where still compatible.
- CATS Vega and Fluctus photographs (removed 22 Nov 2026, reuse rights unresolved): geometry, access, connector, and stack observations only.

### Recent design framing

- Connective Tissue record `rec_443820df07f258acba2a8de9d2a64741ed54ca70bd735e13a6bae186f547e07d`, 2026-08-28: attributed Seán notes while watching Sir Peter Beck. It records the “valley of death,” the difference between reaching orbit and living there for twelve years, and the different qualification duration of a single-use versus reusable engine. It is evidence of Seán's design framing. It is not used as a verified Peter Beck transcript.
- Seán's instruction on 2026-08-29: scope this work to “it makes it to the Kármán line at apogee and back down”; analyse deeply without importing the reliability problem of a six-month or multi-year spacecraft; treat video as a separate consideration.
- Connective Tissue record `rec_75acf8afac76014b1eadade505eb0de9dec1ec3c9cc25e8ee824cbb31b154ae4`, 2026-08-31: explicitly attributed Anav/Seán discussion of coating, high-g measurement, GNSS envelope, low-pressure thermal concerns, error checking, measured execution timing, and possible BPS.space review. “Coating could have saved Fluctus” remains an unproven hypothesis; no coating or outreach was selected by that conversation.
- Connective Tissue record `rec_9a8411aad8ba4018258da2e2aaa77bf172014f20561de31095004834a2906cdc`, 2026-09-01: attributed Seán statement that avionics-bay work belongs within electronics.
- Connective Tissue record `rec_b94e2f6e4e8e8225a37a366d267af763114dea3afbd970cddb1eed1f4bad5d26`, recorded 2026-09-01 and transcribed 2026-09-02: anonymous-speaker voice transcript describing Anav's proposal for external replaceable e-match connections, a closed tested avionics assembly, contamination separation, and removable service access. Attribution to Anav is indirect through the transcript wording; speech recognition and diarisation may contain errors.
- Connective Tissue record `rec_282f3ba5050e5b35a0fd9db774b446a937fc09b46364eacc8e0e093919d4d110`, 2026-09-01: saved model launch-process analysis followed by Seán's direct recollection of the Anav/Ashen pyro matrix marked “Test v2,” “Seal everything!” and “Pins = Flight.” Only the attributed follow-up is treated as Seán's recollection.
- Seán's instruction on 2026-09-03: screw terminals are too fiddly and electrically exposed; WAGO-style terminals are safer for temporary raw-wire work but generally too large; such terminals are temporary servo/pyro interfaces and will not fly on the space-shot; battery and CAN use proper connectors from the start. Seán then accepted proper Ogma connectors for pyro and servo as well, with WAGO terminals confined to detachable adapters and connectorised assemblies used for Kármán flight.

### Primary external sources

The relevant primary sources are linked where their claims appear. The main groups are:

- NASA NEPP radiation-effects and system-level hardening material;
- NASA NAIRAS, NASA Standard Atmosphere, NASA GEVS, and NASA grounding/workmanship material;
- ESA SPENVIS and ECSS PCB workmanship/design material;
- ST, TI, NXP, Microchip, and VORAGO manufacturer MCU documents;
- u-blox, TE Connectivity, and Bosch sensor documents;
- Analog Devices hot-plug application evidence;
- TI and ST interface/ESD design material;
- Harwin, Molex, JST, and WAGO connector manufacturer data;
- RunCam and GoPro manufacturer camera/storage material.

### Inference and unknowns

- The architectural recommendations are engineering inferences from the stated short mission, current Ogma architecture, Rev 1 failures, local mechanical evidence, and the cited primary material.
- No radiation event probability has been calculated because the trajectory and device cross-sections are missing.
- No regulator, supervisor, connector, IMU, storage, CAN transceiver, radio, or pyro driver has been selected by this report.
- No vibration, shock, ESD, thermal-vacuum, or reliability level has been accepted.
- No claim is made that current Ogma 2 hardware can survive the mission. No schematic or PCB exists.

## Closure condition

This report remains a design study until the team dispositions the P0 questions. Individual proposals may enter [`current-system.md`](../../current-system.md) only through explicit acceptance; that does not ratify the rest of the report. Test results and decisions enter [`project-log.md`](../../project-log.md) without rewriting earlier chronological entries.
