## HERA — Run 6: field response (B⊥ kill / B_c⊥) at the SC optimum — first magnet energization

Supercurrent confirmed (Ic≈18 nA). Now the field hallmark (`field-sweep-1d`, investigation Step 3): does a small B⊥ quench the zero-resistance state **while the normal state stays ≈ unchanged** (the field-kill that counts *strong* for SC), and what is B_c⊥?

**First field energization this session** — applying the brief's field discipline:
- **One-sided, monotonic toward 0:** position-ramp 0 → **+80 mT** (well into expected normal state, inside the 100 mT cap), settle, then **sweep +80 mT → 0** (decreasing |B|, never crossing 0). The −B side and an effective-zero zoom are follow-ups.
- **Settle 120 s** after the positioning ramp (ramp-heating is largest at low |B| — rig card); T is fp'd densely so I can verify base-T recovery post-hoc and *derive the real settle for later ramps* (none measured yet this session).
- **Measured field recorded:** fp `magnet.field` (readback) alongside the setpoint — after an 80 mT excursion, nominal 0 carries up to ~10 mT remanence, so the true-field axis matters.

At the optimum (Vtg=−5.444, Vbg=+4.053), **1 nA AC, zero DC bias** (so Rxx≈0 while Ic>1 nA; Rxx rises toward normal once B suppresses Ic below the probe). 161 pts (0.5 mT), delay 1.

**Preconditions** asserted: base T, B≈0 start; prints `magnet.ramp_rate()`. **Cost ~6–8 min.** **Read after:** Rxx rising from ~0 at low B to a **flat normal plateau (~55 Ω, matching run 5)** = field-kill confirmed + B_c⊥ estimate (where Rxx ≈ half-normal). A sloping/non-saturating high-B Rxx = generic MR caveat. If Rxx hasn't saturated by 80 mT, B_c⊥ > 80 mT (note ξ ≲ 60 nm) — escalate toward the cap.
