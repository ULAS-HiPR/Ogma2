# Height estimation above 80 km

7 September 2026. Exploratory study requested by Seán. **Nothing here is a new
requirement, parts selection or approval to alter Croí.**

## Judgment

For credible absolute height through a short 100 km sortie, the most promising
route is a receiver explicitly supported for the actual flight dynamics and
altitude, a suitable installed antenna system, and inertial propagation through
outages. Independent tracking or post-flight reconstruction can corroborate the
result. Buying a newer consumer GNSS receiver or integrating another low-g
accelerometer does not close this problem.

This is minutes of high-dynamic suborbital flight, not years in orbit. COTS
hardware is worth considering. Antenna visibility, receiver behaviour, timing,
power continuity and the evidence supporting the estimate are likely to dominate
this navigation decision. There is no reason here to require radiation-hardened
GNSS, an atomic clock or a premium inertial unit on every competition Croí.

The [accepted system](../../current-system.md) already puts Kármán recovery,
actuation and full-envelope altitude proof at vehicle level. Ordinary Croí has
unpowered/DNP outputs in that configuration. This study preserves that boundary.

## 1. First distinguish three different jobs

| Job | What must be available | What is insufficient |
| --- | --- | --- |
| Onboard real-time navigation | Timely height/velocity with validity and bounded uncertainty | A correct result recovered after landing |
| Live telemetry | A useful estimate plus a functioning link, age and quality indicators | Repeating the last fix as if current |
| Evidence of maximum height | Traceable height reference, calibrated observations and defensible uncertainty around apogee | A single screen value or a model constrained to reach 100 km |

“Accurate” remains unspecified. Ten metres, one hundred metres and merely
showing that the vehicle crossed a threshold are different jobs. No tolerance
is selected here. An illustrative ±100 m objective could tolerate errors that
would be unacceptable for ±10 m; neither is a promised capability.

