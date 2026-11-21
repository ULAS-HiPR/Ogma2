"""Check for step 5: bus 1's J501 and B-39 changes listed; bus 2 derived from bus 1 by the reference
and net maps (every bus-2 pin must sit on the mapped twin of its bus-1 pin's net); ERC closures."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture as C
from s05_can import REF_MAP, NET_MAP

REF = '/05-can/CAN_REF'
CLOSES = {"Global Label 'CAN2_TX'", "Global Label 'CAN2_RX'"}

if __name__ == '__main__':
    C.export('s05')
    ca, pa = C.load_net('s04')
    cb, pb = C.load_net('s05')
    mid1 = pb[('R516', '2')]
    assert pb[('F501', '1')] == mid1 and mid1.startswith('Net-'), mid1
    expect = {('J501', '3'): REF, ('J501', '4'): 'NC', ('J501', '5'): 'NC', ('J501', '6'): 'NC',
              ('R516', '1'): REF, ('R516', '2'): mid1, ('F501', '1'): mid1, ('F501', '2'): 'GND'}
    # bus 2: each copied pin takes its bus-1 twin's net, mapped; the shared-net pull-up R505 is not copied
    def twin(net):
        if net.startswith('/05-can/'):
            return '/05-can/' + NET_MAP.get(net[8:], net[8:])
        if net.startswith('Net-('):
            return None                                   # auto-named: checked by membership below
        return NET_MAP.get(net, net)
    autos = {}
    for (ref, pin), net in pb.items():
        if ref in REF_MAP and REF_MAP[ref]:
            new = (REF_MAP[ref], pin)
            want = twin(net)
            if want is None:
                autos.setdefault(net, set()).add(new)
                want = pb.get(new)
            expect[new] = want
    for net, members in autos.items():                  # auto-named bus-1 nets map to one bus-2 net each
        nets2 = {pb.get(m) for m in members}
        assert len(nets2) == 1 and {k for k, v in pb.items() if v in nets2} == members, (net, members, nets2)
    added = sorted({r for r in REF_MAP.values() if r} | {'R516', 'F501'})
    changed = {('J501', 'value'): ('JST GH / 3-way', 'G125-MS10605M2P'),
               ('J501', 'fp'): ('Ogma2:BM03B-GHS-TBT_LF__SN_', 'Ogma2:G125-MS10605M2P')}
    rep = C.check('s04', 's05', expect, expect_added=added, expect_changed=changed)
    fixed, new, counts = C.erc_delta('s04', 's05')
    print('problems:', rep['problems'] or 'none')
    print('fixed:', fixed); print('new:', new)
    assert not rep['problems'] and {x[3] for x in fixed} == CLOSES and not new
    print('step 5 ok:', rep['components'], rep['pins'], f"{rep['pin_changes']} pin changes;",
          f'ERC closed {len(fixed)}, added 0;', dict(counts))
