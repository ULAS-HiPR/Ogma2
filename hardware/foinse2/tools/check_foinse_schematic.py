"""Native connectivity plus independent boundary assertions; no analog qualification."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from check_schematic_full import verify


def check(project, netlist, erc):
    root = ET.parse(netlist).getroot()
    expected = json.loads((project/'full-expected-pins.json').read_text())
    actual, count = verify(root, expected)
    parts = {c.get('ref'): c for c in root.findall('components/comp')}
    checks = []
    def require(test, text):
        assert test, text
        checks.append(text)
    def pin(ref, number, net):
        require(actual.get((ref, str(number))) == net, f'{ref}.{number} = {net}')
    require(set(parts) == {r for r in expected if not r.startswith('#')}, 'Every physical component covered')
    require(not any('STM32' in c.findtext('value', '') for c in parts.values()), 'No MCU populated')
    require(not any('CAN' in v for v in actual.values()), 'No CAN endpoint or conductor')
    require(not any('24V' in v for v in actual.values()), 'No invented regulated 24 V rail')
    for index, tag, out in [(1, 'AV', 'VBAT_CROI'), (2, 'PROP', 'PROP_RAW')]:
        pre = index*10
        efuse, mosfet = f'U{pre}01', f'Q{pre}01'
        for number, net in {1:tag+'_REV_BLOCKED', 2:tag+'_REV_BLOCKED', 3:tag+'_BLOCK_GATE',
            4:tag+'_BLOCK_DRV', 5:tag+'_PACK', 8:'GND', 12:tag+'_SHDN_N',
            14:'FOINSE_FAULT_N', 17:out if index==1 else tag+'_PROTECTED', 18:out if index==1 else tag+'_PROTECTED', 25:'GND'}.items():
            pin(efuse, number, net)
        require(actual.get((efuse, '11'), 'unconnected-').startswith('unconnected-'), f'{efuse} MODE open: latch-off')
        for number in [1, 2, 3]: pin(mosfet, number, tag+'_PACK')
        pin(mosfet, 4, tag+'_BLOCK_GATE'); pin(mosfet, 5, tag+'_REV_BLOCKED')
        pin(f'R{pre}06', 1, tag+'_SHDN_N'); pin(f'R{pre}06', 2, 'GND')
        require(parts[f'R{pre}06'].findtext('value')=='22.1k 1%',f'{tag} SHDN has a local off-default pull-down')
        enable = {r for (r, p), net in actual.items() if net == tag+'_SHDN_N'}
        connector='J103' if index==1 else 'J104'
        require(enable == {efuse, f'R{pre}06',f'C{pre}06',connector}, f'{tag} external master has no MCU or AUX dependency')
        for ref,pins in {f'D{pre}02':{1:tag+'_PACK',3:tag+'_SW_DIODE'},
                         f'R{pre}12':{1:tag+'_SW_DIODE',2:tag+'_SW_RMID'},
                         f'R{pre}13':{1:tag+'_SW_RMID',2:tag+'_SWITCH_3V'},
                         f'U{pre}02':{1:tag+'_SWITCH_3V',2:'GND'},
                         connector:{1:tag+'_SWITCH_3V',2:tag+'_SHDN_N'},
                         f'C{pre}06':{1:tag+'_SHDN_N',2:'GND'}}.items():
            for number,net in pins.items():pin(ref,number,net)
        if index==2:
            pin(f'R{pre}11', 1, tag+'_PROTECTED'); pin(f'R{pre}11', 2, out)
        else:
            require('R1011' not in parts and 'U4001' not in parts,'No duplicate AV shunt or current monitor on Foinse')
        pin(f'D{pre}01', 1, tag+'_PACK'); pin(f'D{pre}01', 2, 'GND')
        require(parts[f'D{pre}01'].find('libsource').get('part') == 'D_Zener', 'Unidirectional TVS symbol: cathode pin 1')
        if index==1:continue
        mon = f'U{30+index*10}01'
        for number, net in {1:'GND', 2:'GND' if index==1 else 'FOINSE_AUX_3V3', 3:'FOINSE_FAULT_N',
            4:'MON_SDA', 5:'MON_SCL', 6:tag+'_MON_3V3', 7:'GND', 8:tag+'_VBUS_FILTER',
            9:tag+'_IN_MINUS', 10:tag+'_IN_PLUS'}.items(): pin(mon, number, net)
    for number, net in {1:'VBAT_CROI',2:'GND',3:'FOINSE_AUX_3V3',4:'GND',5:'FOINSE_SCL',
                       6:'FOINSE_SDA',7:'FOINSE_FAULT_N'}.items(): pin('J301', number, net)
    require(actual.get(('J301','8'),'unconnected-').startswith('unconnected-'), 'Spare mate contact not energised')
    for number, net in {1:'GND',2:'ADC_READY',3:'GND',4:'AV_NTC_ADC',5:'PROP_NTC_ADC',
                       6:'AV_V_ADC',7:'PROP_V_ADC',8:'ADC_3V3',9:'MON_SDA',10:'MON_SCL'}.items(): pin('U6001',number,net)
    pin('J101',1,'AV_PACK'); pin('J101',2,'GND')
    pin('J201',1,'PROP_PACK'); pin('J201',3,'GND')
    pin('J701',1,'PROP_RAW'); pin('J701',2,'GND')
    for voltage, top in [(9,22.1),(27,110)]:
        require(voltage*10/(top+10)<3.3, 'One shorted divider top resistor remains below 3.3 V at nominal OV boundary')
    bad = copy.deepcopy(root)
    for net in bad.findall('nets/net'):
        if net.get('name') == 'PROP_RAW': net.set('name','VBAT_CROI')
    try: verify(bad, expected)
    except AssertionError: checks.append('Negative test rejects merged battery-positive branches')
    else: raise AssertionError('Checker accepted a merged 6S/2S positive rail')
    violations = [v for s in json.loads(erc.read_text())['sheets'] for v in s['violations']]
    require(not violations, 'Native ERC has no violations or exclusions')
    return {'status':'engineering draft; connectivity passes, not hardware qualification',
        'physical_component_count':len(parts), 'checked_pin_count':count, 'architecture_checks':len(checks),
        'erc_violations':len(violations), 'checks':checks,
        'missing_footprints':[r for r,c in parts.items() if not c.findtext('footprint')],
        'netlist_sha256':hashlib.sha256(netlist.read_bytes()).hexdigest()}


if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('project',type=Path); p.add_argument('netlist',type=Path)
    p.add_argument('erc',type=Path); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    result=check(a.project,a.netlist,a.erc)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
