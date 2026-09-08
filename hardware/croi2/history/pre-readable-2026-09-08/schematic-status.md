# Croí2 schematic — engineering draft

## Latest accepted revision — 7 September

Three servo channels; J6602 ten-contact Micro-Fit 430451000 with a new complete
pinout; J4601 vertical standard SMA 132134. USB stays unchanged. Flight PD10
is servo3 LPTIM2_CH2 AF3; PD7 drives complementary green/red readiness through
U9101. Green is profile checks passed, not armed or launch authority.
Current totals: 635 symbols, 634 footprints, 493 front/141 back, 99 placement
cells, 68 native groups, 28 rule areas, 28 DNP. 2,163 pin / 346 architecture
checks pass; existing four ERC errors/six warnings and DRC findings remain.
567 model instances resolve after the additional power-package recovery.
34 physical component bodies still lack models; 33 further bodyless patterns are
flat probes/Tag-Connect. [Complete gaps and sources](../../docs/model-recovery-2026-09-07.md).
Earlier counts/pin statements below describe prior checkpoints.
[Full delta and verification](../../docs/connector-servo-readiness-revision-2026-09-07.md).


7 September 2026. Editable KiCad 9 project. **Not ready for PCBA or flight.**

## What exists

Open [Croi2.kicad_pro](Croi2.kicad_pro), then its schematic. If KiCad still has
the old Ogma2 project open, reopen **without saving the stale in-memory
drawing over the new files**. No GUI automation was used for this build.

The [root drawing](Croi2.kicad_sch) indexes 42 functional sheets: 43 pages total.
Both STM32H563VIT6 physical pin allocations are implemented, with no GPIO
reassignment. Foinse2 remains a separate MCU-less board; its Croí-facing
connector, auxiliary boundary and local bulk-current monitor are drawn here. Its own eleven-page project
now exists separately. Firmware belongs to Anav. Original project settings are
preserved; the tables now bind to this repo's portable library snapshot.

The [PCB](Croi2.kicad_pcb) now contains 629 placed footprints, positioned as
96 small circuit cells rather than 25 rigid subsystems. The 25 outer logical
groups and 43 original sheet groups remain. The four-layer outline is now
80 × 230 mm, down 42.98% in area from the preceding 123.75 × 260.75 board.
It is not a proposed production size or routing-capacity proof. Front/back
choices and 28 rule areas are installed; no routing or filled pours. See
[layout/use notes](README.md). The original empty PCB and
complete pre-split project remain in the recovery snapshot. No exact Nano-Fit
footprint, mounting pattern, routing or fabrication release is implied.

| PDF pages | Circuit |
| --- | --- |
| 1 | Functional-sheet index |
| 2–11 | 2S entry, reverse protection, source mux, bootstrap, preregulator, held core and three main LDO domains |
| 12–15 | Both MCUs, decoupling, analog supplies and independent oscillators |
| 16–21 | Five independently powered sensors and fixed quad-SPI NOR |
| 22–28 | Reset/watchdog/debug, MCU boundary, USB service, GNSS and radio |
| 29–31 | Foinse auxiliary return, rail ADCs and indicators |
| 32–41 | Output permissions, unresolved physical arm interface, three energetic channels, harnesses, diagnostics and servos |
| 42 | Vehicle CAN |
| 43 | Croí bulk battery shunt and INA228 0x40 |

The draft has **630 physical symbols**, including 28 DNP parts and 51 test
points: 271 resistors, 193 capacitors, 89 ICs, nine connectors, six transistors,
seven diodes/LEDs, three crystals and one populated passive piezo. Twenty-one additional
PWR_FLAG symbols are ERC annotations, not components. These are drawn quantities,
not a procurement-ready BOM. Support-part cost, board area and whether every
boundary earns its component count still need an implementation review.

The 20 raised rail/ground probes now use insulated miniature Keystone 5000
(17 red supplies) / 5001 (three black grounds), with exact MPNs and the local
Keystone footprint assigned. The 31 flat probes and all connectivity are
unchanged. Their exact 3D model is missing; see
[test-point selection](libraries/testpoint-selection.md). Total resolved PCB
model instances are now 552, with no wrong bare-loop substitute attached.

## Sensing/status revision B

Croi U7101 INA228 0x40 and R7101 5mΩ now measure the common protected battery path. Its optional domain is enabled even standalone. The PA0 battery ADC remains; both frozen MCU maps are unchanged. CPT-9019S-SMT-TR is populated with its discharge resistor/clamp; a hardware PWR LED is added. All output-energy DNP links remain. [Decision and firmware consequences](../../docs/sensing-indication-time-review-2026-09-07.md).

## Accepted architecture retained

