# Standing rules

Seán's standing rules for all Ogma2 work, in his words. Read this file before starting any session. Each rule
carries the date he gave it and its number in [decisions.md](decisions.md); entries run in the order he gave them.

How this file works (D-23Nov.24), in his words: "Every standing rule I give goes in it, in my words, with the date and
its D- number." "When Burrito closes, we fold this file into the skill in one go and start Churro from there." "But it
should change, or rather new ideas be appended to it over time that can supersede"

So entries are only appended. When a new rule supersedes an older one, the older entry stays and is marked with the
rule that replaced it; where two rules differ, the later one holds. Seán's global contract and the hipr-avionics
skill apply as well, and [AGENTS.md](AGENTS.md) holds the repository's other working rules.

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
