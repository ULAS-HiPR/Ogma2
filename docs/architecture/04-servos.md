# 04 Servos

Two servo outputs driven straight from flight TIM3 (PC6, PC7), powered from the
battery through their own fuse and a 2.0 A switch. The CAD still has three
channels; the third goes at capture and its pin, PD10, becomes the service
power enable.

```mermaid
flowchart TB
  T["ENERGY_TAP"] --> FU["F6801 servo fuse
not behind the pyro arm"]
  FU --> W["U6802 TPS1H100
≈2.0 A limit"]
  W --> L["U6803 TPS70933
3.3 V for the buffer only"]
  F["Flight MCU
PC6 / PC7 · TIM3"] -->|"2 × PWM"| B["U6804 TXU0304
off-state signal boundary"]
  L --> B
  B -->|"PWM1 / PWM2"| J["J6602 · Micro-Fit
430451000, 10 contacts"]
  W -->|"SERVO_VBAT · ≥220 µF"| J
```

| Item | Choice | Why |
| --- | --- | --- |
| Command | Direct TIM3 PWM on PC6/PC7 | Already mapped; no extra controller or bus |
| Signal boundary | U6804 TXU0304 | Stops back-powering when either side is off |
| Power | Raw 2S through F6801 and U6802 | No new regulator. R6802 1.24 kΩ sets ≈1.989 A; 1.5 A combined normal allocation |
| Bulk | ≥220 µF on SERVO_VBAT at J6602 | Stall and regeneration transients; regen returns to the battery through the fuse (D-6.7) |
| Arm | Not behind the pyro arm | Servos can be checked on the pad with outputs safe (D-6.1) |
| Connector | Keep J6602 430451000, mate 430251000 | Different contact count from the output harness J6601 |

Pins: 1/2/3 = PWR1/PWM1/GND1, 4/5/6 = PWR2/PWM2/GND2, 7–10 unwired. Crimp
candidate 430300007, matched to wire size. A six-contact connector was
considered and dropped: it would mate with J6601.

## Limits

- Servos must take 8.4 V on a full pack and a 3.3 V command.
- One fault can take out both channels; they share U6802.
- Don't raise the limit for an unspecified load. A servo needing more current
  or another voltage needs its own interface change.
- Qualify the actual mechanism for current, regeneration, response and
  temperature. Back-drive it on the bench and scope the battery side.
- PC6 and PC7 share TIM3's period. Bring up on an inert load; a mid-range
  pulse is not a proven safe position.

## Remote actuation

No remote actuator node. Fajita keeps its own local control. A future remote
mechanism must justify where its feedback lives and how commands expire. The
earlier 200 Hz / 13.3% CAN load example is a comparison, not a requirement.
End-to-end timing includes sensing, computation, queueing, PWM phase and the
mechanism, not only CAN wire time.

## Capture

Remove R6606/R6607 and the channel-3 branches to J6602.7/.8/.9; leave contacts
7–10 unconnected. Tie U6804.4 (A3) to GND and leave U6804.11 (B3Y) unconnected;
keep the existing fourth-channel terminations. Add F6801 and the bulk capacitor;
fit R6804. [Capture delta](schematic-capture-spec.md#burrito-changes).

Background: [interface reasoning](justifications/interfaces-and-installation.md#two-local-pwm-interfaces-no-speculative-remote-node) ·
[timer choice](../archive/architecture/implementation-reference/04-servos.md#why-direct-timers) ·
[CAN and stall study](../archive/architecture/2026-09-18-review-investigations.md#4-can-fd-and-servo-investigation) ·
[harness record](../archive/connector-servo-readiness-revision-2026-09-07.md#j6602-servo-harness-new-ten-contact-connector)
