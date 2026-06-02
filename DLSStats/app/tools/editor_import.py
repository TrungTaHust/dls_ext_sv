import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

from editor_config import get_price, _cast
from editor_widgets import EditDialog

# ── Preview helpers shared by ImportTab & OCRTab ──────────────────────────────
PREVIEW_COLS = ["fname", "lname", "nat", "club", "pos", "foot", "rate", "hgt",
                "spe", "acc", "sta", "str", "con", "pas", "sho", "tac", "prc",
                "id", "version", "status"]
STAT_COLS = {"rate", "spe", "acc", "sta", "str", "con", "pas", "sho", "tac"}


def _validate_row(row):
  """Return list of error strings, empty = valid."""
  errs = []
  for col in STAT_COLS:
    v = row.get(col)
    if v == "" or v is None:
      continue
    try:
      if int(v) > 100:
        errs.append(f"{col} > 100 ({v})")
    except (ValueError, TypeError):
      errs.append(f"{col} not int ({v})")
  if str(row.get("status", "1")) not in ("0", "1", "2", "3"):
    errs.append(f"status invalid ({row.get('status')})")
  return errs


def _build_preview_tree(parent, rows):
  """Build a Treeview showing rows with validation colouring. Returns (frame, tree)."""
  cols = [c for c in PREVIEW_COLS if c != "prc"] + ["prc", "errors"]
  frame = ttk.Frame(parent)
  tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="extended")
  for c in cols:
    w = 90 if c in ("fname", "lname", "nat", "club", "errors") else 55
    tree.heading(c, text=c)
    tree.column(c, width=w, minwidth=36, anchor="center")
  vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
  hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
  tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
  tree.grid(row=0, column=0, sticky="nsew")
  vsb.grid(row=0, column=1, sticky="ns")
  hsb.grid(row=1, column=0, sticky="ew")
  frame.rowconfigure(0, weight=1)
  frame.columnconfigure(0, weight=1)
  tree.tag_configure("ok",   background="#e8f5e9")
  tree.tag_configure("warn", background="#fff9c4")
  tree.tag_configure("error", background="#ffebee")
  _populate_preview_tree(tree, rows)
  return frame, tree


def _populate_preview_tree(tree, rows):
  tree.delete(*tree.get_children())
  cols = [c for c in PREVIEW_COLS if c != "prc"] + ["prc", "errors"]
  for idx, row in enumerate(rows):
    errs = _validate_row(row)
    tag  = "error" if errs else "ok"
    vals = []
    for c in cols:
      if c == "prc":     vals.append(get_price(row))
      elif c == "errors": vals.append("; ".join(errs) if errs else "")
      else:              vals.append(row.get(c, ""))
    tree.insert("", "end", iid=str(idx), values=vals, tags=(tag,))


def _commit_rows(rows, ver_tab, pid_tab):
  """Add rows to the given VersionTab, auto-assigning id from pid_tab."""
  added = 0
  for row in rows:
    new_row = dict(row)
    new_row["prc"] = get_price(new_row)
    new_row["version"] = ver_tab.ver
    fname = new_row.get("fname", "").strip()
    lname = new_row.get("lname", "").strip()
    pid = pid_tab.lookup_id(fname, lname) if pid_tab else None
    if pid is None and pid_tab:
      pid = pid_tab.add_player(fname, lname)
    new_row["id"] = pid or 0
    ver_tab.data.append(new_row)
    added += 1
  if ver_tab._tbl:
    ver_tab._tbl.refresh()
  return added


# ── ImportTab ─────────────────────────────────────────────────────────────────
class ImportTab(ttk.Frame):
  """Browse a JSON file, preview rows, validate, then add to a chosen version."""

  def __init__(self, parent, data_tab, pid_tab):
    super().__init__(parent)
    self._data_tab = data_tab
    self._pid_tab  = pid_tab
    self._rows     = []
    self._build()

  def _build(self):
    # ── top bar ──────────────────────────────────────────────────────────────
    top = ttk.Frame(self)
    top.pack(fill="x", padx=6, pady=6)

    ttk.Button(top, text="Browse JSON...", command=self._browse).pack(side="left", padx=4)
    self._file_lbl = ttk.Label(top, text="No file selected", foreground="#888888")
    self._file_lbl.pack(side="left", padx=6)

    ttk.Label(top, text="Target version:").pack(side="left", padx=(20, 4))
    self._ver_var = tk.StringVar()
    self._ver_cb  = ttk.Combobox(top, textvariable=self._ver_var, width=10, state="readonly")
    self._ver_cb.pack(side="left")
    self._refresh_versions()

    ttk.Button(top, text="Add selected",  command=self._add_selected).pack(side="right", padx=4)
    ttk.Button(top, text="Add all valid", command=self._add_all_valid).pack(side="right", padx=4)

    # ── status ───────────────────────────────────────────────────────────────
    self._status_lbl = ttk.Label(self, text="")
    self._status_lbl.pack(fill="x", padx=8)

    # ── preview area ─────────────────────────────────────────────────────────
    self._preview_frame = ttk.Frame(self)
    self._preview_frame.pack(fill="both", expand=True, padx=4, pady=4)
    self._tree = None

  def _refresh_versions(self):
    vers = [lbl for lbl in self._data_tab._ver_tabs]
    self._ver_cb["values"] = vers
    if vers:
      self._ver_var.set(vers[-1])

  def _browse(self):
    from tkinter import filedialog
    path = filedialog.askopenfilename(
      title="Select JSON file to import",
      filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if not path:
      return
    try:
      with open(path, encoding="utf-8") as f:
        data = json.load(f)
      if not isinstance(data, list):
        messagebox.showerror("Invalid", "File must contain a JSON array.")
        return
      self._rows = data
      self._file_lbl.config(text=os.path.basename(path), foreground="#000000")
      self._refresh_versions()
      self._show_preview()
    except Exception as e:
      messagebox.showerror("Error", str(e))

  def _show_preview(self):
    for w in self._preview_frame.winfo_children():
      w.destroy()
    frame, self._tree = _build_preview_tree(self._preview_frame, self._rows)
    frame.pack(fill="both", expand=True)
    ok    = sum(1 for r in self._rows if not _validate_row(r))
    total = len(self._rows)
    self._status_lbl.config(
      text=f"{total} rows loaded  |  {ok} valid  |  {total-ok} with errors  "
           f"(green=ok, yellow=warn, red=error)  —  Ctrl+click to multi-select"
    )

  def _selected_rows(self):
    if not self._tree:
      return []
    return [self._rows[int(iid)] for iid in self._tree.selection()]

  def _add_selected(self):
    rows = self._selected_rows()
    if not rows:
      messagebox.showwarning("Nothing selected", "Select rows in the preview table first.")
      return
    self._do_add(rows)

  def _add_all_valid(self):
    rows = [r for r in self._rows if not _validate_row(r)]
    if not rows:
      messagebox.showwarning("No valid rows", "No valid rows to add.")
      return
    self._do_add(rows)

  def _do_add(self, rows):
    label = self._ver_var.get()
    vt = self._data_tab._ver_tabs.get(label)
    if not vt:
      messagebox.showerror("No version", "Select a target version first.")
      return
    vt.ensure_loaded()
    n = _commit_rows(rows, vt, self._pid_tab)
    messagebox.showinfo("Done", f"Added {n} rows to version {label}.")
