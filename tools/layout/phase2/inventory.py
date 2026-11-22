"""Burrito part inventory for the routing brief (S2): courtyard area per sheet,
every connector, and the large parts. Read-only: loads the netlist and the
footprints, writes a JSON report. Run inside the KiCad 9.0.8 chroot:

    python3 /work/tools/layout/phase2/inventory.py > /work/hardware/croi2/output/layout/inventory.json
"""
import sys, json
sys.path.insert(0, '/work/tools/layout/phase1/engine')
import pcbnew as K
import netlist, board as B
from place import geometry

NET = '/work/hardware/croi2/output/full-netlist.xml'
LIB = '/work/hardware/croi2/libraries'

comps, nets = netlist.load(NET)
b = B.new_board('/tmp/inventory.kicad_pcb')
fps, netinfo, missing = B.add_parts(b, comps, nets, LIB)

def sheet_key(path):
    parts = [p for p in path.split('/') if p]
    return parts[0] if parts else '/'

rows, per_sheet = [], {}
for r, fp in sorted(fps.items()):
    c = comps[r]
    x0, y0, x1, y1 = geometry(fp)[0][0]
    w, h = x1 - x0, y1 - y0
    s = sheet_key(c.sheet)
    d = per_sheet.setdefault(s, {'parts': 0, 'area_mm2': 0.0, 'dnp': 0})
    d['parts'] += 1
    d['area_mm2'] += w * h
    d['dnp'] += int(bool(c.dnp))
    rows.append({'ref': r, 'value': c.value, 'fp': c.fp, 'sheet': c.sheet, 'w': round(w, 2),
                 'h': round(h, 2), 'area': round(w * h, 1), 'pads': len(list(fp.Pads())),
                 'dnp': bool(c.dnp), 'tht': any(p.GetAttribute() == K.PAD_ATTRIB_PTH for p in fp.Pads())})

out = {
    'parts_with_footprint': len(rows),
    'missing_footprint': sorted(missing) if missing else [],
    'courtyard_area_total_mm2': round(sum(r['area'] for r in rows), 0),
    'board_area_mm2': 80 * 230,
    'per_sheet': {k: {**v, 'area_mm2': round(v['area_mm2'], 0)} for k, v in sorted(per_sheet.items())},
    'connectors': [r for r in rows if r['ref'].startswith('J')],
    'large_parts': sorted([r for r in rows if r['area'] >= 25 and not r['ref'].startswith('J')],
                          key=lambda r: -r['area']),
    'tht_parts': [r['ref'] for r in rows if r['tht']],
}
json.dump(out, sys.stdout, indent=1)
