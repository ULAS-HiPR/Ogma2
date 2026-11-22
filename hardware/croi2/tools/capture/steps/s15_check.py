"""Check for step 15: only J101's footprint changes (none -> Ogma2:105311-1102); no pin change, no new ERC finding.
Then the footprint itself against the drawing's numbers, and its clearances against the board minimums."""
import math
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture as C
import s15_j101 as S

if __name__ == '__main__':
    C.export('s15')
    ca, _ = C.load_net('s14')
    changed = {('J101', 'fp'): (ca['J101']['fp'], S.FIELDS['Footprint'])}
    rep = C.check('s14', 's15', {}, expect_added=[], expect_removed=[], expect_changed=changed)
    fixed, new, counts = C.erc_delta('s14', 's15')
    print('problems:', rep['problems'] or 'none', '| ERC fixed:', fixed, 'new:', new)
    assert not rep['problems'] and not new and not fixed

    t = (S.LIB / 'Ogma2.pretty' / f'{S.NAME}.kicad_mod').read_text()
    pads = [(m[0], m[1], float(m[2]), float(m[3]), float(m[4]), float(m[5])) for m in re.findall(
        r'\(pad "([^"]*)" (\w+) circle\s+\(at ([-\d.]+) ([-\d.]+)\)\s+\(size ([-\d.]+) [-\d.]+\)\s+\(drill ([-\d.]+)\)', t)]
    by = lambda n: [p for p in pads if p[0] == n]
    (p1,), (p2,), clips, (peg,) = by('1'), by('2'), by('MP'), by('')
    drawing = [
        ('pin pitch 2.50', abs(p2[3] - p1[3]) - 2.50),
        ('pin holes D1.20', p1[5] - 1.20), ('', p2[5] - 1.20),
        ('clip holes D1.60, C = 6.84 apart', clips[0][5] - 1.60), ('', clips[1][5] - 1.60),
        ('', abs(clips[1][3] - clips[0][3]) - 6.84), ('clips centred on the pins', (clips[0][3] + clips[1][3]) / 2 - (p1[3] + p2[3]) / 2),
        ('clips on the row', clips[0][2] - p1[2]), ('', clips[1][2] - p1[2]),
        ('peg D1.30, unplated', peg[5] - 1.30), ('peg 1.34 off the row', abs(peg[2] - p1[2]) - 1.34),
        ('peg midway', peg[3] - (p1[3] + p2[3]) / 2),
    ]
    bad = [(k, round(v, 4)) for k, v in drawing if abs(v) > 1e-6]
    assert peg[1] == 'np_thru_hole' and all(c[1] == 'thru_hole' for c in clips)
    latch = re.findall(r'\(start (-4\.6) ', t)
    assert latch and peg[2] < 0, 'the peg must sit on the latch side (-x)'

    def edge_gap(a, b, ra, rb):
        return math.hypot(a[2] - b[2], a[3] - b[3]) - ra - rb
    copper = [(p1, p2, '1-2'), (p1, clips[0], '1-clip'), (p2, clips[1], '2-clip')]
    gaps = {k: round(edge_gap(a, b, a[4] / 2, b[4] / 2), 3) for a, b, k in copper}
    gaps |= {'1-peg hole': round(edge_gap(p1, peg, p1[4] / 2, peg[5] / 2), 3), '2-peg hole': round(edge_gap(p2, peg, p2[4] / 2, peg[5] / 2), 3)}
    holes = {'1-peg': round(edge_gap(p1, peg, p1[5] / 2, peg[5] / 2), 3), '1-clip': round(edge_gap(p1, clips[0], p1[5] / 2, clips[0][5] / 2), 3)}
    rings = {'pin': round((p1[4] - p1[5]) / 2, 3), 'clip': round((clips[0][4] - clips[0][5]) / 2, 3)}
    print('drawing mismatches:', bad or 'none')
    print('copper gaps (mm):', gaps, '| hole to hole:', holes, '| annular rings:', rings)
    # board minimums (spec.RULES, from JLC's capabilities read 21 Nov): pad-to-pad in one part 0.15 (the DRU), copper to
    # hole 0.25, hole to hole 0.25, ring 0.1 (vias; we keep 0.25 on pads)
    assert not bad and min(v for k, v in gaps.items() if 'hole' not in k) >= 0.15 and min(v for k, v in gaps.items() if 'hole' in k) >= 0.25
    assert min(holes.values()) >= 0.25 and min(rings.values()) >= 0.25
    print('step 15 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;", dict(counts))
