# Croí power evidence, indication and time

7 September 2026. Implemented engineering recommendation under Seán's explicit
unattended authority. Anav has not separately reviewed this revision. No hardware
or flight qualification is implied. The 6 September review remains the history;
this note controls these specific changes.

## Recommendation

Put one bulk avionics-current monitor on Croí. Retain separate propulsion-current
monitoring on Foinse. Keep Croí's existing battery-voltage ADC. Use four simple
LEDs and an externally driven piezo sounder. Keep the H563's internal RTC and the
already-drawn 32.768 kHz crystal; add neither an external RTC nor a backup battery.

The same standalone flight computer should produce useful power evidence whether
or not a larger vehicle needs the Foinse companion. This moves a function rather
than multiplying monitors. No MCU pins or interboard contacts change.

## What was already there

- Croí J101 and Samtec J102 both joined `VBAT_CROI_INPUT`. These are electrically
  common, **not an ORing circuit**. Their sources must remain mechanically
  exclusive; no simultaneous packs or live mating is authorised.
- `08-rail-diagnostics` measured protected battery voltage on flight PA0, physical
  pad 23, ADC1_INP0. It also measured flight, recovery and servo rails. Battery
  voltage sensing therefore already worked conceptually in both configurations.
- `09-indicators` had two flight LEDs, one comms LED, a 2N7002 buzzer driver, but
  **no selected/populated transducer**. A driver symbol alone was not a buzzer.
- Flight already had an internal RTC/LSE allocation, an ABS07 crystal and load
  capacitors. MCU VBAT was tied to held flight 3.3 V, not the vehicle battery.
- Foinse had AV and PROP INA228s, an ADS1115 and autonomous source protection.

These are observations from the native schematics/netlists, not assumptions
based on the architecture prose.

## Current measurement: exact boundary

```text
standalone J101 ─┐
                ├─ common input ─ reverse FET ─ Croí eFuse ─ R7101 ─ VBAT_PROTECTED
Foinse J102 ────┘                                             │        ├─ logic mux/buck
       mutually exclusive                              INA228 U7101   └─ future physical
                                                                      arm/actuator feeds
USB ─ reverse-limited USB path ──────────────────────────────── logic mux only

Foinse 2S ─ autonomous protection ─ Croí mate (no AV shunt/INA)
Foinse 6S ─ autonomous protection ─ R2011 + U5001 ─ propulsion
```

R7101 is the proposed **WSLP2512R0050FEA**, 5 mΩ, 1%, 2512. U7101 is
**INA228AIDGSR**, 7-bit address **0x40**. This is a 20-bit converter; its signed
20-bit samples occupy 24-bit registers. The existing Foinse propulsion monitor
remains 0x41 and ADS1115 remains 0x48.

At 6 A the new Croí shunt drops 30 mV and dissipates 0.18 W. At 0.5 A it drops
2.5 mV and dissipates 1.25 mW. These are nominal Ohm's-law calculations. They do
not establish a 6 A continuous board rating or a pulse-survival rating. Check
the actual shunt suffix, land pattern, current crowding, fuse clearing and surge.
No 0603 zero-ohm resistor replaces the removed high-current shunt on Foinse: its
AV output is a direct conductor. The shunt is another series failure point on
standalone Croí; its justified benefit is recorded current evidence. There is
no parallel copper bypass that would defeat the measurement.

Both source inputs pass through the shunt before **all downstream Croí battery
loads**. The future arm assembly must take its source from `VBAT_PROTECTED`,
never a connector-side tap. The arm assembly is still unspecified, the three
armed rails still have no physical source, and R6310/R6410/R6510/R6804 remain
DNP. This revision does not complete or energise those paths.

The monitor excludes upstream protection quiescent/leakage currents, USB power,
propulsion power and the charging harness. It is a protected-load discharge
measurement, not an exact whole-pack coulomb counter. A capacitor downstream
can supply the leading edge of a pulse before battery current rises. Keep
existing per-channel driver-current observations; bulk sensing does not replace
their channel identity or hardware protection.

U7101 VBUS reads **after the reverse FET, before Croí's eFuse** through 100 Ω /
10 nF. The existing PA0 ADC reads **after the shunt**. Label them input voltage
and protected-load voltage, respectively. INA power/energy registers therefore
multiply pre-eFuse voltage by post-eFuse load current: useful source-side load
estimates, not exact delivered-load energy or total pack energy.

U7101 is powered through R7105 from `FOINSE_AUX_3V3` and attaches to the AUX side
of Croí's existing TMUX I²C boundary. `FOINSE_RETURN_EN` now means **enable the
optional power-monitor domain**, even when no Foinse board is installed. Keep
the electrical net/pin name for compatibility; software may use a clearer alias.
There is no new GPIO, regulator or processor. An AUX short/stuck bus can remove
current telemetry, not flight timing or autonomous source protection. Foinse
hot-plugging is not supported. A fault on the external segment can also prevent
reading the local INA; do not promise independent monitor availability.

