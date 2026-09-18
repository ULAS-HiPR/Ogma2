# Next review: investigated answers and decisions

18 September 2026. Desk investigation of the remaining meeting questions.
Recommendations below are for review; existing CAD and electrical contracts
remain unchanged. Bench results, canard requirements and purchased-part prices
are not invented. Start here, then finish chapters 6–8 together.

## Decisions to make in the room

| Question | Recommended starting answer | What could change it |
| --- | --- | --- |
| Flight/comms MCU | Keep flight H563; H563 LQFP64 preferred comms candidate, G474 the meaningful alternative | Cost quote, alternate-function map and application RAM budget |
| Third rail | Keep three for this revision; compare a merged non-flight rail only with separate comms power switching | Demonstrated assembly-area/cost saving and equivalent fault containment |
| Sensor power enables | Keep individual enables while retaining latch-off switches | Explicit choice to accept permanent loss of each tripped sensor for that flight |
| Comms evidence | Forward bounded diagnostic records to flight NOR; do not add flash yet | Requirement to recover comms data while flight MCU/internal link is dead |
| Remote actuation | Central computation, local PWM and stale-command response; trial 500 kbit/s arbitration / 2 Mbit/s data | Canard age/jitter limits, harness/peer qualification |
| Indicators | Preserve flight readiness + comms status + flight power; detailed USB readback | Installed visibility/operator tests; independent arm indication remains a separate requirement |
| GNSS | Treat aiding as unavailable outside documented receiver envelope | Qualified replacement/navigation evidence; antenna changes alone do not extend it |
| Energetic simplification | Require an explicit fault/consequence comparison before deleting mechanisms | Accepted ordinary-mission scope and inert verification; no new circuit approval here |

## 1. MCU comparison and pin rationale

Selection criteria for comms: USB device, two UARTs (flight/GNSS), radio SPI,
interrupt/control pins, watchdog, independent SWD and RAM for service/parsers.
Flight additionally needs its existing dense sensor/ADC/timer/CAN/NOR allocation.
Package fit and CPU timing are different tests.

| Candidate class | Published headline resources | Role fit / cost of choosing it |
| --- | --- | --- |
| H563 LQFP100, existing | M33, up to 250 MHz, 640 KB SRAM, up to 2 MB flash | Flight mapping exists; excessive comms pins but lowest redesign effort |
| H563 LQFP64 | Same H563 resource class; flash depends on ordering code | Comms mapping already desk-checked; UART moves PD8/9 → PC10/11; preferred low-risk package reduction |
| H503 | M33 up to 250 MHz, 32 KB main RAM, 128 KB flash, USB | Current 32 KiB service block alone consumes main RAM; needs streaming contract and smaller firmware; reject as default |
| G474RE LQFP64 | M4 up to 170 MHz, 512 KB flash, 128 KB SRAM (96 KB + 32 KB CCM), USB/FDCAN | Credible comms contender; 32 KiB service buffer leaves 64 KiB ordinary SRAM before other uses; CCM/DMA constraints and new target matter |
| U575RI class | M33 up to 160 MHz, 2 MB flash, 786 KB SRAM | Memory-rich alternative with low-power emphasis; no measured system saving yet; new target/pin map required |

