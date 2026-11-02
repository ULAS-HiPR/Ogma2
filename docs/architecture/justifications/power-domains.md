# Power domains, restart and energy

Proposed capture baseline, 22 September 2026, updated for D-6.5, D-6.8, D-7.1,
D-2Nov.3, D-2Nov.6 and D-2Nov.11. It replaces the earlier two-regulator idea.
CAD is unchanged. See the [power chapter](../02-power.md).

## Decision

**Keep three TPS7A91 regulators: flight, comms and services.** One TPSM63603
buck at 4 V feeds all three.

Why three: comms regulation belongs inside the comms fault boundary, and
logging and CAN belong outside it. That is what
[FF-01](../../../interfaces/flight-fault-contract.md) needs: a comms failure
must leave sensing and recording running. It also means a comms regulator fault
can't make an otherwise healthy vehicle unreachable over CAN.

The earlier two-rail version contained comms shorts but put the regulator
failure and the group latch-off on the same side as storage and CAN. Recovering
that group would reboot USB and radio and interrupt storage and CAN at the same
time. A third regulator and its parts buy a named, useful boundary. No
reliability number is claimed for it.

| Fault | Result with three domains | Still shared |
| --- | --- | --- |
| Short on comms MCU, GNSS or radio | U1501 limits and latches. Flight can cycle the comms branch on battery | The common buck must ride through the limited load |
| Comms regulator output short | Comms lost; services keep their own regulator | U1501 and common-buck transients |
| Short on one service device | Its local limiter acts; other service branches stay up if selectivity holds | Service regulator and input limiter |
| Service regulator or input trip | Flight and comms survive; flight can restart services with PE8 | NOR tail and CAN / monitoring outage, stated openly |
| Flight regulator or common source fails | Flight is down | Three domains are not three independent computers |
| A regulator fails input-to-output | Its output group may see over-voltage | Current limiting does not stop over-voltage |

Rejected: one regulator, because every output failure is shared. Two
regulators, because a comms regulator fault then takes logging and CAN. A buck
per domain, because it adds magnetics and source interactions without giving
independent recovery. Keep the common buck for this revision.

## Capture changes

| Reference or net | Instruction |
| --- | --- |
| U1701 / U1801 / U1901 | Keep TPS7A9101DSKR ×3 with their input and output caps, NR/SS and PG networks |
| U1501 | Keep **before U1801**. IN = `4V_PRE`, OUT = `COMMS_LDO_IN` through the existing link, EN = `COMMS_BRANCH_EN` |
| R1504 | 36.5 kΩ → **66.5 kΩ 1%**; calculated limit 351–449 mA |
| U1601 | Keep **before U1901**. IN = `4V_PRE`, OUT = `OPTIONAL_LDO_IN` through the existing link |
| U1601 EN (pin 3) / R1602 | Move EN and the top of its 100 kΩ pull-down from `FLIGHT_3V3` to the new **`SERVICE_POWER_EN`** |
| Flight PE8, pad 39 | GPIO `SERVICE_POWER_EN`, low at reset and power-off. Uses a pin freed by D-6.2 (was the channel 1 low-side select, which moves to PA9 under D-2Nov.1); servo 3 keeps PD10 (D-7.1) |
| R1701 / R1801 / R1901 | **31.9 kΩ 0.1%** each; lower legs stay 10 kΩ 0.1% → 3.352 V nominal on all three |
| R1604 | 56.2 kΩ → **49.9 kΩ 1%**; calculated limit 470–588 mA |
| `3V3_OPTIONAL` | Keep the net name for capture; call it "services" on labels. It feeds NOR, CAN, AUX and the sounder, not comms |
| Local limits and boundaries | Keep NOR, CAN and AUX limits and their partial-power signal isolation. Sensors run from `FLIGHT_3V3` through 47 Ω links (D-6.6, D-2Nov.3); the magnetometer through 22 Ω (D-2Nov.11) |
| Source logic | Core enabled by `4V_PRE` presence (D-6.5); keep the battery-priority comms enable |

PE8 is the only reassigned flight pin for this. No output or arm-sense pin is reused. The
proposed flight CSV records this; the frozen input CSVs stay as they are until
capture is approved.

## Service restart

- Services start off. Flight turns them on after basic clock, GPIO and watchdog
  setup.
- On a service fault: switch off local service loads, hold `SERVICE_POWER_EN`
  low for 100 ms to start with, then allow **one** restart with loads sequenced.
- 100 ms is a starting bench value, not proof that the rail resets. Measure every
  affected rail below its peripherals' reset threshold for long enough, then
  measure the restart. Set the off-time from those results; it may need to be
  longer. Until that is shown, don't claim power-cycle recovery works.
- A second fault latches the group off for that power session. Never reset
  flight to fix it.
- In a mission, restart only if the mission's peer-loss contract accepts the
  outage. Otherwise stay degraded and say so.
