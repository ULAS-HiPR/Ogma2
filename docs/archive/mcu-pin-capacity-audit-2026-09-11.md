# MCU pin-capacity audit and package comparison

**Current recommendation:** [processor review](../architecture/01-mcus.md).
This dated audit describes the preserved allocation. The current proposal adds
a complete 64-pad comms map and streamed service buffering; the whole-32-KiB
buffer discussion below is historical, not a present H503 exclusion.

Date: 11 September 2026. Status: read-only desk investigation of the preserved
draft. No processor choice, pin remap, schematic edit or firmware change approved.

## Evidence and method

- Read the controlled [flight CSV](../../hardware/croi2/libraries/inputs/flight-pinout.csv)
  and [comms CSV](../../hardware/croi2/libraries/inputs/comms-pinout.csv): 100 physical
  pad records each. These carry individual pad numbers, logical net names and AFs.
- Exported a fresh KiCad XML netlist from the current Croí schematic to temporary
  storage, without saving or editing CAD.
- Checked all 200 pad records against that export, using the documented mapping
  from CSV logical names to physical boundary nets. Every comparison passed.
- Classified every pad exactly once. All category totals equal 100 per MCU.
- Inspected single-node nets: comms RXEN and TXEN contain only their MCU pins.
  The firmware handoff already marks these as unused after the radio revision.
- Used ST DS14258 Rev 6, Figure 5 and alternate-function tables, for the proposed
  H563 LQFP64 port mapping. This is a desk mapping, not a new native CAD audit.

The read-only [audit utility](../../tools/audit_mcu_pins.py) prints the grouped
allocation and fails on a CSV/netlist mismatch or unclassified pad. Run it with
a fresh KiCad XML netlist argument. The machine's default Python had a local
Expat library-loading fault; the system Python completed the audit. No runtime
installation or system repair was performed.

Pin connectivity is not proof of appropriate voltage, AF configuration, DMA
routing, interrupt behaviour, timing or safe operation. Existing ERC/DRC findings
were not resolved or represented as clean by this audit.

## Verdict

Flight: 20 dedicated support pads, 79 connected port pads, one deliberately
quiet port pad. The 79 comprise 73 application signals, four oscillator pins
and two SWD pins. There is no unassigned ordinary port pin in this allocation.

Comms: 20 dedicated support pads, 27 connected port pads, two legacy radio
reservations, two unfitted LSE reservations, one quiet reservation and 48 other
unused port pads. The 27 comprise 22 application signals, two HSE pins and three
debug/trace pins. A named signal is not necessarily an externally connected one.

Do not call both MCUs “at capacity.” Flight's **pin allocation** is full; CPU,
memory and scheduling occupancy have not been measured for either MCU.

## Flight: complete grouped allocation

| Job | Pads | Port names / dedicated pad functions |
| --- | ---: | --- |
| Recording | 8 | PE2, PB2, PE11, PD11, PD12, PD13, PA11, PD3 |
| Sensors | 24 | PE3, PE4, PE5, PE6, PA4, PA5, PA6, PA7, PB10, PB12, PB13, PB14, PB15, PA8, PA9, PA10, PC10, PC11, PC12, PD2, PB3, PB6, PB7, PE0 |
| Supply/reference/core caps/reset/boot | 20 | VBAT, VSS, VDD, NRST, VSSA, VREF-, VREF+, VDDA, VSS, VDD, VCAP, VSS, VDD, VDDUSB, VSS, VDD, BOOT0, VCAP, VSS, VDD |
| Quiet reserve | 1 | PC13 |
| Clocks | 4 | PC14, PC15, PH0, PH1 |
| Energetic control and diagnostics | 19 | PC0, PC1, PC2, PC3, PA2, PC4, PC5, PE7, PE8, PE9, PE10, PE12, PE13, PE14, PE15, PD14, PD15, PC8, PC9 |
| Battery and logic voltage | 2 | PA0, PA1 |
| Servo control and diagnostics | 5 | PA3, PB0, PD10, PC6, PC7 |
| CAN | 4 | PB1, PD0, PD1, PB5 |
| Comms link and control | 4 | PD8, PD9, PA12, PB4 |
| Debug | 2 | PA13, PA14 |
| Auxiliary monitoring | 3 | PA15, PB8, PB9 |
| Health and indication | 4 | PD4, PD5, PD6, PD7 |

