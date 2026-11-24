"""Burrito (Croí2) board spec: data for tools/layout/build.py. Every value cites its decision or is
marked [J] (judgement, from the routing brief, docs/briefs/layout-brief.md, D-22Nov.3).

Board-local coordinates in mm, seen from the top with the forward end up: x across (0-80), y along
(0 = forward edge). The y values below are written for the 230 mm reference board; build.py's stretch()
maps them to LENGTH (D-22Nov.10): 12 mm at each end as written, each band in proportion to its parts'
area, edge connectors slid clear of the holes. Rotations are KiCad's (counter-clockwise on screen)."""

NAME = 'Croi2'
W, H = 80.0, 230.0                     # D-21Nov.6, B-35: the reference board the y values are written for
LENGTH = 160.0                         # D-22Nov.21: Burrito is 80 x 160 (Seán, 22 Nov: "Let's try get 80x160");
                                       # was 180 (D-22Nov.10)
ORIGIN = (100.0, 50.0)                 # page offset, as the 8 September draft
THICKNESS = 1.6

# --- holes, fiducials (D-21Nov.23; JLC rails-and-fiducials article, 9 Sep 2026)
HOLES = [(x, y) for y in (6.0, 79.0, 152.0, 225.0) for x in (4.0, 76.0)]
# D-22Nov.11: plated, with an exposed 6.4 mm GND ring both sides and eight stitching vias; the sled mounts
# Burrito on insulating standoffs or washers, so GND never bonds to it (IR-6)
HOLE_FP = 'MountingHole:MountingHole_3.2mm_M3_Pad_Via'
HOLE_NET = 'GND'
HOLE_TRACK_KEEPOUT_D = 8.0             # no track or via under the washer; pours and the ring allowed
HOLE_PART_KEEPOUT_D = 8.0
FIDUCIAL_FP = 'Fiducial:Fiducial_1mm_Mask2mm'
FIDUCIALS = [(6.0, 44.0), (74.0, 44.0), (12.0, 104.0)]    # [J] three, asymmetric, >= 3.35 mm from the edges; the third
                                                         # inboard of the left-edge connectors' column (stage B)

# --- stackup: JLC06161H-3313 (D-22Nov.29; JLC's quote page, 22 Nov 2026: its stackup table; it finishes 1.5384 mm, JLC's
# figure, within its +-10 % of the 1.6 mm ordered). Plan P1: L1 signals and parts, L2 GND, L3 signals, L4 GND, L5 power
# islands in GND fill, L6 signals. L1-L2 is the same 3313 prepreg as on four layers, so D-22Nov.2's widths stand.
COPPER_LAYERS = 6
STACKUP = [
    ('F.SilkS', 'Top Silk Screen', None, None, None),
    ('F.Paste', 'Top Solder Paste', None, None, None),
    ('F.Mask', 'Top Solder Mask', 0.01, None, None),
    ('F.Cu', 'copper', 0.035, None, None),
    ('dielectric 1', 'prepreg', 0.0994, 4.05, '3313'),
    ('In1.Cu', 'copper', 0.0152, None, None),
    ('dielectric 2', 'core', 0.55, 4.6, 'FR4'),
    ('In2.Cu', 'copper', 0.0152, None, None),
    ('dielectric 3', 'prepreg', 0.1088, 4.25, '2116'),
    ('In3.Cu', 'copper', 0.0152, None, None),
    ('dielectric 4', 'core', 0.55, 4.6, 'FR4'),
    ('In4.Cu', 'copper', 0.0152, None, None),
    ('dielectric 5', 'prepreg', 0.0994, 4.05, '3313'),
    ('B.Cu', 'copper', 0.035, None, None),
    ('B.Mask', 'Bottom Solder Mask', 0.01, None, None),
    ('B.Paste', 'Bottom Solder Paste', None, None, None),
    ('B.SilkS', 'Bottom Silk Screen', None, None, None),
]
ROUTER_LAYERS = ['F.Cu', 'In2.Cu', 'B.Cu']      # L1, L3, L6 (D-22Nov.29)
GND_LAYERS = ['In1.Cu', 'In3.Cu']               # L2, L4: never routed or cut
ISLAND_LAYER = 'In4.Cu'                         # L5: power islands in GND fill; no L6 track crosses an island edge

# --- JLC's multilayer capabilities: the board's rule set, with no margin of our own (D-23Nov.17). Read from
# jlcpcb.com/capabilities/pcb-capabilities and the order page, 23 Nov 2026 [J]. Fire copper's widths and gaps are
# current and safety decisions, not fab margin, and stay (D-23Nov.17).
JLC = dict(
    track=0.09, space=0.09,                 # 3.5 mil at 1 oz outer copper; 3 mil only in BGA fan-outs (none here)
    pad_to_track=0.1,                       # 0.09 locally at BGA pads (none here)
    smd_pad_to_pad=0.15,                    # different nets
    via_hole_to_hole=0.2, pth_hole_to_hole=0.45,
    via_hole_to_track=0.2, pth_to_track=0.28, npth_to_track=0.2,   # PTH: 0.35 recommended
    edge=0.2,                               # copper to a routed edge (0.4 to a V-cut)
    via_min=(0.25, 0.15),                   # diameter, hole: the capability; 0.1 / 0.2 only on boards up to 1 mm
    via_ring=0.05,                          # the diameter 0.1 mm over the hole (0.15 preferred)
    pth_ring=0.15,                          # 0.20 recommended at 1 oz
    mask_bridge=0.10,                       # green; 0.13 for black or white
    silk_line=0.15, silk_text=1.0, pad_to_silk=0.15,
)
# Which vias cost extra (order page): a hole under 0.3 mm with a diameter of 0.4 mm or less; on six layers a 0.45 mm
# via with a 0.2 mm hole doesn't. So the signal via is 0.45 / 0.2, the smallest that costs nothing (amends D-23Nov.4's
# 0.5 / 0.3). Price, not capability: a costlier via is legal; every via the scripts and the router make is a free size.
SIGNAL_VIA = (0.45, 0.2)

# --- net classes (brief section 5; widths from IPC-2152, impedances from JLC's calculator)
def nc(name, track, clearance, **kw):
    return dict(name=name, track_width=track, clearance=clearance, via_diameter=kw.get('via_d', 0.6),
                via_drill=kw.get('via_drill', 0.3), diff_pair_width=kw.get('dp_w', 0.2), diff_pair_gap=kw.get('dp_gap', 0.25),
                priority=kw.get('priority', 10))

NETCLASSES = [
    # JLC's track (0.09) at JLC's pad-to-track clearance (0.1): the router keeps one clearance per net, and a track's
    # nearest neighbour is mostly a pad, so 0.1 holds everywhere; 0.09 track to track stays the board's minimum
    nc('Default', JLC['track'], JLC['pad_to_track'], via_d=SIGNAL_VIA[0], via_drill=SIGNAL_VIA[1],
       priority=2147483647),                      # the free 0.45 / 0.2 via (D-23Nov.17)
    nc('SRC_6A', 4.0, 0.2, priority=1),
    nc('PYRO_RAIL', 2.0, 0.2, priority=2),        # 0.5 mm to other nets: custom rule below
    nc('FIRE', 1.0, 0.2, priority=3),
    nc('FIRE_LOGIC', 0.15, 0.2, priority=4),
    nc('LOGIC_FEED', 1.0, 0.2, priority=5),
    nc('RAIL_3V3', 0.4, JLC['pad_to_track'], via_d=SIGNAL_VIA[0], via_drill=SIGNAL_VIA[1], priority=6),   # width: current
    nc('RF50', 0.151, 0.203, priority=7),
    nc('USB_DIFF', 0.154, 0.2, dp_w=0.154, dp_gap=0.203, priority=8),
    nc('CAN_DIFF', 0.2, 0.2, dp_w=0.2, dp_gap=0.2, priority=9),
    nc('GND', 0.3, 0.2, priority=10),
]
RAILS = ['FLIGHT_3V3', 'COMMS_3V3', '3V3_OPTIONAL', '3V3_OPTIONAL_PRELINK', 'BOOT_3V3', 'CAN_3V3', 'NOR_3V3', 'NOR_3V3_PRELINK',
         'GNSS_3V3', 'LORA_3V3', 'FOINSE_AUX_3V3', 'FOINSE_AUX_3V3_PRELINK', 'BMP_3V3', 'HG_3V3', 'MAG_3V3', 'ST_3V3', 'TDK_3V3',
         'TE_3V3', 'CROI_MON_3V3', 'COMMS_3V3_PRELINK', 'FLIGHT_3V3_PRELINK', 'USB_VBUS', 'USB_LIMITED']
PATTERNS = ([('SRC_6A', n) for n in ('VBAT_CROI_INPUT', 'ENERGY_TAP')]
            + [('PYRO_RAIL', n) for n in ('*RECOVERY_ARM_FEED', '*STAGING_ARM_FEED', 'RECOVERY_ARMED_VBAT', 'STAGING_ARMED_VBAT')]
            + [('FIRE', f'{k}{i}{s}') for i in (1, 2, 3) for k, s in (('PYRO', '_ENERGY'), ('OUTPUT', '_HIGH'), ('OUTPUT', '_LOW'))]
            + [('FIRE_LOGIC', f'PYRO{i}{s}') for i in (1, 2, 3) for s in ('_GATE', '_FIRE', '_LS_SELECT')]
            + [('FIRE_LOGIC', n) for n in ('PYRO3_HS_ENABLE', 'STAGE_ELIGIBLE')]     # D-23Nov.10, D-23Nov.12
            + [('LOGIC_FEED', n) for n in ('VBAT_SHUNT_IN', 'VBAT_PROTECTED', 'LOGIC_SELECTED', '4V_PRE', 'CORE_HELD_4V')]
            + [('RAIL_3V3', n) for n in RAILS]
            + [('RF50', n) for n in ('GNSS_RF', 'LORA_RF_SUBG')]
            + [('USB_DIFF', n) for n in ('USB_DP', 'USB_DM', 'USB_DP_CONN', 'USB_DM_CONN')]
            + [('CAN_DIFF', n) for n in ('CAN_H', 'CAN_L', 'CAN2_H', 'CAN2_L')]
            + [('GND', 'GND')])

