# Wio-LR2021 library integration

7 September 2026. Engineering draft. No fabrication or RF qualification.

Selected module: **Seeed Wio-LR2021, 868/915 MHz, SKU 100058045**.
U4606 replaces E22-900M22S. No MCU pad changes. No second radio population.

## Provenance and corrections

Seeed's [official resource page](https://wiki.seeedstudio.com/wio_lr2021_introduction/)
supplied `kicad-library.zip` and the STEP assembly. Original downloads and
checksums are retained in `../../../../radio-upgrade-2026-09-07/sources/`
and `../../../../radio-upgrade-2026-09-07/candidate-audit.json`.

The supplied assets used KiCad 10 syntax. This KiCad 9 adaptation preserves
all 22 pad numbers, dimensions, pitch and relative positions. The footprint
origin is translated to the module body centre; no electrical pad is invented.
The manufacturer symbol's generic passive pins now have electrical types
matching their functions. Its half-grid graphic is placed so pins land on grid.

Corrections to the supplied footprint:

- Remove its accidental DNP attribute and unexplained pad-2 net-tie declaration.
- Replace the body-only courtyard and stray courtyard circle with a closed
  rectangle enclosing body and pads with at least 0.25 mm allowance.
- Remove body-outline silk crossing solder pads; retain an external pin-1 mark.
- Keep the fabrication body rectangle and complete manufacturer land pattern.

**The official Wio STEP is present but not attached.** It is a compound KiCad
assembly with nontrivial transforms; its alignment has not been verified.
Do not assume it is a centred single-part model. This remains a mechanical
library closure, not permission to attach a guessed transform. The host U.FL
connector uses the matching locally copied KiCad footprint and STEP.

## Circuit delta

U4605, C4605, R4606 and R4607 are removed. The fourth U4604 switch channel is
disabled with its enable grounded and terminals NC. Comms PC3/PC4 keep their
frozen names but no longer drive external RXEN/TXEN hardware.

R4614–R4620 are initial 470 Ω module-end series resistors on SCK, MOSI, MISO,
NSS, reset, BUSY and IRQ respectively. R4621 is the 10 kΩ BUSY pull-up to the
switched radio rail. Validate values and timing on the first PCBA; these are
not evidence that 16 MHz SPI works through the complete isolation path.

J4601 is Hirose U.FL-R-SMT-1(10). Module pad 10 feeds its signal contact;
pad 13 is NC, without a host stub or high-band transmission. Installed antenna
retention remains required. This connector is not a new external harness family.

Source supply, load switch, power gating and bulk capacitance remain. C4611
moves with the new power pin. Other circuits, both MCU maps and all output DNP
links remain unchanged. Radio placement is a routeable starting arrangement,
not a validated RF layout; see the ordered layout guide.

## Validation scope

Native schematic connectivity, exact independent radio pin assertions,
library hashes, saved-PCB pad nets, source-to-candidate isolation and native
DRC are checked before promotion. Neither the historical 499 local-distance
checks nor a STEP file establishes the new circuit's RF or mechanical quality.
The prior placement evidence remains labelled historical in the placement report.
