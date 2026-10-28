"""Clean maps (cached) + acquisition + live-check detection for synth-score."""
import sys, warnings, pickle, time
warnings.filterwarnings('ignore'); sys.dont_write_bytecode = True
from pathlib import Path
import numpy as np
TOP = Path('/data/sharpelab/hera-data/vti02-fan-scoring-v2')
sys.path[:0] = [str(TOP / 'synth-calibrate'), str(TOP / 'model-reconcile'), str(TOP / 'live-check')]
import vti02_sim as vs
import tone_fn as TF
from fft_q1 import col_fft, band_peak
HERE = Path(__file__).resolve().parent
CACHE = HERE / 'work'; CACHE.mkdir(exist_ok=True)
P = vs.load_params()
RFIT = (0.0394, 0.1235)


def _hal_t(n):
    f, h, _ = TF.tone_fn(float(n), 'e', 'Halder_ABAB', warn=False)
    return (f, h) if f > 0.05 else (0.0, 10.3392 * n)


def _hal_m(n):
    ml, mh = TF.mstar_fn(float(n), 'e', 'Halder_ABAB')
    return max(ml, 1e-3), mh


TONES = {'halder': (_hal_t, _hal_m), 'observed': (vs.observed_tones, vs.corpus_masses), 'corpus': (vs.corpus_tones, vs.corpus_masses)}


def light_ref(tone, n):
    """|F_light| of the simulated tone model at n (truth for light_true)."""
    return np.array([abs(float(TONES[tone][0](x)[0])) for x in n])


def clean(d, tone):
    f = CACHE / f"clean_{d['label'].replace('/', '_').replace(' ', '_')}_{tone}.npy"
    if f.exists():
        return np.load(f)
    t0 = time.time()
    tf, mf = TONES[tone]
    R = vs.clean_R(d['B'], d['n_sim'], P, tf, mf, 1.0)
    np.save(f, R)
    print(f"clean {d['label']} {tone} {R.shape} {time.time() - t0:.1f}s", flush=True)
    return R


def acquire(Rc, B, I, tau, sens, fd, rng, excess):
    p = dict(P, e_excess_V_rtHz=excess)
    return vs.acquire(Rc, B, I, tau, sens, rng, p, 24, fd)


def acq_stats(Rc, I, tau, sens, excess):
    sig = np.hypot(P['e_n_V_rtHz'], excess) * np.sqrt(vs.ENBW[24] / tau)
    V = np.abs(Rc) * I
    return dict(clip_frac=float((V >= 1.092 * sens).mean()), near_fs=float((V >= 0.95 * sens).mean()),
                lsb_over_sigma=float(vs.lsb(sens) / sig), osc_over_lsb=float(np.median(np.std(Rc, 0)) * I / vs.lsb(sens)), sigma_V=sig)


def detect(R, B, n, ref, lo, hi=None, thr=4.0):
    """live-check analyse + q1_eval light_true / split_true on columns of R (rows on sorted B).
    ref: truth light tone per column (sim tone); the RFIT observed-curve truth is also returned."""
    lo = max(lo, B.min()); hi = min(hi or B.max(), B.max())
    span = 1 / lo - 1 / hi; dF = 1 / span
    out = []
    for j in range(R.shape[1]):
        F, S, m, du, wn = col_fft(R[:, j], B, lo, hi)
        nyq = 0.5 / du; fL = 10.3392 * n[j]
        hb = (F > 1.12 * fL) & (F < 0.95 * nyq)
        floor = np.median(S[hb]) if hb.sum() > 20 else np.nan
        pl = band_peak(F, S, 0.08 * fL, 0.33 * fL)
        ph = band_peak(F, S, 0.66 * fL, 0.895 * fL)
        pL = band_peak(F, S, 0.925 * fL, 1.08 * fL)
        sep = np.nan
        if np.isfinite(ph[0]) and np.isfinite(pL[0]):
            k = (F > ph[0]) & (F < pL[0]); sep = S[k].min() / min(ph[1], pL[1]) if k.any() else 1.0
        sl, sh, sL = pl[1] / floor, ph[1] / floor, pL[1] / floor
        tol = max(0.5 * dF, 0.75)
        lt = bool(sl >= thr and abs(pl[0] - ref[j]) <= tol)
        lt_rfit = bool(sl >= thr and abs(pl[0] - np.polyval(RFIT, n[j]) * fL) <= tol)
        split = bool(sh >= thr and sL >= thr and sep < 0.8 and (pL[0] - ph[0]) >= 0.5 * dF)
        out.append((lt, lt_rfit, split, sl, sh, sL, pl[0], np.isfinite(floor)))
    a = np.array(out, dtype=object)
    return dict(light=a[:, 0].astype(bool), light_rfit=a[:, 1].astype(bool), split=a[:, 2].astype(bool),
                snr_light=a[:, 3].astype(float), snr_heavy=a[:, 4].astype(float), snr_FL=a[:, 5].astype(float),
                Fpk=a[:, 6].astype(float), floor_ok=a[:, 7].astype(bool), W=span, dF=dF, lo=lo)


def capped(mask, f, W):
    if not mask.any():
        return 0.0
    f = f[mask]; dF = 1 / W
    cell = np.floor((f - f.min()) / dF + 1e-9).astype(int)
    return min(15, np.minimum(3, np.bincount(cell)).sum()) / 15.0