RULES = {  # the board's minimums: JLC's table as it stands (D-23Nov.17)
    'min_clearance': JLC['space'], 'min_track_width': JLC['track'], 'min_via_diameter': JLC['via_min'][0],
    'min_through_hole_diameter': JLC['via_min'][1], 'min_via_annular_width': JLC['via_ring'],
    'min_hole_clearance': JLC['via_hole_to_track'], 'min_hole_to_hole': JLC['via_hole_to_hole'],
    'min_copper_edge_clearance': JLC['edge'], 'min_text_height': JLC['silk_text'], 'min_text_thickness': JLC['silk_line'],
    'min_silk_clearance': JLC['pad_to_silk'],
}
DRU = '''(version 1)
# Burrito custom rules (D-22Nov.3; docs/briefs/layout-brief.md). Generated by tools/layout/build.py.
(rule "L2 is an unbroken GND plane: no track (D-22Nov.29)"
  (layer In1.Cu)
  (condition "A.Type == 'Track' || A.Type == 'Arc'")
  (constraint disallow track))
(rule "L4 is an unbroken GND plane: no track (D-22Nov.29)"
  (layer In3.Cu)
  (condition "A.Type == 'Track' || A.Type == 'Arc'")
  (constraint disallow track))
# JLC's minimums first: KiCad lets a later rule override an earlier one, so the fire rules below win where both apply
(rule "JLC: SMD pad to pad 0.15 mm, different nets (D-23Nov.17)"
  (condition "A.Type == 'Pad' && B.Type == 'Pad' && A.Net != B.Net")
  (constraint clearance (min 0.15mm)))
(rule "JLC: pad to track 0.1 mm (D-23Nov.17)"
  (condition "A.Type == 'Pad' && (B.Type == 'Track' || B.Type == 'Arc') && A.Net != B.Net")
  (constraint clearance (min 0.1mm)))
(rule "JLC: plated hole to track 0.28 mm (D-23Nov.17)"
  (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole' && (B.Type == 'Track' || B.Type == 'Arc')")
  (constraint hole_clearance (min 0.28mm)))
(rule "JLC: unplated hole to track 0.2 mm (D-23Nov.17)"
  (condition "A.Type == 'Pad' && A.Pad_Type == 'NPTH, mechanical' && (B.Type == 'Track' || B.Type == 'Arc')")
  (constraint hole_clearance (min 0.2mm)))
(rule "JLC: plated hole to plated hole 0.45 mm (D-23Nov.17)"
  (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole' && B.Type == 'Pad' && B.Pad_Type == 'Through-hole'")
  (constraint hole_to_hole (min 0.45mm)))
(rule "JLC: plated hole's ring 0.15 mm (D-23Nov.17)"
  (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'")
  (constraint annular_width (min 0.15mm)))
(rule "Fire copper keeps 0.5 mm from other nets, except between pads of one part"
  (condition "(A.NetClass == 'FIRE' || A.NetClass == 'FIRE_LOGIC' || A.NetClass == 'PYRO_RAIL') && A.Net != B.Net && !(A.Type == 'Pad' && B.Type == 'Pad' && A.Parent.Reference == B.Parent.Reference)")
  (constraint clearance (min 0.5mm)))
(rule "Fire logic keeps 0.2 mm inside a fine-pitch part's escape area: its courtyard and 0.2 mm (D-23Nov.8, D-23Nov.13)"
  (condition "((A.NetClass == 'FIRE_LOGIC' && (%s)) || (B.NetClass == 'FIRE_LOGIC' && (%s))) && A.Net != B.Net")
  (constraint clearance (min 0.2mm)))
(rule "RF lines take no via (D-21Nov.25)"
  (condition "A.Type == 'Via' && A.NetClass == 'RF50'")
  (constraint disallow via))
(rule "Pads of one part keep the maker's land-pattern spacing, down to JLC's 0.15 mm (last: it overrides the rules above)"
  (condition "A.Type == 'Pad' && B.Type == 'Pad' && A.Parent.Reference == B.Parent.Reference && A.Net != B.Net")
  (constraint clearance (min 0.15mm)))
'''

# --- parts fixed by the spec, never moved (D-21Nov.24 amended 22 Nov: every connector on an edge, facing out)
# J102: IR-3 datum read from the 8 September draft. Edge parts: `edge` puts the body (pads and F.Fab) `inset`
# mm from that edge, centred at `at` along it; `datum` gives an exact origin instead.
FIXED = {
    'J102': dict(xy=(40.0, 230.0), rot=0),                                        # [R] IR-3: opens aft
    'J6601': dict(edge='fwd', at=40.0, rot=0, inset=0.0),                         # [R] forward edge; centred [J]
    'J4601': dict(xy=(12.5, 5.0), rot=0),                                         # [R] LoRa SMA, forward left [J]
    'J4501': dict(xy=(67.5, 5.0), rot=0),                                         # [R] GNSS SMA, forward right [J]
    'J4401': dict(datum=(3.675, 120.0), rot=270),                                 # USB-C, left edge, opens left; its PCB-edge line on x = 0
    'J6101': dict(edge='left', at=165.0, rot=270, inset=0.3),                     # recovery arm, latch to the edge
    'J6102': dict(edge='left', at=181.0, rot=90, inset=0.3),                      # staging arm, latch to the edge
    'J502': dict(edge='right', at=110.0, rot=90, inset=0.3),                      # CAN bus 2, Salsa
    'J501': dict(edge='right', at=172.0, rot=90, inset=0.3),                      # CAN bus 1, Fajita
    'J103': dict(edge='right', at=200.0, rot=90, inset=0.3),                      # master-enable loop
    'J101': dict(edge='left', at=203.0, rot=0, inset=0.3),                        # standalone 2S (Nano-Fit 105311-1102), latch to the edge
    'J2301': dict(xy=(4.0, 90.0), rot=90),     # flight Tag-Connect: left edge, 11 mm from hole (4, 79), clear of the L4 corridor [J]
    'J4201': dict(xy=(4.0, 136.0), rot=90),    # comms Tag-Connect: left edge, 16 mm from hole (4, 152) [J]
}
# stage C step 0 (D-22Nov.30): the placement is data, written by build.py --replace and read by every other build
PLACEMENT = 'placement.json'
# D-23Nov.8, D-23Nov.13: fire logic keeps 0.2 mm inside each of these parts' escape areas, named <ref>_ESCAPE: the
# courtyard and ESCAPE_MARGIN round it. Each part's own pads sit closer than the fire rule's 0.5 mm.
ESCAPE_AREAS = ['U201', 'U6304', 'U6404', 'U6504', 'Q6301', 'Q6401', 'Q6501', 'U6502', 'U6001']
ESCAPE_MARGIN = 0.2
DRU = DRU % (' || '.join(f"A.enclosedByArea('{r}_ESCAPE')" for r in ESCAPE_AREAS),
             ' || '.join(f"B.enclosedByArea('{r}_ESCAPE')" for r in ESCAPE_AREAS))   # both orders: the other item may be fire copper
# stage C step 3 stopped at kill line 1 (docs/briefs/burrito-stage-c-step3.md): fanning the MCUs' pins inward left 34
# ordinary nets open against 17, and their plane pins alone 19. engine/copper.py's mcu_fanout keeps
# both, off, for Seán's call. To draw one: {'U201': [the nets its pins leave for their own copper], ...}, with
# MCU_FANOUT_SIGNALS = False for the plane and fire-logic pins only
MCU_FANOUT = {}
RESERVED = {}      # J101's 20 x 22 mm block gave way to its footprint (capture step 15, D-22Nov.13)

ANCHORS = {   # [J] placed before everything else, at these centres
    'U201': (40.0, 70.0, 0),                 # flight MCU, band 2
    'U401': (33.0, 126.0, 180),              # comms MCU, band 3: turned so USB leaves on the side facing J4401, and
                                             #   7 mm left of centre (stage B2 step 3: its wrong-side pins 19 -> 9)
    'U6304': (32.5, 26.206, 270),            # channel high sides in a row behind J6601, OUT pins (5-7) forward,
    'U6404': (41.5, 26.206, 270),            #   VS pins (8-10) aft toward the armed rails; at 26.206 (25.011 on the
    'U6504': (50.5, 26.206, 270),            #   160 mm board; 24.35 until 23 Nov) two rows of capacitors and J6601's
                                             #   name fit between (D-22Nov.28, D-23Nov.9)
    'U3304': (66.0, 72.0, 0),                # ADXL375 ~12 mm from hole (76, 79): near a hard mount (ADI Rev. B p. 26)
}

