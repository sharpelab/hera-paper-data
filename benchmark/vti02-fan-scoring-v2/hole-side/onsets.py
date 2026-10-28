"""Q3: per-tone low-field onsets on the hole side.
(a) hera.analysis.sdh_onset (f_min 1.0, clip check at the lock-in full scale) on each monotone trace;
(b) the same matched-filter walk (_track_tone, 3 periods, 5-sigma, white floor from _noise_sigma) at fixed
    frequencies: the observed heavy tone and the Halder light / F_L tones at the trace's reference density.
alias_B: the field below which the record holds < 2 rows per period of the tone (the onset is not measurable there).
Writes onsets.csv.  Run from the measurement-env checkout (uv run python ...)."""
import os, sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from common import model
from tones import n_ref, combos
from hera.analysis import sdh_onset, _track_tone, _noise_sigma, _bg_subtract_B

KW = dict(n_periods=3.0, min_periods=2.0, step_frac=0.25, min_pts=8, snr_threshold=5.0, gap_widths=0.5, marginal_mult=2.0)


def alias_B(B, f):
    u = np.sort(1 / B); du = np.diff(u); uc = 0.5 * (u[1:] + u[:-1])
    bad = 1 / (f * du) < 2
    return float(1 / uc[bad].min()) if bad.any() else None   # highest field with < 2 rows/period


def ident(F, n, dF=0.9):
    fl, fh, fL = model(n); fl = 0.0 if np.isnan(fl) else fl
    c = {k: v for k, v in combos(fl, fh, fL).items() if abs(F - v) <= max(0.6 * dF, 0.08 * F)}
    return ', '.join(sorted(c, key=lambda k: abs(F - c[k]))) or 'unassigned'


if __name__ == '__main__':
    os.chdir('/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
    heavy_obs = pd.read_csv('tones.csv')
    rows = []
    sel = lambda t: t['id'] in ('0822-r7', '0824-r5-c0', '0825-r7-c0') or (t['id'].startswith('0824-r4') and t['col'] <= 7)
    for t in [t for t in load_all(include_ramp=False) if sel(t)]:
        n, src = n_ref(t); B, R = t['B'], t['R']
        fs = t['sens_V'] / (t['I_nA'] * 1e-9)
        for bhi in ((4.5, 10.0) if t['id'] == '0822-r7' else (float(B.max()),)):
            base = dict(trace=t['id'], n_ref=round(n, 3), I_nA=round(t['I_nA'], 1), tau_s=t['tau_s'], rows=int(B.size), b_hi=bhi, record_lo=round(float(B.min()), 2))
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                try:
                    o = sdh_onset(R, B, b_hi=bhi, b_lo=float(B.min()), f_min=1.0, r_full_scale=fs)
                    for tt in o.tones:
                        rows.append(dict(base, method='sdh_onset', F=round(tt.freq, 2), identity=ident(tt.freq, n), onset_B=round(tt.onset_b, 2), censored=tt.censored,
                                         marginal=tt.marginal, near_residual=tt.near_residual, contrast=round(tt.contrast, 1), max_snr=round(float(tt.snr.max()), 1),
                                         alias_B=alias_B(B, tt.freq), headline=bool(abs(tt.freq - o.onset_freq) < 1e-9)))
                    for f, why in o.untracked:
                        rows.append(dict(base, method='sdh_onset', F=round(f, 2), identity=ident(f, n), onset_B=np.nan, note='untracked: ' + why[:80]))
                except Exception as e:
                    rows.append(dict(base, method='sdh_onset', note='error: ' + str(e)[:120]))
            # fixed-frequency walks
            s = (B >= B.min()) & (B <= bhi)
            bg = _bg_subtract_B(B[s], R[s], 5); u = 1 / B[s]; o_ = np.argsort(u); u, bg = u[o_], bg[o_]
            sig = _noise_sigma(bg)
            fl, fh, fL = model(n)
            hv = heavy_obs[(heavy_obs.trace == t['id']) & heavy_obs.tone.astype(str).str.startswith('heavy')]
            fho = float(hv.F.iloc[0]) if len(hv) else fh
            for name, f in (('heavy (observed)', fho), ('light (Halder)', fl), ('F_L', fL), ('2 heavy', 2 * fho)):
                if not np.isfinite(f) or f < 0.5:
                    continue
                tr_, why = _track_tone(u, bg, f, sig, **KW)
                if tr_ is None:
                    rows.append(dict(base, method='fixed-F walk', F=round(f, 2), identity=name, onset_B=np.nan, note=why[:90], alias_B=alias_B(B, f)))
                else:
                    rows.append(dict(base, method='fixed-F walk', F=round(f, 2), identity=name, onset_B=round(tr_['onset_b'], 2), censored=tr_['censored'],
                                     marginal=tr_['marginal'], max_snr=round(float(tr_['snr'].max()), 1), revived=tr_['revived'], alias_B=alias_B(B, f), sigma_ohm=round(sig, 2)))
    O = pd.DataFrame(rows); O.to_csv('onsets.csv', index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 400); pd.set_option('display.max_colwidth', 50)
    cols = ['trace', 'n_ref', 'b_hi', 'method', 'F', 'identity', 'onset_B', 'censored', 'marginal', 'max_snr', 'alias_B', 'note']
    print(O[[c for c in cols if c in O]].to_string(index=False))
