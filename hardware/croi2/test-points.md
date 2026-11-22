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

Stage B2 places each test point beside its net's route, the spanning tree of the net's other pads (step 5);
the pads on the six pyro ADC nodes and `BAT_BLOCK_GATE` go in with their circuit. Stubs to the route
(`output/layout/build.json`, `metrics.tp_stubs`): median 4.2 mm, 6 over 10 mm and 1 over 20 mm; misses against the brief's limits
(10 mm for those with their circuit, 20 mm for the rest): TP36 22.1 mm. TP12–TP14, the spare pads,
moved with their pins to PA9, PA11 and PA12 and took their names (D-22Nov.25).

| TP | Net | Size | x, y (mm) | Sheet |
| --- | --- | --- | --- | --- |
| TP1 | `GND` | black loop (Keystone 5011) | 24.5, 6.5 | 10-test-points |
| TP2 | `LORA_3V3` | yellow loop (Keystone 5194TR, surface mount) | 8.4, 29.5 | 04f-radio-module |
| TP3 | `GNSS_3V3` | yellow loop (Keystone 5194TR, surface mount) | 67.8, 26.1 | 10-test-points |
| TP4 | `SUPERVISOR_WDI` | 1.0 mm pad | 17.3, 71.0 | 10-test-points |
| TP5 | `ADC_PYRO3_CURRENT` | 1.0 mm pad | 29.1, 58.0 | 10-test-points |
| TP6 | `ADC_PYRO1_CONTINUITY` | 1.0 mm pad | 27.6, 29.2 | 10-test-points |
| TP7 | `ADC_PYRO3_CONTINUITY` | 1.0 mm pad | 35.8, 30.7 | 10-test-points |
| TP8 | `NOR_3V3` | yellow loop (Keystone 5194TR, surface mount) | 10.7, 39.4 | 10-test-points |
| TP9 | `ADC_PYRO1_CURRENT` | 1.0 mm pad | 48.3, 32.2 | 10-test-points |
| TP10 | `ADC_PYRO2_CURRENT` | 1.0 mm pad | 44.4, 32.5 | 10-test-points |
| TP11 | `ADC_PYRO2_CONTINUITY` | 1.0 mm pad | 29.1, 64.8 | 10-test-points |
| TP12 | `TP_PA9` | 1.0 mm pad | 52.5, 55.4 | 02a-flight-support |
| TP13 | `TP_PA12` | 1.0 mm pad | 50.8, 48.7 | 02a-flight-support |
| TP14 | `TP_PA11` | 1.0 mm pad | 51.9, 52.0 | 02a-flight-support |
| TP15 | `GNSS_PPS` | yellow loop (Keystone 5194TR, surface mount) | 49.5, 67.8 | 10-test-points |
| TP16 | `GND` | black loop (Keystone 5011) | 10.1, 64.4 | 02flight-reset-debug |
| TP17 | `FLIGHT_BOOT0` | 1.0 mm pad | 27.1, 68.2 | 02flight-reset-debug |
| TP18 | `RESET_MEMORY` | 1.0 mm pad | 52.1, 63.5 | 02a-flight-support |
| TP19 | `TP_STROBE_PAD` | yellow loop (Keystone 5194TR, surface mount) | 53.2, 59.6 | 02a-flight-support |
| TP20 | `USB_VBUS` | yellow loop (Keystone 5194TR, surface mount) | 17.8, 75.9 | 10-test-points |
| TP21 | `STAGING_ARM_SENSE` | 1.0 mm pad | 26.8, 72.4 | 10-test-points |
| TP22 | `RECOVERY_ARM_SENSE` | 1.0 mm pad | 25.5, 92.2 | 10-test-points |
| TP23 | `GND` | black loop (Keystone 5011) | 12.5, 84.5 | 02comms-reset-debug |
| TP24 | `COMMS_BOOT0` | 1.0 mm pad | 20.6, 91.8 | 02comms-reset-debug |
| TP25 | `FLIGHT_3V3` | yellow loop (Keystone 5194TR, surface mount) | 29.4, 92.8 | 01flight-ldo |
| TP26 | `COMMS_LDO_PG` | 1.0 mm pad | 34.8, 101.2 | 10-test-points |
| TP27 | `CORE_HELD_4V` | yellow loop (Keystone 5194TR, surface mount) | 29.7, 100.0 | 01d-held-core |
| TP28 | `FC_POWER_HOLD` | 1.0 mm pad | 43.2, 87.8 | 10-test-points |
| TP29 | `USB_LIMITED` | yellow loop (Keystone 5194TR, surface mount) | 25.6, 100.2 | 10-test-points |
| TP30 | `BOOT_3V3` | yellow loop (Keystone 5194TR, surface mount) | 38.9, 100.5 | 10-test-points |
| TP31 | `COMMS_3V3` | yellow loop (Keystone 5194TR, surface mount) | 37.9, 95.9 | 01comms-ldo |
| TP32 | `OPTIONAL_LDO_PG` | 1.0 mm pad | 50.8, 106.7 | 10-test-points |
| TP33 | `BRANCH_FAULT_N` | 1.0 mm pad | 54.6, 110.1 | 10-test-points |
| TP34 | `CAN_3V3` | yellow loop (Keystone 5194TR, surface mount) | 62.9, 105.4 | 05-can |
| TP35 | `3V3_OPTIONAL` | yellow loop (Keystone 5194TR, surface mount) | 58.9, 108.0 | 01optional-ldo |
| TP36 | `BUCK_PG` | 1.0 mm pad | 23.9, 96.0 | 01c-preregulator |
| TP37 | `LOGIC_SELECTED` | yellow loop (Keystone 5194TR, surface mount) | 33.8, 97.2 | 01c-preregulator |
| TP38 | `FLIGHT_LDO_PG` | 1.0 mm pad | 20.6, 131.2 | 10-test-points |
| TP39 | `4V_PRE` | yellow loop (Keystone 5194TR, surface mount) | 58.5, 113.3 | 01c-preregulator |
| TP40 | `FOINSE_AUX_3V3` | yellow loop (Keystone 5194TR, surface mount) | 60.1, 145.7 | 10-test-points |
| TP41 | `BAT_SOURCE_PG` | 1.0 mm pad | 30.8, 133.7 | 01-power |
| TP42 | `VBAT_CROI_INPUT` | yellow loop (Keystone 5194TR, surface mount) | 14.0, 131.1 | 01-power |
| TP43 | `BAT_BLOCK_GATE` | 1.0 mm pad | 25.9, 134.8 | 01-power |
| TP44 | `BAT_SHDN_N` | 1.0 mm pad | 61.1, 136.3 | 10-test-points |
| TP45 | `BAT_SOURCE_FAULT_N` | 1.0 mm pad | 26.8, 131.2 | 10-test-points |
| TP46 | `VBAT_PROTECTED` | yellow loop (Keystone 5194TR, surface mount) | 53.0, 132.6 | 01-power |
| TP47 | `GND` | black loop (Keystone 5011) | 69.0, 153.5 | 10-test-points |
