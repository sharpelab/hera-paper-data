"""SdH spot-check analysis, runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).
Per-run: raw R(B), sdh_onset tone table, FFT in 1/B above onset; compare tone
frequencies against the full-density Onsager frequency and stacking models."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, luttinger_frequency, SdhOnsetError)
from scipy.signal import find_peaks

base = Path("/home/hera/measurements/zack/20260822-vti-02/data")
FS = 50e-6 / 10e-9  # 5 kOhm full scale

fig, axs = plt.subplots(2, 3, figsize=(15, 8))
for row, (rid, n12) in enumerate(((6, +3.2), (7, -1.2))):
    r = open_run(base / str(rid))
    chs = resolve_channels(r.meta)
    cur = current_channel(chs)
    I = r.col(cur.col) / cur.gain
    vch = [c for c in chs if not c.is_current and abs(r.col(c.col)).max() > 0][0]
    R = (r.col(vch.col) / vch.gain) / I
    B = r.col("magnet_field")
    o = np.argsort(B)
    B, R = B[o], np.abs(R[o])
    F_full = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n===== run {rid}: n = {n12:+.1f}e12, F_full(4-fold) = {F_full:.1f} T =====")
    print(f"rows {len(B)}, B {B.min():.2f}-{B.max():.2f} T, R {R.min():.0f}-{R.max():.0f} Ohm")
    try:
        so = sdh_onset(R, B, r_full_scale=FS)
        print(so.summary())
        onset = so.onset_b
        tones = [(t.freq, t.contrast, t.onset_b, t.marginal, t.harmonic_of) for t in so.tones]
    except SdhOnsetError as e:
        print(f"sdh_onset FAILED: {e}")
        onset, tones = 1.5, []
    # FFT above max(onset, 1.0) — n12=-1.2 low field ok
    b_lo = max(onset, 1.0)
    freqs, spec = sdh_fft(R[:, None], B, b_range=(b_lo, B.max()), nfft=4096, log=False)
    sp = spec[0]
    sel = freqs > 2
    pk, _ = find_peaks(sp[sel], prominence=0.05 * sp[sel].max())
    pkf = [(freqs[sel][p], sp[sel][p]) for p in sorted(pk, key=lambda p: -sp[sel][p])[:6]]
    print(f"FFT window B = [{b_lo:.2f}, {B.max():.2f}] T; peaks (T, amp): "
          + ", ".join(f"{f:.1f} ({a:.2g})" for f, a in pkf))
    if len(tones) >= 2:
        fs = [t[0] for t in tones if t[4] is None and not t[3]]
        print(f"non-harmonic robust tone sum = {sum(fs):.1f} T vs F_full {F_full:.1f} T; tones: "
              + ", ".join(f"{f:.1f}" for f in fs))
    axs[row, 0].plot(B, R, lw=0.5)
    axs[row, 0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid}  n={n12:+.1f}e12  raw")
    m = B >= b_lo
    cf = np.polyfit(B[m], R[m], 5)
    axs[row, 1].plot(1 / B[m], R[m] - np.polyval(cf, B[m]), lw=0.5)
    axs[row, 1].set(xlabel="1/B (1/T)", ylabel="dRxx (Ohm)", title="bg-subtracted vs 1/B")
    axs[row, 2].plot(freqs, sp, lw=0.8)
    axs[row, 2].axvline(F_full, color="r", ls="--", label=f"F_full {F_full:.1f} T")
    for f, a in pkf[:4]:
        axs[row, 2].annotate(f"{f:.1f}", (f, a))
    axs[row, 2].set(xlabel="F (T)", xlim=(0, 60), title="FFT in 1/B")
    axs[row, 2].legend(fontsize=7)
fig.tight_layout()
fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_sdh.png", dpi=110)
print("\nsaved spot_sdh.png")