# --- regions per schematic sheet [J] (brief section 3): (x0, y0, x1, y1)
B1, B2, B3, B4 = (0, 46), (44, 102), (98, 152), (150, 230)
REGIONS = {
    '04e-radio': (1, 1, 30, 48), '04f-radio-module': (1, 1, 30, 48),
    '04d GNSS ': (50, 1, 79, 46),
    **{s: (22, 1, 58, 50) for s in ('06-outputs', '06b-output-harness', '06pyro1', '06pyro2', '06pyro3',
                                     '06c-output-diagnostics', '06e-continuity', '06f-continuity-isolation')},
    '02-flight-mcu': (16, 46, 64, 100), '02a-flight-support': (14, 44, 64, 102),
    '02flight-reset-debug': (1, 60, 30, 102),
    '03-sensors-storage': (1, 44, 26, 100),
    **{s: (58, 62, 72, 98) for s in ('03st-sensor', '03tdk-sensor', '03hg-sensor')},     # near hole (76, 79), >= 9 mm from U201 [J]
    '03bmp-pressure': (57, 44, 66, 63), '03te-pressure': (57, 44, 66, 63),
    '03mag-magnetometer': (64, 44, 79, 62),
    '04-comms-gnss-radio': (16, 100, 64, 150), '04a-comms-support': (16, 100, 64, 150),
    '02comms-reset-debug': (1, 132, 26, 150),
    '04b-uart-boundary': (18, 96, 62, 114),
    '04c-usb-service': (1, 104, 28, 136),
    '09-indicators': (56, 126, 79, 150),
    'CAN2': (54, 98, 79, 128), 'CAN1': (54, 154, 79, 192),
    '01-power': (12, 186, 68, 220), '07a-battery-monitor': (12, 186, 68, 220),
    '07-foinse-aux': (12, 192, 68, 220), '08-rail-diagnostics': (12, 180, 68, 220),
    **{s: (16, 150, 66, 196) for s in ('01a-source-mux', '01b-bootstrap', '01c-preregulator', '01d-held-core',
                                        '01flight-ldo', '01comms-ldo', '01optional-ldo', '01comms-limit', '01optional-limit')},
    '06a-arm-boundary': (1, 155, 22, 220),
    '44-master-enable': (56, 190, 79, 220),
    '10-test-points': (1, 1, 79, 229),       # each goes beside the circuit it probes (probe_target)
}
# --- the four black GND loops (Keystone 5011) claim edge spots, spread fore to aft (D-22Nov.9) [J]
REF_REGIONS = {
    'TP1': (18, 1, 31, 12),                # fwd edge, between the LoRa SMA and J6601
    'TP16': (1, 83, 12, 103),              # left edge by the flight Tag-Connect
    'TP23': (1, 126, 12, 148),             # left edge by the comms Tag-Connect
    'TP47': (50, 218, 72, 229),            # aft edge, right of J102
}
# --- top silk (D-22Nov.19): function names replace refs at connectors and say what each LED means; checked
# against current-system's interface table and the 09-indicators sheet ("Green means checks passed, not armed")
SILK_NAMES = {
    'J6601': 'PYRO 1 2 3\n+ PINS 1-3, - PINS 4-6',     # 1/2/3 high sides, 4/5/6 returns
    'J501': 'CAN 1', 'J502': 'CAN 2',                   # bus 1 Fajita, bus 2 the active board
    'J6101': 'RECOVERY ARM', 'J6102': 'STAGING ARM', 'J103': 'ENABLE', 'J101': '2S PACK',
    'J4401': 'USB', 'J4501': 'GNSS', 'J4601': 'LORA', 'J2301': 'SWD FLIGHT', 'J4201': 'SWD COMMS',
    'D9001': 'CHECKS OK', 'D9101': 'NOT READY', 'D9201': 'COMMS', 'D9301': 'POWER',
}
# names set further off than 0.25 mm, so parts that must sit at the pins fit between; the name stays clear as a box of
# its own (D-22Nov.28): J6601's leaves a strip for C6601-C6606, a row of 0603s on their side
SILK_NAME_GAP = {'J6601': 3.3}     # 1.6 until 23 Nov: two rows of capacitors now sit between (D-23Nov.9)
# refs kept clear as boxes of their own, not merged into the courtyard's box: an MCU's ref above its pins made that box
# 1.9 mm deeper along the whole side, so no capacitor could sit at a pin there (D-23Nov.1); U4606's, turned, would
# have spanned the side its RF pin faces (D-23Nov.3). The refs stay where they were
REFS_APART = ('U201', 'U401', 'U4606')
# the logic regulators, whose own parts sit at their pins on every side (the brief's block templates, D-23Nov.29): their
# refs don't count as courtyard for the placer, and the silk pass sets them where there's room
LABELS_MOVE = ('U1301', 'U1401', 'U1101', 'U1701', 'U1102')
# where each MCU's own decoupling capacitors are drawn, for tools/layout/caps_to_pins.py (D-23Nov.1)
DECOUPLING_SHEETS = {'U201': ('/02a-flight-support/',), 'U401': ('/04a-comms-support/',)}
# parts that may move this far, mm, to make room for those capacitors (D-23Nov.5): test points and pull resistors
# beside U201, the USB side's resistors beside U401. A test point keeps its stub limit (PROBE_STUB_MAX)
DECOUPLING_ROOM = {r: 8.0 for r in ('TP4', 'TP5', 'TP11', 'R2303', 'R2311', 'R4406', 'R4407')}
# silk marks the placer finds room for, as board-only footprints (tools/layout/marks.py): the board axes with the
# nose arrow, near the IMUs [J]. The white S/N box is drawn by art.board_art on the top silk after placing, in
# space that's left (Seán, 22 Nov: "put it in the free space up top"); it never counts as courtyard.
MARKS = {'MK1': 'Ogma2:MARK_AXES'}
REF_REGIONS.update({'MK1': (40, 44, 79, 104)})
# loops moved after placement (Sean, 22 Nov: "move 4 loops, keep layout"): x only, so y and the fore-to-aft numbers
# hold. Since stage B (brief B4) no loop pin is placed under the back's fixed blocks in the first place
# (art.art_skeleton), and build.py's clear_legend moves any that still block the legend, so this stays empty. [J]
PROBE_MOVES = {}
BANDS = {'1 RF and fire': B1, '2 Flight': B2, '3 Comms': B3, '4 Power and harness': B4}
# courtyard area (mm2) per band on the 230 mm board, lean test points, silk labels, function names and marks counted
# (re-measured after capture step 17 and the S/N box's move to the back, 22 Nov; was [2002, 1847, 1460, 3891] after
# steps 14-16, and [1880, 2083, 1443, 3846] before): how build.py's stretch() shares a shorter board's length
# between the bands
BAND_AREA = [2031, 1861, 1356, 3891]

# --- silkscreen art and legends (Sean, 22 Nov: name, version, "funny little vector memes ... both sides") [J]
ART = dict(
    name='BURRITO', version='R1.0',
    lines=['OGMA 2 FLIGHT COMPUTER   R1.0   2026-11', 'ULAS HiPR'],
    logo='layout/art/ulas-hipr-logo.png',          # the team's logo, from github.com/ULAS-HiPR/ulas-hipr.github.io
    found='IF FOUND IN A FIELD, IT IS OURS: ULAS HiPR, UNIVERSITY OF LIMERICK',
    specs=['FLIGHT  STM32H563VIT6', 'COMMS   STM32H563RIT6', 'IMU     LSM6DSV32X, ICM-42688-P',
           'HIGH G  ADXL375', 'BARO    BMP390, MS5607', 'MAG     MMC5983MA', 'GNSS    u-blox MAX-M10S',
           'RADIO   Wio-LR2021 LoRa', 'LOG     MX66L2G45G 2 Gbit NOR', 'CAN     2x TCAN3413',
           'PYRO    3x TPS1H100 + CSD17318', 'MONITOR  INA228', '', 'POWER CHAIN', 'TPS26630 eFuse',
           '> TPS2121 source mux', '> TPSM63603 buck, 4 V', '> LM73100 hold', '> 3x TPS7A91, 3.3 V',
           'BOOT    TPS70933', 'WATCH   TPS3430, 2x TPS3808', '', '4 LAYERS, 1.6 mm, {W:g} x {H:g} mm'],
    title_font='layout/art/fonts/texgyreheros-bold.otf',   # TeX Gyre Heros Bold, a free Helvetica clone (GUST licence)
    # where Sean saw and liked the blocks on 22 Nov (bottom-view mm, v aft): BURRITO's centre and cap height,
    # the subtitle's first line, IF FOUND, and the logo's centre then (it moves up from there)
    place=dict(cap=7.0, title=32.1, lines=38.9, found=59.6, logo=95.41, logo_seen=92.04, at=180.0),
    # Claude's addition, 22 Nov, at Sean's invitation: "Burrito son of Ogma" in Ogham, the script the Ogam
    # Tract credits to Ogma, in the old stones' X MAQI Y form, across the top band. None drops it.
    ogham_text='BURRITO MAQI OGMA',
    serial_box=(10.0, 3.0))       # the S/N box on the top silk, 10 x 3 mm, in leftover space (Seán, 22 Nov)

# --- rotation limits: MLCCs of 1206 and larger lie across the long axis (B-33) [J]
BIG_MLCC = ('Capacitor_SMD:C_1206', 'Capacitor_SMD:C_1210', 'Capacitor_SMD:C_1812', 'Capacitor_SMD:C_2220')

# --- pulls [J]: net-name regex -> weight. RF and fire nets short; the armed rails run the corridor anyway.
NET_WEIGHTS = [(r'LORA_RF_SUBG|GNSS_RF', 30.0), (r'OUTPUT\d_(HIGH|LOW)', 6.0), (r'PYRO\d_ENERGY', 3.0),
               (r'(RECOVERY|STAGING)_ARMED_VBAT|.*ARM_FEED', 0.1), (r'VBAT_CROI_INPUT|ENERGY_TAP', 4.0),
               (r'USB_D[PM](_CONN)?', 4.0), (r'CAN2?_[HL]', 3.0)]
# distance rules (stage B2 step 6, the sweep's section 5): the build places these parts first and reports every miss
# (build.json `metrics.near`). Distances are copper gaps, pad edge to pad edge.
_SWEEP = 'burrito-sweep.md section 5'
NEAR = [
    # each MCU supply pin measured on its own, one capacitor to one pin (D-23Nov.1)
    dict(rule='supply_caps', ic='U201', nets=('FLIGHT_3V3', 'FLIGHT_VBAT'), value='100n', mm=3.0,
         src=f'{_SWEEP}: one 100 nF per supply pin, on its side; 3 mm [J]; D-23Nov.1'),
    dict(rule='supply_caps', ic='U201', nets=('FLIGHT_VDDA',), value='100n', mm=3.0,
         src=f'{_SWEEP}: one 100 nF per supply pin; VDDA and VREF+ each; 3 mm [J]; D-23Nov.1'),
    dict(rule='supply_caps', ic='U201', nets=('FLIGHT_VDDA',), value='1u', mm=3.0,
         src="ST's VDDA and VREF+ pairing: 1 uF with each 100 nF; 3 mm [J]; D-23Nov.1"),
    dict(rule='supply_caps', ic='U201', nets=('FLIGHT_VCAP',), value='2.2u', mm=2.0,
         src=f'{_SWEEP}: VCAP capacitors within 2 mm, one at each VCAP pin; D-23Nov.1'),
    dict(rule='supply_caps', ic='U401', nets=('COMMS_3V3',), value='100n', mm=3.0,
         src=f'{_SWEEP}: one 100 nF per supply pin, on its side; 3 mm [J]; D-23Nov.1'),
    dict(rule='supply_caps', ic='U401', nets=('COMMS_VDDA',), value='100n', mm=3.0,
         src=f'{_SWEEP}: one 100 nF per supply pin; 3 mm [J]; D-23Nov.1'),
    dict(rule='supply_caps', ic='U401', nets=('COMMS_VDDA',), value='1u', mm=3.0,
         src="ST's VDDA pairing: 1 uF with its 100 nF; 3 mm [J]; D-23Nov.1"),
    dict(rule='supply_caps', ic='U401', nets=('COMMS_VCAP',), value='2.2u', mm=2.0,
         src=f'{_SWEEP}: VCAP capacitors within 2 mm, one at each VCAP pin; D-23Nov.1'),
    dict(rule='part_to_pins', part='Y201', ic='U201', mm=5.0, src=f'{_SWEEP}: crystals within 5 mm of the pins'),
    dict(rule='part_to_pins', part='Y202', ic='U201', mm=5.0, src=f'{_SWEEP}: crystals within 5 mm of the pins'),
    dict(rule='part_to_pins', part='Y401', ic='U401', mm=5.0, src=f'{_SWEEP}: crystals within 5 mm of the pins'),
    dict(rule='net_caps', ic='U1701', nets=('CORE_HELD_4V', 'FLIGHT_3V3_PRELINK'), mm=2.0,
         src=f'{_SWEEP}: TPS7A91 input and output capacitors within 2 mm'),
    dict(rule='net_caps', ic='U1801', nets=('COMMS_LDO_IN', 'COMMS_3V3_PRELINK'), mm=2.0,
         src=f'{_SWEEP}: TPS7A91 input and output capacitors within 2 mm'),
    dict(rule='net_caps', ic='U1901', nets=('OPTIONAL_LDO_IN', '3V3_OPTIONAL_PRELINK'), mm=2.0,
         src=f'{_SWEEP}: TPS7A91 input and output capacitors within 2 mm'),
    dict(rule='net_caps', ic='U1102', nets=('LOGIC_SELECTED', 'BOOT_3V3'), mm=2.0,
         src=f'{_SWEEP}: TPS70933 input and output capacitors within 2 mm'),
    # D-22Nov.28: as close as J6601's courtyard allows. The HIGH row (pins 1-3) sits 4.3 mm inside its aft edge, so about
    # 4-5 mm; the LOW row (pins 4-6) 1.3 mm, so 3 mm holds. HIGH first: they have fewer places that fit. The strip
    # between J6601 and its name leaves their centres 0.1 mm of play fore and aft, so they're searched at 0.05 mm
    *[dict(rule='part_to_pins', part=f'C660{n}', ic='J6601', mm=5.0, step=0.05,
           src="D-22Nov.28: each HIGH output's 1 nF at J6601's courtyard edge, 5 mm") for n in (1, 3, 5)],
    *[dict(rule='part_to_pins', part=f'C660{n}', ic='J6601', mm=3.0, step=0.05,
           src="D-22Nov.20, D-22Nov.28: each LOW output's 1 nF at J6601, 3 mm") for n in (2, 4, 6)],
    dict(rule='on_line', part='D4601', net='LORA_RF_SUBG', **{'from': 'J4601', 'to': 'U4606'}, mm=1.0,
         src='D-22Nov.20: the LoRa ESD part on the line between connector and module; 1 mm [J]'),
    dict(rule='on_line', part='D4501', net='GNSS_RF', **{'from': 'J4501', 'to': 'U4504'}, mm=1.0,
         src='D-22Nov.8: the GNSS ESD part on the line between connector and module; 1 mm [J]'),
    # the pyro output stage (D-22Nov.27's stamp, PYRO_STAMP below): each channel's supply capacitor, limit and sense
    # resistors at their high side's pins, Kelvin (sweep section 5); its low side's gate parts at the FET's gate [J]
    *[dict(rule='part_to_pins', part=p, ic=f'U6{c}04', mm=1.0, src=f'{_SWEEP}: at the pins, Kelvin; D-22Nov.27')
      for c in (3, 4, 5) for p in (f'C6{c}04', f'R6{c}14', f'R67{c - 2}1')],
    *[dict(rule='part_to_pins', part=f'R6{c}0{k}', ic=f'Q6{c}01', mm=2.0,
           src='the gate resistor and gate pull-down at the FET gate, so the gate stays low with its line open [J]')
      for c in (3, 4, 5) for k in (4, 5)],
]
# D-22Nov.27: the three output stages placed as one block, at the same offsets from each high side (a TPS1H100 at
# 270 degrees). One row of 0603s under its pin row 8-14: the energy link and the supply capacitor under the supply
# pins (8-10), the current-limit resistor under pin 13, the sense resistor under pin 14, the IN pull-down beside them
# the continuity and test taps on the fire outputs (sheet 06c) stay by the output stage, so their fire-net stubs are short
NEAR += [dict(rule='part_to_pins', part=r, ic='J6601', mm=15.0,
              src='a resistor on a fire output stays by the output stage: its stub is fire copper [J]')
         for r in ('R6912', 'R6913', 'R6915', 'R6922', 'R6923', 'R6925', 'R6932', 'R6933', 'R6935')]
