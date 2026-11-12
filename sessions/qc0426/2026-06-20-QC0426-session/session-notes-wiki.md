# Session notes — 20260620-QC0426 (wiki)

Operator's live observations during the 2026-06-20 QC0426 VTI session.
Pulled from the wiki for archiving alongside the session artifacts.

- Source: https://wiki.sharpelab.science/doc/20260620-qc0426-Kq8giJ298s
- Wiki title: `20260620-QC0426`
- Updated: 2026-06-21T19:24:40Z

---

* it is reading the qswitch API, we should provide an example so it doesn't have to read code
  * maybe we should provide api documentation
  * yeah now it's reading the megasweep api and getting blasted with a shitload of unnecessary stuff
  * check why the two rigs have different measureme apis (if so) and consolidate them so we can provide a single api ref
  * it likes to confirm its not snake
* markdown \~ strikeout, annoying
* looks like it didn't do the electron side (which I believe the recipe says is mandatory?)  electron side data is much cleaner
* I'm not seeing it use the sdh_onset helper
