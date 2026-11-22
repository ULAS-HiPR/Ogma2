# Churro power review (S2)

**22 November 2026, draft for Seán.** A recommended answer for each open item
in Churro's power design (D-21Nov.22). Each follows the
[design-review procedure](../design-review-operating-procedure.md):
recommendation, reason, downside, alternative, uncertainty, smallest test.

Nothing here is decided. What Seán accepts becomes decision rows, and
[churro.md](../requirements/churro.md) freezes (D-21Nov.9). C-02's branch
ratings stay his call; section 1 only proposes a setting.

**Sources:**
- Stock is from the jlcparts scrape of JLC's library, deployed 21 Nov 2026
  (`tools/layout/phase2/jlc_find.py`). It's third-party data; confirm each LCSC
  number on jlcpcb.com.
- Datasheets are cited by revision and page.

**What's fixed already:**
- The interface rules IR-1 to IR-7: I²C only, the fault line, the Samtec
  unchanged, AV ≥ 6 A with auto-retry.
- No MCU on Churro (C-18).
- The umbilical, with per-source ideal diodes (D-2Nov.7).
- Damping on every J801 pair (D-21Nov.3).
- Chargers on board, standalone, temperature-gated, at ≤ 0.2 C (D-21Nov.2).
- 80 mm wide (D-21Nov.6).

## 1. PROP and ACT at ≈ 15 A peaks

**Recommendation:** each branch gets the same stage:
- an LM5069-2 hot-swap controller (auto-retry);
- one 60 V N-FET;
- a 2.5 mΩ Kelvin sense resistor.

| Item | Detail |
| --- | --- |
| Controller | LM5069MM-2/NOPB: 9–80 V; 55 mV current-limit threshold (48.5–61.5 mV); power limit; fault timer; auto-retry at 0.5% duty; VSSOP-10 (TI SNVS452G, pp. 1, 6, 12, 16). JLC C111822, 6,421 stocked |
| Current limit | 2.5 mΩ: 19.4 A at the minimum threshold, 22 A typical, 24.6 A maximum. Above C-02's ≈ 15 A peaks at the minimum, with 29% margin. **The setting is Seán's call (C-02)** |
| Power limit, timer | Sized with TI's procedure (pp. 18–23): start-up into Fajita's or Salsa's input capacitance finishes inside the timer with 50% margin. The FET handles 1.3× the hot-short power within its SOA, derated for case temperature |
| FET | A 60 V part in a 5 × 6 mm package with a published SOA, picked at capture. The CSD18540Q5B fits, but JLC stocks only 26 genuine parts (C86513), and Burrito uses it |
| Measurement | An INA237 per branch on the same shunt's Kelvin taps: 85 V common mode, on I²C4 at 0x44 (PROP) and 0x45 (ACT). JLC C2864837, 4,204 stocked. The INA228 isn't stocked (Burrito gets it through Global Sourcing) |
| Enables | PROP: its Gecko enable loop pulls the LM5069's UVLO pin low (C-07). ACT: Salsa's key sits in series in the supply (C-03, LV-0700 per D-18Nov.1), ahead of the LM5069, so the controller takes the inrush when the key closes |
| ORing | The two 6S sources (pack, umbilical) each have an LM74700 stage (D-2Nov.7), sized for both branches together: ≈ 29 A peaks (C-02). LM74700-Q1: JLC C2941042, 9,667 stocked |
| Faults | Each branch's fault output wire-ORs onto the Samtec fault line (IR-2) |

**Reason:**
- The TPS2663 limits at 6 A at most (C-02). The LM5069 is TI's standard
  controller for an external FET at this current.
- It limits inrush into the loads' capacitance, not just shorts.
- Auto-retry keeps PROP alive through a transient, so Fajita can still vent
  (C-05).
- Both branches use one design.

**Downside:**
- Each branch needs its SOA sized by hand, and a FET that has an SOA curve.
- It takes more area than an integrated eFuse.
- Auto-retry means a hard short keeps retrying at 0.5% duty until the enable
  opens.
- The key in series carries ACT's peaks through the panel harness:
  - roughly 1.2 V drop at 15 A over 6 m of 16 AWG (inferred, harness not
    designed);
  - a harness question for the panel subproject.

**Alternative:**
- **TPS48111-Q1 smart high-side driver** (JLC C17558994, 4,009 stocked). It
  cuts a short faster and has a current-monitor output. But it is built around
  back-to-back FETs and a separate pre-charge path for capacitive loads, so it
  needs more parts.
- **LM5066I** (C1848356, 135 stocked). It puts protection and PMBus telemetry in
  one IC, at the cost of a 28-pin package and PMBus firmware on Burrito.

**Uncertainty:** 3/5.
- C-02's currents are a 2/5 model estimate.
- The loads' input capacitance is unknown, and it sets the timer and the FET.

**Smallest test:**
- TI's LM5069 design calculator with the load capacitance bounded at 10–1,000 µF.
- Then C-02's bench test: the worst simultaneous move from the pack at its
  lowest Go voltage.

