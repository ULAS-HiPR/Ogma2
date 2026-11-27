"""T5b: TB1 with scripted critical nets and GND fanout, locked, saved before any autorouter."""
import sys, math, json
sys.path.insert(0, '/lab/engine')
import pcbnew as K
import route as R
b = K.LoadBoard('/lab/tb1/tb1-k.kicad_pcb')
obs = R.Obstacles(b)
CRIT = {'FLIGHT_HSE_IN': .2, 'FLIGHT_HSE_OUT': .2, 'FLIGHT_LSE_IN': .2, 'FLIGHT_LSE_OUT': .2,
        'CAN+': .25, 'CAN-': .25, 'CAN2+': .25, 'CAN2-': .25}
res = {}
for net, w in CRIT.items():
    pads = [(f.GetReference(), p.GetNumber()) for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == net]
    xy = {k: R.pad_xy(b, *k) for k in pads}
    inside, ok, n = {pads[0]}, 0, 0
    while len(inside) < len(pads):
        a, c = min(((a, c) for a in inside for c in pads if c not in inside), key=lambda e: math.dist(xy[e[0]], xy[e[1]]))
        inside.add(c); n += 1
        ok += R.direct(b, obs, a[0], a[1], c[0], c[1], w) is not None
    res[net] = f'{ok}/{n}'
done, failed = R.fanout(b, obs, 'GND')
K.SaveBoard('/lab/tb1/tb1-pre.kicad_pcb', b)
import hashlib
items = sorted((t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetLayer()) for t in b.GetTracks() if t.IsLocked())
print(json.dumps({'critical': res, 'gnd_fanout': [len(done), len(failed)], 'locked': len(items),
                  'locked_hash': hashlib.sha256(repr(items).encode()).hexdigest()[:16]}))
