# Croi2 (Burrito): JLC stock

21 November 2026, during capture (B-38: assembled by JLC from its parts library).
Parts with an MPN were checked during capture; every generic resistor and capacitor was
matched at the close-out (step 8), below.

Source: the [jlcparts](https://github.com/yaqwsx/jlcparts) scrape of JLC's assembly parts
library, deployed 21 Nov 2026 11:53 UTC. It lists in-stock parts only, so "not stocked" means
not in JLC's library today. It does not cover JLC Global Sourcing (parts JLC buys from
distributors for an order, with lead time) or consigned parts. Third-party data: confirm
each LCSC number on jlcpcb.com before ordering. Quantities are per board, after capture.

## Not in JLC stock

| Part | Refs | Stocked alternative (LCSC, stock) | Fit |
| --- | --- | --- | --- |
| INA228AIDGSR | U7101 | INA237AIDGSR (C2864837, 4,204): 85 V, VSSOP-10, 16-bit instead of 20-bit | Same family and package; pinout to verify; firmware registers change |
| BMP390 | U3403 | BMP388 (C779278, 7,462): same 2 × 2 mm LGA-10 | Drop-in; older, noisier |
| LSM6DSV16XTR | U3104 | LSM6DSV32XTR (C22461202, 4,958): same LGA-14, ±32 g instead of ±16 g | Drop-in; firmware range constants |
| MX66L2G45GMI00 (2 Gbit NOR) | U3604 | No 2 Gbit NOR stocked. W25Q01JVSFIQ (C2962013, 45): 1 Gbit, SOIC-16 300 mil | Half the log space; pinout to verify |
| LM73100RPWR | U1401 | None (LM66100 is 1.5 A, not equivalent) | Global Sourcing or consign |
| TPSM63603RDHR | U1301 | None (TPSM63610: 15 stocked, different footprint) | Global Sourcing or consign |
| TPS3430WDRCR | U2302 | None (TPS3435 has a different pinout) | Global Sourcing or consign |
| TXU0304PWR | U502, U504, U4303 | TXU0304RUTR (C2959768, 13,977): UQFN-12 1.7 × 2 mm | New footprint; no probe access to pins |
| TXU0101DCKR | U4302 | TXU0101DBVR (C7136368, 2,820): SOT-23-6 | New footprint |
| TXU0202DCUR | U4301 | TXU0202QDCURQ1 (C7372013, 1,028): automotive grade, same VSSOP-8 | Drop-in |
| ESD2CAN24DBZRQ1 | D501, D502 | ESD2CANFD24DBZRQ1 (C20345392, 12,484): TI, SOT-23 | Drop-in |
| LM4040CEM3-3.0/NOPB | U1002 | LM4040CIM3-3.0/NOPB (C132056, 2,880): same TI part, rated to 85 °C instead of 125 °C | Drop-in |
| WSLP2512R0050FEA (5 mΩ) | R7101 | RLP25FEGMR005 (C393074, 218,606): 5 mΩ 1% 3 W 2512 | Drop-in |
| CRCW20104K70FKEF | R1012, R1013 | RC2010FK-074K7L (C513572, 4,716): 4.7 kΩ 1% 0.75 W 2010 | Drop-in |
| Keystone 5000 (red test point) | 15 power test points | 5003 orange (C238124, 7,350) or 5002 white | Drop-in; colour only |
| Molex 1053111102 | J101 | None: the spec rules out a 105309 substitute | Global Sourcing or consign; footprint from Molex's drawing at step 8 |
| Samtec MPT-08-01-01-L-RA-SD | J102 | None; must mate the bay's Samtec half | Global Sourcing or consign |
| Amphenol 132134 (SMA, vertical) | J4501, J4601 | None (132203 is right-angle) | Global Sourcing or consign |
| Seeed Wio-LR2021 | U4606 | Not carried (module) | Consign or hand-fit |
| Harwin G125-MS10605M2P (Gecko-SL 2×3, step 5) | J501, J502 | None (G125-MS10605L3P: 2 in stock) | Global Sourcing or consign |
| J6101 / J6102 arm-switch connectors (step 6) | J6101, J6102 | Part not chosen | Checked once the family is picked |
| Nichicon PCW0J102MCO1GS (1000 µF polymer, step 3) | C1403 | None in SMD; JLC's stocked 1000 µF polymers are through-hole | Global Sourcing or consign |

## Stocked, but thin

