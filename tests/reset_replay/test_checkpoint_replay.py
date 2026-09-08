"""Host-only EX-03 checkpoint model. No hardware, flight estimator or outputs.

Assumes ordered, atomic byte writes to two independent logical slots. This is
not an STM32 memory model, firmware record format or qualification test.
"""

from dataclasses import dataclass, replace
import struct
import unittest
import zlib


PAYLOAD = struct.Struct(">BIIIIQBBB")
CRC = struct.Struct(">I")
SLOT_SIZE = 1 + PAYLOAD.size + CRC.size
COMMITTED = 0xA5
MASK = (1 << 32) - 1
HALF_RANGE = 1 << 31
PHASES = range(5)  # Synthetic PAD, BOOST, COAST, DESCENT, LANDED labels.


@dataclass(frozen=True)
class Checkpoint:
    generation: int
    flight_id: int
    profile_id: int
    calibration_id: int
    mission_us: int
    phase: int
    attempted: int = 0
    observed: int = 0

    def body(self):
        payload = PAYLOAD.pack(
            1, self.generation, self.flight_id, self.profile_id,
            self.calibration_id, self.mission_us, self.phase,
            self.attempted, self.observed,
        )
        return payload + CRC.pack(zlib.crc32(payload))


def write_operations(checkpoint):
    """Invalidate the reused slot, write its body, then publish last."""
    return ([(0, 0)] + list(enumerate(checkpoint.body(), start=1))
            + [(0, COMMITTED)])


def write_prefix(slot, checkpoint, count=None):
    operations = write_operations(checkpoint)
    for offset, value in operations[:count]:
        slot[offset] = value


def decode(slot):
    if len(slot) != SLOT_SIZE or slot[0] != COMMITTED:
        return None
    payload = slot[1:1 + PAYLOAD.size]
    if zlib.crc32(payload) != CRC.unpack(slot[-CRC.size:])[0]:
        return None
    version, *fields = PAYLOAD.unpack(payload)
    checkpoint = Checkpoint(*fields)
    if (version != 1 or checkpoint.phase not in PHASES
            or checkpoint.attempted not in (0, 1)
            or checkpoint.observed not in (0, 1)):
        return None
    return checkpoint


def select(slots, identity):
    candidates = [decode(slot) for slot in slots]
    candidates = [cp for cp in candidates if cp is not None and
                  (cp.flight_id, cp.profile_id, cp.calibration_id) == identity]
    if not candidates:
        return None
    newest = candidates[0]
    for cp in candidates[1:]:
        delta = (cp.generation - newest.generation) & MASK
        if delta == HALF_RANGE or (delta == 0 and cp != newest):
            return None  # Ambiguous order or contradictory equal generations.
        if 0 < delta < HALF_RANGE:
            newest = cp
    return newest


def restart_candidate(slots, identity, reset_class, now_us, max_age_us):
    """Return data eligible for further validation, never actuation authority.

    Power validity and mission time are fixture inputs, not inferred hardware
    evidence. Freshness values in tests are synthetic, not flight allocations.
    """
    if reset_class not in ("warm_valid", "main_lost_retention_valid"):
        return None
    if now_us is None or max_age_us < 0:
        return None
    checkpoint = select(slots, identity)
    if checkpoint is None:
        return None
    age = now_us - checkpoint.mission_us
    return checkpoint if 0 <= age <= max_age_us else None


