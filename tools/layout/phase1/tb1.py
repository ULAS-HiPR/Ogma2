"""TB1: a throwaway board cut from Burrito (flight MCU, CAN, USB service), built by pcbnew."""
import sys, time, json
sys.path.insert(0, '/lab/engine')
import pcbnew as K
import netlist, board as B
from place import Placer

T0 = time.time()
NET = '/work/hardware/croi2/output/full-netlist.xml'
LIB = '/work/hardware/croi2/libraries'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/lab/tb1/tb1.kicad_pcb'
SHEETS = {'mcu': ['/02-flight-mcu/', '/02a-flight-support/', '/02flight-reset-debug/'],
          'can': ['/05-can/'], 'usb': ['/04c-usb-service/']}
REGION = {'mcu': (1.5, 1.5, 52, 62), 'can': (52, 1.5, 78.5, 98.5), 'usb': (1.5, 62, 52, 98.5)}
OX, OY, W, H = 100.0, 50.0, 80.0, 100.0

comps, nets = netlist.load(NET)
comps, nets = netlist.subset(comps, nets, [s for v in SHEETS.values() for s in v])
b = B.new_board(OUT)
fps, netinfo, missing = B.add_parts(b, comps, nets, LIB)
B.outline(b, OX, OY, W, H)
P = Placer(fps, nets, (OX, OY), (W, H))
group = {r: g for g, ss in SHEETS.items() for r, c in comps.items() if any(c.sheet.startswith(s) for s in ss) and r in fps}
# fixed parts: MCU in the middle of its region, connectors at edges
P.fix('U201', 26, 30, 0)
P.fix('J4401', 26, 95.5, 0)
for ref, x, y, a in (('J501', 72, 8, 0), ('J502', 72, 92, 180)):
    if ref in fps:
        P.fix(ref, x, y, a)
left = [r for r in fps if r not in P.placed]
fails = []
while left:
    def score(r):
        links = 0
        for p, n in P.pin_nets.get(r, {}).items():
            if P.fanout[n] <= P.power_fanout and any(q in P.placed for q, _ in nets[n] if q != r):
                links += 1
        bx = P.geo[r][0][0]
        return (links, (bx[2] - bx[0]) * (bx[3] - bx[1]))
    r = max(left, key=score)
    left.remove(r)
    if not P.place(r, REGION[group[r]]):
        fails.append(r)
P.apply()
gnd = netinfo.get('GND')
B.zone(b, gnd, K.In1_Cu, [(OX + .3, OY + .3), (OX + W - .3, OY + .3), (OX + W - .3, OY + H - .3), (OX + .3, OY + H - .3)], name='L2 GND')
B.fill(b)
K.SaveBoard(OUT, b)
print(json.dumps({'parts': len(fps), 'missing_fp': missing, 'unplaced': fails, 'nets': len(nets),
                  'hpwl_mm': round(P.hpwl(), 1), 'seconds': round(time.time() - T0, 1)}))
