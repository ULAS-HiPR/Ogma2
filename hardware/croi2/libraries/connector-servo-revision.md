# Connector/readiness/third-servo library revision

7 September 2026. Exact-named KiCad 9 stock imports: SMA_Amphenol_132134_Vertical,
Molex_Micro-Fit_3.0_43045-1000_2x05_P3.00mm_Horizontal (local name 430451000),
and SOT-23-5. Stock provenance/licence retained. The new 10-pin symbol is the
stock generic connector graphic with explicit Molex identity and pin numbers;
its graphic is NOT a physical mating-face view.

SN74LVC1G04DBVR symbol follows TI's DBV pin table: NC1/A2/GND3/Y4/VCC5.
Its SOT-23-5 STEP is the existing verified package model. J6601, new J6602 and
J4601 exact 3D bodies remain missing; failed public downloads and login gates
were not bypassed. No wrong variant was attached. Stock land patterns still
require final manufacturer/assembly drawing audit before fabrication release.

Only flight CSV row PD10/pad57 changes. Comms CSV is byte-identical.
See ../../../docs/connector-servo-readiness-revision-2026-09-07.md for the
complete acceptance, harness change, firmware contract and evidence links.
