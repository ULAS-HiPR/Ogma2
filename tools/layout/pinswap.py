"""MCU pin swaps for a placement (stage B2 step 7, burrito-stage-b2-brief.md; Seán, 22 Nov: "yes you may swap any pin
you want so long as it's justified and verified and documented").

    python3 tools/layout/pinswap.py BOARD.kicad_pcb NETLIST.xml --out DIR [--ref U201 --ref U401]

For each MCU it moves nets between pins so each pin sits nearer the part it connects to, on the placed board, and
writes the moves (moves.json), a trial netlist with them (netlist.xml) and a report. A move is allowed only where
ST's pin data (STM32_open_pin_data 45c0459, the CubeMX 6.19.0 subset; libraries/inputs/st-open-pin-data) says the
new pin can carry the function:

- a GPIO net goes to any GPIO-capable pin;
- an ADC input stays on the same converter (ADC1 or ADC2), at whatever channel the new pin has;
- a peripheral signal (SPI1_SCK, OCTOSPI1_IO0, FDCAN2_TX, ...) goes only to another pin with that same signal;
- clocks, debug, USB, power, BOOT0 and NRST stay.

Where a net may go (a move only; a net may stay where it was captured):
- never: SWD (PA13, PA14), PB3 (JTDO), PC13 (kept quiet beside the LSE, the pin map's erratum note), PC14, PC15, PH0, PH1,
  and any pin the pin map reserves (comms PC3 and PC4, for the radio's RX and TX enables);
- the pins the ROM bootloader drives once it has found its host (AN2606 rev. 70, table 137, STM32H562/563/573: the
  USART TX pins PA9, PA2, PD8; SPI MISO PA6, PB14, PC11; I2C3 PA8, PC9; I2C4 PD12, PD13; I3C PB6, PB7; FDCAN2 TX PB13;
  USB PA11, PA12): only a spare test pad, which has nothing on it but a pad (and a spare pad moves nowhere else);
- PA15 and PB4, which are pulled up from reset (as JTDI and NJTRST; DS14258 rev 6, table 14, note 7) until firmware
  changes them, and the pins the bootloader only reads (RX PA10, PA3, PD9; SPI SCK, MOSI and NSS PA5, PA7, PA4, PB10,
  PC1, PB12, PC10, PC12, PA15; FDCAN2 RX PB5): any net but an output that must stay off by default, an arm sense or
  the staging inhibit (the checker's rule: no fire or arm net on a bootloader pin);
- every other I/O pin: any net its function allows.
The outputs that must stay off by default (the enables with pull-downs, every fire and low-side select, the strobe)
pay a large penalty for sitting on a pulled or bootloader pin, so the search moves them off if it can.

And the energetic chapter's rules hold (docs/architecture/03-energetic-outputs.md): the three high-side fire pins
stay on port E, no low-side select goes on port E, the low-side selects stay on three different ports, and no fire
pin is a neighbouring pad of a low-side select. Added here (D-22Nov.25): no fire pin or low-side select is a neighbour
of another, of an arm sense, of the staging latch or of the new-flight request, so one solder bridge never ties two
inhibits together or ties one to a signal that changes only when armed; and the fire pins, low-side
selects, the new-flight request, the arm senses and the staging latch stay off pins with trace, debug-trigger, tamper,
RTC_OUT or LSCO outputs (ST's pin data; the backup domain's outputs outlive a system reset). Interrupt inputs keep distinct EXTI lines. A swap must save at least
MIN_GAIN mm, so no pin moves for nothing.

The search: each net's cost is its pin's distance to the nearest pad of the same net on another part (test points
left out), weighted as the placer weighs nets. Best single swap or move to a free pin, repeated until none helps;
the order is fixed, so the result repeats. While a net must still leave its pin, three-way moves compete too, so the
nets that must move go first, before the ports and pins they need are taken.
"""
import argparse
import csv
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ROOT = HERE.parents[1]
INPUTS = ROOT / 'hardware' / 'croi2' / 'libraries' / 'inputs'
PIN_XML = {'U201': INPUTS / 'st-open-pin-data' / 'STM32H563VITx.xml', 'U401': INPUTS / 'st-open-pin-data' / 'STM32H563RITx.xml'}
PIN_CSV = {'U201': INPUTS / 'flight-pinout.csv', 'U401': INPUTS / 'comms-pinout.csv'}

