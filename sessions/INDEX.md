# Sessions

Model and corpus commit per session. Model = the `model` field of the assistant entries in the measurement agent's transcript (all values seen, most frequent first; `<synthetic>` entries are harness messages; the transcript field drops the `[1m]` context suffix). Transcripts = number of the session's own jsonl files, plus the `hera-session` setup agent's jsonl where it was archived alongside (told apart by the `cwd` of the entries: the setup agent runs from the shared `measurement_env` checkout). 0 means the measurement agent's transcript was lost; what survives instead is listed in the archive's `transcripts/recovered/README.md` and in metrics/runs.yaml caveats.

| device | session | model | transcripts | corpus commit |
|---|---|---|---|---|
| qc0426 | 2026-06-10-QC0426-session | claude-fable-5 (464) | 1 | `d197ec7` |
| qc0426 | 2026-06-14-QC0426-session | claude-opus-4-8 (568) | 1 | `78afaf6` |
| qc0426 | 2026-06-16-QC0426-session | claude-opus-4-8 (902) | 1 | `5a18746` |
| qc0426 | 2026-06-17-QC0426-session | claude-opus-4-8 (425) | 1 | `6a3fa74` |
| qc0426 | 2026-06-19-QC0426-session | claude-opus-4-8 (544) | 1 (+1 setup) | `9f72450` |
| qc0426 | 2026-06-19-QC0426-session-2 | claude-opus-4-8 (152) | 1 | `219de29` |
| qc0426 | 2026-06-19-QC0426-session-3 | claude-opus-4-8 (504) | 1 (+3 setup) | `425bc8d` |
| qc0426 | 2026-06-20-QC0426-session | claude-opus-4-8 (434) | 1 | `6c810ff` |
| qc0426 | 2026-06-21-QC0426-session | claude-opus-4-8 (515) | 1 | `c54361c` |
| qc0426 | 2026-06-21-QC0426-session-2 | claude-opus-4-8 (544) | 1 | `870c29d` |
| qc0426 | 2026-07-14-QC0426-session | claude-fable-5 (225) | 1 | `3b4ff05` |
| qc0426 | 2026-07-14-QC0426-session-2-full | claude-fable-5 (517) | 1 | `64b0d1b` |
| qc0426 | 2026-07-16-QC0426-session-3 | claude-fable-5 (432) | 1 | `97402c3` |
| qc0426 | 2026-07-17-QC0426-capstone-2 | claude-fable-5 (437) | 1 | `17bc077` |
| qc0426 | 2026-07-17-QC0426-raman-fusion | — | 0 | `fe7525a` |
| qc0426 | 2026-07-18-QC0426-session-full | claude-fable-5 (474) | 1 | `ad78aaf` |
| qc0426 | 2026-07-25-QC0426-prefab-raman | — | 0 | `a8bc119` |
| zf1 | 2026-06-20-zf1-session | claude-opus-4-8 (529) | 1 | `d3b7885` |
| zf1 | 2026-06-21-zf1-session | claude-opus-4-8 (474) | 1 | `12fa296` |
| zf1 | 2026-06-22-zf1-session | claude-opus-4-8 (418) | 1 | `f1fc725` |
| zf1 | 2026-06-23-zf1-session-full | — (lost; setup agent claude-opus-4-8 (51)) | 0 (+2 setup) | `84857f8` |
| zf1 | 2026-06-24-zf1-session | — (lost; setup agent claude-opus-4-8 (90)) | 0 (+1 setup) | `256ccd5` |
| zf1 | 2026-06-25-zf1-reference-session | — | 0 | `f87396c` |
| zf1 | 2026-06-25-zf1-session | claude-opus-4-8 (388) | 1 | `591da57` |
| vti-01 | 2026-08-18-vti-01-session | claude-fable-5 (535) | 1 | `d8e1337` |
| vti-02 | 2026-08-21-vti-02-session | claude-fable-5 (358) | 1 | `13b07e9` |
| vti-02 | 2026-08-22-vti-02-session | claude-fable-5 (486) | 1 (+1 setup) | `13b07e9` |
| vti-02 | 2026-08-23-vti-02-session | claude-fable-5 (296) | 1 | `039b0f5` |
| vti-02 | 2026-08-24-vti-02-session | claude-opus-5 (464) | 1 | `039b0f5` |
| vti-02 | 2026-08-25-vti-02-session | claude-opus-5 (600) | 1 | `13b07e9` |
