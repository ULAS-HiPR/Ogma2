# Standing rules

Seán's standing rules for all Ogma2 work, in his words. Read this file before starting any session. Each rule
carries the date he gave it and its number in [decisions.md](decisions.md); entries run in the order he gave them.

How this file works (D-23Nov.24), in his words: "Every standing rule I give goes in it, in my words, with the date and
its D- number." "When Burrito closes, we fold this file into the skill in one go and start Churro from there." "But it
should change, or rather new ideas be appended to it over time that can supersede"

So entries are only appended. When a new rule supersedes an older one, the older entry stays and is marked with the
rule that replaced it; where two rules differ, the later one holds. Seán's global contract and the hipr-avionics
skill apply as well, and [AGENTS.md](AGENTS.md) holds the repository's other working rules.

Since D-24Nov.3, learnings drawn out in a reasoning review also go in once he approves them: in Claude's words as he
approved them, with his go-ahead quoted.

## D-23Nov.19 (20 and 21 Nov 2026): commits, posting and checkpoints

> "I will be pushing to main from now on re Ogma2" (20 Nov)
>
> "Rules: commit to main as before; don't post or send anything (Discord, Notion, email) without asking me.
> Checkpoint often; I want to spend a lot of usage today and tomorrow, so go deep. Watch for sunk cost and "we've
> come this far" in both of us, and for a requirement loosened to fit a design." (21 Nov)

*Supersedes 19 Nov: "Yeah, continue to wait on my go before you commit anything."*

## D-21Nov.2 (21 Nov 2026): one and done

> "We need to have charging on revision A of churro. We're not going to waste our time making a second revision.
> We're just going to get it one and done."

## D-21Nov.21 (21 Nov 2026): the board is the output of scripts

> "The board is the output of scripts in the repo. Everything you do to the .kicad_pcb (outline, stackup, rules,
> placement, routing, pours, silkscreen) is done by a script that can be rerun from a clean state. No one-off manual
> edits I can't replay."

## D-23Nov.20 (21 Nov 2026): ground rules for layout

> "I want you to do as much of it as possible, and to do it through code, not by looking at screenshots and
> clicking."
>
> "The requirements we defined together, the schematics and the decided board outline are the source of truth. Read
> them in the repo before anything else. If something you need is missing or contradicts itself, ask me; don't fill
> the gap with a guess."
>
> "Use JLC's current capabilities for the stackup, minimum track/space, via sizes, impedance-controlled stackups and
> assembly rules. Look them up; don't work from memory. Cite where each number came from."
>
> "Keep what you've checked (DRC result, a measured value), what you've assumed and what you don't know separate.
> Never report a check as passed that you didn't run."
>
> "Mark every point as either fixed by our requirements or your engineering judgement, so I can challenge the
> judgement calls."
>
> "At each stop, give me: the DRC/ERC output, the unrouted count, renders of each layer (kicad-cli export) so I can
> check it visually, and a short list of the decisions you made and the ones you're unsure about. Use renders and
> screenshots to check the result, not to drive the work."
>
> "When a script can't do something well, say so and propose the smallest manual step for me, rather than forcing
> it."

## D-21Nov.24 (night of 21 Nov 2026): connectors at the edge, facing out

> "receptacles and plugs ... go at edge of board facing out"

## D-23Nov.21 (22 Nov 2026): no test point is deleted

> "We are not deleting any test points so don’t worry about renumbering…."

## D-22Nov.25 (22 Nov 2026): pin swaps

> "yes you may swap any pin you want so long as it’s justified and verified and documented"

*Widened by D-23Nov.16.*

## D-23Nov.7 (23 Nov 2026): parts move wherever the layout needs

> "And note for all future work I permit you to move things however you like. We have to make this work."

*Extended by D-23Nov.11 to the edge connectors, the holes and J102.*

## D-23Nov.22 (23 Nov 2026): learn from every stop

> "We should view our work as this iterative loop where every time we stop and go back to reasoning, we need to look
> at what's working, what's not, where are we going, and is there anything that we can fundamentally change going
> forward and not have to repeat the same mistake. And then we can take these principles and reapply them to every
> PCB that we build, and even Churro, like that's the next one that I'm going to be building with you. Let us learn
> maximally so that we can stop making the same mistakes. But we must accept that there has to be a bit of slog in
> the middle. But a lot of this slog is like figuring out how to break down and approach the problem in a way that
> is tractable. And all of this is transferable."

## D-23Nov.11 (23 Nov 2026): the edge connectors, holes and J102 may move, on two conditions

> "D, yup. Assuming the edge connectors remain at edges and the holes remain lying on a rectangle"

## D-23Nov.16 (23 Nov 2026): pin functions

> "Do not feel like you can't change pin functions. If you check and it can work, do it."
>
> "Anav isn't writing firmware and we'll most likely generate it later, so the firmware interface is not a
> constraint."
>
> "For fire pins the check includes reset: no debug or boot pins, since they have pulls or toggle at reset. Every
> fire pin stays low through reset and boot."

## D-23Nov.17 (23 Nov 2026): JLC's capabilities are the rule set

> "JLC's published capabilities are our rule set, not our own margins."
>
> "We need to operate at JLC's capacity and go by its rules. We don't add some sort of weird safety margin."
>
> "The fire copper's 1.0 mm width and 0.5 mm gaps are current and safety decisions, not fab margin, so they stay."

## D-23Nov.18 (23 Nov 2026): levers

> "Standing rule: if a lever sits inside the standing rules, pick it yourself and keep going. Only stop for me if it
> loosens a fire or safety rule, or at a stage boundary, and then bring everything batched."

