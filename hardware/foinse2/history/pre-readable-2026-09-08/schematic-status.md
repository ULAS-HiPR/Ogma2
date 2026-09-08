# Foinse2 schematic and layout starter

7 September 2026. Engineering draft. Native KiCad 9.0.6 files are the working
CAD. Drawn circuitry and provisional values are model-authored implementation
proposals under Seán's authorisation, not a further team-approved parts freeze.

## What exists

11 schematic pages, 101 physical symbols, 100 assigned/imported footprints.
No MCU, firmware, CAN transceiver, onboard charger, automatic mission authority
or independent-recovery power path. The board is a power companion, not a
general vehicle controller.

| Sheet | Function |
| --- | --- |
| Foinse2 | Functional index |
| f01 / f01a | 2S source protection, transients and probes; no AV shunt |
| f02 / f02a | Separate 6S source protection, transients, shunt and probes |
| f03 | Samtec mate, protected auxiliary power and TCA4307 I2C boundary |
| f04 | Relocation note: AV monitor 0x40 is now Croí U7101 |
| f05 | Propulsion INA228 monitor, address 0x41 |
| f06 / f06a | ADS1115 0x48, dedicated temperature probes, voltage dividers and powered-off isolation |
| f07 | Named raw propulsion output and explicit charging/24 V scope boundary |

## Autonomous power paths

Each pack enters its own reverse-blocking CSD18540Q5B/TPS26630 circuit. A small
2N7002 implements the specified reverse-blocker gate arrangement. TPS26630
MODE is open for latch-off; SHDN is pulled from that branch's source. No MCU,
I2C transaction, monitor READY signal or Croí auxiliary supply is required for
source startup. Fault clearing is deliberate source cycling in this draft.

The battery positives never join. Both paths share the accepted ground
reference. Pack-side harness fuses are mandatory upstream: an eFuse on this
PCB cannot protect wire between the pack and PCB or a failed-short input TVS.
No fuse rating is invented without the pack, wire and connector limits.

| Starting setting | 2S avionics | 6S propulsion |
| --- | --- | --- |
| UV divider | 100k / 22.1k, 0.1% | 156k / 10k, 0.1% |
| Nominal UV start / stop | 6.63 / 6.20 V | 19.92 / 18.63 V |
| OV divider | 64.9k / 10k, 0.1% | 215k / 10k, 0.1% |
| Nominal OV | 8.99 V | 27.0 V |
| ILIM resistor | 3.00k, approximately 6 A | 6.04k, approximately 2.98 A |
| Slew capacitor | 22 nF | 22 nF |
| Input TVS proposal | Unidirectional SMBJ12A | Unidirectional SMBJ28A |
| Discharge shunt | None; moved to Croí R7101 | 5 mΩ, 2512, 1%, nominal 3 W |

These are nominal calculations, not guaranteed thresholds or usable continuous
load ratings. Minimum current-limit tolerance, source impedance, thermal
derating, startup capacitance, surge waveform, fuse clearing and reverse
transients remain to be checked. Source/output 2.2 µF 100 V 1210 capacitors are
starting footprints/values; effective capacitance and damping are unresolved.

R2011 proposes Vishay WSLP2512R0050FEA. Croí now owns the AV shunt R7101 and INA228 0x40; R1011 and U4001 are removed. R2011 is a two-terminal resistor
with Kelvin-routed measurement traces to its terminations, not a claimed
four-terminal package. At 6 A the nominal drop/dissipation is 30 mV/0.18 W;
at 3 A, 15 mV/0.045 W. The shunt follows protection and measures protected
discharge only. It does not measure current in the separate charging harness.
There is no tiny 0603 zero-ohm resistor in a main power or ground path.

## Croí boundary and monitoring

| Samtec contact | Foinse net | Direction / requirement |
| --- | --- | --- |
| 1 | VBAT_CROI | Protected 2S output to Croí input |
| 2 | GND | Full-current return |
| 3 | FOINSE_AUX_3V3 | Croí's protected auxiliary output powers monitoring |
| 4 | GND | Each return contact/path must withstand the full 6 A alternative return |
| 5 | FOINSE_SCL | Dedicated optional monitor bus |
| 6 | FOINSE_SDA | Dedicated optional monitor bus |
| 7 | FOINSE_FAULT_N | Open-drain source-switch / optional INA alert aggregation |
| 8 | NC | Spare, not energised |

J301 is MPS-08-01-01-L-RA-SD; Croí carries MPT. Both library footprints retain
six solder tails per electrical contact. Ground return geometry must not rely
on perfect current sharing or narrow down to one small via.

TCA4307 has connector-side pulls on Croí and 4.7k monitor-side pulls to AUX.
Its READY is a local probe, not source-enable authority. Pull-ups disappear
with the protected monitor supply. Croí must bound failed-bus work; this device
is not permission to block flight timing indefinitely.

The remaining propulsion INA228 has 10 Ω / 10 nF differential shunt filtering and a 100 Ω / 10 nF
VBUS filter. VBUS is sampled **after the reverse FET, before the eFuse**, not
at an unprotected cell tap. Positive high-voltage inputs may remain present
with VS absent within the INA228 specification. Negative transients and
differential overload remain separate limits. Revision-B initial ADCRANGE=0 provides ±163.84 mV for overcurrent headroom; measurement range is not permitted load current.
Die temperature is not battery temperature; no uncalibrated state-of-charge
authority follows from these devices.

