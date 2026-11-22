"""Step 19: MCU pin swaps for the placement (stage B2 step 7, D-22Nov.25).

Seán, 22 Nov: "yes you may swap any pin you want so long as it's justified and verified and documented".

`tools/layout/pinswap.py` chose the moves below on the placed 160 mm board, in two rounds with a re-place between
(project log, 22 Nov). Each net moves only where ST's pin data (libraries/inputs/st-open-pin-data, STM32_open_pin_data
45c0459) says the new pin carries its function: GPIO to GPIO, an ADC input to a pin on the same converter, a peripheral
signal to another pin with the same signal. This step takes each new ADC channel and AF number from the same data.

The rules the search kept, and why:
- The fault the brief asked to verify first holds. After reset PA15 is JTDI with an internal pull-up, as are PA13 and
  PB4 (DS14258 rev 6, table 14, note 7), of 30-50 kohm (table 58). Against R7002's 100 kohm that holds
  FOINSE_RETURN_EN at 2.2-2.5 V from reset until firmware drives PA15: over the TPS2553's 1.1 V enable threshold
  (SLVS841G) and the TMUX1511's 1.2 V select threshold (SCDS390B), so U7001 powered Foinse's aux rail and U7002
  joined its I2C and fault lines at every power-up. It moves off PA15.
- The ROM bootloader drives some pins (AN2606 rev 70, table 137): USART1 TX on PA9 held PYRO1_LS_SELECT, USB on PA11
  and PA12 held NOR_EN and FLIGHT_COMMS_EN. They move; the three spare test pads take those pins, a pad and nothing
  else, and are renamed for them.
- No pulled-down output sits on a pulled-up debug pin or a pin the bootloader drives; no fire, low-side, arm-sense or
  staging-latch net sits on any bootloader pin; the fire pins stay on port E and the low-side selects on three other
  ports; no fire pin or low-side select is beside another, an arm sense, the staging latch or the new-flight request
  (as captured, PE12 sat beside PE13 and PD14 beside PD15); and none of them is on a pin with a trace, debug-trigger,
  tamper, RTC_OUT or LSCO output. The checker holds each (A24-A26).

Edits the MCU sheets in place: U201's moves trade labels; on U401's sheet six nets move onto pins that had no-connect
flags and six pins they leave get one. Then the three spare pads' labels and values, and the two pin maps.
"""
import csv
import io
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
INPUTS = BOARD / 'libraries' / 'inputs'
ST = INPUTS / 'st-open-pin-data'
SHEETS = {'U201': '02-flight-mcu.kicad_sch', 'U401': '04-comms-gnss-radio.kicad_sch'}
MAPS = {'U201': INPUTS / 'flight-pinout.csv', 'U401': INPUTS / 'comms-pinout.csv'}
XMLS = {'U201': ST / 'STM32H563VITx.xml', 'U401': ST / 'STM32H563RITx.xml'}
FIELDS = ['role', 'mpn', 'pad', 'port_or_supply', 'net', 'function', 'alternate_function', 'notes']
D = 'D-22Nov.25'
SPARE = re.compile(r'^TP_P[A-K]\d+$')           # a spare test pad, named for its pin (D-19Nov.3)

