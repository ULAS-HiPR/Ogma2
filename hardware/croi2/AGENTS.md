# Croi2 hardware

Read README.md, schematic-status.md, full-checks.json and board-checks.json.
This is a tracked engineering draft in the Ogma2 monorepo, not manufacturing or flight release.

- Both STM32H563VIT6 physical pin allocations in libraries/inputs are frozen
  at the approved 7 September revision: flight PD10 is now SERVO3_PWM,
  LPTIM2_CH2 AF3; PD7 controls complementary readiness indication.
  Do not silently remap pins or take over Anav's firmware implementation.
- Croí must operate standalone. Flight must complete with comms held in reset.
  The processors separate responsibilities; they are not redundant.
- Preserve the accepted Samtec, CAN and output pinouts. J6602 is now the
  approved ten-contact 430451000: servo triplets 1/2/3, 4/5/6, 7/8/9
  (PWR/PWM/GND), contact10 NC. The old eight-contact pinout is superseded. Physical arm hardware,
  pulse/current/no-fire values and output release remain unresolved. Preserve
  all four DNP output-energy links and other documented DNP safeguards.
- Native KiCad files are current working CAD. Scripts may create scratch
  candidates; never overwrite manual schematic edits, placement or routing.
- Keep active symbols, footprints and models local to this repo. Preserve
  provenance, update intentional library hashes, and rerun native checks.
- The Nano-Fit reservation and C1403 volume allocation are not exact approved
  land patterns/part selections. No invented pads or silently substituted models.
- Preserve symbol UUID paths, DNP flags, pad nets and schematic-sheet groups.
- Use the parent Ogma2 review branch; do not initialise a nested repository.
  Publication is not purchase, hazardous-test or flight authority.
