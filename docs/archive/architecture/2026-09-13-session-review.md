# 13 September 2026 architecture review: learning and dispositions

Compiled 14 September from the complete recording sequence and subsequent
reflections. Remote review branch verified at
`695b6779faa45ee62949164e82c375551da11e83` before this documentation update.
This is a review record, not hardware qualification or final-stack permission.

## Extraction completeness correction — 18 September

The first integration captured themes but left several explicit requested
deliverables unfinished. See the [full change ledger](2026-09-18-meeting-change-ledger.md)
for timestamped coverage and completion status. The power-path drawing was a
concrete missed request, now corrected in chapter 2.

## Sources and limits

Recording time is distinct from capture time. Anonymous transcript speaker labels
are unreliable; the second recording also includes model speech. Quoted proposals
and model explanations do not establish team agreement. Timestamps below are
elapsed recording time; names are used only where attribution is explicit.

| Key | Recorded 13 September | Duration | Connective Tissue source |
| --- | --- | --- | --- |
| P: preparation | 16:48:41 | 16:37 | `rec_7b57dceb5ae6e0c07cae522dd4dcaa461ff2b4303c93fa5bccfa2708c50974f7` |
| A: architecture first part | 17:08:52 | 59:25 | `rec_ba14534e3931cd36b1bb177136382b0dd657c65abbcf4f4ef0e0df4b8fe36a6a` |
| B: continuation and LTS | 18:20:42 | 1:35:00 | `rec_72a0a6af3693b1be42861125009f42f8384d0ca2dc55e6c35c9e88f0922450ea` |
| D: after-meeting reflection | 21:44:15 | 33:19 | `rec_0519896123170365db10ac477250d2d55e9ab883015ab59da7a6477fc6fbbb74` |

B covers Ogma until approximately 21:18, LTS preparation at 22:19–35:25,
the LTS meeting at 46:01–1:32:31, and immediate aftermath thereafter.
The model reflection captured at 23:00:34 is
`rec_5015928b74d12709577f21e2700cf53ccb5ce62f022908e7b8f6c5279d808d0a`.
Its optimistic recruitment interpretation was corrected by Seán on 14 September
at 00:34 and 00:39, followed by model corrections. Those are reflections, not
new electrical requirements. Raw transcripts and private reflections are not
copied into this repository.

## What actually changed

| Topic | Review disposition | Implementation status |
| --- | --- | --- |
| Burrito, Churro, Fajita | Canonical names stated by Seán, A 02:24–02:51 | Existing file/net names retained |
| Standalone core and separate flight/comms roles | Reaffirmed; two processors are workload separation, not redundancy | Preserved baseline |
| Local servo count | Two local channels agreed, B 04:26–05:46 | CAD still has three; reconciliation awaits final stack |
| Remote control | Central estimation/control favored; remote node still receives commands and handles stale data | Timing and mechanism requirements unresolved |
| CAN FD | Direction explicitly settled in discussion, B 10:58–11:24 | Rates, topology, peers and qualification not settled; Classical CAN contract preserved pending revision |
| Rail count and input envelope | Reopened; compare two-rail allocation and narrow core input | No regulator deletion or voltage-range change approved |
| Energetic complexity | Necessity challenged, not merely terminology misunderstood | No mechanism deletion approved |
| Diagnostics | Broad inventory requested before reducing hardware | No LED driver/display selected |
| Review coverage | Chapters 0–5 discussed; 6–8 not reached | Unread chapters are not accepted |

## Processors: count jobs before pins

The explanation of two processors was useful (A 09:12). The pin audit answered
whether signals fit, but not whether their jobs were justified (A 12–25).
For each enable, sense line and reserved function, state: the event that uses it,
the consequence without it, the fixed-state/deletion alternative, and the test
that would distinguish those choices. A pin-full package is not evidence of a
CPU-full workload.

Specific misunderstandings to prevent:

- Pressure sensors use I2C1/I2C2; Churro monitoring uses a separate I2C4.
- Six energetic ADC inputs mean three current plus three continuity inputs,
  not three servo plus three energetic inputs. Six request/select lines are
  two controls for each of three energetic channels.
- Arm sense observes a physical condition; it does not create physical isolation.
- OCTOSPI1 is the peripheral name. The present NOR interface uses four data lines.
- DRDY announces a sample; it is not another sensor bus.
- CAN enable and standby have different electrical functions, but both still
  need a use case. A schematic symbol alone does not justify either control.
- An aggregate branch-fault input reports a fault, not which branch caused it.
- External watchdog recovery, internal watchdog recovery and full power removal
  are different fault experiments. No interruption test was performed in this review.
- PPS is a timing pulse; SWO is a diagnostic trace option. LSE/RTC and active HSE
  clock roles differ. PC13 restrictions require the exact device erratum.

The existing H563 LQFP100 audit gives flight 79 connected pins plus one quiet
pin and comms 48 unused pins under its stated allocation. DMA reservations are
not proven concurrent operation. Broaden the MCU comparison beyond one smaller
H563 and H503: memory, required peripherals, package routing, execution budget,
software reuse and procurement all matter. A full mock firmware exercise was
suggested and disputed; it is not an agreed prerequisite (A 25:27–27:35).

## Power: compare actual alternatives

The room needed ordered paths and failure consequences, not another definition
of a regulator (A 34–50; B 00:07–00:45). Reverse polarity, reverse-current
blocking, current limiting, physical arming and stored energy do different jobs.
AUX is the monitoring feed to Churro, not Churro's main vehicle power source.

