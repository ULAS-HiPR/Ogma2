# Readable schematics and external installation interfaces

8 September 2026. Engineering draft; not a fabrication or flight release.

## What changed

The schematics now show local connections as wires, with a short explanation
of what each circuit does and what it connects to. Root pages provide the
reading order. Technical cautions remain beside the relevant circuitry.
Croí has 44 pages; Foinse has 12. MCU pin allocations and firmware ownership
are unchanged. Open each schematic and PCB through the same KiCad project.

The two authorised electrical changes are external GNSS reception and external
maintained power-enable contacts. Physical energetic arming remains unfinished
and separate. No automatic PCB packing or routing was performed.

## GNSS outside the carbon airframe

Croí U4504 is now MAX-M10S-00B rather than the integrated-antenna SAM-M10Q.
J4501 is a vertical Amphenol 132134 SMA. D4501 is TPD1E0B04DPYR RF ESD
protection. The starting antenna arrangement is passive, 50 Ω, without bias
or ANT_CHECK. The actual antenna, coax loss, retention and installed reception
remain to be selected and tested. An active antenna would require reopening
the bias/protection design.

| MAX pin | Connection |
| --- | --- |
| 1, 10, 12 | Ground |
| 2 TXD | Comms PA10 / USART1 RX through existing boundary |
| 3 RXD | Comms PA9 / USART1 TX through existing boundary |
| 4 TIMEPULSE | Comms PA0 / TIM2 CH1 through existing boundary |
| 7 V_IO, 8 VCC | Switched GNSS_3V3 |
| 9 RESET_N | Comms PC5 open-drain through existing boundary |
| 11 RF_IN | External SMA and low-capacitance ESD protection |
| 5, 6, 13–18 | Not connected |

PB0 remains GNSS enable. TIMEPULSE4 is internally coupled through 1 kΩ to
SAFEBOOT18. Leave SAFEBOOT unloaded and do not apply a startup-low load or MCU
pull-down to PPS. Separate package pins do not remove this restriction.

The MAX receiver still has an 80 km navigation limit. External reception is
not a solution to full-envelope Kármán altitude estimation.

The MAX copper land matches the manufacturer's drawing; rectangular stock
paste openings still need assembler review against its T-shaped recommendation.
The TI DPY land uses 0.3 × 0.5 mm pads at 0.7 mm pitch. Exact new package models
remain incomplete. Eight obsolete SAM rule areas and their two custom rules
were removed; unrelated placement and rule areas were retained. Review the new
RF installation before routing; old drawing reservations are not MAX constraints.

Sources: [u-blox datasheet](https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf),
[integration manual](https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf),
[TI RF protector](https://www.ti.com/lit/ds/symlink/tpd1e0b04.pdf).

## External power-enable contacts

Croí J103 controls its battery entry. Foinse J103 controls avionics; J104
controls propulsion. All three use vertical JST GH BM02B-GHS-TBT(LF)(SN),
GHR-02V-S housing and contacts selected for the actual wire gauge.

Pin 1 is bounded 3.0 V bias; pin 2 returns to that branch's SHDN. Close a
maintained external contact to enable. Open or unplug it to switch the branch
electronically off. The cable carries control current, not battery load current.

Each branch derives its own bias directly from its pack: BAS116,215 → two
CRCW20104K70FKEF 4.7 kΩ resistors → LM4040CEM3-3.0/NOPB shunt reference.
The clamp is before the connector. A 22.1 kΩ pull-down and 100 nF capacitor
hold SHDN low with the contact open. Croí R1006 and Foinse R1006/R2006 now
provide those pull-downs. UV/OV, current limit, MODE and slew settings remain.

A two-pole maintained switch can control Foinse's two branches; keep the
positive bias circuits separate. Foinse-fed Croí also needs a deliberate
retained closed enable plug on its J103, or its own isolated switch pole.
No particular mechanical switch or qualified harness has been selected.

OFF is not battery disconnection. The reference bias alone draws about 0.5 mA
at nominal 2S and 2.3 mA at nominal 6S, in addition to existing upstream loads.
These currents bypass the discharge shunts. Unplug batteries for storage.
USB can still supply service logic. This is not an energetic safing system.

A shorted contact or semiconductor fault can defeat OFF. Clamp-open is not a
contained single fault. Cold/minimum-pack headroom requires measurement;
BAS116 low-current forward voltage is not guaranteed over the entire cold
range used in the calculation. The capacitor filters edges, not guaranteed
switch debounce. Contact bounce can reset a latched eFuse fault and repeatedly
restart the board. Test open/short, bounce, cable ESD, vibration retention,
startup and shutdown on the first PCBA with current-limited supplies.

Sources: [TPS2663](https://www.ti.com/lit/ds/symlink/tps2663.pdf),
[LM4040-N](https://www.ti.com/lit/ds/symlink/lm4040-n.pdf),
[BAS116](https://assets.nexperia.com/documents/data-sheet/BAS116.pdf).

## What the checks establish

| Check | Croí | Foinse |
| --- | --- | --- |
| Physical symbols / assigned footprints | 643 / 642 | 113 / 112 |
| Schematic pin checks / architecture checks | 2,179 / 381 | 306 / 117 |
| Native ERC | Original 4 errors, 6 warnings | 0 |
| Native PCB DRC findings, excluding unrouted/parity | 61, previously 62 | 24, unchanged |
| Missing footprint in schematic/PCB parity | J101 Nano-Fit | J101 Nano-Fit |
| New footprints staged outside outline | 8 | 12 |
| Remaining rule areas | 20 | 0 |

Independent checks compare symbol UUIDs, sheet paths, PCB pad nets and component
properties against the native netlist. Original footprint positions, angles,
sides and identities are preserved; U4504's package is intentionally replaced
at its existing origin. Existing tracks/vias are unchanged: both boards remain
unrouted. No native GUI cross-selection event was observed; matching identity
paths support that feature when both editors use the same project.

The Croí ERC errors are the unresolved output-energy sources. All 28 DNP parts,
including the four energy links, remain. No initiators should be connected.
Nano-Fit land patterns, C1403 selection, existing DRC findings, exact missing
models, RF/power/layout review and physical qualification remain open.

## Next

Seán and Anav read the short architecture pack and these schematics independently,
then review the actual circuits together. Seán integrates the staged parts and
finishes placement/routing. Anav continues firmware using the updated handoff.
Close component/rating/assembly issues before ordering; functional-block testing
is on the first complete PCBA, not a mandatory separate coupon programme.
