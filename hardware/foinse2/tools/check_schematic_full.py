"""Verify native exported connectivity, frozen MCU allocations and safety defaults.

Generated expectations check serialization/geometry. Separate fixed assertions
check architectural boundaries. Neither is an analog simulation or qualification.
"""
import argparse
import copy
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

HW=Path(__file__).resolve().parents[1]


def node_map(root):
    out={}
    for net in root.findall('nets/net'):
        for pin in net.findall('node'):
            key=(pin.get('ref'),pin.get('pin'))
            assert key not in out,('duplicate pin',key)
            out[key]=net.get('name').rsplit('/',1)[-1]
    return out


def verify(root,expected):
    actual=node_map(root);count=0
    for ref,pins in expected.items():
        if ref.startswith('#'):continue  # Power symbols are absent from netlist BOM.
        for pin,net in pins.items():
            found=actual.get((ref,pin))
            if net is None:
                assert found is None or found.startswith('unconnected-'),(ref,pin,'NC',found)
            else:
                assert found==net,(ref,pin,net,found)
            count+=1
    assert set(actual).issubset({(r,p) for r,ps in expected.items() for p in ps}), 'Unexpected pins'
    return actual,count


def check(project,netlist,erc):
    root=ET.parse(netlist).getroot()
    expected=json.loads((project/'full-expected-pins.json').read_text())
    actual,pincount=verify(root,expected)
    checks=[]
    def require(condition,description):
        assert condition,description
        checks.append(description)
    for role,ref in [('flight','U201'),('comms','U401')]:
        tag=role.upper();rows=list(csv.DictReader((HW/f'libraries/inputs/{role}-pinout.csv').open()))
        require(len(rows)==100,f'{role}: 100 frozen allocation rows')
        for row in rows:
            pin=row['pad'];net=row['net'];fn=row['function']
            if net.startswith('NC') or (role=='comms' and fn=='LSE'):
                require(actual.get((ref,pin),'unconnected-').startswith('unconnected-'),f'{ref}.{pin} intentionally unused')
                continue
            if fn.startswith('ADC'):net='ADC_'+net
            elif net in ['HSE_IN','HSE_OUT','LSE_IN','LSE_OUT','SWDIO','SWCLK','STATUS_LED','STATUS_LED1','STATUS_LED2']:
                net=tag+'_'+net
            elif role=='comms' and net in ['FLIGHT_TO_COMMS','COMMS_TO_FLIGHT','BRANCH_FAULT_N','BAT_VALID','USB_CONFIG_OK']:
                net='CC_'+net
            elif role=='flight' and net=='COMMS_EN':net='FLIGHT_COMMS_EN'
            if pin in ['21','22']:net=tag+'_VDDA'
            require(actual[(ref,pin)]==net,f'{ref}.{pin}: frozen allocation with documented physical-net mapping')
    parts={c.get('ref'):c for c in root.findall('components/comp')}
    require(set(parts)=={ref for ref in expected if not ref.startswith('#')},'Every native component covered')
    for ref,mpn in [('U201','STM32H563VIT6'),('U401','STM32H563VIT6'),
                    ('U3604','MX66L2G45GMI00'),('U4504','SAM-M10Q-00B'),('U4606','E22-900M22S')]:
        require(parts[ref].findtext('value')==mpn,f'{ref}: accepted exact device')
    require(actual[('U201','22')]!=actual[('U201','11')],'Flight VDDA link is not bypassed by a drawing short')
    require(actual[('U401','22')]!=actual[('U401','11')],'Comms VDDA link is not bypassed by a drawing short')
    for pin in ['48','98']:
        require(actual[('U201',pin)]=='FLIGHT_VCAP',f'Flight VCAP pad {pin} is not a 3.3 V supply')
    require(actual[('U201','6')]=='FLIGHT_3V3','Backup pin is held flight 3.3 V, not vehicle battery')
    require(actual[('U4504','8')].startswith('unconnected-'),'GNSS SAFEBOOT_N intentionally unloaded')
    require(actual[('U4606','12')]=='GND' and actual[('U4606','15')]=='LORA_RESET_N_ISO','E22 dated-manual pin correction retained')
    require(actual[('U4606','21')].startswith('unconnected-'),'No host-board ANT stub in IPX population')
    require(actual[('U101','11')].startswith('unconnected-'),'TPS26630 MODE open selects latch-off, not retry')
    for pin,net in {'1':'VBAT_CROI_INPUT','2':'GND','3':'FOINSE_AUX_3V3','4':'GND',
                    '5':'FOINSE_SCL_EXT','6':'FOINSE_SDA_EXT','7':'FOINSE_FAULT_N_EXT'}.items():
        require(actual[('J102',pin)]==net,f'Samtec contact {pin} / {net}')
    for net,pin in [('CAN_H','1'),('CAN_L','2')]:
        required={('J501',pin),('D501',pin),('R510',pin),('U503','7' if pin=='1' else '6')}
        require({n for n,v in actual.items() if v==net}==required,f'Exact {net} conductors; no H/L short')
    require(actual[('U502','1')]!=actual[('U502','14')],'CAN translator supply domains remain separate')
    require(actual[('U503','3')]==actual[('U503','5')]=='CAN_3V3','CAN VCC and VIO both follow switched rail')
    require(actual[('U1401','1')]=='CORE_INPUT_EN' and actual[('U1701','7')]=='CORE_HELD_4V',
            'Core gate precedes hold-up; LDO enable stays on held input')
    # Evaluate the actual two source-policy gates from their exported pin nets.
    def gate_value(ref,states):
        return states[actual[(ref,'3')]] if states[actual[(ref,'6')]] else states[actual[(ref,'1')]]
    for bat in [0,1]:
        for usb in [0,1]:
            for config in [0,1]:
                for flight in [0,1]:
                    states={'GND':0,'BOOT_3V3':1,'BAT_VALID':bat,'USB_PRESENT':usb,
                            'USB_CONFIG_OK':config,'FLIGHT_COMMS_EN':flight}
                    require(gate_value('U1203',states)==(bat or config),'Core source-permission truth-table row')
                    require(gate_value('U1202',states)==(flight if bat else usb),'Comms source-permission truth-table row')
    require(actual[('U6001','1')]=='NEW_FLIGHT_CLEAR_REQUEST','Staging request clocks latch directly')
    require(actual[('U6001','2')]=='STAGE_NEW_FLIGHT_ALLOWED','Physical disarm qualifies D, never CLK')
    require(actual[('U6001','6')]=='FLIGHT_NRST','Reset clears staging eligibility asynchronously')
    require(actual[('U6001','3')]=='STAGE_INHIBIT_LATCHED','Q-bar readback polarity preserved')
    require(actual[('U4302','4')]=='COMMS_MR_N','Flight reset buffer drives comms supervisor MR, not NRST bus')
    require(actual[('U201','14')]!=actual[('U401','14')],'No cross-reset net short')
    # Native XML includes DNP entries as explicit properties, not only a value string.
    dnp=[r for r,c in parts.items() if any(p.get('name')=='dnp' for p in c.findall('property'))]
    for ref in ['R6310','R6410','R6510','R6804']:
        require(ref in dnp,f'{ref}: raw energetic/servo source link is DNP')
    require(all(f'R69{i}{j}' in dnp for i in [1,2,3] for j in [1,2,3,4]),'All continuity injection/return limiting paths DNP')
    missing=[r for r,c in parts.items() if not c.findtext('footprint')]
    require(set(missing)=={'J101'},'Only exact Nano-Fit footprint remains missing')
    require(actual[('U101','17')]==actual[('U101','18')]=='VBAT_SHUNT_IN','Both eFuse OUT pads feed upstream shunt node')
    require(actual[('R7101','1')]=='VBAT_SHUNT_IN' and actual[('R7101','2')]=='VBAT_PROTECTED','Bulk shunt separates common source protection from load branches')
    require(actual[('J101','1')]==actual[('J102','1')]=='VBAT_CROI_INPUT','Both mutually exclusive sources feed the same measured path')
    require(actual[('U7101','1')]==actual[('U7101','2')]=='GND','Croi INA228 address 0x40')
    require(actual[('U7101','4')]=='FOINSE_SDA_EXT' and actual[('U7101','5')]=='FOINSE_SCL_EXT','Current monitor remains behind existing optional bus boundary')
    require(actual[('R7105','1')]=='FOINSE_AUX_3V3' and actual[('R7105','2')]=='CROI_MON_3V3','Local current monitor operates without Foinse board')
    require('BZ9001' not in dnp,'Selected external-drive piezo populated')
    require(actual[('R9005','1')]=='3V3_OPTIONAL' and actual[('R9005','2')]=='BUZZER_LOW','Piezo discharge path present')
    # Negative tests exercise the checker, not a modified live schematic.
    bad=copy.deepcopy(root)
    h=next(net for net in bad.findall('nets/net') if net.get('name')=='CAN_H')
    n=next(n for n in h.findall('node') if n.get('ref')=='J501');n.set('pin','2')
    try:verify(bad,expected)
    except AssertionError:checks.append('Negative test: swapped CAN contact rejected')
    else:raise AssertionError('Checker accepted corrupted connector map')
    bad=copy.deepcopy(root)
    for net in bad.findall('nets/net'):
        if net.get('name')=='FLIGHT_VDDA':net.set('name','FLIGHT_3V3')
    try:verify(bad,expected)
    except AssertionError:checks.append('Negative test: analog-supply bypass short rejected')
    else:raise AssertionError('Checker accepted shorted VDDA')
    report=json.loads(erc.read_text());violations=[v for s in report['sheets'] for v in s['violations']]
    categories=Counter((v['severity']+' / '+v['type']) for v in violations)
    return {'status':'connectivity checks pass; engineering draft, not release',
            'physical_component_count':len(parts),'checked_pin_count':pincount,'architecture_checks':len(checks),
            'dnp_count':len(dnp),'dnp_refs':dnp,'missing_footprints':missing,
            'erc_categories':dict(categories),'checks':checks,
            'netlist_sha256':hashlib.sha256(netlist.read_bytes()).hexdigest(),
            'schematic_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(project.glob('*.kicad_sch'))},
            'limits':'No analog simulation, target test, layout/rating/thermal/inrush/ESD qualification or energetic release.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('project',type=Path);p.add_argument('netlist',type=Path)
    p.add_argument('erc',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();result=check(a.project,a.netlist,a.erc)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','schematic_sha256','dnp_refs']}))
