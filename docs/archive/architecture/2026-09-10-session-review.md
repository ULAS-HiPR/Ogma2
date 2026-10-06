# 10 September joint review: Burrito, Churro and Fajita

Recorded: 10 September 2026. Extracted: 11 September 2026.
Participants: Seán, Anav and Arnav. Status: source-backed review record, not final
stack approval. No schematic, PCB, pin allocation or firmware change follows
from this document. Seán explicitly paused those changes pending authorization
of the final stack.

## How to read this

The 8 September CAD is the preserved implementation reference. The discussion
reopens requirements and allocation choices; it does not silently replace the
existing interface contracts. **Working direction** means a direction expressed
in the room, not an approved circuit. **Open** means the session did not settle
it. **Clarification** distinguishes the intended mechanism from a misleading
phrase or technical claim in the transcript. **Follow-up** is proposed work,
not an assignment accepted by another person.

Anonymous transcription labels are inconsistent. Participant names below are
used only where the conversation supports attribution. AI voice responses are
not independent evidence or team decisions. Timestamps are offsets within the
source recording, not capture time. Repeated questions are consolidated without
discarding changes of mind. Private conversation, incidental media and career
discussion are omitted from this engineering record.

## Source ledger

The complete recordings were read, rather than just retrieval excerpts.

| Key | Recording start, Europe/Dublin | Duration | Stream record |
| --- | --- | --- | --- |
| N1 | 10 Sep 18:13:40 | 4:22 | `rec_ee6b47bfdf275ede672eb54701b9f10414578c94538235ecaff552d33f408d6f` |
| N2 | 10 Sep 18:19:11 | 5:04 | `rec_887767f8f7222956f8de7886ec2f8491268ecd50f39eb3da6beead506774aff3` |
| N3 | 10 Sep 18:24:20 | 3:10 | `rec_000ce7a7a75caabda71687ff12d008a464ffd0de0c649f3e339012bf340cc9cd` |
| N4 | 10 Sep 18:44:03 | 2:09 | `rec_2411a9e958497146858360ee572b47b58dd5762e54a7633274c87577a3eb67e0` |
| A | 10 Sep 18:53:18 | 32:19 | `rec_4ad9d295258498078b76b9ec8e59153f097a51b4acca8dadd894b0bb240553d5` |
| B | 10 Sep 19:28:23 | 1:10:37 | `rec_d05e30ca3d0e7fb3a08d3357371829771471ab1233660a9f6ec5ea2862b41fdd` |

Naming recordings total 14:45; the two review sessions total 1:42:56. The
recordings were captured into Stream around 23:07–23:12, later than the events.
A separate saved voice-chat exchange at 23:46:57 supplies the explicit
food/silkscreen rationale. The read window was 10 September 15:05:13 through
11 September 01:05:13, including the subsequent department message and LTS
correspondence. Raw transcripts remain outside this repository.

## Names and what they mean

| Spoken name | Existing technical name / role | Meaning retained from discussion |
| --- | --- | --- |
| **Burrito** | Croí2, standalone core flight computer | The essentials wrapped together: sensing, flight state, logging and communications |
| **Churro** | Foinse2, vehicle power companion | The power-board member of the shared food theme |
| **Fajita** | Separate propulsion controller | Heat/sizzle/energy association; engine sensing and local control |
| **Ogma / Ogma2** | Overall project/family | Retained for now; not another board |

N1–N4, A 02:35–03:50, and the saved voice exchange establish the mapping.
Salsa, tortilla, queso, beans, guacamole and other suggestions were explored,
not selected aliases. The group preferred recognisable meal/item names rather
than an increasingly obscure naming system. Board food illustrations and
spiciness markings were enthusiastic silkscreen ideas; colour, artwork and
marking rules remain open. White/black versus green or multicolour boards was
also discussed (A 30:21). No CAD files, net names or repositories are renamed.
A food-company sponsorship joke is not a sponsorship commitment.

## 1. The system boundary matters more than the names