## Comms: complete grouped allocation

| Job | Pads | Port names / dedicated pad functions |
| --- | ---: | --- |
| Unused | 48 | PE2, PE3, PE4, PE5, PE6, PA3, PE7, PE8, PE9, PE10, PE11, PE12, PE13, PE14, PE15, PB10, PB12, PB13, PB14, PB15, PD10, PD11, PD12, PD13, PD14, PD15, PC6, PC7, PC8, PC9, PA8, PA15, PC10, PC11, PC12, PD0, PD1, PD2, PD3, PD4, PD5, PD6, PD7, PB6, PB7, PB8, PB9, PE0 |
| Supply/reference/core caps/reset/boot | 20 | VBAT, VSS, VDD, NRST, VSSA, VREF-, VREF+, VDDA, VSS, VDD, VCAP, VSS, VDD, VDDUSB, VSS, VDD, BOOT0, VCAP, VSS, VDD |
| Quiet reserve | 1 | PC13 |
| Unfitted LSE reservation | 2 | PC14, PC15 |
| Clocks | 2 | PH0, PH1 |
| Radio | 8 | PC0, PC1, PC2, PA4, PA5, PA6, PA7, PB1 |
| Legacy radio reservations | 2 | PC3, PC4 |
| GNSS | 5 | PA0, PC5, PB0, PA9, PA10 |
| USB and source status | 5 | PA1, PA2, PB2, PA11, PA12 |
| Flight link | 2 | PD8, PD9 |
| Debug | 3 | PA13, PA14, PB3 |
| Health and indication | 2 | PB4, PB5 |


## Why flight filled up

Five individually powered sensors account for 24 pins: three separate SPI
interfaces with chip selects, three interrupt/data-ready lines, five enables,
and two pressure-sensor I2C pairs. Three energetic channels consume 19 pins
because command selection, permission, arm/latch state, rail voltage, continuity
and current are represented separately. Servos add five more.

The early [6 September reservation](mcu-resource-and-timing-results.md) counted
40 flight and 20 comms port pins while explicitly leaving major controls and
diagnostics unresolved. It is historical reservation work, not a contradictory
current pin map. The diagram in the [MCU chapter](../architecture/01-mcus.md) now
accounts for the complete design.

## First comparison: H563 in LQFP64 for comms

Suggested exact comparison candidate: STM32H563RIT6, non-SMPS LQFP64, rather
than the existing STM32H563VIT6 LQFP100. Same MCU/memory class; different package.
ST lists nominal bodies of 10 × 10 mm and 14 × 14 mm respectively: 96 mm² less
body area, not 96 mm² guaranteed total PCB saving. Footprint, decoupling and
routing also consume space. No current price or power saving is claimed.

The existing connected comms functions have the following candidate port map.
The two legacy radio pins are retained as reservations in this comparison so
the proposed fit does not depend on deleting them.

| Function | Current port(s) | LQFP64 candidate | Mode |
| --- | --- | --- | --- |
| Main crystal | PH0, PH1 | Same | HSE |
| Radio SPI | PA4, PA5, PA6, PA7 | Same | GPIO CS; SPI1 AF5 |
| Radio reset, busy, IRQ, enable | PC0, PC1, PC2, PB1 | Same | GPIO; IRQ EXTI2 |
| Legacy radio reservations | PC3, PC4 | Same, still unused | No active module function |
| GNSS serial | PA9, PA10 | Same | USART1 AF7 |
| GNSS pulse, reset, enable | PA0, PC5, PB0 | Same | TIM2 CH1 AF1; GPIO |
| USB data | PA11, PA12 | Same | USB AF10 |
| USB/source state | PA1, PA2, PB2 | Same | GPIO |
| Flight UART | PD8, PD9 | **PC10, PC11** | USART3 TX/RX AF7 |
| Debug and trace | PA13, PA14, PB3 | Same | SWD / trace AF0 |
| LED and fault | PB4, PB5 | Same | GPIO; fault EXTI5 |
| Quiet / low-speed-clock reservation | PC13, PC14, PC15 | Same reservation | No new function authorized |

