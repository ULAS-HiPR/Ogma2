"""Draw the 3D models KiCad's library doesn't have for Burrito's parts, with CadQuery (22 Nov 2026).

    python3 tools/layout/models3d.py [part]   # writes hardware/croi2/libraries/3d/<lib>.3dshapes/<name>.step
                                              # (all, or the outputs whose path contains `part`)

Each model is a simplified body at the maker's size: XY from the footprint's F.Fab outline (itself from the
maker's drawing), height and features from the cited datasheet. They're for the 3D view and the fit check,
not for tooling. Coordinates follow KiCad: model origin = footprint origin, +y of the model = -y of the
footprint, z up from the board's top face. The basis of every model is in libraries/3d/GENERATED.md.
"""
import math
import sys
from pathlib import Path
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / 'hardware' / 'croi2' / 'libraries'
OUT = LIB / '3d'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import sexpr as S                         # noqa: E402

C = {'orange': (1.0, 0.42, 0.08), 'black': (0.08, 0.08, 0.09), 'ivory': (0.93, 0.90, 0.80),
     'tin': (0.80, 0.80, 0.82), 'gold': (0.86, 0.70, 0.30), 'pcb': (0.08, 0.32, 0.18), 'grey': (0.35, 0.35, 0.38),
     'white': (0.95, 0.95, 0.93), 'yellow': (0.98, 0.82, 0.10)}


def fp_info(rel):
    t = S.parse((LIB / rel).read_text())
    xs, ys = [], []
    for kind in ('fp_line', 'fp_rect', 'fp_circle', 'fp_poly', 'fp_arc'):
        for g in S.children(t, kind):
            lay = S.first(g, 'layer')
            if lay and lay[1] == 'F.Fab':
                for tag in ('start', 'end', 'mid'):
                    n = S.first(g, tag)
                    if n:
                        xs.append(float(n[1])); ys.append(float(n[2]))
                pts = S.first(g, 'pts')
                for xy in (S.children(pts, 'xy') if pts else []):
                    xs.append(float(xy[1])); ys.append(float(xy[2]))
    pads = []
    for p in S.children(t, 'pad'):
        at, size = S.first(p, 'at'), S.first(p, 'size')
        pads.append((p[1], p[2], float(at[1]), float(at[2]), float(size[1]), float(size[2])))
    return (min(xs), min(ys), max(xs), max(ys)), pads


def box(x0, y0, x1, y1, z0, z1):
    """A box from footprint coordinates (y down) to model coordinates (y up)."""
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, -y1, z0))


def save(assy, rel):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    assy.save(str(path), exportType='STEP')
    return path


def loop(name, body_d, body_h, top, wire, color, pin_len=3.0):
    """Keystone PC test point: insulator cylinder, a wire loop above it, one pin below."""
    a = cq.Assembly(name=name)
    a.add(cq.Workplane('XY').circle(body_d / 2).extrude(body_h), name='body', color=cq.Color(*C[color]))
    r = (top - body_h - wire) / 2                       # the loop: a half ring on two legs, in the XZ plane
    w = max(r, body_d * 0.28)
    path = (cq.Workplane('XZ').moveTo(-w, body_h * 0.6).lineTo(-w, top - w - wire / 2)
            .threePointArc((0, top - wire / 2), (w, top - w - wire / 2)).lineTo(w, body_h * 0.6))
    ring = cq.Workplane('YZ').workplane(offset=-w).center(0, body_h * 0.6).circle(wire / 2).sweep(path)
    a.add(ring, name='loop', color=cq.Color(*C['tin']))
    a.add(cq.Workplane('XY').circle(wire / 2).extrude(-pin_len), name='pin', color=cq.Color(*C['tin']))
    return a


def smt_loop(name, base_w, base_d, base_h, top, strip_w, strip_t, color):
    """Keystone colour-keyed SMT test point: an LCP base, and a phosphor-bronze strip arched over it in the XZ
    plane, its feet on the pad."""
    a = cq.Assembly(name=name)
    a.add(box(-base_w / 2, -base_d / 2, base_w / 2, base_d / 2, 0.0, base_h), name='base', color=cq.Color(*C[color]))
    w2, s2 = base_w / 2, strip_w / 2
    for nm, (x0, x1, z0, z1) in (('leg_l', (-w2, -w2 + strip_t, 0.0, top)), ('leg_r', (w2 - strip_t, w2, 0.0, top)),
                                 ('top', (-w2, w2, top - strip_t, top))):
        a.add(box(x0, -s2, x1, s2, z0, z1), name=nm, color=cq.Color(*C['tin']))
    return a


