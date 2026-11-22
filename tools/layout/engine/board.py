"""Board construction with the pcbnew SWIG module (KiCad 9.0.8): outline, board-only footprints,
rule areas, parts from the netlist. Coordinates are board-local mm; `B.origin` offsets them on the page."""
import pcbnew as K

MM, TOMM = K.FromMM, K.ToMM


class Board:
    def __init__(self, path, origin, copper=4, thickness=1.6):
        self.b = K.NewBoard(path)
        self.b.SetCopperLayerCount(copper)
        self.b.GetDesignSettings().SetBoardThickness(MM(thickness))
        self.ox, self.oy = origin
        self.netinfo = {}

    def V(self, x, y):
        return K.VECTOR2I(MM(self.ox + x), MM(self.oy + y))

    def outline(self, w, h, width=0.05):
        pts = [(0, 0), (w, 0), (w, h), (0, h)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
            s = K.PCB_SHAPE(self.b)
            s.SetShape(K.SHAPE_T_SEGMENT)
            s.SetStart(self.V(ax, ay)); s.SetEnd(self.V(bx, by))
            s.SetLayer(K.Edge_Cuts); s.SetWidth(MM(width))
            self.b.Add(s)

    def board_only(self, libroot, fid, ref, x, y, rot=0, value=''):
        """A footprint that isn't in the schematic (hole, fiducial): board-only, out of BOM and CPL."""
        lib, name = fid.split(':', 1)
        fp = K.FootprintLoad(f'{libroot}/{lib}.pretty', name)
        assert fp is not None, fid
        fp.SetFPID(K.LIB_ID(lib, name))
        fp.SetReference(ref); fp.SetValue(value or name)
        fp.SetBoardOnly(True); fp.SetExcludedFromBOM(True); fp.SetExcludedFromPosFiles(True)
        fp.SetOrientationDegrees(rot); fp.SetPosition(self.V(x, y))
        fp.Reference().SetVisible(False)
        self.b.Add(fp)
        return fp

    def rule_area(self, name, poly, layers, tracks=True, vias=True, pads=True, pours=True, footprints=False):
        z = K.ZONE(self.b)
        z.SetIsRuleArea(True)
        z.SetZoneName(name)
        ls = K.LSET()
        for l in layers:
            ls.AddLayer(l)
        z.SetLayerSet(ls)
        z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowVias(vias); z.SetDoNotAllowPads(pads)
        z.SetDoNotAllowCopperPour(pours); z.SetDoNotAllowFootprints(footprints)
        o = z.Outline(); o.NewOutline()
        for x, y in poly:
            p = self.V(x, y)
            o.Append(p.x, p.y)
        self.b.Add(z)
        return z

    def note_rect(self, box, text, layer=K.Dwgs_User):
        x0, y0, x1, y1 = box
        r = K.PCB_SHAPE(self.b)
        r.SetShape(K.SHAPE_T_RECT)
        r.SetStart(self.V(x0, y0)); r.SetEnd(self.V(x1, y1))
        r.SetLayer(layer); r.SetWidth(MM(0.1))
        self.b.Add(r)
        t = K.PCB_TEXT(self.b)
        t.SetText(text); t.SetLayer(layer)
        t.SetPosition(self.V((x0 + x1) / 2, (y0 + y1) / 2))
        t.SetTextSize(K.VECTOR2I(MM(1.0), MM(1.0)))
        self.b.Add(t)

    def nets(self, names):
        for name in sorted(names):
            ni = K.NETINFO_ITEM(self.b, name)
            self.b.Add(ni)
            self.netinfo[name] = ni

    def parts(self, comps, nets, libroot):
        """Every netlist part with a footprint: UUID path, value, fields, DNP and pad nets. Returns {ref: fp}, missing."""
        pin_net = {(r, p): n for n, nodes in nets.items() for r, p in nodes}
        fps, missing = {}, []
        for ref in sorted(comps):
            c = comps[ref]
            if not c.fp:
                missing.append(ref)
                continue
            lib, name = c.fp.split(':', 1)
            fp = K.FootprintLoad(f'{libroot}/{lib}.pretty', name)
            if fp is None:
                missing.append(ref)
                continue
            fp.SetFPID(K.LIB_ID(lib, name))
            fp.SetReference(ref)
            fp.SetValue(c.value)
            fp.SetPath(K.KIID_PATH(c.path))
            for k in ('MPN', 'Manufacturer', 'LCSC'):
                if c.fields.get(k):
                    fp.SetField(k, c.fields[k])
                    f = fp.GetFieldByName(k)               # data, not silkscreen: hidden, on F.Fab
                    f.SetVisible(False)
                    f.SetLayer(K.F_Fab)
            fp.SetDNP(bool(c.dnp))                         # attributes follow the symbol, so parity holds
            fp.SetExcludedFromBOM(bool(c.exclude_bom))
            for pad in fp.Pads():
                n = pin_net.get((ref, pad.GetNumber()))
                if n:
                    pad.SetNet(self.netinfo[n])
            self.b.Add(fp)
            fps[ref] = fp
        return fps, missing

    def silk_policy(self, fps, labelled, names=None):
        """Refs on the silkscreen only where someone uses them on the board (D-22Nov.9): `labelled(ref, fp)`.
        Every other ref goes to the assembly drawing only (F.Fab): hidden if the footprint already prints
        ${REFERENCE} there, else moved there, centred and small. Run before placement (parts at the origin).
        names: {ref: (text, (dx, dy), angle)}: a function name replaces the ref on the silk (D-22Nov.19), put
        just outside the courtyard on the footprint's local side (dx, dy) at the local text angle given."""
        names = names or {}
        for ref, fp in fps.items():
            pads = [p.GetBoundingBox() for p in fp.Pads()]
            for g in fp.GraphicalItems():              # silk text (pin-1 marks) at JLC's 1.0 mm minimum height,
                if g.GetClass() == 'PCB_TEXT' and g.GetLayer() == K.F_SilkS and g.GetTextHeight() < MM(1.0):
                    g.SetTextSize(K.VECTOR2I(MM(1.0), MM(1.0)))   # moved outward until it clears its pads
                    g.SetTextThickness(MM(0.15))
                    for _ in range(30):
                        tb = g.GetBoundingBox()
                        tb.Inflate(MM(0.2))
                        hit = [b for b in pads if tb.Intersects(b)]
                        if not hit:
                            break
                        c, q = hit[0].GetCenter(), g.GetPosition()
                        vx, vy = q.x - c.x, q.y - c.y
                        n = max(1.0, (vx * vx + vy * vy) ** 0.5)
                        g.SetPosition(K.VECTOR2I(int(q.x + vx / n * MM(0.1)), int(q.y + vy / n * MM(0.1))))
            f = fp.Reference()
            if ref in names:
                self._name_label(fp, *names[ref])
            elif labelled(ref, fp):
                f.SetVisible(True)
                f.SetLayer(K.F_SilkS)
                if not ref.startswith('TP'):           # outside its own courtyard and silk, above, centred
                    fp.BuildCourtyardCaches()
                    cy = fp.GetCourtyard(K.F_CrtYd)
                    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False, False)
                    for g in fp.GraphicalItems():
                        if g.GetLayer() == K.F_SilkS:
                            bb.Merge(g.GetBoundingBox())
                    f.SetTextAngleDegrees(0)
                    h = f.GetBoundingBox().GetHeight()
                    f.SetPosition(K.VECTOR2I(bb.GetCenter().x, bb.GetTop() - MM(0.2) - h // 2))
                continue
            fab = [g for g in fp.GraphicalItems() if g.GetClass() == 'PCB_TEXT' and g.GetLayer() == K.F_Fab
                   and '${REFERENCE}' in g.GetText()]
            if fab:
                f.SetVisible(False)
            else:
                f.SetLayer(K.F_Fab)
                f.SetPosition(fp.GetPosition())
                f.SetTextSize(K.VECTOR2I(MM(0.5), MM(0.5)))
                f.SetTextThickness(MM(0.08))

    def _name_label(self, fp, text, side, angle, size=1.0, gap=0.25):
        fp.BuildCourtyardCaches()
        cy = fp.GetCourtyard(K.F_CrtYd)
        bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False, False)
        for g in fp.GraphicalItems():
            if g.GetLayer() == K.F_SilkS:
                bb.Merge(g.GetBoundingBox())
        t = K.PCB_TEXT(fp)
        t.SetText(text)
        t.SetLayer(K.F_SilkS)
        t.SetTextSize(K.VECTOR2I(MM(size), MM(size)))
        t.SetTextThickness(MM(0.15))
        t.SetTextAngleDegrees(angle)
        t.SetPosition(bb.GetCenter())
        fp.Add(t)
        tb = t.GetBoundingBox()
        hw, hh = tb.GetWidth() // 2, tb.GetHeight() // 2
        c = bb.GetCenter()
        dx, dy = side
        x = c.x if not dx else (bb.GetRight() + MM(gap) + hw if dx > 0 else bb.GetLeft() - MM(gap) - hw)
        y = c.y if not dy else (bb.GetBottom() + MM(gap) + hh if dy > 0 else bb.GetTop() - MM(gap) - hh)
        t.SetPosition(K.VECTOR2I(int(x), int(y)))
        r = fp.Reference()                                 # the ref goes to the assembly drawing
        fab = [g for g in fp.GraphicalItems() if g.GetClass() == 'PCB_TEXT' and g.GetLayer() == K.F_Fab and '${REFERENCE}' in g.GetText()]
        if fab:
            r.SetVisible(False)
        else:
            r.SetLayer(K.F_Fab)
            r.SetPosition(fp.GetPosition())
            r.SetTextSize(K.VECTOR2I(MM(0.5), MM(0.5)))
            r.SetTextThickness(MM(0.08))

    def save(self, path):
        K.SaveBoard(path, self.b)


def circle(cx, cy, d, n=32):
    import math
    r = d / 2
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
