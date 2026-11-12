#!/usr/bin/env python3
"""nb.py — navigate Jupyter notebooks without dragging multi-MB outputs into context.

Cell indices are 0-based (they match nb['cells'][i] in the raw JSON).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import struct
import sys
from pathlib import Path

# Collapse a run of this many (or more) consecutive identical rendered outputs
# into a single block. A sweep progress bar leaves one stored display_data
# output per update under the RTC notebook stack (thousands per cell); without
# this, `nb cells --outputs` dumps them all into the reader's context.
_COLLAPSE_RUN_MIN = 3


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _src_text(cell: dict) -> str:
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def _src_lines(cell: dict) -> list[str]:
    return _src_text(cell).splitlines()


def _str(v) -> str:
    return "".join(v) if isinstance(v, list) else (v or "")


def _data_size(mime: str, value) -> int:
    s = _str(value)
    if mime.startswith("image/") or mime == "application/pdf":
        try:
            return len(base64.b64decode(s.encode("ascii"), validate=False))
        except Exception:
            return len(s)
    return len(s)


def _output_size(out: dict) -> int:
    if "data" in out:
        return sum(_data_size(mt, v) for mt, v in out["data"].items())
    if "text" in out:
        return len(_str(out["text"]))
    return 0


def _png_dims(b64_data: str) -> tuple[int, int] | None:
    try:
        head = base64.b64decode(b64_data[:64].encode("ascii"), validate=False)
        if head[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        w, h = struct.unpack(">II", head[16:24])
        return w, h
    except Exception:
        return None


_ADD_COMMENT_RE = re.compile(r"""add_comment\(\s*(?:"([^"]*)"|'([^']*)')\s*\)""")
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)


def _truncate(s: str, n: int) -> str:
    return s[: n - 1] + "…" if len(s) > n else s


def _first_meaningful_line(text: str) -> str:
    """First non-blank line that isn't an import or '#' comment.
    Falls back to first non-blank line if filtering eats everything."""
    fallback = ""
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if not fallback:
            fallback = s
        if s.startswith("#"):
            continue
        if s.startswith("import "):
            continue
        if s.startswith("from ") and " import " in s:
            continue
        return s
    return fallback


def _preview(cell: dict, n: int = 80) -> str:
    text = _src_text(cell)
    if cell["cell_type"] == "code":
        comments = [(a or b).strip() for a, b in _ADD_COMMENT_RE.findall(text)]
        comments = [c for c in comments if c]
        if comments:
            return _truncate("; ".join(comments), n)
        return _truncate(_first_meaningful_line(text), n)
    for raw in text.splitlines():
        s = raw.strip()
        if s:
            return _truncate(s, n)
    return ""


def cmd_stats(nb: dict) -> None:
    cells = nb["cells"]
    by_type = {"code": 0, "markdown": 0, "raw": 0}
    empty: list[int] = []
    src_lines = 0
    out_bytes = 0
    cells_with_outputs = 0
    for i, c in enumerate(cells):
        by_type[c["cell_type"]] = by_type.get(c["cell_type"], 0) + 1
        text = _src_text(c)
        if not text.strip():
            empty.append(i)
        src_lines += len(text.splitlines())
        outs = c.get("outputs", [])
        if outs:
            cells_with_outputs += 1
            out_bytes += sum(_output_size(o) for o in outs)
    print(f"total cells: {len(cells)}")
    print(f"code: {by_type.get('code', 0)}  markdown: {by_type.get('markdown', 0)}  raw: {by_type.get('raw', 0)}")
    if empty:
        shown = empty[:20]
        suffix = ", …" if len(empty) > 20 else ""
        print(f"empty: {len(empty)} (indices: {', '.join(str(i) for i in shown)}{suffix})")
    else:
        print("empty: 0")
    print(f"source lines: {src_lines}")
    print(f"output bytes: {out_bytes}")
    print(f"cells with outputs: {cells_with_outputs}")


def cmd_summary(nb: dict, spec: str | None = None) -> None:
    cells = nb["cells"]
    if spec is not None:
        indices = parse_range(spec, len(cells))
        if not indices:
            print(f"(no cells in range; notebook has {len(cells)} cells)")
            return
    else:
        indices = list(range(len(cells)))
    w_idx = max(3, len(str(max(1, len(cells) - 1))))
    print(f"{'idx':>{w_idx}}  type  {'exec':>5}  {'src':>4}  {'out':>3}  {'bytes':>9}  preview")
    for i in indices:
        c = cells[i]
        kind = "md" if c["cell_type"] == "markdown" else "code" if c["cell_type"] == "code" else c["cell_type"][:4]
        if c["cell_type"] == "code":
            ec = c.get("execution_count")
            exec_s = f"[{ec}]" if ec is not None else "-"
        else:
            exec_s = ""
        outs = c.get("outputs", [])
        size = sum(_output_size(o) for o in outs)
        print(f"{i:>{w_idx}}  {kind:<4}  {exec_s:>5}  {len(_src_lines(c)):>4}  {len(outs):>3}  {size:>9}  {_preview(c)}")


