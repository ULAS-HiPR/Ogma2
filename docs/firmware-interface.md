# Firmware interface

**2 November 2026.** The hardware interface for Ogma 2's two firmware images: every
pin by function, the sequences that touch hardware, and the budgets. It replaces
the [7 September handoff](archive/firmware-handoff-2026-09-07.md), which
described the 8 September CAD and had three layers of later changes stacked on
top. Where this page and [decisions.md](../decisions.md) disagree, the decisions
win; the [capture specification](architecture/schematic-capture-spec.md) has the
circuit detail. No target firmware exists yet. Anav owns the firmware.

## What changed since the 7 September handoff

| Change | Decision | What firmware does differently |
| --- | --- | --- |
| Two images: flight and comms; comms is an H563RIT6 (LQFP64) | D-6.12, D1 | Same core and build flags; comms pins from the 64-pad map |
| Sensors have no power enables; each has a 47 Ω supply link | D-6.6, D-2Nov.3 | Recover by clocking SCL and soft reset; park a dead sensor's pins |
| No one-shots or permit gates; a low side per channel again | D-6.2, D-2Nov.1 | Firmware bounds every pulse; fires in a four-step sequence; runs the pad self-tests |
| Staging latch and its own arm | D-7.1, D-7.2 | Set a new flight with PD15 only while staging is disarmed |
| Power hold | D-6.3, D-2Nov.4 | Assert at launch detect; re-assert within 50 ms of a reset in flight; release at LANDED or the time cap |
| Magnetometer on I²C3 | D-2Nov.11 | 100 Hz, logged, non-essential |
| Recording from launch detect | D-6.9 | Low-rate pad log, RAM pre-trigger, full rate from launch detect |
| Pad datum, ground-test mode, pad telemetry | D-2Nov.10 | See [Recovery logic](architecture/10-recovery-logic.md) |
| What CAN carries | D-2Nov.9 | Permissions, mode, slow state, health and stale-safe commands only |
| Rail power from the umbilical | D-2Nov.7 | Report which source is live |

## Build target

Both MCUs are STM32H563: Cortex-M33, single-precision FPU, 2 MiB flash,
640 KiB RAM. Build with `-mcpu=cortex-m33 -mfpu=fpv5-sp-d16 -mfloat-abi=hard`.
Start at 128 MHz with legal 64 MHz peripheral kernels; each MCU has its own
16 MHz HSE, flight alone has the 32.768 kHz LSE for its RTC, and comms uses
HSI48 with CRS for USB. A compiled clock tree still has to prove the kernel
mux sources, VOS and flash wait states.

## Flight boot order

1. Record the reset cause and supply evidence before any library clears them.
2. Set `PWR_UCPDR.UCPD_DBDIS`. PA9 and PC9 are the UCPD dead-battery pins: until
   this bit is set, a high level on them switches pull-downs onto PB13 / PB14,
   the TDK IMU's SPI clock and data.
3. Keep every output in its safe state: fire and low-side pins low, services off.
   They are pulled down externally, so they're already safe at reset.
4. Read the checkpoint. If it's valid and says in flight, drive `FC_POWER_HOLD`
   high within 50 ms of reset, then restore phase, launch time and the frozen
   datum.
5. Start essential acquisition and the earned watchdog heartbeat. Nothing waits
   for a NOR scan, GNSS, CAN or USB.
6. Bring up services with PE8, then NOR, CAN and monitoring one at a time.

## Flight MCU pins

STM32H563VIT6, LQFP100. Pads in brackets. Every output below has an external
pull-down, so it's off at reset and power-off. Pins not listed are supplies,
ground, VCAP or unused.

**Outputs and arming**

| Signal | Pin | Direction | Notes |
| --- | --- | --- | --- |
| `PYRO1_FIRE` | PE7 (38) | Out | Channel 1 high side, straight to U6304 IN |
| `PYRO2_FIRE` | PE9 (40) | Out | Channel 2 high side, U6404 IN |
| `PYRO3_FIRE` | PE12 (43) | Out | Channel 3 high side, through the AND with the staging latch |
| `PYRO1_LS_SELECT` | PA9 (68) | Out | Channel 1 low side Q6301 |
| `PYRO2_LS_SELECT` | PA10 (69) | Out | Channel 2 low side Q6401 |
| `PYRO3_LS_SELECT` | PD14 (61) | Out | Channel 3 low side Q6501 |
| `RECOVERY_ARM_SENSE` | PC8 (65) | In | High = recovery energy present (armed) |
| `STAGING_ARM_SENSE` | PE15 (46) | In | `STAGE_ARM_INVALID`: high = staging disarmed, low = armed |
| `STAGE_INHIBIT_LATCHED` | PE14 (45) | In | Latch Q̄ through 1 kΩ: high = channel 3 inhibited |
| `NEW_FLIGHT_CLEAR_REQUEST` | PD15 (62) | Out | Rising edge sets the latch, only if staging is disarmed |

