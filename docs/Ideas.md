# Dual Delay: ideas and v0.1 plan (2026-10-25)

## Where the idea came from

The **VFE Möbius Strip** (madbean doc `~/Documents/Guitar/Effects/Schematics/VFE_MobiusStrip.pdf`, schematic p.9): two PT2399 lines, TIME 40–580 ms each, FB1 / FB2, MIX, and a **MODE** DPDT:
- **Parallel:** each line feeds back into itself (two independent echoes).
- **Möbius:** line 1's feedback goes into line 2 and line 2's into line 1. The loop time becomes t1 + t2, so repeats fall at **t1, t2, t1 + t2**, then repeat: 3-step rhythms. Tip from VFE: set one TIME short, the other long, then raise the short one until a rhythm locks in.

Worth copying as **practice**, not circuit (VFE boards are DIY-only; we design our own):
- a separate 5 V regulator for the PT2399s, big caps on pins 1–2;
- double filtering around each chip (input and output), plus an extra low-pass on each wet output;
- the dry path never touches a PT2399;
- MIX as gain on the wet sum (0 to unity).

## Our twist: a TWIST knob instead of the MODE switch

One **dual-gang B pot** blends each line's feedback between "self" and "cross":
- Gang A: ends at **FB1** and **FB2**, wiper → line 1's feedback input.
- Gang B: reversed (ends at FB2 and FB1), wiper → line 2's feedback input.
- **Fully CCW = parallel** (each line hears itself), **fully CW = Möbius** (each hears the other), **in between = both**: denser, more diffuse patterns. A smooth sweep from echo to rhythm to wash.
- FB1 / FB2 (the FEEDBACK pots) need **buffering** (one op-amp half each) so the TWIST pot doesn't load them.
- Loop gain can add up with both paths open: keep Loop Echo's **diode limiter** in each feedback path so self-oscillation stays musical.

## v0.1 plan (blocks)

| Block | From | Notes |
|---|---|---|
| Input buffer → DRY | Loop Echo U2A | |
| 2 × PT2399 line | Loop Echo / Small Time network | TIME = B50k + 1k (~30–340 ms in Loop Echo). Longer = noisier; a B100k gives more time if the noise is OK |
| FB1 / FB2 level pots + buffers | new | |
| TWIST (dual-gang) | new | see above |
| Limiter in each feedback | Loop Echo (1N4148 pair after 1k) | |
| SERIES option (toggle) | new | line 2's input from line 1's output instead of DRY: a third structure, combines with TWIST |
| Modulation | Loop Echo LFO (Schmitt + integrator, AC-coupled into pin 6) | On **line 2 only**: one line steady, one wobbling = chorus-like spread |
| Mixer | Loop Echo U2B | DRY + W1 + W2, MIX |
| Power | 78L05 for the PT2399s | One per chip if crosstalk is a problem (see below) |

**Stereo (later):** OUT L = dry + line 1, OUT R = dry + line 2. TRS out or a second jack.

## Known dual-PT2399 problem: clock whistle

Each PT2399 runs a VCO clock (MHz, set by TIME). With two chips, the clocks can **beat against each other** and leak a whistle or tone that slides as TIME moves, worst when the two TIMEs are close. Mitigations:
- separate 5 V regulators (or at least an RC filter per chip) and good local decoupling on each chip;
- solid ground plane, chips apart, analog and clock returns kept separate;
- the double filtering on every output.
Test this early on the breadboard: set both TIMEs equal and sweep one slowly.

## Panel (decided 2026-10-25: option A)

**TIME 1, TIME 2, FB 1, FB 2, TWIST, MIX + SERIES toggle in a 1590BB.** RATE / DEPTH are internal trims (a fixed light chorus on line 2).

Options that were considered:

Candidates: TIME 1, TIME 2, FB 1, FB 2, TWIST, MIX (6 knobs) + RATE, DEPTH + SERIES toggle.
- **6 knobs + toggle:** 1590BB (like Casualty), with RATE / DEPTH as internal trims or a fixed light chorus.
- **8 knobs:** 1590BB tight, or 9 mm pots.
- Simplify: one FEEDBACK (dual-gang) for both lines → 5 knobs + modulation → 125B possible.

