"""Read-only count/group audit against an exported KiCad XML netlist.

Run from any directory with: python3 tools/audit_mcu_pins.py NETLIST.xml
Does not prove alternate-function, DMA, timing or electrical correctness.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def group(role, row):
    port, net, fn = (row[k] for k in ('port_or_supply', 'net', 'function'))
    if not re.fullmatch(r'P[A-H]\d+', port):
        return 'Supply/reference/core caps/reset/boot'
    if net == 'NC_LSE_QUIET':
        return 'Quiet reserve'
    if net == 'NC':
        return 'Unused'
    if fn in ('HSE', 'LSE'):
        return 'Clocks' if role == 'flight' or fn == 'HSE' else 'Unfitted LSE reservation'
    if fn in ('SWD', 'TRACESWO'):
        return 'Debug'
    if role == 'comms' and net in ('LORA_RXEN', 'LORA_TXEN'):
        return 'Legacy radio reservations'
    if role == 'flight':
        if net.startswith(('ST_', 'TDK_', 'HG_', 'BMP_', 'TE_')):
            return 'Sensors'
        if net.startswith('NOR_'):
            return 'Recording'
        if net.startswith(('PYRO', 'RECOVERY_', 'STAGING_', 'STAGE_', 'NEW_FLIGHT_')):
            return 'Energetic control and diagnostics'
        if net.startswith('SERVO'):
            return 'Servo control and diagnostics'
        if net.startswith('CAN_'):
            return 'CAN'
        if net.startswith('CHURRO_'):
            return 'Auxiliary monitoring'
        if net in ('FLIGHT_TO_COMMS', 'COMMS_TO_FLIGHT', 'COMMS_EN', 'COMMS_RESET_REQUEST'):
            return 'Comms link and control'
        if net in ('VEHICLE_VBAT', 'FLIGHT_3V3'):
            return 'Battery and logic voltage'
        if net in ('SUPERVISOR_WDI', 'BRANCH_FAULT_N', 'BUZZER_DRIVE', 'STATUS_LED1'):
            return 'Health and indication'
    else:
        if net.startswith('LORA_'):
            return 'Radio'
        if net.startswith('GNSS_'):
            return 'GNSS'
        if net.startswith('USB_') or net == 'BAT_VALID':
            return 'USB and source status'
        if net in ('FLIGHT_TO_COMMS', 'COMMS_TO_FLIGHT'):
            return 'Flight link'
        if net in ('STATUS_LED', 'BRANCH_FAULT_N'):
            return 'Health and indication'
    raise ValueError(('Ungrouped allocation', role, row))


def audit(netlist):
    tree = ET.parse(netlist)
    actual = {}
    for net in tree.findall('nets/net'):
        for node in net.findall('node'):
            key = (node.get('ref'), node.get('pin'))
            assert key not in actual, ('Duplicate netlist pad', key)
            actual[key] = net.get('name').rsplit('/', 1)[-1]
    result = {}
    for role, ref in [('flight', 'U201'), ('comms', 'U401')]:
        with (ROOT / f'hardware/croi2/libraries/inputs/{role}-pinout.csv').open() as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 100
        assert {r['pad'] for r in rows} == {str(i) for i in range(1, 101)}
        groups = defaultdict(list)
        for row in rows:
            pin, net, fn = row['pad'], row['net'], row['function']
            found = actual.get((ref, pin), '')
            if net.startswith('NC') or (role == 'comms' and fn == 'LSE'):
                assert found.startswith('unconnected-'), (ref, pin, found)
            else:
                # CSV logical names -> existing schematic boundary names.
                if fn.startswith('ADC'):
                    net = 'ADC_' + net
                elif net in ('HSE_IN','HSE_OUT','LSE_IN','LSE_OUT','SWDIO','SWCLK','STATUS_LED','STATUS_LED1','STATUS_LED2'):
                    net = role.upper() + '_' + net
                elif role == 'comms' and net in ('FLIGHT_TO_COMMS','COMMS_TO_FLIGHT','BRANCH_FAULT_N','BAT_VALID','USB_CONFIG_OK'):
                    net = 'CC_' + net
                elif role == 'flight' and net == 'COMMS_EN':
                    net = 'FLIGHT_COMMS_EN'
                if pin in ('21', '22'):
                    net = role.upper() + '_VDDA'
                assert found == net, (ref, pin, net, found)
            groups[group(role, row)].append(row['port_or_supply'])
        assert sum(map(len, groups.values())) == 100
        result[role] = {'counts': dict(Counter({k: len(v) for k, v in groups.items()})), 'ports': dict(groups)}
    return result


if __name__ == '__main__':
    print(json.dumps(audit(sys.argv[1]), indent=2))
