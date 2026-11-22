# Burrito test points

**22 November 2026** (D-22Nov.9). Burrito has 47 test points, numbered fore to aft at the
80 × 180 mm placement (capture step 13). The silkscreen shows only the TP number, and the
bottom silkscreen repeats this table.

- **Black loop:** GND only, at the board edges. It's for a scope ground clip.
- **Orange loop:** each regulator or switch output, the timing strobe and GNSS PPS.
  It's where a probe stays clipped on.
- **1.0 mm pad:** nets you only touch with a probe.

No test point goes on a fire net or a line that drives a fire switch (B-02). The scaled
ADC nodes show each channel's state instead.

Positions are board-local in mm: x across from the left edge and y aft from the
forward edge, seen from the top. They come from `output/layout/build.json` and move if
the placement changes. The numbers don't change.

| TP | Net | Size | x, y (mm) | Sheet |
| --- | --- | --- | --- | --- |
| TP1 | `GND` | black loop (Keystone 5011) | 24.5, 6.5 | 10-test-points |
| TP2 | `LORA_3V3` | orange loop (Keystone 5003) | 4.7, 22.0 | 04f-radio-module |
| TP3 | `GNSS_3V3` | orange loop (Keystone 5003) | 60.5, 25.4 | 10-test-points |
| TP4 | `SUPERVISOR_WDI` | 1.0 mm pad | 17.8, 48.0 | 10-test-points |
| TP5 | `ADC_PYRO3_CURRENT` | 1.0 mm pad | 21.8, 47.8 | 10-test-points |
| TP6 | `ADC_PYRO1_CONTINUITY` | 1.0 mm pad | 25.8, 47.9 | 10-test-points |
| TP7 | `ADC_PYRO3_CONTINUITY` | 1.0 mm pad | 50.9, 49.6 | 10-test-points |
| TP8 | `NOR_3V3` | orange loop (Keystone 5003) | 4.4, 53.0 | 10-test-points |
| TP9 | `ADC_PYRO1_CURRENT` | 1.0 mm pad | 50.8, 53.0 | 10-test-points |
| TP10 | `ADC_PYRO2_CURRENT` | 1.0 mm pad | 52.4, 57.1 | 10-test-points |
| TP11 | `ADC_PYRO2_CONTINUITY` | 1.0 mm pad | 53.9, 60.8 | 10-test-points |
| TP12 | `TP_PC7` | 1.0 mm pad | 52.4, 64.3 | 02a-flight-support |
| TP13 | `TP_PC6` | 1.0 mm pad | 52.5, 67.8 | 02a-flight-support |
| TP14 | `TP_PD10` | 1.0 mm pad | 49.4, 71.2 | 02a-flight-support |
| TP15 | `GNSS_PPS` | orange loop (Keystone 5003) | 53.3, 72.5 | 10-test-points |
| TP16 | `GND` | black loop (Keystone 5011) | 8.2, 74.1 | 02flight-reset-debug |
| TP17 | `FLIGHT_BOOT0` | 1.0 mm pad | 14.4, 76.5 | 02flight-reset-debug |
| TP18 | `RESET_MEMORY` | 1.0 mm pad | 43.6, 75.7 | 02a-flight-support |
| TP19 | `TP_STROBE_PAD` | orange loop (Keystone 5003) | 14.6, 81.0 | 02a-flight-support |
| TP20 | `USB_VBUS` | orange loop (Keystone 5003) | 16.1, 86.6 | 10-test-points |
| TP21 | `STAGING_ARM_SENSE` | 1.0 mm pad | 28.2, 91.4 | 10-test-points |
| TP22 | `RECOVERY_ARM_SENSE` | 1.0 mm pad | 29.6, 94.8 | 10-test-points |
| TP23 | `GND` | black loop (Keystone 5011) | 6.8, 97.4 | 02comms-reset-debug |
| TP24 | `COMMS_BOOT0` | 1.0 mm pad | 15.6, 96.4 | 02comms-reset-debug |
| TP25 | `FLIGHT_3V3` | orange loop (Keystone 5003) | 33.8, 108.2 | 01flight-ldo |
| TP26 | `COMMS_LDO_PG` | 1.0 mm pad | 38.9, 109.0 | 10-test-points |
| TP27 | `CORE_HELD_4V` | orange loop (Keystone 5003) | 43.0, 107.7 | 01d-held-core |
| TP28 | `FC_POWER_HOLD` | 1.0 mm pad | 38.9, 112.4 | 10-test-points |
| TP29 | `USB_LIMITED` | orange loop (Keystone 5003) | 28.9, 113.9 | 10-test-points |
| TP30 | `BOOT_3V3` | orange loop (Keystone 5003) | 34.9, 113.2 | 10-test-points |
| TP31 | `COMMS_3V3` | orange loop (Keystone 5003) | 42.9, 112.7 | 01comms-ldo |
| TP32 | `OPTIONAL_LDO_PG` | 1.0 mm pad | 47.5, 113.3 | 10-test-points |
| TP33 | `BRANCH_FAULT_N` | 1.0 mm pad | 49.0, 116.7 | 10-test-points |
| TP34 | `CAN_3V3` | orange loop (Keystone 5003) | 60.4, 121.3 | 05-can |
| TP35 | `3V3_OPTIONAL` | orange loop (Keystone 5003) | 54.9, 124.8 | 01optional-ldo |
| TP36 | `BUCK_PG` | 1.0 mm pad | 57.6, 130.0 | 01c-preregulator |
| TP37 | `LOGIC_SELECTED` | orange loop (Keystone 5003) | 59.7, 135.8 | 01c-preregulator |
| TP38 | `FLIGHT_LDO_PG` | 1.0 mm pad | 14.6, 141.7 | 10-test-points |
| TP39 | `4V_PRE` | orange loop (Keystone 5003) | 63.2, 141.1 | 01c-preregulator |
| TP40 | `FOINSE_AUX_3V3` | orange loop (Keystone 5003) | 26.3, 150.8 | 10-test-points |
| TP41 | `BAT_SOURCE_PG` | 1.0 mm pad | 30.4, 151.6 | 01-power |
| TP42 | `VBAT_CROI_INPUT` | orange loop (Keystone 5003) | 22.2, 152.6 | 01-power |
| TP43 | `BAT_BLOCK_GATE` | 1.0 mm pad | 28.6, 154.9 | 01-power |
| TP44 | `BAT_SHDN_N` | 1.0 mm pad | 58.2, 154.2 | 10-test-points |
| TP45 | `BAT_SOURCE_FAULT_N` | 1.0 mm pad | 35.5, 155.6 | 10-test-points |
| TP46 | `VBAT_PROTECTED` | orange loop (Keystone 5003) | 43.5, 155.7 | 01-power |
| TP47 | `GND` | black loop (Keystone 5011) | 69.0, 173.5 | 10-test-points |