| Part | Refs | In stock |
| --- | --- | --- |
| STM32H563RIT6 (comms, fitted at step 7; C20619634) | U401 | 12 |
| STM32H563VIT6 | U201 | 43 |
| CSD18540Q5B | Q101 | 26 |
| TPS26630RGER | U101 | 48 |
| ECS-160-10-36Q-ES-TR | Y201, Y401 | 67 |
| MAX-M10S-00B(-01) | U4504 | 68 |
| ADXL375BCCZ | U3304 | 160 |
| TPS1H100BQPWPRQ1 | U6304, U6404, U6504 | 273 |
| CPT-9019S-SMT-TR | BZ9001 | 277 |

JLC can hold parts in an account's private library ahead of an order.

The LTC6993 one-shots (U6301, U6401, U6501) were short too (1 stocked); step 6 removed all three.

## Parts added by capture

| Part | Step | LCSC, stock |
| --- | --- | --- |
| BAT54T1G, onsemi, SOD-123 | 1 | C152458, 60,607 |
| 100 µF 6.3 V X5R 1206 (C219) | 1 | C15008 (Basic), 1,464,361 |
| MMC5983MA | 4 | C404329, 14,167 |
| SN74LVC1G08DBVR (U6502) | 6 | C7666, 72,536 |
| Littelfuse 0451004.MRL, 4 A NANO2 (F6101, F6102) | 6 | C27515, 20,383 |
| TCAN3413DRBR (second, U505) | 5 | C22445415, 1,001 |
| 470 µF aluminium hold capacitor | 2 | Many 6.3 × 7.7 mm parts stocked; a 6.3 V part's catalogue leakage (0.01CV ≈ 30 µA) meets the limit. Chosen at step 2 |

## Stocked with margin

STM32 aside, every other part with an MPN is stocked well beyond one board's need:
SN74LVC1G04/74/97, TMUX1511, TPD1E0B04, TPS2121, TPS22918, TPS2553-1, TPS3700, TPS3808G33,
TPS70933, TPS7A9101, USB4105-GF-A, USBLC6-2SC6, BAS116, ICM-42688-P, MS5607,
ABS07-32.768KHZ-7-T, JST GH BM02B, Molex 430450600 / 430451000, Keystone 5001.

## Generic passives (full pass, step 8)

73 value lines, 417 parts, from the as-captured netlist, matched by
[tools/capture/jlc_passives.py](tools/capture/jlc_passives.py): value, package, tolerance (1% where
the schematic states none), power where stated; capacitors at or above the stated voltage, same
dielectric (X7R also covers X5R). Basic first, then stock. 68 lines match: 34 of them Basic
(295 parts), 34 Extended. The TC2030 pads and the 1 mm test pads are footprints only and stay out of the BOM.

Five lines have no stocked part as specified:

| Line | Refs | Nearest stocked | Fit |
| --- | --- | --- | --- |
| 47 µF 16 V X7R 1210 | C1305, C1306, C1705, C1706, C1805, C1806, C1905, C1906 | No X7R. GRM32EC81C476KE15L X6S (C162512, 62,976) or GRM32ER61C476KE15L X5R (C77101, 132,470) | Seán's call: X6S keeps more capacitance hot; or Global Sourcing for X7R |
| 100 µF 10 V X7R 1210 | C4613 | X5R only: CL32A107MPVNNNE 10 V (C23742) or EMK325ABJ107MM-P 16 V (C90143) | Seán's call |
| 10 µF 16 V X7R 0603 | C4504 | X5R in 0603 (CL10A106MO8NQNC, C92487), or X7R in a larger case | Seán's call |
| 31.9k 0.1% 0603 | R1701, R1801, R1901 | Not stocked. 31.6k 0.1% is (RT0603BRE0731K6L, C705846) but moves the LDOs to 3.328 V nominal | Global Sourcing to keep 3.352 V, or a new divider (a design change) |
| 74.9k 0.1% 0603 | R1103 | Not stocked at 0.1% | Global Sourcing, or another 0.1% pair |

