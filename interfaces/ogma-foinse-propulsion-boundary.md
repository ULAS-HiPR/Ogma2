# Ogma, Foinse and propulsion boundary

**Status, 6 October 2026, amended 2, 18 and 20 November: controlling contract.** Electrical
detail describes the 8 September CAD. Decided changes are in
[decisions.md](../decisions.md) and the
[capture specification](../docs/architecture/schematic-capture-spec.md). Capture
waits for Seán's go-ahead. The LTS copy in `lts-controls/interfaces/` points
here; if the two differ, this file wins.

Authority: [current system](../current-system.md). This file sets the boundary
between Ogma 2, Foinse 2 and the liquid-propulsion controller so each can be
developed without merging their jobs. Controlled interface definitions and
tested hardware override it where they conflict.

## Background

- Foinse 2 has no MCU and no firmware image. Its source and protection circuits
  can still depend on supplies; the
  [power review](../docs/archive/reliability-design-review.md#51-mcu-less-foinse-startup)
  and the [EX-02 power contract](power-contract.md) cover those without adding a
  processor.
- Seán accepted keeping the protected auxiliary return, on condition that source
  protection runs on its own and fault containment is demonstrated.
- The [7 September acceptance](../docs/archive/architecture-acceptance-2026-09-07.md)
  chose the Croí and Foinse parts and connectors. That changes no system's
  authority and doesn't edit the LTS project.
- Current sensing (7 September, [revision](../docs/archive/sensing-indication-time-review-2026-09-07.md)):
  Croí owns the protected AV discharge shunt and INA228 0x40, standalone too;
  Foinse keeps propulsion INA228 0x41 and ADS1115 0x48, and adds ACT INA237 0x44,
  ADS1115 0x49 and charger-status TCA9535 0x20, all only read by Croí
  (D-22Nov.4, D-22Nov.5). `FOINSE_RETURN_EN` must
  also enable Croí-local monitoring when Foinse isn't there. No duplicate Foinse
  AV shunt; Croí logic takeoffs come after its shunt. Pyro and servo energy leave
  before U101 through their own fuses and bypass it (D-6.1); per-channel current
  comes from the TPS1H100 sense. USB, charging and propulsion are outside the
  measured path. Monitoring never enables autonomous protection. Power authority
  is unchanged.

## Who owns what

| System | Owns | Doesn't own |
| --- | --- | --- |
| Ogma 2 | Vehicle mission state, high-level engine requests, bounded propulsion summaries, recovery, staged-flight energetic authority | Engine redlines, main-engine actuation, GSE, propulsion power distribution |
| Propulsion controller | Engine-critical acquisition, local state and redlines, main-engine valves, ignition, local abort, local full-rate evidence | General GSE sequencing, research-only stand DAQ, vehicle recovery |
| Foinse 2 | Vehicle source entry, protection and vehicle-specific power distribution, including the rail umbilical, on-board charging through it (D-20Nov.1, D-21Nov.2) and the actuator feeds to Fajita and the active board (D-21Nov.1) | Flight state, propulsion state, redlines, command decisions |

The propulsion controller is a self-governing peer. It must carry out its own
defined safe response while Ogma is in reset, CAN is missing or corrupt, and the
operator UI is disconnected.

## Logic interface

- One linear two-node CAN link between Ogma and propulsion, terminated at both
  ends.
- GSE, the stand host and the remote operator computer never join that
  production bus.
- CAN carries versioned, bounded requests, plus propulsion state, health,
  counters, validity and selected summaries. Ogma's rule for every node
  (D-2Nov.9): permissions and mode; slow state that stays valid through Ogma's
  worst-case 550 ms restart; health; and commands the receiver drops to safe
  when they go stale. No sensor streams or control loops at loop rate.
- The closed-loop actuator node (roll control, grid fins) is the active board,
  on its own CAN bus from Ogma (D-5Nov.3), powered through Foinse's ACT branch
  (D-21Nov.1). It never joins this link, so this link stays two-node.
- Full-rate engine data stays in propulsion-local storage or goes over a bounded
  test-only path.
- Croí: 500 kbit/s Classical CAN, TCAN3413DRBR, fixed 120 Ω end termination,
  pin 1 CAN H, pin 2 CAN L, pin 3 reference. No power pin. Connector: Ogma
  moves J501 from JST GH to Harwin Gecko (D-18Nov.4), so Fajita's end
  has to match, which is ours to design in since D-20Nov.2.
- Croí's two transceivers share one standby line (PE10) and one supply limiter
  (D-5Nov.3): one fault there quiets this link and bus 2 together. Propulsion's
  safe response to a missing link covers it.
- Exact messages and installed cable and bonding evidence still need doing
  together.
- An open propulsion return must not push actuator current through the CAN
  reference. Burrito puts a series part in each reference to limit it
  (D-21Nov.11, B-39); Fajita may also isolate its CAN.
- Once implementation starts, Ogma and propulsion firmware both use one
  machine-readable, versioned message contract.

Before a real Ogma exists, an LTS host-controlled adapter may sit in Ogma's
second-node position. It comes out when Ogma goes in. It doesn't make a
production third node and doesn't bridge the vehicle bus to GSE.

## LTS implementation and recording

- The 4 September LTS baseline puts propulsion and GSE on one controller PCB
  with one primary MCU.
- CAN A keeps the production Ogma / propulsion contract. A separate, unbridged
  CAN B takes GSE requests from a second host adapter.
- Both partitions share the primary MCU's reset and power fault boundary.
  Neither survives a whole-MCU reset because of its software role.
- The LTS controller streams a bounded combined full-rate copy over local USB-C
  to a Linux stand PC, which owns the complete LTS run record. The board keeps
  only a bounded incident package from before and after an event. Exact reset and
  power-loss retention are open.
- None of this changes the flight propulsion local-recording direction or Ogma's
  full-rate flight evidence requirements.
- The LTS PCB doesn't have to fly unchanged. What carries over is proven
  circuits, software, interfaces and tests; later vehicle hardware is qualified
  against its own needs. No flight depends on the stand PC.
- Losing the whole LTS operator path must trigger automatic safing, and
  continuing Ubuntu or CAN heartbeats must not defeat that. A locally expiring
  operator permission is an LTS proposal; its contract and real-Ogma test
  integration still need joint review. It doesn't impose an operator-presence
  requirement on flight.

## Power interface

- Foinse supplies protected, named vehicle branches with paired returns.
- Ogma makes and supervises its own internal rails from its defined input.
- The propulsion controller makes and supervises its own logic and sensor rails
  from its Foinse branch.
- Ogma's logic rail never powers propulsion logic, sensors or actuators.
- Foinse may take only the bounded, protected low-power return accepted in the
  current architecture. It is not a general Ogma power bus.
- Foinse's basic source and protection path must start and keep working without
  that return and without Ogma software. If real devices can't manage that
  cleanly, local Foinse regulation needs a recorded review before dependent
  layout is frozen. It isn't chosen here.
- Croí takes one protected 2S feed, provisional 6 A aggregate, through the
  Samtec pair: MPS-08-01-01-L-RA-SD on Foinse, MPT-08-01-01-L-RA-SD on Croí.

  | Pins | Signal |
  | --- | --- |
  | 1 / 2 | VBAT / return |
  | 3 / 4 | Protected auxiliary 3.3 V / return |
  | 5 / 6 | Local monitor SCL / SDA |
  | 7 | nFAULT |
  | 8 | `CROI_POWER_HOLD` (D-6.3) |

  Each ground path must carry the full alternate fault return on its own. No
  charger or propulsion current goes through Croí. The coplanar assembly needs a
  retention bridge.
- Foinse source protection is pack-powered TPS26630 / CSD18540. INA228 and
  ADS1115 are bounded monitoring, never needed for boot or protection.
- Liquid use adds a 6S actuator pack, planning range 18–25.2 V raw, feeding two
  protected Foinse branches: PROP to Fajita and ACT to the active board
  (D-21Nov.1). Fajita converts to its actuators' voltages itself. Jay (20 Nov,
  said): about nine valve servos, three per bank, angle sensors on all but the
  main fuel valves, no propulsion solenoids. PROP's rating is set at the Churro
  power review; each valve's unpowered state, and the vent's, are still to
  define (ECU-06, LV-0190).
