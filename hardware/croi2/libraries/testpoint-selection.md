# Croí2 insulated rail test points

## 22 November 2026 (stage B2): the rail loops go surface-mount (D-22Nov.24)

Seán agreed to surface-mount loops (“why do we have holes going the entire way
through”). Keystone's SMT Test Points catalogue page (Mouser's copy,
https://www.mouser.com/pdfDocs/KeystoneSMTTestPoints.pdf, read 22 Nov 2026):

| Family | Keystone says | Pad (mm) | Height (mm) | JLC (21 Nov scrape) |
| --- | --- | --- | --- | --- |
| 5015 / 5017 micro-miniature | miniature probes, clips and hooks | 3.4 × 1.8 | 1.5 | C2906768, 60,348 |
| 5019 / 5029 miniature | most standard probes, clips and hooks | 3.0 × 1.6 | 1.8 | not listed |
| 5190TR–5199TR colour keyed | most standard probes, clips and hooks | 3.0 × 1.5 | 2.5 | 5191TR black 616, 5194TR yellow 486, 5192TR white 282; orange not listed |
| 5016 / 5018 compact | standard probes, clips and hooks | 4.7 × 3.4 | 2.3 | C238129, 4,917 |

The pick: 5194TR, yellow (C22388408). Of the families that take a standard
scope hook and JLC stocks, it has the smallest pad, and its base keeps a
colour. Its footprint, `Ogma2:TestPoint_Keystone_5190TR_ColorKeyed`, is drawn
by capture step 18 from the page: one 3.0 × 1.5 mm pad, the 3.0 × 2.4 mm base
centred on it, courtyard 0.25 mm round the base (10.2 mm², against 11.5 mm² for
the 5003). The four GND loops stay Keystone 5011, through-hole.

Not checked: a standard hook and a mini-grabber on a real part; the base's
exact outline (the page's view has a notch, drawn here as a rectangle).

## 22 November 2026: three sizes, 47 test points (D-22Nov.9)

Supersedes the part choices below; the 7 September notes stay for the
footprint and the model gap. The orange loops are replaced above.

| Size | Part | JLC | Where | Count |
| --- | --- | --- | --- | --- |
| Big black loop | Keystone 5011, multipurpose, 1.6 mm hole | C238127 | GND, at the board edges | 4 |
| Orange loop | Keystone 5003, miniature, 1.0 mm hole | C238124 | Each regulator or switch output, the strobe, GNSS PPS | 18 |
| 1.0 mm pad | `TestPoint_Pad_D1.0mm` (copper only) | none | BOOT0, reset memory, spare pins, power status, pyro ADC and arm sense | 25 |

- Keystone 5000 (red) is not in JLC's assembly library (jlcparts scrape,
  21 Nov 2026; LCSC C5199900 only), so the rail loops are 5003, orange.
- 5011's footprint is KiCad 9.0.7's `TestPoint_Keystone_5010-5014_Multipurpose`
  (2.8 mm pad, 1.6 mm hole, 4.0 mm courtyard), vendored in step 12. Its height
  (about 8 mm, 0.320 in per DigiKey) isn't checked against Keystone's drawing,
  which refuses automated fetches.
- The silkscreen shows only each test point's TP number.
- No test point goes on a fire net or a line that drives a fire switch (B-02).

## 7 September 2026

Selected under Seán's request for a small cylindrical plastic
body with a short exposed loop. Replaces all 20 previously assigned bare-loop
footprints. No new probe nodes or electrical changes.

- **17 supply points: Keystone 5000, red.**
- **Three grounds: Keystone 5001, black:** TP2304, TP4204, TP502.
- The remaining **31 flat 1 mm signal pads are unchanged**.

Schematic values remain rail names. MPN and Manufacturer fields specify the
actual purchased part; the PCB carries the same fields and footprint binding.

## Package and library

`TestPoint:TestPoint_Keystone_5000-5004_Miniature`, from the installed KiCad 9
library. Nominal body diameter 2.5 mm, installed height 4.6 mm, loop opening
1.25 mm. One 1 mm plated hole and 2 mm copper pad; 3.3 mm circular courtyard.
The pad/hole and centre are unchanged from the former generic loop. The body
outline and courtyard now describe the insulated miniature part.

The manufacturer drawing uses rounded metric dimensions beside inch values.
Confirm the finished-hole tolerance and insertion fit with the fabricator and
assembler. These are through-hole parts, not tape-and-reel SMT test loops.
Reserve probe-hook access above and beside the body; a courtyard is not a
guarantee that a clip fits. Keep probe leads out of sensitive loops and strain
relieve them during powered bench work. The exposed top loop can still short.

## Sources and limits

- [Keystone 5000 current product page](https://www.keyelco.com/product.cfm/Miniature-Style/5000/product_id/1309).
- [Keystone 5001 current product page](https://www.keyelco.com/product.cfm/Miniature-Style/5001/product_id/1310).
- [Manufacturer family drawing](https://www.keyelco.com/product-pdf.cfm?p=1309).
- [Manufacturer dimensional catalogue, page 51](https://www.keyelco.com/pdfs/M55p51.pdf).
  This older catalogue was downloaded and visually checked; it establishes
  the geometry, not a current material/process qualification.
- Local footprint source and hashes: `board-library-manifest.json`.
  KiCad-derived geometry retains `KICAD-LICENSE.md`.

**Exact 3D model unavailable.** The stock footprint names a STEP absent from the
installed library; direct upstream STEP/VRML lookups also returned no file.
The manufacturer's model download requests contact details. No details were
submitted. The broken model reference was removed from the new local footprint;
the previous bare-wire model is not attached to these parts. Croí now resolves
547 model instances, down from 567. This is an explicit model gap, not twenty
missing PCB footprints. Do not treat the resulting 3D view as an assembly-fit
check. The obsolete generic library files remain unused for traceability.

Foinse2 was outside this replacement pass and is unchanged.
