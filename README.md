# Ogma 2

HiPR's workhorse flight computer: **Burrito** (Croí2), the flight board, and
**Churro** (Foinse2), an MCU-less power board. **Fajita** is the separate
propulsion controller. The capture specification is ready; capture waits for
Seán's go-ahead after the 3 November review, and native CAD holds the
8 September draft. Nothing is built or flown yet.

**Start here:** [system tour](docs/architecture/system-tour.md) →
[decisions](decisions.md) → the chapter for your block.

## Read in this order

1. [System tour](docs/architecture/system-tour.md): boards, power, data, connectors with photos.
2. [Decisions](decisions.md): what is settled, what is proposed, what is open.
3. [Current system](current-system.md): what is true now.
4. [Requirements](docs/requirements/README.md): Burrito's, frozen 21 Nov; Churro's, draft. Then the [behaviour map](docs/architecture/behaviour-map.md).
5. [Block chapters](docs/architecture/README.md): one page per block, plus the capture specification.
6. [Hardware](hardware/README.md) for CAD, or the [firmware interface](docs/firmware-interface.md) for firmware.
7. [Verification](docs/architecture/11-verification.md): release gates and what has to pass.

Don't start at the project log or `docs/archive/`.

## Repository

| Path | Contents |
| --- | --- |
| `hardware/croi2/`, `hardware/foinse2/` | Native KiCad projects, tracked directly; no submodules |
| `docs/requirements/` | Requirements with their sources, mechanisms and verification; the dated rules sweep |
| `docs/architecture/` | Block chapters, behaviour map, capture specification, justifications |
| `interfaces/` | Owned contracts: power, flight fault, reset, vehicle boundary |
| `docs/archive/` | Superseded reviews, studies and history: evidence, not instructions |
| `project-log.md` | Append-only history |

Use branches and bounded pull requests. `main` is reviewed truth once merged.
Native CAD, contracts and measurements outrank prose. No raw transcripts,
private correspondence, generated dumps or render trees. No licence selected;
Rev 1 is a separate project.
