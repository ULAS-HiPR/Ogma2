"""KiCad-native unrouted floorplan from the actual exported schematic netlist.

Run with KiCad's Python/wx framework. Output is a NEW scratch PCB, never a routed
live board. Courtyard packing is an editable starting point, not PCB layout.
"""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import pcbnew as k
import wx


def block(sheet, name):
    if name=='Foinse2':
        return {'f01-source':'2S source', 'f01a-source-passives':'2S source',
            'f02-source':'6S source','f02a-source-passives':'6S source',
            'f03-croi-interface':'Croi interface','f04-monitor':'2S monitor',
            'f05-monitor':'6S monitor','f06-temperature-adc':'Temperature ADC',
            'f06a-adc-isolation':'Temperature ADC','f07-propulsion-service':'Propulsion output'}[sheet]
    if sheet=='04d-gnss': return 'GNSS'
    if sheet in ['04e-radio','04f-radio-module']: return 'Radio'
    if sheet in ['02-flight-mcu','02a-flight-support','02flight-reset-debug']: return 'Flight MCU'
    if sheet in ['04-comms-gnss-radio','04a-comms-support','02comms-reset-debug']: return 'Comms MCU'
    if sheet.startswith('03'): return 'Sensors and storage'
    if sheet=='04b-uart-boundary': return 'UART boundary'
    if sheet=='04c-usb-service': return 'USB service'
    if sheet=='05-can': return 'CAN'
    if sheet.startswith('06'): return 'Outputs'
    if sheet in ['01-power','01a-source-mux','01b-bootstrap','01c-preregulator']: return 'Power entry and buck'
    if sheet in ['01d-held-core','01flight-ldo']: return 'Held flight rail'
    if sheet.startswith('01'): return 'Branch supplies'
    if sheet=='07-foinse-aux': return 'Foinse AUX'
    if sheet=='08-rail-diagnostics': return 'Rail diagnostics'
    if sheet=='09-indicators': return 'Indicators'
    raise ValueError(sheet)


def courtyard(fp):
    fp.BuildCourtyardCaches()
    layer=k.B_CrtYd if fp.IsFlipped() else k.F_CrtYd
    shape=fp.GetCourtyard(layer)
    box=shape.BBox() if shape.OutlineCount() else fp.GetBoundingBox(False,False)
    return [k.ToMM(box.GetX()),k.ToMM(box.GetY()),k.ToMM(box.GetWidth()),k.ToMM(box.GetHeight())]


def load(project, name, netlist):
    board=k.BOARD(); board.SetCopperLayerCount(4)
    board.GetDesignSettings().SetBoardThickness(k.FromMM(1.6))
    root=ET.parse(netlist).getroot(); parts={}; nets={}; pin_nets={}
    for node in root.findall('nets/net'):
        net=k.NETINFO_ITEM(board,node.get('name'));board.Add(net);nets[node.get('name')]=net
        for pin in node.findall('node'):pin_nets[(pin.get('ref'),pin.get('pin'))]=node.get('name')
    missing=[]
    # Include the root UUID: XML sheetpath deliberately omits it.
    import re
    root_uuid=re.search(r'\(uuid "([^"]+)"\)',(project/(name+'.kicad_sch')).read_text()).group(1)
    for c in root.findall('components/comp'):
        ref=c.get('ref'); identifier=c.findtext('footprint')
        if not identifier:
            missing.append({'ref':ref,'value':c.findtext('value')});continue
        family,local=identifier.split(':',1)
        fp=k.FootprintLoad(str(project/'libraries'/(family+'.pretty')),local)
        assert fp is not None, identifier
        board.Add(fp);fp.SetReference(ref);fp.SetValue(c.findtext('value'));fp.SetFPIDAsString(identifier)
        path='/'+root_uuid+c.find('sheetpath').get('tstamps')+c.findtext('tstamps')
        fp.SetPath(k.KIID_PATH(path))
        props={p.get('name'):p.get('value') for p in c.findall('property')}
        sheet=props['Sheetname']; fp.SetSheetname(sheet);fp.SetSheetfile(props['Sheetfile'])
        attributes=fp.GetAttributes() & ~k.FP_EXCLUDE_FROM_BOM
        if 'exclude_from_bom' in props:attributes |= k.FP_EXCLUDE_FROM_BOM
        if 'dnp' in props:attributes |= k.FP_DNP
        fp.SetAttributes(attributes)
        for pad in fp.Pads():
            number=pad.GetNumber()
            if number and (ref,number) in pin_nets:
                pad.SetNet(nets[pin_nets[(ref,number)]])
        fp.Reference().SetVisible(True);fp.Value().SetVisible(False)
        fp.Reference().SetLayer(k.F_Fab)
        fp.Reference().SetTextSize(k.VECTOR2I_MM(1,1));fp.Reference().SetTextThickness(k.FromMM(.15))
        parts[ref]={'fp':fp,'sheet':sheet,'block':block(sheet,name),'path':path,
            'through':any(p.GetDrillSize().x>0 for p in fp.Pads())}
    return board,parts,missing,pin_nets


