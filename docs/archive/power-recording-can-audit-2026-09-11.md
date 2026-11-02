# Power, recording and remote-actuation budgets

11 September 2026. **Desk investigation; recommendations, not accepted changes.**
Supports chapters 2, 4, 7 and 8 of the architecture reading pack. No schematic,
PCB, pin allocation, firmware or cross-project interface was changed.

## Evidence and reproduction

- Current [system](../../current-system.md), [power contract](../../interfaces/power-contract.md)
  and [vehicle interface](../../interfaces/ogma-foinse-propulsion-boundary.md).
- Current [firmware handoff](firmware-handoff-2026-09-07.md): 7 September current
  record revision, optional CAN branch, memory allocation and device starting rates.
- [Croí schematic](../../hardware/croi2/Croi2.kicad_sch), inspected through the fresh
  KiCad XML export used by the pin audit. Schematic hashes still match the native
  checked snapshot in [full-checks.json](../../hardware/croi2/full-checks.json).
- [Preserved recording analysis](architecture/implementation-reference/07-sensors-logging.md).
- Run `python3 tools/architecture_budgets.py` from the repository root for the
  arithmetic below. Constants are explicitly illustrative where requirements
  are absent. The script neither changes files nor models electrical transients.

## Optional rail: traced loads and failure paths

The netlist's `3V3_OPTIONAL` powers more than the earlier drawing showed:

| Source connection | Trace / downstream load | Evidence distinction |
| --- | --- | --- |
| U3601 IN | Limited NOR supply, NOR and interface switches | Populated branch |
| U501 IN | Limited CAN supply, transceiver VCC/VIO and translator VCCB | Populated branch |
| U7001 IN | AUX return, local INA228 through R7105, external monitoring | Populated branch; standalone monitor shares it |
| BZ9001 positive, D9002 cathode and R9005 | Piezo/driver and discharge network | Direct rail load, not a separately limited branch |
| R6911/R6921/R6931 | Proposed continuity injection feeds | DNP; not active loads and no values selected here |
| R1903, local capacitors/testpoint | Rail feedback/support and decoupling | Also attached; cannot assume only the named peripheral switches can fail |

These are schematic connections, not proof that a populated assembly contains
shorts. The checked snapshot retains the continuity DNPs. No live-output work
is authorized by this analysis.

Separate peripheral switches bound individual faults; an optional-regulator or
shared-rail fault can remove NOR, CAN, monitoring and audible indication together.
The upstream limiter aims to keep that off flight power. A common buck, return
impedance, finite trip time and signal injection remain possible couplings.
The earlier functional drawing omitted CAN and the direct rail loads; chapter 2
now includes them.

**Recommendation:** retain this domain pending a demonstrated simpler equivalent.
Moving the loads onto held flight removes the intended boundary. Moving them to
the switched comms rail makes a comms power cycle interrupt logging and CAN.
A merged nonessential rail with independent comms sub-switching is a real
alternative, but needs revised sequencing, aggregate current, fault selectivity
and signal-isolation analysis. It is not deletion of one LDO alone.

Normal budget is 100 mA on this domain, not a measured maximum; approximately
0.5 A is its upstream allocation. NOR, CAN, AUX, sounder and support loads must
be added by mode, including startup and faults. The model does not claim each
downstream limiter trips before the upstream one. Retaining the rail costs
parts/area and retains a common failure domain for those nonessential functions.

Smallest validation after assembly: observe essential rail/reset alongside the
faulted branch during bounded, current-limited inert tests. Set fixture/stimulus
limits from actual components before applying faults. No battery hard-short or
energetic load is part of this check.

## Hold-up: brief dips only

The capacitor is on `CORE_HELD_4V`, after reverse blocking and before the flight
LDO. NOR and CAN have separate supplies from the unheld optional domain.

The existing contract assumed 800 µF effective and 204 mA. For the LDO's roughly
constant input current, `t = C × ΔV / I` is the useful first-order model. The
usable fall must already subtract dropout, tolerances, ESR step and other drops:

| Usable fall | Calculated time |
| --- | --- |
| 0.10 V | 0.392 ms |
| 0.25 V | 0.980 ms |
| 0.50 V | 1.961 ms |

