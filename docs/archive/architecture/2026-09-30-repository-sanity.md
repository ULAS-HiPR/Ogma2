# Ogma2 repository sanity pass — 30 September 2026

## Verdict and inspected authority

**Coherent ordinary-electronics proposal; incomplete full-system design and
unrouted native CAD. Not green for full-platform capture, manufacture or flight.**

Inspected the full tracked repository, current instructions, controlling docs,
interfaces, proposal maps/calculations, both native CAD projects, local library
dependencies, check tools and host tests. Fresh remote fetch confirmed
`docs/reliability-review-execution` at
`f18141e4f4580c6c3284e280914faa9b44fde537`, equal to its remote. `main` remains at
`f81e6a6` and predates the hardware/detail pack. Latest work has not been merged
there. Three fetched branches contained no supporting design note for Anav's
newly reported switch recommendation; that does not establish that his research
does not exist elsewhere.

The branch has 404 tracked files, including 101 Markdown documents and 12 Python
scripts. Ogma owns two native boards. There is no tracked target-firmware source
or build project on this branch. Fajita and groundstation implementation remain
outside this audit. Ignored scratch history and private raw recordings were not
treated as current design authority.

## Material findings and disposition

| Finding | Meaning / disposition |
| --- | --- |
| Proposal and CAD are different versions | September 22 package/rails/services/two-PWM/probe changes remain proposals against September 8 CAD. Clarified this at the firmware handoff and added an illustrated comparison; no acceptance invented |
| Output and physical-arm assembly unresolved | Existing draft and DNP safeguards remain; this is a design gap, not merely later qualification. Recorded Anav's shared-low-side/per-channel-high-side recommendation as reported, unreviewed and unaccepted |
| Both J101 battery footprints absent | Exact Nano-Fit 1053111102 has been selected, but neither PCB has its footprint. Both missing-footprint parity errors persist; exact capture/placement needed after authorization |
| USB socket footprint differs from local library | Burrito J4401 USB4105-GF-A has a native `lib_footprint_mismatch`. A pin/net checker does not prove dimensional parity. Compare exact geometry and deliberately reconcile the board/library; no automatic replacement performed |
| Native ERC/DRC not clean | Burrito has four errors/six warnings; both boards have clearance/drill violations and unrouted items. Fine-pitch/default-rule interactions need explicit review against drawings/fabricator rules, not blanket suppression |
| Stale Churro full-check CLI | Its copied Croí-specific check failed at nonexistent MCU U201. Replaced its body with a compatibility delegate to the canonical MCU-less Churro checker; retained pin helpers and CLI. Both entrypoints now pass identical 117 assertions |
| Old budget tool could appear current | Marked `tools/architecture_budgets.py` as historical September 11 scenarios and pointed at current proposal checks. Preserved historical numbers; its old sixteen-data-page scenario is not the selected format |
| Two active library-note links broken | Corrected `manifest.json` to the actual `source-manifest.json` on both boards |
| Historical/nonportable documentation references | Whole-repo scan found 76 missing relative-file links before correction: two active library-note defects and 74 archived/log references. No broken heading targets found. Another 29 references leave the clean clone; some remain active historical supporting evidence. The handoff now identifies its three external research links and points at current portable chapters |
| Measurements remain absent | Load/energy/hold-up/USB budgets, logger rate/restart, cascading protection, RF profile and flight/recovery validity are proposed or calculated, not measured. Source selection, independent recovery and peer agreement remain release gates |

Archived snapshots are explicitly preserved verbatim. Their relocated relative
links and old log paths were not silently rewritten. Existing root `AGENTS.md`
working-tree edits were preserved. No CAD, frozen pin CSV, controlled interface,
DNP, target firmware or remote branch was changed by this pass.

## Fresh native checks

KiCad 9.0.6 freshly exported both native XML netlists and ERC reports, and ran
DRC with schematic parity. Results were written to temporary audit directories;
tracked evidence files were not regenerated. Fresh ref/pin/net maps equal the
saved native outputs, and fresh DRC category counts equal their saved reports.

| Check | Burrito / Croí2 | Churro / Foinse2 |
| --- | --- | --- |
| Physical schematic components | 643 | 113 |
| Native connected pins checked | 2,179 | 306 |
| Architecture assertions | 381 pass | 117 pass |
| Saved PCB footprints / numbered pads checked | 642 / 2,256 | 112 / 370 |
| Outline / layers | 80 × 230 mm / 4 | 60 × 80 mm / 4 |
| Staged components outside working placement | 8 | 12 |
| DNP count | 28 preserved | 0 |
| ERC | 4 errors, 6 warnings | 0 violations |
| Native DRC violations, excluding unrouted/parity items | 61 | 24 |
| Unconnected items | 499 | 262 |
| Schematic/PCB missing-footprint parity | J101 | J101 |
| Local dependency files matching manifest hashes | 117 / 117 | 43 / 43 |

