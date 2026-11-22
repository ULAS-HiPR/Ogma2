# Burrito test points

**22 November 2026** (D-22Nov.9). Burrito has 47 test points, numbered fore to aft at the
80 × 180 mm placement (capture step 13). The silkscreen shows only the TP number, and the
bottom silkscreen repeats this table.

- **Black loop:** GND only, at the board edges. It's for a scope ground clip.
- **Yellow loop:** each regulator or switch output, the timing strobe and GNSS PPS.
  It's where a probe stays clipped on. Surface mount since D-22Nov.24 (Keystone 5194TR;
  it was the orange through-hole 5003).
- **1.0 mm pad:** nets you only touch with a probe.

No test point goes on a fire net or a line that drives a fire switch (B-02). The scaled
ADC nodes show each channel's state instead.

Positions are board-local in mm: x across from the left edge and y aft from the
forward edge, seen from the top. They come from `output/layout/build.json` and move if
the placement changes. The numbers don't change.

Stage B re-placed the board on 22 November (the 0402s, J101, J103, the silk names and
marks). The positions below are from the 80 × 160 mm build (D-22Nov.21), after capture
step 19's pin swaps (D-22Nov.25). Seán kept the numbers, so most of the 47 no longer run fore to aft. No black loop's
pin sits under the back's fixed blocks, so the legend fits without the hand moves of
22 November. The yellow loops have no pin on the back, so they can go anywhere.

Stage B2 measures each test point's stub to its net's route (`output/layout/build.json`,
`metrics.tp_stubs`): median 8.4 mm, 17 over 10 mm and 3 over 20 mm. TP12–TP14, the
spare pads, moved with their pins to PA9, PA11 and PA12 and took their names (D-22Nov.25).

