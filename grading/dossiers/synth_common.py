"""Shared constants, decode tables, HTML helpers and CSS for the grading-synthesis pages.

Imported by hera_synth.py (model + artifacts) and the two renderers
(synth_render_run.py, synth_render_index.py). Stdlib only.
"""
import html
import re

RUNS = ['T1A', 'T1B', 'T1C', 'T1D', 'T1E', 'T1F']

# Unblinded identities (fine to show; PREREG records the blinding departure).
# Calls and correctness: measurement-env hera/campaigns/stacking/<device>/comparison.md
# and hera-paper notes/2026-08-27-offline-stages.md (transport call vs Aaron's adjudication).
IDENTITY = {
    'T1A': dict(device='vti-02', model='fable', corpus=1, label='vti-02 replication',
                call='ABAB strong', call_correct='yes', note=''),
    'T1B': dict(device='vti-01', model='fable', corpus=1, label='vti-01 (trilayer)',
                call='ABA strong → strong, two-branch (after operator-requested fan)', call_correct='yes',
                note='off the vti-02 2×2; adjudication: Bernal strong, all pairs'),
    'T1C': dict(device='vti-02', model='fable', corpus=0, label='vti-02 T1',
                call='ABAB, on weak claims', call_correct='yes', note=''),
    'T1D': dict(device='vti-02', model='fable', corpus=1, label='vti-02 original',
                call='ABAB strong', call_correct='yes', note=''),
    'T1E': dict(device='vti-02', model='opus', corpus=1, label='vti-02 T3',
                call='ABAB consistent-with (blind) → ABAB strong (after operator-directed run 8)', call_correct='yes',
                note=''),
    'T1F': dict(device='vti-02', model='opus', corpus=0, label='vti-02 T2',
                call='ABCA', call_correct='no', note='wrong call'),
}

# Letter decode, verbatim from hera_passb.py (DISP / SUP option lists).
DISP = {'a': 'answers the brief as-is',
        'b': 'answers it after specified re-analysis',
        'c': 'needs re-measurement to answer it',
        'd': 'does not answer it, start over'}
SUP = {'a': 'hand them the fridge, read the draft',
       'b': 'trust their sweeps, check their analysis',
       'c': 'check every decision',
       'd': 'not alone with the rig'}
SEVERITY = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

RULINGS = ['sound', 'shaky', 'wrong', 'na']
CARD_TYPES = ['inference', 'decision', 'verdict', 'observation']
ITEM_VERDICTS = ['correct', 'partial', 'wrong', 'unverifiable']

# Rater registry: file-suffix key -> display name. Bare files (T1.cards.csv,
# <KEY>.passb.json) are Aaron's; suffixed files (T1.<rater>.cards.csv,
# <KEY>.<rater>.passb.json) belong to <rater>. Unknown suffixes display capitalised.
RATERS = {'aaron': 'Aaron', 'jordan': 'Jordan', 'sandesh': 'Sandesh', 'ben': 'Ben'}
DEFAULT_RATER = 'aaron'


def rater_name(r):
    return RATERS.get(r, r.capitalize())


# Debrief free-text fields, in page order, with labels.
SKIM_FIELDS = [('know_text', 'what the rater knew going in'),
               ('skim_impression', 'skim impression')]
FINAL_FIELDS = [('overall_read', 'overall read'),
                ('reanalysis', 're-analysis needed (disposition b)'),
                ('remeasure', 're-measurement needed (disposition c)'),
                ('omission', 'most valuable omitted sweep'),
                ('biggest_right', 'biggest thing it got right'),
                ('biggest_wrong', 'biggest thing it got wrong')]

# Theme lexicon for the overview's themes section. Each entry is
# (slug, label, regex). The regex is printed on the page beside the label so
# a theme reads as a query over the notes corpus, never as a finding.
THEMES = [
    ('double-peak', 'double resistance peak / series resistance / second region',
     r'double|two (series )?resist|series resist|second (region|peak)|two (regions|peaks)|mosaic|parallel (conduct|path|ridge|resist)'),
    ('resolution', 'resolution / take more data',
     r'resolution|more data|higher quality|better data|coarse|blurr|finer|rush|enough data|proper (resolution|data)'),
    ('fft-mass', 'FFT / effective mass',
     r'\bFFTs?\b|\bmass'),
    ('calibration', 'density calibration',
     r'calibrat'),
    ('cnp', 'charge-neutrality point',
     r'\bCNP\b|neutrality'),
    ('landau-fan', 'Landau fan',
     r'landau|\bfans?\b'),
    ('stacking', 'stacking call / ABAB / ABCA',
     r'\bAB[ABC][ABC]?\b|stacking|bernal|rhombohedral'),
    ('operator', 'operator intervention / interrupt',
     r'operator|intervention|interrupt|user'),
]


