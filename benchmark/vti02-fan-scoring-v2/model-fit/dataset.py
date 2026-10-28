"""Assemble the partition data set (frame-free y = F_tone / F_L_ref vs F_L_ref) -> partition_points.csv.
Electron F_L_ref: per-session F_L-tone frame fit (session_frames.csv): 0825 origin s = 0.9496; 0822 with offset
(s = 0.8625, n0 = -0.100; chi2 18 -> 5.7); 0821 origin s = 0.927 (its low-n F_L tone merges with heavy at dF 3.8 T,
so the offset fit is not trusted). 0824 (no F_L anchor): F_L_ref = F_light + F_heavy (Luttinger), kept only where
the sum sits within 10 % of the 08-25 LL-lever-arm frame (0.90).
Hole points: F_L_ref = tone sum or the F_L tone, per point (named in 'fl_src').
Validity cuts: light used if k_light = F_light * span >= 2 (injection: bias <= 0.015 at k >= 2, +0.03..0.10 at k 1.5..1.9);
heavy used if F_L_ref - F_heavy >= 1.5 dF (resolved from the F_L tone)."""
import numpy as np, pandas as pd
FLN = 10.3392
C = pd.read_csv('columns_tones.csv', dtype={'session': str})
FR = {'0825': (0.9496, 0.0), '0822': (0.8625, -0.100), '0821': (0.927, 0.0)}
SIG_FRAME = {'0825': 0.002, '0822': 0.004, '0821': 0.01}   # relative, from fit + choice of offset model
pts = []
for _, r in C.iterrows():
    if r.kind == 'lk' and r.T_K > 2.0:
        continue                       # heated rungs repeat the base density; masses only
    if r.n_frame < 0:
        continue                       # hole points assembled below
    if r.session in FR:
        s, n0 = FR[r.session]; FLr = FLN * s * (r.n_frame - n0); src = 'frame'
        sfl = SIG_FRAME[r.session] * FLr
    elif r.session == '0824':
        if not (np.isfinite(r.F_light) and np.isfinite(r.F_heavy)):
            continue
        FLr = r.F_light + r.F_heavy; src = 'sum'
        if abs(FLr / (FLN * 0.90 * r.n_frame) - 1) > 0.10:
            continue
        sfl = np.hypot(r.sig_light, r.sig_heavy)
    else:
        continue
    kl = r.F_light * r.span if np.isfinite(r.F_light) else np.nan
    ok_l = np.isfinite(r.F_light) and kl >= 2.0
    ok_h = np.isfinite(r.F_heavy) and (FLr - r.F_heavy) >= 1.5 * r.dF
    base = dict(session=r.session, run=r.run, col=r.col, kind=r.kind, side='e', n_frame=r.n_frame, F_L_ref=FLr, fl_src=src,
                n_act=FLr / FLN, dF=r.dF, F_L_tone=r.F_L, F_light=r.F_light, sig_light=r.sig_light, k_light=kl,
                F_heavy=r.F_heavy, sig_heavy=r.sig_heavy)
    if src == 'sum':   # both tones define F_L_ref: a single partition value, light/sum
        if ok_l:
            p = r.F_light / FLr
            sp = np.hypot(r.sig_light * r.F_heavy, r.sig_heavy * r.F_light) / FLr ** 2
            pts.append(dict(base, tone='sum', y=p, sy=sp))
        continue
    if ok_l:
        pts.append(dict(base, tone='light', y=r.F_light / FLr, sy=np.hypot(r.sig_light / FLr, r.F_light * sfl / FLr ** 2)))
    if ok_h:
        pts.append(dict(base, tone='heavy', y=1 - r.F_heavy / FLr, sy=np.hypot(r.sig_heavy / FLr, r.F_heavy * sfl / FLr ** 2)))
# hole side (all test): numbers from columns_tones.csv, reference named per point
H = [('0822', 7, 0, 'heavy', 7.44, 0.10, 3.63 + 7.44, 'sum (3.63 + 7.44; 0.886 frame gives 10.99)'),
     ('0822', 7, 0, 'light', 3.63, 0.71, 3.63 + 7.44, 'sum'),
     ('0825', 7, 0, 'heavy', 6.68, 0.32, FLN * 0.9496 * 0.9, 'frame 0.9496 (only the heavy tone resolved, dF 2.4 T)'),
     ('0824', 5, 0, 'heavy', 5.86, 0.15, 7.74, 'F_L tone 7.74'),
     ('0824', 4, 1, 'heavy', 6.56, 0.23, 8.81, 'F_L tone 8.81'),
     ('0824', 4, 2, 'sum', 1.78, 0.08, 1.78 + 5.92, 'sum'),
     ('0824', 4, 3, 'sum', 1.68, 0.18, 1.68 + 5.64, 'sum')]
for s, run, col, tone, F, sF, FLr, src in H:
    r = C[(C.session == s) & (C.run == run) & (C.col == col)].iloc[0]
    y = 1 - F / FLr if tone == 'heavy' else F / FLr
    sy = sF / FLr * (1 if tone != 'sum' else (FLr - F) / FLr)
    sy = np.hypot(sy, 0.02)   # hole reference F_L carries ~2 % (sum/frame disagreement)
    pts.append(dict(session=s, run=run, col=col, kind=r.kind, side='h', n_frame=r.n_frame, F_L_ref=FLr, fl_src=src,
                    n_act=-FLr / FLN, dF=r.dF, F_L_tone=r.F_L, F_light=r.F_light, sig_light=r.sig_light, k_light=np.nan,
                    F_heavy=r.F_heavy, sig_heavy=r.sig_heavy, tone=tone, y=y, sy=sy))
P = pd.DataFrame(pts)
P['split'] = np.where((P.side == 'e') & P.session.isin(['0825', '0822']), 'train', 'test')
P.to_csv('partition_points.csv', index=False)
print(P.groupby(['split', 'side', 'session', 'tone']).agg(n=('y', 'size'), FL_min=('F_L_ref', 'min'), FL_max=('F_L_ref', 'max'),
                                                           y_med=('y', 'median'), sy_med=('sy', 'median')).round(3).to_string())