| TP | Net | Size | x, y (mm) | Sheet |
| --- | --- | --- | --- | --- |
| TP1 | `GND` | black loop (Keystone 5011) | 24.5, 6.5 | 10-test-points |
| TP2 | `LORA_3V3` | yellow loop (Keystone 5194TR, surface mount) | 9.3, 29.6 | 04f-radio-module |
| TP3 | `GNSS_3V3` | yellow loop (Keystone 5194TR, surface mount) | 65.1, 26.1 | 10-test-points |
| TP4 | `SUPERVISOR_WDI` | 1.0 mm pad | 25.9, 70.8 | 10-test-points |
| TP5 | `ADC_PYRO3_CURRENT` | 1.0 mm pad | 50.9, 62.6 | 10-test-points |
| TP6 | `ADC_PYRO1_CONTINUITY` | 1.0 mm pad | 50.9, 47.2 | 10-test-points |
| TP7 | `ADC_PYRO3_CONTINUITY` | 1.0 mm pad | 29.2, 46.5 | 10-test-points |
| TP8 | `NOR_3V3` | yellow loop (Keystone 5194TR, surface mount) | 4.4, 48.2 | 10-test-points |
| TP9 | `ADC_PYRO1_CURRENT` | 1.0 mm pad | 54.0, 54.5 | 10-test-points |
| TP10 | `ADC_PYRO2_CURRENT` | 1.0 mm pad | 52.1, 58.6 | 10-test-points |
| TP11 | `ADC_PYRO2_CONTINUITY` | 1.0 mm pad | 52.5, 50.9 | 10-test-points |
| TP12 | `TP_PA9` | 1.0 mm pad | 55.2, 64.1 | 02a-flight-support |
| TP13 | `TP_PA12` | 1.0 mm pad | 56.1, 60.8 | 02a-flight-support |
| TP14 | `TP_PA11` | 1.0 mm pad | 49.3, 66.0 | 02a-flight-support |
| TP15 | `GNSS_PPS` | yellow loop (Keystone 5194TR, surface mount) | 50.3, 70.1 | 10-test-points |
| TP16 | `GND` | black loop (Keystone 5011) | 10.1, 64.4 | 02flight-reset-debug |
| TP17 | `FLIGHT_BOOT0` | 1.0 mm pad | 28.0, 67.3 | 02flight-reset-debug |
| TP18 | `RESET_MEMORY` | 1.0 mm pad | 54.4, 67.8 | 02a-flight-support |
| TP19 | `TP_STROBE_PAD` | yellow loop (Keystone 5194TR, surface mount) | 18.7, 72.1 | 02a-flight-support |
| TP20 | `USB_VBUS` | yellow loop (Keystone 5194TR, surface mount) | 10.8, 89.8 | 10-test-points |
| TP21 | `STAGING_ARM_SENSE` | 1.0 mm pad | 19.5, 76.0 | 10-test-points |
| TP22 | `RECOVERY_ARM_SENSE` | 1.0 mm pad | 30.9, 91.2 | 10-test-points |
| TP23 | `GND` | black loop (Keystone 5011) | 12.5, 84.5 | 02comms-reset-debug |
| TP24 | `COMMS_BOOT0` | 1.0 mm pad | 22.5, 92.1 | 02comms-reset-debug |
| TP25 | `FLIGHT_3V3` | yellow loop (Keystone 5194TR, surface mount) | 23.9, 98.3 | 01flight-ldo |
| TP26 | `COMMS_LDO_PG` | 1.0 mm pad | 32.2, 95.2 | 10-test-points |
| TP27 | `CORE_HELD_4V` | yellow loop (Keystone 5194TR, surface mount) | 26.7, 93.8 | 01d-held-core |
| TP28 | `FC_POWER_HOLD` | 1.0 mm pad | 51.0, 106.7 | 10-test-points |
| TP29 | `USB_LIMITED` | yellow loop (Keystone 5194TR, surface mount) | 27.9, 98.3 | 10-test-points |
| TP30 | `BOOT_3V3` | yellow loop (Keystone 5194TR, surface mount) | 38.0, 98.8 | 10-test-points |
| TP31 | `COMMS_3V3` | yellow loop (Keystone 5194TR, surface mount) | 36.4, 94.3 | 01comms-ldo |
| TP32 | `OPTIONAL_LDO_PG` | 1.0 mm pad | 54.9, 114.8 | 10-test-points |
| TP33 | `BRANCH_FAULT_N` | 1.0 mm pad | 34.0, 98.5 | 10-test-points |
| TP34 | `CAN_3V3` | yellow loop (Keystone 5194TR, surface mount) | 62.9, 105.3 | 05-can |
| TP35 | `3V3_OPTIONAL` | yellow loop (Keystone 5194TR, surface mount) | 54.9, 111.0 | 01optional-ldo |
| TP36 | `BUCK_PG` | 1.0 mm pad | 58.6, 119.0 | 01c-preregulator |
| TP37 | `LOGIC_SELECTED` | yellow loop (Keystone 5194TR, surface mount) | 57.1, 123.4 | 01c-preregulator |
| TP38 | `FLIGHT_LDO_PG` | 1.0 mm pad | 14.3, 125.8 | 10-test-points |
| TP39 | `4V_PRE` | yellow loop (Keystone 5194TR, surface mount) | 59.0, 115.1 | 01c-preregulator |
| TP40 | `FOINSE_AUX_3V3` | yellow loop (Keystone 5194TR, surface mount) | 60.1, 145.7 | 10-test-points |
| TP41 | `BAT_SOURCE_PG` | 1.0 mm pad | 29.4, 135.6 | 01-power |
| TP42 | `VBAT_CROI_INPUT` | yellow loop (Keystone 5194TR, surface mount) | 14.1, 131.0 | 01-power |
| TP43 | `BAT_BLOCK_GATE` | 1.0 mm pad | 23.9, 132.1 | 01-power |
| TP44 | `BAT_SHDN_N` | 1.0 mm pad | 58.5, 135.4 | 10-test-points |
| TP45 | `BAT_SOURCE_FAULT_N` | 1.0 mm pad | 28.1, 132.2 | 10-test-points |
| TP46 | `VBAT_PROTECTED` | yellow loop (Keystone 5194TR, surface mount) | 45.1, 138.1 | 01-power |
| TP47 | `GND` | black loop (Keystone 5011) | 69.0, 153.5 | 10-test-points |
