"""TB2 with Freerouting: GND fanout by script (locked), L2 a plane, then Freerouting headless."""
import sys, json, subprocess, time
sys.path.insert(0, '/lab/engine')
import pcbnew as K
import route as R
MM = K.FromMM
b = K.LoadBoard('/lab/tb2/tb2.kicad_pcb')
ds = b.GetDesignSettings()
ds.m_TrackMinWidth = MM(0.1); ds.m_MinClearance = MM(0.1); ds.m_ViasMinSize = MM(0.45)
ds.m_MinThroughDrill = MM(0.2); ds.m_HoleClearance = MM(0.2); ds.m_CopperEdgeClearance = MM(0.3)
d = ds.m_NetSettings.GetDefaultNetclass()
d.SetTrackWidth(MM(0.15)); d.SetClearance(MM(0.15)); d.SetViaDiameter(MM(0.6)); d.SetViaDrill(MM(0.3))
t0 = time.time()
obs = R.Obstacles(b)
done, failed = R.fanout(b, obs, 'GND')
t1 = time.time()
out = '/lab/tb2/tb2-fr.kicad_pcb'
dsn, ses = out.replace('.kicad_pcb', '.dsn'), out.replace('.kicad_pcb', '.ses')
K.ExportSpecctraDSN(b, dsn)
r = subprocess.run(['java', '-Xmx3g', '-jar', '/lab/bin/freerouting-2.5.0.jar', '-de', dsn, '-do', ses, '--gui.enabled=false',
                    '--usage_and_diagnostic_data.disable_analytics=true', '--router.optimizer.enabled=false',
                    '--router.autorouter.max_passes=40'], capture_output=True, text=True)
t2 = time.time()
open('/lab/tb2/fr.log', 'w').write(r.stdout + r.stderr)
K.ImportSpecctraSES(b, ses)
K.ZONE_FILLER(b).Fill(b.Zones())
K.SaveBoard(out, b)
fin = [l for l in (r.stdout + r.stderr).splitlines() if 'Auto-routing stage completed' in l]
print(json.dumps({'gnd_fanout': [len(done), len(failed)], 'fanout_s': round(t1 - t0), 'freerouting_s': round(t2 - t1),
                  'summary': fin[0][-170:] if fin else None}))
