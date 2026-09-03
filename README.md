# Ogma 2 flight computer

Hardware, firmware, architecture, interfaces, and qualification planning for
HiPR's second-generation flight-computer platform.

No Ogma 2 schematic or PCB exists yet. This repository currently records the
accepted architecture, the evidence behind it, the open decisions, and the
tests required before parts or layouts are frozen.

## Start here

1. [Current system](current-system.md): canonical short architecture, accepted
   decisions, open questions, and immediate sequence.
2. [Kármán-line mission hardening report](docs/karman-line-mission-hardening-report.md):
   deep design study covering mission duration, error correction, MCU choice,
   power, isolation, interfaces, connectors, storage, sensing, packaging, and
   qualification.
3. [Ogma, Foinse, and propulsion boundary](interfaces/ogma-foinse-propulsion-boundary.md):
   owned vehicle authority, power, and CAN boundary.
4. [Design evidence](sources/README.md): curated CATS Vega, Fluctus, and CATS
   Configurator references and the decision-relevant Ogma Rev 1 evidence package.
5. [Project log](project-log.md): append-only chronology; newest entries are at
   the end.

## Current architecture

Ogma 2 is one accessible flight-computer PCB with two non-redundant MCUs. The
flight MCU owns sensing, estimation, flight state, local logging, three energetic
channels, and two servo channels. The communications MCU owns GNSS, LoRa,
telemetry buffering, and normal USB-facing work. Foinse 2 remains a separate
vehicle-specific power board. External CAN exists only for named independent
vehicle systems, currently the self-governing liquid-propulsion controller.

The space-shot requirement is one bounded suborbital sortie to at least 100 km
near apogee followed by descent, recovery, and retained local evidence. It is not
an orbital-lifetime requirement. Exact mission envelope, parts, schematics,
board geometry, and qualification levels remain open where the current-system
document says so.

## Directory map

```text
AGENTS.md                    project instructions
README.md                    reader entry point
current-system.md            stable current architecture
project-log.md               append-only chronology

docs/
  README.md
  karman-line-mission-hardening-report.md
                              deep mission-hardening design study

interfaces/
  README.md
  ogma-foinse-propulsion-boundary.md
                              owned cross-system boundary

sources/
  README.md                   source authority and inclusion rule
  project/ogma-rev1/          flight closure, requirements, plots, and checklists
  inspiration/
    hardware-comparison/      four current CATS/Fluctus hardware references
    cats-configurator/        seven selected operator-interface references
```

Hardware CAD, firmware, host tooling, tests, fixtures, and controlled interface
definitions should enter this same repository when they exist. Their live
implementation and measured results outrank prose.

## Repository boundary

This repository contains the active material required to understand, design,
review, build, and qualify Ogma 2. It excludes raw model output, duplicate
screenshots, machine metadata, broad unsynthesised research, temporary renders,
and superseded working files. Those remain in Seán's local sibling `archive/`
and are not required for a clean clone.

Ogma Rev 1 and its board repositories remain separate. They are evidence and
predecessors, not the implementation repository for Ogma 2.

## Collaboration workflow

- `main` is reviewed current truth. Use branches and pull requests for changes.
- Keep proposals marked as proposals until the owning team accepts them.
- A real architecture change updates its decision surface,
  `current-system.md`, affected interfaces or requirements, and
  `project-log.md` together.
- Keep observation, requirement, decision, candidate, inference, and unknown
  distinct.
- Do not commit credentials, private correspondence, personal data, raw model
  runs, temporary render trees, or uncurated source dumps.
- Controlled requirements, implementation, CAD, selected component data,
  measurements, and qualification evidence outrank prose.

The repository is private. The included reference images still have unresolved
provenance or reuse rights and must not be published merely because they are
present here.
