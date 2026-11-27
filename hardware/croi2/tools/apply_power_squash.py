#!/usr/bin/env python3
"""Apply D-27Nov.2 (proposed): gut Burrito's services domain, NOR limiter and isolators, GNSS / LoRa gates, and the
pyro current sense. Plan and reasons: docs/briefs/power-squash-plan.md.

    python3 tools/apply_power_squash.py                 # dry run: what would go, per sheet (writes nothing)
    python3 tools/apply_power_squash.py --apply         # edit the sheets in place, git rm the two emptied sheets
    python3 tools/apply_power_squash.py --apply --board DIR   # edit a copy of the sheets in DIR instead

Close KiCad first. Run on a clean branch: this edits the native sheets text-wise (tools/capture/kicadsch.py).
Afterwards: python3 tools/netcheck.py --diff <dir with the old sheets> <dir with the new sheets>; then KiCad ERC; then Update PCB from Schematic.
Nothing here edits the PCB, the pin CSVs, the checks JSON or the docs: those follow once the sheets pass ERC.
"""
import argparse, subprocess, sys, shutil, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'capture'))
sys.path.insert(0, str(HERE))
import kicadsch as K
import netcheck as N
from sexpr import children, first, emit

BOARD = HERE.parent

# 1. Whole sheets that empty out (every symbol goes; the sheet block leaves Croi2.kicad_sch; the file is git rm'd)
EMPTY_SHEETS = ['01optional-ldo', '01optional-limit']

# 2. Parts that go, per sheet
PARTS = {
    '03-sensors-storage': ['U3601', 'R3601', 'R3602', 'R3603', 'R3604', 'C3601', 'C3602', 'U3602', 'U3603'],
    '04d-gnss': ['U4501', 'U4502', 'U4503', 'R4501', 'R4502', 'R4503', 'C4502'],
    '04e-radio': ['U4601', 'U4602', 'U4603', 'U4604', 'R4601', 'R4602', 'R4603', 'C4602'],
    '06c-output-diagnostics': ['U6701', 'C6701', 'R6711', 'R6712', 'R6713', 'R6715', 'C6711', 'R6721', 'R6722', 'R6723',
                               'R6725', 'C6721', 'R6731', 'R6732', 'R6733', 'R6735', 'C6731'],
    '10-test-points': ['TP5', 'TP9', 'TP10', 'TP3', 'TP8', 'TP32'],   # TP35 goes with its sheet
    '04f-radio-module': ['TP2'],
}

# 3. Nets renamed (labels), so the pieces join: services and gated rails fold into the flight and comms rails; the
#    isolators' far side takes the near side's name.
RELABEL = {
    '3V3_OPTIONAL': 'FLIGHT_3V3', 'NOR_3V3': 'FLIGHT_3V3',
    'GNSS_3V3': 'COMMS_3V3', 'LORA_3V3': 'COMMS_3V3',
    'NOR_CLK_ISO': 'NOR_CLK', 'NOR_NCS_ISO': 'NOR_NCS', 'NOR_IO0_ISO': 'NOR_IO0', 'NOR_IO1_ISO': 'NOR_IO1',
    'NOR_IO2_ISO': 'NOR_IO2', 'NOR_IO3_ISO': 'NOR_IO3', 'NOR_RESET_N_ISO': 'NOR_RESET_REQUEST',
    'GNSS_PPS_ISO': 'GNSS_PPS', 'GNSS_RX_ISO': 'GNSS_RX', 'GNSS_TX_ISO': 'GNSS_TX', 'GNSS_RESET_N_ISO': 'GNSS_RESET_N',
    'LORA_MISO_ISO': 'LORA_MISO', 'LORA_MOSI_ISO': 'LORA_MOSI', 'LORA_NCS_ISO': 'LORA_NCS', 'LORA_SCK_ISO': 'LORA_SCK',
    'LORA_BUSY_ISO': 'LORA_BUSY', 'LORA_DIO1_ISO': 'LORA_DIO1', 'LORA_RESET_N_ISO': 'LORA_RESET_N',
}
# NOR_CLK_ISO -> NOR_CLK keeps R3609 (22 ohm damping) in the line: it sat between NOR_CLK_ISO and NOR_CLK_DAMP.

# 4. Nets left with nothing on the far side: the MCU pin gets a no-connect flag
FREE = ['NOR_EN', 'SERVICE_POWER_EN', 'GNSS_EN', 'LORA_EN',
        'ADC_PYRO1_CURRENT', 'ADC_PYRO2_CURRENT', 'ADC_PYRO3_CURRENT',
        # the TPS1H100's current-sense pin (U6304 / U6404 / U6504 pin 14) loses its burden: flagged no-connect.
        # Read TI's TPS1H100-Q1 datasheet for an unused sense pin before trusting this.
        'PYRO1_CS', 'PYRO2_CS', 'PYRO3_CS']


def pins_of(tree, sym):
    return N.sheet_pins(tree, sym)


def patch_pin_positions():
    def pp(tree, ref):
        sym = K.symbols(tree)[ref]
        return {n: (x, y, 0) for n, (x, y) in N.sheet_pins(tree, sym).items()}
    K.pin_positions = pp


