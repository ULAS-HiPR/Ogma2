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

External power-switch connections are authorised for standalone Croí and Foinse.
The exact circuit, connector and contact requirements await the checked change
record. The physical switch is retained off-board, not soldered onto a board
that sees the vehicle vibration environment.

The review must distinguish electronics enable from a physical energy break.
A remote low-current enable could avoid a long high-current loop, but would not
provide galvanic disconnection or energetic isolation. Do not label an
unqualified enable contact “safe” or use it in place of pyro arming.

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
