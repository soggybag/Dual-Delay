# Enclosure: Hammond/Tayda 1590BB (landscape)

Made 2026-10-25 by `scripts/make_enclosure.py` (KiCad python), which reads every hole from `DualDelay.kicad_pcb`: pot shafts (mid-point of the mounting tabs), the LED, the SERIES toggle, the footswitch circle on Dwgs.User, and the jack positions. Same conventions as Loop Echo. Re-run it if the board changes.

| File | Use |
|---|---|
| `DualDelay_1590BB_drill.csv` | Tayda Box Tool. Face: origin = face centre, mm, +X right / +Y toward the jack wall, outside view; plus "Tayda portrait" columns. Jack wall: along = face X, depth from the face's outside surface. Raw-aluminium diameters. |
| `DualDelay_1590BB_drill_template.svg` | 1:1 printable template: the face, with the jack wall unfolded above it. Check the 50 × 10 mm box when printed. |
| `DualDelay_1590BB_mill_marks.svg` | Othermill face marks (page = the 119.5 × 94 mm face, outside view, jack wall at the top). |

## Face (outside view, jack wall at the top)

```
     TIME 1    TIME 2     MIX            (Y +15)
     FB 1      TWIST      FB 2           (Y -1)     X -32 / 0 / +32
                LED                      (Y -15)
    SERIES                               (X -32, Y -21)
             FOOTSWITCH                  (Y -26)
```

- Pots (9 mm, M7 bushing; TWIST is the dual): 7.5 mm. LED: 3.2 mm. SERIES (Taiway 100): 6.5 mm. Footswitch: 12.2 mm.

## Jack wall (top long wall, outside, left to right)

| Jack | Along X | Depth | Hole |
|---|---|---|---|
| OUT | −30 | 22.5 | 11.5 (7/16" bushing) |
| DC 9V | 0 | 21.0 | 8.1 |
| IN | +30 | 22.5 | 11.5 |

**The depths are estimates** (face ~3 mm + 9.91 mm pot gap measured on GlitchStorm v3 + 1.6 mm board + the jack's centre height). Fit the pots and board first, measure one barrel, then drill the wall. The same fit checks as Loop Echo apply: jack body depth (~30 of ~34 mm) and DC plug reach.
