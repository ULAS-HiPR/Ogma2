# Ogma 2 engineering and documentation instructions

## Read order

1. `current-system.md`
2. The relevant interface under `interfaces/`
3. `docs/karman-line-mission-hardening-report.md` when mission or reliability
   consequences matter
4. `project-log.md`, newest entries last
5. The specific source, implementation, CAD, or test evidence needed

The controlled requirements, implementation, CAD, selected component data,
hardware, measurements, and tests outrank prose.

## Documentation rules

- `current-system.md` is the canonical prose baseline. Keep it concise enough to
  orient work while retaining every decision that constrains the design.
- `project-log.md` is append-only. Correct an old conclusion with a new dated
  entry; do not rewrite history.
- `docs/karman-line-mission-hardening-report.md` is the deep design study. A
  proposal in that report becomes architecture only when explicitly accepted in
  `current-system.md` and logged.
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

- `main` is reviewed current truth. Use branches and pull requests.
- Keep pull requests bounded. Do not mix an electrical decision, prose cleanup,
  and unrelated source import.
- Architecture changes update `current-system.md`, the affected interface or
  requirement, and append `project-log.md` in the same pull request.
- Never commit credentials, private correspondence, personal data, raw model
  output, temporary rendering trees, or machine metadata.
- Reference images with unresolved reuse rights may remain in this private
  repository for internal design review. Do not publish them without provenance
  and permission.

## Current architecture rules

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
- Every extra component, board, processor, connector, interface, and software
  mode needs a named function, failure boundary, and verification need.