def cmd_sections(nb: dict) -> None:
    header_re = re.compile(r"^(#{1,6})\s+(.*)$")
    any_found = False
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] != "markdown":
            continue
        for line in _src_lines(c):
            m = header_re.match(line)
            if m:
                level = len(m.group(1))
                indent = "  " * (level - 1)
                print(f"{indent}{m.group(1)} {m.group(2).strip()}  [cell {i}]")
                any_found = True
    if not any_found:
        print("(no markdown headers found)")


def parse_range(spec: str, n_cells: int) -> list[int]:
    """Parse `5`, `5-10`, `5,8,12`, `5-`, `5-10,12,15-` into a sorted unique list of valid indices."""
    if n_cells == 0:
        return []
    last = n_cells - 1
    out: list[int] = []
    seen: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo_s, hi_s = part.split("-", 1)
            lo = int(lo_s) if lo_s else 0
            hi = int(hi_s) if hi_s else last
        else:
            lo = hi = int(part)
        for i in range(max(0, lo), min(last, hi) + 1):
            if i not in seen:
                seen.add(i)
                out.append(i)
    return out


def _render_output(cell_idx: int, out_idx: int, out: dict) -> str:
    """Render one output to text (the body of `nb cells --outputs`).

    Returns the same text `_print_output` emits, so `cmd_cells` can compare
    consecutive renders and run-length-collapse identical ones (e.g. the
    thousands of `<IPython.core.display.HTML object>` placeholders a sweep
    progress bar leaves in the stored notebook — see `_COLLAPSE_RUN_MIN`).
    """
    otype = out.get("output_type", "?")
    if otype == "stream":
        text = out.get("text", "")
        if isinstance(text, list):
            text = "".join(text)
        name = out.get("name", "stream")
        return f"[stream:{name}]\n{text.rstrip(chr(10))}"
    if otype == "error":
        # Error outputs carry no `data` key — they hold ename/evalue plus a
        # traceback (list of strings, usually with ANSI color codes). Render
        # them so a raised exception is visible instead of "[error: no data]".
        ename = out.get("ename", "")
        evalue = out.get("evalue", "")
        header = ": ".join(p for p in (ename, evalue) if p) or "error"
        lines = [f"[error] {_strip_ansi(header)}"]
        tb = out.get("traceback") or []
        if isinstance(tb, str):
            tb = [tb]
        tb_text = "\n".join(tb)
        if tb_text.strip():
            lines.append(_strip_ansi(tb_text).rstrip("\n"))
        return "\n".join(lines)
    data = out.get("data", {})
    if not data:
        return f"[{otype}: no data]"
    # Prefer text/plain; otherwise show one placeholder per non-text mime.
    if "image/png" in data:
        b64 = data["image/png"]
        if isinstance(b64, list):
            b64 = "".join(b64)
        try:
            n_bytes = len(base64.b64decode(b64.encode("ascii"), validate=False))
        except Exception:
            n_bytes = len(b64)
        dims = _png_dims(b64)
        suffix = f"  {dims[0]}×{dims[1]}" if dims else ""
        return f"[image: cell {cell_idx} out {out_idx}  image/png  {n_bytes} bytes{suffix}]"
    if "text/plain" in data:
        t = data["text/plain"]
        if isinstance(t, list):
            t = "".join(t)
        return t.rstrip("\n")
    # Fallback: list mime types and sizes.
    parts = [f"{mt}={_data_size(mt, v)}B" for mt, v in data.items()]
    return f"[{otype}: {', '.join(parts)}]"


def _print_output(cell_idx: int, out_idx: int, out: dict) -> None:
    print(_render_output(cell_idx, out_idx, out))


def cmd_cells(nb: dict, spec: str, show_outputs: bool) -> None:
    cells = nb["cells"]
    indices = parse_range(spec, len(cells))
    if not indices:
        print(f"(no cells in range; notebook has {len(cells)} cells)")
        return
    for i in indices:
        c = cells[i]
        kind = c["cell_type"]
        sep = "=" * 60
        print(f"\n{sep}")
        print(f"cell {i}  [{kind}]")
        print(sep)
        src = _src_text(c).rstrip("\n")
        if kind == "code":
            print("```python")
            print(src)
            print("```")
        else:
            print(src)
        if show_outputs:
            outs = c.get("outputs", [])
            rendered = [_render_output(i, j, o) for j, o in enumerate(outs)]
            j = 0
            while j < len(rendered):
                k = j + 1
                while k < len(rendered) and rendered[k] == rendered[j]:
                    k += 1
                run = k - j
                if run >= _COLLAPSE_RUN_MIN:
                    # A run of identical renders — e.g. a sweep progress bar's
                    # per-update HTML placeholders. Show it once, not N times.
                    print(f"--- out {j}–{k - 1}  (×{run} identical, collapsed) ---")
                    print(rendered[j])
                else:
                    for m in range(j, k):
                        print(f"--- out {m} ---")
                        print(rendered[m])
                j = k


_MIME_EXT = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/svg+xml": "svg",
    "application/pdf": "pdf",
}


