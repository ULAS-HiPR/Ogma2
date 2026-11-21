"""Churro PROP and ACT branch current at 6S: a first estimate for C-02 (21 Nov 2026).

Model estimate only. No valve servo, fin servo or solenoid is chosen yet, so every
input is a (low, central, high) guess. What the branch sees is what the load
converters draw from the 6S pack (Fajita and Salsa convert at the load, D-21Nov.1):

    I_branch = P_load / (efficiency * V_pack)

How a servo draws current:
- Starting a move, the motor is at standstill, so for tens of milliseconds it draws
  close to its stall current, whatever the load.
- Moving against a valve or fin, it draws roughly in proportion to torque. With the
  usual 2x torque margin over the load, that is about half of stall.
- Holding still, it draws its idle current, unless a load pushes back.

Servo sources (stall current at 7.4 V unless stated):
- Hitec DB961WP, 55 kg·cm brushless: 6.5 A (8.0 A at 6.0 V); no-load 0.5 A;
  standing 35 mA. Hitec general specification 502.
- Savox SB-2290SG, 55 kg·cm at 7.4 V, brushless: 9.2 A (10.5 A at 8.4 V);
  idle 5 mA. Savox data sheet.
- Kpower HB80T, 80 kg·cm brushless: 12.3 A (voltage not stated). Kpower page.
- Valve servos: a ball valve at pressure can need several N·m to break away
  (LTS controls review, 6 Oct 2026); 55 kg·cm is about 5.4 N·m.
- Fin servos: the canards team's shortlist (Notion "Servo Shopping") is
  45–80 kg·cm; grid fins under drogue could use smaller ones, hence the lower low.
- Churro's PROP stage today is a TPS2663 eFuse: integrated 31 mΩ FET, current
  limit adjustable 0.6–6 A (TI product page).

Run: python3 docs/calculations/actuator-branch-estimate.py
"""

SERVO_V = 7.4                        # servo rail, converted at the load
EFF = (0.93, 0.90, 0.85)             # converter efficiency; the low case uses the best
V_PACK = 19.5                        # 6S under load, near PROP's 19.92 / 18.63 V start/stop

VALVE_STALL_A = (6.5, 8.0, 12.3)
FIN_STALL_A = (4.0, 8.0, 12.3)
MOVE_FRACTION = (0.35, 0.5, 0.7)     # moving against the load, as a fraction of stall
IDLE_A = (0.005, 0.035, 0.05)
EREG_WORK_A = (1.0, 2.0, 4.0)        # the e-reg servo modulating through a burn
FIN_HOLD_A = (0.2, 0.7, 2.0)         # a fin held at drogue loads (low dynamic pressure)
SOLENOID_W = (6.0, 12.0, 20.0)       # each cold-gas solenoid, held open
FAJITA_LOGIC_W, SALSA_LOGIC_W = 3.0, 2.0

VALVES, FINS = 9, 4
GROUP = (2, 3, 4)                    # valve servos starting together, plus the e-reg


def amps(watts, c):
    return watts / (EFF[c] * V_PACK)


def prop(c):
    n, stall = GROUP[c], VALVE_STALL_A[c]
    move = MOVE_FRACTION[c] * stall
    rest_w = (VALVES - n) * IDLE_A[c] * SERVO_V + FAJITA_LOGIC_W
    together = (n + 1) * stall * SERVO_V + rest_w            # every start overlaps
    staggered = (stall + n * move) * SERVO_V + rest_w        # starts 50 ms or more apart
    sustained = (n + 1) * move * SERVO_V + rest_w
    busy = (EREG_WORK_A[c] + 0.3 * move) * SERVO_V           # e-reg working, a valve 30% of the time
    busy += (VALVES - 1) * IDLE_A[c] * SERVO_V + FAJITA_LOGIC_W
    return [amps(w, c) for w in (together, staggered, sustained, busy)]


def act(c):
    stall = FIN_STALL_A[c]
    move = MOVE_FRACTION[c] * stall
    rest_w = 2 * SOLENOID_W[c] + SALSA_LOGIC_W               # both solenoids open as well
    together = FINS * stall * SERVO_V + rest_w
    staggered = (stall + (FINS - 1) * move) * SERVO_V + rest_w
    sustained = FINS * move * SERVO_V + rest_w
    busy = FINS * FIN_HOLD_A[c] * SERVO_V + SOLENOID_W[c] + SALSA_LOGIC_W   # one solenoid on average
    return [amps(w, c) for w in (together, staggered, sustained, busy)]


if __name__ == '__main__':
    cols = ('start together', 'staggered', 'sustained', 'busy avg')
    print(f'Amps from the 6S pack at {V_PACK} V; servo rail {SERVO_V} V.')
    print('Start figures last tens of ms; sustained lasts a move (0.2-0.5 s).\n')
    for name, fn in (('PROP: 2, 3 or 4 valve servos plus the e-reg', prop), ('ACT: 4 fin servos plus 2 solenoids', act)):
        print(name)
        print(f'{"":9}' + ''.join(f'{h:>16}' for h in cols))
        for c, case in enumerate(('low', 'central', 'high')):
            print(f'{case:9}' + ''.join(f'{v:16.1f}' for v in fn(c)))
        print()
    both = [prop(c)[0] + act(c)[0] for c in range(3)]
    print('Both branches starting together (low, central, high): ' + ', '.join(f'{v:.0f} A' for v in both))
