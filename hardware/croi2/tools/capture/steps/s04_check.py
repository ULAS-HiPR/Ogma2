"""Check for step 4: the sensor sheets' delta, derived from rules over the step-3 netlist, plus the
magnetometer's pins listed one by one; and the ERC findings the step closes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture as C

SENSORS = {  # sheet path: (prefix, removed parts, sensor-side pull-ups moved to FLIGHT_3V3)
    '/03st-sensor/': ('ST', ['U3101', 'U3102', 'U3103', 'C3101', 'C3103', 'C3104', 'C3105', 'C3106', 'R3102', 'R3103'], ['R3105']),
    '/03tdk-sensor/': ('TDK', ['U3201', 'U3202', 'U3203', 'C3201', 'C3203', 'C3204', 'C3205', 'C3206', 'R3202', 'R3203'], ['R3205']),
    '/03hg-sensor/': ('HG', ['U3301', 'U3302', 'U3303', 'C3301', 'C3303', 'C3304', 'C3305', 'C3306', 'R3302', 'R3303'], ['R3305']),
    '/03bmp-pressure/': ('BMP', ['U3401', 'U3402', 'C3401', 'C3403', 'R3402', 'R3403'], ['R3405', 'R3406']),
    '/03te-pressure/': ('TE', ['U3501', 'U3502', 'C3501', 'C3503', 'R3502', 'R3503'], ['R3505', 'R3506'])}
PREFIXES = tuple(p for p, _, _ in SENSORS.values())
REMOVED = [r for _, rs, _ in SENSORS.values() for r in rs]
PULLUPS = [r for _, _, ps in SENSORS.values() for r in ps]
MAG = {('U3701', '1'): 'MAG_SCL_DAMP', ('U3701', '16'): 'MAG_SDA_DAMP', ('U3701', '15'): 'MAG_INT', ('U3701', '4'): 'MAG_3V3',
       ('U3701', '2'): 'MAG_3V3', ('U3701', '10'): 'MAG_3V3', ('U3701', '13'): 'MAG_3V3', ('U3701', '9'): 'GND', ('U3701', '11'): 'GND',
       ('R3701', '1'): 'FLIGHT_3V3', ('R3701', '2'): 'MAG_3V3',
       ('R3704', '1'): 'MAG_SCL', ('R3704', '2'): 'MAG_SCL_DAMP', ('R3705', '1'): 'MAG_SDA', ('R3705', '2'): 'MAG_SDA_DAMP',
       ('R3702', '1'): 'FLIGHT_3V3', ('R3702', '2'): 'MAG_SCL', ('R3703', '1'): 'FLIGHT_3V3', ('R3703', '2'): 'MAG_SDA'}
MAG.update({(f'C370{i}', '1'): 'MAG_3V3' for i in range(1, 5)})
MAG.update({(f'C370{i}', '2'): 'GND' for i in range(1, 5)})
MAG.update({('U3701', p): 'NC' for p in ('3', '5', '6', '7', '8', '12', '14')})
ADDED = ['U3701', 'R3701', 'R3702', 'R3703', 'R3704', 'R3705', 'C3701', 'C3702', 'C3703', 'C3704']
CLOSES = {"Global Label 'MAG_INT'", "Global Label 'MAG_SCL'", "Global Label 'MAG_SDA'"}


def renamed(net):
    if net.startswith(PREFIXES) and net.endswith('_ISO'):
        return net[:-4]
    if net.startswith(PREFIXES) and net.endswith('_3V3_PRELINK'):
        return 'FLIGHT_3V3'
    return net


if __name__ == '__main__':
    C.export('s04')
    ca, pa = C.load_net('s03')
    expect = dict(MAG)
    for (ref, pin), net in pa.items():
        if ref.startswith('#'):
            continue
        if ref in REMOVED:
            expect[(ref, pin)] = None
            continue
        new = 'FLIGHT_3V3' if (ref in PULLUPS and pin == '1') else renamed(net)
        if new != net:
            expect[(ref, pin)] = new
    changed = {(f'R3{i}01', 'value'): ('0R', '47R 1%') for i in range(1, 6)}
    changed.update({(r, 'value'): (c['value'], c['value'][:-4]) for r, c in ca.items()
                    if r.startswith('TP') and c['sheet'] in SENSORS and c['value'].endswith('_ISO')})
    rep = C.check('s03', 's04', expect, expect_added=ADDED, expect_removed=REMOVED, expect_changed=changed)
    fixed, new, counts = C.erc_delta('s03', 's04')
    print('problems:', rep['problems'] or 'none')
    print('fixed:', fixed); print('new:', new)
    assert not rep['problems'] and {x[3] for x in fixed} == CLOSES and not new
    print('step 4 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;",
          f'ERC closed {len(fixed)}, added 0;', dict(counts))