# (net, from pad, to pad): pinswap.py's moves, against the as-captured maps
MOVES = {
    'U201': [
        ('NOR_EN', '70', '2'), ('SUPERVISOR_WDI', '85', '3'), ('BRANCH_FAULT_N', '86', '4'),
        ('NOR_RESET_REQUEST', '84', '5'), ('ADC_PYRO3_CONTINUITY', '34', '23'), ('ADC_PYRO2_CONTINUITY', '33', '24'),
        ('NOR_CLK', '37', '26'), ('RESET_MEMORY', '26', '29'), ('ADC_FLIGHT_3V3', '24', '33'),
        ('ADC_VEHICLE_VBAT', '23', '34'), ('FLIGHT_COMMS_EN', '71', '35'), ('PYRO2_LS_SELECT', '65', '36'),
        ('COMMS_RESET_REQUEST', '90', '37'), ('PYRO3_FIRE', '43', '40'), ('TP_STROBE', '35', '41'),
        ('FOINSE_RETURN_EN', '77', '43'), ('FC_POWER_HOLD', '4', '45'), ('PYRO2_FIRE', '40', '46'),
        ('FLIGHT_STATUS_LED1', '88', '51'), ('CAN_POWER_EN', '36', '57'), ('ST_NCS', '29', '61'),
        ('CAN_STB', '41', '62'), ('PYRO3_LS_SELECT', '61', '63'), ('ST_DRDY', '97', '64'), ('TDK_NCS', '51', '65'),
        ('TP_PC7', '64', '68'), ('TP_PD10', '57', '70'), ('TP_PC6', '63', '71'), ('TDK_DRDY', '2', '77'),
        ('MAG_INT', '5', '84'), ('PYRO1_LS_SELECT', '68', '85'), ('BUZZER_DRIVE', '87', '86'),
        ('STAGING_ARM_SENSE', '46', '87'), ('NEW_FLIGHT_CLEAR_REQUEST', '62', '88'), ('HG_INT1', '3', '90'),
        ('STAGE_INHIBIT_LATCHED', '45', '97')],
    'U401': [
        ('COMMS_STATUS_LED', '56', '8'), ('CC_BRANCH_FAULT_N', '57', '9'), ('CC_BAT_VALID', '16', '10'),
        ('USB_VBUS_PRESENT', '28', '15'), ('GNSS_RESET_N', '25', '17'), ('LORA_BUSY', '9', '20'),
        ('GNSS_EN', '26', '25'), ('LORA_DIO1', '10', '26'), ('LORA_RESET_N', '8', '28'),
        ('CC_COMMS_TO_FLIGHT', '51', '29'), ('LORA_NCS', '20', '33'), ('GNSS_RX', '43', '36')],
}
# why a net left its pin, where the reason is not distance
LEFT = {
    'FOINSE_RETURN_EN': "PA15's reset pull-up held U7001 and U7002 on until firmware ran",
    'PYRO1_LS_SELECT': 'the ROM bootloader drives PA9 as USART1 TX',
    'NOR_EN': 'the ROM bootloader drives PA11 as USB D-',
    'FLIGHT_COMMS_EN': 'the ROM bootloader drives PA12 as USB D+',
    'PYRO2_LS_SELECT': 'PC8 carries trace data (TRACED1)',
    'PYRO3_FIRE': 'PE12 sits beside the recovery arm sense on PE13',
    'PYRO3_LS_SELECT': 'PD14 sits beside the new-flight request on PD15',
}
# what a pin brings to whatever it carries; and the old notes that belonged to the pin, not the net
PIN_FACT = {
    ('U201', 'PA9'): 'the ROM bootloader drives it as USART1 TX: a pad and nothing else here',
    ('U201', 'PA11'): 'VDDUSB powered; the ROM bootloader drives it as USB D-: a pad and nothing else here',
    ('U201', 'PA12'): 'VDDUSB powered; the ROM bootloader drives it as USB D+: a pad and nothing else here',
    ('U201', 'PA15'): 'JTDI with an internal pull-up from reset (DS14258 table 14 note 7) until firmware sets it',
    ('U201', 'PB4'): 'NJTRST with an internal pull-up from reset (DS14258 table 14 note 7) until firmware sets it',
}
PIN_ONLY = ('; VDDUSB powered', '; disable JTAG beyond SWD', '; never drives, neighbours PC8')
STALE_TP = {'TP201': 'TP19'}                    # the strobe's loop since the test points were renumbered


def st_data(ref):
    r = ET.parse(XMLS[ref]).getroot()
    tag = r.tag.split('}')[0] + '}'
    sig = {p.get('Position'): {s.get('Name') for s in p.findall(f'{tag}Signal')} for p in r.findall(f'{tag}Pin')}
    af = {}
    for gp in ET.parse(ST / 'IP' / 'GPIO-STM32H56x_gpio_v1_0_Modes.xml').getroot().iter():
        port = re.match(r'P[A-Z]\d+', gp.get('Name', '')) if gp.tag.endswith('GPIO_Pin') else None
        for ps in (gp if port else []):
            if ps.tag.endswith('PinSignal'):
                for v in ps.iter():
                    m = re.match(r'GPIO_(AF\d+)_', v.text or '') if v.tag.endswith('PossibleValue') else None
                    if m:
                        af[(port.group(0), ps.get('Name'))] = m.group(1)
    return sig, af


def renames():
    """Each moved spare pad's net, renamed for its new pin."""
    out = {}
    for ref in MOVES:
        rows = {r['pad']: r for r in csv.DictReader(open(MAPS[ref]))}
        for net, a, b in MOVES[ref]:
            if SPARE.match(net):
                out[net] = 'TP_' + rows[b]['port_or_supply']
    return out


def stub(t, pins, pad):
    """The wire end and label angle that a labelled pin on the same side uses, applied to pad."""
    x, y, ang = pins[pad]
    for q, (qx, qy, qa) in sorted(pins.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0):
        if qa != ang or q == pad:
            continue
        pts, used = K.connected_points(t, (qx, qy))
        labs = K.labels_at(t, pts)
        if len(used) == 1 and len(labs) == 1:
            lx, ly = K.xy(labs[0])
            return (round(x + (lx - qx), 4), round(y + (ly - qy), 4)), float(K.first(labs[0], 'at')[3])
    raise AssertionError(f'no labelled pin beside pad {pad}')


