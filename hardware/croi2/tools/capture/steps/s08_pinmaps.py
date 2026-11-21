"""Step 8b, close-out: the as-captured pin maps.

libraries/inputs/{flight,comms}-pinout.csv become the as-captured allocations with exact native net
names. The 7 September versions (functional shorthand) move to history/baseline-2026-09-08/inputs.

Flight: the 22 September 100-pad map (docs/architecture/proposed-flight-pinout.csv) amended by the
capture specification's "Flight pad changes" row: 23 pads.
Comms: the 64-pad map (docs/architecture/proposed-comms-pinout.csv), with PC3 / PC4 unconnected
as drawn at step 7 (the map's "MCU-only reservation, no external connection").

Every alternate-function row of both maps is checked against ST's open pin data (as in step 7).
"""
import csv
import io
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BOARD = Path(__file__).resolve().parents[3]
REPO = BOARD.parents[1]
DOCS = REPO / 'docs/architecture'
INPUTS = BOARD / 'libraries/inputs'
ARCHIVE = BOARD / 'history/baseline-2026-09-08/inputs'
PINDATA = Path('/tmp/claude-0/pindata/mcu')
FIELDS = ['role', 'mpn', 'pad', 'port_or_supply', 'net', 'function', 'alternate_function', 'notes']

FLIGHT = {  # pad: (net, function, AF, note) from the capture specification's flight pad changes
    '4': ('FC_POWER_HOLD', 'GPIO', '', 'Output; R1015 1M pull-down; high after launch detect (D-2Nov.18)'),
    '5': ('MAG_INT', 'GPIO', '', 'EXTI6; optional magnetometer data-ready (D-2Nov.11)'),
    '6': ('FLIGHT_VBAT', 'BACKUP_SUPPLY', '', 'D201 from FLIGHT_3V3; C207 100nF and C219 100uF (D-6.4)'),
    '26': ('RESET_MEMORY', 'GPIO', '', 'Input; reset-memory RC node (D-19Nov.3)'),
    '35': ('TP_STROBE', 'GPIO', '', 'Output; R203 to TP201 timing strobe; R205 holds it low at reset (D-19Nov.3)'),
    '38': ('PYRO1_FIRE', 'GPIO', '', 'Output; U6304 IN; R6303 100k pull-down (D-6.2, D-2Nov.1)'),
    '39': ('SERVICE_POWER_EN', 'GPIO', '', 'Output; U1601 EN; R1602 pull-down (D-6.5)'),
    '40': ('PYRO2_FIRE', 'GPIO', '', 'Output; U6404 IN; R6403 100k pull-down (D-6.2, D-2Nov.1)'),
    '41': ('CAN_STB', 'GPIO', '', 'Output; standby for both transceivers (D-5Nov.3)'),
    '43': ('PYRO3_FIRE', 'GPIO', '', 'Output; U6502 AND with STAGE_ELIGIBLE; R6501 100k pull-down (D-7.2)'),
    '44': ('RECOVERY_ARM_SENSE', 'GPIO', '', 'Input; U6103 OUTA via R6107 (D-5Nov.3)'),
    '45': ('STAGE_INHIBIT_LATCHED', 'GPIO', '', 'Input; U6001 Q-bar via R6005 1k (D-7.2)'),
    '46': ('STAGING_ARM_SENSE', 'GPIO', '', 'Input; STAGE_ARM_INVALID via R6108, read inverted (D-7.2, D-2Nov.11)'),
    '57': ('TP_PD10', 'GPIO', '', 'Spare test pad TP204; input with pull-down (D-19Nov.3)'),
    '61': ('PYRO3_LS_SELECT', 'GPIO', '', 'Output; Q6501 gate via R6504; R6502 100k pull-down (D-5Nov.3)'),
    '63': ('TP_PC6', 'GPIO', '', 'Spare test pad TP202; input with pull-down (D-19Nov.3)'),
    '64': ('TP_PC7', 'GPIO', '', 'Spare test pad TP203; input with pull-down; never drives, neighbours PC8 (D-19Nov.3)'),
    '65': ('PYRO2_LS_SELECT', 'GPIO', '', 'Output; Q6401 gate via R6404; R6402 100k pull-down (D-5Nov.3)'),
    '66': ('MAG_SDA', 'I2C3_SDA', 'AF4', 'Via R3705 22R; R3703 2.7k pull-up (D-2Nov.11)'),
    '67': ('MAG_SCL', 'I2C3_SCL', 'AF4', 'Via R3704 22R; R3702 2.7k pull-up (D-2Nov.11)'),
    '68': ('PYRO1_LS_SELECT', 'GPIO', '', 'Output; Q6301 gate via R6304; R6302 100k pull-down (D-2Nov.1)'),
    '69': ('CAN2_TX', 'FDCAN2_TX', 'AF9', 'Bus 2 via U504 (D-5Nov.3)'),
    '91': ('CAN2_RX', 'FDCAN2_RX', 'AF9', 'Bus 2 via U504 (D-5Nov.3)'),
}
COMMS = {'11': 'Reserved LORA_RXEN: MCU-only, no external connection (no-connect); firmware sets analog',
         '24': 'Reserved LORA_TXEN: MCU-only, no external connection (no-connect); firmware sets analog'}
