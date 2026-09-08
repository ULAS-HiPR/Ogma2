# Foinse2 engineering status

8 September 2026. Current draft; supersedes the historical counts below the
[previous status](history/pre-readable-2026-09-08/schematic-status.md).
That archived document retains earlier support-value rationale and open tests;
its old GNSS/switch descriptions are superseded by the current change record.

## Read and inspect

12 pages explain circuit purpose, interfaces and local connections. The
root index sets the reading order. 113 physical symbols / 112 footprints.
Schematic-to-PCB paths, pad nets, values, DNP and original placements were
checked independently against native KiCad exports.

306 schematic pins and 117 architecture assertions pass. Native ERC has no
findings. PCB DRC retains 24 findings, with J101 the only missing-footprint
parity finding.

60 × 80 mm provisional canvas; four copper layers, 1.6 mm. Nine original groups;
12 new parts staged outside the outline. 100 model instances resolve; missing
models and the Nano-Fit reservation are not approved package geometry.

Both boards remain unrouted. Original locations, sides, angles and identities
are retained; no original package is relocated.
These checks do not establish routing capacity, vehicle fit, EMC, thermal
performance, assembly quality or flight reliability.

## Electrical delta and next work

Read [installation-change-record.md](installation-change-record.md). It defines
external maintained source-enable contacts.
Electronic OFF is not physical battery disconnection or energetic safing.
Firmware remains Anav's responsibility; final placement and routing are Seán's.

Review circuits together, integrate the staged parts, close footprint/rating/
assembly issues before ordering, then test functional blocks on the first
complete PCBA with current-limited supplies and inert loads. No separate
mini-PCB gate was introduced. Earlier unresolved engineering details remain
in the archived status and current architecture contracts.
