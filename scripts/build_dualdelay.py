"""Dual Delay (working name): two PT2399 delay lines with a TWIST knob that blends each line's feedback
between itself (parallel) and the other line (Moebius cross-feedback, idea from the VFE Moebius Strip).
Blocks reused from Loop Echo (PT2399 network from the user's Small Time, diode limiter, LFO, mixer).
  - U3A input buffer (DRY); U3B inverting output mixer (DRY + MIXW)
  - U1 / U2 PT2399 lines, each on its own AMS1117-5.0 (U7 / U8) to limit clock beating between the chips.
    TIME = B50k + 2k7 from VCO (pin 6) to ground (~50-600 ms); node TMIN between them takes the LFO (v0.2)
  - FEEDBACK: W1 / W2 -> FB pot -> 1k + 1N4148 limiter -> U4 followers -> FB1B / FB2B
  - TWIST (dual-gang B10k): gang A FB1B (CCW) .. FB2B (CW) -> RPT1; gang B FB2B (CCW) .. FB1B (CW) -> RPT2
    CCW = parallel, CW = Moebius, middle = both
  - SERIES (SW1): line 2's input = DRY (parallel) or W1 (series)
  - U5A wet summer (W1 + W2) -> MIX; U5B spare (future stereo R)
  - U6 LFO (LM358: Schmitt + integrator, RATE / DEPTH trims) -> 33k + 10u -> TMIN_2 (line 2 only). Injecting at the
    TIME / 2k7 node (Dragonfish) keeps the modulation depth even across TIME: dI/I = -I_lfo x 2k7 / 2.8 V
v1.0 (2026-10-25): SMD for JLC, ordered as a prototype with Loop Echo (not breadboarded; the blocks are Loop Echo's).
v0.2 breadboard kept as build_dualdelay_v0.2.py. Changes from v0.2:
  - footprints + LCSC; MLCC instead of electrolytics; 1N4148W; SS14; AMS1117-5.0 per PT2399 (U7 / U8, kept apart on the board)
  - FB MAX 1 / 2 trims (10k rheostats in series with the top of each FB pot): set the maximum repeat level
  - board-mounted jacks (PJ-646F IN / OUT, A-4118 DC, top wall of a 1590BB, landscape), status LED, 1x6 header to the SwitchPCB v2
usage: build_dualdelay.py <out.kicad_sch>"""
from sch import *
import sys
OUT = sys.argv[1]
g = lambda n: round(n * 2.54, 3)
s = Sheet('DualDelay', 'A0')
W = lambda *p: s.wire(*p)
P = s.P
FR = 'Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
FC = 'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
FC12 = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
FPOT = 'Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical'
FDUAL = 'SuperFreq:Potentiometer_9mm_Dual_Vertical_Tayda'
FTRIM = 'Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical'
FSO8 = 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
FJACK = 'SuperFreq:Jack_6.35mm_PJ-646F_Horizontal'
LR = {'100': 'C17408', '1k': 'C17513', '2k7': 'C17530', '10k': 'C17414', '15k': 'C17475', '22k': 'C17560',
      '33k': 'C17633', '47k': 'C17713', '100k': 'C149504', '1M': 'C17514', '4k7': 'C17673'}
LC = {'220p': ('C107145', FC), '1n': ('C46653', FC), '2n2': ('C28260', FC), '10n': ('C1710', FC), '47n': ('C53134', FC),
      '100n': ('C49678', FC), '1u': ('C28323', FC), '4u7': ('C1779', FC), '10u': ('C15850', FC), '22u': ('C45783', FC), '47u': ('C96123', FC12)}
_n = {}
def nx(p):
    _n[p] = _n.get(p, 0) + 1
    return f'{p}{_n[p]}'
def GND(p): s.power('GND', p)
def V9(p): s.power('+9V', p)
def lab(n, p, side='r'): s.label(n, p, side)
def Rh(v, cx, y, d=''):
    r = nx('R'); s.part(r, 'Device', 'R', v, cx, y, 90, fp=FR, lcsc=LR[v], desc=d, text='t'); return r
def Rv(v, x, cy, side='r', d=''):
    r = nx('R'); s.part(r, 'Device', 'R', v, x, cy, 0, fp=FR, lcsc=LR[v], desc=d, text=side); return r
def Ch(v, cx, y, d=''):
    r = nx('C'); s.part(r, 'Device', 'C', v, cx, y, 90, fp=LC[v][1], lcsc=LC[v][0], desc=d, text='t'); return r
def Cv(v, x, cy, side='r', d=''):
    r = nx('C'); s.part(r, 'Device', 'C', v, x, cy, 0, fp=LC[v][1], lcsc=LC[v][0], desc=d, text=side); return r
