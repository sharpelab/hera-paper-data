"""Physical refits of the ABAB partition p = F_light / F_L vs F_L on the training sessions (08-25 + 08-22, electron),
held-out on 08-21, 08-24 and the hole side. Model families (fixed = corpus ABAB values unless named):
  corpus : corpus ABAB set, gamma3 = 0 (radial solve)           -- no free parameter
  A      : fit gamma2, gamma3 = 0                                -- 1 free parameter
  B      : fit gamma2, gamma3 = 0.3 eV fixed (graphite literature; 2D solve)   -- 1 free parameter
  C      : fit gamma2 and Delta', gamma3 = 0.3 fixed              -- 2 free parameters
Uncertainties: chi2 scaled to chi2/dof = 1, then inflated by sqrt(N / N_eff), N_eff = tone cells
(per session x tone: F span / dF). Outputs fit_results.json, fit_curves.csv, heldout.csv."""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, '.')
import swm

FLN = swm.FL_PER_N
P = pd.read_csv('partition_points.csv', dtype={'session': str})
TR = P[P.split == 'train']
NE = np.linspace(0.95, 3.4, 50); NH = np.linspace(-1.25, -0.6, 14)
NN = np.concatenate([NH, NE])


def curve(p, g3):
    t = swm.tones_2d(p, NN) if g3 else swm.tones(p, NN)
    return t[:, 0] / t[:, 2]


def predict(cv, side, FL):
    FL = np.asarray(FL, float)
    if side == 'e':
        return np.interp(FL, FLN * NE, cv[len(NH):])
    return np.interp(FL, (FLN * np.abs(NH))[::-1], cv[:len(NH)][::-1])


def chi2(cv, D):
    r = (D.y - np.array([predict(cv, s, f) for s, f in zip(D.side, D.F_L_ref)])) / D.sy
    return float(np.sum(r ** 2)), r


# N_eff: tone cells per (session, tone)
cells = 0.0
for (s, t), g in TR.groupby(['session', 'tone']):
    F = g.y * g.F_L_ref if t == 'light' else (1 - g.y) * g.F_L_ref
    cells += max(1.0, (F.max() - F.min()) / g.dF.median())
N = len(TR); infl = N / cells
print(f'training points {N}, tone cells {cells:.1f}, inflation x{np.sqrt(infl):.2f} on sigma')

res = {}
curves = {'n': NN.tolist()}
cv0 = curve(swm.ABAB, False); curves['corpus'] = cv0.tolist()
c0, _ = chi2(cv0, TR); res['corpus'] = dict(chi2=c0, dof=N, params={})


def scan1(g3):
    g2s = np.round(np.arange(-0.030, -0.0049, 0.001), 4)
    out = []
    for g2 in g2s:
        cv = curve(swm.params(g2=g2, g3=g3), g3 != 0.0)
        out.append((g2, chi2(cv, TR)[0], cv))
    return out


def profile(vals, chis, dof):
    chis = np.array(chis); i = int(np.argmin(chis))
    scale = chis[i] / dof * infl
    # parabola through the minimum neighbourhood
    j = slice(max(i - 3, 0), min(i + 4, len(vals)))
    a, b, c = np.polyfit(vals[j], chis[j], 2)
    x0 = -b / (2 * a); sig = np.sqrt(scale / a)
    return x0, sig, chis[i], scale


for name, g3 in (('A', 0.0), ('B', 0.3)):
    sc = scan1(g3)
    v = np.array([x[0] for x in sc]); ch = [x[1] for x in sc]
    x0, sig, cmin, scale = profile(v, ch, N - 1)
    cv = curve(swm.params(g2=x0, g3=g3), g3 != 0.0)
    res[name] = dict(chi2=chi2(cv, TR)[0], dof=N - 1, params=dict(g2=x0, sig_g2=sig, g3=g3), scale=scale)
    curves[name] = cv.tolist()
    for dg in (-1, 1):
        curves[f'{name}_g2{"+" if dg > 0 else "-"}1s'] = curve(swm.params(g2=x0 + dg * sig, g3=g3), g3 != 0.0).tolist()
    print(name, f'gamma2 = {x0:.4f} +- {sig:.4f} eV, chi2 {cmin:.1f}/{N - 1}, scale {scale:.2f}')

# C: gamma2 x Delta'
g2s = np.round(np.arange(-0.028, -0.0049, 0.001), 4); dps = np.round(np.arange(0.0, 0.1001, 0.01), 3)
G = np.zeros((len(g2s), len(dps)))
for i, g2 in enumerate(g2s):
    for j, dp in enumerate(dps):
        G[i, j] = chi2(curve(swm.params(g2=g2, g3=0.3, dp=dp), True), TR)[0]
i, j = np.unravel_index(np.argmin(G), G.shape)
scale = G[i, j] / (N - 2) * infl
ok = (G - G[i, j]) / scale <= 1.0
res['C'] = dict(chi2=float(G[i, j]), dof=N - 2, scale=scale,
                params=dict(g2=float(g2s[i]), g2_1s=[float(g2s[ok.any(1)].min()), float(g2s[ok.any(1)].max())],
                            dp=float(dps[j]), dp_1s=[float(dps[ok.any(0)].min()), float(dps[ok.any(0)].max())], g3=0.3))
curves['C'] = curve(swm.params(g2=float(g2s[i]), g3=0.3, dp=float(dps[j])), True).tolist()
np.save('chi2_grid_C.npy', G)
print('C', res['C']['params'], f"chi2 {G[i, j]:.1f}/{N - 2}")
json.dump(res, open('fit_results.json', 'w'), indent=1)
pd.DataFrame(curves).to_csv('fit_curves.csv', index=False)
