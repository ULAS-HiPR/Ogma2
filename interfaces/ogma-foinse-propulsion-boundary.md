# Ogma, Foinse, and propulsion boundary

Updated: 5 September 2026

Status: current owned architecture boundary; exact electrical interfaces remain
open

Authority: [`../current-system.md`](../current-system.md)

This file carries the cross-system boundary needed to develop Ogma 2, Foinse 2,
and the liquid-propulsion controller without merging their responsibilities.
Controlled interface definitions and tested hardware override it where they
conflict.

Foinse 2 is MCU-less and has no firmware image. Its source/protection circuitry
can still have electrical supply dependencies; the
[power review](../docs/reliability-design-review.md#51-mcu-less-foinse-startup)
and EX-02 examine those without adding a processor or selecting a new supply
topology. This clarification does not change any system's authority.

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
- Classical CAN versus CAN FD, bitrate, connector, cable, reference/isolation,
  and exact messages remain open.
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
- Exact voltage ranges, source impedance, current, connector, actuation split,
  protection, and monitoring remain open.

## Required boundary tests

- communications MCU held in reset without loss of flight function;
- propulsion controller held in reset or failed short without collapse of the
  flight-computer branch;
- CAN removed, corrupt, bus-off, and incorrectly terminated;
- stale, replayed, and illegal high-level requests;
- each source branch browned out, interrupted, shorted where safe to test, and
  restored;
- failure of Ogma's logic rail without unsafe propulsion output;
- full-rate local evidence and first-fault retention through the above;
- production Ogma/emulator interchange without adding another CAN node.

## Change rule

A pull request may clarify this boundary. It must not silently change Ogma,
Foinse, propulsion, GSE, or recovery authority. A real change requires an
owning-project decision, updated interface and verification definitions, and a
corresponding update to current system truth and the project log in every
affected repository.
