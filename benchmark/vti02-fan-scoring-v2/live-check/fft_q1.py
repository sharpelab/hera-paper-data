"""Q1: per-column SdH FFT of R vs 1/B over [lo, hi]; peak SNR near model F_light / F_heavy / F_L."""
import numpy as np, sys, pandas as pd
sys.path.insert(0, '.')
from load import load, f_light, f_heavy, f_L
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

# additive (quadrature-channel) noise per fan, V rms per point (ynoise.py / tau_pair.py)
SIGV = {'0821-r8': 34e-9, '0822-r8': 22e-9, '0825-r8': 25e-9, '0824-r4': 37e-9}

def col_fft(Rcol, B, lo, hi, nfft=2048, deg=None):
    sel = (B >= lo - 1e-9) & (B <= hi + 1e-9)
    Bs = B[sel]; y = Rcol[sel]
    deg = deg if deg is not None else (3 if sel.sum() < 30 else 5)
    ok = np.isfinite(y)
    y = y - np.polyval(np.polyfit(Bs[ok], y[ok], deg), Bs); y = y - y.mean()
    u = 1 / Bs; o = np.argsort(u); u = u[o]; y = y[o]
    du = np.diff(u)
    if du.std() / du.mean() > 0.1:  # non-uniform: resample
        uu = np.linspace(u[0], u[-1], len(u)); y = np.interp(uu, u, y); u = uu
    m = len(u); d = (u[-1] - u[0]) / (m - 1); w = np.hanning(m)
    F = np.fft.rfftfreq(max(nfft, m), d); S = np.abs(np.fft.rfft(y * w, n=max(nfft, m)))
    return F, S, m, d, np.sqrt((w**2).sum())

def band_peak(F, S, a, b):
    """highest interior local max in [a, b]; returns (F, amp) or (nan, 0)"""
    k = np.where((F >= a) & (F <= b))[0]
    k = k[(k > 0) & (k < len(F) - 1)]
    k = [i for i in k if S[i] >= S[i-1] and S[i] >= S[i+1]]
    if not k: return np.nan, 0.0
    i = max(k, key=lambda i: S[i]); return F[i], S[i]

def analyse(nm, lo_req, hi_req=None, tag=None, thr=4.0):
    d = load(nm); B = d['B']; R = d['R']; I = np.median(np.abs(d['I']))
    lo = max(lo_req, B.min()); hi = min(hi_req or B.max(), B.max())
    rows = []
    specs = []
    for j in range(d['nfast']):
        n = d['n'][j]
        if n < 0.3: continue
        F, S, m, du, wn = col_fft(R[:, j], B, lo, hi)
        nyq = 0.5 / du; span = 1 / lo - 1 / hi; dF = 1 / span
        fl, fh, fL = f_light(n), f_heavy(n), f_L(n)
        # floors: (a) measured additive noise, (b) empirical median above 1.12 F_L
        floor_a = SIGV[nm] / I * wn * np.sqrt(np.log(2))          # Rayleigh median of pure noise
        hb = (F > 1.12 * fL) & (F < 0.95 * nyq)
        floor_b = np.median(S[hb]) if hb.sum() > 20 else np.nan
        floor = floor_b if np.isfinite(floor_b) else floor_a
        pl = band_peak(F, S, 0.08 * fL, 0.33 * fL)
        ph = band_peak(F, S, 0.66 * fL, 0.895 * fL)
        pL = band_peak(F, S, 0.925 * fL, 1.08 * fL)
        # merged? heavy and F_L local maxima distinct and a dip between them
        sep = np.nan
        if np.isfinite(ph[0]) and np.isfinite(pL[0]):
            k = (F > ph[0]) & (F < pL[0]); sep = S[k].min() / min(ph[1], pL[1]) if k.any() else 1.0
        rows.append(dict(fan=nm, win=tag or f"{lo:.2f}-{hi:.1f}", col=j, n_act=round(n, 3), F_light_mod=round(fl, 2), F_heavy_mod=round(fh, 2),
                         F_L=round(fL, 2), dF=round(dF, 2), nyq=round(nyq, 1), rows=m, rpp_FL=round(1 / (fL * du), 2),
                         k_light_mod=round(fl * span, 2), floor_noise=round(floor_a, 1), floor_emp=round(floor_b, 1),
                         Fpk_light=round(pl[0], 2), snr_light=round(pl[1] / floor, 1), k_light_obs=round(pl[0] * span, 2) if np.isfinite(pl[0]) else np.nan,
                         Fpk_heavy=round(ph[0], 2), snr_heavy=round(ph[1] / floor, 1), Fpk_FL=round(pL[0], 2), snr_FL=round(pL[1] / floor, 1),
                         dip_heavy_FL=round(sep, 2)))
        specs.append((n, F, S / floor))
    df = pd.DataFrame(rows)
    df['det_light'] = (df.snr_light >= thr) & (df.Fpk_light >= 0.75 * df.dF)   # below ~dF it is the background-residual band
    df['det_heavy'] = df.snr_heavy >= thr
    df['det_FL'] = df.snr_FL >= thr
    df['split_heavy_FL'] = df.det_heavy & df.det_FL & (df.dip_heavy_FL < 0.8)
    return df, specs

