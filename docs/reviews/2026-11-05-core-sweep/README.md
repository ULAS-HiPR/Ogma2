# Core-board sweep, 5 November 2026

Seán and the model go through the whole system, top to tail, up to three
times tonight. The aim is to close Burrito and Churro: made and tested as soon
as possible (agreed with Jay, Anav and Arnav). After the sweep, Seán signs off,
then comes human-readable schematic capture, then the av-bay limits with Jay,
the board outlines, and routing.

## How a pass runs

- One section at a time, in the order below. For each: the diagrams, what's
  decided (with its decision ID), what's open, and the question that closes it.
- Seán asks, explores and decides. Every question and decision goes into
  [log.md](log.md) as it happens, tagged with its section.
- Labels: **Decided** is in `decisions.md`. **Decided tonight** is logged here
  but not yet recorded. **Proposed** and **Open** mean what they say.
- At the end of the evening every decision taken here goes into
  `decisions.md`, `current-system.md`, the chapters, the capture spec and
  `project-log.md` together, in one commit on PR #2, with Seán's go-ahead.
- `diagrams/` holds renders of the docs' own Mermaid, plus
  [system-5nov.mmd](system-5nov.mmd), the one new drawing. The PNGs aren't
  committed (no rendering trees in the repo); `python3 render.py` remakes them.

## Sections, top to tail

### 1. The vehicle and the system

Diagrams: `01-system-5nov` (tonight's state), `01-vehicle` (as recorded),
`01-inside-burrito`.

- **Decided:** one core board, Burrito, with two processors (D-6.12). Churro
  protects and distributes power with no MCU. Fajita runs the engine and
  governs itself. Closed-loop actuators get their own board (D-2Nov.8). The
  CATS Vega is the independent COTS recovery chain (LV-0240, 0250).
- **Decided tonight:** the active board gets its own CAN bus and its own
  Churro branch (log entries 5 and 6).
- **Open:** who owns Fajita (the repo says propulsion; Jay wants Seán and last
  year's people); what the active board drives (canards in the meeting; RCS
  solenoids and grid fins in the repo); LV-0690, one set of electronics or two;
  who buys the CATS Vega.
- Sources: [current-system](../../../current-system.md),
  [system tour](../../architecture/system-tour.md),
  [decisions](../../../decisions.md).

### 2. Churro

Diagrams: `02-churro-power`, `02-churro-temperature`,
`02-source-dependencies`.

- **Decided:** AV (2S) and PROP (6S) feeds, each from its pack or the rail
  umbilical, through ideal diodes and an eFuse each (U1001, U2001), with fuse
  and TVS at the umbilical (D-2Nov.7). Voltage, temperature and PROP current go
  to Burrito over I²C, powered from Burrito's 3.3 V.
- **Decided tonight:** a third branch from the AV source with its own eFuse
  and enable loop, not after U1001, sized for two servos stalling (log 6).
- **Open:** the third branch's eFuse, current limit, connector and enable; the
  AV pack and harness ceiling (3 A today, 5 A pack fuse); the umbilical
  connector and voltages; PROP pack chemistry; PROP current for 24 V solenoids
  and 5 V servos on 6S (2 A continuous, U2001 latches off); U2001's fault mode;
  a wrong pack on J101; the "dumb driver" wording in the LTS boundary copy.
- Sources: [08 Foinse and CAN](../../architecture/08-foinse-can.md),
  [power contract](../../../interfaces/power-contract.md),
  [Churro monitoring](../../architecture/justifications/churro-monitoring.md).

### 3. Burrito power

Diagrams: `03-power-overview`, `03-burrito-battery-to-everything`,
`03-burrito-regulated-domains`.

- **Decided:** Q101 reverse blocking → energy tap (outputs and servos) → U101
  eFuse → TPS2121 battery/USB mux → 4.0 V buck → three LDO domains (D-6.1;
  flight core enabled by source presence, D-6.5). Tap decoupling (D-2Nov.15). Power hold, with PE5's pull-down at
  1 MΩ (D-2Nov.4, D-2Nov.18). Regeneration: DNP bulk footprint, trips stay
  (D-2Nov.17).
- **Open:** the back-drive test; a firing pulse through a long pack harness
  against U101's 6.20 V stop (needs the raceway run length).
- Sources: [02 Power](../../architecture/02-power.md).

### 4. Processors and pins

Diagram: `04-processors`.

- **Decided:** flight STM32H563 and a separate comms MCU on a framed UART; the
  flight MCU finishes the mission with comms held in reset (D-6.12). Pin maps
  checked against CubeMX data (D-2Nov.11).
- **Decided tonight, pins proposed:** FDCAN2 on PB5 (RX) and PA10 (TX); the CAN
  standby moves to PE10 and serves both transceivers; recovery arm sense PC8 →
  PE13; channel-2 low side PA10 → PC8 (still off port E). That uses the last
  two spare flight pins.
- **Open:** confirm the shuffle.
- Sources: [01 Processors](../../architecture/01-mcus.md),
  [flight pinout](../../architecture/proposed-flight-pinout.csv),
  [capture spec](../../architecture/schematic-capture-spec.md).

### 5. Sensors and recording

Diagram: `05-sensors-recording`.

- **Decided:** two low-g IMUs, a high-g accelerometer, two barometers, the
  magnetometer on Burrito (D-2Nov.11), the 256 MiB NOR on the flight MCU
  (recording rules D-6.9). Both confirmed tonight (log 2, 3).
- **Open:** what the magnetometer has to deliver (Radion).
- Sources: [07 Sensors and recording](../../architecture/07-sensors-logging.md).

### 6. Pyro outputs

Diagrams: `06-pyro-outputs`, `06-pyro-one-channel`.

- **Decided:** three channels, two recovery and one staging, one e-match each
  (D-7.1). A high side and its own low side per channel (D-2Nov.1). Separate
  recovery and staging arm switches and fuses; staging latch (D-7.2). Continuity
  legs 3.9 kΩ (D-2Nov.14). One channel fires at a time. Confirmed tonight
  (log 1).
- **Open:** igniters (no owner), which also decides when R6310 / R6410 / R6510
  are fitted; Anav's pyro-channel circuit; pyro over CAN (Jay's ask, answered
  "not for recovery"; close it?); TVS at J6601 and the arm loops; the arm-loop
  length in the all-fire margin.
