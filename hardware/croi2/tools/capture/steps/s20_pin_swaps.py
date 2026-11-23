"""Step 20: U201's fire-logic pins, re-dealt so the fire logic's runs don't cross (take 2, D-23Nov.25).

Seán, 23 Nov: "swap U201's pins so the fire pins face the output stage, run ST's pin check"; standing rule D-23Nov.16:
"Do not feel like you can't change pin functions. If you check and it can work, do it."

The output stage is north of U201, beyond its top row (pads 76-100). The fire pins can't face it: A26 keeps them on port
E, and the top row's one port-E pin, PE0 (pad 97), sits beside VCAP (pad 98), a supply pad, which D-22Nov.25's
neighbour rule bars for a fire pin (pad 98 is VCAP, not PE1, on this package; PE2-PE6 on the west side carry trace
outputs). So the fire pins stay on the bottom row's three legal pins, and what can face north does: channel 3's low side
takes PD4, port D being the one other port with a legal top-row pin. Then, west to east, no run crosses another on L3:

- the two low sides at the board's top left leave from the bottom row's west end (PC4, PB1);
- PYRO1_FIRE from PE7, up the lane under U201 that the budget kept, then north-west to U6304 and R6303;
- PYRO3_LS_SELECT north from PD4, between channel 1's high side and channel 2's, to R6504 and R6502;
- PYRO2_FIRE from PE9, under U201 to its east side and north to U6404 and R6403;
- PYRO3_FIRE from PE15, under U201 to its north-east corner and on to U6502.

The moves, a swap and a cycle:
- PYRO2_FIRE PE15 (46) -> PE9 (40); PYRO3_FIRE PE9 -> PE15. The fire pins' neighbours don't change.
- PYRO3_LS_SELECT PC6 (63) -> PD4 (85); PYRO1_LS_SELECT PD4 -> PC4 (33); ADC_FLIGHT_3V3 PC4 -> PB0 (35), ADC1 input 4
  to input 9; FLIGHT_COMMS_EN PB0 -> PC6, its load (U1202, R1205) being south of U201 either way.

Checked by the checker (A24, A25: no pulled-down output on a debug pull-up or bootloader pin, no fire, low-side,
arm-sense or latch net on a bootloader pin; A26, now with D-22Nov.25's whole neighbour rule) and by step 20's check.
Every fire pin is a plain GPIO that wakes as an analog input (no pull) with its 100 kohm pull-down outside, so it stays
low through reset and boot: none is a debug pin (pulls at reset) or a pin the ROM bootloader drives or reads (AN2606).

Edits the flight MCU's sheet in place (the six pins trade labels) and the flight pin map.
"""
import csv
import io
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicadsch as K
from s19_pin_swaps import st_data

BOARD = Path(__file__).resolve().parents[3]
SHEET = '02-flight-mcu.kicad_sch'
MAP = BOARD / 'libraries' / 'inputs' / 'flight-pinout.csv'
FIELDS = ['role', 'mpn', 'pad', 'port_or_supply', 'net', 'function', 'alternate_function', 'notes']
D = 'D-23Nov.25'

# (net, from pad, to pad) on U201
MOVES = [('PYRO2_FIRE', '46', '40'), ('PYRO3_FIRE', '40', '46'),
         ('PYRO3_LS_SELECT', '63', '85'), ('PYRO1_LS_SELECT', '85', '33'), ('ADC_FLIGHT_3V3', '33', '35'),
         ('FLIGHT_COMMS_EN', '35', '63')]
WHY = {
    'PYRO2_FIRE': 'from PE9 its run passes under U201 west of channel 3\'s, to the east side',
    'PYRO3_FIRE': 'PE15 is the fire pin nearest U6502, the east-most target',
    'PYRO3_LS_SELECT': 'PD4 faces the output stage, between channel 1 and channel 2',
    'PYRO1_LS_SELECT': 'from PC4 it joins channel 2\'s low side west of the fire pins',
    'ADC_FLIGHT_3V3': 'a low side takes PC4; PB0 is on the same converter',
    'FLIGHT_COMMS_EN': 'a low side takes PD4',
}


def relabel():
    t = K.load(BOARD / SHEET)
    pins = K.pin_positions(t, 'U201')
    found = {}
    for _, a, b in MOVES:
        for pad in (a, b):
            pts, used = K.connected_points(t, pins[pad][:2])
            labs = K.labels_at(t, pts)
            assert len(labs) == 1, ('U201', pad, [l[1] for l in labs])
            found[pad] = labs[0]
    olds = {pad: lab[1] for pad, lab in found.items()}
    for net, a, b in MOVES:
        assert olds[a] == net, (net, a, olds[a])
        found[b][1] = net
    K.save(t, BOARD / SHEET)


def remap():
    sig, _ = st_data('U201')
    rows = list(csv.DictReader(open(MAP)))
    by_pad = {r['pad']: r for r in rows}
    old = {r['net']: dict(r) for r in rows}
    for net, a, b in MOVES:
        o, r = old[net], by_pad[b]
        assert o['pad'] == a, (net, o)
        f = o['function']
        m = re.match(r'(ADC\d)_INP\d+$', f)
        if m:                                  # the new pin's channel on the same converter
            ch = [s for s in sig[b] if re.match(rf'{m.group(1)}_INP\d+$', s)]
            assert len(ch) == 1, (net, b, ch)
            f = ch[0]
        else:
            assert f == 'GPIO' and 'GPIO' in sig[b], (net, b, f)
        note = f"{o['notes']}; from {o['port_or_supply']} (pad {a}): {WHY[net]} ({D})"
        r.update(net=net, function=f, alternate_function=o['alternate_function'], notes=note)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, quoting=csv.QUOTE_ALL, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    MAP.write_text(buf.getvalue())


if __name__ == '__main__':
    relabel()
    remap()
    print('step 20:', len(MOVES), 'nets moved on U201:', ', '.join(f'{n} {a}->{b}' for n, a, b in MOVES))
