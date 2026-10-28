"""Runs 6-7 SdH content: per-tone onsets (sdh_onset) + FFT in 1/B (sdh_fft), against the
step-2 model anchors: e-side total F = 33.1 T (ABAB pair ~7.5/25.6, ABCA single 33.1);
h-side total 12.4 T (ABAB pair ~5.3/7.1, ABCA LK-dead)."""
from hera.analysis import sdh_onset, SdhOnsetError

MODEL = {6: [("F_tot 33.1", 33.1, "r"), ("ABAB 7.5", 7.5, "g"), ("ABAB 25.6", 25.6, "g")],
         7: [("F_tot 12.4", 12.4, "r"), ("ABAB 5.3", 5.3, "g"), ("ABAB 7.1", 7.1, "g")]}
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
for a, rid in zip(ax, (6, 7)):
    B, R, I, r = load_spot(rid)
    try:
        o = sdh_onset(R, B, r_full_scale=50e-6 / I.mean())
        print(f"=== run {rid} ===\n{o.summary()}\n")
    except SdhOnsetError as e:
        print(f"=== run {rid} === sdh_onset FAILED: {e}\n")
    for blo, ls in [(1.5, "-"), (3.0, "--")]:
        sel = B >= blo
        f, s = sdh_fft(R[sel][:, None], B[sel])
        a.plot(f, s[0] / s[0].max(), ls, lw=0.8, label=f"B {blo:.1f}-10 T")
    for lab, F, c in MODEL[rid]:
        a.axvline(F, color=c, ls=":", lw=0.8)
        a.text(F, 1.02, lab, rotation=90, fontsize=6, ha="center", va="bottom", color=c)
    a.set_xlim(0, 60); a.set_xlabel("F (T)"); a.set_ylabel("FFT mag (norm)")
    a.set_title(f"run {rid} SdH FFT in 1/B"); a.legend(fontsize=7)
fig.tight_layout()
