"""hera-replay — cut a frontier out of an archived HERA session and replay it.

`inspect` lists the tactical transcript, `cut` materializes the episode dir,
`run` starts N copies of a case's episode in containers, `summarize` tabulates a
run dir, `grade` runs the case's grader over a run's episodes. `run` and `grade` are
foreground jobs; `submit` starts one detached (`wait`, `status`, `cancel`, `reap`
manage them); `cell` pools a case's run dirs; `quota` reports the plan windows.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from hera.replay import cell, jobs, quota
from hera.replay.archive import open_archive
from hera.replay.case import EFFORTS, load_case
from hera.replay.container import DockerError
from hera.replay.derive import derive
from hera.replay.errors import CutError
from hera.replay.grade import grade_run, render as render_grades
from hera.replay.inspect_cmd import render
from hera.replay.mask import load_mask
from hera.replay.materialize import materialize
from hera.replay.rewrite import Corpus
from hera.replay.run import hera_data_root, run_case
from hera.replay.summarize import render as render_summary, write_summary


def hera_data() -> Path:
    return hera_data_root()


def cmd_inspect(args: argparse.Namespace) -> int:
    archive = open_archive(Path(args.archive))
    print(render(archive, grep=args.grep, around=args.around, context=args.context))
    return 0


def cmd_cut(args: argparse.Namespace) -> int:
    source, at, close, corpus, stage, mask = Path(args.archive or "."), args.at, args.close, None, True, None
    if args.case:
        case = load_case(Path(args.case))
        if case.source is None:
            raise CutError(f"{case.path.name}: the case names no archive, so there is no cut to make")
        source, at = case.source, case.cut_at
        close = args.close or case.resume_close
        stage = case.start == "resume"
        corpus = Corpus(case.corpus_sha, case.condition) if case.read_source == "corpus" else None
        mask = load_mask(case.mask_path) if case.mask_path else None
    elif not (args.archive and args.at):
        raise CutError("cut takes an archive and --at, or --case")
    archive = open_archive(source)
    d = derive(archive, at)
    dest = Path(args.dest) if args.dest else hera_data() / "replay" / "cuts" / archive.root.name / at[:8]
    episode = materialize(archive, d, dest, close=close, corpus=corpus, stage_transcript=stage, mask=mask)
    print(f"episode: {dest}")
    print(f"cut:     line {episode['cut']['index']} {episode['cut']['uuid']} {episode['cut']['timestamp']} ({episode['cut']['tool']} result)")
    for name, nb in episode["notebooks"].items():
        cell = nb["cut_cell"]
        where = f"cell {cell['id']} @ {cell['index']}" if cell else "no agent cell"
        print(f"notebook: {name}: {nb['cells_kept']}/{nb['cells_total']} cells, cut at {where}, {nb['code_cells_renumbered']} code cells renumbered")
    runs = episode["runs"]
    inferred = runs.get("end_from_mtime") or {}
    print(f"runs:    kept {runs['kept']}, in flight {[r['id'] for r in runs['in_flight_dropped']]}, unobserved {runs['unobserved']}"
          + (f", end from mtime {[int(k) for k in inferred]}" if inferred else ""))
    if episode.get("mask"):
        print(f"mask:    dropped {episode['mask']['dropped']}, edited {[e['target'] for e in episode['mask']['edits']]}")
        if episode["mask"]["appended"]:
            cells = ", ".join(f"{a['notebook']}#{a['id']} ({a['cell_type']} @ {a['index']})" for a in episode["mask"]["appended"])
            print(f"append:  {cells}; clock starts {episode['clock']['start']} ({episode['clock']['after_cut_s']} s after the cut)")
    files = episode["files"]["reconstructed"]
    print(f"files:   as archived {episode['files']['as_archived']}; reconstructed {len([f for f in files if 'not_materialized' not in files[f]])}; "
          f"not materialized {len(episode['not_materialized'])}")
    if not stage:
        print(f"start:   fresh — no transcript staged  (cwd {episode['container']['session_dir']})")
        return 0
    rw = episode["transcript"]["rewrites"]
    print(f"paths:   session dir {rw['session_dir']} (+{rw['tilde_session_dir']} tilde), measurement_env {rw['measurement_env']}, other home {rw['home_other']}")
    cr = episode["transcript"]["corpus_reads"]
    if cr["mode"] == "corpus":
        print(f"corpus:  reads at {cr['sha']} ({cr['condition']}): {len(cr['rewritten'])} substituted "
              f"({sum(r['identical'] for r in cr['rewritten'])} identical), {len(cr['unrewritten'])} left archived")
        for r in cr["rewritten"]:
            state = "identical" if r["identical"] else "missing at the sha" if r.get("missing_at_sha") else "substituted"
            print(f"         line {r['line']:5d} {r['tool']:4} {r['path']}  {state}")
        for r in cr["unrewritten"]:
            print(f"         line {r['line']:5d} {r['tool']:4} {', '.join(r['paths'])}  archived: {r['reason']}")
    print(f"resume:  {episode['container']['transcript']}  (cwd {episode['container']['session_dir']})")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    case = load_case(Path(args.case))
    run_dir = run_case(case, n=args.n, parallel=args.parallel, model=args.model, effort=args.effort,
                       hera_data=hera_data())
    print()
    if (run_dir / "summary.csv").exists():
        print(render_summary(run_dir))
    print(f"run dir: {run_dir}")
    return 130 if json.loads((run_dir / "run.json").read_text(encoding="utf-8"))["interrupted"] else 0


def cmd_summarize(args: argparse.Namespace) -> int:
    write_summary(Path(args.run_dir))
    print(render_summary(Path(args.run_dir)))
    return 0


def cmd_grade(args: argparse.Namespace) -> int:
    records = grade_run(Path(args.run_dir), n=args.n, parallel=args.parallel, grader=args.grader,
                        regrade=args.regrade, model=args.model, effort=args.effort)
    print(render_grades(records))
    print(f"table: {Path(args.run_dir) / 'grades.csv'}")
    return 0


def cmd_submit(args: argparse.Namespace) -> int:
    cwd = Path.cwd()
    if args.grade:
        if args.target:
            raise CutError("submit takes a spec, a case, or --grade run dirs; not a target and --grade")
        items = [{"grade": d, "grader": args.grader, "n": args.n, "regrade": args.regrade or None,
                  "parallel": args.parallel, "model": args.model or jobs.GRADE_DEFAULTS["model"],
                  "effort": args.effort or jobs.GRADE_DEFAULTS["effort"]} for d in args.grade]
        spec, base = {"label": args.label, "items": items}, cwd
    elif args.target and _is_case(Path(args.target)):
        spec = {"label": args.label, "items": [{"case": args.target, "n": args.n, "parallel": args.parallel,
                                                 "model": args.model, "effort": args.effort}]}
        base = cwd
    elif args.target:
        if any(v is not None for v in (args.n, args.model, args.effort, args.grader)):
            raise CutError("--n/--model/--effort/--grader go in the spec's items")
        spec, base = jobs.load_spec_file(Path(args.target)), cwd
        if args.label:
            spec["label"] = args.label
        if args.parallel is not None:
            spec["parallel"] = args.parallel
    else:
        raise CutError("submit takes a spec yaml, a case yaml, or --grade <run-dir>...")
    job_id = jobs.submit(spec, base=base)
    print(job_id)
    print(f"wait: hera-replay wait {job_id}", file=sys.stderr)
    return 0


def _is_case(path: Path) -> bool:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return isinstance(data, dict) and "items" not in data


def cmd_wait(args: argparse.Namespace) -> int:
    try:
        return jobs.wait(args.job)
    except KeyboardInterrupt:
        print(f"\nstopped waiting; job {args.job} goes on (hera-replay cancel {args.job} stops it)")
        return 130


def cmd_status(args: argparse.Namespace) -> int:
    print(jobs.status_text(args.job))
    return 0


def cmd_cancel(args: argparse.Namespace) -> int:
    print(jobs.cancel(args.job))
    return 0


def cmd_reap(args: argparse.Namespace) -> int:
    print("\n".join(jobs.reap()))
    return 0


def cmd_job(args: argparse.Namespace) -> int:
    return jobs.run_detached(args.job)


def cmd_cell(args: argparse.Namespace) -> int:
    target = Path(args.case)
    name = load_case(target).name if target.suffix in (".yaml", ".yml") else args.case
    print(cell.render(hera_data(), name))
    return 0


def cmd_quota(args: argparse.Namespace) -> int:
    print(quota.report(jobs.quota_log_path()))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hera-replay", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    ip = sub.add_parser("inspect", help="list the tactical transcript to pick a cut")
    ip.add_argument("archive")
    ip.add_argument("--grep", help="show only rows matching this regex (case-insensitive)")
    ip.add_argument("--around", type=int, help="show only rows within --context lines of this index")
    ip.add_argument("--context", type=int, default=10)
    ip.set_defaults(func=cmd_inspect)

    cp = sub.add_parser("cut", help="materialize the episode dir at a cut")
    cp.add_argument("archive", nargs="?", help="session archive (a --case gives its own)")
    cp.add_argument("--case", help="case yaml: its source, cut, corpus and start (resume.close, or fresh)")
    cp.add_argument("--at", help="uuid of the tool_result entry to cut after")
    cp.add_argument("--dest", help="episode dir (default $HERA_DATA/replay/cuts/<archive>/<uuid8>)")
    cp.add_argument("--close", help="synthetic assistant line closing the cut turn (a run takes it from the case file)")
    cp.set_defaults(func=cmd_cut)

    rp = sub.add_parser("run", help="start N copies of a case's episode in containers")
    rp.add_argument("case", help="case yaml")
    rp.add_argument("--n", type=int, help="episodes (default: the case's run.n)")
    rp.add_argument("--parallel", type=int, default=1, help="containers at once (default 1)")
    rp.add_argument("--model", help="override the case's run.model")
    rp.add_argument("--effort", choices=EFFORTS, help="override the case's run.effort")
    rp.set_defaults(func=cmd_run)

    sp = sub.add_parser("summarize", help="tabulate a run dir (rewrites its summary.csv)")
    sp.add_argument("run_dir")
    sp.set_defaults(func=cmd_summarize)

    gp = sub.add_parser("grade", help="grade a run's finished episodes with the case's grader")
    gp.add_argument("run_dir")
    gp.add_argument("--n", type=int, default=1, help="extractions per episode (default 1)")
    gp.add_argument("--parallel", type=int, default=4, help="containers at once (default 4)")
    gp.add_argument("--grader", help="override the case's grader")
    gp.add_argument("--regrade", action="store_true", help="grade episodes that already have a grade from this grader too")
    gp.add_argument("--model", default="claude-opus-5")
    gp.add_argument("--effort", default="medium")
    gp.set_defaults(func=cmd_grade)

    jp = sub.add_parser("submit", help="start a detached job: a spec yaml, a case yaml (--n), or --grade run dirs; prints its id")
    jp.add_argument("target", nargs="?", help="spec yaml (items: case/grade) or case yaml")
    jp.add_argument("--grade", nargs="+", metavar="RUN_DIR", help="one grade item per run dir")
    jp.add_argument("--label", help="who/what, shown in status")
    jp.add_argument("--n", type=int, help="episodes (a case) or extractions per episode (--grade)")
    jp.add_argument("--parallel", type=int, help="this job's cap (default: the pools alone)")
    jp.add_argument("--model", help="override the case's run.model, or the extraction model")
    jp.add_argument("--effort", choices=EFFORTS, help="override the case's run.effort, or the extraction effort")
    jp.add_argument("--grader", help="override the case's grader (--grade)")
    jp.add_argument("--regrade", action="store_true", help="--grade: repeat episodes already graded")
    jp.set_defaults(func=cmd_submit)

    wp = sub.add_parser("wait", help="stream a job's log until it ends; exit 0 done, 130 interrupted, 1 otherwise")
    wp.add_argument("job")
    wp.set_defaults(func=cmd_wait)

    stp = sub.add_parser("status", help="pools, live and recent jobs, orphans; or one job's items")
    stp.add_argument("job", nargs="?")
    stp.set_defaults(func=cmd_status)

    kp = sub.add_parser("cancel", help="SIGTERM a job: in-flight items interrupted, queued ones cancelled")
    kp.add_argument("job")
    kp.set_defaults(func=cmd_cancel)

    ap = sub.add_parser("reap", help="stop and remove containers no live job lists; record dead jobs")
    ap.set_defaults(func=cmd_reap)

    lp = sub.add_parser("cell", help="pool a case's run dirs by case, image, first message and cut")
    lp.add_argument("case", help="case yaml or case name")
    lp.set_defaults(func=cmd_cell)

    qp = sub.add_parser("quota", help="latest plan-window readings per runner and the measured burn rate")
    qp.set_defaults(func=cmd_quota)

    xp = sub.add_parser("_job")  # the detached job process `submit` starts
    xp.add_argument("job")
    xp.set_defaults(func=cmd_job)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (CutError, DockerError) as err:
        sys.exit(f"hera-replay {args.command}: {err}")


if __name__ == "__main__":
    sys.exit(main())
