# Ogma 2 architecture — reading pack

8 September 2026. Current design explained for joint review. Engineering draft,
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

Each page gives the circuit, its purpose, cost, credible alternative and the
next evidence required. The pack can be read without local CAD or sibling
research directories. Component references identify the inspected live draft.

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
