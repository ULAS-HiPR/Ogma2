# CATS Configurator interaction references

Status: selected operator-interface evidence only. These screens are references
for legibility and workflow, not a requirement to copy CATS behaviour.

## Selected screens

| Image | Useful visible evidence |
| --- | --- |
| [`general-identity-and-configuration.png`](general-identity-and-configuration.png) | Connection state, board identity, code/schema/app versions, captured time, current values, and explicit reset/save controls |
| [`flight-events-and-timers.png`](flight-events-and-timers.png) | Flight-state sequence and timer chains visible as one reviewable configuration |
| [`edit-pyro-action.png`](edit-pyro-action.png) | General action editor permitting a direct pyro action |
| [`edit-delay-action.png`](edit-delay-action.png) | General delay action used inside the configurable sequence |
| [`profile-readback-comparison.png`](profile-readback-comparison.png) | Stored-profile comparison against current board values |
| [`preflight-report-and-simulator.png`](preflight-report-and-simulator.png) | Preflight checks beside a human-readable event/timer simulation |
| [`testing-mode-confirmation.png`](testing-mode-confirmation.png) | Deliberate test-mode state and visible confirmation of a changed value |

Ogma should preserve visible identity, readback, comparison, preflight, sequence
preview, explicit persistence state, and separated test mode. The arbitrary
`PYRO ON -> DELAY -> PYRO OFF` construction is not Ogma's safety model. Ogma
uses typed, finite, one-shot energetic actions with fixed guards.

## Selection and provenance

Seven non-redundant screens were copied from the complete eleven-screen local
capture. The four omitted screens are alternate or collapsed views preserved in
the local archive. Original filenames indicate 25 August 2026 screen captures;
creator, source URL, and reuse licence are otherwise unverified.

SHA-256:

- `general-identity-and-configuration.png`:
  `1793d31808260af3759298d4759c0799dda03cb8543e522e8d440e00d52c993e`
- `flight-events-and-timers.png`:
  `8a7cc13cb82bbf64b3790b2ed97782403173a2edc20872192c44dabba301d759`
- `edit-pyro-action.png`:
  `c5593afe77261035d7ddb2621e06e73d4bbd57f31a4340e4448f73759f62b96e`
- `edit-delay-action.png`:
  `619a766859302108f28f52bd4125c93f4a34b3df477e8c25b9eee7aa9503c0c5`
- `profile-readback-comparison.png`:
  `db978c3305621ce2dbe021af717d46e2a29e97496662d00609e6b40cc613ae28`
- `preflight-report-and-simulator.png`:
  `e8e730bcfce9446733373ecbb7ee95e672be6d3f07802c35754de8461445dadc`
- `testing-mode-confirmation.png`:
  `700dded8a92373f434fbc87c65ba5ac46fcc2454933e7c50c4695233053ba3dd`
