# Ogma 2 engineering and documentation instructions

## Read order

1. [`standing-rules.md`](standing-rules.md): Seán's standing rules, in his words. Read it before starting any session.
2. `decisions.md`
3. `current-system.md`
4. The relevant interface under `interfaces/` and chapter under `docs/architecture/`
5. `project-log.md`, newest entries last
6. The specific source, implementation, CAD, or test evidence needed

`docs/archive/` holds superseded reviews and studies: evidence, not instructions.

The controlled requirements, implementation, CAD, selected component data,
hardware, measurements, and tests outrank prose.

## Documentation rules

- `current-system.md` is the canonical prose baseline. Keep it concise enough to
  orient work while retaining every decision that constrains the design.
- `project-log.md` is append-only. Correct an old conclusion with a new dated
  entry; do not rewrite history.
- `decisions.md` records every decision with its status. A proposal anywhere,
  including the archived studies, becomes architecture only when it appears there
  as Decided and `current-system.md` reflects it.
- `interfaces/` owns cross-system contracts. A real boundary change must also be
  reconciled with the other owning project.
- Historical or generated material stays outside this repository unless a named
  current decision, requirement, or verification need justifies a concise
  durable artifact.
- Keep observation, requirement, decision, working recommendation, candidate,
  inference, and unknown distinct.
- Preserve raw evidence and provenance. Link or curate it; do not silently
  rewrite it.
- Update active internal links after moving files.

## Collaboration rules

- Use the [recommendation-first design-review procedure](docs/design-review-operating-procedure.md)
  when reviewing a section or open design question. Bring a recommended answer,
  rationale, downside, material alternative, uncertainty and smallest validation
  step. Review one coherent section at a time unless Seán asks for a batch.
  Agreement with the method does not accept its technical examples.
- Coordinate overlapping work with other tasks. Nominate one writer for shared
  Git staging, commits and pushes; inspect the full staged scope before committing.

- `main` is reviewed current truth. Since 20 November 2026 Seán pushes reviewed
  changes straight to main.
- Keep commits bounded. Do not mix an electrical decision, prose cleanup,
  and unrelated source import.
- Architecture changes update `decisions.md`, `current-system.md`, the affected
  interface or chapter, and append `project-log.md` in the same commit.
- Never commit credentials, private correspondence, personal data, raw model
  output, temporary rendering trees, or machine metadata.
- The repository is public. Nothing goes in without the right to publish it:
  no third-party photographs or screenshots without permission, no datasheets,
  no private correspondence.

## Current architecture rules

- Ogma2 is one monorepo. Active CAD is tracked directly in `hardware/croi2/`
  and `hardware/foinse2/`, not nested repositories or submodules. Read each
  board's README, AGENTS, schematic status and native reports before editing.
  Keep board dependencies local and never regenerate over manual CAD edits.

- Ogma 2 is one serviceable main PCB. Do not reintroduce a component-obscuring
  board stack or speculative internal modules.
- The two MCUs separate flight-critical timing from communications work. They
  are not redundant. The flight MCU must complete the mission with the
  communications MCU held in reset.
- The flight MCU owns recovery and staged-flight energetic authority. External
  systems do not directly command these outputs.
- CAN is external, linear, and limited to named independent peers. The current
  production propulsion path is a two-node Ogma/propulsion link.
- Foinse owns vehicle source entry and protected distribution. Ogma does not
  become a general power distributor.
- Battery, CAN, pyro, and servo use keyed, shrouded, positive-lock board
  connectors from Rev A. Bare-wire terminals exist only on detachable
  development adapters and are absent from the Kármán flight configuration.
- The avionics bay is integrated and qualified as a controlled assembly.
  Routine charge replacement, USB service, log extraction, and charging use
  deliberate external service boundaries.
- “Space-shot capable” means the bounded suborbital mission defined in
  `current-system.md`, not orbital lifetime.
- Ogma 2 is the workhorse board for ordinary HiPR competition and development
  flights. Use the accepted provisional platform envelope for Rev A design;
  replace it with mission-specific simulation and measured environments before
  qualification rather than blocking schematic work now.
- Every extra component, board, processor, connector, interface, and software
  mode needs a named function, failure boundary, and verification need.