NEVER = {'PA13', 'PA14', 'PB3', 'PC13', 'PC14', 'PC15', 'PH0', 'PH1'}
BOOT_DRIVES = {'PA9', 'PA2', 'PD8', 'PA6', 'PB14', 'PC11', 'PA8', 'PC9', 'PD12', 'PD13', 'PB6', 'PB7', 'PB13', 'PA11', 'PA12'}
PULLED_OR_READ = {'PA15', 'PB4', 'PA10', 'PA3', 'PD9', 'PA5', 'PA7', 'PA4', 'PB10', 'PC1', 'PB12', 'PC10', 'PC12', 'PB5'}
NO_DEST = NEVER | BOOT_DRIVES | PULLED_OR_READ           # where an off-by-default output pays the penalty
HARMLESS = re.compile(r'^TP_P[A-K]\d+$')                # spare test pads, named for their pin: a pad and nothing else
ARM = {'RECOVERY_ARM_SENSE', 'STAGING_ARM_SENSE', 'STAGE_INHIBIT_LATCHED'}   # never on a bootloader or pulled pin
MIN_GAIN = 1.0
MUST_AVOID = {'FC_POWER_HOLD', 'SERVICE_POWER_EN', 'CAN_POWER_EN', 'NOR_EN', 'FLIGHT_COMMS_EN', 'FOINSE_RETURN_EN',
              'TP_STROBE', 'NEW_FLIGHT_CLEAR_REQUEST', 'GNSS_EN', 'LORA_EN',
              'PYRO1_FIRE', 'PYRO2_FIRE', 'PYRO3_FIRE', 'PYRO1_LS_SELECT', 'PYRO2_LS_SELECT', 'PYRO3_LS_SELECT'}
FIRE = {'PYRO1_FIRE', 'PYRO2_FIRE', 'PYRO3_FIRE'}
LOW_SIDE = {'PYRO1_LS_SELECT', 'PYRO2_LS_SELECT', 'PYRO3_LS_SELECT'}
FIRE_PORT = 'E'
# the nets that command the fire chain stay off any pin something other than a running GPIO can drive: trace data and
# the debug trigger (a debugger sets them), and the backup domain's outputs (tamper, RTC_OUT, LSCO), which outlive a
# system reset once firmware has turned them on
QUIET = FIRE | LOW_SIDE | {'NEW_FLIGHT_CLEAR_REQUEST'}
SPECIAL = re.compile(r'^(DEBUG_TRACE|DEBUG_TRGIO|TAMP_OUT|RTC_OUT|RCC_LSCO)')
NEIGHBOUR_MM = 0.6            # pads closer than this are neighbours (0.5 mm pitch)
AVOID_PENALTY = 1000.0
FIXED_FUNCS = re.compile(r'^(SWD|HSE|LSE|USB_D[MP]|TRACESWO|RESET|BOOT_STRAP)$')


def pin_name(n):
    return re.match(r'P[A-Z]\d+', n).group(0) if re.match(r'P[A-Z]\d+', n) else n


def short(n):
    return n.split('/')[-1] if n else ''


class MCU:
    def __init__(self, ref, pads_xy, netlist_root):
        self.ref = ref
        r = ET.parse(PIN_XML[ref]).getroot()
        tag = r.tag.split('}')[0] + '}'
        self.pin = {}                   # pad -> dict(name, type, signals)
        for p in r.findall(f'{tag}Pin'):
            self.pin[p.get('Position')] = dict(name=pin_name(p.get('Name')), full=p.get('Name'), type=p.get('Type'),
                                               signals={s.get('Name') for s in p.findall(f'{tag}Signal')})
        self.xy = pads_xy               # pad -> (x, y) board mm
        # each net's function and notes as captured (the pin map, keyed by net: a net keeps its function wherever it
        # moves; the ADC channel and AF number follow the new pin)
        rows = {row['net']: row for row in csv.DictReader(open(PIN_CSV[ref])) if row['net'] and row['net'] != 'NC'}
        self.func = {}                  # net -> function as captured
        self.exti = set()               # nets read as interrupts
        self.notes = {}
        self.net_at = {}                # pad -> net (full name) or None
        for n in netlist_root.findall('nets/net'):
            name = n.get('name')
            for x in n.findall('node'):
                if x.get('ref') == ref:
                    self.net_at[x.get('pin')] = None if name.startswith('unconnected-') else name
        for net in set(n for n in self.net_at.values() if n):
            row = rows.get(short(net))
            if row:
                self.func[net] = row['function']
                self.notes[net] = row['notes']
                if 'EXTI' in row['notes']:
                    self.exti.add(net)
        # pins the map reserves (comms PC3 / PC4 for the radio's RX and TX enables): never a destination
        self.reserved = {row['pad'] for row in csv.DictReader(open(PIN_CSV[ref])) if 'Reserved' in row['notes']}
        self.start = dict(self.net_at)

    def kind(self, net):
        f = self.func.get(net, '')
        if not f or FIXED_FUNCS.match(f) or f in ('ANALOG',):
            return None
        if f == 'GPIO':
            return ('gpio', None)
        m = re.match(r'ADC(\d)_INP\d+', f)
        if m:
            return ('adc', m.group(1))
        return ('sig', f)

    def can_host(self, pad, net, dest=True):
        """Whether pad may carry net. dest=False checks the function only (a net already there may stay)."""
        p = self.pin.get(pad)
        if p is None or p['type'] != 'I/O':
            return False
        if dest:
            nm = p['name']
            if nm in NEVER or pad in self.reserved:
                return False
            if nm in BOOT_DRIVES and not HARMLESS.match(short(net)):
                return False
            if HARMLESS.match(short(net)) and nm not in BOOT_DRIVES:   # a spare pad moves only to free a driven pin
                return False
            if nm in PULLED_OR_READ and (short(net) in MUST_AVOID or short(net) in ARM):
                return False
            if (short(net) in QUIET or short(net) in ARM) and self.special(pad):
                return False
        k = self.kind(net)
        if k is None:
            return False
        if k[0] == 'gpio':
            return 'GPIO' in p['signals']
        if k[0] == 'adc':
            return any(re.match(rf'ADC{k[1]}_INP\d+$', s) for s in p['signals'])
        return k[1] in p['signals']

    def special(self, pad):
        return any(SPECIAL.match(x) for x in self.pin[pad]['signals'])

    def adc_channel(self, pad, inst):
        ch = [s for s in self.pin[pad]['signals'] if re.match(rf'ADC{inst}_INP\d+$', s)]
        return ch[0] if ch else None


