# Historical pilot snapshot — 7 September 2026

Superseded by [current schematic status](schematic-status.md). The native CAD
now contains the later engineering draft. Counts, commands and circuit descriptions
below describe the earlier seven-sheet pilot, not the files now at those paths.
Its complete pre-update project copy is retained outside Git in
`../../../schematic-work-2026-09-07/pre-full.99GULg/`.

---

# Ogma2 schematic pilot

7 September 2026. Engineering draft. No fabrication, powered-board or flight claim.

## What exists

Open `Ogma2.kicad_pro`; the root is `Ogma2.kicad_sch`. If KiCad was already
open before the text edits, close/reopen the schematic without saving the stale
in-memory drawing over these files. No further GUI automation was used.

Seven A3 sheets: implementation map; power; flight MCU; sensors/storage;
communications/GNSS/radio/USB; CAN; outputs. **Only CAN has a detailed circuit.**
The flight sheet places STM32H563VIT6 and connects five CAN-related signals.
Other sheets have explicit unfinished-work notes, not invented circuits.
Foinse2 remains a separate future PCB/project. The existing PCB is untouched.

The pilot contains 26 PCB symbols, each with a footprint: 25 CAN-block parts
and one flight MCU. Six capacitors, ten resistors, the three accepted CAN ICs,
connector, proposed TVS and four test points. There is no completed board BOM.
Passives have values, package and relevant class/rating notes; procurement MPNs
and final derating/drawing audits remain open.

## CAN implementation

