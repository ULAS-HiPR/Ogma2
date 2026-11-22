# Burrito 3D models: borrowed and drawn (22 Nov 2026)

Every physical part on Burrito now has a 3D model. Footprints with no model are pads only: the three
fiducials, the eight mounting holes, the two Tag-Connect TC2030 patterns (J2301, J4201) and the 25
1.0 mm test pads. J101's footprint came in capture step 15, from Molex drawing SD-105311-100; its model is drawn.

Before this, 17 part types had no model: KiCad's library has none for them, or the footprint named a
model that wasn't vendored. `tools/layout/fp_models.py` points the footprints at the files below.

## From KiCad's library

KiCad 9.0.7's 3D library, Ubuntu package `kicad-packages3d_9.0.7-1_all.deb`, fetched with apt (apt checks
the package hash). The files are copied unchanged: each SHA-256 matches the file in the package.

| Model | Footprint | Parts | Fit |
| --- | --- | --- | --- |
| `Crystal.3dshapes/Crystal_SMD_3215-2Pin_3.2x1.5mm.step` | `Ogma2:ABS07-32.768KHZ-7-T` | Y202 | Same 3.2 × 1.5 mm package |
| `Crystal.3dshapes/Crystal_SMD_2016-4Pin_2.0x1.6mm.step` | `Ogma2:ECS-160-10-36Q-ES-TR` | Y201, Y401 | Same 2.0 × 1.6 mm package |
| `Diode_SMD.3dshapes/D_SOD-882.step` | `Diode_SMD:D_SOD-882` | D4501 | KiCad's own pair |
| `Package_SO.3dshapes/Texas_HTSSOP-14-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3.155x3.255mm.step` | `Ogma2:TPS1H100BQPWPRQ1` | U6304, U6404, U6504 | TI's PWP package |
| `Package_SON.3dshapes/WSON-10-1EP_2.5x2.5mm_P0.5mm_EP1.2x2mm.step` | `Ogma2:TPS7A9101DSKR` | U1701, U1801, U1901 | TI's DSK package |
| `Package_LGA.3dshapes/ST_HLGA-10_2x2mm_P0.5mm_LayoutBorder3x2y.step` | `Ogma2:BMP390` | U3403 | **Stand-in.** Same 2 × 2 mm, 10-pad outline. Bosch gives 0.75 mm height; the model's height isn't checked against it |
| `Connector_Coaxial.3dshapes/SMA_Amphenol_132291_Vertical.step` | `Ogma2:SMA_Amphenol_132134_Vertical` | J4501, J4601 | **Stand-in.** The footprint copies KiCad's 132291 pad for pad (footprint audit). KiCad has 132134-10 and -11 models but no plain 132134 |

## Drawn here

These are drawn by `tools/layout/models3d.py` (CadQuery): `python3 tools/layout/models3d.py [part]`.
Each one is a simplified body:

- the outline is the footprint's F.Fab layer, itself from the maker's drawing;
- the height and features are listed below;
- the pins sit at the footprint's pads.

They're for the 3D view and fit checks, not for tooling. **Status** says what was checked:

- **unverified** means the number has no recorded source;
- **check** means it should be read off the maker's drawing before the bay fit check.