N1 and N3: Rev 1's many boards brought duplicated functions, version/interface
coordination and more failure points. The proposed simplification is a useful
standalone core, a power companion when required, and a separate engine
controller. It is not a return to interchangeable internal flight-computer
modules. The core must remain useful without Churro.

A 03:50 onward and B 08:05: two processors divide timing and fault exposure,
but share a PCB and upstream resources. They are not independent recovery
computers. Losing radio/USB/GNSS work should not stop the flight loop. Neither
the discussion nor the documents demonstrate that containment yet.

The engine controller's autonomous sensing, redlines and actuation were used
as an analogy for remote control. That analogy does not settle where a fin
controller should estimate state. Different mechanisms have different loop
rates, observability and safe states.

## 2. Servo count, remote actuation and CAN: genuinely reopened

### Local output demand — A 04:31–05:53

Three servo channels were challenged. Two nearby functions seemed plausible;
neither a final count nor a complete load inventory was agreed. A distant
canard/grid-fin assembly need not justify long PWM wiring or another complete
flight computer. The existing three-channel CAD remains unchanged while the
vehicle/function inventory is established. The nominal common 2 A limit is
not a grid-fin qualification or a measured load budget.

### Where the loop runs — A 05:53–17:48

| Candidate discussed | Motivation | Cost / unresolved proof |
| --- | --- | --- |
| Flight MCU estimates state and computes actuator commands; remote MCU generates local outputs | Reuse the flight estimate; avoid duplicate sensors and estimators | Bound command age, bus loading, timing, controller execution and behaviour when messages stop |
| Actuator module has local sensors and closes its own loop | Local timing and isolation from optional algorithms or bus delay on the flight computer | Additional sensors, calibration, estimator consistency, software and failure modes |

Anav argued for using the existing central estimate; Seán emphasised local
autonomy and containment. Neither position was validated by a latency or
control-stability calculation. A neutral-on-silence response was suggested;
the mechanically safe response is mission-dependent and remains unproved.
Calling the actuator noncritical is not a completed vehicle hazard analysis.

Follow-up: describe the actual controlled quantity and actuator position,
required update rate and maximum age/jitter, then compare both routes. Include
boot, stale commands, bus-off, peer reset, jam/stall and power loss. A possible
third comparison—central state estimate with a local controller consuming it—
is an analyst suggestion, not a recorded selection.

### Physical network — A 17:48–25:02

The working physical proposal was a linear trunk with short drops, rather than
depending on each board forwarding the wiring to the next. One connector per
node and selectable end termination were discussed. This could accommodate
propulsion and a remote actuation peer; arbitrary payload traffic was not the
goal. Removing a board must not accidentally remove trunk continuity or a
required terminator. Harness termination and stub lengths need actual design.

**Conflict retained:** the controlled baseline is currently a fixed-termination,
500 kbit/s Classical CAN, two-node Ogma–propulsion connection. The discussion
does not authorize CAN FD, a third node, jumpers or transceiver replacement.
Those changes require a reviewed vehicle contract, including the stand's Ogma
emulator arrangement. A trunk diagram alone does not close the protocol.

Clarifications: bits/s and bytes/s were mixed in conversation; CAN FD headline
data-phase rates cannot be assumed for this hardware or harness. CRC does not
prove that a valid frame is fresh, appropriate or from the intended peer.
Differential signalling rejects some common-mode noise within device limits;
the illustrative positive/negative voltage explanation is not a bus-level
electrical specification. Neither “CAN is too slow” nor “CAN is reliable”
settles the control allocation.

A 21:10 left CAN ownership uncertain. B 13:59 resolved that the current design
already gives CAN to the **flight MCU**. No MCU ownership change was chosen.

## 3. Processor selection and firmware structure

A 28:23–32:19; B 16:00–20:35.

The team questioned why both roles need the same H563/LQFP100 device. The
follow-up is a role-based comparison, not changing parts because newer ones
exist: GPIO/alternate functions, CAN, timers, buses, memory, protected state,
clock/timing budget, cost, package, toolchain and maintained target count.
The existing shortlist is useful evidence, not proof that only four options
exist. A smaller comms MCU remains a candidate. Fewer pins are not, by
themselves, a demonstrated reliability improvement.

