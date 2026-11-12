"""Joint matched-filter onset walk: the _track_tone walk (Gaussian window of 3 periods of the tone of interest, 5-sigma,
gap rule 0.5 widths) but at each window the amplitude comes from a weighted least-squares fit of ALL listed tones
(cos + sin each) plus a linear background, so a strong neighbour (the heavy tone beside F_L) cannot leak into the
tone of interest.  SNR = amplitude / its standard error under white noise sigma (hera _noise_sigma)."""
import numpy as np

W_STEP = 0.25; GAP = 0.5; THR = 5.0; NPER = 3.0; MINPER = 2.0; MINPTS = 8


def walk(u, y, f0, others, sigma):
    span = u[-1] - u[0]
    n_eff = min(NPER, span * f0 * 2.355 / 5.0)
    if n_eff < MINPER:
        return None, f'record {span:.2f}/T < {5.0 * MINPER / 2.355 / f0:.2f}/T needed for {MINPER:g} periods at {f0:.2f} T'
    su = n_eff / f0 / 2.355; w = 5 * su; step = w * W_STEP
    freqs = [f0] + [f for f in others if abs(f - f0) > 1e-6]
    centers = np.arange(u[-1] - w / 2, u[0] + w / 2 - 1e-12, -step)[::-1]
    Bc, snr, amp = [], [], []
    for c in centers:
        m = np.abs(u - c) <= 2.5 * su
        if m.sum() < max(MINPTS, 2 * len(freqs) + 3):
            continue
        uu, yy = u[m], y[m]
        g = np.exp(-0.5 * ((uu - c) / su) ** 2)
        cols = [np.ones_like(uu), uu - c]
        for f in freqs:
            cols += [np.cos(2 * np.pi * f * uu), np.sin(2 * np.pi * f * uu)]
        X = np.array(cols).T
        XtG = X.T * g
        M = XtG @ X
        try:
            Mi = np.linalg.inv(M)
        except np.linalg.LinAlgError:
            continue
        beta = Mi @ (XtG @ yy)
        cov = sigma ** 2 * Mi @ (XtG * g) @ X @ Mi
        a, b = beta[2], beta[3]
        A = np.hypot(a, b)
        # standard error of the amplitude along its own direction
        v = np.array([a, b]) / max(A, 1e-300)
        se = float(np.sqrt(max(v @ cov[2:4, 2:4] @ v, 1e-300)))
        Bc.append(1 / c); snr.append(A / se); amp.append(A)
    if not Bc:
        return None, 'no window holds enough points'
    Bc, snr, amp = map(np.array, (Bc, snr, amp))
    good = snr >= THR
    if not good.any():
        return None, f'never above threshold (max SNR {snr.max():.1f})'
    max_gap = int(np.ceil(GAP / W_STEP)); idx, gap, started = 0, 0, False
    for i in range(Bc.size):
        if good[i]:
            idx, gap, started = i, 0, True
        elif started:
            gap += 1
            if gap > max_gap:
                break
    return dict(onset_B=float(Bc[idx]), censored=bool(idx == Bc.size - 1), lowest_window_B=float(Bc[-1]), max_snr=float(snr.max()),
                snr_at_1T=float(np.interp(1.0, Bc[::-1], snr[::-1])) if Bc.min() <= 1.0 <= Bc.max() else np.nan, B=Bc, snr=snr, amp=amp), None