CPh, CPv = Ch, Cv      # v1.0: all MLCC (non-polar), the v0.2 electrolytic positions kept
def gnd_down(p, n=1): W(p, (p[0], p[1] + g(n))); GND((p[0], p[1] + g(n)))
def lab_at(p, name, dx=2, side='r'):
    q = (p[0] + g(dx) * (1 if side == 'r' else -1), p[1]); W(p, q); lab(name, q, side)
def lab_v(p, name, dy, side='r'):
    q = (p[0], p[1] + g(dy)); W(p, q); lab(name, q, side)
PINS = {1: ('3', '2', '1'), 2: ('5', '6', '7')}
OPS = {'TL072': ('C6961', 'Dual JFET op-amp'), 'LM358': ('C7950', 'Dual op-amp (LFO: inputs to ground)')}
def OP(ref, unit, x, ytop, sym='TL072'):
    s.part(ref, 'Amplifier_Operational', sym, sym, x, ytop + 2.54, 0, unit=unit, fp=FSO8, lcsc=OPS[sym][0], desc=OPS[sym][1], text='ic',
           extra={'FT Rotation Offset': '270'})
    pl, mi, ou = PINS[unit]
    return P(ref, pl), P(ref, mi), P(ref, ou)
def follower(ref, unit, x, ytop):
    pl, mi, ou = OP(ref, unit, x, ytop)
    W(mi, (mi[0] - g(1), mi[1]), (mi[0] - g(1), mi[1] + g(3)), (ou[0] + g(1), mi[1] + g(3)), (ou[0] + g(1), ou[1]))
    W(ou, (ou[0] + g(1), ou[1]))
    return pl, (ou[0] + g(1), ou[1])
def pot(v, name, x, y, mirror='x', text=None, sym='R_Potentiometer'):
    r = nx('RV')
    s.part(r, 'Device', sym, v, x, y, 0, mirror=mirror, fp=FPOT if sym == 'R_Potentiometer' else FTRIM, desc=name, bom=False,
           extra={'Panel': name} if sym == 'R_Potentiometer' else None,
           text=text or ((x - g(4), y + g(2)), (x - g(4), y + g(3.5)), 'right'))
    return r
def rheo(r):
    """tie the wiper to pin 3 (rheostat), return pin 3's lower stub point"""
    w = P(r, '2'); p3 = P(r, '3')
    W(w, (w[0] + g(1), w[1]), (w[0] + g(1), p3[1] + g(1)), (p3[0], p3[1] + g(1))); W(p3, (p3[0], p3[1] + g(1)))
    return (p3[0], p3[1] + g(1))
def limiter(L, d):
    """1N4148 pair from node L to ground (one each way)"""
    for dx, rot in ((0, 90), (4, 270)):
        ref = nx('D'); s.part(ref, 'Diode', '1N4148W', '1N4148W', L[0] + g(dx), L[1] + g(1) + 3.81, rot, fp='Diode_SMD:D_SOD-123', lcsc='C81598', desc=d,
                              text='l' if dx == 0 else 'r')
        top = min(P(ref, '1'), P(ref, '2'), key=lambda t: t[1]); bot = max(P(ref, '1'), P(ref, '2'), key=lambda t: t[1])
        W(L, (top[0], L[1]), top); gnd_down(bot, 1)

# ================================================================ POWER
s.box('POWER: DC jack, SS14, VB, AMS1117-5.0 x2', g(4), g(6), g(46), g(78))
s.part('J4', 'Connector', 'Barrel_Jack_Switch', 'DC 9V', g(7), g(15), 0, mirror='x', fp='SuperFreq:DC_Jack_2.1mm_A-4118_Horizontal',
       desc='Tayda A-4118 2.1 mm DC jack, centre negative (Boss). Pads 2 + 3 tied, so it works whichever blade is the sleeve',
       text=((g(4.5), g(9.6)), (g(4.5), g(10.6)), 'left'), bom=False)
W(P('J4', '3'), P('J4', '2')); W(P('J4', '2'), (g(10), g(12)))
W(P('J4', '1'), (g(10), g(20))); GND((g(10), g(20))); s.power('PWR_FLAG', (g(10), g(20)))
s.part('D1', 'Diode', 'SS14', 'SS14', g(13), g(12), 180, fp='Diode_SMD:D_SMA', lcsc='C2480', desc='Reverse-polarity protection', text='t'); _n['D'] = 1
W((g(10), g(12)), P('D1', '2')); W(P('D1', '1'), (g(18), g(12)))
V9((g(18), g(12))); s.power('PWR_FLAG', (g(18), g(12)))
W((g(18), g(12)), (g(42), g(12)))
for x, v, d in ((22, '22u', 'Bulk'), (26, '22u', 'Bulk'), (30, '100n', 'U3 decoupling'), (34, '100n', 'U4 decoupling'), (38, '100n', 'U5 decoupling'),
                (42, '100n', 'U6 decoupling')):
    c = Cv(v, g(x), g(15.5), d=d); W((g(x), g(12)), P(c, '1')); GND(P(c, '2'))
