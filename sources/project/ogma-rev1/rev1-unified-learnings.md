# Ogma Rev 1: What We Learned Building a Modular Rocket Flight Computer

> Superseded after flight by [`ogma-rev1-flight-closure.md`](ogma-rev1-flight-closure.md). This file preserves the pre-flight July 2026 assessment.

Updated: 2026-07-11

## Executive Summary

Ogma Rev 1 proved that the distributed idea is workable: independent STM32 boards, a shared 500 kbit/s CAN bus, common power conventions, a central logger/controller, separate telemetry, power, actuation, and recovery functions, plus a standalone science payload.

It also showed that a board can be electrically repairable and still be painfully difficult to bring up. Most lost time came from poor observability and isolation: shared buses with no branch links, rails with few test points, package pins hidden under devices, ambiguous connector nets, and firmware that initially reported too little about low-level failures.

The governing Rev 2 rule is simple: every critical subsystem must be isolatable, measurable, and capable of failing into a known state.

## What Ogma Is

Ogma is a university rocket avionics project targeting a flight near 9 km. It combines a five-board CAN flight stack with a separate Mu science payload:

- Croi: flight state, inertial/barometric sensing, coordination, and SPI NOR logging.
- Teachtaire: SX1272 LoRa telemetry and u-blox GNSS.
- Foinse: stack power and current monitoring.
- Lamh: four-channel airbrake/servo actuation.
- Pleasc: recovery deployment outputs and continuity monitoring.
- Mu: standalone SiPM cosmic-ray detector payload.

Groundstation is the companion receiver/display. Ogma Console is the SWD/laptop tool used to identify, flash, diagnose, configure, retrieve logs, and plot data from one connected board at a time.

## Repositories

- Croi: https://github.com/ULAS-HiPR/croi
- Teachtaire: https://github.com/ULAS-HiPR/teachtaire
- Foinse: https://github.com/ULAS-HiPR/foinse
- Lamh: https://github.com/ULAS-HiPR/lamh
- Pleasc: https://github.com/ULAS-HiPR/pleasc
- Groundstation: https://github.com/ULAS-HiPR/gs_receiver
- Mu: https://github.com/sean-o-sullivan/mu

## Cross-Board Lessons

### 1. Observability is part of the design

Rev 1 often required a scope, a bodge wire, and custom firmware just to answer whether a rail, bus, or peripheral was alive. Rev 2 needs labelled test points, useful LEDs, accessible reset/programming signals, and counters that identify the layer at fault.

Minimum common access:

- every rail and local regulator stage,
- SWDIO, SWCLK, NRST, BOOT0, 3.3 V, and ground,
- CAN TX/RX plus CANH/CANL,
- SPI/I2C/UART signals and every chip select/reset,
- actuator/deployment enable and output nodes,
- at least one spare debug UART or recovery header.

### 2. Shared buses need isolation

One wrongly routed, rotated, mis-strapped, or damaged SPI device can hide every other device. Per-device 0 ohm links or small series footprints turn destructive PCB surgery into a reversible measurement.

The same principle applies to distributed power and external 5 V loads: branch links/fusing make one failed board diagnosable without deleting the whole stack rail.

### 3. Symbols, footprints, and purchased packages are separate checks

Several faults came from treating a generic symbol or remembered package convention as authoritative. The exact orderable part must be checked against:

1. schematic pin number and function,
2. footprint pad number,
3. package orientation/pin-1 drawing,
4. 3D/assembly orientation,
5. actual purchased suffix.

MOSFET pinouts, imported footprints, bottom-contact sensors, and radio-module identity deserve explicit sign-off.

### 4. Power trees must be readable from the board

Foinse's alternate input masked a dead battery path. Croi's buzzer depended on a rail that was not present in common bench use. A failed diode collapsed a local rail in a way that was not immediately visible.

Each board needs a power-tree diagram, expected-voltage table, rail ownership labels, test pads, and coarse LEDs. Bench procedure must state which sources may be connected together.

### 5. Minimal firmware is a first-class tool

Bare CAN, SPI probes, input probes, silent rescue images, and SRAM status blocks were often more useful than the full application. They reduced a system problem to one peripheral and one observable result.

