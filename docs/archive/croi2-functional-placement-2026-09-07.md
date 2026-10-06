# Croí2 functional placement

7 September 2026. Working PCB changed; circuitry and MCU allocation unchanged.

Open [Croi2.kicad_pro](../../hardware/croi2/Croi2.kicad_pro), then its PCB.
If an editor still shows the old starter, reload the disk version. Do not save
the stale editor over the new placement.

## What is done

**Later radio-only revision:** Wio-LR2021 replaces E22, giving 629 footprints
in 96 cells. All unrelated placement remains unchanged. The measurements below
record the preceding 624-footprint compaction; they do not validate the new
radio geometry. See [radio revision](radio-change-2026-09-07.md) and current
native reports for the saved state.

At the compaction checkpoint, all 624 assigned footprints were positioned as
**97 small circuit cells**.
The 25 native outer groups remain logical subsystem selections, retaining the
43 original sheet groups. They are no longer rigid placement blocks. The
97 cells are recorded in the placement report, not new native KiCad groups.
483 parts are front, 141 back. The local geometry
comes from the reviewed [circuit catalogue](../../cluster-layout-2026-09-07/START-HERE.md):
IC supply bypassing, clocks, regulator feedback, shunt filtering and local
signal-boundary support stay with their actual circuit.

After two rigid-subsystem passes, Seán inspected the 2D and 3D views and
explicitly released that constraint: several groups contained multiple widely
spaced circuits. The latest pass takes **123.75 × 260.75 to 80 × 230 mm**:
**42.98% less area**. This is a provisional placement result, not a production
size, vehicle-fit proof or packing optimum. A tighter 80 × 220 trial was not
promoted; the extra 10 mm improves the power/interface arrangement.

Independent circuits now move within their old subsystem. Critical support
remains with its IC: the 499 recorded local distance relationships, MCU clocks,
regulator input/output capacitors, reverse-blocking MOSFETs and shunt/filter
geometry are preserved. No footprint rotated or changed face. Native checks
cover all 2,353 pad translations and 28 rule-area translations. No component,
symbol, footprint selection, model or schematic changed in this pass.

Front: converters, LDOs, MCUs and high-frequency support, all sensor bodies,
NOR, RF, CAN/USB, source shunt, output drivers, connectors, LEDs and piezo.
Back: permission/timing/observation logic and six MCU bulk capacitors.
Same-side short-path bulk placement remains preferable if compaction allows it;
the back-side choice is a review tradeoff, not an exception granted by a datasheet.

28 native rule areas reserve thermal underside, sensor/clock/RF quiet regions
and the GNSS restrictions. The project-local custom rules reject non-GND vias
within the named antenna area and non-GND pours underneath the module.
User.1/User.2 drawings show intent; drawings alone do not enforce a rule.
There are no tracks, routing vias or filled copper pours. The new polygon
request was paused when Seán challenged the spacing; no additional rule area
or copper polygon was created. The earlier conservative 56 × 56 GNSS packing
reservation also remains. It is broader than the native via-only restriction,
not a newly established manufacturer component-clearance requirement.

## How to work with it

Enter the logical groups and arrange small circuits independently. Do not use
an outer subsystem's box as a minimum area. Keep each IC's actual local support
together; the report's `cell_membership` identifies the relationships preserved
in this pass. Native rule areas are still attached to the logical outer groups:
when moving a smaller circuit manually, move its named rule area and associated
User.1/User.2 drawing too. Moving an IC alone does not move its reservation.

Original sheet membership is preserved for schematic synchronisation, but a
sheet is not always an electrically independent block. In particular, the
R67n1 driver filters belong beside their channel's power switch, and the
source-entry/INA sheets form one power path. Keep those relationships while
fine-arranging the output bank.

J6601/J6602 and their local support were turned together so the Micro-Fit
mouths face the right edge. J102 and its input test point moved to the bottom
datum. No connector pin or net changed. Samtec currently sits at local
(40, 230), 0°. Foinse's unchanged mate is at (30, 0), 180°; align their connector
datums across the nominal 7.39 mm gap. The present outlines do not define a
finished carrier or mounting pattern. Cable plugs, latch access and bending
space still need the physical assembly review.

The old optimizer already checked footprint-level rectangles, not filled
subsystem boxes. Its important limitation was the frozen internal spacing:
source entry and its distant mate spanned about 90 mm, while the 121-part output
bank occupied roughly 74 × 118 mm. Releasing those internal relationships is
what made the major width reduction possible. The new placement uses individual
courtyards on each face, with both faces reserved for drilled footprints.
Visual front/back and reservation-overlay inspection supplemented those checks.

