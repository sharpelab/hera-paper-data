"""Per-column tone extraction over all vti-02 SdH runs, several extraction choices per column.
FFT method mirrors live-check/fft_q1.py col_fft (poly-in-B background, Hann, direct in 1/B, zero-pad),
with a finer zero-pad for peak position. Tone search is anchored on a per-session F_L comb fit.
Outputs: columns_raw.csv (per column x choice), columns.csv (per column medians), session_frames.csv."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/model-fit')
from runs import RUNS, load_run

FLN = 10.3392
# per-run window table: (lo0, hi0, hi1)
WIN = {('0821', 5): (2.0, 10.0, 7.0), ('0821', 8): (2.4, 10.0, 8.0), ('0821', 'lk'): (2.4, 10.0, 7.0),
       ('0822', 6): (1.0, 8.0, 5.5), ('0822', 7): (1.0, 5.0, 4.0), ('0822', 8): (1.0, 8.0, 6.0), ('0822', 'lk'): (2.0, 7.0, 5.5),
       ('0823', 6): (0.7, 8.0, 6.0), ('0824', 4): (0.76, 6.0, 4.5), ('0824', 5): (0.6, 6.0, 4.0),
       ('0825', 7): (1.5, 6.0, 5.0), ('0825', 8): (1.0, 8.0, 6.0)}
S0 = {'0821': 0.92, '0822': 0.886, '0823': 1.0, '0824': 0.90, '0825': 1.0}   # search-band prior only


def fft(B, R, lo, hi, deg, nfft=16384):
    sel = (B >= lo - 1e-9) & (B <= hi + 1e-9) & np.isfinite(R)
    Bs, y = B[sel], R[sel]
    if len(Bs) < 12:
        return None
    y = y - np.polyval(np.polyfit(Bs, y, deg), Bs); y = y - y.mean()
    u = 1 / Bs; o = np.argsort(u); u, y = u[o], y[o]
    u, iu = np.unique(u, return_index=True); y = y[iu]
    du = np.diff(u)
    if du.std() / du.mean() > 0.1:
        uu = np.linspace(u[0], u[-1], len(u)); y = np.interp(uu, u, y); u = uu
    m = len(u); d = (u[-1] - u[0]) / (m - 1)
    F = np.fft.rfftfreq(max(nfft, m), d); S = np.abs(np.fft.rfft(y * np.hanning(m), n=max(nfft, m)))
    return F, S, 1 / (u[-1] - u[0]), 0.5 / d


def peak(F, S, a, b):
    k = np.where((F >= a) & (F <= b))[0]
    k = k[(k > 0) & (k < len(F) - 1)]
    k = [i for i in k if S[i] >= S[i - 1] and S[i] >= S[i + 1]]
    if not k:
        return np.nan, 0.0
    i = max(k, key=lambda i: S[i])
    return F[i], S[i]


def choices(key):
    lo0, hi0, hi1 = key
    return [(lo, hi, deg) for lo in (lo0, round(lo0 * 1.2, 3)) for hi in (hi0, hi1) for deg in (3, 5)]


def spectra(cols):
    out = []
    for c in cols:
        key = WIN.get((c['session'], c['run'])) or WIN[(c['session'], c['kind'])]
        for lo, hi, deg in choices(key):
            lo_, hi_ = max(lo, c['B'].min()), min(hi, c['B'].max())
            r = fft(c['B'], c['R'], lo_, hi_, deg)
            if r is None:
                continue
            out.append((c, (lo_, hi_, deg), r))
    return out


def floor_of(F, S, FLg, nyq):
    hb = (F > 1.15 * FLg) & (F < 0.95 * nyq)
    if hb.sum() > 50:
        return np.median(S[hb])
    hb = (F > 0.5 * FLg) & (F < 0.95 * nyq)
    return np.percentile(S[hb], 30) if hb.sum() > 20 else np.median(S)


def comb_scale(specs, session):
    """(s, n0) maximising the mean F_L-tone SNR along F = FLN*s*(n_frame - n0), full-window choices, n>0 columns."""
    best = None
    ss = np.arange(0.70, 1.20, 0.0025); n0s = np.arange(-0.25, 0.2501, 0.01)
    use = [(c, ch, r) for c, ch, r in specs if ch[2] == 5 and c['n_frame'] > 0.4]
    snr = []
    for c, ch, (F, S, dF, nyq) in use:
        fl = floor_of(F, S, FLN * S0[session] * c['n_frame'], nyq)
        snr.append((c['n_frame'], F, S / fl, nyq))
    grid = np.zeros((len(ss), len(n0s)))
    for n, F, Z, nyq in snr:
        for j, n0 in enumerate(n0s):
            Fp = FLN * ss * (n - n0)
            v = np.interp(Fp, F, Z); v[Fp > 0.95 * nyq] = np.nan
            grid[:, j] += np.nan_to_num(np.log(np.maximum(v, 1e-3)))
    i, j = np.unravel_index(np.argmax(grid), grid.shape)
    return ss[i], n0s[j], grid, ss, n0s


def measure(specs, s, n0, lk_T=None):
    rows = []
    for c, (lo, hi, deg), (F, S, dF, nyq) in specs:
        n = c['n_frame']
        FLp = FLN * s * abs(n - n0)
        fl = floor_of(F, S, FLp, nyq)
        pL = peak(F, S, FLp - max(1.0, 0.07 * FLp), FLp + max(1.0, 0.07 * FLp))
        ref = FLp
        pl = peak(F, S, max(0.08 * ref, 0.75 * dF), 0.40 * ref) if n > 0 else peak(F, S, max(0.2 * ref, 0.75 * dF), 0.5 * ref)
        ph = peak(F, S, 0.64 * ref, 0.90 * ref) if n > 0 else peak(F, S, 0.5 * ref, 0.85 * ref)
        span = 1 / lo - 1 / hi
        rows.append(dict(session=c['session'], run=c['run'], kind=c['kind'], col=c['col'], n_frame=round(n, 4), T_K=c['T_K'],
                         lo=lo, hi=hi, deg=deg, dF=dF, nyq=nyq, FL_pred=FLp,
                         F_L=pL[0], snr_L=pL[1] / fl, F_light=pl[0], snr_light=pl[1] / fl, F_heavy=ph[0], snr_heavy=ph[1] / fl,
                         k_light=pl[0] * span if np.isfinite(pl[0]) else np.nan, A_light=pl[1], A_heavy=ph[1], A_L=pL[1], floor=fl))
    return pd.DataFrame(rows)


if __name__ == '__main__':
    allraw, frames = [], []
    for sess in ('0821', '0822', '0824', '0825'):   # 0823 r6 excluded: 38 ramp rows, Nyquist 14-21 T < F_L above n ~ 1.4
        cols = [c for s, r, k in RUNS if s == sess for c in load_run(s, r, k)]
        specs = spectra(cols)
        fanspecs = [x for x in specs if x[0]['kind'] in ('fan', 'spot')]
        s, n0, grid, ss, n0s = comb_scale(fanspecs, sess)
        if sess == '0824':   # comb has no F_L tone to lock on (sr1 1 mV, LSB/noise 1.6); anchor on the 08-25 LL lever arm
            s, n0 = 0.90, 0.0
        prof = grid.max(axis=1)
        print(f'{sess}: comb scale s = {s:.4f}, n0 = {n0:+.3f}; profile half-max width in s: '
              f'{ss[prof > prof.max() - 0.5 * (prof.max() - np.median(prof))].min():.3f}-{ss[prof > prof.max() - 0.5 * (prof.max() - np.median(prof))].max():.3f}')
        frames.append(dict(session=sess, s_comb=s, n0_comb=n0))
        allraw.append(measure(specs, s, n0))
    raw = pd.concat(allraw); raw.to_csv('columns_raw.csv', index=False)
    pd.DataFrame(frames).to_csv('session_comb.csv', index=False)
