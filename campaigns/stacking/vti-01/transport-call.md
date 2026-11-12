# vti-01 — transport call (locked)

**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Prereg §5 step 1.

## Provenance

- Session: E1 HERA tactical on the VTI, 2026-08-18 21:41 → 2026-08-20 17:24
  (rig local). Archive: `hera/docs/notes/2026-08-18-vti-01-session/`.
- Corpus: `d8e1337` (= `arm1-freeze`), clean (`corpus_provenance.json`).
- Transcript: `transcripts/18ed1c71-d971-4290-b0c2-752d15437e88.jsonl`.
- Call: ana notebook `20260818_ana.ipynb` cell 33, landed 2026-08-20 ~02:45;
  addendum cell 38, landed 2026-08-20 ~17:15 after the operator-requested
  τ = 300 ms extension (runs 19–20). Text below is verbatim from
  `hera_scratch/ana_call.md` + `hera_scratch/ana_call_addendum.md`; the
  notebook cells carry the same text plus a one-line nb-collab banner.
- Session log: `session_notes.md` (grant, E0 drop + re-grant, rulings,
  handoffs).

---

## THE CALL — vti-01 stacking order (investigation step 7, output contract)

**1. Per-region verdicts** (STYLE strength scale):
- **sr1 (B_SD–L4): ABA / Bernal (strong).**
- **sr3 (L3–L2): ABA (consistent-with)** — agrees with sr1 on all frequency content (fan, spot checks) but its LK amplitudes are SNR-limited and non-monotonic; no independent mass.
- **sr2 (L4–L1): uninformative** (weak short pair; signals near floor throughout).
- No positive evidence of an ABC domain on any channel; "most channels uninformative" is within normal outcome space.

**2. Evidence (all D = 0 true, hole side unless noted; runs cited):**
- **Branch A**: F_A = (0.87–0.90)·F_L(n), linear through origin over n = −0.70…−1.74×10¹² (run 10 per-column FFT, sr1+sr3) and present at n = ±1.7–1.8×10¹² (runs 8, 9). At **scale 1.0** this equals the ABA model's BL fraction f_BL/F_L = 0.87 (fs_count_b0, Datta SWMcC+γ₄); the ABC reading requires a 0.90 global rescale *and* fails the mass (below).
- **LK mass on A: m* = 0.049 ± 0.002 mₑ** (runs 12–18, 7 rungs 1.25–15.1 K, B_eff 2.86 T, sr1) vs ABA BL **0.060** (−18%, within model parameter error) vs ABC **0.108** (excluded: predicts 0.3% residual amplitude at 15 K; measured 16%).
- **A/2 component: m* = 0.047 ± 0.003 mₑ** — identical to A ⇒ even–odd modulation of the same LL ladder, not a second band. Its position is locked at F_A/2 across all densities and both signs (runs 8–11), ruling out an independent pocket.
- **Harmonic screen**: 2F_A, 3F_A combs identified and excluded (runs 8, 10). Sum line at F_A + F_A/2 weak (mixing).
- **Luttinger**: at scale 1.0, A carries 87–90% of F_L; the residual 10–13% ⇒ f_ML ≈ 1.9–2.4 T — exactly the model's ML fraction and below this campaign's resolution (see hedges) — self-consistent ABA budget. The ABC alternative closes the sum only via the rescale.
- Calibration provenance: ratio data-calibrated (run 7, c_bg/c_tg = 0.7222, channels agree 0.4%); absolute scale geometry prior — QH lever-arm upgrade still pending, which is precisely why the scale-free discriminators (mass, BL fraction, A/2 locking) carry the call.

