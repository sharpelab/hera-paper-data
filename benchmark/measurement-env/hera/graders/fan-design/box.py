"""The (n, F) box for vti-02 fans: hera/docs/fan-design-grader.md is the scheme and its evidence.

Two parts per column, each weighted by its effective light-tone periods p = F_light * W_eff, where
W_eff is the part's 1/B record with each row interval counted by how well it samples the part's tone:
  light  tone F_light, window from b_lo_light
  split  tone F_L, window from b_lo_split (p is then the F_L / F_heavy separation in FFT bins)
Each scores its best CAP columns whose light tones sit at least SPACING of an FFT bin (1 / W of its
own window) apart; quality = A * (light + split) / (2 * CAP), A from the case's signal lock-in.
p_call is the probability that the fan supports the call.  Per part, K independent columns are
detected (each with probability A * weight) and the call follows with probability
smoothstep(K / SATURATION); for the fan, the lesser of the two parts.  A fan must do both; no
column has to.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FLN = 10.3392          # F_L = (h/4e)|n|, tesla per 1e12 cm^-2
M = (2.0, 3.0)         # rows per tone period in one interval: its 1/B length counts 0 -> 1 (below 2 the tone aliases)
K = (1.5, 3.5)         # effective light-tone periods: column weight 0 -> 1 (live split detection is 50 % at ~2.5)
SPACING = 0.5          # FFT bins: the light-tone residuals of 08-25 r8 and 08-22 r8 decorrelate by half a bin
CAP = 7                # columns per part: 7 at half a bin covers the ~3 bins of F_light(n) that make the call
SATURATION = 4         # detected points at which the call is certain; fewer count in part
# A = P(a tone's Fourier peak clears the 4x-floor detection threshold), relative to the reference
# acquisition; median peak SNR scales as (I*sqrt(tau))**A_BETA with lognormal spread A_SIGMA across
# columns.  Fitted on 08-25 r8 (50 nA, 0.3 s: median F_L SNR 16) and 08-22 r8 (10 nA, 0.3 s: 5.8,
# split plateau 0.82); it reproduces the rig noise model at short tau (0.04 at 10 nA / 10 ms).
A_X_REF = 50 * 0.3 ** 0.5   # x = I[nA] * sqrt(tau[s])
A_SNR_REF = 16.0
A_THRESHOLD = 4.0
A_BETA = 0.63
A_SIGMA = 0.41
TAU_MIN_S = 3e-3       # below: the SR830's 2 f_ref ripple (sync filter off)
DELAY_MIN_TAU = 3.0
DELAY_PENALTY = 0.75
CLIP_FRACTION = 0.95
R_MAX_COVERED = (0.85, 3.25)   # the live composite's density coverage, actual frame
R_MAX_GLOBAL_OHM = 1557.5      # its worst point (n 1.47, 10 T), used outside coverage
E_N_V = 40e-9                  # lock-in input white floor, V/sqrt(Hz)

_T = np.genfromtxt(HERE / "tones.csv", delimiter=",", names=True)
_R = np.genfromtxt(HERE / "rmax.csv", delimiter=",", names=True)
TONE_MODELS = ("Halder_ABAB", "Shi_ABAB", "graphite_eps5.7", "B", "corpus", "env_lo", "env_hi")


def f_light(n: np.ndarray, model: str) -> np.ndarray:
    """Electron-side light tone (T) at actual density n (1e12 cm^-2); NaN off the table."""
    if model not in TONE_MODELS:
        raise ValueError(f"tone model must be one of {TONE_MODELS}, got {model!r}")
    sel = _T["n"] > 0
    na, fl = _T["n"][sel], _T["F_light_" + model.replace(".", "")][sel]
    o = np.argsort(na)
    return np.interp(n, na[o], fl[o], left=np.nan, right=np.nan)


def r_max(n: np.ndarray) -> np.ndarray:
    idx = np.abs(_R["n_actual_1e12"][None, :] - n[:, None]).argmin(1)
    inside = (n >= R_MAX_COVERED[0]) & (n <= R_MAX_COVERED[1])
    return np.where(inside, _R["R_max_ohm"][idx], R_MAX_GLOBAL_OHM)


def ramp(x: np.ndarray, edges: tuple[float, float]) -> np.ndarray:
    return np.clip((x - edges[0]) / (edges[1] - edges[0]), 0.0, 1.0)


def window(B: np.ndarray, b_lo: float) -> dict:
    """The rows at or above b_lo: their span in 1/B and their row intervals in 1/B."""
    Bw = B[B >= b_lo - 1e-9]
    du = np.diff(np.sort(1 / Bw)) if Bw.size >= 2 else np.zeros(0)
    return {"B_lo_T": b_lo, "B_from_T": float(Bw[0]) if Bw.size else None, "rows": int(Bw.size),
            "W_per_T": float(du.sum()), "intervals": du}


def w_eff(tone: np.ndarray, du: np.ndarray, m: tuple[float, float]) -> np.ndarray:
    """Per column, the 1/B record that samples its tone: each interval's length times ramp(rows per period)."""
    if not du.size:
        return np.zeros(tone.size)
    rows = np.divide(1.0, tone[:, None] * du[None, :], out=np.zeros((tone.size, du.size)), where=tone[:, None] > 0)
    return (du[None, :] * ramp(rows, m)).sum(axis=1)


