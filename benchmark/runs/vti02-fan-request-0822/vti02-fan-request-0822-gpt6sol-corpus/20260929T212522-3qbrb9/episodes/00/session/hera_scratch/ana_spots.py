"""Raw then SdH spot-check read, runs 6 and 7 (session data only)."""
from pathlib import Path
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, resolve_channels
from scipy.signal import find_peaks

_candidates = [Path.cwd(), *Path.cwd().parents]
_data_dir = next((p / "data" for p in _candidates if (p / "data" / "6" / "metadata.json").is_file()), None)
if _data_dir is None:
    raise FileNotFoundError("session data/6 absent below ana kernel cwd")

for rid, n_nom in ((6, 3.2), (7, -1.2)):
    r = open_run(_data_dir / str(rid))
    print(summarize_run(r))
    ch = {x.cid: x for x in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I_bias = (r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"] /
              r.meta["measurement_config"]["bias_resistor"])
    R = r.col("sr1_X") / ch["sr1"].gain / I_bias
    I_drain = r.col("sr0_X") / ch["sr0"].gain
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    print(f"run {rid}: I_bias={I_bias*1e9:.2f} nA; Rxx {R.min():.1f}..{R.max():.1f} Ohm; "
          f"drain {I_drain.min()*1e9:.2f}..{I_drain.max()*1e9:.2f} nA; "
          f"T {T.min():.3f}..{T.max():.3f} K; "
          f"I_tg {itg.min()*1e12:.0f}..{itg.max()*1e12:.0f} pA; "
          f"I_bg {ibg.min()*1e12:.0f}..{ibg.max()*1e12:.0f} pA")
    fig, ax = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
    ax[0].plot(B, R, lw=.8); ax[0].set_ylabel("raw Rxx (Ohm)")
    ax[1].plot(B, itg*1e12, lw=.6, label="TG")
    ax[1].plot(B, ibg*1e12, lw=.6, label="BG")
    ax[1].set(xlabel="B (T)", ylabel="gate current (pA)"); ax[1].legend()
    fig.suptitle(f"run {rid}: raw B_1–B_2 and gate currents, n={n_nom:+.1f}e12, D=0")
    fig.tight_layout(); plt.show()

    on = sdh_onset(R, B, r_full_scale=50e-6/I_bias)
    print(on.summary())
    print("The lowest-frequency tracks may include detrending residuals; test by B-window stability.")
    fig, ax = plt.subplots(figsize=(8, 3.5))
    for cutoff in ((1.5, 2.0, 2.5) if rid == 6 else (1.0, 2.0, 3.0)):
        f, spec = sdh_fft(R[:, None], B, b_range=(cutoff, 10.0), nfft=2048, log=False)
        y = spec[0]
        pk, _ = find_peaks(y, prominence=.02*y.max(), distance=8)
        pk = sorted(pk, key=lambda p: y[p], reverse=True)[:5]
        print(f"run {rid} FFT B={cutoff:g}..10 T: " +
              ", ".join(f"{f[p]:.1f} T" for p in pk))
        ax.plot(f, y, label=f"B>{cutoff:g} T")
    ax.set(xlim=(0, 75), xlabel="frequency (T)", ylabel="FFT amplitude",
           title=f"run {rid}: B-window stability, B-space detrend first")
    ax.legend(); fig.tight_layout(); plt.show()
