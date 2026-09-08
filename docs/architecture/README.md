# Ogma 2 architecture — reading pack

8 September 2026. Expanded research-backed design review. Engineering draft,
not a new component-selection exercise or qualification claim.

Start with the overview. Read the remaining sections independently, then compare
notes together. Flag a specific circuit or failure case, not merely whether the
board feels complicated. Existing choices stand unless the review identifies
a reason to change them.

| Order | Section | Question answered |
| --- | --- | --- |
| 0 | [Overview](00-overview.md) | What is this computer, and where does authority stop? |
| 1 | [MCUs and execution](01-mcus.md) | Why two processors, and what survives one failing? |
| 2 | [Croí power](02-power.md) | Where does energy come from, and what isolates a fault? |
| 3 | [Energetic outputs](03-energetic-outputs.md) | What physically prevents and bounds an output? |
| 4 | [Servo outputs](04-servos.md) | How do three timer signals become three powered actuators? |
| 5 | [Service, status and time](05-service-status-time.md) | How do we operate, debug and understand the board? |
| 6 | [GNSS and radio](06-gnss-radio.md) | How do antennas work with the real airframe? |
| 7 | [Sensors and local recording](07-sensors-logging.md) | Which measurements remain useful, and where is evidence kept? |
| 8 | [Foinse and vehicle boundary](08-foinse-can.md) | What does the power board own, and what stays with propulsion? |

Each chapter begins with the circuit, then explains the alternatives, selection
reasoning, calculations, source limitations and next evidence. The pack can be
read without local CAD or sibling research directories. Component references
identify the inspected draft. This is the substantive joint-review material;
[current-system](../../current-system.md) remains the short orientation.

## Research trail

The 6 September architecture study and 7 September follow-ups contain more
than the earlier compressed chapters showed. Their useful reasoning is now
included here, reconciled with later accepted changes rather than pasted as
another contradictory baseline.

| Read in this pack | Research recovered | Detailed record already on GitHub |
| --- | --- | --- |
| MCUs | H563/H573, lockstep and radiation-oriented alternatives; exact package, ECC banks, timing/resource budgets | [Hardening study](../karman-line-mission-hardening-report.md#mcu-selection), [execution plan](../reliability-execution-plan.md), [handoff](../firmware-handoff-2026-09-07.md) |
| Power | Buck/LDO versus alternatives, dropout/startup, hold-up, branch faults and energy arithmetic | [Power contract](../../interfaces/power-contract.md), [Rev 1 review](../rev1-external-review-lessons.md) |
| Outputs / servos | Independent duration/permission boundaries, timer versus expander, raw versus regulated actuator supply | [Fault study](../karman-line-mission-hardening-report.md#energetic-outputs-and-recovery), [third-servo revision](../connector-servo-readiness-revision-2026-09-07.md) |
| Service / time | Hall versus shunt/IMON, indication choices, drift versus reset continuity | [Sensing/status/time analysis](../sensing-indication-time-review-2026-09-07.md) |
| GNSS / radio | Four radio modules, GNSS alternatives, airtime/sensitivity, revised antenna installation | [Options review](../avionics-options-review-2026-09-07.md), [radio decision](../radio-change-2026-09-07.md), [installation delta](../installation-change-record-2026-09-08.md) |
| Sensors / recording | Each sensor's role/range/timing, dissimilarity limits, coast sensing, NOR capacity and commit-throughput trade | [Configuration review](../sensor-configuration-review-2026-09-07.md), [handoff](../firmware-handoff-2026-09-07.md) |
| Foinse / vehicle | Pack count/energy, charging, conditional 24 V options, interboard geometry and return faults | [Power contract](../../interfaces/power-contract.md), [vehicle boundary](../../interfaces/ogma-foinse-propulsion-boundary.md) |

Manufacturer links appear beside the claims they support. They were the sources
used in the dated research, not a claim of newly verified price, stock or
document revision. The original sensor work checked the selected suite and
meaningful architectural alternatives; it did not exhaustively benchmark every
available sensor. Unknown comparisons stay unknown.

Older records retain their contemporary recommendations. Read their later
amendments and the current chapters before treating SAM, E22, two servos or
coupon-first language as present direction. Hardware results, desk calculations
and engineering judgments are distinct evidence classes throughout this pack.

## Current checkpoint and review

- Preserve the accepted architecture and both MCU allocations.
- External GNSS and power-switch contacts are installed in the checked draft;
  physical energetic arming stays separate.
- Circuit sheets now explain purpose and connections with visible local wiring.
- Symbol-to-footprint identity and pad nets pass native checks. Open both editors
  through the same project; GUI cross-selection itself was not exercised.
- Keep automatic PCB placement/routing frozen. Seán finishes layout; Anav writes
  firmware. Neither must reverse-engineer a different silent model revision.

Exact GNSS/switch selection, installed checks and open tests are in the
[implementation record](../installation-change-record-2026-09-08.md).
The [current system](../../current-system.md) carries the controlling
summary; the [interfaces](../../interfaces/README.md) retain detailed boundaries.

## Reading is not requalification

The first full engineering PCBA remains the functional-block test article.
No separate mini-PCB requirement has returned. Pin, footprint, rating, physical
inhibit and assembly review still precede ordering. No flight, live energetic
test or automatic acceptance follows from readable drawings.
