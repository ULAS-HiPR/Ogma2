# Hardware handoff for Anav — updated 8 September

## 30 September status — preserved CAD, newer proposal

This handoff describes the **8 September implementation**, including two
LQFP100 MCUs and three servo channels. It remains the interface reference for
that CAD; it is not the latest proposed capture baseline. The
[22 September capture specification](architecture/schematic-capture-spec.md)
proposes a 64-pad comms MCU and a separately controlled services supply; the
three servo channels stay (D-7.1). Those changes have not been implemented or accepted. The
[system tour](architecture/system-tour.md) compares the two states.

The historical DMA/component/rationale links below point outside this clone.
They are supporting workspace evidence, not portable current authority. Use the
repository's [processor chapter](architecture/01-mcus.md),
[sensor/recording chapter](architecture/07-sensors-logging.md),
[GNSS/radio chapter](architecture/06-gnss-radio.md) and linked native/proposed
pin tables for current review. No target firmware implementation is present on
the inspected review branch; this document does not prove driver completion.

## 6–7 October changes that affect firmware

- Two processors, decided (D-6.12): flight and comms, two firmware images. Flight
  must complete the mission with comms held in reset.
- Both MCUs are STM32H563: Cortex-M33 with single-precision FPU. Build flags
  `-mcpu=cortex-m33 -mfpu=fpv5-sp-d16 -mfloat-abi=hard` hold for either comms package.
