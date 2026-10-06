# EX-04: MCU resource allocation and timing evidence

Date: 2026-09-06
Status: accepted selection strategy; initial source-backed resource reservation.
No production MCU selected. No target build, measured timing or retention result.

## Decision

Seán accepted the EX-04 recommendations on 6 September:

- Start with STM32H563; compare H573 directly. Extra cryptography alone does
  not establish better flight reliability.
- Use **STM32H563VIT6, LQFP100**, as the first exact allocation candidate.
- Start both roles in the same family. Consider a smaller communications part
  only when its area, power or cost saving justifies another maintained target.
- Allocate the simultaneous system, including debug, clocks, interrupts, DMA,
  analogue monitoring and output controls. Count usable protected memory.
- Put critical state, stacks and restart records in verified ECC regions with
  known reset behaviour. Reject incorrect placement at build time.
- Keep an initial **30% scheduling and critical-memory reserve**. This is an
  engineering allowance, not a reliability probability or deadline proof.
- Choose clock speed from measured workload and power. Keep development
  provisioning reversible; record silicon, option bytes, boot state and errata.

The two processors retain different jobs. They are not redundant. Foinse has
no MCU. The external preregulator/low-noise-LDO decision is unchanged.

## Exact-part comparison

| Property | STM32H563VIT6 | STM32H573VIT6 | Consequence |
| --- | --- | --- | --- |
| Package | LQFP100 | LQFP100 | Inspectable leads; physical pin/footprint audit still required |
| Core / maximum clock | Cortex-M33 / 250 MHz | Cortex-M33 / 250 MHz | No demonstrated compute advantage for this workload |
| Flash / raw main SRAM | 2 MiB / 640 KiB | 2 MiB / 640 KiB | Raw capacity is not the protected allocation budget |
| Additional H573 facilities | Comparison baseline | AES, PKA, external-memory decryption, ST-iROT | Select only for a named requirement; not presumed fault tolerance |
| Current disposition | First allocation candidate | Direct comparator | Neither is flight-qualified by this review |