- Sources: [03 Outputs](../../architecture/03-energetic-outputs.md).

### 7. Servos

Diagram: `07-servos`.

- **Decided:** three event-only servos on one shared 2.0 A switch, ≥220 µF
  bulk plus a DNP footprint (D-6.7, D-2Nov.17).
- **Open:** the servos and their motion profiles; the back-drive test.
- Sources: [04 Servos](../../architecture/04-servos.md).

### 8. Recovery logic

Diagram: `08-recovery-states`.

- **Decided:** pad datum, ground-test mode and pad telemetry (D-2Nov.10,
  D-2Nov.16); the 100 m gate (D-2Nov.13); power-hold rules (D-2Nov.4).
- **Open (Anav):** the rest of D-6.11; writing the in-flight checkpoint first;
  a missed-launch backup; what counts as inertial evidence for the gate;
  recovery parameters with the vehicle lead.
- Sources: [10 Recovery logic](../../architecture/10-recovery-logic.md),
  [firmware interface](../../firmware-interface.md).

### 9. CAN and the boards around Burrito

Diagram: `09-can-today` (as recorded; tonight's two buses are in
`01-system-5nov`).

- **Decided:** CAN carries permissions, mode, slow state and health, never
  anything a loop needs at loop rate (D-2Nov.9).
- **Decided tonight:** two buses, Burrito–Fajita on FDCAN1 and Burrito–active
  board on FDCAN2. Burrito sends the active board Safe / Active / Abort with a
  counter at 10–20 Hz; stale means Safe; Burrito holds the field-adjustable
  dormancy; the board has its own hardware path to neutral (log 4, 5).
- **Open:** CAN connectors (log 7); bus 2's termination, frame contents and
  stale timeout; the third-node row now closes with bus 2.
- Sources: [08 Foinse and CAN](../../architecture/08-foinse-can.md),
  [propulsion boundary](../../../interfaces/ogma-foinse-propulsion-boundary.md).

### 10. GNSS, radio, USB and status

Diagrams: `10-gnss-radio`, `10-service-status-time`.

- **Decided:** the comms MCU runs the MAX-M10S with an external antenna, the
  Wio-LR2021 sub-GHz radio and USB-C. Status is a power lamp, flight red/green,
  comms amber and a ground-only sounder.
- **Open:** the ground radio and a link test before ordering (Arnav); antenna
  placement in the bay.
- Sources: [05](../../architecture/05-service-status-time.md),
  [06](../../architecture/06-gnss-radio.md).

### 11. Connectors, arming and harness

Diagram: `11-connectors-arming`.

- **Decided:** keyed, shrouded, positive-lock connectors from Rev A (AGENTS.md).
  Packs and arm switches go low, with the wiring in a raceway outside the tanks
  (Jay, 2 Nov).
- **Open:** where exactly the packs and switches sit, and the run length; arm
  switch and connector parts; PTFE wiring past the N₂O tank (LV-0500); ESD on
  the harnesses; the active board's enable switch joins the others at the
  bottom.
- Sources: [09 Connectors and arming](../../architecture/09-connectors-arming.md).

### 12. Verification and the first bench

Diagram: `12-verification`.

- **Decided:** release gates and test campaigns (D-2Nov.12).
- **Open:** the order of the first PCBA's block tests; the G0 bench procedure
  (draft in Seán's night-shift handoffs, folder 16).
- Sources: [11 Verification](../../architecture/11-verification.md).

### 13. Capture readiness and what's next

- **Blocks capture:** checked library entries for the new parts (MMC5983MA,
  SN74LVC1G08, LM74700-Q1-class stages and FETs, the fuses, the hold
  capacitor, the Nano-Fit footprint, the DNP bulk can), plus tonight's: the
  second CAN transceiver and connector, and Churro's third branch.
- **Doesn't block:** igniters, fuse and arm-switch parts, the umbilical and
  arm connectors, where the packs and switches sit.
- **Then:** Seán lifts the capture hold; human-readable capture with a page-by
  -page review (Arnav power and connectors, Anav MCU and sensors); the bay
  envelope with Jay (EuRoC is 6 in, which Croí's 80 mm fits; bay length
  open); board outlines; routing.
