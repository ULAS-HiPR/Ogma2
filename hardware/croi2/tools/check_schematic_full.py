"""Verify native exported connectivity, the as-captured MCU allocations and the capture safety assertions.

Generated expectations (full-expected-pins.json) check netlist parity pin by pin. The fixed
assertions check architectural boundaries: the capture assertions of
docs/architecture/11-verification.md (numbered A1-A26) and the board's retained checks.
Neither is an analog simulation or qualification. Rewritten at capture close-out, 21 Nov 2026.
"""
import argparse
import copy
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

HW = Path(__file__).resolve().parents[1]
ENERGETIC = re.compile(r'PYRO|ARM|STAGE|OUTPUT\d|SERVO')
OUTPUT_ENABLES = re.compile(r'^(PYRO\d_(FIRE|LS_SELECT|HS_ENABLE|GATE)|STAGE_ELIGIBLE|STAGE_INHIBIT_LATCHED|STAGE_ARM_INVALID)$')
# Test points (D-22Nov.9): three sizes, by what the probe does there.
TP_GND = ('TestPoint:TestPoint_Keystone_5010-5014_Multipurpose', '5011', 'C238127')     # black loop, board edge
TP_LOOP = ('Ogma2:TestPoint_Keystone_5190TR_ColorKeyed', '5194TR', 'C22388408')         # yellow SMT loop, probe stays on (D-22Nov.24)
TP_PAD = ('TestPoint:TestPoint_Pad_D1.0mm', None, None)                                  # 1.0 mm pad, probe touches
TP_LOOP_NETS = frozenset({   # each regulator or switch output, the strobe, PPS
    'VBAT_CROI_INPUT', 'VBAT_PROTECTED', 'LOGIC_SELECTED', '4V_PRE', 'CORE_HELD_4V', 'FLIGHT_3V3', 'COMMS_3V3',
    '3V3_OPTIONAL', 'LORA_3V3', 'CAN_3V3', 'BOOT_3V3', 'NOR_3V3', 'GNSS_3V3', 'FOINSE_AUX_3V3', 'USB_VBUS',
    'USB_LIMITED', 'TP_STROBE_PAD', 'GNSS_PPS'})
TP_SENSE_ONLY = frozenset({f'ADC_PYRO{n}_{k}' for n in (1, 2, 3) for k in ('CONTINUITY', 'CURRENT')}
                          | {'RECOVERY_ARM_SENSE', 'STAGING_ARM_SENSE', 'ADC_PYRO_RAIL'})


# Reset-state rules for the MCU pins (D-22Nov.25, stage B2 brief step 7.9).
# DS14258 rev 6 (STM32H562/563 datasheet), table 14, note 7: after reset the debug pins are alternate functions, with
# internal pull-ups on PA13, PA15 and PB4 (30-50 kohm, table 58) and a pull-down on PA14, until firmware changes them.
DEBUG_PULL_UPS = frozenset({'PA13', 'PA15', 'PB4'})
# AN2606 rev 70, table 137 (STM32H562/563/573): the pins the ROM bootloader drives (USART TX, SPI MISO, I2C and I3C,
# FDCAN2 TX, USB) and the ones it only reads (USART RX, SPI SCK / MOSI / NSS, FDCAN2 RX).
BOOT_DRIVES = frozenset({'PA9', 'PA2', 'PD8', 'PA6', 'PB14', 'PC11', 'PA8', 'PC9', 'PD12', 'PD13', 'PB6', 'PB7',
                         'PB13', 'PA11', 'PA12'})
BOOT_PINS = BOOT_DRIVES | {'PA10', 'PA3', 'PD9', 'PA4', 'PA5', 'PA7', 'PB10', 'PB12', 'PC1', 'PA15', 'PC10', 'PC12', 'PB5'}
# U201's pins with an output something other than a running GPIO can drive: trace data and the debug trigger (a
# debugger), the backup domain's tamper, RTC_OUT and LSCO outputs (they outlive a system reset). ST's pin data,
# STM32H563VITx.xml (STM32_open_pin_data 45c0459, libraries/inputs/st-open-pin-data).
FLIGHT_SPECIAL_PINS = frozenset({'PE2', 'PE3', 'PE4', 'PE5', 'PE6', 'PC13', 'PC1', 'PA0', 'PA1', 'PA2', 'PB2', 'PC7', 'PC8',
                                 'PC12', 'PD2'})
FIRE_OR_ARM = re.compile(r'^(PYRO\d_(FIRE|LS_SELECT)|RECOVERY_ARM_SENSE|STAGING_ARM_SENSE|STAGE_INHIBIT_LATCHED|NEW_FLIGHT_CLEAR_REQUEST)$')