def cmd_extract(nb: dict, spec: str, out_dir: str, mime: str) -> int:
    cells = nb["cells"]
    indices = parse_range(spec, len(cells))
    if not indices:
        print(f"(no cells in range; notebook has {len(cells)} cells)")
        return 0
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ext = _MIME_EXT.get(mime, mime.replace("/", "_"))
    is_binary = (mime.startswith("image/") and mime != "image/svg+xml") or mime == "application/pdf"
    n_written = 0
    for i in indices:
        for j, o in enumerate(cells[i].get("outputs", [])):
            data = o.get("data", {})
            if mime not in data:
                continue
            payload = _str(data[mime])
            path = out / f"cell{i:03d}_out{j}.{ext}"
            if is_binary:
                try:
                    raw = base64.b64decode(payload.encode("ascii"), validate=False)
                except Exception as e:
                    print(f"error decoding cell {i} out {j}: {e}", file=sys.stderr)
                    continue
                path.write_bytes(raw)
                size = len(raw)
            else:
                path.write_text(payload, encoding="utf-8")
                size = len(payload)
            print(f"wrote {path}  ({size} bytes)")
            n_written += 1
    if n_written == 0:
        print(f"(no {mime} outputs found in range)")
    return 0


def cmd_grep(nb: dict, pattern: str, type_filter: str | None, ignore_case: bool) -> int:
    flags = re.IGNORECASE if ignore_case else 0
    try:
        rx = re.compile(pattern, flags)
    except re.error as e:
        print(f"error: invalid regex {pattern!r}: {e}", file=sys.stderr)
        return 2
    hits = 0
    for i, c in enumerate(nb["cells"]):
        kind = c["cell_type"]
        if type_filter == "code" and kind != "code":
            continue
        if type_filter == "md" and kind != "markdown":
            continue
        matches = []
        for ln, line in enumerate(_src_lines(c), start=1):
            if rx.search(line):
                matches.append((ln, line))
        if matches:
            hits += 1
            print(f"cell {i}  [{kind}]")
            for ln, line in matches:
                print(f"  {ln}: {line}")
    if hits == 0:
        print("(no matches)")
    return 0


def _install_sigpipe_handler() -> None:
    """Default SIGPIPE handling so piping into head/less terminates quietly.
    SIGPIPE doesn't exist on Windows; fall back silently there."""
    try:
        import signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (AttributeError, ImportError):
        pass


def main(argv: list[str] | None = None) -> int:
    _install_sigpipe_handler()
    if sys.platform == "win32":
        # Windows consoles default to cp1252; previews/sources contain unicode.
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(
        prog="nb",
        description="Navigate Jupyter notebooks without dragging multi-MB outputs into context. "
        "Cell indices are 0-based (they match nb['cells'][i] in JSON).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser(
        "summary",
        help="one line per cell: idx, type, src lines, outputs, bytes, preview. "
        "Optional range (same syntax as `cells`) to slice the notebook. "
        "Code-cell preview surfaces add_comment(...) strings if present, "
        "else the first non-import non-comment line.",
    )
    s.add_argument("file")
    s.add_argument("range", nargs="?", default=None, help="optional cell range (e.g. 30-80, 5,12,30-)")

    s = sub.add_parser(
        "stats",
        help="six-line notebook overview: cell counts by type, empty cells, total source lines, total output bytes",
    )
    s.add_argument("file")

    s = sub.add_parser("sections", help="markdown-header outline with cell indices")
    s.add_argument("file")

    s = sub.add_parser(
        "cells",
        help="extract specific cells. Range: 5, 5-10, 5,8,12, 5-, 5-10,12,15-. Outputs OFF by default.",
    )
    s.add_argument("file")
    s.add_argument("range")
    s.add_argument("--outputs", action="store_true", help="include cell outputs (images shown as placeholders)")

    s = sub.add_parser("grep", help="find cells whose source matches a regex")
    s.add_argument("file")
    s.add_argument("pattern")
    s.add_argument("--type", choices=["code", "md"], default=None, help="filter by cell type")
    s.add_argument("-i", "--ignore-case", action="store_true")

    s = sub.add_parser(
        "extract",
        help="dump image/PDF outputs to disk. Same range syntax as `cells`. Default mime image/png.",
    )
    s.add_argument("file")
    s.add_argument("range")
    s.add_argument("--out", default=".", help="output directory (default: cwd)")
    s.add_argument("--mime", default="image/png", help="mime type to extract (default image/png)")

    args = p.parse_args(argv)
    path = Path(args.file)
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 2
    nb = _load(str(path))

    if args.cmd == "summary":
        cmd_summary(nb, args.range)
    elif args.cmd == "stats":
        cmd_stats(nb)
    elif args.cmd == "sections":
        cmd_sections(nb)
    elif args.cmd == "cells":
        cmd_cells(nb, args.range, args.outputs)
    elif args.cmd == "grep":
        return cmd_grep(nb, args.pattern, args.type, args.ignore_case)
    elif args.cmd == "extract":
        return cmd_extract(nb, args.range, args.out, args.mime)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        try:
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        except Exception:
            pass
        sys.exit(0)
