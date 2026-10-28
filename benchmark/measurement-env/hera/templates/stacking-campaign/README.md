# Stacking-campaign kit templates

**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** This directory names
the blind; deployed kits never reference it, nor `hera/campaigns/`.

*Frozen kit templates for the trilayer stacking series: per device, one
brief + one device card, instantiated mechanically — slots filled, prose
never authored — so every device runs the identical campaign. The
templates ride the prereg freeze tag
(`hera/campaigns/stacking/prereg-protocol.md` §3); `hera/campaigns/`
does not. `device_card.template.md` follows the
`device-cards/EXAMPLE.md` schema, specialized to the series class
(dual-gated trilayer, VTI); `session_template.md` stays the generic
non-campaign brief layer. The `.template.md` names keep `hera-mksession`
from ever matching this directory as a device. The QC0426 capstone kit
is an instantiation of these templates (`SI_GATE: yes`).*

## Intake — per device

Shield (Aaron):

1. Cool + wire the device; fix the provided contact configuration at
   the breakout.
2. Assign a neutral alias; the alias↔device mapping stays with you until
   that device unseals.
3. Copy `intake-facts.template.md`, fill every field (form-fill only —
   no prose beyond the listed fields), run the two greps in its header,
   send the file to Zack.

Operator (Zack) — mechanical from here; either side can run it:

4. `hera-mkkit new stacking-campaign <alias> --facts <file>` — the kit
   lands at the canonical consumer paths:
   `hera/docs/brief-<alias>.md` and
   `hera/templates/<alias>/device_card.md`.
5. `hera-mkkit check stacking-campaign <alias>` — unfilled slots,
   unresolved conditionals, device-id match, then (last) the
   `hera/blinding.md` grep + `frame-words.grep`.
6. Commit on `hera`; the rig pulls; `hera-session` builds the session as
   usual (its post-build blinding grep is the final fence).

The fact handoff (step 3→4) is the blind's cut point. Instantiation is
audit-clean by construction: `git diff` of a kit against its template
shows slot fills only. Hardware that doesn't match the fixed template
text (non-Keithley gates, a mux, a different bias chain) is not a
slot — it's a protocol deviation (`prereg-protocol.md` §7), settled
before instantiating.

## After the session

Locking and per-device artifacts: `prereg-protocol.md` §5.
