"""Compare two KiCad XML netlists: components, values, footprints, DNP and pin->net."""
import sys, json, xml.etree.ElementTree as ET
from collections import Counter
def load(p):
    r = ET.parse(p).getroot()
    comps = {}
    for c in r.findall('components/comp'):
        ref = c.get('ref')
        props = {pp.get('name'): pp.get('value') for pp in c.findall('property')}
        comps[ref] = dict(value=(c.findtext('value') or ''), fp=(c.findtext('footprint') or ''),
                          dnp=('dnp' in props) or props.get('DNP') in ('yes', '1'),
                          sheet=(c.find('sheetpath').get('names') if c.find('sheetpath') is not None else ''))
    pins = {}
    for n in r.findall('nets/net'):
        name = n.get('name')
        if name.startswith('unconnected-'):
            name = 'NC'
        for nd in n.findall('node'):
            pins[(nd.get('ref'), nd.get('pin'))] = name
    return comps, pins
def erc(p):
    d = json.load(open(p))
    return Counter(f"{v['severity']}/{v['type']}" for s in d['sheets'] for v in s['violations'])
if __name__ == '__main__':
    a, b = sys.argv[1], sys.argv[2]
    ca, pa = load(a); cb, pb = load(b)
    phys = lambda c: {k: v for k, v in c.items() if not k.startswith('#')}
    print('components', len(phys(ca)), '->', len(phys(cb)), '| pins', len(pa), '->', len(pb))
    added = sorted(set(phys(cb)) - set(phys(ca))); removed = sorted(set(phys(ca)) - set(phys(cb)))
    print('added refs', len(added), added[:40]); print('removed refs', len(removed), removed[:40])
    for k in sorted(set(phys(ca)) & set(phys(cb))):
        for f in ('value', 'fp', 'dnp'):
            if ca[k][f] != cb[k][f]:
                print('changed', k, f, repr(ca[k][f]), '->', repr(cb[k][f]))
    diff = sorted(k for k in set(pa) | set(pb) if pa.get(k) != pb.get(k))
    print('pin-net differences', len(diff))
    for k in diff[:60]:
        print('  ', k, pa.get(k), '->', pb.get(k))
