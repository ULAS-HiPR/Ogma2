# Burrito power after the 4 V buck: what to delete (plan, not applied)

27 November 2026. Seán approved the gut calls in chat; this note turns them into a parts list. Nothing is
changed in the schematic. Status of each claim: **observed** = read from the sheets on branch `diffpair-names`
(KiCad 10 files, parsed with `tools/capture/kicadsch.py`); **inferred** = my reading, confirm on the sheet.

## Why it is not applied yet

The sheets are KiCad 10 files (`version 20260306`). The cloud session only has KiCad 9.0.8: it refuses them, and
with the version number lowered it loads the sheets but finds zero components. So no netlist or ERC check can run
here. An unchecked edit across 45 hierarchical sheets is not worth the risk. Apply on the Mac, then run ERC and
**Update PCB from Schematic** (the PCB is hand-routed now, so the old layout scripts no longer own it).

## Calls, as approved, with one reversal

| Change | Status |
| --- | --- |
| Delete services limiter U1601 and services LDO U1901, merge `3V3_OPTIONAL` into `FLIGHT_3V3` | Go |
| Delete NOR limiter U3601 and feed NOR from `FLIGHT_3V3` | Go, with the isolators below |
| Keep CAN limiter U501 and AUX limiter U7001 | Go |
| **Delete the two TPS22918 (GNSS, LoRa gates)** | **Reversed: keep** |
| Keep comms limiter U1501 and comms LDO U1801 | Go |

**Why the TPS22918 stay (observed):** the GNSS and LoRa gates are enabled through `CC_BAT_VALID`
(U4501 / U4601 SN74LVC1G97 gate logic). That is what keeps RF and GNSS off when the board runs from USB alone.
power-domains.md: "USB download … no CAN, RF, GNSS or sounder", ≤ 300 mA from VBUS. U1501 only restarts the whole
comms branch, so without the gates the radio and GNSS come on whenever the comms MCU does. Dropping them would
need that rule met some other way (a firmware GPIO is not a hardware limit).

## Parts to delete (observed refs; confirm which passives belong to which block)

**Services regulator, 19 parts** (sheets `01optional-ldo`, `01optional-limit`; sheet files removable once empty):
- U1901 TPS7A9101; C1901–C1906; R1901–R1904; TP35 (`3V3_OPTIONAL` test loop)
- U1601 TPS2553; C1601, C1602; R1601–R1604
- Nets gone: `3V3_OPTIONAL`, `3V3_OPTIONAL_PRELINK`, `OPTIONAL_LDO_*`, `SERVICE_POWER_EN` (PE8 freed)
  and `BRANCH_FAULT_N` on that sheet. Check where else `BRANCH_FAULT_N` is used before removing the net.

**NOR limiter and its isolation** (sheet `03-sensors-storage`; the flash U3604 stays):
- U3601 TPS2553 with its set and filter passives. Inferred: R3601 (0 Ω link), R3604 (set resistor), R3602/R3603 and
  C3601/C3602. Confirm.
- U3602, U3603 TMUX1511PWR (the `*_ISO` signal switches) and, inferred, the pull-downs R3605–R3610. They exist
  because NOR could be off while the MCU was on. On `FLIGHT_3V3` it never is, so the `*_ISO` nets merge with the
  plain ones. Keep R3609 (22 Ω damping) if it is on `NOR_CLK`.
- Nets: `NOR_3V3` and the PRELINK/ILIM nets merge into `FLIGHT_3V3`; `NOR_EN` goes (free pin).

**Merge into `FLIGHT_3V3`:** the inputs of U501 and U7001 (they now come from the flight rail), BZ9001 and the
continuity legs (still to find: `3V3_OPTIONAL` appears in `05-can`, `06e-continuity`, `07-churro-aux`, `09-indicators`).

Counted so far: about 19 + 3 + 2 + 6 = 30 parts and 5–8 nets. The CAN, AUX, buzzer and continuity edits do not remove
parts.

## Checks before applying

1. U1401 (LM73100) current limit and C1403 hold-up at about 400 mA on `FLIGHT_3V3` (flight 200 mA + services 200 mA).
   A CAN or AUX short (≤ 152 mA) on top is about 550 mA on U1701. This could reverse the services merge.
2. Where the buzzer and the continuity legs read `3V3_OPTIONAL` as a reference. Continuity numbers must still hold.
3. Whether the NOR isolators also serve comms-side reads (USB download uses NOR). If so, keep them.
4. After the edit: ERC, then a pin-by-pin netlist diff against `output/full-netlist.xml`.
