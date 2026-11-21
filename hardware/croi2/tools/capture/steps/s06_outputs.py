"""Step 6, the output sheets and the servo removal.

Capture specification rows: Pyro feed and arm; Staging feed and arm; Recovery channels 1 and 2;
Staging channel 3; Staging reset latch; Servo block (D-6.1, D-6.2, D-7.1, D-7.2, D-2Nov.1, D-2Nov.2,
D-2Nov.14, D-19Nov.2). Edits the sheets in place (run from a clean checkout) and deletes
06d-servo-power.kicad_sch with its root sheet symbol.

Beyond the parts the specification names, this removes what only served them: the logic gates'
own bypass capacitors, R6301 / R6401 (the old request pull-downs: PYROn_FIRE keeps R6303 / R6403),
U6801 and the rest of 06d, R6601-R6607 on the servo nets, and the 08 servo-rail divider.
"""
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
R0603 = 'Resistor_SMD:R_0603_1608Metric'
FUSE_FP = 'Fuse:Fuse_Littelfuse-NANO2-451_453'
SERVO_SHEET_UUID = '004862ed-8fd8-54df-824a-a46ff8ec255a'

FUSE = {'MPN': '0451004.MRL', 'Manufacturer': 'Littelfuse'}             # JLC C27515
GATE = 'SN74LVC1G08DBVR'                                                 # JLC C7666

PYRO = {  # sheet: (n, refs prefix, fire pin, select pin)
    '06pyro1.kicad_sch': (1, '63', 'PE7', 'PA9'),
    '06pyro2.kicad_sch': (2, '64', 'PE9', 'PC8'),
    '06pyro3.kicad_sch': (3, '65', 'PE12', 'PD14'),
}


def retext(t, pairs):
    for old, new in pairs:
        hits = [n for n in K.children(t, 'text') if old in n[1]]
        assert len(hits) == 1, (old, len(hits))
        hits[0][1] = hits[0][1].replace(old, new)


def drop_text(t, *starts):
    for s in starts:
        assert K.remove(t, lambda x: x[0] == 'text' and x[1].startswith(s)) == 1, s


def set_props(sym, dnp=None, **kv):
    pr = {p[1]: p for p in K.children(sym, 'property')}
    for k, v in kv.items():
        if k in pr:
            pr[k][2] = v
        else:
            i = next(i for i, x in enumerate(sym) if isinstance(x, list) and x and x[0] == 'instances')
            sym.insert(i, K.prop(k, v, K.xy(sym)))
    if dnp is not None:
        K.first(sym, 'dnp')[1] = K.A('yes' if dnp else 'no')


def relabel(t, old, new, at=None, angle=None, sheet='', n=None):
    """Rename global labels; with `at`, only the one there (and optionally re-orient it)."""
    hits = [l for l in K.children(t, 'global_label') if l[1] == old and (at is None or K.xy(l) == at)]
    assert hits and (n is None or len(hits) == n), (old, at, len(hits))
    for l in hits:
        if angle is None:
            l[1] = new
        else:                                       # replace, so the justification follows the angle
            i = t.index(l)
            t[i] = K.global_label(new, K.xy(l), angle, sheet, 'relabel')
    return len(hits)


def gate_symbol():
    """KiCad 9.0.7 74xGxx:74LVC1G08, renamed to the TI part, with the house fields."""
    src = [s for s in K.children(K.load(f'{K.KICAD_SYMBOLS}/74xGxx.kicad_sym'), 'symbol') if s[1] == '74LVC1G08'][0]
    sym = copy.deepcopy(src)
    assert not K.first(sym, 'extends')
    sym[1] = GATE
    for sub in K.children(sym, 'symbol'):
        sub[1] = sub[1].replace('74LVC1G08', GATE)
    pr = {p[1]: p for p in K.children(sym, 'property')}
    pr['Value'][2] = GATE
    pr['Footprint'][2] = 'Package_TO_SOT_SMD:SOT-23-5'
    i = sym.index(pr['ki_fp_filters']) + 1
    for k, v in (('MPN', GATE), ('Manufacturer', 'Texas Instruments'),
                 ('Library_Check', 'KiCad 9.0.7 74xGxx:74LVC1G08, renamed. DBV pinout: 1 A, 2 B, 3 GND, 4 Y, 5 VCC '
                                   '(TI SN74LVC1G08 datasheet). Footprint: KiCad Package_TO_SOT_SMD:SOT-23-5, as U2 / U3 gates')):
        sym.insert(i, K.el('property', k, v, K.el('at', K.num(0), K.num(0), K.num(0)), K.fx(1.27, hide=True)))
        i += 1
    return sym


