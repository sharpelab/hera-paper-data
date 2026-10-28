"""Noise model for the sr1 voltage channel on the vti-02 rig, and helpers to simulate it on a run's real timestamps.

  v(t_i) = white + broadband(B) + line
  white      : e_w nV/rtHz, white at the lock-in input -> filtered by the tau/slope response (sampled with its true ACF)
  broadband  : e_b(B) = b1 * B**p nV/rtHz, white at the input (same filter treatment)
  line       : additive current i_n at f_ref + f0 (f0 = 1.21628 Hz) through transfer impedance Z_t(B) = z0 + z1*B;
               lock-in output = H(f0; tau) * i_n * Z_t(B) * exp(i(2 pi f0 t + phi)), coherent, H = (1 + (2 pi f0 tau)^2)^(-slope/12)
"""
import numpy as np, sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
from noise_q import acf4
F0 = 1.21628
ENBW = {6: 1/4, 12: 1/8, 18: 3/32, 24: 5/64}
def H(f, tau, slope=24):
    return (1 + (2 * np.pi * f * tau) ** 2) ** (-slope / 12)
_S = np.linspace(0, 40, 4001); _A = np.array([acf4(x) for x in _S])
def acf(x): return np.interp(x, _S, _A, right=0.0)
def corr_noise(t, tau, rng):
    """unit-variance Gaussian samples at times t (1D, one row) with the 24 dB filter output ACF."""
    dtm = np.abs(t[:, None] - t[None, :]) / tau
    C = acf(dtm)
    Lc = np.linalg.cholesky(C + 1e-9 * np.eye(len(t)))
    return Lc @ rng.standard_normal(len(t))
_acf_cache = {}
def corr_noise_fast(t, tau, rng):
    # approximation good for dt >= 3 tau: only lags 1 and 2 matter
    n = len(t)
    if n < 3: return rng.standard_normal(n)
    return corr_noise(t, tau, rng)
def simulate_quadrature(t, B, tau, i_n, prm, rng, slope=24, phase_walk_hz=3e-4, component=None):
    """t, B: arrays [rows, cols] (time s, field T). Returns simulated quadrature (V) with the model; component in (None,'white','bb','line')."""
    e_w, b1, p, z0, z1 = prm['e_w'], prm['b1'], prm['p'], prm['z0'], prm['z1']
    s = np.sqrt(ENBW[slope] / tau)
    out = np.zeros_like(t, dtype=float)
    nr = t.shape[0]
    for i in range(nr):
        g = corr_noise_fast(t[i], tau, rng)
        g2 = corr_noise_fast(t[i], tau, rng)
        Bi = np.abs(B[i])
        w = e_w * 1e-9 * s * g
        bb = b1 * 1e-9 * Bi ** p * s * g2
        out[i] = (w if component in (None, 'white') else 0) + (bb if component in (None, 'bb') else 0)
    # coherent line with a slow random phase walk (grid-frequency wander)
    tt = t.ravel(); o = np.argsort(tt); ts = tt[o]
    dph = 2 * np.pi * phase_walk_hz * np.sqrt(np.maximum(np.diff(ts, prepend=ts[0]), 0)) * rng.standard_normal(ts.size) * 0.1
    ph = 2 * np.pi * F0 * (ts - ts[0]) + rng.uniform(0, 2 * np.pi) + np.cumsum(dph)
    A = H(F0, tau, slope) * i_n * (z0 + z1 * np.abs(B.ravel()[o]))
    line = np.empty_like(tt); line[o] = A * np.sin(ph)
    if component in (None, 'line'):
        out = out + line.reshape(t.shape)
    return out