def intersect(a,b):
    return a[0]<b[0]+b[2]-.001 and b[0]<a[0]+a[2]-.001 and a[1]<b[1]+b[3]-.001 and b[1]<a[1]+a[3]-.001


def contains(a,b):
    return a[0]<=b[0]+.001 and a[1]<=b[1]+.001 and a[0]+a[2]>=b[0]+b[2]-.001 and a[1]+a[3]>=b[1]+b[3]-.001


def remove_rect(rectangles, used):
    result=[]
    for r in rectangles:
        if not intersect(r,used):result.append(r);continue
        x,y,w,h=r;u,v,uw,vh=used
        if u>x:result.append([x,y,u-x,h])
        if u+uw<x+w:result.append([u+uw,y,x+w-u-uw,h])
        if v>y:result.append([x,y,w,v-y])
        if v+vh<y+h:result.append([x,v+vh,w,y+h-v-vh])
    result=[r for r in result if r[2]>.1 and r[3]>.1]
    return [r for i,r in enumerate(result) if not any(j!=i and contains(other,r) and (other!=r or j<i) for j,other in enumerate(result))]


def position(fp,x,y,angle=0,back=False):
    fp.SetPosition(k.VECTOR2I_MM(0,0));fp.SetOrientationDegrees(0)
    if fp.IsFlipped()!=back:fp.Flip(k.VECTOR2I_MM(0,0),False)
    fp.SetOrientationDegrees(angle)
    bounds=courtyard(fp)
    fp.SetPosition(k.VECTOR2I_MM(x-bounds[0],y-bounds[1]))


def drawing(board,points,layer=k.Dwgs_User,width=.15):
    for a,b in zip(points,points[1:]):
        shape=k.PCB_SHAPE();shape.SetShape(k.SHAPE_T_SEGMENT);shape.SetStart(k.VECTOR2I_MM(*a))
        shape.SetEnd(k.VECTOR2I_MM(*b));shape.SetWidth(k.FromMM(width));shape.SetLayer(layer);board.Add(shape)


def note(board,text,x,y,size=1.0):
    item=k.PCB_TEXT(board);item.SetText(text);item.SetPosition(k.VECTOR2I_MM(x,y))
    item.SetTextSize(k.VECTOR2I_MM(size,size));item.SetTextThickness(k.FromMM(.15))
    item.SetLayer(k.Dwgs_User);item.SetHorizJustify(k.GR_TEXT_H_ALIGN_LEFT);board.Add(item)


