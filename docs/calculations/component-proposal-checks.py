#!/usr/bin/env python3
"""22 Sep 2026 desk checks. Calculations and netlist facts, not hardware tests."""
import csv
import binascii
import itertools
import json
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
netlist = ET.parse(ROOT / 'hardware/croi2/output/full-netlist.xml').getroot()
pins = {}
native_ports = {}
for net in netlist.findall('./nets/net'):
    for node in net.findall('node'):
        pins[node.get('ref'), node.get('pin')] = net.get('name')
        port = node.get('pinfunction', '')
        gpio = re.match(r'^(P[A-Z]\d+)', port)
        if gpio:
            port = gpio.group(1)  # PA13(JTMS/SWDIO), for example
        native_ports.setdefault((node.get('ref'), port), set()).add(net.get('name'))


def electrical_name(name):
    """NC denotes an individual unconnected pad, never a shared electrical net."""
    return 'NC' if name.startswith('unconnected-') else name

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
assert by_port['PC10']['net'] == pins['U4301', '1'] == 'CC_COMMS_TO_FLIGHT'
assert by_port['PC11']['net'] == pins['U4301', '8'] == 'CC_FLIGHT_TO_COMMS'
# Compare every proposed connection to native electrical nodes, not shorthand
# hardware-input CSV names. UART ports migrate; analog supply pads combine.
for row in comms:
    old_port = {'PC10': 'PD8', 'PC11': 'PD9', 'VDDA/VREF+': 'VDDA'}.get(
        row['port_or_supply'], row['port_or_supply'])
    expected = {electrical_name(n) for n in native_ports['U401', old_port]}
    assert expected == {row['net']}, (row['pad'], old_port, expected, row['net'])
assert native_ports['U401', 'VDDA'] == native_ports['U401', 'VREF+']
assert pins['U401', '19'] == pins['U401', '20'] == 'GND'
assert by_port['PA1']['net'] == pins['U4303', '10'] == 'CC_USB_CONFIG_OK'
assert by_port['PA2']['net'] == pins['U4303', '13'] == 'CC_BAT_VALID'
assert by_port['PB5']['net'] == 'CC_BRANCH_FAULT_N'
# Native connectivity checks supplement, not replace, ST package/AF review.

# Only PD10 changes function. Other corrected names preserve native wiring.
with (ROOT / 'docs/architecture/proposed-flight-pinout.csv').open() as f:
    flight = list(csv.DictReader(f))
with (ROOT / 'hardware/croi2/libraries/inputs/flight-pinout.csv').open() as f:
    native_flight = list(csv.DictReader(f))
assert len(flight) == 100
assert {int(row['pad']) for row in flight} == set(range(1, 101))
native_by_pad = {row['pad']: row for row in native_flight}
functional_fields = ('role', 'mpn', 'port_or_supply', 'function', 'alternate_function')
changed_pads = [row['pad'] for row in flight if any(
    row[key] != native_by_pad[row['pad']][key] for key in functional_fields)]
assert changed_pads == ['57']
for row in flight:
    expected = ('SERVICE_POWER_EN' if row['pad'] == '57' else
                electrical_name(pins['U201', row['pad']]))
    assert row['net'] == expected, (row['pad'], expected, row['net'])
assert flight[56]['port_or_supply'] == 'PD10'
assert flight[56]['net'] == 'SERVICE_POWER_EN'
assert flight[56]['function'] == 'GPIO'

# Confirm retained placement of limiters/LDOs and exact native divider values.
components = {c.get('ref'): c for c in netlist.findall('./components/comp')}
for ref in ('R1701', 'R1801', 'R1901'):
    assert components[ref].findtext('value') == '31.2k 0.1%'
assert pins['U1601', '3'] == 'FLIGHT_3V3'  # proposed EN rewiring is not installed

rate = 96672
comms_rate = 1024
capacity = 256 * 1024**2
reserve = 64 * 1024**2
existing_mission = 180587776
added = comms_rate * 1800 + (rate + comms_rate) * 10

# TI TPS2553 equation 1, including 1% external resistor tolerance.
def current_limit_ma(resistor_kohm):
    return (25230 / (resistor_kohm * 1.01)**1.016,
            22980 / (resistor_kohm * 0.99)**0.94)

limits = {name: current_limit_ma(r) for name, r in {
    'services_U1601_R1604_49k9': 49.9, 'comms_U1501_R1504_66k5': 66.5,
    'usb_retained_60k4': 60.4, 'nor_retained_100k': 100,
    'can_aux_retained_210k': 210}.items()}
service_min_ma, service_max_ma = limits['services_U1601_R1604_49k9']
comms_max_ma = limits['comms_U1501_R1504_66k5'][1]
assert abs(service_min_ma - 470.17) < .01
assert abs(comms_max_ma - 448.746) < .01
assert pins['U4402', '1'] == 'USB_VBUS'
assert pins['U4402', '2'] == 'USB_ILIM'
assert pins['U4402', '4'] == 'USB_CONFIG_OK'
for ref in ('U3101', 'U3201', 'U3301', 'U3401', 'U3501'):
    assert pins[ref, '5'] == pins[ref, '1'] == 'FLIGHT_3V3'

