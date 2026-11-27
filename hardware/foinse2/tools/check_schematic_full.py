"""Churro native-netlist helpers and compatible full-check entrypoint.

Boundary checks live in check_foinse_schematic; this board has no MCUs.
Generated pin expectations are not analog or hardware qualification.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def node_map(root):
    out={}
    for net in root.findall('nets/net'):
        for pin in net.findall('node'):
            key=(pin.get('ref'),pin.get('pin'))
            assert key not in out,('duplicate pin',key)
            out[key]=net.get('name').rsplit('/',1)[-1]
    return out


def verify(root,expected):
    actual=node_map(root);count=0
    for ref,pins in expected.items():
        if ref.startswith('#'):continue  # Power symbols are absent from netlist BOM.
        for pin,net in pins.items():
            found=actual.get((ref,pin))
            if net is None:
                assert found is None or found.startswith('unconnected-'),(ref,pin,'NC',found)
            else:
                assert found==net,(ref,pin,net,found)
            count+=1
    assert set(actual).issubset({(r,p) for r,ps in expected.items() for p in ps}), 'Unexpected pins'
    return actual,count


def check(project, netlist, erc):
    # Import after verify is defined: the board-specific checker uses that helper.
    from check_foinse_schematic import check as check_foinse
    return check_foinse(project, netlist, erc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('project', type=Path)
    parser.add_argument('netlist', type=Path)
    parser.add_argument('erc', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = check(args.project, args.netlist, args.erc)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'checks'}))
