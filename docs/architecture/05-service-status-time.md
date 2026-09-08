# 5. Service, status and time

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

Evidence: [status/time revision](../sensing-indication-time-review-2026-09-07.md),
[readiness revision](../connector-servo-readiness-revision-2026-09-07.md),
[reset contract](../../interfaces/reset-recovery-contract.md).
