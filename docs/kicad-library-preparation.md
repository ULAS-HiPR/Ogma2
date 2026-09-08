# Ogma 2 KiCad library preparation

7 September 2026. Project-local draft libraries now exist: **46 PCB symbols,
45 assigned footprints, 27 parts with resolved local 3D models**. The exact
Nano-Fit footprint remains unassigned and final drawing/assembly audits remain open.
See [library usage and current status](../hardware/README.md),
[per-part checks](../hardware/libraries/inventory.csv) and
[remaining work](../hardware/libraries/review-notes.md).

The material below records the preceding feasibility audit and intended checks;
its “not imported” observations describe that earlier audit, not the current
library state. No global KiCad tables were changed.
Selected hardware is fixed by the [accepted baseline](architecture-acceptance-2026-09-07.md).

## Answer

The library work can be handled through files and KiCad's native tools. It does
not require Seán to manually repeat Ultra Librarian imports or authorise UI
schematic/PCB routing. Prefer checked native KiCad assets; use vendor-native
downloads or manufacturer drawings for the gaps.

Deliver project-local symbols, footprints, available 3D models, portable library
tables and a per-part source/check record. Keep exact MPNs and suffixes. Do not
substitute a different component because its library model is easier to obtain.

## Observed local capability

Installed KiCad: **9.0.6**, at `/Applications/KiCad.app`.
Its CLI advertises symbol and individual footprint SVG export. Native `pcbnew`
loaded the selected MCU package and six connector footprints, exposing their
pad numbers. Export rendering was not executed in this read-only audit.
The [KiCad CLI reference](https://docs.kicad.org/9.0/en/cli/cli.html) documents
the automated export path; installed command help governs version differences.

Stock library roots:

- `/Applications/KiCad.app/Contents/SharedSupport/symbols`
- `/Applications/KiCad.app/Contents/SharedSupport/footprints`

The review's partial core table has 40 unique MPNs. Eleven stock symbol/family
matches were located. **Availability is not completed electrical validation.**

| Selected part | Stock symbol |
| --- | --- |
| STM32H563VIT6 | `MCU_ST_STM32H5:STM32H563VITx` |
| ADS1115IDGSR | `Analog_ADC:ADS1115IDGS` |
| MS560702BA03-50 | `Sensor_Pressure:MS5607-02BA` |
| TPS7A9101DSKR | `Regulator_Linear:TPS7A91` |
| TPS3430WDRCR | `Power_Supervisor:TPS3430WDRC` |
| TPS3808G33DBVR | `Power_Supervisor:TPS3808DBV` |
| INA228AIDGSR | `Sensor_Energy:INA228` |
| TPS26630RGER | `Power_Management:TPS26630RGE` |
| CSD18540Q5B | `Transistor_FET:CSD18540Q5B` |
| LTC6993IS6-1#TRMPBF | `Timer:LTC6993xS6-1` |
| SN74LVC1G97DBVR | `74xGxx:74LVC1G97` |

H563's non-Q symbol has 100 numbered pins. The native parser confirmed 100 pads
in `Package_QFP:LQFP-100_14x14mm_P0.5mm`. A complete audit must still compare
every pin with the ST package table and the accepted flight/comms allocations.
Family symbols need the exact value, footprint and variant-specific checks.

Nine distinct PCB connector footprint requirements were identified; six have
stock matches:

| Selected PCB part | Stock footprint |
| --- | --- |
| 430450400 | `Connector_Molex:Molex_Micro-Fit_3.0_43045-0400_2x02_P3.00mm_Horizontal` |
| 430450600 | `Connector_Molex:Molex_Micro-Fit_3.0_43045-0600_2x03_P3.00mm_Horizontal` |
| 430450800 | `Connector_Molex:Molex_Micro-Fit_3.0_43045-0800_2x04_P3.00mm_Horizontal` |
| BM03B-GHS-TBT | `Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical` |
| USB4105-GF-A | `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` |
| TC2030-NL pattern | `Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical` |

Missing exact connector footprints: **Nano-Fit 1053111102 and both Samtec
MPS/MPT halves**. Existing 105309, UMPS and UMPT footprints are not substitutes.
Audit Samtec's six tails per contact, body orientation, drill positions, board
edge, 7.39 mm mating gap and separate retention hardware against both drawings.

Many new sensors, RF/storage and TI protection/isolation parts lack exact stock
symbols. A missing symbol does not necessarily require a custom footprint:
reuse a standard package only after checking its actual drawing and pad map.

## Rev 1 reuse and traps

The old Croí library contains an exact MS560702BA03-50 vendor symbol and
`SON125P300X500X100-8N` footprint under
the separate Ogma 1 checkout, `croi/hardware/Croí - Kicad/Lib/`
(workspace-local historical source, not part of this repository).
ADXL375 is embedded in the old Croí schematic and board; the board parser found
U2 with 14 pads. Reuse requires revalidation, not an assumption that Rev 1 was
correct. Loading that old board emitted a wxApp assertion despite returning
the expected objects; do not hide this as a clean native validation run.

Do not copy the old library tables: they contain absolute `C:/Users/...` paths.
Resolve symbol inheritance when extracting stock or embedded definitions.

Stock MCU, JST and USB STEP references resolve locally. The three Micro-Fit
footprints reference absent STEP files. Tag-Connect is a bare PCB pattern and
needs no connector model. Other 3D coverage is unaudited. Model appearance does
not prove land-pattern dimensions; an approximate body is labelled approximate.

## Preparation and checks

1. Freeze the exact selected MPN inventory, distinguishing PCB parts, harness
   parts, unselected support passives and conditional propulsion populations.
2. Create project-local `Ogma2.kicad_sym`, `Ogma2.pretty` and model directories,
   with library tables based on `${KIPRJMOD}`. No global table edits or another
   computer's absolute paths. Preserve source licences and attribution.
3. Reuse stock/Rev 1 assets where suitable. Fetch manufacturer/vendor-native
   assets where available. Generate the remainder from primary package and
   pin tables. If a vendor requires Seán's login or terms approval, report that
   specific dependency; no assumption that Ultra Librarian access is available.
4. Check full pin sets/names/electrical types, exposed-pad connectivity,
   multi-pad contacts, pin 1, mirror/top-bottom conventions, drill and annular
   dimensions, mask/paste, courtyard, body and insertion/service clearance.
5. Load through KiCad, export review views and inspect them. Match the MCU
   symbols against both accepted 100-pad CSVs. A parser pass is not a drawing
   or schematic correctness pass.
6. Return one reviewable part inventory with explicit unchecked items. The
   deliverable is ready for schematic use only to its stated verification scope;
   no schematic routing, board routing, purchasing or firmware work is included.

KiCad's design-use exception permits use in electronic designs without imposing
its library licence on the board. Redistributed library collections retain
CC-BY-SA 4.0 and attribution; keep that distinct from the unresolved Ogma 2
project licence. [Official library licence](https://www.kicad.org/libraries/license/)

No project library, global configuration or predecessor hardware was changed
by this feasibility audit. No vendor download, installation or upload occurred.
