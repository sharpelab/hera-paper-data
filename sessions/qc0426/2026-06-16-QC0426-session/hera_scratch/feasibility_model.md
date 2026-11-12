# FS-count forward-model output (Step 2 prep) — fs_count_b0.py, D=0

VF(ABA)=1.003e6 m/s ; v0(ABC)=1.023e6 m/s

## ABA (D=0): n[1e12] -> #FS, freqs[T] (ML small, BL big), sum
- 0.25 -> 1 [2.6]
- 0.50 -> 1 [5.2]
- 1.00 -> 2 [0.0, 10.3]  sum 10.3
- 1.50 -> 2 [0.2, 15.3]  sum 15.5
- 2.00 -> 2 [0.5, 20.2]  sum 20.7
- 3.00 -> 2 [1.5, 29.5]  sum 31.0

## ABC (D=0): n -> topo, #freq, F_tot
- 0.25 -> 3-pocket, 1, 2.6
- 0.50 -> 3-pocket, 1, 5.2
- 1.00 -> single, 1, 10.3
- 1.50 -> single, 1, 15.5
- 2.00 -> single, 1, 20.7
- 3.00 -> single, 1, 31.0

## ABA ML pocket vs displacement U (n=1e12)
- U=0/5/10 meV -> 2 FS [~0.01, 10.33]
- U=20/40 meV -> 1 FS [10.34]  (ML merges)

## Reads for design
- DISCRIMINATOR = small ML tone F~0.5-1.5T (grows with |n|); ABC lacks it.
- BL tone (10-30T) ~ ABC single tone -> NOT discriminating (big tone useless).
- Operate D~0 (ML merges by U~20meV). CNP at (0,0) -> D~0 reachable.
- ML tone >5 periods: F=1.5T needs B_lo~0.2-0.3T (periods come from low B).
  -> fan needs good LOW-field resolution + n~2-3e12.
- Luttinger: sum(f) = n*(h/4e) consistency check across the fan.
- Step 3 go/no-go B-sweep gives the actual SdH onset field (vs B_lo need).
- Nyquist (Step 4): ΔB ≈ (4e/h)·B²/n; check at low-B/high-n corner, >=2-3
  rows/period. Device history (2026-06-14): ΔB=0.1T undersampled n=10,B=4T
  -> spurious pocket. Trim n-pts / floor high-n claim; don't coarsen B.
