"""Silkscreen pass after placement (D-22Nov.9): each visible reference moves, if it must, to the nearest spot
that clears every pad, every courtyard of another part, every other silk item and the board edge.
Boxes are axis-aligned bounding boxes, so the test errs on the side of more room. Board-local mm."""
import math
import pcbnew as K

TOMM, MM = K.ToMM, K.FromMM


def _box(bb, ox, oy, grow=0.0):
    return (TOMM(bb.GetX()) - ox - grow, TOMM(bb.GetY()) - oy - grow,
            TOMM(bb.GetRight()) - ox + grow, TOMM(bb.GetBottom()) - oy + grow)


def _hit(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def silk_pass(board, origin, size, clearance=0.15, edge=0.3, reach=3.0, step=0.25):
    """Returns (moved {ref: (dx, dy)}, stuck [ref]): refs that had to move, and refs with no clear spot."""
    ox, oy = origin
    W, H = size
    fps = list(board.GetFootprints())
    pads, crts, silk, labels = [], {}, [], {}
    for fp in fps:
        ref = fp.GetReference()
        for p in fp.Pads():
            pads.append((ref, _box(p.GetBoundingBox(), ox, oy)))
        fp.BuildCourtyardCaches()
        cy = fp.GetCourtyard(K.F_CrtYd)
        if cy.OutlineCount():
            crts[ref] = _box(cy.BBox(), ox, oy)
        for g in fp.GraphicalItems():
            if g.GetLayer() == K.F_SilkS and (g.GetClass() != 'PCB_TEXT' or g.IsVisible()):
                silk.append((ref, _box(g.GetBoundingBox(), ox, oy)))
        f = fp.Reference()
        if f.IsVisible() and f.GetLayer() == K.F_SilkS:
            labels[ref] = (fp, f)
        for f2 in fp.GetFields():                      # other visible silk fields (the ref itself is the mover)
            if f2.GetName() != 'Reference' and f2.IsVisible() and f2.GetLayer() == K.F_SilkS:
                silk.append((ref, _box(f2.GetBoundingBox(), ox, oy)))
    placed = {r: _box(f.GetBoundingBox(), ox, oy) for r, (fp, f) in labels.items()}

    def clear(ref, box):
        g = (box[0] - clearance, box[1] - clearance, box[2] + clearance, box[3] + clearance)
        if g[0] < edge or g[1] < edge or g[2] > W - edge or g[3] > H - edge:
            return False
        if any(_hit(g, b) for _, b in pads):
            return False
        if any(r != ref and _hit(box, b) for r, b in crts.items()):
            return False
        if any(_hit(g, b) for _, b in silk):
            return False
        return not any(r != ref and _hit(g, b) for r, b in placed.items())

    moved, stuck = {}, []
    for ref in sorted(labels):
        fp, f = labels[ref]
        box = placed[ref]
        if clear(ref, box):
            continue
        best = None
        w, h = box[2] - box[0], box[3] - box[1]
        cands = []
        c = crts.get(ref)
        if c:                                          # first: just outside its own courtyard, the side facing
            cx, cy = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2  # the board centre first, sliding along that side
            sides = {'up': (cx - w / 2, c[1] - 0.2 - h), 'down': (cx - w / 2, c[3] + 0.2),
                     'left': (c[0] - 0.2 - w, cy - h / 2), 'right': (c[2] + 0.2, cy - h / 2)}
            pref = sorted(sides, key=lambda s: math.hypot(sides[s][0] + w / 2 - W / 2, sides[s][1] + h / 2 - H / 2))
            for s in pref:
                x0, y0 = sides[s]
                for k in (0, 1, -1, 2, -2, 3, -3, 4, -4):
                    sx, sy = (k * 0.5, 0) if s in ('up', 'down') else (0, k * 0.5)
                    cands.append((x0 + sx - box[0], y0 + sy - box[1]))
        for k in range(1, int(reach / step) + 1):      # then: a ring search around where it is
            d = k * step
            for a in range(0, 360, 45):
                cands.append((round(d * math.cos(math.radians(a)), 3), round(-d * math.sin(math.radians(a)), 3)))
        for dx, dy in cands:
            cand = (box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy)
            if clear(ref, cand):
                best = (round(dx, 3), round(dy, 3), cand)
                break
        if best is None:
            stuck.append(ref)
            continue
        dx, dy, cand = best
        pos = f.GetPosition()
        f.SetPosition(K.VECTOR2I(pos.x + MM(dx), pos.y + MM(dy)))
        placed[ref] = cand
        moved[ref] = (dx, dy)
    return moved, stuck

