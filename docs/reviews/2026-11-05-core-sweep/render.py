"""Re-render this sweep's diagrams from the docs' own Mermaid.

Run from anywhere: python3 docs/reviews/2026-11-05-core-sweep/render.py
Needs the Mermaid CLI (mmdc). PNGs land in diagrams/ and aren't committed.
"""
import pathlib
import re
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / 'diagrams'

# (source file, index of its mermaid block) -> output name, in sweep order.
PLAN = {
    ('docs/architecture/system-tour.md', 0): '01-vehicle',
    ('docs/architecture/system-tour.md', 1): '01-inside-burrito',
    ('docs/architecture/08-foinse-can.md', 0): '02-churro-power',
    ('docs/architecture/08-foinse-can.md', 1): '02-churro-temperature',
    ('interfaces/power-contract.md', 0): '02-source-dependencies',
    ('docs/architecture/system-tour.md', 2): '03-power-overview',
    ('docs/architecture/02-power.md', 0): '03-burrito-battery-to-everything',
    ('docs/architecture/02-power.md', 1): '03-burrito-regulated-domains',
    ('docs/architecture/01-mcus.md', 0): '04-processors',
    ('docs/architecture/07-sensors-logging.md', 0): '05-sensors-recording',
    ('docs/architecture/03-energetic-outputs.md', 0): '06-pyro-outputs',
    ('docs/architecture/03-energetic-outputs.md', 1): '06-pyro-one-channel',
    ('docs/architecture/04-servos.md', 0): '07-servos',
    ('docs/architecture/10-recovery-logic.md', 0): '08-recovery-states',
    ('docs/architecture/08-foinse-can.md', 2): '09-can-today',
    ('docs/architecture/06-gnss-radio.md', 0): '10-gnss-radio',
    ('docs/architecture/05-service-status-time.md', 0): '10-service-status-time',
    ('docs/architecture/09-connectors-arming.md', 0): '11-connectors-arming',
    ('docs/architecture/11-verification.md', 0): '12-verification',
}


def render(source: str, name: str, work: pathlib.Path) -> None:
    mmd = work / f'{name}.mmd'
    mmd.write_text(source)
    subprocess.run(['mmdc', '-i', str(mmd), '-o', str(OUT / f'{name}.png'),
                    '-b', 'white', '-w', '1200', '-s', '2'],
                   check=True, capture_output=True, timeout=120)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp)
        for (path, index), name in PLAN.items():
            blocks = re.findall(r'```mermaid\n(.*?)```', (ROOT / path).read_text(), re.S)
            render(blocks[index], name, work)
        render((HERE / 'system-5nov.mmd').read_text(), '01-system-5nov', work)
    print(f'{len(PLAN) + 1} diagrams in {OUT}')


if __name__ == '__main__':
    main()
