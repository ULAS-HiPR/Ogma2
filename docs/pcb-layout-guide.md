# Ogma 2 layout guide for Seán

7 September 2026. Working instructions for the current Croí2 and Foinse2 CAD.
This supersedes the 6 September layout chapter where this guide is more specific.
These are provisional engineering layouts, not files to order unchanged.

**Current Croí placement:** the reviewed clusters are installed in the
[working Croí PCB](../hardware/croi2/Croi2.kicad_pcb). All 629 assigned footprints
have front/back placement and grouped ground, thermal and quiet reservations.
The flexible placement separates 25 coarse subsystems into small circuit cells;
96 remain after the Wio radio revision removed one obsolete isolation cell.
It reduces 123.75 × 260.75 to **80 × 230 mm**, 42.98% less area. Critical local
geometry, rotations and sides are preserved, but independent circuits within
the old groups have moved. The 80 mm target is reached only as a provisional
placement outline; routing, plugged-connector access and vehicle fit are open.
No new rule areas or copper polygons were added. The existing 28 rule areas
moved with their owning circuits. The earlier insulated test points remain. Use the
[placement notes](archive/croi2-functional-placement-2026-09-07.md) for this pass. The
separate [cluster catalogue](../../cluster-layout-2026-09-07/START-HERE.md)
remains available for circuit-by-circuit source notes and close-ups.
The fourteen parts labelled REV-B are intended for the first engineering PCBA,
not deferred to a second manufacturing revision. Foinse is unchanged by this study.

## Since 7 September (read this first)

Where this guide and [decisions.md](../decisions.md) disagree, the decisions win.

- **21 November:** the layout is now scripted and placed fresh from the schematic
  (D-21Nov.21); the placement, cells and rule areas below describe the 8 September
  draft only. Decided since: eight isolated M3 holes (D-21Nov.23), J102's end aft
  and connectors by harness end (D-21Nov.24), both SMAs forward (D-21Nov.25), four
  layers on JLC's 0.1 mm-prepreg stackup (D-21Nov.26), every part on top (D-21Nov.27).
  The circuit notes (C04–C14) still apply.

- **Sensors (C09):** the per-sensor limiters and translators are gone (D-6.6).
  Each sensor's supply comes through a 47 Ω link (D-2Nov.3). New magnetometer:
  [C09a](#c09a-magnetometer).
- **Outputs (C14):** the one-shots and permit gates are gone (D-6.2). Each
  channel keeps its high side and its low side (D-2Nov.1). New fuses F6101 /
  F6102 / F6801 and arm connectors J6101 / J6102 (D-6.1, D-2Nov.2). Beside
  D-6.7's servo bulk at J6602 goes a DNP footprint for a 1000–2200 µF can, with
  room to stake it (D-2Nov.17).
- **GNSS (C03):** U4504 is now a MAX-M10S with an external passive antenna on
  J4501 (SMA). The SAM-M10Q patch geometry in C03 is history; see the note there.
- **Power (C04):** the energy tap sits at `BAT_EFUSE_IN`, after Q101 (D-2Nov.5),
  with its 100 nF and 10 µF at Q101's drain (D-2Nov.15). The hold RC (330 Ω,
  470 µF) sits between PE14 (`FC_POWER_HOLD`) and the SHDN diodes; its pull-down is 1 MΩ
  (D-2Nov.4, D-2Nov.18).
- **Churro:** a ground umbilical connector J801 and four ideal-diode stages
  ahead of the eFuses (D-2Nov.7).

## Open these

- [Croí project](../hardware/croi2/Croi2.kicad_pro).
- [Foinse project](../hardware/foinse2/Foinse2.kicad_pro).
- [Manufacturer page index](../../layout-reference-2026-09-07/DATASHEET-PAGES.md).
- [Power sensing, indicators and RTC decision](archive/sensing-indication-time-review-2026-09-07.md).
- [Firmware interface](firmware-interface.md) (replaces the 7 September handoff).

