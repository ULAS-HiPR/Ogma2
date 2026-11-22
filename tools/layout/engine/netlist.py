"""KiCad XML netlist -> components and nets (plain data, no KiCad import)."""
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass
class Comp:
    ref: str
    value: str
    fp: str                     # 'Lib:Name'
    sheet: str                  # '/05-can/'
    path: str                   # '/<sheet uuid>/<symbol uuid>'
    fields: dict = field(default_factory=dict)
    dnp: bool = False
    exclude_bom: bool = False


def load(path):
    root = ET.parse(path).getroot()
    comps = {}
    for c in root.findall('components/comp'):
        sp = c.find('sheetpath')
        props = {p.get('name'): p.get('value') for p in c.findall('property')}
        fields = {f.get('name'): (f.text or '') for f in c.findall('fields/field')}
        comps[c.get('ref')] = Comp(
            ref=c.get('ref'), value=c.findtext('value') or '', fp=c.findtext('footprint') or '',
            sheet=sp.get('names'), path=sp.get('tstamps') + (c.findtext('tstamps') or '').strip(),
            fields=fields, dnp='dnp' in props, exclude_bom='exclude_from_bom' in props)
    nets = {}
    for n in root.findall('nets/net'):
        nets[n.get('name')] = [(x.get('ref'), x.get('pin')) for x in n.findall('node')]
    return comps, nets


def subset(comps, nets, sheets):
    """Components on the given sheets; nets restricted to them, keeping nets with 2+ pads."""
    keep = {r: c for r, c in comps.items() if any(c.sheet.startswith(s) for s in sheets)}
    sub = {}
    for name, nodes in nets.items():
        k = [(r, p) for r, p in nodes if r in keep]
        if k:
            sub[name] = k
    return keep, sub
