# Dual Delay: breadboard plan (schematic v0.2, 2026-10-25)

Schematic: `docs/DualDelay_schematic.pdf` (generator `scripts/build_dualdelay.py`). Design notes and history: `docs/Ideas.md`.

**v0.2 changes (from the Dragonfish notes):** TIME minimum resistor 1k → **2k7** on both lines (~50–600 ms); the LFO now enters at the **TIME 2 / 2k7 node** (TMIN_2) through **33k + 10µ** instead of pin 6 through 100k + 1µ, so the modulation depth stays even across TIME (ΔI / I = −I_lfo × 2k7 / 2.8 V ≈ ±4–5 % at full DEPTH); LFO op-amp U6 → **LM358** (less supply-current ripple than a TL072).

## Parts (through-hole)

| Qty | Part | Where |
|---|---|---|
| 2 | PT2399 DIP-16 (socket them: they vary; genuine Princeton if possible) | U1, U2 |
| 3 | TL072 | U3 (input buffer, output mixer), U4 (feedback buffers), U5 (wet summer, spare) |
| 1 | LM358 | U6 (LFO) |
| 2 | 78L05 (TO-92) | U7, U8: one per PT2399 (the SMD board will use AMS1117-5.0, a JLC basic part) |
| 5 | 1N4148 | feedback limiters (2 per line) |
| 1 | 1N5817 | D1 |
| pots | B50k ×2 (TIME 1 / 2), B10k ×2 (FB 1 / 2), **B10k dual-gang (TWIST)**, B10k (MIX); trims 1M (RATE), 100k (DEPTH) | |
| switch | SPDT | SW1 SERIES |

Use film caps for the PT2399 filter networks and the LFO timing cap; the rest can be ceramic / electrolytic as drawn.

## Bring-up, in order

1. **Power and one line.** Fit power, U3, U7, U1 and line 1's network, U4A, U5A and the mixer (leave U2 out). Check: VB ≈ 4.5 V, U1 pin 1 ≈ 5.0 V, pin 2 (REF) ≈ 2.5 V, pin 6 (VCO) ≈ 2.5 V (about half the chip supply). Play: echoes on line 1; TIME 1 sweeps ~50–600 ms; FB 1 up to self-oscillation, which the 1N4148 pair keeps musical (no runaway to the rails).
2. **Line 2 + TWIST.** Fit U2, U8 and line 2. With TWIST fully **CCW** (parallel) each FB pot should only affect its own line. Fully **CW** (Möbius): FB 1 now feeds line 2 and FB 2 feeds line 1. Set TIME 1 short and TIME 2 long, FB moderate: listen for the **t1, t2, t1 + t2** rhythm. Check that with both FB pots equal, turning TWIST doesn't change how close it is to self-oscillation.
3. **Clock-whistle test.** MIX low, FB at zero, TIME 1 and TIME 2 near each other; sweep one slowly and listen for a beating tone. If present: more decoupling right at each PT2399 pin 1 (add 10µ + 100n), keep the two chips and their regulators apart, separate ground returns to the supply point.
4. **SERIES.** Line 2 fed from line 1's output: echoes of echoes; check the levels don't build up.
5. **Modulation.** Fit U6. RATE slow, DEPTH up: line 2's repeats should wobble by the same amount at short and long TIME 2 (the point of the v0.2 change). Set DEPTH for a light chorus; if full DEPTH is too much or too little, change the 33k (22k = more, 47k = less).

## Things to try

- **Voicing pair:** line 2 darker (Dragonfish values: extra 10k / 22n and 10k / 10n before the chip, 15n in LPF2) against a bright line 1: tape-like repeats against crisp ones. Clip the extra caps in on line 2 and compare.
- **Wet level:** the wet summer U5A is unity (10k / 10k); raise its feedback resistor for more echo on tap.
- **Ducking** (Ideas.md): an envelope on DRY turning the wet sum down while playing; a later add-on.
- **Stereo:** U5B is spare for a second output (line 1 left, line 2 right).

## Next after the breadboard

SMD schematic and a 1590BB board: panel TIME 1, TIME 2, FB 1, FB 2, TWIST (dual gang), MIX + SERIES toggle; RATE / DEPTH trims; AMS1117-5.0 ×2; PT2399-SN (C126407).