def detection(x: float) -> float:
    def p(v):
        z = math.log(A_SNR_REF * (v / A_X_REF) ** A_BETA / A_THRESHOLD) / A_SIGMA
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))
    return float(p(x) / p(A_X_REF))


def acquisition(doc: dict, lockin: str) -> dict:
    """A for the signal lock-in (the one that records the tone): 0 when the sweep doesn't record it,
    None when its tau or the drive is untraced."""
    li = next((x for x in doc["lockins"] if x["name"] == lockin), None)
    I = doc["excitation_V"] / doc["bias_resistor_ohm"] if doc["excitation_V"] and doc["bias_resistor_ohm"] else None
    out = {"lockin": lockin, "recorded": li is not None, "I_A": I, "tau_s": None, "sensitivity_V": None,
           "x_nA_rt_s": None, "delay_over_tau": None, "quantized": False, "A": 0.0}
    if li is None:
        return out
    tau, sens = li["time_constant_s"], li["sensitivity_V"]
    out.update(tau_s=tau, sensitivity_V=sens)
    if tau is None or I is None:
        return {**out, "A": None}
    x = I * 1e9 * np.sqrt(tau)
    a = 0.0 if tau <= TAU_MIN_S else detection(x)
    delay_tau = doc["fast_delay_s"] / tau
    if delay_tau < DELAY_MIN_TAU:
        a *= DELAY_PENALTY
    quantized = sens is not None and 2.0 ** (np.ceil(np.log2(sens)) - 15) >= E_N_V * np.sqrt(5 / (64 * tau))
    return {**out, "A": a, "x_nA_rt_s": float(x), "delay_over_tau": delay_tau, "quantized": bool(quantized)}


def best_spaced(w: np.ndarray, f: np.ndarray, gap: float, cap: int) -> tuple[float, list[int]]:
    """The largest total weight of at most `cap` columns whose f sit pairwise >= gap apart, and their
    indices.  Exact: dynamic programming over the columns sorted by f."""
    idx = np.flatnonzero(w > 0)
    if not idx.size:
        return 0.0, []
    idx = idx[np.argsort(f[idx], kind="stable")]
    ws, fs = w[idx], f[idx]
    # before[i]: how many sorted columns sit at least `gap` below column i (all of them precede it)
    before = np.searchsorted(fs, fs - gap * (1 - 1e-9), side="right")
    D = np.zeros((idx.size + 1, cap + 1))
    for i in range(1, idx.size + 1):
        for c in range(1, cap + 1):
            D[i, c] = max(D[i - 1, c], ws[i - 1] + D[before[i - 1], c - 1])
    chosen, i, c = [], idx.size, cap
    while i > 0 and c > 0:
        if D[i, c] == D[i - 1, c]:
            i -= 1
        else:
            chosen.append(int(idx[i - 1]))
            i, c = int(before[i - 1]), c - 1
    return float(D[idx.size, cap]), sorted(chosen, key=lambda j: f[j])