- On the rail, a ground umbilical feeds both Foinse branches through per-source
  ideal diodes ahead of the eFuses, so the enables and protection still apply
  and the diodes can't charge a pack. Pulling it hands each branch to its pack (D-2Nov.7).
  AV is set at 8.4 V; the PROP umbilical voltage is set at the Churro review
  (D-21Nov.1), to suit the 6S charger and both actuator branches.
- Charging is on board, through the umbilical: one standalone charger per pack
  voltage, at maintenance rate, temperature-gated. There is no charge/arm
  interlock; fault analysis and a bench test show no charger fault makes a
  firing path (D-20Nov.1, D-21Nov.2). Independent recovery keeps its own cell
  and path; its charge lead is protected so no Foinse fault can drain or short
  that cell (C-23).
- The e-reg is its own board on its own CAN link to Fajita, and never joins this
  link. Fajita protects against overpressure independently of it (D-21Nov.10).

## EuRoC items on the propulsion side

From EuRoC SRD Issue 1.1 (traced 18 November). Fajita's owner answers and
evidences these with propulsion (D-20Nov.2); listed here because each
touches this boundary. None is decided.

- **PROP pack (LV-0300, 0310, 0320):** no LiPo; Li-ion only in metal-can
  cylindrical cells (Appendix C). 6S Li-ion keeps Foinse's 18–25.2 V planning
  range; LiFePO4 would change its protection values. Reachable from the ground,
  and good for 6 h on the rail with whatever Fajita draws there.
