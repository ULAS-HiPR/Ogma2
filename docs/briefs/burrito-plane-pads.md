# Burrito: the 52 open plane pads (D-24Nov.16)

Board 54ba53cd's first plane-pad count (D-24Nov.15) found 52 of 623 pads with no via and no drawn join. This table says why each had none (tools/layout/plane_pad_table.py, on trial d25-54ba53cd's fanned board, true copper shapes) and how each is closed on board e532c976 (0 of 623 open).

Columns: **centre**, what rejects a via in the middle of the pad (the closest shortfall: copper, gap, needed, mm); **along**, the nearest in-pad site along the pad's long axis that clears (offset from the centre, mm), else none; **GND at 0.1**, for a GND pad, whether a centre or along site would clear if GND kept JLC's 0.1 mm instead of its class's 0.2 mm; **closed by**.

| Pad | Net | Part | Centre: rejected by | Along | GND at 0.1 | Closed by |
| --- | --- | --- | --- | --- | --- | --- |
| C205.1 | FLIGHT_3V3 | 100n 16V X7R | F.Cu GND 0.199 < 0.21 | 0.025 |  | the fan-out, widened |
| C205.2 | GND | 100n 16V X7R | clears | 0.025 | yes | the fan-out, widened |
| C207.2 | GND | 100n 16V X7R | clears | 0.025 | yes | the fan-out, widened |
| C4603.2 | GND | 100n 16V X7R | B.Cu RECOVERY_ARMED_VBAT -0.225 < 0.51; B.Cu RECOVERY_ARMED_VBAT 0.129 < 0.51 |  | no | the fan-out, widened |
| C6603.2 | GND | 1n 50V C0G | B.Cu OUTPUT2_LOW -0.225 < 0.51 |  | no | drawn on L1 to C6604.2 |
| R1204.2 | GND | 100k | B.Cu STAGING_ARM_FEED -0.225 < 0.51; B.Cu STAGING_ARM_FEED -0.225 < 0.51 |  | no | drawn on L1 to C1705.2 |
| R2310.1 | FLIGHT_3V3 | 10k | B.Cu RECOVERY_ARMED_VBAT -0.225 < 0.51; B.Cu RECOVERY_ARMED_VBAT 0.16 < 0.51 |  |  | drawn on L1 to U2301.6 |
| R6105.1 | FLIGHT_3V3 | 47k | B.Cu GND -0.225 < 0.21 |  |  | drawn on L1 to R6106.1 |
| R6303.2 | GND | 100k | In2.Cu PYRO2_LS_SELECT -0.113 < 0.51; In2.Cu PYRO2_LS_SELECT 0.018 < 0.51 |  | no | drawn on L1 to R6711.2 |
| U101.11 | GND | TPS26630RGER | pad U101.12 0.15 < 0.21; pad U101.10 0.15 < 0.21 |  | yes | drawn on L1 to U101.25 |
| U101.8 | GND | TPS26630RGER | pad U101.9 0.15 < 0.21; pad U101.7 0.15 < 0.21 |  | yes | the fan-out, widened |
| U1101.12 | GND | TPS2121RUXR | B.Cu 4V_PRE 0.075 < 0.21; pad U1101.11 0.175 < 0.21 |  | no | a via 0.67 mm north-east of the pad |
| U1401.8 | GND | LM73100RPWR | pad U1401.9 0.1 < 0.21; pad U1401.7 0.1 < 0.21 |  | no | the fan-out, widened |
| U201.100 | FLIGHT_3V3 | STM32H563VIT6 | pad U201.99 0.125 < 0.21 |  |  | drawn on L1 to its capacitor C201.1, whose pad takes the via |
| U201.11 | FLIGHT_3V3 | STM32H563VIT6 | pad U201.10 0.125 < 0.21; F.Cu GND 0.175 < 0.21 |  |  | drawn on L1 to its capacitor C205.1, whose pad takes the via |
| U201.19 | GND | STM32H563VIT6 | pad U201.18 0.125 < 0.21 |  | yes | the fan-out, widened |
| U201.20 | GND | STM32H563VIT6 | pad U201.21 0.125 < 0.21 |  | yes | the fan-out, widened |
| U201.27 | GND | STM32H563VIT6 | pad U201.28 0.125 < 0.21; pad U201.26 0.125 < 0.21 |  | yes | the fan-out, widened |
| U201.28 | FLIGHT_3V3 | STM32H563VIT6 | pad U201.27 0.125 < 0.21 |  |  | drawn on L1 to its capacitor C208.1, whose pad takes the via |
| U201.49 | GND | STM32H563VIT6 | pad U201.50 0.125 < 0.21; pad U201.48 0.125 < 0.21 |  | yes | the fan-out, widened |
| U201.50 | FLIGHT_3V3 | STM32H563VIT6 | pad U201.49 0.125 < 0.21 |  |  | drawn on L1 to its capacitor C203.1, whose pad takes the via |
| U201.73 | FLIGHT_3V3 | STM32H563VIT6 | pad U201.74 0.125 < 0.21 |  |  | drawn on L1 to its capacitor C202.1, whose pad takes the via |
| U201.74 | GND | STM32H563VIT6 | pad U201.73 0.125 < 0.21; pad U201.75 0.125 < 0.21 |  | yes | the fan-out, widened |
| U201.75 | FLIGHT_3V3 | STM32H563VIT6 | pad U201.74 0.125 < 0.21 |  |  | drawn on L1 to its capacitor C204.1, whose pad takes the via |
| U201.99 | GND | STM32H563VIT6 | pad U201.98 0.125 < 0.21; pad U201.100 0.125 < 0.21 |  | yes | the fan-out, widened |
| U2301.6 | FLIGHT_3V3 | TPS3808G33DBVR | B.Cu STAGING_ARMED_VBAT -0.225 < 0.51; B.Cu STAGING_ARMED_VBAT 0.494 < 0.51 |  |  | drawn on L1 to its capacitor C2302.1, whose pad takes the via |
| U2302.1 | FLIGHT_3V3 | TPS3430WDRCR | B.Cu STAGING_ARMED_VBAT -0.225 < 0.51 |  |  | drawn on L1 to U2302.10 |
| U2302.3 | GND | TPS3430WDRCR | B.Cu STAGING_ARMED_VBAT -0.225 < 0.51; B.Cu STAGING_ARMED_VBAT 0.066 < 0.51 |  | no | drawn on L1 to U2302.5 |
| U2302.5 | GND | TPS3430WDRCR | B.Cu STAGING_ARMED_VBAT -0.225 < 0.51; B.Cu STAGING_ARMED_VBAT -0.225 < 0.51 |  | no | the fan-out, widened |
| U2302.6 | GND | TPS3430WDRCR | pad U2302.7 0.135 < 0.21; via FLIGHT_3V3 0.203 < 0.21 |  | yes | the fan-out, widened |
| U3104.2 | GND | LSM6DSV32XTR | pad U3104.1 0.1 < 0.21 |  | no | the fan-out, widened |
| U3104.3 | GND | LSM6DSV32XTR | pad U3104.4 0.1 < 0.21 |  | no | the fan-out, widened |
| U3104.6 | GND | LSM6DSV32XTR | pad U3104.5 0.1 < 0.21 |  | no | the fan-out, widened |
| U3104.7 | GND | LSM6DSV32XTR | pad U3104.8 0.133 < 0.21 | 0.225 | yes | the fan-out, widened |
| U3204.6 | GND | ICM-42688-P | pad U3204.5 0.1 < 0.21 |  | no | the fan-out, widened |
| U3204.7 | GND | ICM-42688-P | pad U3204.8 0.133 < 0.21 | 0.225 | yes | the fan-out, widened |
| U3701.11 | GND | MMC5983MA | pad U3701.12 0.125 < 0.21; pad U3701.10 0.125 < 0.21 |  | yes | the fan-out, widened |
| U3701.9 | GND | MMC5983MA | pad U3701.10 0.125 < 0.21 |  | yes | the fan-out, widened |
| U401.12 | GND | STM32H563RIT6 | pad U401.13 0.125 < 0.21; pad U401.11 0.125 < 0.21 |  | yes | the fan-out, widened |
| U401.18 | GND | STM32H563RIT6 | pad U401.19 0.125 < 0.21; pad U401.17 0.125 < 0.21 |  | yes | the fan-out, widened |
| U401.31 | GND | STM32H563RIT6 | pad U401.32 0.125 < 0.21; pad U401.30 0.125 < 0.21 |  | yes | the fan-out, widened |
| U401.47 | GND | STM32H563RIT6 | pad U401.46 0.125 < 0.21; pad U401.48 0.125 < 0.21 |  | yes | the fan-out, widened |
| U401.63 | GND | STM32H563RIT6 | pad U401.62 0.125 < 0.21; pad U401.64 0.125 < 0.21 |  | yes | the fan-out, widened |
| U4301.2 | GND | TXU0202DCUR | pad U4301.1 0.1 < 0.21; pad U4301.3 0.1 < 0.21 |  | yes | the fan-out, widened |
| U4301.3 | FLIGHT_3V3 | TXU0202DCUR | pad U4301.2 0.1 < 0.21; pad U4301.4 0.1 < 0.11 |  |  | drawn on L1 to its capacitor C4301.1, whose pad takes the via |
| U6001.4 | GND | SN74LVC1G74DCUR | In2.Cu PYRO3_LS_SELECT -0.1 < 0.51; pad U6001.3 0.1 < 0.21 |  | no | the fan-out, widened |
| U6304.2 | GND | TPS1H100BQPWPRQ1 | In2.Cu PYRO1_LS_SELECT -0.225 < 0.51; pad U6304.1 0.2 < 0.21 |  | no | drawn on L1 to U6304.15 (its exposed pad) |
| U6404.12 | FLIGHT_3V3 | TPS1H100BQPWPRQ1 | In2.Cu PYRO3_LS_SELECT 0.35 < 0.51 |  |  | a via 0.91 mm off the pad, under the body |
| U6404.2 | GND | TPS1H100BQPWPRQ1 | pad U6404.1 0.2 < 0.21; pad U6404.3 0.2 < 0.21 |  | yes | drawn on L1 to U6404.15 (its exposed pad) |
| U6504.2 | GND | TPS1H100BQPWPRQ1 | pad U6504.1 0.2 < 0.21; pad U6504.3 0.2 < 0.21 |  | yes | drawn on L1 to U6504.15 (its exposed pad) |
| U7101.2 | GND | INA228AIDGSR | pad U7101.3 0.125 < 0.21 |  | yes | the fan-out, widened |
| U7101.7 | GND | INA228AIDGSR | pad U7101.6 0.125 < 0.21; pad U7101.8 0.125 < 0.21 |  | yes | the fan-out, widened |

