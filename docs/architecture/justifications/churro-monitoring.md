# Churro monitoring and source boundaries — recommendation

22 September 2026. Proposed additions/deltas for capture; not installed circuitry.
[Churro chapter](../08-foinse-can.md).

## Keep the power companion small

Retain pack-powered TPS26630/CSD18540 protection on separate 2S AV and 6S PROP
positives, common reference, existing thresholds and source enables. Keep both
AV protection stages so Burrito works standalone. Do not claim selective
latch-off between the similar upstream/downstream stages. Fajita owns local
conversion; Churro supplies **protected raw 6S**, not regulated 24 V.

Set the reference continuous PROP distribution envelope to **2 A**, below the
existing nominal ~2.98 A limiter. Set the reference AV harness continuous ceiling
to **3 A**, including every connected load. Larger loads require an explicit
source/harness revision; a nominal 6 A limiter is not a promise of 6 A continuous
connector/PCB operation. These ceilings permit capture of a bounded distributor
without inventing a valve or motor. Preserve the source ratings in the electrical
notes; qualification verifies the real load fits them.

Recommend one **Littelfuse 0287005.PXCN 5 A, 32 V ATOF** at each pack's positive
service boundary, outside the PCB and close to the pack, in a **FHAC0001ZXJ covered holder**, with 20 AWG copper paired supply/return
for this short assembly. The holder's 16 AWG leads need retained, strain-relieved
joints to that harness; do not force 16 AWG into a 20–22 AWG contact. Keep
unfused length mechanically protected. The fuse protects wiring/upstream faults;
the eFuse handles downstream overload. Do not claim guaranteed fuse clearing at
an eFuse-limited ~3 A. Require source prospective fault current below the fuse's
1000 A interruption rating, and actual wire/holder/cable-temperature coordination
before assembly release. A pack or installation outside this envelope reopens
that assembly choice, not the MCU or sensor schematic.

Use the existing 2S Nano-Fit and 6S four-contact Micro-Fit source connectors;
never substitute matching source plugs. Grounds require full alternate-return
assessment through Samtec/CAN/USB. Charging remains an external matched charger
with packs isolated from the vehicle. No onboard charger, BMS or 24 V converter.

## Finish the two temperature inputs

**Select Vishay NTCLE305E4103SB**, 10 kΩ at 25 °C, insulated-lead sensor, for both
pack-surface probes. Use its published resistance table; do not substitute a
single generic beta coefficient. A surface probe is not a cell-core measurement.
Keep J601 cavity order AV probe / GND / PROP probe / GND. Each probe has its own
return; no connection to an externally biased charger thermistor.

Add **REF3325AIDBZR** for a 2.5 V bias and **ADG7421FBCPZ-RL7** for the two external
signal leads. The reference avoids treating ADS1115's internally referenced
voltage as ratiometric to an unmeasured AUX rail. The protected switch earns its
place because the probe cable can contact either nearby pack while AUX is off.
A small series resistor alone does not contain that sustained fault.

| Part / pin | Proposed connection |
| --- | --- |
| New U6201 REF3325, SOT-23-3 | 1 IN=ADC_3V3; 2 OUT=NTC_REF_2V5; 3 GND; C6201 1 µF input and C6202 1 µF output to GND, 16 V X7R 0603 |
| New U6202 ADG7421F, LFCSP-10 3×2 mm | 5 VDD=ADC_3V3; 4 GND and 6 VSS=GND; 7 IN2 and 8 IN1=ADC_3V3; C6203 100 nF, 16 V X7R 0603 local bypass |
| U6202 1 S1 / 2 S2 | J601.1 / J601.3 through separate **2.2 kΩ, 0.1%, 1206** resistors R6211/R6212 |
| U6202 10 D1 / 9 D2 | New AV_NTC_BIAS / PROP_NTC_BIAS nodes |
| Existing R6003/R6004 | Retain 10 kΩ 0.1%, but connect tops to NTC_REF_2V5 and bottoms to the respective **D-side** bias node |
| Existing R6005/R6006 | Retain 1 kΩ from bias nodes to ADS1115 AIN0/AIN1; change existing C6002/C6003 to 1 µF, 16 V X7R 0603 at each ADC pin to GND |
| New D6201/D6202 | Littelfuse SMF33CA from each connector signal to GND, ahead of the 2.2 kΩ resistor; short connector-side return |
| U6202 3 FF | R6201 10 kΩ 0603 pull-up to ADC_3V3 and TP6201; no new MCU GPIO or unexplained service-status bit |
| R6202 | 10 kΩ 0603 from ADC_3V3 to GND, discharging the otherwise floating off rail; ~0.34 mA powered cost |
| U6202 package | CP-10-16 manufacturer package; verify the exact land pattern, pin-one and underside drawing during library creation |

