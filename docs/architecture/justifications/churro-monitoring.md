# Churro monitoring and source boundaries

Proposed additions for capture, 22 September 2026, updated for D-6.3 and
D-2Nov.7. Not built.
See the [Churro chapter](../08-foinse-can.md).

## Keep the power companion small

**Protection stays as it is.** Pack-powered TPS26630 / CSD18540 protection on
separate 2S AV and 6S PROP positives, a common reference, the existing
thresholds and source enables. Both AV protection stages stay, so Burrito still
works standalone. Don't claim which of the two similar AV stages trips first.
AV U1001 moves to auto-retry (D-6.3); PROP U2001 waits for the propulsion owner.
Fajita does its own conversion. Churro supplies **protected raw 6S**, not
regulated 24 V.

**Current ceilings.**

- PROP: **2 A** continuous, below the existing ≈2.98 A nominal limiter.
- AV harness: **3 A** continuous, counting every connected load.
- A 6 A nominal limiter is not a promise of 6 A continuous through connectors
  and PCB. Bigger loads need a source and harness revision.
- These ceilings let capture go ahead with a bounded distributor, without
  inventing a valve or motor. Keep the source ratings in the electrical notes;
  qualification checks the real load fits.

**Pack fuse.** One **Littelfuse 0287005.PXCN** (5 A, 32 V, ATOF) at each pack's
positive service boundary, off the PCB and close to the pack, in a
**FHAC0001ZXJ** covered holder.

- 20 AWG copper paired supply and return for this short assembly.
- The holder's 16 AWG leads need retained, strain-relieved joints to that
  harness. Don't force 16 AWG into a 20–22 AWG contact.
- Keep the unfused length mechanically protected.
- The fuse covers wiring and upstream faults; the eFuse handles downstream
  overload. Don't claim the fuse clears at an eFuse-limited ≈3 A.
- Source prospective fault current must stay below the fuse's 1000 A
  interrupting rating. Check wire, holder and cable temperature together before
  releasing the assembly.
- A pack or installation outside this envelope reopens the fuse assembly, not
  the MCU or sensor schematic.

**Connectors and charging.** Use the existing 2S Nano-Fit and 6S four-contact
Micro-Fit source connectors; never swap in matching source plugs. Grounds need a
full alternate-return check through Samtec, CAN, USB and the umbilical. Charging
stays on an external matched charger with the packs off the vehicle. No onboard
charger, BMS or 24 V converter, and the umbilical never charges.

**Rail power (D-2Nov.7).** A ground umbilical (J801) feeds both branches on the
rail. Each source, pack or umbilical, gets its own ideal-diode stage (LM74700-Q1
class plus an N-FET) ahead of U1001 / U2001, so the same enables and protection
apply to either source, and no current flows into a pack. That's four stages,
two per branch. A fuse and a TVS sit at the umbilical connector. The AV umbilical
is set at 8.4 V at Churro, below U1001's 8.99 V and Burrito's TPS2121 trip; the
PROP voltage (≈24–25 V) is the propulsion owner's call. The higher source
carries the load. The enable bias and the UV / OV dividers move to the ORed node
so the umbilical alone can enable.

## Finish the two temperature inputs

**Probe: Vishay NTCLE305E4103SB**, 10 kΩ at 25 °C, insulated leads, one on each
pack surface.

- Use Vishay's resistance table, not a generic beta value.
- A surface probe doesn't measure cell core temperature.
- J601 order: AV probe / GND / PROP probe / GND. Each probe has its own return
  and never connects to a charger's externally biased thermistor.

**Add a 2.5 V reference and a protected switch.** REF3325AIDBZR biases the
probes. ADG7421FBCPZ-RL7 protects the two external leads.

- The reference is needed because the ADS1115 measures against its own internal
  reference, not the AUX rail, which nothing measures.
- The switch is needed because the probe cable can touch either nearby pack
  while AUX is off. A small series resistor alone can't hold off that sustained
  fault.

| Part and pin | Connection |
| --- | --- |
| New U6201 REF3325, SOT-23-3 | 1 IN = `ADC_3V3`; 2 OUT = `NTC_REF_2V5`; 3 GND. C6201 1 µF at input and C6202 1 µF at output to GND, 16 V X7R 0603 |
| New U6202 ADG7421F, LFCSP-10 3 × 2 mm | 5 VDD = `ADC_3V3`; 4 GND and 6 VSS = GND; 7 IN2 and 8 IN1 = `ADC_3V3`. C6203 100 nF 16 V X7R 0603 local bypass |
| U6202 1 S1 / 2 S2 | J601.1 / J601.3, each through its own **2.2 kΩ 0.1% 1206** resistor, R6211 / R6212 |
| U6202 10 D1 / 9 D2 | New nodes `AV_NTC_BIAS` / `PROP_NTC_BIAS` |
| Existing R6003 / R6004 | Keep 10 kΩ 0.1%. Tops to `NTC_REF_2V5`; bottoms to their **D-side** bias node |
| Existing R6005 / R6006 | Keep 1 kΩ from the bias nodes to ADS1115 AIN0 / AIN1. Change C6002 / C6003 to 1 µF 16 V X7R 0603, ADC pin to GND |
| New D6201 / D6202 | Littelfuse SMF33CA from each connector signal to GND, before the 2.2 kΩ resistor; short return on the connector side |
| U6202 3 FF | R6201 10 kΩ 0603 pull-up to `ADC_3V3` and TP6201. No new MCU pin, no unexplained status bit |
| R6202 | 10 kΩ 0603, `ADC_3V3` to GND, to drain the otherwise floating off rail. Costs ≈0.34 mA when powered |
| U6202 package | CP-10-16. Check the land pattern, pin one and underside drawing when building the library |

