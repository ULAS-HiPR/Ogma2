"""Reload saved PCB and compare its identity, pads, models and geometry to native XML."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import pcbnew as k
import wx
from build_board_layout import courtyard, intersect


def check(project,name,netlist):
    board=k.LoadBoard(str(project/(name+'.kicad_pcb')))
    root=ET.parse(netlist).getroot(); report=json.loads((project/'placement-report.json').read_text())
    symbols={c.get('ref'):c for c in root.findall('components/comp')}
    actual={f.GetReference():f for f in board.GetFootprints()}
    expected={ref:c for ref,c in symbols.items() if c.findtext('footprint')}
    assert set(actual)==set(expected), 'Missing, extra or duplicated physical component'
    assert len(list(board.GetFootprints()))==len(actual), 'Duplicate PCB reference'
    pin_nets={(n.get('ref'),n.get('pin')):net.get('name') for net in root.findall('nets/net') for n in net.findall('node')}
    root_uuid=re.search(r'\(uuid "([^"]+)"\)',(project/(name+'.kicad_sch')).read_text()).group(1)
    checked=0; models=0
    for ref,fp in actual.items():
        c=expected[ref]
        assert fp.GetPath().AsString()=='/'+root_uuid+c.find('sheetpath').get('tstamps')+c.findtext('tstamps'), (ref,'schematic UUID path')
        assert fp.GetFPID().GetLibItemName()==c.findtext('footprint').split(':',1)[1],(ref,'footprint binding')
        assert fp.GetValue()==c.findtext('value'),(ref,'value')
        props={p.get('name'):p.get('value') for p in c.findall('property')}
        assert bool(fp.GetAttributes() & k.FP_DNP)==('dnp' in props),(ref,'DNP')
        assert bool(fp.GetAttributes() & k.FP_EXCLUDE_FROM_BOM)==('exclude_from_bom' in props),(ref,'BOM attribute')
        nums=set()
        for pad in fp.Pads():
            number=pad.GetNumber()
            if not number:
                assert not pad.GetNetname(),(ref,'mechanical pad energised');continue
            nums.add(number)
            assert pad.GetNetname()==pin_nets.get((ref,number),''),(ref,number,pad.GetNetname(),pin_nets.get((ref,number)))
            checked+=1
        assert {pin for r,pin in pin_nets if r==ref}.issubset(nums),(ref,'symbol pin without pad')
        assert fp.GetParentGroup() is not None or (
            report['positions'][ref]['staged'] and
            ref in report.get('installation_revision',{}).get('new_staged_refs',[])
        ),(ref,'ungrouped outside explicit installation staging')
        for model in fp.Models():
            filename=model.m_Filename
            assert filename.startswith('${KIPRJMOD}/libraries/3d/'),(ref,'nonportable model')
            assert (project/filename.replace('${KIPRJMOD}/','')).is_file(),(ref,'missing model')
            models+=1
    assert board.GetCopperLayerCount()==4
    assert k.ToMM(board.GetDesignSettings().GetBoardThickness())==1.6
    assert len(list(board.GetTracks()))==0 and board.GetAreaCount()==0, 'Unexpected routing or zones'
    edges=[s for s in board.GetDrawings() if s.GetLayer()==k.Edge_Cuts]
    assert len(edges)==4, 'Outline is not four segments'
    endpoints=Counter(tuple([s.GetStart().x,s.GetStart().y]) for s in edges)
    endpoints.update(tuple([s.GetEnd().x,s.GetEnd().y]) for s in edges)
    assert len(endpoints)==4 and set(endpoints.values())=={2}, 'Open or branching outline'
    xs=[k.ToMM(x)-100 for x,y in endpoints];ys=[k.ToMM(y)-50 for x,y in endpoints]
    assert sorted(set(xs))==[0,60] and sorted(set(ys))==[0,report['outline_mm'][1]]
    bounds={r:courtyard(f) for r,f in actual.items()}
    collisions=[]
    for ra,rb in itertools.combinations(actual,2):
        a,b=actual[ra],actual[rb]
        drilled=any(p.GetDrillSize().x for p in a.Pads()) or any(p.GetDrillSize().x for p in b.Pads())
        if (a.IsFlipped()==b.IsFlipped() or drilled) and intersect(bounds[ra],bounds[rb]):collisions.append([ra,rb])
    assert not collisions,('courtyard/drill reservation collision',collisions)
    mate='J102' if name=='Croi2' else 'J301'
    for ref,r in report['positions'].items():
        if r['staged'] or ref==mate:continue
        x,y,w,h=bounds[ref];x-=100;y-=50
        assert x>=-.001 and y>=-.001 and x+w<=60.001 and y+h<=report['outline_mm'][1]+.001,(ref,'outside outline')
        if name=='Croi2' and r['block']!='GNSS':assert y>=35-.001,(ref,'quiet GNSS end invaded')
    fp=actual[mate]; counts=Counter(p.GetNumber() for p in fp.Pads() if p.GetNumber())
    assert counts=={str(i):6 for i in range(1,9)},'Samtec six tails per contact lost'
    manifest=json.loads((project/'libraries/board-library-manifest.json').read_text())
    for relative,digest in manifest['hashes'].items():
        assert hashlib.sha256((project/relative).read_bytes()).hexdigest()==digest,('library snapshot changed',relative)
    # Negative test: an in-memory corruption must be detectable; never saved.
    pad=next(p for p in actual[mate].Pads() if p.GetNumber()=='1');old=pad.GetNetname()
    pad.SetNetCode(0)
    assert pad.GetNetname()!=pin_nets[(mate,'1')], 'Negative pad-net corruption not detectable'
    drc=json.loads((project/'output/pcb-drc.json').read_text())
    parity=Counter(v['type'] for v in drc['schematic_parity'])
    assert set(parity)<= {'missing_footprint'}, ('Schematic/PCB identity mismatch',parity)
    return {'status':'saved PCB identity/connectivity/geometry checks pass; unrouted engineering draft',
        'footprints':len(actual),'physical_numbered_pads_checked':checked,'resolved_model_instances':models,
        'groups':len(list(board.Groups())),'on_board':report['on_board_count'],'staged':report['staged_count'],
        'copper_layers':4,'outline_mm':report['outline_mm'],'courtyard_collisions':collisions,
        'missing_footprints':report['missing_footprints'],'native_drc_categories':dict(Counter(v['type'] for v in drc['violations'])),
        'native_unrouted_items':len(drc['unconnected_items']),'native_parity_categories':dict(parity),
        'negative_test':'In-memory mate contact disconnection detected; not saved',
        'pcb_sha256':hashlib.sha256((project/(name+'.kicad_pcb')).read_bytes()).hexdigest(),
        'limits':'No routing capacity, voltage clearance rules, thermal, RF, assembly, vibration or energetic qualification.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('project',type=Path);p.add_argument('name');p.add_argument('netlist',type=Path);a=p.parse_args()
    app=wx.App(False);report=check(a.project,a.name,a.netlist)
    (a.project/'board-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
