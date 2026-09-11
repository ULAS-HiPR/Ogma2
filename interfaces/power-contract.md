# Ogma 2 power contract

**11 September review hold:** this contract's electrical and safety obligations
are unchanged. The [joint-review record](../docs/architecture/2026-09-10-session-review.md)
identifies proposed changes; none is implemented or accepted here. Earlier
instructions below to proceed with schematics are superseded by Seán's explicit
hold: no schematic/PCB changes until the final stack is authorized.

Updated: 8 September 2026
Status: EX-02 and the complete architecture review accepted; circuit completion
and hardware verification remain open.

## 8 September source-enable implementation

Authorised change, installed in the checked native CAD draft; see the
[change record](../docs/installation-change-record-2026-09-08.md),
[current system](../current-system.md) and project log. Existing battery
limits, autonomous protection, source exclusion, MCU pins and physical arming
requirements are unchanged.

| Board / connector | Pin 1 | Pin 2 | Operation |
| --- | --- | --- | --- |
| Standalone Croí J103 | Bounded 3.0 V source bias | BAT_SHDN_N | Close maintained external contact to enable |
| Foinse J103 | Avionics bounded 3.0 V bias | AV_SHDN_N | Close avionics pole to enable |
| Foinse J104 | Propulsion bounded 3.0 V bias | PROP_SHDN_N | Close separate propulsion pole to enable |

All use vertical `BM02B-GHS-TBT(LF)(SN)` JST GH and `GHR-02V-S`, with the
actual wire-gauge-matched crimp. These carry control current only. Foinse-fed
Croí uses a deliberate retained closed enable plug at Croí J103. One maintained
two-pole switch can control Foinse; the two positive bias conductors remain
separate. The thermistor connector is a different four-contact harness.

Each source independently supplies BAS116 → 4.7k + 4.7k → LM4040 3.0 V
shunt. The bias is clamped before the cable. SHDN has 22.1k to GND and 100nF.
Open contact/unplug defaults to electronic OFF without MCU, I²C or AUX power.
Croí R1006 and Foinse R1006/R2006 become those 22.1k pull-downs; the source
protection MODE/UVLO/OVP/limit/slew networks are otherwise unchanged.

OFF does not disconnect the pack. Entry, bias and sensing remain live; USB may
still supply Croí service logic. Reference bias alone is approximately 0.5 mA
at nominal 2S and 2.3 mA at nominal 6S, plus existing leakage/sensing/shutdown
currents. These upstream currents are outside the discharge shunts. Unplug
packs for storage. Power indication and source enable never establish disarm.

This adds no physical pyro/servo energy break, independent disarm proof or
charging exclusion. Those remain separate unresolved assemblies. A shorted
contact forces enable; clamp-open or a semiconductor fault is not contained by
this switch circuit. Cold/minimum-pack diode headroom, assembled thermal/surge
response, cable ESD, open-wire leakage and retained-contact vibration/bounce
need tests. The 100nF filter is not a debounce guarantee. SHDN cycling resets
a latched eFuse fault and may cause repeated board resets.

The 6 A Croí/avionics, roughly 3 A propulsion and 2 A shared-servo starting
limits are unchanged, provisional and not load qualification. The new switch
does not expand the declared battery range or permit depleted-pack boost.

The sections below retain prior accepted rationale and open verification work;
this dated implementation controls earlier unspecified-switch wording.

7 September third-servo revision: Croí now has three battery-derived servo
channels behind the existing common protected switch. The nominal shared 2 A
starting limit is unchanged and is not proof of three-servo/grid-fin capacity.
Selected actuator voltage, simultaneous/stall demand, regeneration and upstream
protection selectivity must close before the existing DNP energy link is released.
No Foinse power-boundary change is implied. See the
[accepted revision](../docs/connector-servo-readiness-revision-2026-09-07.md).


7 September sensing revision: Croí owns the common protected AV discharge shunt
and INA228 0x40, including standalone operation; Foinse retains propulsion INA
0x41 and ADS1115 0x48. The Samtec pinout and power authority are unchanged.
FOINSE_RETURN_EN must also enable Croí-local monitoring without Foinse present.
No duplicate Foinse AV shunt remains. All Croí battery load takeoffs, including
future physical arm feeds, must follow its shunt; USB/charging/propulsion remain
outside that measured path. Monitoring never enables autonomous protection.
See [the revision contract](../docs/sensing-indication-time-review-2026-09-07.md).

