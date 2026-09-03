# Ogma Current System

Updated: 2026-08-17

Ogma is a modular avionics project for a university high-powered rocket targeting approximately 9 km altitude. Its five-board flight stack uses independent STM32 nodes and a 500 kbit/s CAN bus. Mu is a separate standalone science payload developed alongside the stack.

The first revision uses compact stackable boards with a shared power/CAN backplane. Foinse supplies the stack rails. Each board locally converts 5 V to 3.8 V with a switching preregulator and then to 3.3 V with an LDO.

## Flight Boards

| Board | Role | Current implementation |
| --- | --- | --- |
| Croi | Core flight computer | STM32F072, LSM6DSO32 IMU, MS5607 barometer, SPI NOR logging, flight-state coordination |
| Teachtaire | Telemetry and navigation | STM32F072, SX1272 LoRa module, u-blox MAX-M10S GNSS, CAN telemetry relay |
| Foinse | Power source and monitoring | Stack power generation/distribution, battery and servo-current sensing, CAN health |
| Lamh | Airbrake actuator control | STM32F072, PCA9685, four routed servo outputs, physical arm input, leased CAN commands |
| Pleasc | Recovery deployment | STM32F072, continuity monitoring, four deployment channels, guarded CAN arm/fire path |
| Mu | Cosmic-ray payload | Standalone SiPM muon detector and logger that can share Ogma mechanical/electrical conventions |

Groundstation is the companion receiver rather than a flight-stack board. It receives Teachtaire packets, provides a local display, and bridges telemetry to Ogma Console over USB.

## Software

Ogma Console identifies one attached board over SWD, builds/flashes the correct firmware, reads SRAM diagnostics, configures mission/servo parameters, retrieves Croi flash logs, plots data, and can operate as a higher-detail groundstation display.

SWD diagnostics are deliberately subordinate to flight behaviour. Active commands use short leases and are rejected when flight conditions make bench control inappropriate.

## Status

Croí, Foinse, Lámh and Teachtaire flew together in an L1 rocket on 15 August
2026. Pléasc did not fly because its optocouplers and full bring-up were still
incomplete. The flown stack returned live LoRa telemetry, GNSS records and a
valid Croí flash log. Croí detected POWERED, COASTING and DROGUE, and logged the
programmed servo deploy and stow commands. Servo-current data supports load
activity, but there was no position sensor and physical travel is not proven.

Croí reset 14.976 seconds after liftoff while Mu still measured about 696 m
relative altitude. The reset cause is unknown. MAIN and LANDED were not reached
in the recovered onboard run. Foinse recorded main-rail and servo-rail current,
but its voltage, temperature and state-of-charge fields remained zero. Croí did
not preserve the reset-cause flags early enough in startup, so the available
records cannot identify an electrical or firmware cause.

The launch-day external battery connector became intermittent but remained
plugged in and in circuit. A twisted joint through a drilled access hole
connected the battery to the Wago terminal so the closed stack could be powered.
This arrangement did not bypass the connector or destroy the post-flight
evidence.

Rev 1 is closed as a flown prototype, not a qualified reusable platform. The
canonical result, board findings and next-stack requirements are in
[`ogma-rev1-flight-closure.md`](ogma-rev1-flight-closure.md).
