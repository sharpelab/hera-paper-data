# Corpus commit per session

The frozen tree in measurement-env/ is `13b07e9898b973aa34066587c27ac61db13c26cc`. Each patch in this directory turns that tree into the corpus a session actually ran on (apply with `git apply` or `patch -p1` from inside measurement-env/). Patches exclude session archives, third-party PDFs and the replay fixture tree (hera/test-cases).

Sessions from 2026-07-17 onward stamp their corpus commit in `corpus_provenance.json`. Earlier sessions did not; for those the commit is the last commit on the `hera` branch before the session transcript's first timestamp, which is the best available reconstruction of what the rig checkout could have been, not a record of what it was.

| session | corpus commit | stamped? | patch |
|---|---|---|---|
| 2026-06-10-QC0426-session | `d197ec7` | no (inferred from transcript start 2026-06-10T23:34:05.543Z) | corpus-d197ec7.patch |
| 2026-06-14-QC0426-session | `78afaf6` | no (inferred from transcript start 2026-06-15T03:42:42.150Z) | corpus-78afaf6.patch |
| 2026-06-16-QC0426-session | `5a18746` | no (inferred from transcript start 2026-06-16T09:37:40.769Z) | corpus-5a18746.patch |
| 2026-06-17-QC0426-session | `6a3fa74` | no (inferred from transcript start 2026-06-17T20:22:53.525Z) | corpus-6a3fa74.patch |
| 2026-06-19-QC0426-session | `9f72450` | no (inferred from transcript start 2026-06-19T03:05:47.076Z) | corpus-9f72450.patch |
| 2026-06-19-QC0426-session-2 | `219de29` | no (inferred from transcript start 2026-06-20T02:37:55.328Z) | corpus-219de29.patch |
| 2026-06-19-QC0426-session-3 | `425bc8d` | no (inferred from transcript start 2026-06-20T03:29:36.322Z) | corpus-425bc8d.patch |
| 2026-06-20-QC0426-session | `6c810ff` | no (inferred from transcript start 2026-06-21T03:38:56.766Z) | corpus-6c810ff.patch |
| 2026-06-21-QC0426-session | `c54361c` | no (inferred from transcript start 2026-06-21T10:53:46.433Z) | corpus-c54361c.patch |
| 2026-06-21-QC0426-session-2 | `870c29d` | no (inferred from transcript start 2026-06-22T05:45:44.548Z) | corpus-870c29d.patch |
| 2026-07-14-QC0426-session | `3b4ff05` | no (inferred from transcript start 2026-07-14T20:14:04.852Z) | corpus-3b4ff05.patch |
| 2026-07-14-QC0426-session-2-full | `64b0d1b` | no (inferred from transcript start 2026-07-15T03:31:07.300Z) | corpus-64b0d1b.patch |
| 2026-07-16-QC0426-session-3 | `97402c3` | no (inferred from transcript start 2026-07-16T20:18:34.138Z) | corpus-97402c3.patch |
| 2026-07-17-QC0426-capstone-2 | `17bc077` | yes | corpus-17bc077.patch |
| 2026-07-17-QC0426-raman-fusion | `fe7525a` | no (no transcript; inferred from the archive date, noon PDT) | corpus-fe7525a.patch |
| 2026-07-18-QC0426-session-full | `ad78aaf` | yes | corpus-ad78aaf.patch |
| 2026-07-25-QC0426-prefab-raman | `a8bc119` | no (no transcript; inferred from the archive date, noon PDT) | corpus-a8bc119.patch |
| 2026-06-20-zf1-session | `d3b7885` | no (inferred from transcript start 2026-06-20T20:55:19.434Z) | corpus-d3b7885.patch |
| 2026-06-21-zf1-session | `12fa296` | no (inferred from transcript start 2026-06-21T21:07:33.841Z) | corpus-12fa296.patch |
| 2026-06-22-zf1-session | `f1fc725` | no (inferred from transcript start 2026-06-22T23:43:45.981Z) | corpus-f1fc725.patch |
| 2026-06-23-zf1-session-full | `84857f8` | no (inferred from transcript start 2026-06-23T22:12:15.880Z) | corpus-84857f8.patch |
| 2026-06-24-zf1-session | `256ccd5` | no (inferred from transcript start 2026-06-24T22:41:34.148Z) | corpus-256ccd5.patch |
| 2026-06-25-zf1-session | `591da57` | no (inferred from transcript start 2026-06-25T05:39:03.537Z) | corpus-591da57.patch |
| 2026-06-25-zf1-reference-session | `f87396c` | no (no transcript; inferred from the archive date, noon PDT) | corpus-f87396c.patch |
| 2026-08-18-vti-01-session | `d8e1337` | yes | corpus-d8e1337.patch |
| 2026-08-21-vti-02-session | `13b07e9` | yes | (frozen tree) |
| 2026-08-22-vti-02-session | `13b07e9` | yes | (frozen tree) |
| 2026-08-23-vti-02-session | `039b0f5` | yes | corpus-039b0f5.patch |
| 2026-08-24-vti-02-session | `039b0f5` | yes | corpus-039b0f5.patch |
| 2026-08-25-vti-02-session | `13b07e9` | yes | (frozen tree) |