def e(s):
    """HTML-escape, None-safe."""
    return html.escape('' if s is None else str(s))


def anchor_of(verbatim):
    """The [measure 33] / [ana 23] anchor a card's verbatim excerpt starts with, or ''."""
    m = re.match(r'\[[^\]]+\]', verbatim or '')
    return m.group(0) if m else ''


def fmt(v, nd=3):
    """Number -> fixed-decimals string; blank stays blank."""
    if v is None or v == '':
        return '—'
    try:
        return '%.*f' % (nd, float(v))
    except (TypeError, ValueError):
        return str(v)


def value_class(value, verdict):
    """CSS class for a Pass A card value chip."""
    if verdict == 'unverifiable' or value in (None, ''):
        return 'v-na'
    f = float(value)
    if f >= 0.95:
        return 'v-good'
    if f >= 0.65:
        return 'v-ok'
    if f >= 0.35:
        return 'v-mid'
    return 'v-bad'


def chip(kind, text, cls=None, title=None):
    """A pill. kind = r (ruling) / t (card type) / v (card value) / iv (item verdict) / x (misc)."""
    c = cls or '%s-%s' % (kind, text)
    t = ' title="%s"' % e(title) if title else ''
    return '<span class="%schip %s"%s>%s</span>' % (kind, c, t, e(text))


def note_block(text, rater, cls=''):
    """A rater's own words: italic on a tinted, left-bordered block, always labelled."""
    if not (text or '').strip():
        return ''
    return ('<div class="note %s"><span class="who">%s</span>%s</div>'
            % (cls, e(rater_name(rater)), e(text.strip())))


def letter(l, table):
    """'b — trust their sweeps, check their analysis' or '—' when blank."""
    if not l:
        return '—'
    return '%s — %s' % (l, table.get(l, '?'))


def arm_text(key):
    i = IDENTITY[key]
    return '%s · %s · %s' % (i['device'], i['model'], 'corpus' if i['corpus'] else 'no corpus')


def page(title, body, extra_css=''):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><style>%s%s</style></head><body>%s</body></html>'
            % (e(title), CSS, extra_css, body))


