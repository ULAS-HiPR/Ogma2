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

Stage B re-placed the board on 22 November (the 0402s, J101, J103, the silk names and
marks). The positions below are from that 180 mm build. The numbers were kept, so 31 of
the 47 no longer run fore to aft; [stop 1](../../docs/briefs/burrito-stop1.md) asks
whether to renumber once the length is picked. No loop's pin sits under the back's
fixed blocks, so the legend fits without the hand moves of 22 November.

| TP | Net | Size | x, y (mm) | Sheet |
| --- | --- | --- | --- | --- |
| TP1 | `GND` | black loop (Keystone 5011) | 24.5, 6.5 | 10-test-points |
| TP2 | `LORA_3V3` | orange loop (Keystone 5003) | 11.2, 31.9 | 04f-radio-module |
| TP3 | `GNSS_3V3` | orange loop (Keystone 5003) | 60.4, 25.6 | 10-test-points |
| TP4 | `SUPERVISOR_WDI` | 1.0 mm pad | 12.8, 48.0 | 10-test-points |
| TP5 | `ADC_PYRO3_CURRENT` | 1.0 mm pad | 54.0, 58.6 | 10-test-points |
| TP6 | `ADC_PYRO1_CONTINUITY` | 1.0 mm pad | 21.9, 50.0 | 10-test-points |
| TP7 | `ADC_PYRO3_CONTINUITY` | 1.0 mm pad | 50.8, 55.1 | 10-test-points |
| TP8 | `NOR_3V3` | orange loop (Keystone 5003) | 4.2, 55.4 | 10-test-points |
| TP9 | `ADC_PYRO1_CURRENT` | 1.0 mm pad | 25.9, 50.1 | 10-test-points |
| TP10 | `ADC_PYRO2_CURRENT` | 1.0 mm pad | 50.8, 51.0 | 10-test-points |
| TP11 | `ADC_PYRO2_CONTINUITY` | 1.0 mm pad | 52.4, 62.7 | 10-test-points |
| TP12 | `TP_PC7` | 1.0 mm pad | 51.0, 66.2 | 02a-flight-support |
| TP13 | `TP_PC6` | 1.0 mm pad | 55.0, 66.2 | 02a-flight-support |
| TP14 | `TP_PD10` | 1.0 mm pad | 51.0, 69.7 | 02a-flight-support |
| TP15 | `GNSS_PPS` | orange loop (Keystone 5003) | 48.5, 76.0 | 10-test-points |
| TP16 | `GND` | black loop (Keystone 5011) | 10.2, 73.2 | 02flight-reset-debug |
| TP17 | `FLIGHT_BOOT0` | 1.0 mm pad | 28.0, 71.0 | 02flight-reset-debug |
| TP18 | `RESET_MEMORY` | 1.0 mm pad | 41.5, 74.8 | 02a-flight-support |
| TP19 | `TP_STROBE_PAD` | orange loop (Keystone 5003) | 53.4, 74.1 | 02a-flight-support |
| TP20 | `USB_VBUS` | orange loop (Keystone 5003) | 16.1, 84.8 | 10-test-points |
| TP21 | `STAGING_ARM_SENSE` | 1.0 mm pad | 30.2, 95.8 | 10-test-points |
| TP22 | `RECOVERY_ARM_SENSE` | 1.0 mm pad | 22.9, 87.2 | 10-test-points |
| TP23 | `GND` | black loop (Keystone 5011) | 6.7, 96.0 | 02comms-reset-debug |
| TP24 | `COMMS_BOOT0` | 1.0 mm pad | 17.4, 99.8 | 02comms-reset-debug |
| TP25 | `FLIGHT_3V3` | orange loop (Keystone 5003) | 14.2, 133.8 | 01flight-ldo |
| TP26 | `COMMS_LDO_PG` | 1.0 mm pad | 45.0, 117.0 | 10-test-points |
| TP27 | `CORE_HELD_4V` | orange loop (Keystone 5003) | 14.2, 142.9 | 01d-held-core |
| TP28 | `FC_POWER_HOLD` | 1.0 mm pad | 44.9, 113.2 | 10-test-points |
| TP29 | `USB_LIMITED` | orange loop (Keystone 5003) | 10.0, 116.5 | 10-test-points |
| TP30 | `BOOT_3V3` | orange loop (Keystone 5003) | 49.8, 116.0 | 10-test-points |
| TP31 | `COMMS_3V3` | orange loop (Keystone 5003) | 50.3, 121.6 | 01comms-ldo |
| TP32 | `OPTIONAL_LDO_PG` | 1.0 mm pad | 53.4, 131.8 | 10-test-points |
| TP33 | `BRANCH_FAULT_N` | 1.0 mm pad | 40.6, 115.0 | 10-test-points |
| TP34 | `CAN_3V3` | orange loop (Keystone 5003) | 59.5, 121.7 | 05-can |
| TP35 | `3V3_OPTIONAL` | orange loop (Keystone 5003) | 53.0, 127.7 | 01optional-ldo |
| TP36 | `BUCK_PG` | 1.0 mm pad | 23.9, 116.0 | 01c-preregulator |
| TP37 | `LOGIC_SELECTED` | orange loop (Keystone 5003) | 14.2, 148.2 | 01c-preregulator |
| TP38 | `FLIGHT_LDO_PG` | 1.0 mm pad | 20.1, 148.6 | 10-test-points |
| TP39 | `4V_PRE` | orange loop (Keystone 5003) | 30.2, 149.6 | 01c-preregulator |
| TP40 | `FOINSE_AUX_3V3` | orange loop (Keystone 5003) | 40.0, 160.4 | 10-test-points |
| TP41 | `BAT_SOURCE_PG` | 1.0 mm pad | 35.2, 158.3 | 01-power |
| TP42 | `VBAT_CROI_INPUT` | orange loop (Keystone 5003) | 44.1, 160.0 | 01-power |
| TP43 | `BAT_BLOCK_GATE` | 1.0 mm pad | 24.1, 151.8 | 01-power |
| TP44 | `BAT_SHDN_N` | 1.0 mm pad | 59.8, 154.6 | 10-test-points |
| TP45 | `BAT_SOURCE_FAULT_N` | 1.0 mm pad | 29.5, 155.2 | 10-test-points |
| TP46 | `VBAT_PROTECTED` | orange loop (Keystone 5003) | 34.4, 152.3 | 01-power |
| TP47 | `GND` | black loop (Keystone 5011) | 69.0, 173.5 | 10-test-points |
