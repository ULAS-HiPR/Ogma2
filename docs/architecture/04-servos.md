# Two local servo interfaces

**22 September · proposal, servo feed amended by [D-6.1, D-6.7](../../decisions.md) · CAD still has three channels.**

Use **PC6/PC7, TIM3**, through the existing **TXU0304PWR** powered-off signal
boundary. Two channels match the review direction; no PWM expander is needed.
Reallocate PD10 from the third channel to service power enable. Select a raw-2S,
3.3 V PWM interface with a combined 1.5 A motor allocation; compatible actuators
are an installation choice within that envelope.

## Justification and deeper detail

| Question | Follow through | Source status |
| --- | --- | --- |
| What is the actual capture baseline? | [Bounded PWM/power interface and local-control decision](justifications/interfaces-and-installation.md#two-local-pwm-interfaces-no-speculative-remote-node) | Current recommendation; electrical interface chosen, mechanism qualification separate |
| Why direct PWM and a buffer? | [Timer choice and interface alternatives](../archive/architecture/implementation-reference/04-servos.md#why-direct-timers) | Earlier circuit reasoning; current target is two channels |
| What determines remote control and supply? | [CAN FD, latency and stall investigation](../archive/architecture/2026-09-18-review-investigations.md#4-can-fd-and-servo-investigation) | Numerical examples; control split remains open |
| Which harness is retained? | [Connector revision and mating parts](../archive/connector-servo-readiness-revision-2026-09-07.md#j6602-servo-harness-new-ten-contact-connector) | Preserved three-channel harness; current two-group proposal below |

```mermaid
flowchart LR
  F["Flight H563VIT6
PC6 / PC7 · TIM3"] -->|"two PWM signals"| B["TXU0304PWR
U6804 · partial-power boundary"]
  B -->|"PWM1 / PWM2"| J["Retain J6602
Molex 430451000 · 10 contacts"]
  V["ENERGY_TAP → F6801 servo fuse
not behind the pyro arm"] --> W["TPS1H100BQPWPRQ1
U6802 · common switch / limit"]
  W -->|"servo energy"| J
  W --> L["TPS70933DBVR · U6803
3.3 V for buffer side only"]
  L --> B
```

| Item | Proposed choice | Reason / limit |
| --- | --- | --- |
| Commands | Direct TIM3 PWM | Two channels already mapped; no extra controller or bus |
| Signal boundary | Retain TXU0304PWR | Limits parasitic powering with either domain off; verify ramps |
| Connector | Retain 430451000, ten-contact Micro-Fit | Existing harness; different contact count from J6601; no new connector family |
| Power switching | Retain TPS1H100BQPWPRQ1, R6802 1.24 kΩ 1% | ~1.989 A nominal limit; 1.5 A combined normal allocation |
| Buffer supply | Retain TPS70933DBVR | Powers logic interface only; **does not regulate motor power** |

**Two-channel harness proposal:** retain J6602 430451000 and mating
430251000. Keep contacts 1/2/3 = PWR1/PWM1/GND1, 4/5/6 = PWR2/PWM2/GND2.
Leave 7–10 unwired in the proposed harness; existing CAD still routes channel 3.
Retain the wire-size-dependent 430300007 crimp candidate. Releasing PD10 and
removing channel-3 wiring require the later CAD/harness revision.

The earlier six-contact proposal is withdrawn: it would use the same connector
as the output harness. Saving four cavities does not justify introducing that
mis-mating opportunity and another harness change.

## Supply decision

**Raw 2S, through the existing common switch; no new regulator.** Compatible
actuators must accept the installed source range including 8.4 V fully charged
and 3.3 V command levels. Combined normal motor allocation: **1.5 A**.
R6802 1.24 kΩ 1% sets ~1.989 A nominal limit; the source-derived overload bounds
and their limitations are in the [justification](justifications/interfaces-and-installation.md#two-local-pwm-interfaces-no-speculative-remote-node).
Servo energy now comes from `ENERGY_TAP`, before U101's switch, through its own
≈4 A fuse F6801; R6804 is fitted. It is not behind the pyro arm, so servos can
be checked on the pad with the outputs safe. Add ≥220 µF on SERVO_VBAT at J6602:
regeneration returns to the battery through the fuse instead of into the logic
input (D-6.7).

One fault can remove both motor channels. A different voltage, higher stall/start
current or unacceptable shared failure needs a separate interface revision.
Do not enlarge the limiter to accommodate an unspecified load. Qualification
measures the chosen mechanism's current, regeneration, response and temperature.
That does not prevent capturing this bounded electrical interface.

## Remote actuation

**Baseline: two local PWM outputs; no new remote actuator node.** Fajita keeps
its independent local control. A future remote mechanism must justify its own
feedback location and command-age/expiry contract. The earlier 200 Hz / 13.3%
CAN example remains a comparison, not a requirement to add that node.

PC6/PC7 share TIM3's period. The mechanism profile supplies compatible pulse
limits/rate. Bring up signals on an inert receiver/load; an arbitrary middle
pulse is not an established safe position. End-to-end timing includes sensing,
computation, queueing, PWM phase and mechanical response, not just CAN wire time.

## Schematic handoff

Keep J6602 430451000 and housing 430251000; contacts 1/2/3 and 4/5/6 are
PWR/PWM/GND. Remove R6606/R6607 and the channel-3 branches to J6602.7/.8/.9;
leave contacts 7–10 unconnected. Tie U6804.4 (A3) to GND and leave U6804.11
(B3Y) NC; retain the existing unused fourth-channel terminations. The first two
channels retain powered-off boundaries and off defaults. PD10 becomes
SERVICE_POWER_EN in the [proposed map](proposed-flight-pinout.csv).

This closes the board interface. It does not select or qualify a vehicle
mechanism. Back-drive the chosen servo on the bench and scope the battery side
before flight. [Capture delta](schematic-capture-spec.md#burrito-capture-delta).