def flag(t, ref, at, sheet):
    K.import_lib(t, 'power:PWR_FLAG', LIB / 'power.kicad_sym')
    x, y = at
    K.make_symbol(t, 'power:PWR_FLAG', ref, at, 0, 'PWR_FLAG', '', sheet,
                  ref_at=(x, y - 7.62), val_at=(x, y - 5.08), justify=None)


# ---------------------------------------------------------------- sheets

def outputs(log):
    """06-outputs: only the staging reset latch stays (D-7.2)."""
    S = '06-outputs.kicad_sch'
    t = K.load(BOARD / S)
    for r in ('U6002', 'U6003', 'U6004', 'U6005', 'C6002', 'C6003', 'C6004', 'C6005', 'R6002', 'R6003', 'R6004'):
        log[r] = K.remove_part(t, r)
    relabel(t, 'STAGE_NEW_FLIGHT_ALLOWED', 'STAGE_ARM_INVALID', n=1)      # U6001 D
    # Q-bar -> R6005 1k -> STAGE_INHIBIT_LATCHED (PE14)
    assert K.remove(t, lambda x: x[0] == 'global_label' and x[1] == 'STAGE_INHIBIT_LATCHED') == 1
    r = K.make_symbol(t, 'Device:R', 'R6005', (148.59, 124.46), 90, '1k', R0603, S,
                      extra={'Implementation_Note': 'Series 1k: a wrongly configured PE14 cannot fight the latch output (D-7.2)'},
                      ref_at=(148.59, 119.38), val_at=(148.59, 121.92), field_angle=90, justify=None)
    assert r['1'][:2] == (144.78, 124.46) and r['2'][:2] == (152.4, 124.46), r
    K.path(t, [(152.4, 124.46), (157.48, 124.46)], S, 'r6005')
    K.add(t, K.global_label('STAGE_INHIBIT_LATCHED', (157.48, 124.46), 180, S, 'r6005'))
    drop_text(t, '2  RECOVERY REQUEST', '3  STAGING REQUEST', 'D = reset released')
    K.add(t, K.text('D = STAGE_ARM_INVALID (U6103 OUTB, 06a): the latch can only be set while staging is disarmed.',
                    (30.48, 187.96), S, 'tD', 1.27))
    retext(t, [
        ('OUTPUT AUTHORITY', 'OUTPUT AUTHORITY / STAGING RESET LATCH'),
        ('Physical-arm assembly/proof-contact pinout remains OPEN, so no energy source is connected here.',
         'Q-bar -> R6005 1k -> PE14. Arm feeds and arm sense: 06a. Channel 3 fires only through U6502 (PYRO3_FIRE AND STAGE_ELIGIBLE), 06pyro3.'),
        ('Combines flight requests with the logic conditions that permit recovery and staging outputs.\n'
         'Connects to: Flight MCU, reset and arm/disarm indications -> 06a and the three channel sheets.',
         'Holds the staging channel inhibited after any flight reset or power-up, until the flight MCU clocks the latch with staging disarmed (D-7.2).\n'
         'Connects to: FLIGHT_NRST, PD15 request and STAGE_ARM_INVALID (06a) -> STAGE_ELIGIBLE to 06pyro3; STAGE_INHIBIT_LATCHED -> PE14.'),
    ])
    K.save(t, BOARD / S)


