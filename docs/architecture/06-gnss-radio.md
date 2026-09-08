# 6. GNSS and radio

## Installation change

The carbon airframe makes antenna placement a system decision. External GNSS
reception is implemented in the draft; the integrated-antenna SAM-M10Q is
replaced. The checked native CAD uses U4504 `MAX-M10S-00B`, external
passive 50 Ω antenna/coax and vertical J4501 `Amphenol 132134` SMA. D4501
`TPD1E0B04DPYR` is the .15 pF-typical RF ESD candidate. No antenna bias or
ANT_CHECK. Native pin/footprint checks are complete; installed RF/ESD behaviour
is not qualified. See the [installed change record](../installation-change-record-2026-09-08.md).

Keep comms USART1, PPS capture, reset and the switched GNSS domain unless a
real pin/interface conflict is demonstrated. An external antenna does not
improve the receiver's allowed dynamics or altitude envelope by itself.

MCU pins stay PA9 TX, PA10 RX, PA0 PPS, PC5 reset and PB0 enable. MAX VCC8 and
V_IO7 use GNSS_3V3; VIO_SEL15 and backup input6 stay open. SAFEBOOT18 stays
unloaded. TIMEPULSE4 and SAFEBOOT18 are internally coupled through 1 kΩ:
no MCU pull-down or other startup-low PPS load. Separate package pins do not
remove that constraint. [u-blox datasheet, page 9](https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf).

The antenna must see the sky from its actual installed location. Harness
retention, bend radius, strain relief, feedthrough and ground environment
matter. Carbon nearby remains part of the RF installation even when the
antenna is technically outside the electronics enclosure.

## Minimal GNSS circuitry

Start with the chosen receiver's reference RF input. For an active antenna,
provide its required protected bias feed and correctly selected RF coupling/
filtering; for a passive antenna, do not add an unnecessary bias source.
Protect an exposed connector appropriately and preserve a controlled-impedance
feed and return. The proposed passive antenna needs an actual assembly and
coax-loss budget; long cable loss is not recovered by selecting a different
connector. If it requires an active antenna, reopen the bias/protection decision.

The MAX copper land was checked against the u-blox drawing. Its stock rectangular
paste openings still need assembler review against the manufacturer's T-shaped
recommendation. The RF ESD land uses .3 × .5 mm pads at .7 mm pitch from TI's
DPY drawing. A device ESD rating does not establish receiver survival on this PCB.
Exact MAX/ESD models are not linked; do not reuse the old SAM body.

Do not restore the Rev 1 antenna-check/switch network by habit. It consumed
space and was bypassed. A diagnostic circuit must name the detectable fault,
required action and electrical cost before it earns a place.

An onboard patch remains a simpler cable-free alternative only in a suitable
RF-transparent installation. That is not the accepted carbon-airframe direction.

## Radio retained

U4606 is Wio-LR2021 868/915 MHz, Seeed 100058045; J4601 is vertical standard
SMA 132134. Only sub-GHz RF is connected. Its DIO5 uses the historic LORA_DIO1
interrupt net. RXEN/TXEN remain reserved/unused; an LR2021 driver replaces SX1262
assumptions. Keep reset, BUSY, framing and failures bounded on comms.

The castellated module contains the difficult RF implementation. A bare
transceiver might save space or give more control but transfers matching,
RF layout and validation work onto us. It is not selected.

## Remaining proof

Installed antenna retention and RF link quality, module revision/TCXO settings,
SPI timing through the existing boundaries, startup and burst-current effects
need testing. The SMA's solder/rework access near sensors needs Seán's layout
review; this task does not silently move the board placement.

GNSS absence, invalid fixes or receiver limits must not remove essential
flight operation. Neither the existing receiver nor ordinary barometers prove
100 km apogee. Full-envelope altitude evidence remains vehicle-level work;
the above-80-km study is non-binding.

Evidence: [radio contract](../radio-change-2026-09-07.md),
[height study](../height-estimation-above-80km-2026-09-07.md),
[firmware handoff](../firmware-handoff-2026-09-07.md).
