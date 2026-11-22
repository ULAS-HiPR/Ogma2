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
    'Ogma2:MMC5983MA': f'{K9}, Package_LGA:LGA-16_3x3mm_P0.5mm; capture step 4; pads checked against MEMSIC MMC5983MA Rev. A p. 20 (step 11)',
    'Ogma2:G125-MS10605M2P': f'{K9}, Connector_Harwin:Harwin_Gecko_G125-MS10605M2P_2x03_P1.25mm_Vertical; capture step 5',
    'Fuse:Fuse_1206_3216Metric': f'{K9}, Fuse.pretty; capture step 5 (F501 / F502)',
    'Fuse:Fuse_Littelfuse-NANO2-451_453': f'{K9}, Fuse.pretty; capture step 6 (F6101 / F6102)',
    'Package_QFP:LQFP-64_10x10mm_P0.5mm': f'{K9}, Package_QFP.pretty; capture step 7 (U401)',
    'Connector_Molex:Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical': f'{K9}, Connector_Molex.pretty; capture step 9 (J6101, D-21Nov.12)',
    'Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical': f'{K9}, Connector_JST.pretty; capture step 9 (J6102, D-21Nov.12)',
    'Buzzer_Beeper:MagneticBuzzer_PUI_SMT-1028-T-2-R': f'{K9}, Buzzer_Beeper.pretty; capture step 9 (BZ9001, D-21Nov.20)',
    'Capacitor_SMD:C_0805_2012Metric': f'{K9}, Capacitor_SMD.pretty; capture step 9 (C4504, D-21Nov.17)',
    'Diode_SMD:D_SOD-882': f'{K9}, Diode_SMD.pretty; capture step 10 (D4501, D-22Nov.8); 3D model not in the GitHub mirror',
    'Capacitor_SMD:CP_Elec_8x10': f'{K9}, Capacitor_SMD.pretty, Nichicon 8 x 10 mm; capture step 11 (C1403, Nichicon PCW phi 8 x 10)',
    'TestPoint:TestPoint_Keystone_5010-5014_Multipurpose': f'{K9}, TestPoint.pretty; capture step 12 (GND loops, Keystone 5011, D-22Nov.9); 3D model not in the GitHub mirror',
    'Connector_Molex:Molex_Micro-Fit_3.0_43650-0215_1x02_P3.00mm_Vertical': f'{K9}, Connector_Molex.pretty, from Molex drawing 436500215; capture step 14 (J103, D-22Nov.18)',
}
MODEL_SOURCE = 'KiCad kicad-packages3D, master branch (GitHub mirror), fetched 21 Nov 2026 at capture close-out'
FETCHED = ['Capacitor_SMD.3dshapes/CP_Elec_6.3x7.7.step', 'Capacitor_SMD.3dshapes/CP_Elec_8x10.5.step', 'Capacitor_SMD.3dshapes/CP_Elec_8x10.step',
           'Fuse.3dshapes/Fuse_1206_3216Metric.step', 'Package_LGA.3dshapes/LGA-16_3x3mm_P0.5mm.step',
           'Package_QFP.3dshapes/LQFP-64_10x10mm_P0.5mm.step', 'Capacitor_SMD.3dshapes/C_0805_2012Metric.step']
DEB_SOURCE = ('KiCad 9.0.7 3D library, Ubuntu package kicad-packages3d_9.0.7-1_all.deb fetched with apt, 22 Nov 2026; '
              'copied unchanged (see libraries/3d/GENERATED.md)')
FROM_DEB = ['Crystal.3dshapes/Crystal_SMD_3215-2Pin_3.2x1.5mm.step', 'Crystal.3dshapes/Crystal_SMD_2016-4Pin_2.0x1.6mm.step',
            'Diode_SMD.3dshapes/D_SOD-882.step',
            'Package_SO.3dshapes/Texas_HTSSOP-14-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask3.155x3.255mm.step',
            'Package_SON.3dshapes/WSON-10-1EP_2.5x2.5mm_P0.5mm_EP1.2x2mm.step',
            'Package_LGA.3dshapes/ST_HLGA-10_2x2mm_P0.5mm_LayoutBorder3x2y.step',
            'Connector_Coaxial.3dshapes/SMA_Amphenol_132291_Vertical.step']
DRAWN_SOURCE = ('Drawn by tools/layout/models3d.py from the footprint F.Fab outline and the heights in '
                'libraries/3d/GENERATED.md, 22 Nov 2026; simplified, several heights unverified')
DRAWN = ['TestPoint.3dshapes/TestPoint_Keystone_5000-5004_Miniature.step',
         'TestPoint.3dshapes/TestPoint_Keystone_5010-5014_Multipurpose.step',
         'Connector_JST.3dshapes/JST_VH_B2P-VH_1x02_P3.96mm_Vertical.step',
         'Connector_Molex.3dshapes/Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical.step',
         'Connector_Harwin.3dshapes/Harwin_Gecko_G125-MS10605M2P_2x03_P1.25mm_Vertical.step',
         'Fuse.3dshapes/Fuse_Littelfuse-NANO2-451_453.step', 'Buzzer_Beeper.3dshapes/MagneticBuzzer_PUI_SMT-1028-T-2-R.step',
         'RF_GPS.3dshapes/ublox_MAX-M10S.step', 'Package_DFN_QFN.3dshapes/Texas_RDH0030A_TPSM63603.step',
         'Connector_Samtec.3dshapes/Samtec_MPT-08-01-01-L-RA-SD.step',
         'Connector_Molex.3dshapes/Molex_Micro-Fit_3.0_43650-0215_1x02_P3.00mm_Vertical.step']


def base_note(note):
    """The note from before capture (2026-09-08), once: earlier runs appended the whole old note each time."""
    k = note.rfind('2026-09-08: ')
    return note[k:] if k >= 0 else note


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
        'model_sources': {m: MODEL_SOURCE for m in FETCHED} | {m: DEB_SOURCE for m in FROM_DEB} | {m: DRAWN_SOURCE for m in DRAWN},
        'scope': old['scope'], 'hashes': {str(p.relative_to(BOARD)): sha(p) for p in files},
        'revision_note': ('2026-11-21: schematic capture (capture specification, D-21Nov.9), steps 0-9; 22 Nov: steps 10-13 (D4501, C1403, '
                          'test points); 22 Nov: a 3D model for every part (KiCad 9.0.7 package, or drawn: libraries/3d/GENERATED.md); '
                          'step 14: J103 to Micro-Fit 3.0 43650-0215 (D-22Nov.18). J101 still lacks its Nano-Fit footprint. '
                          + base_note(old['revision_note'])),
        'symbol_count_definition': old['symbol_count_definition'],
    }
    assert all(f['source'] != 'unrecorded' for f in footprints), [f['id'] for f in footprints if f['source'] == 'unrecorded']
    OUT.write_text(json.dumps(new, indent=2, ensure_ascii=False) + '\n')
    return new


if __name__ == '__main__':
    m = main(Path(sys.argv[1]))
    print({k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in m.items() if k not in ('scope', 'revision_note', 'symbol_count_definition')})
    print('missing models:', m['unavailable_model_references'])
