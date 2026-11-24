# Ogma 2: mechanisms and behaviours

**21 November 2026, after D-21Nov.1–D-21Nov.9.** Mechanisms and behaviours only, no part numbers. Each line traces to [Burrito's](../requirements/burrito.md) or [Churro's](../requirements/churro.md) requirements. Tick or strike each line; a strike becomes a decision row.

Tags:

| Tag | Meaning |
| --- | --- |
| **D** | Decided on main |
| **P** | Proposed |
| **?** | Open |

---

## 0. The pieces

```
EuRoC vehicle, bottom to top (Jay, Fri):

  engine │ tanks + COPVs │ valve bay │ grid-fin + RCS module │ AV-BAY │ recovery │ nose + payload
                                                                 │
  ACCESS PANEL ── lowest ~1.8 m, opposite the rail ──── harness up through the tank downcomer

AV-BAY
  ┌──────────────┐ edge mate ┌──────────────┐
  │   BURRITO    │═══════════│    CHURRO    │   power: sources, protection, charging, actuator feeds
  │ flight comp. │           └──────────────┘
  └──┬───────┬───┘
     │CAN 1  │CAN 2
     ▼       ▼
  FAJITA   SALSA         CATS VEGA: COTS recovery, own cell, own switch, own e-matches
  (where?) (below/at bay)
```

---

## 1. Power

```
 UMBILICAL ─┬─ AV pair ─────[protect + damp]──[one-way]──┐
            │                                             ├──[AV branch: UV/OV/limit, held on in flight]──► BURRITO
 AV PACK 2S ─────────────────────────────────[one-way]──┘          (logic + pyro energy)
            │
            ├─ ACT pair ────[protect + damp]──[one-way]──┐
 ACT PACK 6S ────────────────────────────────[one-way]──┼──[PROP branch: limit, enable]──────────► FAJITA
            │                                             └──[ACT branch: limit, enable, ARM KEY]─► SALSA
            │
            └─ CHARGE pair ──► one charger per pack (CC/CV, temperature-gated) ──► AV, ACT, CATS cell
 USB (service) ──► Burrito logic only
```

| # | Behaviour | Tag |
| --- | --- | --- |
| P1 | On the rail the umbilical carries every load; the packs only top up | D |
| P2 | Pulled at Go, each feed hands to its pack with no dropout, and Burrito doesn't reset | D |
| P3 | Current reaches a pack from the umbilical only through its charger | D (D-21Nov.2) |
| P4 | Packs charge until Go; a hot pack doesn't charge | D (D-21Nov.2) |
| P5 | A short on any branch trips that branch only | D (D-21Nov.1) |
| P6 | Churro powers all actuation (Salsa and Fajita) | D (D-21Nov.1) |
| P6a | The drive voltage is set at the load; Churro sets the limit, enable and arm per group | D (D-21Nov.1); ratings open |
| P7 | Burrito holds AV on through any in-flight reset (RC ≥0.75 s; firmware re-asserts within 50 ms) | D |
| P8 | Logic runs in three protected domains (flight, comms, services); a services fault never drops flight | D |
| P9 | One shorted sensor can't pull down the flight rail | D |
| P10 | USB runs logic only, ≤387 mA; never outputs, never charging | D |
| P11 | Pad mode ≤150 mA; the AV pack alone covers 6 h plus the flight | D |
| P12 | Repeated hot-plugging of the umbilical can't overvolt anything | D (D-21Nov.3); test open |
| P13 | Burrito reads every pack (pack side), each branch's current and voltage, both NTCs and each charger's state, all over I²C4; Churro adds no pins | D for the interface (B-36, interface rules); PROP pack side, ACT, CATS cell and charge state open (C-15, C-17, C-22, C-23) |
| P14 | Actuator return current stays off Burrito, even with an actuator return broken | D (D-21Nov.11, B-39); values on the bench |

---

## 2. Energetics

