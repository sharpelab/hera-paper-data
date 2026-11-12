<!-- Aaron's + Zack's live session notes from the lab wiki (Outline).
     Source: https://wiki.sharpelab.science/doc/20260625-zf1-O4kv8TQskS
     Captured 2026-06-25. The tactical chat transcript DID persist this time
     (nested-launch fix) — see transcripts/24fe0462-…jsonl. These notes are the
     operator-facing critiques to feed into triage. -->

# Notes

* AS: we like the tables
  * zg: hera-session
* zack: temp freshness check is good but should be tooled into the template
  probe setup cell, hera can read the output
* zack: first turn non-autonomy prompt is likely due to gate-current-sanity-check
  recipe requiring the operator — verify and fix
  * AS: reduce number of points in this recipe by a bit (maybe down to just 150)
* zack: time has big offset in .plots(), should be relative to the start of the sweep
* AS: The ana notebook should have more timestamping
