# Accepted radio change and Anav handoff

Later 7 September amendment: J4601 is now vertical standard SMA female
**Amphenol 132134**, replacing the U.FL described in the initial integration
record below. Wio RF/MCU pin mapping is unchanged. See the
[installed connector revision](connector-servo-readiness-revision-2026-09-07.md).

7 September 2026. Seán accepted the six-action review and authorised implementation.
This supersedes its proposal status and the earlier E22 selection. No firmware
implementation, procurement or flight release is authorised by this document.

## Decision

Use **Seeed Wio-LR2021, 868/915 MHz module, SKU 100058045**, in Croí U4606.
Keep SAM-M10Q, all five sensors, JST GH CAN, the two STM32H563VIT6s and both
frozen physical pin maps. Keep the Croí/Foinse boundary. Above-80-km height
estimation remains a non-binding vehicle-level study.

The sensor configuration checklist and CAN harness recommendation are accepted.
Exact cable, installed length and propulsion-end cavity numbering remain open;
the drawing is not a harness fabrication release. No new sensor is required.
No pre-order custom evaluation board is added.

## Anav: exact radio contract

The existing net names survive so the MCU allocation CSVs do not change.
`LORA_DIO1` is now a historical host signal name: **it reaches Wio DIO5**, not
a physical module pin called DIO1. Configure DIO5 as the required interrupt
output before enabling its interrupt handling. PC3 and PC4 remain reserved;
do not drive an external RF switch or assign another function without review.

| Comms pad / GPIO | Host signal | Wio physical contact |
| --- | --- | --- |
| 15 / PC0 | LORA_RESET_N | 3 RESET, active low |
| 16 / PC1 | LORA_BUSY | 8 BUSY, open-drain |
| 17 / PC2 | LORA_DIO1 | 2 DIO5, configured IRQ |
| 18 / PC3 | LORA_RXEN | Unused, reserved; initialise low |
| 29 / PA4 | LORA_NCS | 7 NSS |
| 30 / PA5 | LORA_SCK | 6 SCK |
| 31 / PA6 | LORA_MISO | 4 MISO |
| 32 / PA7 | LORA_MOSI | 5 MOSI |
| 33 / PC4 | LORA_TXEN | Unused, reserved; initialise low |
| 36 / PB1 | LORA_EN | Existing hardware-gated radio power permission |

Module pad 1 is LORA_3V3. Ground pads: 9, 11, 12, 14, 15, 20. Pad 10 is
sub-GHz RF to J4601, Hirose U.FL-R-SMT-1(10). Pad 13 high-band RF is NC;
no high-band transmission. Unused DIO pads 16–19 and 21–22 are NC.

Use an **LR2021 driver**, not the SX1262 command implementation with a changed
device name. Initial SPI proposal: mode 0, 1 MHz; raise speed only after timing
checks through the real isolation and 470 Ω series paths. The device's 16 MHz
limit is not an approved board SPI rate. BUSY has a 10 kΩ pull-up on the
switched radio side. Check BUSY before commands with bounded timeouts; account
for its assertion following NSS and the driver's wake/reset rules. Reapply
DIO configuration after cold reset in the state required by the LR2021 driver.

**Do not carry over E22's 2.2 V TCXO setting.** The Wio documentation identifies
an internal 3.0 V TCXO. Confirm the exact module-revision clock/startup settings
against the official driver before transmitting; this setting is not falsely
declared closed here. Power recovery must repeat complete radio initialisation.
Keep failures inside the communications domain; flight does not wait on radio.

Keep sub-GHz LoRa as the first telemetry mode. Faster PHY experiments need a
matching ground receiver and their own link budget. No live-video or full-log
radio guarantee. Start the power budget around 120 mA typical high-power TX,
with transient/tolerance margin; do not use the ambiguous 12.07 mA table row
as continuous +22 dBm consumption. Actual rail and RF tests use the first PCBA.

## CAD and remaining closure

The bounded implementation replaces U4606, removes U4605/C4605/R4606/R4607,
adds seven series resistors, BUSY pull-up and host U.FL connector, and disables
the unused U4604 channel. It retains the existing radio power topology.
The supply bypass capacitor follows the new module power pin. No other block
is repacked. All four output-energy links remain DNP.

The local [library record](../../hardware/croi2/libraries/radio-integration.md)
documents corrections needed in the manufacturer's KiCad assets. The official
Wio STEP is available but **not linked pending alignment verification**.
Do not mistake an absent 3D body for free mechanical space.

Still open: exact supplied module revision, TCXO/startup configuration, final
SPI edge timing, installed antenna/RF measurements, power transient margin and
ordinary board release checks. These are explicit closures; acceptance does
not turn them into measurements. Consult current native reports for validation.

Sources: [Seeed module resources](https://wiki.seeedstudio.com/wio_lr2021_introduction/),
[module datasheet](https://files.seeedstudio.com/wiki/Wio-LR2021/res/Wio-LR2021%20Module%20Datasheet.pdf),
[host RF layout guide](https://wiki.seeedstudio.com/wio_lr2021_pcb_design_guide/).
