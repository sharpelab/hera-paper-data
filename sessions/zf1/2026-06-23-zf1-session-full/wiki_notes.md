<!-- Aaron's live session notes from the lab wiki (Outline).
     Source: https://wiki.sharpelab.science/doc/20260623-zf1-xp3nfjj7YG
     Captured 2026-06-24 (the tactical chat transcript did not persist; these
     "AS:" critiques are part of the recovered record — see POSTMORTEM.md). -->

# Token usage

* 88K: full init
* 142K: coarse gatemap
* 223k: linecuts
* 277K: midpoint of bias spec
* 338K: field sweep

# Notes

* AS: Two errors popped up again
  * ```
    Two important corrections the placeholders got wrong for zf1:
    1. B_SESSION_CAP — brief sets |B| ≤ 100 mT for this session (lines 89, 114). Placeholder says 5.0 T. Must be 0.1.
    2. ana.ipynb geometry — placeholder t_tg=15.6e-9, t_bg=12e-9 is wrong; card says 23.6 nm / 20 nm.
    Everything else in the measure notebook (TG −7/+6, BG −4/+4.2, heater 6.5 V, geometry 23.6/20, gains) already
    matches the card. Let me fill the slots.
    ```
* AS: gate-current-sanity-check still not going out to full gate range (decided on +/-2 V somehow)
  * AS: it also recognized that it should do multiple legs but did not propose these measurements
  * ```
    Gate C status: 1 of 4 legs in, fully clean. Please run the remaining three legs (edit the EDIT block): k_bg 0→−2,
    k_tg 0→+2, k_tg 0→−2. The negative legs matter especially — the expected proximity-SC region sits at D < 0 (holes
    pushed into the WSe₂), so we'll be living in negative-gate territory downstream, and I want to confirm both gates
    stay clean there too.
    ```
* AS: compared to last session, this coarse gatemap is much more fine
* AS: gate-current-sanity check seems to have messed up the gatelimits.
  * ```
    # Map extent: full validator envelope inset 0.2 V. TG (-7,+6); BG (-4,+4.2).
    V_tg = np.linspace(-6.8, 5.8, 41)   # slow (larger span -> slow to avoid big fast ramp-backs)
    V_bg = np.linspace(-3.8, 4.0, 61)   # fast (smaller span; 0.13 V/pt resolves the CNP)
    ```
* AS: consider entire rebuilt of gate-current-sanity-check or replace with reentry-baseline
* AS: For live plots, I always just plot all live values. No need to truncate things. For example, the gatemap does not plot current
* AS: in bias spec, it doesn't seem to know about the coherence peaks still
* AS: it should really sweep field across zero not from some value to zero
* AS: fraunhoffer is also too narrow in current
* AS: should provide some tooling for heating top loader. it is not doing a great job. just a simple function saying going from some temp to the other and it prints something. wow
* AS: it is getting confused looking at the wrong probe thermometer. we need to point it to both probes
* AS: nice it caught that t_c is higher than expected
* AS: generically we need to use interruptible sleeps generally in case of emergency