def plot(specs, df, fname, title):
    ns = np.array([s[0] for s in specs]); F = specs[0][1]
    Z = np.array([np.interp(F, s[1], s[2]) for s in specs])
    o = np.argsort(ns)
    fig, ax = plt.subplots(figsize=(7, 5))
    pc = ax.pcolormesh(F, ns[o], np.log10(np.maximum(Z[o], 0.3)), shading='nearest', cmap='magma', vmin=0, vmax=np.log10(max(Z.max(), 10)))
    fig.colorbar(pc, ax=ax, label='log10 |FFT| / floor')
    nn = np.linspace(ns.min(), ns.max(), 50)
    ax.plot(f_light(nn), nn, 'c-', lw=1, label='model light'); ax.plot(f_heavy(nn), nn, 'c--', lw=1, label='model heavy'); ax.plot(f_L(nn), nn, 'w:', lw=1.2, label='F_L')
    ax.plot(df.dF.iloc[0] * np.ones(2), [ns.min(), ns.max()], 'y-', lw=0.8, label='dF (k=1)')
    ax.plot(2 * df.dF.iloc[0] * np.ones(2), [ns.min(), ns.max()], 'y:', lw=0.8, label='2 dF (k=2)')
    dl = df[df.det_light]; ax.plot(dl.Fpk_light, dl.n_act, 'o', mfc='none', mec='lime', ms=4, label='light det (SNR>=4)')
    ax.set_xlim(0, min(F.max(), 45)); ax.set_xlabel('F (T)'); ax.set_ylabel('n actual (1e12 cm^-2)'); ax.set_title(title, fontsize=9); ax.legend(fontsize=6, loc='lower right')
    fig.tight_layout(); fig.savefig(fname, dpi=110); plt.close(fig)

if __name__ == '__main__':
    pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 400)
    cfg = [('0821-r8', 2.0, None, 'o2.0'), ('0821-r8', 1.53, None, 'o1.53'),
           ('0822-r8', 2.0, None, 'o2.0'), ('0822-r8', 1.53, None, 'o1.53'), ('0822-r8', 1.0, None, 'full1.0'), ('0822-r8', 1.0, 6.0, 'ana1-6'),
           ('0825-r8', 2.0, None, 'o2.0'), ('0825-r8', 1.53, None, 'o1.53'), ('0825-r8', 1.0, None, 'full1.0'),
           ('0824-r4', 2.0, None, 'o2.0'), ('0824-r4', 1.53, None, 'o1.53'), ('0824-r4', 0.75, None, 'full0.75'),
           # below-onset windows
           ('0822-r8', 1.0, 2.0, 'sub1-2'), ('0825-r8', 1.0, 2.0, 'sub1-2'), ('0822-r8', 1.0, 1.53, 'sub1-1.53'), ('0825-r8', 1.0, 1.53, 'sub1-1.53')]
    allf = []
    for nm, lo, hi, tag in cfg:
        df, specs = analyse(nm, lo, hi, tag)
        allf.append(df)
        plot(specs, df, f"fft_{nm}_{tag}.png", f"{nm} window {tag}: [{max(lo, 0):.2f}, {hi or 'Bmax'}] T, dF={df.dF.iloc[0]} T")
    A = pd.concat(allf); A.to_csv('fft_columns.csv', index=False)
    print(A.groupby(['fan', 'win'], sort=False).agg(cols=('col', 'size'), dF=('dF', 'first'), rpp_min=('rpp_FL', 'min'),
          light=('det_light', 'sum'), heavy=('det_heavy', 'sum'), FL=('det_FL', 'sum'), split=('split_heavy_FL', 'sum')).to_string())