# channel 3's fire command passes the staging inhibit (U6502, the AND gate; U6001, the latch) on its way to the high
# side's IN pin: both are fire logic since D-23Nov.10 and D-23Nov.12, so they sit by the high side and the track stays short
NEAR += [dict(rule='part_to_pins', part='U6502', ic='U6504', mm=18.0,
              src='D-23Nov.10: the staging AND gate by channel 3 IN pin, so PYRO3_HS_ENABLE stays short: 17.6 mm on 23 Nov; nearer is for the fire-logic step [J]'),
         dict(rule='part_to_pins', part='U6001', ic='U6502', mm=6.0,
              src='D-23Nov.12: the staging latch by the AND gate, so STAGE_ELIGIBLE stays short [J]')]
# the logic regulators' own parts at their pins (D-23Nov.29; the brief's block templates, section 4): the buck's
# capacitors and set resistors, the held core's and the mux's input capacitors and set parts [J]
_BLOCK = 'layout brief section 4, block templates [J]'
NEAR += [dict(rule='part_to_pins', part=r, ic=ic, mm=mm, src=f'{_BLOCK}: {why}') for r, ic, mm, why in (
    ('C1303', 'U1301', 1.5, 'input capacitors tight between VIN and PGND'),
    ('C1304', 'U1301', 1.5, 'input capacitors tight between VIN and PGND'),
    ('C1305', 'U1301', 1.5, 'output capacitors at VOUT'), ('C1306', 'U1301', 1.5, 'output capacitors at VOUT'),
    ('C1302', 'U1301', 2.5, 'output capacitors at VOUT'),
    ('C1301', 'U1301', 1.5, '1 uF on VCC close'), ('R1303', 'U1301', 5.0, 'RT by its pin'),
    ('R1302', 'U1301', 1.5, 'RFBT and RFBB as close as possible to the FB pin (TI)'),
    ('C1401', 'U1401', 4.0, '0.1 uF at IN'), ('R1406', 'U1401', 6.0, 'R_IMON close'),
    ('C1402', 'U1401', 6.0, 'set parts by their pins'),
    ('R1402', 'U1401', 15.0, 'the threshold dividers in the block (DC)'),
    ('R1404', 'U1401', 15.0, 'the threshold dividers in the block (DC)'),
    ('C1102', 'U1101', 2.5, 'caps close'), ('C1101', 'U1101', 4.0, 'set parts by their pins'),
    ('R1107', 'U1101', 4.0, 'set parts by their pins'),
    ('R1102', 'U1101', 8.0, 'the threshold dividers in the block (DC)'),
    ('R1104', 'U1101', 8.0, 'the threshold dividers in the block (DC)'),
    ('R1106', 'U1101', 8.0, 'the threshold dividers in the block (DC)'),
    # the flight LDO (D-23Nov.31; TI's TPS7A91 layout)
    ('C1706', 'U1701', 1.5, 'output capacitor at OUT'), ('C1703', 'U1701', 1.5, 'input capacitor at IN'),
    ('C1701', 'U1701', 1.5, 'NR/SS capacitor at its pin'),
    ('R1701', 'U1701', 3.0, 'the feedback divider by FB'), ('R1702', 'U1701', 3.5, 'the feedback divider by FB'),
    ('C1702', 'U1701', 3.5, 'the feed-forward capacitor with the divider'),
    ('R1704', 'U1701', 3.0, 'the isolation link beside the output capacitor'),
    ('C1705', 'U1701', 4.0, 'the 47 uF input capacitor near IN'))]
PYRO_STAMP = {
    'anchors': ('U6304', 'U6404', 'U6504'),
    'rows': [('energy link', ('R6310', 'R6410', 'R6510'), (-3.1, 5.5), 90),
             ('supply capacitor', ('C6304', 'C6404', 'C6504'), (-1.3, 5.5), 270),
             ('current limit', ('R6314', 'R6414', 'R6514'), (1.0, 5.5), 270),
             ('current sense', ('R6711', 'R6721', 'R6731'), (2.6, 5.5), 270),
             ('IN pull-down', ('R6303', 'R6403', 'R6503'), (4.3, 5.5), 270)],
}

# The output stage, drawn once and repeated (D-22Nov.27, D-23Nov.9). Each high side's supply (link, capacitor, VS pins
# 8-10) and OUT stub (pins 7, 6 and the outer 0.15 mm of 5) are stamped; the paths to J6601 are per channel. HIGH 1
# and 3 go round the ends of J6601's LOW row on L1; HIGH 2 passes between LOW pins 4 and 5 through a 0.5 mm neck
# (D-23Nov.9), C6603 on it below the neck. The LOW pins leave on L6 through their barrels to the three FETs, whose
# drains face J6601, each through three vias; each source reaches GND through two. Board mm; L1 F.Cu, L6 B.Cu. Copper
# keeps 0.5 mm from NC pins 4 and 11.
PYRO_PARTS = {      # placed before anything else in the region, at these spots
    'Q6301': (31.15, 6.2, 270), 'Q6401': (31.3, 12.9, 270), 'Q6501': (48.85, 6.0, 270),
    'C6601': (31.35, 8.95, 180), 'C6605': (48.65, 8.95, 0),
    'C6602': (36.225, 14.05, 180), 'C6603': (39.275, 14.05, 0), 'C6606': (43.775, 14.05, 0), 'C6604': (40.775, 15.75, 0),
    # each FET's gate resistor and gate pull-down beside its gate pin (spec.NEAR: within 2 mm), 1 mm clear of the FET
    'R6304': (28.6, 6.4, 90), 'R6305': (29.45, 3.5, 180),
    'R6404': (28.0, 11.6, 0), 'R6405': (28.0, 13.4, 180),
    'R6504': (47.95, 2.55, 270), 'R6505': (49.6, 2.55, 90),
    # the parts the fire logic's frozen copper lands on (D-23Nov.15); R6303, R6403 and R6503 come with the stamp
    'R6302': (23.95, 11.45, 90), 'R6402': (25.55, 11.65, 90),
    # channel 3's low-side pull-down by its gate resistor R6504 (take 2, D-23Nov.25): J6601's courtyard ends at R6504,
    # so the nearest free spot is past R6505, along the board's top edge
    'R6502': (51.95, 1.45, 0),
    'R6501': (49.0, 36.8, 0), 'U6502': (48.4, 39.75, 0), 'U6001': (43.1, 39.85, 0),
    # the nine taps on the fire outputs, each beside its own copper, the fire pad facing it (taps trial, 23 Nov)
    'R6912': (33.1, 15.22, 0), 'R6913': (31.8, 3.2, 90), 'R6915': (37.0, 16.4, 270),
    'R6922': (37.2, 18.82, 0), 'R6923': (31.15, 10.62, 180), 'R6925': (40.75, 17.42, 0),
    'R6932': (45.05, 16.62, 0), 'R6933': (51.05, 7.2, 270), 'R6935': (51.25, 4.0, 90),
}
HS_Y = 25.011       # the three high sides' centre line (placement.json), 1.7 mm further aft than at 23 Nov's region