- Flight pins ([capture delta](architecture/schematic-capture-spec.md#burrito-changes)):
  PE5 → `FC_POWER_HOLD` (assert at launch detect, release after LANDED);
  PE7/PE9 → `PYRO1_FIRE`/`PYRO2_FIRE` straight to the TPS1H100s; PE12 →
  `PYRO3_FIRE` through the staging latch; PD14 reads the latch, PD15 sets a new
  flight (only with staging disarmed), PC9 senses the staging arm; PE8 →
  `SERVICE_POWER_EN`; PD10 stays `SERVO3_PWM` (LPTIM2_CH2); PE6, PA8, PA9, PA10,
  PE10, PE13, PE14, PE15 spare.
- Three pyro channels and three servos (D-7.1). Channel 3 is staging / air-start:
  never a recovery channel, and dead after any reset until a new flight is set.
- Sensors have no power enables: recover I²C by clocking SCL, sensors by soft reset.
- No one-shots: firmware bounds every firing pulse and fires one channel at a time.
- Enable the backup regulator so backup SRAM survives on VBAT's hold-up.
- Recording: full rate from launch detect with a RAM pre-trigger; erase-ahead
  only before launch detect.
- Event logic draft for your review: [recovery logic](architecture/10-recovery-logic.md).
- Decisions: [decisions.md](../decisions.md).

## Read first: external GNSS and power-enable revision

U4504 is MAX-M10S-00B with an external passive antenna, vertical SMA and RF ESD
protection. No antenna bias, ANT_CHECK, backup cell or new GNSS I²C bus.
MCU pins and ownership are unchanged: PA9 TX → MAX RX3; PA10 RX ← MAX TX2;
PA0 TIM2_CH1 ← TIMEPULSE4; PC5 open-drain reset → RESET9; PB0 enable.
Configure for the actual MAX-M10S module/firmware and verify startup/navigation
messages on hardware. Its 80 km navigation limit does not establish Kármán
altitude coverage. Keep loss/invalidity independent of essential flight work.

TIMEPULSE4 and SAFEBOOT18 have an internal 1 kΩ connection. SAFEBOOT stays NC;
do not configure a startup PPS pull-down or force PPS low. V_IO and VCC use
the switched 3.3 V domain. VIO_SEL15 and V_BCKP6 stay open.

External maintained contacts now control Croí battery entry and Foinse's two
separate source branches. Open/unplug is electronic OFF, closed is enable.
This requires no firmware and is not a commanded or sensed arming state.
USB can still run service logic. Contact bounce can cycle power/reset latched
eFuse faults; retain reset evidence and existing reset/output-inhibit policy.
Do not infer physical disarm from power enable or the green readiness LED.

No flight/comms GPIO allocation, bus address, servo timer or firmware ownership
changes. The 28 DNP safeguards and unfinished physical arm assembly remain.
[Exact circuit and harness delta](archive/installation-change-record-2026-09-08.md).

## Latest accepted change: three servos and complementary readiness

**Supersedes the original two-servo / independent red-LED allocation.**
PD10/pad 57 = SERVO3_PWM, LPTIM2_CH2 AF3. PC6/PC7 remain TIM3 CH1/2.
PD7/pad 88 remains FLIGHT_STATUS_LED1, now complementary readiness control:
low/reset = red not ready; high = green selected-profile preflight checks passed.
It is NOT armed/launch authority or an independent watchdog. Clear it on loss
of a required check; a stuck-high firmware fault can leave stale green.
Amber comms, hardware power LED and buzzer remain independent.

Servo3 uses existing TXU0304 A3/B3Y, 100 ohm series and 100k output pull-down.
Reserve and verify LPTIM2 clock, PWM period/polarity, start/stop/reset behavior;
do not assume phase synchronisation with TIM3. Extend channel commands, leases,
safe states and logs to three. Existing common rail permission/reset gate and
R6804 DNP remain; shared nominal 2A is provisional, not grid-fin qualification.

J6602 = 430451000, NEW ten-contact pinout: servo1 PWR/PWM/GND = 1/2/3;
servo2 = 4/5/6; servo3 = 7/8/9; pin10 NC. Old eight-contact harness is obsolete.
Radio J4601 = standard vertical SMA 132134; radio GPIO/driver contract unchanged.
USB unchanged. [Full change and tests](archive/connector-servo-readiness-revision-2026-09-07.md).


7 September 2026. Self-contained paste-to-Claude handoff. Supersedes the
6 September hardware handoff for the changes below; retains its architecture.
Seán authorised implementation of these recommendations while away. This is
not a claim that Anav has already reviewed them. Firmware architecture and code
remain yours and your collaborator's work.

## Read this delta first

- **No MCU or MCU-pin changes.** Both devices remain STM32H563VIT6 non-SMPS,
  LQFP100. Both original 100-pad allocation CSVs remain byte-identical. The
  actual native pin/net tables are embedded at the end of this document.
- **Croí U7101 is INA228AIDGSR at 7-bit I²C address 0x40.** The avionics monitor
  moved from Foinse to Croí; Foinse U5001 remains propulsion INA228 0x41 and
  ADS1115 U6001 remains 0x48. No Foinse MCU or CAN endpoint.
- Enable **FOINSE_RETURN_EN / PA15, pad 77** for power monitoring even in
  standalone Croí. The net name is historical; it now enables the optional
  monitoring domain on both configurations. Do not gate this function solely
  on detecting a Foinse board. Do not scan arbitrary I²C addresses in flight.
- Croí INA is on the AUX side of the existing TMUX boundary. An external stuck
  I²C segment can lose both local and Foinse monitoring; essential acquisition
  must continue. Its ALERT is NC: polling, no newly allocated interrupt pin.
- **Battery ADC already exists:** U201 PA0/pad 23/ADC1_INP0 reads
  `ADC_VEHICLE_VBAT`, after the common eFuse and new 5 mΩ shunt. The divider is
  22.1k + 22.1k over 10k, ratio 10/54.2. U8001 disconnects it with flight power
  absent. Use calibrated VREFINT; do not assume 3.300 V ADC reference.
- INA VBUS reads `BAT_EFUSE_IN`: after the reverse FET, before the eFuse.
  Different voltage nodes must have different telemetry names/validity.
- **Four simple LEDs, no NeoPixel/LCD.** Flight PD7/pad 88 = status green;
  PD10/pad 57 = servo3; red now follows inverted PD7. Comms retains its existing STATUS_LED GPIO = amber.
  New PWR LED is hardware-only, no GPIO. Voltage present is not readiness.
- **BZ9001 CPT-9019S-SMT-TR is an externally driven passive piezo.** PD6/pad 87
  remains GPIO through Q9001. Do not assume a hardware PWM alternate function
  on that pin. Ground-only startup tones may use bounded timer-driven GPIO
  toggles, not blocking delays or interrupt masking. Mute before sensor
  calibration/flight; reset defaults silent. Landed beeps require a qualified
  nonessential mode. No acoustic guarantee in the installed bay or near vacuum.
- **No external RTC or backup cell.** Retain flight H563 internal RTC + existing
  LSE crystal for qualified reset continuity; use a high-resolution monotonic
  timer for acquisition/deadlines. HSE and LSE have separate error budgets.
  Illustrative HSE budget 100 ppm = 90 ms / 15 minutes; provisional LSE
  continuity allowance 200 ppm = 180 ms / 15 minutes. These are not measured
  guarantees. LSE room-temperature ±20 ppm is not its full-temperature bound.
  Full source loss can lose both backup time and checkpoints. UTC/GNSS must
  never step control deadlines or be a boot prerequisite.

## INA228 driver contract and initial settings

Reuse one parameterised driver for 0x40 Croí and optional 0x41 propulsion.
Identify the device, verify configuration readback and calibration, mark
samples with device/epoch, acquisition-window estimate, sequence, validity and
configuration identity. Current sign is positive from source to load.

R7101/R2011 = **0.005 Ω nominal**. Begin ADCRANGE=0 (±163.84 mV, approximately
±32.768 A at this shunt) to preserve fault/peak headroom. That is a measurement
range, not an allowed load current. Proposed current LSB = 100 µA/count;
`SHUNT_CAL = round(13107.2 × 10^6 × CURRENT_LSB × Rshunt) = 6554` for range 0.
Read raw signed 20-bit values correctly from their 24-bit register containers;
sign extension and the unused low bits need unit tests. Do not accidentally
apply range-1 scaling or treat a full 24 bits as the current value.

Start continuous shunt + bus conversion, 150 µs per conversion, averaging 16,
die-temperature conversion disabled unless explicitly requested. Nominal full
pair window = 4.8 ms. Poll/record current at 100 Hz; voltage may be 10–100 Hz.
Use conversion-ready/overflow status, bounded deadlines and valid sample age.
No conversion-ready wire exists, so use the documented status register. A new
read is not proof of a new sample; missed intermediate conversions are expected.

An optional bounded 500 Hz diagnostic window can use averaging 1. On the
initial 100 kHz bus, a three-byte register read uses roughly 54 SCL periods
before extra bus software overhead: 0.54 ms. Adding a two-byte status read is
another 0.45 ms, already roughly half a 2 ms sample budget. During such windows
defer nonessential Foinse reads; cap bus work, measure scheduling and record
missed samples. A later 400 kHz setting requires actual rise-time/ramp tests.
Do not block the 1 kHz essential loop on an optional I²C transaction. Current
monitor absence/failure degrades evidence, not energetic authority or flight.

Power/energy registers use pre-eFuse voltage × protected-load current, so label
them source-side load estimates. They exclude upstream quiescent/leakage,
charging and USB power. Die temperature is not pack temperature. Brownout/AUX
loss creates a gap, not zero current. Reset accumulation cannot silently become
an eight-hour battery/charge total.

## Records and diagnostic meaning

Propose a 16-byte bulk-current record at 100 Hz: timestamp/epoch association,
signed current, status/configuration identity and sample sequence, with actual
encoding owned by you. Allow 20% framing, adding **1,920 B/s** to the old
94,752 B/s estimate: **96,672 B/s**. Thirty minutes adds **3,456,000 bytes**;
the earlier mission budget becomes **180,587,776 bytes** before optional burst
allowance, still below 256 MiB minus the 64 MiB reserve. Cap extra 500 Hz capture
to 30 seconds aggregate initially: another 230,400 bytes over the baseline.
Recalculate if record size, channels, averaging, rate or mission duration changes.
The existing 20 kB/s routine UART cap is unchanged: keep raw current local and
send bounded summaries, not every new raw sample by default.

Correlate request → driver output → measured current → independent physical
outcome. A current increase does not prove servo movement or ignition. A local
capacitor can supply a pulse before the battery current rises. Keep existing
per-channel current ADCs; do not infer a safe re-fire/retry from ambiguous bulk
current. Faulted/clipped/stale samples cannot grant permission. All four output
energy links and load-dependent pulse/continuity DNP safeguards remain.

## Hardware and first bring-up status

Croí has 43 schematic pages, Foinse 11. Native connectivity checks pass: Croí
2,150 pins / 283 assertions, Foinse 278 / 91. Both MCU maps are unchanged.
Croí still has four deliberate unpowered-output ERC errors and four warnings;
Foinse ERC is zero. These checks are not analog or hardware qualification.
The PCBs are unrouted, Nano-Fit exact footprints remain missing, and the physical
arm/load-specific circuit is still unfinished. No test using live energetic
loads is authorised. First-block tests use the first full engineering PCBA;
there is **no pre-order mini-PCB/coupon requirement**.

Implement hardware-independent driver tests now. On hardware, start with the
non-actuating recorder, calibrated ADC/current checks, optional-bus failure,
silent-default/ground-tone tests and RTC/reset-class tests. Retain responsibility
for RTOS/executive, HAL, estimator, task structure and implementation choices.

## Retained architecture and implementation obligations

### Accepted radio revision — 7 September

Wio-LR2021 868/915 MHz (Seeed SKU 100058045) replaces E22/SX1262. Both
MCU pad maps below remain frozen. PC2's historical `LORA_DIO1` signal connects
to Wio **DIO5, pad 2**; configure it for IRQ. PC3/RXEN and PC4/TXEN are reserved
and unused, initialise low. Reset/BUSY/NSS/SCK/MISO/MOSI remain on the same MCU
pads; use an LR2021 driver. BUSY is open-drain with a switched-side pull-up.
Start SPI mode 0 at 1 MHz and verify the isolation/470 Ω paths before increasing.
Do not retain the E22 2.2 V TCXO setting: Wio lists an internal 3.0 V TCXO;
exact revision/startup configuration still needs driver-source confirmation.
Only sub-GHz RF is connected. No high-band TX. Bounded failures and reset
reinitialisation stay in comms; firmware implementation remains Anav's.

The [complete radio contract](archive/radio-change-2026-09-07.md) supplies the exact
22-contact map, hardware delta and remaining checks. It supersedes older
radio rows in historical research files. The accepted
[sensor checklist](archive/sensor-configuration-review-2026-09-07.md) adds no sensor
or physical pin change.

The following consolidates the earlier handoff with superseded wording updated.
The revision above controls any remaining ambiguity. Exact frozen pads and actual
native pin nets follow it, so this file can be pasted without local CSV access.

## What is fixed enough to begin

Two **STM32H563VIT6**, non-SMPS, LQFP100. Flight owns sensing, estimation,
recording, local outputs and propulsion CAN. Comms owns USB, GNSS and radio.
Foinse has no MCU and no CAN endpoint. Standalone Croí has the same flight target
and local branch protection as Croí connected to Foinse.

Use these machine-readable hardware inputs:

- [Flight physical pads](../hardware/croi2/libraries/inputs/flight-pinout.csv),
  [comms physical pads](../hardware/croi2/libraries/inputs/comms-pinout.csv).
- [DMA allocation](../../architecture-review-2026-09-06/research/dma-allocation.csv).
- [Selected sensors/NOR](../../architecture-review-2026-09-06/research/sensors-rf-selected-components.csv)
  (its E22 row is superseded); [current radio map](archive/radio-change-2026-09-07.md).
- [MCU rationale, addresses and manufacturer evidence](../../architecture-review-2026-09-06/research/mcu-and-pinout.md).

They contain 100 physical pads per MCU, including supplies. Flight has no free
GPIO; two status LEDs/buzzer can be reclaimed before changing package. Comms
has 48 unassigned GPIO after the USB source-control additions. Do not use those
spares to let comms directly control flight reset, arm or outputs.

## Initial peripheral configuration

| Owner / peripheral | Device or purpose | Initial setting |
| --- | --- | --- |
| Flight SPI1 | ST LSM6DSV16XTR | 4 MHz; 960 Hz, ±16 g / ±4000°/s; separate DRDY |
| Flight SPI2 | TDK ICM-42688-P | 4 MHz; 1 kHz, ±16 g / ±2000°/s; separate DRDY |
| Flight SPI3 | ADI ADXL375BCCZ | 2 MHz, mode 3; 800 Hz, nominal ±200 g; separate INT1 |
| Flight I²C1 | Bosch BMP390 | 400 kHz bus; 50 Hz pressure target |
| Flight I²C2 | TE MS5607-02BA03 | 400 kHz bus; asynchronous OSR4096 conversions; 50 Hz compensated target |
| Flight I²C4 | Croí INA228 0x40; optional Foinse 0x41 | 100 kHz initial; separate bounded optional bus |
| Same optional I²C4 | Foinse ADS1115IDGSR | Two pack thermistors and two protected-rail dividers; 10 Hz/channel target |
| Flight OCTOSPI1 | MX66L2G45GMI00 | Quad, 16 MHz initial; pre-erased append-only recording |
| Both USART3 | Inter-MCU link | 2 Mbaud 8N1 flight; 8 Mbaud disarmed service |
| Flight FDCAN1 | Propulsion peer | Classical CAN, 500 kbit/s; TCAN3413DRBR |
| Flight TIM3 CH1/2 | PC6/PC7 servo1/2 PWM | Common time base; actual servo limits remain required |
| Flight LPTIM2 CH2 | PD10 servo3 PWM, AF3 | Separate timer; clock, waveform and reset verification required |
| Flight ADC1/2 | Rails, continuity, output current | Protected 3.3 V-safe front ends; normal 100 Hz recorded health |
| Comms USART1 / TIM2 CH1 | MAX-M10S / PPS | GNSS 10 Hz target; independent PPS capture; no startup pull-down |
| Comms SPI1 | Wio-LR2021 868/915 MHz | Mode 0, 1 MHz initial; BUSY/reset/DIO5 IRQ; RXEN/TXEN unused; clock settings require module-specific confirmation |
| Comms USB | Service/extraction | USB 2.0 full-speed; CDC or another maintained bulk transport |

Initial CPU 128 MHz, legal 64 MHz peripheral kernels. Each MCU has its own
16 MHz HSE; flight alone has LSE/RTC. HSI48 + CRS is the USB clock candidate.
The arithmetic fits, but a compiled H563 clock configuration still has to prove
the actual peripheral mux sources, VOS, flash wait states and oscillator limits.
In particular, do not assign a PLL output to USART3 that its kernel mux cannot use.

Oscillator starting components: two **ECS-160-10-36Q-ES-TR**, 16 MHz, 10 pF load,
2.5 × 2.0 mm four-pad package, and one **ABS07-32.768KHZ-7-T**, 7 pF load,
3.2 × 1.5 mm two-pad package. These are schematic candidates, not a proved
oscillator network. Follow the package ground-pad drawing, calculate effective
load from pin/PCB capacitance and prove negative-resistance/startup margin with
the H563 at temperature. Do not just populate capacitors equal to crystal CL.
[ECS exact part](https://ecsxtal.com/products/crystals/surface-mount-crystals/ecs-160-10-36q-es-tr/),
[Abracon part-identification/data sheet](https://abracon.com/Resonators/ABS07.pdf).

Use a 1 kHz essential scheduler allocation and a 200 Hz initial estimator/policy
rate. This does not imply synchronous 1 kHz samples from all sensors. At first,
allow no more than 700 µs total essential execution/blocking per 1 ms interval,
leaving 300 µs reserve. This is a budget, not observed WCET or a requirement to
busy-wait. Your scheduler design may improve it while preserving bounded latency.

## Rail and signal boundaries

Core, communications and optional storage/AUX have separate TPS7A91 branches.
Each of the five flight sensors has its own limited supply and enable. Flight
also controls NOR, communications, Foinse AUX, CAN and servo power separately.
Aggregate branch-fault reporting says something failed, not which branch.
Diagnose with bounded status reads/isolation, never an unbounded discovery loop.

Proposed powered-off interfaces:

| Boundary | Candidate part / connection |
| --- | --- |
| Each three-output/one-input SPI sensor bus | TXU0304PWR; TXU0101DCKR for its separate interrupt |
| Flight ↔ comms UART | TXU0202DCUR; both supplies and output-enable defaults explicit |
| Foinse monitor bus | TCA4307DGKR with isolated-side pull-ups and bounded recovery |
| Each pressure bus | TMUX1511PWR, two bidirectional channels, supplied from that switched sensor domain |
| NOR quad bus plus reset | Two TMUX1511PWR, seven channels; remaining channel disabled |
| CAN TX/STB/RX | Additional TXU0304PWR; two outgoing signals, one incoming, unused channel held inactive |

The pressure/NOR rows close previously unselected support-part functions. TMUX1511
is bidirectional and explicitly isolates up to 3.6 V signals with its supply at
zero. Its partial-supply/ramp behaviour still requires first-PCBA tests; “powered-off”
must not silently mean every brownout voltage. Tie enables to the corresponding
branch permission and qualify with actual rail-valid where necessary; no extra
flight GPIO is assumed. Confirm signal direction/OE, logic levels, current during
a short, reset-line open-drain behaviour and 16 MHz NOR / 8 Mbaud UART integrity.
[TI TMUX1511 data sheet](https://www.ti.com/lit/ds/symlink/tmux1511.pdf).

A failed optional device may consume its bounded branch current until protection
trips. It must not inject enough current through signal pins to defeat that
boundary. The board cannot claim successful containment from a software disable
command alone. Those checks belong in the first engineering PCBA, not your driver API.

Supply CAN from the **optional 3.3 V domain through its own TPS2553 limited
branch**, controlled by the existing CAN_POWER_EN. Start with the 110–150 mA
limit class, then verify dominant-bus peak/current and startup. The optional
domain's upstream approximately 0.5 A allocation still bounds storage + CAN +
AUX collectively. A fault there may remove all three; it must not remove the
flight core. No extra GPIO, fourth main LDO or hidden CAN load on held core is
introduced. The 100 mA optional normal-use estimate is not its simultaneous peak.

## USB source-state contract

The hardware bootstrap path is mandatory. USB-only operation cannot wait for
flight to enable comms if flight is deliberately still off.

| BAT_VALID | USB present / configured | Core input | Comms supply | RF/GNSS |
| --- | --- | --- | --- | --- |
| 0 | Absent | Off | Off | Off |
| 0 | Present, unconfigured | Off | Low-power enumeration | Hardware off |
| 0 | Present, configured | Permitted with controlled inrush | Service | Hardware off |
| 1 | Any USB state | Permitted independently of comms | Flight-controlled | Flight profile permits |
| 0 | USB suspended/deconfigured | Withdraw excess load/core input | Compliant suspend/restart | Off |

Comms PA1 is **USB_CONFIG_OK**, externally pulled low. Assert only after the
host configures the requested USB load; clear on reset, suspend and deconfiguration.
Comms PA2 reads hardware **BAT_VALID**, not a commanded value. PB2 reads protected
VBUS presence. The power circuit implements:

```text
CORE_INPUT_EN = BAT_VALID OR USB_CONFIG_OK
COMMS_SUPPLY_EN = BAT_VALID ? FLIGHT_COMMS_EN : USB_PRESENT
```

Core enable acts **before the hold capacitor**. The core LDO itself stays enabled
from its held input. Comms cannot withdraw valid battery-backed core power.
The initial USB limiter has a 50–100 mA low mode; target ≤40 mA total enumeration
draw so startup works at its minimum. Configured current-limit range is roughly
387–491 mA, not a blanket entitlement to draw 500 mA. Total port current, bias,
inrush and suspend require measurements. A high-clock bootstrap image that cannot
enumerate at the minimum budget is a real failure, not a “bad cable”.

USB has no path to raw actuator energy and does not charge packs. Service on
battery-powered hardware still checks physical disarm. Bulk extraction and
updating cannot run merely because a USB plug is present during flight.

## Memory and fault evidence

Main protected SRAM: SRAM2 64 KiB + usable ECC SRAM3 256 KiB. Keep critical stacks,
control state, descriptors and source-validity information there. Initial spending
limits: 44 KiB SRAM2 and 179 KiB SRAM3. SRAM1's 256 KiB is unprotected and may
hold disposable logging/USB buffers; its contents cannot independently grant
control authority. Reserve 128 KiB for log staging initially, about 1.38 seconds
at the proposed rate. This is buffer headroom, not allowed essential-loop blocking.

Two retained checkpoints occupy the 4 KiB backup SRAM. VBAT follows **held
FLIGHT_3V3** in this proposal, not a separate battery. Only measured valid-supply
processor-reset retention is credited. Confirm backup-regulator-ready and RTC
continuity; do not clear backup state routinely at boot. Cold ECC initialisation
and warm preserved-memory validation are separate startup paths.

Capture reset cause before libraries clear it. A restart must not perform a
stationary IMU calibration, reset the pressure datum, wait for GNSS, scan the
entire NOR or replay an old unqualified command. Restore only capabilities
supported by identity, CRC, age/time and state continuity. Staging stays inhibited
for the rest of the flight after a flight-core reset.

Enforce the hardware role map in configuration validation: channels 1/2 are
recovery-domain hardware, channel 3 is staging-domain hardware. A profile cannot
put sustainer ignition onto channels 1/2 and evade the staging reset veto. Changes
to that mapping require a reviewed circuit/manifest revision, not a field setting.

The selected external watchdog is serviced by an **earned 40 ms heartbeat**:
essential acquisition/validity/decision progress, not logger/CAN success and not
a free-running timer. The predecessor watchdog's dependency on logging and CAN
must not be copied. Watchdog reset assertion itself can last 230 ms: propose
≤400 ms to valid recovered capability after assertion, ≤550 ms after the last
earned heartbeat. The separate software-reset target is ≤100 ms. These new
class-specific budgets still require mission-level acceptance and target proof.

## Record and transport contracts

The original sensor allocation was **94,752 B/s**, including 20% framing.
Add revision B's 1,920 B/s current budget. The retained baseline allocation is:
24-byte ST/TDK samples, 16-byte high-g samples, 20-byte pressure records,
64-byte state records, 32-byte health and 112-byte GNSS records at the declared
rates. These are size budgets, not frozen packed C structures. Include integer
time basis, device identity, sequence, validity/saturation and explicit units.
If your encoding grows, rerun the allocation before accepting it.

The original thirty-minute plus pad/recovery/metadata budget used 177,131,776 bytes in 256 MiB NOR.
Reserve at least 64 MiB; about 23 MiB remains beyond that reserve at this budget.
A separate short high-rate current capture may use bounded queue/storage margin;
it is not an uncounted continuous stream.

Pre-erase the complete flight region while disarmed. Write 4 KiB payload blocks
then a separate 256-byte footer page containing identity, length, sequence and
integrity/commit information. Seventeen maximum-time page programs cost 25.5 ms
before bus/status overhead. Two programs per **256-byte data page** would cap
useful throughput below the allocation and are rejected. Recover by accepting
only fully validated committed blocks; interrupted tail data is expendable.
Test four-byte addressing and 16 MiB/128 MiB boundaries, not just the first sector.

Normal UART frames are bounded, maximum 512-byte payload, with length, type,
version, sequence, epoch and integrity. Cap routine outbound telemetry at 20 kB/s;
full raw samples remain local. Separate queue/deadline budgets for GNSS input,
status, accepted configuration and service. CRC does not replace age or authority.
Comms is an untrusted information producer even when its frame passes CRC.

Disarmed service may negotiate 8 Mbaud and 32 KiB bulk blocks, with credits,
resume and per-block checking. Physical data ceiling is 800 kB/s; 680 kB/s useful
is an **unmeasured target**. Five-minute extraction of 180 MB requires 600 kB/s.
A complete 256 MiB device takes about 6.6 minutes at 680 kB/s. Do not advertise
five minutes for the full chip. On physical arm transition, terminate bulk work
and re-establish the normal bounded protocol before flight readiness.

CAN carries typed requests, current accepted request identity, actual propulsion
state, permission/rejection and fault provenance. Its wire CRC does not prove
freshness or that the engine accepted an action. Propulsion retains local redlines,
permissives, output ownership and phase-specific link-loss policy. No LTS Linux
host or radio operator becomes required in the airborne safety loop.

## What to implement first

1. Non-actuating H563 clock/pin/linker skeleton, reset-cause capture and independent
   SWD recovery. Prove the exact part/AF/DMA map and ECC initialisation.
2. Five-device timestamped recorder with validity flags, pre-erased NOR and
   interruption recovery. No flight event thresholds needed yet.
3. Bounded comms stub, malformed-frame flood and power-off peer tests. Then real
   GNSS/radio/USB, keeping the same flight boundary.
4. Target checkpoint/reset campaign and independent hardware-inhibit observation.
5. Only after that evidence and the inert-load first-PCBA tests: mission-specific active
   recovery software and its separate review.

Choose the RTOS/executive, HAL depth, language, estimator implementation and
testing arrangement with your collaborator. Bring back measured timing, memory
and failure behaviour. The packet is meant to remove hardware guessing, not
occupy your firmware work.

## Frozen physical allocations and live nets

The allocation columns reproduce the original CSV; actual net comes from the
7 September revision-B native netlist. `unconnected-` means deliberately NC.
No firmware is authorised to repurpose those pins from this table alone.

### Flight U201: STM32H563VIT6

| Pad | Port/supply | Original allocation | Function / AF | Live schematic net |
| --- | --- | --- | --- | --- |
| 1 | PE2 | NOR_IO2 | OCTOSPI1_IO2 AF9 | NOR_IO2 |
| 2 | PE3 | TDK_DRDY | GPIO  | TDK_DRDY |
| 3 | PE4 | HG_INT1 | GPIO  | HG_INT1 |
| 4 | PE5 | ST_EN | GPIO  | ST_EN |
| 5 | PE6 | TDK_EN | GPIO  | TDK_EN |
| 6 | VBAT | FLIGHT_3V3 | BACKUP_SUPPLY  | FLIGHT_3V3 |
| 7 | PC13 | NC_LSE_QUIET | ANALOG  | unconnected-(U201-PC13-Pad7) |
| 8 | PC14 | LSE_IN | LSE  | FLIGHT_LSE_IN |
| 9 | PC15 | LSE_OUT | LSE  | FLIGHT_LSE_OUT |
| 10 | VSS | GND | GROUND  | GND |
| 11 | VDD | FLIGHT_3V3 | SUPPLY  | FLIGHT_3V3 |
| 12 | PH0 | HSE_IN | HSE  | FLIGHT_HSE_IN |
| 13 | PH1 | HSE_OUT | HSE  | FLIGHT_HSE_OUT |
| 14 | NRST | FLIGHT_NRST | RESET  | FLIGHT_NRST |
| 15 | PC0 | PYRO1_CURRENT | ADC2_INP10 ANALOG | ADC_PYRO1_CURRENT |
| 16 | PC1 | PYRO2_CURRENT | ADC2_INP11 ANALOG | ADC_PYRO2_CURRENT |
| 17 | PC2 | PYRO3_CURRENT | ADC2_INP12 ANALOG | ADC_PYRO3_CURRENT |
| 18 | PC3 | PYRO1_CONTINUITY | ADC1_INP13 ANALOG | ADC_PYRO1_CONTINUITY |
| 19 | VSSA | GND | GROUND  | GND |
| 20 | VREF- | GND | GROUND  | GND |
| 21 | VREF+ | FLIGHT_3V3 | SUPPLY  | FLIGHT_VDDA |
| 22 | VDDA | FLIGHT_3V3 | SUPPLY  | FLIGHT_VDDA |
| 23 | PA0 | VEHICLE_VBAT | ADC1_INP0 ANALOG | ADC_VEHICLE_VBAT |
| 24 | PA1 | FLIGHT_3V3 | ADC1_INP1 ANALOG | ADC_FLIGHT_3V3 |
| 25 | PA2 | PYRO_RAIL | ADC1_INP14 ANALOG | ADC_PYRO_RAIL |
| 26 | PA3 | SERVO_RAIL | ADC1_INP15 ANALOG | ADC_SERVO_RAIL |
| 27 | VSS | GND | GROUND  | GND |
| 28 | VDD | FLIGHT_3V3 | SUPPLY  | FLIGHT_3V3 |
| 29 | PA4 | ST_NCS | GPIO  | ST_NCS |
| 30 | PA5 | ST_SCK | SPI1_SCK AF5 | ST_SCK |
| 31 | PA6 | ST_MISO | SPI1_MISO AF5 | ST_MISO |
| 32 | PA7 | ST_MOSI | SPI1_MOSI AF5 | ST_MOSI |
| 33 | PC4 | PYRO2_CONTINUITY | ADC1_INP4 ANALOG | ADC_PYRO2_CONTINUITY |
| 34 | PC5 | PYRO3_CONTINUITY | ADC1_INP8 ANALOG | ADC_PYRO3_CONTINUITY |
| 35 | PB0 | SERVO_POWER_EN | GPIO  | SERVO_POWER_EN |
| 36 | PB1 | CAN_POWER_EN | GPIO  | CAN_POWER_EN |
| 37 | PB2 | NOR_CLK | OCTOSPI1_CLK AF9 | NOR_CLK |
| 38 | PE7 | PYRO1_HS_REQUEST | GPIO  | PYRO1_HS_REQUEST |
| 39 | PE8 | PYRO1_LS_SELECT | GPIO  | PYRO1_LS_SELECT |
| 40 | PE9 | PYRO2_HS_REQUEST | GPIO  | PYRO2_HS_REQUEST |
| 41 | PE10 | PYRO2_LS_SELECT | GPIO  | PYRO2_LS_SELECT |
| 42 | PE11 | NOR_NCS | OCTOSPI1_NCS AF6 | NOR_NCS |
| 43 | PE12 | PYRO3_HS_REQUEST | GPIO  | PYRO3_HS_REQUEST |
| 44 | PE13 | PYRO3_LS_SELECT | GPIO  | PYRO3_LS_SELECT |
| 45 | PE14 | RECOVERY_PERMIT | GPIO  | RECOVERY_PERMIT |
| 46 | PE15 | STAGING_PERMIT | GPIO  | STAGING_PERMIT |
| 47 | PB10 | TE_SCL | I2C2_SCL AF4 | TE_SCL |
| 48 | VCAP | FLIGHT_VCAP | CORE_REG_OUT  | FLIGHT_VCAP |
| 49 | VSS | GND | GROUND  | GND |
| 50 | VDD | FLIGHT_3V3 | SUPPLY  | FLIGHT_3V3 |
| 51 | PB12 | TDK_NCS | GPIO  | TDK_NCS |
| 52 | PB13 | TDK_SCK | SPI2_SCK AF5 | TDK_SCK |
| 53 | PB14 | TDK_MISO | SPI2_MISO AF5 | TDK_MISO |
| 54 | PB15 | TDK_MOSI | SPI2_MOSI AF5 | TDK_MOSI |
| 55 | PD8 | FLIGHT_TO_COMMS | USART3_TX AF7 | FLIGHT_TO_COMMS |
| 56 | PD9 | COMMS_TO_FLIGHT | USART3_RX AF7 | COMMS_TO_FLIGHT |
| 57 | PD10 | SERVO3_PWM | LPTIM2_CH2 AF3 | SERVO3_PWM |
| 58 | PD11 | NOR_IO0 | OCTOSPI1_IO0 AF9 | NOR_IO0 |
| 59 | PD12 | NOR_IO1 | OCTOSPI1_IO1 AF9 | NOR_IO1 |
| 60 | PD13 | NOR_IO3 | OCTOSPI1_IO3 AF9 | NOR_IO3 |
| 61 | PD14 | STAGE_INHIBIT_LATCHED | GPIO  | STAGE_INHIBIT_LATCHED |
| 62 | PD15 | NEW_FLIGHT_CLEAR_REQUEST | GPIO  | NEW_FLIGHT_CLEAR_REQUEST |
| 63 | PC6 | SERVO1_PWM | TIM3_CH1 AF2 | SERVO1_PWM |
| 64 | PC7 | SERVO2_PWM | TIM3_CH2 AF2 | SERVO2_PWM |
| 65 | PC8 | RECOVERY_ARM_SENSE | GPIO  | RECOVERY_ARM_SENSE |
| 66 | PC9 | STAGING_ARM_SENSE | GPIO  | STAGING_ARM_SENSE |
| 67 | PA8 | HG_EN | GPIO  | HG_EN |
| 68 | PA9 | BMP_EN | GPIO  | BMP_EN |
| 69 | PA10 | TE_EN | GPIO  | TE_EN |
| 70 | PA11 | NOR_EN | GPIO  | NOR_EN |
| 71 | PA12 | COMMS_EN | GPIO  | FLIGHT_COMMS_EN |
| 72 | PA13 | SWDIO | SWD AF0 | FLIGHT_SWDIO |
| 73 | VDDUSB | FLIGHT_3V3 | SUPPLY  | FLIGHT_3V3 |
| 74 | VSS | GND | GROUND  | GND |
| 75 | VDD | FLIGHT_3V3 | SUPPLY  | FLIGHT_3V3 |
| 76 | PA14 | SWCLK | SWD AF0 | FLIGHT_SWCLK |
| 77 | PA15 | FOINSE_RETURN_EN | GPIO  | FOINSE_RETURN_EN |
| 78 | PC10 | HG_SCK | SPI3_SCK AF6 | HG_SCK |
| 79 | PC11 | HG_MISO | SPI3_MISO AF6 | HG_MISO |
| 80 | PC12 | HG_MOSI | SPI3_MOSI AF6 | HG_MOSI |
| 81 | PD0 | CAN_RX | FDCAN1_RX AF9 | CAN_RX |
| 82 | PD1 | CAN_TX | FDCAN1_TX AF9 | CAN_TX |
| 83 | PD2 | HG_NCS | GPIO  | HG_NCS |
| 84 | PD3 | NOR_RESET_REQUEST | GPIO  | NOR_RESET_REQUEST |
| 85 | PD4 | SUPERVISOR_WDI | GPIO  | SUPERVISOR_WDI |
| 86 | PD5 | BRANCH_FAULT_N | GPIO  | BRANCH_FAULT_N |
| 87 | PD6 | BUZZER_DRIVE | GPIO  | BUZZER_DRIVE |
| 88 | PD7 | STATUS_LED1 | GPIO  | FLIGHT_STATUS_LED1 |
| 89 | PB3 | TE_SDA | I2C2_SDA AF4 | TE_SDA |
| 90 | PB4 | COMMS_RESET_REQUEST | GPIO  | COMMS_RESET_REQUEST |
| 91 | PB5 | CAN_STB | GPIO  | CAN_STB |
| 92 | PB6 | BMP_SCL | I2C1_SCL AF4 | BMP_SCL |
| 93 | PB7 | BMP_SDA | I2C1_SDA AF4 | BMP_SDA |
| 94 | BOOT0 | FLIGHT_BOOT0 | BOOT_STRAP  | FLIGHT_BOOT0 |
| 95 | PB8 | FOINSE_SCL | I2C4_SCL AF6 | FOINSE_SCL |
| 96 | PB9 | FOINSE_SDA | I2C4_SDA AF6 | FOINSE_SDA |
| 97 | PE0 | ST_DRDY | GPIO  | ST_DRDY |
| 98 | VCAP | FLIGHT_VCAP | CORE_REG_OUT  | FLIGHT_VCAP |
| 99 | VSS | GND | GROUND  | GND |
| 100 | VDD | FLIGHT_3V3 | SUPPLY  | FLIGHT_3V3 |

### Comms U401: STM32H563VIT6

| Pad | Port/supply | Original allocation | Function / AF | Live schematic net |
| --- | --- | --- | --- | --- |
| 1 | PE2 | NC | ANALOG  | unconnected-(U401-PE2-Pad1) |
| 2 | PE3 | NC | ANALOG  | unconnected-(U401-PE3-Pad2) |
| 3 | PE4 | NC | ANALOG  | unconnected-(U401-PE4-Pad3) |
| 4 | PE5 | NC | ANALOG  | unconnected-(U401-PE5-Pad4) |
| 5 | PE6 | NC | ANALOG  | unconnected-(U401-PE6-Pad5) |
| 6 | VBAT | COMMS_3V3 | BACKUP_SUPPLY  | COMMS_3V3 |
| 7 | PC13 | NC_LSE_QUIET | ANALOG  | unconnected-(U401-PC13-Pad7) |
| 8 | PC14 | LSE_IN | LSE  | unconnected-(U401-PC14-Pad8) |
| 9 | PC15 | LSE_OUT | LSE  | unconnected-(U401-PC15-Pad9) |
| 10 | VSS | GND | GROUND  | GND |
| 11 | VDD | COMMS_3V3 | SUPPLY  | COMMS_3V3 |
| 12 | PH0 | HSE_IN | HSE  | COMMS_HSE_IN |
| 13 | PH1 | HSE_OUT | HSE  | COMMS_HSE_OUT |
| 14 | NRST | COMMS_NRST | RESET  | COMMS_NRST |
| 15 | PC0 | LORA_RESET_N | GPIO  | LORA_RESET_N |
| 16 | PC1 | LORA_BUSY | GPIO  | LORA_BUSY |
| 17 | PC2 | LORA_DIO1 | GPIO  | LORA_DIO1 |
| 18 | PC3 | LORA_RXEN | GPIO  | LORA_RXEN |
| 19 | VSSA | GND | GROUND  | GND |
| 20 | VREF- | GND | GROUND  | GND |
| 21 | VREF+ | COMMS_3V3 | SUPPLY  | COMMS_VDDA |
| 22 | VDDA | COMMS_3V3 | SUPPLY  | COMMS_VDDA |
| 23 | PA0 | GNSS_PPS | TIM2_CH1 AF1 | GNSS_PPS |
| 24 | PA1 | USB_CONFIG_OK | GPIO  | CC_USB_CONFIG_OK |
| 25 | PA2 | BAT_VALID | GPIO  | CC_BAT_VALID |
| 26 | PA3 | NC | ANALOG  | unconnected-(U401-PA3-Pad26) |
| 27 | VSS | GND | GROUND  | GND |
| 28 | VDD | COMMS_3V3 | SUPPLY  | COMMS_3V3 |
| 29 | PA4 | LORA_NCS | GPIO  | LORA_NCS |
| 30 | PA5 | LORA_SCK | SPI1_SCK AF5 | LORA_SCK |
| 31 | PA6 | LORA_MISO | SPI1_MISO AF5 | LORA_MISO |
| 32 | PA7 | LORA_MOSI | SPI1_MOSI AF5 | LORA_MOSI |
| 33 | PC4 | LORA_TXEN | GPIO  | LORA_TXEN |
| 34 | PC5 | GNSS_RESET_N | GPIO  | GNSS_RESET_N |
| 35 | PB0 | GNSS_EN | GPIO  | GNSS_EN |
| 36 | PB1 | LORA_EN | GPIO  | LORA_EN |
| 37 | PB2 | USB_VBUS_PRESENT | GPIO  | USB_VBUS_PRESENT |
| 38 | PE7 | NC | ANALOG  | unconnected-(U401-PE7-Pad38) |
| 39 | PE8 | NC | ANALOG  | unconnected-(U401-PE8-Pad39) |
| 40 | PE9 | NC | ANALOG  | unconnected-(U401-PE9-Pad40) |
| 41 | PE10 | NC | ANALOG  | unconnected-(U401-PE10-Pad41) |
| 42 | PE11 | NC | ANALOG  | unconnected-(U401-PE11-Pad42) |
| 43 | PE12 | NC | ANALOG  | unconnected-(U401-PE12-Pad43) |
| 44 | PE13 | NC | ANALOG  | unconnected-(U401-PE13-Pad44) |
| 45 | PE14 | NC | ANALOG  | unconnected-(U401-PE14-Pad45) |
| 46 | PE15 | NC | ANALOG  | unconnected-(U401-PE15-Pad46) |
| 47 | PB10 | NC | ANALOG  | unconnected-(U401-PB10-Pad47) |
| 48 | VCAP | COMMS_VCAP | CORE_REG_OUT  | COMMS_VCAP |
| 49 | VSS | GND | GROUND  | GND |
| 50 | VDD | COMMS_3V3 | SUPPLY  | COMMS_3V3 |
| 51 | PB12 | NC | ANALOG  | unconnected-(U401-PB12-Pad51) |
| 52 | PB13 | NC | ANALOG  | unconnected-(U401-PB13-Pad52) |
| 53 | PB14 | NC | ANALOG  | unconnected-(U401-PB14-Pad53) |
| 54 | PB15 | NC | ANALOG  | unconnected-(U401-PB15-Pad54) |
| 55 | PD8 | COMMS_TO_FLIGHT | USART3_TX AF7 | CC_COMMS_TO_FLIGHT |
| 56 | PD9 | FLIGHT_TO_COMMS | USART3_RX AF7 | CC_FLIGHT_TO_COMMS |
| 57 | PD10 | NC | ANALOG  | unconnected-(U401-PD10-Pad57) |
| 58 | PD11 | NC | ANALOG  | unconnected-(U401-PD11-Pad58) |
| 59 | PD12 | NC | ANALOG  | unconnected-(U401-PD12-Pad59) |
| 60 | PD13 | NC | ANALOG  | unconnected-(U401-PD13-Pad60) |
| 61 | PD14 | NC | ANALOG  | unconnected-(U401-PD14-Pad61) |
| 62 | PD15 | NC | ANALOG  | unconnected-(U401-PD15-Pad62) |
| 63 | PC6 | NC | ANALOG  | unconnected-(U401-PC6-Pad63) |
| 64 | PC7 | NC | ANALOG  | unconnected-(U401-PC7-Pad64) |
| 65 | PC8 | NC | ANALOG  | unconnected-(U401-PC8-Pad65) |
| 66 | PC9 | NC | ANALOG  | unconnected-(U401-PC9-Pad66) |
| 67 | PA8 | NC | ANALOG  | unconnected-(U401-PA8-Pad67) |
| 68 | PA9 | GNSS_TX | USART1_TX AF7 | GNSS_TX |
| 69 | PA10 | GNSS_RX | USART1_RX AF7 | GNSS_RX |
| 70 | PA11 | USB_DM | USB_DM AF10 | USB_DM |
| 71 | PA12 | USB_DP | USB_DP AF10 | USB_DP |
| 72 | PA13 | SWDIO | SWD AF0 | COMMS_SWDIO |
| 73 | VDDUSB | COMMS_3V3 | SUPPLY  | COMMS_3V3 |
| 74 | VSS | GND | GROUND  | GND |
| 75 | VDD | COMMS_3V3 | SUPPLY  | COMMS_3V3 |
| 76 | PA14 | SWCLK | SWD AF0 | COMMS_SWCLK |
| 77 | PA15 | NC | ANALOG  | unconnected-(U401-PA15(JTDI)-Pad77) |
| 78 | PC10 | NC | ANALOG  | unconnected-(U401-PC10-Pad78) |
| 79 | PC11 | NC | ANALOG  | unconnected-(U401-PC11-Pad79) |
| 80 | PC12 | NC | ANALOG  | unconnected-(U401-PC12-Pad80) |
| 81 | PD0 | NC | ANALOG  | unconnected-(U401-PD0-Pad81) |
| 82 | PD1 | NC | ANALOG  | unconnected-(U401-PD1-Pad82) |
| 83 | PD2 | NC | ANALOG  | unconnected-(U401-PD2-Pad83) |
| 84 | PD3 | NC | ANALOG  | unconnected-(U401-PD3-Pad84) |
| 85 | PD4 | NC | ANALOG  | unconnected-(U401-PD4-Pad85) |
| 86 | PD5 | NC | ANALOG  | unconnected-(U401-PD5-Pad86) |
| 87 | PD6 | NC | ANALOG  | unconnected-(U401-PD6-Pad87) |
| 88 | PD7 | NC | ANALOG  | unconnected-(U401-PD7-Pad88) |
| 89 | PB3 | COMMS_SWO | TRACESWO AF0 | COMMS_SWO |
| 90 | PB4 | STATUS_LED | GPIO  | COMMS_STATUS_LED |
| 91 | PB5 | BRANCH_FAULT_N | GPIO  | CC_BRANCH_FAULT_N |
| 92 | PB6 | NC | ANALOG  | unconnected-(U401-PB6-Pad92) |
| 93 | PB7 | NC | ANALOG  | unconnected-(U401-PB7-Pad93) |
| 94 | BOOT0 | COMMS_BOOT0 | BOOT_STRAP  | COMMS_BOOT0 |
| 95 | PB8 | NC | ANALOG  | unconnected-(U401-PB8-Pad95) |
| 96 | PB9 | NC | ANALOG  | unconnected-(U401-PB9-Pad96) |
| 97 | PE0 | NC | ANALOG  | unconnected-(U401-PE0-Pad97) |
| 98 | VCAP | COMMS_VCAP | CORE_REG_OUT  | COMMS_VCAP |
| 99 | VSS | GND | GROUND  | GND |
| 100 | VDD | COMMS_3V3 | SUPPLY  | COMMS_3V3 |

### DMA starting allocation (unchanged)

```csv
role,controller,channel,request_symbol,request_number,priority,notes
flight,GPDMA1,0,GPDMA1_REQUEST_SPI1_RX,6,high,Fixed ownership; bounded sensor transaction
flight,GPDMA1,1,GPDMA1_REQUEST_SPI1_TX,7,high,Fixed ownership; bounded sensor transaction
flight,GPDMA1,2,GPDMA1_REQUEST_SPI2_RX,8,high,Fixed ownership; bounded sensor transaction
flight,GPDMA1,3,GPDMA1_REQUEST_SPI2_TX,9,high,Fixed ownership; bounded sensor transaction
flight,GPDMA1,4,GPDMA1_REQUEST_SPI3_RX,10,high,Fixed ownership; bounded sensor transaction
flight,GPDMA1,5,GPDMA1_REQUEST_SPI3_TX,11,high,Fixed ownership; bounded sensor transaction
flight,GPDMA1,6,GPDMA1_REQUEST_ADC1,0,high,Fixed ownership; bounded sensor transaction
flight,GPDMA1,7,GPDMA1_REQUEST_ADC2,1,high,Fixed ownership; bounded sensor transaction
flight,GPDMA2,0,GPDMA2_REQUEST_USART3_RX,25,low,Bounded descriptor; NOR direction switched between transactions
flight,GPDMA2,1,GPDMA2_REQUEST_USART3_TX,26,low,Bounded descriptor; NOR direction switched between transactions
flight,GPDMA2,6,GPDMA2_REQUEST_OCTOSPI1,57,low,Bounded descriptor; NOR direction switched between transactions
comms,GPDMA1,0,GPDMA1_REQUEST_USART3_RX,25,normal,Fixed ownership
comms,GPDMA1,1,GPDMA1_REQUEST_USART3_TX,26,normal,Fixed ownership
comms,GPDMA1,2,GPDMA1_REQUEST_USART1_RX,21,normal,Fixed ownership
comms,GPDMA1,3,GPDMA1_REQUEST_USART1_TX,22,normal,Fixed ownership
comms,GPDMA1,4,GPDMA1_REQUEST_SPI1_RX,6,normal,Fixed ownership
comms,GPDMA1,5,GPDMA1_REQUEST_SPI1_TX,7,normal,Fixed ownership
```