class CheckpointReplayTests(unittest.TestCase):
    identity = (11, 22, 33)

    def checkpoint(self, generation=10, phase=1, **changes):
        return replace(Checkpoint(generation, *self.identity, 100, phase),
                       **changes)

    def slots(self, *checkpoints):
        slots = [bytearray(SLOT_SIZE), bytearray(SLOT_SIZE)]
        for slot, checkpoint in zip(slots, checkpoints):
            write_prefix(slot, checkpoint)
        return slots

    def test_every_update_boundary_at_each_synthetic_phase_transition(self):
        for generation in (10, MASK - 1, MASK):
            for phase in range(4):
                older = self.checkpoint((generation - 1) & MASK, phase)
                previous = self.checkpoint(generation, phase)
                following = self.checkpoint((generation + 1) & MASK,
                                            phase + 1, mission_us=110)
                operations = len(write_operations(following))
                for cut in range(operations + 1):
                    with self.subTest(generation=generation, phase=phase, cut=cut):
                        slots = self.slots(older, previous)
                        write_prefix(slots[0], following, cut)
                        expected = following if cut == operations else previous
                        self.assertEqual(select(slots, self.identity), expected)
                        self.assertEqual(decode(slots[1]), previous)

    def test_first_checkpoint_is_unavailable_until_committed(self):
        cp = self.checkpoint()
        operations = len(write_operations(cp))
        for cut in range(operations + 1):
            slots = self.slots()
            write_prefix(slots[0], cp, cut)
            self.assertEqual(select(slots, self.identity),
                             cp if cut == operations else None)

    def test_each_single_bit_corruption_in_newest_slot_falls_back(self):
        old, new = self.checkpoint(10), self.checkpoint(11)
        for byte in range(SLOT_SIZE):
            for bit in range(8):
                slots = self.slots(old, new)
                slots[1][byte] ^= 1 << bit
                self.assertEqual(select(slots, self.identity), old)

    def test_both_invalid(self):
        self.assertIsNone(select(self.slots(), self.identity))

    def test_identity_mismatch(self):
        for field in ("flight_id", "profile_id", "calibration_id"):
            cp = self.checkpoint(**{field: 999})
            self.assertIsNone(select(self.slots(cp), self.identity))

    def test_sequence_wrap_and_ambiguity(self):
        self.assertEqual(select(self.slots(self.checkpoint(MASK),
                                           self.checkpoint(0)), self.identity),
                         self.checkpoint(0))
        self.assertIsNone(select(self.slots(self.checkpoint(0),
                                           self.checkpoint(HALF_RANGE)), self.identity))
        self.assertIsNone(select(self.slots(self.checkpoint(1),
                                           self.checkpoint(1, phase=2)), self.identity))

    def test_unknown_invalid_or_lost_retention_rejects_intact_bytes(self):
        slots = self.slots(self.checkpoint())
        for reset_class in ("all_power_lost", "brownout_unclassified", "unknown"):
            self.assertIsNone(restart_candidate(slots, self.identity,
                                               reset_class, 110, 20))

    def test_supported_reset_classes_only_return_a_data_candidate(self):
        cp = self.checkpoint()
        for reset_class in ("warm_valid", "main_lost_retention_valid"):
            self.assertEqual(restart_candidate(self.slots(cp), self.identity,
                                               reset_class, 110, 20), cp)

    def test_lost_stale_or_future_time(self):
        slots = self.slots(self.checkpoint())
        for now in (None, 99, 121):
            self.assertIsNone(restart_candidate(slots, self.identity,
                                               "warm_valid", now, 20))

    def test_attempt_is_not_observation(self):
        cp = self.checkpoint(attempted=1, observed=0)
        recovered = restart_candidate(self.slots(cp), self.identity,
                                      "warm_valid", 110, 20)
        self.assertEqual(recovered.attempted, 1)
        self.assertEqual(recovered.observed, 0)

    def test_repeated_restarts_do_not_change_checkpoint(self):
        cp = self.checkpoint()
        slots = self.slots(cp)
        before = [bytes(slot) for slot in slots]
        for _ in range(10):
            self.assertEqual(restart_candidate(slots, self.identity,
                                               "warm_valid", 110, 20), cp)
        self.assertEqual([bytes(slot) for slot in slots], before)

    def test_unknown_format_rejected_even_with_correct_crc(self):
        slot = self.slots(self.checkpoint())[0]
        slot[1] = 2
        slot[-CRC.size:] = CRC.pack(zlib.crc32(slot[1:1 + PAYLOAD.size]))
        self.assertIsNone(decode(slot))


if __name__ == "__main__":
    unittest.main(verbosity=2)