Diagnostic targets should remain versioned, documented, and build-tested. They are part of the product, not temporary scraps.

### 6. Hardware abstraction layers must report failure

An I2C or SPI wrapper that returns plausible data while hiding HAL status makes every higher layer untrustworthy. Drivers now expose readiness, error state, counters, and exact device identity. This should be the default across the stack.

### 7. Protocols and configuration need one source of truth

Early telemetry depended on an exact but informal 14-byte packet and conflicting radio sync-word notes. Shared CAN code also leaked board-local debug headers.

Rev 1 software was corrected toward pinned shared libraries, explicit CAN payloads, versioned CRC-checked radio packets, and build-time mission manifests. Rev 2 should carry that discipline into hardware BOMs, radio settings, connector maps, and calibration data.

### 8. Safe state must exist below application intent

Software can command a safe servo angle or finite deployment pulse, but hardware still defines the reset window. Lamh Rev 1 ties PCA9685 OE low; Pleasc Rev 1 lacks an MCU-readable physical arm input.

Rev 2 needs hardware-default-disabled outputs, readable physical arm/RBF state, pulldowns sized from worst-case leakage, watchdogs, bounded command leases, and mechanical safe-state validation.

### 9. SWD can be a useful service interface

The stack has no required UART link to the laptop. A small SRAM mailbox and momentary halt can identify boards, read diagnostics, configure bench actions, and retrieve flash logs. This worked well enough to justify Ogma Console.

The constraint is that SWD support must never take ownership away from flight code. Read-only status is always available; active bench actions use leases and are rejected when Croi or flight state indicates operation.

### 10. Documentation must distinguish history from truth

Old architecture notes named an STM32F411, SPI NAND, and SX126x radio. Rev 1 hardware/firmware now uses STM32F072 boards, SPI NOR storage on Croi, and an SX1272 path on Teachtaire.

Dated proposals remain useful, but current architecture, fitted BOM, and firmware contract must be separately maintained.

## Board Summary

### Croi

Recovered from marginal SWD, wrong buzzer rail, IMU/flash/ADXL SPI routing faults, a bus-clamping peripheral, sensor orientation risk, and a damaged power-path diode. Bare CAN and SPI probes separated hardware from application failures. Logging now uses device-aware append-only SPI NOR records and chunked SWD retrieval.

### Teachtaire

GNSS became reliable after replacing fragile blocking byte reads with continuous nonblocking UART drain. Radio bring-up exposed configuration and part-identity ambiguity. The present system uses SX1272 and a versioned CRC-checked telemetry protocol.

### Foinse

Battery ORing failed while alternate input hid the downstream effect. The main lesson is to expose each node in the power chain, document expected gate/rail states, and protect/disconnect branches. Current-sensor calibration remains a HIL task.

### Lamh

FreeRTOS tick integration, I2C error propagation, connector polarity, and physical PWM tracing mattered more than the servo algorithm. Rev 1's OE tie-low reset window is a known hardware limitation. Rev 2 must default-disable outputs in hardware.

### Pleasc

Bring-up evidence is incomplete. Confirmed lessons are footprint verification and the inadequacy of a recovery controller with no MCU-readable physical arm state. Rev 1 operation requires an external RBF/pyro-power disconnect and guarded firmware; Rev 2 should fix the architecture.

### Mu

The detector reinforces the need to treat bias, threshold, temperature, grounding, analog noise, pulse injection, and calibration as one chain. It also validated local logging and SWD retrieval for a standalone black-box payload.

## Current Software Position

The release-candidate sources build for all flight boards. Croi and Lamh software-in-the-loop tests pass, and Ogma Console's host tests pass. This is not flight evidence. Remaining work is the documented HIL campaign: power cycling, CAN fault/recovery, logger endurance, servo mechanics, inert deployment loads, radio range, calibration, and integrated launch replay.

## Core Takeaway

Rev 1 taught us that successful bring-up is not luck or heroics with a soldering iron. It is an architectural property. Rev 2 should give the team deliberate handles to isolate every subsystem, prove every state, and recover without damaging the board.
