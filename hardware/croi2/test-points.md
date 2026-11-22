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
marks). The positions below are from the 80 × 160 mm build of the same day (D-22Nov.13),
after capture step 17. Seán kept the numbers, so 43 of the 47 no longer run fore to aft.
No loop's pin sits under the back's fixed blocks, so the legend fits without the hand moves
of 22 November.

At 160 mm the loops have less room beside their circuits: half of them sit within about
16 mm of what they probe (11 mm at 180). TP19 found no spot within 40 mm and went to the
left edge, 43 mm from R203 and R205; the build reports it as `probes_far`.

| TP | Net | Size | x, y (mm) | Sheet |
| --- | --- | --- | --- | --- |
| TP1 | `GND` | black loop (Keystone 5011) | 24.5, 6.5 | 10-test-points |
| TP2 | `LORA_3V3` | orange loop (Keystone 5003) | 6.8, 29.9 | 04f-radio-module |
| TP3 | `GNSS_3V3` | orange loop (Keystone 5003) | 60.7, 21.5 | 10-test-points |
| TP4 | `SUPERVISOR_WDI` | 1.0 mm pad | 20.8, 73.0 | 10-test-points |
| TP5 | `ADC_PYRO3_CURRENT` | 1.0 mm pad | 50.9, 64.7 | 10-test-points |
| TP6 | `ADC_PYRO1_CONTINUITY` | 1.0 mm pad | 50.8, 47.1 | 10-test-points |
| TP7 | `ADC_PYRO3_CONTINUITY` | 1.0 mm pad | 13.8, 40.0 | 10-test-points |
| TP8 | `NOR_3V3` | orange loop (Keystone 5003) | 4.2, 47.1 | 10-test-points |
| TP9 | `ADC_PYRO1_CURRENT` | 1.0 mm pad | 53.9, 57.7 | 10-test-points |
| TP10 | `ADC_PYRO2_CURRENT` | 1.0 mm pad | 53.2, 61.1 | 10-test-points |
| TP11 | `ADC_PYRO2_CONTINUITY` | 1.0 mm pad | 52.3, 51.4 | 10-test-points |
| TP12 | `TP_PC7` | 1.0 mm pad | 54.9, 64.5 | 02a-flight-support |
| TP13 | `TP_PC6` | 1.0 mm pad | 49.6, 68.2 | 02a-flight-support |
| TP14 | `TP_PD10` | 1.0 mm pad | 50.4, 71.5 | 02a-flight-support |
| TP15 | `GNSS_PPS` | orange loop (Keystone 5003) | 76.0, 53.5 | 10-test-points |
| TP16 | `GND` | black loop (Keystone 5011) | 10.1, 64.4 | 02flight-reset-debug |
| TP17 | `FLIGHT_BOOT0` | 1.0 mm pad | 10.6, 68.8 | 02flight-reset-debug |
| TP18 | `RESET_MEMORY` | 1.0 mm pad | 16.4, 71.1 | 02a-flight-support |
| TP19 | `TP_STROBE_PAD` | orange loop (Keystone 5003) | 9.7, 41.4 | 02a-flight-support |
| TP20 | `USB_VBUS` | orange loop (Keystone 5003) | 10.7, 90.0 | 10-test-points |
| TP21 | `STAGING_ARM_SENSE` | 1.0 mm pad | 29.9, 75.2 | 10-test-points |
| TP22 | `RECOVERY_ARM_SENSE` | 1.0 mm pad | 22.8, 79.3 | 10-test-points |
| TP23 | `GND` | black loop (Keystone 5011) | 12.5, 84.5 | 02comms-reset-debug |
| TP24 | `COMMS_BOOT0` | 1.0 mm pad | 24.3, 92.0 | 02comms-reset-debug |
| TP25 | `FLIGHT_3V3` | orange loop (Keystone 5003) | 25.8, 132.3 | 01flight-ldo |
| TP26 | `COMMS_LDO_PG` | 1.0 mm pad | 51.1, 107.2 | 10-test-points |
| TP27 | `CORE_HELD_4V` | orange loop (Keystone 5003) | 29.7, 132.3 | 01d-held-core |
| TP28 | `FC_POWER_HOLD` | 1.0 mm pad | 47.6, 101.8 | 10-test-points |
| TP29 | `USB_LIMITED` | orange loop (Keystone 5003) | 12.2, 104.2 | 10-test-points |
| TP30 | `BOOT_3V3` | orange loop (Keystone 5003) | 51.6, 103.2 | 10-test-points |
| TP31 | `COMMS_3V3` | orange loop (Keystone 5003) | 15.8, 91.9 | 01comms-ldo |
| TP32 | `OPTIONAL_LDO_PG` | 1.0 mm pad | 54.2, 112.0 | 10-test-points |
| TP33 | `BRANCH_FAULT_N` | 1.0 mm pad | 40.4, 100.5 | 10-test-points |
| TP34 | `CAN_3V3` | orange loop (Keystone 5003) | 74.0, 119.9 | 05-can |
| TP35 | `3V3_OPTIONAL` | orange loop (Keystone 5003) | 14.2, 126.9 | 01optional-ldo |
| TP36 | `BUCK_PG` | 1.0 mm pad | 58.2, 122.2 | 01c-preregulator |
| TP37 | `LOGIC_SELECTED` | orange loop (Keystone 5003) | 12.1, 132.5 | 01c-preregulator |
| TP38 | `FLIGHT_LDO_PG` | 1.0 mm pad | 20.1, 131.2 | 10-test-points |
| TP39 | `4V_PRE` | orange loop (Keystone 5003) | 33.6, 134.4 | 01c-preregulator |
| TP40 | `FOINSE_AUX_3V3` | orange loop (Keystone 5003) | 11.2, 150.8 | 10-test-points |
| TP41 | `BAT_SOURCE_PG` | 1.0 mm pad | 39.4, 141.2 | 01-power |
| TP42 | `VBAT_CROI_INPUT` | orange loop (Keystone 5003) | 10.2, 145.3 | 01-power |
| TP43 | `BAT_BLOCK_GATE` | 1.0 mm pad | 56.2, 131.8 | 01-power |
| TP44 | `BAT_SHDN_N` | 1.0 mm pad | 54.1, 135.8 | 10-test-points |
| TP45 | `BAT_SOURCE_FAULT_N` | 1.0 mm pad | 16.1, 131.3 | 10-test-points |
| TP46 | `VBAT_PROTECTED` | orange loop (Keystone 5003) | 12.2, 138.1 | 01-power |
| TP47 | `GND` | black loop (Keystone 5011) | 69.0, 153.5 | 10-test-points |
