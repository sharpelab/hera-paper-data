"""SdH spot checks, runs 6 (electron n=+3.2e12, 0->10 T) and 7 (hole n=-1.2e12, 10->0.3 T):
raw traces, per-tone onsets, FFT tone frequencies vs the stacking-model expectations."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency

base = Path(__file__).resolve().parent.parent / "data"
FS = 50e-6 / 10e-9  # 50 uV sens / 10 nA nominal bias = 5 kOhm full scale

def load(rid):
    r = open_run(base / str(rid))
    ch = resolve_channels(r.meta)
    cur = current_channel(ch)
    vch = [c for c in ch if c.cid == "sr1"][0]
    I = np.abs(r.col_at(cur.idx) / cur.gain)
    R = (r.col_at(vch.idx) / vch.gain) / I
    B = r.col("magnet_field")
    o = np.argsort(B)
    return B[o], np.abs(R[o]), I[o], r

results = {}
fig, axs = plt.subplots(2, 2, figsize=(13, 8))
for row, (rid, label, n12) in enumerate([(6, "electron n=+3.2e12", 3.2), (7, "hole n=-1.2e12", -1.2)]):
    B, R, I, r = load(rid)
    F_full = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n=== run {rid} ({label}) === {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T; "
          f"R {R.min():.1f}-{R.max():.1f} Ohm; F_full(n) = {F_full:.1f} T")
    try:
        o = sdh_onset(R, B, r_full_scale=FS)
        print(o.summary())
        tones = [(t.freq, t.contrast, t.onset_b, t.marginal, t.harmonic_of) for t in o.tones]
        results[rid] = dict(onset_b=float(o.onset_b), onset_freq=float(o.onset_freq),
                            F_full=float(F_full),
                            tones=[dict(freq=float(t.freq), contrast=float(t.contrast),
                                        onset_b=float(t.onset_b), marginal=bool(t.marginal),
                                        harmonic_of=(float(t.harmonic_of) if t.harmonic_of else None))
                                   for t in o.tones])
    except SdhOnsetError as e:
        print(f"sdh_onset FAILED: {e}")
        results[rid] = dict(error=str(e), F_full=float(F_full))
    # FFT on the high-B window (above ~2 T where oscillations live)
    sel = B >= 1.5
    freqs, spec = sdh_fft(R[sel][:, None], B[sel], nfft=4096)
    sp = spec[0]
    axs[row, 0].plot(B, R, lw=0.6)
    axs[row, 0].set_xlabel("B (T)"); axs[row, 0].set_ylabel("|Rxx| (Ohm)")
    axs[row, 0].set_title(f"run {rid} raw — {label}")
    axs[row, 1].plot(freqs, sp, lw=0.8)
    axs[row, 1].axvline(F_full, color="r", ls="--", lw=1, label=f"F_full = {F_full:.1f} T")
    for frac, c in [(0.5, "orange")]:
        axs[row, 1].axvline(F_full * frac, color=c, ls=":", lw=1)
    axs[row, 1].set_xlim(0, 60); axs[row, 1].set_xlabel("F (T)"); axs[row, 1].set_ylabel("FFT mag")
    axs[row, 1].legend(fontsize=8); axs[row, 1].set_title(f"run {rid} SdH FFT (B >= 1.5 T)")
fig.tight_layout()
fig.savefig(Path(__file__).parent / "sdh_spots.png", dpi=110)
json.dump(results, open(Path(__file__).parent / "sdh_spots.json", "w"), indent=1)
print("\nsaved sdh_spots.png / sdh_spots.json")