def valid(m, assign):
    """The energetic chapter's rules and EXTI lines, on a whole assignment pad -> net."""
    where = {short(n): p for p, n in assign.items() if n}
    if m.ref == 'U201':
        for n in FIRE:
            if n in where and m.pin[where[n]]['name'][1] != FIRE_PORT:
                return False
        for n in LOW_SIDE:
            if n in where and m.pin[where[n]]['name'][1] == FIRE_PORT:
                return False
        ls_ports = [m.pin[where[n]]['name'][1] for n in LOW_SIDE if n in where]
        if len(set(ls_ports)) != len(ls_ports):
            return False
    lines = {}
    for p, n in assign.items():
        if n in m.exti:
            k = int(m.pin[p]['name'][2:])
            if k in lines:
                return False
            lines[k] = n
    return True


CHAIN = FIRE | LOW_SIDE | ARM | {'NEW_FLIGHT_CLEAR_REQUEST'}


def beside(m, assign):
    """Pairs of pins that must not be neighbours and are: a fire pin or low-side select beside another, or beside an
    arm sense, the staging latch or the new-flight request, or beside a supply pad. One solder bridge must never join
    two inhibits, nor tie one to a signal that changes only when armed, where the pre-arm self-test can't see it, nor
    to a supply. The search pays a penalty for
    each pair, so it removes the ones it starts with (two, as captured: 43 / 44, 61 / 62) and never adds one."""
    if m.ref != 'U201':
        return set()
    where = {short(n): p for p, n in assign.items() if n and short(n) in CHAIN}
    supplies = [p for p in m.pin if m.pin[p]['type'] == 'Power' and p in m.xy]
    out = set()
    for x in FIRE | LOW_SIDE:
        if x not in where:
            continue
        a = m.xy[where[x]]
        for y in CHAIN - {x}:
            if y in where:
                b = m.xy[where[y]]
                if math.hypot(a[0] - b[0], a[1] - b[1]) < NEIGHBOUR_MM:
                    out.add(frozenset((x, y)))
        for sp in supplies:                  # nor beside a supply pad: VCAP's 1.3 V sits between the logic thresholds
            b = m.xy[sp]
            if math.hypot(a[0] - b[0], a[1] - b[1]) < NEIGHBOUR_MM:
                out.add(frozenset((x, m.pin[sp]['name'] + '.' + sp)))
    return out