def detected(ps: list[float]) -> np.ndarray:
    """P(K = k), k = 0..len(ps), for independent detections with probabilities ps."""
    d = np.zeros(len(ps) + 1)
    d[0] = 1.0
    for p in ps:
        d[1:] = d[1:] * (1 - p) + d[:-1] * p
        d[0] *= 1 - p
    return d


def p_at_least(ps: list[float], m: int) -> float:
    """P(at least m successes) for independent trials with probabilities ps."""
    return float(detected(ps)[m:].sum())


def smoothstep(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return 3 * x ** 2 - 2 * x ** 3


def p_call(ps: list[float], saturation: int = SATURATION, shape=smoothstep) -> float:
    """P(the call) from independent detections with probabilities ps: sum over k of P(K = k) * shape(k / saturation).
    One point is a spot check and counts little; the trend across density comes with the second and third."""
    d = detected(ps)
    return float(d @ shape(np.arange(d.size) / saturation))


def score(B: np.ndarray, n_actual_cm2: np.ndarray, doc: dict, *, b_lo_light: float, b_lo_split: float,
          tone_model: str, signal_lockin: str, m: tuple[float, float] = M, k: tuple[float, float] = K, cap: int = CAP,
          spacing: float = SPACING) -> dict:
    B = np.unique(B[B > 0])
    n = np.asarray(n_actual_cm2, float) / 1e12
    light, split = window(B, b_lo_light), window(B, b_lo_split)
    acq = acquisition(doc, signal_lockin)
    fl = f_light(n, tone_model)
    electron = (n > 0) & ~np.isnan(fl)
    f = np.where(electron, fl, 0.0)
    sens, I, A = acq["sensitivity_V"], acq["I_A"], acq["A"]
    clipped = I * r_max(n) >= CLIP_FRACTION * sens if sens is not None and I is not None else np.zeros(n.size, bool)
    usable = electron & ~clipped
    comps = {}
    for name, tone, win in (("light", f, light), ("split", FLN * np.where(electron, n, 0.0), split)):
        gap = spacing / win["W_per_T"] if win["W_per_T"] else np.inf
        W = w_eff(tone, win["intervals"], m)
        periods = f * W
        w = np.where(usable, ramp(periods, k), 0.0)
        total, chosen = best_spaced(w, f, gap, cap)
        _, spread = best_spaced(w, f, gap, n.size)
        comps[name] = {"score": total,
                       "p_call": None if A is None else p_call([A * w[j] for j in spread]),
                       "min_spacing_T": gap if win["W_per_T"] else None, "chosen_n_actual_1e12": [float(n[j]) for j in chosen],
                       "chosen_weights": [float(w[j]) for j in chosen],
                       "chosen_periods": [float(periods[j]) for j in chosen], "columns_weighted": int((w > 0).sum()),
                       "columns_full": int((w >= 1).sum()),
                       "not_weighted": {"undersampled": int((usable & (W == 0)).sum()),
                                        "periods_short": int((usable & (W > 0) & (w == 0)).sum())}}
    flags = []
    if not acq["recorded"]:
        flags.append(f"{signal_lockin} not recorded: A = 0")
    elif A is None:
        flags.append("tau or drive not extracted: quality not scored")
    if acq["recorded"] and sens is None:
        flags.append("sensitivity not extracted: clipping not checked")
    if acq["quantized"]:
        flags.append("quantized: the sensitivity's LSB is at or above the per-point noise")
    return {
        "quality": None if A is None else A * (comps["light"]["score"] + comps["split"]["score"]) / (2 * cap),
        "p_call": None if A is None else min(comps["light"]["p_call"], comps["split"]["p_call"]),
        "light": comps["light"], "split": comps["split"], "A": A, "acquisition": acq,
        "columns": int(n.size), "hole_or_off_table": int((~electron).sum()), "clipped": int((electron & clipped).sum()),
        "windows": {p: {k2: v for k2, v in w.items() if k2 != "intervals"} for p, w in (("light", light), ("split", split))},
        "params": {"m": list(m), "k": list(k), "cap": cap, "spacing_bins": spacing, "saturation": SATURATION,
                   "tone_model": tone_model, "signal_lockin": signal_lockin, "b_lo_light_T": b_lo_light,
                   "b_lo_split_T": b_lo_split},
        "flags": flags,
    }