```
 AV pack ─► energy tap (ahead of logic protection)
              ├─► fuse ─► RECOVERY ARM (panel) ─► armed rail ─► [high side ─ e-match ─ low side] ch 1, ch 2
              └─► fuse ─► STAGING ARM (panel) ──► armed rail ─► [reset latch AND fire] ─► [high ─ e-match ─ low] ch 3
 fire pins and low-side selects: flight MCU only, on different ports
```

| # | Behaviour | Tag |
| --- | --- | --- |
| E1 | Nothing fires with the arm open | D |
| E2 | A fire needs both switches of a channel, driven from different ports, so one bad write can't fire | D |
| E3 | Continuity is checked before arming, with test current under a tenth of no-fire; a leaking high side is never fired | D |
| E4 | One channel at a time, current-limited to ≈2 A | D |
| E5 | Staging is inhibited after any reset or power-up until cleared on the ground with staging disarmed | D |
| E6 | Nothing deploys below 100 m above the pad datum | D |
| E7 | The drogue fires at or near apogee, never on the transonic spike (Mach lockout) | ? (lockouts proposed) |
| E8 | Main at or below 450 m AGL at EuRoC | D |
| E9 | The CATS Vega fires its own e-matches from its own cell; nothing of ours sits in its firing path | D |
| E10 | Arming beeps at the panel; arm, continuity and latch state go out in the pad telemetry | D |
| E11 | All-fire is met at minimum battery through the real panel harness (the arm switch is in the firing loop) | D (D-21Nov.5); test open |
| E12 | Ground-test mode drives recovery from simulated pressure; it stays until the configurator ends it, and the lamp, sounder and every frame show it (G1) | D (D-24Nov.18) |

---

## 3. Authority

```
 FLIGHT MCU ── only it ───────────────────────────► pyro channels, staging
 FLIGHT MCU ── CAN 2: Safe / Active / Abort, 10–20 Hz ─► SALSA ─► actuators (neutral unless fresh Active)
 FLIGHT MCU ── CAN 1: requests, permissions ────────► FAJITA (governs itself; may refuse)
 FAJITA ── own CAN link ──► E-REG (pressure loop; Fajita can always vent)
 COMMS MCU ── radio · GNSS · USB ── no path to any output
 GROUND ── radio ─► comms MCU ── framed UART ─► flight MCU (requests only)
```

| # | Behaviour | Tag |
| --- | --- | --- |
| A1 | Only the flight MCU commands pyro and staging; radio, USB and CAN can't | D |
| A2 | Salsa moves only on a fresh Active. Stale or missing means Safe (neutral); Abort means neutral until power-cycled on the ground | D |
| A3 | Burrito sends Active only after the field-adjustable dormancy (EuRoC: ≥1500 m AGL with no flight history) | D |
| A4 | The phases in which Burrito grants Active: ascent after dormancy (RCS), under drogue (grid fins steering back) | ? no table yet |
| A5 | Fajita keeps its own safe response with Burrito in reset, CAN dead, or the operator link lost | D |
| A5a | The e-reg runs the pressure loop on its own board and link; Fajita's overpressure protection doesn't depend on it | D (D-21Nov.10); PTs and link open |
| A6 | An unpowered actuator sits neutral (mechanical centring); IREC 7.3, EuRoC LV-0670 | D (D-21Nov.7); mechanism open |
| A7 | No firmware over CAN; each board is flashed through its own USB | D |
| A7a | The USB ports sit at the av-bay, Burrito's extended to the panel; nothing is flashed on the rail: the running firmware's USB writes settings only, and flashing needs the av-bay open | D (D-21Nov.4, D-24Nov.18) |

---

## 4. Sensing and decisions (Burrito)

```
 2 IMUs + high-g ─┐
 2 barometers ────┼─► estimator (200 Hz) ─► flight states ─► outputs · authority · telemetry
 magnetometer ────┘   essential loop 1 kHz   PAD → BOOST → COAST → APOGEE → DROGUE → MAIN → LANDED
 GNSS (comms) ─────► position for recovery and telemetry
```

