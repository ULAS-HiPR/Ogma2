# 3D models and missing parts — 7 September 2026

Status: partial recovery, not a complete library or mechanical release.

Follow-up: five more Croí instances now have checked third-party package CAD:
U1101 TPS2121, U1401 LM73100, and Q6301/Q6401/Q6501 CSD17318Q2.
[Sources, dimensions, transformations and rejected downloads](../../hardware/croi2/libraries/model-recovery-easyeda-2026-09-07.md).
Croí now resolves 567 models; Foinse remains 88. No placement/electrical change.

## What this pass recovered

| Board | Reference | Model | Evidence / limitation |
| --- | --- | --- | --- |
| Croí | U4606 | Wio-LR2021 | Existing Seeed STEP, now aligned and linked. Original assembly coordinates were the problem. |
| Croí | U4504 | SAM-M10Q-00B | Exact named component extracted from Vimdrones' public assembly. Third-party CAD; checked against u-blox mechanical drawing and terminal positions. |
| Croí | BZ9001 | CPT-9019S-SMT-TR | Downloaded directly through Same Sky's public model service; rotated onto its seating plane and aligned with both pads. |
| Croí | J6601 | 430450600 | Manufacturer-derived Micro-Fit model from a KiCad contribution. |
| Croí | J6602 | 430451000 | Manufacturer-derived Micro-Fit model from the same contribution. |
| Croí | U503 | TCAN3413 DRB package | KiCad TI S-PVSON-N8 package CAD: 3 × 3 mm, 0.65 mm pitch, 1.65 × 2.4 mm exposed pad, 0.92 mm modeled height against 1 mm maximum. Package model, not a branded TCAN model. |
| Foinse | J201 | 430450400 | Manufacturer-derived Micro-Fit model from the same contribution. |
| Foinse | J701 | 430450200 | Manufacturer-derived Micro-Fit model from the same contribution. |

All are project-local. No schematic, footprint pads, nets, placement, rule areas,
outline, DNP population or firmware allocation changed. A visible body does not
prove the land pattern, mating clearance, assembly process or component rating.

## Everything still missing a physical body

**35 placed component instances, covering 11 part numbers.** Nano-Fit is additional:
it still has no PCB footprint, so it is not included in placed-footprint counts.

