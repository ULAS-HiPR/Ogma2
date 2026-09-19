# Ogma 2: recommendation-first design review

Updated 19 September 2026. The model prepares the concrete proposal; the team
accepts or changes it. CAD and electrical contracts change only within the
explicitly authorised implementation scope.

## Current method

Start with the [connected component proposal](architecture/00-overview.md).
Use the drawing during conversation. Follow the block being questioned; a
complete reread of every chapter is not a prerequisite.

For each consequential block show:

- Exact component and labelled connections.
- The requirement/fault it addresses, in one short reason.
- Cost or lost capability; one material alternative when useful.
- Specific unresolved input or test that could change the selection.

Perform the available research, pin mapping and calculations before review.
Do not replace a missing design with another list of questions for the team.
Do not protect a generated baseline simply because it appears in older prose.
Compare simplifications on function, failure exposure and the team's actual
assembly/verification burden.

Use provisional values where defensible; label their basis. Keep observed,
calculated, proposed, accepted and verified distinct. An exact part selection
is not a claim of qualification. Missing actuator data may block its power
stage without blocking unrelated processor or sensor work.

## Acceptance and work

Record the result beside the block: accepted choice, amendment or named missing
input. Understanding an explanation does not accept the design. Participation
does not assign ownership. Existing accepted owners remain unless changed.

When the scope is authorised, complete routine implementation/checks without
repeated permission requests. If a consequential ambiguity remains, ask the
smallest question after doing independent useful work.

Architecture implementation updates current-system, affected interfaces and the
append-only project log together. Preserve historical evidence separately;
current drawings must show the actual latest proposal rather than accumulated
review commentary. The root README must point to that proposal.

## Existing boundaries

- The reopened architecture still has a hold on schematic/PCB changes until
  final-stack authorisation. Documentation preparation does not lift it.
- No implicit authorisation for purchases, live energetic tests or flight release.
- First-full-PCBA block testing remains the agreed sequence; no new mandatory
  separate coupon programme.
- Nominate one writer for shared staging/commit/push; inspect the complete scope.
- Raw transcripts and private correspondence stay outside the repository.

Historical decisions: [7 September acceptance](architecture-acceptance-2026-09-07.md),
[10 September reopening](architecture/2026-09-10-session-review.md),
[13 September review](architecture/2026-09-13-session-review.md).
The 19 September method follows the latest meeting's request for exact parts,
connected diagrams and concise justification. It supersedes the former
whole-pack reading procedure; it does not accept the proposal's technical choices.
