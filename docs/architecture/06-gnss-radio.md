# 6. GNSS and radio

## Installation change

The carbon airframe makes antenna placement a system decision. External GNSS
reception is authorised; the integrated-antenna SAM-M10Q arrangement is to be
replaced. The inspected CAD still contains U4504 SAM-M10Q-00B. The implementation
candidate is MAX-M10S-00B with a passive external 50 Ω antenna through vertical
Amphenol 132134 SMA. No antenna bias or ANT_CHECK is proposed for that passive
path. Footprint and RF ESD checks are still in progress; it is not yet installed.

Keep comms USART1, PPS capture, reset and the switched GNSS domain unless a
real pin/interface conflict is demonstrated. An external antenna does not
improve the receiver's allowed dynamics or altitude envelope by itself.

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
