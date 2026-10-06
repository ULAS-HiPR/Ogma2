# EX-03 host checkpoint replay

Status: non-actuating executable model of selected checkpoint semantics.
It is not flight firmware, a selected binary record format or MCU qualification.

Run from the repository root with Python 3:

```sh
python3 -B tests/reset_replay/test_checkpoint_replay.py
```

No dependencies, device access, network, hardware outputs or result-file writes.
The script's exit status and assertions are the result, not a simulated flight
success label.

The model assumes two logical slots and ordered atomic byte writes. It writes
an invalid marker, body and CRC, then publishes a commit marker last. It checks
every interruption boundary, including when overwriting an older valid slot,
across four synthetic phase transitions and sequence wrap. It also checks
single-bit corruption, identity mismatch, ambiguous sequence ordering, missing
retention validity, lost/stale/future time, repeated restart and the distinction
between attempted and observed action.

The synthetic phase labels have no flight-detection thresholds. A returned
checkpoint is only a candidate for further state validation. It grants no
actuation or staging authority. The fixture has no actuator API. Its small
integer identities and time/freshness values are test inputs, not mission data
or allocated flight limits.

The model does not test actual RAM/ECC, flash programming granularity, cache or
DMA concurrency, barriers, rail validity, boot code, clock retention, physical
deployment, estimator reconstruction, restart latency or flight firmware. Power
validity and current mission time are supplied as fixture inputs. Both slots
share the simulated retention domain; neither is independent vehicle recovery.

Hardware porting must establish those assumptions or change the implementation.
Use the [reset contract](../../interfaces/reset-recovery-contract.md) and
[RST-01](../../docs/archive/reliability-execution-plan.md#experiment-rst-01-restart-with-known-evidence)
for the wider campaign. Keep numerical pass limits explicit before a hardware
run. A host-model pass does not close EX-03.

## Observed first run — 6 September 2026

All 12 test methods passed, including 420 update-cut subcases across four
synthetic phase transitions and three generation positions, 35 first-write
cut cases, and 264 single-bit slot-corruption cases. A temporary in-memory
mutation removing the initial slot invalidation caused 12 expected failed
subcases and no execution errors. No source mutation was retained.

The failure occurs when a reused slot's old valid marker publishes the new
body before its intended commit step. This checks that the interruption test
detects that particular protocol defect; it is not proof against every defect.

Reproduce the mutation check from the repository root:

```sh
python3 -B - <<'PY'
import io
import runpy
import unittest
m = runpy.run_path('tests/reset_replay/test_checkpoint_replay.py')
original = m['write_operations']
m['write_prefix'].__globals__['write_operations'] = lambda cp: original(cp)[1:]
suite = unittest.TestSuite([m['CheckpointReplayTests'](
    'test_every_update_boundary_at_each_synthetic_phase_transition')])
result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
print('Expected failed subcases:', len(result.failures), 'Errors:', len(result.errors))
assert len(result.failures) == 12 and not result.errors
PY
```
