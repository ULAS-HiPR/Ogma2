# 0. What we are building

Ogma 2 is the computer we maintain for ordinary HiPR launches, then qualify for
specific harder missions. Croí2 works alone. Foinse2 adds vehicle power
distribution without adding a processor or another flight-state machine.

The useful difference is integration with our vehicles: three energetic
channels, three servo channels, measured power, dissimilar sensors, a bounded
propulsion link and serviceable wiring. A newer chip is useful only when it
improves one of those jobs.

## Power and information

```text
Standalone 2S OR Foinse protected 2S
                 │
       Croí protection + current shunt
          ┌──────┴───────────┐
       logic rails      physical output-energy breaks
          │                  │
  flight MCU U201       3 energetic + 3 servo channels
    │   │    │
 sensors NOR vehicle CAN ─────── propulsion controller
    │
 bounded UART
    │
 comms MCU U401 ─── GNSS / radio / USB

Foinse: separate 6S pack ── protected paired power ── propulsion
        Croí auxiliary 3.3 V ── monitoring only
```

The drawing shows responsibilities, not a finished power or arm schematic.
USB service does not power the outputs. Only one Croí battery source may be
connected. Propulsion owns local valves, redlines and abort; CAN carries
coordination rather than a remote substitute for its control loop.

## What is already accepted

Two role-separated H563 MCUs; separate flight/comms/optional power domains;
five flight sensors; fixed local NOR; three energetic and three servo channels;
MCU-less Foinse; keyed connectors; independent debug; first-full-PCBA testing.
The current review is not permission to silently remove these choices.

The carbon airframe changes the GNSS installation: reception must move outside
it. External power-switch connections are also authorised. Exact implementation
remains separate from these requirements. Computer power and energetic arming
must remain distinguishable electrically and to the operator.

## What the split buys, and what it does not

Comms can reset without taking essential flight work with it. A failed optional
device should be isolated locally; a failed peripheral must not stall the
scheduler. These are testable containment claims.

Both MCUs still share a board and upstream power path. The flight processor,
core conversion, installation, software defects and common environment remain
common failure points. Two MCUs are not two independent recovery systems.

Ordinary flights use the workhorse outputs after qualification. The bounded
Kármán configuration has those energy paths physically absent/DNP; independent
vehicle systems own recovery, actuation and full-envelope altitude proof.

## Next decision

Can Seán and Anav point to every source, decision owner and unsafe failure path
on the drawings? If not, improve the drawing or resolve that boundary before
packing the PCB. Keep the previous routing study separate.

Evidence: [current system](../../current-system.md),
[accepted baseline](../architecture-acceptance-2026-09-07.md),
[vehicle boundary](../../interfaces/ogma-foinse-propulsion-boundary.md).
