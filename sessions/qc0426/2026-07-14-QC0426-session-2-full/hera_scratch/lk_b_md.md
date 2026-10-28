### Cell B — LK-mass ladder, 25 → 1.5 K on the cooldown (`temperature-dependence` Flavor B; unblocked by operator ruling, see session notes)

**Goal**: per-branch effective masses of f_s (~10–14 T), f_B (~53 T), f_top (~67 T) at the electron point (n = +6×10¹², D = 0) — the decider for the f_top fork: two distinct masses (light ML + heavy BL) confirm the pair; an f_top mass ≥ m_B + m_s says breakdown/intermod, a distinct third mass says third band (ABC domain). Plus the beat exclusion: a coexisting component *lighter* than the main branch cannot be a beat.

**Rungs (descending, LK-damping-spaced)**: **25, 18, 14, 10, 7, 5, 3, base(≤1.6)** K. Ladder tops at 25 K, not 50 — X/sinh(X) with m_B ≈ 0.1 m_e at 8 T gives A(25 K)/A(base) ≈ 0.09; rungs above that buy dead spectra (50 K stays a *machinery* proof, per Cell A). The low rungs double as the **T_e probe**: if amplitudes sit flat below ~8 K, the rig card's T_e ≈ 8 K is confirmed and the fit's T-axis becomes an effective T_e — decided by the data, not assumed.

**Per rung**: `set_T_verified(T)` (settle ≤ ±max(50 mK, 0.5%) held 60 s), then one field sweep over **B ∈ [4, 8] T uniform 9.5 mT (421 pts)** — δF ≈ 8 T, enough to separate f_B from f_top (Δ = 14 T); **directions alternate** (8→4, 4→8, …) so the magnet never re-traverses. Identical excitation/sensitivity at every rung (20 nA; sr1/sr2 2e-5, sr3 5e-5, sr0 5e-2) — comparability is the point; T_sample is fp'd so each run carries its own measured T. Final rung: heaters **off**, settle ≤ 1.6 K, sweep.

**Cost**: sweep ≈ 45 min/rung (29 min traverse + 16 min dwell) + settle ~5–15 min/rung → **~7.5–8.5 h total** (8 runs). Trim option if that's too rich: drop 18 K and 7 K → 6 rungs ≈ 5.5–6 h; the fit loses redundancy, not reach. Tag per run: `temperature-dependence` + rung comment.

Abort-safe: interrupt any time — heaters go off in the `finally`; a partial ladder is still a usable mass fit (each rung is self-contained).
