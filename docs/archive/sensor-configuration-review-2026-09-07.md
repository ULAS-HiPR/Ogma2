# Sensor configuration review for Anav

7 September 2026. Checklist subsequently accepted by Seán; not a new firmware task or pin-map
revision. The [accepted handoff](firmware-handoff-2026-09-07.md) remains controlling.
Anav chooses the implementation. No firmware was written in this review.

## Keep the existing sensors

| Device / owner | Existing starting point | Check before treating data as valid |
| --- | --- | --- |
| ST LSM6DSV16X, flight SPI1 | 4 MHz SPI; 960 Hz; ±16 g / ±4000°/s; DRDY | Identity, read-back config, fresh samples, selected filter delay and clipping |
| TDK ICM-42688-P, flight SPI2 | 4 MHz; 1 kHz; ±16 g / ±2000°/s; DRDY | Identity, startup state, filter configuration, FIFO/interrupt timing and clipping |
| ADXL375, flight SPI3 | 2 MHz, mode 3; 800 Hz; nominal ±200 g; INT1 | Format, scale, actual headroom and clipping; specified minimum range is ±180 g |
| BMP390, flight I²C1 | 400 kHz bus; 50 Hz pressure target | Calibration/configuration, conversion time versus chosen oversampling, data-ready and pressure validity |
| MS5607-02BA03, flight I²C2 | 400 kHz; OSR4096; asynchronous D1/D2; 50 Hz compensated target | PROM CRC, correct compensation arithmetic, temperature sample age and worst-case conversion schedule |
| SAM-M10Q, comms UART/PPS | 10 Hz navigation target; captured PPS | Exact product/FW, navigation model, constellation/performance mode, sustained rate, fix validity and timestamps |

Sources for limits/register work: [ST datasheet](https://www.st.com/resource/en/datasheet/lsm6dsv16x.pdf),
[TDK datasheet](https://invensense.tdk.com/wp-content/uploads/2020/04/ds-000347_icm-42688-p-datasheet.pdf),
[ADI datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ADXL375.PDF),
[Bosch datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp390-ds002.pdf),
[TE datasheet](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=MS5607-02BA03&DocType=Data+Sheet&DocLang=English),
[SAM-M10Q R05](https://content.u-blox.com/sites/default/files/documents/SAM-M10Q_DataSheet_UBX-22013293.pdf).

## Recommended implementation checks

- Retain fixed ±16 g IMU ranges initially. Both IMUs already provide low-g
  sensing. Do not switch to ±2 g at coast unless measured noise/quantisation
  makes it useful and transition behaviour has been characterised.
- Record sensor-frame raw data, scale/range/filter configuration, temperature,
  sequence, timestamp and validity. Axis transforms remain provisional until
  final placement and vehicle orientation are fixed. Front versus back and
  pin-1 direction both affect them; photographs alone are insufficient.
- Timestamp acquisition/DRDY or a documented FIFO sample epoch. Record receive
  time separately where useful. A 200 Hz estimator does not make the 960/1000/800 Hz
  sensors synchronous. Account for filtering and conversion latency.
- Use bounded bus transactions and bounded recovery. Missing DRDY, a stuck bus,
  repeated/stale data, startup and saturation are distinct states. A branch reset
  invalidates data until identity/configuration and fresh-sample checks pass.
- Track each channel's usable range separately. ST gyro data beyond ±2000°/s
  does not make a saturated TDK gyro a second valid observation. High-g acceleration
  does not restore attitude after both gyros have lost it.
- Two disagreeing sensors are not a majority vote. Use self-status, freshness,
  range, residuals and other valid observations to diagnose disagreement.
  Shared vibration, alignment errors and pressure vents remain common modes.
- Coast is near-zero **specific force**, not necessarily low speed. Do not use
  a near-zero accelerometer vector as a trustworthy gravity direction for tilt
  correction. Preserve the motion model's explicit gravity term.
- A GNSS estimate forwarded to flight carries source time, age and validity.
  GNSS loss or comms reset cannot stall the flight scheduler or silently produce
  repeated “fresh” coordinates. No GNSS-dependent safety-policy change is implied.

## Two details worth catching now

**MS5607 timing and accuracy.** At OSR4096, each conversion may take 9.04 ms.
A new D1 and D2 every 20 ms therefore consume up to 18.08 ms before bus and
scheduling overhead. The 50 Hz target is plausible but needs an actual timeline;
do not block a 1 ms flight schedule waiting on either conversion. PROM CRC-4
checks stored calibration, not every subsequent pressure sample. Use wide signed
intermediates and the second-order low-temperature compensation.

Its March 2024 sheet distinguishes 300–1100 mbar full accuracy from 10–2000 mbar
extended ADC range; older-style calculation examples still use 10–1200 mbar.
Below the characterised region, mark the different evidence status rather than
silently extending the normal accuracy model. BMP390's documented range starts
at 300 hPa. Pressure extrapolation is not an above-80-km solution.

**SAM navigation rate.** The current R05 table gives four-constellation 10 Hz in
high-performance mode, versus 4 Hz in default mode; GPS+Galileo can give 10 Hz
in default mode. Match the real ROM/product revision, configure deliberately,
read back, measure power and prove the actual output interval. A UART receiving
ten messages per second need not be receiving ten new navigation solutions.

## First-PCBA evidence, with outputs inert

Suggested checks for joint bring-up: read-back configuration; six static
orientations; timestamp/rate/latency histograms; stationary noise versus filter
settings; temperature drift; controlled motion and clipping; stale/FIFO-overrun
handling; one sensor reset or disconnected; pressure disagreement; GNSS loss;
maximum radio activity and load switching while observing sensor/rail noise.

Capture raw data and exact settings. These checks characterise the board and
drivers; they do not establish a qualified high-altitude estimator. Hardware
has not yet been tested, and this checklist does not assign Anav a new schedule.
