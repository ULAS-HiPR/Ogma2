# Croi2 (Burrito): JLC stock, early pass

21 November 2026, during capture (B-38: assembled by JLC from its parts library).
The full pass, with every generic passive matched, comes at capture step 8.

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
| TXU0304PWR | U502, U4303, bus 2's boundary (3) | TXU0304RUTR (C2959768, 13,977): UQFN-12 1.7 × 2 mm | New footprint; no probe access to pins |
| TXU0101DCKR | U4302 | TXU0101DBVR (C7136368, 2,820): SOT-23-6 | New footprint |
| TXU0202DCUR | U4301 | TXU0202QDCURQ1 (C7372013, 1,028): automotive grade, same VSSOP-8 | Drop-in |
| ESD2CAN24DBZRQ1 | D501, bus 2's | ESD2CANFD24DBZRQ1 (C20345392, 12,484): TI, SOT-23 | Drop-in |
| LM4040CEM3-3.0/NOPB | U1002 | LM4040CIM3-3.0/NOPB (C132056, 2,880): same TI part, rated to 85 °C instead of 125 °C | Drop-in |
| WSLP2512R0050FEA (5 mΩ) | R7101 | RLP25FEGMR005 (C393074, 218,606): 5 mΩ 1% 3 W 2512 | Drop-in |
| CRCW20104K70FKEF | R1012, R1013 | RC2010FK-074K7L (C513572, 4,716): 4.7 kΩ 1% 0.75 W 2010 | Drop-in |
| Keystone 5000 (red test point) | 15 power test points | 5003 orange (C238124, 7,350) or 5002 white | Drop-in; colour only |
| Molex 1053111102 | J101 | Nano-Fit 2-way header 1053091102 (C2938824, 11,457) | Settled with J101's footprint at step 8 |
| Samtec MPT-08-01-01-L-RA-SD | J102 | None; must mate the bay's Samtec half | Global Sourcing or consign |
| Amphenol 132134 (SMA, vertical) | J4501, J4601 | None (132203 is right-angle) | Global Sourcing or consign |
| Seeed Wio-LR2021 | U4606 | Not carried (module) | Consign or hand-fit |
| Nichicon PCW0J102MCO1GS (1000 µF polymer, step 3) | C1403 | None in SMD; JLC's stocked 1000 µF polymers are through-hole | Global Sourcing or consign |

## Stocked, but thin

| Part | Refs | In stock |
| --- | --- | --- |
| STM32H563RIT6 (comms, step 7) | U401 | 12 |
| STM32H563VIT6 | U201 | 43 |
| CSD18540Q5B | Q101 | 26 |
| TPS26630RGER | U101 | 48 |
| ECS-160-10-36Q-ES-TR | Y201, Y401 | 67 |
| MAX-M10S-00B(-01) | U4504 | 68 |
| ADXL375BCCZ | U3304 | 160 |
| TPS1H100BQPWPRQ1 | U6304, U6404, U6504 | 273 |
| CPT-9019S-SMT-TR | BZ9001 | 277 |
| Harwin Gecko (G125) | CAN connectors, step 5 | Tens per variant; part chosen at step 5 |

JLC can hold parts in an account's private library ahead of an order.

The LTC6993 one-shots (U6301, U6401, U6501) are short too (1 stocked), but step 6 removes all three.

## Parts added by capture

| Part | Step | LCSC, stock |
| --- | --- | --- |
| BAT54T1G, onsemi, SOD-123 | 1 | C152458, 60,607 |
| 100 µF 6.3 V X5R 1206 (C219) | 1 | C15008 (Basic), 1,464,361 |
| MMC5983MA | 4 | C404329, 14,167 |
| SN74LVC1G08DBVR | 6 | C7666, 72,536 |
| TCAN3413DRBR (second) | 5 | C22445415, 1,001 |
| 470 µF aluminium hold capacitor | 2 | Many 6.3 × 7.7 mm parts stocked; a 6.3 V part's catalogue leakage (0.01CV ≈ 30 µA) meets the limit. Chosen at step 2 |

## Stocked with margin

STM32 aside, every other part with an MPN is stocked well beyond one board's need:
SN74LVC1G04/74/97, TMUX1511, TPD1E0B04, TPS2121, TPS22918, TPS2553-1, TPS3700, TPS3808G33,
TPS70933, TPS7A9101, USB4105-GF-A, USBLC6-2SC6, BAS116, ICM-42688-P, MS5607,
ABS07-32.768KHZ-7-T, JST GH BM02B / BM03B, Molex 430450600 / 430451000, Keystone 5001.

## For the full pass (step 8)

- Generic passives: match every value to a stocked part, Basic where one exists.
  There is no Basic 2.2 µF X7R 0603 (C209, C210, C220, C409, C410).
- Leave footprint-only items out of the BOM: the TC2030 pads and the 1 mm test pads.