def floorplan(board,parts,missing,pin_nets,project,name):
    height=120 if name=='Croi2' else 80
    free={'F':[[1,1,58,height-2]],'B':[[1,1,58,height-2]]}
    placed={};padding=.12
    def occupy(ref):
        p=parts[ref];fp=p['fp'];r=courtyard(fp);side='B' if fp.IsFlipped() else 'F'
        inflated=[r[0]-padding,r[1]-padding,r[2]+2*padding,r[3]+2*padding]
        for layer in ['F','B'] if p['through'] else [side]:free[layer]=remove_rect(free[layer],inflated)
        placed[ref]={'ref':ref,'block':p['block'],'sheet':p['sheet'],'side':side,'courtyard':r,
                     'position_mm':[k.ToMM(fp.GetPosition().x),k.ToMM(fp.GetPosition().y)],
                     'rotation_deg':fp.GetOrientationDegrees(),'staged':False}
    # Exact footprint origins are the PCB-edge centres, not courtyard centres.
    mate='J102' if name=='Croi2' else 'J301'
    parts[mate]['fp'].SetPosition(k.VECTOR2I_MM(30,height if name=='Croi2' else 0))
    parts[mate]['fp'].SetOrientationDegrees(0 if name=='Croi2' else 180)
    occupy(mate)
    # Unverified mechanical reservation only; deliberately no fabricated electrical pads.
    reserve=[1,92,14,18] if name=='Croi2' else [1,20,13,18]
    for side in free:free[side]=remove_rect(free[side],reserve)
    x,y,w,h=reserve
    drawing(board,[(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)])
    note(board,'J101 RESERVE',x,y+2,.7)
    note(board,'NOT A LAND PATTERN',x,y+4,.6)
    # Horizontal housing mouths face a board edge. Final overhang/mating travel is open.
    connectors=({'J4401':(1,36,270),'J6601':(44.9,77,270),'J6602':(44.9,92,270)}
        if name=='Croi2' else {'J201':(44.9,23,270),'J701':(44.9,66,270)})
    for ref,(x,y,angle) in connectors.items():
        position(parts[ref]['fp'],x,y,angle);occupy(ref)
    if name=='Croi2':
        # Quiet RF end. The 50 x 50 ground reference is NOT a cutout or split plane.
        for side in free:free[side]=remove_rect(free[side],[0,0,60,35])
        gnss_refs=[r for r,p in parts.items() if p['block']=='GNSS']
        fp=parts['U4504']['fp'];fp.SetPosition(k.VECTOR2I_MM(30,16));occupy('U4504')
        # Support cluster below the patch; no unrelated circuitry in this end.
        local=[[3,26,54,8]]
        for ref in sorted([r for r in gnss_refs if r!='U4504'],key=lambda r:-math.prod(courtyard(parts[r]['fp'])[2:])):
            fp=parts[ref]['fp']; w,h=courtyard(fp)[2:]
            candidates=[r for r in local if r[2]>=w+padding and r[3]>=h+padding]
            assert candidates, 'GNSS support cluster overflow'
            r=min(candidates,key=lambda r:(r[1],r[0]));position(fp,r[0],r[1]);occupy(ref)
            local=remove_rect(local,[r[0],r[1],w+padding,h+padding])
        targets={'Comms MCU':(15,48),'USB service':(5,38),'Radio':(48,49),
            'Flight MCU':(14,74),'Sensors and storage':(43,76),'UART boundary':(28,63),
            'Power entry and buck':(12,103),'Held flight rail':(15,92),'Branch supplies':(27,98),
            'Outputs':(47,103),'CAN':(55,62),'Foinse AUX':(26,108),'Rail diagnostics':(26,86),'Indicators':(3,57)}
        order=['Comms MCU','Radio','Flight MCU','Sensors and storage','Power entry and buck',
               'Held flight rail','Outputs','Branch supplies','USB service','CAN','UART boundary',
               'Foinse AUX','Rail diagnostics','Indicators']
    else:
        targets={'Croi interface':(30,13),'2S source':(14,29),'2S monitor':(15,47),
            '6S source':(45,29),'6S monitor':(44,47),'Temperature ADC':(24,63),'Propulsion output':(52,71)}
        order=['2S source','6S source','Croi interface','2S monitor','6S monitor','Temperature ADC','Propulsion output']
    # Large connectors/ICs lead; small support parts are attracted to their block.
    refs=[r for r in parts if r not in placed]
    refs.sort(key=lambda r:(0 if r.startswith('J') else 1,0 if math.prod(courtyard(parts[r]['fp'])[2:])>100 else 1,
                           order.index(parts[r]['block']),-math.prod(courtyard(parts[r]['fp'])[2:]),r))
    overflow=defaultdict(list)
    for ref in refs:
        p=parts[ref];fp=p['fp'];target=targets[p['block']];options=[]
        base_w,base_h=courtyard(fp)[2:]
        for side in (['F'] if p['through'] or ref.startswith('J') or ref in ['U201','U401','U4606','U3604'] else ['F','B']):
            for angle in [0,90]:
                w,h=(base_w,base_h) if angle==0 else (base_h,base_w)
                for r in free[side]:
                    if w+2*padding>r[2] or h+2*padding>r[3]:continue
                    x=max(r[0]+padding,min(target[0]-w/2,r[0]+r[2]-w-padding))
                    y=max(r[1]+padding,min(target[1]-h/2,r[1]+r[3]-h-padding))
                    candidate=[x-padding,y-padding,w+2*padding,h+2*padding]
                    if p['through'] and not any(contains(other,candidate) for other in free['B']):continue
                    score=(x+w/2-target[0])**2+(y+h/2-target[1])**2+(35 if side=='B' else 0)
                    options.append((score,x,y,angle,side))
        if not options:overflow[p['block']].append(ref);continue
        _,x,y,angle,side=min(options);position(fp,x,y,angle,side=='B');occupy(ref)
    # Visible, non-overlapping block staging, never counterfeit in-board placement.
    stage_y=4
    for title,refs in overflow.items():
        x=75;y=stage_y;row_height=0
        note(board,'STAGED / '+title,75,y-2,.9)
        for ref in refs:
            fp=parts[ref]['fp'];position(fp,0,0);w,h=courtyard(fp)[2:]
            if x+w>130:x=75;y+=row_height+.8;row_height=0
            position(fp,x,y);occupy(ref);placed[ref]['staged']=True
            x+=w+.6;row_height=max(row_height,h)
        stage_y=y+row_height+6
    drawing(board,[(0,0),(60,0),(60,height),(0,height),(0,0)],k.Edge_Cuts,.05)
    if name=='Croi2':
        drawing(board,[(5,0),(55,0),(55,50),(5,50),(5,0)])
        note(board,'50 x 50 GNSS ground-reference study; continuous plane',0,-7,.8)
        note(board,'Quiet RF end to y=35; no noisy blocks on either face',0,-4,.8)
    note(board,f'{name} / 60 x {height} mm / 4 layers / 1.6 mm / PROVISIONAL',0,height+13,1)
    note(board,'Unrouted block floorplan. No mounting pattern or manufacturing release.',0,height+16,.8)
    note(board,'Samtec mating edge: nominal board-edge gap 7.39 mm; add independent supports.',0,height+19,.8)
    note(board,'F: components/signals | In1: continuous GND | In2: power/slow | B: components/slow',0,height+22,.8)
    for i,item in enumerate(missing):
        note(board,f'NO FOOTPRINT: {item["ref"]} / {item["value"]}',75,stage_y+4+i*3,.85)
    for i,title in enumerate((['GNSS'] if name=='Croi2' else [])+order):
        rows=[r for r in placed.values() if r['block']==title]
        front=sum(r['side']=='F' and not r['staged'] for r in rows)
        back=sum(r['side']=='B' and not r['staged'] for r in rows)
        staged=sum(r['staged'] for r in rows)
        note(board,f'{title}: F {front} / B {back} / staged {staged}',-61,5+i*4,.85)
    groups={}
    for ref,p in parts.items():
        key=p['block']+' / '+p['sheet']
        if key not in groups:
            group=k.PCB_GROUP(board);group.SetName(key);board.Add(group);groups[key]=group
        groups[key].AddItem(p['fp'])
    # Shift away from the global origin; all report coordinates remain board-local.
    offset=k.VECTOR2I_MM(100,50)
    for fp in board.GetFootprints():fp.Move(offset)
    for item in board.GetDrawings():item.Move(offset)
    board.GetDesignSettings().SetAuxOrigin(offset)
    output=project/(name+'.kicad_pcb')
    assert not output.exists(), 'Never overwrite an existing PCB'
    project_file=project/(name+'.kicad_pro')
    settings_before=project_file.read_bytes()
    k.SaveBoard(str(output),board,True)  # aSkipSettings: preserve schematic/ERC/user settings.
    assert project_file.read_bytes()==settings_before, 'PCB save unexpectedly changed project settings'
    report={'project':name,'outline_mm':[60,height],'thickness_mm':1.6,'copper_layers':4,
        'board_origin_mm':[100,50],'placed_count':len(placed),'on_board_count':sum(not r['staged'] for r in placed.values()),
        'staged_count':sum(r['staged'] for r in placed.values()),'missing_footprints':missing,
        'groups':len(groups),'positions':placed,
        'limits':'Unrouted initial placement; no electrical/thermal/RF/assembly/height/connector-access qualification. Courtyard spacing is not routing capacity.'}
    (project/'placement-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='positions'}))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('project',type=Path);ap.add_argument('name',choices=['Croi2','Foinse2'])
    ap.add_argument('netlist',type=Path);ap.add_argument('--inventory',action='store_true');args=ap.parse_args()
    app=wx.App(False)
    board,parts,missing,pin_nets=load(args.project,args.name,args.netlist)
    if not args.inventory:
        floorplan(board,parts,missing,pin_nets,args.project,args.name)
        return
    summary=defaultdict(lambda:{'count':0,'courtyard_area_mm2':0,'largest':[]})
    for ref,p in parts.items():
        x,y,w,h=courtyard(p['fp']);r=summary[p['block']];r['count']+=1;r['courtyard_area_mm2']+=w*h
        r['largest'].append((round(w*h,1),ref,round(w,2),round(h,2)))
    for row in summary.values():
        row['largest']=sorted(row['largest'],reverse=True)[:4];row['courtyard_area_mm2']=round(row['courtyard_area_mm2'],1)
    print(json.dumps({'blocks':summary,'missing':missing},indent=2))


if __name__=='__main__':main()
