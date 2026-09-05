# Ogma 2 active documents

| Document | Use |
| --- | --- |
| [Reliability execution plan](reliability-execution-plan.md) | Start here for the review work queue: EX-01–EX-10, dependencies, proposed G0–G3 gates, bench procedures, pass criteria and open decisions; no tests completed or owners assigned |
| [Reliability design review](reliability-design-review.md) | Deepens the power/reset/state, measurement, MCU/ECC, actuation, storage and bay analysis; separates source corrections from proposed architecture |
| [Kármán-line mission hardening report](karman-line-mission-hardening-report.md) | Full short-duration space-shot reliability study, candidate analysis, failure controls, and qualification plan |
| [Verification-record template](templates/verification-record.md) | Reusable run record: exact configuration, stimulus, limits, instruments, raw evidence, result, uncertainty and decision |

Current architecture remains in [`../current-system.md`](../current-system.md).
Chronology remains in [`../project-log.md`](../project-log.md). Controlled
cross-system boundaries are indexed under [`../interfaces/`](../interfaces/README.md).

The 5 September review is authorised documentation, not acceptance of every
recommendation. Exact parts, Foinse auxiliary regulation, restart policy,
per-mission independent recovery, and release-gate allocation remain explicit
decisions. Foinse remains MCU-less. The accepted provisional workhorse envelope
is unchanged. Planned output paths in the execution plan are created when their
work packages start; they are not existing results.

Add a separate durable artifact only when it answers a recurring design,
verification, failure, or handoff question better than the current-system
document or project log. Raw research and generated output remain outside this
repository.