## Accepted implementation update — 7 September

The [batch acceptance](../docs/architecture-acceptance-2026-09-07.md) and its
linked integrated review supersede the earlier candidate/open wording below.
Use 2S, TPS2121 battery/USB logic-source selection, TPSM63603RDHR at 4.0 V,
three TPS7A9101DSKR 3.3 V domains and a TPS70933 bootstrap supply. No logic boost
or VIOC loop is selected. LM73100 precedes the held core-LDO input; the
core-LDO input/output short remains explicitly uncontained. Hold-up is about
1 ms at the estimated 204 mA and effective 800 µF, not an outage UPS or a test.

USB enters the logic source mux only, with pre-enumeration/configured current
limits and battery-independent bootstrap as detailed in the accepted review.
It never powers the energetic/servo source or charges the battery. Battery
validity keeps essential power independent of the comms processor.

Foinse uses autonomous TPS26630/CSD18540 source protection, a protected
auxiliary monitor return, INA228 and ADS1115 monitoring. One protected Croí
feed has a provisional 6 A aggregate ceiling. Liquid propulsion has a separate
6S pack/domain, not a load added to Croí's logic rail. External matched balance
chargers provide charging; physical charge/arm exclusion remains required.
Each Samtec ground path must tolerate the full 6 A alternate fault return.

All detailed branch limits, energy estimates and rail-sequencing qualifications
in the accepted power appendix remain. Separate power coupons are no longer
a pre-order requirement: run the defined bounded tests on the first full PCBA.
The sections below retain earlier rationale and test requirements; they do not
reopen selected parts or restore the old approximately 3.8 V placeholder.

Authority: [current system](../current-system.md),
[flight fault contract](flight-fault-contract.md) and the
[Ogma/Foinse/propulsion boundary](ogma-foinse-propulsion-boundary.md).
This is an initial contract, not a completed schematic or qualification result.

## Accepted decisions

1. Foinse's protected source path starts and continues basic power delivery
   without Ogma software or returned 3.3 V. Retain the protected return for
   bounded low-power devices. If their actual dependencies cannot meet this
   cleanly, bring back local Foinse regulation for review; do not hide a circular
   startup or protection dependency. Foinse has no MCU or firmware.
2. Communications/RF, bulk storage and the Foinse auxiliary return have bounded
   electrical branches. Their declared faults must not remove essential flight
   power or execution. This includes signal back-power and bus clamps, not only
   current limiting. One regulator per chip is not required.
3. Retain switching preregulator followed by a low-noise LDO as the baseline
   logic conversion chain. Direct-buck logic power is a comparison/revisit
   option, not the default. The earlier approximately 3.8 V intermediate value
   is provisional; exact voltage follows headroom, noise and thermal evidence.
4. Support USB-only configuration, readback and log extraction without any USB
   path capable of powering pyro or servo loads. Battery plus USB must not
   backfeed or unintentionally charge either source. Charging remains within
   Foinse's explicitly designed service path; standalone battery servicing must
   not introduce an implicit Ogma charger.
5. Allocate core hold-up to bounded brief interruptions, not indefinite
   continued flight after a broken source connection. No additional battery or
   large supercapacitor is selected by default. Budget measured modes against
   8 hours operating plus 4 hours reduced-duty recovery. Longer outages use
   EX-01's restart or primary-unavailable policy.

Servo/pyro power and return paths stay outside the logic supply path. An accepted
branch-containment requirement is not proof that a particular shared regulator,
fuse, switch or battery protection can satisfy it. The common source, core
conversion chain and PCB remain common failure points.

## Source dependencies

These are functional drawings. Every arrow requires a reviewed voltage/current,
return path, startup default and fault definition before schematic release.
They do not select connector pins, isolation devices or a regulator count.

### Standalone

```text
Local battery -> protected Ogma input -> switching preregulator -> low-noise LDO
                                          -> supervised logic and bounded branches
Local battery -> defined actuator power/arm paths -> pyro and servo loads
USB -> reverse-isolated service source path -> required service logic only
```

The exact point at which USB joins the logic supply remains open. It must work
at the permitted USB voltage/current limits and battery states. It cannot feed
back into the battery or actuator source paths through conversion or signals.

### Integrated with Foinse

