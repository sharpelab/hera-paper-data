## SdH spot A (run 4): electron n=+8e12, D=0 -> FS count

First FS-count spot check (`fs-count` step 3). Fixed-(n,D=0) field sweep 0->8T, FFT
in 1/B. **Result: both Rxx channels show a two-tone pair** (f_ML ~17 T + f_BL ~70 T)
summing to F_L (evaluated at the Hall density n_H=8.4e12 -> F_L=86.8 T) -> **two Fermi
surfaces -> ABA**. Tones are detrender-robust (poly 3/5/7, hann/blackman). sr1
overloads >5.44T (MR climb to 218 ohm); its FFT is windowed to [2,5.3]T, sr2 to
[2,8]T. Hedges: f_ML mildly window-sensitive; LK-mass and Onsager-overlay cross-
checks unavailable this session (temperature-dependence blocklisted; model clamp
<3.5e12). To be firmed by F(n) partition-robustness across the fan.
