# Recording, restart and service

Proposed firmware contract, 22 September 2026, updated for D-6.8 and D-6.9.
Anav owns firmware. See the [recording chapter](../07-sensors-logging.md) and
the [service chapter](../05-service-status-time.md).

## Use one erase sector per commit

Keep the MX66L2G45GMI00 and the 128 KiB staging allocation. One commit is
**fifteen 256-byte data pages and one 256-byte footer**: exactly one 4 KiB erase
sector. The old sixteen-pages-plus-footer unit crossed sector boundaries.
Matching the commit to the erase unit makes recovery and space accounting
simpler, with no extra hardware or second recorder.

Writing rules:

- Program each data page once, then the footer once. Never rewrite a footer.
- Pad a part-filled last data region with 0xFF.
- A sector counts only when its footer is complete and both CRCs match.
- Ignore an interrupted sector. Never repair it in place during acquisition;
  carry on at another verified-erased sector.
- Keep gaps and reset epochs visible when extracting.
- A power cut may lose the unfinished sector and the writer queue. No promise
  otherwise.

| Footer offset | Field | Encoding |
| --- | --- | --- |
| 0 | Magic | Four ASCII bytes `OGM2` |
| 4 | Format version | uint16, starts at 1 |
| 6 | Footer header length | uint16, 32 |
| 8 | Boot epoch | uint64; stored monotonic counter, never taken from GNSS time alone |
| 16 | Sector sequence | uint32 within the epoch |
| 20 | Used data bytes | uint16, 0–3840 |
| 22 | Record count | uint16 |
| 24 | Data CRC | uint32 over all 3840 bytes, including 0xFF padding |
| 28 | Footer CRC | uint32 over bytes 0–27 |
| 32–255 | Reserved | 0xFF |

All integers are little-endian. Both CRCs are CRC-32/ISO-HDLC (reflected
polynomial 0xEDB88320, initial 0xFFFFFFFF, final XOR 0xFFFFFFFF);
`123456789` → 0xCBF43926. The CRC catches corruption; it is not authentication.

Reading rules: reject unknown format versions, impossible lengths or counts, and
duplicate or out-of-order sequences within an epoch. Report gaps and new epochs.
Don't throw away later good sectors just because an interrupted one is missing.

What goes in the records:

- Record types, timestamp compression and sensor packing are firmware's choice,
  inside the byte budget.
- The first committed record names both builds, the profile, configuration and
  calibration hashes, the format schema and the sensor configuration.
- Every stream carries sequence, monotonic sample time, validity and clipping.
  Resets and lost samples are records, never interpolated over.
- An epoch is reserved and verified in an MCU configuration journal before
  recording starts. If that fails, logging is unavailable. No MCU flash erase in
  flight. This is a firmware requirement; no such journal exists yet.

After a restart, don't assume the old RAM write cursor survived. Recover a
cursor only inside the verified prepared region, checking candidate sectors in
bounded background work. Essential acquisition starts on its own. No whole-flash
scan at boot and no speculative overwrite. Until a safe cursor and epoch exist,
report recording unavailable and keep the gap.

## Capacity and preparation

**Recording trigger (D-6.9, 6 October):** full rate from launch detect, with a
RAM pre-trigger. Erase-ahead is allowed only until launch detect. The rest of
this section is the 22 September sizing, which D-6.8 now treats as the Kármán
overlay. The workhorse window will come from measured loads and the vehicle
timeline.

Recording region: **0x00000000–0x0BFFFFFF (192 MiB)**. Leave the last 64 MiB
unallocated. Don't use it to hide budget growth, and don't erase it as a side
effect of preparing the recording region. Use four-byte addressing everywhere
and test reads and writes across 16 MiB and region boundaries.