Standalone Croí, raw 2S source, fixed 4 V switching preregulator, three quiet
3.3 V domains and bootstrap bias; no boost. Two role-separated H563 processors,
not redundancy. LSM6DSV16X, ICM-42688-P, ADXL375, BMP390, MS5607, 256 MiB NOR,
SAM-M10Q integrated antenna, Wio-LR2021 868/915 MHz radio and fixed-termination Classical CAN.

The accepted Nano-Fit, Samtec, Micro-Fit, JST GH, USB4105 and Tag-Connect
interfaces remain. Samtec contacts are 1 battery, 2 power ground, 3 protected
auxiliary 3.3 V, 4 auxiliary ground, 5 SCL, 6 SDA, 7 fault, 8 NC. Both ground
contacts bond directly to board ground; neither uses a thin removable link.
Standalone and Foinse source connectors are electrically common. Mechanical
source exclusion is mandatory; this is not a hot-mate or dual-battery OR input.

CAN remains 500 kbit/s, non-isolated, with JST GH 1 H / 2 L / 3 ground reference,
no power contact, fixed 120 Ω termination and both transceiver supplies switched.
The earlier [CAN implementation record](pilot-status-2026-09-07.md) retains
its protection/termination rationale; its whole-board counts are historical.

The GNSS antenna is soldered onto the receiver assembly. No host antenna-check,
bias or unnecessary RF connector circuit was added. SAFEBOOT_N stays unloaded.
Wio pad 10 connects to the new host J4601 U.FL connector; high-band pad 13 is
NC. The old E22 pin map is superseded. See [radio integration](libraries/radio-integration.md)
for all changes and library provenance. Wio's official STEP is retained but
not aligned or linked. Installed antenna retention and RF performance remain
mechanical/layout and hardware checks. Both MCU maps remain unchanged.

Radio revision checks: 2,148 schematic pins, 322 independent architecture checks,
2,218 numbered PCB pads, 629 footprints and all 28 DNP flags. Native ERC has
four existing errors and six warnings, including two new unused RXEN/TXEN labels.
No new native DRC finding; earlier verification totals later in this document
are historical. No routing or first-PCBA RF tests have been performed.

## Circuit-level proposals added in this draft

These implement the accepted functions. Exact support values and additions below
are **model proposals awaiting circuit review**, not another human-approved freeze.

