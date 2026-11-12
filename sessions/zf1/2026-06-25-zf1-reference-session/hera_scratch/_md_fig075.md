## HERA — Figure 4 (+0.75 mT): intermediate field, with 1-hour base dwell

**Queued for after run 9 (+1.25 mT) completes.** Fills the 0→1 mT gap — the dome-collapse set becomes 0 / 0.75 / 1 / 1.25 / 2 mT (true fields). At 0.75 mT the SC is only mildly suppressed (expect Tc ~190 mK), so cap **350 mK**, **80 points** (~4 mK), same 1τ settled method.

**Change you asked for:** after positioning the field (controller +0.384 mT, decreasing |B| one-sided, no zero-cross) and the post-ramp R-settle, it now **dwells a full hour at base** (`interruptable_sleep(3600)`) for complete thermalization before the ladder starts — on top of the T<45 mK poll. This should kill the early base-floor transient / any not-quite-settled base that showed up before. **~9.3 h total** (1 h dwell + ~8.3 h ladder).

Field positioned one-sided + read back; preconditions asserted (gates at optimum, heater off). The hour dwell is interruptible. Run it whenever run 9 is done; I’ll catch it and plot it. After this we have a clean 5-point B_c(T); then back to B_eff0 for Fig 5.