The 0.25 V example reproduces the order of the earlier ~1 ms allowance; it does
not establish an actual minimum valid voltage. At this same fall/load, 10 ms
requires 8,160 µF effective. The 1000 µF nominal placeholder has no approved
part, tolerance/temperature curve, ESR or footprint qualification.

**Recommendation:** retain the brief-dip objective, not an emergency-flush claim.
The MCU can outlive the NOR supply. Increasing only its capacitor cannot change
that. A logger-energy redesign would be a separate architecture choice; none
is justified solely to preserve an uncommitted tail. Prefer continuous commits,
explicit gaps and the existing bounded reset policy.

## Recording: history and writer queue share RAM

Use the current 96,672 B/s allocation conservatively for both RAM and storage.
It includes framing allowance; a final packed-RAM format might be smaller,
but no such implementation was inspected. KiB/MiB mean powers of 1024.

| Exclusive RAM capacity | Seconds at the budgeted rate |
| --- | --- |
| 32 KiB | 0.339 |
| 64 KiB | 0.678 |
| 96 KiB | 1.017 |
| 128 KiB | 1.356 |
| 256 KiB | 2.712 |

The handoff's old ~1.38 s description predates the latest rate. The current
128 KiB staging allocation is not a second independent history allocation.
The 256 KiB row is arithmetic only, not permission to spend all SRAM1.

Five seconds is 483,360 bytes; ten seconds is 966,720. A 96/32 KiB history/queue
split supports ~one second plus ~0.339 s of initially empty writer queue, less
metadata and occupancy. This is a candidate only. Trigger preservation must
not freeze a buffer while acquisition overwrites it; ownership/copy/drain
semantics need implementation. Unprotected SRAM remains non-authoritative.

**Recommended first implementation for review:** continuous append-only full-rate
recording shortly before arming; proposed minimum 10-second lead-in before launch,
with timestamped event markers and the existing staging queue. No in-flight erase.
This preserves pre-event context without requiring a large volatile ring. It
costs pad storage and needs an explicit readiness/start/abort policy. It does
not promise zero tail loss on power failure or an unlimited wait at full rate.

### Capacity ledger

| Allocation | Bytes |
| --- | --- |
| Installed nominal capacity, 256 MiB | 268,435,456 |
| Retained reserve, 64 MiB | 67,108,864 |
| Available outside reserve | 201,326,592 |
| Thirty minutes full rate | 174,009,600 |
| Existing other pad/recovery/metadata allowance, by subtraction | 6,578,176 |
| Existing complete mission budget | 180,587,776 |
| Remaining beyond that budget and reserve | 20,738,816 |

The last line is 214.5 additional full-rate seconds. An extra 10-second lead-in
costs 966,720 bytes; 30 seconds costs 2,900,160. Count it once, not again if it
is already inside the old allowance. Multiple full-rate aborted attempts spend
the same finite capacity. The final encoding must reconcile headers, footers,
alignment, bad-region policy and burst allowances against this ledger. Existing
20% overhead is a budget, not proof the final format consumes exactly that much.

### Program throughput versus transfer width

