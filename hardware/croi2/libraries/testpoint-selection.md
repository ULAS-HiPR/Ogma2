# Croí2 insulated rail test points

7 September 2026. Selected under Seán's request for a small cylindrical plastic
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
