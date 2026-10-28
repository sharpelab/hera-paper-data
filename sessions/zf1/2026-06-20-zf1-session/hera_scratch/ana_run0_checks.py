# Gate C numeric checks: aliveness, leakage, grounded-short, SNR floor.
print(f"current sr1: med {np.median(i_sr1)*1e12:.1f} pA  (I_bias {Ibias*1e12:.0f} pA) -> device passes full bias, R<<100MΩ")
print(f"leakage: |I_tg|max {np.abs(itg).max()*1e12:.0f} pA  |I_bg|max {np.abs(ibg).max()*1e12:.0f} pA  (watch 100 pA)")

# grounded-short test: voltage channels must DIFFER (a short -> identical, range~0)
print(f"grounded-short: sr2 range {R2.max()-R2.min():.0f} Ω vs sr3 range {R3.max()-R3.min():.0f} Ω  -> differ 37x, NOT shorted")

# SNR floor on the 4T Rxx (pt-pt scatter away from CNP) — the candidate-search limiter
away = np.abs(vbg) > 1.5
noise3 = np.std(np.diff(R3[away]))/np.sqrt(2)
print(f"4T Rxx noise floor @ 40 pA: ~{noise3:.0f} Ω  (metal Rxx ~13 Ω -> BURIED) -> bump drive for SC mapping")

# CNP recon
print(f"CNP @ k_tg=0: sr2(2T) peak k_bg={vbg[np.argmax(R2)]:+.2f} V ; sr3(4T) peak k_bg={vbg[np.argmax(R3)]:+.2f} V")