```text
Vehicle battery -> Foinse autonomous protection/distribution -> Ogma VBAT
Ogma VBAT -> switching preregulator -> low-noise LDO -> supervised logic
Ogma regulated supply -> protected 3.3 V auxiliary branch -> Foinse low-power devices
Foinse -> named actuator source paths and paired returns -> selected loads
USB -> reverse-isolated service source path -> required Ogma service logic only
```

The returned auxiliary supply is never a prerequisite for the first line.
Foinse's source/protection defaults must remain correct with that return absent,
shorted within the declared containment case, or sequencing late. Essential
protection devices need their own valid autonomous bias path.

### Integrated with propulsion

```text
Vehicle battery -> Foinse autonomous protected distribution
                    +-> Ogma branch -> Ogma conversion and bounded branches
                    +-> propulsion branch -> propulsion-local logic/actuator power
Ogma protected 3.3 V return -> bounded Foinse low-power devices only
Ogma <-> narrow two-node CAN <-> self-governing propulsion controller
```

Propulsion is not powered from Ogma logic. Its existing local authority remains
unchanged. Shared-battery protection, return impedance and ground faults still
need analysis; separate branch names do not prove independence. These drawings
do not change the LTS implementation or assign another project's work.

## Branch contract

| Domain | Required behaviour | Numbers and implementation still needed |
| --- | --- | --- |
| Flight core and minimum recovery sensing | Valid supply and supervised essential execution; acknowledged primary loss if the common/core supply fails beyond the accepted envelope | Current modes, rail-valid window, supervisor tolerance, transient/restart budget |
| Communications/RF | Contain declared overload/short; bounded safe restart if possible; persistent failure disabled without a flight reset | Startup/transmit current, limit tolerance, disconnect/retry bounds, discharge and signal isolation |
| Bulk storage | Electrical or protocol failure permits degraded flight operation under FF-02 | Program/erase peaks, isolation, bus ownership, timeout and remaining evidence path |
| Foinse 3.3 V return | Bounded load and fault energy; return loss does not remove basic source delivery | Actual devices, current budget, isolation, signal/pull-up paths and autonomous defaults |
| Pyro and servo power | No USB or logic-rail energy source; deliberate high-current routes and paired returns | Selected loads, battery/rail ratings, physical arm paths, peak/stall/pulse currents and transient limits |

Protection must be selective: a contained branch fault must not trigger the
upstream battery/protection disconnect or sag the shared conversion chain
beyond the flight limit before that branch isolates. Hold-up energy must not
discharge into the failed branch. Check both power and signal paths in all
powered/unpowered combinations.

## Source-state table

| Connection/state | Accepted behaviour | Closure needed |
| --- | --- | --- |
| No source | No powered operation; output defaults remain defined | Discharge, retained-domain state and output bias |
| Standalone battery only | Autonomous start into the appropriate validated mode | Battery envelope, inrush, input protection and startup |
| Foinse source only | Same Ogma logic chain; source path independent of returned auxiliary power | Device dependency drawing and absent-return test |
| USB only | Configuration/readback/log extraction; no actuator power from USB | USB budget, power-entry point, rail sequencing and backfeed tests |
| One vehicle source plus USB | Supported servicing without source contention, backfeed or unintended charging | Priority/ORing mechanism and attach/remove tests |
| Integrated charging service | Only through the controlled Foinse service path | Charger/source combinations, allowed operating mode, isolation and operator procedure |
| Standalone battery and Foinse feed together | Not authorised by this contract; physically exclude or explicitly review/protect before permitting | Exact connector/source arrangement |
| Source removed or interrupted | Continue only within proven hold-up; otherwise defined reset/unavailable outcome | Interruption envelope and EX-03 retention classes |
| Auxiliary or communications rail absent while interfaces remain connected | No damaging injection, half-powered operation or defeated isolation | Exact pin limits, pull-ups, discharge and bus ownership |

Source priority and charging combinations are not silently selected by this
table. No live energetic or charging operation is authorised by policy adoption.

## Regulator selection and evidence

The retained chain came from the Rev 1 external review supplied again by Seán
on 6 September. The rationale is efficient preregulation followed by a genuinely
low-noise post-regulator, with mechanically suitable packaging. Its provenance
and the associated packaging feedback are recorded in the
[external-review note](../docs/rev1-external-review-lessons.md).

Shortlist integrated switching modules and compact integrated-switching IC
solutions; distinguish a module with an internal inductor from a converter IC
that still needs an external inductor and critical layout. TI, ADI and MPS are
comparison sources, not selected vendors or guaranteed EMI performance.