# TPS7A91 reference/accuracy, resistor ratio, feedback leakage. Input switches
# precede LDOs: their drop is an input-headroom check, not an output subtraction.
def ldo_corners(top_kohm, bottom_kohm=10):
    low = .8 * .99 * (1 + top_kohm * .999 / (bottom_kohm * 1.001))
    high = .8 * 1.01 * (1 + top_kohm * 1.001 / (bottom_kohm * .999))
    feedback_error = 100e-9 * top_kohm * 1000 * 1.001
    return low - feedback_error, high + feedback_error

low, high = ldo_corners(31.9)
reset_release_upper_v = 3.07 * 1.015 * 1.025
assert high < 3.6
assert low - .050 > reset_release_upper_v
voltage = dict(nominal_v=.8*(1+31.9/10), low_v=low, high_v=high,
    static_release_margin_v=low-reset_release_upper_v,
    margin_after_50mv_allocation_v=low-.050-reset_release_upper_v)

# Sector-aligned commit, 15 data pages plus footer; conservatively charge footer
# overhead again even though the original 20% ledger already included framing.
data_bytes = 15 * 256
sector_bytes = 16 * 256
conservative_storage = math.ceil((existing_mission + added) / data_bytes) * sector_bytes
assert conservative_storage == 195637248
assert conservative_storage + reserve < capacity
assert binascii.crc32(b'123456789') == 0xCBF43926
throughput_target = 125000
assert throughput_target > rate + comms_rate
assert throughput_target < data_bytes / (16 * .0015)

# Replace the affected healthy branch allocation when considering one fault.
service_faults = {
    'NOR': limits['nor_retained_100k'][1] + 200 - 65,
    'CAN': limits['can_aux_retained_210k'][1] + 200 - 80,
    'AUX': limits['can_aux_retained_210k'][1] + 200 - 25,
}
assert all(current < service_min_ma for current in service_faults.values())

# Churro probe nominal transfer; published Vishay resistance table, not beta fit.
probe_points = {-20: 96761, 25: 10000, 70: 1747.7}
probe_volts = {t: 2.5*(r+2200+12)/(10000+r+2200+12)
               for t, r in probe_points.items()}
assert all(.55 < v < 2.40 for v in probe_volts.values())
short_volts = 2.5*(2200+12)/(10000+2200+12)
assert short_volts < .55
assert 2.5 > 2.40  # ideal open; real diagnostic behavior requires fault tests
for t, v in probe_volts.items():
    assert abs(10000*v/(2.5-v)-2200-12-probe_points[t]) < 1e-6
churro = ET.parse(ROOT / 'hardware/foinse2/output/full-netlist.xml').getroot()
churro_refs = {c.get('ref') for c in churro.findall('./components/comp')}
new_refs = {'U6201','U6202','C6201','C6202','C6203','R6201','R6202',
            'R6211','R6212','D6201','D6202','TP6201'}
assert not (new_refs & churro_refs)

active_w = 4 * .700
endurance_wh = 8*(active_w/.85+.10) + 4*(.4/.75+.10)
assert endurance_wh < 30
reference_usable_wh = 7.4 * 8 * .65
assert reference_usable_wh > endurance_wh
servo_nominal_a = 1.233 * 2000 / 1240
print(json.dumps({
    'scope': 'Proposed capture arithmetic and native baseline checks; not measurements',
    'maps': '64 comms and 100 flight pads checked against native electrical nodes; only flight PD10 changes function',
    'source_mux_truth_table': source_states,
    'current_limit_bounds_ma_including_resistor_tolerance': limits,
    'three_ldo_voltage_corners': voltage,
    'supervisor_release_upper_v_conservative': reset_release_upper_v,
    'service_fault_plus_remaining_healthy_load_ma': service_faults,
    'common_buck_simultaneous_limited_fault_allocation_ma': service_max_ma + comms_max_ma + 200,
    'writer_seconds_including_comms': 128 * 1024 / (rate + comms_rate),
    'revised_mission_ledger_bytes': existing_mission + added,
    'conservative_storage_bytes': conservative_storage,
    'spare_beyond_64MiB_reserve_bytes': capacity - reserve - conservative_storage,
    'record_expansion_after_footer_within_20pct_allowance': 1.2 * 15 / 16 - 1,
    'program_only_useful_bytes_per_second': data_bytes / (16*.0015),
    'required_measured_useful_bytes_per_second': throughput_target,
    'prepare_192MiB_at_2sec_per_64KiB_minutes': (capacity-reserve)/65536*2/60,
    'ideal_full_flash_download_minutes_at_2Mbaud_8N1': capacity / 200000 / 60,
    'probe_nominal_volts_by_temperature_C': probe_volts,
    'probe_ideal_short_voltage': short_volts,
    'servo_nominal_limit_a': servo_nominal_a,
    'servo_overload_limit_bounds_a_including_1pct_resistor': [servo_nominal_a*.86/1.01, servo_nominal_a*1.14/.99],
    'nominal_ldo_loss_w_before_series_drops': (4-3.352)*.700,
    'logic_endurance_wh_assumptions_in_rationale': endurance_wh,
    'reference_8Ah_usable_wh_at_assumed_65pct': reference_usable_wh,
    'full_allocation_USB_current_ma_at_4V35_85pct_before_overhead': active_w/(4.35*.85)*1000,
}, indent=2))
