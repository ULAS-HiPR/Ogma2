"""Export DSN from a board, run Freerouting headless, import the SES, fill zones, save.
usage: fr_route.py src.kicad_pcb out.kicad_pcb [freerouting args...]"""
import sys, subprocess, time, json, hashlib
import pcbnew as K
src, out, extra = sys.argv[1], sys.argv[2], sys.argv[3:]
MM = K.FromMM
b = K.LoadBoard(src)
b.SetLayerType(K.In1_Cu, K.LT_POWER)          # L2: GND plane, not a routing layer
ds = b.GetDesignSettings()
ds.m_TrackMinWidth = MM(0.1); ds.m_MinClearance = MM(0.1); ds.m_ViasMinSize = MM(0.45)
ds.m_MinThroughDrill = MM(0.2); ds.m_HoleClearance = MM(0.2); ds.m_CopperEdgeClearance = MM(0.3)
dflt = ds.m_NetSettings.GetDefaultNetclass()
dflt.SetTrackWidth(MM(0.15)); dflt.SetClearance(MM(0.15)); dflt.SetViaDiameter(MM(0.6)); dflt.SetViaDrill(MM(0.3))
dsn = out.replace('.kicad_pcb', '.dsn'); ses = out.replace('.kicad_pcb', '.ses')
t0 = time.time()
assert K.ExportSpecctraDSN(b, dsn)
t1 = time.time()
cmd = ['java', '-jar', '/lab/bin/freerouting-2.5.0.jar', '-de', dsn, '-do', ses,
       '--gui.enabled=false', '--usage_and_diagnostic_data.disable_analytics=true'] + extra
r = subprocess.run(cmd, capture_output=True, text=True)
t2 = time.time()
log = [l for l in (r.stdout + r.stderr).splitlines() if 'JAVA_TOOL' not in l]
open(out.replace('.kicad_pcb', '-fr.log'), 'w').write('\n'.join(log))
ok = K.ImportSpecctraSES(b, ses)
K.ZONE_FILLER(b).Fill(b.Zones())
K.SaveBoard(out, b)
tr = [t for t in b.GetTracks() if t.Type() == K.PCB_TRACE_T]
print(json.dumps({'ses_import': ok, 'freerouting_s': round(t2 - t1, 1), 'tracks': len(tr),
                  'vias': sum(1 for t in b.GetTracks() if t.Type() == K.PCB_VIA_T),
                  'min_width': min((round(K.ToMM(t.GetWidth()), 3) for t in tr), default=None),
                  'layers': sorted({b.GetLayerName(t.GetLayer()) for t in tr}),
                  'ses_sha': hashlib.sha256(open(ses, 'rb').read()).hexdigest()[:16]}))
print('\n'.join(l for l in log if 'WARN' in l or 'ERROR' in l)[-1500:])
