# Rev 1 external review: power and packaging lessons

Recorded: 6 September 2026
Status: attributed review context supplied by Seán; selected power direction
accepted below. Reviewer suggestions are not qualification evidence.

## Provenance

Seán supplied excerpts from two Reddit reviews of Ogma 1 while correcting the
EX-02 recommendation. The first excerpt names `dr__Chernobyl`; no first-thread
URL or absolute comment date was supplied. The second includes the linked
comments below. Relative labels such as “7mo ago” and “6mo ago” are not converted
into invented dates. Empty comment placeholders contain no usable feedback.

Seán described the first reviewer as an experienced designer of power systems
for such devices. That experience is Seán's attribution, not independently
verified employment or qualification. The excerpts identify the replying account
as `International-Try525`; Seán presented those replies as his review history.

## Power recommendation and present decision

The first reviewer advised avoiding unsupported TO-220 packages in the expected
high-acceleration/vibration installation, retaining other heavy parts properly,
and considering compact switching regulator modules. For noise-sensitive loads,
the recommendation was switching preregulation followed by an ultra-low-noise
LDO, rather than treating the existing TLV704 as such a part. LT3045, ADI VIOC
guidance and integrated switchers from several manufacturers were suggested.
Seán's supplied reply accepted investigation of that chain and removal of the
TO-220s. This records the discussion, not proof of the final Rev 1 build.

**Current decision:** Seán explicitly wants the switching preregulator followed
by low-noise LDO retained in Ogma 2. This supersedes the model's direct-buck-first
preference in the EX-02 conversation. The [power contract](../../interfaces/power-contract.md)
and [current system](../../current-system.md) now carry that direction. Exact
module, LDO, intermediate voltage and VIOC use remain open.

Manufacturer checks made on 6 September:

- ADI distinguishes **LT3045-1 with VIOC** from **LT3045 without VIOC**. Both
  part identity and available load current matter; the family name does not
  settle the Ogma rail budget.
  [ADI product/variant table](https://www.analog.com/en/products/lt3045-1.html)
- VIOC coordinates converter output with LDO headroom. ADI documents converter
  feedback/compensation restrictions and an added control path; it is not a
  feature to enable without checking the complete pair.
  [ADI VIOC Part 1](https://www.analog.com/en/resources/technical-articles/voltage-input-output-control-linear-regulators-part-1.html)
- LT3045-1's documented VIOC programming starts at a 1 V differential. The old
  approximately 0.5 V preregulator/LDO separation must not silently become its
  VIOC setpoint. This does not establish the minimum for a different LDO or
  fixed-output cascade.
  [Datasheet, pp. 23–24](https://www.analog.com/media/en/technical-documentation/data-sheets/30451fa.pdf)
- The reviewer also linked [TI SNVA935A](https://www.ti.com/lit/an/snva935a/snva935a.pdf).
  Its body could not be retrieved in this pass; no detailed claim from it is
  treated as verified. The reviewer's module/EMI argument remains attributed
  advice pending exact-part/layout evaluation.

The design question is now how to implement and verify the chosen chain.
Noise, headroom, heat, fault containment and mechanics still need measurements.
The model's simplification preference is not evidence against prior engineering
rationale; equally, an external recommendation is not a measured Ogma result.

## Packaging feedback for EX-08

[Quartinus's second-review comment](https://www.reddit.com/r/PCB/comments/1rffryq/comment/o7la0qk/)
questioned assembly order, material assumptions in topology optimisation,
battery support, loose spacers/nuts and missing harness restraint. The concrete
suggestions were to capture metal spacers and nuts in the printed structure,
provide strain relief near connectors, and design assembly for cold hands and
poor field conditions. The commenter described their spacecraft work as
packaging-dominated. These are attributed observations and recommendations.

[Seán's supplied reply](https://www.reddit.com/r/PCB/comments/1rffryq/comment/o7lf8i6/)
clarified that the sled was a visual mock-up using automated modelling, with
avoid/connect geometry but no modelled flight loads. This is not evidence that
a completed stress analysis used incorrect loads. He welcomed captured spacers,
recessed nuts and mounting provisions, and considered returning to XT30s with
cable ties. None proves implementation or current connector selection.

Carry these questions into the existing EX-08 1:1 service mock-up:

- Can each board and retained harness be installed/removed in an unambiguous
  order without inaccessible loose hardware?
- Are spacers, nuts and connector strain relief captive or readily controlled
  during field work, while their load paths remain inspectable?
- Does the actual printed material/process/orientation and battery restraint
  support the declared loads? A visual optimisation is not substantiation.
- Are regulator modules and other heavy parts supported without assuming that
  every component should receive the same adhesive treatment?

The XT30/cable-tie suggestion is historical candidate context. It does not
replace Ogma 2's accepted keyed, shrouded, positive-lock board-connector rule
or select a new connector family. Adhesive, staking, structural retention and
environmental qualification remain controlled design work, not blanket adoption
of every review comment.
