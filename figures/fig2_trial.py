"""Fig. 2: HERA's session on device 1 (vti-01, the trilayer), lock-in sr1 (B_SD-L4, three-terminal).

(a) the session timeline in active hours, with the operator waits cut out at the two breaks; (b) run 20, the
hole-side spot check at n = -1.74e12 from the operator-requested extension, as background-subtracted R_3T against 1/B
(runs 8 and 9, the first spot checks, carry an instrumental ~83 mT-periodic line in B); (c) run 19, the operator-requested
Landau fan (0.9-5 T uniform in 1/B, 131 x 53, tau 300 ms); (d) its per-column SdH FFT with the trilayer model tones.
Densities are in HERA's own calibration frame (geometry-anchored top-gate capacitance). The model tones come from
the corpus's trilayer Fermi-surface counter; the ABC singleton coincides with F_L by Luttinger's theorem.

Run from the repo root: uv run --project measurement-env python figures/fig2_trial.py [outdir]
Adapted from Zack's figures/fig2_panels.py (paper repo) and the TikZ timeline fig-main-timeline-dev1.tex.
"""
import sys

import numpy as np
import matplotlib.pyplot as plt

import style

sys.path.insert(0, str(style.ROOT / "measurement-env/src"))
sys.path.insert(0, str(style.ROOT / "measurement-env/hera/models/trilayer_fs_count"))
from hera.analysis import open_run, luttinger_frequency  # noqa: E402
from fs_count_b0 import aba_fs  # noqa: E402

style.use()
SESS = style.ROOT / "sessions/vti-01/2026-08-18-vti-01-session"
C_FL, C_MOD = "white", "#33d6ff"     # model lines: visible on both ends of magma
N_SPOT = -1.74                               # density of the panel (b) spot check, 1e12 cm^-2
NF = 53
NS = np.linspace(-0.70, -1.74, NF)          # the fan's gate rows, 1e12 cm^-2
NOTE = plt.rcParams["legend.fontsize"]
X0 = 0.19                                    # every panel shifted right by half the spare width, so the ink is centred
LETTER_X = X0 + 0.04                         # in from the left: the timeline column's letters (as Fig. 5a)

# (a) timeline: active hours of each run start, from the transcript and data/<run>/metadata.json (rig clock PDT);
# active time = hours after the brief - 0.08 (grant) - 11.38 (standby) for runs after the first wait
GAP = 3.4        # axis units left open at each break for its glyph and label
CUT, G3 = 4.0, 1.0   # the third break, inside the operator's fan, only shortens the axis: 4 h cut, 1 unit for its glyph
OFF = [0, GAP, 2 * GAP, 2 * GAP + G3 - CUT]   # drawn x offset of each axis segment
EVENTS = [       # (active h, axis segment, label)
    (0.05, 0, "gate checks"),
    (0.86, 1, "Si gate, gate map"),
    (1.30, 1, None),
    (4.15, 1, "spot check, holes"),
    (6.05, 1, "spot check, electrons"),
    (8.11, 1, "Landau fan"),
    (11.30, 1, "Temperature dep."),
    (16.2, 1, "Return conclusion"),
    (16.1, 2, "Operator's fan (c)"),   # 22.45 h active = 16.1 h + the 6.4 h wait
    (21.9, 3, "spot check (b)"),       # run 20, 5.79 h after run 19 starts
]


def r3t(g):
    """Three-terminal resistance in kOhm; the drain current is sr0 through its 1 MOhm sense."""
    return g.col("sr1_X") / (np.abs(g.col("sr0_X")) / 1e6) / 1e3


def fft_padded(R, B, b_range, bg_degree=5, pad=16):
    """Per-column SdH FFT in 1/B as hera.analysis.sdh_fft does it (log10, B-space polynomial background,
    Hann), zero-padded so the spectrum is drawn between its natural bins. R is (n_B, n_cols)."""
    sel = (B >= b_range[0]) & (B <= b_range[1])
    Bs = B[sel]; u = 1.0 / Bs; order = np.argsort(u); us = u[order]
    m = us.size; ug = np.linspace(us[0], us[-1], m); du = ug[1] - ug[0]
    win = np.hanning(m); nout = pad * m
    freqs = np.fft.rfftfreq(nout, du)
    spec = np.zeros((R.shape[1], freqs.size))
    for j in range(R.shape[1]):
        y = np.log10(np.maximum(R[sel, j] * 1e3, 1.0))
        y = y - np.polyval(np.polyfit(Bs, y, bg_degree), Bs)
        spec[j] = np.abs(np.fft.rfft(np.interp(ug, us, y[order]) * win, n=nout))
    return freqs, spec


def timeline(ax):
    style.timeline(
        ax, end=21.9 + OFF[3] + 2.6, breaks=[0.85, 16.2 + GAP + 0.9, 17.3 + 2 * GAP + G3 / 2],
        ticks=[(0, "0")] + [(t + GAP, str(t)) for t in (4, 8, 12, 16)] + [(22 + OFF[3], "22")],
        events=[(t + OFF[g], lab) for t, g, lab in EVENTS],
        waits=[(1.9, "11.4 h wait for ruling"), (16.2 + GAP + 1.6, "6.4 h wait for request")],
        xlabel="active hours into the session", fs=5)   # Nature's 5 pt floor; 6 pt crowded the labels