**3. Confidence + hedges:**
- Strong, not decisive: the **ML pocket was never directly resolved** — the low-B hunt (run 11, δF ≈ 0.6 T, 3.8 periods at the predicted 2.4 T) returned no reproducible tone (its candidate pair failed grid-change reproduction vs run 8), so the ML is *searched-but-unresolved*: below ~1.5 T it is unresolvable in principle here, and a disorder-broadened ML (τ_q much shorter than BL's) evades at any F. Two distinct masses were therefore never observed; the call rests on the BL fraction + single mass + modulation identity, not on counting two surfaces.
- A blended ABC+ABA mixed-domain peak inside A is disfavored by the clean single-mass LK fit (a 0.049/0.108 mixture damps non-LK), but small-area ABC domains below spectral weight cannot be excluded. R_CNP grows symmetrically with |D| yet caps ~20 kΩ at 0.14 V/nm (run 7) — uninformative at T_e ≈ 8 K (domain caveat), fed here, not read alone.
- T_e ≈ 8 K (rig) limits everything; absolute-T claims inherit the uncharacterized mount→device gradient (rig card); mass errors are fit-statistical only. **No automated LK fit exists in the corpus — fit flagged for expert review.**
- Transport is contact-limited through a single ~109 MΩ T_SD source contact (I ≈ 1 nA); all Rxx normalized by measured drain current per point.

**4. What would firm it to decisive:**
- **Resolve the ML pocket directly**: mK electron temperature (different rig) at low B — the 2–3 T frequency band with δF ≲ 0.5 and low T_e; or
- **Step-6 Streda/Chern complement at 10 T+**: ABA's non-dispersing ML N = 0 doublet offsets the QH sequence (larger gaps, resolvable at this T_e) — the natural next VTI measurement if the campaign continues;
- Per-branch LK at a *second* density and on the electron side (side-symmetry of the mass);
- QH lever-arm scale upgrade (removes the scale-vs-fraction degeneracy independently).

**5.** Per the contract: this is a call with feature-level evidence; the ML non-resolution is stated, not silently absorbed.

---

## CALL ADDENDUM — runs 19–20 (τ = 300 ms, operator-requested): ML pocket resolved

**The hedge is retired. Verdict upgrade: sr1 region ABA / Bernal — now carried by both pockets.**

- **ML branch directly resolved** (run 19, sr1): a third tone at 1.7 → ~3.6 T over n = −0.70…−1.42, tracking its own shallow Onsager slope (~2.4 T/10¹² — the model f_ML *shape*), distinct from A/2; corroborated at lower SNR on sr3. Confirmed at the high-|n| endpoint by run 20 (δF 0.72 window): **f_ML = 4.4 T** (window sensitivity 4.4–5.5 → quote 4.7 ± 0.6) at n = −1.74. Run 19's apparent 2.0 T pinning beyond n = −1.5 was sub-0.9 T background contamination (excluded by cutoff), the same artifact class killed twice before.
- **Luttinger closes with the pair at one global scale**: f_ML + f_BL = (1.14 ± 0.02)·F_L across ten run-19 columns and run 20's endpoint (20.8 vs 20.6). λ = 1.14 sits at the lever-arm band's edge — the QH lever-arm check remains the pending upgrade. Partition f_ML/Σ ≈ 20% vs model 13% (inside the model's stated partition uncertainty).
- **Branch identities pinned by masses**: f_BL = branch A (16.4 at −1.74), measured m* = 0.049(2) mₑ (model BL 0.060). The alternative — {4.4, 12.0} as the pair with 16.4 a magnetic-breakdown sum — is **excluded**: a sum orbit damps with m_ML + m_BL (~0.07 model), and 16.4 is measured *lighter* than its would-be BL parent. 12.0 = 16.4 − 4.4 exactly → mixing/difference line. A/2 (8.2–8.8) keeps its even–odd-modulation identity (mass 0.047 ≈ parent; an ML 2nd harmonic would read ~0.02).
- Under the revised scale the earlier "ABC singleton at 0.90·F_L" reading is fully dissolved: it was f_BL at λ = 1.14 with the ML branch unresolved at τ = 100 ms.

**Remaining softness** (kept from the original contract): ML mass unmeasured (predicted ~0.01 mₑ — a low-B-window ladder would finish it); λ = 1.14 pending QH lever-arm; sr3 corroborates without independent tracking; sr2 uninformative. On the strength scale this is **ABA (strong, two-branch)** — the last step to *decisive* is the ML mass or the Streda complement.
