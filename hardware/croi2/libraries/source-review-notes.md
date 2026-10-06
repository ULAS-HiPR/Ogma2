# Library drawing review and open checks

7 September 2026. Engineering work record, not fabrication release.

## Drawing-derived footprints

| Part | Source and transcription | Remaining qualification |
| --- | --- | --- |
| MPS-08-01-01-L-RA-SD | [Samtec MPS RA-SD footprint Rev B](https://suddendocs.samtec.com/prints/mps-xx-01-xx-x-ra-xx-footprint.pdf): eight contacts, six 1.04 mm finished holes/contact, 2.54 mm tail-row pitch, 5 mm contact pitch; pin 1 on right in top view; first row 1.98 mm behind PCB edge; 3.56 mm retention holes. | Body projection, actual board thickness, mating envelope, 7.39 mm board-edge gap and retention bridge still require a joint mechanical review. Copper diameter 1.64 mm is a stated design choice, not a manufacturer requirement. |
| MPT-08-01-01-L-RA-SD | [Samtec MPT RA-SD footprint Rev B](https://suddendocs.samtec.com/prints/mpt-xx-xx-x-ra-xx-footprint.pdf): same tail grouping; pin 1 on left; first row 2.85 mm behind edge. Separate footprint, not a reflected socket asset. | Same mechanical review. Positive Y projects beyond board; the datum line is documentation, not an automatic board-edge cut. |
| SAM-M10Q-00B | [u-blox integration manual UBX-22020019 R02](https://content.u-blox.com/sites/default/files/documents/SAM-M10Q_IntegrationManual_UBX-22020019.pdf), Figures 23–24, pp64–65: 1.8 × 1.5 mm lands, 1.9 mm pitch, 0.05 mm mask expansion, four 0.58 × 0.72 mm paste apertures per pad. Pad numbers checked against the datasheet's top view. | Stencil/process agreement; manual suggests 120 µm. Ground-plane, nearby heat/noise and antenna clearance are board-level work. Footprint does not establish GNSS performance. |
| BMP390 | [Bosch datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp390-ds002.pdf), p49: recommended lands equal the outline dimensions. Bottom view mirrored into PCB top view. | Pressure-port cleanliness, assembly process and final independent check. |
| CSD17318Q2 | [TI datasheet](https://www.ti.com/lit/ds/symlink/csd17318q2.pdf), top view p1 and DQK0006C land pattern p10. Six leads plus source exposed pad 7 and drain exposed pad 8. | Paste currently follows copper; final stencil review remains. Thermal paths remain board work. |
| LM73100RPWR | [TI LM7310 family datasheet](https://www.ti.com/lit/ds/symlink/lm7310.pdf), RPW0010A drawing 4225183/A. Two 0.3 × 2.4 mm power strips; four L-shaped corner lands represented by overlapping same-number primitives. | Copper extents checked; corner-rounding differences and stencil need final review. No generic 10-pin QFN substitution. |
| TPSM63603RDHR | [TI datasheet](https://www.ti.com/lit/ds/symlink/tpsm63603.pdf), RDH0030A drawing 4226150/B, pp43–44. Nonuniform 30-pad map and stepped corner extents checked against annotations and PDF vector coordinates. Exposed pads 27/30 use 1.17 × 0.74 mm paste; 28/29 use 1.47 × 0.95 mm paste. | Compound primitives approximate corner fillets. Final stencil/assembly audit remains; drawing assumes 125 µm stencil. Optional vias are board thermal-design work. |
| TPS1H100BQPWPRQ1 | [TI Rev D datasheet](https://www.ti.com/lit/ds/symlink/tps1h100-q1.pdf), PWP0014K drawing 4229706/B, pp45–46. 1.5 × 0.45 mm leads on 0.65 mm pitch; 5.8 mm row-centre separation; 3.4 × 5 mm thermal copper with 2.6 × 2.59 mm mask/paste window. | Stencil window assumes 125 µm. Optional thermal vias are not embedded; board thermal design and assembler agreement remain. Replaces a stock candidate with a different exposed mask size. |
| ECS-160-10-36Q-ES-TR | [ECX-2236Q Rev2020](https://ecsxtal.com/store/pdf/ECX-2236Q.pdf), p1: 1.2 × 1.0 mm lands, centre separation 1.7 × 1.3 mm. Pins 2/4 case ground, 1/3 crystal. | Load network and drive level are schematic work. |
| ABS07-32.768KHZ-7-T | Abracon ABS07 mechanical drawing revised 2022-08-10, p4: 1.1 × 1.9 mm lands, 1.4 mm internal gap, nonpolar. Public source is recorded in the manifest. | Oscillator network and final assembly review. |
| E22-900M22S | Ebyte E22-M series manual v1.2, section 3.2, printed p6/PDF p9. 14 × 20 mm body and 22 castellations; upper eight-pin rows and lower three-pin groups are not one regular pitch row. | Manufacturer drawing gives module pads rather than a host-PCB recommendation. Selected host lands are 1.4 × 0.8 mm, centred 0.2 mm inside each body edge; check toe/heel with assembler. Leave ANT21 unrouted when using the fitted IPX connector. |

The Ebyte manual is retained with the accepted review at
`../../../architecture-review-2026-09-06/sources/manufacturer/Ebyte-E22-M-Series-User-Manual-v1.2.pdf`.
Part/source URLs and pin tables for all remaining parts are in
[source-manifest.json](source-manifest.json) and the authored definitions.

## Pin traps preserved in exact-part symbols

- TCAN3413 pin 5 is **VIO**. It is not the other variant's shutdown pin.
- SN74LVC1G74 DCU has **Q̅ on 3, Q on 5**.
- TPS1H100 **B** uses analogue **CS on 14**, not Version A's status output.
- TXU0304 PW14 has NC pins 6 and 9. Do not import its 16-pin package map.
- TS5A3167's `NC_SWITCH` means **normally closed**, not no-connect.
- ADXL375 pin 3 is reserved: VS or open. Pin 11 is GND or open. They are
  separately named; neither is silently turned into an arbitrary ground pad.
- ICM-42688-P reserved pin 7 must be grounded. Other reserved-pin permissions
  differ; consult the exact table before assigning their nets.
- E22-900M22S **12 is GND; 15 is NRST**. Do not use the smaller MM22S map.
- SAM-M10Q TIMEPULSE and SAFEBOOT_N are internally coupled through 1 kΩ.
  External loading during startup matters even though the library pins differ.
- MS5607 stock symbol exposes pins 4 and 5 as CSB. The manufacturer's table
  groups these with an internal-connection note. Do not invent a separate
  function for pin 5; its exact hookup and prohibited under-package routing
  remain part of the final sensor drawing review.
- USB A1/B12 and A12/B1 share ground lands; A4/B9 and A9/B4 share VBUS lands.
  All those symbol pins must resolve to their corresponding common nets.

## Complete the library before fabrication

1. Complete final compound-corner fillet and assembly review for TPSM63603RDHR
   and LM73100. Both now have drawing-derived footprints with checked extents.
2. Obtain and visually inspect [Nano-Fit 1053111102's exact drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/105/105311/1053111102_sd.pdf).
   Repeated direct retrieval returned HTTP errors/timeouts; no retention-hole
   coordinates were guessed. Its two-contact symbol is present.
3. Complete the remaining stock-family package and pin audits, especially both
   IMUs' top/bottom view and axes, ADXL375 orientation, MS5607, NOR SOP dimensions,
   TPS7A91/TPS2121/TPS26630 exposed pads, and connector mating orientation.
   The common LGA candidate for both IMUs is **not** a declaration of physical
   interchangeability or matching sensor axes.
4. Confirm mask, paste, minimum copper/clearance, soldering and thermal-via
   treatment with the selected PCBA process. Then perform schematic ERC,
   board DRC, mechanical mating review and the normal pre-order release check.
5. Add exact support-component selections when schematic values are settled;
   this inventory is a major-parts library, not an invented completed BOM.

These are unfinished model/engineering tasks, not a request for another round
of architectural approval. The first full PCBA remains the functional-block
test article; no separate pre-order coupon requirement was reintroduced.