for ref, y, net in (('U7', 28, 'V5_1'), ('U8', 42, 'V5_2')):
    s.part(ref, 'Regulator_Linear', 'AMS1117-5.0', 'AMS1117-5.0', g(16), g(y), 0, fp='Package_TO_SOT_SMD:SOT-223-3_TabPin2', lcsc='C6187',
           desc=f'5 V for {"U1" if net[-1] == "1" else "U2"} (PT2399) only: one regulator per chip limits clock beating', text='t')
    q = P(ref, '3'); V9((q[0] - g(2), q[1])); W(q, (q[0] - g(2), q[1]))
    GND(P(ref, '1'))
    q = P(ref, '2'); W(q, (g(34), q[1])); lab(net, (g(34), q[1]))
    c = Cv('10u', g(26), q[1] + g(3.5), d='5 V output'); W((g(26), q[1]), P(c, '1')); GND(P(c, '2'))
    c = Cv('100n', g(30), q[1] + g(3.5), d='PT2399 VCC decoupling (at pin 1)'); W((g(30), q[1]), P(c, '1')); GND(P(c, '2'))
    c = Cv('10u', g(40), q[1] + g(3.5), d=f'{ref} input'); V9(P(c, '1')); GND(P(c, '2'))
r1 = Rv('10k', g(9), g(56)); V9(P(r1, '1'))
r2 = Rv('10k', g(9), g(64)); GND(P(r2, '2'))
W(P(r1, '2'), P(r2, '1'))
c = Cv('47u', g(15), g(63.5), d='VB filter')
W((g(9), g(60)), (g(15), g(60)), P(c, '1')); GND(P(c, '2'))
W((g(15), g(60)), (g(19), g(60))); lab('VB', (g(19), g(60))); s.power('PWR_FLAG', (g(19), g(60)))
for ref, x, sym in (('U3', 25, 'TL072'), ('U4', 30, 'TL072'), ('U5', 35, 'TL072'), ('U6', 40, 'LM358')):
    s.part(ref, 'Amplifier_Operational', sym, sym, g(x), g(68), 0, unit=3, fp=FSO8, lcsc=OPS[sym][0], desc=OPS[sym][1], text='ic',
           extra={'FT Rotation Offset': '270'})
    V9(P(ref, '8')); GND(P(ref, '4'))

# ================================================================ INPUT + MIXER (U3)
s.box('INPUT BUFFER (U3A) + OUTPUT MIXER (U3B): as Loop Echo / Small Time', g(50), g(6), g(120), g(70))
y = g(26)
lab('IN', (g(53), y), 'l'); W((g(53), y), (g(57), y))
r = Rv('1M', g(57), y + g(3.5), side='l', d='Input pull-down'); W((g(57), y), P(r, '1')); GND(P(r, '2'))
W((g(57), y), (g(59), y)); c = Ch('100n', g(60.5), y, d='Input coupling'); W((g(59), y), P(c, '1'))
r = Rh('100', g(66.5), y, d='Input stopper'); W(P(c, '2'), P(r, '1'))
W(P(r, '2'), (g(71), y))
r = Rv('1M', g(71), y + g(3.5), side='r', d='Bias to VB'); W((g(71), y), P(r, '1'))
q = P(r, '2'); W(q, (q[0], q[1] + g(1))); lab('VB', (q[0], q[1] + g(1)), 'l')
pl, o = follower('U3', 1, g(84), y)
W((g(71), y), pl); W(o, (o[0] + g(4), o[1])); lab('DRY', (o[0] + g(4), o[1]))
y2 = g(46)
pl, mi, ou = OP('U3', 2, g(96), y2)
W(pl, (pl[0] - g(6), pl[1])); lab('VB', (pl[0] - g(6), pl[1]), 'l')
tap = mi[0] - g(1)
W(mi, (tap, mi[1]))
r = Rh('10k', tap - g(1) - 3.81, mi[1], d='Dry into the mixer'); W(P(r, '2'), (tap, mi[1]))
q = P(r, '1'); W(q, (q[0] - g(2), q[1])); lab('DRY', (q[0] - g(2), q[1]), 'l')
r = Rh('10k', tap - g(1) - 3.81, mi[1] + g(3), d='Echoes into the mixer'); W(P(r, '2'), (tap, mi[1] + g(3)))
c = CPh('10u', P(r, '1')[0] - g(1) - 3.81, mi[1] + g(3), d='MIX coupling'); W(P(c, '2'), P(r, '1'))
q = P(c, '1'); W(q, (q[0] - g(2), q[1])); lab('MIXW', (q[0] - g(2), q[1]), 'l')
fy = mi[1] + g(7); rx = ou[0] + g(1)
W((tap, mi[1]), (tap, fy + g(3)))
r = Rh('10k', (tap + rx) / 2, fy, d='Mixer feedback'); W((tap, fy), P(r, '1')); W(P(r, '2'), (rx, fy))
c = Ch('1n', (tap + rx) / 2, fy + g(3), d='HF roll-off'); W((tap, fy + g(3)), P(c, '1')); W(P(c, '2'), (rx, fy + g(3)))
W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, fy + g(3)))
W((rx, ou[1]), (rx + g(1), ou[1])); r = Rh('100', rx + g(1) + 3.81, ou[1], d='Output stopper')
c = CPh('10u', P(r, '2')[0] + g(1) + 3.81, ou[1], d='Output coupling'); W(P(r, '2'), P(c, '1'))
q = P(c, '2'); W(q, (q[0] + g(3), q[1]))
r = Rv('100k', q[0] + g(3), q[1] + g(3.5), side='r', d='Output pull-down'); W((q[0] + g(3), q[1]), P(r, '1')); GND(P(r, '2'))
W((q[0] + g(3), q[1]), (q[0] + g(6), q[1])); lab('OUT', (q[0] + g(6), q[1]))

