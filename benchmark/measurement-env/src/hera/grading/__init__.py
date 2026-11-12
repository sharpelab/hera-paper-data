"""Grading a replay episode: an LLM extractor writes a small output file, a deterministic
``grade.py`` turns it into scores.  Design: Obsidian "HERA Grader Plan".

Grader directories live at ``hera/graders/<name>/`` (``prompt.md`` + ``grade.py``); this
package is the harness only: the per-device table (``devices``), ``submit_output``
(``submit``), the runner (``runner``) and the calibration harness (``calibrate``).  Physics
lives next to the grader that uses it (``sdh-field-resolution/s1.py``, ``sc-survey/sc_arc.py``).
"""
