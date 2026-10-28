# SdH spot-check read — runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12)
# sdh-spot-check Verify: onset from background-subtracted data, FFT above onset,
# stability sweep over bg_degree/cutoff, tones vs F_L and the model F(n).
import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, resolve_channels, SdhOnsetError

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fs

SPOTS = {6: +3.2e16, 7: -1.2e16}  # m^-2
R_FS = 50e-6 / 10e-9              # sr1 sensitivity / I_bias = 5 kOhm

results = {}
fig, axes = plt.subplots(2, 3, figsize=(15, 8))

for row, (rid, nspot) in enumerate(SPOTS.items()):
    run = open_run(f"data/{rid}")
    ch = resolve_channels(run.meta)
    B = run.col("magnet_field")
    # R from measured drain current (signed)
    Icur = None; V = None
    for c in ch.channels if hasattr(ch, "channels") else []:
        pass
    # generic: find sr0 (current) and sr1 (voltage) columns + gains from measurement_config
    mc = run.meta["measurement_config"]
    g_cur = float(mc["sr0_gain"]); g_v = float(mc.get("sr1_gain", 1))
    I = run.col("sr0_X") / g_cur
    Rraw = (run.col("sr1_X") / g_v) / I
    order = np.argsort(B)
    B, R = B[order], Rraw[order]

    FL = float(luttinger_frequency(nspot))
    on = sdh_onset(R, B, r_full_scale=R_FS)
    print(f"===== run {rid}  n = {nspot/1e16:+.2f}e12 cm^-2   F_L = {FL:.1f} T =====")
    print(on.summary())

    cutoff = max(on.onset_b, 1.2 * on.onset_b)
    bmax = on.clip_high_b if on.clip_high_b else B.max()
    dF = 1.0 / (1.0 / on.onset_b - 1.0 / bmax)
    print(f"onset_b={on.onset_b:.3f} T  b_max={bmax:.2f} T  deltaF={dF:.2f} T")

    f, spec = sdh_fft(R[:, None], B, b_range=(cutoff, bmax), bg_degree=5, log=False)
    sp = spec[0]

    # stability sweep: bg_degree x low-cutoff
    print("stability (bg_degree, cutoff) -> top-3 peak freqs [T]:")
    for bg in (4, 5, 6):
        for co in (cutoff, 1.3 * cutoff, 1.6 * cutoff):
            ff, ss = sdh_fft(R[:, None], B, b_range=(co, bmax), bg_degree=bg, log=False)
            s0 = ss[0]
            # peaks: local maxima above 10% of max, f>2T
            m = (ff > 2)
            idx = [i for i in np.argsort(s0)[::-1] if m[i]][:12]
            picks = []
            for i in sorted(idx, key=lambda i: -s0[i]):
                if all(abs(ff[i] - p) > 1.5 for p in picks):
                    picks.append(float(ff[i]))
                if len(picks) == 3:
                    break
            print(f"  bg={bg} cut={co:.2f}: " + ", ".join(f"{p:.1f}" for p in picks))

    # model tones at this density
    try:
        _, abab = fs.abab_fs(nspot)
        abab_F = [F for F, kF in abab]
    except Exception as e:
        abab_F = []; print("abab model:", e)
    try:
        _, topo, ncomp, nfreq, Ftot = fs.abca_fs(nspot)
        abca_F = [Ftot]
        print(f"abca: topo={topo} ncomp={ncomp} nfreq={nfreq} F_total={Ftot:.1f}")
    except Exception as e:
        abca_F = []; print("abca model:", e)
    print(f"model ABAB tones: {['%.1f' % x for x in abab_F]}  ABCA: {['%.1f' % x for x in abca_F]}")

    results[rid] = dict(n=nspot, FL=FL, onset=float(on.onset_b), bmax=float(bmax),
                        dF=float(dF), abab=abab_F, abca=abca_F,
                        tones=[dict(f=float(t.freq), onset=float(t.onset_b),
                                    censored=bool(t.censored), marginal=bool(t.marginal),
                                    harmonic_of=t.harmonic_of)
                               for t in on.tones])

    ax = axes[row]
    ax[0].plot(B, R, lw=0.5); ax[0].set_xlabel("B [T]"); ax[0].set_ylabel("Rxx [Ohm]")
    ax[0].set_title(f"run {rid} raw  n={nspot/1e16:+.1f}e12")
    # background-subtracted vs 1/B above onset
    sel = (B >= on.onset_b) & (B <= bmax)
    pf = np.polyfit(B[sel], R[sel], 5)
    dR = R[sel] - np.polyval(pf, B[sel])
    ax[1].plot(1 / B[sel], dR, lw=0.6)
    ax[1].set_xlabel("1/B [1/T]"); ax[1].set_ylabel("dRxx [Ohm]")
    ax[1].set_title(f"detrended, B>{on.onset_b:.2f} T")
    ax[2].plot(f, sp, lw=0.8)
    ax[2].axvline(FL, color="k", ls="--", label=f"F_L={FL:.1f}")
    for x in abab_F:
        ax[2].axvline(x, color="tab:red", ls=":", alpha=0.8)
    for x in abca_F:
        ax[2].axvline(x, color="tab:green", ls="-.", alpha=0.8)
    ax[2].set_xlim(0, 1.6 * FL); ax[2].set_xlabel("F [T]"); ax[2].set_ylabel("|FFT|")
    ax[2].set_title("FFT in 1/B (red: ABAB, green: ABCA)"); ax[2].legend()

fig.tight_layout()
fig.savefig("hera_scratch/spots_67.png", dpi=110)
json.dump(results, open("hera_scratch/spots_67.json", "w"), indent=1)
print("saved hera_scratch/spots_67.png, spots_67.json")
