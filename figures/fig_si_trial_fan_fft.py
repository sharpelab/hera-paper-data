"""SI Fig. trial_fans panel (c): the fan HERA concluded from (vti-01 run 10, 1.6-5 T uniform in 1/B, 71 x 53)
and its per-column SdH FFT with the trilayer model tones, drawn as Fig. 2 (c, d) are. The light ABA tone (~2 T)
lies below the record's frequency resolution (2.4 T), so the spectrum carries one ridge.
Writes fig-si-trial-fan-fft.pdf. Run: uv run --project measurement-env python figures/fig_si_trial_fan_fft.py [outdir]"""
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
import style  # noqa: E402
ROOT = style.ROOT
sys.path.insert(0, str(ROOT / "measurement-env/src"))
sys.path.insert(0, str(ROOT / "measurement-env/hera/models/trilayer_fs_count"))
from hera.analysis import open_run, luttinger_frequency  # noqa: E402
from fs_count_b0 import aba_fs  # noqa: E402
from fig2_trial import fft_padded, r3t, NF, NS  # noqa: E402

style.use()
SESS = ROOT / "sessions/vti-01/2026-08-18-vti-01-session"
out = style.outdir(sys.argv)

g = open_run(SESS / "data/10")
gr = lambda c: c[: len(c) // NF * NF].reshape(-1, NF)
B = gr(g.col("magnet_field"))[:, 0]
R = gr(r3t(g))
dn = NS[1] - NS[0]
ne = np.r_[NS - dn / 2, NS[-1] + dn / 2]
be = np.r_[B[0] - (B[1] - B[0]) / 2, (B[1:] + B[:-1]) / 2, B[-1] + (B[-1] - B[-2]) / 2]
xt = [-1.6, -1.2, -0.8]

f, spec = fft_padded(R, B, (1.6, 5.0))
Sn = spec / spec[:, f > 1.5].max(axis=1, keepdims=True)
df = f[1] - f[0]
FL = luttinger_frequency(NS * 1e16)
pair = np.array([sorted(F for F, _ in aba_fs(n)[1]) for n in NS * 1e16])

W, H = 4.3, 2.75
fw, fh, fy = 1.55, 1.85, 0.48
fig = plt.figure(figsize=(W, H))
c = style.axes_in(fig, 0.42, fy, fw, fh)
im = c.pcolormesh(ne, be, R, shading="flat", cmap="viridis", vmin=np.percentile(R, 2), vmax=np.percentile(R, 98), rasterized=True)
c.grid(False); c.set_xlim(NS.min(), NS.max()); c.set_xticks(xt)
c.set_xlabel("$n$ ($10^{12}$ cm$^{-2}$)"); c.set_ylabel("$B$ (T)"); c.set_yticks([2, 3, 4, 5])
lo, hi = np.percentile(R, 2), np.percentile(R, 98)
style.topbar(fig, c, im, "$R_{3T}$ (k$\\Omega$)", [round(lo, 1), round(hi, 1)])

d = style.axes_in(fig, 0.42 + fw + 0.42, fy, fw, fh)
im = d.pcolormesh(ne, np.r_[f - df / 2, f[-1] + df / 2], Sn.T, shading="flat", cmap="magma", vmin=0, vmax=1, rasterized=True)
d.grid(False)
d.plot(NS, FL, color="w", ls="--", lw=0.9, label="ABC stacking")
d.plot(NS, pair[:, -1], color="c", ls="-.", lw=0.9, label="ABA stacking")
d.plot(NS, pair[:, 0], color="c", ls="-.", lw=0.9)
d.set_ylim(0, 30); d.set_xlim(NS.min(), NS.max()); d.set_xticks(xt)
d.set_xlabel("$n$ ($10^{12}$ cm$^{-2}$)"); d.set_ylabel("$F$ (T)")
d.legend(loc="upper left", labelcolor="white", handlelength=2.2)
style.topbar(fig, d, im, "$|\\mathrm{FFT}|$ (norm.)", [0, 0.5, 1])
style.save(fig, out / "fig-si-trial-fan-fft.pdf")
