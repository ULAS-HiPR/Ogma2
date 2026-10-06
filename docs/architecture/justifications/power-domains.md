# Power domains, recovery and energy — recommendation

22 September 2026. **Proposed capture baseline; supersedes the earlier two-LDO
candidate.** CAD remains unchanged. [Power chapter](../02-power.md).

## Decision and reason

**Keep three TPS7A91 regulators: flight, comms, services.** One shared 4 V
TPSM63603 supplies them. Comms regulation belongs inside the comms fault boundary;
logging and CAN belong outside it. This directly supports the retained
[FF-01 behavior](../../../interfaces/flight-fault-contract.md): communications
failure must leave local sensing and recording available. It also avoids making
an otherwise healthy vehicle peer unreachable through a comms-regulator fault.

The earlier two-rail candidate contained downstream comms shorts but merged the
regulator-failure and aggregate-latch consequences. Recovering the merged group
would reboot USB/RF while also interrupting storage and CAN. A third LDO and its
support parts buy a named useful boundary; no quantitative reliability gain is
claimed. Keep the existing topology instead of implementing that merge.

| Fault | Proposed three-domain result | Residual common dependency |
| --- | --- | --- |
| Comms MCU/GNSS/radio short | U1501 limits/latches; flight can cycle the comms branch in battery mode | Common buck must withstand the limited load |
| Comms LDO output short | Comms lost; independently regulated services remain available | U1501 and common-buck transient behavior |
| Service device short | Its local limiter acts; unaffected service branches stay available if selectivity holds | Service LDO/input limiter |
| Service LDO/input trip | Flight and comms survive; flight can restart services using PD10 | Lost NOR tail and CAN/monitor outage are explicit |
| Flight LDO/common source failure | Flight unavailable | Three domains are not three independent computers |
| Regulator input-to-output failure | Its output group may be overvolted | Current limiting is not overvoltage isolation |

One LDO was rejected because it shares every regulated-output failure. Two were
rejected because a comms-regulator fault then loses logging/CAN. A separate buck
per domain adds magnetics and source interactions without creating independent
recovery; retain the common converter for this revision.

## Exact capture delta

| Reference / net | Capture instruction |
| --- | --- |
| U1701/U1801/U1901 | Retain TPS7A9101DSKR ×3, their input/output caps, NR/SS and PG networks |
| U1501 | Keep **before U1801**; IN=4V_PRE, OUT=COMMS_LDO_IN via existing link, EN=COMMS_BRANCH_EN |
| R1504 | Change 36.5 kΩ to **66.5 kΩ, 1%**; calculated limit 351–449 mA |
| U1601 | Keep **before U1901**; IN=4V_PRE, OUT=OPTIONAL_LDO_IN via existing link |
| U1601 EN (pin 3) / R1602 | Disconnect EN and the top of its 100 kΩ pulldown from FLIGHT_3V3; connect both to new **SERVICE_POWER_EN** |
| Flight PD10, pad 57 | GPIO SERVICE_POWER_EN, reset/off default low; replaces deleted servo3 PWM only |
| R1701/R1801/R1901 | **31.9 kΩ, 0.1%**, each; lower resistors remain 10 kΩ, 0.1% → 3.352 V nominal on all three domains |
| R1604 | Change 56.2 kΩ to **49.9 kΩ, 1%**; calculated limit 470–588 mA |
| 3V3_OPTIONAL | Keep the net identifier during capture; use “services” in human-facing labels. It powers NOR/CAN/AUX/sounder, not comms |
| Local enables/boundaries | Retain NOR/CAN/AUX limits and partial-power signal isolation; sensors direct from FLIGHT_3V3 (D-6.6) |
| Source logic | Core enable from 4V_PRE presence (D-6.5); keep battery-priority comms enable |

PD10 is the only new flight allocation. No output-authority or arm-sense pin is
reused. The proposed flight CSV records this delta; original frozen input CSVs
are unchanged until capture is authorized.

**Restart behavior:** service supply starts off; flight enables it after basic
clock/GPIO/watchdog setup. On a service fault, disable local service loads, bring
SERVICE_POWER_EN low for an initial 100 ms service-recovery interval, then permit
one restart with loads sequenced. **100 ms is an initial bench setting, not proof
of a power reset.** Measure every affected rail below its peripheral reset
threshold for the required interval, then measure restart. Set the released
off-time from those results; it may need to increase. Until demonstrated, do
not claim successful power-cycle recovery. A repeated fault latches the group unavailable for that power
session. Do not reset flight to repair it. In an active mission, restart only
when the mission's peer-loss contract permits the resulting outage; otherwise
remain explicitly degraded. This is a bounded recovery capability, not an
unconditional automatic retry loop or a command to an actuator.

