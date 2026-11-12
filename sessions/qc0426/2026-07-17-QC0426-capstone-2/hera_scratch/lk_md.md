## HERA — LK mass ladder (`temperature-dependence-vti`, Flavor B) — the deciding cross-check

Fan verdict so far (ana): hole side shows the ABA template — three-tone
{f_ML, f_BL, ≈λF_L} in 99% of columns, partition f_ML+f_BL = λF_L
(λ = 1.069 Luttinger-pinned), B-window split favors breakdown for the
≈F_L tone. **Per-branch LK masses decide**: expect m*(f_ML) ~ 0.013 mₑ,
m*(f_BL) ~ 0.05–0.07 mₑ, and the F_L tone damping with ≈ m_ML + m_BL if
it is the breakdown sum orbit (an ABC-domain pocket would carry its own
single-band mass). Two distinct masses + a sum-mass = **ABA confirmed**.

**Design**: fixed point = hole spot (n = −3.0e12, D = 0, run-5/6-proven
sens); B 1.5 ↔ 8 T (δF = 1.85 T — resolves the 28/33 split), 288 pts at
ΔB = 22.6 mT (⅓-Nyquist on 33.2 T), alternating direction from live field
per rung. **Rungs ascending** (up-legs catch in 2.5–4 min; descents are
passive-limited): base, 6, 10, 15, 22, 32 K — all ≤ 50 K cap,
`set_both(T, ratio=0.95)` (sanctioned; ratio untouched). Ladder covers
heavy-tone kill (~15–20 K at m* ~ 0.06) with the light tone surviving to
32 K; T_e ≈ 8 K floor noted — masses lean on the T ≥ 6 K rungs. One file
per rung.

**Guard set (mandatory, VTI variant)**: hover acceptance (spread < 0.1 K
over 90 s in [nom−0.5, nom+3]); logfile-freshness (< 15 s = 3 write
periods) on every poll; direction-aware runaway guard (T_vap > start+2 ∧
> target+2 → heaters off + abort); range-nonzero check after every
`set_both`; all waits interruptible. Ladder ends heaters-off, passive
descent, gates holding the spot.

**Cost**: 6 × (~55 min traverse-floored sweep) + 5 hover catches ≈
**6–6.6 h**. Checkpoints: per-rung first rows + completion; abort on
runaway, stale logfile, railing. E1 auto: T via sanctioned `set_both`
within cap, B/gates inside validators.