def arm_boundary(log):
    """06a: the fused arm feeds (D-6.1, D-2Nov.2, D-7.2); the staging permission gates go."""
    S = '06a-arm-boundary.kicad_sch'
    t = K.load(BOARD / S)
    for r in ('U6101', 'U6102', 'U6104', 'C6101', 'C6102', 'C6104'):
        log[r] = K.remove_part(t, r)
    # STAGE_ARM_INVALID straight to R6108 -> PE15 (U6104 inverter gone); label turned to face the empty space
    relabel(t, 'STAGING_ARM_VALID', 'STAGE_ARM_INVALID', at=(370.84, 292.1), angle=0, sheet=S, n=1)
    K.vendor_symbol(LIB / 'Device.kicad_sym', 'Fuse', f'{K.KICAD_SYMBOLS}/Device.kicad_sym')
    K.vendor_footprint(LIB, 'Fuse', 'Fuse_Littelfuse-NANO2-451_453')
    K.import_lib(t, 'Device:Fuse', LIB / 'Device.kicad_sym')
    K.import_lib(t, 'Connector_Generic:Conn_01x02', LIB / 'Connector_Generic.kicad_sym')
    rows = (('F6101', 'J6101', 83.82, 'RECOVERY', 'recovery', 'D-6.1, D-2Nov.2',
             'must not mate Churro J701 (Micro-Fit 430450200) or the GH enable loops'),
            ('F6102', 'J6102', 114.3, 'STAGING', 'staging', 'D-7.2, D-2Nov.2',
             'must not mate J6101, Churro J701 (Micro-Fit 430450200) or the GH enable loops'))
    for f, j, y, NAME, name, why, mate in rows:
        fp = K.make_symbol(t, 'Device:Fuse', f, (63.5, y), 90, '4A fast', FUSE_FP, S,
                           extra={**FUSE, 'Implementation_Note':
                                  f'{name.capitalize()} arm feed from ENERGY_TAP ({why}). NANO2 451, 4 A fast-acting, 50 A breaking (JLC listing). '
                                  'A 2 A firing pulse is half the rating; breaking capacity against the pack fault current to check'},
                           ref_at=(63.5, y - 5.08), val_at=(63.5, y - 2.54), field_angle=90, justify=None)
        assert fp['1'][:2] == (59.69, y) and fp['2'][:2] == (67.31, y), fp
        jp = K.make_symbol(t, 'Connector_Generic:Conn_01x02', j, (93.98, y), 0, f'{name.capitalize()} arm switch (part open)', '', S,
                           extra={'Implementation_Note': f'2-contact connector to the external {name} arm switch ({why}); '
                                                         f'placeholder until the part is chosen: {mate}'})
        assert jp['1'][:2] == (88.9, y) and jp['2'][:2] == (88.9, y + 2.54), jp
        K.add(t, K.global_label('ENERGY_TAP', (50.8, y), 0, S, f'{f}.in'))
        K.path(t, [(50.8, y), (59.69, y)], S, f'{f}.in')
        K.path(t, [(67.31, y), (69.85, y), (88.9, y)], S, f'{f}.out')
        K.add(t, K.local_label(f'{NAME}_ARM_FEED', (69.85, y), 0, S, f))
        K.path(t, [(88.9, y + 2.54), (83.82, y + 2.54), (83.82, y + 10.16), (73.66, y + 10.16)], S, f'{j}.ret')
        K.add(t, K.global_label(f'{NAME}_ARMED_VBAT', (73.66, y + 10.16), 0, S, j))
    K.add(t, K.text('F6101 / F6102: Littelfuse 0451004.MRL, 4 A fast-acting NANO2, one per arm feed so a staging short cannot open recovery\'s fuse (D-2Nov.2).\n'
                    'A 2 A firing pulse is half the rating and cannot open it; both recovery channels at once are 4 A, at the rating.\n'
                    'J6101 / J6102: 2-contact connectors to the external arm switches, placeholders until the part is chosen.\n'
                    'Neither may mate Churro J701 (Micro-Fit 430450200), the GH enable loops or each other.',
                    (40.64, 137.16), S, 'nF', 1.016))
    retext(t, [
        ('PHYSICAL ARM BOUNDARY / UNRESOLVED ASSEMBLY', 'ARM FEEDS / ARM SENSE'),
        ('1  STAGING AUTHORITY: ELIGIBLE LATCH + ARM/REQUEST + RESET', '1  ARM FEEDS: FUSED ENERGY_TAP TO EACH EXTERNAL ARM SWITCH'),
        ('OPEN: keyed arm interface, real energy break, independent disarm proof contact, group protection.',
         'OPEN: the J6101 / J6102 connector parts and the arm switches; F6101 / F6102 breaking capacity against the pack.'),
        ('RECOVERY_ARMED_VBAT / STAGING_ARMED_VBAT have NO board source in this draft.',
         'STAGE_ARM_INVALID (U6103 OUTB) -> R6108 -> PE15, read inverted; it is also the staging latch D input on 06-outputs.'),
        ('Senses armed-rail voltage and combines the conditions for the staging channel.\n'
         'Connects to: 06-outputs eligibility + flight requests + external arm indications -> channel permissions. '
         'The physical arm assembly and its proof contacts are still undefined.',
         'Feeds each pyro group from ENERGY_TAP through its own fuse and external arm switch, and senses the armed voltage.\n'
         'Connects to: ENERGY_TAP (01-power) -> F6101 / F6102 -> J6101 / J6102 -> RECOVERY_ARMED_VBAT (06pyro1, 06pyro2) and '
         'STAGING_ARMED_VBAT (06pyro3); arm sense -> PE13 / PE15.'),
    ])
    K.save(t, BOARD / S)