Positive shunt/VBUS voltage with INA VS absent is allowed by its datasheet;
negative transients, partial rails and differential overload remain explicit
limits. Sensor absence/staleness must never become zero current. AUX loss or a
flight reset creates a measurement gap, possibly during the event of greatest
interest. Preserve that gap in the log.

### Why not simply use the old sensor or the eFuse IMON?

Ogma 1 Foinse's local firmware identifies **ACS71240** Hall sensing and uses
132 mV/A, a 1650 mV zero and eight-sample averaging. Its component library also
contains the ACS71240 family. That proves the design/firmware precedent, not
the installed part's calibration or a newly re-measured waveform. Seán reports
that the current trace helped correlate servo activity with the main-event reset.
No adjacent Ogma 1 files were changed.

Hall sensing avoids an external shunt and can offer isolation. Neither advantage
justifies a second sensing architecture here: these boards intentionally share
ground and carry a bounded 2S AV feed. Moving the already-selected INA228 keeps
one monitor driver family, needs no spare ADC pin, and measures low normal logic
draw as well as actuator increments. Its 85 V capability is unused on Croí, but
reusing the Foinse part/driver is a concrete simplification, not a demand for
space-grade metrology. The INA and shunt still need a priced BOM review.

TPS26630 already exposes IMON at a local probe. Using it would save the INA,
but logging it requires an ADC allocation/front end and characterization of its
transfer accuracy and useful low-current range. Flight has no spare ADC/GPIO
allocation; the optional I²C bus already exists. Keep IMON as a bench cross-check.

### What a current event means

Record four different things: request, driver output, measured electrical
response, and independent physical outcome. A current rise can be a motor
starting, stalling, holding torque, another load changing, or a short. It cannot
establish shaft angle, canard deflection, ignition or successful deployment.
No current rise may mean a disconnected load, an undersampled pulse, charge
supplied by a local capacitor, lost monitoring, or a failed command. Do not
automatically retry an energetic action from this ambiguous evidence.

Start 100 Hz current records. Bounded 500 Hz capture is a diagnostic option,
not a flight requirement or guarantee of resolving short initiator pulses.
Retain faster existing per-channel ADC observations where their validated
front ends support them. Test current evidence first with inert electronic
loads and a measured shunt voltage, not an initiator.

## Indication

Use existing flight green/red status LEDs, existing comms amber LED, and new
hardware green **PWR** LED D9301/R9301. The PWR LED is fed by `FLIGHT_3V3` through
3.3 kΩ. It only says that rail has voltage; it is neither calibrated power-good
nor proof of software readiness. Flight/comms indicators remain independent.
Final LED MPNs/brightness remain BOM items; ordinary 0603 land patterns exist.

No NeoPixel in Rev A. One addressable RGB part can encode more colours, but
colour count is not our limiting information channel. It adds serial timing,
startup/latched-state behaviour and part-specific logic-level checks. A dead
comms MCU must not erase the flight indication, and flight needs no extra
one-wire timing work to replace two already-allocated GPIOs. A nonblocking DMA
implementation is possible; there is no named need to build it now. Distinct
labels and blink patterns remain readable without colour discrimination.

Select **Same Sky CPT-9019S-SMT-TR**, a 9 × 9 × 1.9 mm external-drive piezo.
It is **passive**, deliberately: a normal active buzzer's internal oscillator
sets one pitch. We need controllable tones. It is rated for 3 Vpp excitation at
4 kHz, with 65 dB minimum specified at 10 cm under the stated conditions. Other
pitches are possible but their loudness differs; this is not a broadband speaker.
Its −30 to +70 °C operating rating covers the provisional board envelope, but
does not meet the preferred −40 to +85 °C component grade. Accept that explicit
exception for nonessential indication; it is not a recovery-location guarantee.

The existing PD6/Q9001 drive remains. R9005 = 1 kΩ across the piezo restores its
low terminal when Q9001 opens; D9002 = 1N4148W clamps positive excursion above
the optional rail. With maximum nominal 15.6 nF transducer capacitance, the
return time constant is 15.6 µs versus 125 µs half-period at 4 kHz. At 50% duty
the resistor adds about 1.65 mA from 3.3 V. Transducer waveform, FET drive,
mechanical impulse coupling and sound level still require first-PCBA measurement.

**PD6 is a frozen GPIO, not a promised timer-channel PWM output.** Firmware can
use a bounded timer interrupt to toggle it for ground chirps; no blocking delays,
interrupt masking or free-running sound task in essential flight operation.
Mute before flight acquisition/calibration and through active flight. A qualified
landed mode may use short low-duty beeps. Silence is the default after reset.
No audible output is promised at near vacuum or through a closed noisy bay.
Keep its sound ports clear of glue, wash liquid, coating and the enclosure wall.

