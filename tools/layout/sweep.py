"""Length sweep (execution brief B3): build the board at each length into scratch, then tabulate what each build
reports. Never writes the repository's board.

    python3 tools/layout/sweep.py croi2 180 140 5 /cap/sweep     # inside the chroot: builds; prints the table

Per length: unplaced parts and marks, density per band (courtyard area over band area), the densest band, JLC
spacing breaches, parts grown out of their regions, whether the back's art fits and what it dropped, and the
error if the build stopped."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(board, lengths, out):
    rows = []
    for L in lengths:
        d = Path(out) / str(L)
        r = subprocess.run([sys.executable, str(HERE / 'build.py'), board, '--to', 'place', '--length', str(L), '--out', str(d)],
                           capture_output=True, text=True)
        rep = json.loads((d / 'build.json').read_text()) if r.returncode == 0 else None
        err = None if rep else (r.stderr.strip().splitlines() or ['?'])[-1]
        rows.append((L, rep, err))
    return rows


def table(rows):
    bands = None
    out = []
    for L, rep, err in rows:
        if rep is None:
            out.append(f'| {L} | build stopped: {err} | | | | | |')
            continue
        d = rep['density_by_band']
        bands = bands or list(d)
        art = rep.get('art_error') or ', '.join(rep.get('art', {}).get('misses', [])) or 'fits'
        out.append(f"| {L} | {len(rep['unplaced'])} {' '.join(rep['unplaced'])} | {' '.join(rep.get('marks_unplaced', [])) or '-'} | "
                   + ' / '.join(f'{d[b]:.3f}' for b in bands) + f" | **{max(d.values()):.3f}** | {len(rep['jlc_spacing_violations'])} | "
                   f"{len(rep['spills'])} | {art} |")
    head = ['| Length (mm) | Unplaced parts | Unplaced marks | Density per band (' + ', '.join(bands or []) + ') | Densest | JLC spacing breaches | Grown out of region | Back art |',
            '| --- | --- | --- | --- | --- | --- | --- | --- |']
    return '\n'.join(head + out)


if __name__ == '__main__':
    board, hi, lo, step, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    rows = run(board, list(range(hi, lo - 1, -step)), out)
    print(table(rows))