The reference folder contains shortened original PDFs named for components.
Follow the actual package/version: TPS26630 **QFN**, H563 **non-SMPS LQFP100**,
Wio-LR2021 **868/915 MHz**, and the exact Samtec mates. A different package's nice example
is not our land pattern. Each PDF keeps its original printed page number; the
index also records the original PDF page. Missing downloads are listed openly.

In particular, TI's TXU0304 example is DTR, while ours is PWR; its TXU0202
example is DTM, while ours is DCU. TCAN3413's example draws an eight-lead
package and optional split termination/choke, while ours is DRB with the
actual fixed termination drawn in CAD. Use those pages for bypass placement,
signal flow and return paths. Do not copy the example package geometry or
silently add its optional circuitry.

## What the PCB files actually contain

Croí: 80 × 230 mm provisional working outline, four layers, 1.6 mm, 629 placed
footprints; 96 placement cells, 25 logical groups containing 43 sheet groups;
488 front, 141 back.
No parts remain in the old staging banks. Foinse:
60 × 80 mm, four layers, 1.6 mm, 100 footprints, all within its outline. Both are
unrouted. Croí's outer groups identify subsystems and carry rule areas;
Foinse retains its earlier coarse schematic-sheet grouping.

The later Croí functional-placement pass moved the retained footprints while
preserving their electrical identities and reviewed local geometry. Foinse's duplicate
avionics shunt and eight monitor components were removed. Croí now carries the
bulk-current monitor and selected piezo. Native pad/identity checks pass; DRC
is not clean. The exact Nano-Fit footprint is missing on both boards. C1403 is
still a volume allocation. Do not infer final fit or qualification from a 3D view.

Enter the logical groups and move small circuits independently. The old 25
subsystem boundaries are not placement constraints. The 96 cells are recorded
in the placement report, not native groups. Some support belongs to an IC on
a different sheet. Preserve those relationships. Move each thermal/quiet rule
area and drawing with its actual owner, not the subsystem centroid. Do not regenerate
the starter or study over your work. Save a layout revision before moving blocks.

Board coordinates below are local to the upper-left outline corner. Existing
KiCad absolute coordinates use an offset of (100, 50) mm. A Dwgs.User box is a
placement/reference reservation, not a copper keepout or an Edge.Cuts cutout.

## Before either board

1. Obtain the intended fabricator's actual four-layer stack-up, finished copper,
   minimum clearance/drill/annular ring, solder-mask web and assembler limits.
   Set rules before routing. Do not reduce a global clearance merely to hide
   an internal fine-pitch footprint violation.
2. Start L1 components/signals/local power, L2 continuous GND, L3 power/slow
   signals, L4 secondary components/slow signals. Fast L4 routes need a real
   continuous reference below them; do not cross L3 power splits blindly.
3. Agree the carrier/connector envelope at actual scale, with plugged connectors,
   extraction travel, cable bends, captive hardware and tools. A 60 mm board is
   not proof of fit inside a 3-inch bay. No drilled mounting pattern is frozen.
4. Use one continuous system GND. Separate noisy current paths by placement and
   short returns, not arbitrary analogue/digital moats. Local regulator AGND
   geometry is a specific exception within that continuous-ground architecture.

## Croí: placement order

### C01. Interboard mate and mechanical datums

Place **J102 MPT-08-01-01-L-RA-SD first** when fixing the final board envelope.
Its provisional working-outline origin is (40, 230), rotation
0°. Its footprint datum is the board edge. Reserve its complete body, six tails
per electrical contact, retaining screws, mating counterpart and tool access.
Do not compress it to the visible plastic body. Foinse J301 opposes it at
(30, 0), 180°; nominal board-edge gap 7.39 mm. Align connector datums in the
assembly, not the different-width boards' left edges. The pair checker uses
relative contact coordinates. Moving either outline requires rechecking datums.

