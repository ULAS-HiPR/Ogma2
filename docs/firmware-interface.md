# Firmware interface

**2 November 2026, amended 18 and 22 November.** The hardware interface for Ogma 2's two firmware images: every
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
| Staging latch and its own arm | D-7.1, D-7.2 | Set a new flight with PD7 (PD15 until D-22Nov.25) only while staging is disarmed |
| Power hold | D-6.3, D-2Nov.4, D-2Nov.18 | Assert at launch detect; re-assert within 50 ms of a reset in flight; release at LANDED or the time cap |
| Magnetometer on I²C3 | D-2Nov.11 | 100 Hz, logged, non-essential |
| Recording from launch detect | D-6.9 | Low-rate pad log, RAM pre-trigger, full rate from launch detect |
| Pad datum, ground-test mode, pad telemetry | D-2Nov.10, D-2Nov.16 | See [Recovery logic](architecture/10-recovery-logic.md); any reset ends ground-test mode |
| No deployment below 100 m | D-2Nov.13 | Gate the drogue and main, primary and backup, on 100 m above the pad datum |
| What CAN carries | D-2Nov.9 | Permissions, mode, slow state, health and stale-safe commands only |
| Rail power from the umbilical | D-2Nov.7 | Report which source is live |
| CAN bus 2 to the active board; pins moved | D-5Nov.3 | FDCAN2 on PA10 / PB5; one standby for both buses (PD15 since D-22Nov.25); channel 2's low side and the recovery arm sense moved |
| Authority over the active board | D-5Nov.2 | Send Safe, Active or Abort at a fixed 10–20 Hz with a counter; Active only after the dormancy |
| Main altitude limit at EuRoC | D-18Nov.5 | Readback checks the main altitude is at most 450 m above the pad |
| No servos; freed pins; sounder at arming | D-19Nov.2–D-19Nov.4 | No servo timers or enable; a timing strobe, a reset memory read at boot step 1, three spare pads as inputs with pull-downs (pins since D-22Nov.25 below); the sounder beeps continuity and state at arming |
| Board temperatures | B-30 (LV-0510) | Log the flight MCU die, one IMU and one barometer temperature at 1 Hz on the pad (in pad telemetry) and 10 Hz in flight; pad telemetry warns above [60] °C |
| Charge state | D-21Nov.2, C-15 | Read each charger's state over I²C4: charging, done, temperature hold, fault. Cross-check against the pack-voltage trend. Burrito controls nothing in the charge path |
| Pack voltages | C-17, C-22, C-23 | AV and actuator packs on their pack side (readable on the umbilical), the CATS cell, both NTCs; pad telemetry shows each, with the live source |
| No flashing on the rail | D-21Nov.4 | USB service at the av-bay only |
| IREC radio behaviour | B-27 (proposed) | Transmit off by default; on once the recovery arm closes on the pad, or by a flag set over USB; channel set over USB |
| Checkpoint first at launch detect; missed-launch catch in PAD | D-19Nov.1 | **Must, before first flight.** Write the in-flight checkpoint before anything else at launch detect. In PAD with an arm closed, run the missed-launch catch (proposed: 50 m above the datum for 2 s) into the armed row. A pad pressure transient can't make it fire the main |
| Pins re-allocated for the placement | D-22Nov.25 | 36 flight pins and 12 comms pins moved; three spare pads moved and renamed. See [Pin changes](#pin-changes-d-22nov25) |

## Pin changes (D-22Nov.25)

Pins moved on 22 November so each sits nearer what it connects to on the placed board, and to clear four reset-state faults: `FOINSE_RETURN_EN` on PA15, whose reset pull-up switched Foinse's aux rail on at every power-up until firmware ran, and three outputs on pins the ROM bootloader drives (PA9, PA11, PA12). Seán agreed the swaps; capture step 19 made them. The tables below are as captured; the pin maps in [libraries/inputs](../hardware/croi2/libraries/inputs) are the record.

**Flight MCU (U201)**

| Signal | Was | Now | Function on the new pin | Why |
| --- | --- | --- | --- | --- |
| `ADC_FLIGHT_3V3` | PA1 (24) | PC4 (33) | ADC1_INP4 (was ADC1_INP1) | nearer what it connects to |
| `ADC_PYRO2_CONTINUITY` | PC4 (33) | PA1 (24) | ADC1_INP1 (was ADC1_INP4) | nearer what it connects to |
| `ADC_PYRO3_CONTINUITY` | PC5 (34) | PA0 (23) | ADC1_INP0 (was ADC1_INP8) | nearer what it connects to |
| `ADC_VEHICLE_VBAT` | PA0 (23) | PC5 (34) | ADC1_INP8 (was ADC1_INP0) | nearer what it connects to |
| `BRANCH_FAULT_N` | PD5 (86) | PE5 (4) | GPIO, EXTI5 | nearer what it connects to |
| `BUZZER_DRIVE` | PD6 (87) | PD5 (86) | GPIO | nearer what it connects to |
| `CAN_POWER_EN` | PB1 (36) | PD10 (57) | GPIO | nearer what it connects to |
| `CAN_STB` | PE10 (41) | PD15 (62) | GPIO | nearer what it connects to |
| `COMMS_RESET_REQUEST` | PB4 (90) | PB2 (37) | GPIO | nearer what it connects to |
| `FC_POWER_HOLD` | PE5 (4) | PE14 (45) | GPIO | nearer what it connects to |
| `FLIGHT_COMMS_EN` | PA12 (71) | PB0 (35) | GPIO | the ROM bootloader drives PA12 as USB D+ |
| `FLIGHT_STATUS_LED1` | PD7 (88) | PB12 (51) | GPIO | nearer what it connects to |
| `FOINSE_RETURN_EN` | PA15 (77) | PE12 (43) | GPIO | PA15's reset pull-up held U7001 and U7002 on until firmware ran |
| `HG_INT1` | PE4 (3) | PB4 (90) | GPIO, EXTI4 | nearer what it connects to |
| `MAG_INT` | PE6 (5) | PD3 (84) | GPIO, EXTI3 | nearer what it connects to |
| `NEW_FLIGHT_CLEAR_REQUEST` | PD15 (62) | PD7 (88) | GPIO | nearer what it connects to |
| `NOR_CLK` | PB2 (37) | PA3 (26) | OCTOSPI1_CLK (AF3) (was OCTOSPI1_CLK AF9) | nearer what it connects to |
| `NOR_EN` | PA11 (70) | PE3 (2) | GPIO | the ROM bootloader drives PA11 as USB D- |
| `NOR_RESET_REQUEST` | PD3 (84) | PE6 (5) | GPIO | nearer what it connects to |
| `PYRO1_LS_SELECT` | PA9 (68) | PD4 (85) | GPIO | the ROM bootloader drives PA9 as USART1 TX |
| `PYRO2_FIRE` | PE9 (40) | PE15 (46) | GPIO | nearer what it connects to |
| `PYRO2_LS_SELECT` | PC8 (65) | PB1 (36) | GPIO | PC8 carries trace data (TRACED1) |
| `PYRO3_FIRE` | PE12 (43) | PE9 (40) | GPIO | PE12 sits beside the recovery arm sense on PE13 |
| `PYRO3_LS_SELECT` | PD14 (61) | PC6 (63) | GPIO | PD14 sits beside the new-flight request on PD15 |
| `RESET_MEMORY` | PA3 (26) | PA4 (29) | GPIO | nearer what it connects to |
| `STAGE_INHIBIT_LATCHED` | PE14 (45) | PE0 (97) | GPIO | nearer what it connects to |
| `STAGING_ARM_SENSE` | PE15 (46) | PD6 (87) | GPIO | nearer what it connects to |
| `ST_DRDY` | PE0 (97) | PC7 (64) | GPIO, EXTI7 | nearer what it connects to |
| `ST_NCS` | PA4 (29) | PD14 (61) | GPIO | nearer what it connects to |
| `SUPERVISOR_WDI` | PD4 (85) | PE4 (3) | GPIO | nearer what it connects to |
| `TDK_DRDY` | PE3 (2) | PA15 (77) | GPIO, EXTI15 | nearer what it connects to |
| `TDK_NCS` | PB12 (51) | PC8 (65) | GPIO | nearer what it connects to |
| `TP_PA11` (was `TP_PD10`) | PD10 (57) | PA11 (70) | GPIO | a spare pad, renamed: the bootloader may drive this pin |
| `TP_PA12` (was `TP_PC6`) | PC6 (63) | PA12 (71) | GPIO | a spare pad, renamed: the bootloader may drive this pin |
| `TP_PA9` (was `TP_PC7`) | PC7 (64) | PA9 (68) | GPIO | a spare pad, renamed: the bootloader may drive this pin |
| `TP_STROBE` | PB0 (35) | PE10 (41) | GPIO | nearer what it connects to |

**Comms MCU (U401)**

| Signal | Was | Now | Function on the new pin | Why |
| --- | --- | --- | --- | --- |
| `CC_BAT_VALID` | PA2 (16) | PC2 (10) | GPIO | nearer what it connects to |
| `CC_BRANCH_FAULT_N` | PB5 (57) | PC1 (9) | GPIO, EXTI1 | nearer what it connects to |
| `CC_COMMS_TO_FLIGHT` | PC10 (51) | PB10 (29) | USART3_TX (AF7) | nearer what it connects to |
| `COMMS_STATUS_LED` | PB4 (56) | PC0 (8) | GPIO | nearer what it connects to |
| `GNSS_EN` | PB0 (26) | PC5 (25) | GPIO | nearer what it connects to |
| `GNSS_RESET_N` | PC5 (25) | PA3 (17) | GPIO | nearer what it connects to |
| `GNSS_RX` | PA10 (43) | PB15 (36) | USART1_RX (AF4) (was USART1_RX AF7) | nearer what it connects to |
| `LORA_BUSY` | PC1 (9) | PA4 (20) | GPIO | nearer what it connects to |
| `LORA_DIO1` | PC2 (10) | PB0 (26) | GPIO, EXTI0 | nearer what it connects to |
| `LORA_NCS` | PA4 (20) | PB12 (33) | GPIO | nearer what it connects to |
| `LORA_RESET_N` | PC0 (8) | PB2 (28) | GPIO | nearer what it connects to |
| `USB_VBUS_PRESENT` | PB2 (28) | PA1 (15) | GPIO | nearer what it connects to |

Now unused (no-connect, set to analog): PA2 (16), PA10 (43), PC10 (51), PB4 (56), PB5 (57).

PA15 and PB4 come out of reset as JTDI and NJTRST with internal pull-ups (DS14258 table 14, note 7). Set them to GPIO inputs before reading `TDK_DRDY` and `HG_INT1`; both lines are driven by their sensors, so the pull-ups do no harm. PA9, PA11 and PA12 now carry only the spare pads: in the bootloader they may be driven, and nothing else is there.

## Build target

Both MCUs are STM32H563: Cortex-M33, single-precision FPU, 2 MiB flash,
640 KiB RAM. Build with `-mcpu=cortex-m33 -mfpu=fpv5-sp-d16 -mfloat-abi=hard`.
Start at 128 MHz with legal 64 MHz peripheral kernels; each MCU has its own
16 MHz HSE, flight alone has the 32.768 kHz LSE for its RTC, and HSI48 with CRS
is the candidate USB clock on comms. A compiled clock tree still has to prove
the kernel mux sources, VOS and flash wait states.

## Flight boot order

1. Record the reset cause and supply evidence before any library clears them,
   and read the reset memory on PA4: a pin reset with it low means the watchdog
   fired; with it high, a supply dip; the power-on flag means power-on (D-19Nov.3).
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

STM32H563VIT6, LQFP100 (as captured: [flight map](../hardware/croi2/libraries/inputs/flight-pinout.csv)). Pads in brackets. Every output below is off at reset
and power-off: pulled down externally, or open drain and released. Pins not
listed are supplies, ground, VCAP or unused.

**Outputs and arming**

| Signal | Pin | Direction | Notes |
| --- | --- | --- | --- |
| `PYRO1_FIRE` | PE7 (38) | Out | Channel 1 high side, straight to U6304 IN |
| `PYRO2_FIRE` | PE15 (46) | Out | Channel 2 high side, U6404 IN |
| `PYRO3_FIRE` | PE9 (40) | Out | Channel 3 high side, through the AND with the staging latch |
| `PYRO1_LS_SELECT` | PD4 (85) | Out | Channel 1 low side Q6301 |
| `PYRO2_LS_SELECT` | PB1 (36) | Out | Channel 2 low side Q6401 |
| `PYRO3_LS_SELECT` | PC6 (63) | Out | Channel 3 low side Q6501 |
| `RECOVERY_ARM_SENSE` | PE13 (44) | In | High = recovery energy present (armed) |
| `STAGING_ARM_SENSE` | PD6 (87) | In | `STAGE_ARM_INVALID`: high = staging disarmed, low = armed |
| `STAGE_INHIBIT_LATCHED` | PE0 (97) | In | Latch Q̄ through 1 kΩ: high = channel 3 inhibited |
| `NEW_FLIGHT_CLEAR_REQUEST` | PD7 (88) | Out | Rising edge sets the latch, only if staging is disarmed |

**Power and services**

| Signal | Pin | Direction | Notes |
| --- | --- | --- | --- |
| `FC_POWER_HOLD` | PE14 (45) | Out | Holds Burrito's and Churro's battery enables on in flight |
| `SERVICE_POWER_EN` | PE8 (39) | Out | Services domain (NOR, CAN, AUX, sounder); one restart per session |
| `NOR_EN` | PE3 (2) | Out | NOR local limiter |
| `CAN_POWER_EN` | PD10 (57) | Out | CAN local limiter |
| `FOINSE_RETURN_EN` | PE12 (43) | Out | Monitoring domain (Croí INA228 and Churro); enable standalone too |
| `TP_STROBE` | PE10 (41) | Out | Timing strobe: toggle at loop start, at reset recovery and at each firing step (D-19Nov.3) |
| `FLIGHT_COMMS_EN` | PB0 (35) | Out | Comms branch, on battery |
| `COMMS_RESET_REQUEST` | PB2 (37) | Out, open drain | Resets the comms MCU only |
| `NOR_RESET_REQUEST` | PE6 (5) | Out, open drain | NOR reset |
| `BRANCH_FAULT_N` | PE5 (4) | In, EXTI5 | Wired-OR fault from the local limiters: says something tripped, not which |

**Sensors and storage**

| Device | Bus and pins | Data-ready | Start setting |
| --- | --- | --- | --- |
| LSM6DSV32X (D-21Nov.16) | SPI1: PA5 SCK, PA6 MISO, PA7 MOSI (AF5); PD14 NCS | PC7 (EXTI7) | 4 MHz; 960 Hz, ±16 g, ±4000°/s |
| ICM-42688-P | SPI2: PB13 SCK, PB14 MISO, PB15 MOSI (AF5); PC8 NCS | PA15 (EXTI15) | 4 MHz; 1 kHz, ±16 g, ±2000°/s |
| ADXL375 | SPI3: PC10 SCK, PC11 MISO, PC12 MOSI (AF6); PD2 NCS | PB4 (EXTI4) | 2 MHz, mode 3; 800 Hz, ±200 g |
| BMP390 | I²C1: PB6 SCL, PB7 SDA (AF4) | — | 400 kHz; 50 Hz |
| MS5607 | I²C2: PB10 SCL, PB3 SDA (AF4) | — | 400 kHz; OSR4096, 50 Hz |
| MMC5983MA | I²C3: PA8 SCL, PC9 SDA (AF4), address 0x30 | PD3 (EXTI3), optional | 400 kHz; BW = 01 (100 Hz, 0.6 mG) |
| MX66L2G45G NOR | OCTOSPI1 quad: PA3 CLK (AF3), PE11 NCS (AF6), PD11 / PD12 / PE2 / PD13 IO0–3 (AF9) | — | 16 MHz to start |

Check every AF number against ST DS14258 when the clock tree is built.

**Links, monitoring, status**

| Function | Pins | Notes |
| --- | --- | --- |
| Inter-MCU UART | USART3: PD8 TX, PD9 RX (AF7) | 2 Mbaud 8N1 through the TXU0202 boundary |
| CAN bus 1, to Fajita | FDCAN1: PD1 TX, PD0 RX (AF9); PD15 standby, shared with bus 2 | Classical CAN, 500 kbit/s; TCAN3413 |
| CAN bus 2, to the active board | FDCAN2: PA10 TX, PB5 RX (AF9, checked against ST's open pin data on 21 Nov); PD15 standby, shared | Classical CAN, 500 kbit/s; second TCAN3413 (D-5Nov.3) |
| Spare test pads | PA9, PA11, PA12 (`TP_PA9`, `TP_PA11`, `TP_PA12`) | Inputs with pull-downs. The ROM bootloader drives these pins, so they carry a pad and nothing else (D-19Nov.3, D-22Nov.25) |
| Monitor bus | I²C4: PB8 SCL, PB9 SDA (AF6) | 100 kHz; INA228 0x40 (Croí), 0x41 (Churro PROP); INA237 0x44 (Churro ACT); ADS1115 0x48, 0x49; TCA9535 0x20 (Churro charger status) |
| Watchdog | PE4 `SUPERVISOR_WDI` | Toggled only on earned essential progress |
| Readiness lamp | PB12 | Low or reset = red, high = green |
| Sounder | PD5 through Q9001 | Magnetic transducer, PUI SMT-1028-T-2-R (D-21Nov.20): drive a 2.83 kHz square wave, its rated frequency; ground only, silent in flight |
| Debug | PA13 SWDIO, PA14 SWCLK; BOOT0 pulled down | Service only |
| Spare | None since D-5Nov.3 | PC13 stays quiet (LSE erratum) |

**Analog**

| Signal | Pin | Channel |
| --- | --- | --- |
| Battery after the eFuse and shunt (÷5.42) | PC5 (34) | ADC1_INP8 |
| `FLIGHT_3V3` | PC4 (33) | ADC1_INP4 |
| Recovery armed rail (`RECOVERY_ARMED_VBAT`, ÷5.42; staging has no ADC, only its arm sense) / reset memory `RESET_MEMORY` | PA2 (25) / PA4 (29) | ADC1_INP14 / digital input, read at boot (D-19Nov.3) |
| Pyro current, channels 1–3 | PC0 / PC1 / PC2 (15–17) | ADC2_INP10–12 |
| Continuity, channels 1–3 | PC3 / PA1 / PA0 (18, 24, 23) | ADC1_INP13 / INP1 / INP0 |

Use calibrated VREFINT for absolute voltages; the ADC reference is the flight
rail itself. The continuity inputs have no filter capacitor and a source of
about 8 kΩ, so give them a long sampling time (start at 47.5 cycles and check it
against the reference manual's source-impedance table); the rail dividers have
10 nF at their scaled node.

## Comms MCU pins

STM32H563RIT6, LQFP64 ([64-pad map](architecture/proposed-comms-pinout.csv); as captured: [comms map](../hardware/croi2/libraries/inputs/comms-pinout.csv)).

| Function | Pins |
| --- | --- |
| Inter-MCU UART | USART3: PB10 TX, PC11 RX (AF7) |
| GNSS (MAX-M10S) | USART1: PA9 TX (AF7), PB15 RX (AF4); PA0 PPS (TIM2_CH1); PA3 reset (open drain); PC5 enable |
| Radio (Wio-LR2021) | SPI1: PA5 SCK, PA6 MISO, PA7 MOSI (AF5), PB12 NSS; PB2 reset, PA4 BUSY, PB0 IRQ (DIO5, EXTI0); PB1 enable. PC3 / PC4 unused, held low |
| USB | PA11 DM, PA12 DP; PA1 VBUS sense |
| Source status | PC2 `CC_BAT_VALID` (in), PC1 `CC_BRANCH_FAULT_N` (in, EXTI1). PA2, PA10, PC10, PB4 and PB5 unused since D-22Nov.25 |
| Status and debug | PC0 amber lamp; PA13 / PA14 SWD; PB3 SWO |

Comms has no path to flight reset, the arms or any output, and never gets one.
Set `UCPD_DBDIS` here too.

## Pyro outputs

**Fire one channel:**

1. Low side on (`PYROn_LS_SELECT` high).
2. High side on (`PYROn_FIRE` high) for the configured pulse.
3. High side off.
4. Low side off.

Wait about 1 ms between steps to start with; set the gaps on the bench. After
step 3, that channel's current sense should fall to zero. If it doesn't, the
high side is stuck on: step 4 still breaks the circuit, so do it, then report
the channel and never use it again that session. One channel at a time. Every pulse is bounded by the per-flight configuration;
nothing in hardware shortens it now. Channel 3's high side also needs the latch
set, and the latch is cleared by any flight reset.

**Before arming (arms open):** for each channel, read continuity with both
switches open (expect the mid-level reading), close the low side alone (expect
≈0), reopen it (expect the mid-level reading again). While one low side is
closed, the other channels' readings must not move; if one drops too, its low
side is bridged or shorted to the one under test. A bridge from a neighbouring
pad shows only while that neighbour is high, so run the check with every
neighbour live (D-22Nov.25): channel 1's low side (PD4) sits between the
magnetometer's data-ready (PD3) and the sounder (PD5), channel 2's (PB1)
between the comms enable (PB0) and the comms reset request (PB2), channel 3's
(PC6) between the CAN standby (PD15) and the LSM6DSV32X's data-ready (PC7). So:
sensors streaming, sounder on, comms powered, and CAN both in standby and awake.
An igniter that reads open makes that channel's check inconclusive; report it.

**After arming:** a return node above its disarmed reading, anywhere up to the
armed rail, means that channel's high side conducts: leaking or shorted. Never
close its low side; report it. A partial leak counts: closing the low side
removes the return resistors and lets the leak current rise. Set the margin on
the bench. Never run the low-side self-test with an arm closed.

Two things move that reading without any leak, so the margin has to cover
them. With the arm open, part of the test current runs back through each
TPS1H100's body diode into the unpowered armed rail (once R6310 / R6410 are
fitted), so the disarmed reading sits about 5% low: ≈0.25 V at the ADC instead
of ≈0.27 V with the 3.9 kΩ legs (D-2Nov.14). With the arm closed, DIAG_EN is
tied high, so the TPS1H100 runs its off-state open-load check and its output
leaks up to 50 µA at 125 °C into the test network: up to ≈+30 mV at the ADC hot,
a few millivolts at room temperature. Compare the armed reading with the armed
level measured on the bench across temperature, not only with the disarmed one.

**Continuity reading:** the return node reaches the ADC divided by 5.86 (the
22.1 + 22.1 / 10 kΩ divider with R6714 / R6724 / R6734's 100 kΩ in parallel
while U6901 is on); the rail dividers are ÷5.42. Classify each reading as
present (mid-level), zero, or high side leaking (above the disarmed reading, up
to the armed rail), and send both the class and the raw value. Zero means an
open igniter or harness when the low side is commanded open, and a working low
side when it's commanded closed; zero with the low side open on a channel that
read present before can also mean a shorted low side. The test current comes
from the services rail, so services must be on.

**Staging latch:** pulse PD7 only on the pad, with staging disarmed (PD6
high). Then PE0 reads low (eligible). Any reset or power-up sets PE0 high
(inhibited), and only a new PD7 edge while disarmed clears it. A profile can't
move ignition onto channels 1 or 2.

## Power hold

- Drive `FC_POWER_HOLD` high at launch detect, never earlier. On the pad, J103
  and Churro's enable must still switch the vehicle off.
- Release it by driving PE14 low (not high-Z), at LANDED plus the configured
  delay, or at the configured maximum flight time, whichever comes first.
- After any reset, if the checkpoint says in flight, drive it high within 50 ms.
  The RC keeps the enables on for about 1 s (≥0.75 s worst case, D-2Nov.18),
  longer than the worst-case 550 ms restart.
- In flight, write PE14 high again every essential-loop cycle, so a stray port-E
  write can't drop it for longer than one cycle.
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
- At arming, the sounder beeps continuity and state, ground only and silent in
  flight, so the crew at the panel hears go or no-go (D-19Nov.4).
- Ground-test mode: a configuration flag loaded over USB, shown in readback and
  held in RAM only; launch declared over USB; barometric logic alone; recovery
  channels only; no power hold; cleared at power-off and at any reset, and a
  checkpoint written in ground-test mode never reads as in flight (D-2Nov.16);
  every use logged.
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
  Rev A on both buses. Bus 1's message contract is written with Fajita's
  owner. Bus 2 carries one authority message to the active board at a fixed
  10–20 Hz with a counter: Safe (the default), Active (only after the
  field-adjustable boost dormancy, at least 1500 m AGL without flight history)
  or Abort (neutral until power-cycled on the ground); the board treats stale or
  missing as Safe (D-5Nov.2). Slow flight state may ride alongside; the board's
  health comes back and is logged. Frame layout, counter width, rate and stale
  timeout are still to set.

## Monitoring

- **INA228** (Croí 0x40, Churro PROP 0x41): one parameterised driver; check
  identity and read back configuration. 5 mΩ shunts; ADCRANGE = 0; current LSB
  100 µA; `SHUNT_CAL` = 6554. Continuous shunt and bus conversions, 150 µs,
  averaging 16. Read current at 100 Hz. Sign-extend the 20-bit values
  correctly. The Croí INA's bus voltage is `BAT_EFUSE_IN`. Churro PROP's INA228
  moves onto its LM5069 stage's 2.5 mΩ shunt (D-22Nov.4): `SHUNT_CAL` = 3277 at
  the same LSB.
- **INA237** (Churro ACT 0x44, D-22Nov.4): the same 2.5 mΩ stage shunt. Its
  configuration is written at Churro's capture, from its datasheet.
- **TCA9535** (0x20 on Churro, D-22Nov.5): read the two input-port registers
  only. Never write its configuration or output registers: every pin stays an
  input (IR-7). Bits: each charger's STAT1, STAT2 and PG, each temperature
  gate, the branch faults; the map is fixed at capture.
- **ADS1115** (0x48 and 0x49 on Churro; 0x49 reads the CATS cell and ACT's key
  state, D-22Nov.4): ±4.096 V, 128 SPS single-shot. Voltages at 10 Hz,
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
