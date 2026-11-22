"""TB2: all of Burrito, quick banded placement in 80 x 230 (capacity test only, not the floorplan)."""
import sys, time, json
sys.path.insert(0, '/lab/engine')
import pcbnew as K
import netlist, board as B
from place import Placer

T0 = time.time()
NET = '/work/hardware/croi2/output/full-netlist.xml'
LIB = '/work/hardware/croi2/libraries'
OUT = '/lab/tb2/tb2.kicad_pcb'
OX, OY, W, H = 100.0, 50.0, 80.0, 230.0
GROUPS = [  # forward (y = 0) to aft (y = 230)
    ('rf', ['/04d', '/04e', '/04f']), ('out', ['/06-outputs', '/06b', '/06c', '/06e', '/06f', '/06pyro']),
    ('mag', ['/03mag']), ('sens', ['/03']), ('fmcu', ['/02-flight-mcu', '/02a', '/02flight-reset']),
    ('cmcu', ['/04-comms', '/04a', '/02comms', '/04b', '/04c', '/09']),
    ('can', ['/05']), ('pwr', ['/01', '/07', '/08', '/44']), ('arm', ['/06a'])]
comps, nets = netlist.load(NET)
b = B.new_board(OUT)
fps, netinfo, missing = B.add_parts(b, comps, nets, LIB)
B.outline(b, OX, OY, W, H)
P = Placer(fps, nets, (OX, OY), (W, H))
for hx in (4, 76):                                 # D-21Nov.23 hole keep-outs, 8 mm square
    for hy in (6, 79, 152, 225):
        P.keepouts.append((hx - 4, hy - 4, hx + 4, hy + 4, 'H'))
group = {}
for r, c in comps.items():
    if r not in fps: continue
    for g, pre in GROUPS:
        if any(c.sheet.startswith(p) for p in pre) and not (g == 'sens' and c.sheet.startswith('/03mag')):
            group[r] = g; break
area = {g: 0.0 for g, _ in GROUPS}
for r, g in group.items():
    bx = P.geo[r][0][0]; area[g] += (bx[2] - bx[0]) * (bx[3] - bx[1])
tot = sum(area.values()); y = 1.0; REG = {}
for g, _ in GROUPS:
    h = (H - 2) * area[g] / tot
    REG[g] = (1.0, y, W - 1.0, min(H - 1.0, y + h)); y += h
REG['arm'] = (1.0, REG['arm'][1] - 6, W - 1.0, H - 1.0)
P.fix('J102', 40, 230, 0)
fixed = {'J4501': (8, 8, 0), 'J4601': (72, 8, 0)}
for r, (x, yy, a) in fixed.items():
    P.fix(r, x, yy, a)
left = [r for r in fps if r not in P.placed]
fails = []
def score(r):
    links = sum(1 for p, n in P.pin_nets.get(r, {}).items()
                if P.fanout[n] <= P.power_fanout and any(q in P.placed for q, _ in nets[n] if q != r))
    bx = P.geo[r][0][0]
    return (links, (bx[2] - bx[0]) * (bx[3] - bx[1]))
while left:
    r = max(left, key=score); left.remove(r)
    if not P.place(r, REG[group[r]], rmax=40):
        # spill: anywhere on the board
        if not P.place(r, (1, 1, W - 1, H - 1), rmax=120):
            fails.append(r)
P.apply()
for hx in (4, 76):
    for hy in (6, 79, 152, 225):
        fp = K.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3')
        fp.SetReference(f'H{len([f for f in b.GetFootprints() if f.GetReference().startswith("H")]) + 1}')
        fp.SetAttributes(fp.GetAttributes() | K.FP_BOARD_ONLY | K.FP_EXCLUDE_FROM_BOM | K.FP_EXCLUDE_FROM_POS_FILES)
        fp.SetPosition(K.VECTOR2I(K.FromMM(OX + hx), K.FromMM(OY + hy))); b.Add(fp)
gnd = netinfo['GND']
B.zone(b, gnd, K.In1_Cu, [(OX + .3, OY + .3), (OX + W - .3, OY + .3), (OX + W - .3, OY + H - .3), (OX + .3, OY + H - .3)], name='L2 GND')
b.SetLayerType(K.In1_Cu, K.LT_POWER)
B.fill(b)
K.SaveBoard(OUT, b)
print(json.dumps({'parts': len(fps), 'missing_fp': missing, 'unplaced': fails,
                  'regions': {g: [round(v, 1) for v in REG[g]] for g in REG}, 'hpwl_m': round(P.hpwl() / 1000, 2),
                  'seconds': round(time.time() - T0, 1)}))
