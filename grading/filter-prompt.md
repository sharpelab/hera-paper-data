# Post-extraction filter pass (v1, 2026-08-26). Model: Sonnet 5. Fill {KEY}, {ARCHIVE}.

Read /home/aaron/work/projects/hera/quality/raw/{KEY}.claims.jsonl (one claim per line). Archive for reference: {ARCHIVE} (corpus recipes the agent followed are referenced in *_measure.ipynb markdown; the recipe slug is data/<id>/metadata.json comments[0]).

Produce two JSON files:
1. /home/aaron/work/projects/hera/quality/raw/{KEY}.exclude.json — {claim_id: reason} for claims to DROP from scoring:
   - "recipe-default": a `decision` where the agent simply executed the corpus recipe's default (drive, ranges, step, order as written). Keep decisions where the agent chose among alternatives, departed from the recipe, or the recipe left it open. If unsure whether a value is the recipe default, check the recipe text referenced in the measure notebook; if still unsure, KEEP (do not exclude).
   - "column-repeat": a per-column / per-row / per-temperature restatement ("column k: tones at f1,f2") whose content is subsumed by a synthesis claim. Name the synthesis claim id in the reason string, e.g. "column-repeat -> {KEY}-041".
2. /home/aaron/work/projects/hera/quality/raw/{KEY}.merges.json — {source_id: target_id} for claims to FOLD into another card as supporting context:
   - a "fork"/"open question" claim → the later claim that resolves it (score on the resolution; fork appears as context);
   - near-duplicate inferences (same content restated) → the later/stronger statement.
   Sources must not themselves be targets. Never merge across types except fork(inference)→resolution(inference/verdict).

Do not edit the claims file. Return only: counts excluded by reason, count merged, and any claim ids where you were unsure.
