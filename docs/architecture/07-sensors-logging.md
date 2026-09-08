# 7. Sensors and local recording

## Selected measurements

| Device | Role | Starting configuration |
| --- | --- | --- |
| U3104 ST LSM6DSV16XTR | Low-g acceleration and rotation | 960 Hz, ±16 g / ±4000°/s, SPI1 |
| U3204 TDK ICM-42688-P | Dissimilar low-g/rotation measurement | 1 kHz, ±16 g / ±2000°/s, SPI2 |
| U3304 ADI ADXL375 | Boost/high-g evidence | 800 Hz, nominal ±200 g, SPI3 |
| U3403 Bosch BMP390 | Lower-flight pressure | 50 Hz target, I²C1 |
| U3503 TE MS5607 | Dissimilar pressure measurement | 50 Hz compensated target, I²C2 |
| U3604 MX66L2G45GMI00 | Full local flight record | 256 MiB NOR, quad interface |

Rates are initial budgets, not measured delivery or a demand that all samples
arrive synchronously. ADXL375 minimum specified range is ±180 g; do not conceal
saturation behind the ±200 g nominal label.

## Why five sensors

The two low-g IMUs provide finer-range coast measurements and dissimilar
manufacturer implementations. The separate high-g sensor covers acceleration
that saturates both IMUs. The two pressure devices expose disagreement and
device-specific failure. This is purposeful measurement diversity, not a
claim that any arbitrary two readings identify the truth.

Each sensor has a separately controlled limited supply and bus boundary.
The cost is more passives, isolation parts, firmware health logic and testing.
A smaller sensor set is simpler but removes these named diagnostic/range
capabilities; no deletion is authorised in this pass.

They still share the board, mounting, temperature, vibration, estimator and
some upstream power. Pressure devices also share an installation/vent failure.
Different manufacturers do not remove those common causes.

## Recording

NOR is soldered rather than socketed. Pre-erase while disarmed; flight recording
must not wait for an erase or scan the entire chip during restart. Records need
sequence, time, identity, integrity and explicit losses. Telemetry is a reduced
copy, never the sole evidence.

The current planning estimate is 96,672 B/s including the added current record;
30-minute storage budget is about 180.6 MB with previous allowance, below the
256 MiB capacity while retaining the stated 64 MiB reserve. These are budget
calculations, not measured worst-case write throughput.

Removable SD would simplify physical extraction but adds a socket, media and
field-handling boundary. It is not selected for flight logging. USB extraction
must remain bounded and must not interfere with active essential logging.

## Next review

Show each actual sensor and its local power, bypass and signal isolation as a
connected circuit. Prove axis transforms, timestamps, saturation/freshness,
pressure validity, start/stop behaviour and stuck-bus isolation. Never average
a known-invalid pressure reading into a trustworthy altitude claim.

Test interrupted NOR writes, full/corrupt storage and bounded logger recovery.
Logging failure may degrade evidence after launch; it must not create a flight
reset loop. Keep current monitoring explicitly separate from mechanical proof.

Evidence: [sensor configuration](../sensor-configuration-review-2026-09-07.md),
[firmware handoff](../firmware-handoff-2026-09-07.md),
[fault contract](../../interfaces/flight-fault-contract.md).