## Time

Seán is right about the timescale. An external RTC chip/coin cell is not needed
to keep 15-minute mission time. Retain **what is already present**: H563 internal
RTC, flight ABS07-32.768KHZ-7-T LSE, independent 16 MHz HSE on both MCUs.

For 900 seconds, 20 ppm gives 18 ms error; a provisional total 100 ppm timing
budget gives 90 ms. Neither is a measured board guarantee. Include initial
tolerance, temperature curve, load-capacitance error and ageing. The tuning-fork
crystal's room-temperature tolerance alone is not its full-temperature bound.
At 100 ppm, an eight-hour pad wait could accumulate 2.88 seconds: duration still
matters. Timestamp fast acquisition with a monotonic high-resolution counter,
not a once-per-second calendar read. Map optional GNSS/PPS time onto that clock;
never let a late GNSS time correction step flight deadlines.

Do not apply the illustrative 100 ppm bound to the LSE as a guaranteed limit.
The retrieved ABS07 sheet specifies a temperature coefficient down to
−0.040 ppm/°C² and turnover up to +30 °C. At −20 °C that term alone can be
−100 ppm; adding −20 ppm initial tolerance and −3 ppm first-year ageing gives
−123 ppm before load error. Start with a **200 ppm provisional LSE continuity
allowance** (180 ms per 15 minutes; 5.76 seconds per eight hours), then replace
it with the measured oscillator/error budget. HSE-based active mission timing
has its own independent tolerance budget. Neither number grants event-timing
accuracy without the mission's actual tolerances.

The LSE/RTC earns its small footprint mainly by preserving a time basis across
qualified MCU resets while the backup domain remains powered. HSE/timer uptime
alone restarts on reset. The existing held-flight-3.3 V VBAT connection does not
retain time across complete power loss. Validate reset-class continuity before
using it to age a checkpoint; otherwise mark the epoch discontinuous and follow
the accepted reset contract. LSE failure, GNSS loss or UTC absence must not stall
the essential scheduler. Cold restart is not continuous flight time by inference.

## Observed revision checks and next evidence

Native netlist checks: Croí **2,150 pins / 283 assertions**, Foinse **278 / 91**.
Croí ERC remains four deliberately unpowered-output errors and four warnings;
Foinse ERC remains zero. Both 100-pad MCU CSVs are unchanged. Native saved-board
checks validate 2,219 Croí pads and 338 Foinse pads, including repeated connector
tails, local model paths and schematic identity. Existing footprints were not
moved; 14 Croí additions are staged outside the outline. Croí has 624 footprints,
95 staged; Foinse has 100, all inside. These are still unrouted layouts with
documented DRC/library/rating gaps, not manufacturing-ready boards.

Nine obsolete Foinse components were removed from active schematic/PCB; the
complete prior boards are recoverable in
`../../schematic-work-2026-09-07/sensing-status.KvNwHP/{croi2,foinse2}-before/`.
Nano-Fit exact footprints and the hold capacitor's exact selection remain open.
The new buzzer footprint is manufacturer-drawing-derived; no exact 3D model was
invented. See the layout pack for its original dimensioned page.

On the first full PCBA: verify both exclusive source modes, no unmeasured branch
bypass, shunt polarity/gain, current steps and timestamp latency, AUX off/stuck
bus behaviour, voltage ADC calibration, buzzer waveform/noise and all supported
RTC reset classes. Use current-limited supplies and inert loads. No coupon order,
live firing, charging experiment or flight is authorised by this revision.

## Sources

- Live Croí/Foinse schematics, native XML exports and check reports under
  [hardware](../hardware/README.md).
- [INA228 datasheet](https://www.ti.com/lit/ds/symlink/ina228.pdf), especially
  power-off input limits, calibration/register format and Kelvin layout.
- [WSLP resistor family](https://www.vishay.com/docs/30122/wslp.pdf).
- [CPT-9019S-SMT-TR](https://www.sameskydevices.com/product/resource/cpt-9019s-smt-tr.pdf),
  11 September 2024, pages 1–2; locally retrieved and visually inspected.
- [STM32H5 hardware guidance](https://www.st.com/resource/en/application_note/an5711-getting-started-with-stm32h5-mcu-hardware-development-stmicroelectronics.pdf)
  and [ABS07](https://abracon.com/Resonators/ABS07.pdf).
- Ogma 1: `../../../ogma/foinse/firmware/src/main.cpp`, ACS71240 constants and
  `../../../ogma/foinse/hardware/Lib/ACS71240LLCBTR020U5.kicad_sym`.

The component sources support their stated characteristics. Placement, sampling
policy and the revision choice are engineering judgments, awaiting the checks
above. Raw source downloads remain outside the tracked umbrella.