# ================================================================ DELAY LINES (U1, U2)
def line(n, dy, dry_net):
    Y = lambda v: g(v) + dy
    k = f'_{n}'
    s.box(f'DELAY LINE {n}: PT2399 (U{n}), network as Loop Echo / Small Time. TIME {n} = B50k + 2k7',
          g(124), Y(6), g(250), Y(80))
    U = f'U{n}'
    xu, yu = g(150), Y(40)
    s.part(U, 'Audio', 'PT2399', 'PT2399', xu, yu, 0, fp='Package_SO:SOIC-16_3.9x9.9mm_P1.27mm', lcsc='C126407',
           desc=f'PT2399 echo processor, line {n}', text=((xu - g(3), yu - g(7)), (xu - g(3), yu - g(5.5)), 'left'))
    lab_at(P(U, '1'), f'V5{k}', 3, 'l')
    q = P(U, '2'); W(q, (q[0] - g(6), q[1])); c = CPv('47u', q[0] - g(6), q[1] + 3.81, side='l', d='REF'); gnd_down(P(c, '2'), 0)
    p3_, p4_ = P(U, '3'), P(U, '4')
    gx_ = p3_[0] - g(4)
    W(p3_, (gx_, p3_[1])); W(p4_, (gx_, p4_[1])); W((gx_, p3_[1]), (gx_, p4_[1])); GND((gx_, p4_[1]))
    s.noconnect(P(U, '5'))
    lab_at(P(U, '6'), f'VCO{k}', 3, 'l')
    for pin, dx in (('7', 10), ('8', 6)):
        q = P(U, pin); cc = (q[0] - g(dx), q[1]); W(q, cc)
        c = Cv('100n', cc[0], cc[1] + g(1) + 3.81, side='l', d=f'Compander (pin {pin})'); W(cc, P(c, '1')); GND(P(c, '2'))
    for pin, name in (('9', 'OP1O'), ('10', 'OP1I'), ('11', 'OP2I'), ('12', 'OP2O'), ('13', 'LP2I'), ('14', 'LP2O'), ('15', 'LP1O'), ('16', 'LP1I')):
        lab_at(P(U, pin), name + k, 3)
    for a, b, x in (('OP1I', 'OP1O', 172), ('OP2I', 'OP2O', 186)):
        c = Ch('100n', g(x), Y(68), d=f'{a}-{b} (PT2399 integrator)')
        lab_at(P(c, '1'), a + k, 2, 'l'); lab_at(P(c, '2'), b + k, 2, 'r')
    # LPF1
    xa, ya = g(176), Y(18)
    lab(f'DIN{k}', (xa, ya), 'l')
    r = Rh('10k', xa + g(1) + 3.81, ya, d='LPF1'); W((xa, ya), P(r, '1')); lab_at(P(r, '2'), 'LP1I' + k, 2)
    W((xa, ya), (xa, ya + g(4)))
    r = Rh('15k', xa + g(1) + 3.81, ya + g(4), d='LPF1'); W((xa, ya + g(4)), P(r, '1')); lab_at(P(r, '2'), 'LP1O' + k, 2)
    c = Ch('2n2', xa + g(18), ya + g(8), d='LPF1'); lab_at(P(c, '1'), 'LP1I' + k, 2, 'l'); lab_at(P(c, '2'), 'LP1O' + k, 2, 'r')
    W((xa, ya + g(4)), (xa, ya + g(6)))
    c = Cv('10n', xa, ya + g(6) + 3.81, side='l', d='LPF1'); W((xa, ya + g(6)), P(c, '1')); GND(P(c, '2'))
    # DIN sources: dry (or line 1 in series) and repeats from TWIST
    for src, yy, d in ((dry_net, 14, 'Input into the delay'), (f'RPT{k}', 20, 'Repeats (from TWIST) into the delay')):
        lab(src, (g(196), Y(yy)), 'l'); W((g(196), Y(yy)), (g(198), Y(yy)))
        c = Ch('100n', g(199.5), Y(yy), d=d); W((g(198), Y(yy)), P(c, '1'))
        r = Rh('10k', P(c, '2')[0] + g(1) + 3.81, Y(yy), d=d); W(P(c, '2'), P(r, '1'))
        lab_at(P(r, '2'), f'DIN{k}', 2)
    # LPF2
    xb, yb = g(176), Y(44)
    lab('OP2O' + k, (xb, yb), 'l')
    r = Rh('10k', xb + g(1) + 3.81, yb, d='LPF2'); W((xb, yb), P(r, '1'))
    N = (P(r, '2')[0] + g(2), yb); W(P(r, '2'), N)
    W(N, (N[0], yb + g(2))); c = Cv('10n', N[0], yb + g(2) + 3.81, side='l', d='LPF2'); GND(P(c, '2'))
    r = Rh('10k', N[0] + g(1) + 3.81, yb, d='LPF2'); W(N, P(r, '1')); lab_at(P(r, '2'), 'LP2I' + k, 2)
    W(N, (N[0], yb - g(4)))
    r = Rh('10k', N[0] + g(1) + 3.81, yb - g(4), d='LPF2'); W((N[0], yb - g(4)), P(r, '1')); lab_at(P(r, '2'), 'LP2O' + k, 2)
    c = Ch('2n2', N[0] + g(16), yb + g(8), d='LPF2'); lab_at(P(c, '1'), 'LP2I' + k, 2, 'l'); lab_at(P(c, '2'), 'LP2O' + k, 2, 'r')
    # wet out: LP2O -> 10u -> 1k -> Wn (DC-referenced to GND by the FB pot)
    lab('LP2O' + k, (g(212), Y(44)), 'l'); W((g(212), Y(44)), (g(214), Y(44)))
    c = CPh('10u', g(216), Y(44), d='Wet coupling'); W((g(214), Y(44)), P(c, '1'))
    r = Rh('1k', P(c, '2')[0] + g(1) + 3.81, Y(44), d='Wet out'); W(P(c, '2'), P(r, '1'))
    lab_at(P(r, '2'), f'W{n}', 2)
    # TIME: VCO -> pot (rheostat) -> 1k -> GND
    lab(f'VCO{k}', (g(134), Y(62)), 'l'); W((g(134), Y(62)), (g(138), Y(62)))
    rv = pot('B50k', f'TIME {n}', g(138), Y(62) + 3.81, mirror=None, text=((g(134), Y(66)), (g(134), Y(67.5)), 'right'))
    q = rheo(rv)
    r = Rv('2k7', q[0], q[1] + 3.81 + g(1), side='r', d='Minimum delay (~50 ms); also sets the LFO injection gain'); W(q, P(r, '1')); GND(P(r, '2'))
    lab_at(q, f'TMIN{k}', 3, 'l')

