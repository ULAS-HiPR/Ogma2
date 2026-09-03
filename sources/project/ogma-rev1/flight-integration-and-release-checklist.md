# Ogma Rev 2 Flight Integration and Release Checklist

Status: required process draft; not flight clearance

Updated: 2026-08-31

## Purpose

Make subsystem ownership, full-vehicle integration, configuration control and
field release explicit before Ogma Rev 2 flies. This checklist supplements the
technical HIL campaign. It does not replace board qualification, structures or
recovery review, range procedures, or an approved energetic-test procedure.

## Evidence and decision

- Ogma Rev 1 reached the launch site with field changes to its power path, and
  the exact flashed release could not later be reconstructed from clean commit
  hashes alone.
- The Rev 1 closure already requires the field configuration to match a
  rehearsed configuration and forbids launch-site feature work without a full
  acceptance replay.
- An August 2026 two-stage integration showed that paired subsystem ownership
  can work well: separate booster and sustainer teams completed configuration
  and deployment tests while an avionics lead moved between the interfaces.
  However, first full-vehicle integration on launch day left too little time for
  discrepancies. The weather scrubbed the flight, so flight readiness was not
  demonstrated.
- A handwritten deployment-test matrix usefully externalised controller,
  channel, compartment and test-state decisions, but ambiguous marks also showed
  why a working test matrix and the final as-flown manifest must be separate.

Decision: Rev 2 requires at least one planned full integration event and one
flight-like dress rehearsal before launch. Launch day is for verification and
execution, not first integration.

## Roles

- Name one integration lead.
- Name one owner and one checker for every critical subsystem and interface.
- Require an empowered representative for avionics, structures and recovery at
  the full integration event. The entire project membership need not attend.
- Keep subsystem work parallel. Owners bring evidence-complete assemblies to
  the integration event; the integration lead resolves seams rather than
  rebuilding every subsystem.

## 1. Integration entry gate

- [ ] Vehicle, flight, revision, event date and integration lead identified.
- [ ] Every flight board and support device identified by role and hardware
      revision; serial or other unique identity recorded where available.
- [ ] Candidate firmware, configuration, calibration and dependency versions
      exported and hashed.
- [ ] Subsystem owner and checker named; bench evidence linked.
- [ ] Mechanical interfaces, harnesses, batteries, switches, antennas, cameras,
      storage media and required programming adapters available.
- [ ] Open findings reviewed. Any unresolved flight blocker stops integration or
      is explicitly bounded to a non-flight test.

## 2. Full integration event

- [ ] Assemble the exact intended board stack, retention, structures, harness,
      power path, switches, antennas and service access.
- [ ] Verify connector identity, strain relief, polarity, continuity, isolation
      and expected voltage before powering each branch.
- [ ] Power the closed assembly through the intended flight path; verify boot,
      board identities, CAN peers, storage, sensor validity and reset evidence.
- [ ] Read back the mission configuration from the hardware and compare it with
      the candidate manifest.
- [ ] Exercise groundstation, telemetry, GNSS, cameras and local status together.
- [ ] Run the complete countdown, abort, safing, flight replay, deployment and
      recovery sequence using inert simulators where energetic outputs are not
      specifically authorised.
- [ ] Record discrepancies, owners and retest scope before disassembly.

Energetic deployment testing must use a separately reviewed procedure. Its test
matrix records the exact controller, physical output, target compartment,
candidate configuration, sealed mechanical state, expected result, observed
result and pass/fail decision. Only reviewed results are promoted into the
as-flown manifest; circles, ticks and scratch annotations are not flight
configuration authority.

## 3. Dress rehearsal and release freeze

- [ ] Repeat assembly using the intended flight hardware and field tools.
- [ ] Execute the integrated dress rehearsal required by the
      [HIL campaign](hil-test-campaign.md).
- [ ] Close or disposition every discrepancy. Repeat affected tests; repeat the
      full rehearsal when a change crosses subsystem boundaries.
- [ ] Freeze the as-flown manifest: hardware identities, firmware binaries and
      hashes, configuration readbacks, calibrations, wiring/channel map,
      batteries, switches, antennas, storage and mechanical revision.
- [ ] Archive the signed checklist, test evidence and release package together.
- [ ] Any post-freeze hardware, wiring, firmware or configuration change
      invalidates the affected sign-off and triggers defined re-verification.

## 4. Launch-day checklist

- [ ] Confirm crew roles, communications, site authority and stop conditions.
- [ ] Inventory flight hardware, support equipment, chargers, adapters, cables,
      radios, storage media, tools and spares. Record borrowed-item owner and
      return responsibility.
- [ ] Inspect the sealed vehicle for transport damage, connector movement,
      retention, strain relief and unintended switch state.
- [ ] Verify board identity, release/manifest identity, battery state, storage,
      telemetry, GNSS, continuity and groundstation capture without changing the
      frozen configuration.
- [ ] Follow the reviewed arm, pad, launch, abort and safe-state procedures.
- [ ] Stop on any identity/configuration mismatch, unexplained reset, invalid
      sensor, failed continuity, damaged retention, uncertain wiring or missing
      required evidence.

## 5. Scrub or post-flight closeout

- [ ] Safely disarm and account for every energetic and power state.
- [ ] Preserve configurations, logs, groundstation data, photographs and the
      actual physical state before repair or reconfiguration.
- [ ] Record scrub/flight result, discrepancies and whether each previous test
      remains valid.
- [ ] Return borrowed equipment and close its owner record.
- [ ] Assign inspection, repair and retest owners before the next launch window.

## Acceptance and unknowns

Flight release requires the integration lead plus the named subsystem owners and
checkers to accept the final manifest and checklist. Exact sign-off authority,
minimum lead times, structures/recovery gates and energetic-test procedures
remain team decisions and must be settled before this draft becomes operational.

Next checkpoint: run this checklist as a paper exercise at the first Rev 2
avionics/structures integration event, record the friction, then revise it from
observed use.
