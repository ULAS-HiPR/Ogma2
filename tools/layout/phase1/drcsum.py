import json, sys
from collections import Counter
d = json.load(open(sys.argv[1]))
ign = {'lib_footprint_issues', 'lib_footprint_mismatch'}
v = Counter(x['type'] for x in d['violations'] if x['type'] not in ign)
print('violations', dict(v), '| unconnected', len(d['unconnected_items']), '| parity', len(d.get('schematic_parity', [])))
for x in d['violations']:
    if x['type'] not in ign | {'silk_overlap', 'silk_over_copper', 'silk_edge_clearance'} and x['severity'] == 'error':
        print('  ', x['type'], '|', x['description'][:90], '|', ' ; '.join(i['description'][:60] for i in x['items']))