**Power and services**

| Signal | Pin | Direction | Notes |
| --- | --- | --- | --- |
| `FC_POWER_HOLD` | PE5 (4) | Out | Holds Burrito's and Churro's battery enables on in flight |
| `SERVICE_POWER_EN` | PE8 (39) | Out | Services domain (NOR, CAN, AUX, sounder); one restart per session |
| `NOR_EN` | PA11 (70) | Out | NOR local limiter |
| `CAN_POWER_EN` | PB1 (36) | Out | CAN local limiter |
| `FOINSE_RETURN_EN` | PA15 (77) | Out | Monitoring domain (Croí INA228 and Churro); enable standalone too |
| `SERVO_POWER_EN` | PB0 (35) | Out | Servo switch U6802 |
| `FLIGHT_COMMS_EN` | PA12 (71) | Out | Comms branch, on battery |
| `COMMS_RESET_REQUEST` | PB4 (90) | Out, open drain | Resets the comms MCU only |
| `NOR_RESET_REQUEST` | PD3 (84) | Out, open drain | NOR reset |
| `BRANCH_FAULT_N` | PD5 (86) | In, EXTI5 | Wired-OR fault from the local limiters: says something tripped, not which |

**Sensors and storage**

| Device | Bus and pins | Data-ready | Start setting |
| --- | --- | --- | --- |
| LSM6DSV16X | SPI1: PA5 SCK, PA6 MISO, PA7 MOSI, PA4 NCS (AF5) | PE0 (EXTI0) | 4 MHz; 960 Hz, ±16 g, ±4000°/s |
| ICM-42688-P | SPI2: PB13 SCK, PB14 MISO, PB15 MOSI, PB12 NCS (AF5) | PE3 (EXTI3) | 4 MHz; 1 kHz, ±16 g, ±2000°/s |
| ADXL375 | SPI3: PC10 SCK, PC11 MISO, PC12 MOSI, PD2 NCS (AF6) | PE4 (EXTI4) | 2 MHz, mode 3; 800 Hz, ±200 g |
| BMP390 | I²C1: PB6 SCL, PB7 SDA (AF4) | — | 400 kHz; 50 Hz |
| MS5607 | I²C2: PB10 SCL, PB3 SDA (AF4) | — | 400 kHz; OSR4096, 50 Hz |
| MMC5983MA | I²C3: PA8 SCL, PC9 SDA (AF4), address 0x30 | PE6 (EXTI6), optional | 400 kHz; BW = 01 (100 Hz, 0.6 mG) |
| MX66L2G45G NOR | OCTOSPI1 quad: PB2 CLK (AF9), PE11 NCS (AF6), PD11 / PD12 / PE2 / PD13 IO0–3 (AF9) | — | 16 MHz to start |

Check every AF number against ST DS14258 when the clock tree is built.

**Links, servos, monitoring, status**

| Function | Pins | Notes |
| --- | --- | --- |
| Inter-MCU UART | USART3: PD8 TX, PD9 RX (AF7) | 2 Mbaud 8N1 through the TXU0202 boundary |
| CAN to Fajita | FDCAN1: PD1 TX, PD0 RX (AF9); PB5 standby | Classical CAN, 500 kbit/s; TCAN3413 |
| Servos | TIM3 CH1 / CH2: PC6 / PC7 (AF2); LPTIM2 CH2: PD10 (AF3) | Servos 1 and 2 share a period; servo 3 has its own |
| Monitor bus | I²C4: PB8 SCL, PB9 SDA (AF6) | 100 kHz; INA228 0x40 (Croí), 0x41 (Churro PROP); ADS1115 0x48 |
| Watchdog | PD4 `SUPERVISOR_WDI` | Toggled only on earned essential progress |
| Readiness lamp | PD7 | Low or reset = red, high = green |
| Sounder | PD6 through Q9001 | Passive piezo; ground only, silent in flight |
| Debug | PA13 SWDIO, PA14 SWCLK; BOOT0 pulled down | Service only |
| Spare | PE10 (41), PE13 (44) | PC13 stays quiet (LSE erratum) |

**Analog**