## D-23Nov.23 (23 Nov 2026): one sub-circuit at a time

> "Surely the standing rules will also encompass our entire philosophy of one sub circuit at a time. The latest
> direction we’ve settled on."
>
> "You have to take it subsystem by subsystem, and the components of a certain subsystem are probably going to be
> grouped together anyways, and they are. So you do them one at a time, and I'm happy that we've converged on that
> now with our more recent work."
>
> "You look at every subcircuit, you look at what wiring has to stay within its locality, and you get that done
> first, and you get it done as tightly as possible. And then you branch out and you look at like things that
> connect to one another. Like you look at subcircuits, then you look at power distribution, if anything. And then
> you look at connections between adjacent and further away subcircuits. Of course, you need to like bake in the
> hard copper as well."

Earlier forms of the same idea, in his words: "I'm happy that we're going to go into subsystem by subsystem next."
(19 Nov); "One sheet at a time, ERC clean, I review each before the next." (schematics, 21 Nov); "one board at a
time, Burrito first" (layout, 21 Nov). The method as it runs now is
[the midpoint review](docs/briefs/burrito-midpoint-review.md), which he accepted on 23 Nov: "I agree to all above.
Read them."

## D-24Nov.1 (24 Nov 2026): every passive at its chip, by name and pin

Given after the re-check Fable asked for found most of Burrito's chip capacitors far from their chips, with nothing
checking them. Dictated, so "pastors are closed" means "passives are close".

> "The above probably need some sort of it needs to be an operating rule like make sure that all the pastors are
> closed will actually look at them make a rule for each of them like an acceptable distance and then fix it"
>
> "That's every passive that serves a chip, not only the capacitors: resistors, inductors and ferrites too."
>
> "Each rule names the part and the pin it serves, so no other part can satisfy it. Where a part can't get inside
> its distance, say why and what it would take, and batch those for me."
>
> "The whole point is that you look at every single passive and you figure out how far does it actually need to be.
> Or another way of putting it is like, how close can it be whilst still doing its job?"
>
> "I want you to make it a standing rule so that we don't ever forget this."

How it runs: every passive that serves a chip gets its own row in the layout spec, naming the part, the chip and the
pin, with the distance its job needs; the build checks every row. A rule that any part on a net can satisfy is not
one of these.

## D-24Nov.3 (24 Nov 2026): the meta rule, learnings from a reasoning turn become rules once approved

> "And can you update the contract here somehow; perhaps in the rule file, that when we switch back to fable and have
> such an introspective moment you add them to adjust how we operate going on once I approve? The meta rule ;)"

How it runs: when the work goes back to the reasoning model (Fable) and a review draws out learnings, Claude writes
them up as candidate rules. Once Seán approves, Claude appends them here as approved, with his go-ahead quoted and a
D- number, and they hold from then on. Nothing is added before he approves.

## D-24Nov.4 (24 Nov 2026): eight operating rules from the review of the passives batch

Asked for and approved by Seán; written by Claude (Fable) and logged as written. "Today" below is 24 November 2026.

> "So what learnings can we transfer into things we can log in the operating rule file for this work?"
>
> "Log the above as you’ve written them also"

Six learnings would have changed today, and all carry to Churro:

1. **A block is done when all of it is done.** Inside a block the order is the chip, its own parts at their pins,
   then its copper. Lock it only when every rule in it passes.
   - **Today:** power parts 1 to 3 were logged done on their copper alone. U101, U1101 and U1401 never had their
     small parts placed, and U101's own 6 A copper then boxed in its pins.
   - **Extends:** one sub-circuit at a time.
2. **Every check says how many things it measured, and is proven on a planted miss.** Zero misses out of zero
   measured is a failure.
   - **Today:** the old capacitor rule let any capacitor on a net answer, so it passed with 82 of 118 far away. A
     supply rule did the same before 23 November: it measured nothing. We already plant a violation for every DRC
     rule; the placement rules never got that.
   - **Extends:** never report a check you didn't run.
3. **A miss has three suspects: the tool, the rule and the board. Clear them in that order.**
   - **Tool:** pick one spot that looks free and make the tool say why it refuses it.
   - **Rule:** work the distance from the part's job and write the working down. Any re-rule that turns a miss into
     a pass comes to you.
   - **Today:** Opus treated all 24 as the board's fault, and nine were the rule's. Before that, four faults in the
     mover had it reporting no room beside open board. Probing one refused spot at a time exposed them.
4. **What leaves a high-energy rail leaves through its resistor, and the resistor sits at the rail.** That covers
   divider tops and sense and monitor lines. A divider's bottom and any filter cap sit at the pin.
   - **Today:** five parts were placed this way and ruled the other way, and one proposed fix would have run unfused
     battery across the board.
5. **Scarce room goes by consequence.** Rank a chip's parts by what an upset costs, and place in that order.
   - **Today:** the one strip under U101 went to whichever part the mover reached first, and ILIM was left out.
6. **Read the chip maker's layout section before placing a chip's parts, and cite it in the rule.**
   - **Today:** every distance came from general reasoning or my memory of TI's text. Nobody opened a datasheet.
   - **Extends:** "Look them up; don't work from memory", which so far names only JLC's numbers.

Two smaller ones:

- **Long jobs save as they go.** A 32-minute run was lost to a 30-minute limit. It belongs under "checkpoint often".
- **A reader who didn't do the work closes each block.** Today's two biggest finds came that way. It costs Fable
  usage, so whether it becomes a rule is your call. He logged it with the rest.