Anav's architectural role includes scheduler and driver boundaries. RTOS
versus bare-metal operation was discussed without a decision. An anecdote
does not establish that an RTOS is necessary or faster. Judge bounded work,
blocking, memory, fault recovery and measured deadlines on the actual workload.

ECC needs explanation by memory region and error coverage. MCU SRAM, internal
program flash and external NOR have different jobs and protections. ECC is
not immunity to radiation, wrong software or common board faults. Existing
128 MHz / 1 kHz / 200 Hz figures are budgets, not measurements. New indicators
and interfaces cannot consume imaginary spare GPIO: the current flight
allocation is already full.

## 4. Missions, reset history, measurements and GNSS

B 08:58–14:52; A 29:44.

- External GNSS reception remains justified by the carbon installation. The
  existing MAX-M10S/external antenna draft already implements that direction.
- The altitude/speed restriction debate did not establish a legal workaround
  or invalidate the selected receiver's documented 80 km limit. Ordinary
  launches and a bounded 100 km recorder mission are different configurations.
  Explain why the latter needs independent recovery and full-envelope height
  evidence; do not make ordinary users infer this from a “space” label.
- Rev 1's reset around recovery remains unexplained. The conversation does not
  prove a brownout, connector or software cause. Preserve voltage/current,
  reset class, commands and event ordering so the next incident is diagnosable.
- Orientation, exact package and shared-bus mistakes remain concrete lessons.
  Keep axis transforms, part identity, bus isolation and installation checks.
- “Source age, validity and datum” was not clear to the room. Explain it with
  an example: receiving another copy of a one-second-old fix is not receiving
  a new position; pressure-derived height and GNSS height are not the same
  measurement or necessarily measured from the same zero.
- USB ownership was questioned but no change was settled. Current normal USB
  service belongs to comms. Comparing another computer's USB arrangement is
  not evidence that either arrangement is wrong.
- The six-contact Tag-Connect/SWD interface was called JTAG colloquially.
  Keep SWD terminology and distinguish electrical contacts from alignment holes.

B 20:35: “staging inhibited after reset” was read as a boot/calibration issue.
It means inhibiting a subsequent rocket-stage motor ignition after an ambiguous
in-flight reset. It does not mean restarting calibration is the mitigation.
Recovery continuation needs validated flight phase and time; resetting cannot
declare a new flight or simply replay the entire event sequence.

## 5. Power: expose each job before selecting its part

B 23:40–39:35, 58:53–1:00:00 and 1:09.

### Three rails and startup

The purpose of the optional rail was unclear and deletion was proposed. Trace
its actual loads and failure boundary first, including logger/AUX and Churro
monitoring dependencies. The documents already identify those loads; “nothing
uses it” is not established. Removing a domain would require reallocating the
loads and their fault containment, not just deleting an LDO.

“Bootstrap bias” prompted a generic high-side-MOSFET explanation, which did not
explain this design. Here the documented USB/source-selection startup problem
is avoiding dependence on firmware that has not yet received power. Explain
that dependency and the actual U1102 path. Do not substitute a generic internet
definition. Ordinary external switch bias is another named function.

The requested diagram must show source selection, protection, buck conversion,
all post-regulators, loads, switching/control dependencies and output energy.
A diagram ending at the LDOs hides the reason there are several rails.

### Arithmetic and evidence

- LDO efficiency is approximately Vout/Vin before quiescent losses: 3.3/4.0
  is 82.5%, not a generic 30% or 95% rule. Overall efficiency also includes
  the buck, switches and operating point.
- Nominal 2S is not full-charge voltage. Use the actual pack envelope, not
  just 7.4 V, in device and actuator checks.
- The module's startup threshold and the 4 V downstream setpoint describe
  different nodes. Headroom also includes tolerance, load and transients.
- C1403 / 1000 µF is an unresolved allowance, not measured hold-up. Reverse
  blocking, stored energy and current limiting solve different faults.
- A power budget is calculated demand. A measured power trace is evidence.
  Neither substitutes for the other; label which one is being discussed.

### What Churro is for