| Signal | Pin | Channel |
| --- | --- | --- |
| Battery after the eFuse and shunt (÷5.42) | PA0 (23) | ADC1_INP0 |
| `FLIGHT_3V3` | PA1 (24) | ADC1_INP1 |
| Pyro rail / servo rail | PA2 (25) / PA3 (26) | ADC1_INP14 / ADC1_INP15 |
| Pyro current, channels 1–3 | PC0 / PC1 / PC2 (15–17) | ADC2_INP10–12 |
| Continuity, channels 1–3 | PC3 / PC4 / PC5 (18, 33, 34) | ADC1_INP13 / INP4 / INP8 |

Use calibrated VREFINT for absolute voltages; the ADC reference is the flight
rail itself.

## Comms MCU pins

STM32H563RIT6, LQFP64 ([64-pad map](architecture/proposed-comms-pinout.csv)).

| Function | Pins |
| --- | --- |
| Inter-MCU UART | USART3: PC10 TX, PC11 RX (AF7) |
| GNSS (MAX-M10S) | USART1: PA9 TX, PA10 RX (AF7); PA0 PPS (TIM2_CH1); PC5 reset (open drain); PB0 enable |
| Radio (Wio-LR2021) | SPI1: PA5 SCK, PA6 MISO, PA7 MOSI (AF5), PA4 NSS; PC0 reset, PC1 BUSY, PC2 IRQ (DIO5); PB1 enable. PC3 / PC4 unused, held low |
| USB | PA11 DM, PA12 DP; PB2 VBUS sense |
| Source status | PA1 `CC_USB_CONFIG_OK` (out), PA2 `CC_BAT_VALID` (in), PB5 `CC_BRANCH_FAULT_N` (in) |
| Status and debug | PB4 amber lamp; PA13 / PA14 SWD; PB3 SWO |

Comms has no path to flight reset, the arms or any output, and never gets one.
Set `UCPD_DBDIS` here too.

## Pyro outputs

**Fire one channel:**

1. Low side on (`PYROn_LS_SELECT` high).
2. High side on (`PYROn_FIRE` high) for the configured pulse.
3. High side off.
4. Low side off.

Wait about 1 ms between steps to start with; set the gaps on the bench. One
channel at a time. Every pulse is bounded by the per-flight configuration;
nothing in hardware shortens it now. Channel 3's high side also needs the latch
set, and the latch is cleared by any flight reset.

**Before arming (arms open):** for each channel, read continuity with both
switches open (expect the mid-level reading), close the low side alone (expect
≈0), reopen it (expect the mid-level reading again). An igniter that reads open
makes that channel's check inconclusive; report it.

**After arming:** a return node near the armed rail means that channel's high
side is leaking or shorted. Never close its low side; report it. Never run the
low-side self-test with an arm closed.

**Continuity reading:** the return node is divided by 5.42 to the ADC. Classify
each reading as present, open (≈0 V), low side closed (0 V), or high side
leaking (near the armed rail), and send both the class and the raw value. The
test current comes from the services rail, so services must be on.

**Staging latch:** pulse PD15 only on the pad, with staging disarmed (PE15
high). Then PE14 reads low (eligible). Any reset or power-up sets PE14 high
(inhibited), and only a new PD15 edge while disarmed clears it. A profile can't
move ignition onto channels 1 or 2.

## Power hold

- Drive `FC_POWER_HOLD` high at launch detect, never earlier. On the pad, J103
  and Churro's enable must still switch the vehicle off.
- Release it by driving PE5 low (not high-Z), at LANDED plus the configured
  delay, or at the configured maximum flight time, whichever comes first.
- After any reset, if the checkpoint says in flight, drive it high within 50 ms.
  The RC keeps the enables on for ≥1 s, longer than the worst-case 550 ms restart.
- Never in ground-test mode.

## Sensors

- No sensor has a power enable. Recover a hung I²C bus by clocking SCL; recover
  a sensor with its soft-reset command. Bound the retries.
- A sensor you give up on is **dead for the session**: park its pins. Drive its
  SPI SCK, MOSI and NCS low or set them to analog; set its I²C pins to analog.
  Otherwise the MCU can feed a dead or shorted sensor through the 22 Ω damping.
- Each sensor keeps its own timestamp, axis transform, validity and clipping
  flag. Rates are allocations, not measurements.
- The magnetometer is non-essential: it never earns the watchdog heartbeat and
  never gates the estimator or a flight event. Run its SET/RESET as the data
  sheet describes, log every sample at 100 Hz, and mark it unavailable on any
  fault. Its calibration comes from the assembled bay.

## Recording, telemetry and service