Sources: [H563](https://www.st.com/en/microcontrollers-microprocessors/stm32h563-573.html),
[H563 package example](https://www.st.com/en/microcontrollers-microprocessors/stm32h563rg.html),
[H503](https://www.st.com/en/microcontrollers-microprocessors/stm32h503.html),
[G474RE](https://www.st.com/en/microcontrollers-microprocessors/stm32g474re.html),
[U575RI](https://www.st.com/en/microcontrollers-microprocessors/stm32u575ri.html).
U575 direct page retrieval failed; its official indexed summary supplied the
headline values. This is a shortlist, not five fully mapped replacements.

A smaller LQFP package reduces body area; confirm exact ordering-code dimensions
and courtyard before layout. Peripheral support circuitry prevents treating
body-area reduction as total board saving.
ST's inspected G474 price table returned no price. No comparable landed quotes
were obtained. Do not claim another family is cheaper or lower power from MHz
or marketing alone. Compare the same quantity, temperature grade and supplier;
measure comms workloads at the required clock. The recommendation is driven by
verified mapping and integration burden, not a fictitious price ranking.

### Every allocation has a job and a deletion alternative

Names below are logical CSV names; exact pad/AF and isolated physical-net aliases
are in the [pin audit](../mcu-pin-capacity-audit-2026-09-11.md) and linked CSVs.
Recommendations do not edit those allocations.

| Signals / function | When and why used | Fixed/deleted alternative and discriminating evidence |
| --- | --- | --- |
| ST/TDK/HG SPI + NCS | Independent sensor acquisition | Shared bus saves pins but shares stuck-line faults; inject a simulated timeout and check other acquisition continues |
| ST_DRDY, TDK_DRDY, HG_INT1 | Sample availability/timestamp alignment | Polling may suffice; compare timestamp jitter and missed samples at required rate |
| ST_EN, TDK_EN, HG_EN, BMP_EN, TE_EN | Start/restart individual latch-off protected branches | Tying on saves five outputs but forfeits firmware-controlled latch clearing/power cycle; keep unless that loss is accepted |
| BMP_SCL/SDA, TE_SCL/SDA | Separate pressure I2C buses | Shared bus needs addressing and stuck-bus analysis; Churro uses a different I2C4 pair |
| PYROx_HS_REQUEST/LS_SELECT, permits, latch controls | Existing output request/inhibit scheme | Simplification must follow output review, not pin pressure; no servo signals in this group |
| PYROx_CURRENT/CONTINUITY, PYRO_RAIL, ARM_SENSE | Electrical diagnostics and physical-state observation | Current/continuity are different observations; remove only after defining what the operator/record still needs |
| NOR_CLK/NCS/IO0–3 | Quad-data NOR transfers through OCTOSPI1 peripheral | Single-lane saves two data pins; existing throughput study is a feasibility budget, not measured writer service rate |
| NOR_EN, NOR_RESET_REQUEST | Clear powered-device faults/reset interface | Reset cannot clear every latch-off supply fault; power cycle interrupts recording; forbid unbounded repeated recovery |
| SERVO1/2_PWM, SERVO_POWER_EN, SERVO_RAIL | Two target position commands, separate supply permission and voltage evidence | SERVO3 removal recovers one pin after approval; tying enable on loses controllable supply isolation |
| CAN_RX/TX, CAN_POWER_EN, CAN_STB | Data, branch power recovery, powered standby | Standby preserves supply while disabling normal participation; power enable clears branch fault. Tie standby active only if its startup/quiet-state job is unnecessary |
| FLIGHT_TO_COMMS / COMMS_TO_FLIGHT | Bounded UART records/requests | Removing separate MCU changes the architecture, not just two pins |
| COMMS_EN / COMMS_RESET_REQUEST | Whole-branch power recovery versus processor-only reset | Keep both only with distinct recovery escalation; verify no comms failure resets flight |
| FOINSE_SCL/SDA / FOINSE_RETURN_EN | Local INA228 plus external monitoring domain | Not just a Churro feature: disabling AUX also removes standalone INA measurement |
| VEHICLE_VBAT ADC | Protected downstream battery voltage | INA bus voltage observes another node and loses supply with AUX; retain for independent downstream evidence |
| FLIGHT_3V3 ADC | Scaled rail observation | Same-rail VREF is ratiometric; use calibrated VREFINT for absolute value. Supervisor, not ADC, owns brownout validity |
| SUPERVISOR_WDI | Progress-qualified external watchdog heartbeat | Internal watchdog is cheaper but different clock/device failure boundary; compare forced scheduler stall and reset behavior |
| BRANCH_FAULT_N | Aggregate electrical fault notice | Does not locate fault; correlate enables/status, never infer failed branch solely from this input |
| BUZZER_DRIVE / STATUS_LED1 | Ground service / flight readiness | Keep minimum indication; buzzer silent in calibration/flight; avoid new flight RGB pins |
| HSE pair / LSE pair / PC13 | Active clock / retained RTC while supplied / LSE restriction | Internal clocks need timing analysis; comms LSE is DNP, so its quiet reservation need not be inherited blindly |
| SWDIO/SWCLK, NRST, BOOT0 | Recovery/debug/startup | Keep per-processor service access; service-only does not mean unnecessary |
| Supply/GND/VREF/VCAP pads | Device electrical operation | Not reclaimable GPIO; no external load on core-capacitor pins |
| Comms radio SPI, BUSY, DIO1, RESET, EN | Commands, completion/interrupts, device recovery | Polling IRQ is possible but needs bounded service; RXEN/TXEN reservations are obsolete in current module wiring |
| Comms GNSS UART, PPS, RESET, EN | Navigation records, precise time edge, reset/power recovery | UART receipt time is not PPS time; omit PPS only if reduced timing evidence is accepted |
| USB_DM/DP, VBUS_PRESENT, USB_CONFIG_OK, BAT_VALID | Service data, source/configuration state | Boot/source-control dependencies must remain explicit if changing chip or firmware |
| Comms STATUS_LED, BRANCH_FAULT_N, SWO | Local status, aggregate fault, optional trace | SWO can be omitted from production use; retain accessible debug option while debugging |

**PC13 resolved:** ES0565 Rev 8 §2.2.1 says PC13 transitions can disturb the
crystal LSE on LQFP/VFQFPN; avoid toggling it when LSE is used. The table's “N”
means limitation present/no workaround, not unaffected. Keep flight PC13 quiet.
Comms has no fitted LSE; that rationale alone does not reserve comms PC13.
[ST errata](https://www.st.com.cn/resource/en/errata_sheet/es0565-stm32h562xx563xx573xx-device-errata-stmicroelectronics.pdf).

DMA: flight reservation 11 = three SPI RX/TX pairs + two ADC + UART RX/TX +
NOR; comms 6 = two UART RX/TX pairs + radio SPI RX/TX. Count reservations per
MCU, then validate request routing, priorities and simultaneous service. A
minimal driver/buffer stress harness answers those questions; an empty build
or waiting for all flight firmware does not.

## 2. Power alternatives and input boundary

| Case | A: existing three LDO rails | B: flight + shared non-flight LDO |
| --- | --- | --- |
| Flight | Held flight rail, MCU/sensors | Same held flight rail |
| Comms MCU/GNSS/radio | Dedicated comms rail | Shared rail → separately controlled comms branch; GNSS/radio switches remain |
| NOR/CAN/AUX | Optional rail → individual protected branches | Shared rail → same individual protected branches |
| Sounder/continuity candidates | Direct optional rail / DNP feeds | Move to shared rail; continuity remains DNP |
| Comms reset/power cycle | Can leave optional services powered | Must switch comms subbranch, never whole shared rail |
| Logger branch short | Local limiter intended to clear first | Same intended local action; upstream sharing still needs selectivity |
| Comms LDO short | Comms branch fault; optional domain separate | Shared-LDO fault removes comms, recording, CAN and monitoring together |
| Parts removed/added | Baseline | One LDO/support set removed; comms branch switch/limit still needed; redesign enable/power budget |
| Heat at same 4→3.3 V and same total load | (4−3.3) × 0.6 A = 0.42 W | Also 0.42 W before differing quiescent/switch losses |

**Recommendation:** keep A for this revision unless B's actual layout/BOM saving
is valuable enough to accept the larger common failure domain. This is not a
claim that two rails cannot work. B does not inherently save the 0.42 W conversion
loss. C, placing NOR/CAN on held flight, additionally spends hold-up energy and
couples their current transients to sensing; it is the least attractive deletion.
Moving CAN actuation onto the vehicle makes loss of the “optional” rail a mission
failure for that function. Rename it “recording/CAN/monitoring rail” in discussion.

**Proposed core source requirement:** 2S source only; 8.4 V maximum normal fully
charged value; do not connect 15 V. Existing nominal thresholds are ~6.63 V start,
6.20 V stop, 8.99 V OVP. Those are circuit thresholds, not a guaranteed operating
range. Suggested acceptance tests cover startup at 6.8 V and operation down to
6.4 V under declared load, but resistor/IC tolerances and load sag must confirm
those margins before making them a contract. Higher-voltage vehicles require
Churro adaptation or a separate approved supply; current Churro must not be
assumed to contain a newly proposed step-down converter.

Hold-up remains ~0.98 ms at 800 µF effective, 204 mA and 0.25 V usable fall.
Use t=CΔV/I and include ESR step, leakage, temperature, LDO dropout and supervisor
threshold. No capacitor part or hold-up measurement is available; changing that
status requires hardware. A loose battery lasting milliseconds is not covered.

## 3. Comms evidence, GNSS and radio

**Recommend bounded forwarding to flight NOR first.** Proposed record: source
sequence, comms monotonic time, corresponding flight time/offset uncertainty,
reset epoch, GNSS validity/solution age, packet direction/sequence/RSSI/SNR,
radio errors, UART drops and USB-session/configuration events. Log state changes
plus a capped diagnostic stream; never let it block essential acquisition.

| Failure | Forward into flight NOR | Independent comms flash |
| --- | --- | --- |
| Radio link lost | Evidence still recorded over internal UART | Also survives link loss |
| Comms resets | Flight can log reset/gap; unforwarded tail lost | Committed local records survive; uncommitted tail still lost |
| Flight MCU/UART fails | New comms evidence not retained there | Can retain it while comms power remains |
| Whole board loses power | Committed NOR survives; tail may not | Same principle; not an independent power source |
| Readout/firmware burden | Existing recorder plus record types | Another driver, power/pins, format and service path |

Illustrative cap: 1 KiB/s for 30 minutes adds 1,843,200 B (1.76 MiB).
The previous mission ledger had 20,738,816 B spare beyond reserve: this cap
would leave 18,895,616 B, before any new encoding overhead. At 2 Mbaud 8N1,
1 KiB/s uses 0.512% of ideal UART payload capacity. Add a bounded queue and
explicit dropped-record counter. These are proposed caps, not observed traffic.

RSSI is measured at the receiver. Uplink RSSI belongs to the vehicle receiver;
downlink RSSI belongs to the ground receiver and must be returned explicitly if
wanted onboard. Different transmitter powers, antennas, noise and calibration
mean values need not match. Store direction, receiver identity and age; RSSI
alone is not delivery probability. [Semtech explanation](https://www.semtech.com/design-support/faq/P20).

MAX-M10S data sheet R08, table 1: dynamics ≤4 g, altitude 80,000 m, velocity
500 m/s, with its stated airborne platform assumption. All are limits to respect;
remembered “AND/OR” export restrictions do not waive a manufacturer operating
limit. This does not establish exact shutdown behavior outside them. Boost may
exceed dynamics/speed before reaching the altitude limit. Treat such GNSS aiding
as unqualified and provide validity/age handling; recovery/reacquisition requires
flight-profile evidence. External antenna fixes reception geometry, not these
limits. [u-blox data sheet](https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf).

## 4. CAN FD and servo investigation

**Proposed evaluation configuration:** 11-bit identifiers, 500 kbit/s arbitration,
2 Mbit/s data, bit-rate switching; one linear trunk, short drops, two end
terminations. All active peers must accept FD frames; Classical-only nodes
cannot simply remain on a bus carrying FD traffic. Existing two-node contract
must be reconciled with Fajita/actuator owners before changing it.

Burrito H563 has FDCAN; fitted TCAN3413 is specified up to 8 Mbit/s. That is
component capability, not approval for an 8 Mbit/s harness. Start at 2 Mbit/s
and measure at the longest installed harness. [TI transceiver](https://www.ti.com/product/TCAN3413),
[Bosch FD overview](https://www.bosch-semiconductors.com/products/ip-modules/can-protocols/can-fd/).

Proposed complete traffic scenario for ONE remote actuator node:

| Message | Bytes | Rate | Contents / priority |
| --- | ---: | ---: | --- |
| Actuator command | 16 | 200 Hz | Sequence, execution/deadline time, two setpoints, mode/validity; high |
| Actuator status | 16 | 200 Hz | Echoed command sequence, local age, measured status/faults; below command |
| Health | 8 | 20 frames/s aggregate | Boot/reset epoch, health; lower |
| Fajita/background allocation | 8 | 100 frames/s aggregate | Reserved scenario, not agreed propulsion contract; lower |
| Bulk service | 64 | 0 during active control | Ground-only until separately budgeted |

Planning airtime envelope (not a bit-exact standard calculator):
T(N)=80/500000 + 1.25×(8N+40)/2000000 seconds.
This deliberately pads nominal phase, data overhead and stuffing; it excludes
error retries. It gives 0.225/0.265/0.345/0.505 ms for 8/16/32/64 bytes.
The scenario uses 13.3% of bus time. At 500 Hz command+status it is 29.2%;
at 1 kHz, 55.7%. These figures do not select a loop rate.

With the command highest scheduled priority, one already-transmitting 64-byte
frame plus the command costs about 0.77 ms in this envelope, before software
queueing, errors or other higher-priority traffic. Bound queue depth to latest
valid command; never drain old position commands after a stall. A proposed
software budget of 0.25 ms sender + 0.25 ms receiver gives 1.27 ms before PWM
phase/mechanics. Unsynchronised 50 Hz PWM may add nearly 20 ms; 200 Hz nearly
5 ms. Sensor filtering and estimator age are additional. Thus PWM/mechanism
requirements can dominate even when the bus is mostly idle.

No finite error-case delivery deadline follows from this model: define local
expiry response when delivery fails. Neutral is not universally safe. The canards
team must provide: mechanism/servo part, supply, travel/load, update frequency,
maximum sample-to-motion age and jitter, feedback need, and permitted behavior
on stale command/reset for each phase. This is a ready requirements request,
not a message sent or an answer fabricated.

Servo supply must sustain declared simultaneous stall demand for its required
duration without rail collapse or inappropriate trip. For two devices each
stalling at I_s, start with 2I_s plus interface load, then account for cable and
connector loss/thermal limits. A transient capacitor obeys C≥I_deficit·t/ΔV:
a 2 A deficit for 0.5 s with 0.5 V allowed sag needs 2 F before ESR. Ordinary
bulk decoupling cannot substitute for that supply requirement.

The fitted TXU0304 signal boundary supports partial power-down and disables
outputs when either supply is below 100 mV/disconnected under specified
conditions. This supports keeping it when flight is powered and servo power is
off; it is not a motor regulator or a guarantee across the whole ramp region.
Check powered-off leakage and boot/ramp waveforms on the actual assembly.
[TI TXU0304 data sheet](https://www.ti.com/lit/ds/symlink/txu0304.pdf).

## 5. Indicators and operator sequence

Recommend existing simple LEDs plus USB detail first. “Hardware” means it follows
an electrical condition without firmware; “software” can be stale/frozen.

| Question | Present/proposed driver and connection | Reset/off behavior and proof |
| --- | --- | --- |
| Flight rail exists | Present D9301 via R9301 from FLIGHT_3V3 to GND | Lit only indicates rail energy; not correct voltage/healthy execution |
| Flight ready / not ready | Present PD7 STATUS_LED1; D9001 and U9101 complementary D9101 path | Firmware state; pull-down/inverter is intended not-ready default while powered; verify boot. Frozen output can lie |
| Comms progress | Present PB4 STATUS_LED through R9201/D9201 | Firmware-controlled; heartbeat freshness belongs in readback, not steady green |
| Comms rail exists | Proposed resistor/LED on COMMS_3V3 | Independent of comms code; add only if installation visibility justifies load/area |
| Physical arm | Separate qualified electrical sense/indication, assembly unresolved | Never substitute software LED; no exact new wire is claimed selected |
| Continuity by channel | Existing sense paths are unfinished/DNP; proposed USB channel state | Unknown/unavailable must not display pass; no direct LED injection path selected |
| Test vs flight | Proposed explicit USB state plus distinctive existing LED pattern | Boot defaults unverified/not-ready; reset cannot silently claim flight-ready |
| Identity/build/config updated | USB on comms, request/readback from both processors | Compare returned running build/config checksum after reboot, not transport success |
| Sensor calibration/validity | Flight diagnostics forwarded over internal UART to USB | Include sample age, errors and calibration identity; timeout becomes unknown |
| Storage space/commits/gaps | Flight recorder diagnostics to USB | Ready requires writable prepared space; persist gap/reset evidence where possible |
| CAN activity vs peer health | Flight CAN counters/last valid response → UART → USB; optional comms-driven LED | Traffic alone never means correct peer. Include age, sequence loss, bus-off/error counters |
| GNSS/radio | Comms diagnostics → USB and bounded log | Fix age, out-of-envelope status, packet direction/loss and radio mode separately |
| Source/voltage/current | ADC and INA diagnostics → USB | AUX loss removes INA; never keep displaying stale current as live |
| Reset history/watchdog | Per-MCU cause/epoch/progress → USB | Whole power loss may erase volatile evidence; mark that limitation |
| Ground audible feedback | Present PD6 transistor/piezo path | Silent before calibration/flight; not sole indication in enclosed bay |

No RGB driver is required by this allocation. If richer local display is chosen,
use comms spare GPIO or an I2C driver there, with a distinct stale-flight state;
do not consume three flight GPIOs. RGB adds readability options, not independent
health evidence. The matrix separates actual nets from proposed circuitry.

Operator sequence: USB-only identity/readback → physically disarmed inspection
and diagnostics → controlled battery startup → declared configuration/calibration
and peer freshness checks → explicit mode/readiness verification → separately
verified physical arm procedure. After an update, reboot and read back both
running versions/configurations. After reset, show unknown/not-ready until the
appropriate state validation completes. The final arm assembly is still open;
this sequence does not select or bypass it.

## 6. Energetic complexity and reset: decision analysis

This investigation does not design or modify an ignition circuit. Compare the
ordinary-mission requirement against failure outcomes, then have the responsible
team approve the circuit. Current DNP links remain.

| Mechanism challenged | Failure it attempts to address | Simpler alternative / limitation |
| --- | --- | --- |
| Independent pulse termination | Request remains asserted after software stalls | Software-only termination loses that independent bound; whether required depends on load/fault thermal consequences, not nominal burnout alone |
| Current diagnostics | Whether an electrical response occurred | Aggregate battery trace is cheaper but cannot reliably identify simultaneous channels or prove mechanical outcome |
| Continuity diagnostic | Missing connection before use | Manual preflight verification reduces circuitry but changes operator workflow; cannot be assumed equivalent |
| Separate switching conditions | Single control/wiring failure | Fewer elements reduce parts but alter fault exposure; no generic “more parts is safer” conclusion |
| Reset staging inhibit | Unknown prior event/state after reset | Automatic resume risks repeating an event; a retained flag alone may be stale/incomplete |

Recommendation: first decide which evidence is required in ordinary operation,
then compare mechanisms. Do not add retry state machinery absent a requirement.
Do not approve pulse-circuit deletion solely from “the load normally burns out.”
The open evidence is concrete: declared load/fault envelope and inert behavior,
not another terminology paragraph.

Reset examples: on a disarmed bench boot, establish a new session through the
explicit procedure. After a known-phase flight reset, recover measurements/time
and apply the already-reviewed phase-specific recovery policy; do not calibrate
launch height again. With ambiguous state/time, primary continuation is unavailable;
independent recovery allocation applies. A reset never clears the preserved
sustainer veto. A comms-only reset does not create a new flight or reset flight.
These explain the existing contract; they do not newly approve flight behavior.

## 7. Smallest tests and external inputs still required

| Test/input | Stimulus and observations | Pass condition to establish |
| --- | --- | --- |
| Logic power/reset | Bench current-limited source; MCU-only reset and bounded supply interruption; outputs inert/disconnected | Reset cause/epoch recorded; no boot recalibration/event replay; safe defaults; actual hold-up measured |
| Branch selectivity | Controlled electronic-load fault within component/fixture limits; monitor flight rail/reset | Non-flight fault does not violate essential rail or its defined reset behavior; determine actual trip order |
| Servo partial power | Flight on/servo off and reverse sequence, inert interface fixture | No unintended PWM or unacceptable back-power; inspect ramp regions, not only zero volts |
| Actuator envelope | Selected servo under declared load/stall duration, current-limited mechanical fixture | Required motion, voltage/thermal margin and defined overload recovery; parts/load not yet provided |
| CAN timing | Actual FD peers, longest harness, full traffic, captured timestamps | Agreed maximum age/jitter and local expiry behavior, including errors/restarts |
| Firmware resources | Concurrent USB transfer, GNSS/radio parsing, UART logging and error load | Bounded buffers/queues, stack headroom, no essential deadline misses |
| Navigation | Declared flight envelope compared with receiver limits and recorded solution validity | No unsupported aiding claim; reacquisition/age handled |
| Operator UI | Enclosed bay, USB-only, reset/stale peer and sensor-fault cases | Users distinguish power, readiness, arm, continuity and unknown without interpretation |

Still external: actual actuator requirements; peer FD support; accepted owners;
physical arm assembly; component quotes and built-board measurements. These
cannot be closed by desk research. Chapters 6–8 still need human review; this
investigation does not mark them accepted.