Do not leave the old NTC pull-ups at the connector: that would bypass the fault
boundary. Retain TMUX1511 U6101 for the **separate voltage-divider inputs**; it
does not protect the NTC leads. New references are board-local proposals.

Normal conversion uses `Rprobe = 10000 × Vadc / (Vref − Vadc) − 2200 − Ron`;
the post-bias 1 kΩ contributes input-leakage error, not the divider's series leg.
Use 12 Ω nominal Ron for a starting correction and include its 19 Ω bound through
85 °C in the error ledger. Account for bias/reference tolerance, ADC input loading,
lead resistance, switch leakage and mounting/self-heating. **±2 °C installed
surface-temperature accuracy over −20…+70 °C** is the proposed acceptance target,
not a result. Open/short/out-of-range reports invalid; never display a fabricated
cold or healthy temperature.

Use ADS1115 ±4.096 V range, 128 SPS single-shot conversions; voltages at 10 Hz,
temperatures at 2 Hz, with bounded I²C work. Allow 100 ms after bias startup before
accepting a temperature. Initial diagnostic windows: below 0.55 V or above 2.40 V
means invalid/probe fault or outside this platform range; retain raw voltage.
The normal nominal range is approximately 0.71–2.27 V. Refine calibration, not
hardware authority, from measured error. Probe wiring is ≤0.5 m per assembly.

ADG source terminals have ±60 V powered/unpowered protection. SMF33CA's listed
53.3 V clamp is at its specified pulse, not an IEC system guarantee. Cable-fault
and transient tests must include AUX absent, both polarities and the ADC-side
waveform. No component rating alone proves the assembled input survives ESD.

REF33 Rev I §8.1 (Figure 8-1) and §8.4 recommend 1–10 µF at IN; the selected C6201 is 1 µF.
C6202 is also 1 µF, within the specified output range. ADG7421F Rev 0 p. 30
identifies the exact CP-10-16 package; use that drawing for the land pattern.

## Other measurements and observability

Keep AV INA228 at Burrito 0x40, PROP INA228 at Churro 0x41, ADS1115 at 0x48 and
I2C4 initially 100 kHz. INA AV current remains 100 Hz; PROP monitoring starts at
10 Hz. A read timeout is bounded; no retry loop may stall flight. Source protection
starts and operates with AUX missing. INA PROP VBUS is before its eFuse; ADS's
protected-output tap answers a different question. Publish both with location,
validity and age. Low shared nFAULT identifies a fault, not its source.

## Why these choices

Keeping rail-biased NTCs was cheaper but lacked an absolute bias measurement.
Adding another ADC channel solely for that rail costs topology/firmware changes;
a 2.5 V reference preserves all four existing ADS channels. Simple clamps can
back-power the ADC rail during a cable fault; the protected switch addresses
power-off faults explicitly. The cost is two ICs and passives, one new LFCSP
footprint and a modest resistance correction. That is confined to the two
external probes rather than spreading a new controller across Churro.

Sources: [Vishay probe table](https://www.vishay.com/docs/29076/ntcle305.pdf),
[REF33 Rev I](https://www.ti.com/lit/ds/symlink/ref33.pdf),
[ADG7421F Rev 0](https://www.analog.com/media/en/technical-documentation/data-sheets/adg7421f.pdf)
(manufacturer PDF inspected, pp. 5–6, 13, 25–30; [backup mirror](https://static.chipdip.ru/lib/552/DOC056552915.pdf)),
[ADS1115](https://www.ti.com/lit/ds/symlink/ads1115.pdf),
[SMF ratings](https://www.littelfuse.com/assetdocs/tvs-diode-smf-datasheet?assetguid=7eb8a5b6-bdd0-4561-8f19-0c3cc6f9b2af),
[ATOF ratings](https://www.littelfuse.com/assetdocs/littelfuse-datasheet-287-atof?assetguid=43dcdce8-8ca2-426f-8998-7e566f048d40),
[FHAC0001ZXJ holder drawing](https://www.littelfuse.com/assetdocs/fhac0001zxj-2d-print?assetguid=3959eb51-0df1-4ffd-a2a6-c64b8e165c85),
[native source](../../../hardware/foinse2/output/full-netlist.xml).
