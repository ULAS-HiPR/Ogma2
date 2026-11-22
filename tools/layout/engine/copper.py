"""Stage C (S4): the copper the router never touches, drawn by script after placement (execution brief, stage C;
stage C and D handoff). Everything here is deterministic and locked, and it is rebuilt from the spec and the
placement on every build, so the board stays the output of scripts (D-21Nov.21).

Board-local mm, y down, as the rest of the engine. Each step takes the Board wrapper, the spec and the placed
footprints, adds its items and returns a short report for build.json.
"""
import pcbnew as K

MM, TOMM = K.FromMM, K.ToMM


def courtyard_poly(fp, origin):
    """A footprint's front courtyard as a list of board-local (x, y) points."""
    fp.BuildCourtyardCaches()
    cy = fp.GetCourtyard(K.F_CrtYd)
    if not cy.OutlineCount():
        bb = fp.GetBoundingBox(False, False)
        x0, y0, x1, y1 = TOMM(bb.GetX()), TOMM(bb.GetY()), TOMM(bb.GetRight()), TOMM(bb.GetBottom())
        return [(x0 - origin[0], y0 - origin[1]), (x1 - origin[0], y0 - origin[1]),
                (x1 - origin[0], y1 - origin[1]), (x0 - origin[0], y1 - origin[1])]
    o = cy.Outline(0)
    return [(TOMM(o.CPoint(i).x) - origin[0], TOMM(o.CPoint(i).y) - origin[1]) for i in range(o.PointCount())]


def escape_areas(bd, spec, fps):
    """Named rule areas with no restrictions of their own, for the custom rules to test against: the fire-logic
    waiver inside U201's courtyard (D-22Nov.26) reads `A.enclosedByArea('U201_ESCAPE')`."""
    out = {}
    for ref in getattr(spec, 'ESCAPE_AREAS', ()):
        poly = courtyard_poly(fps[ref], spec.ORIGIN)
        bd.rule_area(f'{ref}_ESCAPE', poly, list(bd.b.GetEnabledLayers().CuStack()),
                     tracks=False, vias=False, pads=False, pours=False)
        out[ref] = [[round(x, 3), round(y, 3)] for x, y in poly]
    return out