Sources: [H563 datasheet, DS14258 Rev 6, May 2025](https://www.st.com/resource/en/datasheet/stm32h563vi.pdf),
[H573 datasheet, DS14121 Rev 5, May 2025](https://www.st.com/resource/en/datasheet/stm32h573vi.pdf),
and [ST family comparison](https://www.st.com/en/microcontrollers-microprocessors/stm32h563-573.html).
H563 also has security facilities; the table does not mean it has none.
H573 has not received an independent complete pin/boot equivalence audit here.
Do not treat it as a drop-in substitution.

For H563VIT6 use the **non-SMPS** package drawing, Figure 8. ST identifies
the SMPS variants with the trailing Q commercial-code distinction in Table 14.
Internal core regulation and the board's external logic-supply cascade are
different decisions. Audit VCAP, supplies, grounds, reference, backup supply
and decoupling against the exact variant before importing a symbol.

Price, stock, fitted silicon revision and measured consumption are unknown.
No purchase or production availability claim follows from this comparison.

## Simultaneous port reservation

This is a first allocation for **two H563VIT6 devices**, not a released netlist.
Port names and alternate functions below were checked against DS14258 Figure 8
and Tables 15–16. Physical package numbers and symbol/footprint agreement still
need an independent audit. PDF download/render attempts failed; readable
manufacturer tables were available, but no visual footprint inspection occurred.

Bus choices and GPIO counts are provisional implementation proposals. Sensor,
NOR, protection and output circuits are not selected. A resource reservation
does not silently select those circuits or assert that their complete needs fit.

### Flight MCU

| Consumer | Reserved port pins | Peripheral / mode |
| --- | --- | --- |
| Primary IMU | PA5, PA6, PA7; PA4 | SPI1 SCK/MISO/MOSI AF5; GPIO chip select |
| Separate high-g sensor | PB13, PB14, PB15; PB12 | SPI2 SCK/MISO/MOSI AF5; GPIO chip select |
| Soldered bulk NOR | PC10, PC11, PC12; PD2 | SPI3 SCK/MISO/MOSI AF6; GPIO chip select |
| Pressure sensor | PB6, PB7 | I2C1 SCL/SDA AF4; revisit for selected sensor |
| Communications link | PD8, PD9 | USART3 TX/RX AF7 |
| Vehicle CAN | PD0, PD1 | FDCAN1 RX/TX AF9; external transceiver required |
| Two servo signals | PC6, PC7 | TIM3 CH1/CH2 AF2; shared period |
| Independent SWD | PA13, PA14 | SWDIO/SWCLK AF0; dedicated NRST access |
| External clocks | PH0, PH1; PC14, PC15 | HSE and LSE reservation; circuits not selected |
| IMU / high-g data-ready | PE0, PE2 | GPIO interrupt inputs; distinct line numbers |
| Three output-channel control pairs | PE7, PE8, PE9, PE10, PE11, PE12 | Six provisional GPIO reservations; topology remains EX-07 |
| Optional auxiliary-monitor bus | PD12, PD13 | I2C4 SCL/SDA AF4; use only if the Foinse interface requires it |
| Comms, logger, auxiliary branch enables | PD3, PD4, PD5 | GPIO reservations; hardware defaults independent of software |
| Supervisor heartbeat | PD6 | GPIO reservation; progress-qualified firmware action |

Two servo channels on TIM3 share the timer period. This fits the present
ordinary RC-servo direction only if both selected actuators accept that period.
Different periods require a different timer allocation. No servo safety state
is established by selecting a timer.

There are **40 distinct reserved port pins** above, with no duplicate within
this table. GPIO reservations for output pairs do not select high/low-side
topology, pulse duration, arming circuitry or energetic test authority.

Unallocated obligations remain explicit:

- ADC inputs for battery/rails, current and channel diagnostics. Candidate
  analogue pads must be checked individually against Table 14, source impedance,
  acquisition time, protection and the eventual circuit. No ADC-channel count
  or simultaneous analogue fit is claimed yet.
- Physical arm sensing, branch fault inputs, CAN standby, any additional
  hardware inhibits, status indicators and buzzer drive. Allocate actual
  consumers rather than declaring all remaining GPIO spare.
- Exact sensor reset/interrupt needs, bus electrical limits and unpowered-device
  behaviour. Separate SPI peripherals do not alone establish fault containment.
- DMA channels, request routing, arbitration, EXTI routing, priorities and
  interrupt blocking. Reserve SPI RX/TX and UART RX/TX work in the resource
  budget; assign channels only with the target configuration in hand.
- Dedicated NRST, BOOT0, all power/reference pins and debug access on the
  physical symbol. These are not included in the port-pin count.

Keep PC13 free of ordinary switching activity while evaluating the LSE erratum.
Do not use the flight-side USB pins as evidence of a second normal USB port;
the accepted user interface remains on communications.

### Communications MCU

| Consumer | Reserved port pins | Peripheral / mode |
| --- | --- | --- |
| Flight link | PD8, PD9 | USART3 TX/RX AF7 |
| GNSS serial | PA9, PA10 | USART1 TX/RX AF7 |
| GNSS PPS | PA0 | TIM2 CH1 capture AF1; not proof of a fix |
| LoRa interface | PA5, PA6, PA7; PA4 | SPI1 SCK/MISO/MOSI AF5; GPIO chip select |
| Radio reset, busy, interrupt | PC0, PC1, PC2 | Provisional GPIO reservations; selected radio decides needs |
| Host USB | PA11, PA12 | USB DM/DP AF10; supply/ESD/attachment circuit remains open |
| Independent SWD | PA13, PA14 | SWDIO/SWCLK AF0; dedicated NRST access |
| External clocks | PH0, PH1; PC14, PC15 | HSE and LSE reservation; justify each fitted oscillator |

This table reserves **20 distinct port pins** without duplicate assignment.
GNSS power/reset, host attachment sensing, radio front-end control and status
may add pins. Check the selected devices before considering a smaller package.
PPS capture and USB clock accuracy need real clock configurations. No GNSS
altitude or dynamics capability follows from this MCU allocation.

**Fit verdict: incomplete.** The named digital buses can be reserved together
without a port conflict in this draft. The whole-board resource proof is still
open, particularly analogue/output circuits, DMA, physical pin audit and timing.

## Memory allocation

The protected-main-memory accounting is the same starting point for H563/H573:

| Bank | Usable capacity in this configuration | Provisional owner |
| --- | --- | --- |
| SRAM1 | 256 KiB, not ECC-protected | Disposable bulk buffers; never the sole critical-state copy |
| SRAM2 | 64 KiB, ECC | Small critical state and stacks, subject to reset/init proof |
| SRAM3 | 256 KiB with ECC enabled | Estimator state and critical acquisition/working buffers |
| Backup SRAM | 4 KiB, separate domain | Checkpoint candidate only after supply/reset/initialisation proof |

SRAM3's raw 320 KiB includes 64 KiB consumed by ECC storage when enabled.
Protected main capacity is therefore **320 KiB**, excluding backup SRAM.
At 30% reserve the total spending ceiling is **224 KiB**, not a measured use.
Apply margin per bank as well: for initial integer-KiB budgets, cap SRAM2 at
44 KiB and SRAM3 at 179 KiB. Their combined 223 KiB cap conservatively rounds
down. Alignment, stacks, interrupt nesting and DMA ownership count as use.
Free space in one bank does not cure an overflow in another.

Source: [ST H5 RAMCFG training](https://www.st.com/content/ccc/resource/training/technical/product_training/group1/9d/5c/38/7e/32/71/41/e0/STM32H5-RAM-configuration-RAMCFG/files/stm32h5-ram-configuration-ramcfg.pdf/jcr:content/translations/en.stm32h5-ram-configuration-ramcfg.pdf).
The [reliability review](reliability-design-review.md) preserves the ST source
conflict on ECC word geometry and the limits of documented injection methods.
Do not copy the older safety-manual word width into a test without resolving
the exact part and revision.

No linker addresses or final bank assignment are released here. The next target
build must record the memory map, ECC options, startup clearing and retained
sections; reject misplaced critical sections and demonstrate that rejection.
CRC detects some corrupt content but does not replace ECC, freshness or correct
ownership. Corrected reads require a verified safe writeback/scrub strategy.

## Timing and provisioning evidence still needed

Select candidate clocks only after EX-05 supplies acquisition and latency
requirements. At each tested clock, record each task's activation bound, period,
deadline, observed maximum duration, justified execution bound, blocking and
overrun response. Include ISR work, DMA/bus contention, diagnostics and flash
stalls. A preliminary total utilisation below 70% is necessary for the chosen
reserve, but not sufficient for schedulability. Prove individual response
deadlines under the actual scheduler; average CPU use is not that proof.

Measure power in the same configurations. No duration, energy, stack-use or
worst-case execution-time result exists yet. EX-03's host checkpoint model
establishes none of these properties.

Start the errata checklist from [ES0565 Rev 8, January 2026](https://www.st.com.cn/resource/en/errata_sheet/es0565-stm32h562xx563xx573xx-device-errata-stmicroelectronics.pdf):

- §2.2.1: PC13 transitions can disturb LSE; check layout and use.
- §2.2.14: backup-domain reset can erase SRAM2; test the actual reset path.
- §2.2.33: first flash erase/program after power-on or Standby can make flash
  inaccessible for approximately 120 microseconds; account for the documented
  conditions and workaround rather than assuming a second bank solves it.
- §2.2.39: inspect conditional ST-iROT/backup-domain behaviour if applicable.

This is an initial applicability list, not a complete errata audit. Record
fitted device/revision IDs, supply mode, option-byte readback, boot/security
state, compiler/linker configuration, cache/MPU choices and debugger state for
every target run. Do not close lifecycle/security states irreversibly during
development. Independently recover and program each MCU with the other in reset.

## Next executable checkpoint

1. Review EX-05's measurement defaults, then fill required rates and validity
   limits. EX-07 supplies the remaining circuit-level output resources.
2. Complete the exact symbol/pin, ADC and DMA allocation with selected devices;
   run an independent audit before treating this map as G1 evidence.
3. Build the smallest non-actuating target spike described by
   [MCU-01](reliability-execution-plan.md#experiment-mcu-01-memory-diagnostics-and-timing).
   Prove placement rejection, reset/clock/retention and deadline behaviour on an
   identified assembly. Document unsupported tests explicitly.

The accepted strategy can guide work now. EX-04 remains open until the actual
candidate meets its closure criteria. No PCB order, physical fault test or
flight release is authorised by this document.