| Quantity | Bound |
| --- | --- |
| Base records / budget with 20% allowance | 80,560 / 96,672 B/s |
| Extra comms diagnostics | ≤1024 B/s; bounded queue and drop counter |
| Mission ledger + diagnostics + ten-second lead-in | 183,407,936 B |
| Charging sector footers again, to be safe | ceil(183,407,936 / 3840) × 4096 = **195,637,248 B** |
| Left in the 192 MiB region | **5,689,344 B**, before anything new |
| Queue duration at 97,696 B/s | **1.342 s** when empty; real free space sets the margin |
| Adding the magnetometer, 1,600 B/s for 1,810 s (D-2Nov.11) | 186,303,936 B; sector-rounded 198,725,632 B; **2,600,960 B** left; queue 1.320 s |
| Most encoding growth allowed if footers must fit the original 20% | **12.5%** before footers |

The ledger deliberately charges footers twice, where the old allowance already
included them. Session headers, low-rate waiting, aborted attempts and damaged
or skipped sectors must all fit in what's left. Reserve the next full mission
window before reporting the recorder ready. Hours of full-rate logging don't fit.
A rolling RAM history needs its own RAM allocation; the writer queue isn't it.

Preparation:

- Done while disarmed, after old data is extracted or explicitly discarded.
- 64 KiB block erases inside the recording region, blank-checked before use.
  Never erase during acquisition (D-6.9 allows erase-ahead before launch detect).
- At the 2 s worst case per block, all 3072 blocks take **102.4 minutes** plus
  verification. Typical may be faster. Preparation is a deliberate service
  step, not part of flight boot.
- Never use a whole-chip erase; it destroys the reserved area.
- An interrupted preparation resumes only in service mode. One good sample
  write doesn't prove the region is prepared.

## Throughput and independence

At 1.5 ms worst-case page program, sixteen programs take 24 ms for 3840 useful
bytes: **160 kB/s before bus, status and software overhead**. Requirement:
measured sustained useful throughput **≥125 kB/s** while acquiring, including
commit and CRC work, with no unbounded queue growth. That is about 28% above
the 97,696 B/s arrival budget. It's an acceptance target, not a measurement.
Test at the worst clock, temperature and load for the assembly, with write
interruptions, a full region and repeated restarts. A logger failure must never
block essential acquisition or the watchdog.

**No separate comms flash.** Flight NOR takes capped comms diagnostics, so if
flight or the UART is lost, later comms evidence is lost too. A second memory
would only help if comms had to keep its own record through that failure. Keep
receiver identity, packet direction and sequence, local timestamp and reset
epoch. RSSI and SNR are receiver measurements, not evidence about the
transmitter.

**USB download.** Two 4 KiB payload buffers; offset, length, sequence and CRC;
receiver credit. An interrupted download resumes from a verified offset. Reads
never erase or change configuration. At 2 Mbaud 8N1, the full 256 MiB takes at
least 22.4 minutes. Configuration changes only in an explicit ground-service
state, commit atomically and are read back after reboot. Protocol mismatch and
stale flight responses stay visible. A responsive comms MCU can't claim flight
is ready.

## Evidence

- [Macronix Rev 1.1 PDF](https://www.macronix.com/Lists/Datasheet/Attachments/8959/MX66L2G45G%2C%203V%2C%202Gb%2C%20v1.1.pdf):
  the indexed timing table gives 1.5 ms page, 400 ms sector, 2 s 64 KiB block
  and 300 s chip maxima. The full Rev 1.1 file couldn't be downloaded.
- [Rev 1.0 mirror](https://static6.arrow.com/aropdfconversion/5e45eabe6084505d7e235405c4b6448828ec4498/mx66l2g45g203v202gb20v1.0.pdf),
  maker-authored: full command and timing context. Its ordering list is BGA, so
  it isn't claimed as the fitted SOP revision.
- [Recording budget audit](../../archive/power-recording-can-audit-2026-09-11.md),
  [reproducible checks](../../calculations/component-proposal-checks.py).

The exact ordering revision and driver behaviour are checked at capture and
bring-up. The existing pinout is kept. No timing figure here qualifies the part.
