"""Review arithmetic only. Not vehicle simulation, navigation code or qualification.

Run with Python 3; standard library only. Outputs JSON to stdout.
Radio: classic LoRa, explicit header, CRC on, CR 4/5, eight preamble symbols.
Coast: radial point mass, spherical nonrotating Earth, inverse-square gravity,
no thrust, drag, attitude, sensor noise, atmosphere or receiver implementation.
"""

import json
import math

G0 = 9.80665
R = 6_371_000.0
MU = G0 * R**2


def lora_airtime(payload_bytes, sf, bandwidth_hz):
    symbol_s = 2**sf / bandwidth_hz
    low_data_rate_opt = int(symbol_s >= 0.016)
    n = math.ceil((8 * payload_bytes - 4 * sf + 28 + 16) /
                  (4 * (sf - 2 * low_data_rate_opt)))
    payload_symbols = 8 + max(n * 5, 0)
    return (8 + 4.25 + payload_symbols) * symbol_s


def fspl(frequency_mhz, distance_km):
    return 20 * math.log10(4 * math.pi * frequency_mhz * 1e6 *
                         distance_km * 1e3 / 299_792_458)


def derivative(h, v):
    return v, -MU / (R + h)**2


def coast(h, v, dt):
    t = 0.0
    while v > 0:
        old_h, old_v = h, v
        a = derivative(h, v)
        b = derivative(h + dt * a[0] / 2, v + dt * a[1] / 2)
        c = derivative(h + dt * b[0] / 2, v + dt * b[1] / 2)
        d = derivative(h + dt * c[0], v + dt * c[1])
        h += dt * (a[0] + 2 * b[0] + 2 * c[0] + d[0]) / 6
        v += dt * (a[1] + 2 * b[1] + 2 * c[1] + d[1]) / 6
        if v <= 0:
            fraction = old_v / (old_v - v)
            return t + dt * fraction, old_h + fraction * (h - old_h)
        t += dt
    raise ValueError("Initial velocity must be positive")


def main():
    assert math.isclose(lora_airtime(64, 7, 125_000), 0.118016)
    assert math.isclose(lora_airtime(64, 12, 125_000), 2.793472)
    assert math.isclose(fspl(915, 100) - fspl(915, 10), 20)
    v80 = math.sqrt(2 * MU * (1 / (R + 80_000) - 1 / (R + 100_000)))
    t_apogee, h_apogee = coast(80_000, v80, 0.01)
    t_fine, h_fine = coast(80_000, v80, 0.005)
    assert abs(h_apogee - 100_000) < 0.001
    assert abs(h_apogee - h_fine) < 0.001
    assert abs(t_apogee - t_fine) < 0.00001
    h_at_500 = 1 / (1 / (R + 100_000) + 500**2 / (2 * MU)) - R
    results = {
        "scope": __doc__,
        "checks": "golden airtimes; 20 dB distance scaling; coast energy and half-step convergence passed",
        "lora_64B": [
            {"sf": sf, "bandwidth_hz": bw,
             "airtime_ms": round(lora_airtime(64, sf, bw) * 1000, 3),
             "airtime_percent_at_10Hz": round(lora_airtime(64, sf, bw) * 1000, 3)}
            for sf, bw in [(7, 125_000), (7, 250_000), (7, 500_000), (12, 125_000)]
        ],
        "fspl_100km_db": {str(f): round(fspl(f, 100), 3) for f in (868, 915, 2400)},
        "received_915MHz_100km_dbm_22dBm_0dBi_each_3dBloss": round(22 - 3 - fspl(915, 100), 3),
        "wio_vs_e22_module_body_area_reduction_percent": round(100 * (1 - 17.07 * 10.42 / (14 * 20)), 2),
        "radial_coast": {"v_at_80km_mps": v80, "seconds_80km_to_apogee": t_apogee,
                         "seconds_above_80km": 2 * t_apogee, "apogee_m": h_apogee,
                         "height_at_500mps_m": h_at_500, "g_at_100km_mps2": MU / (R + 100_000)**2,
                         "constant_g0_apogee_from_same_80km_state_m": 80_000 + v80**2 / (2 * G0)},
        "vertical_error_examples": [
            {"outage_s": t, "constant_bias_mg": mg,
             "bias_only_height_error_m": round(0.5 * (mg * 1e-3 * G0) * t**2, 4),
             "one_mps_initial_velocity_error_m": t}
            for t in (60, 120, 180) for mg in (0.1, 1, 10)
        ],
    }
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