line(1, 0, 'DRY')
line(2, g(78), 'D2IN')
s.text('Line 2 input: DRY (parallel) or W1 (series), set by SW1 SERIES. Line 2 VCO also gets the LFO (chorus-like spread).', g(126), g(155))

# ================================================================ FEEDBACK + TWIST (U4)
s.box('FEEDBACK (FB 1 / FB 2) -> limiter -> U4 buffers -> TWIST (dual gang): CCW = parallel, CW = Moebius', g(254), g(6), g(370), g(110))
def fb(n, y):
    lab(f'WF{n}', (g(258), y), 'l'); W((g(258), y), (g(262), y))
    rv = pot('B10k', f'FB {n}', g(262), y + 3.81, text=((g(258), y + g(3)), (g(258), y + g(4.5)), 'right'))
    GND(P(rv, '1'))
    w = P(rv, '2')
    r = Rh('1k', w[0] + g(1) + 3.81, w[1], d='Limiter series R'); W(w, P(r, '1'))
    L = (P(r, '2')[0] + g(2), w[1]); W(P(r, '2'), L)
    limiter(L, 'Feedback limiter (keeps self-oscillation musical)')
    W(L, (L[0] + g(7), L[1]))
    c = Ch('1u', L[0] + g(7) + g(1) + 3.81, L[1], d='Buffer coupling'); W((L[0] + g(7), L[1]), P(c, '1'))
    B = (P(c, '2')[0] + g(3), L[1]); W(P(c, '2'), B)
    r = Rv('1M', B[0], B[1] + g(3.5), side='r', d='Bias to VB'); W(B, P(r, '1'))
    q = P(r, '2'); W(q, (q[0], q[1] + g(1))); lab('VB', (q[0], q[1] + g(1)), 'l')
    pl, o = follower('U4', n, B[0] + g(12), B[1])
    W(B, pl); lab_at(o, f'FB{n}B', 4)