ADS1115 uses two dedicated thermistor inputs and two protected-output voltage
inputs. The 2S divider is 22.1k + 22.1k over 10k; 6S is 110k + 110k over 10k.
TMUX1511 disconnects scaled voltage from the unpowered ADC. At nominal OV,
one shorted top resistor gives approximately 2.80 V or 2.25 V respectively.
This limited calculation is not a full single-fault analysis. Check absolute
input limits, partial rails, settling and leakage. Suggested sampling is
128 SPS with approximately 10 Hz/channel reporting, not an achieved result.

## Two new connector proposals

These are explicit draft selections, additional to the previously accepted
interface inventory. They do not redefine existing accepted pinouts.

- **J601: JST GH BM04B-GHS-TBT(LF)(SN)**, vertical four-way. 1 AV probe,
  2 ground, 3 propulsion probe, 4 ground. Dedicated isolated two-wire NTCs;
  10k bias resistors are provisional. Do not share a charger's probe bias.
  Thermistor curve, cable ESD/injection protection, clamp behavior and open/short
  classification remain open. This is not a finished external-lead protection
  circuit merely because the connector is drawn.
- **J701: Molex 430450200**, two-way Micro-Fit raw propulsion output. 1 positive,
  2 paired return. Its two-way circuit count differs from four-way 6S input
  J201; the 2S input uses the distinct Nano-Fit family. This is battery-class
  raw power, not regulated 24 V. The approximately 3 A branch limit is an
  aggregate proposal, not an allocation for unspecified solenoids.

Propulsion still owns its regulators, valve switching, state machine,
permissives, local safe behavior and physical hazardous-energy isolation. Croí
does not distribute general propulsion power or acquire direct valve authority.

## Charging and regulated actuator power

The accepted recommendation uses external matched balance chargers and a
passive, segregated service harness. Charging joins upstream of each discharge
reverse blocker through source-end protection. Pack-specific balance taps and
charger temperature leads stay with that harness. There is no charging through
Croí, no live generic balance connector invented here and no onboard charger.
Pack/charger pinout, service fusing and physical charging/arming exclusion still
need actual pack and harness choices before a charging assembly can be built.

A regulated 24 V actuator stage remains conditional on the coil schedule. No
LM5176 power stage, fabricated valve current budget or 24 V output connector is
included. The 60 × 80 mm footprint is the protection/monitor board described
here; it is not a promise that a future power converter fits. Independent
recovery power remains outside these shared paths.

## Layout and verification

All assigned parts are in nine movable functional-sheet groups. The outline and
four-layer setup are provisional; no copper routes, pours or drilled mounting
pattern have been created. Reference labels are on fabrication layers; finish
silkscreen during layout. Place source loops, shunt Kelvin traces, local bypass
capacitors and TVS return paths deliberately. Coarse clustering is not a final
decoupling or power layout. Do not route source/load current under the ADC or
through its reference connections. The missing Nano-Fit rectangle has no pads.

Observed from native exports: **278 pin checks, 91 boundary checks, zero ERC
violations, no exclusions**. A negative test rejects a merged 2S/6S positive
rail. Saved-board verification checks 100 footprints, 338 numbered pads,
schematic identity/DNP/BOM linkage, model paths, four layers, the outline and
courtyard/drill reservations. All pass. There are 86 locally resolved model
instances; the missing exact model list remains explicit in the library manifest.

DRC is not clean: six default 0.2 mm clearance findings concern the TCA4307's
0.15 mm internal pad gaps; 18 drill findings concern the two TPS26630 patterns'
0.2 mm thermal vias against a default 0.3 mm drill constraint. These need an
actual fabricator/assembly-compatible land-pattern and rule review, not hidden
exclusions. Unrouted connections are expected. Schematic parity reports only
the missing J101 footprint. No analog simulation, hardware, thermal, surge,
ESD, fuse, vibration, charge-service or flight test has passed by implication.

## Primary sources

The accepted architecture and local power study remain the decision source.
Component behavior and package checks use the manufacturers:

- [TI TPS2663](https://www.ti.com/lit/ds/symlink/tps2663.pdf) and
  [CSD18540Q5B](https://www.ti.com/lit/ds/symlink/csd18540q5b.pdf): source protection and reverse blocker.
- [TI INA228](https://www.ti.com/lit/ds/symlink/ina228.pdf): physical pin order,
  address straps and high-voltage inputs with independent VS.
- [TI ADS1115](https://www.ti.com/lit/ds/symlink/ads1115.pdf),
  [TMUX1511](https://www.ti.com/lit/ds/symlink/tmux1511.pdf) and
  [TCA4307](https://www.ti.com/lit/ds/symlink/tca4307.pdf): monitor pin order,
  rail limits, powered-off boundary and bus recovery.
- [Vishay WSLP](https://www.vishay.com/docs/30122/wslp.pdf): shunt family;
  final orderable suffix and assembly acceptance remain review items.
- [Littelfuse SMBJ](https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smbj_datasheet.pdf.pdf):
  TVS family starting selections. Installed surge/fuse coordination is unproven.

The local source-library manifest retains connector drawing provenance. The
exact Nano-Fit drawing's visual download remains blocked; textual dimensions
were not treated as enough to invent retention-hole coordinates.
