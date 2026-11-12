import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ICellModel } from '@jupyterlab/cells';
import { INotebookTracker, NotebookPanel, Notebook } from '@jupyterlab/notebook';
import { DisposableSet, IDisposable } from '@lumino/disposable';

/**
 * The attributes we stamp onto every cell node. CSS rules in `style/base.css`
 * render them in the left gutter via `attr(...)`.
 *
 * `data-cell-index` — the cell's 0-based model index. Computed in JS from the
 * notebook *model* order (`notebook.widgets` is one widget per model cell, in
 * order), NOT from DOM order. This is the whole point: under JupyterLab 4's
 * windowed rendering (`windowingMode: "full"`) off-screen cells are detached
 * from the DOM, so a CSS counter — or anything derived from DOM order — would
 * miscount on scroll. Because the value lives on each persistent widget node
 * as a data attribute, scrolling triggers no work here at all.
 *
 * `data-cell-time` — the cell's landing time, read from
 * `metadata.hera.appended_at` (stamped by `nb-collab` at append, ISO-8601
 * UTC). Rendered in the viewer's local timezone as `HH:MM`, date-prefixed
 * (`MM-DD HH:MM`) when the stamp is not from the current day. Cells without
 * the stamp (template cells, operator-typed cells) get no badge. Render-only:
 * this extension never writes metadata.
 */
const INDEX_ATTR = 'data-cell-index';
const TIME_ATTR = 'data-cell-time';

/**
 * Format an ISO-8601 stamp for the gutter: local `HH:MM`, prefixed with
 * `MM-DD ` when the stamp's local date differs from today's. Returns null on
 * an unparseable stamp.
 */
function formatStamp(iso: string): string | null {
  const t = new Date(iso);
  if (isNaN(t.getTime())) {
    return null;
  }
  const pad = (n: number): string => String(n).padStart(2, '0');
  const hhmm = `${pad(t.getHours())}:${pad(t.getMinutes())}`;
  const now = new Date();
  const sameDay =
    t.getFullYear() === now.getFullYear() &&
    t.getMonth() === now.getMonth() &&
    t.getDate() === now.getDate();
  return sameDay ? hhmm : `${pad(t.getMonth() + 1)}-${pad(t.getDate())} ${hhmm}`;
}

/** The formatted landing time for a cell, or null when it has none. */
function appendedTime(model: ICellModel): string | null {
  const hera = model.getMetadata('hera') as unknown;
  if (!hera || typeof hera !== 'object') {
    return null;
  }
  const iso = (hera as { appended_at?: unknown }).appended_at;
  return typeof iso === 'string' ? formatStamp(iso) : null;
}

/**
 * Stamp the 0-based model index and the landing time onto every cell.
 *
 * `notebook.widgets` mirrors `notebook.model.cells` exactly — same order, one
 * entry per cell including markdown and raw cells — so the widget's position is
 * the index `nb['cells'][i]` would report. Writing a data attribute on a
 * detached node is harmless; the value is still there when JupyterLab
 * re-attaches the node on scroll.
 */
function stampCells(notebook: Notebook): void {
  const widgets = notebook.widgets;
  for (let i = 0; i < widgets.length; i++) {
    const widget = widgets[i];
    const node = widget.node;
    const index = String(i);
    // Avoid touching the DOM when nothing changed (cheap guard for the common
    // append case where only the tail shifts).
    if (node.getAttribute(INDEX_ATTR) !== index) {
      node.setAttribute(INDEX_ATTR, index);
    }
    const time = appendedTime(widget.model);
    if (time === null) {
      node.removeAttribute(TIME_ATTR);
    } else if (node.getAttribute(TIME_ATTR) !== time) {
      node.setAttribute(TIME_ATTR, time);
    }
  }
}

/**
 * Wire a single notebook panel: renumber once it's ready, then again on every
 * structural change to the cell list (insert / delete / move). Returns a
 * disposable that detaches all listeners.
 */
function wirePanel(panel: NotebookPanel): IDisposable {
  const notebook = panel.content;
  const disposables = new DisposableSet();

  const update = (): void => {
    // The model can be null transiently during teardown.
    if (!notebook.model) {
      return;
    }
    // Wire each cell model's metadataChanged so the time badge appears the
    // moment nb-collab stamps `appended_at` — the stamp lands *after* the
    // cell insert (a separate RTC transaction), so cells.changed alone would
    // miss it. Lumino dedupes identical (signal, slot) pairs, so re-connecting
    // on every pass is a no-op for already-wired cells, and cell-model
    // disposal clears its own connections — no per-cell teardown needed.
    for (const widget of notebook.widgets) {
      widget.model.metadataChanged.connect(update);
    }
    stampCells(notebook);
  };

  const connectModel = (): void => {
    const model = notebook.model;
    if (!model) {
      return;
    }
    model.cells.changed.connect(update);
    disposables.add({
      isDisposed: false,
      dispose: () => {
        model.cells.changed.disconnect(update);
      }
    });
    update();
  };

  // The model may swap (e.g. notebook reload); rewire when it does.
  notebook.modelChanged.connect(connectModel);
  disposables.add({
    isDisposed: false,
    dispose: () => {
      notebook.modelChanged.disconnect(connectModel);
    }
  });

  // Initial pass once the context (and thus the model) is ready.
  void panel.context.ready.then(() => {
    if (!panel.isDisposed) {
      connectModel();
    }
  });

  return disposables;
}

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-cell-index:plugin',
  description:
    "Show each cell's stable 0-based model index and landing time in the notebook gutter.",
  autoStart: true,
  requires: [INotebookTracker],
  activate: (_app: JupyterFrontEnd, tracker: INotebookTracker): void => {
    const wired = new WeakSet<NotebookPanel>();
    tracker.widgetAdded.connect((_sender, panel: NotebookPanel) => {
      if (wired.has(panel)) {
        return;
      }
      wired.add(panel);
      const disposable = wirePanel(panel);
      panel.disposed.connect(() => {
        disposable.dispose();
      });
    });
  }
};

export default plugin;