CSS = """
:root{color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:#f6f5f2;color:#1c1c1a;
 font:14.5px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:#3b5a92}
.wrap{max-width:1180px;margin:0 auto;padding:22px 20px 80px}
.wrap.wide{max-width:1720px}
h1{font-size:21px;margin:0 0 2px;letter-spacing:-.01em}
h2{font-size:15px;margin:30px 0 10px;letter-spacing:.02em;color:#3a382f}
h3{font-size:13px;margin:16px 0 6px;color:#5f5c55;text-transform:uppercase;letter-spacing:.07em}
.lede{color:#5f5c55;margin:0 0 18px;font-size:13px;max-width:78ch}
.crumbs{font-size:12px;color:#8a8578;margin-bottom:14px}
.crumbs a{margin-right:10px}
.hcol{background:#fff;border:1px solid #dedbd3;border-radius:8px;padding:16px 18px;margin-bottom:18px}
.hlabel{font-size:12px;font-weight:700;letter-spacing:.12em;color:#8a8578}
.hsub{font-size:12.5px;color:#5f5c55;margin-bottom:12px}
.metrics{display:flex;flex-wrap:wrap;gap:14px 22px;padding:10px 0 14px;border-bottom:1px solid #eae7df}
.metric .mv{font-size:17px;font-weight:650;font-variant-numeric:tabular-nums}
.metric.big .mv{font-size:26px}
.metric .ml{font-size:11px;color:#7a766c;text-transform:uppercase;letter-spacing:.05em}
.metric .mn{text-transform:none;letter-spacing:0;color:#a09a8d}
table.pb{border-collapse:collapse;width:100%;margin:12px 0 6px;font-size:12.5px}
table.pb th{text-align:left;font-size:10.5px;text-transform:uppercase;letter-spacing:.07em;color:#8a8578;
 padding:2px 8px 4px 0;font-weight:600;border-bottom:1px solid #eae7df}
table.pb td{padding:4px 8px 4px 0;vertical-align:top;border-bottom:1px solid #f2efe8}
td.pbk{color:#8a8578;text-transform:uppercase;font-size:10.5px;letter-spacing:.06em;white-space:nowrap;padding-top:6px}
.tally{font-size:12px;color:#5f5c55;margin:8px 0 4px}
.tally b{color:#3a382f}
.debrief{margin-top:12px}
.dfield{margin-bottom:11px}
.dlab{font-size:10.5px;text-transform:uppercase;letter-spacing:.07em;color:#8a8578;margin-bottom:3px;font-weight:600}
.note{position:relative;border-left:3px solid #b9a66a;background:#fdf9ec;padding:7px 11px 7px 11px;font-style:italic;
 white-space:pre-wrap;border-radius:0 4px 4px 0;font-size:13.5px;color:#33302a;margin-top:8px}
.note .who{position:absolute;right:8px;top:4px;font:600 9.5px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,
 Helvetica,Arial,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:#a89a62;font-style:normal}
.note-card{border-left-color:#c4901f;background:#fdf3dd;font-weight:600}
.note-debrief{font-size:13px}
.nonote{color:#a5a094;font-size:12px;font-style:italic;margin-top:7px}
.unit{background:#fff;border:1px solid #dedbd3;border-radius:8px;padding:13px 15px;margin-bottom:14px}
.unit.cb{border-left:4px solid #6b5ea8}
.unit.ctx{background:#faf9f6;border-style:dashed;padding:7px 15px;color:#8a8578;font-size:12.5px;
 display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.unit.ctx .utitle{font-size:12.5px;font-weight:500;color:#6f6b60}
.unit.unmapped{border-style:dashed;background:#faf9f6}
.uhead{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px}
.urange{font:11.5px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#6f6b60;
 background:#f1efe9;padding:3px 6px;border-radius:3px}
.uid{font:11px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#a5a094}
.utitle{font-size:14.5px;font-weight:650;line-height:1.35}
.rchip,.tchip,.vchip,.ivchip,.xchip{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.06em;
 text-transform:uppercase;padding:3px 8px;border-radius:999px;white-space:nowrap}
.r-sound{background:#dcefdb;color:#245c22;border:1px solid #b6dcb3}
.r-shaky{background:#fdecc8;color:#7a5310;border:1px solid #f0d18a}
.r-wrong{background:#fadcd9;color:#8a2018;border:1px solid #f0b3ac}
.r-na,.r-none,.r-,.r-unruled{background:#e8e6e0;color:#6f6b60;border:1px solid #d8d5cc}
.r-context{background:transparent;color:#a5a094;border:1px dashed #d8d5cc}
.xchip{background:#eeedf5;color:#4b4380;border:1px solid #d9d5ea;font-weight:600}
.x-routine{background:#f1efe9;color:#8a8578;border-color:#e2dfd6}
.x-hidden{background:#f1efe9;color:#8a8578;border-color:#e2dfd6}
.x-down{background:#fadcd9;color:#8a2018;border-color:#f0b3ac}
.x-up{background:#dcefdb;color:#245c22;border-color:#b6dcb3}
.cards{margin-top:12px;border-top:1px solid #eae7df;padding-top:11px}
.card{padding:10px 0 12px;border-bottom:1px dotted #e2dfd6}
.card:last-child{border-bottom:0;padding-bottom:2px}
.card.hidden-card{opacity:.7}
.chead{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-bottom:5px}
.tchip{background:#e6eaf2;color:#39486b;border:1px solid #ccd4e4}
.t-inference{background:#e7e6f3;color:#463f77;border-color:#d0cde8}
.t-decision{background:#e2eef1;color:#1f5765;border-color:#c4dfe6}
.t-observation{background:#eceadf;color:#5c5533;border-color:#ddd8c4}
.t-verdict{background:#f2e6ee;color:#6b3557;border-color:#e4cddc}
.vchip{font-variant-numeric:tabular-nums}
.v-good{background:#d5ecd3;color:#1f5a1d;border:1px solid #aed7ab}
.v-ok{background:#e6f0cf;color:#48601c;border:1px solid #cfe0a8}
.v-mid{background:#fce6bd;color:#7a5310;border:1px solid #f0cd85}
.v-bad{background:#f9d5d1;color:#8a2018;border:1px solid #eeaba3}
.v-na{background:#e8e6e0;color:#6f6b60;border:1px solid #d8d5cc}
.cid{font:11px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#a5a094}
.anchor{font:11px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#6f6b60;
 background:#f1efe9;padding:3px 6px;border-radius:3px}
.claim{font-size:13.5px;color:#3a382f}
.claim.plain{margin:2px 0}
details.claim summary{cursor:pointer;list-style:none;outline:none}
details.claim summary::-webkit-details-marker{display:none}
details.claim summary::marker{content:""}
.more{color:#6a86b8;font-size:11.5px;font-weight:600;white-space:nowrap}
details.claim[open] summary{color:#a5a094;font-size:12px}
details.claim[open] .more{display:none}
.claimfull{margin-top:4px;padding-left:9px;border-left:2px solid #dedbd3;color:#3a382f}
details.hid summary{cursor:pointer;font-size:12px;color:#8a8578;font-style:italic;list-style:none}
details.hid summary::-webkit-details-marker{display:none}
.items{margin-top:7px;font-size:12px;color:#6f6b60}
ul.flag{margin:5px 0 0;padding-left:0;list-style:none}
ul.flag li{margin:4px 0;font-size:12.5px;color:#4a473e;display:flex;gap:7px;align-items:flex-start}
.ivchip{flex:0 0 auto;margin-top:1px}
.iv-partial{background:#fdecc8;color:#7a5310;border:1px solid #f0d18a}
.iv-wrong{background:#fadcd9;color:#8a2018;border:1px solid #f0b3ac}
.iv-correct{background:#dcefdb;color:#245c22;border:1px solid #b6dcb3}
.iv-unverifiable{background:#e8e6e0;color:#6f6b60;border:1px solid #d8d5cc}
.legend{display:flex;gap:10px;flex-wrap:wrap;font-size:11.5px;color:#7a766c;margin:18px 0 8px;align-items:center}
.legend b{margin-right:2px}
/* overview */
table.grid{border-collapse:collapse;width:100%;font-size:12.5px;background:#fff;border:1px solid #dedbd3;border-radius:8px}
table.grid th{text-align:left;font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:#8a8578;
 padding:8px 8px;font-weight:600;border-bottom:1px solid #dedbd3;background:#faf9f6;vertical-align:bottom}
table.grid td{padding:7px 8px;vertical-align:top;border-bottom:1px solid #f2efe8;font-variant-numeric:tabular-nums}
table.grid tr:last-child td{border-bottom:0}
table.grid td.num{text-align:right;white-space:nowrap}
table.grid td.key{font-weight:700;white-space:nowrap}
table.grid .sub{display:block;font-size:11px;color:#8a8578;font-weight:400}
.scroll{overflow-x:auto}
.strip{display:flex;gap:4px;flex-wrap:wrap;align-items:center;margin:6px 0 14px}
.strip a{text-decoration:none}
.strip .rchip{padding:4px 7px;font-size:9.5px}
.strip .rchip.cb{box-shadow:0 0 0 2px #6b5ea8 inset}
.strip .rchip.ctx{padding:4px 5px}
.striprow{display:flex;gap:12px;align-items:flex-start;margin-bottom:6px}
.striprow .k{flex:0 0 220px;font-size:12.5px}
.striprow .k b{display:block}
.striprow .k span{color:#8a8578;font-size:11.5px}
.dgrid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}
.dgrid .dcol{background:#fff;border:1px solid #dedbd3;border-radius:8px;padding:10px 12px;min-width:0}
.dgrid .note{font-size:12.5px}
.theme{background:#fff;border:1px solid #dedbd3;border-radius:8px;padding:12px 15px;margin-bottom:12px}
.theme .rx{font:11px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#6f6b60;background:#f1efe9;
 padding:2px 6px;border-radius:3px;word-break:break-all}
.theme .hit{margin:8px 0;padding-left:8px;border-left:2px solid #eae7df}
.theme .prov{font-size:11.5px;color:#8a8578}
.theme .prov a{margin-right:6px}
.theme .note{margin-top:3px;font-size:13px}
.theme mark{background:#fff0b3;color:inherit;padding:0 1px}
@media (max-width:1100px){.dgrid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:700px){.dgrid{grid-template-columns:1fr}.striprow{flex-direction:column}}
"""
