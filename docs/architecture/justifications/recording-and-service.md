# Recording, recovery and service — recommendation

22 September 2026. Proposed implementation contract; Anav owns firmware.
[Recording chapter](../07-sensors-logging.md) · [Service chapter](../05-service-status-time.md).

## Use one erase sector per commit

Keep MX66L2G45GMI00 and the 128 KiB staging allocation. Use **fifteen 256-byte
data pages followed by one 256-byte footer**, exactly one 4 KiB erase sector.
The previous sixteen-data-page plus footer unit crossed sector boundaries.
Aligning a commit to an erase unit simplifies recovery and space accounting
without adding hardware or a second recorder.

Program each data page once, then program the footer once. Never rewrite a
programmed footer. A partially filled final data region is padded with 0xFF.
Only a complete footer with matching data/footer CRCs commits a sector. Ignore
an interrupted sector; never repair it in place during acquisition. Resume at
another verified-erased sector. Preserve gaps and reset epochs in extraction.
No promise that a power cut preserves the unfinished sector or writer queue.

| Footer offset | Field | Encoding |
| --- | --- | --- |
| 0 | Magic | Four ASCII bytes `OGM2` |
| 4 | Format version | uint16, initially 1 |
| 6 | Footer header length | uint16, 32 |
| 8 | Boot epoch | uint64; persisted monotonic counter, never derived solely from GNSS time |
| 16 | Sector sequence | uint32 within epoch |
| 20 | Used data bytes | uint16, 0–3840 |
| 22 | Record count | uint16 |
| 24 | Data CRC | uint32 over all 3840 bytes, including 0xFF padding |
| 28 | Footer CRC | uint32 over bytes 0–27 |
| 32–255 | Reserved | 0xFF |

All integers little-endian. Both CRCs use CRC-32/ISO-HDLC (reflected polynomial
0xEDB88320, initial 0xFFFFFFFF, final XOR 0xFFFFFFFF); `123456789` → 0xCBF43926.
CRC detects corruption; it is not authentication. Reject unknown format versions,
impossible lengths/counts and duplicate or out-of-order sequences within an
epoch. Report gaps and new epochs explicitly; do not discard later valid sectors
merely because an interrupted sector is missing.

Record types, timestamp compression and sensor packing remain firmware-owned,
subject to the byte budget. A first committed record identifies both builds,
profile/configuration/calibration hashes, format schema and sensor configuration.
Each stream carries sequence, monotonic sample time, validity and clipping;
reset/lost-sample events are records, not silently interpolated samples.
An epoch is reserved and verified in an MCU configuration journal
before recording; failed reservation makes logging unavailable. No in-flight
MCU-flash erase is introduced. This epoch rule is a firmware requirement, not
a claim that such a journal is already implemented.

A restart cannot assume the former RAM write cursor survived. Recover a cursor
only inside the verified prepared recording region, validating candidate sectors
in bounded background work. Essential acquisition starts independently; no
whole-flash boot scan or speculative overwrite is allowed. Until a safe cursor
and epoch exist, report recording unavailable and preserve the resulting gap.

## Capacity and preparation

Allocate **0x00000000–0x0BFFFFFF (192 MiB)** to recording. Keep the final 64 MiB
unallocated; do not use it to conceal budget growth or erase it as a side effect
of preparing the recording region. Use four-byte addressing throughout and
verify reads/writes across 16 MiB and region boundaries.

| Quantity | Bound |
| --- | --- |
| Base records / budget after 20% allowance | 80,560 / 96,672 B/s |
| Additional comms diagnostics | At most 1024 B/s; bounded queue and drop counter |
| Existing mission ledger + diagnostics + ten-second lead-in | 183,407,936 B |
| Conservatively charge sector footers again | ceil(183,407,936 / 3840) × 4096 = **195,637,248 B** |
| Space remaining within the 192 MiB recording region | **5,689,344 B**, before any newly added use |
| Queue duration at 97,696 B/s | **1.342 s** when empty; actual free space controls margin |
| Maximum encoding expansion if footers must fit the original 20% allowance | **12.5%** before sector footers |

The conservative ledger intentionally charges footer overhead twice where the
old allowance already included it. Session headers, low-rate waiting, aborted
attempts and damaged/skipped sectors must all fit the remaining region. Reserve
the next full mission window before reporting recorder-ready. Full-rate logging
for hours is outside this budget. Use a rolling ten-second RAM history only if
another explicit RAM allocation exists; the writer queue is not that history.
The baseline instead continuously writes prepared space with event markers.

Prepare while disarmed, after explicit extraction/discard of old data. Use
64 KiB block erases within the recording region, blank-check before use and
never erase during acquisition. At the published 2 s maximum per block, all
3072 blocks could take **102.4 minutes**, plus verification. Typical time may be
shorter; preparation is a deliberate service operation, not part of flight boot.
Do not substitute a whole-chip erase that destroys reserved contents. Interrupted
preparation resumes only in service mode; preparation status is not inferred
from one successful sample write.

## Throughput and independence

At a 1.5 ms maximum page-program time, sixteen programs take 24 ms for 3840
useful bytes: **160 kB/s before bus/status/software overhead**. Require measured
sustained useful throughput **≥125 kB/s** concurrently with acquisition, including
commit/CRC work, and no unbounded queue growth. This leaves ~28% over the proposed
97,696 B/s arrival budget; it is an acceptance target, not a measured result.
Exercise maximum clock/temperature/load conditions relevant to the assembly,
write interruptions, a full region and repeated restarts. Logger failure cannot
block essential acquisition or watchdog progress.

No separate comms flash. Flight NOR accepts capped diagnostics; flight/UART loss
therefore loses subsequent comms evidence. A second memory would help only if
independent comms recording were required through that failure. Preserve receiver
identity, packet direction/sequence, local timestamp and reset epoch; RSSI/SNR
are receiver measurements, not transmitter evidence.

USB uses two 4 KiB payload buffers, offset/length/sequence/CRC and receiver credit.
Resume an interrupted download from a verified offset. Reads never erase or
change configuration. At 2 Mbaud 8N1, a full 256 MiB takes at least 22.4 minutes.
Configuration changes occur only in an explicit ground-service state, commit
atomically and read back after reboot. Protocol incompatibility and stale flight
responses remain visible; a responsive comms MCU cannot assert flight readiness.

## Evidence

- [Macronix Rev 1.1 manufacturer PDF](https://www.macronix.com/Lists/Datasheet/Attachments/8959/MX66L2G45G%2C%203V%2C%202Gb%2C%20v1.1.pdf): indexed manufacturer timing table supports 1.5 ms page, 400 ms sector, 2 s 64 KiB erase and 300 s chip maxima. Full Rev 1.1 download was unavailable in this pass.
- [Manufacturer-authored Rev 1.0 PDF mirror inspected](https://static6.arrow.com/aropdfconversion/5e45eabe6084505d7e235405c4b6448828ec4498/mx66l2g45g203v202gb20v1.0.pdf): full command/timing context; its ordering list is BGA, so it is not claimed as the exact fitted SOP ordering revision.
- [Existing recording budget](../../power-recording-can-audit-2026-09-11.md), [current reproducible checks](../../calculations/component-proposal-checks.py).

The exact ordering/revision source and driver operation remain capture/bring-up
checks. Existing geometry/pin mapping is retained; no timing figure constitutes
device qualification.