## To do

1. Decide the panel and the enclosure.
2. Check PT2399 (SOP-16) and a dual-gang 16 mm B pot: JLC stock / price; PT2399 is probably an extended part.
3. v0.1 breadboard schematic (generator, reusing `../Loop Echo/scripts/`).
4. Breadboard: one line first (the Loop Echo breadboard proves it), then the second line, TWIST, clock-whistle test.

## v0.1 schematic (2026-10-25)

`DualDelay.kicad_sch` (generator `scripts/build_dualdelay.py`, toolkit copied from Loop Echo). ERC 0, nets checked.

| Block | Parts | Notes |
|---|---|---|
| Power | D1 1N5817, C1 100µ, VB R1/R2 10k + 47µ; **U7 / U8 78L05, one per PT2399** (V5_1, V5_2) | Separate 5 V to reduce clock beating |
| Input / output | U3A follower → DRY; U3B inverting mixer (DRY + MIXW, 10k / 10k / 10k ∥ 1n) | As Loop Echo |
| Lines 1 / 2 | U1 / U2 PT2399, Small Time network; DIN = input (DRY or D2IN) + RPT via 100n + 10k each; wet = LP2O → 10µ → 1k → W1 / W2 | TIME n = B50k + 1k (pin 6 to GND): ~40–580 ms (VFE quotes this range for the same values; past ~340 ms gets noisier and darker) |
| Feedback | W n → FB n (B10k) → 1k + 1N4148 pair → 1µ → U4 follower → FB1B / FB2B | Limiter only in the loop: the first echo is clean |
| TWIST | RV5 dual-gang B10k: gang A pin 1 FB1B / pin 3 FB2B → RPT_1; gang B pin 4 FB2B / pin 6 FB1B → RPT_2 | CCW parallel, CW Möbius. Both FBs equal: same loop gain at every TWIST position |
| SERIES | SW1 SPDT: D2IN = DRY or W1 | |
| Wet sum + MIX | U5A: W1 + W2 (1µ + 10k each, 10k ∥ 220p) → 10µ → 1k → 47n top-cut → MIX B10k → MIXW | Raise the 10k feedback for more wet ("more gain on tap") |
| LFO | U6 (Schmitt + integrator), RATE trim 1M + 47k, DEPTH trim 100k → 100k + 1µ → VCO_2 | Line 2 only |
| Spare | U5B (follower, + to VB) | Future stereo R output |

## Breadboard order

1. **Line 1 alone** (power, U3, U1, FB 1, U4A, mixer with W1 only): TIME range, FB to self-oscillation (the limiter should keep it musical), noise. The Loop Echo breadboard proves the same block.
2. **Add line 2 + TWIST:** parallel at CCW, Möbius at CW (set TIME 1 short, TIME 2 long: listen for the t1, t2, t1+t2 rhythm), the middle.
3. **Clock whistle test:** both TIMEs equal, sweep one slowly; listen for a beating tone at low MIX and with FB at zero. If it's there: more decoupling at each pin 1, chip spacing, separate ground returns.
4. **SERIES:** echoes of echoes; check levels.
5. **LFO on line 2:** RATE / DEPTH trims for a light chorus, then decide whether DEPTH deserves a knob.

## Parts at JLC / LCSC (checked 2026-10-25)

| Part | LCSC | Type | Stock | Price | Note |
|---|---|---|---|---|---|
| **PT2399-SN** (Princeton, genuine) | **C126407** | extended | 4056 | $1.20 | SOP-16 narrow. First choice for v1 |
| PT2399-S(LX) (clone) | C26159242 | extended | 3686 | $0.26 | SOP-16. Cheaper; clones vary, compare on a later run |
| PT2399S | C85146 | extended | 184 | $1.01 | **SOP-16 300 mil (wide body)**: different footprint, avoid |
| PT2399 DIP-16 | C84963 | | 794 | $0.94 | For the breadboard |
| **AMS1117-5.0** | **C6187** | **basic** | 148k | $0.26 | SOT-223. Basic, so no fee; 1.3 V dropout is fine from 9 V. Replaces the 78L05 (L78L05ABUTR C42738 is extended) |

