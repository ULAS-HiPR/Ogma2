#!/usr/bin/env python3
"""19 Sep 2026 desk checks. Calculations and netlist facts, not hardware tests."""
import csv
import itertools
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
netlist = ET.parse(ROOT / 'hardware/croi2/output/full-netlist.xml').getroot()
pins = {}
for net in netlist.findall('./nets/net'):
    for node in net.findall('node'):
        pins[node.get('ref'), node.get('pin')] = net.get('name')

# TI SN74LVC1G97 Table 1: In2 selects In0 (high) or In1 (low).
assert [pins['U1202', str(n)] for n in (6, 3, 1, 4)] == [
    'BAT_VALID', 'FLIGHT_COMMS_EN', 'USB_PRESENT', 'COMMS_BRANCH_EN']
assert [pins['U1203', str(n)] for n in (6, 3, 1, 4)] == [
    'USB_CONFIG_OK', 'BOOT_3V3', 'BAT_VALID', 'CORE_INPUT_EN']
source_states = []
for battery, usb, flight_enable in itertools.product((0, 1), repeat=3):
    source_states.append(dict(battery_valid=battery, usb_present=usb,
        flight_comms_enable=flight_enable,
        comms_enable=flight_enable if battery else usb))

with (ROOT / 'docs/architecture/proposed-comms-pinout.csv').open() as f:
    comms = list(csv.DictReader(f))
assert len(comms) == 64
assert {int(row['pad']) for row in comms} == set(range(1, 65))
ports = [row['port_or_supply'] for row in comms if row['port_or_supply'].startswith('P')]
assert len(ports) == len(set(ports))
by_port = {row['port_or_supply']: row for row in comms}
assert by_port['PC10']['net'] == 'COMMS_TO_FLIGHT'
assert by_port['PC11']['net'] == 'FLIGHT_TO_COMMS'
# CSV structure and direction checks supplement, not replace, ST package/AF review.

rate = 96672
comms_rate = 1024
capacity = 256 * 1024**2
reserve = 64 * 1024**2
existing_mission = 180587776
added = comms_rate * 1800 + (rate + comms_rate) * 10
# TI TPS2553 Table 2 values already include 1% ILIM resistor tolerance.
service_min_ma, service_max_ma = 729.1, 882.1
comms_max_ma, other_service_ma = 448.7, 100
print(json.dumps({
    'comms_map': '64 unique pads; active UART directions checked',
    'source_mux_truth_table': source_states,
    'flight_writer_seconds': 128 * 1024 / rate,
    'new_storage_allowance_bytes': added,
    'remaining_storage_bytes': capacity - reserve - existing_mission - added,
    'ideal_full_flash_download_minutes_at_2Mbaud_8N1': capacity / (2000000 / 10) / 60,
    'static_comms_fault_plus_other_service_ma': comms_max_ma + other_service_ma,
    'static_aggregate_margin_ma_before_quiescent_and_inrush': service_min_ma - comms_max_ma - other_service_ma,
    'aggregate_fault_power_w_at_4V': 4 * service_max_ma / 1000,
    'comms_switch_drop_v_at_limit': comms_max_ma / 1000 * 0.135,
    'comms_dc_floor_v_before_trace_and_transients': 3.3 * 0.99 - comms_max_ma / 1000 * 0.135,
    'flight_holdup_ms_illustrative': 800e-6 * 0.25 / 0.204 * 1000,
    'capacitor_esr_step_v_illustrative': 0.204 * 0.014,
    'nominal_total_ldo_loss_w': (4 - 3.3) * 0.6,
}, indent=2))
