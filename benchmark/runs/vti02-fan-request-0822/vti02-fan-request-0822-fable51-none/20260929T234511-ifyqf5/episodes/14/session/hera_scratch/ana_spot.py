"""Runs 6, 7 — SdH spot checks: raw R(B), bg-removed dR vs 1/B, FFT in 1/B, sdh_onset tone table."""
from hera.analysis import resolve_channels, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency

def _load(rid):
    r = open_run(str(Path(file_path) / str(rid)))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    B = r.col("magnet_field"); o = np.argsort(B)
    return B[o], R[o], I[o], r.col("T_sample")[o]

runs = {6: ("electron n = +3.2e12", 3.2), 7: ("hole n = -1.2e12", -1.2)}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, (lab, n12)) in enumerate(runs.items()):
    B, R, I, T = _load(rid)
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"=== run {rid} ({lab}) === {len(B)} pts, B {B.min():.2f}..{B.max():.2f} T; R {R.min():.0f}..{R.max():.0f} Ohm; "
          f"I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA; T {T.min():.3f}..{T.max():.3f} K; F_L(full n, 4-fold) = {FL:.1f} T")
    ax[0, k].plot(B, R, lw=0.8); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("Rxx (Ohm)"); ax[0, k].set_title(f"run {rid} — {lab} — raw")
    m = B >= 1.0
    dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[1, k].plot(1 / B[m], dR, lw=0.8); ax[1, k].set_xlabel("1/B (1/T)"); ax[1, k].set_ylabel("dRxx (Ohm)"); ax[1, k].set_title("bg-removed (deg-5 in B), B >= 1 T")
    f, spec = sdh_fft(R[:, None], B, b_range=(2.0, B.max()), nfft=2048, bg_degree=5, log=False)
    sp = spec[0]; sel = f > 2
    ax[2, k].plot(f, sp / sp[sel].max(), lw=1, label=f"FFT [2, {B.max():.0f}] T")
    ax[2, k].axvline(FL, color="r", ls="--", lw=1, label=f"F_L = {FL:.1f} T"); ax[2, k].axvline(FL / 2, color="orange", ls=":", lw=1, label="F_L/2")
    ax[2, k].set_xlim(0, 60); ax[2, k].set_xlabel("F (T)"); ax[2, k].set_ylabel("FFT amp (norm)"); ax[2, k].legend(fontsize=7)
    try:
        print(sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 10e-9).summary())
    except SdhOnsetError as e:
        print(f"sdh_onset: {e}")
fig.tight_layout(); plt.show()
