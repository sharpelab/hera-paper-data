# Second-rater agreement — sandesh vs scores of record, pool T1

*Computed by `hera_agree.py` (pre-declared). Subset: 56 cards / 212 items, seed 20260904.*

## Main text (pre-declared, two numbers)

- Items paired (both raters correct/partial/wrong): **145** of 212; unverifiable by either rater: 67 (record 24, sandesh 51); unscored by sandesh: 0.
- **Exact agreement: 0.648**
- **Quadratic-weighted κ (items, 1/0.5/0): 0.383**

## Supplement (pre-declared)

| stratum | n items | exact | κ_w |
|---|---|---|---|
| type inference | 74 | 0.568 | 0.336 |
| type decision | 51 | 0.784 | 0.529 |
| type verdict | 20 | 0.600 | 0.292 |
| run T1A | 31 | 0.645 | 0.360 |
| run T1B | 24 | 0.792 | 0.524 |
| run T1C | 26 | 0.423 | -0.130 |
| run T1D | 24 | 0.708 | 0.604 |
| run T1E | 19 | 0.632 | 0.497 |
| run T1F | 21 | 0.714 | 0.636 |

Card level (53 cards with both raters scoring ≥1 item): exact 0.453, κ_w 0.508.

| run | S_claim record (subset) | S_claim sandesh (subset) |
|---|---|---|
| T1A | 0.751 | 0.804 |
| T1B | 0.941 | 0.902 |
| T1C | 0.525 | 0.802 |
| T1D | 0.840 | 0.848 |
| T1E | 0.781 | 0.824 |
| T1F | 0.621 | 0.704 |

Partition test (every corpus arm > every no-corpus arm): record on subset **True**; sandesh **True**.

## Disagreements (for characterization; both raters' notes)

- **T1-100** (T1A/inference): item 2 record=wrong sandesh=partial; item 4 record=correct sandesh=partial
  - record: 2) Hall adxmixture should not stop, the mixed component should continue to get larger. In this case, the mixed in component should drive the Rxx hugely negative. This is almost certainly not admixture
  - sandesh: The drop in Rxx could also arise from weak localization. It does not have the right functional form for weak localization though, but I think the agent should relay that to the user before saying definitively that the drop arises from the Rxx pair being at the flake corner. 

- **T1-042** (T1C/inference): item 1 record=partial sandesh=correct; item 3 record=partial sandesh=wrong; item 4 record=partial sandesh=wrong
  - record: You can't judge it is ohmic from this! Also it is probably reading CNP. docking points
  - sandesh: sr1 (B1-B2) does not look like a sensible measurement as it is reading large negative values.
For Rxx, there is a peak at -0.2V. I disagree that the resistance is monotonic with gate voltage. The peak at -0.2V could be CNP.


- **T1-091** (T1D/inference): item 1 record=wrong sandesh=partial; item 2 record=partial sandesh=correct
  - record: 1) The light tone's mass is unstable to window. It is certainly not 2.4 SD apart. 2)/3) correct conclusion drawn on improper data. 
  - sandesh: The FFT data is too coarse to draw crisp conclusions about the oscillations. It is hard to see why two effective masses are involved.
- **T1-152** (T1E/decision): item 2 record=correct sandesh=partial
  - sandesh: There is a caveat from using Landau levels to calibrate density. For LLs from a single band, the spacing between SdH oscillations in indeed set by density. But for more complicated SdH oscillations say from multiple orbits along disconnected Fermi surfaces, this conversion is not simple. What the agent did is better relying than the zero field data, but it should make the user aware that there will be issues even with the in-field data.
- **T1-087** (T1D/inference): item 2 record=wrong sandesh=partial
  - record: 1) correct conclusion for median of data, but error bars from extraction process do not allow for such a sharp conclusion. 2) This conclusion was previously ruled as innacurate given the resolution of the data taken. 3) plausible conclusion but not reached in a particularly valid mannor.
- **T1-049** (T1A/decision): item 2 record=correct sandesh=partial
  - sandesh: What is sensitivity here? Is it for the lockins? Agent should specify to the user that the sensitivity limits the Rxx range to a particular set of values in Ohms. 
- **T1-114** (T1F/verdict): item 1 record=wrong sandesh=correct; item 2 record=correct sandesh=partial
  - record: 5) The scan did not have the resolution to make such a claim
  - sandesh: Gap minimum being centered at zero displacement field is not a robust criterion. Even at 1K, correlated phases near D=0 can make the distinction between stacking orders difficult to determine. Agent should clarify this caveat or at least give the user some reservations about extracting the stacking order from just this one criterion.
- **T1-119** (T1F/decision): item 3 record=correct sandesh=partial
  - sandesh: Density range seems to have more of the electron size than the hole side by just looking at the fan as a function of top gate voltage.
- **T1-141** (T1E/decision): item 1 record=wrong sandesh=partial; item 2 record=wrong sandesh=partial
  - record: Or your fits are just terrible because you too bad data. 2 is cherry picking
  - sandesh: I think this dataset is too coarse to do any of the LL fitting.
- **T1-150** (T1F/inference): item 1 record=partial sandesh=correct; item 3 record=partial sandesh=correct
  - record: These are not gaps. docking points. Also, where the gap crosses zero has little physical meaning as it doesn't necessarily reflect any 'gap'. Simply a proxy for symmetry and linecut can give