Working direction: keep vehicle-specific power and possible actuator regulation
off the reusable Burrito wherever the interface permits. Standalone Burrito
still needs a compatible source. A regulated servo rail belongs in the power
allocation discussion, but no converter, voltage or new connector was chosen.
Churro exists partly so changing a vehicle's power needs does not force a new
expensive flight-computer design.

No BMS was requested on Burrito. The boundary between a battery's protection,
Churro protection and external charging remains to be specified. Conformal
coating was discussed as assembly protection, not a guarantee against shorts.
Reverse polarity, reverse current/backfeed, overvoltage and overcurrent require
distinct explanations. Do not merge them into “protection.”

### Current sensing: an objection and its resolution

N3 and B 37:05–39:35 revisited core versus companion placement. Keeping the
common battery-current measurement on Burrito preserves evidence in standalone
use; Churro may measure other branches without duplicating that same path.
This matches the existing INA228 allocation. The cost is shunt drop, series
failure exposure, measurement bandwidth and driver work.

A current change can support an electrical-response observation. It does not
prove servo position, successful ignition or a completed mechanical action.
Continuity is also not proof the whole mechanism will work. Keep intent,
electrical response and observed outcome separate.

## 6. Operator interface and human error

B 36:32–50:08.

Launch stress and misconfiguration are design inputs. The team wants to know
which firmware is actually running and whether configuration/upload succeeded.
The on-board display idea was challenged by fragility and precedent with the
groundstation display. OLED and seven-segment options were discussed; the
working direction favoured detailed USB/configurator readback rather than a
new fragile display. The host must read device identity/build/configuration,
not merely report that a file was sent. No display has been added.

| Indication discussed | What the operator needs | Status and distinction |
| --- | --- | --- |
| RGB readiness/health | A concise operating/fault state | Candidate replacement for complementary red/green; GPIO/driver/reset behaviour unresolved |
| Hardware physical-arm indication | Output-energy availability without trusting a running MCU | Requested direction; exact sensing and independent proof remain safety-review work |
| Separate flight/comms rail LEDs | Distinguish present supplies | Candidate; voltage present is not software alive |
| Per-channel continuity | See which external circuit has continuity | Candidate; diagnostic energy and fault paths need no-fire review |
| CAN activity | Notice intermittent traffic/cable symptoms | Discussed favourably later; human-visible activity does not measure packet loss accurately |
| CAN peer health/freshness | Know a required peer is responding usefully | Distinct from activity; exact combination of indicators remains open |

Do not turn every suggestion into an extra LED. Agree the operator questions,
then choose the smallest indication set. Any-traffic blinking is not a valid
peer heartbeat; a latched green state is not proof of ongoing health. Signal
handling is not free at high rates, even if the LED is simple. The question of
how continuity indication is driven was not resolved in the session.

## 7. Energetics: the review was deferred, not accepted

B 50:23–58:00 and 1:08:19–1:08:58.

The group could not use the component-heavy explanation to reason comfortably
about the mechanism. This is a documentation defect, not approval to simplify
the circuit or evidence that everyone understood it. Re-review with an energy
path, permission path, failure example and only then the device references.

Non-retriggerable does not mean a channel can only ever fire once. It describes
whether another trigger extends/restarts an active timing interval. Independent
duration bounding addresses a stuck request; it is not justified merely by
saying the charge is spent. High-side and low-side switches act on different
sides of the load and have distinct failed-short/sneak-path implications.
Their presence alone does not establish single-fault safety.

The group leaned toward one physical enable for servo and energetic output
energy, distinct from computer power. That is a working operator-level
direction, not an approved common arm circuit. Review recovery versus sustainer
hazards, diagnostic leakage, fault isolation and observable disarm before
selecting grouping. All existing DNP links and no-live-test restrictions stay.

## 8. Logging: three different survival problems

B 21:20–23:40, 1:04:08–1:04:32 and 1:06:35–1:08:19.

1. **Interrupted write:** recover prior committed records and reject an
   incomplete final record/block. An interrupted write must not invalidate the
   entire flight. Existing footer/commit and bounded restart work addresses
   this, but has not been demonstrated on hardware.
