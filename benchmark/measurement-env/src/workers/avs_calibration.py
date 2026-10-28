"""AVS-47B calibration curves and sensor arrays.

Pure functions — no I/O, no GPIB, no InfluxDB. Consumed from avs_bridge
(https://github.com/sharpelab/avs_bridge).

Each calibration function takes resistance in ohms and returns temperature
in kelvin (0 if out of calibration range).
"""

import numpy as np


def Pt1000_cal(r):
    """Fridge/probe mixing chamber high."""
    if r < 25 or r > 1400:
        return 0
    coeffs = [
        -469.544790033,
        2142.429105073,
        -4278.355519358,
        4917.129912473,
        -3583.140137551,
        1717.059717072,
        -541.269035711,
        108.277676198,
        -12.478784052,
        0.631579503,
    ]
    return np.power(10, np.polynomial.polynomial.polyval(np.log10(r), coeffs))


def RuO2_10k_cal(r):
    """Fridge/probe 3K low, still, magnet."""
    r = r / 1000
    if r < 10.8 or r > 320:
        return 0
    coeffs = [
        6909.149278051,
        -38314.105969326,
        93795.121719782,
        -132881.190697614,
        120024.664196962,
        -71674.983797385,
        28300.34446649,
        -7125.704599868,
        1038.446472548,
        -66.75479913,
    ]
    return np.power(10, np.polynomial.polynomial.polyval(np.log10(r), coeffs)) / 1000


def RuO2_1k5_cal(r):
    """Fridge/probe 50 mK."""
    if r < 2000 or r > 17000:
        return 0
    coeffs = [
        -109406225.453069,
        264570367.275206,
        -284130767.924156,
        177858095.325872,
        -71516430.0477208,
        19156216.6038666,
        -3418108.54721648,
        391778.170838493,
        -26174.3212975398,
        776.590777082747,
    ]
    return np.power(10, np.polynomial.polynomial.polyval(np.log10(r), coeffs)) / 1000


def TT1304_cal(r):
    """Straight probe (Probe 1) mixing chamber low."""
    if r < 1600 or r > 75000:
        return 0
    coeffs = [
        -85991.97200244224,
        170101.13604422542,
        -146816.39437206375,
        72250.85152375244,
        -22180.90228857295,
        4351.18582667978,
        -532.76537613975,
        37.23402757752,
        -1.13741001238,
        0,
    ]
    return np.power(10, np.polynomial.polynomial.polyval(np.log10(r), coeffs)) / 1000


def TT1305_cal(r):
    """Fridge mixing chamber low."""
    if r < 1600 or r > 75000:
        return 0
    coeffs = [
        -163733.07258096553,
        333718.31665939908,
        -296819.44270129508,
        150507.78635092167,
        -47595.4776533601,
        9613.0779306768,
        -1211.12055853135,
        87.02647862814,
        -2.73081792303,
        0,
    ]
    return np.power(10, np.polynomial.polynomial.polyval(np.log10(r), coeffs)) / 1000


def TT1308_cal(r):
    """Rotator probe (Probe 2) mixing chamber low."""
    if r < 1600 or r > 75000:
        return 0
    coeffs = [
        252133.15476484009,
        -489555.75060558028,
        414687.06848509354,
        -200136.59816212513,
        60188.36749358858,
        -11549.4276043042,
        1380.88202910224,
        -94.0528605672,
        2.79391775134,
        0,
    ]
    return np.power(10, np.polynomial.polynomial.polyval(np.log10(r), coeffs)) / 1000


def S0927_cal(r):
    """Spare calibration curve."""
    if r < 600 or r > 100000:
        return 0
    coeffs = [
        340.0066359697,
        -428.9444332334,
        219.360664071,
        -56.2474119288,
        7.2087047046,
        -0.3691158405,
    ]
    return np.power(10, np.polynomial.polynomial.polyval(np.log10(r), coeffs)) / 1000


# Sensor arrays: (name, calibration_fn) indexed by channel 0-5.
# Only channel 3 (MixingCh_low) differs between fridge/probe1/probe2.

SENSORS_FRIDGE = [
    ("3K_low", RuO2_10k_cal),       # 0
    ("Still", RuO2_10k_cal),        # 1
    ("50mK", RuO2_1k5_cal),         # 2
    ("MixingCh_low", TT1305_cal),   # 3  fridge-specific
    ("MixingCh_high", Pt1000_cal),  # 4
    ("Magnet", RuO2_10k_cal),       # 5
]

SENSORS_PROBE1 = [
    ("3K_low", RuO2_10k_cal),       # 0
    ("Still", RuO2_10k_cal),        # 1
    ("50mK", RuO2_1k5_cal),         # 2
    ("MixingCh_low", TT1304_cal),   # 3  straight probe
    ("MixingCh_high", Pt1000_cal),  # 4
    ("Magnet", RuO2_10k_cal),       # 5
]

SENSORS_PROBE2 = [
    ("3K_low", RuO2_10k_cal),       # 0
    ("Still", RuO2_10k_cal),        # 1
    ("50mK", RuO2_1k5_cal),         # 2
    ("MixingCh_low", TT1308_cal),   # 3  rotator probe
    ("MixingCh_high", Pt1000_cal),  # 4
    ("Magnet", RuO2_10k_cal),       # 5
]
