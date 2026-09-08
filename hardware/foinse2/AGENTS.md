# Foinse2 hardware

Read README.md, schematic-status.md, full-checks.json and board-checks.json.
This is a tracked engineering draft in the Ogma2 monorepo, not manufacturing or flight release.

- No MCU or CAN endpoint. Autonomous source protection cannot depend on Croí,
  I2C, the monitoring ADC or the auxiliary supply starting successfully.
- Keep the 2S avionics and 6S propulsion positive rails separate. Preserve the
  accepted eight-contact Samtec interface and shared-reference architecture.
- Native KiCad files are current working CAD. Scripts may create scratch
  candidates; never overwrite manual schematic edits, placement or routing.
- Keep all active symbol, footprint and model dependencies inside this repo.
  Update library provenance/hashes when intentionally changing a library asset.
- No invented Nano-Fit pads. Charging pinout, actuator converter requirements,
  pack fusing, analog limits and manufacturing review remain open.
- Match schematic and PCB UUID paths, pin nets, DNP and BOM attributes. Rerun the
  local checks after edits. Passing these checks is not hardware qualification.
- Use the parent Ogma2 review branch; do not initialise a nested repository.
  Publication is not purchase, hazardous-test or flight authority.
