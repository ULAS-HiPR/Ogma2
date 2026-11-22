"""Track widths per current for the routing brief (section 5).

IPC-2152 baseline fit as published by smps.us (https://smps.us/pcb-calculator.html,
read 22 Nov 2026): A [sq mil] = (117.555 * dT^-0.913 + 1.15) * I^(0.84 * dT^-0.108 + 1.159).
The baseline is IPC-2152's still-air chart for a trace with no nearby plane, so it is
conservative for a 4-layer board with planes; no correction factor is applied here.
Width = A / copper thickness. Plain Python 3.
"""
MIL = 0.0254
def area_sqmil(i, dt):
    return (117.555 * dt ** -0.913 + 1.15) * i ** (0.84 * dt ** -0.108 + 1.159)

def width_mm(i, dt, t_mm):
    return area_sqmil(i, dt) / (t_mm / MIL) * MIL

print('I (A) | dT 10 C, 1 oz | dT 20 C, 1 oz | dT 20 C, 0.5 oz inner')
for i in (0.5, 1, 2, 2.5, 4, 6):
    print(f"{i:5} | {width_mm(i, 10, 0.035):6.2f} mm | {width_mm(i, 20, 0.035):6.2f} mm | {width_mm(i, 20, 0.0175):6.2f} mm")
