"""Q3 per-tone onsets with the joint walk (jointwalk.py) on the hole traces; tone sets from tones.csv and the model.
Run from the measurement-env checkout.  Writes onsets_joint.csv."""
import os, sys
import numpy as np, pandas as pd
HERE = '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side'
sys.path.insert(0, HERE)
from load_hole import load_all
from common import model
from jointwalk import walk
from hera.analysis import _noise_sigma, _bg_subtract_B

# tone sets per trace: (name, F).  08-22 r7 uses its own tones (heavy 6.6-6.9 / F_L-like 9.38; light = difference 2.8)
SETS = {'0822-r7': [('heavy', 6.75), ('F_L', 9.38), ('light', 2.63), ('F_L/2', 4.72), ('2 heavy', 13.5), ('F_L+2light', 14.83), ('low-F 1.75', 1.75)],
        '0824-r5-c0': [('heavy', 5.90), ('F_L', 7.50), ('light', 1.55), ('2 heavy', 11.4)],
        '0825-r7-c0': [('heavy', 6.54), ('F_L', 8.71), ('light', 2.20), ('2 heavy', 13.1)]}


def tone_set(t):
    if t['id'] in SETS:
        return SETS[t['id']]
    n = abs(t['n_act_e']); fl, fh, fL = model(n)
    T = pd.read_csv(os.path.join(HERE, 'tones.csv'))
    h = T[(T.trace == t['id']) & T.tone.astype(str).str.match(r'^heavy \(|^heavy-light|^heavy \(')].sort_values('contrast_med', ascending=False)
    fho = float(h.F.iloc[0]) if len(h) else fh
    s = [('heavy', fho), ('F_L', fL), ('2 heavy', 2 * fho)]
    if fl > 0.5:
        s.append(('light', fl))
    return s


if __name__ == '__main__':
    os.chdir(HERE)
    rows = []
    for t in load_all(include_ramp=False):
        if not (t['id'] in SETS or (t['id'].startswith('0824-r4') and t['col'] <= 7)):
            continue
        B, R = t['B'], t['R']
        for bhi in ((4.5, 10.0) if t['id'] == '0822-r7' else (float(B.max()),)):
            s = B <= bhi
            bg = _bg_subtract_B(B[s], R[s], 5); u = 1 / B[s]; o = np.argsort(u); u, bg = u[o], bg[o]
            sig = _noise_sigma(bg)
            ts = tone_set(t)
            for name, f in ts:
                others = [x for _, x in ts if x != f]
                r, why = walk(u, bg, f, others, sig)
                base = dict(trace=t['id'], n_frame=round(t['n_frame'], 3), I_nA=round(t['I_nA'], 1), tau_s=t['tau_s'], b_hi=round(bhi, 2), record_lo=round(float(B.min()), 2),
                            sigma_ohm=round(sig, 2), tone=name, F=round(f, 2))
                if r is None:
                    rows.append(dict(base, note=why)); continue
                rows.append(dict(base, onset_B=round(r['onset_B'], 2), censored=r['censored'], lowest_window_B=round(r['lowest_window_B'], 2),
                                 max_snr=round(r['max_snr'], 1), snr_at_1T=round(r['snr_at_1T'], 1) if np.isfinite(r['snr_at_1T']) else np.nan))
    O = pd.DataFrame(rows); O.to_csv('onsets_joint.csv', index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300)
    print(O.to_string(index=False))