def _pyro_copper():
    F, B, out = 'F.Cu', 'B.Cu', []
    t = lambda net, lay, w, *path: out.append(dict(net=net, layer=lay, w=w, path=[(round(x, 3), round(y, 3)) for x, y in path]))
    v = lambda net, *xy: out.extend(dict(net=net, via=p) for p in xy)
    yo, ys = HS_Y - 2.9, HS_Y + 2.9          # OUT pins (5-7) and VS pins (8-10), each 0.45 x 1.5 mm
    yb = yo - 2.01                           # the top of each OUT stub
    for k, c in enumerate((1, 2, 3)):
        dx = 9.0 * k
        t(f'PYRO{c}_ENERGY', F, 1.47, (31.04 + dx, ys + 0.24), (31.04 + dx, ys + 1.49))   # VS pins 8, 9, 10 to the cap
        t(f'PYRO{c}_ENERGY', F, 0.9, (29.4 + dx, HS_Y + 4.679), (31.04 + dx, HS_Y + 4.679))  # the energy link's pad
        t(f'OUTPUT{c}_HIGH', F, 1.47, (31.04 + dx, yo - 0.25), (31.04 + dx, yb))         # OUT pins 7, 6, 5
    t('OUTPUT1_HIGH', F, 1.0, (31.04, yb), (31.04, yb - 0.8), (33.7, yb - 3.46), (33.7, 8.97), (37.0, 8.97))
    t('OUTPUT1_HIGH', F, 1.0, (33.7, 8.97), (32.125, 8.97))                         # C6601
    t('OUTPUT3_HIGH', F, 1.0, (49.04, yb), (49.04, yb - 0.8), (46.3, yb - 3.54), (46.3, 8.97), (43.0, 8.97))
    t('OUTPUT3_HIGH', F, 1.0, (46.3, 8.97), (47.875, 8.97))                         # C6605
    t('OUTPUT2_HIGH', F, 1.0, (40.0, 8.97), (38.5, 10.47), (38.5, 11.04))
    t('OUTPUT2_HIGH', F, 0.5, (38.5, 11.04), (38.5, 12.9))                          # the neck, between pins 4 and 5
    t('OUTPUT2_HIGH', F, 1.0, (38.5, 12.9), (38.5, yb - 0.9), (40.04, yb))           # past C6603's pad 1
    t('OUTPUT1_LOW', F, 1.0, (37.0, 11.97), (37.0, 14.05))                          # C6602
    t('OUTPUT3_LOW', F, 1.0, (43.0, 11.97), (43.0, 14.05))                          # C6606
    # each gate to its gate resistor and pull-down; the part inside the FET's escape area ends there (D-23Nov.8)
    t('PYRO1_GATE', F, 0.15, (30.45, 5.225), (29.9, 5.35), (28.9, 5.575))
    t('PYRO1_GATE', F, 0.15, (30.45, 5.225), (30.275, 4.65), (30.275, 3.5))
    t('PYRO2_GATE', F, 0.15, (30.6, 11.925), (30.0, 11.78), (28.825, 11.6), (28.825, 13.4))
    t('PYRO3_GATE', F, 0.15, (48.2, 4.95), (48.2, 4.47))
    t('PYRO3_GATE', F, 0.15, (48.2, 4.47), (47.95, 3.45))
    t('PYRO3_GATE', F, 0.15, (48.2, 4.47), (49.6, 3.45))
    for net, (px, py), vx, sx in (('OUTPUT1_LOW', (31.475, 6.2), 32.3, 1), ('OUTPUT2_LOW', (31.625, 12.9), 32.3, 1),
                                  ('OUTPUT3_LOW', (49.175, 6.0), 50.25, 1)):     # drain pad 8, and the via column
        # from pad 8's outer half to just short of the column: 0.5 mm clear of the source pin 7 and of HIGH 1
        t(net, F, 0.95, (px + sx * 0.275, py), (vx - sx * 0.2, py))
        t(net, F, 0.6, (vx, py - 0.7), (vx, py + 0.7))
        # on L6 the column spans both its vias and reaches the one in pad 8, so all three carry the fire current
        t(net, B, 1.0, (vx, py - 0.7), (vx, py + 0.7))
        t(net, B, 0.95, (px, py), (vx, py))
        v(net, (vx, round(py - 0.7, 3)), (vx, round(py + 0.7, 3)), (px, py))
        # the drain pins (1, 2 above pad 8, 5, 6 below) joined to it on L1; the lower bridge starts at pin 5's inner
        # edge, 0.5 mm from the source pin 4 (GND); the upper one passes the gate pin 3 at 0.38 mm, inside the waiver
        t(net, F, 0.25, (px - 0.325, py - 0.975), (px + 0.325, py - 0.975), (px + 0.325, py - 0.4))
        t(net, F, 0.25, (px - 0.195, py + 0.975), (px + 0.325, py + 0.975), (px + 0.325, py + 0.4))
    # each FET's source (pins 7 and 4) to GND through a via beside each pin; the 0.2 mm tracks end 0.52 mm from the
    # drain pads (the fire rule) and the vias sit 0.57 mm from the gate parts' pads
    for x, y7, y4, gx in ((30.5, 6.295, 7.175, 29.95), (30.65, 12.995, 13.875, 30.1), (48.2, 6.095, 6.975, 47.65)):
        for y in (y7, y4):
            t('GND', F, 0.2, (gx, y), (x - 0.12, y))
        v('GND', (gx, y7), (gx, y4))
    t('OUTPUT1_LOW', B, 1.0, (37.0, 11.97), (35.3, 10.27), (32.3, 7.27), (32.3, 5.5))
    t('OUTPUT2_LOW', B, 1.0, (40.0, 11.97), (40.0, 16.6), (33.4, 16.6), (32.3, 15.5), (32.3, 12.2))
    v('OUTPUT2_LOW', (40.0, 15.75))                                                  # C6604's pad 1
    t('OUTPUT3_LOW', B, 1.0, (43.0, 11.97), (44.7, 10.27), (48.3, 10.27), (50.25, 8.32), (50.25, 6.7))
    return out


def _fire_logic_escapes():
    """The fire logic's ends (D-22Nov.26, D-23Nov.8, D-23Nov.13): each pin leaves on L1 inside its part's escape area
    (0.2 mm), to a 0.5 mm via; the runs between are on L3, between the GND planes, at 0.5 mm."""
    F, out = 'F.Cu', []
    t = lambda net, *path: out.append(dict(net=net, layer=F, w=0.15, path=[(round(x, 3), round(y, 3)) for x, y in path]))
    v = lambda net, *xy: out.extend(dict(net=net, via=p, d=0.5) for p in xy)
    # U201 (take 2, D-23Nov.25): five bottom-row pins and pin 85 leave inward to vias under the body. West to east on
    # L3: the two low sides at the board's top left leave from the bottom row's west end, PYRO1_FIRE goes up the lane
    # under U201, PYRO3_LS_SELECT north from PD4, PYRO2_FIRE and PYRO3_FIRE under U201 to its east side; no run crosses
    # another
    for net, x in (('PYRO1_LS_SELECT', 37.5), ('PYRO2_LS_SELECT', 39.0), ('PYRO1_FIRE', 40.0), ('PYRO2_FIRE', 41.0),
                   ('PYRO3_FIRE', 44.0)):
        t(net, (x, 61.8), (x, 60.9)); v(net, (x, 60.9))
    t('PYRO3_LS_SELECT', (41.5, 47.85), (41.5, 48.75)); v('PYRO3_LS_SELECT', (41.5, 48.75))
    # each high side's IN pin (3): off its tip, along the tips of pins 2 and 1 inside the area, then out to a via. A
    # track straight off the tip can't cross the area's edge 0.5 mm from pins 2 and 4: it needs 0.39 mm past the tips
    # plus its half width, and the area gives 0.44
    for net, x in (('PYRO1_FIRE', 33.15), ('PYRO2_FIRE', 42.15), ('PYRO3_HS_ENABLE', 51.15)):
        t(net, (x, 21.6), (x, 21.02), (x + 2.15, 21.02), (x + 2.95, 21.02)); v(net, (x + 2.95, 21.02))
    # the staging latch's Q (U6001 pin 5) straight to the AND gate's pin 2 on L1: out of the latch's area 0.54 mm
    # from its pin 6, into the gate's 0.66 mm from its pins 1 and 3 (a run on L3 would wall off the trunk); the AND
    # gate's output (pin 4) east to a via
    t('STAGE_ELIGIBLE', (44.6, 40.6), (45.45, 40.8), (46.25, 39.75), (47.2, 39.75))
    # PYRO3_FIRE's via under the gate's body: north of it is the armed rails' crossing on L6, no via (spec.BUDGET);
    # R6501 on L1 across it
    t('PYRO3_FIRE', (47.85, 38.8), (48.4, 38.8), (48.4, 39.75)); v('PYRO3_FIRE', (48.4, 39.75))
    t('PYRO3_FIRE', (47.262, 38.6), (47.262, 37.4), (47.95, 36.86))
    t('PYRO3_HS_ENABLE', (49.75, 40.7), (50.75, 40.7)); v('PYRO3_HS_ENABLE', (50.75, 40.7))
    # the pull-downs and gate resistors, each pad to a via beside it
    t('PYRO1_FIRE', (36.8, 28.75), (36.8, 29.5)); v('PYRO1_FIRE', (36.8, 28.75))                  # R6303
    t('PYRO2_FIRE', (45.8, 28.75), (45.8, 29.5)); v('PYRO2_FIRE', (45.8, 28.75))                  # R6403
    t('PYRO3_HS_ENABLE', (54.6, 28.75), (54.7, 29.45)); v('PYRO3_HS_ENABLE', (54.6, 28.75))       # R6503
    t('PYRO3_LS_SELECT', (46.6, 1.725), (47.6, 1.725)); v('PYRO3_LS_SELECT', (46.6, 1.725))       # R6504, 1 mm clear of Q6501's source vias
    # R6502 along the top edge from R6504's pad, past R6505's GND pad (0.57 mm), 0.5 mm in from the edge; its GND pad to a via
    t('PYRO3_LS_SELECT', (47.95, 1.725), (47.95, 0.6), (51.125, 0.6), (51.125, 1.45))
    t('GND', (52.775, 1.45), (53.65, 1.45)); v('GND', (53.65, 1.45))
    t('PYRO1_LS_SELECT', (28.6, 8.45), (28.6, 7.45)); v('PYRO1_LS_SELECT', (28.6, 8.45))          # R6304
    t('PYRO1_LS_SELECT', (22.7, 12.3), (23.7, 12.3)); v('PYRO1_LS_SELECT', (22.7, 12.3))          # R6302
    t('PYRO2_LS_SELECT', (26.9, 11.7), (26.3, 11.95), (25.85, 12.3)); v('PYRO2_LS_SELECT', (26.3, 11.95))  # R6404, R6402
    return out