LT3045 is a low-noise LDO candidate. **LT3045-1** is the variant with VIOC;
ordinary LT3045 has no VIOC. The family is not selected for Ogma's total load.
The LT3045-1's rated output is 500 mA; the branch budget must establish whether
that is appropriate. [ADI product and variant table](https://www.analog.com/en/products/lt3045-1.html)

VIOC lets the LDO control its upstream converter to maintain input/output
headroom. It is a candidate, not an accepted extra control loop. Pairing,
startup, compensation and feedback-fault behaviour need review; ADI documents
compatibility restrictions. A fixed preregulator plus LDO remains a valid
implementation of the accepted architecture.
[ADI VIOC guidance](https://www.analog.com/en/resources/technical-articles/voltage-input-output-control-linear-regulators-part-1.html)

For LT3045-1, the datasheet's documented VIOC differential starts at 1 V. Thus
a nominal 3.8 V to 3.3 V chain cannot be assumed compatible with that VIOC
configuration. This is a part-specific constraint, not a universal minimum for
all buck/LDO chains. Do not select 4.3 V or any other value without the full
tolerance, ripple, droop, startup and thermal calculation.
[LT3045-1 datasheet, pp. 23–24](https://www.analog.com/media/en/technical-documentation/data-sheets/30451fa.pdf)

Measure intrinsic noise and rejection at relevant frequencies separately from
simple DC regulation. Also measure load steps, branch faults, startup/restart,
thermal behaviour and sensor performance with maximum relevant radio activity.
Retaining the LDO does not waive any of these checks.

## Initial numerical budget

| Quantity | Current allocation | Next evidence |
| --- | --- | --- |
| Logic output | Nominal 3.3 V baseline; tolerances not allocated | Exact MCU/sensor/storage operating limits |
| Intermediate output | Approximately 3.8 V historical placeholder, not frozen | Selected LDO headroom/PSRR and preregulator worst-case output |
| Input voltage/source impedance | Open | Candidate pack, protection, harness and USB service envelope |
| Continuous/startup/peak branch currents | Open; no measured Ogma 2 values | Exact-part estimates followed by branch measurements |
| Operating duration | 8 h | Measured mode/duty schedule and conversion losses |
| Reduced-duty recovery | Further 4 h | Beacon, retained state, log protection and quiescent currents |
| Flight-core hold-up duration | Open; bounded brief-interruption objective | EX-01/03 interruption allocation and measured core load |
| Temperature | Accepted powered envelope −20 to +70 °C | Junction/PCB thermal model, then installed measurements |

At battery level, calculate `E_required = sum(P_battery,mode × time_mode)` for
the complete 8 h + 4 h sequence. Include conversion/protection loss, quiescent
current and event loads once, without double counting. Available pack energy
must reflect temperature, age, source droop and protection cutoff; nominal
amp-hours alone do not close the budget.

For initial hold-up sizing use usable capacitor energy,
`0.5 × C × (V_start² − V_min²)`, against the load energy over the allocated
interruption. Include conversion efficiency, effective capacitance at voltage
and temperature, ESR, isolation loss and all attached loads. No numerical
capacity or flight endurance is claimed here.

## First experiment and closure

Use [PWR-01](../docs/reliability-execution-plan.md#experiment-pwr-01-source-transition-and-branch-containment)
on identified blocks of the first full PCBA with current-limited supplies and
inert loads. A separate pre-order coupon is not required. Begin with
cold startup with the Foinse return absent, then controlled optional-branch
faults and source transitions. Capture input, core rail, faulted branch, reset
and an essential-loop marker on an external common timebase.

Before applying a fault, identify the real parts and fixture, normal load,
instrument ratings, numerical stimulus/stop limits and claimed pass limits.
An emulator characterises that emulator and harness; it is not a real-pack pass.
No unknown battery hard-short, energetic load or unbounded fault injection.

EX-02 closes only with the actual source-state drawing, numerical budgets,
selected topology, owner/reviewer and measured corner cases. The protected
Foinse return is the accepted starting choice; exact device feasibility remains
to be checked with its owner. No hardware run, part purchase or flight release
has occurred. EX-03's [reset contract](reset-recovery-contract.md) is now
accepted at policy level; its host-model results do not establish hardware
retention. Proceed with library/schematic implementation under the accepted
batch baseline, followed by the first-PCBA tests.