- Pad: low-rate log. Keep ≈1 s of full-rate samples (or ≈10 s decimated) in a
  RAM ring and commit it at launch detect; full rate from launch detect to LANDED
  plus a tail. Erase ahead only before launch detect (D-6.9).
- One commit = 15 data pages plus a footer per 4 KiB sector; accept only a valid
  CRC, length, epoch and sequence; drop torn tails.
- Pad telemetry at 1 Hz from arming to launch detect: both arm senses,
  continuity per channel (class and raw), the staging latch, AV pack voltage,
  bus voltage, live source, phase, faults and configuration identity. The same
  frame goes to USB.
- Ground-test mode: a configuration flag loaded over USB and shown in readback;
  launch declared over USB; barometric logic alone; recovery channels only; no
  power hold; cleared at power-off; every use logged.
- USB service: bounded 4 KiB chunks with credits; never blocks acquisition; a
  timed-out flight reply is unknown, never the last value.

Event rules: [Recovery logic](architecture/10-recovery-logic.md). Format:
[Recording and service](architecture/justifications/recording-and-service.md).

## Links

- **Inter-MCU UART:** 2 Mbaud 8N1; frames ≤512-byte payload with length, type,
  version, sequence, epoch and CRC. Routine telemetry ≤20 kB/s; comms
  diagnostics ≤1 KiB/s. Comms is an untrusted producer even when its CRC passes.
  An 8 Mbaud disarmed service mode is a later target.
- **CAN (D-2Nov.9):** carries permissions and mode, slow state that stays valid
  through a 550 ms restart, health, and commands the receiver drops to safe when
  stale. No sensor streams, no loops at loop rate. Classical 500 kbit/s for
  Rev A; the message contract is written with Fajita's owner. A closed-loop
  actuator node, if added, takes IDs below Burrito's and Fajita's.

## Monitoring

- **INA228** (Croí 0x40, Churro PROP 0x41): one parameterised driver; check
  identity and read back configuration. 5 mΩ shunts; ADCRANGE = 0; current LSB
  100 µA; `SHUNT_CAL` = 6554. Continuous shunt and bus conversions, 150 µs,
  averaging 16. Read current at 100 Hz. Sign-extend the 20-bit values
  correctly. The Croí INA's bus voltage is `BAT_EFUSE_IN`.
- **ADS1115** (0x48 on Churro): ±4.096 V, 128 SPS single-shot. Voltages at 10 Hz,
  temperatures at 2 Hz; wait 100 ms after the probe bias starts. The AV voltage
  channel now reads the AV pack (D-2Nov.7). The source is the umbilical when the
  Croí bus voltage sits clearly above the AV pack; set the threshold on the
  bench and report "unclear" when the two are close.
- Monitoring can vanish (AUX off, bus stuck): it degrades evidence, never
  flight. No retry loop may stall the essential loop. Probe and conversion
  details: [Churro monitoring](architecture/justifications/churro-monitoring.md).

## Budgets

| Item | Value |
| --- | --- |
| Clock | 128 MHz to start |
| Essential loop | 1 kHz; ≤700 µs of essential work per 1 ms, 30% reserve |
| Estimation and phase policy | 200 Hz |
| Watchdog | Earned 40 ms heartbeat; TPS3430 reset 170–230 ms |
| Restart targets | Software reset 100 ms; 400 ms from watchdog assertion; 550 ms from the last earned heartbeat |
| Protected RAM | SRAM2 64 KiB and ECC SRAM3 256 KiB for critical state; SRAM1 for disposable buffers |
| Log staging | 128 KiB in RAM |
| Recording rate | 96,672 B/s plus ≈1,600 B/s for the magnetometer |
| Checkpoints | Two 1 KiB slots in backup SRAM; VBAT held up by 100 µF |
| Download | ≥22.4 min for a full 256 MiB at 2 Mbaud |

These are allocations, not measurements.

## What to build first

1. A non-actuating clock, pin and linker skeleton: reset-cause capture, the
   UCPD setting, SWD recovery, ECC initialisation.
2. The six-sensor timestamped recorder with validity flags, pre-erased NOR and
   interruption recovery. No flight thresholds yet.
3. A bounded comms stub, malformed-frame floods and power-off peer tests; then
   real GNSS, radio and USB behind the same boundary.
4. The checkpoint and reset campaign, with the power hold, and independent
   observation of the hardware inhibits.
5. Pad self-tests and pad telemetry on inert loads.
6. Only then, with that evidence and the first-PCBA inert tests, mission
   recovery software and its own review.

Test campaigns and gates: [11 Verification](architecture/11-verification.md).
Retained-state rules: [reset contract](../interfaces/reset-recovery-contract.md).
