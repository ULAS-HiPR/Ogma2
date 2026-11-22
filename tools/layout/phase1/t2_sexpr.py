"""T2: S-expression round trip and edits on TB1, checked by loading in pcbnew."""
import sys, hashlib
sys.path.insert(0, '/work/hardware/croi2/tools/capture')
import sexpr as S
import pcbnew as K
src = '/lab/tb1/tb1.kicad_pcb'
text = open(src).read()
tree = S.parse(text)
rt = S.emit(tree) + '\n'
print('byte-identical round trip:', rt == text, len(rt), len(text))
open('/lab/tb1/t2-rt.kicad_pcb', 'w').write(rt)
# semantic: pcbnew saves both the same way?
for name in ('tb1', 't2-rt'):
    b = K.LoadBoard(f'/lab/tb1/{name}.kicad_pcb'); K.SaveBoard(f'/lab/tb1/{name}-resaved.kicad_pcb', b)
h = [hashlib.sha256(open(f'/lab/tb1/{n}-resaved.kicad_pcb', 'rb').read()).hexdigest()[:12] for n in ('tb1', 't2-rt')]
print('pcbnew re-save identical:', h[0] == h[1], h)
# edits by text: stackup, move U201, a segment and a via
setup = next(x for x in tree if isinstance(x, list) and x and x[0] == 'setup')
A = S.Atom
stack = [A('stackup')]
for name, typ, th in (('F.SilkS', 'Top Silk Screen', None), ('F.Mask', 'Top Solder Mask', '0.01'), ('F.Cu', 'copper', '0.035'),
                      ('dielectric 1', 'prepreg', '0.1'), ('In1.Cu', 'copper', '0.0175'), ('dielectric 2', 'core', '1.265'),
                      ('In2.Cu', 'copper', '0.0175'), ('dielectric 3', 'prepreg', '0.1'), ('B.Cu', 'copper', '0.035'),
                      ('B.Mask', 'Bottom Solder Mask', '0.01'), ('B.SilkS', 'Bottom Silk Screen', None)):
    lay = [A('layer'), name, [A('type'), typ]]
    if th: lay.append([A('thickness'), A(th)])
    if typ in ('prepreg', 'core'): lay += [[A('material'), 'FR4'], [A('epsilon_r'), A('4.05')], [A('loss_tangent'), A('0.02')]]
    stack.append(lay)
setup.insert(1, stack)
fp = next(x for x in tree if isinstance(x, list) and x and x[0] == 'footprint' and
          any(isinstance(p, list) and p[:3] == [A('property'), 'Reference', 'U201'] for p in x))
at = next(x for x in fp if isinstance(x, list) and x and x[0] == 'at')
at[1], at[2] = A('127'), A('81')
net = next(x for x in tree if isinstance(x, list) and x and x[0] == 'net' and x[2] == 'GND')
tree.append([A('segment'), [A('start'), A('105'), A('55')], [A('end'), A('110'), A('55')], [A('width'), A('0.3')],
             [A('layer'), 'B.Cu'], [A('net'), net[1]]])
tree.append([A('via'), [A('at'), A('110'), A('55')], [A('size'), A('0.6')], [A('drill'), A('0.3')],
             [A('layers'), 'F.Cu', 'B.Cu'], [A('net'), net[1]]])
open('/lab/tb1/t2-edit.kicad_pcb', 'w').write(S.emit(tree) + '\n')
b = K.LoadBoard('/lab/tb1/t2-edit.kicad_pcb')
u = b.FindFootprintByReference('U201').GetPosition()
st = b.GetDesignSettings()
print('edited board loads; U201 at', K.ToMM(u.x), K.ToMM(u.y), '; tracks', len(b.GetTracks()), '; thickness', K.ToMM(st.GetBoardThickness()))