Put independent mechanical supports behind the mating region. Neither the
connector nor its solder tails supports the other PCB. Ground contacts 2 and 4
each need a path capable of the full 6 A alternate-return case. Do not use two
thin traces and assume perfect current sharing. Do not narrow six power tails
into one via.

### C02. External connectors, supports and service access

Arrange J101 Nano-Fit at the power-entry edge; keep its explicit blank-footprint
reservation until the **1053111102** drawing is resolved. Do not borrow a 105309
land pattern. Standalone battery and Foinse feeds are common copper: mechanically
exclude simultaneous packs. Place the physical source exclusion in the assembly
drawing, not just a warning in firmware.

Reserve J6601 energetic and J6602 servo connector mouths outward, next to their
drivers. Keep J4401 USB accessible without opening the installed bay. Place
J501 and bus 2's CAN connector (D-5Nov.3) at their harness exits, not through the quiet sensor area. Add independent
harness strain relief to the carrier near each connector; the connector latch
does not secure the wire mass. Leave room for fingers in field conditions.

Place both Tag-Connect patterns so the actual cable body and alignment pins can
reach them without hitting underside parts. The footprint holes occupy both
faces. Put mounting supports near high insertion-force connectors, while keeping
MEMS devices away from the immediate mounting-hole strain field.

### C03. Correct the GNSS reservation before packing around it

