# Burrito: hand-off to Seán (25 November 2026)

From here the board is edited by hand in KiCad (D-25Nov.1). Open `hardware/croi2/Croi2.kicad_pro` (saved by KiCad 9.0.8).
Coordinates below are KiCad's, as the DRC report gives them (the build's board millimetres plus 100, 50).

## What the board is

- `hardware/croi2/Croi2.kicad_pcb`, sha256 `de46421a`. The last scripted board (832b743a, commit ebf6bb5, tag
  `burrito-scripted-final`) plus routing trial d25-832b743a's copper: 3,827 tracks and 1,142 vias (the router's
  routes and the trial fan-out's plane vias), carried over by `tools/layout/keep_routes.py` and refilled.
- The trial routed 292 of 293 signal nets and joined all 623 plane pads. 724 router vias, 7.5 m of track.
- KiCad DRC under the project rules (`Croi2.kicad_dru`): **0 errors, 20 unconnected items**
  (`hardware/croi2/output/pcb-drc.json`):
  - PYRO3_CS_HALF: R6733.1 (145.30, 87.78) to R6735.2 (139.90, 90.58). R6733.1 is boxed in by the router's
    NEW_FLIGHT_CLEAR_REQUEST.
  - FLIGHT_3V3: a track at (113.59, 113.00) to a via at (111.49, 116.03).
  - 18 on the logic feeds, which the trials never routed (spec class LOGIC_FEED):
    - VBAT_PROTECTED 6: R1101, R1103, C1003, TP46, R8001, R1201.
    - 4V_PRE 5: U1401, R1210, C1401, R1401, C1601, U1501, C1501, TP39.
    - LOGIC_SELECTED 5: U1102 pins 1 and 3, U1301, C1104, C1105, TP37.
    - CORE_HELD_4V 2: R1403, TP27, C1403.

## What's locked and why

- 967 of the 5,936 tracks and vias are locked: the spec's scripted copper. That is the fire copper, the armed rails,
  the RF lines, the plane joins, U201's escapes, and the USB and CAN pairs. Unlock to move them. Footprints aren't
  locked.
- 17 rule areas stay on the board: `*_ESCAPE` around the fire-logic parts and the 8 `HOLE*_WASHER` keep-outs. In an
  escape area, fire logic keeps 0.2 mm (D-22Nov.26); elsewhere it keeps 0.5 mm. The DRU reads them.
- `build.py croi2` now refuses to write this board. Build to `--out`, or pass `--overwrite-hand-edits`.

## Numbers that stay

- Fire copper: 1.0 mm wide, 0.5 mm from other nets. These are current and safety values, not fab margin.
- So no via within 0.8 mm of an L3 fire run's centreline, and none on the L6 armed rail's strip (STAGING_ARMED_VBAT,
  2 mm wide at y 87.4: vias at y ≥ 89.125 or ≤ 85.675). DRC enforces both.
- Vias 0.45 / 0.2 mm. JLC's six-layer limits and its part spacing (`tools/layout/engine/place.py`) as they are, with
  no margin added.

## Weak spots

- U6001's cluster (U6001, R6001, R6005, R6735, R6733, C6001): no via fits anywhere near it. The armed rail on L6 and
  the fire logic on L3 close every site.
- CAN, both buses:
  - Each TVS has 9.7 to 13.3 mm of trace to its connector (CAN_H 13.1, CAN_L 10.9, CAN2_H 9.7, CAN2_L 13.3). TI wants
    it at the connector, with two vias on its GND and on the bypass capacitors (SLVSFW5D 9.1, SLLSFS8A 8.5.1).
  - The two blocks are laid out differently.
  - Each pair crosses itself through a via pair. This is inferred from pad positions and not checked against the
    harness: J501 and J502 put CAN H on the outboard row, south of L, while U503 and U505 put H north of L. Turning
    each Gecko 180° puts the bus pins on the inboard row with H north. That gives a straight pair with no vias, but
    it flips the plug's keying.
  - TI 8.4 wants 100 nF at VCC and at VIO. The spec puts bus 1's C505 and C506 both at VIO (C502, 1 µF, at VCC).

## Datasheet asks not yet checked on the board

- TPS709: the output capacitor's GND goes straight to the device's GND pin.
- TPS7A91: the GND pin goes to the thermal pad and not to an external plane (7.4.1.1).
- MMC5983MA: no current-carrying trace under the sensor or opposite it.
- TPS3430: the CRST, CWD and WDO parts sit at their pins.
- TPS2553: RILIM's traces are short.
- SN74LVC1G08 and G97: 8 to 12 mil traces. The board uses 0.09 mm.
- Not read at all: TDK AN-000393 (ICM-42688-P) and ST TN0018 (LSM6DSV32X).

## Not done

- Second vias on the TVS and bypass capacitor grounds.
- Moving D501 and D502.
- Layout references for the 22 parts the reads covered.
- Stop 3: zero unconnected items.

## Getting the scripted board back

- `git show burrito-scripted-final:hardware/croi2/Croi2.kicad_pcb` gives the last scripted board.
  `build.py croi2 --out DIR` at that tag rebuilds it.
- The cloud session couldn't push the tag (HTTP 403). It's in your clone: `git push origin burrito-scripted-final`.
- The datasheets stay in `Claude outputs/2026-11-22-burrito/` on the Mac and never go in the repository.