def reset_pin_faults(root):
    """(A24, A25) on a netlist: off-by-default nets on a pulled-up or bootloader-driven pin; fire or arm nets on a
    bootloader pin."""
    actual = node_map(root)
    port = {(n.get('ref'), n.get('pin')): re.match(r'P[A-K]\d+', n.get('pinfunction') or '')
            for net in root.findall('nets/net') for n in net.findall('node')}
    pulled_down = {net for (r, p), net in actual.items() if r.startswith('R') and net != 'GND'
                   and actual.get((r, '1' if p == '2' else '2')) == 'GND'}
    a24, a25 = [], []
    for (r, p), net in sorted(actual.items()):
        m = port.get((r, p)) if r in ('U201', 'U401') else None
        if not m:
            continue
        if (m.group(0) in DEBUG_PULL_UPS or m.group(0) in BOOT_DRIVES) and net in pulled_down:
            a24.append(f'{r} {m.group(0)} {net}')
        if m.group(0) in BOOT_PINS and FIRE_OR_ARM.match(net):
            a25.append(f'{r} {m.group(0)} {net}')
    return a24, a25


def node_map(root):
    out = {}
    for net in root.findall('nets/net'):
        for pin in net.findall('node'):
            key = (pin.get('ref'), pin.get('pin'))
            assert key not in out, ('duplicate pin', key)
            out[key] = net.get('name').rsplit('/', 1)[-1]
    return out


def verify(root, expected):
    actual = node_map(root)
    count = 0
    for ref, pins in expected.items():
        if ref.startswith('#'):
            continue  # Power symbols are absent from the netlist BOM.
        for pin, net in pins.items():
            found = actual.get((ref, pin))
            if net is None:
                assert found is None or found.startswith('unconnected-'), (ref, pin, 'NC', found)
            else:
                assert found == net, (ref, pin, net, found)
            count += 1
    assert set(actual).issubset({(r, p) for r, ps in expected.items() for p in ps}), 'Unexpected pins'
    return actual, count


def expected_from(root):
    """The generated expectation: every exported pin and its net (None for an unconnected pad)."""
    out = defaultdict(dict)
    for (ref, pin), net in sorted(node_map(root).items()):
        out[ref][pin] = None if net.startswith('unconnected-') else net
    return dict(out)


