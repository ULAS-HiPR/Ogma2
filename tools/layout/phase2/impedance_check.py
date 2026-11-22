"""Closed-form cross-check of the JLC impedance-calculator widths in the
routing brief (docs/briefs/layout-brief.md, section 2). Plain Python 3.

IPC-2141 approximations for surface microstrip and the edge-coupled pair,
without solder mask. They are estimates to catch a misread width, not a
replacement for the fab's calculator, which models the mask and its own
laminate data. The coplanar width is JLC's figure only.
"""
import math

def microstrip(w, h, t, er):
    return 87 / math.sqrt(er + 1.41) * math.log(5.98 * h / (0.8 * w + t))

def diff_pair(w, s, h, t, er):
    return 2 * microstrip(w, h, t, er) * (1 - 0.48 * math.exp(-0.96 * s / h))

MIL = 0.0254
T = 0.035          # 1 oz outer copper, mm (JLC calculator)
CASES = [          # stackup, L1-L2 prepreg h (mm), Dk for the estimate
    ('JLC04161H-3313', 0.0994, 4.05),   # Dk of the 0.1 mm prepreg, JLC's stackup page (JLC2313)
    ('JLC04161H-7628', 0.2104, 4.6),    # Dk of 7628, same page
]
JLC = {            # JLC impedance calculator, read 22 Nov 2026: widths in mil
    'JLC04161H-3313': {'se50': 5.94, 'diff90_s8': 6.05},
    'JLC04161H-7628': {'se50': 14.12, 'diff90_s8': 11.44},
}
for name, h, er in CASES:
    w1, w3 = (JLC[name][k] * MIL for k in ('se50', 'diff90_s8'))
    print(f"{name}: h={h} mm, Dk={er}")
    print(f"  50 ohm microstrip   w={w1:.3f} mm -> {microstrip(w1, h, T, er):5.1f} ohm")
    print(f"  90 ohm pair s=0.203 w={w3:.3f} mm -> {diff_pair(w3, 8 * MIL, h, T, er):5.1f} ohm")