PD8/PD9 are not brought out in LQFP64; PC10/PC11 are, and are currently unused
on comms. All proposed port names are distinct. The same USART3 peripheral can
remain, avoiding a peripheral-instance change to its DMA request selection.
GPIO initialization and PCB routing would still change.

Required before acceptance: independently check all physical package pads,
supplies/USB supply arrangement, electrical limits and boot options; build the
actual target configuration; review errata; and verify the supported package
and stock with procurement. A proposed port map is not a drop-in part swap.

Source: [ST H563 datasheet](https://www.st.com/resource/en/datasheet/stm32h563vi.pdf),
Figure 5, Tables 14–16 and package drawings. Current implementation remains
the 100-pad device.

## Second comparison: a smaller device, not just a package

H503 has USB and much less memory: 128 KiB flash and 32 KiB main RAM. It is not
ruled out by “needs USB,” but is not a demonstrated fit for the current service
requirements. [ST H503 datasheet](https://www.st.com/resource/en/datasheet/stm32h503cb.pdf).

The current handoff allows 32 KiB service payload blocks. Buffering even one
whole payload fills 32 KiB before metadata, stack, USB and UART queues or other
state. A streaming implementation could change the requirement, but has not
been demonstrated. Two 32 KiB ping-pong buffers already need 64 KiB; this is an
illustrative design cost, not an approved buffering allocation.

At the proposed 680 kB/s service throughput, 10 ms of backpressure accumulates
6.8 kB; 100 ms accumulates 68 kB. The useful question is how much bounded buffering
and flow control the implementation needs, not only whether the chip runs fast.
The UART's normal 2 Mbaud 8N1 wire ceiling is 200 kB/s, versus the 20 kB/s routine
outbound telemetry cap. Disarmed 8 Mbaud has an 800 kB/s wire ceiling. These
arithmetic ceilings do not prove processing or end-to-end throughput.

Recommendation: keep the H563 device class while evaluating the smaller comms
package. A different device should earn its added development and memory
constraints with a concrete benefit. Do not reuse the flight-only 128 KiB
logging-buffer allowance as a claimed measurement of comms RAM use.

## DMA, memory and execution scope

The handoff reserves 11 DMA channels for flight and six for comms. Flight uses
six SPI RX/TX channels, two ADC channels, two UART channels and one OctoSPI
channel. Comms uses two channels each for the flight UART, GNSS UART and radio
SPI. This counts reservations; it is not an independent validation of request
numbers, arbitration or simultaneous operation.

No target firmware sources/build for Ogma2 were found in this repository.
Consequently, flash/RAM occupancy, stack watermarks, ISR blocking, worst-case
execution and power cannot be measured here yet. The 1 kHz schedule, 200 Hz
policy and 30% reserve remain budgets. A generated empty firmware benchmark
would not answer whether Anav's actual architecture fits.

The next software evidence is the actual target configuration and build map,
followed by a bounded non-actuating workload test. There is no need to wait for
that to understand the pin allocation or consider the package alternative.

## Flight pin-pressure options, not approved deletions

- Omit one unneeded local servo PWM: one pin. Does not remove the shared power
  or voltage-monitor requirements of the remaining servos.
- Use single-lane SPI recording instead of quad: two fewer data pins; validate
  selected NOR mode and bounded throughput first.
- Share sensor bus wires: possible savings, but changes failure containment and
  scheduling. Derive savings from the chosen topology; do not assume shared
  data-ready, chip-select or enable lines.
- Move nonessential status work to comms: possible, but its loss must remain
  acceptable with comms failed.
- Larger flight package: a legitimate alternative if requirements justify it;
  adds footprint/routing work, not automatic reliability.

Do not recover pins by moving flight authority onto comms or removing physical
inhibits merely to satisfy a spreadsheet. All changes require explicit review.

## Remaining uncertainty

The desk investigation supports a package comparison, not final silicon
selection. Prices, measured power, firmware fit and timing remain unknown.
The architecture is still open; neither CSV, schematic, PCB nor firmware was
changed. Further model work can inspect a supplied target build and configuration;
physical timing, fault and power claims need corresponding evidence.