def pyro(sheet, log):
    """06pyroN: the TPS1H100 high side straight from the MCU (D-6.2); channel 3 through the latch AND (D-7.2)."""
    n, rr, fire_pin, sel_pin = PYRO[sheet]
    t = K.load(BOARD / sheet)
    gone = [f'U{rr}01', f'U{rr}03', f'R{rr}11', f'R{rr}12', f'R{rr}13', f'C{rr}01', f'C{rr}03']
    gone += [f'U{rr}02', f'C{rr}02', f'R{rr}01'] if n < 3 else [f'U{rr}02']
    for r in gone:
        log[r] = K.remove_part(t, r)
    relabel(t, f'PYRO{n}_LS_ENABLE', f'PYRO{n}_LS_SELECT', n=1)          # joined where the select gate was
    if n < 3:
        relabel(t, f'PYRO{n}_HS_ENABLE', f'PYRO{n}_FIRE', n=2)            # U{rr}04 IN, with R{rr}03 pull-down
    else:
        relabel(t, 'PYRO3_HS_REQUEST', 'PYRO3_FIRE', n=1)                 # R6501 pull-down stays
        K.add_lib_symbol(LIB / 'Ogma2.kicad_sym', gate_symbol())
        K.import_lib(t, f'Ogma2:{GATE}', LIB / 'Ogma2.kicad_sym')
        g = K.make_symbol(t, f'Ogma2:{GATE}', 'U6502', (228.6, 106.68), 0, GATE, 'Package_TO_SOT_SMD:SOT-23-5', sheet,
                          extra={'MPN': GATE, 'Manufacturer': 'Texas Instruments',
                                 'Implementation_Note': 'True 2-input AND: PYRO3_FIRE AND STAGE_ELIGIBLE -> PYRO3_HS_ENABLE (D-7.2). '
                                                        'Not the 1G97: its configuration gave A AND NOT B'},
                          ref_at=(233.68, 97.79), val_at=(233.68, 115.57))
        assert (g['1'][:2], g['2'][:2], g['3'][:2], g['4'][:2], g['5'][:2]) == \
            ((213.36, 104.14), (213.36, 109.22), (228.6, 116.84), (241.3, 106.68), (228.6, 96.52)), g
        K.path(t, [(241.3, 106.68), (243.84, 106.68)], sheet, 'u6502.y')
        K.path(t, [(228.6, 96.52), (228.6, 81.28)], sheet, 'u6502.vcc')
        K.path(t, [(228.6, 116.84), (228.6, 121.92)], sheet, 'u6502.gnd')
        K.add(t, K.global_label('GND', (228.6, 121.92), 0, sheet, 'u6502'))
        for net, y in (('PYRO3_FIRE', 104.14), ('STAGE_ELIGIBLE', 109.22)):
            K.path(t, [(213.36, y), (205.74, y)], sheet, f'u6502.{net}')
            K.add(t, K.global_label(net, (205.74, y), 0, sheet, 'u6502'))
    sym = K.symbols(t)
    set_props(sym[f'R{rr}14'], dnp=False, Value='1.24k 1%',
              Implementation_Note='TPS1H100 current limit, about 2.0 A (D-6.2, D-7.1)')
    flag(t, f'#FLG0{21 + n}', (185.42, 251.46), sheet)                       # PYROn_ENERGY: fed through the DNP link
    assert any(K.xy(l) == (163.83, 251.46) and l[1] == f'PYRO{n}_ENERGY' for l in K.children(t, 'global_label'))
    assert any({a, b} == {(163.83, 251.46), (185.42, 251.46)} for w, a, b in K.wires(t))
    who = (f'recovery channel {n}: {fire_pin} drives the high side, {sel_pin} the low side' if n < 3 else
           f'the staging channel: {fire_pin} through the latch AND gate drives the high side, {sel_pin} the low side')
    rail = 'RECOVERY_ARMED_VBAT' if n < 3 else 'STAGING_ARMED_VBAT'
    what = [x for x in K.children(t, 'text') if x[1].startswith('What this does:')]
    assert len(what) == 1
    what[0][1] = (f'What this does: Shows the two switched sides for {who}.\n'
                  f'Connects to: {rail} (06a){", STAGE_ELIGIBLE (06-outputs)" if n == 3 else ""} and the flight MCU '
                  f'-> J6601 load pair on 06b; current report -> 06c. Energy link remains DNP: do not connect an initiator.')
    retext(t, [
        ('1  ONE-SHOT HIGH-SIDE REQUEST / LOAD-SPECIFIC TIMING',
         f'1  HIGH-SIDE REQUEST: PYRO{n}_FIRE DIRECT TO U{rr}04 IN' if n < 3 else '1  HIGH-SIDE REQUEST: PYRO3_FIRE AND STAGE_ELIGIBLE (U6502)'),
        ('Load/pulse/no-fire evidence absent: energy link and timing/current-setting resistors DNP.',
         f'Igniter values open: energy link R{rr}10 stays DNP. R{rr}14 1.24k sets the switch limit near 2.0 A; pulse length is set in firmware (D-6.2).'),
    ])
    K.save(t, BOARD / sheet)


