# Ogma 2: recommendation-first design review

## Cumulative coverage, added 14 September

Mark explanation comprehension separately from design disposition and physical
verification. Retain understood explanations, briefly revisit changed assumptions,
and continue unread sections next session. Never count skipped chapters as
accepted. Rewrite confusing text in place and preserve dated review evidence.
For each unresolved feature bring a reasoned default, concrete alternative and
smallest distinguishing test. A proposed owner needs explicit acceptance;
participation alone does not assign integration responsibility.

Date: 6 September 2026
Status: active collaboration procedure. Technical recommendations still require acceptance.

## Purpose

The model prepares proposed answers to the design questions. Seán and the team
guide the choices. Implementation and measured evidence test whether those
choices work.

The model should bring engineering judgment to the review: a recommended
default, its downside, and what evidence could change it. A list of unanswered
questions is not a sufficient handoff when the model can investigate and
propose defensible answers.

## 1. Prepare the recommendation

Read the accepted architecture, relevant interfaces, existing evidence and
recent decisions before asking the team to reconstruct context.

For each question in the section under review, provide:

1. **Recommended default:** the concrete answer the model would start with.
2. **Reason:** the requirement, failure mechanism or evidence behind it.
3. **Cost:** the main disadvantage, lost capability or added complexity.
4. **Alternative:** a credible alternative only when it could materially change
   the decision; state when it becomes preferable.
5. **Uncertainty:** what is observed, inferred, assumed or still unknown.
6. **Validation:** the smallest calculation, inspection or experiment that could
   support or overturn the recommendation.
7. **Next action:** the bounded work that follows acceptance and who needs to
   perform it. Do not assign another person without agreement.

Exercise judgment without presenting taste as evidence. Prefer the simplest
design that meets the named function and failure boundary. Push back when a
proposed simplification removes a necessary capability or conceals a dependency.

## 2. Use provisional answers deliberately

Use the accepted workhorse envelope now. Do not wait for final vehicle
simulations when a labelled provisional assumption can support useful work.

Propose numerical values where there is a defensible basis. State that basis,
their provisional status and what would replace them. Never invent a measured
limit, safety margin, test result or reliability probability.

Where a missing value prevents a safe or meaningful decision, identify the
specific missing evidence and propose how to obtain it. Do not pass the entire
requirements problem back to Seán.

## 3. Match the review to the requested pass

**11 September: whole-system sessions are the current mode.** Start at the
architecture overview and pass through every chapter together. Pause for the
team's responses within each chapter, but do not turn an unresolved question
into a requirement to finish that subsystem before seeing the rest.

After each session, rewrite the same reading pack. Preserve accepted choices
and their reasons; explain terms where confusion arose; redraw misleading
ownership or mechanism diagrams; retain competing arguments and the evidence
needed to resolve them. Improve the delivery as well as the technical content.
Appending review notes above unchanged confusing prose is not sufficient.

Keep component designators and exact allocation tables in linked implementation
references. Main chapters must remain understandable without opening CAD.
The next session revisits the whole architecture, with settled material clear
and unresolved decisions visible in context. Record history separately.

For a specifically bounded, single-section review, use the following mode:

Present the proposed answers conversationally, then leave room for the team's
response. Do not advance through the whole design review before that response
unless a batch review has been requested.

Highlight the few choices that materially affect architecture, safety, cost,
maintainability or mission capability. The model handles supporting research,
calculations and ordinary implementation details within the authorised scope.

Seán should not need to invent the next detailed prompt. End with the next
specific action and make clear whether it requires:

- **Reading:** name and open the smallest useful section; say what understanding
  or decision the reading supports.
- **Waiting:** name the external dependency, owner and condition that ends the
  wait; identify useful work that can continue.
- **Model work:** propose a concrete deliverable with a completion check.

Do not make reading a long report a prerequisite when a short explanation or
model-prepared proposal would let the decision proceed.

## 4. Keep acceptance explicit

A recommendation remains a proposal until the relevant choice is accepted.
Agreement with this review method does not accept every technical example used
to demonstrate it. Enthusiasm, silence and continued discussion are not blanket
approval.

If a response leaves a consequential choice ambiguous, ask the smallest
clarifying question. Record accepted, rejected, provisional and deferred
choices distinctly, including conditions that would reopen them.

This procedure does not authorise live energetic testing, flight release,
purchases, publication or cross-system authority changes by implication.

## 5. Execute and test

Once the choice and execution scope are authorised, carry out the bounded work
without seeking approval for every routine step. Bring back an inspectable
design, calculation, implementation or experiment result.

Define the claim and pass criteria before calling a test successful. Preserve
failed runs, measurement limits and unexplained behaviour. A bench pass supports
only the conditions actually tested; it is not automatic flight qualification.

If evidence contradicts the recommendation, revise it and explain why. Do not
protect an earlier answer by weakening the test or overstating the result.

## 6. Preserve the decision and hand off cleanly

Keep proposed analysis, accepted architecture and chronological history
separate. Record accepted architectural changes in the current-system document,
affected interfaces and append-only project log. Link the supporting evidence.

When work shares a repository with another task, coordinate overlapping edits
and nominate one writer for shared staging, commits and pushes. Inspect the
complete staged change before committing; do not absorb another task's work
silently.

Finish with the observed result, remaining uncertainty and one next checkpoint.
Avoid creating another planning document when the next useful step is already
clear.

Stream capture remains Seán's choice. When asked for a verbatim record, return
the exact saved procedure or agreed text without silently rewriting it. Do not
automatically ingest it into Stream or Connective Tissue.

## Current application

**11 September amendment:** the joint 10 September review reopened requirements
and system allocation. Preserve the existing CAD; no schematic/PCB work until
Seán explicitly authorizes the final stack. The earlier sequence below is
history, not permission to continue it. See the
[complete session record](architecture/2026-09-10-session-review.md).

The review exposed a presentation failure: part references and specialist
terms appeared before the function was understood. Start each section with
the vehicle job, a mechanism/ownership diagram, its failure boundary and a
concrete example. Then give alternatives, costs, component evidence and the
next discriminating check. Define staging, one-shot, bootstrap, ECC and datum
where used. Do not treat an unread or deferred section as accepted. Retain the
deep research as supporting material, not an obstacle to joining the review.

Seán requested a batch architecture review, then accepted the complete result
on 7 September, including qualifications and the selected connectors. The
[acceptance record](architecture-acceptance-2026-09-07.md) carries the exact
scope and hardware baseline. EX-01–EX-10 no longer need sequential policy
approval. Anav has the firmware handoff according to Seán; implementation and
measurement remain open.

The explicit sequence amendment removes separate pre-order mini-PCBs/coupons.
Functional-block tests move to the first full PCBA. Library, schematic, layout,
rating, inhibit and assembly checks remain before order; qualification remains
before the corresponding flight claim. The next model work is checked KiCad
library preparation, not another generic architecture questionnaire.

Source: Seán's 6 September 2026 instruction to prepare proposed answers using
engineering judgment, let the team guide them, and formalise that working method
inside Ogma 2.
