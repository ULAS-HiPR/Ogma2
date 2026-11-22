#!/bin/bash
# T6: KiCad IPC API — pcbnew GUI under Xvfb with the API server on, driven by kicad-python.
export HOME=/root
mkdir -p $HOME/.config/kicad/9.0
python3 - <<'PY'
import json, os
p = '/root/.config/kicad/9.0/kicad_common.json'
d = json.load(open(p)) if os.path.exists(p) else {}
d.setdefault('api', {})['enable_server'] = True
json.dump(d, open(p, 'w'), indent=2)
PY
[ -f $HOME/.config/kicad/9.0/fp-lib-table ] || printf '(fp_lib_table\n  (version 7)\n)\n' > $HOME/.config/kicad/9.0/fp-lib-table
[ -f $HOME/.config/kicad/9.0/sym-lib-table ] || printf '(sym_lib_table\n  (version 7)\n)\n' > $HOME/.config/kicad/9.0/sym-lib-table
cp /lab/tb1/tb1.kicad_pcb /lab/tb1/t6.kicad_pcb
rm -rf /tmp/kicad; mkdir -p /tmp/kicad
Xvfb :99 -screen 0 1600x1000x24 >/tmp/xvfb.log 2>&1 &
XV=$!
sleep 2
DISPLAY=:99 pcbnew /lab/tb1/t6.kicad_pcb >/tmp/pcbnew.log 2>&1 &
PN=$!
for i in $(seq 1 60); do [ -S /tmp/kicad/api.sock ] && break; sleep 1; done
ls -la /tmp/kicad/ 2>&1 | tail -3
/opt/kipy/bin/python - <<'PY'
import time
from kipy import KiCad
t = time.time()
try:
    k = KiCad(timeout_ms=10000)
    for i in range(90):
        try:
            k.ping(); break
        except Exception as e:
            last = e; time.sleep(1)
    print('ready after', round(time.time() - t, 1), 's')
    print('version', k.get_version())
    b = k.get_board()
    fps = b.get_footprints()
    print('footprints', len(fps), 'in', round(time.time() - t, 2), 's')
    from kipy.geometry import Vector2
    f = next(x for x in fps if x.reference_field.text.value == 'U201')
    f.position = Vector2.from_xy(int(127e6), int(81e6))
    t1 = time.time(); b.update_items([f]); print('move U201', round(time.time() - t1, 3), 's')
    from kipy.board_types import Track
    tr = Track(); tr.start = Vector2.from_xy(int(105e6), int(55e6)); tr.end = Vector2.from_xy(int(110e6), int(55e6)); tr.width = int(0.3e6)
    t1 = time.time(); b.create_items([tr]); print('add track', round(time.time() - t1, 3), 's')
    b.save(); print('saved')
except Exception as e:
    print('IPC failed:', type(e).__name__, str(e)[:300])
PY
DISPLAY=:99 xwd -root -silent > /tmp/screen.xwd 2>/dev/null; kill $PN $XV 2>/dev/null
sleep 1
grep -i -E "error|api" /tmp/pcbnew.log | head -5