| # | Behaviour | Tag |
| --- | --- | --- |
| S1 | Pad datum tracked on the pad and frozen at launch detect; a reset never creates one | D |
| S2 | Launch detect writes the in-flight checkpoint first; PAD catches a missed launch | D |
| S3 | After an in-flight reset, recovery resumes from the checkpoint and staging stays inhibited | D |
| S4 | The watchdog is fed only by real progress | D |
| S5 | A failed sensor is given up and its pins parked; invalid data never becomes valid | D |
| S6 | The flight completes with the comms MCU held in reset | D |
| S7 | Measures to ±30 g and ±2000 °/s without clipping | D (OG-04) |
| S8 | MCU, IMU and barometer temperatures are logged; pad telemetry warns when hot (LV-0510) | D (B-30) |
| S9 | The magnetometer serves the hopper and heading; it never gates the watchdog | D |

---

## 5. Records and links

| # | Behaviour | Tag |
| --- | --- | --- |
| R1 | Full rate from launch detect to LANDED plus a tail, with pre-trigger; append-only; a recording failure never takes control | D |
| R2 | Telemetry is never the only record | D |
| R3 | 1 Hz pad telemetry: arm, continuity, latch, live source, pack voltage | D |
| R4 | The radio stays silent in the pit until authorised, changes channel quickly, and stays out of COTS tracker bands at IREC | ? (B-27; mechanism P) |
| R5 | Flight data comes out over USB after landing, without site power | D |
| R6 | The official altitude comes from the CATS Vega (EuRoC; IREC's COTS altimeter) | D |
| R7 | IREC: a Primary COTS GPS tracker per section, independently switched | ? |

---

## 6. Physical

| # | Behaviour | Tag |
| --- | --- | --- |
| H1 | Every board is 80 mm wide; Burrito stays 80 × 230 | D (D-21Nov.6) |
| H2 | Burrito and Churro mate edge to edge; separate supports carry the load | D |
| H3 | Ériú's av-bay grows from 321 mm to about 400–420 mm, or the sled goes two-sided | D (D-21Nov.6); Jay's answer open |
| H4 | Every pad-touched item sits on one panel, low and opposite the rail | D (D-21Nov.5) |
| H5 | Harness through the tank downcomer is PTFE, with a connector at every joint it crosses | D (LV-0500), ? route |
| H6 | Connectors are keyed and locking; the arm plugs can't cross-mate; everything passes the tug test | D |
| H7 | Canard leads cross a separation joint through a breakaway | D (D-21Nov.7) |
| H8 | Antennas sit behind a ≥356 mm RF window at EuRoC, or go outside the skin | ? |
| H9 | Bays are vented with 3–5 mm holes, placed for low barometer error | ? |

---

## 7. The EuRoC flight, board by board

```
 INTEGRATION   flash over USB · balance packs off the vehicle · bay mockup checks
 ON THE RAIL   umbilical powers all · chargers top up · Burrito in PAD mode · datum tracked · 1 Hz telemetry
 ARM           at the panel: recovery arm · staging arm (if used) · Salsa arm key · CATS switch · enables · beeps confirm
 FILL          Fajita runs the valves · Burrito relays requests and monitors · still charging
 GO            umbilical pulls · each feed hands to its pack · charging stops
 BOOST         launch detect → checkpoint → full-rate log · power hold on · Salsa Safe (dormant)
 COAST         dormancy ends (≥1500 m AGL) → Active → RCS roll control
 APOGEE        drogue: Burrito ch 1 and the CATS, independently
 UNDER DROGUE  grid fins steer back and damp roll (EuRoC plan) · Active granted?  [?]
 MAIN          ≤450 m AGL: Burrito ch 2 and the CATS
 LANDED        Salsa Safe · power hold released after a delay · GNSS position for recovery
```

## 8. How IREC differs

```
 no Fajita, no propulsion control · SRAD solid O motor · ESRA launch control
 Salsa drives the nose canards (roll) · leads cross a breakaway · no dormancy rule · neutral on power loss
 Primary COTS GPS tracker per section · SRAD radio rules · proof-of-function flight before June
 bay: Ø104 inside the sheath, 321 mm today
```