def shroud(name, rel, h, wall, color, post, post_h, tht=True, floor=1.0):
    """A shrouded header: the F.Fab outline as a box with a cavity, a square post at each contact."""
    (x0, y0, x1, y1), pads = fp_info(rel)
    body = box(x0, y0, x1, y1, 0, h).cut(box(x0 + wall, y0 + wall, x1 - wall, y1 - wall, floor, h + 1))
    a = cq.Assembly(name=name)
    a.add(body, name='body', color=cq.Color(*C[color]))
    for num, kind, x, y, sx, sy in pads:
        if not num or (tht and kind != 'thru_hole'):
            continue
        z0 = -3.2 if kind == 'thru_hole' else 0.0
        a.add(cq.Workplane('XY').box(post, post, post_h - z0, centered=(True, True, False)).translate((x, -y, z0)),
              name=f'pin{num}_{x}_{y}', color=cq.Color(*C['gold']))
        if kind == 'smd':
            a.add(box(x - sx / 2 + 0.05, y - sy / 2 + 0.05, x + sx / 2 - 0.05, y + sy / 2 - 0.05, 0, 0.15),
                  name=f'tail{num}_{x}_{y}', color=cq.Color(*C['gold']))
    return a


def plain(name, rel, h, color, cap=None, hole=None, pcb=None):
    """A block over the F.Fab outline; options: metal end caps (fuse), a sound hole, a PCB base (module)."""
    (x0, y0, x1, y1), pads = fp_info(rel)
    a = cq.Assembly(name=name)
    if cap:                                             # NANO2: ceramic body between two tinned caps
        a.add(box(x0 + cap, y0, x1 - cap, y1, 0, h), name='body', color=cq.Color(*C[color]))
        a.add(box(x0, y0, x0 + cap, y1, 0, h), name='cap1', color=cq.Color(*C['tin']))
        a.add(box(x1 - cap, y0, x1, y1, 0, h), name='cap2', color=cq.Color(*C['tin']))
        return a
    z = 0.0
    if pcb:                                             # module: green PCB, then a tinned shield can
        a.add(box(x0, y0, x1, y1, 0, pcb), name='pcb', color=cq.Color(*C['pcb']))
        z = pcb
    b = box(x0 + (0.2 if pcb else 0), y0 + (0.2 if pcb else 0), x1 - (0.2 if pcb else 0), y1 - (0.2 if pcb else 0), z, h)
    if hole:
        b = b.cut(cq.Workplane('XY').circle(hole / 2).extrude(h + 1).translate(((x0 + x1) / 2, -(y0 + y1) / 2, h - 0.4)))
    a.add(b, name='body', color=cq.Color(*C[color]))
    return a


def mpt(name, rel, h):
    """Samtec MPT right-angle power header: a body with eight square openings on its mating face (beyond the
    board edge, aft), and screw-down ears on the board round the footprint's two NPTH holes."""
    (x0, y0, x1, y1), pads = fp_info(rel)
    body = box(x0 + 7.86, y0, x1 - 7.86, y1, 0, h)     # the screw-down ears are lower and flatter
    pitch, n = 5.0, 8
    for i in range(n):
        cx = (i - (n - 1) / 2) * pitch
        body = body.cut(box(cx - 1.7, y1 - 6.0, cx + 1.7, y1 + 1, 1.0, h - 1.0))
    a = cq.Assembly(name=name)
    a.add(body, name='body', color=cq.Color(*C['black']))
    holes = [(x, y) for num, kind, x, y, sx, sy in pads if kind == 'np_thru_hole']
    for side in (x0, x1 - 7.86):                        # screw-down ears, on the board, round the NPTH holes
        ear = box(side, y0, side + 7.86, -3.6, 0, 1.6)
        for hx, hy in holes:
            if side <= hx <= side + 7.86:
                ear = ear.cut(cq.Workplane('XY').circle(1.78).extrude(3).translate((hx, -hy, -0.5)))
        a.add(ear, name=f'ear{side}', color=cq.Color(*C['black']))
    for num, kind, x, y, sx, sy in pads:
        if kind == 'thru_hole':
            a.add(cq.Workplane('XY').box(0.64, 0.64, 3.2, centered=(True, True, False)).translate((x, -y, -3.2)),
                  name=f'tail{num}_{x}_{y}', color=cq.Color(*C['gold']))
    return a


def nanofit(name, rel, h, latch_h, depth, length, latch_depth, latch_len, tail=3.2):
    """Molex Nano-Fit vertical header with solder clips: a shroud on the pin row, the latch as a solid envelope
    on its side (-x), posts at the pins, tin clips at the clip holes. Sizes from the footprint's maker drawing."""
    (_, _, _, _), pads = fp_info(rel)
    pins = [(x, y) for num, kind, x, y, sx, sy in pads if kind == 'thru_hole' and num not in ('', 'MP')]
    clips = [(x, y) for num, kind, x, y, sx, sy in pads if num == 'MP']
    cy = sum(y for _, y in pins) / len(pins)
    y0, y1 = cy - length / 2, cy + length / 2
    body = box(-depth / 2, y0, depth / 2, y1, 0, h).cut(box(-depth / 2 + 0.5, y0 + 0.5, depth / 2 - 0.5, y1 - 0.5, 1.0, h + 1))
    a = cq.Assembly(name=name)
    a.add(body, name='body', color=cq.Color(*C['black']))
    a.add(box(-depth / 2 - latch_depth, cy - latch_len / 2, -depth / 2, cy + latch_len / 2, 0, latch_h),
          name='latch', color=cq.Color(*C['black']))
    for x, y in pins:
        a.add(cq.Workplane('XY').box(0.64, 0.64, h - 2.0 + tail, centered=(True, True, False)).translate((x, -y, -tail)),
              name=f'pin_{x}_{y}', color=cq.Color(*C['tin']))
    for x, y in clips:
        a.add(box(x - 0.2, y - 0.6, x + 0.2, y + 0.6, -1.6, 1.0), name=f'clip_{x}_{y}', color=cq.Color(*C['tin']))
    return a


