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
    assert parts['U4606'].findtext("fields/field[@name='MPN']")=='Wio-LR2021 / SKU 100058045','Stale radio procurement identity'
    assert parts['U4606'].findtext("fields/field[@name='Manufacturer']")=='Seeed Studio','Stale radio manufacturer'
    require(set(parts)=={ref for ref in expected if not ref.startswith('#')},'Every native component covered')
    for ref,mpn in [('U201','STM32H563VIT6'),('U401','STM32H563VIT6'),
                    ('U3604','MX66L2G45GMI00'),('U4504','MAX-M10S-00B'),('U4606','Wio-LR2021')]:
        require(parts[ref].findtext('value')==mpn,f'{ref}: accepted exact device')
    require(actual[('U201','22')]!=actual[('U201','11')],'Flight VDDA link is not bypassed by a drawing short')
    require(actual[('U401','22')]!=actual[('U401','11')],'Comms VDDA link is not bypassed by a drawing short')
    for pin in ['48','98']:
        require(actual[('U201',pin)]=='FLIGHT_VCAP',f'Flight VCAP pad {pin} is not a 3.3 V supply')
    require(actual[('U201','6')]=='FLIGHT_3V3','Backup pin is held flight 3.3 V, not vehicle battery')
    for pin,net in {'1':'GND','2':'GNSS_RX_ISO','3':'GNSS_TX_ISO','4':'GNSS_PPS_ISO',
                    '7':'GNSS_3V3','8':'GNSS_3V3','9':'GNSS_RESET_N_ISO','10':'GND','11':'GNSS_RF','12':'GND'}.items():
        require(actual[('U4504',pin)]==net,f'MAX-M10S manufacturer pin {pin}: {net}')
    for pin in ['5','6','13','14','15','16','17','18']:
        require(actual[('U4504',pin)].startswith('unconnected-'),f'MAX unused pin {pin}; SAFEBOOT18 and backup6 unloaded')
    require({key for key,net in actual.items() if net=='GNSS_RF'}=={('U4504','11'),('J4501','1'),('D4501','1')},'Single passive GNSS RF path with ESD; no bias supply')
    require(actual[('J4501','2')]==actual[('D4501','2')]=='GND','GNSS SMA and ESD returns')
    require(parts['J4501'].findtext('value')=='132134','External GNSS vertical SMA')
    require(parts['D4501'].findtext('value')=='TPD1E0B04DPYR','GNSS low-capacitance ESD selection')
    require(parts['R1006'].findtext('value')=='22.1k 1%' and actual[('R1006','1')]=='BAT_SHDN_N' and actual[('R1006','2')]=='GND','Source enable defaults OFF locally; no raw-pack pull-up')
    for ref,pins in {'D1002':{'1':'VBAT_CROI_INPUT','3':'BAT_SW_DIODE'},
                     'R1012':{'1':'BAT_SW_DIODE','2':'BAT_SW_RMID'},
                     'R1013':{'1':'BAT_SW_RMID','2':'BAT_SWITCH_3V'},
                     'U1002':{'1':'BAT_SWITCH_3V','2':'GND'},
                     'J103':{'1':'BAT_SWITCH_3V','2':'BAT_SHDN_N'},
                     'C1006':{'1':'BAT_SHDN_N','2':'GND'}}.items():
        for pin,net in pins.items():require(actual[(ref,pin)]==net,f'External master {ref}.{pin}: {net}')
    require({r for (r,p),net in actual.items() if net=='BAT_SHDN_N'}=={'U101','R1006','J103','C1006'},'No firmware/AUX dependency in master-enable return')
    for pin,net in {'1':'LORA_3V3','2':'LORA_DIO1_MOD','3':'LORA_RESET_N_MOD',
                    '4':'LORA_MISO_MOD','5':'LORA_MOSI_MOD','6':'LORA_SCK_MOD',
                    '7':'LORA_NCS_MOD','8':'LORA_BUSY_MOD','9':'GND','10':'LORA_RF_SUBG',
                    '11':'GND','12':'GND','14':'GND','15':'GND','20':'GND'}.items():
        require(actual[('U4606',pin)]==net,f'Wio manufacturer pin {pin}: {net}')
    for pin in ['13','16','17','18','19','21','22']:
        require(actual[('U4606',pin)].startswith('unconnected-'),f'Wio unused RF/DIO pin {pin} NC')
    require({key for key,net in actual.items() if net=='LORA_RF_SUBG'}=={('U4606','10'),('J4601','1')},'Single sub-GHz host RF path')
    require(actual[('J4601','2')]=='GND','RF connector ground')
    require(parts['J4601'].findtext('value')=='132134' and parts['J4601'].findtext('footprint')=='Ogma2:SMA_Amphenol_132134_Vertical','Approved vertical standard SMA')
    require(actual[('U201','57')]=='SERVO3_PWM' and actual[('U201','88')]=='FLIGHT_STATUS_LED1','PD10 servo3; PD7 complementary readiness control')
    require(actual[('U6804','4')]=='SERVO3_PWM' and actual[('U6804','11')]=='SERVO3_PWM_ISO','Third forward PWM-buffer channel')
    require(actual[('R6606','1')]=='SERVO3_PWM_ISO' and actual[('R6606','2')]=='SERVO3_PWM_EXT','Servo3 series boundary')
    require(actual[('R6607','1')]=='SERVO3_PWM_EXT' and actual[('R6607','2')]=='GND','Servo3 connector-side off-default pull-down')
    require(parts['J6602'].findtext('value')=='430451000','Ten-contact servo connector')
    for pin,net in {'1':'SERVO_VBAT','2':'SERVO1_PWM_EXT','3':'GND','4':'SERVO_VBAT','5':'SERVO2_PWM_EXT','6':'GND','7':'SERVO_VBAT','8':'SERVO3_PWM_EXT','9':'GND'}.items():
        require(actual[('J6602',pin)]==net,f'Three-servo harness contact {pin}')
    require(actual[('J6602','10')].startswith('unconnected-'),'Servo connector contact10 NC')
    for pin,net in {'2':'FLIGHT_STATUS_LED1','3':'GND','4':'FLIGHT_NOT_READY','5':'FLIGHT_3V3'}.items():
        require(actual[('U9101',pin)]==net,f'Inverter manufacturer DBV contact {pin}')
    require(parts['U9101'].findtext('value')=='SN74LVC1G04DBVR','Readiness inverter exact selection')
    require(actual[('R9102','1')]=='FLIGHT_STATUS_LED1' and actual[('R9102','2')]=='GND' and parts['R9102'].findtext('value')=='47k','Readiness defaults low when MCU pin floats')
    require(actual[('R9101','1')]=='FLIGHT_NOT_READY','Red LED no longer loads servo GPIO')
    require(actual[('C9101','1')]=='FLIGHT_3V3' and actual[('C9101','2')]=='GND','Local inverter bypass')
    require(actual[('R4621','1')]=='LORA_3V3' and actual[('R4621','2')]=='LORA_BUSY_MOD','Open-drain BUSY pulled to switched rail')
    for i,sig in enumerate(['SCK','MOSI','MISO','NCS','RESET_N','BUSY','DIO1']):
        ref=f'R{4614+i}'
        require(actual[(ref,'1')]==f'LORA_{sig}_ISO' and actual[(ref,'2')]==f'LORA_{sig}_MOD',f'{sig} series boundary')
        require(parts[ref].findtext('value')=='470R',f'{sig} initial damping value')
    require(not {'U4605','C4605','R4606','R4607'} & set(parts),'Obsolete external RF-switch control components removed')
    require(actual[('U4604','13')]=='GND' and all(actual[('U4604',pin)].startswith('unconnected-') for pin in ['11','12']),'Unused isolation channel disabled')
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
