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
step 18. Seán kept the numbers, so most of the 47 no longer run fore to aft. No black loop's
pin sits under the back's fixed blocks, so the legend fits without the hand moves of
22 November. The yellow loops have no pin on the back, so they can go anywhere.

Stage B2 measures each test point's stub to its net's route (`output/layout/build.json`,
`metrics.tp_stubs`): median 9.2 mm, 21 over 10 mm and 6 over 20 mm.

| TP | Net | Size | x, y (mm) | Sheet |
| --- | --- | --- | --- | --- |
| TP1 | `GND` | black loop (Keystone 5011) | 24.5, 6.5 | 10-test-points |
| TP2 | `LORA_3V3` | yellow loop (Keystone 5194TR, surface mount) | 7.0, 29.6 | 04f-radio-module |
| TP3 | `GNSS_3V3` | yellow loop (Keystone 5194TR, surface mount) | 60.5, 21.7 | 10-test-points |
| TP4 | `SUPERVISOR_WDI` | 1.0 mm pad | 20.8, 73.0 | 10-test-points |
| TP5 | `ADC_PYRO3_CURRENT` | 1.0 mm pad | 50.9, 64.7 | 10-test-points |
| TP6 | `ADC_PYRO1_CONTINUITY` | 1.0 mm pad | 50.8, 47.1 | 10-test-points |
| TP7 | `ADC_PYRO3_CONTINUITY` | 1.0 mm pad | 13.8, 40.0 | 10-test-points |
| TP8 | `NOR_3V3` | yellow loop (Keystone 5194TR, surface mount) | 4.2, 47.5 | 10-test-points |
| TP9 | `ADC_PYRO1_CURRENT` | 1.0 mm pad | 53.9, 57.7 | 10-test-points |
| TP10 | `ADC_PYRO2_CURRENT` | 1.0 mm pad | 53.2, 61.1 | 10-test-points |
| TP11 | `ADC_PYRO2_CONTINUITY` | 1.0 mm pad | 52.3, 51.4 | 10-test-points |
| TP12 | `TP_PC7` | 1.0 mm pad | 54.9, 64.5 | 02a-flight-support |
| TP13 | `TP_PC6` | 1.0 mm pad | 49.6, 68.2 | 02a-flight-support |
| TP14 | `TP_PD10` | 1.0 mm pad | 50.4, 71.5 | 02a-flight-support |
| TP15 | `GNSS_PPS` | yellow loop (Keystone 5194TR, surface mount) | 50.4, 75.7 | 10-test-points |
| TP16 | `GND` | black loop (Keystone 5011) | 10.1, 64.4 | 02flight-reset-debug |
| TP17 | `FLIGHT_BOOT0` | 1.0 mm pad | 10.6, 68.8 | 02flight-reset-debug |
| TP18 | `RESET_MEMORY` | 1.0 mm pad | 16.4, 71.1 | 02a-flight-support |
| TP19 | `TP_STROBE_PAD` | yellow loop (Keystone 5194TR, surface mount) | 68.8, 68.0 | 02a-flight-support |
| TP20 | `USB_VBUS` | yellow loop (Keystone 5194TR, surface mount) | 16.1, 75.5 | 10-test-points |
| TP21 | `STAGING_ARM_SENSE` | 1.0 mm pad | 29.9, 75.2 | 10-test-points |
| TP22 | `RECOVERY_ARM_SENSE` | 1.0 mm pad | 22.8, 79.3 | 10-test-points |
| TP23 | `GND` | black loop (Keystone 5011) | 12.5, 84.5 | 02comms-reset-debug |
| TP24 | `COMMS_BOOT0` | 1.0 mm pad | 24.3, 92.0 | 02comms-reset-debug |
| TP25 | `FLIGHT_3V3` | yellow loop (Keystone 5194TR, surface mount) | 58.3, 121.3 | 01flight-ldo |
| TP26 | `COMMS_LDO_PG` | 1.0 mm pad | 51.6, 102.0 | 10-test-points |
| TP27 | `CORE_HELD_4V` | yellow loop (Keystone 5194TR, surface mount) | 58.6, 126.4 | 01d-held-core |
| TP28 | `FC_POWER_HOLD` | 1.0 mm pad | 47.6, 101.8 | 10-test-points |
| TP29 | `USB_LIMITED` | yellow loop (Keystone 5194TR, surface mount) | 24.4, 98.5 | 10-test-points |
| TP30 | `BOOT_3V3` | yellow loop (Keystone 5194TR, surface mount) | 38.5, 98.3 | 10-test-points |
| TP31 | `COMMS_3V3` | yellow loop (Keystone 5194TR, surface mount) | 54.2, 110.9 | 01comms-ldo |
| TP32 | `OPTIONAL_LDO_PG` | 1.0 mm pad | 57.8, 116.7 | 10-test-points |
| TP33 | `BRANCH_FAULT_N` | 1.0 mm pad | 50.9, 105.3 | 10-test-points |
| TP34 | `CAN_3V3` | yellow loop (Keystone 5194TR, surface mount) | 61.6, 107.7 | 05-can |
| TP35 | `3V3_OPTIONAL` | yellow loop (Keystone 5194TR, surface mount) | 58.1, 112.8 | 01optional-ldo |
| TP36 | `BUCK_PG` | 1.0 mm pad | 62.2, 122.0 | 01c-preregulator |
| TP37 | `LOGIC_SELECTED` | yellow loop (Keystone 5194TR, surface mount) | 62.2, 118.2 | 01c-preregulator |
| TP38 | `FLIGHT_LDO_PG` | 1.0 mm pad | 14.3, 125.8 | 10-test-points |
| TP39 | `4V_PRE` | yellow loop (Keystone 5194TR, surface mount) | 62.6, 126.7 | 01c-preregulator |
| TP40 | `FOINSE_AUX_3V3` | yellow loop (Keystone 5194TR, surface mount) | 60.1, 145.8 | 10-test-points |
| TP41 | `BAT_SOURCE_PG` | 1.0 mm pad | 29.4, 135.6 | 01-power |
| TP42 | `VBAT_CROI_INPUT` | yellow loop (Keystone 5194TR, surface mount) | 14.1, 131.0 | 01-power |
| TP43 | `BAT_BLOCK_GATE` | 1.0 mm pad | 24.7, 132.2 | 01-power |
| TP44 | `BAT_SHDN_N` | 1.0 mm pad | 54.1, 135.8 | 10-test-points |
| TP45 | `BAT_SOURCE_FAULT_N` | 1.0 mm pad | 28.8, 132.2 | 10-test-points |
| TP46 | `VBAT_PROTECTED` | yellow loop (Keystone 5194TR, surface mount) | 33.5, 135.1 | 01-power |
| TP47 | `GND` | black loop (Keystone 5011) | 69.0, 153.5 | 10-test-points |
