"""Step 0, sheet 02-flight-mcu: the flight pad map as amended by the capture specification.

Edits the sheet in place (run from a clean checkout).
Only labels on U201 pins change, plus VBAT (pad 6) leaving FLIGHT_3V3 for FLIGHT_VBAT.
"""
import sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

LIVE = Path(__file__).resolve().parents[3]
CAND = LIVE
SHEET = '02-flight-mcu.kicad_sch'

# pad: (old net, new net, source)
RELABEL = {
    '4':  ('ST_EN', 'FC_POWER_HOLD', 'D-6.3, D-2Nov.18'),
    '5':  ('TDK_EN', 'MAG_INT', 'D-2Nov.11'),
    '26': ('ADC_SERVO_RAIL', 'RESET_MEMORY', 'D-19Nov.3'),
    '35': ('SERVO_POWER_EN', 'TP_STROBE', 'D-19Nov.3'),
    '38': ('PYRO1_HS_REQUEST', 'PYRO1_FIRE', 'D-2Nov.1'),
    '39': ('PYRO1_LS_SELECT', 'SERVICE_POWER_EN', 'D-6.5, D-19Nov.3'),
    '40': ('PYRO2_HS_REQUEST', 'PYRO2_FIRE', 'D-2Nov.1'),
    '41': ('PYRO2_LS_SELECT', 'CAN_STB', 'D-5Nov.3'),
    '43': ('PYRO3_HS_REQUEST', 'PYRO3_FIRE', 'D-7.2'),
    '44': ('PYRO3_LS_SELECT', 'RECOVERY_ARM_SENSE', 'D-5Nov.3'),
    '45': ('RECOVERY_PERMIT', 'STAGE_INHIBIT_LATCHED', 'D-7.2'),
    '46': ('STAGING_PERMIT', 'STAGING_ARM_SENSE', 'D-7.2, D-2Nov.11'),
    '57': ('SERVO3_PWM', 'TP_PD10', 'D-19Nov.3'),
    '61': ('STAGE_INHIBIT_LATCHED', 'PYRO3_LS_SELECT', 'D-2Nov.1'),
    '62': ('NEW_FLIGHT_CLEAR_REQUEST', 'NEW_FLIGHT_CLEAR_REQUEST', 'unchanged'),
    '63': ('SERVO1_PWM', 'TP_PC6', 'D-19Nov.3'),
    '64': ('SERVO2_PWM', 'TP_PC7', 'D-19Nov.3'),
    '65': ('RECOVERY_ARM_SENSE', 'PYRO2_LS_SELECT', 'D-5Nov.3'),
    '66': ('STAGING_ARM_SENSE', 'MAG_SDA', 'D-2Nov.11'),
    '67': ('HG_EN', 'MAG_SCL', 'D-2Nov.11'),
    '68': ('BMP_EN', 'PYRO1_LS_SELECT', 'D-2Nov.1'),
    '69': ('TE_EN', 'CAN2_TX', 'D-5Nov.3'),
    '91': ('CAN_STB', 'CAN2_RX', 'D-5Nov.3'),
}

TEXT = {
    'Allocation: accepted 100-pad CSV. No GPIO reassignment.':
        'Allocation: the 100-pad map as amended by the capture specification, 21 Nov 2026\n'
        '(D-2Nov.1, D-2Nov.11, D-2Nov.18, D-5Nov.3, D-7.2, D-19Nov.2, D-19Nov.3).\n'
        'Pin names and directions: docs/firmware-interface.md.',
    'VBAT is the backup-domain pin, supplied by this MCU domain.':
        'VBAT is the backup-domain pin: FLIGHT_VBAT, from FLIGHT_3V3 through a Schottky\n'
        'with 100 uF hold-up on 02a (D-6.4).',
    'What this does: Runs flight sensing, estimation, mission decisions, recording, outputs and vehicle CAN.':
        'What this does: Runs flight sensing, estimation, mission decisions, recording, outputs and both vehicle CAN buses.',
    'Connects to: Sensor/storage sheets 03*, outputs 06*, CAN 05, monitoring 07*/08 and comms link 04b. Supplies/clocks: 02a. Reset/debug: 02flight-reset-debug.':
        'Connects to: Sensor/storage sheets 03*, outputs 06*, CAN 05, monitoring 07*/08, comms link 04b and the power hold on 01-power. Supplies/clocks/test pads: 02a. Reset/debug: 02flight-reset-debug.',
}


def build():
    t = K.load(LIVE / SHEET)
    pins = K.pin_positions(t, 'U201')

    for pad, (old, new, _) in RELABEL.items():
        pts, used = K.connected_points(t, pins[pad][:2])
        labs = K.labels_at(t, pts)
        assert len(used) == 1 and len(labs) == 1 and labs[0][1] == old, (pad, old, [l[1] for l in labs])
        labs[0][1] = new

    # VBAT (pad 6) leaves the FLIGHT_3V3 bus: drop its bus link and the corner junction at pad 11.
    p6 = pins['6'][:2]
    top = (p6[0], 86.36)
    keep = []
    for w, a, b in K.wires(t):
        if {a, b} == {top, (149.86, 86.36)}:
            continue
        if {a, b} == {p6, top}:
            continue
        keep.append(w)
    t[:] = [x for x in t if not (isinstance(x, list) and x and x[0] == 'wire' and x not in keep)]
    t[:] = [x for x in t if not (isinstance(x, list) and x and x[0] == 'junction' and K.xy(x) == (149.86, 86.36))]
    end = (p6[0], 81.28)
    t.append(K.wire(p6, end, SHEET, 'vbat'))
    t.append(K.global_label('FLIGHT_VBAT', end, 0, SHEET, 'vbat'))

    for node in K.children(t, 'text'):
        for old, new in TEXT.items():
            if old in node[1]:
                node[1] = node[1].replace(old, new)
    K.save(t, CAND / SHEET)


if __name__ == '__main__':
    build()
    print('candidate written:', CAND / SHEET)