`3V3_OPTIONAL -> TPS2553DBVR-1 -> R501 removable link -> CAN_3V3`.
The accepted latch-off part is used. A 210 kΩ, 1% ILIM resistor implements the
chosen limit class: TI's equations with resistor tolerance estimate
109.2–152.3 mA, nominal 129.0 mA. The earlier 110–150 mA class is not an exact
assembled-board bound. The 100 kΩ enable pull-down defaults the branch off.
R501 must be selected for at least 0.25 A continuous at temperature; it is
not a fuse. No removable link is placed in a reference/fault-current return.
[TI TPS2553 datasheet, sections 7.5 and 9.5](https://www.ti.com/lit/ds/symlink/tps2553.pdf)

TXU0304 separates held-flight and switched-CAN signal supplies. OE follows
CAN_POWER_EN. TX/STB have pull-ups on both sides; RX has a flight-side pull-up.
Unused A3 is grounded; B3Y and the two NC package pins are genuinely unconnected.
Zero-supply isolation does not establish containment at every partial rail
voltage; that remains a first-PCBA test. [TI TXU0304 datasheet, section 9](https://www.ti.com/lit/ds/symlink/txu0304.pdf)

TCAN3413 VCC **and VIO** use CAN_3V3, with separate 100 nF decouplers. Both ground
pads connect to board GND. Fixed 120 Ω, 1%, 0.25 W termination is across H/L.
JST GH: **1 H, 2 L, 3 reference**; no power pin. This is non-isolated CAN.
The reference is bonded directly to board GND; installation must prevent an
open propulsion return diverting load current through it.
[TI TCAN3413 datasheet](https://www.ti.com/lit/ds/symlink/tcan3413.pdf)

Support-part proposal: **ESD2CAN24DBZRQ1**, SOT-23; pins 1/2 to H/L and 3 to GND.
Pin mapping follows TI SLVSFW5D table 4-1. Place it at connector entry with a
short return path. Its component ratings do not qualify this board or harness;
transient waveform, clamping/inductance and final DBZ land-pattern checks remain.
[TI ESD2CAN24-Q1 datasheet](https://www.ti.com/lit/ds/symlink/esd2can24-q1.pdf)

Raised loops: CAN_3V3 and GND. Needle pads: isolated TX/RX. A 10 kΩ rail bleed
draws 0.33 mA nominal; power-down timing must be measured with actual capacitance
and devices. No bus stubs for speculative test connectors were added.

## Frozen MCU connections

| Pad / port | Net |
| --- | --- |
| 36 / PB1 | CAN_POWER_EN |
| 81 / PD0 | CAN_RX, FDCAN1 AF9 |
| 82 / PD1 | CAN_TX, FDCAN1 AF9 |
| 91 / PB5 | CAN_STB |
| 86 / PD5 | BRANCH_FAULT_N, EXTI5 |

The other 95 physical pads are unfinished. The stock symbol stacks five VSS
pads at one floating graphical node; that node is **not** wired to board GND.
Do not interpret it as completed MCU grounding. No NC markers were used to hide
unfinished pins. Aggregate fault pull-up/other contributors belong to the
upcoming flight-power/supervision work. Anav's allocation and firmware ownership
are unchanged. ADC quantity names in the CSV are not permission to connect raw
battery rails directly to ADC pins.

## Observed verification

- KiCad 9.0.6 parses and exports all seven sheets.
- [79 checks pass](pilot-checks.json) against KiCad's **exported netlist**:
  intended pin-to-net mapping, separate H/L and supply domains, connector/TVS
  numbering, required values, footprints, five frozen MCU connections and the
  three intentional translator NC pins.
- Negative test: swapping connector H/L in an exported-netlist copy is rejected.
- Four functional symbol views preserve the canonical number/name/electrical-type
  maps exactly. The fifth support symbol is the proposed TVS. Their footprint
  assignments reference the existing major-part library or installed stock.
- Full-board ERC: **108 errors, zero warnings**. Flight scaffold: 90 unconnected
  pins, 10 undriven power checks, 4 undriven-input checks. CAN: four undriven-power
  checks: source 3.3 V, flight 3.3 V, ground and downstream of the removable link.
  These are unresolved dependencies, not excluded errors. CAN has no dangling-pin,
  symbol-library or footprint-link warnings. No PWR_FLAG was added to fake a source.
- All seven exported PDF pages were visually inspected. The reading PDF is a
  generated local output under `output/pdf/`, ignored by Git.

Initial wire generation missed native T-junction splitting. The first correction
also exposed a termination lead ending on the other bus line. Native-net checks
caught both; wire splitting and routing were corrected, then the full exact H/L
node sets were tested. This is why parsing or a plausible picture alone is not
the verification method. A separate checker correction recognises the stock
MCU's stacked, floating VSS pins rather than falsely calling them external wires.

No hardware, analogue transient simulation, timing test, ESD test or environmental
qualification was performed. Fontconfig warnings arose from the local installed
font configuration; exports completed. System Python's XML module failed to
load, so XML checks used the bundled Python runtime. These failures were not
reported as successful tests.

## Files and editing

Native CAD is the editable artifact. `Ogma2_Circuit.kicad_sym` provides readable
functional pin arrangements without changing accepted electrical pin maps.
Stock-derived assets retain [KiCad attribution](../libraries/KICAD-LICENSE.md).
The major-part library and its existing verification caveats are unchanged.
The relative `libraries` symlink resolves the library's existing model paths
from this nested project. Preserve symlinks when copying the project tree.

The [builder](../tools/build_schematic_pilot.py) generates into a scratch directory
and refuses the live project directory. Do not regenerate over manual edits.
Review and apply the delta; re-export, test and render. Scratch source exports,
the original two GUI-made schematic files and full native ERC reports remain in
`../../../schematic-work-2026-09-07/` outside this repository.

From this directory, with an installed KiCad CLI and working Python XML module:

```sh
kicad-cli sch export netlist --format kicadxml --output /tmp/ogma2-pilot.xml Ogma2.kicad_sch
python3 ../tools/check_schematic_pilot.py /tmp/ogma2-pilot.xml .
kicad-cli sch erc --format json --output /tmp/ogma2-pilot-erc.json Ogma2.kicad_sch
```

The checker currently describes this pilot, not future whole-board acceptance.
Expand its independently reviewed expectations when implementing more circuitry.
Next: source selection/regulation/supervision and the flight MCU's power,
decoupling, clocks, reset and debug; then the sensor, storage and comms blocks.
Installed-grounding, source-ramp and exact support-part audits remain explicit
review/test obligations. Do not send the present files to PCBA.
