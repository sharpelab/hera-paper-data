import os, numpy as np, hera.analysis as a
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

MDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(MDIR, "hera_scratch")
run = a.open_run(os.path.join(MDIR, "data", "2"))
B = run.col("magnet_field"); I = run.col("sr0_X")/(-1e6)
R1 = run.col("sr1_X")/I; R2 = run.col("sr2_X")/I; Rxy = run.col("sr3_X")/I
o = np.argsort(B)                      # sort ascending in B
B, R1, R2, Rxy, I = B[o], R1[o], R2[o], Rxy[o], I[o]
print(f"N={len(B)}  B[{B.min():.3f},{B.max():.3f}]  I med={np.median(I)*1e9:.2f} nA")
print(f"no-clip check: sr1 max |X|={np.abs(run.col('sr1_X')).max()*1e6:.1f}uV vs 100uV FS; Rxx max={np.max(np.abs(R1)):.0f} ohm")

# --- Hall-slope density (low-field, below SdH) lever-arm cross-check ---
lf = (B > 0.25) & (B < 1.2)
sl = np.polyfit(B[lf], Rxy[lf], 1)[0]      # dRxy/dB
n_hall = 1.0/(1.602176634e-19 * abs(sl))   # |n| = 1/(e dRxy/dB)
print(f"\nHall slope dRxy/dB={sl:.1f} ohm/T (B 0.25-1.2T) -> n_Hall={n_hall:.3e} m^-2 = {n_hall/1e4/1e12:.2f}e12 cm^-2")
print(f"  (gate-derived target n=3.00e12 cm^-2; ratio n_Hall/n_gate={n_hall/3.0e16:.3f})")

# --- F_L band ---
FL_gate = float(a.luttinger_frequency(3.0e16))
FL_hall = float(a.luttinger_frequency(n_hall))
print(f"F_L(gate n)={FL_gate:.2f} T   F_L(Hall n)={FL_hall:.2f} T")

# --- onset ---
onset = a.sdh_onset(R1, B)
print(f"sdh_onset: onset_b={getattr(onset,'onset_b',None)} consensus_freq={getattr(onset,'consensus_freq',None):.2f} clip_high_b={getattr(onset,'clip_high_b',None)}")

# --- FFT stability scan: cutoffs x bg_degree ---
def fftpk(R, lo, hi, deg):
    f, mag = a.sdh_fft(R.reshape(-1,1), B, b_range=(lo,hi), bg_degree=deg)
    m = mag[0]; sel = f > 4
    fs, ms = f[sel], m[sel]
    pk,_ = find_peaks(ms, prominence=ms.max()*0.08)
    pk = pk[np.argsort(ms[pk])[::-1][:6]]
    return f, m, sorted([(round(float(fs[i]),1), round(float(ms[i]/ms.max()),2)) for i in pk])
print("\n--- sr1 Rxx FFT peak stability (f[T], rel-mag) ---")
for lo in (0.4, 0.6, 0.8, 1.0):
    for deg in (4, 5, 6):
        _,_,pks = fftpk(R1, lo, 7.9, deg)
        print(f"  cut={lo} deg={deg}: {pks}")
print("--- sr2 Rxx ---")
for lo in (0.6, 0.8):
    _,_,pks = fftpk(R2, lo, 7.9, 5); print(f"  cut={lo} deg5: {pks}")
print("--- sr3 Rxy ---")
for lo in (0.6, 0.8):
    _,_,pks = fftpk(Rxy, lo, 7.9, 5); print(f"  cut={lo} deg5: {pks}")

# --- representative spectra for plot ---
f1, m1, _ = fftpk(R1, 0.6, 7.9, 5)
f2, m2, _ = fftpk(R2, 0.6, 7.9, 5)
fxy, mxy, _ = fftpk(Rxy, 0.6, 7.9, 5)

# --- plots ---
fig, ax = plt.subplots(2, 2, figsize=(14, 9))
ax[0,0].plot(B, R1, label="sr1"); ax[0,0].plot(B, R2, label="sr2")
ax[0,0].set_xlabel("B [T]"); ax[0,0].set_ylabel("Rxx [Ω]"); ax[0,0].set_title("Raw Rxx(B) (no clip)"); ax[0,0].legend()
# ΔRxx vs 1/B
m = B > 0.6; bb=B[m]; rr=R1[m]; bg=np.polyval(np.polyfit(bb,rr,5),bb)
ax[0,1].plot(1/bb, rr-bg); ax[0,1].set_xlabel("1/B [1/T]"); ax[0,1].set_ylabel("ΔRxx sr1 [Ω]"); ax[0,1].set_title("sr1 SdH vs 1/B (B>0.6T)")
for axx, ff, mm, lab in [(ax[1,0], f1, m1, "sr1"), (ax[1,0], f2, m2, "sr2"), (ax[1,1], fxy, mxy, "sr3 Rxy")]:
    axx.plot(ff, mm/mm[ff>4].max(), label=lab)
for axx in (ax[1,0], ax[1,1]):
    axx.axvline(FL_gate, c='k', ls='--', label=f"F_L gate {FL_gate:.0f}T")
    axx.axvline(FL_hall, c='r', ls=':', label=f"F_L Hall {FL_hall:.0f}T")
    axx.set_xlim(0, 55); axx.set_xlabel("F [T]"); axx.set_ylabel("FFT (norm)"); axx.legend(fontsize=8)
ax[1,0].set_title("Rxx FFT"); ax[1,1].set_title("Rxy FFT")
fig.suptitle("Run 2 — hole SdH spot check n=-3e12, D=0, full field 0.2-7.9T")
fig.tight_layout(); out=os.path.join(SCR,"run2_sdh_hole.png"); fig.savefig(out,dpi=110); print("\nsaved",out)