fb(1, g(20))
fb(2, g(46))
for n, y in ((1, g(16)), (2, g(42))):    # FB MAX trims: W -> 10k rheostat -> WF -> top of the FB pot
    lab(f'W{n}', (g(346), y), 'l'); W((g(346), y), (g(350), y))
    tv = pot('10k', f'FB MAX {n} (trim)', g(350), y + 3.81, mirror=None, sym='R_Potentiometer_Trim',
             text=((g(354), y + g(3)), (g(354), y + g(4.5)), 'left'))
    q = rheo(tv); lab_v(q, f'WF{n}', 1, 'l')
s.text('FB MAX trims: 0 = full feedback (as v0.2); turn up to lower the maximum repeat level.', g(330), g(60))
s.text('Limiter: the loop gain can reach 1 with FB up (and stays 1 across TWIST), so the 1N4148s cap self-oscillation at about +-0.6 V.', g(256), g(68))
TW = nx('RV')
# TWIST: gang A pin 1 (CCW) = FB1B, pin 3 (CW) = FB2B, wiper = RPT_1; gang B pin 4 (CCW) = FB2B, pin 6 (CW) = FB1B, wiper = RPT_2
s.part(TW, 'Device', 'R_Potentiometer_Dual_Separate', 'B10k dual', g(272), g(86), 0, unit=1, mirror='x', fp=FDUAL, bom=False, desc='TWIST (dual gang)',
       extra={'Panel': 'TWIST'}, text=((g(268), g(88)), (g(268), g(89.5)), 'right'))
s.part(TW, 'Device', 'R_Potentiometer_Dual_Separate', 'B10k dual', g(300), g(86), 0, unit=2, mirror='x', fp=FDUAL, bom=False, desc='TWIST (dual gang)',
       extra={'Panel': 'TWIST'}, text=((g(296), g(88)), (g(296), g(89.5)), 'right'))
lab_v(P(TW, '1'), 'FB1B', 2, 'l'); lab_v(P(TW, '3'), 'FB2B', -2, 'l'); lab_at(P(TW, '2'), 'RPT_1', 3)
lab_v(P(TW, '4'), 'FB2B', 2, 'l'); lab_v(P(TW, '6'), 'FB1B', -2, 'l'); lab_at(P(TW, '5'), 'RPT_2', 3)
s.text('TWIST CCW: line 1 repeats itself, line 2 itself (parallel). CW: each line repeats the other (Moebius: echoes at t1, t2, t1+t2).', g(256), g(100))
s.text('Middle: both. Fully up with both FB = same total loop gain at every TWIST setting.', g(256), g(103))

# ================================================================ SERIES switch, WET SUM + MIX (U5)
s.box('SERIES (SW1) + WET SUM (U5A) -> MIX. U5B spare (future stereo R)', g(254), g(114), g(370), g(158))
s.part('SW1', 'Switch', 'SW_SPDT', 'SPDT on-on', g(266), g(124), 0, fp='SuperFreq:SW_Taiway_100_SPDT_PC', bom=False,
       desc='SERIES: line 2 input from DRY (parallel) or W1 (series). Taiway 100 SPDT on-on, slotted pads',
       extra={'Panel': 'SERIES'}, text=((g(263), g(120)), (g(263), g(121.5)), 'left'))
lab_at(P('SW1', '2'), 'D2IN', 3, 'l'); lab_at(P('SW1', '1'), 'DRY', 3); lab_at(P('SW1', '3'), 'W1', 3)
ys = g(136)
pl, mi, ou = OP('U5', 1, g(300), ys)
W(pl, (pl[0] - g(4), pl[1])); lab('VB', (pl[0] - g(4), pl[1]), 'l')
tap = mi[0] - g(1); W(mi, (tap, mi[1]))
for i, dyy in ((1, 0), (2, 3)):
    r = Rh('10k', tap - g(1) - 3.81, mi[1] + g(dyy), d=f'Line {i} into the wet sum'); W(P(r, '2'), (tap, mi[1] + g(dyy)))
    c = Ch('1u', P(r, '1')[0] - g(1) - 3.81, mi[1] + g(dyy), d='Coupling'); W(P(c, '2'), P(r, '1'))
    lab_at(P(c, '1'), f'W{i}', 2, 'l')