# The fire logic's runs on L3, between the GND planes: KiCadRoutingTools on L3 alone between the escapes above, at
# 0.5 mm from everything (trials fl3, and fl5 for PYRO2_FIRE and PYRO3_FIRE, 23 Nov), frozen here as data. 0.15 mm
# wide; board mm; each list one run.
FIRE_LOGIC_L3 = {
    'PYRO1_FIRE': [
        [(36.1, 21), (36.1, 28.05), (36.8, 28.75), (36.8, 29.7), (40, 32.9), (40, 60.9)],
    ],
    'PYRO1_LS_SELECT': [
        [(37.5, 60.9), (37.5, 31.35), (36.25, 30.1), (36.25, 30.05), (36.2, 30), (36.2, 29.95), (36.15, 29.9),
         (36.15, 29.35), (36.05, 29.25), (36.05, 29.2), (36, 29.15), (36, 29.1), (35.95, 29.05), (35.95, 28.9),
         (35.9, 28.85), (35.9, 28.8), (35.55, 28.45), (35.55, 28.4), (35.5, 28.35), (35.5, 28.3), (35.45, 28.25),
         (35.45, 23.8), (23.95, 12.3), (22.7, 12.3)],
        [(24.5, 12.85), (26.4, 12.85), (26.45, 12.8), (26.6, 12.8), (26.65, 12.75), (26.7, 12.75), (26.75, 12.7),
         (26.8, 12.7), (28.6, 10.9), (28.6, 8.45)],
    ],
    'PYRO2_FIRE': [
        [(45.1, 21), (45.1, 28.05), (45.8, 28.75), (45.8, 56.1), (41, 60.9)],
    ],
    'PYRO2_LS_SELECT': [
        [(26.3, 11.95), (24.55, 11.95), (24, 11.4), (22.35, 11.4), (21.95, 11.8), (21.95, 11.85), (21.9, 11.9),
         (21.9, 11.95), (21.85, 12), (21.85, 12.15), (21.8, 12.2), (21.8, 12.4), (21.85, 12.45), (21.85, 12.6),
         (21.9, 12.65), (21.9, 12.7), (21.95, 12.75), (21.95, 12.8), (34.8, 25.65), (34.8, 28.45), (34.85, 28.5),
         (34.85, 28.55), (34.9, 28.6), (34.9, 28.65), (34.95, 28.7), (34.95, 28.75), (35, 28.8), (35, 28.85),
         (35.3, 29.15), (35.3, 29.25), (35.35, 29.3), (35.35, 29.35), (35.4, 29.4), (35.4, 29.45), (35.45, 29.5),
         (35.45, 29.55), (35.5, 29.6), (35.5, 30.1), (35.55, 30.15), (35.55, 30.2), (35.6, 30.25), (35.6, 30.3),
         (35.65, 30.35), (35.65, 30.4), (35.7, 30.45), (35.7, 30.5), (36.85, 31.65), (36.85, 60.3), (36.6, 60.55),
         (36.6, 61.25), (37, 61.65), (37.05, 61.65), (37.1, 61.7), (37.15, 61.7), (37.2, 61.75), (37.35, 61.75),
         (37.4, 61.8), (37.6, 61.8), (37.65, 61.75), (37.8, 61.75), (37.85, 61.7), (37.9, 61.7), (37.95, 61.65),
         (38, 61.65), (38.75, 60.9)],
    ],
    'PYRO3_FIRE': [
        [(48.4, 39.75), (46.45, 41.7), (46.45, 56.275), (46.425, 56.3), (46.425, 56.325), (46.4, 56.35),
         (46.4, 56.4), (46.35, 56.45), (46.35, 56.475), (44, 58.825), (44, 60.9)],
    ],
    'PYRO3_HS_ENABLE': [
        [(54.1, 21), (54.1, 28.25), (54.8, 28.95), (54.8, 36.65), (50.75, 40.7)],
    ],
    'PYRO3_LS_SELECT': [
        [(46.6, 1.7), (41.5, 6.8), (41.5, 48.75)],
    ],
}


def _fire_logic_runs():
    return [dict(net=n, layer='In2.Cu', w=0.15, path=[tuple(p) for p in c]) for n, cs in FIRE_LOGIC_L3.items() for c in cs]



def _tap_stubs():
    """Each fire-output tap's fire pad to its own copper on L1, 0.3 mm (taps trial, 23 Nov); a pad that sits on its
    copper needs none."""
    nets = {'R6912': 'OUTPUT1_HIGH', 'R6913': 'OUTPUT1_LOW', 'R6915': 'OUTPUT1_LOW', 'R6922': 'OUTPUT2_HIGH',
            'R6923': 'OUTPUT2_LOW', 'R6925': 'OUTPUT2_LOW', 'R6932': 'OUTPUT3_HIGH', 'R6933': 'OUTPUT3_LOW',
            'R6935': 'OUTPUT3_LOW'}
    return [dict(net=nets[r], layer='F.Cu', w=0.3, path=[a, b]) for r, a, b in (
        ('R6913', (31.8, 4.025), (31.8, 5.2)),
        ('R6915', (37.0, 15.575), (37.0, 14.35)),
        ('R6923', (31.975, 10.624), (31.975, 11.9)),
        ('R6925', (39.925, 17.424), (39.925, 16.025)),
        ('R6933', (51.054, 6.375), (50.35, 6.375)),
        ('R6935', (51.254, 4.825), (50.34, 5.258)),
    )]

PYRO_COPPER = _pyro_copper() + _fire_logic_escapes() + _fire_logic_runs() + _tap_stubs()

# --- power, stage C step 4 (midpoint review: "Power the same way"), part 1 (D-23Nov.28): the 6 A path, the arm feeds,
# and the corridor with its taps and links, locked like the pyro band. Board mm; L1 F.Cu, L3 In2.Cu, L6 B.Cu.
POWER_PARTS = {     # moved for this copper; placement.json holds them
    'TP16': (12.5, 64.4, 0),     # the flight GND loop onto the corridor's GND strip (was 2.45 mm west, on a rail's line)
    'TP42': (9.0, 142.0, 0),     # VBAT_CROI_INPUT's test point onto J101's run (was in the recovery feed's way)
    'R8007': (12.6, 105.6, 0),   # the pyro-rail divider's top beside the recovery rail: the 40 mm to R8008 is then
                                 # PYRO_RAIL_MID's, behind 22.1 kohm, not armed-rail copper's
    # the logic regulators' blocks (D-23Nov.29; the brief's block templates; TI's TPSM63603 layout guidelines: "Place
    # ceramic input and output capacitors close to the device pins", "Place RFBT and RFBB as close as possible to the FB
    # pin"). The buck U1301 keeps its place; the held core U1401 and the flight LDO U1701 step west and the input mux
    # U1101 east, so the buck's parts sit at its pins, each 1.0 mm off (JLC's spacing to a QFN): an input capacitor at
    # each pair of VIN and PGND pins, the two output capacitors under the VOUT row, and above the top row the feedback
    # divider over FB (its two FB pads side by side) and the VCC capacitor over VCC
    'U1401': (22.0, 125.65, 90), 'U1101': (36.45, 127.2, 0),
    'C1304': (25.55, 125.95, 270), 'C1303': (33.775, 125.38, 270),
    'C1305': (28.45, 131.6, 270), 'C1306': (31.75, 131.6, 270), 'C1302': (25.6, 129.4, 180),
    'R1301': (27.6, 119.92, 270), 'R1302': (29.12, 119.92, 90), 'C1301': (30.64, 119.925, 90),
    # the held core's input capacitor on its input feed, its current-monitor resistor and slew capacitor below it (their
    # pins on the top row reach them by L3: the 1000 uF sits over U1401); the mux's input capacitor at IN1
    'C1401': (23.85, 129.9, 270), 'R1406': (21.5, 129.5, 270), 'C1402': (22.8, 129.9, 270),
    'C1102': (39.15, 127.93, 270),
    'TP41': (18.75, 131.5, 0),   # BAT_SOURCE_PG's probe: the blocks took its spot; the nearest free one, 15 mm from R1010
    # the flight LDO's block (D-23Nov.31; the brief's LDO template; TI's TPS7A91 layout: input and output capacitors
    # at the pins, the feedback divider by FB with its top sensed at the output capacitor). Its output capacitor was
    # 12 mm off and its divider 12-15 mm, the 1000 uF filling the only room by it, so the 1000 uF moves 8 mm north,
    # turned so its CORE_HELD_4V pad faces east, and the LDO turns so OUT faces it: C1706 1.0 mm over the OUT pins,
    # the 0 ohm link R1704 beside it, the divider R1701-R1702 and the feed-forward cap C1702 west of the FB pin, the
    # NR/SS cap C1701 1.0 mm under the NR pin, the 100 nF C1703 east of the IN pins and the 47 uF C1705 where the
    # LDO stood, on the held core's feed to them
    'C1403': (20.4, 109.35, 180),
    'U1701': (19.5, 119.5, 270), 'C1706': (21.73, 115.5, 0), 'R1704': (17.85, 114.9, 180),
    'R1701': (16.7, 118.9, 270), 'R1702': (16.7, 122.0, 270), 'C1702': (16.9, 116.5, 0),
    'C1701': (19.55, 122.9, 270), 'C1703': (22.6, 121.0, 0), 'C1705': (17.35, 126.1, 270),
    'R6101': (21.2, 101.95, 90),  # on the recovery rail's tap
}