def relabel(ref):
    t = K.load(BOARD / SHEETS[ref])
    pins = K.pin_positions(t, ref)
    sheet = SHEETS[ref]
    new = {}                                   # pad -> net after (None: left empty)
    for net, a, b in MOVES[ref]:
        new[b] = net
        new.setdefault(a, None)
    found = {}
    for pad in new:
        pts, used = K.connected_points(t, pins[pad][:2])
        labs = K.labels_at(t, pts)
        assert len(used) <= 1 and len(labs) <= 1, (ref, pad, [l[1] for l in labs])
        found[pad] = (labs[0] if labs else None, used[0] if used else None)
    ncs = {K.xy(x): x for x in K.children(t, 'no_connect')}
    for pad, net in sorted(new.items(), key=lambda kv: int(kv[0])):
        lab, w = found[pad]
        at = pins[pad][:2]
        if net and lab is not None:
            lab[1] = net
        elif net:                              # was a no-connect: a wire and a label like its neighbours'
            nc = ncs.get(tuple(at))
            assert nc is not None, (ref, pad, 'neither a label nor a no-connect')
            t.remove(nc)
            end, ang = stub(t, pins, pad)
            K.add(t, K.wire(at, end, sheet, f's19-{ref}-{pad}'))
            K.add(t, K.global_label(net, end, ang, sheet, f's19-{ref}-{pad}'))
        else:                                  # left empty: its label and wire go, a no-connect flag comes
            assert lab is not None, (ref, pad)
            t.remove(lab)
            if w is not None:
                t.remove(w)
            K.add(t, K.no_connect(at, sheet, f's19-{ref}-{pad}'))
    K.save(t, BOARD / sheet)
    return new


def rename_spares(names):
    """The moved spare pads' global labels and test point values, on every sheet."""
    done = 0
    for fn in sorted(BOARD.glob('*.kicad_sch')):
        t = K.load(fn)
        hit = False
        for lab in K.children(t, 'global_label'):
            if lab[1] in names:
                lab[1] = names[lab[1]]; hit = True; done += 1
        for ref, sym in K.symbols(t).items():
            for p in K.children(sym, 'property'):
                if p[1] == 'Value' and p[2] in names and ref.startswith('TP'):
                    p[2] = names[p[2]]; hit = True; done += 1
        if hit:
            K.save(t, fn)
    return done


def remap(ref, new, names, tp_of):
    sig, af = st_data(ref)
    rows = list(csv.DictReader(open(MAPS[ref])))
    by_pad = {r['pad']: r for r in rows}
    old = {r['net']: dict(r) for r in rows if r['net'] not in ('', 'NC')}
    moved = {net: (a, b) for net, a, b in MOVES[ref]}
    for pad, net in new.items():
        r = by_pad[pad]
        port = r['port_or_supply']
        if net is None:
            gone = next(n for n, (a, b) in moved.items() if a == pad)
            r.update(net='NC', function='ANALOG', alternate_function='',
                     notes=f"Unused since {D}: {gone} moved to {by_pad[moved[gone][1]]['port_or_supply']}; no-connect, "
                           'safe as analog')
            continue
        o = old[net]
        a = moved[net][0]
        f, alt = o['function'], o['alternate_function']
        m = re.match(r'(ADC\d)_INP\d+$', f)
        if m:                                  # the new pin's channel on the same converter
            ch = [s for s in sig[pad] if re.match(rf'{m.group(1)}_INP\d+$', s)]
            assert len(ch) == 1, (ref, net, pad, ch)
            f = ch[0]
        elif alt.startswith('AF'):             # the same signal: the new pin's AF number
            assert f in sig[pad], (ref, net, pad, f)
            alt = af[(port, f)]
        else:
            assert f == 'GPIO' and 'GPIO' in sig[pad], (ref, net, pad, f)
        note = o['notes']
        for s in PIN_ONLY:
            note = note.replace(s, '')
        for k, v in STALE_TP.items():
            note = note.replace(k, v)
        note = re.sub(r'\bEXTI\d+\b', f'EXTI{int(port[2:])}', note)
        if SPARE.match(net):
            note = re.sub(r'Spare test pad TP\d+', f'Spare test pad {tp_of[net]}', note)
        parts = [note] if note else []
        if (ref, port) in PIN_FACT:
            parts.append(PIN_FACT[(ref, port)])
        why = LEFT.get(net)
        assert not why or by_pad[a]['port_or_supply'] in why, (net, why)
        parts.append(f"from {by_pad[a]['port_or_supply']} (pad {a}){': ' + why if why else ''} ({D})")
        r.update(net=names.get(net, net), function=f, alternate_function=alt, notes='; '.join(parts))
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, quoting=csv.QUOTE_ALL, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    MAPS[ref].write_text(buf.getvalue())


def test_points():
    """Each spare pad's test point, from the netlist as captured."""
    root = ET.parse(BOARD / 'output' / 'full-netlist.xml').getroot()
    out = {}
    for n in root.iter('net'):
        name = n.get('name').rsplit('/', 1)[-1]
        if SPARE.match(name):
            out[name] = next(x.get('ref') for x in n.iter('node') if x.get('ref').startswith('TP'))
    return out


def build():
    names, tp_of = renames(), test_points()
    news = {ref: relabel(ref) for ref in ('U201', 'U401')}
    n = rename_spares(names)
    assert n == 3 * len(names), ('each spare pad: its two labels and its test point value', n)
    for ref in ('U201', 'U401'):
        remap(ref, news[ref], names, tp_of)
    return names


if __name__ == '__main__':
    names = build()
    print('step 19:', {r: len(m) for r, m in MOVES.items()}, 'nets moved; spare pads renamed', names)
