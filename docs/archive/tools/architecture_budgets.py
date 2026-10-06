"""Read-only illustrative budgets; not firmware timing or hardware qualification.

Run: python3 tools/architecture_budgets.py
Inputs and limitations: docs/power-recording-can-audit-2026-09-11.md.
Historical 11 September scenarios. Current recording/rail proposal checks:
docs/calculations/component-proposal-checks.py. Do not use this older ledger
or sixteen-data-page scenario as the current capture specification.
"""
import json

KIB = 1024
MIB = KIB * KIB
LOG_BPS = 96_672
MISSION_BYTES = 180_587_776
CAPACITY_BYTES = 256 * MIB
RESERVE_BYTES = 64 * MIB
CAN_BPS = 500_000
STANDARD_FRAME_BITS = 135  # Conservative full frame + intermission allowance.
EXTENDED_FRAME_BITS = 160
BACKGROUND_FPS = 100  # Scenario, not an observed or approved allocation.


def calculate():
    spare = CAPACITY_BYTES - RESERVE_BYTES - MISSION_BYTES
    return {
        'status': 'Historical 11 September scenarios; current proposal checks are docs/calculations/component-proposal-checks.py; not measured performance',
        'hold_up_ms_800uF_204mA': {
            str(v): 800e-6 * v / .204 * 1000 for v in (.1, .25, .5)
        },
        'effective_uF_for_10ms_at_025V_204mA': .204 * .010 / .25 * 1e6,
        'history_seconds_by_KiB': {
            str(k): k * KIB / LOG_BPS for k in (32, 64, 96, 128, 256)
        },
        'history_bytes_by_seconds': {
            str(s): s * LOG_BPS for s in (1, 5, 10, 30, 60)
        },
        'full_rate_30min_bytes': LOG_BPS * 1800,
        'existing_other_mission_allowance_bytes': MISSION_BYTES - LOG_BPS * 1800,
        'remaining_after_mission_and_reserve_bytes': spare,
        'remaining_full_rate_seconds': spare / LOG_BPS,
        'sixteen_data_pages_one_footer': {
            str(lanes): {
                'simplified_service_Bps': 4096 / (17 * .0015 + 17 * 256 * 8 / (16e6 * lanes)),
                'note': 'Excludes command/status/scheduler overhead; no in-flight erase',
            } for lanes in (1, 4)
        },
        'CAN_full_frame_ms': {
            'standard': STANDARD_FRAME_BITS / CAN_BPS * 1000,
            'extended': EXTENDED_FRAME_BITS / CAN_BPS * 1000,
        },
        'CAN_standard_utilisation_percent': {
            str(hz): {
                str(frames): (BACKGROUND_FPS + frames * hz) * STANDARD_FRAME_BITS / CAN_BPS * 100
                for frames in (2, 4, 6)
            } for hz in (100, 200, 500, 1000)
        },
    }


if __name__ == '__main__':
    result = calculate()
    assert result['full_rate_30min_bytes'] == 174_009_600
    assert result['remaining_after_mission_and_reserve_bytes'] == 20_738_816
    assert 1.35 < result['history_seconds_by_KiB']['128'] < 1.36
    assert .98 < result['hold_up_ms_800uF_204mA']['0.25'] < .99
    assert result['CAN_standard_utilisation_percent']['1000']['4'] > 100
    print(json.dumps(result, indent=2))