- Don't leave the old NTC pull-ups at the connector. That would bypass the fault
  boundary.
- Keep TMUX1511 U6101 for the **separate voltage-divider inputs**. It doesn't
  protect the NTC leads.
- New reference designators are board-local proposals.

**Converting a reading.**
`Rprobe = 10000 × Vadc / (Vref − Vadc) − 2200 − Ron`. The 1 kΩ after the bias
node adds input-leakage error; it isn't part of the divider.

- Start with Ron = 12 Ω nominal. Carry its 19 Ω bound up to 85 °C in the error
  budget.
- Also count bias and reference tolerance, ADC input loading, lead resistance,
  switch leakage, mounting and self-heating.
- Target: **±2 °C installed surface accuracy over −20 to +70 °C**. That is the
  acceptance target, not a result.
- Open, short or out of range reports invalid. Never show a made-up cold or
  healthy temperature.

**ADC settings.** ADS1115 ±4.096 V range, 128 SPS single-shot. Voltages at 10 Hz,
temperatures at 2 Hz, bounded I²C work. Wait 100 ms after the bias starts before
trusting a temperature. Below 0.55 V or above 2.40 V means invalid, a probe
fault or outside this platform's range; keep the raw voltage. The normal range is
about 0.71–2.27 V. Measured error refines calibration, not hardware authority.
Probe wiring is ≤0.5 m per assembly.

**Fault limits.** The ADG source pins survive ±60 V powered or unpowered. The
SMF33CA's 53.3 V clamp is at its rated test pulse, not an IEC system guarantee.
Cable-fault and transient tests must cover AUX absent, both polarities and the
ADC-side waveform. No part rating alone proves the assembled input survives ESD.

REF33 Rev I §8.1 (Figure 8-1) and §8.4 recommend 1–10 µF at IN; C6201 is 1 µF.
C6202 is 1 µF, inside the output range. ADG7421F Rev 0 p. 30 names the exact
CP-10-16 package; use that drawing for the land pattern.

## Other measurements and observability

- AV INA228 on Burrito at 0x40, PROP INA228 on Churro at 0x41, ADS1115 at 0x48.
  I2C4 starts at 100 kHz.
- AV current at 100 Hz; PROP monitoring starts at 10 Hz.
- A read timeout is bounded. No retry loop may stall flight.
- Source protection starts and runs with AUX missing.
- PROP INA228 VBUS is before its eFuse; the PROP ADS tap is on the protected
  output. They answer different questions. Publish both with location, validity
  and age.
- The AV ADS tap moves from the protected output to the AV pack, before its
  ideal diode (D-2Nov.7), so the pack stays readable while the umbilical carries
  the load. Burrito's INA228 reads the AV bus; bus well above pack means the
  umbilical is live.
- A low shared nFAULT says there's a fault, not where.

## Alternatives considered

- **Keep rail-biased NTCs.** Cheaper, but no absolute bias measurement.
- **Spend another ADC channel on that rail.** Changes topology and firmware. The
  2.5 V reference keeps all four ADS channels.
- **Simple clamps.** Can back-power the ADC rail during a cable fault. The
  protected switch handles power-off faults directly.

Cost of the choice: two ICs plus passives, one new LFCSP footprint and a small
resistance correction, all confined to the two external probes. No new
controller on Churro.

Sources: [Vishay probe table](https://www.vishay.com/docs/29076/ntcle305.pdf),
[REF33 Rev I](https://www.ti.com/lit/ds/symlink/ref33.pdf),
[ADG7421F Rev 0](https://www.analog.com/media/en/technical-documentation/data-sheets/adg7421f.pdf)
(pages 5–6, 13, 25–30 checked; [backup mirror](https://static.chipdip.ru/lib/552/DOC056552915.pdf)),
[ADS1115](https://www.ti.com/lit/ds/symlink/ads1115.pdf),
[SMF ratings](https://www.littelfuse.com/assetdocs/tvs-diode-smf-datasheet?assetguid=7eb8a5b6-bdd0-4561-8f19-0c3cc6f9b2af),
[ATOF ratings](https://www.littelfuse.com/assetdocs/littelfuse-datasheet-287-atof?assetguid=43dcdce8-8ca2-426f-8998-7e566f048d40),
[FHAC0001ZXJ holder drawing](https://www.littelfuse.com/assetdocs/fhac0001zxj-2d-print?assetguid=3959eb51-0df1-4ffd-a2a6-c64b8e165c85),
[Churro netlist](../../../hardware/foinse2/output/full-netlist.xml).
