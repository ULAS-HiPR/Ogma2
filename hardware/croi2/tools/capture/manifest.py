"""Regenerate libraries/board-library-manifest.json from the exported netlist and the vendored libraries.

Keeps each earlier footprint's recorded source; footprints added during capture get theirs from
ADDED. Models: every (model ...) a footprint names, checked for a file under libraries/3d.
Usage: python3 manifest.py <netlist.xml>
"""
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

BOARD = Path(__file__).resolve().parents[2]
LIB = BOARD / 'libraries'
OUT = LIB / 'board-library-manifest.json'
K9 = 'KiCad 9.0.7 official library'
ADDED = {
    'Capacitor_SMD:CP_Elec_6.3x7.7': f'{K9}, Capacitor_SMD.pretty; capture step 2 (C1007)',
    'Capacitor_SMD:CP_Elec_8x10.5': f'{K9}, Capacitor_SMD.pretty; capture step 3 (C1403); land pattern to check against Nichicon',
    'Ogma2:MMC5983MA': f'{K9}, Package_LGA:LGA-16_3x3mm_P0.5mm (drawn from MEMSIC MMC5883MA); capture step 4; pads to check against the MMC5983MA drawing',
    'Ogma2:G125-MS10605M2P': f'{K9}, Connector_Harwin:Harwin_Gecko_G125-MS10605M2P_2x03_P1.25mm_Vertical; capture step 5',
    'Fuse:Fuse_1206_3216Metric': f'{K9}, Fuse.pretty; capture step 5 (F501 / F502)',
    'Fuse:Fuse_Littelfuse-NANO2-451_453': f'{K9}, Fuse.pretty; capture step 6 (F6101 / F6102)',
    'Package_QFP:LQFP-64_10x10mm_P0.5mm': f'{K9}, Package_QFP.pretty; capture step 7 (U401)',
}
MODEL_SOURCE = 'KiCad kicad-packages3D, master branch (GitHub mirror), fetched 21 Nov 2026 at capture close-out'
FETCHED = ['Capacitor_SMD.3dshapes/CP_Elec_6.3x7.7.step', 'Capacitor_SMD.3dshapes/CP_Elec_8x10.5.step',
           'Fuse.3dshapes/Fuse_1206_3216Metric.step', 'Package_LGA.3dshapes/LGA-16_3x3mm_P0.5mm.step',
           'Package_QFP.3dshapes/LQFP-64_10x10mm_P0.5mm.step']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(netlist):
    old = json.loads(OUT.read_text())
    sources = {f['id']: f['source'] for f in old['footprints']} | ADDED
    root = ET.parse(netlist).getroot()
    comps = root.findall('components/comp')
    refs, libids, nofp = defaultdict(list), set(), []
    for c in comps:
        fp = c.findtext('footprint') or ''
        ls = c.find('libsource')
        libids.add(f"{ls.get('lib')}:{ls.get('part')}")
        if fp:
            refs[fp].append(c.get('ref'))
        else:
            nofp.append({'ref': c.get('ref'), 'value': c.findtext('value')})
    footprints, missing_models, modelless = [], [], []
    for fid in sorted(refs):
        lib, name = fid.split(':', 1)
        path = LIB / f'{lib}.pretty' / f'{name}.kicad_mod'
        assert path.exists(), fid
        models = [m.split('libraries/3d/', 1)[-1] for m in re.findall(r'\(model "?([^"\s)]+)', path.read_text())]
        for m in models:
            if not (LIB / '3d' / m).exists():
                missing_models.append({'footprint': fid, 'model': m})
        if not models:
            modelless.append(fid)
        footprints.append({'id': fid, 'source': sources.get(fid, 'unrecorded'), 'models': models, 'refs': sorted(refs[fid])})
    files = sorted([*LIB.glob('*.kicad_sym'), *LIB.glob('*.pretty/*.kicad_mod'), *(p for p in (LIB / '3d').rglob('*') if p.is_file())])
    new = {
        'project': 'Croi2', 'source_project': old['source_project'], 'symbol_count': len(libids),
        'physical_components': len(comps), 'footprints': footprints, 'components_without_footprints': nofp,
        'unavailable_model_references': missing_models, 'model_less_footprints': modelless,
        'model_sources': {m: MODEL_SOURCE for m in FETCHED},
        'scope': old['scope'], 'hashes': {str(p.relative_to(BOARD)): sha(p) for p in files},
        'revision_note': ('2026-11-21: schematic capture (capture specification, D-21Nov.9), steps 0-8. '
                          'J101 still lacks its Nano-Fit footprint (Molex drawing not obtained); J6101 / J6102 are placeholders '
                          'until their parts are chosen. ' + old['revision_note']),
        'symbol_count_definition': old['symbol_count_definition'],
    }
    assert all(f['source'] != 'unrecorded' for f in footprints), [f['id'] for f in footprints if f['source'] == 'unrecorded']
    OUT.write_text(json.dumps(new, indent=2, ensure_ascii=False) + '\n')
    return new


if __name__ == '__main__':
    m = main(Path(sys.argv[1]))
    print({k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in m.items() if k not in ('scope', 'revision_note', 'symbol_count_definition')})
    print('missing models:', m['unavailable_model_references'])