DEBUG = {'SWD': ('DEBUG_JTMS-SWDIO', 'DEBUG_JTCK-SWCLK'), 'TRACESWO': ('DEBUG_JTDO-SWO',)}


def af_check(rows, xml):
    ns = {'m': 'http://dummy.com'}
    pins = {p.get('Position'): (p.get('Name'), [s.get('Name') for s in p.findall('m:Signal', ns)])
            for p in ET.parse(PINDATA / xml).getroot().findall('m:Pin', ns)}
    af = {}
    for gp in ET.parse(PINDATA / 'IP/GPIO-STM32H56x_gpio_v1_0_Modes.xml').getroot().iter():
        port = re.match(r'P[A-Z]\d+', gp.get('Name', '')) if gp.tag.endswith('GPIO_Pin') else None
        for ps in (gp if port else []):
            if ps.tag.endswith('PinSignal'):
                af[(port.group(0), ps.get('Name'))] = [v.text for v in ps.iter() if v.tag.endswith('PossibleValue')]
    n = 0
    for r in rows:
        name, signals = pins[r['pad']]
        want = r['port_or_supply'].split('/')[0]
        assert re.match(rf'{re.escape(want)}(\W|$)', name), (r['pad'], want, name)
        if r['alternate_function'] == 'ANALOG':                       # ADC inputs: the channel is on the pad
            assert r['function'] in signals, (r['pad'], r['function'], signals)
            n += 1
        elif r['alternate_function']:
            sig = [s for s in DEBUG.get(r['function'], (r['function'],)) if s in signals]
            assert len(sig) == 1, (r['pad'], r['function'])
            assert any(v.startswith(f"GPIO_{r['alternate_function']}_") for v in af[(want, sig[0])]), (r['pad'], sig)
            n += 1
    return n


def write(path, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, FIELDS, quoting=csv.QUOTE_ALL, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    path.write_text(buf.getvalue())


def build():
    flight = list(csv.DictReader((DOCS / 'proposed-flight-pinout.csv').open()))
    for r in flight:
        if r['pad'] in FLIGHT:
            r['net'], r['function'], r['alternate_function'], r['notes'] = FLIGHT[r['pad']]
    comms = list(csv.DictReader((DOCS / 'proposed-comms-pinout.csv').open()))
    for r in comms:
        if r['pad'] in COMMS:
            r['net'], r['function'], r['notes'] = 'NC', 'ANALOG', COMMS[r['pad']]
    assert len(flight) == 100 and len(comms) == 64
    counts = af_check(flight, 'STM32H563VITx.xml'), af_check(comms, 'STM32H563RITx.xml')
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for name, rows in (('flight-pinout.csv', flight), ('comms-pinout.csv', comms)):
        if not (ARCHIVE / name).exists():
            shutil.copy2(INPUTS / name, ARCHIVE / name)
        write(INPUTS / name, rows)
    return counts


if __name__ == '__main__':
    print('alternate-function rows checked against ST data (flight, comms):', build())