- **Valve power disconnect (Appendix E1, a "should"):** a manual, ground-level
  disconnect (pull-plug or key) in the valves' hot line, not the return. Where it
  sits (the PROP harness, Foinse or Fajita) is to agree.
- **Remote vent after an abort (LV-0190):** once the umbilical is pulled at Go,
  which path carries the command: Fajita's own link, or Ogma's radio relayed over
  this link (firmware, not hardware).
- **Igniter arming (LV-0030):** armable and disarmable only with nobody within
  15 m, so remotely.
- **Loading (LV-0110, 0130, 0150):** pressurise only after the loading lines are
  off; a hand-operated emergency release on any remote loading mechanism; loading
  done within 90 minutes.
- **Hold-down (LV-1020):** released only once thrust is enough for stable flight.
- **Launch control (SE-0010–0030):** electronically operated, with at least
  750 m of reliable command range; one-fault tolerant, with a removable
  interlock in series with the launch switch, kept by the arming crew; momentary
  dead-man ignition switches.

## Boundary tests

To be done; none has run.

- Comms MCU held in reset, with no loss of flight function.
- Propulsion controller held in reset or failed short, without collapsing the
  flight-computer branch.
- CAN removed, corrupt, bus-off and wrongly terminated.
- Stale, replayed and illegal high-level requests.
- Each source branch browned out, interrupted, shorted where safe, and restored.
- Foinse cold start and continued source delivery with the auxiliary return
  absent, then controlled auxiliary-branch faults.
- Ogma's logic rail failing without unsafe propulsion output.
- Full-rate local evidence and first-fault retention through all of the above.
- Swapping production Ogma and the emulator without adding a CAN node.
- Ogma held in reset with propulsion active.
- Umbilical pulled under load: both branches move to their packs without
  resetting Ogma or propulsion.
- Bus 2 faults (the active board unplugged, held in reset or babbling), with
  this link unaffected; then Croí's shared CAN standby stuck, with both links
  quiet and propulsion in its safe response.

Specify retained evidence separately for host loss, MCU reset and total power
loss.

## Change rule

A pull request may clarify this boundary. It must not quietly change Ogma,
Foinse, propulsion, GSE or recovery authority. A real change needs a decision by
the owning project, updated interface and verification definitions, and matching
updates to current-system truth and the project log in every affected
repository.