## 2. The three chargers and their temperature gate

**Recommendation:**

| Pack | Charger | Set by |
| --- | --- | --- |
| AV 2S | BQ25756 in autonomous mode (JLC C19272232, 9,107 stocked) | FB divider for 8.4 V; R_ICHG for ≤ 0.2 C; R_ILIM for the input |
| Actuator 6S | BQ25756, same part, set for 25.2 V | Same |
| CATS Vega 1S | BQ25185 linear charger (C19725033, 3,834 stocked), fed from a local 5 V buck: LM5164 (C477928, 6–100 V) or LMR36506 (C2866484, 3.6–65 V) | Its resistors, at ≤ 0.2 C of the cell |

- **The charge pair on J801 runs at 24 V** *[J]*: a standard pad supply.
- **The BQ25756 is buck-boost**, so it charges the 6S pack above its input and the
  2S below it. It is rated 4.2–70 V operating and 85 V absolute (TI SLUSEN5A,
  pp. 1, 6–7). D-21Nov.3's twice-the-bus rule is met.
- **It charges with no software:**
  - charge voltage, charge current and input current are set by resistors;
  - CE enables it;
  - STAT1, STAT2 and PG report charging, done, fault and input good
    (pp. 3–4, 18, 31).
- **Temperature gate (C-12):**
  - each pack's NTC probe also drives a TLV1701 comparator (C130035) with
    hysteresis, which pulls CE: off above 45 °C, back on below 40 °C;
  - the BQ25756's own JEITA window stays as a backstop (it suspends outside
    0–60 °C by default, pp. 26–27);
  - the comparator sits on a high-impedance tap, so C-17's ADC reading of the
    same probe is undisturbed.
- **The CATS cell has no probe.** It is gated by the AV pack's probe, which is
  in the same bay *[J]*.
- **Status (C-15):** every STAT, PG and gate output goes into an I²C expander
  that Burrito only reads (section 5). Burrito has no path into the charge
  circuit.

**Reason:**
- It is the one stocked 6S-capable charger rated for twice a 24 V bus. The
  BQ24610 (12,269 stocked) stops at 28 V, and the LTC4015 and LTC4162 at 35 V.
- Using the same part for 2S halves the design work.
- The BQ25185 has a TS pin and status outputs, and the CATS cell needs only
  tens of mA.

**Downside:**
- The BQ25756 is a controller: four FETs, a 2.2–15 µH inductor, two sense
  resistors, and ≥ 80 µF in and out (p. 7). About 25 × 20 mm per charger
  (inferred), twice over. That is the biggest pressure on Churro's length
  (section 6).
- Buck-boost switching at 200–600 kHz sits next to the monitors. It only runs
  on the pad, while charging, and stops at Go (C-13).

**Alternative:**
- **Set the charge pair to 30 V**, so the 6S charger only needs to buck. But no
  stocked simple buck charger handles 6S at 60 V input. It also forces a
  non-standard pad supply.
- **Or charge 6S off the vehicle**, which D-20Nov.1 rules out.

**Uncertainty:** 3/5.
- Pack capacities, and so the charge currents, aren't fixed.
- The officials' answer on charging the CATS cell (LV-0430) is open, and the
  CATS cell's capacity is unknown.

**Smallest test:** a bench charge of each pack through the real umbilical (C-11).
First, a BQ25756 evaluation module, or the first PCBA, at 24 V in, set for 6S at
0.5 A into a pack.

## 3. Damping at J801, and the J801 part

**Recommendation, damping** (D-21Nov.3 decided that it goes on every pair; this
sizes it):
- Each pair gets an aluminium electrolytic whose ESR damps the cable's
  inductance against the ceramic input capacitors:
  - 100 µF / 50 V on the two 24–25 V pairs (actuator, charge);
  - 100 µF / 25 V on the AV pair.
- Target ESR is about √(L_cable / C_ceramic), with C_bulk ≥ 4 × C_ceramic
  (standard RC damping, inferred). With ≈ 1 µH for 2 m of cable and 10 µF of
  ceramics, that is ≈ 0.3 Ω.
- The fuse and TVS per pair stay (D-2Nov.7).

**Recommendation, J801:**
- A board-side keyed, positive-lock, 2 × 4 header: Molex Mini-Fit Jr.
  *[J]*.
- The 6S pair on two contacts each, so peaks spread. The AV pair and the charge
  pair on one contact each.
- The pull-away at Go stays at the skin, Jay's (C-10, access-panel brief).
- An 8-way Mini-Fit doesn't mate the 2-way recovery-arm plug or J701's
  Micro-Fit.

**Reason:**
- Ogma 1's ORing part died of hot-plug ringing (D-21Nov.3). A lossy bulk
  capacitor is the cheapest damper and needs no tuning.
- Doubling the 6S contacts covers C-02's ≈ 29 A peaks on the rail.