fy = mi[1] + g(7); rx = ou[0] + g(1)
W((tap, mi[1]), (tap, fy + g(3)))
r = Rh('10k', (tap + rx) / 2, fy, d='Wet sum gain (raise for more wet)'); W((tap, fy), P(r, '1')); W(P(r, '2'), (rx, fy))
c = Ch('220p', (tap + rx) / 2, fy + g(3), d='HF roll-off'); W((tap, fy + g(3)), P(c, '1')); W(P(c, '2'), (rx, fy + g(3)))
W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, fy + g(3)))
c = CPh('10u', rx + g(1) + 3.81, ou[1], d='MIX coupling'); W((rx, ou[1]), P(c, '1'))
r = Rh('1k', P(c, '2')[0] + g(1) + 3.81, ou[1], d='Echo top-cut R'); W(P(c, '2'), P(r, '1'))
M = (P(r, '2')[0] + g(2), ou[1]); W(P(r, '2'), M)
W(M, (M[0], M[1] + g(2))); c = Cv('47n', M[0], M[1] + g(2) + 3.81, side='l', d='Echo top-cut'); GND(P(c, '2'))
W(M, (M[0] + g(4), M[1]))
rv = pot('B10k', 'MIX', M[0] + g(4), M[1] + 3.81, text=((M[0] + g(7), M[1] + g(3)), (M[0] + g(7), M[1] + g(4.5)), 'left'))
GND(P(rv, '1')); lab_at(P(rv, '2'), 'MIXW', 3)
pl, o = follower('U5', 2, g(340), g(150))
W(pl, (pl[0] - g(4), pl[1])); lab('VB', (pl[0] - g(4), pl[1]), 'l')

# ================================================================ LFO (U6) -> line 2 VCO
s.box('MODULATION: LFO (U6) -> DEPTH trim -> line 2 VCO only. RATE / DEPTH are internal trims', g(4), g(82), g(120), g(158))
yl = g(98)
pl, mi, ou = OP('U6', 1, g(40), yl, 'LM358')
W(pl, (pl[0] - g(6), pl[1])); lab('VB', (pl[0] - g(6), pl[1]), 'l')
r27 = Rh('47k', mi[0] - 6.35, mi[1], d='Max rate'); W(P(r27, '2'), mi)
q = P(r27, '1')
rv = pot('1M', 'RATE (trim)', q[0] - g(2), q[1] + 3.81, mirror=None, sym='R_Potentiometer_Trim',
         text=((q[0] - g(6), q[1] + g(3)), (q[0] - g(6), q[1] + g(4.5)), 'right'))
W(q, (q[0] - g(2), q[1]))
e = rheo(rv); W(e, (e[0], e[1] + g(2))); lab('SQR', (e[0], e[1] + g(2)), 'l')
fy = mi[1] + g(4); rx = ou[0] + g(1)
W(P(r27, '2'), (P(r27, '2')[0], fy))
c = Ch('1u', (P(r27, '2')[0] + rx) / 2, fy, d='LFO timing (film)'); W((P(r27, '2')[0], fy), P(c, '1')); W(P(c, '2'), (rx, fy))
W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, fy)); W((rx, ou[1]), (rx + g(4), ou[1])); lab('TRI', (rx + g(4), ou[1]))
pl, mi, ou = OP('U6', 2, g(80), yl, 'LM358')
W(mi, (mi[0] - g(6), mi[1])); lab('VB', (mi[0] - g(6), mi[1]), 'l')
ra = Rh('10k', pl[0] - 6.35, pl[1], d='Schmitt input')
W(P(ra, '2'), pl); q = P(ra, '1'); W(q, (q[0] - g(2), q[1])); lab('TRI', (q[0] - g(2), q[1]), 'l')
W((P(ra, '2')[0], pl[1]), (P(ra, '2')[0], pl[1] - g(4)))
rb = Rh('22k', (P(ra, '2')[0] + ou[0] + g(1)) / 2, pl[1] - g(4), d='Schmitt hysteresis')
W((P(ra, '2')[0], pl[1] - g(4)), P(rb, '1')); W(P(rb, '2'), (ou[0] + g(1), pl[1] - g(4)), (ou[0] + g(1), ou[1]))
W(ou, (ou[0] + g(1), ou[1])); W((ou[0] + g(1), ou[1]), (ou[0] + g(4), ou[1])); lab('SQR', (ou[0] + g(4), ou[1]))
ym = g(130)
lab('TRI', (g(10), ym), 'l'); W((g(10), ym), (g(13), ym))
c = CPh('4u7', g(15), ym, d='LFO coupling'); W((g(13), ym), P(c, '1'))
W(P(c, '2'), (g(24), ym))
rv = pot('100k', 'DEPTH (trim)', g(24), ym + 3.81, sym='R_Potentiometer_Trim', text=((g(20), ym + g(3)), (g(20), ym + g(4.5)), 'right'))
GND(P(rv, '1'))
w = P(rv, '2')
r = Rh('33k', w[0] + g(1) + 3.81, w[1], d='LFO injection: about +-4 % delay change at full DEPTH (tune on the breadboard)'); W(w, P(r, '1'))
c = nx('C'); s.part(c, 'Device', 'C', '10u', P(r, '2')[0] + g(1) + 3.81, w[1], 270, fp=FC, lcsc='C15850', desc='LFO coupling into TMIN_2', text='t')
W(P(r, '2'), P(c, '2'))
lab_at(P(c, '1'), 'TMIN_2', 3)
s.text('~0.5-12 Hz. Injected at the TIME 2 / 2k7 node: the same DEPTH gives the same percentage wobble at any TIME setting.', g(6), g(150))