def pre_trim(tree, p, ref):
    """Before a part goes: if the wire chain leaving pin point p has a net label on the body of one of its wires
    (not at a wire end), keep the stretch from that label onward: it joins the part's far side to its own pin.
    strip_branch only looks at wire ends and would take the whole chain, label and all."""
    chain, seen, q0 = [], set(), p
    while True:
        ws = [(w, a, b) for w, a, b in K.wires(tree) if q0 in (a, b) and id(w) not in seen]
        if len(ws) != 1:
            return
        pins, labs, juns = K._others_at(tree, q0, ref) if chain else ([], [], [])
        if chain and (pins or labs or juns):
            return
        w, a, b = ws[0]
        seen.add(id(w))
        q = b if a == q0 else a
        body = [l for k in ('global_label', 'label') for l in children(tree, k)
                if K.on_segment(K.xy(l), a, b) and K.xy(l) not in (a, b)]
        if body:
            m = min((K.xy(l) for l in body), key=lambda m: abs(m[0] - q0[0]) + abs(m[1] - q0[1]))
            for cw in chain + [w]:
                K.remove(tree, lambda x, cw=cw: x is cw)
            K.add(tree, K.wire(m, q, 'squash', f'{m}.{q}'))
            return
        chain.append(w)
        q0 = q


def free_net(tree, name, log, sheet):
    """Remove labels called `name` and the wires to the one pin they served; put a no-connect on that pin."""
    done = 0
    for kind in ('global_label', 'label'):
        for l in [x for x in children(tree, kind) if x[1] == name]:
            p = K.xy(l)
            pts, used = K.connected_points(tree, p)
            pins = []
            for s in children(tree, 'symbol'):
                ref = K.props(s).get('Reference', '?')
                if first(s, 'lib_id')[1].startswith('power:'):
                    continue
                for n, q in N.sheet_pins(tree, s).items():
                    if q in pts:
                        pins.append((ref, n, q))
            others = [x for x in children(tree, 'global_label') + children(tree, 'label')
                      if K.xy(x) in pts and x is not l and x[1] != name]
            if len(pins) > 1 or others:
                log.append(f'  WARN {sheet}: {name} at {p} still joins {[(a, b) for a, b, _ in pins]} {[o[1] for o in others]}; left')
                continue
            for w in used:
                K.remove(tree, lambda x, w=w: x is w)
            K.remove(tree, lambda x, l=l: x is l)
            for ref, n, q in pins:
                K.add(tree, K.no_connect(q, sheet, f'free.{name}'))
                log.append(f'  {sheet}: {name} freed, no-connect on {ref}.{n}')
            done += 1
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--board', default=str(BOARD))
    a = ap.parse_args()
    board = Path(a.board)
    patch_pin_positions()
    log = []
    trees, orig = {}, {}

    def tree(name):
        if name not in trees:
            trees[name] = K.load(board / f'{name}.kicad_sch')
            orig[name] = K.emit(trees[name])
        return trees[name]

    nparts = 0
    for sh in EMPTY_SHEETS:
        t = tree(sh)
        refs = [r for r in K.symbols(t) if not r.startswith('#')]
        log.append(f'{sh}: whole sheet goes ({len(refs)} parts: {" ".join(sorted(refs))})')
        nparts += len(refs)
    for sh, refs in PARTS.items():
        t = tree(sh)
        for r in refs:
            if r not in K.symbols(t):
                log.append(f'  WARN {sh}: {r} not found'); continue
            for pt in {v for v in N.sheet_pins(t, K.symbols(t)[r]).values()}:
                pre_trim(t, pt, r)
            lg = K.remove_part(t, r)
            nparts += 1
            log.append(f'{sh}: remove {r} ({len(lg)} wires/labels/flags stripped)')
    # freed nets: on the sheets that still carry the other end
    for f in sorted(board.glob('*.kicad_sch')):
        sh = f.stem
        if sh in EMPTY_SHEETS or sh == 'Croi2':
            continue
        t = tree(sh)
        for n in FREE:
            free_net(t, n, log, sh)
    # relabel everywhere
    nl = 0
    for f in sorted(board.glob('*.kicad_sch')):
        sh = f.stem
        if sh in EMPTY_SHEETS or sh == 'Croi2':
            continue
        t = tree(sh)
        for k in ('global_label', 'label'):
            for l in children(t, k):
                if l[1] in RELABEL:
                    l[1] = RELABEL[l[1]]
                    nl += 1
    log.append(f'relabelled {nl} labels')
    # the root: drop the two sheet blocks
    root = tree('Croi2')
    for sh in EMPTY_SHEETS:
        n = K.remove(root, lambda x, sh=sh: x[0] == 'sheet' and any(
            p[0] == 'property' and p[1] == 'Sheetfile' and p[2] == f'{sh}.kicad_sch' for p in x if isinstance(p, list)))
        log.append(f'Croi2: sheet block {sh} removed ({n})')
    print('\n'.join(log))
    print(f'{nparts} parts removed (the two emptied sheets included).')
    if not a.apply:
        print('dry run: nothing written.')
        return
    for name, t in trees.items():
        if name in EMPTY_SHEETS or K.emit(t) == orig[name]:
            continue                                    # untouched sheets keep KiCad's own formatting
        K.save(t, board / f'{name}.kicad_sch')
        print('wrote', name)
    for sh in EMPTY_SHEETS:
        f = board / f'{sh}.kicad_sch'
        if f.exists():
            try:
                subprocess.check_call(['git', '-C', str(board), 'rm', '-q', '-f', f.name])
            except Exception:
                f.unlink()
    print('written. Next: netcheck --diff-against, KiCad ERC, Update PCB from Schematic.')


if __name__ == '__main__':
    main()
