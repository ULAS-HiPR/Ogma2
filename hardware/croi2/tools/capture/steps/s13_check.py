"""Check for step 13: 47 test points renamed, each new ref on its old ref's net; nothing else changes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture as C
from s13_tp_numbers import MAP

if __name__ == '__main__':
    C.export('s13')
    _, pa = C.load_net('s12')
    expect = {**{(o, '1'): None for o in MAP}, **{(n, '1'): pa[(o, '1')] for o, n in MAP.items()}}
    rep = C.check('s12', 's13', expect, expect_added=sorted(MAP.values()), expect_removed=sorted(MAP), expect_changed={})
    fixed, new, counts = C.erc_delta('s12', 's13')
    print('problems:', rep['problems'] or 'none', '| ERC fixed:', fixed, 'new:', new)
    assert not rep['problems'] and not new
    print('step 13 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;", dict(counts))
