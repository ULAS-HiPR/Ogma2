# 2. Croí power

## Circuit

```text
exclusive Nano-Fit J101 / Samtec J102 battery input
  → reverse protection + TPS26630 U101
  → 5 mΩ R7101 shunt → protected battery loads

protected battery ─┐
USB service limit ─┴→ TPS2121 U1101 → TPSM63603 U1301, 4.0 V
                                         ├→ held flight input → TPS7A91
                                         ├→ limited comms input → TPS7A91
                                         └→ limited optional input → TPS7A91
```

U1102 supplies bootstrap bias. LM73100 U1401 isolates the held flight input.
C1403 is an unresolved capacitor volume allowance, not a qualified 1000 µF part.
Battery output energy takes off after the common shunt and through separately
defined physical arm paths; it does not come from the 3.3 V logic rails.

U7101 INA228 measures common battery current. PA0 reads protected battery voltage.
Its INA voltage measurement is before the eFuse, so the two voltage readings
must remain separately named. USB current is outside the battery measurement.

## Why this topology

The preregulator handles the battery voltage efficiently; the LDOs provide the
accepted quiet-rail approach and separate fault domains. That cascade follows
the Rev 1 review and Seán's explicit choice. A direct-buck design is a real
alternative, not the current baseline. No boost is added merely to run a
depleted pack further down.

Limits and powered-off signal boundaries aim to stop a shorted optional device
from removing flight power. They add parts and dropout and require partial-rail
testing. A low-noise regulator does not excuse poor return paths or layout.
Shared source, preregulator and a shorted core LDO remain common failure points.

## New external switch

The installed 8 September draft adds Croí J103, a two-contact vertical JST
GH `BM02B-GHS-TBT(LF)(SN)` with `GHR-02V-S` housing. Pin 1 supplies bounded
3.0 V bias; pin 2 returns to `BAT_SHDN_N`. Close the maintained external
contact to enable; open/unplug to disable. The switch carries control current,
not the battery load. No on-board mechanical switch is added.

Bias path: input battery → BAS116 → two 4.7k/2010 resistors → LM4040 3.0 V
shunt, clamped before the connector. R1006 becomes a local 22.1k pull-down;
C1006 adds 100nF at SHDN. Protection thresholds and MCU pins stay unchanged.
Standalone uses an external switch. With Foinse, a deliberate retained Croí
enable plug closes J103; Foinse operates its separate source loops.

OFF is electronic disable, not physical isolation. Bias and pack entry remain
live; USB can still power service logic. Bias alone draws about 0.5 mA from
nominal 2S and is upstream of Croí's current shunt. Unplug packs for storage.
Neither an enable contact nor a power LED proves pyro disarm.

Native checks pass; installation is tracked in the current-system
and change record. Cold/minimum-pack startup, switch retention/bounce, cable
ESD, clamp faults and assembled thermal/surge margins still require tests.
100nF is an edge filter, not a debounce guarantee; bouncing SHDN can restart
the board and reset a latched protection fault.

## Remaining electrical work

Existing nominal battery thresholds are approximately 6.63 V start / 6.20 V
stop, 8.99 V overvoltage and 6 A limiting; tolerances and load margins matter.
The general 6 V planning envelope does not prove operation down to 6 V.

Verify minimum-USB-VBUS regulation, startup/inrush, source exclusion/backfeed,
hold-up effective capacitance, LDO shutdown/reverse voltage, fault selectivity
with pack fuses, and external-switch open/short/bounce behaviour. The battery
connector footprint and real C1403 remain pre-order closure items.
Test on the first complete PCBA with current-limited supplies.

Evidence: [power contract](../../interfaces/power-contract.md),
[Rev 1 power rationale](../rev1-external-review-lessons.md),
[sensing revision](../sensing-indication-time-review-2026-09-07.md).
