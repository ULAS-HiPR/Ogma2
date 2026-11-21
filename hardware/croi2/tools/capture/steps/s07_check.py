"""Check for step 7.

1. The 64-pad map against ST's open pin data (github.com/STMicroelectronics/STM32_open_pin_data,
   mcu/STM32H563RITx.xml and mcu/IP/GPIO-STM32H56x_gpio_v1_0_Modes.xml, fetched to PINDATA):
   every pad's port or supply name, and every alternate-function row's signal and AF number.
2. Netlist: every U401 pad on the map's net (PC3 / PC4 unconnected, as reservations), the
   LQFP100's pads 65-100 gone, C405 / C408 removed; nothing else moves.
3. ERC: the LORA_RXEN / LORA_TXEN dangling labels close; nothing new.
"""
import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture as C
from s07_comms_mcu import MAP, RESERVED, FP

PINDATA = Path('/tmp/claude-0/pindata/mcu')
CLOSES = {"Global Label 'LORA_RXEN'", "Global Label 'LORA_TXEN'"}
DEBUG = {'SWD': ('DEBUG_JTMS-SWDIO', 'DEBUG_JTCK-SWCLK'), 'TRACESWO': ('DEBUG_JTDO-SWO',)}


def st_check(rows):
    ns = {'m': 'http://dummy.com'}
    pins = {}
    for p in ET.parse(PINDATA / 'STM32H563RITx.xml').getroot().findall('m:Pin', ns):
        pins[p.get('Position')] = (p.get('Name'), [s.get('Name') for s in p.findall('m:Signal', ns)])
    af = {}
    for gp in ET.parse(PINDATA / 'IP/GPIO-STM32H56x_gpio_v1_0_Modes.xml').getroot().iter():
        if gp.tag.endswith('GPIO_Pin'):
            port = re.match(r'P[A-Z]\d+', gp.get('Name', ''))
            for ps in gp:
                if port and ps.tag.endswith('PinSignal'):
                    af[(port.group(0), ps.get('Name'))] = [v.text for v in ps.iter() if v.tag.endswith('PossibleValue')]
    n_af = 0
    for r in rows:
        name, signals = pins[r['pad']]
        want = r['port_or_supply'].split('/')[0]                      # VDDA/VREF+: VREF+ double-bonded
        assert re.match(rf'{re.escape(want)}(\W|$)', name), (r['pad'], want, name)
        if r['alternate_function']:
            sigs = DEBUG.get(r['function'], (r['function'],))
            sig = [s for s in sigs if s in signals]
            assert len(sig) == 1, (r['pad'], r['function'], signals)
            vals = af[(want, sig[0])]
            assert any(v.startswith(f"GPIO_{r['alternate_function']}_") for v in vals), (r['pad'], sig, vals)
            n_af += 1
    return len(rows), n_af


if __name__ == '__main__':
    rows = list(csv.DictReader(MAP.open()))
    n_pads, n_af = st_check(rows)
    print(f'ST pin data: {n_pads} pads and {n_af} alternate-function rows match')
    C.export('s07')
    ca, pa = C.load_net('s06')
    cb, pb = C.load_net('s07')
    state = {('U401', str(n)): None for n in range(65, 101)}
    for r in rows:
        state[('U401', r['pad'])] = 'NC' if r['pad'] in RESERVED else r['net']
    for ref in ('C405', 'C408'):
        state.update({(ref, p): None for (r, p) in pa if r == ref})
    expect = {k: v for k, v in state.items() if pa.get(k) != v}
    changed = {('U401', 'value'): ('STM32H563VIT6', 'STM32H563RIT6'), ('U401', 'fp'): ('Ogma2:STM32H563VIT6', FP)}
    rep = C.check('s06', 's07', expect, expect_removed=['C405', 'C408'], expect_changed=changed)
    fixed, new, counts = C.erc_delta('s06', 's07')
    print('problems:', rep['problems'] or 'none')
    print('fixed:', fixed)
    print('new:', new)
    assert not rep['problems'] and {x[3] for x in fixed} == CLOSES and not new
    print('step 7 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;",
          f'ERC closed {len(fixed)}, added 0;', dict(counts))
