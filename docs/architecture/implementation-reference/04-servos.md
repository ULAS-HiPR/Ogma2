# Preserved reference — not the session reading path

Snapshot retained before the 11 September full-pack rewrite. Detailed component,
pin and calculation evidence follows. Current review status lives in the
[reading pack](../README.md); this snapshot does not authorize implementation.

# 4. Servo outputs and remote actuation

## Job and current review

Turn an intended actuator position into a local electrical command, with a
defined response to lost commands, reset and power faults. The signal buffer
keeps a powered MCU signal from parasitically feeding an unpowered output
domain; its part number does not explain that job by itself.

**Three local channels is the preserved CAD allocation, now under review.**
List actual nearby functions before retaining all three. Distant fins/canards
may need a remote node. Compare central estimation/control with a local output
node against locally autonomous sensing/control. No measured CAN timing or
stability result settled this in the room. Neutral on silence is a suggestion,
not a universally safe fin state.

The possible regulated servo supply belongs in the Churro/vehicle power review;
no voltage or converter was chosen. Neither 2 A nor raw 2S is qualification for
an unspecified actuator. No channel, pin, connector or power component changes
follow from this discussion.
[Options and evidence required](../2026-09-10-session-review.md#2-servo-count-remote-actuation-and-can-genuinely-reopened).

## Circuit

PC6/PC7 drive servo 1/2 from TIM3. PD10 drives servo 3 from LPTIM2_CH2 AF3.
The existing TXU0304 U6804 carries three PWM signals across the powered-off
boundary. Series resistors and output pull-downs complete the external signals.

U6802 TPS1H100 switches their common raw battery-derived supply. U6803 TPS709
powers only the servo-side signal buffer; it is not a servo regulator.
R6804 remains the DNP energy link.

J6602 is Micro-Fit 430451000. This completely replaces the old eight-contact
harness pinout:

| Servo | Power | PWM | Ground |
| --- | --- | --- | --- |
| 1 | 1 | 2 | 3 |
| 2 | 4 | 5 | 6 |
| 3 | 7 | 8 | 9 |

Contact 10 is NC. The common nominal 2 A limit is provisional, not a
three-grid-fin load qualification.

## Why direct timers

Three independent commanded outputs do not need a PCA9685. MCU timers remove
an extra bus device, driver and output-enable dependency. The downside is
explicit timer allocation and waveform validation. Servo3 uses a different
timer: do not assume it starts in phase with channels 1/2.

A separate regulated servo rail could support lower-voltage actuators, but adds
conversion and fault behaviour. The current baseline uses compatible HV servos
on the battery-derived rail. Exact actuators decide whether that remains valid;
no mechanism is qualified by a connector or PWM waveform alone.

## What the earlier alternatives would change

| Option | Benefit | Tradeoff |
| --- | --- | --- |
| Direct MCU timer channels, selected | No extra PWM controller or command bus | Requires exact timer/pin allocation and safe start/stop behaviour |
| PCA9685-class PWM expander | Many channels with few MCU pins | Adds I²C, another stateful device and output-disable/reset questions; unnecessary for three channels |
| Raw 2S HV-compatible servos, selected baseline | No large servo converter; short energy path | Every actuator must tolerate full charged voltage and low-pack operation |
| Regulated servo rail | Supports a different actuator voltage envelope | Adds conversion loss, heat, peak-current and regeneration behaviour to qualify |
| Separate switch/protection per servo | Could contain one stalled actuator more locally | More parts and current/return paths; not what the current common rail implements |

The third channel was a bounded change: PD10 became LPTIM2_CH2, the existing
buffer's spare forward channel was used, and J6602 became ten-contact Micro-Fit.
The supply was not tripled and its nominal 2 A limit did not become a measured
grid-fin budget. The hardware changes establish three command interfaces;
they do not establish simultaneous loaded performance.
[Exact accepted revision](../../connector-servo-readiness-revision-2026-09-07.md).

### What must come from the mechanism rather than the board drawing

An actuator choice supplies the valid voltage band, input logic threshold,
update rate, endpoint limits, stall current and permitted transient behaviour.
The grid-fin mechanism adds inertia, aerodynamic load, gearing and required
position response. A no-load servo demonstration answers almost none of that.
The first loaded tests must distinguish normal travel, stall, reconnect and
energy returned during deceleration.

The 2 A setting is a provisional protection allocation, not a desirable servo
operating point. Raising it without checking the complete source, interboard
contact, switch, copper and return merely moves the limiting element. A supply
converter may become justified by the chosen actuators; it is not installed
speculatively before that choice exists.

The low-side buffer supply disappearing must not turn an MCU PWM output into
a parasitic power feed. That is why the signal boundary and local pull-downs
remain even though direct timers are simple. Firmware still needs a defined
loss-of-command response and reset default; hardware alone cannot choose the
mechanically safe fin position.

## What fails together

All three servos share a switch, source and return. One stalled actuator may
limit or collapse the common rail. The buffer boundary must prevent powered
PWM from feeding an unpowered servo rail. Motor regeneration and cable
transients can also move energy toward the board.

A PWM command records intent. Bulk current records electrical response.
Neither establishes actual fin angle or successful deployment. Add witnessed
position/end-state evidence when the mechanism's qualification claim needs it.

## Next review

Choose the actual voltage range, peak/stall currents, permitted PWM voltage,
endpoints, update rate, safe position and loss-of-command response. Decide the
physical servo-energy break in the installed arm assembly. Verify switch
limiting, reset/off defaults, regeneration clamp and all three loaded channels.
Do not populate R6804 just to make an early demo move.

Evidence: [third-servo revision](../../connector-servo-readiness-revision-2026-09-07.md),
[firmware handoff](../../firmware-handoff-2026-09-07.md).
