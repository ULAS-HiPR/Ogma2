"""krt_wrap.py py_router/route.py ARGS...: KiCadRoutingTools' route.py with its final finer-grid lap switched off
(meter.py --no-finer-lap). Run from the router's checkout, as the meter runs route.py.

The lap (#1763, finer_grid_rung.py) maps the whole board again at half the run's grid for the nets still boxed in
after the ordinary laps. On Burrito it is the router's biggest allocation: board 1927e4ad's trial was killed for
memory at that step twice running (24 Nov, 5.8 GB, the session's limit). In the three complete trials before, it
rescued one net once and none otherwise. Setting its cell budget to zero makes the router skip it with its own
logged reason ("Finer-grid rung (#1763) skipped: ..."); nothing else changes."""
import os
import runpy
import sys

sys.path[0] = os.path.abspath('py_router')       # as `python py_router/route.py` would set it
import routing_defaults                           # noqa: E402

routing_defaults.FINER_GRID_RUNG_MAX_CELLS = 0
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