- This is a bounded recovery step. It is not an endless auto-retry and it never
  commands an actuator.

## Voltage and headroom

The earlier relocated comms switch is dropped. Setting all three regulators to
3.352 V gives one divider value and supervisor margin:

- ±1% regulator, ±0.1% resistors, ±100 nA feedback current → **3.310–3.394 V**.
- TPS3808G33 worst-case release, with threshold tolerance and hysteresis:
  **3.194 V**.
- Static margin **116 mV** before PCB drops, ripple and transients. Allow 50 mV
  for those in healthy running; about 66 mV is left.

The MCU, five sensors, the magnetometer, NOR, GNSS, CAN and 3.3 V logic all stay
under their 3.6 V limits; the Wio allows 3.7 V. The magnetometer's 3.6 V is an
absolute maximum, so overshoot matters most there. Startup overshoot must still
not pass those limits. Use the actual set point for reference and analog ratios
and for rail measurements. Keep ≥10 µF effective at each TPS7A91 input and
output after DC-bias derating. At 300 mA a 135 mΩ upstream switch drops about
41 mV **at the regulator input**; check regulation against that input, and don't
subtract it again from the output.

Keep C1403 **PCW0J102MCO1GS**, 1000 µF / 6.3 V, on the held flight input after
the LM73100. The old 0.98 ms figure is only an example (800 µF effective,
0.25 V usable drop, 204 mA). Recalculate the usable drop with the new set point
and measured regulator headroom. A final flash flush is not guaranteed.

## Loads and limiter coordination

These are **allocations** that firmware, clocks and modes must fit. They are not
measured or summed worst-case currents.

| Domain | Ceiling | Split |
| --- | --- | --- |
| Flight | 200 mA | MCU and support 150; sensors 35; magnetometer ≈3 at 100 Hz; margin 12 |
| Comms | 300 mA | MCU and support 100; RF 150; GNSS tracking 35; margin 15 |
| Services | 200 mA | NOR writing 65; CAN 80; AUX 25; sounder, support and margin 30 |

- GNSS startup gets a separate 100 mA allowance: start it with RF off.
- Fast NOR reads can exceed the 65 mA writing allowance. USB download switches
  off CAN and the sounder and uses the whole domain ceiling.
- Average radio current says nothing about transmit peaks.
- 700 mA total is **2.8 W at 4 V** before upstream losses. Ideal regulator
  dissipation is about 0.454 W before switch drops.

Selectivity check: a NOR fault at its 306 mA maximum plus **135 mA** of healthy
services is about 441 mA, under the service input limiter's 470 mA minimum. For
a CAN or AUX fault, swap that branch's healthy allocation for the fault current;
don't add the whole group twice. A group trip is still recoverable and doesn't
take comms. Even with comms and service limiters both at their limits plus
200 mA for flight, the common buck sees about **1.237 A**. Its 3 A rating is not
a transient test.

## USB and endurance

USB (D-6.5, 6 October): U4402 is removed. U4401 limits at 387–491 mA from
attach. USB alone starts the flight core and comms at reduced clock. During a
configured download: ≤300 mA from VBUS, only reduced-clock flight and comms plus
NOR; no CAN, RF, GNSS or sounder. Run optional health measurements one after
another. Battery presence allows normal running; USB alone never means full
load. USB suspend is not supported.

**Kármán overlay (D-6.8): the reference AV pack is 2S, 8 Ah nominal.** The
workhorse pack is sized from measured loads instead.

- The overlay needs at least **30 Wh usable** at the installed temperature, load
  and UVLO, not nameplate.
- Budget: 8 h at 2.8 W through 85% conversion plus 0.10 W upstream overhead,
  then 4 h at 0.4 W through 75% plus the same overhead = **29.69 Wh**.
- 7.4 V × 8 Ah × a provisional 65% usable allowance = 38.48 Wh. That 65% is an
  assumption to test, not a cold or ageing guarantee.
- Actuator and output energy is extra. It can't come out of this logic and
  recovery budget without redoing the sum.

The pack interface is electrical, not a brand or SKU: 2S lithium, 8.4 V maximum
charge, connector and polarity, and ≥30 Wh usable. The workhorse pack uses
metal-can cylindrical Li-ion cells, 21700 by default, and never LiPo (EuRoC
LV-0300, D-2Nov.6). A smaller pack can fly a shorter declared mission; it
doesn't meet 8 h + 4 h by default. Nothing here approves buying or building a
pack.

Sources: [netlist](../../../hardware/croi2/output/full-netlist.xml),
[TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf),
[TPS7A91](https://www.ti.com/lit/ds/symlink/tps7a91.pdf),
[TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf),
[platform envelope](../../archive/karman-line-mission-hardening-report.md#accepted-provisional-platform-envelope),
[calculations](../../calculations/component-proposal-checks.py).
