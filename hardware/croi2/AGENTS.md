# Croi2 hardware

Read README.md, schematic-status.md, full-checks.json and board-checks.json.
This is a tracked engineering draft in the Ogma2 monorepo, not manufacturing or flight release.

- The MCU pin allocations in libraries/inputs are the as-captured maps of
  21 November 2026 (capture specification, D-21Nov.9), with exact native net
  names: flight STM32H563VIT6 (LQFP100), comms STM32H563RIT6 (LQFP64). The
  7 September versions are in history/baseline-2026-09-08/inputs. Change a pin
  only through a recorded decision; do not take over Anav's firmware.
- Croí must operate standalone. Flight must complete with comms held in reset.
  The processors separate responsibilities; they are not redundant.
- Preserve the accepted Samtec, CAN and output pinouts. No servo outputs
  (D-19Nov.2): J6602 and sheet 06d are gone. J6101 (Mini-Fit Jr.) and
  J6102 (JST VH) are two families so the arm plugs can't cross-mate (D-21Nov.12). Igniter values and
  output release remain unresolved. Keep the three DNP energy links
  R6310 / R6410 / R6510 and the other documented DNP safeguards.
- Native KiCad files are current working CAD. The PCB is the output of the
  layout scripts (D-21Nov.21): change a script and rerun it from a clean state;
  never hand-edit the .kicad_pcb. Never overwrite manual schematic edits.
- Keep active symbols, footprints and models local to this repo. Preserve
  provenance, update intentional library hashes, and rerun native checks.
- J101 (Molex Nano-Fit 105311-1102) uses `Ogma2:105311-1102`, drawn by script
  from Molex's drawing SD-105311-100 rev H (capture step 15, D-22Nov.13); no
  105309 substitute. C1403 is selected (Nichicon PCW0J102MCO1GS); its land
  pattern still needs checking against Nichicon's drawing.
- Preserve symbol UUID paths, DNP flags, pad nets and schematic-sheet groups.
- Use the parent Ogma2 review branch; do not initialise a nested repository.
  Publication is not purchase, hazardous-test or flight authority.