## Voltage and headroom

The relocated downstream comms switch is removed from the proposal. Raising the
three LDO set points to 3.352 V gives common divider values and supervisor margin:
±1% LDO accuracy, ±0.1% resistors and ±100 nA feedback current give **3.310–3.394 V**.
Conservative TPS3808G33 release bound is **3.194 V** including threshold tolerance
and hysteresis. Static margin is **116 mV**, before PCB/ripple/transients. Allocate
50 mV for those healthy-operation effects; approximately 66 mV remains.

Selected MCU, five sensors, NOR, GNSS, CAN and 3.3 V logic stay within their
3.6 V operating ceilings; Wio allows 3.7 V. This does not allow startup overshoot
past those ceilings. Reference/analog ratios and rail measurements use the actual
set point. Preserve effective ≥10 µF at each TPS7A91 input/output after ceramic
bias derating. At 300 mA a 135 mΩ upstream switch loses ~41 mV **at the LDO input**;
check regulation against that input, not by subtracting it again from the output.

Retain C1403 **PCW0J102MCO1GS**, 1000 µF/6.3 V, on the held flight input after
LM73100. The old 0.98 ms example remains an illustration using 800 µF effective,
0.25 V usable drop and 204 mA; recalculate actual usable drop with the new output
set point and measured regulator headroom. No guaranteed final flash flush.

## Loads and limiter coordination

These are **design allocations**, not a claim to have measured or summed every
worst-case device current. Firmware/clock/mode choices must fit them.

| Domain | Continuous design ceiling | Allocation within ceiling |
| --- | --- | --- |
| Flight | 200 mA | MCU/support 150; sensors/boundaries 35; margin 15 |
| Comms | 300 mA | MCU/support 100; RF 150; tracking GNSS 35; margin 15 |
| Services | 200 mA | NOR write/boundary 65; CAN/boundary 80; AUX 25; sounder/support/margin 30 |

GNSS startup has a separate 100 mA allowance: start it with RF off. High-speed NOR
read can exceed the 65 mA writing allocation; USB download disables CAN/sounder
and uses the total-domain ceiling. No inference that average radio consumption
covers transmit peaks. The 700 mA sum allocates **2.8 W at 4 V** before upstream
losses; ideal LDO dissipation is ~0.454 W before switch drops.

For selectivity, use a NOR fault at its 306 mA maximum plus **135 mA** of healthy
services: ~441 mA versus service-input minimum 470 mA. CAN/AUX fault scenarios
must replace that branch's healthy allocation rather than blindly adding the
entire group again. An aggregate trip is still recoverable and does not remove
comms. Even simultaneous comms/service input limits plus 200 mA flight are about
**1.237 A** at the common converter; its 3 A nameplate is not a transient test.

## USB and endurance choices

Superseded 6 October (D-6.5): U4402 removed; U4401 limits at 387–491 mA from
attach and USB-only starts the flight core and comms at reduced clock. Configured download: ≤300 mA VBUS, only reduced-clock flight/comms and NOR;
no CAN/RF/GNSS/sounder. Sequence optional health measurements. Battery presence
permits normal operation; USB alone never implies full-load operation. Suspend is not supported.

**Kármán overlay (D-6.8): size the reference AV pack around 2S, 8 Ah nominal.** The workhorse pack comes from measured loads. Required usable energy is
at least **30 Wh at the installed temperature/load/UVLO**, not nameplate capacity.
Conservative budget: 8 h at 2.8 W/85% conversion plus 0.10 W upstream overhead,
then 4 h at 0.4 W/75% plus that overhead = **29.69 Wh**. 7.4 V × 8 Ah × a
provisional 65% usable-energy allowance gives 38.48 Wh. This allowance is a design
assumption to validate, not a cold/age guarantee. Actuator/output energy is extra
and cannot consume this logic/recovery allocation without recomputing it.

Reference pack envelope does not require a particular SKU or brand for capture:
2S lithium chemistry, 8.4 V maximum charge, connector/polarity and the ≥30 Wh
usable requirement are the electrical interface. A smaller pack may support a
shorter declared mission; it does not meet 8 h + 4 h by implication. No purchase
or pack construction is authorized by this recommendation.

Sources: [preserved netlist](../../../hardware/croi2/output/full-netlist.xml),
[TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf),
[TPS7A91](https://www.ti.com/lit/ds/symlink/tps7a91.pdf),
[TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf),
[accepted platform envelope](../../archive/karman-line-mission-hardening-report.md#accepted-provisional-platform-envelope),
[reproducible calculations](../../calculations/component-proposal-checks.py).
