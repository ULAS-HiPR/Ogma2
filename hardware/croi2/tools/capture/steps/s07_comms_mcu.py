"""Step 7, the comms MCU moves to the STM32H563RIT6 (LQFP64).

Capture specification rows: Comms U401; Inter-MCU link (USART3 on PC10 / PC11, AF7); the processor
notes (PA1 / PA2 / PB5 boundaries kept; VDDA/VREF+ pad 13 on COMMS_VDDA through R401; VCAP pads
30 and 62 with 2.2 uF each; no VDDUSB pad). U401 is redrawn from the 64-pad map
(docs/architecture/proposed-comms-pinout.csv), keeping its symbol UUID.

The symbol is KiCad 9.0.7's MCU_ST_STM32H5:STM32H563RITx (generated from ST's pin data), renamed to
the MPN; the footprint is KiCad's Package_QFP:LQFP-64_10x10mm_P0.5mm. The map's pads, port names
and alternate functions are checked against ST's open pin data (STM32H563RITx.xml and the H56x
GPIO modes file) by s07_check.py.

PC3 / PC4 (LORA_RXEN / LORA_TXEN) are "MCU-only reservations, no external connection" in the map:
they get no-connect flags and a note, which closes the baseline dangling-label findings.
On 04a, the decoupling follows the package: C405 (old VDD pad 100) and C408 (old VDDUSB pad 73) go.
"""
import copy
import csv
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
REPO = BOARD.parents[1]
LIB = BOARD / 'libraries'
MAP = REPO / 'docs/architecture/proposed-comms-pinout.csv'
SHEET, SUPPORT = '04-comms-gnss-radio.kicad_sch', '04a-comms-support.kicad_sch'
MCU, FP = 'STM32H563RIT6', 'Package_QFP:LQFP-64_10x10mm_P0.5mm'
AT = (154.94, 162.56)
RESERVED = {'11': 'LORA_RXEN', '24': 'LORA_TXEN'}           # map: MCU-only reservation, no external connection
SUPPLY = {'1', '19', '32', '48', '64'}                      # VBAT and VDD: COMMS_3V3
GROUND = {'12', '18', '31', '47', '63'}                     # VSSA and VSS


def pad_map():
    rows = list(csv.DictReader(MAP.open()))
    assert [int(r['pad']) for r in rows] == list(range(1, 65))
    return {r['pad']: r for r in rows}


def mcu_symbol():
    src = [s for s in K.children(K.load(f'{K.KICAD_SYMBOLS}/MCU_ST_STM32H5.kicad_sym'), 'symbol') if s[1] == 'STM32H563RITx'][0]
    sym = copy.deepcopy(src)
    assert not K.first(sym, 'extends')
    sym[1] = MCU
    for sub in K.children(sym, 'symbol'):
        sub[1] = sub[1].replace('STM32H563RITx', MCU)
    pr = {p[1]: p for p in K.children(sym, 'property')}
    pr['Value'][2] = MCU
    assert pr['Footprint'][2] == FP
    vcap = [p for p in K.walk(sym, 'pin') if K.first(p, 'number')[1] == '62']
    assert len(vcap) == 1 and vcap[0][1] == 'power_out'
    vcap[0][1] = K.A('passive')                                 # one driver on COMMS_VCAP (ERC_Model)
    i = sym.index(pr['ki_fp_filters']) + 1
    for k, v in (('MPN', MCU), ('Manufacturer', 'STMicroelectronics'),
                 ('Library_Check', 'KiCad 9.0.7 MCU_ST_STM32H5:STM32H563RITx (generated from ST pin data), renamed. '
                                   'Pads, ports and AFs of the 64-pad map checked against ST open pin data STM32H563RITx.xml '
                                   '(capture step 7). Footprint: KiCad Package_QFP:LQFP-64_10x10mm_P0.5mm, ST LQFP64 10 x 10 mm'),
                 ('ERC_Model', 'VCAP pads 30 and 62 share the internal regulator output: pad 30 power_out, pad 62 passive, '
                               'so ERC sees one driver. Numbers, names and footprint unchanged')):
        sym.insert(i, K.el('property', k, v, K.el('at', K.num(0), K.num(0), K.num(0)), K.fx(1.27, hide=True)))
        i += 1
    return sym


