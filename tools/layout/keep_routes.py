"""keep_routes.py ROUTED [--board BOARD] [--out OUT]: a routing trial's routes kept on the built board, for the hand-off
(25 Nov 2026: Seán takes the board by hand from here; the last board a script can rebuild is tag burrito-scripted-final).

    python3 /work/tools/layout/keep_routes.py /root/layers/d25-832b743a/routed.kicad_pcb

Run in the KiCad chroot. BOARD (default the repo's hardware/croi2/Croi2.kicad_pcb) gets every track, arc and via of
ROUTED that it lacks: the router's routes and the trial fan-out's plane vias and stubs. Nets are matched by name; a
fire-logic waiver twin (NET_WAIVED, meter.fan_out) goes back to its own net. Nothing else comes across: no rule areas
(the trial's keep-outs), no twin nets, no zones; BOARD keeps its own zones, refilled afterwards under the project's
rules (refill.py, in a fresh process). Copper already on BOARD (the spec's, locked) is left as it is; the kept routes
are unlocked. Writes OUT (default BOARD) and prints what came across and anything it couldn't match.
"""
import argparse
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pcbnew as K                               # noqa: E402
from engine import metrics as M                  # noqa: E402

TWIN = '_WAIVED'


def key(t, net, b):
    """An item's identity: kind, net, layer(s), geometry and size, in KiCad's integer units."""
    if t.Type() == K.PCB_VIA_T:
        p = t.GetPosition()
        return ('V', net, p.x, p.y, t.GetWidth(K.F_Cu), t.GetDrillValue(), int(t.GetViaType()))
    ends = tuple(sorted([(t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)]))
    if t.Type() == K.PCB_ARC_T:
        m = t.GetMid()
        return ('A', net, b.GetLayerName(t.GetLayer()), ends, (m.x, m.y), t.GetWidth())
    return ('T', net, b.GetLayerName(t.GetLayer()), ends, t.GetWidth())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('routed')
    ap.add_argument('--board', default=str(HERE.parent.parent / 'hardware' / 'croi2' / 'Croi2.kicad_pcb'))
    ap.add_argument('--out')
    a = ap.parse_args()
    out = a.out or a.board
    b = K.LoadBoard(a.board)
    r = K.LoadBoard(a.routed)

    by_full = {str(n): ni for n, ni in b.GetNetsByName().items()}
    by_short = {M.short(str(n)): ni for n, ni in b.GetNetsByName().items()}

    def target(name):
        s = M.short(name)
        if s.endswith(TWIN):
            s = s[:-len(TWIN)]
            return by_short.get(s)
        return by_full.get(name) or by_short.get(s)

    have = {key(t, M.short(t.GetNetname()), b) for t in b.GetTracks()}
    added, unmatched, seen = Counter(), Counter(), set()
    for t in r.GetTracks():
        ni = target(t.GetNetname())
        if ni is None:
            unmatched[t.GetNetname()] += 1
            continue
        k = key(t, M.short(ni.GetNetname()), r)
        seen.add(k)
        if k in have:
            continue
        if t.Type() == K.PCB_VIA_T:
            n = K.PCB_VIA(b)
            n.SetPosition(t.GetPosition())
            n.SetViaType(t.GetViaType())
            n.SetLayerPair(K.F_Cu, K.B_Cu)
            n.SetWidth(t.GetWidth(K.F_Cu))
            n.SetDrill(t.GetDrillValue())
            kind = 'vias'
        elif t.Type() == K.PCB_ARC_T:
            n = K.PCB_ARC(b)
            n.SetStart(t.GetStart()); n.SetMid(t.GetMid()); n.SetEnd(t.GetEnd())
            n.SetWidth(t.GetWidth()); n.SetLayer(b.GetLayerID(r.GetLayerName(t.GetLayer())))
            kind = 'arcs'
        else:
            n = K.PCB_TRACK(b)
            n.SetStart(t.GetStart()); n.SetEnd(t.GetEnd())
            n.SetWidth(t.GetWidth()); n.SetLayer(b.GetLayerID(r.GetLayerName(t.GetLayer())))
            kind = 'tracks'
        n.SetNet(ni)
        n.SetLocked(False)
        b.Add(n)
        have.add(k)
        added[kind] += 1
    # the board's own copper the trial doesn't have (the router doesn't move locked copper, so this should be none)
    missing = [k for k in (key(t, M.short(t.GetNetname()), b) for t in b.GetTracks()) if k not in seen]
    K.SaveBoard(out, b)
    print(f'kept from {a.routed}: {dict(added)}')
    print(f'unmatched nets (copper left behind): {dict(unmatched) or "none"}')
    print(f'board copper the trial lacked (kept as it was): {len(missing)}')
    rc = subprocess.run([sys.executable, str(HERE / 'refill.py'), out]).returncode
    print(f'wrote {out}; refill rc {rc}')
    sys.exit(rc)


if __name__ == '__main__':
    main()