def _power_copper():
    out = []
    t = lambda net, lay, w, *path: out.append(dict(net=net, layer=lay, w=w, path=[(round(x, 3), round(y, 3)) for x, y in path]))
    v = lambda net, d, dr, *xy: out.extend(dict(net=net, via=(round(x, 3), round(y, 3)), d=d, drill=dr) for x, y in xy)
    F, B, L3 = 'F.Cu', 'B.Cu', 'In2.Cu'
    VB, ET = 'VBAT_CROI_INPUT', 'ENERGY_TAP'
    # the 6 A path on L1 (SRC_6A, 4.0 mm: on L1 alone it meets 20 C at 6 A; L4, the brief's second layer, is GND
    # since D-22Nov.29). J101 and J102 to Q101's source pins; R1003 and C1002 sit on it
    t(VB, F, 4.0, (9.0, 147.8), (17.0, 147.8))
    t(VB, F, 4.0, (17.0, 149.6), (23.4, 149.6))
    t(VB, F, 4.0, (22.5, 150.0), (22.5, 156.6))                # J102's six VBAT pins
    t(VB, F, 1.2, (18.39, 147.2), (20.93, 147.2))              # Q101's source pins 1-3, 0.4 mm short of its gate
    t(VB, F, 0.2, (24.39, 145.2), (23.65, 145.2), (23.65, 147.9))   # U101's IN_SYS (pin 5)
    t(VB, F, 1.6, (4.95, 133.81), (8.0, 133.81))               # J101's pin, between its peg and its GND pin
    t(VB, F, 4.0, (9.0, 132.3), (9.0, 147.8))                  # J101 down the left side; TP42 sits on it
    # the UV divider's top (R1001) and Q102's source, north of Q101's tab, by L6
    t(VB, F, 0.3, (22.75, 137.22), (23.9, 137.2))
    t(VB, F, 0.3, (26.45, 139.57), (26.45, 140.2))
    v(VB, 0.45, 0.2, (23.9, 137.2), (26.45, 140.2), (23.6, 148.4))
    t(VB, B, 0.3, (23.9, 137.2), (23.6, 137.5), (23.6, 148.4))
    t(VB, B, 0.3, (26.45, 140.2), (24.0, 140.2), (23.6, 140.6))
    # D1002, the master-enable diode by J103, along the clear strip between the power parts and J102
    t(VB, F, 0.2, (25.0, 149.0), (55.6, 149.0), (55.6, 143.0), (56.95, 142.0))
    # Q101's tab (ENERGY_TAP) to the two fuses, C1004, C1005, U101's IN pins and R7104
    t(ET, F, 2.6, (15.4, 140.4), (21.0, 140.4))
    t(ET, F, 1.9, (15.0, 138.76), (20.9, 138.76))
    t(ET, F, 0.7, (13.4, 139.02), (15.0, 139.02))
    t(ET, F, 0.75, (22.3, 143.45), (24.35, 143.45))
    t(ET, F, 0.25, (22.3, 141.3), (28.6, 141.3), (29.83, 140.6))
    # the arm feeds (PYRO_RAIL, 2.0 mm): recovery's on L1, up the gap west of the LDO's column of parts and across to
    # J6101; staging's drops through three vias in its fuse's pad and runs on L6 to J6102, so the two never cross
    RF, SF = 'RECOVERY_ARM_FEED', 'STAGING_ARM_FEED'
    t(RF, F, 2.0, (16.05, 133.84), (16.05, 131.0), (14.4, 129.35), (14.4, 112.5), (9.1, 112.5))
    v(SF, 0.6, 0.3, (19.2, 133.9), (20.05, 133.9), (20.9, 133.9))
    t(SF, B, 2.0, (20.05, 133.9), (20.05, 129.0), (4.05, 129.0), (4.05, 125.76))
    # the corridor on L6 (D-22Nov.3, D-23Nov.2): recovery west, a 1.0 mm GND strip, staging east, each 0.55 mm from
    # the strip, north along the left edge, then east under the stamp row to the three links. The two GND loops (TP16,
    # TP23) sit on the strip; the rails step 0.9 mm out round them
    RA, SA = 'RECOVERY_ARMED_VBAT', 'STAGING_ARMED_VBAT'
    xr, xg, xs = 10.45, 12.5, 14.55
    yr, yg, ys = 33.3, 35.35, 37.4
    loops = (84.55, 64.4)                                      # TP23 and TP16, both at x 12.5

    def stepped(x0, dx, y_top, y_bottom):
        pts = [(x0, y_bottom)]
        for yc in loops:
            pts += [(x0, yc + 3.1), (x0 + dx, yc + 2.2), (x0 + dx, yc - 2.2), (x0, yc - 3.1)]
        return pts + [(x0, y_top)]
    t(RA, B, 2.0, (3.6, 112.15), (3.6, 109.9), (4.6, 108.9), (xr - 1.0, 108.9), (xr, 107.9),
      *stepped(xr, -0.9, yr + 2.0, 107.9)[1:], (xr + 2.0, yr), (39.1, yr))
    t(SA, B, 2.0, (4.05, 121.8), (xs - 1.0, 121.8), (xs, 120.8), *stepped(xs, 0.9, ys + 2.0, 120.8)[1:],
      (xs + 2.0, ys), (45.6, ys), (46.85, ys - 1.25), (46.85, 32.3), (47.4, 31.34))
    t('GND', B, 1.0, (xg, 106.9), (xg, yg + 1.0), (xg + 1.0, yg), (40.6, yg))
    v('GND', 0.45, 0.2, *[(xg, y) for y in (41, 50, 56, 69, 75, 82, 90, 98, 102, 106.9)], *[(x, yg) for x in (18, 22, 29)])
    # the links: each armed pad drops to its rail through vias 0.5 mm from every other net on every layer, the fire
    # logic's runs on L3 included. Channel 1's: one in the pad and three below
    t(RA, F, 0.95, (29.4, 31.34), (29.4, 32.2))
    t(RA, F, 0.5, (28.75, 32.5), (30.15, 32.5))
    v(RA, 0.6, 0.3, (29.4, 31.34), (28.75, 32.6), (29.4, 32.45), (30.15, 32.45))
    # channel 2's: two below, in the 2.5 mm between the fire logic's runs at x 37.5 and x 40.0 and clear of
    # PYRO1_FIRE's diagonal under the pad (so none in the pad)
    t(RA, F, 0.95, (38.4, 31.34), (38.75, 32.0), (38.75, 33.85))
    v(RA, 0.6, 0.3, (38.75, 33.3), (38.75, 34.0))
    # channel 3's: one in the pad and a column of three west of R6926, 0.5 mm east of PYRO2_FIRE's run (x 45.8)
    t(SA, F, 0.6, (47.4, 31.34), (46.85, 32.55), (46.85, 34.25))
    v(SA, 0.6, 0.3, (47.4, 31.34), (46.85, 32.55), (46.85, 33.4), (46.85, 34.25))
    # the taps, each divider's top resistor, 0.3 mm on L1 from a via on its rail; R6101's crosses the corridor on L3
    t(SA, F, 0.3, (xs, 99.6), (16.22, 99.6))
    v(SA, 0.45, 0.2, (xs, 99.6))
    v(RA, 0.45, 0.2, (xr, 103.6), (21.5, 103.9), (xr, 105.6))
    t(RA, L3, 0.3, (xr, 103.6), (21.2, 103.6), (21.5, 103.9))
    t(RA, F, 0.3, (21.2, 102.78), (21.5, 103.9))
    t(RA, F, 0.3, (xr, 105.6), (11.77, 105.6))                 # R8007
    return out