def main(out):
    W, H = style.TEXT_W, 2.85
    fig = plt.figure(figsize=(W, H))
    # the old layout: a 0.295 textwidth column (a over b), then two 0.345 textwidth columns (c, d)
    fy, fh = 0.43, 1.92                                  # fan axes bottom and height, in
    BH = 0.60                                            # (b) axes height, in
    cx, dx, fw = X0 + 2.515, X0 + 4.86, 1.72                        # fan axes left edges and width, in

    # ---- (c) run 19, the operator-requested fan, raw
    g = open_run(SESS / "data/19")
    gr = lambda c: c[: len(c) // NF * NF].reshape(-1, NF)
    B = gr(g.col("magnet_field"))[:, 0]
    R = gr(r3t(g))
    dn = NS[1] - NS[0]
    ne = np.r_[NS - dn / 2, NS[-1] + dn / 2]
    be = np.r_[B[0] - (B[1] - B[0]) / 2, (B[1:] + B[:-1]) / 2, B[-1] + (B[-1] - B[-2]) / 2]
    xt = [-1.6, -1.2, -0.8]
    c = style.axes_in(fig, cx, fy, fw, fh)
    im = c.pcolormesh(ne, be, R, shading="flat", cmap="viridis", vmin=np.percentile(R, 2), vmax=np.percentile(R, 98),
                      rasterized=True)
    c.grid(False)
    c.set_xlim(NS.min(), NS.max()); c.set_xticks(xt)
    c.set_xlabel("$n$ ($10^{12}$ cm$^{-2}$)"); c.set_ylabel("$B$ (T)"); c.set_yticks([1, 2, 3, 4, 5])
    lo, hi = np.percentile(R, 2), np.percentile(R, 98)
    style.topbar(fig, c, im, "$R_{3T}$ (k$\\Omega$)", [round(lo, 1), round(hi, 1)])

    # ---- (d) its per-column FFT with the model tones
    f, spec = fft_padded(R, B, (0.9, 5.0))
    Sn = spec / spec[:, f > 1.5].max(axis=1, keepdims=True)
    df = f[1] - f[0]
    FL = luttinger_frequency(NS * 1e16)
    pair = np.array([sorted(F for F, _ in aba_fs(n)[1]) for n in NS * 1e16])
    d = style.axes_in(fig, dx, fy, fw, fh)
    im = d.pcolormesh(ne, np.r_[f - df / 2, f[-1] + df / 2], Sn.T, shading="flat", cmap="magma", vmin=0, vmax=1,
                      rasterized=True)
    d.grid(False)
    d.plot(NS, FL, color=C_FL, ls="--", lw=0.9, label="ABC stacking")
    d.plot(NS, pair[:, -1], color=C_MOD, ls="-.", lw=0.9, label="ABA stacking")
    d.plot(NS, pair[:, 0], color=C_MOD, ls="-.", lw=0.9)
    d.set_ylim(0, 30); d.set_xlim(NS.min(), NS.max()); d.set_xticks(xt)
    d.set_xlabel("$n$ ($10^{12}$ cm$^{-2}$)"); d.set_ylabel("$F$ (T)")
    d.legend(loc="upper left", labelcolor="white", handlelength=2.2)
    style.topbar(fig, d, im, "$|\\mathrm{FFT}|$ (norm.)", [0, 0.5, 1])

    # ---- (b) run 20, the hole-side spot check, oscillations against 1/B
    g8 = open_run(SESS / "data/20")                  # at n = N_SPOT
    B8, R8 = g8.col("magnet_field"), r3t(g8)
    sel = (B8 >= 0.9) & (B8 <= 5.0)
    Bs, Rs = B8[sel], R8[sel]
    dR = Rs - np.polyval(np.polyfit(Bs, Rs, 5), Bs)
    b = style.axes_in(fig, X0 + 0.42, fy, 1.62, BH)
    b.plot(1 / Bs, dR, color="k", lw=0.5)
    b.set_xlim(1 / 5.0, 1 / 0.9)
    b.set_xlabel("$1/B$ (T$^{-1}$)"); b.set_ylabel("$\\Delta R_{3T}$ (k$\\Omega$)")
    sec = b.secondary_xaxis("top", functions=(lambda u: 1 / np.maximum(u, 1e-3), lambda x: 1 / np.maximum(x, 1e-3)))
    sec.set_xticks([5, 2, 1]); sec.set_xlabel("$B$ (T)", labelpad=1)

    # ---- (a) timeline
    a = style.axes_in(fig, X0 + 0.12, 1.32, 1.95, 0.45)
    timeline(a)

    top = fy + fh + 0.22                                       # one row for a, c, d, above the timeline labels
    style.snug_below(fig, a, top)
    style.panel_label(fig, b, "a", y=top, x=LETTER_X)
    style.panel_label(fig, b, "b", y=fy + BH + 0.36, x=LETTER_X)
    style.panel_label(fig, c, "c", y=top)
    style.panel_label(fig, d, "d", y=top)
    style.save(fig, out)
    plt.close(fig)
    print(f"run 20 window 0.9-5 T: {sel.sum()} pts; run 19: {R.shape}")


if __name__ == "__main__":
    out = style.outdir(sys.argv)
    main(out / "fig2-trial.pdf")
    print("wrote", out / "fig2-trial.pdf")