def harness(log):
    """06b: J6602 and the servo PWM / enable resistors go (D-19Nov.2)."""
    S = '06b-output-harness.kicad_sch'
    t = K.load(BOARD / S)
    for r in ('J6602', 'R6601', 'R6602', 'R6603', 'R6604', 'R6605', 'R6606', 'R6607'):
        log[r] = K.remove_part(t, r)
    drop_text(t, '2  THREE SERVO TRIPLETS', 'Each triplet:', 'Servo-enable default.', 'Servo power/PWM boundary',
              'HV servo supply range', 'External physical servo-energy break', 'J6602 NEW 10-way')
    K.add(t, K.text('Servos removed (D-19Nov.2): J6602, its PWM and enable resistors and sheet 06d are gone.', (15.24, 299.72), S, 'nS', 1.27))
    retext(t, [
        ('OUTPUT HARNESSES', 'OUTPUT HARNESS'),
        ('Defines the physical connector contacts for three energetic loads and three servos.', 'Defines the physical connector contacts for three energetic loads.'),
        (' Servo power/PWM on 06d -> J6602.', ''),
    ])
    K.save(t, BOARD / S)


def continuity():
    """06e: the twelve TBD resistors become 3.9k 1%, fitted (D-2Nov.14); 06c's note follows."""
    S = '06e-continuity.kicad_sch'
    t = K.load(BOARD / S)
    sym = K.symbols(t)
    for ch in (1, 2, 3):
        for k in (1, 2, 3, 4):
            s = sym[f'R69{ch}{k}']
            assert K.props(s)['Value'].startswith('TBD') and K.props(s)['Footprint'] == R0603
            set_props(s, dnp=False, Value='3.9k 1%')
        retext(t, [(f'CHANNEL {ch} / NO CREDITED CONTINUITY CAPABILITY', f'CHANNEL {ch} / CONTINUITY: 3.9k TEST AND RETURN')])
    retext(t, [
        ('All four test/return resistors per channel are DNP. No continuity capability is credited.',
         'Test and return resistors 3.9k 1% 0603, fitted (D-2Nov.14): under a tenth of the no-fire current of any igniter rated 25 mA or more.'),
        ('Test resistors remain DNP until load-specific no-fire limits are proved.',
         'Test and return resistors are 3.9k, safe for an igniter with a no-fire current of 25 mA or more.'),
    ])
    K.save(t, BOARD / S)
    S = '06c-output-diagnostics.kicad_sch'
    t = K.load(BOARD / S)
    retext(t, [('Continuity injection DNP; zero is not safe-arm proof.', 'Continuity injection fitted (06e, 3.9k); zero is not safe-arm proof.')])
    K.save(t, BOARD / S)