def main():
    import pcbnew as K
    from engine import metrics as M
    ap = argparse.ArgumentParser()
    ap.add_argument('pcb')
    ap.add_argument('netlist')
    ap.add_argument('--out', required=True)
    ap.add_argument('--ref', action='append')
    ap.add_argument('--spec', default='croi2')
    ap.add_argument('--force', action='append', default=[],
                    help='a trial: REF:NET=PAD puts NET on PAD first and keeps it there; what it displaces must find a legal pin')
    a = ap.parse_args()
    refs = a.ref or ['U201', 'U401']
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    import importlib.util
    s = importlib.util.spec_from_file_location('spec', ROOT / 'hardware' / a.spec / 'layout' / 'spec.py')
    spec = importlib.util.module_from_spec(s); s.loader.exec_module(spec)
    b = K.LoadBoard(a.pcb)
    from build import stretch
    stretch(spec, float(round(K.ToMM(b.GetBoardEdgesBoundingBox().GetHeight()))))
    bd = M.BoardData(b, spec.ORIGIN, (spec.W, spec.H))
    weights = [(re.compile(rx), w) for rx, w in getattr(spec, 'NET_WEIGHTS', [])]
    wt = lambda n: next((w for rx, w in weights if rx.fullmatch(short(n))), 1.0)
    root = ET.parse(a.netlist).getroot()
    report, all_moves = {}, []
    for ref in refs:
        xy = {d['num']: (d['x'], d['y']) for d in bd.pads if d['ref'] == ref}
        m = MCU(ref, xy, root)
        partners = {}
        for net in set(n for n in m.net_at.values() if n):
            pts = [(d['x'], d['y']) for d in bd.by_net.get(net, []) if d['ref'] != ref and not d['ref'].startswith('TP')]
            if pts:
                partners[net] = pts

        def cost_of(pad, net):
            if not net or net not in partners or m.kind(net) is None:
                return 0.0
            x, y = m.xy[pad]
            c = wt(net) * min(math.hypot(px - x, py - y) for px, py in partners[net])
            if short(net) in MUST_AVOID and m.pin[pad]['name'] in NO_DEST:
                c += AVOID_PENALTY
            if (short(net) in QUIET or short(net) in ARM) and m.special(pad):
                c += AVOID_PENALTY
            return c

        assign = dict(m.net_at)
        locked = set()
        for f in a.force:                       # a trial group move: the net to its pad, the occupant to the net's pin
            r_, rest = f.split(':', 1)
            if r_ != ref:
                continue
            net, pad = rest.split('=')
            src = next(k for k, v in assign.items() if v and short(v) == net)
            assert m.can_host(pad, assign[src]), (net, pad)
            assign[src], assign[pad] = assign[pad], assign[src]
            locked.add(assign[pad])
        pads = sorted((p for p in m.pin if m.pin[p]['type'] == 'I/O' and p in m.xy), key=int)
        before = sum(cost_of(p, n) for p, n in assign.items())
        moves = 0
        def stuck(p, n):
            """A net that must leave its pin: an off-by-default output on a pulled or bootloader pin, or a fire-chain
            or arm net on a pin with a trace, tamper, RTC_OUT or LSCO output."""
            return bool(n) and m.kind(n) is not None and m.pin[p]['type'] == 'I/O' and (not m.can_host(p, n, dest=False)
                                or (short(n) in MUST_AVOID and m.pin[p]['name'] in NO_DEST)
                                or ((short(n) in QUIET or short(n) in ARM) and m.special(p))
                                or any(short(n) in pair for pair in cur))

        def pen(trial, names):
            """The change in forbidden neighbour pairs a move makes, as cost (only fire-chain nets can change them)."""
            if not any(x and short(x) in CHAIN for x in names):
                return 0.0
            return AVOID_PENALTY * (len(beside(m, trial)) - len(cur))

        cur = beside(m, assign)
        while True:
            cur = beside(m, assign)
            # while a net must still leave its pin, only moves that free one count, so the stuck nets go first, before
            # the ports and pins they need are taken; then the plain search
            stuck_pads = set() if getattr(stuck, 'given_up', False) else {p for p in pads if stuck(p, assign.get(p))}
            best = None
            for i, p in enumerate(pads):
                for q in pads[i + 1:]:
                    n, o = assign.get(p), assign.get(q)
                    if not n and not o:
                        continue
                    if stuck_pads and not ({p, q} & stuck_pads):
                        continue
                    if (n and m.kind(n) is None) or (o and m.kind(o) is None) or n in locked or o in locked:
                        continue
                    if n and not m.can_host(q, n):
                        continue
                    if o and not m.can_host(p, o):
                        continue
                    d = cost_of(q, n) + cost_of(p, o) - cost_of(p, n) - cost_of(q, o)
                    trial = None
                    if n and short(n) in CHAIN or o and short(o) in CHAIN:
                        trial = dict(assign); trial[p], trial[q] = o, n
                        d += pen(trial, (n, o))
                    if d < -MIN_GAIN and (best is None or d < best[0]):
                        if trial is None:
                            trial = dict(assign); trial[p], trial[q] = o, n
                        if valid(m, trial):
                            best = (d, p, q)
            # and three-way moves for a stuck net: it to a legal pin, that pin's net to a third, the third's net onto
            # its old pin; whichever move gains most
            rot = None
            for p in pads:
                n = assign.get(p)
                if not stuck(p, n):
                    continue
                for q in pads:
                    o = assign.get(q)
                    if q == p or not m.can_host(q, n) or (o and m.kind(o) is None) or o in locked:
                        continue
                    for r in pads:
                        h = assign.get(r)
                        if r in (p, q) or (h and (m.kind(h) is None or not m.can_host(p, h) or h in locked)):
                            continue
                        if o and not m.can_host(r, o):
                            continue
                        d = (cost_of(q, n) + cost_of(r, o) + cost_of(p, h)
                             - cost_of(p, n) - cost_of(q, o) - cost_of(r, h))
                        trial = dict(assign); trial[q], trial[r], trial[p] = n, o, h
                        d += pen(trial, (n, o, h))
                        if d < -MIN_GAIN and (rot is None or d < rot[0]):
                            if valid(m, trial):
                                rot = (d, p, q, r)
            if rot is not None and (best is None or rot[0] < best[0]):
                d, p, q, r = rot
                assign[q], assign[r], assign[p] = assign[p], assign[q], assign[r]
                moves += 1
                continue
            if best is None:
                if stuck_pads and not getattr(stuck, 'given_up', False):
                    stuck.given_up = True          # no move frees the rest: carry on with the plain search
                    continue
                break
            d, p, q = best
            assign[p], assign[q] = assign[q], assign[p]
            moves += 1
        after = sum(cost_of(p, n) for p, n in assign.items())
        changes = []
        for p in sorted(assign, key=int):
            if assign[p] != m.start.get(p) and assign[p]:
                old = next(k for k, v in m.start.items() if v == assign[p])
                f_old = m.func[assign[p]]
                k = m.kind(assign[p])
                f_new = m.adc_channel(p, k[1]) if k and k[0] == 'adc' else f_old
                changes.append({'net': short(assign[p]), 'from': [old, m.pin[old]['name']], 'to': [p, m.pin[p]['name']],
                                'function': f_old if f_new == f_old else f'{f_old} -> {f_new}',
                                'mm_before': round(cost_of(old, assign[p]) % AVOID_PENALTY / wt(assign[p]), 1),
                                'mm_after': round(cost_of(p, assign[p]) % AVOID_PENALTY / wt(assign[p]), 1),
                                'left_a_must_avoid_pin': short(assign[p]) in MUST_AVOID and m.pin[old]['name'] in NO_DEST})
        report[ref] = {'cost_before': round(before, 1), 'cost_after': round(after, 1), 'swaps': moves, 'moved_nets': changes,
                       'still_on_must_avoid_pins': [short(n) for p, n in assign.items() if stuck(p, n)],
                       'neighbour_pairs_left': sorted(sorted(x) for x in beside(m, assign))}
        all_moves += [(ref, c) for c in changes]
        # the trial netlist: each moved net's node to its new pad; vacated pads become unconnected
        nodes = {}
        for n in root.findall('nets/net'):
            for x in n.findall('node'):
                if x.get('ref') == ref:
                    nodes[x.get('pin')] = (n, x)
        newnet = {p: assign[p] for p in assign}
        nets_el = root.find('nets')
        for p, (n, x) in list(nodes.items()):
            want = newnet.get(p)
            cur = None if n.get('name').startswith('unconnected-') else n.get('name')
            if want == cur:
                continue
            n.remove(x)
            if not list(n.findall('node')):
                nets_el.remove(n)
            if want:
                tgt = next((e for e in nets_el.findall('net') if e.get('name') == want), None)
                tgt.append(x)
            else:
                e = ET.SubElement(nets_el, 'net', code=str(90000 + int(p)),
                                  name=f"unconnected-({ref}-{x.get('pinfunction') or m.pin[p]['full']}-Pad{p})")
                e.append(x)
    ET.ElementTree(root).write(out / 'netlist.xml', encoding='utf-8', xml_declaration=True)
    (out / 'moves.json').write_text(json.dumps(report, indent=1) + '\n')
    for ref, r in report.items():
        print(ref, 'cost', r['cost_before'], '->', r['cost_after'], '| swaps', r['swaps'], '| nets moved', len(r['moved_nets']),
              '| still on avoid pins', r['still_on_must_avoid_pins'])
        for c in r['moved_nets']:
            print('   ', c['net'], c['from'], '->', c['to'], c['function'], c['mm_before'], '->', c['mm_after'],
                  '(off an avoid pin)' if c['left_a_must_avoid_pin'] else '')


if __name__ == '__main__':
    main()
