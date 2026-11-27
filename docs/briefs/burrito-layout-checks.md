# Burrito: parts that need a particular arrangement

Prepared 27 November 2026 for Seán's hand-routing. A checklist, not a decision. The rules come from
[layout-brief.md](layout-brief.md) (block templates, locked by D-22Nov.1) and the datasheet layout sections named
there. Claude has read the TPS7A91 section (§7.4.1, p. 25) again for this note; the other pages are as the brief
cites them and were not re-read.

## 1. The three quiet 3V3 LDOs (TPS7A91): U1701, U1801, U1901

Rule from the datasheet layout section (observed, p. 25), as the brief states it: input and output capacitors
grounded together at the GND pin; the feedback divider top sensed at the output capacitor; CNR/SS and the lower
divider returned to the thermal pad; a via array in the pad; the GND pin tied to the pad.
[TPS7A91 datasheet](https://www.ti.com/lit/ds/symlink/tps7a91.pdf)

| Check | U1701 FLIGHT | U1801 COMMS | U1901 OPTIONAL |
| --- | --- | --- | --- |
| Input cap at IN | C1703 (47 µF C1705 beyond it) | C1803 (C1805) | C1903 (C1905) |
| Output cap at OUT | C1706 | C1806 | C1906 |
| NR/SS cap at its pin | C1701 | C1801 | C1901 |
| Feedback divider by FB | R1701, R1702, C1702 (feed-forward) | R1801, R1802 | R1901, R1902 |
| Isolation link by the output cap | R1704 | R1804 | R1904 |
| PG pull-up | not listed in the brief | R1803 | R1903 |

Measured on the committed board (b4e9841, from the file, pad centre to pad centre on the shared net, so not the same
figure as the part-to-part distances in `layout/spec.py`):

| Part | U1701 | U1801 | U1901 |
| --- | --- | --- | --- |
| Input cap | C1703 1.2 mm | C1803 1.8 mm | C1903 1.8 mm |
| Output cap | C1706 2.4 mm | C1806 3.1 mm | C1906 3.1 mm |
| NR/SS cap | C1701 1.4 mm | C1801 2.7 mm | C1901 3.6 mm |
| Feedback divider | R1701 2.4, C1702 2.5, R1702 4.3 mm | R1802 2.9, R1801 3.6 mm | R1901 2.1, R1902 3.6 mm |
| Isolation link | R1704 3.3 mm | R1804 3.6 mm | R1904 3.0 mm |

Things to look at when routing:
- The feedback divider top goes to the output capacitor, not to the LDO's OUT pin copper.
- C1701 / C1801 / C1901 (NR/SS) are the noise-critical parts: keep them short and away from the switching
  nodes (U1301 SW, the pyro corridor).
- Each LDO's GND via array sits in its own pad; the input and output cap grounds meet at the GND pin.
- U1901 feeds the buzzer BZ9001 and the continuity legs as well as its limiters; keep its copper away from the
  flight and comms LDO islands.
- Seán's list of the three flows is in the flow diagram (`ogma2-flow-v3`).

## 2. Other blocks with a datasheet layout rule

All from the brief's block-template table; open it for the full wording.

| Block | Parts | Source (brief) |
| --- | --- | --- |
| Source path | J102, Q101, U101, C1002 | TPS2663 pp. 38–40 (see flag below) |
| Shunt | R7101, R7102, R7103, C7101, U7101 | INA228 p. 39 |
| Source mux | U1101, C1101, C1102, R1102/1104/1106/1107 | TPS2121 p. 33 |
| Buck | U1301, C1303, C1304, R1301 | TPSM63603 p. 36 |
| Held core | U1401, C1403 | LM73100 p. 41 |
| Output channels | U6304, U6404, U6504 with Q6301, Q6401, Q6501 | TPS1H100-Q1 pp. 37–38 |
| CAN transceivers | the two TCAN3413 stages | TCAN3413 p. 29 |

## 3. Flags

- The brief cites the TPS2663 datasheet for U101, but the part on the board is TPS26630RGER. The two are related
  but are different documents: check the page numbers against the TPS26630 datasheet before relying on pp. 38–40.
- The pair rules (width, gap, skew) for CAN and USB are in `Croi2.kicad_dru`. Whether KiCad's router takes the `opt`
  values from custom rules when X is pressed is **unverified**: if it does not, set the net-class values.
- Test point renumbering waits until the island layout is done.