2. **Physical damage:** recover data when the main PCB is damaged. Soldered NOR
   may help avoid socket failure, but is not a crash-survivable recorder. Define
   the damage case, storage placement and service/extraction path before adding
   hardware or claiming survival.
3. **Lost vehicle:** ground recording provides an independent partial copy.
   Seán reported the Mac Ogma app already records; Arnav reported recording on
   the Cyberdeck. These were reported capabilities, not inspected here. Verify
   what each saves, timestamps, losses, flush behaviour and playback. Radio
   cannot replace the full-rate on-board record.

The pre-trigger buffer proposal matters: capture the lead-up to an event,
particularly a pad/ignition transient, rather than starting only when launch
is detected. While waiting, retain a rolling history; when triggered, preserve
that history and continue recording. Define what starts the buffer, what
triggers preservation, how much time each stream covers, how it relates to
low-rate pad logging, and what survives a reset or aborted launch.

“100 samples” was an example, not an accepted requirement: at 1 kHz it covers
only 100 ms. Size by seconds, stream rates/record sizes and available memory.
Do not promise that a volatile rolling buffer survives complete power loss.
No erase, storage stall or crash-recovery scan may block essential flight work.

Follow-up: use the existing 96,672 B/s draft budget, actual memory ownership and
commit method to calculate a useful pre/post-event window; test interruption
at each record/commit phase with inert bench operation. Exact duration and
mechanical survivability are still open.

## 9. Pad power, external service and GNSS lock

B 1:05:14–1:06:35.

The team discussed external/on-rail charging, a removable connection and
maintaining GNSS lock while waiting. Capture an operating sequence: packs
connected, service/charging state, logic on, valid GNSS acquisition, output
disarmed, external service disconnected, deliberate arming. This sequence is
proposed review structure, not an approved launch procedure.

Removing a charging/service plug must not silently become permission to arm.
Charging, logic enable and physical output-energy isolation are separate
functions. “Screw terminal” in conversation does not supersede the installed
JST-GH maintained-contact draft or the locking-connector rule. The present
electronic enable is open/unplug = OFF, closed = ON; it is not a load-current
switch or complete battery isolation. External matched charging remains the
baseline; no on-board charger was authorized.

## 10. Expansion and onboarding without enlarging the core

B 00:00–03:00, 1:00:00–1:04:08; A 17:48–25:02.

Anav proposed mikroBUS-style expansion on the power companion. Discussion
settled toward a **separate generic payload carrier**, rather than adding
arbitrary experiments to the flight computer's safety/timing domain. A small
MCU, suitable power input/regulation, programming access, connector/mounting
and experiment interfaces could give beginners something reusable. External
memory and independent radio were possibilities, not selected hardware.

Keep the existing eight-contact Samtec interface distinct from a 16-contact
mikroBUS footprint. Its present pins do not carry every proposed bus. Do not
assume Quad-SPI is supplied by a standard mikroBUS arrangement; verify the
actual desired module/interface before drafting a carrier.

Candidate work from the session:

| Candidate | Useful first result | Boundary |
| --- | --- | --- |
| Small MCU/power/programming board | A board its builder can order, assemble and bring up | Start with a named use and understandable power/debug path |
| Buzzer/music experiment | A personally motivating first working circuit | Bench/payload work; do not inject unbounded work into flight timing |
| Generic payload carrier | A repeatable platform for experiments | Independent scope; not a miniature copy of every Burrito feature |
| Remote CAN actuator demonstrator | Test command age, timeout and local outputs with inert loads | A learning rig first; flight control needs competent ownership and formal review |
| On-rail service/charging investigation | Defined operator sequence and interface | No live charging/arming shortcut or invented battery wiring |

A brief introductory build and roughly three weeks to get people up to speed
were discussed, not an approved universal timetable. FC, groundstation and
payload interests can form working groups within the same weekly room. JLCPCB
coupons/order support can lower the barrier; procurement terms were not checked
in this pass. Tutorials support a project when a tool is needed, not an entire
term spent preparing to build.