**Update, 2 November:** U4504 is a MAX-M10S-00B receiver with an external
passive antenna on J4501, not the SAM-M10Q patch module this section describes.
It needs no sky view or 50 × 50 mm ground patch: keep its RF input short to
J4501, 50 Ω over solid ground, and give the receiver its own quiet ground and
bypass. The old 56 × 56 mm reservation around it can shrink, which frees the top
end for the magnetometer ([C09a](#c09a-magnetometer)). The text below is the
7 September record.

U4504 **SAM-M10Q-00B** anchors the opposite, sky-facing end. Read the supplied
integration-manual pages **60–63** before moving it. The manufacturer reference
puts the module centrally on a 50 × 50 mm ground area, recommends nothing within
10 mm of its edges, prohibits signal traces beneath it, and calls for at least
20 mm from its edge when changing a signal from the top layer to another layer.
Smaller than 40 × 40 mm ground can significantly reduce performance. These are
more specific than “leave some quiet space near GPS.”

**Current placement:** module centre (40, 30), with the reviewed support
geometry and native restrictions retained. The earlier (30, 16) starter and
its too-close support row are historical. The 50 × 50 ground-reference drawing
is still only a reservation until connected copper is designed. Native rule
areas and the project-local rules distinguish the component, signal-route and
signal-via restrictions. This packing pass additionally retains the earlier
conservative 56 × 56 no-unrelated-component reservation. That packing margin
is broader than the native via-only rule; do not mistake it for a new
manufacturer component-clearance requirement or silently remove it.

Keep solid connected ground below the module, with the recommended GND vias
and thermal relief at solder pads. Keep **signals**, including L3/L4 shortcuts,
out from underneath. Supply/digital escape starts on top and follows the manual;
do not pour an isolated antenna-ground island. No battery, metal support or
transmitting antenna can obstruct the sky-facing patch. Check the full installed
bay, not just bare PCB.

This may consume more area than the starter allocated. Protect this requirement
before squeezing the remaining circuits. Extend a provisional board outline
with a recorded mechanical review if necessary; do not sacrifice RF space or
quiet returns to defend the initial rectangle.

### C04. Power-entry circuit and the new common-current shunt

Place Q101, Q102 and U101 together immediately behind the source region. Use
**TPS26630RGER pages 38–39**, specifically the QFN figure. Keep Q101 drain close
to U101 IN; Q102's drain/source and Q101's gate/source form a small local loop.
Put input bypass at IN_SYS/GND and current-limit/UV/OV/slew parts at their pins.
TPS26630 thermal holes and solder-pad treatment need the assembler's approval.

Place **R7101** immediately after U101 OUT, before downstream power distribution.
Place **U7101 INA228** and its filter components beside the shunt. Treat the
whole `07a-battery-monitor` group as part of this power-entry circuit, even
though it is schematic page 43.

Route the chain physically:

`J101 or J102 → Q101/U101 → VBAT_SHUNT_IN → R7101 → VBAT_PROTECTED → loads`.

Take current-sense traces from the **resistor terminations**, on the sense side
of each high-current connection. Use a matched, short Kelvin pair. Place the
two 10 Ω input resistors and differential 10 nF at U7101. No load current may
flow in either sense trace; no parallel plane can bridge the shunt. Its 2512
package has two terminals, not four dedicated Kelvin pads. Check the actual
Vishay pad drawing before treating the generic 2512 assignment as released.

VBUS comes from `BAT_EFUSE_IN` through its own 100 Ω / 10 nF filter. Do not
confuse that with either shunt pickup. Local 100 nF bypass goes directly at INA
VS/GND. It is supplied from the optional monitor rail, not raw battery.

All future Croí arm-feed takeoffs must be **after R7101**, outside the logic mux
and regulators. Those physical connections are not designed yet. Reserve the
power corridor; preserve the DNP energy links. Input TVS/damping/fuse coordination
on Croí is still an electrical closure item; leave useful entry area rather than
routing it into an unchangeable corner.

### C05. Logic source mux and bootstrap

Place U1101 TPS2121 between protected battery/USB power and the buck. Keep the
USB leg separate from raw battery and armed outputs. Its high-current geometry
and local capacitors follow its reference page; divider and soft-start nodes
stay clear of the buck loop. USB bypass must not backfeed the battery.

Group U1102 bootstrap bias and U1201–U1204 source-permission logic near the mux.
Do not move this small logic island into the sensor zone just because it has
few parts. The core **input** enables from its own 4V_PRE level (R1210 / R1204 into U1401
EN/UVLO, D-6.5), whatever the source; the held-side LDO must not lose enable
merely because the incoming source vanished.

### C06. Buck: place and route its local loop before leaving the block

Place **U1301 TPSM63603RDHR** using its page **36** example, rotated as a complete
circuit if needed. Place the high-frequency input ceramics at VIN/PGND first,
then local output ceramics, then larger output capacitance toward the loads.
The input/output pin banks need short, wide local copper. Do not put a scope
loop or an isolation jumper in the hot capacitor-to-module path.

Put R1301/R1302 at FB, take feedback from the proper output node, and keep it
away from noisy power routing. Route RT/VCC support locally. Preserve the
specified **local AGND-to-PGND join**. “One global GND net” does not mean a
random plane connection gives the same noise performance. Use geometry or a
reviewed local copper constraint to make the intended return path real.

Connect thermal/power copper to internal layers with adequate vias; do not
blindly replicate a stencil or thermal-via pattern without the chosen process.
No added external SW copper, probe antenna or speculative inductor is required
for this integrated-inductor module. Audit the imported RDH land pattern before
routing its escape. Fixed 4 V is the accepted design; no boost is added.

### C07. Held core, LDOs and branch boundaries

Put U1401 LM73100 **before C1403**, then core LDO U1701 toward the flight MCU.
C1403's current footprint is only a 10 mm-class volume placeholder. Select the
actual effective capacitance/ESR/retention part before final placement. Give it
mechanical support without trapping service access or loading nearby MEMS.

Place each TPS7A91 and its support parts as a compact same-face cell. Pages
22–23 matter: NR/SS capacitor and bottom FB resistor return quietly to the
device power pad; GND goes directly to that pad. Do not dump these returns into
the output-load ground corridor. Input/output capacitors need a wide, short
component-side return. Thermal vias then connect the pad to the ground planes.

The generic datasheet suggests remote load sensing. Our drawn feedback is
deliberately **before each removable output link**. Preserve that: do not move
feedback across an open 0 Ω link without revisiting the resulting regulator
fault/startup behaviour. Sample the regulated node near its local output bank.

Place comms limiter/LDO U1501/U1801 toward U401 and optional limiter/LDO
U1601/U1901 toward NOR/CAN/AUX. Put each small sensor limiter at its device, not
in a remote decorative row. Removable links and test points belong at accessible
boundaries; their packages must carry the intended branch current.

### C08. Flight MCU, its supply pins, HSE/LSE and reset

Place U201 so three local sensor buses and NOR can escape without crossing the
power/output corridor. Then bring over **02a-flight-support** and
**02flight-reset-debug**; do not leave their capacitors in the original sheet
packing rows.

At VDD pads 11, 28, 50, 75 and 100, place the corresponding 100 nF capacitors
first. Give each a short pin-to-cap connection and local ground return/via.
Place both VCAP capacitors at pads 48/98, with the specified common VCAP node
and no external load. Place VDDA/VREF+ capacitors at pads 22/21, after the
dedicated positive-supply link. Ground remains continuous; no thin VSSA island.

HSE Y201 and its two load capacitors sit at PH0/PH1. LSE Y202 and its load caps
sit at PC14/PC15. Short, symmetric, quiet traces; no high-current/clock/signal
route beneath the oscillator network. Do not put test-loop stubs on crystal
nodes. PC13 stays quiet per the selected erratum policy. Do not add a backup
cell or an external RTC chip.

Keep U2301 supervisor/U2302 watchdog with their bypass/timing components close
to the core. Keep reset and earned-heartbeat routes out of output-switching
loops. The drawing's capacitor values are starts, not proved oscillator margin.

### C09. MEMS and pressure devices

Place U3104 LSM6DSV16X, U3204 ICM-42688-P and U3304 ADXL375 in one stiff
measurement region. Respect their individual axes and package pad maps. Be
near useful board support, not directly in connector-insertion or mounting-hole
strain. Keep them away from the buck, hold-up can, hot drivers and sounder.

Record each sensor's actual rotation and position for Anav. A silkscreen body
axis is useful; a guessed firmware axis transform is not. Place each sensor's
47 Ω supply link, bypass and series damping nearby; the limiters and translators
are gone (D-6.6, D-2Nov.3).
Same-sheet membership does not justify a long shared sensor supply route.

Read the ADXL375 mounting/land-pattern pages. Retrieve the listed missing ST/TDK
assembly pages before closing those footprints. Similar-looking IMUs are not
pin-compatible. Do not independently soft-mount every sensor; a resonance or
flexible board can manufacture disagreement.

U3403 BMP390 and U3503 MS5607 need comparable access to the intended bay
pressure volume, clean ports and a venting arrangement. Keep them away from
local heat and airflow jets. The BMP390 solder standoff is part of mechanical
decoupling; its datasheet calls for at least 50 µm after reflow. No glue, coating,
flux residue or cleaning liquid in either port. A sealed/blocked common bay
defeats both pressure readings regardless of two manufacturers.

### C09a. Magnetometer

U3701 MMC5983MA (D-2Nov.11) needs the magnetically quietest spot on the board,
which is the top end, away from the power and output corridor.

- Put it in the top 20 mm (local y 0–20; KiCad absolute y ≈ 50–70), at least
  20 mm from the GNSS receiver U4504 (local (40, 30)).
- Keep it as far as the board allows from power entry (J101 / J102, U101 and
  its shunt), the buck U1301, the outputs J6601 and the servo connector J6602.
  At the top end all of those are about 150 mm or more away.
- No current-carrying copper under it, on any layer, and none on the opposite
  side. No ferromagnetic part close by: no steel screws or standoffs, no shield
  cans, and no battery behind it in the bay.
- R3701 (22 Ω), C3701 (10 µF on CAP) and the decoupling go at its pins. Route
  I²C3 (PA8 / PC9) and INT (PD3) as a short group over solid ground, with the
  22 Ω damping at the MCU end.
- Record its axes in board coordinates for Anav, like the IMUs. It's calibrated
  in the assembled bay, so the bay hardware near it should be final before
  calibration.

### C10. NOR and its signal-isolation boundary

Place U3604 near U201's OCTOSPI escape. Bring U3601 power limiter and U3602/U3603
TMUX parts with it. Short clock/CS/data routes, continuous reference, no fast
route across a power split. Put source damping at the actual driver if needed;
data is bidirectional, so do not apply an output-only recipe blindly. Do not
add needless length-matching serpentine. Initial 16 MHz operation still has
fast edges and needs waveform evidence.

The flash is a wide SOP16, not an interchangeable narrow package. Preserve its
exact footprint. Keep reset and isolated-side pulls on the intended switched
side so an off flash cannot backpower itself through I/O.

### C11. Comms MCU, UART boundary and USB

Place U401 between USB, radio and GNSS, outside GNSS's protected geometry.
Apply the same local VDD/VCAP/VDDA/HSE discipline as U201; its LSE pins remain
unused. U4301/U4302/U4303 belong at the inter-MCU domain crossing. Do not let
the 8 Mbaud disarmed-service UART become a long route around the PCB.

For J4401, run the USB pair from the connector through its intended ESD boundary
to U401, short and together over continuous GND. Calculate 90 Ω differential
geometry from the **actual** stack-up; no magic universal width. Duplicated
receptacle D+/D− contacts need short convergence, not long stubs. Put USB power
limiting and its mode circuitry near VBUS entry. Audit CC protection, shell
return and the known footprint/drill issues before considering this block done.

### C12. Radio and CAN

U4606 is now Wio-LR2021 868/915 MHz. Keep it away from the GNSS patch and
switching-power loops. Its host J4601 vertical SMA 132134 is required: **pad 10 now
needs a short 50 Ω host trace**. The old E22 “no host ANT stub” rule is superseded.
Pad 13 high-band RF remains NC, with no trace or high-band transmission.

Refine this block in order: module orientation and restrained cable access;
J4601 beside pad 10; C4611 immediately at pad 1/GND; remaining supply capacitors;
R4614–R4620 at the digital pad exits and R4621 by BUSY. The current placement
is a starting point; shorten the longer BUSY path before routing. Do not spread
these parts to preserve an obsolete E22 group envelope.

Route RF on the top layer over uninterrupted adjacent-layer GND. Choose the
50 Ω geometry from the actual fabricator stack-up, not the manufacturer's
example width. Keep the route short, without a branch or layer-change via;
stitch its ground return and the module grounds. Reserve a signal-free routing
corridor beneath RF while allowing continuous ground. Do not create a copper
void under the module. Existing rule areas require a final check against this
new footprint and actual route; their unchanged presence does not qualify RF.
See [Seeed's host layout guide](https://wiki.seeedstudio.com/wio_lr2021_pcb_design_guide/)
and the [integration record](archive/radio-change-2026-09-07.md). The official Wio STEP
is not yet aligned/linked; its missing 3D body does not make this space available.

CAN U503 sits by J501, and bus 2's transceiver by its connector, each with protection and fixed end termination placed so cable
transients do not cross the MCU/sensor area first. The example page shows options
such as split termination; do not add them when our schematic does not use them.
Pair CAN H/L and preserve the explicit reference/return policy. Croí exports
CAN and reference, **not propulsion power**.

J4601 now occupies more space than U.FL. Reserve its top-entry coupling/antenna
volume and through-hole legs on both faces. The exact STEP remains missing.

### C13. Optional monitoring, voltage ADCs and status

Readiness revision: keep U9101 and C9101 together, C9101 at supply pin 5/GND;
R9102 pulls the PB12 control low (PD7 until D-22Nov.25). Keep both red/green LEDs visible. Servo 3
and its PD10 are gone (D-19Nov.2). J6602 is ten-contact 430451000; its complete new
pinout is in the [revision](archive/connector-servo-readiness-revision-2026-09-07.md).
R6602/R6603 moved locally to clear the larger header; route all three PWM
series resistors at the buffer boundary. USB-C placement remains untouched.


U7001/U7002 form the AUX power/bus boundary; keep the connector-side conductors
short. U7101 belongs at the shunt from C04, not automatically beside U7002.
I²C routes may travel between them away from sensitive analog traces.

U8001 and the voltage-divider filter bottoms sit near the MCU ADC side, away
from switching edges. Keep raw battery routing out of that quiet area by
splitting the divider placement sensibly: high-side resistors at the source,
scaled/filter/switch near ADC, with the full path audited for pickup and
powered-off injection. Preserve both series top resistors; no raw battery to PC5 (PA0 until D-22Nov.25).

Place the four LEDs where they can actually be read through the service opening:
PWR, FLIGHT, FAULT, COMMS. Place BZ9001 at a supported accessible edge away
from MEMS, with its sound port unobstructed and Q9001/D9002 nearby.
It is a PUI SMT-1028-T-2-R magnetic transducer driven at 2.83 kHz (D-21Nov.20), not a
fixed-pitch active buzzer. Its land pattern is KiCad's; KiCad has no 3D model for it. No LCD or NeoPixel is included.

### C14. Output circuits: reserve now, route after their open circuit boundary closes

Bring each channel's high side, low side and continuity parts beside the output
connector. The one-shots and permit gates are gone (D-6.2); the low sides stay
(D-2Nov.1), with their gate resistors at the FET. Put driver bypass,
clamp/current-sense components and high-current copper at their driver. Use
short outgoing/return paths that do not travel under IMUs or through the
ADC-reference region. Respect thermal copper and current limits.

**Do not finish the raw armed-power routes from the current drawing.** Physical
arm contacts, disarm proof, group protection, actual loads and pulse/no-fire
settings remain open. Preserve R6310/R6410/R6510 DNP until the igniter values
close (R6804 is fitted, D-6.1; the continuity resistors are 3.9 kΩ, D-2Nov.14).
No thin trace or fitted 0 Ω shortcut may defeat that absence.
The three recovery/staging roles and servo boundary remain distinct. Current
sensing is observation, never permission to omit hardware inhibition.

### C15. Route in this order

1. Finish local power/return loops and thermal connections block by block.
2. Route crystal networks, local ADC/sense lines, reset/supervision and bypass.
3. Route short USB/UART/SPI/OCTOSPI/sensor lines over uninterrupted reference.
4. Route slower control/I²C/status, then remaining power distribution.
5. Add/fill planes, ground-stitching vias and local return vias at signal layer
   transitions. Recheck every reference crossing after filling, not only before.
6. Route completed output energy paths only after C14 closes; otherwise leave
   clearly identified unresolved nets and do not export an order set.

Use the fabricator's current/temperature-rise model for sustained routes, and
fault energy for source/return paths. An eFuse's 6 A setting is not a trace-width
calculation. Thermal spokes that are good for soldering can be bad high-current
bottlenecks; audit both power and ground necks.

### C16. Probes, silkscreen and second-side review

Croí's 20 raised points now use **Keystone 5000 red supplies (17)** and
**5001 black grounds (3)**: a 2.5 mm cylindrical insulated body and a short
top loop, nominally 4.6 mm above the PCB. Use the assigned miniature Keystone
footprint, not the old generic bare loop. Its pad/drill centre is unchanged.
The schematic and PCB carry the actual MPNs. The 31 flat pads remain unchanged.
[Package dimensions, sources and model limitation](../hardware/croi2/libraries/testpoint-selection.md).
The exact 3D model is absent: check installed height and clip access manually;
do not mistake the missing rendered body for free space. Confirm the finished
hole/insertion fit and through-hole assembly step. Foinse was not changed.

Raised loops for source/protected source, 4 V, held core, each 3.3 V rail and AUX,
with nearby ground access. Keep them out of hot loops and physically separated
from hazardous/raw nodes. Use appropriate probe technique; an earth-referenced
scope clip cannot go on a high-side shunt terminal.

Needle pads for reset, watchdog, faults, relevant ADC nodes, UART, I²C, SPI/CS,
PPS and arm/readback. Put no via hole under a needle landing. Confirm access with
the actual probe and carrier, including the underside. Add pin-1 marks, body
axes, rail names, connector functions and fitted/DNP population identification.
Do not print a readiness claim beside a mere power LED.

## Foinse: placement and routing order

1. **J301 MPS mate first**, top-centre (30, 0), 180°, opposing Croí. Establish
   the 7.39 mm gap, independent supports and each full-current ground path.
2. Place J101 2S Nano-Fit reservation, J201 6S Micro-Fit entry and J701 raw
   propulsion outlet around the edges. Keep their plugs, wire bends and strain
   relief reachable. J601 dedicated temperature-probe connector stays away
   from high-current exit loops. No generic charge socket is invented here.
3. Place the **2S protection block**, Q1001/Q1002/U1001, with TVS D1001 and
   local input capacitors at entry. Follow the same TPS26630 QFN loops as Croí.
   It now feeds VBAT_CROI directly. There is **no AV shunt or AV INA** on Foinse.
4. Place the **6S protection block**, Q2001/Q2002/U2001, D2001 and capacitors
   separately. Both boards share ground; 2S/6S positive copper must never join.
   Use actual clearances for 6S maximum voltage/transients, not a copied 3.3 V
   net class. Protection is autonomous with AUX off.
5. Place **R2011 and U5001** immediately after propulsion protection. Route
   a Kelvin pair, input filters at INA, and no parallel shunt bypass. Keep its
   high-current path short to J701 and pair its return. U5001 VBUS samples
   reverse-protected input; it is not exact delivered-load power.
6. Place U3001 TCA4307 near the mate. Its two bus segments have separate
   supply-following pulls. READY is local observation, not source enable.
   Keep AUX bypass and the source-fault aggregation readable and probeable.
7. Place U6001 ADS1115, U6101 isolation, filter capacitors and divider bottoms
   together on a quiet side. Route thermistor pairs away from 6S power/current
   sense. These are dedicated isolated two-wire probes; do not share a charger's
   NTC bias. The probe curve and external-lead ESD/clamp design remain open.
8. Route source paths/returns and thermal vias first, Kelvin pairs and analog
   second, AUX/I²C/fault third. Keep power copper away from analog acquisition
   loops without splitting the whole ground plane. Put rail/ground loops where
   clips cannot bridge 6S to AUX or the mate's small signals.
9. Check both boards together in the carrier, actual plugs fitted. Foinse has
   no actuator-voltage converter: Fajita and Salsa convert at the load
   (D-21Nov.1). Its chargers (D-21Nov.2) and the ACT branch need room, set at
   the Churro review; charge current never goes through Croí.

## Final layout checks before an order

Run native ERC and DRC with schematic parity. Inspect every exclusion rather
than assuming a zero count can replace review. Current starting findings include
fine-pitch default-clearance issues, 0.2 mm thermal holes versus default 0.3 mm,
USB drill/library issues, missing Nano-Fit and unpowered outputs. None is waived.

Check exact symbol pin → footprint pad → board net → connector contact. Check
MCU variants, QFN exposed pad, shunt terminals, diode polarity, reversed connector
views, repeated Samtec tail numbering and bottom-side orientation. Compare the
new buzzer pads against its original dimensioned page. An attractive 3D model
does not establish any of those facts.

Walk battery and USB startup, each power boundary, a shorted load return,
powered-off signal injection, input interruption/held core, and each hardware
output inhibit through the actual copper. Then check physical probe access,
port masking, tall-part retention, installation strain and thermal paths.
Anav independently checks the physical MCU map against the unchanged CSVs.

There is no separate mini-PCB gate. First-block electrical/thermal/RF/clock
tests happen on the first full engineering PCBA, with current-limited supplies
and inert loads. Pre-order footprint/rating/inhibit/mechanical review remains
necessary. Routing these files does not authorise live energetic tests or flight.
