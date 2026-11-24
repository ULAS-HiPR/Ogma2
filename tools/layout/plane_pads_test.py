"""plane_pads_test.py FANNED: the plane-pad count (meter.plane_pads_open, D-24Nov.15) proven on a planted miss.

    python3 tools/layout/plane_pads_test.py /root/layers/<trial>/fanned.kicad_pcb

Counts the fanned board's open plane pads, then takes away the via of one pad that reaches its plane through a via
of its own (in memory; the file is not touched) and expects that pad listed. Prints the counts and exits non-zero
if the planted miss isn't caught."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build                                     # noqa: E402
import meter                                     # noqa: E402
from engine import metrics as M                  # noqa: E402
import pcbnew as K                               # noqa: E402


def main():
    spec = build.load_spec('croi2')
    b = K.LoadBoard(sys.argv[1])
    bd = M.BoardData(b, spec.ORIGIN, (spec.W, spec.H))
    planes = {n: l for n, l in M.plane_nets(bd, set(spec.RAILS)).items() if M.short(n) in ('GND', 'FLIGHT_3V3')}
    n0, open0 = meter.plane_pads_open(b, spec.ORIGIN, planes, [])
    print(f'{len(open0)} of {n0} plane pads open')
    ox, oy = spec.ORIGIN
    vias = [t for t in b.GetTracks() if t.Type() == K.PCB_VIA_T and t.GetNetname() in planes]
    for f in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
        for p in f.Pads():
            name = f'{f.GetReference()}.{p.GetNumber()}'
            if p.GetNetname() not in planes or name in open0 or p.GetAttribute() == K.PAD_ATTRIB_PTH:
                continue
            mine = [v for v in vias if v.GetNetname() == p.GetNetname() and p.HitTest(v.GetPosition())]
            if len(mine) != 1:
                continue
            b.RemoveNative(mine[0])
            n1, open1 = meter.plane_pads_open(b, spec.ORIGIN, planes, [])
            ok = name in open1
            print(f"{'PASS' if ok else 'FAIL'} planted: {name}'s in-pad via taken away -> "
                  f"{'listed' if ok else 'not listed'} ({len(open1)} of {n1} open)")
            sys.exit(0 if ok else 1)
    print('FAIL no plane pad with a single in-pad via to plant a miss in')
    sys.exit(1)


if __name__ == '__main__':
    main()