def rail_adc(log):
    """08: the servo-rail divider goes; TMUX1511 channel 4 is left unused."""
    S = '08-rail-diagnostics.kicad_sch'
    t = K.load(BOARD / S)
    for r in ('R8010', 'R8011', 'R8012', 'C8004'):
        log[r] = K.remove_part(t, r)
    for p in ('11', '12'):
        at = K.pin_positions(t, 'U8001')[p][:2]
        log[f'U8001.{p}'] = K.strip_branch(t, at, 'U8001')
        K.add(t, K.no_connect(at, S, f'u8001.{p}'))
    retext(t, [
        ('All four analog switches enable only with FLIGHT_3V3.',
         'All four analog switches enable only with FLIGHT_3V3; the fourth (pins 11 / 12) is unused since the servos went (D-19Nov.2).'),
        ('Recovery-arm voltage and servo-rail voltage are evidence inputs.', 'Recovery-arm voltage is an evidence input.'),
        ('battery, flight-supply, recovery-arm and servo-supply voltages.', 'battery, flight-supply and recovery-arm voltages.'),
        ('Connects to: Four rails ->', 'Connects to: Three rails ->'),
    ])
    K.save(t, BOARD / S)


def other_text():
    for S, pairs in (('04c-usb-service.kicad_sch', [('power servos/energetic outputs.', 'power energetic outputs.')]),
                     ('07a-battery-monitor.kicad_sch', [('It does not prove that a servo moved or an initiator fired.',
                                                         'It does not prove that an initiator fired.')]),
                     ('09-indicators.kicad_sch', [('PD10 remains servo channel 3; it is not an LED output.',
                                                   'PD10 is a labelled test pad (D-19Nov.3); it is not an LED output.')])):
        t = K.load(BOARD / S)
        retext(t, pairs)
        K.save(t, BOARD / S)


def root():
    """Drop 06d's sheet symbol and its caption; page numbering is redone at close-out."""
    t = K.load(BOARD / 'Croi2.kicad_sch')
    assert K.remove(t, lambda x: x[0] == 'sheet' and K.first(x, 'uuid')[1] == SERVO_SHEET_UUID) == 1
    drop_text(t, 'P39  Servos / protected raw 2S')
    K.save(t, BOARD / 'Croi2.kicad_sch')
    (BOARD / '06d-servo-power.kicad_sch').unlink()


def build():
    log = {}
    outputs(log)
    arm_boundary(log)
    for s in PYRO:
        pyro(s, log)
    harness(log)
    continuity()
    rail_adc(log)
    other_text()
    root()
    return log


if __name__ == '__main__':
    for ref, items in build().items():
        print(ref, len(items))