**Downside:**
- The electrolytics are tall. They need staking under B-33-style loads, as
  Burrito's are.
- The ESR drifts with cold.

**Alternative:**
- **An RC snubber per pair** (a film capacitor with a resistor): exact damping,
  more parts.
- **A 6-way Nano-Fit, as the panel brief proposed.** Its contacts carry less
  per pin than Mini-Fit's (not read yet).

**Uncertainty:** 2/5.
- The cable inductance is a guess until the harness exists.
- The J801 part is the vehicle owner's call.

**Smallest test:** D-21Nov.3's 50 plug and pull cycles at full voltage with the
real cable, with the input scoped at each eFuse.

## 4. The CATS cell lead

**Recommendation:** C-23's mechanism, made concrete *[J]*:
- **The lead:** an inline adapter at the CATS Vega's own cell plug, so the unit
  isn't modified (LV-0430). It carries a fuse at the cell end: a 0.5 A fast
  fuse in the adapter.
- **On Churro:**
  - reverse blocking after the BQ25185 (a Schottky, or the charger's own
    blocking);
  - the cell voltage read through a 1 MΩ / 1 MΩ divider behind 10 kΩ, into a
    second ADS1115 at 0x49 (JLC C37593, 23,467 stocked).

**Reason:**
- A short anywhere on Churro or the lead opens the fuse at the cell. The
  backup chain (LV-0240 / 0250) then keeps its cell.

**Downside:** the adapter is one more harness joint in the av-bay.

**Alternative:** charge the CATS cell off the vehicle. That needs the officials'
answer, and then needs a hatch, which Jay won't allow (D-20Nov.1).

**Uncertainty:** 2/5. It hangs on the officials' answer.

**Smallest test:** C-23's bench test: short the charger output and the divider,
and the cell holds.

## 5. The I²C additions

**Recommendation:** on I²C4, behind Churro's buffer (IR-1):

| Part | Address | Job |
| --- | --- | --- |
| ADS1115 | 0x48 (taken, existing) | Temperatures, AV pack side |
| ADS1115 | 0x49 | CATS cell, 6S pack side (C-22), ACT key state |
| INA237 | 0x44, 0x45 | PROP, ACT current and voltage |
| TCA9535 (16 inputs) | 0x20 | The three chargers' STAT1, STAT2 and PG, the three temperature gates, the branch faults |

- **Parts:** TCA9535PWR, JLC C130204, 8,437 stocked.
- **IR-7:** the TCA9535 powers up with every pin an input. No output is wired
  to anything, so a Burrito reset switches nothing.
- **Address clashes:** none with 0x40 and 0x41 (taken).
- **AUX budget:** the new parts add ≈ 2 mA to AUX: two INA237 at ≈ 0.75 mA, an
  ADS1115, a TCA9535. That is far inside IR-5's 109–152 mA.

**Reason:** it is all reads over the one bus Burrito already has (IR-1, IR-3).

**Downside:** Burrito's firmware grows: three more device drivers.

**Alternative:** an 8-bit TCA6408A (C206177). Too few inputs for three chargers
with their gates.

**Uncertainty:** 4/5.

**Smallest test:** C-15's bench test: force each state, read it over I²C4.

## 6. Outline length

**Recommendation:** keep 80 × 120 mm as the target (D-21Nov.22) until Churro's
placement at S6.
- If the courtyards pass about 45% of one side, which is Burrito's density,
  grow to 140 mm before routing.
- 230 + 7.4 + 140 mm stays inside a 400 mm bay, but that's Jay's to confirm.

**Reason:**
- The two chargers (≈ 500 mm² each, inferred) and the two branch stages
  (≈ 150 mm² each) add ≈ 1,600 mm² to the 8 September draft's parts.
- That likely fits in 9,600 mm² at Burrito's density. A guessed length is
  worse than a measured one.

**Downside:** if Churro grows, the bay's length budget shrinks by 20 mm.

**Alternative:** parts on both sides of Churro, at Standard PCBA's cost.

**Uncertainty:** 2/5. No placement exists.

**Smallest test:** Churro's inventory run, as Burrito's, once it is captured.

## What Seán decides at S2

1. Accept, change or reject each section above.
2. C-02: the branch limits, proposed at ≈ 19 A minimum (2.5 mΩ).
3. The charge-pair voltage: 24 V proposed.
4. Whether Churro may grow to 140 mm, with Jay.

## Sources

- TI [LM5069](https://www.ti.com/lit/ds/symlink/lm5069.pdf), SNVS452G (Jan 2020)
- TI [BQ25756](https://www.ti.com/lit/ds/symlink/bq25756.pdf), SLUSEN5A (Aug 2026)
- [jlcparts](https://github.com/yaqwsx/jlcparts) scrape of JLC's library, deployed 21 Nov 2026
- [churro.md](../requirements/churro.md), [decisions.md](../../decisions.md), [access-panel brief](access-panel.md)
