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

# --- net classes (brief section 5; widths from IPC-2152, impedances from JLC's calculator)
def nc(name, track, clearance, **kw):
    return dict(name=name, track_width=track, clearance=clearance, via_diameter=kw.get('via_d', 0.6),
                via_drill=kw.get('via_drill', 0.3), diff_pair_width=kw.get('dp_w', 0.2), diff_pair_gap=kw.get('dp_gap', 0.25),
                priority=kw.get('priority', 10))

NETCLASSES = [
    nc('Default', 0.15, 0.15, priority=2147483647),
    nc('SRC_6A', 4.0, 0.2, priority=1),
    nc('PYRO_RAIL', 2.0, 0.2, priority=2),        # 0.5 mm to other nets: custom rule below
    nc('FIRE', 1.0, 0.2, priority=3),
    nc('FIRE_LOGIC', 0.15, 0.2, priority=4),
    nc('LOGIC_FEED', 1.0, 0.2, priority=5),
    nc('RAIL_3V3', 0.4, 0.15, priority=6),
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
            + [('LOGIC_FEED', n) for n in ('VBAT_SHUNT_IN', 'VBAT_PROTECTED', 'LOGIC_SELECTED', '4V_PRE', 'CORE_HELD_4V')]
            + [('RAIL_3V3', n) for n in RAILS]
            + [('RF50', n) for n in ('GNSS_RF', 'LORA_RF_SUBG')]
            + [('USB_DIFF', n) for n in ('USB_DP', 'USB_DM', 'USB_DP_CONN', 'USB_DM_CONN')]
            + [('CAN_DIFF', n) for n in ('CAN_H', 'CAN_L', 'CAN2_H', 'CAN2_L')]
            + [('GND', 'GND')])

RULES = {  # board minimums, above JLC's (PCB capabilities, read 21 Nov) [J]
    'min_clearance': 0.15, 'min_track_width': 0.15, 'min_via_diameter': 0.5, 'min_through_hole_diameter': 0.3,
    'min_via_annular_width': 0.1, 'min_hole_clearance': 0.25, 'min_hole_to_hole': 0.25,
    'min_copper_edge_clearance': 0.3, 'min_text_height': 1.0, 'min_text_thickness': 0.15,
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
(rule "Fire copper keeps 0.5 mm from other nets, except between pads of one part"
  (condition "(A.NetClass == 'FIRE' || A.NetClass == 'FIRE_LOGIC' || A.NetClass == 'PYRO_RAIL') && A.Net != B.Net && !(A.Type == 'Pad' && B.Type == 'Pad' && A.Parent.Reference == B.Parent.Reference)")
  (constraint clearance (min 0.5mm)))
(rule "Fire logic leaves U201's pins at its class clearance, inside U201's courtyard only (D-22Nov.26)"
  (condition "A.NetClass == 'FIRE_LOGIC' && A.enclosedByArea('U201_ESCAPE') && A.Net != B.Net")
  (constraint clearance (min 0.2mm)))
(rule "RF lines take no via (D-21Nov.25)"
  (condition "A.Type == 'Via' && A.NetClass == 'RF50'")
  (constraint disallow via))
(rule "Pads of one part keep the maker's land-pattern spacing, down to the 0.15 mm board minimum"
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
ESCAPE_AREAS = ['U201']       # named rule areas on U201's courtyard, for the fire-logic waiver (D-22Nov.26)
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
    'U6304': (32.5, 24.35, 270),             # channel high sides in a row behind J6601, OUT pins (5-7) forward,
    'U6404': (41.5, 24.35, 270),             #   VS pins (8-10) aft toward the armed rails; at 24.35 (was 24.0) their
    'U6504': (50.5, 24.35, 270),             #   refs clear J6601's name behind the capacitor row (D-22Nov.28)
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
SILK_NAME_GAP = {'J6601': 1.6}
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
    dict(rule='supply_caps', ic='U201', nets=('FLIGHT_VCAP',), value='2.2u', mm=2.0,
         src=f'{_SWEEP}: VCAP capacitors within 2 mm, one at each VCAP pin; D-23Nov.1'),
    dict(rule='supply_caps', ic='U401', nets=('COMMS_3V3',), value='100n', mm=3.0,
         src=f'{_SWEEP}: one 100 nF per supply pin, on its side; 3 mm [J]; D-23Nov.1'),
    dict(rule='supply_caps', ic='U401', nets=('COMMS_VDDA',), value='100n', mm=3.0,
         src=f'{_SWEEP}: one 100 nF per supply pin; 3 mm [J]; D-23Nov.1'),
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
