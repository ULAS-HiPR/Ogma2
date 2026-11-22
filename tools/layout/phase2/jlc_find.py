"""Find parts in a local jlcparts scrape (https://github.com/yaqwsx/jlcparts, gh-pages data).

    python3 jlc_find.py DATA_DIR REGEX [REGEX ...]

Prints LCSC number, MPN, stock, first price break and description for every
in-stock part whose MPN matches a regex (case-insensitive). Third-party data:
confirm each LCSC number on jlcpcb.com before ordering.
"""
import sys, os, re, gzip, json

data, pats = sys.argv[1], [re.compile(p, re.I) for p in sys.argv[2:]]
pre = [re.compile(p.lstrip('^'), re.I) for p in sys.argv[2:]]   # raw-line prefilter, unanchored
for fn in sorted(os.listdir(data)):
    if not fn.endswith('.jsonl.gz'):
        continue
    with gzip.open(os.path.join(data, fn), 'rt') as f:
        head = json.loads(f.readline())
        i_l, i_m, i_d, i_p, i_s = head['lcsc'], head['mfr'], head['description'], head['price'], head['stock']
        for line in f:
            if not any(p.search(line) for p in pre):
                continue
            r = json.loads(line)
            if any(p.search(r[i_m]) for p in pats):
                price = r[i_p][0]['price'] if r[i_p] else None
                print(f"{r[i_l]:>10} {r[i_m]:<26} stock {r[i_s]:>7} ${price} | {r[i_d][:90]}")