| Model | Parts | Body | Height | Status |
| --- | --- | --- | --- | --- |
| `TestPoint.3dshapes/TestPoint_Keystone_5190TR_ColorKeyed.step` | 18 yellow loops (Keystone 5194TR): TP2 … TP46 | 3.0 × 2.4 mm base 1.2 mm tall; 0.2 mm strip 1.2 mm wide arched over it | Strip top 2.5 mm | Keystone's SMT catalogue page (base, 2.5 mm height, .008 in strip); the base's height and the strip's width are drawn by eye |
| `TestPoint.3dshapes/TestPoint_Keystone_5000-5004_Miniature.step` | unused since D-22Nov.24 (was the 18 orange loops) | Ø2.5 mm insulator 1.6 mm tall; 0.5 mm tinned wire loop; one pin | Loop top 4.6 mm | Recorded in [testpoint-selection](../testpoint-selection.md) from Keystone's drawing (installed height 4.6 mm, body Ø2.5 mm); the insulator's 1.6 mm and the wire's 0.5 mm are drawn by eye |
| `TestPoint.3dshapes/TestPoint_Keystone_5010-5014_Multipurpose.step` | 4 black loops (Keystone 5011): TP1, TP16, TP23, TP47 | Ø3.2 mm insulator 2.8 mm tall; 0.8 mm wire | Loop top 8.1 mm | Distributor figure (DigiKey: 0.320 in), not checked against Keystone's drawing; the insulator and wire sizes are drawn by eye |
| `Connector_JST.3dshapes/JST_VH_B2P-VH_1x02_P3.96mm_Vertical.step` | J6102 | Shroud on the F.Fab outline; □1.14 mm posts 8.5 mm tall | 9.4 mm | Partly checked. JST's eVH drawing gives the □1.14 mm post and "8.5 (9.4)", but doesn't label which value is the housing top |
| `Connector_Molex.3dshapes/Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical.step` | J6101 | Shroud on the F.Fab outline; 0.64 mm posts | 9.4 mm | Unverified. Farnell's 39-28-1023 sheet gives no housing height; check Molex's drawing |
| `Connector_Harwin.3dshapes/Harwin_Gecko_G125-MS10605M2P_2x03_P1.25mm_Vertical.step` | J501, J502 | Black shroud on the F.Fab outline; posts at the SMT tails | 4.6 mm | Unverified. Harwin's G125-MS1XX05L2P drawing (same body family) shows 3.10 to 6.9 mm in side view, but its text doesn't label the height |
| `Fuse.3dshapes/Fuse_Littelfuse-NANO2-451_453.step` | F6101, F6102 | White ceramic body; 0.9 mm tinned end caps | 2.69 mm | Checked: Littelfuse's 451/453 sheet (Farnell copy) gives 6.10 × 2.69 × 2.69 mm. The 0.9 mm cap length is drawn by eye |
| `Buzzer_Beeper.3dshapes/MagneticBuzzer_PUI_SMT-1028-T-2-R.step` | BZ9001 | Black block with a 2 mm sound hole | 3.5 mm | Distributor figure (RS: 10.8 × 10 × 3.5 mm). PUI's PDF couldn't be read here |
| `RF_GPS.3dshapes/ublox_MAX-M10S.step` | U4504 | 0.8 mm green PCB with a tinned can | 2.5 mm | Checked: u-blox's data sheet UBX-20035208, table 21, gives 2.5 mm typical and 2.7 mm maximum. The can and PCB split is drawn by eye |
| `Package_DFN_QFN.3dshapes/Texas_RDH0030A_TPSM63603.step` | U1301 | Black body | 1.9 mm | Checked: TI's drawing RDH0030A is titled “1.9 mm max height” (the features list says 1.8 mm) |
| `Connector_Samtec.3dshapes/Samtec_MPT-08-01-01-L-RA-SD.step` | J102 | Black body with eight openings on its mating face, which projects 6.12 mm past the board edge (F.Fab); screw-down ears on the board around the two Ø3.56 mm NPTH holes at (±23.14, −6.15) | 6.28 mm | The height is marked REF on Samtec's drawing. The ear depth (to 3.6 mm in from the edge) is inferred |
| `Connector_Molex.3dshapes/Molex_Micro-Fit_3.0_43650-0215_1x02_P3.00mm_Vertical.step` | J103 | Black shroud on the F.Fab outline (latch ramp included); 0.64 mm posts | 9.9 mm | Unverified. JLC's listing gives 9.65 and 9.9 mm unlabelled; 9.65 mm is the body's length on the F.Fab, so 9.9 mm is taken as the height. Check Molex's SD-43650-006 |
| `Connector_Molex.3dshapes/Molex_Nano-Fit_105311-1102_1x02_P2.50mm_Vertical.step` | J101 | Black housing 3.48 × 5.94 mm with a cavity; the latch as a solid envelope on its side, 5.20 mm long, to 6.34 mm deep; tin clips and pins | 9.06 mm, latch 10.51 mm | Checked: Molex SD-105311-100 rev H gives 3.48, 6.34, 5.20, 9.06 and 10.51 mm. The latch's real shape, the clips and the pin size are drawn by eye |

None of these drawn models is from a maker's CAD file. Before the avionics-bay fit check, replace each
one with the maker's STEP file where one exists (Keystone, JST, Molex, Harwin, Littelfuse, PUI, u-blox,
TI and Samtec all publish them behind their sites' downloads), or confirm its height.
