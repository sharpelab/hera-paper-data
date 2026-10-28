"""Runs 6 & 7 — sdh-spot-check pair at D = 0 (run-5 calibration): raw traces, then
per-tone onsets (sdh_onset) and the SdH FFT vs the full-density Onsager frequency."""
from hera.analysis import resolve_channels, current_channel, sdh_onset, SdhOnsetError

FS_R = 50e-6 / 10e-9   # sr1 sens / nominal bias = 5 kOhm full scale (both runs)

def sdh_trace(rid):
    r = run(rid)
    ch = resolve_channels(r.meta); cur = current_channel(ch)
    v = [c for c in ch if c.cid == "sr1"][0]
    I = np.abs(r.col_at(cur.idx) / cur.gain)
    R = np.abs((r.col_at(v.idx) / v.gain) / I)
    B = r.col("magnet_field"); o = np.argsort(B)
    return B[o], R[o], r

fig, axs = plt.subplots(2, 2, figsize=(13, 8))
for row, (rid, label, n12) in enumerate([(6, "electron, n = +3.2e12, D = 0", 3.2),
                                         (7, "hole, n = -1.2e12, D = 0", -1.2)]):
    B, R, r = sdh_trace(rid)
    F_full = luttinger_frequency(abs(n12) * 1e16)
    print(f"=== run {rid} ({label}) === {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T; "
          f"R {R.min():.1f}-{R.max():.1f} Ohm; F_full(|n|) = {F_full:.1f} T")
    try:
        o = sdh_onset(R, B, r_full_scale=FS_R)
        print(o.summary())
    except SdhOnsetError as e:
        print(f"sdh_onset failed: {e}")
    sel = B >= 1.5
    freqs, spec = sdh_fft(R[sel][:, None], B[sel], nfft=4096)
    axs[row, 0].plot(B, R, lw=0.6)
    axs[row, 0].set_xlabel("B (T)"); axs[row, 0].set_ylabel("|Rxx| (Ohm)")
    axs[row, 0].set_title(f"run {rid} raw — {label}")
    axs[row, 1].plot(freqs, spec[0], lw=0.8)
    axs[row, 1].axvline(F_full, color="r", ls="--", lw=1, label=f"F_full = {F_full:.1f} T")
    axs[row, 1].set_xlim(0, 60); axs[row, 1].set_xlabel("F (T)"); axs[row, 1].set_ylabel("FFT mag")
    axs[row, 1].legend(fontsize=8); axs[row, 1].set_title(f"run {rid} SdH FFT (B >= 1.5 T; dF ~ 1.8 T)")
    print()
fig.tight_layout(); plt.show()