def libraries():
    K.add_lib_symbol(LIB / 'Ogma2.kicad_sym', mcu_symbol())
    (LIB / 'Package_QFP.pretty').mkdir(exist_ok=True)
    K.vendor_footprint(LIB, 'Package_QFP', 'LQFP-64_10x10mm_P0.5mm')
    table = BOARD / 'fp-lib-table'
    t = K.load(table)
    if not any(K.first(l, 'name')[1] == 'Package_QFP' for l in K.children(t, 'lib')):
        t.append(K.el('lib', K.el('name', 'Package_QFP'), K.el('type', 'KiCad'), K.el('uri', '${KIPRJMOD}/libraries/Package_QFP.pretty'),
                      K.el('options', ''), K.el('descr', 'KiCad 9.0.7 footprints added during capture')))
        K.save(t, table)


def comms_sheet():
    S = SHEET
    rows = pad_map()
    t = K.load(BOARD / S)
    old = K.symbols(t)['U401']
    uid, desc, inst = K.first(old, 'uuid')[1], K.props(old)['Description'], K.sheet_path(t)
    assert inst and inst.startswith('/'), inst
    K.remove_part(t, 'U401')
    assert not K.wires(t) and not K.children(t, 'global_label') and not K.children(t, 'no_connect')
    K.import_lib(t, f'Ogma2:{MCU}', LIB / 'Ogma2.kicad_sym')
    pins = K.make_symbol(t, f'Ogma2:{MCU}', 'U401', AT, 0, MCU, FP, S,
                         extra={'MPN': MCU, 'Manufacturer': 'STMicroelectronics'}, inst=inst,
                         ref_at=(AT[0] + 22.86, AT[1] - 43.18), val_at=(AT[0] + 22.86, AT[1] + 43.18))
    sym = K.symbols(t)['U401']
    K.first(sym, 'uuid')[1] = uid                                # keep the PCB link
    {p[1]: p for p in K.children(sym, 'property')}['Description'][2] = desc
    left, right = AT[0] - 25.4, AT[0] + 25.4
    done = set()
    for pad, (x, y, _) in pins.items():
        net = rows[pad]['net']
        if pad in SUPPLY | GROUND or pad == '13':
            continue
        if net == 'NC' or pad in RESERVED:
            assert net == RESERVED.get(pad, 'NC'), (pad, net)
            K.add(t, K.no_connect((x, y), S, f'u401.{pad}'))
        elif x == left:
            K.path(t, [(x, y), (x - 5.08, y)], S, f'u401.{pad}')
            K.add(t, K.global_label(net, (x - 5.08, y), 0, S, f'u401.{pad}'))
        elif x == right:
            K.path(t, [(x, y), (x + 5.08, y)], S, f'u401.{pad}')
            K.add(t, K.global_label(net, (x + 5.08, y), 180, S, f'u401.{pad}'))
        else:
            raise AssertionError((pad, x, y))
        done.add(pad)
    # top: VBAT and the four VDD pads tied to one COMMS_3V3 label; VDDA/VREF+ (pad 13) to COMMS_VDDA
    top = AT[1] - 45.72
    xs = sorted(pins[p][0] for p in SUPPLY)
    assert all(pins[p][1] == top for p in SUPPLY | {'13'}) and all(rows[p]['net'] == 'COMMS_3V3' for p in SUPPLY)
    for x in xs:
        K.path(t, [(x, top), (x, top - 7.62)], S, f'vdd.{x}')
    K.path(t, [(xs[0] - 5.08, top - 7.62)] + [(x, top - 7.62) for x in xs], S, 'vdd.bus')
    K.add(t, K.global_label('COMMS_3V3', (xs[0] - 5.08, top - 7.62), 0, S, 'vdd'))
    for x in xs[:-1]:
        K.add(t, K.junction((x, top - 7.62), S, 'vdd'))
    xa = pins['13'][0]
    assert rows['13']['net'] == 'COMMS_VDDA'
    K.path(t, [(xa, top), (xa, top - 15.24), (xa + 5.08, top - 15.24)], S, 'vdda')
    K.add(t, K.global_label('COMMS_VDDA', (xa + 5.08, top - 15.24), 180, S, 'vdda'))
    # bottom: the four VSS pads are stacked in the symbol; VSSA beside them; one GND label
    bot = AT[1] + 45.72
    vss = {pins[p][:2] for p in GROUND - {'12'}}
    assert len(vss) == 1 and all(rows[p]['net'] == 'GND' for p in GROUND)
    (xv, _), xs_a = vss.pop(), pins['12'][0]
    K.path(t, [(xv, bot), (xv, bot + 7.62)], S, 'vss')
    K.path(t, [(xs_a, bot), (xs_a, bot + 7.62)], S, 'vssa')
    K.path(t, [(xs_a, bot + 7.62), (xv, bot + 7.62), (xv - 5.08, bot + 7.62)], S, 'gnd')
    K.add(t, K.junction((xv, bot + 7.62), S, 'gnd'))
    K.add(t, K.global_label('GND', (xv - 5.08, bot + 7.62), 0, S, 'gnd'))
    done |= SUPPLY | GROUND | {'13'}
    assert done | {p for p, r in rows.items() if r['net'] == 'NC'} | set(RESERVED) == set(rows)
    K.add(t, K.text('PC3 / PC4: LORA_RXEN / LORA_TXEN reservations, MCU-only, no external\n'
                    'connection (64-pad map); firmware holds them low or analog.', (30.48, AT[1] - 6.35), S, 'nRes', 1.016))
    for n in K.children(t, 'text'):
        if n[1] == 'COMMS MCU / STM32H563VIT6 / NON-Q LQFP100':
            n[1] = 'COMMS MCU / STM32H563RIT6 / LQFP64'
        elif n[1].startswith('Allocation: accepted 100-pad CSV. No GPIO reassignment.'):
            n[1] = n[1].replace('Allocation: accepted 100-pad CSV. No GPIO reassignment.',
                                'Allocation: the 64-pad map (proposed-comms-pinout.csv). Link to flight: USART3, PC10 TX / PC11 RX, AF7.')
    assert any('LQFP64' in n[1] for n in K.children(t, 'text')) and any('64-pad' in n[1] for n in K.children(t, 'text'))
    K.save(t, BOARD / S)