Also define the height reference. GNSS ellipsoid height, height above mean sea
level/geoid, and height above the launch site differ. The usual relation is
`H = h − N`: orthometric height, ellipsoid height and geoid separation. Use a
documented model/datum applicable to the launch region, not an arbitrary US
geoid model. Survey the pad and record antenna offsets. A threshold claim
needs the reference accepted by whoever evaluates it. [NOAA explanation](https://www.ngs.noaa.gov/GEOID/geoid_def.html).

For a trajectory spanning considerable downrange distance, do not treat one
flat local vertical or the pad's geoid offset as exact everywhere. Keep the
underlying position coordinates and transformation metadata in the record.

## 2. Why 80 km appears here

SAM-M10Q's documented operational limits are 80,000 m, 500 m/s and ≤4 g with
the airborne-4g platform assumption. Those are supported-operation limits, not
a promise of a particular shutdown/recovery sequence. We have not established
that the retail module will keep producing valid measurements outside them.
[u-blox datasheet, p. 4](https://content.u-blox.com/sites/default/files/documents/SAM-M10Q_DataSheet_UBX-22013293.pdf).

80 km is not the physical end of GNSS visibility. At these heights the vehicle
is still far below the navigation satellites. Receiver restrictions, tracking
dynamics and the installed RF environment are the relevant obstacles. Discuss
the exact product and supported configuration with its vendor; do not build a
mission around folklore about combinations of altitude/speed limits or bypasses.

The [workhorse GNSS comparison](avionics-options-review-2026-09-07.md#2-gnss-retain-the-clean-workhorse-integration)
shows why a newer u-blox generation is not automatically a solution.

### The missing-fix interval may start during boost

A calculation was run for a deliberately simple example: radial unpowered
coast, spherical nonrotating Earth, inverse-square gravity, no drag, ending at
100 km. It is not a proposed HiPR trajectory.

| Result | Calculated value |
| --- | ---: |
| Upward velocity at 80 km | 617.6 m/s |
| Time from 80 km to apogee | 64.84 s |
| Total time above 80 km | 129.67 s |
| Height at which speed falls to 500 m/s during ascent | 86.88 km |
| Gravity at 100 km in this model | 9.506 m/s² |

The entire portion above 80 km is outside SAM's altitude specification. At the
80 km crossing it is also outside the quoted speed specification. Boost can
exceed the acceleration and speed envelope much earlier. Thus **“bridge only
80–100 km using the last good fix at 80 km” is not a defensible assumption**.
The last usable position and velocity may come from substantially earlier.

The same initial 80 km state propagated with constant sea-level gravity predicts
an apogee about **553 m too low** in this idealised example. That is model error
before any sensor error. A serious estimator needs an appropriate gravity and
coordinate model; it does not need an elaborate atmospheric simulation where
the environment contributes negligible specific force.

## 3. There is relevant flight evidence

DLR's MAPHEUS-15 flight on 11 November 2024 reached 309 km. A 2026 paper reports
tests of Septentrio AsteRx-m3 Pro+ and mosaic-X5 receivers using multi-frequency
antennas and simulator-tuned tracking loops. The detailed mosaic-X5 results
include an initial 4.5-second outage and a later 77.4-second reentry outage,
despite navigation through apogee. Antenna coverage and tumbling mattered.

This is useful evidence for a COTS route. It is not a purchase specification,
a universal accuracy bound or evidence that any stock receiver configuration
will reproduce the result. Exact orderable firmware/options, restrictions and
support for our trajectory still need confirmation.
[Braun et al., flight report](https://www.mdpi.com/2673-4591/126/1/39),
[DLR-hosted paper](https://elib.dlr.de/214653/1/engproc-126-00039.pdf).

NovAtel separately offers aerospace/space configurations with high-speed tracking
firmware and identifies OEM719/OEM7720 products. That gives a second supplier
route, not a selected alternative or an established cost. Request a supported
sounding-rocket configuration, not simply a receiver with a space-related web
page. [NovAtel aerospace](https://novatel.com/industries/aerospace).

## 4. Routes worth considering

### A. Supported high-dynamic GNSS — leading route

Obtain written specification for the exact orderable receiver/firmware:
maximum altitude, speed, acceleration, jerk and reacquisition behaviour. Ask
whether these are simultaneous conditions; what happens when exceeded; whether
raw observations continue; and which model, tracking-loop options or authorisations
are required. No supplier has been contacted in this review.

The hardware delta is broader than one chip:

- Receiver supply and peak-current allocation, reset/power sequencing and
  protected data/PPS connection. Re-evaluate its own voltage levels; no assumption
  that every event/PPS pin accepts 3.3 V.
- A multiband antenna with verified installed sky coverage. Budget the antenna,
  filtering, LNA/bias where needed, RF loss and mechanically restrained feed.
- Sensible separation from telemetry and switching noise. Check simultaneous
  reception during actual maximum TX duty and load switching.
- Logging of position **and velocity**, receiver time, fix status, accuracy
  estimates, satellite/signal quality and reset/outage events. Raw observations
  are desirable when available; their storage rate must be measured separately.

For scale, mosaic uses a roughly 31 × 31 mm module and separate RF integration;
its hardware manual distinguishes 1.8 V timing/event interfaces from other
interfaces. This is not a drop-in SAM patch replacement.
[Septentrio hardware manual](https://www.septentrio.com/system/files/support/mosaic_hardware_manual_v1.11.0.pdf).

My preference for exploration is a vehicle-specific tracking installation,
potentially independent of ordinary Croí. The cost and mechanical implications
would then apply to the space-shot vehicle. A new receiver on every board is not
justified yet. Supported hardware price, licence conditions and availability are
unknown; retail module cost alone would not include the antenna, integration
and verification effort.

### B. Consumer GNSS plus inertial/ballistic bridging — useful, but conditional

Keep the last *valid* state and propagate position/velocity with calibrated
inertial data and gravity. Preserve uncertainty rather than pretending GNSS
continued. Later valid fixes can help post-flight smoothing, but cannot repair
a real-time decision already made during the outage.

An accelerometer measures specific force. In near-freefall its reading tends
towards zero, although the vehicle still accelerates gravitationally. Gravity
belongs in the navigation equations. A low-g accelerometer measures coast drag
and disturbances; it does not directly measure height or speed.

For a one-dimensional illustration, constant unmodelled vertical acceleration
bias gives `δh = δh₀ + t·δv₀ + ½·b·t²`.

| Outage | 0.1 mg bias alone | 1 mg bias alone | 10 mg bias alone | Initial velocity error of 1 m/s alone |
| --- | ---: | ---: | ---: | ---: |
| 60 s | 1.8 m | 17.7 m | 176.5 m | 60 m |
| 120 s | 7.1 m | 70.6 m | 706.1 m | 120 m |
| 180 s | 15.9 m | 158.9 m | 1,588.7 m | 180 m |

These are signed-error magnitudes for isolated assumptions, not confidence
intervals or predictions for the selected IMUs. At 120 seconds, a 10 m budget
would allow only 0.083 m/s initial velocity error if that were the sole error,
or about 0.14 mg constant bias if that were the sole error. A real budget must
share allowance among many effects.

During boost, scale-factor error, clipping, vibration rectification, temperature
and attitude error can corrupt the velocity we carry into coast. ADXL375's
nominal ±200 g does not ensure unlimited headroom or precision. Two low-g IMUs
can both saturate. The gyro ranges also differ. The actual flight dynamics and
installed data determine whether any inertial solution is credible.

Attitude error rotates measured specific force incorrectly. Do not automatically
apply a `g × tilt error` argument to a sensor experiencing nearly zero specific
force in coast. Conversely, large boost forces make even modest alignment errors
important. A spinning sensor away from the vehicle centre also sees rotational
acceleration; lever arms and body-axis transforms matter.

Ballistic fitting can outperform blindly integrating noise during a demonstrably
quiet coast. It can also produce a convincing wrong answer if drag, attitude,
venting, a residual thrust event or the initial state is wrong. Keep raw data;
compare models and residuals; never constrain the result to the target altitude.

### C. Independent ground tracking — valuable evidence

An instrumented range's tracking radar can give an independent trajectory.
Range **and angle**, surveyed station location, timing and their uncertainties
are needed to turn tracking into height. A precise slant range alone defines
a surface, not a unique altitude.

Surveyed multi-station optical tracking can provide triangulation where target
visibility, weather, pointing calibration and geometry permit. At 100 km,
100 microradians corresponds to roughly 10 m transverse displacement; this
does not by itself establish 10 m vertical accuracy. One attractive camera
recording is not a calibrated height measurement.

LoRa RSSI is not useful precision altimetry. LR2021 ranging is also not a GNSS
replacement: even accurate two-way range needs suitable ground geometry,
calibration, timestamps and a verified dynamic error budget. This review does
not select radar, optical hardware or a ranging network.

### D. Raw GNSS recording and post-processing — research route

Recording raw observations, or much heavier RF samples, may enable later
trajectory reconstruction even when real-time navigation is inadequate.
First establish what the exact receiver continues to output outside its
supported navigation envelope. Raw logging is not an automatic way around
receiver restrictions, lost tracking or a bad antenna. A software-defined
receiver would add substantial RF, storage and signal-processing work.

Treat this as possible independent evidence, not the primary real-time plan
for the current board.

## 5. Why the barometers do not close this gap

Their documented low-pressure limits and accuracy characterisation are far
from this flight regime. The TE extended ADC range starts at 10 mbar, which is
1,000 Pa; that is not its full-accuracy floor. Pressure-to-height conversion
also depends on atmospheric state, vent response and local flow. More ADC bits
cannot repair those limits. The [sensor review](sensor-configuration-review-2026-09-07.md)
keeps full accuracy separate from an extended numerical output.

Barometers remain useful lower down. Above their justified measurement range,
stop treating them as absolute-height truth. Do not feed an extrapolated or
clamped pressure reading into a filter with a small confidence bound.

## 6. Smallest useful next investigation, when this becomes active

1. Specify real-time navigation versus post-flight proof, datum, allowed error
   and longest acceptable outage. These are mission choices, not chosen here.
2. Obtain one representative trajectory envelope: altitude, speed, acceleration,
   jerk, roll/tumble and a plausible antenna installation. It need not be the
   final rocket to screen receiver suitability.
3. Ask two relevant vendors about that envelope and obtain supported configuration
   and delivered cost. Receiver model name alone is insufficient.
4. Replay the envelope through candidate estimation models with biased sensors,
   clipping, clock offset, realistic data rates and missing GNSS. Show error
   distributions and failures against the chosen target, not only a nominal plot.
5. Use GNSS RF simulation or a range/lab with it to check acquisition, reacquisition
   and measurement quality under representative motion and interruptions.
   Serial replay tests parsing/estimation; it cannot test RF tracking loops.
6. Validate the installed assembly with retained raw evidence and an independent
   reference where available. A fitted covariance is not a calibrated uncertainty
   until its coverage has been checked.

These are future discriminating steps, not a new pre-order gate for Croí Rev A.
No accuracy specification, receiver purchase or extra PCB has been authorised.

## Calculation status

[Reproducible arithmetic](../calculations/avionics-options-estimates.py) was executed
with Python 3. It checks the coast against its energy solution and a halved
integration step. It excludes Earth rotation/oblateness, atmosphere, vehicle
dynamics, sensor models and actual receiver behaviour. Its sub-millimetre
numerical agreement is a check of the toy calculation, **not real-world accuracy**.

Conclusion: the useful distinction is supported **measurement through the whole
trajectory** versus an estimate carried through an unobserved interval. Both
can be useful. Only an error budget and evidence tell us which is accurate enough.
