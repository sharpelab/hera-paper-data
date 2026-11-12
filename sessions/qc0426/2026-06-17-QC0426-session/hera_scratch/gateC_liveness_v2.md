## HERA — Gate C liveness v2 (LS335 contention fix)

Cell 30 errored at point 0: per-point `heater.sample_temperature` poll hit the
rig-card LS335/Grafana VISA-contention quirk (run id 0 = dud, metadata only).
Fix: removed the Lakeshore poll from the per-point loop; T is snapshotted once in
`meas_config` and the Grafana logger keeps the time series. Otherwise identical —
provided contacts, TG -3..+3 V at BG=Si=0, B=0. Re-running (~3 min). E1 auto.
