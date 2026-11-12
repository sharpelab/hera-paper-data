# vti-02 stacking investigation — handoff plan, 2026-08-23

Goal: evidence-cited ABAB / ABCA / ABCB / cannot tell for the sole connected
voltage pair B_1-B_2. Two resistance ridges within that pair are candidate
inhomogeneous contributions, not separately wired regions. No prior-session data.
E1 remains engaged per brief, session_notes and measure cells 32/46.

1. COMPLETE: A/B VERIFY and gate-C liveness (measure 18/32/34, data/0-3).
   Validators match card exactly: TG [-0.3,1], BG [-1.3,2], Si [-25,25],
   B [-10,10], heater setpoints [0,100]. No edits to safety surfaces.
2. COMPLETE with caveats: run 5 CNP map. Main-ridge slope gives c_bg/c_tg
   0.772765; c_tg=0.0027960593 F/m2 remains geometry prior. n_offset=-0.0893793
   in 1e12 cm^-2 units, provisional D_offset=-0.013 V/nm. Resistance-minimum
   symmetry is an operational D origin, not an independent electrostatic proof.
   Secondary ridge is at nominal n_A=-0.426e12. Separate domains vs contact
   inhomogeneity remain hypotheses. Do not equate gaplike R(D) with stacking.
3. COMPLETE: data/6 electron +3.2, data/7 hole -1.2 spot traces to 10 T.
   Raw data plus helper FFT/onset analysis promoted before the next acquisition.
   Stable current and sub-0.22 nA leakage; Rmax 530/587 ohm. Electron peaks
   ~7,22,30 T can include harmonics; low-B helper onset is censored/background
   sensitive. Hole spectrum varies with fit window. No stacking verdict yet.
4. NEXT: landau-fan, B slow, co-swept TG/BG fast at operational D~0,
   nominal n_A=-1.2..+3.2e12, 89 points (0.05e12 increments).
   Four context rows B=0,0.5,0.75,1 T, then 103 rows uniform in 1/B from
   1.25 to 6 T. Start from operator's measured ~0 T; end at 6 T, no return.
   Fast dwell 3 s (10 tau at 0.3 s/24 dB); slow dwell 3 s; Si stays 0 V.
   Uniform-inverse-B main grid has delta(1/B)=0.006209 /T: <0.23 cycles
   per row for F<=37 T. Density resolution is ~2.4 points per fourfold
   LL period at 1.25 T, ~11.6 at 6 T under prior scale. Lowest rows are
   context only, not a resolved high-density low-B spectrum.
   Both carrier signs, both candidate CNPs included. Excludes nominal density
   tails [-1.27,-1.2] and [3.2,3.27], higher |n| inaccessible at this D;
   excludes B>6 and negative B. 6..10 T extension would add ~3 h at this
   inverse-B spacing, so defer until branches show it is needed.
   Price from data/5: 1.098 s/pt at 1 s dwell -> ~0.10 s overhead;
   conservatively use 3.2 s/pt for two gate writes + extra readbacks.
   107*89*3.2 s = 8.47 h, 6/0.137=43.8 min ramp, plus field-settle,
   flyback, preflight and 10% contingency -> 10 h 30 min.
   Checkpoints: first 0 T row against run 5 and runs 0-3, next two rows
   for leakage/current/clipping; then every <=30 min using hera-watch.
   Point guard stops for >1 nA leakage, low drain, clipping or base-T failure.
   Interrupt does NOT stop VTI magnet ramp; supply continues to row target.
   On safety stop: read state, notify and E0; no re-entry without explicit grant.
5. AFTER FAN: raw voltage/current/gate/temp grids first, then signed V/I and
   density derivative. Track independent branches vs gate coordinate, crossing
   structure, electron/hole contrast and CNP origins; test harmonics and displaced
   copies before assigning subbands. Compare the ideal low-energy decompositions
   ABAB (J=2+2), ABCA (J=4), ABCB (J=1+3) cautiously; branch count alone is
   insufficient when multiple local dopings contribute. Attempt absolute lever-arm
   calibration only with defensible LL indexing and degeneracy; no Hall channel.
   If a targeted second D cut can distinguish remaining hypotheses, design it
   from 6 T downward, price it, and cite the new evidence. Do not default to
   heating or additional full fans. If ambiguous, calibrated cannot tell.
6. FINAL: final ana cell gives B_1-B_2 verdict + strength, numbered run-id
   evidence, confidence/overturn conditions and unmeasured regions. Ask
   return-to-initial at close-out, then execute authorized field/gate zeroing
   at committed pacing + heater off and log readback. No standalone Si survey.