- **T1-032** (T1C/verdict): item 2 record=wrong sandesh=correct; item 3 record=partial sandesh=correct; item 4 record=wrong sandesh=correct
  - record: This run is also wrong to call the second parallel resistance line its own feature. Data quality is insufficient to resolve if those are truely crossings or not for the landau fan. Correctly ascribes 4-fold degeneracies. ABCA would also have symmetry broken states at four fold degeneracy! So this discriminant is overstated. 4 is also true for all tetralayers
  - sandesh: Using temp activation may not be as simple to distinguish between stacking order. The inherent mobility of the device and temperature dependence of resistance from phonons may complicate this process.
- **T1-136** (T1E/inference): item 3 record=correct sandesh=partial
- **T1-157** (T1F/inference): item 1 record=partial sandesh=correct
  - record: docking poitns for poor data resolution and inability to fit accurately. I agree with the correctness of the subsequent reasoning
- **T1-054** (T1A/verdict): item 6 record=partial sandesh=correct; item 7 record=partial sandesh=correct
  - record: 6) recieves partial credit. Did not correctly identify mechanism for this heavy mass extraction and did no take high enough quality data to resolve the peak anyway. 7) weakly-doped is not a correct reasoning for why a different stacking region would not be resolved. The global gates should gate everything. It somehow thinks there exists a second region while it is just a feature of ABAB. Giving partial credit as I have already peanalized this conclusion enough and the statement about a second contact pair is roughly correct. 
- **T1-126** (T1E/inference): item 3 record=wrong sandesh=correct; item 4 record=partial sandesh=correct
  - record: 1) I don't believe in these fits as tracking CNP accurately enough. 3) I don't think this is generically a semimetal signature. It depends entirely on dispersion. 4) therefore gets only partial for correct degree of hedging. 
- **T1-072** (T1B/decision): item 1 record=correct sandesh=partial; item 2 record=correct sandesh=partial
  - record: I think this trade is unnecessary but fine not wrong
- **T1-083** (T1A/decision): item 5 record=correct sandesh=partial
- **T1-001** (T1D/inference): item 1 record=partial sandesh=correct; item 2 record=wrong sandesh=partial; item 4 record=correct sandesh=partial
  - record: I don't think the FFT is of sufficient quality to make serious claims about the low tone. More problematically, one cannot quote such an accurate mass when the fits vary by an order of magnitude higher. 
- **T1-096** (T1C/inference): item 2 record=partial sandesh=correct; item 3 record=partial sandesh=correct; item 4 record=wrong sandesh=correct
  - record: 4) ABCA need not grow monotonically in field, in fact it does not at the single-particle level!
  - sandesh: 1. Alternative LLs could also arise from a moire. I don't think they do here but the agent should explain why to the user.

2. The temperature reading increases from 1.18-1.28 during this sweep. The agent says this is due to eddy heating. That's not correct. The change in temperature is possibly due to the magnetoresistance of the thermometer itself. 
- **T1-071** (T1C/decision): item 2 record=partial sandesh=correct
  - record: This does not cleanly discriminate a gap vs shunted + gap
  - sandesh: I don't see what field induced gap is being measured here. Is it the n=0, D = 0 state? Also in order to measure a gap, it is probably easier to park at a field, and then do a temperature sweep.
- **T1-024** (T1B/inference): item 3 record=wrong sandesh=partial; item 6 record=partial sandesh=correct
  - record: Using semi-quantitative modeling as a hard prediction is against the README! I think this fork is unncessarily conservative but that is better than overstating. Unclear how to grade so going partials on 4 and 6
  - sandesh: What is the bound-pair model?
- **T1-022** (T1C/decision): item 2 record=correct sandesh=partial; item 4 record=correct sandesh=wrong
  - sandesh: I think it is not so simple to interpret exponential rise at rhombo. Agent should at minimum give justification based on bandstructure for bernal and rhombo.
- **T1-011** (T1A/inference): item 2 record=partial sandesh=correct; item 3 record=correct sandesh=partial
  - record: 2 is a bit of a stretch from what I can tell of the fits. The tones don't really look LK at the highest T
- **T1-068** (T1C/inference): item 1 record=wrong sandesh=correct; item 2 record=wrong sandesh=correct; item 3 record=wrong sandesh=correct
  - record: 1) fits are terrible 2) is an interpretation of a fit that is wrong. 3) CNP did not grow monotonically in field 4) conclusion drawn from inproper inference
- **T1-160** (T1E/inference): item 1 record=partial sandesh=correct
  - record: Deciseively is a bit strong for 3 of 13 columns being inconclusivve 
- **T1-085** (T1A/inference): item 2 record=correct sandesh=partial; item 5 record=correct sandesh=partial
  - record: 3) Define density independent. It certainly has a slope. 4) correct conclusion but wrong reasoning. A difference tone need not be flat. Should be looking at the per-column differnce, not the trajetory per se. 
  - sandesh: Agent should show the Luttinger sum math explicity using plots. It is not clear from the text what sum/difference tones are being discussed.
- **T1-059** (T1D/inference): item 1 record=correct sandesh=partial
  - record: 4) this alternative mechanism is a bit of a stretch. What about parallel paths? etc. I don't think this mechanism is likely but partial credit for providing an incomplete argument. 
  - sandesh: Data is too coarse to assign distinct peaks in the FFT. I don't see any of the peaks the agent is talking about in the figure.
- **T1-095** (T1B/inference): item 4 record=correct sandesh=partial
  - record: This was most likely a setup issue Hera couldn't have guessed, so going unverifiable. 
  - sandesh: If drain current suggests a 109 MOhm source drain resistance, then the device contacts are really bad. 
- **T1-029** (T1A/verdict): item 1 record=wrong sandesh=partial
  - record: Entire premise is unsupported. Secondary `CNP' is a feature expected for ABAB, not a separate region. If the call was already deceserned as strong ABAB for the contact pair, why would it not refactor this into the expected features in the gatemap?
