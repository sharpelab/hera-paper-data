"""vti-02 sr1 noise model v2 (input-referred, additive, current-independent), simulated on real sample times.

  1. white: e_w nV/rtHz at the lock-in input, through the filter (tau, slope): sampled with the filter-output ACF.
  2. line: the 14.9935 Hz interference (3rd harmonic of a mains/12-locked 5 Hz source) = f_ref + f0, f0 = 1.21628 Hz.
     Current i_n (sr0 measures ~95 pA at base T) through transfer impedance Z_t(B) = z0 + z1*|B|.
     Output amplitude H(f0; tau) * i_n * Z_t(B); coherent phase (slow walk).
  3. band: additive noise with amplitude g(B) (nV/rtHz, piecewise-linear knots) and a Gaussian offset-frequency band
     centred at +-f_b (width w_b) around f_ref. Output variance g^2 * int L(f) |H(f;tau)|^2 df with L normalised to
     int L df = 1 Hz... (g is the input density averaged over a 1 Hz band). Simulated by random Fourier features.
"""
import numpy as np, sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
from noise_q import acf4
F0 = 1.21628
ENBW = {6: 1/4, 12: 1/8, 18: 3/32, 24: 5/64}
KNOTS = np.array([0, 1, 2, 3, 4, 5, 6, 8, 10.5])
def H(f, tau, slope=24):
    return (1 + (2 * np.pi * np.asarray(f) * tau) ** 2) ** (-slope / 12)
_S = np.linspace(0, 40, 4001); _A = np.array([acf4(x) for x in _S])
def acf(x): return np.interp(x, _S, _A, right=0.0)
def white_rows(t, tau, rng):
    out = np.empty_like(t, dtype=float)
    for i in range(t.shape[0]):
        C = acf(np.abs(t[i][:, None] - t[i][None, :]) / tau)
        out[i] = np.linalg.cholesky(C + 1e-9 * np.eye(t.shape[1])) @ rng.standard_normal(t.shape[1])
    return out
def band_var(tau, f_b, w_b, slope=24):
    f = np.linspace(max(f_b - 5 * w_b, 0), f_b + 5 * w_b, 2001); L = np.exp(-0.5 * ((f - f_b) / w_b) ** 2); L /= np.trapezoid(L, f)
    return np.trapezoid(L * H(f, tau, slope) ** 2, f)   # output variance per (V^2/Hz input density) ... x g^2
def g_of_B(B, gk):
    return np.interp(np.abs(B), KNOTS, np.r_[0.0, gk])
def simulate(t, B, tau, i_n, prm, rng, slope=24, K=300, parts=('white', 'line', 'band')):
    """t, B [rows, cols]; returns quadrature-channel noise (V) sampled at t."""
    out = np.zeros(t.shape)
    if 'white' in parts:
        out += prm['e_w'] * 1e-9 * np.sqrt(ENBW[slope] / tau) * white_rows(t, tau, rng)
    tt = t - t.min()
    if 'line' in parts:
        ph = 2 * np.pi * F0 * tt + rng.uniform(0, 2 * np.pi)
        out += H(F0, tau, slope) * i_n * (prm['z0'] + prm['z1'] * np.abs(B)) * np.sin(ph)
    if 'band' in parts:
        # random Fourier features drawn from L(f)|H|^2 (importance: draw from L, weight by |H|)
        fk = np.abs(prm['f_b'] + prm['w_b'] * rng.standard_normal(K))
        wk = H(fk, tau, slope); pk = rng.uniform(0, 2 * np.pi, K)
        x = np.zeros(t.size); T = tt.ravel()
        for j in range(0, K, 50):
            x += (wk[j:j+50, None] * np.cos(2 * np.pi * fk[j:j+50, None] * T[None, :] + pk[j:j+50, None])).sum(0)
        x *= np.sqrt(2.0 / K)          # E[x^2] = mean(wk^2) = int L |H|^2
        out += (g_of_B(B, prm['g']) * 1e-9 * x.reshape(t.shape))
    return out