| Board / refs | Exact part | Qty | Source / next step |
| --- | --- | ---: | --- |
| Croí rail probes | Keystone 5000 red | 17 | [Manufacturer STEP entry](https://www.keyelco.com/product.cfm/product_id/1309). Email submission required; no personal details submitted. |
| Croí TP2304, TP4204, TP502 | Keystone 5001 black | 3 | Obtain the exact black variant alongside 5000. Do not replace the insulated body with a bare loop. |
| Croí Y201, Y401 | ECS-160-10-36Q-ES-TR | 2 | [Exact CAD listing](https://componentsearchengine.com/part-view/ECS-160-10-36Q-ES-TR/ECS). Local generic 2520 crystal model is 0.83 mm high; ECX-2236Q drawing specifies 0.5 ± 0.1 mm. Rejected. |
| Croí U6304, U6404, U6504, U6802 | TPS1H100BQPWPRQ1 | 4 | [TI source](https://www.ti.com/product/TPS1H100-Q1). Need PWP0014K geometry. Local PWP0014A model has a different exposed-pad geometry; not silently substituted. |
| Croí Y202 | ABS07-32.768KHZ-7-T | 1 | [Abracon source and 3D PDF](https://abracon.com/parametric/crystals/ABS07-32.768KHZ-7-T), [exact UL listing](https://app.ultralibrarian.com/details/4ee6d166-da2b-11ea-b5d0-0aebb021a1ea/Abracon/ABS07-32-768KHZ-7-T). Local generic model is 0.93 mm high, not the specified 0.9 mm envelope. |
| Croí U1701, U1801, U1901 | TPS7A9101DSKR | 3 | [Exact UL listing](https://app.ultralibrarian.com/details/16ba8965-103f-11e9-ab3a-0a3560a4cccc/Texas-Instruments/TPS7A9101DSKR). STEP advertised; not downloaded in this pass. |
| Croí J102 | MPT-08-01-01-L-RA-SD | 1 | [Samtec exact configuration](https://www.samtec.com/products/mpt-08-01-01-l-ra-sd). Manufacturer model download asks for email. |
| Foinse J301 | MPS-08-01-01-L-RA-SD | 1 | [Samtec exact configuration](https://www.samtec.com/products/mps-08-01-01-l-ra-sd). Same download boundary. Both mates need their actual bodies for assembly clearance. |
| Croí J4601 | Amphenol 132134 | 1 | [Manufacturer part](https://www.amphenolrf.com/en-us/part/132134/662/), [STEP entry](https://www.amphenolrf.com/en-us/assets/file/4066919770/). STEP redirects to login. 132134-10/-11 are not this part. |
| Croí U3403 | BMP390 | 1 | [Exact UL listing](https://app.ultralibrarian.com/details/ba78e82b-7764-11ed-b159-0a34d6323d74/Bosch-Sensortec/BMP390). STEP advertised; not downloaded. |
| Croí U1301 | TPSM63603RDHR | 1 | [Exact UL listing](https://app.ultralibrarian.com/details/3d7668b4-5696-11ec-9033-0a34d6323d74/Texas-Instruments/TPSM63603RDHR), [TI source](https://www.ti.com/product/TPSM63603). This is the integrated-inductor power module, not an ordinary QFN. DigiKey's model page returned HTTP 403. |

The follow-up also downloaded EasyEDA candidates for BMP390, TPS1H100, TPS7A91,
ABS07 and the ECS crystal family, but rejected their dimensional/identity
mismatches. TPSM63603's public record has no linked model. Samtec public API
records were unavailable. The Keystone contributor's public repositories did
not yield the announced model. Nano-Fit remains unrecovered. See the follow-up
record above; rows describing earlier attempts remain useful source pointers.

UL's download workflow requires registered/authorized access. No authentication
was bypassed and no browser control was used. An advertised STEP is a located
source, not a recovered or verified file. The efficient remaining acquisition
step is one batch of exact-part STEP downloads from those accounts, then import
and geometry checks; do not repeat the same unauthenticated requests indefinitely.

## Missing footprint and unresolved selections

- **J101 on both boards: Molex 1053111102.** Symbols exist; exact footprint is
  still absent. [Exact UL listing](https://app.ultralibrarian.com/details/84c38e7e-5a2c-11eb-9033-0a34d6323d74/Molex/1053111102?uid=86965558).
  The manufacturer drawing fetch failed previously over HTTP/2; HTTP/1.1 retry
  here timed out. No invented Nano-Fit pads were added.
- **C1403:** the visible electrolytic is still a volume reservation, not a
  selected MPN or qualified retention arrangement. Its existing 3D body is not
  evidence that procurement is complete.
- Passive MPNs/derating, LED selection, physical arm hardware and load-dependent
  DNP/TBD energetic values remain the electrical closure work listed in each
  board's schematic status. Model acquisition does not resolve those choices.
- No separately referenced `L...` component exists in the inspected Croí PCB.
  U1301 contains its inductor. The user's observed missing inductor may refer to
  that module; this identification remains an inference without a reference.

## Deliberately bodyless patterns

Croí has 31 flat signal probes and two Tag-Connect contact patterns. Foinse has
11 flat probes. These 44 footprints do not need permanently soldered component
bodies. Removable fixture access still matters. They are separate from the 40
genuine component-body gaps above.

## SMA placement concern

Seán identified poor soldering/rework access beside an IMU and proposed the edge
near CAN/JST. This is a valid assembly constraint; thermal damage itself has not
been demonstrated. Trial centers around x=174–175, y=184–190 mm collide with
the radio, USB-support parts, CAN connector or ground probe on one or both faces.
No candidate was promoted and the SMA remains at (146.5126, 180.54).

Move the SMA and the necessary neighbouring cells together during the next local
placement pass. Preserve USB-C's accepted location. Check actual solder-tool and
mating access on both faces, RF-route length/reference continuity and cable load
reaction; courtyard non-overlap alone is insufficient. No universal thermal
clearance distance was invented.

## Verification and provenance

- Croí: 634 footprints, 562 resolved model instances; 72 bodyless footprints,
  of which 39 are genuine component-body gaps. Foinse: 100 footprints, 88 models;
  12 bodyless, of which one is a genuine component-body gap.
- Both saved-board checks pass. Croí: 2,235 numbered pads checked; Foinse: 338.
  DRC remains 62 / 24 findings respectively, with existing unrouted and Nano-Fit
  parity findings. No geometric or electrical change is hidden by this pass.
- The before/after parsed PCB trees are identical after removing model entries.
  All schematic files are untouched. Existing warnings remain, not waived.
- Recovery snapshots, source hashes, downloads, measured geometry, native previews
  and bounded scripts: `../../model-recovery-2026-09-07/` from this document.
  Project-local model provenance is also recorded inside each board's libraries.
- [Micro-Fit contribution](https://gitlab.com/kicad/libraries/kicad-packages3D/-/merge_requests/1272),
  commit `3961ea01afd2d7cd61d63e9f4bf24fc0dec699a1`: contributor reports official
  Molex source, alignment, recoloring and a modification to 43045-family geometry.
  Treat as reviewed visual CAD, not manufacturer mechanical certification.
- [Seeed Wio resources](https://wiki.seeedstudio.com/wio_lr2021_introduction/):
  original geometry retained; model offset (-67.51283, 49.848664, -1.52) mm.
- [Vimdrones GNSS assembly source](https://shop.vimdrones.com/products/vimdrones-ublox-m10q-gps):
  exact named component extracted, no carrier board imported. Terminal centers
  match ±6.6 mm rows and 1.9 mm pitch. Model spans 15.5 × 16 × 6.8 mm, including
  residual tabs/maximum-height representation allowed by the u-blox drawing.
  Offset z=-1.195 mm places terminals on the board. Extracted STEP loses colors;
  geometry remains. Redistribution rights need review before public publication.
- [Same Sky buzzer resource](https://www.sameskydevices.com/product/resource/3dmodel/cpt-9019s-smt-tr):
  exact manufacturer download. Native model rotation (-90, 0, 90) degrees and
  offset (-4.5, 4.62, 0) mm align its original CAD axes with this footprint.
- Rejected Boardoza's file advertised as SAM-M10Q: internal component and carrier
  identities explicitly say SAM-M8Q. Also rejected unmatched generic crystal/
  power-package models. Similar filenames are not sufficient evidence.

No release, purchase, communication, Git commit/push or public model redistribution.
