# Public-library model recovery — 7 September 2026

Status: three package models linked to five Croí components. Third-party visual
CAD, not manufacturer-certified mechanical or land-pattern approval.

## Installed

| Refs | File | Source | Checks / limitations |
| --- | --- | --- | --- |
| U1101 | TPS2121RUXR-EasyEDA.step | [Exact LCSC/EasyEDA record C485916](https://easyeda.com/api/products/C485916/components?version=6.4.19.5), model b3b163ff5ac04d1fb107c30a7d954e0d | Body 2 × 2.5 × 1 mm; twelve underside contacts match RUX0012A arrangement. Decorative library marking extends another 0.001 mm. Zero translation/rotation. |
| U1401 | LM73100RPWR-EasyEDA.step | [Exact record C3210761](https://easyeda.com/api/products/C3210761/components?version=6.4.19.5), model 262834a5342148ebb2da8f3848ec58ce | Nominal 2 × 2 mm, modeled width 2.01 mm; 1 mm seated height. Long central contacts and 0.45 mm side pitch match RPW0010A. Simplified rectangular corner terminals do not reproduce every notch. Z offset +0.05 mm seats lowest terminals at zero; no rotation. |
| Q6301, Q6401, Q6501 | CSD17318Q2-package-EasyEDA.step | [Exact record C2862001](https://easyeda.com/api/products/C2862001/components?version=6.4.19.5), model 5598088b47614774bebb8280ac64d5b4 | Record shares a package model named CSD19538Q2; it is not branded CSD17318 CAD. Measured 2.002 × 2 × 0.78 mm, within DQK0006C envelope. Six side terminals at 0.65 mm pitch; separate central pads 1 × 0.95 and 0.752 × 0.3 mm match this device. Simplified pad corners. Z offset +0.02 mm; no rotation. |

Public STEP endpoint is documented in the
[easyeda2kicad importer](https://github.com/uPesy/easyeda2kicad.py/blob/master/easyeda2kicad/easyeda/easyeda_api.py):
`https://modules.easyeda.com/qAxj6KHrDKw4blvCG8QJPs7Y/{uuid}`.
No login, browser control or personal-data submission used. Public availability
does not establish unrestricted redistribution rights; review before publication.

Dimensions checked against TI's [TPS2121](https://www.ti.com/lit/ds/symlink/tps2121.pdf),
[LM73100](https://www.ti.com/lit/ds/symlink/lm73100.pdf), and
[CSD17318Q2](https://www.ti.com/lit/ds/symlink/csd17318q2.pdf) mechanical drawings.
Native KiCad preview checked seating, orientation and alignment. No imported
EasyEDA footprint or symbol replaced existing electrical CAD.

## Downloaded but not accepted

| Record | Observed model | Reason held outside active library |
| --- | --- | --- |
| BMP390 C5124834 | 2 × 2 × 0.93 mm | Bosch specifies 0.75 mm nominal package; wrong height. |
| TPS1H100BQPWPRQ1 C475505 | 5 × 6.4 × 1.301 mm including marking | PWP0014K maximum height is 1.2 mm. |
| TPS7A9101DSKR C2878140 | 0.810 mm body, 0.811 mm with marking | DSK0010A maximum height is 0.8 mm. Do not call this exact. |
| ABS07 C276424 | 3.2 × 1.5 × 0.801 mm | Linked generic model says H0.8, not the selected 0.9 mm package envelope. |
| ECS crystal C2449912 | 2.5 × 2 × 0.62 mm | Record is AES rather than selected ES; height exceeds the selected drawing's 0.6 mm maximum. |

TPSM63603 C5219327 has a footprint record but no linked 3D model. Both exact
Samtec C3683145/C3683292 public API lookups returned no component record.
Keystone contributor repositories and their available branches did not yield the
model announced in KiCad footprint issue 1790. The Nano-Fit distributor page
lists a STEP ZIP, but its public fetch failed; no file recovered from that route.

Evidence, source JSON, downloaded STEP candidates, dimensions, terminal bounds,
snapshots and native-check output remain under
`../../../../model-recovery-2026-09-07/` (local workspace, outside board repo).
Remaining physical body gaps: 34 Croí plus one Foinse, 11 part numbers. The
separate Nano-Fit footprint gap on both boards remains unresolved.
