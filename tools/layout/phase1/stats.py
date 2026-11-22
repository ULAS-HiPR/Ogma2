import sys, json
import pcbnew as K
from collections import Counter
b = K.LoadBoard(sys.argv[1])
K.ZONE_FILLER(b).Fill(b.Zones())
out = sys.argv[1].replace('.kicad_pcb', '-filled.kicad_pcb'); K.SaveBoard(out, b)
tr = [t for t in b.GetTracks() if t.Type() == K.PCB_TRACE_T]
vi = [t for t in b.GetTracks() if t.Type() == K.PCB_VIA_T]
print(json.dumps({'tracks': len(tr), 'vias': len(vi), 'length_mm': round(sum(K.ToMM(t.GetLength()) for t in tr)),
                  'by_layer': dict(Counter(b.GetLayerName(t.GetLayer()) for t in tr)),
                  'widths': dict(Counter(round(K.ToMM(t.GetWidth()), 3) for t in tr).most_common(6)),
                  'min_w': min(round(K.ToMM(t.GetWidth()), 3) for t in tr)}))