The later message to Jay makes the departmental intention explicit: grow
owners through real hardware, competition payloads and possible month-long
payload build sprints using a custom L1 vehicle. Seán proposes deferring this
REXUS round; Jay's agreement is not recorded. These intentions do not assign
the engine controller or competition payloads to Seán by default, nor commit
unasked newcomers to critical flight work.

## 11. Test opportunities and physical integration

N3 proposed bench work plus repeated real flight opportunities, including
monthly launches and a custom L1 vehicle. Nosecone extensions/inserts were
discussed as ways to fit hardware, not approved changes to someone else's
rocket. Payload volume, recovery clearance, mounting, mass and permission need
agreement for each vehicle. Flight opportunities complement qualification;
they do not replace inert-load, power/reset, logging and fault-injection work.

The phrase “once the boards go for fabrication” must not imply the work is
finished: assembly, bring-up, integration and qualification remain. This session
did not produce a fabrication-ready stack.

## 12. What the documents failed to do

A 00:00–02:35; B 36:04 and 50:23–58:53.

The room tried reading aloud, listening and shared reading. The useful behaviour
was stopping at a confusing statement and debating the actual function. Slow
progress through the text exposed unclear assumptions and real disagreements.
It was not evidence that the team should read faster or approve the rest unseen.

Future chapters must present:

1. The vehicle job and a concrete example.
2. A small diagram of energy, data and decision ownership.
3. What failure the mechanism handles and what it cannot handle.
4. Alternatives and their costs, with current status explicit.
5. Only then component references, calculations and sources.
6. The smallest evidence needed for the next decision.

Do not require readers to decode TXU, one-shot, staging, bootstrap, ECC or
datum before understanding the system. Define the term at first use. Keep the
research depth available, but do not lead with a parts inventory. A later
annotated PCB-domain image can help once placement is meaningful; generating
a polished image now would falsely imply settled geometry.

## 13. Review gates before changing hardware

These are proposed review tasks, not new assignments or a demand to answer
everything before discussing one section.

| Gate | Evidence / choice needed | Hardware remains untouched until accepted |
| --- | --- | --- |
| Vehicle functions | Local recovery/servo count, remote actuator job and actual loads | Channel removal/addition, connectors, current limits |
| Remote control | Loop location, age/jitter/failure response; bounded workload | Added MCU/sensors or changed flight responsibilities |
| CAN contract | Named peers, rate/protocol, harness/termination, stand compatibility | Third node, FD, jumpers, transceiver or pin changes |
| MCU roles | Resource/timing/pin comparison and maintained-target trade | Processor/package replacement |
| Power allocation | All rail loads/startup dependencies, servo supply, pack/BMS/charging boundary | Optional-rail deletion, regulator or Churro expansion |
| Operator safety | Power versus arm versus continuity versus health; full inert-load review | Indicator circuits, arm grouping, output population |
| Evidence | Pre-trigger seconds, commit/restart behaviour, extraction and ground-copy scope | Added storage or claimed damage survival |
| Stack authorization | Team review and Seán's explicit final-stack instruction | All schematic/PCB implementation resumes only within that scope |

The highest-leverage next review is the vehicle-function/output map and remote
actuation/CAN allocation: it constrains processor, connector, power and indicator
choices. Meanwhile the mechanism explanations can improve without changing
hardware. Existing safety restrictions and source-grounded component data remain
valid unless explicitly superseded; a reopened choice is not a blank cheque.

## Adjacent LTS movement, kept separate

The window ends with Daire's annotated pressure-transducer P&ID and candidate
Keller Series 20 / WIKA S-20 links, plus Anav's sampling/filtering questions.
That advances the inputs discussion. It does not close the inventory, exact
output variants, required bandwidth or sample rates. A stated settling time
does not by itself establish a required ADC rate; analogue output does not
remove anti-aliasing requirements. Claims about I²C speed must be evaluated
against the actual device and bus, not used as a universal rejection.

No LTS P&ID, sensor selection or Fajita channel allocation was changed here.
Reconcile through the LTS project's own current authority before deriving the
propulsion-controller hardware envelope from those messages.