def support_sheet(log):
    S = SUPPORT
    t = K.load(BOARD / S)
    for r in ('C405', 'C408'):                                  # old VDD pad 100 and VDDUSB pad 73: no such pads now
        log[r] = K.remove_part(t, r)
    notes = {'C401': 'MCU VDD pad 19', 'C402': 'MCU VDD pad 32', 'C403': 'MCU VDD pad 48', 'C404': 'MCU VDD pad 64',
             'C407': 'MCU VBAT pad 1', 'C409': 'At VCAP pad 30; verify effective value/ESR', 'C410': 'At VCAP pad 62; same shared VCAP node',
             'C411': 'At VDDA/VREF+ pad 13', 'C412': 'At VDDA/VREF+ pad 13',
             'C413': 'At VDDA/VREF+ pad 13 (VREF+ is double-bonded to VDDA in LQFP64)',
             'C414': 'At VDDA/VREF+ pad 13 (VREF+ is double-bonded to VDDA in LQFP64)'}
    sym = K.symbols(t)
    for r, v in notes.items():
        p = {p[1]: p for p in K.children(sym[r], 'property')}['Implementation_Note']
        p[2] = v
    K.save(t, BOARD / S)


def build():
    log = {}
    libraries()
    comms_sheet()
    support_sheet(log)
    return log


if __name__ == '__main__':
    for ref, items in build().items():
        print(ref, len(items))
