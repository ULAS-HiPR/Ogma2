# Recovered model provenance

Private engineering use; mechanical/assembly qualification remains open.

- J6601/J6602: manufacturer-derived Micro-Fit STEP files from
  https://gitlab.com/kicad/libraries/kicad-packages3D/-/merge_requests/1272,
  commit 3961ea01afd2d7cd61d63e9f4bf24fc0dec699a1. Contributor reports alignment,
  recoloring and a 43045-family modification. Not manufacturer-certified CAD.
- U4606: existing official Seeed Wio-LR2021 STEP. Offset
  (-67.51283,49.848664,-1.52) mm, no rotation or scaling. Source geometry unchanged.
  https://wiki.seeedstudio.com/wio_lr2021_introduction/
- U4504: named SAM-M10Q-00B component extracted from
  https://dev.vimdrones.com/datasheets/vimdrones_gps_ublox_m10q_v1.0.step.
  Offset (0,0,-1.195) mm. 20 terminal centers checked against local footprint;
  15.5 x 16 x 6.8 mm envelope checked against u-blox UBX-22013293 R05 p16.
  Extraction retains geometry but loses colors. Public redistribution rights
  require review. This is third-party CAD, not a u-blox-certified model.
- BZ9001: Same Sky manufacturer download,
  https://3dcadfiles.3dexchange.net/step_ap214/205/8125200/Same_Sky_CPT-9019S-SMT-TR.zip.
  Offset (-4.5,4.62,0) mm, native rotation (-90,0,90) degrees. Two terminal
  seating surfaces aligned with the existing pads; body 9 x 9 mm, height 1.91 mm.
- U503: KiCad 9 TI S-PVSON-N8 package STEP, not a branded TCAN model.
  DRB dimensions/pitch/exposed pad checked against TCAN3413 DRB0008B drawing.
  Existing KiCad library licence applies. Package height modeled at 0.92 mm;
  allocate the manufacturer's 1 mm maximum for mechanical design.

Native PCB/model paths resolve locally. Model additions do not alter pads,
nets, schematic UUIDs, DNP, placement or rule areas. SHA256s are recorded in
board-library-manifest.json. Recovery evidence is in the sibling scratch
directory `model-recovery-2026-09-07` outside the umbrella repository.

Full remaining model/footprint register:
[model recovery report](../../../docs/model-recovery-2026-09-07.md).