Closed by: the fan-out, widened, 31; supply pins drawn to their capacitors, 8; drawn to the nearest pad of their net that reaches the plane, 11; a via found on a 0.05 mm grid, 2. No part moved and no smaller via.

What the table shows:

- The fan-out's misses were mostly its own: it tried an in-pad via only at the pad's centre, modelled every drawn track as a 0.3 mm stub, and drew every stub 0.3 mm wide, which can't leave a 0.5 mm pitch pad at GND's 0.2 mm. Widened (in-pad sites along the pad, tracks at their own width, a stub the pad's width or 0.2 mm), it closes 31 of the 52.
- GND's class clearance, 0.2 mm, is what rejects the centre via at the fine-pitch GND pins (U201, U401 and the sensors among them): 25 of the 39 GND pads would take a centre or along via at JLC's 0.1 mm. The layout brief's table gives 0.2 mm for pours; the spec applies it to every GND item. The board doesn't need the change now (all 52 are closed without it); it's recorded for the Open row on GND's clearance.
- Fire copper rejects the centre via at 12 of them (C4603.2, C6603.2, R1204.2, R2310.1, R6303.2, U2301.6, U2302.1, U2302.3, U2302.5, U6001.4, U6304.2, U6404.12): the armed rails on L6 under the supervisors and a few passives, and the fire logic on L3 under U6001, U6304, U6404 and R6303. The widened fan-out found a site for 3 (C4603.2, U2302.5, U6001.4); the rest join on L1 to a pad of their net that has a via, the pyro high sides' GND pins to their own exposed pads, or take a via found on a finer grid (U6404.12).
