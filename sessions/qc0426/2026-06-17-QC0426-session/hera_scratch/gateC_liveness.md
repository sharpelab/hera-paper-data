## HERA — Gate C: cheap liveness on the provided contacts (E1 auto)

First-session branch (no reference runs). Routes the provided contact config
(src T2 / drain B7, Rxx on T3–T4 & B4–B5, Rxy T5–B6) and takes a short
**TG trace at BG=Si=0, B=0** to confirm the device is alive before committing
to the 0 T gate map. This is the **liveness** half of `gate-current-sanity-check`
— **not** the range-finding/leakage walk (blocklisted; the operating limits are
provided as safe). TG stays inside the provided validator (−3..+3 V of [−6,+7]).

What I read from it: current-bias (5 nA) means the **Rxx voltage channels
(sr1/sr2) carry the modulation** (a CNP peak as TG crosses neutrality), while
sr0 (drain current) holds ~constant — that's the alive signature. Channels must
be independent (not all identical → grounded-device short) and BG/Si leakage at
the pA floor. I set sr1/2/3 sens to 5 mV so a high-R CNP peak doesn't overload;
reversible config choice.

~3 min (61 pts × 2 s + overhead). E1 auto — in-envelope, passes preconditions,
no consent gate. Executing now; I'll read the run from disk and report before
designing the gate map.