def check(project, netlist, erc):
    root = ET.parse(netlist).getroot()
    expected = json.loads((project / 'full-expected-pins.json').read_text())
    actual, pincount = verify(root, expected)
    parts = {c.get('ref'): c for c in root.findall('components/comp')}
    nets = defaultdict(set)
    for key, net in actual.items():
        if not key[0].startswith('TP'):          # a test point is a probe, not a conductor: checked on its own below
            nets[net].add(key)
    tps = {r: actual[(r, '1')] for r in parts if r.startswith('TP')}
    ptype = {(n.get('ref'), n.get('pin')): n.get('pintype', '') for net in root.findall('nets/net') for n in net.findall('node')}
    pfunc = {(n.get('ref'), n.get('pin')): n.get('pinfunction', '') for net in root.findall('nets/net') for n in net.findall('node')}
    supplies = {net for net, keys in nets.items() if net == 'GND' or any(ptype[k].startswith(('power_in', 'power_out')) for k in keys)}
    refs = lambda net: {r for r, p in nets.get(net, ())}
    value = lambda ref: parts[ref].findtext('value')
    dnp = [r for r, c in parts.items() if any(p.get('name') == 'dnp' for p in c.findall('property'))]
    checks = []

    def require(condition, description):
        assert condition, description
        checks.append(description)

    def reach(start_nets, through=('R', 'F', 'L', 'D', 'FB', 'JP')):
        """Nets reachable from start_nets through two-terminal passives, never entering a supply net."""
        seen, todo = set(), [n for n in start_nets if n not in supplies]
        while todo:
            net = todo.pop()
            if net in seen:
                continue
            seen.add(net)
            for ref, pin in nets[net]:
                if re.match(rf'^({"|".join(through)})\d', ref) and not ref.startswith(('FL',)):
                    for other in {n for (r, p), n in actual.items() if r == ref} - {net}:
                        if other not in supplies and not other.startswith('unconnected-'):
                            todo.append(other)
        return seen

    # ---- as-captured MCU allocations (libraries/inputs, exact native nets)
    for role, ref, n in (('flight', 'U201', 100), ('comms', 'U401', 64)):
        rows = list(csv.DictReader((HW / f'libraries/inputs/{role}-pinout.csv').open()))
        require(len(rows) == n and {r['pad'] for r in rows} == {str(i) for i in range(1, n + 1)}, f'{role}: {n} allocation rows')
        for row in rows:
            got = actual.get((ref, row['pad']), 'unconnected-')
            if row['net'] == 'NC':
                require(got.startswith('unconnected-'), f"{ref}.{row['pad']} intentionally unused")
            else:
                require(got == row['net'], f"{ref}.{row['pad']}: as-captured allocation {row['net']}")
    for ref, mpn in [('U201', 'STM32H563VIT6'), ('U401', 'STM32H563RIT6'), ('U3604', 'MX66L2G45GMI00'),
                     ('U4504', 'MAX-M10S-00B'), ('U4606', 'Wio-LR2021'), ('U3701', 'MMC5983MA'), ('U6502', 'SN74LVC1G08DBVR'),
                     ('U3104', 'LSM6DSV32XTR'), ('BZ9001', 'SMT-1028-T-2-R'), ('Q9001', 'AO3400A')]:
        require(value(ref) == mpn, f'{ref}: accepted exact device')
    require(set(parts) == {ref for ref in expected if not ref.startswith('#')}, 'Every native component covered')
    assert parts['U4606'].findtext("fields/field[@name='MPN']") == 'Wio-LR2021 / SKU 100058045', 'Stale radio procurement identity'
    assert parts['U4606'].findtext("fields/field[@name='Manufacturer']") == 'Seeed Studio', 'Stale radio manufacturer'

    # ---- processors: supplies and boundaries
    require(actual[('U201', '22')] != actual[('U201', '11')], 'Flight VDDA link is not bypassed by a drawing short')
    require(actual[('U401', '13')] == 'COMMS_VDDA' and actual[('U401', '19')] == 'COMMS_3V3', 'Comms VDDA/VREF+ on its own linked rail')
    for pin in ['48', '98']:
        require(actual[('U201', pin)] == 'FLIGHT_VCAP', f'Flight VCAP pad {pin} is not a 3.3 V supply')
    for pin in ['30', '62']:
        require(actual[('U401', pin)] == 'COMMS_VCAP', f'Comms VCAP pad {pin} is not a 3.3 V supply')
    require(actual[('U201', '6')] == 'FLIGHT_VBAT' and actual[('D201', '1')] == 'FLIGHT_VBAT' and actual[('D201', '2')] == 'FLIGHT_3V3',
            'Flight VBAT fed from FLIGHT_3V3 through D201, never the vehicle battery (D-6.4)')
    require(actual[('U401', '1')] == 'COMMS_3V3', 'Comms backup pin on COMMS_3V3')
    require(actual[('U401', '29')] == actual[('U4301', '1')] == 'CC_COMMS_TO_FLIGHT'
            and actual[('U401', '52')] == actual[('U4301', '8')] == 'CC_FLIGHT_TO_COMMS',
            'Inter-MCU USART3 on PB10 / PC11 through U4301 (TX from PC10, D-22Nov.25)')
    require(actual[('U4302', '4')] == 'COMMS_MR_N', 'Flight reset buffer drives comms supervisor MR, not NRST bus')
    require(actual[('U201', '14')] != actual[('U401', '7')], 'No cross-reset net short')

    # ---- GNSS and radio (unchanged by capture)
    for pin, net in {'1': 'GND', '2': 'GNSS_RX_ISO', '3': 'GNSS_TX_ISO', '4': 'GNSS_PPS_ISO', '7': 'GNSS_3V3', '8': 'GNSS_3V3',
                     '9': 'GNSS_RESET_N_ISO', '10': 'GND', '11': 'GNSS_RF', '12': 'GND'}.items():
        require(actual[('U4504', pin)] == net, f'MAX-M10S manufacturer pin {pin}: {net}')
    for pin in ['5', '6', '13', '14', '15', '16', '17', '18']:
        require(actual[('U4504', pin)].startswith('unconnected-'), f'MAX unused pin {pin}; SAFEBOOT18 and backup6 unloaded')
    require(nets['GNSS_RF'] == {('U4504', '11'), ('J4501', '1'), ('D4501', '1')}, 'Single passive GNSS RF path with ESD; no bias supply')
    require(actual[('J4501', '2')] == actual[('D4501', '2')] == 'GND', 'GNSS SMA and ESD returns')
    require(value('J4501') == '132134' and value('D4501') == 'PESD5V0F1BL,315', 'GNSS SMA and low-capacitance ESD selections (D-22Nov.8)')
    for pin, net in {'1': 'LORA_3V3', '2': 'LORA_DIO1_MOD', '3': 'LORA_RESET_N_MOD', '4': 'LORA_MISO_MOD', '5': 'LORA_MOSI_MOD',
                     '6': 'LORA_SCK_MOD', '7': 'LORA_NCS_MOD', '8': 'LORA_BUSY_MOD', '9': 'GND', '10': 'LORA_RF_SUBG',
                     '11': 'GND', '12': 'GND', '14': 'GND', '15': 'GND', '20': 'GND'}.items():
        require(actual[('U4606', pin)] == net, f'Wio manufacturer pin {pin}: {net}')
    for pin in ['13', '16', '17', '18', '19', '21', '22']:
        require(actual[('U4606', pin)].startswith('unconnected-'), f'Wio unused RF/DIO pin {pin} NC')
    require(nets['LORA_RF_SUBG'] == {('U4606', '10'), ('J4601', '1'), ('D4601', '1')} and actual[('J4601', '2')] == 'GND', 'Single sub-GHz host RF path with ESD (D4601, D-22Nov.20)')
    require(value('J4601') == '132134' and parts['J4601'].findtext('footprint') == 'Ogma2:SMA_Amphenol_132134_Vertical', 'Approved vertical SMA')
    require(actual[('R4621', '1')] == 'LORA_3V3' and actual[('R4621', '2')] == 'LORA_BUSY_MOD', 'Open-drain BUSY pulled to switched rail')
    for i, sig in enumerate(['SCK', 'MOSI', 'MISO', 'NCS', 'RESET_N', 'BUSY', 'DIO1']):
        ref = f'R{4614 + i}'
        require(actual[(ref, '1')] == f'LORA_{sig}_ISO' and actual[(ref, '2')] == f'LORA_{sig}_MOD' and value(ref) == '470R', f'{sig} series boundary')
    require(not {'U4605', 'C4605', 'R4606', 'R4607'} & set(parts), 'Obsolete external RF-switch control components removed')
    require(actual[('U4604', '13')] == 'GND' and all(actual[('U4604', p)].startswith('unconnected-') for p in ['11', '12']), 'Unused isolation channel disabled')

    # ---- source, master enable, monitoring
    require(value('R1006') == '22.1k 1%' and actual[('R1006', '1')] == 'BAT_SHDN_N' and actual[('R1006', '2')] == 'GND', 'Source enable defaults OFF locally')
    for ref, pins in {'D1002': {'1': 'VBAT_CROI_INPUT', '3': 'BAT_SW_DIODE'}, 'R1012': {'1': 'BAT_SW_DIODE', '2': 'BAT_SW_RMID'},
                      'R1013': {'1': 'BAT_SW_RMID', '2': 'BAT_SWITCH_3V'}, 'U1002': {'1': 'BAT_SWITCH_3V', '2': 'GND'},
                      'J103': {'1': 'BAT_SWITCH_3V', '2': 'BAT_SHDN_N'}, 'C1006': {'1': 'BAT_SHDN_N', '2': 'GND'}}.items():
        for pin, net in pins.items():
            require(actual[(ref, pin)] == net, f'External master {ref}.{pin}: {net}')
    require(refs('BAT_SHDN_N') == {'U101', 'R1006', 'J103', 'C1006', 'D1003'}, 'Master-enable return: no firmware path except the FC_POWER_HOLD diode')
    for pin, net in {'1': 'VBAT_CROI_INPUT', '2': 'GND', '3': 'FOINSE_AUX_3V3', '4': 'GND', '5': 'FOINSE_SCL_EXT',
                     '6': 'FOINSE_SDA_EXT', '7': 'FOINSE_FAULT_N_EXT', '8': 'CROI_POWER_HOLD'}.items():
        require(actual[('J102', pin)] == net, f'Samtec contact {pin} / {net}')
    require(actual[('U101', '17')] == actual[('U101', '18')] == 'VBAT_SHUNT_IN', 'Both eFuse OUT pads feed upstream shunt node')
    require(actual[('R7101', '1')] == 'VBAT_SHUNT_IN' and actual[('R7101', '2')] == 'VBAT_PROTECTED', 'Bulk shunt separates source protection from loads')
    require(actual[('J101', '1')] == actual[('J102', '1')] == 'VBAT_CROI_INPUT', 'Both mutually exclusive sources feed the same measured path')
    require(actual[('U7101', '1')] == actual[('U7101', '2')] == 'GND', 'Croi INA228 address 0x40')
    require(actual[('U7101', '4')] == 'FOINSE_SDA_EXT' and actual[('U7101', '5')] == 'FOINSE_SCL_EXT', 'Current monitor behind existing optional bus boundary')
    require(actual[('R7104', '1')] == 'ENERGY_TAP', 'Battery monitor VBUS reads ENERGY_TAP (D-2Nov.5)')
    require(actual[('R7105', '1')] == 'FOINSE_AUX_3V3' and actual[('R7105', '2')] == 'CROI_MON_3V3', 'Local current monitor operates without Foinse board')
    require(actual[('U1401', '1')] == 'CORE_INPUT_EN' and refs('CORE_INPUT_EN') == {'U1401', 'R1210', 'R1204'}
            and actual[('R1210', '1')] == '4V_PRE' and value('R1210') == '200k 1%' and value('R1204') == '100k',
            'Core input enable from its own 4V_PRE divider, whatever the source (D-6.5)')
    require(actual[('U1701', '7')] == 'CORE_HELD_4V', 'Flight LDO input on the held core rail')
    require(actual[('U1601', '3')] == 'SERVICE_POWER_EN' and actual[('U201', '39')] == 'SERVICE_POWER_EN', 'Service restart on PE8 (D-6.5)')

    # ---- CAN
    for bus, (j, d, r, u) in {'': ('J501', 'D501', 'R510', 'U503'), '2': ('J502', 'D502', 'R515', 'U505')}.items():
        for net, pin in [(f'CAN{bus}_H', '1'), (f'CAN{bus}_L', '2')]:
            require(nets[net] == {(j, pin), (d, pin), (r, pin), (u, '7' if pin == '1' else '6')}, f'Exact {net} conductors; no H/L short')
        require(value(j) == 'G125-MS10605M2P' and all(actual[(j, p)].startswith('unconnected-') for p in '456'), f'{j}: Gecko-SL, spare contacts NC')
    require(actual[('U502', '1')] != actual[('U502', '14')], 'CAN translator supply domains remain separate')
    require(actual[('U503', '3')] == actual[('U503', '5')] == actual[('U505', '3')] == actual[('U505', '5')] == 'CAN_3V3', 'Both transceivers on the switched CAN rail')
    require(refs('CAN_STB') == {'U201', 'R505', 'U502', 'U504'} and actual[('U201', '62')] == 'CAN_STB',
            'One standby line (PD15) for both buses (D-5Nov.3, D-22Nov.25)')

    # ---- status and service
    for pin, net in {'2': 'FLIGHT_STATUS_LED1', '3': 'GND', '4': 'FLIGHT_NOT_READY', '5': 'FLIGHT_3V3'}.items():
        require(actual[('U9101', pin)] == net, f'Inverter manufacturer DBV contact {pin}')
    require(value('U9101') == 'SN74LVC1G04DBVR' and actual[('R9102', '1')] == 'FLIGHT_STATUS_LED1' and value('R9102') == '47k', 'Readiness inverter and its default')
    require('BZ9001' not in dnp and actual[('D9002', '1')] == actual[('BZ9001', '1')] == '3V3_OPTIONAL'
            and actual[('D9002', '2')] == actual[('BZ9001', '2')] == actual[('Q9001', '3')] == 'BUZZER_LOW'
            and refs('BUZZER_LOW') == {'BZ9001', 'D9002', 'Q9001'} and actual[('Q9001', '2')] == 'GND',
            'Magnetic sounder: one flyback diode (D9002) across its coil, no bleed resistor, AO3400A low side (D-21Nov.20)')
    require(not [n for n in nets if 'USB_CONFIG_OK' in n] and actual[('U4303', '10')] == 'GND'
            and actual[('U4303', '5')].startswith('unconnected-'), 'USB_CONFIG_OK dropped; its translator channel tied off (D-21Nov.14)')
    require(not [n for n in nets if 'SERVO' in n] and not [r for r in parts if r.startswith(('U68', 'J6602'))], 'No servo nets or parts (D-19Nov.2)')

    # ---- capture safety assertions (11-verification.md)
    for n, fire, sel in ((1, 'U6304', 'Q6301'), (2, 'U6404', 'Q6401'), (3, 'U6502', 'Q6501')):
        for net in (f'PYRO{n}_FIRE', f'PYRO{n}_LS_SELECT'):
            pulls = [r for r in refs(net) if r.startswith('R') and value(r) == '100k' and 'GND' in {actual[(r, '1')], actual[(r, '2')]}]
            drivers = {k for k in nets[net] if k[0] == 'U201' or ptype[k].startswith(('output', 'bidirectional', 'tri_state', 'power_out', 'open'))}
            require(len(pulls) == 1 and {k[0] for k in drivers} == {'U201'}, f'A1: {net} has one 100k pull-down and no driver but its MCU pin')
        gate, series = f'PYRO{n}_GATE', f'R6{n + 2}04'
        gp = [r for r in refs(gate) if r.startswith('R') and value(r) == '100k' and 'GND' in {actual[(r, '1')], actual[(r, '2')]}]
        require(len(gp) == 1 and refs(gate) == {sel, series, gp[0]} and {actual[(series, '1')], actual[(series, '2')]} == {gate, f'PYRO{n}_LS_SELECT'},
                f'A1b: {gate} has one 100k pull-down and is driven only through {series} from PYRO{n}_LS_SELECT (safe with both MCUs in reset)')
        fp = pfunc[next(k for k in nets[f'PYRO{n}_FIRE'] if k[0] == 'U201')][:2]
        sp = pfunc[next(k for k in nets[f'PYRO{n}_LS_SELECT'] if k[0] == 'U201')][:2]
        require(fp != sp, f'A2: channel {n} fire ({fp}) and low-side select ({sp}) on different ports')
        low = refs(f'OUTPUT{n}_LOW')
        require(low == {'J6601', sel, f'R69{n}3', f'R69{n}5', f'C660{2 * n}'} and actual[('J6601', str(n + 3))] == f'OUTPUT{n}_LOW', f'A3: OUTPUT{n}_LOW only on its low-side drain, continuity network, its RF bypass and J6601')
    require(refs('ENERGY_TAP') == {'Q101', 'U101', 'F6101', 'F6102', 'R7104', 'C1004', 'C1005'}, 'A4: ENERGY_TAP only Q101 drain, U101 IN, F6101 / F6102, its sense tap and decoupling')
    for f, j in (('F6101', 'J6101'), ('F6102', 'J6102')):
        require(refs(actual[(f, '2')]) == {f, j}, f'A5: {f} feeds only {j}')
    require(refs('RECOVERY_ARMED_VBAT') == {'J6101', 'R6310', 'R6410', 'R6101', 'R8007'}, 'A6: recovery armed rail only to channels 1 / 2, its arm sense and its ADC divider')
    require(refs('STAGING_ARMED_VBAT') == {'J6102', 'R6510', 'R6103'}, 'A6: staging armed rail only to channel 3 and its arm sense')
    require(refs(actual[('U6504', '3')]) == {'U6504', 'U6502', 'R6503'} and actual[('U6502', '1')] == 'PYRO3_FIRE'
            and actual[('U6502', '2')] == 'STAGE_ELIGIBLE', 'A7: U6504 IN only from U6502 (PYRO3_FIRE AND STAGE_ELIGIBLE)')
    require(actual[('U6001', '6')] == 'FLIGHT_NRST' and actual[('U6001', '2')] == 'STAGE_ARM_INVALID' and actual[('U6001', '1')] == 'NEW_FLIGHT_CLEAR_REQUEST'
            and actual[('U201', '88')] == 'NEW_FLIGHT_CLEAR_REQUEST' and pfunc[('U201', '88')].startswith('PD7')
            and 'R6001' in refs('NEW_FLIGHT_CLEAR_REQUEST') and value('R6001') == '100k',
            'A8: U6001 CLR = FLIGHT_NRST, D = STAGE_ARM_INVALID, CLK = PD7 with pull-down (PD15 until D-22Nov.25)')
    require(all(refs(f'OUTPUT{n}_HIGH') == {'J6601', f'U6{n + 2}04', f'R69{n}2', f'C660{2 * n - 1}'} and refs(f'PYRO{n}_ENERGY') == {f'U6{n + 2}04', f'R6{n + 2}10', f'C6{n + 2}04'}
                and actual[(f'R69{n}1', '1')] == '3V3_OPTIONAL' and refs(actual[(f'R69{n}1', '2')]) == {f'R69{n}1', f'R69{n}2'} for n in (1, 2, 3)),
            'A9: no logic rail on an armed rail; the only logic-rail path to J6601 is R69x1 / R69x2')
    for ref in ['R6310', 'R6410', 'R6510']:
        require(ref in dnp, f'A10: {ref} energy link DNP until the igniter values close')
    comms = {actual[(r, p)] for (r, p) in actual if r == 'U401'} - supplies
    require(not [n for n in reach(comms) if ENERGETIC.search(n)], 'A11: comms MCU has no path to any pyro, servo or arm net')
    starts = [n for n in nets if re.match(r'^(CAN|LORA|USB|CC_USB)', n)]
    require(not [n for n in reach(starts) if OUTPUT_ENABLES.match(n)], 'A12: CAN, radio and USB nets have no path to an output enable')
    require(refs('FC_POWER_HOLD') == {'U201', 'R1014', 'R1015'} and value('R1014') == '330R' and value('C1007').startswith('470u')
            and refs(actual[('R1014', '2')]) == {'R1014', 'C1007', 'D1003', 'D1004'} and actual[('D1003', '1')] == 'BAT_SHDN_N'
            and actual[('D1004', '1')] == 'CROI_POWER_HOLD' and refs('CROI_POWER_HOLD') == {'D1004', 'J102'},
            'A14: FC_POWER_HOLD reaches BAT_SHDN_N and J102.8 only through diodes, 330R / 470uF')
    for ref, rail in (('R3101', 'ST_3V3'), ('R3201', 'TDK_3V3'), ('R3301', 'HG_3V3'), ('R3401', 'BMP_3V3'), ('R3501', 'TE_3V3'), ('R3701', 'MAG_3V3')):
        want = '22R' if ref == 'R3701' else '47R 1%'
        require(value(ref) == want and actual[(ref, '1')] == 'FLIGHT_3V3' and actual[(ref, '2')] == rail, f'A15: {rail} fed through {ref} {want}')
    for net in ('BMP_SCL', 'BMP_SDA', 'TE_SCL', 'TE_SDA', 'MAG_SCL', 'MAG_SDA'):
        ups = [r for r in refs(net) if r.startswith('R') and ({actual[(r, '1')], actual[(r, '2')]} - {net}) & supplies]
        require(ups and all({actual[(r, '1')], actual[(r, '2')]} - {net} == {'FLIGHT_3V3'} for r in ups), f'A15: {net} pull-ups on FLIGHT_3V3')
    mag_mcu = {pfunc[k][:3] for n in ('MAG_SCL', 'MAG_SDA', 'MAG_INT') for k in nets[n] if k[0] == 'U201'}
    require(mag_mcu == {'PA8', 'PC9', 'PD3'} and refs('MAG_INT') == {'U201', 'U3701'}
            and all(refs(n) <= {'U201', 'R3702', 'R3703', 'R3704', 'R3705'} for n in ('MAG_SCL', 'MAG_SDA')),
            'A16: magnetometer nets land on PA8, PC9 and PD3 only (INT on PE6 until D-22Nov.25)')
    require(refs('USB_VBUS') == {'J4401', 'D4401', 'C4401', 'C4402', 'U4401', 'R1208'}, 'A18: USB VBUS only to its ESD, decoupling, U4401 and the R1208 divider')
    for ref in ('R1701', 'R1801', 'R1901'):
        bottom = next(r for r in refs(actual[(ref, '2')]) if r.startswith('R') and r != ref)
        require(value(ref) == '32k 0.1%' and value(bottom).startswith('10k'), f'A19: {ref} 32k over {bottom} 10k (D-21Nov.18)')
    require(actual[('U101', '11')] == 'GND', 'A19: U101 MODE tied to GND (auto-retry, D-6.3)')
    for n in (1, 2, 3):                                 # A23 (D-22Nov.20): a 1 nF C0G from each pyro output to GND at J6601
        for side, c in (('HIGH', f'C660{2 * n - 1}'), ('LOW', f'C660{2 * n}')):
            require(value(c) == '1n 50V C0G' and {actual[(c, '1')], actual[(c, '2')]} == {f'OUTPUT{n}_{side}', 'GND'},
                    f'A23: OUTPUT{n}_{side} has its 1 nF C0G RF bypass ({c}) to GND')
    require(refs('LORA_RF_SUBG') == {'J4601', 'U4606', 'D4601'} and actual[('D4601', '2')] == 'GND'
            and refs('GNSS_RF') == {'J4501', 'U4504', 'D4501'} and actual[('D4501', '2')] == 'GND',
            'A23: each antenna port has its ESD part to GND and nothing else on the line (D4501, D4601)')
    for j, r, f in (('J501', 'R516', 'F501'), ('J502', 'R517', 'F502')):
        ref_net = actual[(j, '3')]
        require(refs(ref_net) == {j, r} and refs(actual[(r, '2')]) == {r, f} and actual[(f, '2')] == 'GND', f'A22: {j} reference reaches GND only through {r} / {f}')

    chain = {}                                          # fire-chain net -> (pad, port) on U201
    for n in [f'PYRO{k}_{x}' for k in (1, 2, 3) for x in ('FIRE', 'LS_SELECT')] + ['NEW_FLIGHT_CLEAR_REQUEST', 'RECOVERY_ARM_SENSE',
                                                                              'STAGING_ARM_SENSE', 'STAGE_INHIBIT_LATCHED']:
        pad = next(k[1] for k in nets[n] if k[0] == 'U201')
        chain[n] = (int(pad), re.match(r'P[A-K]\d+', pfunc[('U201', pad)]).group(0))
    fire = [chain[f'PYRO{k}_FIRE'] for k in (1, 2, 3)]
    low = [chain[f'PYRO{k}_LS_SELECT'] for k in (1, 2, 3)]
    side = lambda pad: (pad - 1) // 25
    beside = lambda a, b: abs(a - b) == 1 and side(a) == side(b)
    require(all(p[1] == 'E' for _, p in fire) and all(p[1] != 'E' for _, p in low) and len({p[1] for _, p in low}) == 3,
            'A26: fire pins on port E; the three low-side selects on three other ports (03-energetic-outputs.md)')
    require(not [1 for a, _ in fire + low for b, _ in fire + low if beside(a, b)],
            'A26: no fire pin or low-side select beside another (one solder bridge never joins two inhibits, D-22Nov.25)')
    # the rest of D-22Nov.25's neighbour rule: nor beside an arm sense, the staging latch, the new-flight request or a
    # supply pad (VDD, VSS, VCAP, VBAT, VREF, VDDA, VDDUSB)
    supply = re.compile(r'^(VDD|VSS|VCAP|VBAT|VREF|VDDA|VSSA|VDDUSB)')
    held = {chain[n][0] for n in ('RECOVERY_ARM_SENSE', 'STAGING_ARM_SENSE', 'STAGE_INHIBIT_LATCHED', 'NEW_FLIGHT_CLEAR_REQUEST')}
    held |= {int(p) for (r, p), f in pfunc.items() if r == 'U201' and p.isdigit() and supply.match(f)}
    require(not [(a, b) for a, _ in fire + low for b in held if beside(a, b)],
            'A26: no fire pin or low-side select beside an arm sense, the staging latch, the new-flight request or a supply '
            'pad (D-22Nov.25)')
    require(not [n for n, (_, p) in chain.items() if p in FLIGHT_SPECIAL_PINS],
            'A26: fire, low-side, new-flight, arm-sense and latch pins carry no trace, debug-trigger, tamper, RTC_OUT or LSCO '
            'output (D-22Nov.25)')
    a24, a25 = reset_pin_faults(root)
    require(not a24, 'A24: no pulled-down net (an output off by default) on a debug pin pulled up from reset (PA13, PA15, PB4) '
                     'or a pin the ROM bootloader drives (D-22Nov.25)')
    require(not a25, 'A25: no fire, low-side, arm-sense or staging-latch net on a pin the ROM bootloader drives or reads (D-22Nov.25)')

    # ---- test points (D-22Nov.9)
    field = lambda ref, k: parts[ref].findtext(f"fields/field[@name='{k}']")
    require(all(len([k for k in actual if k[0] == r]) == 1 for r in tps), 'TP1: every test point is a single pin')
    require(not [n for n in tps.values() if OUTPUT_ENABLES.match(n) or (ENERGETIC.search(n) and n not in TP_SENSE_ONLY)],
            'TP2: no test point on a fire net or a fire-switch driver; only the scaled sense nodes')
    tier = lambda n: TP_GND if n == 'GND' else TP_LOOP if n in TP_LOOP_NETS else TP_PAD
    require(all((parts[r].findtext('footprint'), field(r, 'MPN'), field(r, 'LCSC')) == tier(n) for r, n in tps.items()),
            'TP3: GND test points are black 5011 loops, rails / strobe / PPS yellow surface-mount 5194TR loops, the rest 1.0 mm pads')
    require(not [n for n in set(tps.values()) if n in supplies and n != 'GND' and n not in TP_LOOP_NETS],
            'TP4: every rail with a test point has a loop')
    require(sum(n == 'GND' for n in tps.values()) == 4 and len(set(tps.values())) == len(tps) - 3,
            'TP5: four GND loops; one test point per other net')

    # ---- population
    for n in (1, 2, 3):
        require(value(f'R6{n + 2}14') == '1.24k 1%' and f'R6{n + 2}14' not in dnp, f'Channel {n} current limit fitted (about 2.0 A)')
    require(all(f'R69{i}{j}' not in dnp and value(f'R69{i}{j}') == '3.9k 1%' for i in (1, 2, 3) for j in (1, 2, 3, 4)), 'Continuity resistors 3.9k fitted (D-2Nov.14)')
    missing = sorted(r for r, c in parts.items() if not c.findtext('footprint'))
    require(missing == [], 'Every part has a footprint (J101 since capture step 15)')
    fp = lambda ref: parts[ref].findtext('footprint')
    require(fp('J101') == 'Ogma2:105311-1102', 'J101 is Nano-Fit 105311-1102, from Molex drawing SD-105311-100 (step 15)')
    families = {r: fp(r).split(':')[1].split('_')[1] for r in ('J6101', 'J6102', 'J103')}
    require(fp('J6101').startswith('Connector_Molex:Molex_Mini-Fit_Jr') and fp('J6102').startswith('Connector_JST:JST_VH')
            and len(set(families.values())) == 3 and not {'Micro-Fit', 'Nano-Fit', 'GH', 'Gecko'} & {families['J6101'], families['J6102']},
            'A13: J6101 (Mini-Fit Jr.) and J6102 (JST VH): different families, neither Micro-Fit (J701), Nano-Fit (J101), GH or Gecko')
    require(fp('J103') == 'Connector_Molex:Molex_Micro-Fit_3.0_43650-0215_1x02_P3.00mm_Vertical' and value('J103') == '43650-0215',
            'A13b: J103 is a single-row Micro-Fit 3.0 header (43650), which mates 43645 / 171850 only, not the dual-row '
            '43025 plug of Churro J701 (D-22Nov.18)')

    # ---- negative tests exercise the checker, not a modified live schematic
    bad = copy.deepcopy(root)
    h = next(net for net in bad.findall('nets/net') if net.get('name') == 'CAN_H')
    next(n for n in h.findall('node') if n.get('ref') == 'J501').set('pin', '2')
    try:
        verify(bad, expected)
    except AssertionError:
        checks.append('Negative test: swapped CAN contact rejected')
    else:
        raise AssertionError('Checker accepted corrupted connector map')
    bad = copy.deepcopy(root)
    for net in bad.findall('nets/net'):
        if net.get('name') == 'FLIGHT_VDDA':
            net.set('name', 'FLIGHT_3V3')
    try:
        verify(bad, expected)
    except AssertionError:
        checks.append('Negative test: analog-supply bypass short rejected')
    else:
        raise AssertionError('Checker accepted shorted VDDA')

    report = json.loads(erc.read_text())
    violations = [v for s in report['sheets'] for v in s['violations']]
    categories = Counter(('excluded / ' if v.get('excluded') else '') + v['severity'] + ' / ' + v['type'] for v in violations)
    require(not [v for v in violations if not v.get('excluded')], 'ERC: no unexcluded finding')
    return {'status': 'connectivity checks pass; engineering draft, not release',
            'physical_component_count': len(parts), 'checked_pin_count': pincount, 'architecture_checks': len(checks),
            'dnp_count': len(dnp), 'dnp_refs': dnp, 'missing_footprints': missing,
            'not_checkable_here': {'A17': 'KiCad 9 schematic has no BOM variants; J101 / J102 exclusivity is an assembly rule',
                                   'A20': 'Churro', 'A21': 'Churro'},
            'erc_categories': dict(categories), 'checks': checks,
            'netlist_sha256': hashlib.sha256(netlist.read_bytes()).hexdigest(),
            'schematic_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(project.glob('*.kicad_sch'))},
            'limits': 'No analog simulation, target test, layout/rating/thermal/inrush/ESD qualification or energetic release.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('project', type=Path)
    p.add_argument('netlist', type=Path)
    p.add_argument('erc', type=Path)
    p.add_argument('--output', type=Path)
    p.add_argument('--write-expected', action='store_true', help='regenerate full-expected-pins.json from this netlist first')
    a = p.parse_args()
    if a.write_expected:
        (a.project / 'full-expected-pins.json').write_text(json.dumps(expected_from(ET.parse(a.netlist).getroot()), indent=1, sort_keys=True) + '\n')
    result = check(a.project, a.netlist, a.erc)
    if a.output:
        a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['checks', 'schematic_sha256', 'dnp_refs']}))