- Croí-local TPS26630 protection with CSD18540 and 2N7002 reverse-blocking control
  supports standalone use. MODE is **open for latch-off**, not grounded.
  Nominal UV start/stop is about 6.63/6.20 V; OV about 8.99 V; current limit
  about 6 A. The 6.0 V provisional battery envelope therefore does not imply
  operation down to 6.0 V with these resistors. Normal allowable current must
  sit below the tolerance-minimum limit. Foinse/Croí/pack protection selectivity
  and harness fusing remain unproved. [TI TPS2663, table 8-1](https://www.ti.com/lit/ds/symlink/tps2663.pdf)
- TPS2121 prioritises battery, with CP2 grounded for normal switchover, followed
  by bootstrap bias. Hardware logic makes core input permission
  `BAT_VALID OR USB_CONFIG_OK`; comms permission is
  `BAT_VALID ? FLIGHT_COMMS_EN : USB_PRESENT`. This is not USB charging.
  [TI TPS2121](https://www.ti.com/lit/ds/symlink/tps2121.pdf)
- TPSM63603 starts at 800 kHz and 4 V. Internal bootstrap components stay in use;
  SW/CBOOT/RBOOT are not host probing or loading points. Its full-3-A table does
  **not** establish 4 V regulation from minimum USB VBUS. Verify the smaller
  service load and dropout, not the module's headline current rating.
  [TI TPSM63603](https://www.ti.com/lit/ds/symlink/tpsm63603.pdf)
- LM73100 feeds the held core input with a nominal 4.404 V OV threshold.
  Core LDO enable is tied to the held input, not the disappearing upstream
  permission. C1403 is a **1000 µF volume reservation**, not a selected part:
  at least 800 µF effective, ESR, leakage, retention and temperature still need
  proof. Its 10 × 10.5 mm footprint must not be treated as an approved package.
  [TI LM7310](https://www.ti.com/lit/ds/symlink/lm7310.pdf)
- Three TPS7A91 domains start at 3.296 V, with feedback before each removable
  positive link. Comms and optional branches are current-limited before their
  LDOs. Input/output capacitor selections must meet effective-capacitance
  requirements under bias and temperature. Shutdown reverse-voltage protection
  remains open; a core-LDO input/output short remains an accepted common failure.
  [TI TPS7A91](https://www.ti.com/lit/ds/symlink/tps7a91.pdf)
- Independent MCU decoupling, VCAP networks, backup supply, VDDA/VREF filtering,
  16 MHz crystals, flight-only LSE, supervisors and debug ports are drawn.
  Crystal capacitor values are calculated starts, not measured startup margins.
  External flight watchdog feeds supervisor MR; NRST and MR are separate.
- Each sensor has a removable positive power link and a latch-off branch.
  Translators or switches separate live MCU signals from off peripherals.
  Pressure pull-ups reference the appropriate side's rail; BMP is 0x76 and
  TE is 0x77. ST's auxiliary pads 2/3 are grounded for mode 1.
  [ST LSM6DSV16X pin table](https://www.st.com/resource/en/datasheet/lsm6dsv16x.pdf)
- NOR uses two TMUX1511s for quad data, clock, select and reset. GNSS, radio,
  pressure, auxiliary monitoring and ADCs also have named domain boundaries.
  **Zero-supply isolation is not proof of every partial-rail condition.**
  [TI TMUX1511](https://www.ti.com/lit/ds/symlink/tmux1511.pdf)
- USB has CC pull-downs, configured-current control, data damping and a proposed
  USBLC6-2SC6 protector. CC-specific protection, minimum-VBUS operation,
  preconfiguration/suspend consumption and inrush remain open.
  Hardware prevents GNSS/radio power in USB-only service.
  [ST USBLC6-2](https://www.st.com/resource/en/datasheet/usblc6-2.pdf)
- Raw rail ADC paths use two series upper resistors, attenuation and switched
  isolation. MCU ADC pads see `ADC_*` nodes, never battery nets.
  Absolute flight-rail measurement also requires the internal reference.
  Settling, leakage, injection and calibration remain physical tests.
- Servo proposal: one shared TPS1H100B, roughly 2 A nominal limit, followed by
  raw battery power to the two servo contacts. A small additional TPS709 supplies
  only the servo-side PWM buffer. This does not regulate servo energy. Actual
  servo voltage range, stall current, 3.3 V PWM threshold and regeneration clamp
  remain unknown. [TI TPS1H100-Q1](https://www.ti.com/lit/ds/symlink/tps1h100-q1.pdf)

Both MCU allocations remain the frozen CSVs under `libraries/inputs/`.
Physical aliases distinguish oscillator/debug nets, scaled ADCs, analog supply
links and opposite sides of the flight/comms buffers. The check report tests
those mappings explicitly. `CC_BRANCH_FAULT_N` currently has an idle pull-up
but **no selected local fault producer**; TPS22918 does not provide one.
Firmware must not infer local hardware fault identity from that pin as drawn.

## Output boundary: deliberately unfinished

There is no source connection to `RECOVERY_ARMED_VBAT`,
`STAGING_ARMED_VBAT` or `SERVO_ARMED_VBAT`. The real keyed arm assembly,
energy-break contacts, independent disarm-proof contact and group protection
are not specified. Whether servo arming shares an existing zone is also open;
this drawing does not decide that by inventing a third external arm switch.

R6310, R6410, R6510 and R6804 are DNP energy links. All pulse-setting,
energetic-current-limit and twelve continuity-injection/return resistors are
DNP/TBD. **Do not connect initiators or treat this as an operational firing
schematic.** DNP links do not establish the absence of every parasitic injection
path. The Kármán recorder population still requires independent vehicle recovery.

The staging latch is drawn with a direct request clock, disarm/reset qualification
on D, asynchronous reset clear and Q-bar inhibited-state readback. Arm voltage
absence is not used as proof that a mechanical energy break is open. All MCU
reset classes must actually clear eligibility; that is still target evidence.

Per-channel high-side pulse and low-side select are independently gated by
hardware permission. Current-sense attenuation accounts for the driver's
possible 4.9 V diagnostic output. The proposed 750 Ω burden and split divider
need loading/accuracy/injection review. Continuity is only a proposed topology;
it cannot distinguish an open load from a low-return short. No continuity or
single-fault no-fire capability is credited.

## Remaining circuit and manufacturing work

| Closure | Required next evidence |
| --- | --- |
| Physical arm interface | Seán/Anav choose actual accessible arm hardware and zone relationship; finish keyed pinout, energy break, disarm-proof and group protection |
| Energetic channels | Exact intended initiator no-fire/all-fire current/time limits and harness resistance; select pulse/current/continuity values and independently review faults |
| Servo boundary | Intended HV-servo family, supply/PWM compatibility and worst load; review limit and motor-energy clamp |
| Source transients | Harness/pack/fuse assumptions, input TVS/damping and selectivity calculation; check reset after latch-off |
| Hold-up and LDO shutdown | Exact C1403 MPN/footprint, effective capacitance/ESR/retention, reverse-voltage/discharge circuit review |
| USB service | CC protection, complete bus-power budget, inrush/suspend behavior and 4 V minimum-VBUS margin |
| Library/BOM | Exact Nano-Fit footprint, passive ratings/derating/MPNs, LED choice, sounder waveform/clamp validation and manufacturer drawing checks |
| Fault visibility | Resolve comms local fault-pin semantics without silently changing Anav's frozen allocation |
| First engineering PCBA | Startup/partial-rail/short/recovery, watchdog/reset classes, ADC/clock/bus/noise, thermal and inert-load output tests |

The model can complete calculations, sourcing, CAD changes and checks. Actual
arm/load choices need team input; those electrical loads cannot be inferred from
a generic competition-flight envelope. First-PCBA tests remain the agreed
sequence: **no separate mini-PCB or coupon gate has been reintroduced**.
Pre-order pin, rating, inhibit, mechanical and assembly review still applies.

## Observed verification

[Native-check report](full-checks.json): **2,150 pin checks and 283 architecture
checks pass**, including both frozen MCU maps, domain separation, exact CAN
conductors, source-policy truth tables, reset/staging connections and DNP links.
All physical symbols are covered. Generated expected nets test serialization and
drawing connectivity; separately coded assertions test selected architecture
properties. Neither substitutes for independent circuit review.

Two negative tests deliberately corrupt exported-netlist copies: swapped CAN
contacts and a short bypassing the flight analog-supply link. Both are rejected.

Native KiCad ERC: **4 errors, 4 warnings; none excluded.**

- Four errors: the deliberately unsupplied energetic and servo energy domains.
- Two warnings: ST mode-1 grounded auxiliary pads.
- One warning: BMP grounded SDO/address strap.
- One warning: unresolved `SERVO_ARMED_VBAT` global-label source.

There are no additional unconnected-pin, off-grid, library-link or footprint-link
ERC findings. This does not mean every footprint is assigned: J101 Nano-Fit remains deliberately blank, and C1403's assignment is only a reservation.

Four circuit-library views model internally common output pads with one
`power_out` and remaining common contacts passive. Physical pad numbers, names
and footprints are unchanged; the canonical major-part library was not edited.
Twenty-one PWR_FLAGs describe real external or component-mediated source paths
which ERC cannot propagate through a FET or 0 Ω link. None was placed on the
missing output-energy sources. These annotations do not prove electrical behavior.

All 43 current PDF pages were rendered and visually reviewed, with the new
monitor and indicator pages inspected individually. The earlier 42-page review
also moved six sensor/output pages clear of title blocks. Native exports and
full checks were repeated from the installed project, not only scratch.

Important faults caught during construction: an incorrect TPS26630 retry-mode
strap; a generated VDD bus accidentally bypassing the MCU VDDA link; missing
inherited symbol pins; misplaced label alignment; and overlapping page content.
They were corrected before this checkpoint. The VDDA regression now has an
explicit negative test. Partial-rail behavior, analogue transients, thermal
performance, ESD and no-fire limits were **not** simulated or bench-tested.

System Python's XML loader failed; checks used the bundled Python runtime.
Installed Fontconfig warnings did not stop the native exports.

## Reproduce and edit

Native CAD is the working document. The builder generates only into scratch and
refuses the live project directory. **Do not regenerate over manual edits.**
Review and apply a delta, export a fresh netlist/ERC/PDF, then run the checker.
The generated expectation file must be reviewed when intended connectivity changes.

From this directory with KiCad and a working Python XML module:

```sh
kicad-cli sch export netlist --format kicadxml --output output/full-netlist.xml Croi2.kicad_sch
kicad-cli sch erc --format json --output output/full-erc.json Croi2.kicad_sch
python3 tools/check_schematic_full.py . output/full-netlist.xml output/full-erc.json --output full-checks.json
kicad-cli sch export pdf --output output/pdf/Croi2-schematic-review.pdf Croi2.kicad_sch
```

The umbrella's `hardware/tools/build_schematic_full.py` composes the power,
sensors, comms, diagnostics and output modules. The local [checker](tools/check_schematic_full.py)
records schematic hashes and the exact exported-netlist hash. The previous
[pilot status](pilot-status-2026-09-07.md) and `pilot-checks.json` are historical.

Full native reports and the reading PDF are under `output/`, ignored by Git.
Scratch and manufacturer extracts remain outside the umbrella under the local
`schematic-work-2026-09-07/` and `library-work-2026-09-07/` siblings. The full
pre-split project is `two-board.8O7gAe/original-Ogma2/`, with its matching shared
library tree beside it. The earlier seven-sheet pilot is `pre-full.99GULg/`.

Keep the current project-local tables and vendored libraries; **no library
symlink is needed now**. Stock-derived assets retain
[KiCad attribution](libraries/KICAD-LICENSE.md). The native PCB check report
records placement identity, pad nets, models and open DRC findings. No firmware,
hardware test, purchase, Git staging/commit/push or upload occurred. Placement
can proceed while circuit and arm/load closures are reviewed; ordering cannot.
