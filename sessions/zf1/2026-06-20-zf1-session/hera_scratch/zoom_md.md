## HERA — high-res zoom: V_bg>0 / V_tg<0 quadrant (SC re-investigation)

Per operator: re-investigate SC in the **V_bg positive, V_tg negative** quadrant — the large-negative-D region where BLG-WSe₂ Ising-SOC proximity SC is expected. The coarse Step-1 map (0.13 V) showed only metal + CNP ridge here; this zoom (**0.07 V grid, ~2× finer**) tests whether a narrow SC dome was stepped over. 4T Rxx = **sr830_2** (corrected channel); θ/φ excitations off (clean floor); drive 0.5 nA.

**Box:** V_tg fast **[−7, 0]** (101 pts, 0.07 V) × V_bg slow **[0, +4.2]** (61 pts, 0.07 V). Megasweep, slow_delay=3 / fast_delay=1. Reads trimmed to sr1/sr2 (+ gates, T) to cut per-point time. The CNP ridge crosses this box (Vtg_cnp = −1.19·Vbg+0.08); it covers both sides at large negative D.

**⚠ Field caveat:** taken at `magnet.field()≈0` = ~2 mT at the sample (trapped flux). This is an **under-resolution check only** — a *field-suppressed* fragile SC stays hidden even here. If clean, the effective-zero-field search is the decisive next step (or I re-run this zoom at the effective zero).

**Price:** 6161 pts. From the measured megasweep rate (~1.3–1.5 s/pt with trimmed reads) → **~2–2.5 hr**. **Checkpoint @ ~12 BG rows (~25–30 min):** I'll read the partial sr2 map for any low-Rxx feature; continue / fine-zoom on a hit / abandon if clearly featureless. `hera-watch` armed.

**Preconditions** (asserted): T base; |B|<5 mT; drive 0.5 nA; gates printed. No magnet move; no `volt.step` change. Leakage corners (TG −7, BG +4.2) already validated clean. Gates park to 0 at end.