Dual-gang 16 mm B10k (TWIST): not in the LCSC library; buy with the other panel pots (Alpha, Tayda / Small Bear), hand-soldered.

## Ideas from the Dragonfish (2026-10-25)

Source: madbean **Dragonfish** (`~/Documents/Guitar/Effects/Schematics/Dragonfish.pdf`, schematic p.13; close to the Tonepad Rebote 2.5 plus LFO). Ideas only.

### 1. LFO injection point: even modulation depth across TIME (adopt)

The PT2399 holds pin 6 (VCO) at about **2.8 V**; the clock follows the current drawn out of it, I = 2.8 V / (R_TIME + R_min).
- **Current way (ours):** LFO current straight into **pin 6**. Its share of I is tiny at short delays and large at long ones (with ±15 µA: about ±2 % at 3.7k total, ±27 % at 51k). Depth swings wildly as TIME turns.
- **Dragonfish way:** inject into the node **between the TIME pot and the fixed minimum resistor** (TIME → node → R_min → GND), through **33k + 10 µ**. Solving the node: ΔI / I = −I_lfo · R_min / 2.8 V, **independent of TIME**. Even depth across the range (pitch wobble still grows a little with delay time, but far less).
- **Change:** R_min 1k → **2k7** (also sets the shortest delay, ~50 ms) and LFO → DEPTH → **33k + 10 µ** → the TIME / R_min node (instead of 100k + 1 µ → pin 6). Re-trim DEPTH range on the breadboard (R_min sets the injection gain).

### 2. Darker, "analog-voiced" repeats (option)

Dragonfish adds RC poles **before** the chip (IC1A → 1 µ → **10k / 22n → 10k / 10n** → the PT2399 LPF1 with 10k, 33k, 1n) and uses **15n** caps in LPF2 (vs 10n / 2n2), then **1k5 + 22n** before MIX / RPT. Repeats are darker and get darker each pass, and more clock noise is filtered.

### 3. Low-power op-amp for the LFO

TL022 / TL062-class: much less (and less varying) supply current than a TL072, so less LFO tick on the supply. Check JLC basic status (LM358 C7950 is a known option).

### Skip

The **1N914 in the 78L05 ground leg** that runs the PT2399 at ~5.6–5.7 V for "headroom": above the 5.5 V datasheet maximum (madbean admits the early-failure risk). Keep the PT2399 at 5.0 V.

**Dual Delay specifics:**
- #1 applies to **line 2** (the modulated line): TIME 2's minimum resistor → 2k7, LFO into that node. If line 1 keeps 1k, the two TIME ranges differ slightly at the short end; simplest to make both 2k7.
- #2 could be a **voicing pair**: line 1 bright (Small Time values), line 2 dark (Dragonfish values). With TWIST, crisp echoes against tape-like ones. The extra filtering also helps the two-chip **clock-whistle** risk.
- #3: U6 (LFO) → TL062 / LM358.
- Not yet in the v0.1 schematic: update it when we next touch the generator (`scripts/build_dualdelay.py`, line() TIME block and the LFO output).


## Ideas from Stompboxology / Stomp Box Cookbook (2026-10-25)

Full notes and sources: `../../Stompboxology Ideas.md` (index + deep dives). Ideas only (the books' circuits are for personal use).

- **Ducking:** Envelo-Matic III inverted: the guitar's envelope turns the repeats down while playing, they swell back in the gaps (an LED / LDR or OTA on the wet sum, driven by an envelope detector on DRY).
- **Stereo swap per note** (Attack-O-Matic V) / pan with invert (Pan Tremolo-Matic) for the stereo-out version.

## v0.2 (2026-10-25)

Applied the Dragonfish items: TIME minimum 2k7 on both lines, LFO into TMIN_2 via 33k + 10µ (even depth across TIME), U6 → LM358. Voicing pair left as a breadboard experiment. Bring-up order and tests: `Breadboard Plan.md`.
