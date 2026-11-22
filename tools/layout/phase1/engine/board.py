"""Build a KiCad board from netlist data with the pcbnew SWIG module (KiCad 9)."""
import pcbnew as K

MM = K.FromMM


def V(x, y):
    return K.VECTOR2I(MM(x), MM(y))


def new_board(path, copper=4, thickness=1.6):
    b = K.NewBoard(path)
    b.SetCopperLayerCount(copper)
    b.GetDesignSettings().SetBoardThickness(MM(thickness))
    return b


def outline(b, x0, y0, w, h, width=0.05):
    pts = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
        s = K.PCB_SHAPE(b)
        s.SetShape(K.SHAPE_T_SEGMENT)
        s.SetStart(V(ax, ay)); s.SetEnd(V(bx, by))
        s.SetLayer(K.Edge_Cuts); s.SetWidth(MM(width))
        b.Add(s)


def add_parts(b, comps, nets, libroot):
    """Footprints from <libroot>/<Lib>.pretty, with UUID paths, values, DNP and pad nets."""
    netinfo = {}
    for name in sorted(nets):
        ni = K.NETINFO_ITEM(b, name)
        b.Add(ni)
        netinfo[name] = ni
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
        if c.dnp:
            fp.SetDNP(True); fp.SetExcludedFromBOM(True); fp.SetExcludedFromPosFiles(True)
        if c.exclude_bom:
            fp.SetExcludedFromBOM(True)
        for pad in fp.Pads():
            n = pin_net.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(netinfo[n])
        b.Add(fp)
        fps[ref] = fp
    return fps, netinfo, missing


def track(b, net, pts, width, layer=K.F_Cu):
    out = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        t = K.PCB_TRACK(b)
        t.SetStart(V(ax, ay)); t.SetEnd(V(bx, by))
        t.SetWidth(MM(width)); t.SetLayer(layer); t.SetNet(net)
        b.Add(t); out.append(t)
    return out


def via(b, net, x, y, drill=0.3, diameter=0.6):
    v = K.PCB_VIA(b)
    v.SetPosition(V(x, y)); v.SetDrill(MM(drill)); v.SetWidth(MM(diameter))
    v.SetViaType(K.VIATYPE_THROUGH); v.SetNet(net)
    b.Add(v)
    return v


def zone(b, net, layer, poly, clearance=0.2, min_width=0.2, priority=0, name=''):
    z = K.ZONE(b)
    z.SetLayer(layer); z.SetNet(net)
    z.SetLocalClearance(MM(clearance)); z.SetMinThickness(MM(min_width))
    z.SetAssignedPriority(priority)
    if name:
        z.SetZoneName(name)
    o = z.Outline(); o.NewOutline()
    for x, y in poly:
        o.Append(MM(x), MM(y))
    z.SetPadConnection(K.ZONE_CONNECTION_THERMAL)
    b.Add(z)
    return z


def fill(b):
    K.ZONE_FILLER(b).Fill(b.Zones())