MODELS = [
    # (output, builder, args)
    ('TestPoint.3dshapes/TestPoint_Keystone_5000-5004_Miniature.step', loop,
     dict(name='Keystone5003', body_d=2.5, body_h=1.6, top=4.6, wire=0.5, color='orange')),
    ('TestPoint.3dshapes/TestPoint_Keystone_5190TR_ColorKeyed.step', smt_loop,
     dict(name='Keystone5194TR', base_w=3.0, base_d=2.4, base_h=1.2, top=2.5, strip_w=1.2, strip_t=0.2, color='yellow')),
    ('TestPoint.3dshapes/TestPoint_Keystone_5010-5014_Multipurpose.step', loop,
     dict(name='Keystone5011', body_d=3.2, body_h=2.8, top=8.1, wire=0.8, color='black')),
    ('Connector_JST.3dshapes/JST_VH_B2P-VH_1x02_P3.96mm_Vertical.step', shroud,
     dict(name='JST_B2P-VH', rel='Connector_JST.pretty/JST_VH_B2P-VH_1x02_P3.96mm_Vertical.kicad_mod',
          h=9.4, wall=0.9, color='ivory', post=1.14, post_h=8.5)),
    ('Connector_Molex.3dshapes/Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical.step', shroud,
     dict(name='Molex_39281023', rel='Connector_Molex.pretty/Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical.kicad_mod',
          h=9.4, wall=1.0, color='ivory', post=0.64, post_h=7.6)),
    ('Connector_Harwin.3dshapes/Harwin_Gecko_G125-MS10605M2P_2x03_P1.25mm_Vertical.step', shroud,
     dict(name='Harwin_G125-MS10605M2P', rel='Ogma2.pretty/G125-MS10605M2P.kicad_mod',
          h=4.6, wall=0.6, color='black', post=0.4, post_h=3.6, tht=False, floor=0.8)),
    ('Fuse.3dshapes/Fuse_Littelfuse-NANO2-451_453.step', plain,
     dict(name='Littelfuse_NANO2', rel='Fuse.pretty/Fuse_Littelfuse-NANO2-451_453.kicad_mod', h=2.69, color='white', cap=0.9)),
    ('Buzzer_Beeper.3dshapes/MagneticBuzzer_PUI_SMT-1028-T-2-R.step', plain,
     dict(name='PUI_SMT-1028-T-2-R', rel='Buzzer_Beeper.pretty/MagneticBuzzer_PUI_SMT-1028-T-2-R.kicad_mod',
          h=3.5, color='black', hole=2.0)),
    ('RF_GPS.3dshapes/ublox_MAX-M10S.step', plain,
     dict(name='ublox_MAX-M10S', rel='Ogma2_GNSS.pretty/MAX-M10S-00B.kicad_mod', h=2.5, color='tin', pcb=0.8)),
    ('Package_DFN_QFN.3dshapes/Texas_RDH0030A_TPSM63603.step', plain,
     dict(name='TPSM63603RDH', rel='Ogma2.pretty/TPSM63603RDHR.kicad_mod', h=1.9, color='black')),
    ('Connector_Samtec.3dshapes/Samtec_MPT-08-01-01-L-RA-SD.step', mpt,
     dict(name='Samtec_MPT-08-01-01-L-RA-SD', rel='Ogma2.pretty/MPT-08-01-01-L-RA-SD.kicad_mod', h=6.28)),
    ('Connector_Molex.3dshapes/Molex_Micro-Fit_3.0_43650-0215_1x02_P3.00mm_Vertical.step', shroud,
     dict(name='Molex_43650-0215', rel='Connector_Molex.pretty/Molex_Micro-Fit_3.0_43650-0215_1x02_P3.00mm_Vertical.kicad_mod',
          h=9.9, wall=0.8, color='black', post=0.64, post_h=7.0)),
    ('Connector_Molex.3dshapes/Molex_Nano-Fit_105311-1102_1x02_P2.50mm_Vertical.step', nanofit,
     dict(name='Molex_105311-1102', rel='Ogma2.pretty/105311-1102.kicad_mod', h=9.06, latch_h=10.51,
          depth=3.48, length=5.94, latch_depth=6.34 - 3.48, latch_len=5.20)),
]

if __name__ == '__main__':
    only = sys.argv[1:]                                  # optional: substrings of the outputs to redo
    for rel, fn, kw in MODELS:
        if not only or any(o in rel for o in only):
            print(save(fn(**kw), rel).relative_to(ROOT))
