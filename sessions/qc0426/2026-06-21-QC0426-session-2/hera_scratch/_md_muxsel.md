## HERA — Gate C (1/2): route the provided contact configuration

E1 auto (ContactMux routing, inside the device-card config). Select the provided configuration: source=T2, drain=B7 (sr0), sr1=T3–T4, sr2=B4–B5, sr3=T5–B6 (Hall). `settle_s` = 4 s inside `select`. `qsw.reset()` is forbidden (drops the Si standing closures). Then a quick raw lock-in read-back to confirm the contacts are live before the liveness sweep. ~5 s.
