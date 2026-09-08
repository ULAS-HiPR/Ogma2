# Croi2 engineering status

8 September 2026. Current draft; supersedes the historical counts below the
[previous status](history/pre-readable-2026-09-08/schematic-status.md).
That archived document retains earlier support-value rationale and open tests;
its old GNSS/switch descriptions are superseded by the current change record.

## Read and inspect

44 pages explain circuit purpose, interfaces and local connections. The
root index sets the reading order. 643 physical symbols / 642 footprints.
Schematic-to-PCB paths, pad nets, values, DNP and original placements were
checked independently against native KiCad exports.

2,179 schematic pins and 381 architecture assertions pass. All 28 DNP flags
remain; physical output-energy sources are still undefined. Four ERC errors
and six warnings are the existing baseline. PCB DRC has 61 findings (previously
62), with J101 the only missing-footprint parity finding.

80 × 230 mm provisional canvas; four copper layers, 1.6 mm. 501 front and
141 back footprints, 68 original groups, 20 retained rule areas. Eight new
parts are explicitly staged outside the outline. 572 model instances resolve;
this does not mean every physical component has an exact model.

Both boards remain unrouted. Original locations, sides, angles and identities
are retained; U4504 deliberately changes package at its old origin.
These checks do not establish routing capacity, vehicle fit, EMC, thermal
performance, assembly quality or flight reliability.

## Electrical delta and next work

Read [installation-change-record.md](installation-change-record.md). It defines
external maintained source-enable contacts and MAX-M10S external GNSS.
Electronic OFF is not physical battery disconnection or energetic safing.
Firmware remains Anav's responsibility; final placement and routing are Seán's.

Review circuits together, integrate the staged parts, close footprint/rating/
assembly issues before ordering, then test functional blocks on the first
complete PCBA with current-limited supplies and inert loads. No separate
mini-PCB gate was introduced. Earlier unresolved engineering details remain
in the archived status and current architecture contracts.
