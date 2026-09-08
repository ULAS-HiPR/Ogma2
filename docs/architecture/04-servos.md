# 4. Three servo channels

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

Evidence: [third-servo revision](../connector-servo-readiness-revision-2026-09-07.md),
[firmware handoff](../firmware-handoff-2026-09-07.md).
