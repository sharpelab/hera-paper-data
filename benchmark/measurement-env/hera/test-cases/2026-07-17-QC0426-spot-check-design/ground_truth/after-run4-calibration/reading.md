# Reading — data/4 (run 4: 0 T gatemap, 101×101 full validator box)

Floor (must-see), from the archived ana notebook cells 13–16:

- **Clean single CNP line across the full box**; sweep complete (10201 pts),
  no gate leakage anywhere (|I_gate| ≤ ~110 pA incl. offsets), T stable
  1.165–1.170 K.
- **Ratio is data-calibrated**: CNP slopes −1.2829 (sr1) / −1.2897 (sr2),
  0.5 % cross-channel agreement → c_bg/c_tg = 1.2863; geometry prior 1.300
  agrees to −1.1 %.
- **Absolute scale is still a geometry prior** (C_TG anchored on 15.6 nm
  hBN); N_OFFSET ≈ −0.05e12 cm⁻², D_OFFSET ≈ 0 (R_CNP minimum at
  V_bg ≈ 0).
- **R_CNP is strongly D-tunable** (≥10× rise by |V_bg| ~ 2 V, both channels,
  both signs) — a hint consistent-with a D-induced CNP gap (ABC-leaning or
  mixed), fed to the per-channel read, never a standalone call.
- **Both density signs look clean and metallic away from CNP** — both sides
  eligible for SdH spot checks.

Don't penalize: no quantum-Hall lever-arm check is possible from a 0 T map
(absolute scale stays a prior until a fan/SdH pin); the agent has no
magnet-on data yet, so onset/tone statements are not expected here.