# ================================================================ JACKS, FOOTSWITCH HEADER, STATUS LED
s.box('JACKS (board-mounted, top wall), FOOTSWITCH HEADER (SwitchPCB v2), STATUS LED', g(4), g(162), g(120), g(196))
JK = (('J2', 'INPUT', 14, 176, 'IJ'), ('J3', 'OUTPUT', 34, 176, 'OJ'))
for ref, name, x, y, net in JK:
    s.part(ref, 'Connector_Audio', 'AudioJack3_Switch', name, g(x), g(y), 0, fp=FJACK, desc=f'{name} jack: Tayda A-6728 (PJ-646F)',
           text=((g(x - 1.5), g(y - 4.4)), (g(x - 1.5), g(y - 3.4)), 'left'), bom=False)
    for pin in ('T', 'TN', 'R', 'RN', 'SN'):
        q = P(ref, pin)
        if pin == 'T': W(q, (q[0] + g(3), q[1])); lab(net, (q[0] + g(3), q[1]))
        else: s.noconnect(q)
    q = P(ref, 'S'); W(q, (q[0] + g(2), q[1])); gnd_down((q[0] + g(2), q[1]), 1)
s.part('J1', 'Connector_Generic', 'Conn_01x06', 'IJ/IN/LED/GND/OUT/OJ', g(66), g(178), 0, fp='Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical',
       desc='To the SwitchPCB v2 (same order as its pads): 1 IJ, 2 IN, 3 LED_K, 4 GND, 5 OUT, 6 OJ', text=((g(68), g(174)), (g(68), g(175.2)), 'left'), bom=False)
for pin, net in (('1', 'IJ'), ('2', 'IN'), ('3', 'LED_K'), ('5', 'OUT'), ('6', 'OJ')):
    q = P('J1', pin); W(q, (q[0] - g(3), q[1])); lab(net, (q[0] - g(3), q[1]), 'l')
q = P('J1', '4'); W(q, (q[0] - g(8), q[1]), (q[0] - g(8), q[1] + g(4))); GND((q[0] - g(8), q[1] + g(4)))
r = Rv('4k7', g(96), g(170), side='l', d='Status LED current'); V9(P(r, '1'))
led = nx('D'); s.part(led, 'Device', 'LED', 'LED', g(96), g(176), 90, fp='LED_THT:LED_D3.0mm', desc='Status LED (panel, back side); cathode to the footswitch via J1',
                      text='r', bom=False)
W(P(r, '2'), P(led, '2')); W(P(led, '1'), (g(96), g(180)), (g(99), g(180))); lab('LED_K', (g(99), g(180)))

# ================================================================ PANEL note
s.text('Panel (1590BB landscape): TIME 1, TIME 2, MIX over FB 1, TWIST, FB 2; SERIES toggle; status LED; footswitch. Internal trims: RATE, DEPTH, FB MAX 1 / 2.', g(4), g(202), 2, True)

s.write(OUT, title_block={'title': 'Dual Delay', 'rev': '1.0', 'company': 'Super-Freq', 'date': '2026-10-25',
                         'comments': ['Two PT2399 lines, TWIST blends self / cross feedback (parallel .. Moebius), SERIES toggle',
                                      'Blocks from Loop Echo (PT2399 network from Small Time); LFO on line 2. SMD for JLC (all basic parts except the PT2399s)']})
print('written', OUT)