The third rail has real loads, but saying those loads stop when it is deleted
is circular: compare reallocating them. A meaningful two-rail candidate puts
NOR/CAN/AUX on protected branches of a continuously available non-flight rail,
with communications recovery at a downstream branch. It cannot retain a global
comms-rail power-cycle policy that also removes those loads. Compare added local
switches, fault selectivity, reset independence, area and measured loss against
the existing three-regulator arrangement. No saving is established yet.

USB startup bias breaks a startup dependency; it does not itself select a USB
negotiated current. The hold-up calculation uses 800 µF effective, not 8,800 µF.
Usable voltage fall is the capacitor starting voltage minus the minimum LDO
input needed to maintain flight power, including dropout and path loss.
At 204 mA and 0.25 V, 800 µF gives about 0.98 ms; 10 ms needs about 8,160 µF
before allowances. Neither calculation is a measured survival interval.
NOR/CAN are outside the held flight domain, so an emergency flush is not assured.

Specify a complete accepted core input range; nominal 7.4 V is insufficient.
A narrow 2S core input with Churro adapting other packs is a candidate, not an
accepted UVLO/OVP range or permission to apply another voltage. Continuity was
favored as useful, but its supply allocation remains open. Electrical current
is evidence of electrical response, not proof of mechanical action.

## Energetic outputs: justify the mechanism

A 51:29–58:53 challenges the cost and necessity of protective mechanisms.
The next review must compare each mechanism against a named failure and a
simpler alternative. Do not substitute a definition of a one-shot for evidence
that this system needs one. Conversely, a nominal load burning out does not
establish behavior under every wiring or component fault.

Separate physical permission, command issuance, pulse termination and behavior
after reset. The room heard a retry policy that the pack had not actually
specified. Repeated events and reset-state validation must be stated separately.
Record proposed removals as proposals; preserve the installed contract until
reviewed. Use inert fault tests for discriminating evidence. Space-shot recording
is a separate mission configuration; a possible CO2 actuator does not justify
all workhorse outputs or establish a final deployment design.

## Servos and vehicle CAN: count functions, then prove timing

Two local channels support the stated standalone/canard use; distant mechanisms
can use remote nodes. This is a target, not a CAD edit. Powered-off signal
isolation prevents control-pin back-power; it is not servo voltage regulation.
Simultaneous demand, stall duration and aggregate current remain unqualified.
A capacitor does not resolve an unknown actuator envelope.

Central control avoids immediately duplicating an estimator. The remote node
still needs command receipt, PWM generation and defined stale-command behavior.
Trace sensor sample/filter delay → estimation → queue → CAN arbitration and
transfer → node scheduling → PWM update → mechanical response. Average bus
occupancy alone cannot establish maximum age or jitter.

CAN FD is the new direction; retain the 500 kbit/s Classical calculations only
as a comparison baseline. Do not reinterpret speculative rates as accepted
bitrates. Obtain actual loop rate, permitted delay, mechanism and sensing needs
from the canards team. A participant volunteered to contact them (B 14:02);
there is no source-backed evidence here of a sent message or received answer.

## Diagnostics: build the inventory before choosing LEDs

B 14:51–19:50 asks for useful test/flight distinction and broad diagnostics,
then reduction. USB identity and configuration readback remain useful; a screen
is not thereby required. An I2C RGB driver was suggested, not selected.

Separate electrical power, firmware progress, valid data, activity, operating
mode and physical arm state. For every indicator say what drives it, what it
proves, and what it does when its processor resets. A software-set green light
cannot independently prove physical isolation. Detailed faults can remain in
USB readback; a few lamps need not encode the entire diagnostic inventory.

## Unreached chapters and cross-project boundaries

Chapters 6–8 still need their full review. Earlier discussion raised comms-local
GNSS/radio logs recoverable after link failure: compare forwarding into flight
storage with local storage using reset, link-loss, power-loss, timestamp and
readout cases. No extra flash chip was selected. Two directions of a radio link
need not have identical measured RSSI. The GNSS restriction discussion did not
invalidate a receiver's stated operating limits; verify the exact receiver
specification rather than substituting remembered regulatory rules.

Churro startup must remain autonomous. Fajita retains local propulsion safety.
The LTS discussion supplies interface questions, not authority to change that
project from this repository. CAN FD migration needs named peers, compatibility
and timing before either side's contract changes. Payloads should enter through
bounded interfaces instead of accumulating bespoke core obligations.

## Collaboration learnings from before and after

The first model reflection correctly recognized active questioning and failed
explanations, but overread recruitment interest as future capacity. Seán's later
correction matters: another interested person can add supervision demand before
adding independent throughput. Review participation is not acceptance of ongoing
integration responsibility. A suggested owner is not an accepted owner.

The record also contains concrete progress by collaborators, including Anav's
solid-stand instrumentation work; a blanket story of incapable collaborators
would be unsupported. Separate completed evidence, bounded work somebody accepts,
and hoped-for capacity. Models should bring reasoned defaults and legible
comparisons, reducing the human explanation burden rather than creating another
list Seán must research. Do not assign him every unresolved integration task.

## Next review and closure evidence

1. Briefly revisit retained explanations; resolve changed assumptions in 0–5.
2. Continue through 6–8, explicitly recording coverage.
3. Compare MCU candidates and two-/three-rail allocations with concrete budgets.
4. Obtain actuator requirements; define FD peers and an end-to-end timing budget.
5. Review energetic mechanisms against faults and simpler alternatives.
6. Reduce the diagnostic inventory into hardware and USB behavior.
7. Reconcile electrical contracts and CAD only after final-stack authorization.

Each item needs an accepted owner and a bounded deliverable; none is assigned by
this document. Physical verification remains pending. Keep understood text,
rewrite confusing explanations in place, and distinguish comprehension, design
choice, implementation and validation at every subsequent pass.
