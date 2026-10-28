# Run 7 — hole side, n = -1.2e12, D = 0, B 10 -> 0.3 T: raw, onset, FFT vs F_L
r7 = run(7)
print(summarize_run(r7))
B7 = r7.col("magnet_field")
R7 = r7.col("sr1_X") / IBIAS
i7 = np.argsort(B7)
Bs7, Rs7 = B7[i7], R7[i7]
FL7 = luttinger_frequency(1.2e16)  # 12.4 T
on7 = sdh_onset(Rs7, Bs7, r_full_scale=50e-6 / IBIAS)
print(on7.summary())

fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.6))
ax[0].plot(Bs7, Rs7, lw=0.6, color="#4053d3")
ax[0].set(xlabel="B (T)", ylabel=r"$R_{xx}$ ($\Omega$)", title="run 7 raw — n=-1.2e12, D=0")
m = Bs7 >= on7.onset_b
p = np.polyfit(Bs7[m], Rs7[m], 5)
ax[1].plot(Bs7[m], Rs7[m] - np.polyval(p, Bs7[m]), lw=0.5, color="#4053d3")
ax[1].set(xlabel="B (T)", ylabel=r"$\Delta R_{xx}$ ($\Omega$)", title=f"bg-subtracted above onset {on7.onset_b:.2f} T")
fr, sp = sdh_fft(Rs7[m][:, None], Bs7[m], b_range=(on7.onset_b, Bs7.max()), bg_degree=5)
ax[2].plot(fr, sp[0], lw=0.8, color="#4053d3")
ax[2].axvline(FL7, color="#b51d14", ls="--", label=f"$F_L$ = {FL7:.1f} T")
ax[2].set(xlabel="F (T)", ylabel="|FFT|", xlim=(0, 30), title="1/B FFT above onset")
ax[2].legend()
fig.tight_layout()
print(f"R max {np.nanmax(R7):.0f} Ohm ({np.nanmax(R7)/5e3*100:.0f}% of 5 kOhm FS)  [worst-corner anchor for the fan: |n|=1.2e12 at 10 T]")
print("""model @ n=-1.2e12 (ABAB): near-CNP hole pair, tones close/balanced (recipe's low-|n| exception regime)
model @ n=-1.2e12 (ABCA): 12.4 T, m* ~ 1 m_e -> thermally dead at T_e ~ 8 K
measured: crowded set (4.7, 6.6, 8.5, 9.4, 12.3, 14.8 T) with mutual harmonic flags; onset 0.71 T""")