Footprint-origin separation, before → after: flight/NOR 33.3 → 30.2 mm;
comms/radio 73.6 → 47.5; entry/mux 26.3 → 17.7; mux/buck 19.8 → 14.1;
CAN boundary/transceiver 12.0 → 7.6. These are not routed lengths. Channel 3
driver to J6601 grew from 44.2 to 50.9 mm and remains a refinement target.
Whole-board routing is not settled. Before routing:

1. Bring NOR and its switching boundary close to the flight OCTOSPI escape.
   Bring the flight MCU, inertial branches and rail-ADC boundary together.
   Confirm each sensor's actual body-to-board axis transform; identical KiCad
   angles do not establish identical sensor axes.
2. Bring communications, LoRa and their SPI boundary together. Keep the
   inter-MCU boundary between processors. Bring both pressure branches into
   the intended common vent environment. Move R9004 beside its comms receiver.
3. Compact entry → eFuse → shunt → mux/buck → held core → LDO branches into
   a short power path. Bring each LDO toward its load without invading thermal
   or quiet reservations. Do not route the current loose spacing as-is.
4. Compact output drivers toward their harness, keeping back-side timing logic
   out of driver thermal copper. Preserve every DNP energy/safety link.
5. Resolve final connector/support positions and board outline. Preserve GNSS
   clearances and continuous GND while doing so. Then follow the
   [ordered routing guide](../pcb-layout-guide.md) and exact manufacturer pages.

No local circuit is claimed to be manufacturer-reference-layout identical.
The selected package, pin-relative placement and documented recommendations
guided the blocks; final routed loops, return paths and thermal copper need
Seán's layout judgment and later measurements.

## Insulated rail test points

All 20 old bare loops are replaced with the small cylindrical insulated type:
17 red Keystone 5000 supply points and three black Keystone 5001 grounds.
The 31 flat signal-probe pads remain unchanged. Body diameter is nominally
2.5 mm and installed height 4.6 mm. The local footprint is
`TestPoint:TestPoint_Keystone_5000-5004_Miniature`, with a 1 mm plated hole,
2 mm copper pad and 3.3 mm courtyard. MPN/manufacturer fields are in the
15 affected schematic sheets and the PCB; rail-name values remain intact.

The exact STEP is missing from both the installed stock library and the direct
upstream lookup. No bare-wire or fabricated substitute is attached. The 3D
view therefore omits these 20 bodies; reserve their height and probe access
explicitly. [Selection, sources and model gap](../../hardware/croi2/libraries/testpoint-selection.md).
Foinse's test points were not changed.

## Checks and remaining gaps

Observed on the saved working board: 624 footprint identities, 2,219 numbered pad
nets, 28 DNP flags and all 43 sheet groups preserved. 547 model instances resolve;
the reduction from 567 removes the 20 obsolete bare-loop models explicitly.
All 499 recorded local pin-distance checks pass. No courtyard collision, no
new critical native DRC geometry/keepout finding, and a closed working outline.
All 2,150 schematic netlist nodes are identical. MCU maps, project settings,
custom rules and unrelated library assets are unchanged. Native DRC has no
added finding in any category; the preceding second pass removed one silk overlap.
Foinse is unchanged. The [placement report](../../hardware/croi2/placement-report.json)
records every position and local check; the [board checks](../../hardware/croi2/board-checks.json)
record native readback against the schematic netlist. In this flexible pass,
all schematic and library files remain byte-identical. The checker additionally
reports the 97 placement cells and the outer groups' logical role; no check
was relaxed. Samtec opposing contact/edge checks pass at the new datum.

DRC is not clean: 36 existing clearance findings, four hole-clearance, nine
drill, one footprint-library mismatch, twelve text-height and one silk-overlap
findings remain. Native DRC reports 499 unconnected items; this is not a work
estimate. J101 still has no exact land pattern. C1403 remains a volume/part
selection placeholder. Sensor axes, assembly, thermal design, arm/load closure,
routing and hardware qualification remain open.

The pre-placement working board, reports and changed documentation are backed
up at [pre-placement](../../placement-work-2026-09-07/pre-placement/).
The 130 × 300 mm working board and its reports are separately backed up at
[pre-compaction](../../compaction-work-2026-09-07/pre-compaction/).
The 123.75 × 269.75 mm board, its schematic/library snapshot and changed notes
are backed up at [pre-second-pass](../../compaction-2-2026-09-07/pre-pass/).
The immediately preceding 123.75 × 260.75 mm project is backed up in
[pre-flexible-placement](../../flex-placement-2026-09-07/source/).
The [current native previews](../../flex-placement-2026-09-07/preview/index.html)
show both faces and the moved reservations. The corresponding cells, targets,
source hashes and native DRC delta remain beside them.
The separate cluster catalogue remains untouched. No firmware, publication,
Git staging/commit/push, procurement or live-load testing occurred.
