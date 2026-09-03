# Ogma Rev 2 Requirements From Rev 1 Evidence

Updated: 2026-08-31

## P0 - Safety and Control

- Pleasc physical arm/RBF input readable by firmware.
- Lamh PCA9685 OE controlled by MCU and hardware-default-disabled.
- Boot-safe pulldowns and measured reset behaviour for all energetic/actuator outputs.
- External power branches protected and isolatable.
- Watchdog, bounded leases, finite pulses, one-shot deployment state, and event logging retained.

## P0 - Bring-Up Access

- Standard SWD header: SWDIO, SWCLK, NRST, BOOT0, 3.3 V, ground.
- SWCLK damping footprints and short grounded routing.
- Labelled test pads for every rail, bus, chip select, reset, enable, and external signal.
- Per-device SPI isolation links.
- Spare GPIO and debug UART pads on every STM board.

## P0 - Correctness Reviews

- Exact manufacturer part number, symbol, footprint, pin-1, and orderable suffix sign-off.
- Second-person schematic-to-PCB net audit before release.
- Current architecture, populated BOM, and firmware target agree.
- Automated clean builds for flight and diagnostic targets.

## P0 - Integration and Flight Operations

- Name one owner and one checker for every critical subsystem and interface.
- Hold a planned full-stack integration event before launch with empowered
  avionics, structures and recovery representatives.
- Complete a flight-like dress rehearsal using the intended hardware,
  structures, harness, power path, switches, groundstation and release package.
- Keep working test matrices separate from the reviewed as-flown manifest.
- Freeze and archive hardware identities, firmware/configuration readbacks,
  hashes, calibrations, wiring/channel maps and checklist evidence before flight.
- Use versioned integration, launch-day and scrub/post-flight checklists with
  explicit stop conditions and named sign-off authority.
- Treat any post-freeze cross-subsystem change as invalidating the affected
  sign-off and requiring defined re-verification.
- Follow the canonical
  [flight integration and release checklist](flight-integration-and-release-checklist.md).

## P1 - Power and CAN

- Rail-present LEDs at source and local stages.
- Clear stack power ownership and expected-voltage tables.
- CAN TX/RX, CANH/CANL, enable/standby, and termination access.
- TVS/ESD and keyed connectors reviewed against likely miswiring.
- Branch fusing/links for external 5 V loads.
- Validity-checked battery and rail voltage, current, temperature and
  state-of-charge telemetry.
- Reset-cause and short pre-reset power records preserved before startup clears
  the relevant hardware state.

## P1 - Board-Specific

- Croi: corrected SPI routing/footprints, obvious pin-1 marks, isolated peripherals.
- Teachtaire: GNSS UART/PPS access, SX1272 identity/config truth, RF matching option and reviewed feed.
- Foinse: observable ORing nodes, retained battery interface, documented safe
  laboratory bypass, calibrated current channels and valid
  voltage/temperature/state-of-charge telemetry.
- Lamh: OE safety path, output test points, mechanically verified per-output safe positions.
- Pleasc: physical arm input, explicit logic/energetic separation, continuity and output test points.
- Mu: bias/threshold/temperature calibration points and injected-pulse test input.

## P2 - Documentation

- Connector pinout and idle-state table per board.
- Power tree and bring-up sequence per board.
- One radio configuration and packet protocol shared by flight and ground firmware.
- Dated HIL evidence tied to board, firmware, mission, and calibration revisions.
- Power HIL reproducing the complete connector and Wago arrangement intended for
  flight, including hot-plug, cold-start, disturbance and representative load
  steps.