def _logic_feeds():
    """The logic feeds (D-23Nov.31): the shunt and its Kelvin pair, the protected feed to the input mux, the mux to
    the buck's two inputs and their loops, the buck's output to its loads, the held core to the flight LDO and its
    1000 uF, the flight LDO's block, and the buck's small pins. Widths: the class's 1.0 mm where there is room,
    narrower only into a pin (LOGIC_FEED carries 1.24 A at most)."""
    out = []
    t = lambda net, lay, w, *path: out.append(dict(net=net, layer=lay, w=w, path=[(round(x, 3), round(y, 3)) for x, y in path]))
    v = lambda net, d, dr, *xy: out.extend(dict(net=net, via=(round(x, 3), round(y, 3)), d=d, drill=dr) for x, y in xy)
    F, B, L3 = 'F.Cu', 'B.Cu', 'In2.Cu'
    VS, VP, LS, V4, CH, G = 'VBAT_SHUNT_IN', 'VBAT_PROTECTED', 'LOGIC_SELECTED', '4V_PRE', 'CORE_HELD_4V', 'GND'
    PL, FB, NR, PG = 'FLIGHT_3V3_PRELINK', 'FLIGHT_LDO_FB', 'FLIGHT_LDO_NR', 'FLIGHT_LDO_PG'
    # the shunt R7101: U101's two OUT pins into its outer pad. The Kelvin pair (the brief's template) leaves each pad's
    # inner edge at its middle, drops under the body and runs on L3, between the two GND planes, to the filter
    # resistors R7102 and R7103
    t(VS, F, 0.75, (28.5, 143.445), (30.1, 143.445))
    t(VS, F, 0.2, (30.85, 143.45), (31.55, 143.45), (32.05, 143.95))
    v(VS, 0.45, 0.2, (32.05, 143.95), (37.5, 144.45))
    t(VS, L3, 0.2, (32.05, 143.95), (37.0, 143.95), (37.5, 144.45))
    t(VS, F, 0.2, (37.5, 144.45), (38.42, 144.8))
    t(VP, F, 0.2, (35.75, 143.45), (35.05, 143.45), (34.55, 142.95))
    v(VP, 0.45, 0.2, (34.55, 142.95), (41.65, 142.6))
    t(VP, L3, 0.2, (34.55, 142.95), (41.3, 142.95), (41.65, 142.6))
    t(VP, F, 0.2, (41.65, 142.6), (43.2, 142.475))
    # the protected feed: out of the shunt's far pad at its top through two vias, north on L6 to two vias beside the
    # mux, into its IN1 pin and its capacitor C1102. R1007 (the eFuse's power-good divider) off the pad's bottom
    t(VP, F, 1.0, (36.5, 142.3), (36.5, 140.9), (37.4, 140.9))
    v(VP, 0.6, 0.3, (36.5, 140.9), (37.4, 140.9), (38.0, 128.4), (38.0, 129.3))
    t(VP, B, 1.0, (36.5, 140.9), (37.4, 140.9), (38.0, 140.3), (38.0, 128.4))
    t(VP, F, 0.6, (38.0, 129.3), (38.0, 127.55))
    t(VP, F, 0.4, (37.2, 127.55), (38.0, 127.55), (38.9, 127.3))
    t(VP, F, 0.2, (36.5, 145.0), (36.5, 145.5), (32.0, 145.5), (32.0, 146.0))
    # the mux's two OUT pins joined, west round its capacitor C1303's GND pad into C1303 and the buck's VIN2 pins; an
    # L3 link under the buck, two vias each end, to its other input capacitor C1304, the VIN1 pins and EN/SYNC
    t(LS, F, 0.4, (35.6, 126.85), (37.3, 126.85))
    t(LS, F, 0.5, (35.6, 126.85), (34.75, 126.85), (34.75, 124.6), (33.6, 124.6))
    t(LS, F, 0.9, (31.95, 124.7), (33.6, 124.7))
    t(LS, F, 0.6, (33.0, 123.45), (33.775, 123.45), (33.775, 124.5))
    v(LS, 0.6, 0.3, (33.0, 123.45), (33.775, 123.45), (24.75, 123.45), (25.55, 123.45))
    t(LS, L3, 1.0, (33.775, 123.45), (24.75, 123.45))
    t(LS, F, 0.6, (24.75, 123.45), (25.55, 123.45), (25.55, 124.2))
    t(LS, F, 0.9, (26.6, 124.7), (28.35, 124.7))
    t(LS, F, 0.25, (28.3, 123.58), (28.3, 124.5))
    # the loops' returns (TI: input capacitors tight between VIN and PGND): PGND pins 5-6 to C1304's GND pad and 16-17
    # to C1303's; vias in those pads and two in each of the buck's PGND centre pads (28, 29)
    t(G, F, 0.9, (28.35, 126.15), (27.2, 126.15), (26.5, 127.0))
    t(G, F, 0.9, (31.95, 126.15), (33.6, 126.15))
    v(G, 0.6, 0.3, (24.9, 127.45), (26.2, 127.45), (33.775, 126.15),
      (29.7, 124.75), (30.5, 124.75), (29.7, 125.95), (30.5, 125.95))
    # the buck's output: its VOUT pins either side of SW (pin 11, left bare: TI) down into C1305 and C1306, the
    # centre VOUT pad (30) tied in, pins 7-8 and 14-15 joined; two vias in each output capacitor's GND pad
    t(V4, F, 1.25, (29.105, 128.3), (29.105, 129.9))
    t(V4, F, 1.25, (31.105, 128.3), (31.105, 129.9))
    t(V4, F, 0.25, (29.6, 127.3), (29.6, 128.3))
    t(V4, F, 0.25, (30.6, 127.3), (30.6, 128.3))
    t(V4, F, 0.3, (28.33, 127.1), (28.33, 127.8))
    t(V4, F, 0.3, (31.87, 127.1), (31.87, 127.8))
    v(G, 0.6, 0.3, (27.8, 133.1), (29.1, 133.1), (31.1, 133.1), (32.4, 133.1))
    # west: C1305 to C1302, C1401 and the held core's IN bar (U1401.5), in by its right end
    t(V4, F, 0.6, (27.5, 129.9), (26.95, 128.55), (23.7, 128.55), (23.7, 126.2))
    t(V4, F, 0.3, (23.7, 126.2), (23.7, 125.9), (22.9, 125.9))
    t(V4, F, 0.4, (26.08, 128.55), (26.08, 129.4))
    t(V4, F, 0.4, (23.85, 128.55), (23.85, 129.4))
    # north-east: two vias at C1306, L6 up to the two branch switches U1601 and U1501, a via beside each IN pin
    t(V4, F, 1.0, (32.7, 130.15), (33.8, 130.15))
    v(V4, 0.6, 0.3, (33.8, 129.75), (33.8, 130.55), (35.7, 123.0), (38.6, 123.0))
    t(V4, B, 1.0, (33.8, 130.55), (33.8, 129.75), (34.9, 128.65), (34.9, 123.6), (35.5, 123.0), (38.6, 123.0))
    t(V4, F, 0.6, (35.7, 123.0), (35.7, 122.2))
    t(V4, F, 0.6, (38.6, 123.0), (39.5, 122.85))
    # the buck's VLDOIN (pin 22) and the divider's top (R1301) off that trunk by a thin L6 branch and two vias
    t(V4, B, 0.3, (34.9, 123.6), (34.9, 122.1), (34.4, 121.6), (31.25, 121.6), (31.25, 118.2), (28.35, 118.2))
    v(V4, 0.45, 0.2, (31.25, 121.6), (28.35, 118.2))
    t(V4, F, 0.25, (31.25, 121.6), (31.105, 122.4))
    t(V4, F, 0.25, (28.35, 118.2), (27.6, 118.9))
    # the buck's small pins. FB: R1301 and R1302 joined, short to pin 25. VCC: C1301 to pin 23 (its GND pad takes a
    # plane via of its own: TI puts it on PGND). AGND: pin 24 and the AGND pad (27) to the divider's and the RT
    # resistor's GND pads, and to PGND at one point, pad 27 to pad 28 (TI). RT: R1303 by L3 to pin 1
    t('BUCK_FB', F, 0.2, (27.6, 120.74), (29.1, 120.74))
    t('BUCK_FB', F, 0.2, (29.1, 120.9), (29.35, 121.6), (29.6, 121.85), (29.6, 122.4))
    t('BUCK_VCC', F, 0.25, (30.6, 120.9), (30.6, 122.4))
    t(G, F, 0.25, (30.105, 122.5), (30.105, 123.4))
    t(G, F, 0.4, (30.1, 123.5), (30.1, 124.5))
    t(G, F, 0.2, (30.105, 122.4), (30.105, 121.6), (29.875, 121.37), (29.875, 119.6), (29.4, 119.15))
    t(G, F, 0.2, (29.875, 119.925), (31.45, 119.925), (32.1, 119.74))
    t('BUCK_RT', F, 0.2, (32.1, 120.76), (32.85, 120.76))
    v('BUCK_RT', 0.45, 0.2, (32.85, 120.76), (27.45, 121.65))
    t('BUCK_RT', L3, 0.2, (32.85, 120.76), (28.0, 120.76), (27.45, 121.3), (27.45, 121.65))
    t('BUCK_RT', F, 0.2, (27.45, 121.65), (27.45, 122.25), (28.05, 122.92))
    # the held core: its OUT bar (U1401.6) out by its left end, north to the flight LDO's two IN pins and C1703, then
    # east of the LDO's output capacitor to the 1000 uF. EN (pin 7) sits between NR and GND, so it takes a via each end
    t(CH, F, 0.3, (21.0, 125.4), (20.4, 125.4))
    t(CH, F, 0.5, (20.4, 125.4), (20.4, 121.6))
    t(CH, F, 0.74, (20.25, 121.5), (20.25, 120.6))
    t(CH, F, 0.6, (20.4, 121.0), (22.1, 121.0))
    t(CH, F, 1.0, (22.1, 120.9), (22.1, 119.8), (24.4, 117.9), (24.4, 110.5))
    t(CH, F, 0.8, (18.3, 124.6), (20.2, 124.6))                # C1705
    t(CH, F, 0.2, (19.0, 120.7), (19.0, 121.5), (18.55, 122.0))
    v(CH, 0.45, 0.2, (18.55, 122.0), (20.4, 122.3))
    t(CH, B, 0.3, (18.55, 122.0), (20.4, 122.3))
    # the flight LDO (TI's TPS7A91 layout): OUT pins 1-2 straight into C1706; the link R1704 beside it, its
    # FLIGHT_3V3 end to L5 by two vias; the divider's top sensed at C1706 by a line of its own, C1702 on it; FB over
    # pins 4-5 and down the gap to the divider's middle; PG by a via at its pin; NR down to C1701; GND pins 4 and 6
    # to the thermal pad, three vias in it
    t(PL, F, 0.74, (20.25, 118.3), (20.25, 116.5))
    t(PL, F, 0.8, (18.9, 114.9), (19.9, 114.9))
    t('FLIGHT_3V3', F, 0.8, (17.0, 114.9), (17.0, 113.7))
    t('FLIGHT_3V3', F, 0.6, (16.75, 113.7), (17.55, 113.7))
    v('FLIGHT_3V3', 0.6, 0.3, (16.75, 113.7), (17.55, 113.7))
    t(PL, F, 0.2, (19.75, 115.78), (16.42, 115.78), (16.42, 117.9))
    t(FB, F, 0.15, (19.5, 118.3), (19.5, 117.0), (17.4, 117.0), (17.4, 116.6))
    t(FB, F, 0.15, (17.8, 117.0), (17.8, 120.45), (16.9, 120.45))
    t(FB, F, 0.3, (16.7, 119.8), (16.7, 121.1))
    t(PG, F, 0.2, (18.5, 118.3), (18.5, 117.75), (18.35, 117.55))
    v(PG, 0.45, 0.2, (18.35, 117.55))
    t(NR, F, 0.2, (19.5, 120.7), (19.55, 122.4))
    t(G, F, 0.24, (19.0, 118.4), (19.0, 119.2))
    t(G, F, 0.24, (18.5, 119.9), (18.5, 120.6))
    v(G, 0.45, 0.2, (18.95, 119.5), (19.5, 119.5), (20.05, 119.5))
    v(G, 0.45, 0.2, (19.55, 123.38))                            # C1701's GND pad
    # GND vias in C1706's GND pad and the 1000 uF's; C1705's sit at its pad's top edge, 0.5 mm clear of the staging
    # arm feed on L6 under its pad
    v(G, 0.6, 0.3, (23.2, 114.9), (23.2, 116.1), (16.9, 109.35), (18.0, 109.35))
    v(G, 0.45, 0.2, (16.6, 127.25), (17.5, 127.25), (18.4, 127.25))
    return out


POWER_COPPER = _power_copper() + _logic_feeds()

# the planes (D-22Nov.29, D-23Nov.2, D-23Nov.30): L2 and L4 GND whole; L5 FLIGHT_3V3, 1 mm in from the edge so the GND
# planes reach past it, with GND under the corridor, the arm feed and the strip (their L6 copper and 0.5 mm, the fire
# rule's gap: so no other L6 copper can cross into it). Filled by the build, last
PLANES = [
    dict(layer='In1.Cu', net='GND'),
    dict(layer='In3.Cu', net='GND'),
    dict(layer='In4.Cu', net='FLIGHT_3V3', inset=1.0),
    dict(layer='In4.Cu', net='GND', under=('PYRO_RAIL',), margin=0.5, priority=1, name='GND under the corridor'),
]
SOLID_PADS = ('J102', 'J101')     # their GND pins carry the 6 A return: no thermal relief (brief section 4)

# The hard copper's floor plan, as keep-outs for the budget run (stage C/D review, call 9; meter.py --budget): where
# stage C will draw it, each area with the copper's own clearance to other nets. Board mm, (x0, y0, x1, y1) boxes or
# (path, width) bands; layers L1 F.Cu, L3 In2.Cu, L6 B.Cu. Not modelled: the logic feeds (LOGIC_FEED), the USB and
# CAN pairs and the crystals, which are short or small.
BUDGET = [
    # the armed rails, the arm feeds and the 6 A path: drawn (spec.POWER_COPPER), on the board itself since 23 Nov
    # FIRE_LOGIC: drawn (spec.FIRE_LOGIC_L3 and its escapes), on the board itself since 23 Nov
    # RF lines (D-21Nov.25, D-22Nov.16) on L1 with their gaps and fences
    dict(name='GNSS line', layers=['F.Cu'], box=(60.4, 2.2, 68.3, 6.0)),
    dict(name='LoRa line', layers=['F.Cu'], box=(11.0, 4.2, 14.6, 16.8)),
    # the fire copper itself is drawn (spec.PYRO_COPPER) and on the board
]

# test points (stage B2 step 5): each aims for its net's route. These probe sensitive nodes, so they go in with their
# circuit, before the general parts, and their stub is 10 mm at most; every other one 20 mm (the brief's limits)
PROBES_WITH_CIRCUIT = ('BAT_BLOCK_GATE', 'ADC_PYRO1_CURRENT', 'ADC_PYRO2_CURRENT', 'ADC_PYRO3_CURRENT',
                       'ADC_PYRO1_CONTINUITY', 'ADC_PYRO2_CONTINUITY', 'ADC_PYRO3_CONTINUITY')
PROBE_STUB_MAX = (10.0, 20.0)
# placed right after the anchors, in this order [J]: the parts whose position the datasheets fix; and BZ9001, the
# sounder, which found no room once the pin swaps moved its driver (D-22Nov.25)
PRIORITY = ['U4606', 'U4504', 'D4501', 'Q6301', 'Q6401', 'Q6501',
            'Q101', 'U101', 'R7101', 'U7101', 'U1101', 'U1301', 'U1401', 'C1403', 'U1701', 'U1801', 'U1901',
            'Y201', 'Y202', 'Y401', 'U4402', 'D4401', 'BZ9001']
