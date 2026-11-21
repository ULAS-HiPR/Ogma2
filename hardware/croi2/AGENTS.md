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
  (D-19Nov.2): J6602 and sheet 06d are gone. J6101 / J6102 arm-switch
  connectors are placeholders until their parts are chosen. Igniter values and
  output release remain unresolved. Keep the three DNP energy links
  R6310 / R6410 / R6510 and the other documented DNP safeguards.
- Native KiCad files are current working CAD. Scripts may create scratch
  candidates; never overwrite manual schematic edits, placement or routing.
- Keep active symbols, footprints and models local to this repo. Preserve
  provenance, update intentional library hashes, and rerun native checks.
- J101 (Molex Nano-Fit 1053111102) has no footprint until Molex's drawing is in
  hand: no invented pads and no 105309 substitute. C1403 is selected (Nichicon
  PCW0J102MCO1GS); its land pattern still needs checking against Nichicon's drawing.
- Preserve symbol UUID paths, DNP flags, pad nets and schematic-sheet groups.
- Use the parent Ogma2 review branch; do not initialise a nested repository.
  Publication is not purchase, hazardous-test or flight authority.
