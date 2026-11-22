"""Plant one violation per custom rule of spec.DRU on a copy of Burrito's board and read KiCad's DRC (stage C step 2,
the handoff: "Plant one violation per custom rule and see DRC report it").

    python3 tools/layout/rules_check.py [SCRATCH_DIR]

Each test adds copper to a fresh copy of hardware/croi2/Croi2.kicad_pcb, with the project's rules, and passes when
DRC's errors name the rule expected (or, for a test expecting none, when there are none). Board-local mm.
"""
import json, shutil, subprocess, os, sys
from pathlib import Path
import pcbnew as K
SRC = str(Path(__file__).resolve().parents[2] / 'hardware' / 'croi2' / 'Croi2')
OX, OY = 100.0, 50.0
V = lambda x, y: K.VECTOR2I(K.FromMM(OX + x), K.FromMM(OY + y))
def track(b, net, layer, a, c, w=0.15):
    t = K.PCB_TRACK(b); t.SetStart(V(*a)); t.SetEnd(V(*c)); t.SetWidth(K.FromMM(w)); t.SetLayer(layer); t.SetNet(b.FindNet(net)); b.Add(t)
def via(b, net, x, y):
    v = K.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetWidth(K.FromMM(0.6)); v.SetDrill(K.FromMM(0.3)); v.SetNet(b.FindNet(net)); b.Add(v)
tests = [
 ('track on L2', lambda b: track(b, 'NOR_EN', K.In1_Cu, (20, 100), (24, 100)), "L2 is an unbroken GND plane"),
 ('track on L4', lambda b: track(b, 'NOR_EN', K.In3_Cu, (20, 100), (24, 100)), "L4 is an unbroken GND plane"),
 ('fire logic 0.3 mm from another net on L3, outside U201', lambda b: (track(b, 'PYRO1_FIRE', K.In2_Cu, (20, 100), (24, 100)), track(b, 'NOR_EN', K.In2_Cu, (20, 100.45), (24, 100.45))), "Fire copper keeps 0.5 mm"),
 ('fire logic 0.25 mm from another net under U201', lambda b: (track(b, 'PYRO1_FIRE', K.F_Cu, (38, 52), (38, 56)), track(b, 'NOR_EN', K.F_Cu, (38.4, 52), (38.4, 56))), None),
 ('fire logic 0.15 mm from another net under U201', lambda b: (track(b, 'PYRO1_FIRE', K.F_Cu, (38, 52), (38, 56)), track(b, 'NOR_EN', K.F_Cu, (38.3, 52), (38.3, 56))), "Fire logic leaves U201"),
 ('fire logic crossing the courtyard edge, 0.25 mm from another net', lambda b: (track(b, 'PYRO1_FIRE', K.In2_Cu, (44, 55), (52, 55)), track(b, 'NOR_EN', K.In2_Cu, (44, 55.4), (52, 55.4))), "Fire copper keeps 0.5 mm"),
 ('RF via', lambda b: via(b, 'GNSS_RF', 20, 120), 'RF lines take no via'),
]
res = {}
d = sys.argv[1] if len(sys.argv) > 1 else '/tmp/rules-check'
for name, fn, expect in tests:
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    for ext in ('kicad_pro', 'kicad_dru'):
        shutil.copy(f'{SRC}.{ext}', f'{d}/t.{ext}')
    b = K.LoadBoard(f'{SRC}.kicad_pcb'); fn(b); K.SaveBoard(f'{d}/t.kicad_pcb', b)
    subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--severity-error', '-o', f'{d}/t.json', f'{d}/t.kicad_pcb'], capture_output=True)
    v = json.load(open(f'{d}/t.json'))['violations']
    descs = sorted({x['description'][:120] for x in v if 'library' not in x['description']})
    ok = (not descs) if expect is None else any(expect in x for x in descs)
    res[name] = {'expected': expect or 'no error', 'errors': descs, 'pass': ok}
print(json.dumps(res, indent=1))
sys.exit(0 if all(r['pass'] for r in res.values()) else 1)