PCB identity/pad-net/geometry checks completed, including the in-memory negative
test that detects a disconnected mate pad. All manifest-hashed dependencies are
tracked and all board-resolved model paths are local. This is portability and
stored-connectivity evidence, not footprint approval. Churro's missing exact
J701 body remains a model gap. The headless PCB checks emitted a wx initialization
diagnostic; no GUI cross-selection/interactive test is claimed.

**Burrito ERC:** four `power_pin_not_driven` violations at VS pins on
U6304/U6404/U6504/U6802 in the unfinished output/servo energy domain;
three dangling global labels (`LORA_RXEN`, `LORA_TXEN`, `SERVO_ARMED_VBAT`);
three pin-role conflicts at U3104.2/U3104.3/U3403.5. Do not interpret an expected
violation category as electrically resolved.

**Burrito DRC:** 36 clearance, four hole-clearance, nine drill-range, one
library-footprint mismatch, ten text-height and one silk-overlap violations.
**Churro DRC:** six clearance and eighteen drill-range violations. Some issues
involve fine-pitch pads, thermal via sizes or manufacturer holes versus default
rules. Their correct disposition needs exact dimensional/manufacturing review.
The native checkers intentionally tolerate the saved engineering-draft categories;
their successful exit is not a clean ERC/DRC release.

## Calculation/software verification and limits

- All 12 tracked Python scripts parse.
- Current proposal checker passes all 164 proposed MCU pad comparisons to native
  electrical nodes, rail/limiter/source-enable budgets, recording capacity/rate,
  energy and probe calculations. These are desk calculations.
- Twelve host checkpoint/reset-replay tests pass. They exercise a model, not MCU
  firmware or real interrupted NOR programming.
- Native MCU pin audit passes the preserved two 100-pad maps.
- Both Churro full-check entrypoints produce 113 components, 306 checked pins,
  117 assertions and zero ERC violations; negative branch-merge detection remains.
- Historical September 11 budget calculations still pass and are now explicitly
  labelled historical.

No target run, bench measurement, fault injection on hardware, RF interoperability,
fabricated assembly, final vehicle installation or operational release was
performed. A library provenance table with a pending pin/dimensional review is
not transformed into approval by an unchanged hash.

## System-level conclusions

The proposed three-LDO rationale is explicit: a comms-regulator failure should
not simultaneously remove NOR/CAN. Services failure can still remove recording,
CAN and AUX monitoring together. Battery/mux/common 4 V buck/ground/PCB remain
common causes. Flight input hold-up does not hold up the NOR. Limited-fault
arithmetic does not prove common-buck transient survival.

Churro remains pack-powered and MCU-less. Source protection is independent of
AUX/monitoring; it does not supply a regulated 24 V rail or charge packs. Both
positives share ground. Cascading AV protection selectivity, alternate ground
returns through signal/service harnesses and an installed source-fuse assembly
need physical verification. A powered monitor or inactive fault line is not
proof of healthy/isolateable vehicle power.

Current production CAN is Burrito ↔ Fajita at 500 kbit/s Classical CAN. FD is a
review direction; both peers and a machine-readable message/timing/freshness
contract must be reconciled before migration. Fajita's local authority must be
validated in its owning system. The selected GNSS/pressure/low-g sensor limits
also mean full mission coverage requires an explicit mission overlay; ordinary
flight-core part selection alone does not close independent recovery.

**Recommendation:** review the exact capture deltas, close the distinct
output/physical-arm design, then authorize a bounded capture/placement revision.
Keep firmware/harness/bench validation and fabrication/flight release as separate
gates. Do not route the old PCB as if the newer proposal were already installed.

## Reproduce the bounded checks

From the repository root, use KiCad 9 to export each root schematic netlist and
ERC JSON, then run DRC with `--schematic-parity`. Pass those fresh files to:

```text
python3 -B hardware/croi2/tools/check_schematic_full.py hardware/croi2 <croi-netlist.xml> <croi-erc.json> --output <croi-checks.json>
python3 -B hardware/foinse2/tools/check_schematic_full.py hardware/foinse2 <foinse-netlist.xml> <foinse-erc.json> --output <foinse-checks.json>
python3 -B docs/calculations/component-proposal-checks.py
python3 -B -m unittest discover -s tests/reset_replay -p 'test_*.py'
python3 -B tools/architecture_budgets.py
```

Consult each native checker CLI for its output option. PCB checks use KiCad's
Python/pcbnew runtime and saved DRC categories; compare fresh DRC independently.
Do not run library installation/rebuild or CAD-save tools just to review.

[Illustrated system tour](system-tour.md) ·
[Capture specification](../../architecture/schematic-capture-spec.md) ·
[Connector/arming boundary](../../architecture/09-connectors-arming.md) ·
[Hardware entrypoint](../../../hardware/README.md) ·
[Native Burrito check evidence](../../../hardware/croi2/full-checks.json) ·
[Native Churro check evidence](../../../hardware/foinse2/full-checks.json)
