"""Light-tone scan: over a window, least-squares fit of a cubic-in-1/B background + the known tones (heavy, F_L,
2 heavy; each with a linear-in-1/B amplitude envelope) + one scan tone f (same envelope); SNR(f) = scan-tone
amplitude / its standard error, with sigma from the fit residual (so unmodelled structure counts as noise).
The light tone is 'present' when the SNR(f) maximum in [0.5, 1.6] x F_light(model) clears 4 and sits within
max(0.5 dF, 0.3 T) of F_L - heavy (the Luttinger light tone).  Writes lightscan.csv."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from common import model

CASES = {'0822-r7': [((0.6, 4.5), [6.75, 9.38, 13.5]), ((0.75, 3.0), [6.75, 9.38, 13.5])],
         '0824-r5-c0': [((0.51, 6.01), [5.90, 7.50, 11.4]), ((0.75, 6.01), [5.90, 7.50, 11.4])],
         '0825-r7-c0': [((1.5, 6.0), [6.54, 8.71, 13.1])]}


def design(u, freqs, u0, span):
    x = (u - u0) / span
    cols = [x ** p for p in range(4)]
    for f in freqs:
        for env in (np.ones_like(u), x):
            cols += [env * np.cos(2 * np.pi * f * u), env * np.sin(2 * np.pi * f * u)]
    return np.array(cols).T


def scan(B, R, lo, hi, known, fgrid):
    s = (B >= lo) & (B <= hi) & np.isfinite(R)
    u = 1 / B[s]; y = R[s]; du = np.gradient(u) if False else None
    o = np.argsort(u); u, y = u[o], y[o]
    w = np.sqrt(np.gradient(u) / np.median(np.gradient(u)))      # uniform-in-1/B weighting
    u0, span = u[0], u[-1] - u[0]
    X0 = design(u, known, u0, span) * w[:, None]
    c0, *_ = np.linalg.lstsq(X0, y * w, rcond=None)
    sig = np.sqrt(np.sum((X0 @ c0 - y * w) ** 2) / (u.size - X0.shape[1]))
    out = []
    for f in fgrid:
        X = np.column_stack([X0, (np.cos(2 * np.pi * f * u)) * w, (np.sin(2 * np.pi * f * u)) * w])
        c, *_ = np.linalg.lstsq(X, y * w, rcond=None)
        r = X @ c - y * w; s2 = np.sum(r ** 2) / (u.size - X.shape[1])
        cov = np.linalg.pinv(X.T @ X) * s2
        a, b = c[-2], c[-1]; A = np.hypot(a, b); v = np.array([a, b]) / max(A, 1e-300)
        out.append(A / np.sqrt(v @ cov[-2:, -2:] @ v))
    return np.array(out), 1 / span, sig


if __name__ == '__main__':
    tr = {t['id']: t for t in load_all(include_ramp=False)}
    rows = []
    fgrid = np.arange(0.8, 5.01, 0.02)
    todo = list(CASES.items())
    for k in [f'0824-r4-c{j}' for j in range(0, 7)]:
        t = tr[k]; n = abs(t['n_act_e']); fl, fh, fL = model(n)
        todo.append((k, [((0.76, 6.01), [fh, fL, 2 * fh])]))
    for k, wins in todo:
        t = tr[k]
        for (lo, hi), known in wins:
            snr, dF, sig = scan(t['B'], t['R'], lo, hi, known, fgrid)
            f_lutt = known[1] - known[0]
            n = abs(t['n_act_e']) if k.startswith('0824-r4') else {'0822-r7': 0.907, '0824-r5-c0': 0.725, '0825-r7-c0': 0.842}[k]
            flm = model(n)[0]
            band = (fgrid >= max(0.5 * flm, 0.75 * dF)) & (fgrid <= 1.6 * flm)
            i = np.argmax(np.where(band, snr, -1))
            loc = [fgrid[j] for j in range(1, fgrid.size - 1) if snr[j] >= snr[j - 1] and snr[j] >= snr[j + 1] and snr[j] >= 4]
            rows.append(dict(trace=k, window=f'{lo}-{hi}', n_ref=round(n, 3), dF=round(dF, 2), light_model=round(flm, 2), light_luttinger=round(f_lutt, 2),
                             best_F=round(fgrid[i], 2), best_snr=round(snr[i], 1), present=bool(snr[i] >= 4 and abs(fgrid[i] - f_lutt) <= max(0.5 * dF, 0.3)),
                             all_peaks_snr4=' '.join(f'{x:.2f}' for x in loc), resid_sigma=round(sig, 1)))
            print(rows[-1])
    pd.DataFrame(rows).to_csv('lightscan.csv', index=False)
