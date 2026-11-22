"""Step 12: Burrito's test points in three sizes, a lean set of 47 (D-22Nov.9).

Seán, 22 Nov, from a DAQ board photo: big black loops on GND at the board edges, smaller orange loops, and
tiny round pads, each marked on the silkscreen by its TP number only. Then, seeing 108 on the board, he
picked the lean set: one probe point per net that needs one.

- GND: four Keystone 5011 loops (multipurpose, black; JLC C238127) at the board edges. TP2304 and TP4204
  (Keystone 5001) become 5011; two new ones go fwd and aft. TP502 is cut.
- Orange Keystone 5003 loops (miniature; JLC C238124) where a probe stays clipped on: each regulator or switch
  output (16), the timing strobe and GNSS PPS. The rail loops already on the board were Keystone 5000 (red),
  which is not in JLC's assembly library (jlcparts scrape of 21 Nov 2026). TP201, the strobe, goes from a
  pad to a loop. Cut: the five sensor rails (47R links off FLIGHT_3V3) and the second loops on FLIGHT_3V3
  and COMMS_3V3.
- 1.0 mm pads (TestPoint_Pad_D1.0mm) on 25 nets you only touch: BOOT0 x2, the reset memory, the three
  spare pins, 11 power-status nets, 8 pyro ADC and arm-sense nodes. Cut: buses firmware sees (sensor SPI
  and I2C, LoRa, CAN logic) and NRST (on each Tag-Connect).

No test point of any size on a fire net or on a line that drives a fire switch (B-02): OUTPUTx_HIGH / LOW,
PYROx_ENERGY, the armed rails, PYROx_FIRE / GATE / LS_SELECT, STAGE_ELIGIBLE, PYRO3_HS_ENABLE. Their scaled
ADC nodes are under PYRO DIAGNOSTICS. Each new test point joins its net through a global label. Refs are
renumbered TP1-TPn fore to aft once the board's length is fixed (a later step).
Edits the sheets in place (run from a clean checkout).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
LIB = BOARD / 'libraries'
SHEET = '10-test-points.kicad_sch'
KEY = 'Keystone Electronics'
PAD = {'Footprint': 'TestPoint:TestPoint_Pad_D1.0mm'}
LOOP = {'Footprint': 'TestPoint:TestPoint_Keystone_5000-5004_Miniature', 'MPN': '5003', 'Manufacturer': KEY,
        'LCSC': 'C238124', 'Datasheet': 'https://www.keyelco.com/product-pdf.cfm?p=1309'}
GND_LOOP = {'Footprint': 'TestPoint:TestPoint_Keystone_5010-5014_Multipurpose', 'MPN': '5011', 'Manufacturer': KEY,
            'LCSC': 'C238127', 'Datasheet': 'https://www.keyelco.com/product-pdf.cfm?p=1319'}
KIND = {id(PAD): '1.0 mm pad', id(LOOP): 'orange loop, Keystone 5003', id(GND_LOOP): 'black loop at an edge, Keystone 5011'}

GROUPS = [
    ('ORANGE LOOPS: RAILS, PPS', LOOP, ['BOOT_3V3', 'NOR_3V3', 'GNSS_3V3', 'FOINSE_AUX_3V3', 'USB_VBUS', 'USB_LIMITED',
                                        'GNSS_PPS']),
    ('BLACK LOOPS: GND (FWD, AFT)', GND_LOOP, ['GND', 'GND']),
    ('PADS: POWER STATUS', PAD, ['BAT_SOURCE_FAULT_N', 'BRANCH_FAULT_N', 'FC_POWER_HOLD', 'BAT_SHDN_N', 'FLIGHT_LDO_PG',
                                 'COMMS_LDO_PG', 'OPTIONAL_LDO_PG', 'SUPERVISOR_WDI']),
    ('PADS: PYRO DIAGNOSTICS', PAD, ['ADC_PYRO1_CONTINUITY', 'ADC_PYRO2_CONTINUITY', 'ADC_PYRO3_CONTINUITY',
                                     'ADC_PYRO1_CURRENT', 'ADC_PYRO2_CURRENT', 'ADC_PYRO3_CURRENT', 'RECOVERY_ARM_SENSE',
                                     'STAGING_ARM_SENSE']),
]
NEW = [(f'TP{9501 + i}', net, tier) for i, (net, tier) in enumerate((n, t) for _, t, nets in GROUPS for n in nets)]

# Existing test points kept, at their size: one orange loop per regulator or switch output, the strobe; GND loops.
RAIL_LOOPS = ('TP1001', 'TP1002', 'TP1301', 'TP1302', 'TP1401', 'TP1701', 'TP1801', 'TP1901', 'TP4601', 'TP501')
RETIER = {**{r: LOOP for r in RAIL_LOOPS + ('TP201',)}, **{r: GND_LOOP for r in ('TP2304', 'TP4204')}}
# Existing test points cut (Seán's lean set, 22 Nov): another probe point already serves each net.
REMOVE = {
    'TP3101': 'ST_3V3, a 47R link off FLIGHT_3V3', 'TP3201': 'TDK_3V3, a 47R link off FLIGHT_3V3',
    'TP3301': 'HG_3V3, a 47R link off FLIGHT_3V3', 'TP3401': 'BMP_3V3, a 47R link off FLIGHT_3V3',
    'TP3501': 'TE_3V3, a 47R link off FLIGHT_3V3', 'TP2303': 'second FLIGHT_3V3 loop (TP1701 stays)',
    'TP4203': 'second COMMS_3V3 loop (TP1801 stays)', 'TP502': 'a fifth GND loop; four reach the board',
    **{f'TP3{s}0{i}': 'sensor bus, seen by firmware' for s in (1, 2, 3) for i in (2, 3, 4, 5, 6)},
    **{r: 'barometer I2C, seen by firmware' for r in ('TP3402', 'TP3403', 'TP3502', 'TP3503')},
    **{r: 'LoRa SPI / IRQ, seen by firmware' for r in ('TP4602', 'TP4603', 'TP4604')},
    **{r: 'CAN logic, seen by firmware' for r in ('TP503', 'TP504', 'TP505', 'TP506')},
    'TP2302': 'FLIGHT_NRST, on the Tag-Connect', 'TP4202': 'COMMS_NRST, on the Tag-Connect',
}
STROBE_HEAD = ('TEST PADS / TIMING STROBE AND SPARE PADS', 'TEST POINTS / TIMING STROBE LOOP AND SPARE PADS')


def set_props(sym, kv):
    pr = {p[1]: p for p in K.children(sym, 'property')}
    for k, v in kv.items():
        if k in pr:
            pr[k][2] = v
        else:
            i = next(i for i, x in enumerate(sym) if isinstance(x, list) and x and x[0] == 'instances')
            sym.insert(i, K.prop(k, v, K.xy(sym)))


def text(t, value, at, size, tag, justify='left'):
    K.add(t, K.el('text', value, K.el('exclude_from_sim', K.A('no')), K.el('at', K.num(at[0]), K.num(at[1]), K.num(0)),
                  K.fx(size, justify), K.el('uuid', K.ident(SHEET, 'text', tag))))


def new_sheet(root):
    root_uuid = K.first(root, 'uuid')[1]
    sheet_uuid = K.ident('Croi2.kicad_sch', 'sheet', SHEET)
    inst = f'/{root_uuid}/{sheet_uuid}'
    t = K.new_sheet('Test points / key nets', file_id=SHEET)
    K.import_lib(t, 'Connector:TestPoint', LIB / 'Connector.kicad_sym')
    text(t, 'TEST POINTS / KEY NETS', (15.24, 15.24), 2.54, 'title')
    text(t, 'What this does: test points on key nets not served elsewhere, in three sizes (D-22Nov.9). Silkscreen: TP number only.\n'
            'Black Keystone 5011 loops on GND at the board edges; orange Keystone 5003 loops where a probe stays clipped on\n'
            '(rails, GNSS PPS); 1.0 mm round pads for nets you only touch. Each joins its net by global label.\n'
            'No test point on a fire net or on a line that drives a fire switch: OUTPUTx_HIGH / LOW, PYROx_ENERGY, the armed rails,\n'
            'PYROx_FIRE / GATE / LS_SELECT, STAGE_ELIGIBLE, PYRO3_HS_ENABLE (B-02). Their scaled ADC nodes are under PYRO DIAGNOSTICS.',
         (15.24, 25.4), 1.27, 'what', 'left top')
    i = 0
    for g, (head, tier, nets) in enumerate(GROUPS):
        x = 60.96 + g * 45.72
        text(t, head, (x - 35.56, 55.88), 1.524, f'h{g}')
        for row, net in enumerate(nets):
            ref, net_, tier_ = NEW[i]
            assert (net_, tier_) == (net, tier)
            y = 63.5 + row * 7.62
            extra = {k: v for k, v in tier.items() if k not in ('Footprint', 'Datasheet')}
            extra['Implementation_Note'] = f'Test point on {net}: {KIND[id(tier)]} (D-22Nov.9); silkscreen shows {ref} only'
            K.make_symbol(t, 'Connector:TestPoint', ref, (x, y), 0, net, tier['Footprint'], SHEET, inst=inst, extra=extra,
                          ref_at=(x + 2.54, y - 3.81), val_at=(x + 2.54, y - 3.81), hide_value=True)
            if 'Datasheet' in tier:
                set_props(K.symbols(t)[ref], {'Datasheet': tier['Datasheet']})
            K.add(t, K.global_label(net, (x - 5.08, y), 0, SHEET, ref))
            K.path(t, [(x - 5.08, y), (x, y)], SHEET, ref)
            i += 1
    K.save(t, BOARD / SHEET)

    # Root: a sheet symbol in the next free slot, page 45, and its index line.
    if any(q[2] == SHEET for s in K.children(root, 'sheet') for q in K.children(s, 'property')):
        return
    tmpl = [s for s in K.children(root, 'sheet') if any(q[1] == 'Sheetfile' and q[2] == '03mag-magnetometer.kicad_sch'
                                                         for q in K.children(s, 'property'))][0]
    new = K.copy.deepcopy(tmpl)
    dx = 353.06 - float(K.first(tmpl, 'at')[1])
    K.first(new, 'at')[1] = K.num(353.06)
    K.first(new, 'uuid')[1] = sheet_uuid
    for q in K.children(new, 'property'):
        q[2] = {'Sheetname': '10-test-points', 'Sheetfile': SHEET}[q[1]]
        a = K.first(q, 'at')
        a[1] = K.num(float(a[1]) + dx)
    for pg in K.walk(new, 'page'):
        pg[1] = '45'
    K.add(root, new)
    label = [x for x in K.children(root, 'text') if x[1].startswith('P44  ')][0]
    lab = K.copy.deepcopy(label)
    lab[1] = 'P45  Test points / key nets'
    a = K.first(lab, 'at')
    a[1] = K.num(float(a[1]) + dx)
    K.first(lab, 'uuid')[1] = K.ident('Croi2.kicad_sch', 'text', 'P45')
    K.add(root, lab)


def retier():
    """Existing test points to their size (rails and the strobe to orange 5003 loops, GND to black 5011 loops),
    and the cut ones out with the wiring that served only them."""
    done = {}
    for f in sorted(BOARD.glob('*.kicad_sch')):
        if f.name in ('Croi2.kicad_sch', SHEET):
            continue
        t = K.load(f)
        syms = K.symbols(t)
        hit = [r for r in RETIER if r in syms]
        cut = [r for r in REMOVE if r in syms]
        if not hit and not cut:
            continue
        for r in hit:
            set_props(syms[r], RETIER[r])
            done[r] = f.name
        for r in cut:
            K.remove_part(t, r)
            done[r] = f.name
        if f.name == '02a-flight-support.kicad_sch':
            heads = [n for n in K.children(t, 'text') if n[1] == STROBE_HEAD[0]]
            assert len(heads) == 1, len(heads)
            heads[0][1] = STROBE_HEAD[1]
        K.save(t, f)
    assert set(done) == set(RETIER) | set(REMOVE), sorted(set(RETIER) | set(REMOVE) - set(done))
    return done


def build():
    K.vendor_footprint(LIB, 'TestPoint', 'TestPoint_Keystone_5010-5014_Multipurpose')
    root = K.load(BOARD / 'Croi2.kicad_sch')
    new_sheet(root)
    K.save(root, BOARD / 'Croi2.kicad_sch')
    return retier()


if __name__ == '__main__':
    done = build()
    print('step 12:', len(NEW), 'new test points,', NEW[0][0], '-', NEW[-1][0], ';', len(RETIER), 'resized,', len(REMOVE), 'cut')