| Value | Package | Qty | LCSC | Part | Class | Stock | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 100n 16V X7R | 0603 | 87 | C14663 | CC0603KRX7R9BB104 | Basic | 50,349,394 |  |
| 100n 25V X7R | 0603 | 4 | C14663 | CC0603KRX7R9BB104 | Basic | 50,349,394 |  |
| 100n 50V X7R | 0603 | 3 | C14663 | CC0603KRX7R9BB104 | Basic | 50,349,394 |  |
| 10n 100V C0G | 0603 | 1 | C432938 | CGA3E1C0G2A103JT0Y0E | Extended | 5,911 |  |
| 10n 100V X7R | 0603 | 1 | C107059 | CC0603KRX7R0BB103 | Extended | 1,211,568 |  |
| 10n 16V X7R | 0603 | 8 | C57112 | 0603B103K500NT | Basic | 5,976,362 |  |
| 10u 16V X7R | 0603 | 1 | none | | | | **not matched** |
| 15p C0G provisional | 0603 | 4 | C1644 | CL10C150JB8NNNC | Basic | 804,717 |  |
| 1n 16V X7R | 0603 | 5 | C1588 | CL10B102KB8NNNC | Basic | 6,432,787 |  |
| 1u 10V X7R | 0603 | 1 | C59302 | 0603B105K250NT | Extended | 904,388 |  |
| 1u 16V X7R | 0603 | 17 | C59302 | 0603B105K250NT | Extended | 904,388 |  |
| 2.2u 10V X7R | 0603 | 5 | C99228 | 0603B225K250NT | Extended | 447,538 |  |
| 2.2u 16V X7R | 0603 | 3 | C99228 | 0603B225K250NT | Extended | 447,538 |  |
| 22n 25V X7R | 0603 | 1 | C21122 | CL10B223KB8NNNC | Basic | 937,591 |  |
| 4.7u 16V X7R | 0603 | 3 | C389010 | GRM188Z71C475KE21D | Extended | 11,522 |  |
| 47n 16V X7R | 0603 | 1 | C1622 | CL10B473KB8NNNC | Basic | 527,059 |  |
| 9.1p C0G provisional | 0603 | 2 | C513588 | CC0603CRNPO9BN9R1 | Extended | 18,002 |  |
| 100u 6.3V X5R | 1206 | 1 | C15008 | CL31A107MQHNNNE | Basic | 1,464,361 |  |
| 10u 16V X7R | 1206 | 3 | C14860 | CL31B106KAHNNNE | Extended | 981,002 |  |
| 100u 10V X7R | 1210 | 1 | none | | | | **not matched** |
| 22u 25V X7R | 1210 | 1 | C309062 | CL32B226KAJNNNE | Extended | 85,304 |  |
| 47u 16V X7R | 1210 | 8 | none | | | | **not matched** |
| 0R | 0603 | 14 | C21189 | 0603WAF0000T5E | Basic | 24,128,786 | no tolerance stated: 1% chosen |
| 0R ENERGY LINK - DNP | 0603 | 3 (3 DNP) | C21189 | 0603WAF0000T5E | Basic | 24,128,786 | no tolerance stated: 1% chosen |
| 1.24k 1% | 0603 | 3 | C2933135 | FRC0603F1241TS | Extended | 253,807 |  |
| 100R | 0603 | 6 | C22775 | 0603WAF1000T5E | Basic | 11,248,464 | no tolerance stated: 1% chosen |
| 100k | 0603 | 41 | C25803 | 0603WAF1003T5E | Basic | 19,748,113 | no tolerance stated: 1% chosen |
| 100k 0.1% | 0603 | 1 | C122538 | RT0603BRD07100KL | Extended | 1,363,538 |  |
| 100k 1% | 0603 | 1 | C25803 | 0603WAF1003T5E | Basic | 19,748,113 |  |
| 10R | 0603 | 2 | C22859 | 0603WAF100JT5E | Basic | 6,134,273 | no tolerance stated: 1% chosen |
| 10k | 0603 | 22 | C25804 | 0603WAF1002T5E | Basic | 32,380,385 | no tolerance stated: 1% chosen |
| 10k 0.1% | 0603 | 20 | C95204 | RT0603BRD0710KL | Extended | 2,121,585 |  |
| 127k 0.1% | 0603 | 3 | C1509626 | ARG03BTC1273 | Extended | 7,350 |  |
| 15k 0.1% | 0603 | 1 | C326733 | RT0603BRD0715KL | Extended | 47,687 |  |
| 16.5k 1% | 0603 | 1 | C22812 | 0603WAF1652T5E | Extended | 84,553 |  |
| 1M | 0603 | 1 | C22935 | 0603WAF1004T5E | Basic | 5,647,551 | no tolerance stated: 1% chosen |
| 1k | 0603 | 4 | C21190 | 0603WAF1001T5E | Basic | 24,277,749 | no tolerance stated: 1% chosen |
| 2.2k | 0603 | 3 | C4190 | 0603WAF2201T5E | Basic | 6,762,276 | no tolerance stated: 1% chosen |
| 2.7k | 0603 | 2 | C13167 | 0603WAF2701T5E | Basic | 1,074,013 | no tolerance stated: 1% chosen |
| 200k 1% | 0603 | 1 | C25811 | 0603WAF2003T5E | Basic | 2,578,190 |  |
| 20k 0.1% | 0603 | 2 | C723637 | RT0603BRD0720KL | Extended | 48,214 |  |
| 210k 1% | 0603 | 2 | C2933168 | FRC0603F2103TS | Extended | 669,626 |  |
| 22.1k 0.1% | 0603 | 13 | C723484 | RT0603BRD0722K1L | Extended | 24,915 |  |
| 22.1k 1% | 0603 | 1 | C2960862 | FRC0603F2212TS | Extended | 297,462 |  |
| 22R | 0603 | 12 | C23345 | 0603WAF220JT5E | Basic | 7,914,544 | no tolerance stated: 1% chosen |
| 23.7k 0.1% | 0603 | 6 | C861245 | RT0603BRD0723K7L | Extended | 5,197 |  |
| 26.7k 0.1% | 0603 | 1 | C728587 | RT0603BRD0726K7L | Extended | 12,510 |  |
| 3.3k | 0603 | 1 | C22978 | 0603WAF3301T5E | Basic | 6,068,499 | no tolerance stated: 1% chosen |
| 3.9k 1% | 0603 | 12 | C23018 | 0603WAF3901T5E | Basic | 683,408 |  |
| 30k 0.1% | 0603 | 1 | C723585 | RT0603BRD0730KL | Extended | 365,795 |  |
| 31.9k 0.1% | 0603 | 3 | none | | | | **not matched** |
| 330R | 0603 | 2 | C23138 | 0603WAF3300T5E | Basic | 3,527,043 | no tolerance stated: 1% chosen |
| 39.2k 0.1% | 0603 | 1 | C861369 | RT0603BRD0739K2L | Extended | 26,949 |  |
| 3k 1% | 0603 | 1 | C4211 | 0603WAF3001T5E | Basic | 7,620,180 |  |
| 4.7k | 0603 | 4 | C23162 | 0603WAF4701T5E | Basic | 19,500,720 | no tolerance stated: 1% chosen |
| 40.2k 0.1% | 0603 | 1 | C667101 | TD03G4022BT | Extended | 25,184 |  |
| 43.2k 0.1% | 0603 | 1 | C861404 | RT0603BRD0743K2L | Extended | 6,370 |  |
| 44.2k 1% | 0603 | 1 | C2930103 | FRC0603F4422TS | Extended | 10,818 |  |
| 470R | 0603 | 7 | C23179 | 0603WAF4700T5E | Basic | 5,676,038 | no tolerance stated: 1% chosen |
| 470k | 0603 | 1 | C23178 | 0603WAF4703T5E | Basic | 1,322,160 | no tolerance stated: 1% chosen |
| 47R 1% | 0603 | 5 | C23182 | 0603WAF470JT5E | Basic | 1,432,929 |  |
| 47k | 0603 | 31 | C25819 | 0603WAF4702T5E | Basic | 1,993,053 | no tolerance stated: 1% chosen |
| 47k 0.1% | 0603 | 3 | C335087 | ARG03BTC4702 | Extended | 27,707 |  |
| 49.9k 1% | 0603 | 1 | C23184 | 0603WAF4992T5E | Basic | 1,691,456 |  |
| 5.1k 1% | 0603 | 2 | C23186 | 0603WAF5101T5E | Basic | 23,749,760 |  |
| 60.4k 1% | 0603 | 1 | C2933245 | FRC0603F6042TS | Extended | 774,612 |  |
| 64.9k 0.1% | 0603 | 1 | C861510 | RT0603BRD0764K9L | Extended | 15,866 |  |
| 66.5k 1% | 0603 | 1 | C2933250 | FRC0603F6652TS | Extended | 69,092 |  |
| 74.9k 0.1% | 0603 | 1 | none | | | | **not matched** |
| 750R 1% | 0603 | 3 | C114635 | RC0603FR-07750RL | Extended | 466,345 |  |
| 0R | 0805 | 2 | C17477 | 0805W8F0000T5E | Basic | 6,171,305 | no tolerance stated: 1% chosen |
| 120R 1% 0.25W | 0805 | 2 | C543533 | ERJP06F1200V | Extended | 45,341 |  |
| 5m 1% 3W WSLP2512R0050FEA | 2512 | 1 | C154688 | LR2512-23R005F4 | Extended | 22,829 |  |

