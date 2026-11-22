"""Step 13: test points renumbered TP1-TP47 fore to aft (D-22Nov.9).

Seán picked TP1-TPn, fore to aft, so every silkscreen label is short and the numbers rise from the antenna
end to J102. The order comes from Burrito's placement at 80 x 180 mm (D-22Nov.10): test points sorted by
2.5 mm rows of y, then by x. The placer sizes every test point's label box for 'TP00', and places test
points last in an order set by what each probes, so renumbering them can't move them (checked after the
rebuild). Renames refs only: references, instance paths and any note that names one. No net changes.
Edits the sheets in place (run from a clean checkout).
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kicadsch as K

BOARD = Path(__file__).resolve().parents[3]
MAP = {'TP9508': 'TP1', 'TP9503': 'TP3', 'TP4601': 'TP2', 'TP9520': 'TP7', 'TP9522': 'TP10', 'TP9521': 'TP9', 'TP9518': 'TP6', 'TP9502': 'TP8', 'TP9523': 'TP5', 'TP2301': 'TP17', 'TP9519': 'TP11', 'TP203': 'TP12', 'TP202': 'TP13', 'TP204': 'TP14', 'TP9507': 'TP15', 'TP201': 'TP19', 'TP2304': 'TP16', 'TP205': 'TP18', 'TP9517': 'TP4', 'TP9524': 'TP22', 'TP9505': 'TP20', 'TP9525': 'TP21', 'TP4204': 'TP23', 'TP4201': 'TP24', 'TP9516': 'TP32', 'TP1401': 'TP27', 'TP501': 'TP34', 'TP1901': 'TP35', 'TP1801': 'TP31', 'TP9512': 'TP28', 'TP9501': 'TP30', 'TP9506': 'TP29', 'TP9511': 'TP33', 'TP9514': 'TP38', 'TP9515': 'TP26', 'TP1701': 'TP25', 'TP1301': 'TP37', 'TP1303': 'TP36', 'TP1302': 'TP39', 'TP1001': 'TP42', 'TP1003': 'TP43', 'TP1002': 'TP46', 'TP9513': 'TP44', 'TP9510': 'TP45', 'TP9504': 'TP40', 'TP1004': 'TP41', 'TP9509': 'TP47'}
WORD = re.compile(r'\bTP\d+\b')


def rename(s):
    return WORD.sub(lambda m: MAP.get(m.group(0), m.group(0)), s)


def build():
    done = set()
    for f in sorted(BOARD.glob('*.kicad_sch')):
        t = K.load(f)
        hit = False
        for node in K.walk(t, 'property'):
            if isinstance(node[2], str) and WORD.search(node[2]):
                new = rename(node[2])
                if new != node[2]:
                    if node[1] == 'Reference':
                        done.add(node[2])
                    node[2], hit = new, True
        for node in K.walk(t, 'reference'):
            if node[1] in MAP:
                node[1], hit = MAP[node[1]], True
        for node in K.children(t, 'text'):
            if WORD.search(node[1]):
                new = rename(node[1])
                if new != node[1]:
                    node[1], hit = new, True
        if hit:
            K.save(t, f)
    assert done == set(MAP), sorted(set(MAP) ^ done)
    return done


if __name__ == '__main__':
    print('step 13:', len(build()), 'test points renumbered')
