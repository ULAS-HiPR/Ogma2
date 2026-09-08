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

## The GNSS shortlist and why the answer changed

The 6–7 September research favoured SAM-M10Q because the soldered patch avoided
a coax connector, custom antenna feed and active-antenna supervision. That was
conditional on an RF-transparent installation with usable sky view. The later
carbon-airframe decision broke that condition; MAX-M10S external reception is
now installed. The design changed because of the installation, not because
SAM suddenly became an obsolete receiver.

| Option explored | Benefit | Limit / disposition |
| --- | --- | --- |
| SAM-M10Q integrated patch | Compact integration with no GNSS coax; few host RF parts | Needs an appropriate ground environment and RF-transparent view. Superseded for the carbon installation |
| MAX-M10S external antenna | Receiver can stay on Croí while the antenna occupies a useful location | Adds coax, RF launch, ESD and retention work. Current choice; passive assembly still needs a loss budget |
| MAX-F10S | L1/L5 dual-band reception, potentially useful against measured multipath/interference | The reviewed specification still had an 80 km altitude envelope; more bands do not solve the apogee gap |
| ZED-X20P | Precision/all-band/RTK capability | Reviewed airborne model still listed an 80 km ceiling; higher integration cost was not justified by this mission's workhorse needs |
| Vendor-supported sounding-rocket GNSS | Potential full-envelope dynamics/altitude support | Separate receiver, vendor evidence, price and qualification question; exploratory only |

Primary source trail from the dated shortlist:
[SAM-M10Q](https://content.u-blox.com/sites/default/files/documents/SAM-M10Q_DataSheet_UBX-22013293.pdf),
[MAX-F10S](https://content.u-blox.com/sites/default/files/documents/MAX-F10S_DataSheet_UBXDOC-963802114-12732.pdf),
[ZED-X20P integration manual](https://content.u-blox.com/sites/default/files/documents/ZED-X20P_IntegrationManual_UBXDOC-963802114-12901.pdf).
These were September research findings, not a new live market survey.

The original SAM 10 Hz investigation also caught a mode distinction: the
reviewed firmware could deliver four-constellation 10 Hz in high-performance
mode, versus 4 Hz by default. Do not transfer that exact table to MAX without
checking its product/firmware. Receiving ten messages per second does not prove
ten new navigation solutions. Read identity/configuration and measure actual
solution age, interval, power and reacquisition.

The above-80-km study distinguishes accurate altitude from merely obtaining a
number: ellipsoid height versus launch datum, vertical uncertainty, valid
dynamics, antenna visibility and unaided inertial drift all matter. A simple
10 mg constant acceleration bias over 120 seconds gives roughly 706 m of
position error before attitude/model errors. This was illustrative arithmetic,
not a flight simulation or an IMU accuracy claim. An external antenna alone
does not close any of those estimator requirements.
[Exploratory height study](../height-estimation-above-80km-2026-09-07.md).

## Radio retained

U4606 is Wio-LR2021 868/915 MHz, Seeed 100058045; J4601 is vertical standard
SMA 132134. Only sub-GHz RF is connected. Its DIO5 uses the historic LORA_DIO1
interrupt net. RXEN/TXEN remain reserved/unused; an LR2021 driver replaces SX1262
assumptions. Keep reset, BUSY, framing and failures bounded on comms.

The castellated module contains the difficult RF implementation. A bare
transceiver might save space or give more control but transfers matching,
RF layout and validation work onto us. It is not selected.

## Radio options, cost and link tradeoffs

The Rev 1 SX1272 module established a useful integration preference: solder
down a finished RF frontend rather than reproduce its matching network on the
flight board. The first Ogma 2 choice was E22/SX1262. Anav's newer-hardware
question led to a bounded module comparison and then the accepted Wio change.

| Researched module | Approximate body | Main trade |
| --- | --- | --- |
| Ebyte E22-900M22S / SX1262 | 14 × 20 mm | Existing implementation and module antenna connector; sound fallback, now superseded |
| Seeed Wio-LR2021 868/915 | 17.07 × 10.42 × 2.8 mm | Smaller body, published CAD and faster PHY options; new driver and host RF launch required; selected |
| NiceRF LoRa2021, 22 dBm | 19.72 × 15 × 2.2 mm | Credible SPI alternative; exact band/clock option and purchasing case were not closed |
| LPRS eRIC-LR2021-HCI | 20 × 15 mm | Host-controlled module/support and coax options; quote and integration trade remained open |

Wio's body area is about 36.5% smaller than E22's. That is not the whole-block
saving: the SMA, feed, ground reference and assembly clearance remain. Its
US$6.99 listing in the 7 September review was a dated store observation, not a
delivered quote. [Full dated comparison and supplier sources](../avionics-options-review-2026-09-07.md#shortlist).

### Faster modes spend sensitivity

For a 64-byte ordinary LoRa packet with explicit header, CRC, coding 4/5 and
eight-symbol preamble, the recorded calculation gave:

| Mode | Packet airtime | Meaning at ten packets/s |
| --- | ---: | --- |
| SF7 / 125 kHz | 118.016 ms | Cannot fit even before retries |
| SF7 / 250 kHz | 59.008 ms | About 59% occupancy before overhead |
| SF7 / 500 kHz | 29.504 ms | About 29.5% occupancy before overhead |
| SF12 / 125 kHz | 2,793.472 ms | A very different update-rate regime |

These are illustrative calculations, not the selected packet format or lawful
transmit profile. Regional frequency, bandwidth, EIRP and access rules remain
separate constraints. [Reproducible research calculation](../calculations/avionics-options-estimates.py).

The reviewed Wio table quoted −141.1 dBm for slow SF12/125 kHz versus −110 dBm
at 260 kbit/s FLRC and −100.5 dBm at 2.6 Mbit/s FLRC, under its stated test
conditions. The study's illustrative 915 MHz / 100 km link, 22 dBm transmitter,
unity-gain antennas and 3 dB losses gave about −112.7 dBm received. That can
leave margin for slow LoRa while already missing the quoted FLRC thresholds.
Pattern nulls, polarisation, interference and slant range make the real problem
harder. [Wio datasheet](https://files.seeedstudio.com/wiki/Wio-LR2021/res/Wio-LR2021%20Module%20Datasheet.pdf).

An SX1272 ground receiver cannot decode FLRC simply because both devices are
called LoRa radios. Even ordinary LoRa needs mutually supported settings and
packet formats. Start with one conservative compatible link, record full-rate
data locally and keep faster modes optional. Live video is a separate payload
job, not an implied capability of this radio change.

### New silicon also means new integration evidence

Wio BUSY is open-drain, the IRQ is DIO5 behind the historic LORA_DIO1 host name,
and its TCXO configuration is not E22's 2.2 V setting. The installed handoff
keeps those distinctions explicit. The manufacturer's 470 Ω digital-series
guidance needs actual edge/timing checks; it does not justify copying example
trace geometry without our stack-up. The driver must be LR2021-specific.

The research also rejected an ambiguous 12.07 mA table value as a continuous
+22 dBm power budget: at 3.3 V it would imply about 40 mW input for 158 mW RF
output. Roughly 120 mA typical high-power TX was retained as a starting budget,
with transient and tolerance margin still to measure. Datasheet context is
part of selection, not a footnote after choosing the newest chip.
[Accepted radio handoff](../radio-change-2026-09-07.md).

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
