# Run 6 — onset + 1/B FFT vs F_L (sdh-spot-check step 6)
FL6 = luttinger_frequency(3.2e16)  # n in m^-2 -> 33.1 T
i6 = np.argsort(B6)
Bs6, Rs6 = B6[i6], R6[i6]
on6 = sdh_onset(Rs6, Bs6, r_full_scale=50e-6 / IBIAS)
print(on6.summary())

fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.6))
m = Bs6 >= on6.onset_b
p = np.polyfit(Bs6[m], Rs6[m], 5)
ax[0].plot(Bs6[m], Rs6[m] - np.polyval(p, Bs6[m]), lw=0.5, color="#4053d3")
ax[0].set(xlabel="B (T)", ylabel=r"$\Delta R_{xx}$ ($\Omega$)", title=f"bg-subtracted (deg 5) above {on6.onset_b:.2f} T")
for cut, a in [(0.35, ax[1]), (1.0, ax[2])]:
    mm = Bs6 >= cut
    fr, sp = sdh_fft(Rs6[mm][:, None], Bs6[mm], b_range=(cut, Bs6.max()), bg_degree=5)
    a.plot(fr, sp[0], lw=0.8, color="#4053d3")
    a.axvline(FL6, color="#b51d14", ls="--", label=f"$F_L$ = {FL6:.1f} T")
    for k in (2, 3, 4):
        a.axvline(k * 7.1, color="0.6", ls=":", lw=0.8)
    a.set(xlabel="F (T)", ylabel="|FFT|", xlim=(0, 45), title=f"1/B FFT, cutoff {cut:.2f} T (dots: k x 7.1)")
    a.legend()
fig.tight_layout()

# Model comparison (fs_count_b0, run in scratch — hera_scratch/ana_spots.py):
print("""model @ n=3.2e12 (ABAB): light 7.31 T (0.22 F_L, m*=0.027), heavy 25.78 T (0.78 F_L, m*=0.061), ratio 3.53
model @ n=3.2e12 (ABCA): singleton 33.1 T (= F_L)
measured: 7.1 T (strong, censored at 0.3 T edge) + comb 14.1 / 22.1 / 29.5 T (~2x/3x/4x of 7.1)
ambiguity: 22.1 T = 3rd harmonic (21.3) within ~2*dF, OR the ABAB heavy tone (7.1 + 22.1 = 29.2 ~ F_L at scale 0.88)""")
