# Pass A — second rater: Sandesh

Rater: Sandesh. Scope: a fixed subset of the tier-1 claim pool — **56 cards /
212 items** (every verdict card, plus 30 % of the inference and decision cards
from each of the six August VTI sessions; `manifest.json` has the ids and the
seed). Aaron scored the full pool of 151 cards / 561 items in about 8 h; this
subset is sized for about **3 h**, in sittings. It exists to put an
inter-rater agreement number beside his scores. What gets computed from it
was fixed before you saw a card (`PREREG.md`, "Second rater, Pass A subset").

All work happens on branch **`rater/sandesh`**, cut from the tag
`passa-sandesh-locked`. Aaron's scores live on main; the branch keeps them
out of your working tree.

## For Sandesh

**What we want from you is a physics grade.** Each card is one claim an
autonomous agent made, or one sweep it chose, during a cryostat measurement
session on a multilayer graphene device — with the context it had, the
evidence it cited, its own words verbatim, and the figures it was looking
at. The six sessions are pooled and shuffled; device names, dates, and
session ids are removed. Judge whether the physics holds: is the FFT tone
real, is the mass plausible, does the fit support the number, is this the
sweep an expert would run next. Not whether it reads well.

The standard is printed at the top of the page and it is the whole rubric:
*is this what a careful expert would conclude, or the choice a careful
expert would make, from what the agent had at that moment?* Each card is
broken into numbered items; score every item **correct / partial / wrong /
unverifiable**. Partial means defensible with a qualm — put the qualm in the
note. Unverifiable means the card does not give you enough to judge; it is
excluded, not a penalty. Hedged claims are scored at the strength stated.
Fitted numbers are wrong when the fit does not support quoting a value at
all, whatever the error bar; partial when the value is fine but the stated
precision is not.

Reading tips: the claim is a paraphrase, the verbatim block below it is the
agent's own wording and carries the exact hedge. If a card makes you want
data that is not on the card, that is usually unverifiable, not wrong. Do
not try to guess what Aaron would say; the point is an independent read.
Tick **recognized** if you can tell which device or session a card is from.

Flow: six practice cards first (`CAL2.sandesh.html`, ten minutes, from a
run outside the pool; whole-claim rather than itemized). If anything about
the page or a verdict is unclear after practice, ask Zack before opening the
real page. Then `T1.sandesh.html`: 56 cards, roughly an hour per sitting.
Progress autosaves in the browser you use, so keep to one browser. Click
**Export scores** whenever you stop and again when you finish; export is
the real save.

Two things to write down before the first card, in `knowledge.md` (your
Claude will make the file): what you already know about the August
sessions — which devices, whether you have seen any notebooks or heard the
stacking calls, whether you know which sessions used which model or corpus.
And one line on return attesting that the rulings are yours alone. Nothing
is assumed and knowing things is fine; it gets logged with the scores.
Please do not discuss the cards or your rulings with Aaron or Jordan until
Zack says the passes are frozen.

## For Sandesh's Claude

You are logistics only. **You do not open the card pages' content, do not
summarize or characterize any card or session, and do not offer any
opinion that could bear on a ruling** — an assisted rating is a different
instrument from the pre-registered one, and one hint contaminates the pass.
You handle git, files, the browser, and process questions. Grading is
Sandesh's alone.

### Setup

```bash
git clone git@github.com:sharpelab/hera-quality.git
cd hera-quality
git checkout -b rater/sandesh passa-sandesh-locked
```

Branch from the **tag**, not main. Never pull, merge, rebase, or inspect
main on this branch. Do-not-read list for the life of this task:
`scores/`, `passb/`, `dossiers/`, `cards/`, `raw/`, `calibration-notes.md`,
`blind-map.yaml`, and any `*.scores.json` or `*.passb.json` other than the
one Sandesh exports. The only files you touch are under `raters/sandesh/`.

Do not run `hera_subset.py`, regenerate any page, or edit any `.html` —
the graded page must be byte-identical to the tag. If a page seems broken,
stop and message Zack.

### Flow

1. Ask Sandesh the knowledge-state questions above; write his answer
   verbatim to `raters/sandesh/knowledge.md`; commit and push it **before
   he opens the real page**:

   ```bash
   git add raters/sandesh/knowledge.md
   git commit -m "[passa][sandesh] knowledge state"
   git push -u origin rater/sandesh
   ```

2. Open `raters/sandesh/CAL2.sandesh.html` from `file://` in his browser
   (practice). Then `raters/sandesh/T1.sandesh.html`, same browser every
   time (autosave is in that browser's localStorage under
   `hera-scores-T1.sandesh`).
3. Whenever he exports, move the download into the repo as
   `raters/sandesh/T1.sandesh.scores.json` (that exact name; it overwrites
   the previous export — each export is cumulative) and commit:

   ```bash
   git add raters/sandesh/T1.sandesh.scores.json
   git commit -m "[passa][sandesh] export (<n> of 56 cards)"
   git push
   ```

   The pushed commits are the timestamp trail; push after every sitting.
4. On the final export, append his attestation line to `knowledge.md`,
   commit both, push, and message Zack. Agreement is computed on Zack's
   side (`hera_agree.py`, fixed at the tag); nothing else is asked of you.

### If something goes wrong

Page bug, a ruling that will not save, a malformed export, accidental
exposure to anything on the do-not-read list, git conflict — stop, write
down exactly what happened, message Zack. Do not improvise a fix. If the
browser loses state, the most recent committed export can be re-imported by
pasting it into the page's localStorage key, but ask Zack first.
