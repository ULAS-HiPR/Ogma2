"""T5 hybrid on TB1: scripted critical nets and GND fanout, locked; Freerouting for the rest."""
import sys, json, hashlib, math, subprocess, time
sys.path.insert(0, '/lab/engine')
import pcbnew as K
import route as R

MM = K.FromMM
src, out = '/lab/tb1/tb1.kicad_pcb', '/lab/tb1/tb1-h.kicad_pcb'
b = K.LoadBoard(src)
b.SetLayerType(K.In1_Cu, K.LT_POWER)
ds = b.GetDesignSettings()
ds.m_TrackMinWidth = MM(0.1); ds.m_MinClearance = MM(0.1); ds.m_ViasMinSize = MM(0.45)
ds.m_MinThroughDrill = MM(0.2); ds.m_HoleClearance = MM(0.2); ds.m_CopperEdgeClearance = MM(0.3)
d = ds.m_NetSettings.GetDefaultNetclass()
d.SetTrackWidth(MM(0.15)); d.SetClearance(MM(0.15)); d.SetViaDiameter(MM(0.6)); d.SetViaDrill(MM(0.3))
obs = R.Obstacles(b)
CRIT = {'FLIGHT_HSE_IN': .2, 'FLIGHT_HSE_OUT': .2, 'FLIGHT_LSE_IN': .2, 'FLIGHT_LSE_OUT': .2,
        'CAN+': .25, 'CAN-': .25, 'CAN2+': .25, 'CAN2-': .25, 'USB_CONN_D+': .2, 'USB_CONN_D-': .2}
res = {}
for net, w in CRIT.items():
    pads = [(f.GetReference(), p.GetNumber()) for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == net]
    xy = {k: R.pad_xy(b, *k) for k in pads}
    # MST (Prim) over the pads, each edge routed pad to pad
    inside, edges = {pads[0]}, []
    while len(inside) < len(pads):
        e = min(((a, c) for a in inside for c in pads if c not in inside), key=lambda e: math.dist(xy[e[0]], xy[e[1]]))
        edges.append(e); inside.add(e[1])
    ok = sum(1 for (a, c) in edges if R.direct(b, obs, a[0], a[1], c[0], c[1], w) is not None)
    res[net] = f'{ok}/{len(edges)}'
done, failed = R.fanout(b, obs, 'GND')
def locked_hash():
    items = sorted((t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetWidth(), t.GetLayer())
                   for t in b.GetTracks() if t.IsLocked())
    return hashlib.sha256(repr(items).encode()).hexdigest()[:16], len(items)
h_before = locked_hash()
dsn, ses = out.replace('.kicad_pcb', '.dsn'), out.replace('.kicad_pcb', '.ses')
assert K.ExportSpecctraDSN(b, dsn)
t0 = time.time()
r = subprocess.run(['java', '-jar', '/lab/bin/freerouting-2.5.0.jar', '-de', dsn, '-do', ses, '--gui.enabled=false',
                    '--usage_and_diagnostic_data.disable_analytics=true', '--router.optimizer.enabled=false',
                    '--router.autorouter.max_passes=30'], capture_output=True, text=True)
t1 = time.time()
open(out.replace('.kicad_pcb', '-fr.log'), 'w').write(r.stdout + r.stderr)
K.ImportSpecctraSES(b, ses)
h_after = locked_hash()
K.ZONE_FILLER(b).Fill(b.Zones())
K.SaveBoard(out, b)
fin = [l for l in (r.stdout + r.stderr).splitlines() if 'Auto-routing stage completed' in l]
print(json.dumps({'critical': res, 'gnd_fanout': [len(done), len(failed)], 'gnd_failed': failed,
                  'locked_before': h_before, 'locked_after': h_after, 'freerouting_s': round(t1 - t0, 1),
                  'fr_summary': fin[0][-160:] if fin else None}))
