# Burrito footprint audit (before placement, S3)

**22 November 2026.** Every board-local `Ogma2*` footprint that a Burrito part uses, with what its copper is
checked against. KiCad's own footprints (from `Capacitor_SMD`, `Connector_*` and so on) aren't listed: they are
KiCad 9.0.7's, vendored unchanged ([manifest](libraries/board-library-manifest.json)).

- **Pad for pad:** `tools/layout/phase3/fp_twins.py` matched the copper against every KiCad 9.0.7 footprint
  (pad number, centre and size within 0.01 mm). A twin means the land is KiCad's IPC-7351 nominal for that
  package; the part's package was checked against the twin's name.
- **Maker's drawing:** checked against the drawing named, when the footprint was made or on 22 Nov.
- **J101:** drawn in capture step 15 from Molex SD-105311-100 rev H; see its row.

| Footprint | Parts | Copper checked against | Note |
| --- | --- | --- | --- |
| `Ogma2:TestPoint_Keystone_5190TR_ColorKeyed` | the 18 yellow loops (TP2 … TP46) | Keystone's SMT Test Points catalogue page, 5190TR–5199TR pad layout (.118 × .059 in) and base (.118 × .094 in) | Drawn in capture step 18 (D-22Nov.24). One pad; the base's notch drawn as a rectangle |
| `Ogma2:105311-1102` | J101 | Molex SD-105311-100 rev H (LCSC copy): pin, clip and peg holes, pitch, C, the peg's offset; `s15_check.py` checks them | Drawn in capture step 15. Pads ours (sweep §10): clips no net, 0.22 mm from the pins; peg unplated, on the latch side (the drawing's views; KiCad's 105309-xx02 agrees) |
| `Ogma2:430450600` | J6601 | KiCad `Connector_Molex:Molex_Micro-Fit_3.0_43045-0612_2x03_P3.00mm_Vertical`, pad for pad | Copper twin of KiCad's vertical 43045-0612 (same 3.0 mm grid); its body and courtyard (14.3 x 13.8 mm) are the right-angle part's |
| `Ogma2:ABS07-32.768KHZ-7-T` | Y202 | Abracon ABS07 drawing (2022-08-10, p. 4) |  |
| `Ogma2:ADXL375BCCZ` | U3304 | KiCad `Package_LGA:LGA-14_3x5mm_P0.8mm_LayoutBorder1x6y`, pad for pad |  |
| `Ogma2:BMP390` | U3403 | Bosch BST-BMP390-DS002, p. 49 (land equals outline) |  |
| `Ogma2:CSD17318Q2` | Q6301, Q6401, Q6501 | TI DQK0006C land pattern, p. 10 (also KiCad Texas_DQK, pad for pad) |  |
| `Ogma2:CSD18540Q5B` | Q101 | KiCad `Package_TO_SOT_SMD:TDSON-8-1`, pad for pad |  |
| `Ogma2:ECS-160-10-36Q-ES-TR` | Y201, Y401 | ECS ECX-2236Q suggested land (Rev 2020, p. 1) |  |
| `Ogma2:G125-MS10605M2P` | J501, J502 | KiCad `Connector_Harwin:Harwin_Gecko_G125-MS10605M2P_2x03_P1.25mm_Vertical`, pad for pad |  |
| `Ogma2:ICM-42688-P` | U3204 | KiCad `Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y`, pad for pad |  |
| `Ogma2:INA228AIDGSR` | U7101 | KiCad `Package_SO:VSSOP-10_3x3mm_P0.5mm`, pad for pad |  |
| `Ogma2:LM73100RPWR` | U1401 | TI RPW0010A land drawing 4225183/A |  |
| `Ogma2:LSM6DSV16XTR` | U3104 | KiCad `Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y`, pad for pad |  |
| `Ogma2:MMC5983MA` | U3701 | MEMSIC MMC5983MA Rev. A p. 20 land pattern (checked 22 Nov; also KiCad LGA-16 3x3, pad for pad) |  |
| `Ogma2:MPT-08-01-01-L-RA-SD` | J102 | Samtec MPT RA-SD drawing and footprint, Rev B |  |
| `Ogma2:MS560702BA03-50` | U3503 | KiCad `Package_LGA:LGA-8_3x5mm_P1.25mm`, pad for pad |  |
| `Ogma2:MX66L2G45GMI00` | U3604 | KiCad `Package_SO:SOIC-16W_7.5x12.8mm_P1.27mm`, pad for pad |  |
| `Ogma2:SMA_Amphenol_132134_Vertical` | J4501, J4601 | KiCad `Connector_Coaxial:SMA_Amphenol_132291_Vertical`, pad for pad |  |
| `Ogma2:SN74LVC1G74DCUR` | U6001 | KiCad `Package_SO:VSSOP-8_2.3x2mm_P0.5mm`, pad for pad |  |
| `Ogma2:SN74LVC1G97DBVR` | U1202, U1204, U4501, U4601 | KiCad `Package_TO_SOT_SMD:SOT-23-6`, pad for pad |  |
| `Ogma2:STM32H563VIT6` | U201 | KiCad `Package_QFP:LQFP-100_14x14mm_P0.5mm`, pad for pad |  |
| `Ogma2:TC2030-NL-FP` | J2301, J4201 | KiCad `Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical`, pad for pad |  |
| `Ogma2:TCAN3413DRBR` | U503, U505 | KiCad `Package_SON:VSON-8-1EP_3x3mm_P0.65mm_EP1.65x2.4mm`, pad for pad |  |
| `Ogma2:TMUX1511PWR` | U3602, U3603, U4503, U4603, U4604, U6701, U6901, U7002, U8001 | KiCad `Package_SO:TSSOP-14_4.4x5mm_P0.65mm`, pad for pad |  |
| `Ogma2:TPS1H100BQPWPRQ1` | U6304, U6404, U6504 | TI PWP0014K drawing 4229706/B (TPS1H100-Q1 Rev D) |  |
| `Ogma2:TPS2121RUXR` | U1101 | KiCad `Package_DFN_QFN:Texas_VQFN-HR-12_2x2.5mm_P0.5mm`, pad for pad |  |
| `Ogma2:TPS22918DBVR` | U4502, U4602 | KiCad `Package_TO_SOT_SMD:SOT-23-6`, pad for pad |  |
| `Ogma2:TPS2553DBVR-1` | U1501, U1601, U3601, U4401, U501, U7001 | KiCad `Package_TO_SOT_SMD:SOT-23-6`, pad for pad |  |
| `Ogma2:TPS26630RGER` | U101 | KiCad `Package_DFN_QFN:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias`, pad for pad | Pads 0.825 x 0.25 mm at +-1.9625 (KiCad's IPC nominal); TI's RGE0024H example is 0.58 x 0.24 at +-1.9125, EP 2.7. Kept [J]: standard IPC land, 0.2 mm to the EP |
| `Ogma2:TPS3430WDRCR` | U2302 | KiCad `Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm`, pad for pad |  |
| `Ogma2:TPS3700DDCR` | U1201, U6103 | KiCad `Package_TO_SOT_SMD:SOT-23-6`, pad for pad |  |
| `Ogma2:TPS3808G33DBVR` | U2301, U4201 | KiCad `Package_TO_SOT_SMD:SOT-23-6`, pad for pad |  |
| `Ogma2:TPS70933DBVR` | U1102 | KiCad `Package_TO_SOT_SMD:SOT-23-5`, pad for pad |  |
| `Ogma2:TPS7A9101DSKR` | U1701, U1801, U1901 | KiCad `Package_DFN_QFN:Texas_S-PDSO-N10_EP1.2x2mm`, pad for pad |  |
| `Ogma2:TPSM63603RDHR` | U1301 | TI RDH0030A drawing 4226150/B, pp. 43-44 |  |
| `Ogma2:TXU0101DCKR` | U4302 | TI DCK0006A land pattern 4214835/D (fixed 22 Nov, step 11a) |  |
| `Ogma2:TXU0202DCUR` | U4301 | KiCad `Package_SO:VSSOP-8_2.3x2mm_P0.5mm`, pad for pad |  |
| `Ogma2:TXU0304PWR` | U4303, U502, U504 | KiCad `Package_SO:TSSOP-14_4.4x5mm_P0.65mm`, pad for pad |  |
| `Ogma2:USB4105-GF-A` | J4401 | KiCad `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`, pad for pad | NPTH layers written `*.Cu` (step 11c, 22 Nov) |
| `Ogma2:Wio-LR2021` | U4606 | Seeed's official KiCad library, corrected locally for KiCad 9 |  |
| `Ogma2_GNSS:MAX-M10S-00B` | U4504 | u-blox UBX-20053088 R05 p. 82 (copper); also KiCad RF_GPS:ublox_MAX, pad for pad |  |
