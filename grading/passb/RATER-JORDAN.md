# Pass B — second rater: Jordan

Rater: Jordan. Scope: the 5 non-vti-01 tier-1 runs, in the order
**T1A → T1E → T1D → T1F → T1C**
(`random.Random(20260831).shuffle(['T1A','T1C','T1D','T1E','T1F'])` — seeded
fresh per rater so learning curves don't correlate across raters). Practice
run first: **CAL2** (already burned for calibration; its export is shakedown
data, not a score). All work happens on branch **`rater/jordan`**, cut from
the tag `passb-locked` — Aaron is grading the same instrument in parallel on
main, and the branch guarantees his rulings never enter your working tree.

## For Jordan

You're the second rater on HERA's expert-judgment pass. Each page is one
measurement session — the notebooks, data, and figures from a run — and you
grade it the way you'd read a collaborator's work before a group meeting:
skim and give a first impression, then a full read ruling each section
sound / shaky / wrong / n-a, then a short debrief. Budget roughly an hour
per run; six pages total including practice.

The flow: your Claude sets up the repo, then you open `CAL2.html` in a
browser and do the whole thing once as practice. **If it all made sense,
just continue to the real runs.** If anything was confusing — a question
type, what a ruling should mean, how a page behaves — send it to Zack and
wait for an answer first: five runs graded under a misunderstanding is a lot
of your time wasted, and CAL2 is the free place to catch it.

Ground rules: answer the "what do you already know about this run" question
honestly (the page asks; nothing is assumed, and knowing things is fine —
it just gets logged). Don't discuss the runs or your rulings with Aaron or
anyone else grading until both passes are frozen. Try to do each run in one
sitting, and hit **Export** when you finish a page — export is the real
save; the in-browser autosave is a convenience, not a record.

## For Jordan's Claude

You are logistics only. **You do not open the dossier pages' content, do not
summarize or characterize the runs, and do not offer any opinion that could
bear on a ruling** — an assisted rating is a different instrument than the
pre-declared one, and one hint contaminates the pass. You handle git, files,
and process questions; grading is Jordan's alone.

### Setup

```bash
git clone git@github.com:sharpelab/hera-quality.git
cd hera-quality
git checkout -b rater/jordan passb-locked
```

Branch from the **tag**, not main. This doc lives on main, so it won't
be on your branch after checkout — read it in full right after cloning
(it is the only main file you may touch), or keep the copy Zack sent.
Never pull, merge, or rebase main
onto this branch, and never fetch-and-inspect it: main accumulates Aaron's
exports while he grades.

Do-not-read list (applies to you for the life of this task, even if files
appear unexpectedly): `passb/*.passb.json` (any rater's), `scores/`,
`calibration-notes.md`, `blind-map.yaml`, `PREREG.md` commentary beyond what
Jordan asks about, and anything under `raw/` or `cards/`. The only files you
touch are the ones named below.

Do not run `hera_passb.py`, regenerate any page, or edit any `.html` — the
graded pages must be byte-identical to the `passb-locked` commit. If a page
seems broken, stop and message Zack; never patch around it.

### Per-run loop

1. Open `passb/<key>.html` from `file://` for Jordan — same browser every
   time (autosave lives in that browser's localStorage under
   `hera-passb-<key>`; switching browsers or moving the repo path can orphan
   it). Keyboard on the grading widgets: `1`/`2`/`3`/`4` =
   sound/shaky/wrong/n-a, `j`/`k` move, `n` note.
2. Jordan grades and hits **Export** → the page saves `<key>.passb.json`.
3. Move it into the repo renamed with the rater suffix:
   `passb/<key>.jordan.passb.json`. The suffix is load-bearing — the ingest
   script keys on bare `<key>.passb.json` and a collision would clobber
   Aaron's row at analysis time.
4. One commit per run, then push:

   ```bash
   git add passb/<key>.jordan.passb.json
   git commit -m "[passb][jordan] <key> export"
   git push -u origin rater/jordan
   ```

   Push after every run — the pushed commits are the timestamp trail.

Order: **CAL2** (practice), then **T1A → T1E → T1D → T1F → T1C**. Commit
the CAL2 export too (`passb/CAL2.jordan.passb.json`) — it's shakedown data,
still worth keeping.

### The CAL2 checkpoint

After CAL2: if Jordan says the instrument made sense, proceed straight into
T1A. If he has questions or concerns of any kind, collect them and send to
Zack on Slack, and **do not open a T1 page until
they're resolved** — the point of practice is to spend confusion on the
burned run, not on the five that count.

### If something goes wrong

Page bug, ruling that won't save, an export that looks malformed, accidental
exposure to Aaron's rulings or anything on the do-not-read list, git
conflict — stop, write down exactly what happened, message Zack. Don't
improvise a fix. If the browser loses in-progress state, the Import button
on the page restores from the most recent export.

When all five T1 exports are committed and pushed, message Zack; merging
into main and ingest happen on his side after both raters are frozen.
