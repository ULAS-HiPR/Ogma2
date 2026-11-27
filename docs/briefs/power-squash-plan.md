# Burrito power after the 4 V buck: what to delete (plan, not applied)

27 November 2026. Seán approved the gut calls in chat; this note turns them into a parts list. Nothing is
changed in the schematic. Status of each claim: **observed** = read from the sheets on branch `diffpair-names`
(KiCad 10 files, parsed with `tools/capture/kicadsch.py`); **inferred** = my reading, confirm on the sheet.

## Update, 27 Nov evening

Opus's call, agreed by Seán: delete the GNSS and LoRa gates. "No RF on USB" is a power budget, not a safety rule:
U4401 already limits USB at 387-491 mA, and firmware already switches CAN and the sounder off in USB mode. The
reversal section below is kept for the record. Whole stack, candidates from the sheets (confirm each passive):

- `04d-gnss`: U4502 (TPS22918), U4501 (SN74LVC1G97), U4503 (TMUX1511), R4501-R4504, C4502 (1 n, slew), the
  `GNSS_*_ISO`, `GNSS_POWER_EN`, `GNSS_DISCHARGE`, `GNSS_SLEW` nets
- `04e-radio`: U4602 (TPS22918), U4601 (SN74LVC1G97), U4603 and U4604 (TMUX1511), R4601-R4605, C4602 (1 n, slew),
  the `LORA_*_ISO`, `LORA_POWER_EN`, `LORA_DISCHARGE`, `LORA_SLEW` nets
- About 7 ICs and 15 passives. GNSS and radio sit on `COMMS_3V3`; the comms MCU drives their reset and enable pins.
- Bench check before flight: comms MCU at reduced clock + radio standby + GNSS backup on USB, well under 387 mA.

## Pyro sheets, read 27 Nov (observed from the sheets' own notes)

- **06c (current sense): delete the sense, keep the continuity defaults.** What it does: three 750 ohm burdens, dividers
  and 1 n filters into `ADC_PYRO1..3_CURRENT`. The only use is in firmware-interface.md "Fire one channel": after the
  high side goes off, "current sense should fall to zero, if not the high side is stuck on". The response is the same
  with or without it (open the low side, step 4), so it only adds a report. Candidates: R6711-R6713, R6715, C6711,
  R6721-R6723, R6725, C6721, R6731-R6733, R6735, C6731. Keep R6714 / R6724 / R6734 (100 k continuity ADC defaults)
  and C6701. U6701 (TMUX1511, "output ADC boundary"): read what it gates before deleting. Frees three flight ADC pins.
  **Firmware step 3 and `firmware-interface.md` change with it.**
- **06f (continuity isolation): keep.** Opus guessed it existed for the services rail. It does not: U6901 is on
  `FLIGHT_3V3` and its note says it "disconnects [the dividers] from an unpowered flight ADC". The reason is the armed
  rail being present while the flight rail is off, so it survives the services merge. Whether it is needed at all is a
  separate question (the notes say "clamps ... remain open").
- **06e:** the test-current source `3V3_OPTIONAL` (R6911/R6912 and siblings) moves to `FLIGHT_3V3`.

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
| **Delete the two TPS22918 (GNSS, LoRa gates) and the stack that goes with them** | **Go again (Opus, 27 Nov): the reversal below is withdrawn** |
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
- U3602, U3603 TMUX1511PWR (the `*_ISO` signal switches). They exist because NOR could be off while the MCU was on.
  On `FLIGHT_3V3` it never is, so the `*_ISO` nets merge with the plain ones. **Keep** R3605–R3608 (47 k pull-ups on
  NCS, RESET, IO2, IO3: observed, they go to `NOR_3V3`; retarget to `FLIGHT_3V3`), R3609 (22 Ω CLK damping),
  R3610 (reset default), C3603–C3606 (NOR decoupling). Delete with U3601 (observed from the netlist): R3601 (0 Ω link),
  R3602 (EN pull-down), R3603 (output bleeder), R3604 (ILIM set), C3601 (limiter input, on `3V3_OPTIONAL`) and
  C3602 (1 µ, limiter output, on `NOR_3V3`; optional).
- Nets: `NOR_3V3` and the PRELINK/ILIM nets merge into `FLIGHT_3V3`; `NOR_EN` goes (free pin).

**Merge into `FLIGHT_3V3`:** the inputs of U501 and U7001 (they now come from the flight rail), BZ9001 and the
continuity legs (still to find: `3V3_OPTIONAL` appears in `05-can`, `06e-continuity`, `07-churro-aux`, `09-indicators`).

Counted: services 19, NOR 9, GNSS/LoRa stack about 22, pyro current sense 17 = about 65 parts, 3 test points, 12+ nets. The CAN, AUX, buzzer and continuity edits do not remove
parts.

## Checks before applying: answered 27 Nov

1. **LM73100 and C1403 at about 400 mA: the services merge stands.** Observed (TI SNOSDC0A / lm7310 datasheet, §6.5,
   §7.3.4.2): 5.5 A continuous, RON 28.4 mΩ typ / 44.85 mΩ max, no adjustable limit, a fast-trip at 21.9 A that latches
   off. 400 mA costs at most 18 mV and 7 mW; no limiter on the board can push it near 21.9 A (the LDOs limit first).
   Hold-up is what changes (computed, C·ΔV/I with 1000 µF, 4.0 to 3.55 V, ideal capacitance): about 2.25 ms at
   200 mA becomes about 1.1 ms at 400 mA. Those are the allocation ceilings, not measured loads. The repo has no
   written interruption envelope to compare against (the power contract leaves it to EX-01/03), and its own table says
   the hold-up does not bridge a NOR flush anyway. So: not a reason to reverse. Measure the real flight-rail current
   with services on (PWR-01) and size C1403 to the envelope when that exists; a second capacitor is the fix if short.
2. **U6701 (06c) gates only the three current-sense lines** (`PYRO1..3_CS_HALF` to `ADC_PYRO1..3_CURRENT`; channel 4
   unused). It goes with the current sense: U6701 and its bypass C6701, R6711-R6713, R6715 and C6711 for channel 1 and
   the same for channels 2 and 3, test points TP5, TP9, TP10 and U201 pins 15, 16, 17. The continuity defaults
   R6714 / R6724 / R6734 are on U6901's ADC side and stay. **Open:** what to do with each TPS1H100's current-sense
   pin (U6304 / U6404 / U6504 pin 14, now loaded by the 750 Ω burden) when the burden goes: read the datasheet.
3. **The NOR isolators serve only the flight MCU.** Observed from the netlist: every `NOR_*` net connects U201 (flight)
   and the NOR, nothing on the comms MCU. USB readout reaches the comms MCU over the inter-MCU UART, not through the
   NOR bus. Delete U3602 and U3603 as planned. Correction to the first draft of this file: R3605–R3608 are pull-ups
   to keep, not pull-downs to delete.

## Original checks (kept)

1. U1401 (LM73100) current limit and C1403 hold-up at about 400 mA on `FLIGHT_3V3` (flight 200 mA + services 200 mA).
   A CAN or AUX short (≤ 152 mA) on top is about 550 mA on U1701. This could reverse the services merge.
2. Where the buzzer and the continuity legs read `3V3_OPTIONAL` as a reference. Continuity numbers must still hold.
3. Whether the NOR isolators also serve comms-side reads (USB download uses NOR). If so, keep them.
4. After the edit: ERC, then a pin-by-pin netlist diff against `output/full-netlist.xml`.
