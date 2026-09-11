# Ogma, Foinse, and propulsion boundary

**11 September review hold:** this contract's electrical and safety obligations
are unchanged. The [joint-review record](../docs/architecture/2026-09-10-session-review.md)
identifies proposed changes; none is implemented or accepted here. Earlier
instructions below to proceed with schematics are superseded by Seán's explicit
hold: no schematic/PCB changes until the final stack is authorized.

Updated: 7 September 2026

Status: current owned architecture boundary; Croí/Foinse implementation baseline
accepted, propulsion load sizing and cross-project message implementation open

Authority: [`../current-system.md`](../current-system.md)

This file carries the cross-system boundary needed to develop Ogma 2, Foinse 2,
and the liquid-propulsion controller without merging their responsibilities.
Controlled interface definitions and tested hardware override it where they
conflict.

Foinse 2 is MCU-less and has no firmware image. Its source/protection circuitry
can still have electrical supply dependencies; the
[power review](../docs/reliability-design-review.md#51-mcu-less-foinse-startup)
and [EX-02 power contract](power-contract.md) examine those without adding a
processor. Seán accepted retaining the protected auxiliary return subject to
autonomous source/protection operation and demonstrated fault containment.
The [7 September acceptance](../docs/architecture-acceptance-2026-09-07.md)
selects the Croí/Foinse parts and connectors. This does not change any system's
authority or edit the LTS project.


7 September sensing revision: Croí owns the common protected AV discharge shunt
and INA228 0x40, including standalone operation; Foinse retains propulsion INA
0x41 and ADS1115 0x48. The Samtec pinout and power authority are unchanged.
FOINSE_RETURN_EN must also enable Croí-local monitoring without Foinse present.
No duplicate Foinse AV shunt remains. All Croí battery load takeoffs, including
future physical arm feeds, must follow its shunt; USB/charging/propulsion remain
outside that measured path. Monitoring never enables autonomous protection.
See [the revision contract](../docs/sensing-indication-time-review-2026-09-07.md).

## Authority

| System | Owns | Does not own |
| --- | --- | --- |
| Ogma 2 | Vehicle mission state, high-level engine requests, bounded propulsion summaries, recovery, and staged-flight energetic authority | Engine redlines, main-engine actuation, GSE, or propulsion power distribution |
| Propulsion controller | Engine-critical acquisition, local state/redlines, main-engine valves, ignition, local abort, and local full-rate evidence | General GSE sequencing, research-only stand DAQ, or vehicle recovery |
| Foinse 2 | Vehicle source entry, protection, charging functions, and vehicle-specific power distribution | Flight state, propulsion state, redlines, or command decisions |

The propulsion controller is a self-governing peer. It must perform its defined
local safe response while Ogma is reset, CAN is absent or corrupt, and the
operator UI is disconnected.

## Logic interface

- Ogma and propulsion use one linear two-node CAN link with fixed end
  termination.
- GSE, the stand host, and the remote operator computer do not join that
  production bus.
- CAN carries versioned bounded requests, propulsion state, health, counters,
  validity, and selected summaries.
- Full-rate engine data stays in propulsion-local storage or uses a bounded
  test-only path.
- Croí selects 500 kbit/s Classical CAN with TCAN3413DRBR, fixed 120 Ω end
  termination and JST GH: pin 1 CAN H, pin 2 CAN L, pin 3 reference. No power
  pin. Exact messages and installed cable/bonding evidence still need joint
  implementation. An open propulsion return must not divert actuator current
  through the CAN reference; if bonding cannot satisfy that, review isolation
  of the complete interface boundary before claiming containment.
- Ogma and propulsion firmware consume one machine-readable versioned message
  contract when implementation begins.

An LTS host-controlled adapter may temporarily occupy Ogma's second-node
position before real Ogma exists. It is removed when Ogma is installed. It does
not create a production third node or bridge the vehicle bus to GSE.

## LTS implementation and recording scope

The 4 September LTS working baseline combines propulsion and GSE responsibilities
on one controller PCB and one primary MCU. CAN A retains the production
Ogma/propulsion contract. A separate, unbridged CAN B accepts GSE requests from a
second host adapter. Both logical partitions share the primary-MCU reset/power
fault boundary; neither survives a whole-MCU reset by virtue of its software role.

The LTS controller streams a bounded combined full-rate copy over local USB-C
to a Linux stand PC. That PC owns the complete LTS run; the board keeps only a
bounded pre/post-event incident package. Exact reset/power-loss retention remains
open. This LTS choice does not change the flight propulsion local-recording
direction or Ogma's full-rate flight evidence requirements.

The LTS PCB is not required to fly unchanged. Reuse is proven circuits, software,
interfaces and tests; later vehicle hardware is qualified against its own needs.
No flight mission depends on the stand PC.

Automatic safing on loss of the complete LTS operator path must not be defeated
by continuing Ubuntu/CAN heartbeats. A locally expiring operator permission is
an LTS proposal whose contract and real-Ogma test integration still need joint
review. It does not silently impose an operator-presence requirement on flight.

## Power interface

- Foinse supplies protected named vehicle branches and paired returns.
- Ogma creates and supervises its internal rails from its defined input.
- The propulsion controller creates and supervises its own logic and sensor
  rails from its Foinse branch.
- Ogma's logic rail does not power propulsion logic, sensors, or actuators.
- Foinse may receive only the bounded protected low-power return explicitly
  accepted in the current architecture; it is not a general Ogma power bus.
- Foinse's basic source/protection path must start and remain functional without
  that return or Ogma software. If actual devices cannot satisfy this cleanly,
  local Foinse regulation requires a recorded review before dependent layout
  is frozen; it is not silently selected here.
- Croí uses one protected 2S feed, provisional 6 A aggregate, through the
  Samtec MPS-08-01-01-L-RA-SD (Foinse) / MPT-08-01-01-L-RA-SD (Croí) pair.
  Pins 1/2 are VBAT/return, 3/4 protected auxiliary 3.3 V/return, 5/6 local
  monitor SCL/SDA, 7 nFAULT and 8 NC. Both ground paths must independently
  withstand the full alternate fault return. No charger or propulsion current
  is allocated through Croí. The coplanar assembly needs a retention bridge.
- Foinse source protection is pack-powered TPS26630/CSD18540; INA228 and
  ADS1115 are bounded monitoring, never boot/protection prerequisites.
- Larger liquid use adds a separate 6S propulsion pack/domain, raw 18–25.2 V
  planning range. Actual coil current, duty, surge suppression and need for
  regulated 24 V remain conditional on the propulsion design. This is not a
  frozen valve count or completed propulsion supply specification.
- Charging uses matched external balance chargers and controlled fused service
  wiring with physical charge/arm exclusion. Independent recovery has its own
  qualified supply/path outside the shared Foinse fault boundary.

## Required boundary tests

- communications MCU held in reset without loss of flight function;
- propulsion controller held in reset or failed short without collapse of the
  flight-computer branch;
- CAN removed, corrupt, bus-off, and incorrectly terminated;
- stale, replayed, and illegal high-level requests;
- each source branch browned out, interrupted, shorted where safe to test, and
  restored;
- Foinse cold start and continued basic source delivery with returned auxiliary
  power absent, followed by controlled auxiliary-branch fault containment;
- failure of Ogma's logic rail without unsafe propulsion output;
- full-rate local evidence and first-fault retention through the above;
- production Ogma/emulator interchange without adding another CAN node.

## Change rule

A pull request may clarify this boundary. It must not silently change Ogma,
Foinse, propulsion, GSE, or recovery authority. A real change requires an
owning-project decision, updated interface and verification definitions, and a
corresponding update to current system truth and the project log in every
affected repository.
