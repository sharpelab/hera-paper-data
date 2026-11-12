# Build the artifact HTML with base64-inlined figures
import base64

def b64(p):
    return base64.b64encode(open(p, "rb").read()).decode()

figs = {k: b64(f"hera_scratch/art_{k}.png") for k in ("fan_hero", "fft_map", "ml", "lk")}

html = """<title>vti-01 Landau Fan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  :root {
    --ground:#101318; --surface:#181d24; --edge:#262d37;
    --ink:#e8e6e1; --muted:#9aa3ad; --faint:#6b7480;
    --amber:#cf7229; --teal:#35a08a; --violet:#a86ab0;
    --display:'Spectral',Georgia,serif;
    --body:'IBM Plex Sans','Segoe UI',system-ui,sans-serif;
    --mono:'IBM Plex Mono',Consolas,monospace;
  }
  * { box-sizing:border-box; }
  body { background:var(--ground); color:var(--ink); font-family:var(--body);
         margin:0; line-height:1.6; font-size:16px; }
  .wrap { max-width:1020px; margin:0 auto; padding:0 24px 72px; }
  header { padding:52px 0 8px; }
  .eyebrow { font-family:var(--mono); font-size:12px; letter-spacing:.14em;
             text-transform:uppercase; color:var(--amber); margin:0 0 10px; }
  h1 { font-family:var(--display); font-weight:600; font-size:clamp(30px,4.5vw,44px);
       margin:0 0 10px; line-height:1.15; text-wrap:balance; }
  .dek { color:var(--muted); max-width:62ch; margin:0 0 8px; }
  h2 { font-family:var(--display); font-weight:600; font-size:24px; margin:52px 0 6px; }
  h2 + p.sub { color:var(--muted); margin:0 0 18px; max-width:68ch; }
  figure { margin:18px 0 6px; background:var(--surface); border:1px solid var(--edge);
           border-radius:6px; padding:10px; overflow-x:auto; }
  figure img { display:block; width:100%; height:auto; border-radius:3px; }
  figcaption { color:var(--muted); font-size:13.5px; padding:10px 6px 4px; max-width:90ch; }
  .tiles { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
           gap:12px; margin:26px 0 6px; }
  .tile { background:var(--surface); border:1px solid var(--edge); border-radius:6px;
          padding:16px 18px; }
  .tile .k { font-family:var(--mono); font-size:11.5px; letter-spacing:.1em;
             text-transform:uppercase; color:var(--faint); margin-bottom:6px; }
  .tile .v { font-family:var(--display); font-size:26px; font-weight:600;
             font-variant-numeric:tabular-nums; }
  .tile .v small { font-size:15px; color:var(--muted); font-family:var(--body); }
  .tile.verdict .v { color:var(--amber); }
  table { border-collapse:collapse; width:100%; font-size:14px; margin:14px 0;
          font-variant-numeric:tabular-nums; }
  th { text-align:left; font-family:var(--mono); font-size:11.5px; letter-spacing:.08em;
       text-transform:uppercase; color:var(--faint); font-weight:500;
       border-bottom:1px solid var(--edge); padding:8px 14px 8px 0; }
  td { border-bottom:1px solid var(--edge); padding:8px 14px 8px 0; vertical-align:top; }
  td.mono, .mono { font-family:var(--mono); font-size:13px; }
  .hedge { border-left:3px solid var(--violet); background:var(--surface);
           border-radius:0 6px 6px 0; padding:14px 18px; margin:20px 0; font-size:14.5px;
           color:var(--muted); }
  .hedge b { color:var(--ink); }
  .foot { margin-top:56px; padding-top:18px; border-top:1px solid var(--edge);
          color:var(--faint); font-size:13px; font-family:var(--mono); line-height:1.9; }
  .chip { display:inline-block; font-family:var(--mono); font-size:11.5px;
          border:1px solid var(--edge); border-radius:99px; padding:1px 10px;
          color:var(--muted); margin-right:6px; }
</style>
<div class="wrap">
<header>
  <p class="eyebrow">Sharpe Lab &middot; VTI cryostat &middot; 2026-08-18 → 20</p>
  <h1>vti-01 is Bernal-stacked</h1>
  <p class="dek">Fermi-surface counting on a dual-gated trilayer-graphene device:
  two Shubnikov–de Haas branches, a closed Luttinger sum, and a Lifshitz–Kosevich
  mass — read against the SWMcC forward model at D&nbsp;=&nbsp;0.</p>
</header>

<div class="tiles">
  <div class="tile verdict"><div class="k">verdict (sr1 region)</div>
    <div class="v">ABA <small>strong</small></div></div>
  <div class="tile"><div class="k">BL cyclotron mass</div>
    <div class="v">0.049<small>(2) m<sub>e</sub></small></div></div>
  <div class="tile"><div class="k">Luttinger sum</div>
    <div class="v">1.14<small>&thinsp;·&thinsp;F<sub>L</sub>, one scale</small></div></div>
  <div class="tile"><div class="k">ML partition</div>
    <div class="v">~20<small>&thinsp;% of Σf</small></div></div>
</div>

<h2>The fan</h2>
<p class="sub">Background-subtracted magnetoresistance ΔR<sub>xx</sub>(n,&nbsp;B) at
true D&nbsp;=&nbsp;0, hole side. 53-point paired-gate density line &times; 131 field
rows, uniform in 1/B; τ&nbsp;=&nbsp;300&nbsp;ms, 2.5&nbsp;s dwell.</p>
<figure><img src="data:image/png;base64,{fan_hero}" alt="Landau fan ΔRxx(n, B)">
<figcaption>Run 19. Landau levels of the bilayer-like band fan out from the
charge-neutrality side; a smooth fifth-order background in B is removed per density
column. High-field rows appear blockier because uniform-1/B sampling is coarser in B
there.</figcaption></figure>

<h2>Two Fermi surfaces</h2>
<p class="sub">Per-column FFT in 1/B of the same fan. Two branches disperse with
density — the heavier bilayer-like (BL) band and the light monolayer-like (ML)
pocket — each tracking the ABA model curve under a single global density rescale.</p>
<figure><img src="data:image/png;base64,{fft_map}" alt="Per-column FFT map with ABA model overlay">
<figcaption>Markers: measured branch peaks (shown only where the extraction is
unambiguous; diamonds are the dedicated high-resolution sweep, run 20). Curves: SWMcC
ABA forward model with densities rescaled ×1.14 — the same factor that closes the
Luttinger sum f<sub>ML</sub>&thinsp;+&thinsp;f<sub>BL</sub>&nbsp;=&nbsp;1.14·F<sub>L</sub>
across ten density columns. An ABC (rhombohedral) reading would place a
<em>single</em> branch here.</figcaption></figure>

<h2>The ML pocket, resolved</h2>
<p class="sub">A dedicated τ&nbsp;=&nbsp;300&nbsp;ms sweep at the density-line edge
(5&nbsp;→&nbsp;0.5&nbsp;T, 4&nbsp;mT steps, δF&nbsp;=&nbsp;0.72&nbsp;T in this window)
pins the light pocket the earlier τ&nbsp;=&nbsp;100&nbsp;ms data could not resolve.</p>
<figure><img src="data:image/png;base64,{ml}" alt="Run 20 FFT spectra, sr1 and sr3">
<figcaption>Run 20, both voltage-probe pairs. f<sub>ML</sub>&nbsp;=&nbsp;4.4&nbsp;T and
f<sub>BL</sub>&nbsp;=&nbsp;16.4&nbsp;T sum to 20.8&nbsp;T&nbsp;≈&nbsp;1.14·F<sub>L</sub>;
the 12.0&nbsp;T line equals f<sub>BL</sub>&thinsp;−&thinsp;f<sub>ML</sub> exactly
(difference mixing). Reading 16.4&nbsp;T instead as a magnetic-breakdown sum orbit is
excluded by its measured mass (below) — a sum orbit cannot damp lighter than its
parents.</figcaption></figure>

<h2>The mass check</h2>
<p class="sub">SdH amplitude vs temperature over seven rungs, 1.25–15.1&nbsp;K.</p>
<figure><img src="data:image/png;base64,{lk}" alt="Lifshitz-Kosevich fits">
<figcaption>Runs 12–18. The BL branch damps with m*&nbsp;=&nbsp;0.049(2)&nbsp;m<sub>e</sub>
(model ABA&nbsp;BL: 0.060; model ABC: 0.108 — the dotted curve, which would leave 0.3%
amplitude at 15&nbsp;K against the measured 16%). The half-frequency component carries
the <em>same</em> mass, identifying it as even–odd modulation of the BL ladder rather
than a band. LK fits are manual (no automated corpus fit) — flagged for expert
review.</figcaption></figure>

<h2>Evidence chain</h2>
<table>
<tr><th>Step</th><th>Runs</th><th>What it established</th></tr>
<tr><td>0&nbsp;T gate map + CNP calibration</td><td class="mono">7</td>
<td>c<sub>bg</sub>/c<sub>tg</sub> = 0.7222 (sr1/sr3 agree to 0.4%); D-offset located
from the symmetric R<sub>CNP</sub> minimum</td></tr>
<tr><td>SdH spot checks, both signs</td><td class="mono">8, 9</td>
<td>Dominant branch at ≈0.9·F<sub>L</sub> on hole <em>and</em> electron side;
onset 1.7&nbsp;T</td></tr>
<tr><td>First fan + screens</td><td class="mono">10, 11</td>
<td>Branch A linear through origin; half-tone locked at A/2 (not a pocket);
harmonic comb identified</td></tr>
<tr><td>LK temperature ladder</td><td class="mono">12–18</td>
<td>m*(A) = 0.049(2)&nbsp;m<sub>e</sub> — ABC mass excluded; A/2 shares the mass</td></tr>
<tr><td>Quality fan, τ = 300 ms</td><td class="mono">19</td>
<td>ML branch resolved, own Onsager slope; Luttinger closes at 1.14·F<sub>L</sub></td></tr>
<tr><td>High-resolution descent</td><td class="mono">20</td>
<td>f<sub>ML</sub> = 4.4&nbsp;T confirmed at n = −1.74×10¹²; mixing line at
f<sub>BL</sub>−f<sub>ML</sub></td></tr>
</table>

<div class="hedge"><b>Hedges.</b> The density scale λ&nbsp;=&nbsp;1.14 sits at the
edge of the lever-arm prior band — the quantum-Hall lever-arm check is the pending
upgrade. The ML mass itself (predicted ~0.01&nbsp;m<sub>e</sub>) is unmeasured; a
low-field-window temperature ladder or the high-field Středa complement would take
the call from strong to decisive. sr3 corroborates all frequency content at lower
SNR; sr2 (short pair) is uninformative. Transport is contact-limited through a
~109&nbsp;MΩ source contact — all R<sub>xx</sub> normalized by the measured drain
current per point.</div>

<div class="foot">
<span class="chip">device vti-01 · trilayer graphene</span>
<span class="chip">VTI · base 1.24 K · T<sub>e</sub> ≈ 8 K</span>
<span class="chip">drive 100 mV / 10 MΩ · 13.777 Hz</span><br>
data: zack/20260818-vti-01/data/7–20 &middot; analysis: 20260818_ana.ipynb &middot;
model: hera/models/trilayer_fs_count (SWMcC + MacDonald, semi-quantitative) &middot;
measured by HERA under E1 autonomy, operator Z. Gomez
</div>
</div>
"""
html = html.replace("{fan_hero}", figs["fan_hero"]).replace("{fft_map}", figs["fft_map"]) \
           .replace("{ml}", figs["ml"]).replace("{lk}", figs["lk"])
open("hera_scratch/vti01_landau_fan.html", "w", encoding="utf-8").write(html)
print(f"written, {len(html)/1e6:.2f} MB")
