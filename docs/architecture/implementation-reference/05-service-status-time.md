# Preserved reference — not the session reading path

Snapshot retained before the 11 September full-pack rewrite. Detailed component,
pin and calculation evidence follows. Current review status lives in the
[reading pack](../README.md); this snapshot does not authorize implementation.

# 5. Service, status and time

## Job and current review

An operator should be able to distinguish **powered, running the intended
firmware/configuration, healthy, physically armed and externally connected**.
Those are different questions. A green light cannot answer them all.

The [10 September discussion](../2026-09-10-session-review.md#6-operator-interface-and-human-error)
favoured firmware/configuration readback through the existing USB service over
a fragile display. RGB health, independent arm, per-rail, continuity and CAN
indicators were candidates, not a finalized collection of LEDs. Decide what
each indication proves and its reset/stale state before spending GPIOs.

CAN activity can help expose intermittent wiring; it does not prove a fresh,
valid peer response. A supply LED does not prove execution. Continuity does
not prove ignition or mechanical operation. The common current monitor remains
useful on standalone Burrito and need not be duplicated on Churro.

Debug is SWD through the six-contact pattern; alignment holes are not extra
signals. No indicator, display or debug hardware changes are authorized here.

## What is fitted

Both MCUs have independent TC2030-NL-compatible debug patterns, reset access,
boot probes, supply test points and local clocks. Debug reference voltage is
sense-only, not a programmer power input. J4401 USB-C belongs to the comms MCU.

Flight PD7 drives complementary red/green through U9101 SN74LVC1G04.
Low/reset with valid flight power means red/not ready; high means green/profile
checks passed. Comms amber, hardware PWR LED and BZ9001 piezo are separate.

The piezo is CPT-9019S-SMT-TR, externally driven through Q9001 from PD6.
It can produce ground-service tones. It is not a fixed-tone active buzzer.
Flight retains an internal RTC with LSE; acquisition and deadlines use a
higher-resolution monotonic timer. There is no external RTC or backup cell.

## Why keep this set

USB covers normal configuration and log extraction. SWD remains necessary for
breakpoints, recovery and independent processor access. Flat signal pads and
insulated Keystone rail loops provide measurements without package-pin surgery.
Zero-ohm links make named blocks isolatable; they are not arbitrary fuse links.

The simple LEDs and sounder avoid a display bus and fragile LCD. A NeoPixel
would provide colours with fewer GPIOs but introduce a serial device and stale
latched state. It is not selected. Complementary LEDs preserve both colours
after PD10 became servo3.

## The options and the concrete reasons for the choices

| Question | Options explored | Chosen reasoning |
| --- | --- | --- |
| Local status | LCD, addressable RGB, separate LEDs | LEDs plus detailed USB/telemetry reporting avoid a glass/display interface and another serial state machine |
| Red/green after servo3 consumed PD10 | More independent GPIO, multiplexing, complementary drive | One PD7 state drives complementary readiness through an inverter; neither colour independently proves execution |
| Sound | Active fixed-tone buzzer or externally driven piezo | A passive transducer permits the requested startup tones; an active oscillator fixes pitch |
| Mission time | Main oscillator alone, internal RTC/LSE, external RTC/cell | Keep internal RTC/LSE for qualified reset continuity; monotonic high-resolution time for active control; no external clock IC |
| Development hardware | Separate exposed-GPIO evaluation board or instrumented flight board | Existing SWD, rail loops, signal pads and named zero-ohm boundaries support the first full PCBA |

The piezo choice is CPT-9019S-SMT-TR, a 9 × 9 × 1.9 mm external-drive part.
Its specified sound level applies at the stated 4 kHz excitation and distance,
not every tune or a closed bay. Its −30 to +70 °C operating range is an explicit
exception to the preferred wider component grade for a nonessential function.
PD6 is a GPIO allocation, not a promised timer-channel output. Ground chirps
must use bounded execution and stop before calibration/active flight.
[Recorded transducer selection and drive analysis](../../sensing-indication-time-review-2026-09-07.md#indication).

### Timekeeping: short mission drift and reset continuity are different

For a 900-second mission, 20 ppm corresponds to 18 ms and 100 ppm to 90 ms.
Those calculations explain why an external RTC is not automatically needed.
They are not measured oscillator bounds. Initial tolerance, temperature,
load capacitance and ageing all contribute.

The LSE investigation specifically found that a room-temperature crystal
tolerance understated cold drift. Using the retrieved ABS07 temperature
coefficient/turnover bounds, −20 °C could contribute about −100 ppm before
initial tolerance and ageing. The recorded provisional LSE continuity allowance
was therefore 200 ppm: 180 ms over 15 minutes, 5.76 s over eight hours. Active
HSE-based timing has its own budget; do not apply the LSE number to it blindly.
[Timing arithmetic and source qualifications](../../sensing-indication-time-review-2026-09-07.md#time).

The reason to retain the internal RTC/LSE is mainly knowing elapsed age across
a supported processor reset while the backup domain stays powered. It does
not survive complete power loss on the present VBAT connection. A plausible
RTC value must be rejected if retention validity or epoch is unknown. UTC from
GNSS is useful metadata; it must not step flight deadlines.

### Current evidence: why INA228 moved onto Croí

The original plan placed avionics and propulsion current monitors on Foinse.
The later discussion exposed the flaw: standalone Croí should also record its
battery-load response. Moving the avionics INA228/shunt onto the common Croí
entry retained one measurement path and one driver family; duplicating it on
Foinse would add little.

The Rev 1 precedent was ACS71240 Hall sensing, with an analog conversion path.
Hall sensing can avoid an external shunt and offer isolation, but the current
boards deliberately share ground. Reusing INA228 needed no free flight ADC
pin and covered ordinary logic draw as well as actuator increments. The eFuse
IMON output was another lower-part-count option, but would need an ADC/front
end and validated low-current transfer behaviour. IMON remains a bench probe.
[Native-state and Rev 1 evidence](../../sensing-indication-time-review-2026-09-07.md#why-not-simply-use-the-old-sensor-or-the-efuse-imon).

The 5 mΩ shunt adds 30 mV drop and 0.18 W dissipation at 6 A, nominally. It is
also another series failure point. It measures protected battery-load current,
not USB, charging, upstream bias/leakage or all vehicle power. A downstream
capacitor may supply the start of a pulse; monitor loss may hide it entirely.
Keep request, driver state, electrical response and physical outcome distinct.

## What the indications cannot prove

Green means reported readiness, not armed or launch permission. Stuck-high
firmware can leave stale green. PWR indicates voltage, not correct execution.
No LED or buzzer replaces physical arm-state evidence or a detailed fault log.

Mute the piezo before calibration and flight; it must not contaminate inertial
measurements or delay required work. Audible operation inside the closed bay,
at temperature and low pressure is unproved.

HSE drift and RTC retention are separate questions. Internal RTC/LSE avoids
another IC, but loss of its supply loses retention. GNSS UTC must never step
control deadlines or be required for boot. Reset timestamps need valid age and
epoch, not a plausible-looking wall clock.

## Next review

Draw supervisor/watchdog → reset → staging-clear relationships visibly.
Keep reference/clock capacitors beside their actual schematic nodes rather
than in a passive inventory grid.

Verify USB-only identification/configuration/extraction, disconnected or stalled
comms, silent reset defaults, each readiness transition, SWD recovery and all
claimed clock/reset classes. Normal field service must work with the bay
closed; invasive debug or internal harness changes invalidate flight-ready closure.

Evidence: [status/time revision](../../sensing-indication-time-review-2026-09-07.md),
[readiness revision](../../connector-servo-readiness-revision-2026-09-07.md),
[reset contract](../../../interfaces/reset-recovery-contract.md).