Manufacturer search-index text for MX66L2G45G Rev. 1.1, section 16, reports
1.5 ms maximum page-program time under stated worst conditions. Direct PDF
retrieval returned 404 in this pass; the indexed primary text agrees with the
earlier study, but the exact supplied device/revision still needs verification.
[Macronix source](https://www.macronix.com/Lists/Datasheet/Attachments/8959/MX66L2G45G%2C%203V%2C%202Gb%2C%20v1.1.pdf).

For sixteen 256-byte data pages and one footer page, programming alone takes
17 × 1.5 ms = 25.5 ms per 4096 useful bytes. Add data transfer only:

`service rate = 4096 / (0.0255 + 17 × 256 × 8 / (16,000,000 × lanes))`

| Transfer width | Simplified useful rate | Capacity not used by 96,672 B/s |
| --- | --- | --- |
| One lane | 147,998 B/s | 34.7% |
| Four lanes | 157,272 B/s | 38.5% |

This omits command/address/status, polling, readback, scheduling and contention.
It assumes the corresponding page-program mode and full data pages; no measured
throughput or power-interruption guarantee follows. A second commit program for
every data page gives only ~85.3 kB/s even before transfers, below the budget.

**Recommendation:** retain grouped commits. Single-lane transfer is a credible
two-pin-saving experiment, not an accepted remap. Measure sustained verified
logging with acquisition active, including stall distribution and torn writes.
At this rate a 4 KiB block fills in ~42.4 ms; programming adds ~25.5 ms plus
transfers before commit. Neither that unfinished block nor queued data is
guaranteed by the roughly 1 ms flight-only hold-up.

## CAN traffic and latency

Existing contract: 500 kbit/s Classical CAN, two peers. Standard/extended-ID
selection and new actuator message formats are not frozen by this analysis.
TI lists full-frame maxima of 131/156 bits including stuffing. We conservatively
budget **135/160 bits per eight-byte frame**, allowing intermission and rounding.
These are successful-frame budgets; repeated errors have no finite completion
bound. [TI protocol reference, section 1.2.1](https://www.ti.com/lit/ug/spru074f/spru074f.pdf).

Standard frame service allowance is 0.270 ms; extended is 0.320 ms. All rates
below assume standard IDs and **100 other frames/s**, a deliberately explicit
background scenario rather than observed engine traffic.

`utilisation = (100 + frames_per_update × update_rate) × 135 / 500000`

| Rate | 2 frames/update | 4 frames/update | 6 frames/update |
| --- | --- | --- | --- |
| 100 Hz | 8.1% | 13.5% | 18.9% |
| 200 Hz | 13.5% | 24.3% | 35.1% |
| 500 Hz | 29.7% | 56.7% | 83.7% |
| 1000 Hz | 56.7% | 110.7% | 164.7% |

Above 100% cannot work even without errors. Low average occupancy is necessary,
not sufficient for bounded latency. Extended IDs multiply these cases by
160/135. Two frames represent a hypothetical compact command and status pair;
the actual fields must fit. Four/six represent larger messages or more frequent
feedback. A 32-byte state alone takes four full payloads, or six with a proposed
two-byte per-frame sequence/fragment allowance. Feedback is additional. Do not
assemble a control state from mixed epochs or treat CAN CRC as proof of freshness.

### Conditional delay examples, not a deadline proof

| Situation for one standard command frame | Bus allowance |
| --- | --- |
| Bus idle, command immediately eligible | 0.270 ms |
| One frame already started, command wins next arbitration | 0.540 ms |
| Same, plus at most one higher-priority frame ahead | 0.810 ms |

These assume no transmission errors and bounded local queue behaviour. More
higher-priority traffic invalidates the last row's assumption; a FIFO can also
hide a high-priority command behind old local traffic. Need actual identifiers,
periods, bursts, release jitter and driver-queue policy for response-time analysis.
Priority cannot pre-empt a frame already on the wire.
[TI arbitration explanation](https://www.ti.com/lit/an/sloa101b/sloa101b.pdf).

Total command age includes sensor/filter age, estimator release and execution,
message queue/arbitration, receiver scheduling and output timing. A 200 Hz
estimate can be nearly 5 ms old before communication starts. Re-sending it at
1 kHz does not produce five independent estimates. Retries, bus-off and stale
messages require a bounded local failure response rather than waiting forever.

**Recommendation:** central estimation/control is the first inert comparison
at 100–200 Hz, because the traffic arithmetic does not justify duplicating
sensors and an estimator by itself. Its cost is central workload and link-age
dependence. Prefer local sensing/control if actual dynamics or failure policy
require it. The hybrid can have a larger bus payload than sending commands.
No loop rate, third peer or control allocation is accepted by these scenarios.

Smallest next evidence: a proposed actuator's age/jitter requirement and inert
message inventory. Then exercise both ordinary and burst traffic with timestamped
command production/reception/output, stale-frame rejection and link loss. This
must include the existing engine peer and optional-rail failure; do not silently
change that peer's contract or test the system with live energetic loads.
