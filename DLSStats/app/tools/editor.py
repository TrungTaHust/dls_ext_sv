import json
import copy
import tkinter as tk
from tkinter import ttk, messagebox
import os

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resources", "data")
SPECIAL_FILE   = os.path.join(BASE_DIR, "special.json")
PLAYER_ID_FILE = os.path.join(BASE_DIR, "player_id.json")
PRICE_MAP_FILE = os.path.join(BASE_DIR, "price_map.json")

def ver_file(ver):
  """Return the path for a version file, e.g. 20231.json"""
  return os.path.join(BASE_DIR, f"{ver}.json")

def _load_price_map():
  with open(PRICE_MAP_FILE, encoding="utf-8") as f:
    raw = json.load(f)
  return {int(k): v for k, v in raw.items()}

price_map = _load_price_map()

# Output column order when saving to file (matches data.json sample)
DATA_SAVE_COLS = ["fname", "lname", "nat", "club", "pos", "foot", "rate", "hgt",
          "spe", "acc", "sta", "str", "con", "pas", "sho", "tac", "prc", "id", "version", "status"]

# Columns shown in version tabs (edit dialog + table) — prc is computed, not editable
DATA_COLS_VER = ["id", "fname", "lname", "nat", "club", "pos", "foot", "rate", "hgt",
         "spe", "acc", "sta", "str", "con", "pas", "sho", "tac", "status"]
SPECIAL_COLS = ["fname", "lname", "nat", "type", "pos", "version", "foot", "rate", "hgt",
        "spe", "acc", "sta", "str", "con", "pas", "sho", "tac", "pos_id"]
PLAYER_ID_COLS = ["id", "fname", "lname"]

INT_FIELDS = {"id", "rate", "hgt", "spe", "acc", "sta", "str", "con", "pas",
       "sho", "tac", "prc", "version", "pos_id", "status"}

# Computed / auxiliary columns (hidden by default)
# prc is auto-computed from price_map — shown as aux, not editable
AUX_COLS_DATA  = ["prc", "pos_id", "price_id"]
AUX_COLS_SPECIAL = ["pos_id", "price_id"]

# pos -> pos_id mapping
POS_ID = {
  "CF": 4, "SS": 4, "LW": 4, "RW": 4,
  "LM": 3, "RM": 3, "RWB": 3, "LWB": 3, "CM": 3, "DM": 3, "AM": 3,
  "LB": 2, "CB": 2, "RB": 2,
  "GK": 1,
}


def get_pos_id(row):
  return POS_ID.get(row.get("pos", ""), 0)


def get_price_id(row):
  rate = row.get("rate", 0)
  pid = get_pos_id(row)
  try:
    return int(str(int(rate)) + str(pid))
  except (ValueError, TypeError):
    return 0


def get_price(row):
  """Get price from price_map based on price_id."""
  price_id = get_price_id(row)
  return price_map.get(price_id, 0)


def get_status(row):
  """Read status directly from row; default to 1 if missing."""
  return row.get("status", 1)


def default_sort_key(row):
  """Sort key: price_id desc, pos asc, lname asc → negate price_id for desc."""
  return (-get_price_id(row), row.get("pos", ""), row.get("lname", ""))


def setup_styles():
  style = ttk.Style()
  style.theme_use("clam")
  style.configure("Treeview",
          rowheight=23, font=("Segoe UI", 9),
          relief="solid", borderwidth=1,
          background="#ffffff", fieldbackground="#ffffff")
  style.configure("Treeview.Heading",
          font=("Segoe UI", 9, "bold"),
          background="#c0c0c0", relief="solid", borderwidth=1)
  style.map("Treeview",
       background=[("selected", "#3399ff")],
       foreground=[("selected", "white")])


def _cast(raw):
  result = {}
  for col, val in raw.items():
    if col in INT_FIELDS:
      try:
        result[col] = int(val)
      except (ValueError, TypeError):
        result[col] = val
    else:
      result[col] = val
  return result


# ── Edit dialog ───────────────────────────────────────────────────────────────
class EditDialog(tk.Toplevel):
  def __init__(self, parent, row_data, columns):
    super().__init__(parent)
    self.title("Edit Row")
    self.result = None
    self.resizable(False, False)

    canvas = tk.Canvas(self)
    sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame = ttk.Frame(canvas, padding=10)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    self.entries = {}
    self._entry_widgets = []   # ordered list of Entry widgets for arrow-key nav

    for i, col in enumerate(columns):
      ttk.Label(frame, text=col, width=10, anchor="e").grid(row=i, column=0, padx=4, pady=2, sticky="e")
      var = tk.StringVar(value=str(row_data.get(col, "")))
      e = ttk.Entry(frame, textvariable=var, width=30)
      e.grid(row=i, column=1, padx=4, pady=2)
      self.entries[col] = var
      self._entry_widgets.append(e)

    # prc preview row (read-only)
    prc_row = len(columns)
    ttk.Label(frame, text="prc", width=10, anchor="e",
              foreground="#888888").grid(row=prc_row, column=0, padx=4, pady=2, sticky="e")
    self._prc_var = tk.StringVar(value="")
    prc_lbl = ttk.Label(frame, textvariable=self._prc_var,
                        foreground="#0055cc", font=("Segoe UI", 9, "bold"))
    prc_lbl.grid(row=prc_row, column=1, padx=4, pady=2, sticky="w")

    bf = ttk.Frame(frame)
    bf.grid(row=prc_row + 1, column=0, columnspan=2, pady=8)
    ttk.Button(bf, text="Save", command=self._save).pack(side="left", padx=4)
    ttk.Button(bf, text="Cancel", command=self.destroy).pack(side="left", padx=4)

    # Arrow-key navigation
    for idx, widget in enumerate(self._entry_widgets):
      widget.bind("<Up>",   lambda e, i=idx: self._nav(i - 1))
      widget.bind("<Down>", lambda e, i=idx: self._nav(i + 1))

    # Realtime prc preview — update when rate or pos changes
    for col in ("rate", "pos"):
      if col in self.entries:
        self.entries[col].trace_add("write", lambda *_: self._update_prc_preview())
    self._update_prc_preview()

    frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    self.geometry(f"320x{min(frame.winfo_reqheight()+20, 600)}")
    self.grab_set()
    self.wait_window()

  def _nav(self, idx):
    if 0 <= idx < len(self._entry_widgets):
      self._entry_widgets[idx].focus_set()

  def _update_prc_preview(self):
    try:
      rate = int(self.entries["rate"].get())
    except (ValueError, KeyError):
      self._prc_var.set("—")
      return
    pos = self.entries.get("pos", tk.StringVar()).get().strip() if "pos" in self.entries else ""
    pos_id = POS_ID.get(pos, 0)
    try:
      price_id = int(str(rate) + str(pos_id))
    except (ValueError, TypeError):
      self._prc_var.set("—")
      return
    prc = price_map.get(price_id, 0)
    self._prc_var.set(str(prc) if prc else "0 (not in map)")

  def _save(self):
    self.result = {col: var.get() for col, var in self.entries.items()}
    self.destroy()


# ── TreeTable ─────────────────────────────────────────────────────────────────
class TreeTable(ttk.Frame):
  def __init__(self, parent, base_columns, aux_cols, data_ref,
         on_data_change=None, default_sort=False, master_data=None):
    super().__init__(parent)
    self.base_columns = base_columns
    self.aux_cols   = aux_cols
    self.data_ref   = data_ref
    self.master_data  = master_data # full list to write edits back to
    self.on_data_change = on_data_change
    self.default_sort = default_sort
    self._show_aux   = False
    self._active_cols = list(base_columns)
    self.filtered   = []
    self._sort_col   = None
    self._sort_reverse = False
    self._col_filters = {} # col -> StringVar
    self._build()

  # ── build UI ──────────────────────────────────────────────────────────────
  def _build(self):
    top = ttk.Frame(self)
    top.pack(fill="x", padx=4, pady=3)
    self._aux_btn = ttk.Button(top, text="Show aux columns", command=self._toggle_aux)
    self._aux_btn.pack(side="left", padx=4)
    ttk.Button(top, text="Clear filters", command=self._clear_filters).pack(side="left", padx=4)
    self.status_lbl = ttk.Label(top, text="")
    self.status_lbl.pack(side="left", padx=8)
    container = ttk.Frame(self)
    container.pack(fill="both", expand=True, padx=4, pady=2)

    # Filter row sits INSIDE container, above the treeview, in same grid
    self._filter_frame = tk.Frame(container, bg="#f5f5f5")
    self._filter_frame.grid(row=0, column=0, sticky="ew")

    self.tree = ttk.Treeview(container, columns=self._active_cols,
                 show="headings", selectmode="browse")
    self._configure_columns()

    vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
    hsb = ttk.Scrollbar(container, orient="horizontal", command=self._on_hscroll)
    self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    self.tree.grid(row=1, column=0, sticky="nsew")
    vsb.grid(row=1, column=1, sticky="ns")
    hsb.grid(row=2, column=0, sticky="ew")
    container.rowconfigure(1, weight=1)
    container.columnconfigure(0, weight=1)

    self.tree.tag_configure("odd",    background="#e8e8e8")
    self.tree.tag_configure("even",    background="#ffffff")
    self.tree.tag_configure("odd_active", background="#d0d0d0", font=("Segoe UI", 9, "bold"))
    self.tree.tag_configure("even_active", background="#f0f0f0", font=("Segoe UI", 9, "bold"))
    self.tree.bind("<Double-Button-1>", self._on_double_click)
    self.tree.bind("<Configure>", lambda e: self.after(10, self._sync_filter_widths))
    self.tree.bind("<ButtonRelease-1>", lambda e: self.after(10, self._sync_filter_widths))

  def _on_hscroll(self, *args):
    self.tree.xview(*args)

  def _build_filter_row(self):
    for w in self._filter_frame.winfo_children():
      w.destroy()
    self._col_filters = {}
    for col in self._active_cols:
      var = tk.StringVar()
      var.trace_add("write", lambda *_, c=col: self.refresh())
      frame = tk.Frame(self._filter_frame, bg="#f5f5f5")
      frame.pack(side="left")
      e = tk.Entry(frame, textvariable=var, font=("Segoe UI", 8, "italic"),
             fg="#aaaaaa", relief="flat", bd=1,
             highlightthickness=1, highlightbackground="#cccccc")
      e.pack(fill="both", expand=True)
      # placeholder behaviour
      placeholder = col
      def on_focus_in(event, entry=e, var=var, ph=placeholder):
        if entry.cget("fg") == "#aaaaaa" and var.get() == ph:
          var.set("")
          entry.config(fg="#000000", font=("Segoe UI", 8))
      def on_focus_out(event, entry=e, var=var, ph=placeholder):
        if var.get() == "":
          var.set(ph)
          entry.config(fg="#aaaaaa", font=("Segoe UI", 8, "italic"))
      # initialise with placeholder
      var.set(placeholder)
      e.bind("<FocusIn>", on_focus_in)
      e.bind("<FocusOut>", on_focus_out)
      self._col_filters[col] = (var, e, placeholder)
    self.after(50, self._sync_filter_widths)

  def _sync_filter_widths(self):
    for col, (var, entry, _) in self._col_filters.items():
      try:
        px = self.tree.column(col, "width")
        f = entry.master
        f.config(width=px, height=22)
        f.pack_propagate(False)
        entry.config(width=px)
      except Exception:
        pass

  def _clear_filters(self):
    for col, (var, entry, placeholder) in self._col_filters.items():
      var.set(placeholder)
      entry.config(fg="#aaaaaa", font=("Segoe UI", 8, "italic"))
    self.refresh()

  def _toggle_aux(self):
    self._show_aux = not self._show_aux
    if self._show_aux:
      self._active_cols = self.base_columns + [c for c in self.aux_cols
                           if c not in self.base_columns]
      self._aux_btn.config(text="Hide aux columns")
    else:
      self._active_cols = list(self.base_columns)
      self._aux_btn.config(text="Show aux columns")
    self._configure_columns()
    self._repopulate()

  def _configure_columns(self):
    self.tree.configure(columns=self._active_cols)
    for col in self._active_cols:
      w = 90 if col in ("fname", "lname", "nat", "club", "type") else 60
      # heading command intentionally empty — sort triggered by double-click
      self.tree.heading(col, text=col, command=lambda: None)
      self.tree.column(col, width=w, minwidth=36, anchor="center")
    self._build_filter_row()

  def _on_double_click(self, event):
    region = self.tree.identify_region(event.x, event.y)
    if region == "heading":
      col_id = self.tree.identify_column(event.x)
      try:
        col = self._active_cols[int(col_id.replace("#", "")) - 1]
      except (ValueError, IndexError):
        return
      self._sort(col)
      return
    self._on_double_click_row(event)

  # ── filtering ─────────────────────────────────────────────────────────────
  def _matches(self, row):
    """Return True if row passes all active column filters."""
    for col, (var, entry, placeholder) in self._col_filters.items():
      raw = var.get().strip()
      if not raw or raw == placeholder:
        continue
      terms = [t.strip() for t in raw.split(";") if t.strip()]
      if not terms:
        continue
      if col == "pos_id":  cell = str(get_pos_id(row))
      elif col == "price_id": cell = str(get_price_id(row))
      elif col == "prc":   cell = str(get_price(row))
      elif col == "status": cell = str(get_status(row))
      else:         cell = str(row.get(col, ""))
      cell = cell.lower()
      if not any(t.lower() in cell for t in terms):
        return False
    return True

  # ── data helpers ──────────────────────────────────────────────────────────
  def _row_vals(self, row):
    vals = []
    for c in self._active_cols:
      if c == "pos_id":   vals.append(get_pos_id(row))
      elif c == "price_id": vals.append(get_price_id(row))
      elif c == "prc":    vals.append(get_price(row))
      elif c == "status":  vals.append(get_status(row))
      else:          vals.append(row.get(c, ""))
    return vals

  def refresh(self):
    self.filtered = [r for r in self.data_ref if self._matches(r)]
    # Only apply default sort if no manual sort has been set
    if self.default_sort and self._sort_col is None:
      self.filtered.sort(key=default_sort_key)
    elif self._sort_col is not None:
      col = self._sort_col
      def key(r):
        if col == "pos_id": return get_pos_id(r)
        if col == "price_id": return get_price_id(r)
        if col == "prc": return get_price(r)
        if col == "status": return get_status(r)
        return r.get(col, "")
      try:
        self.filtered.sort(key=lambda r: (key(r) is None, key(r)),
                  reverse=self._sort_reverse)
      except TypeError:
        self.filtered.sort(key=lambda r: str(key(r)), reverse=self._sort_reverse)
    self._repopulate()

  def reset_sort(self):
    """Reset to default sort (called when switching away from this tab)."""
    self._sort_col = None
    self._sort_reverse = False

  def _repopulate(self):
    self.tree.delete(*self.tree.get_children())
    for idx, row in enumerate(self.filtered):
      is_active = get_status(row) == 1
      if is_active:
        tag = "even_active" if idx % 2 == 0 else "odd_active"
      else:
        tag = "even" if idx % 2 == 0 else "odd"
      self.tree.insert("", "end", iid=str(idx),
               values=self._row_vals(row), tags=(tag,))
    self.status_lbl.config(text=f"{len(self.filtered)} / {len(self.data_ref)} rows")

  def _on_double_click_row(self, event):
    sel = self.tree.selection()
    if not sel:
      return
    row = self.filtered[int(sel[0])]
    target = self.master_data if self.master_data is not None else self.data_ref
    data_idx = next((i for i, r in enumerate(target) if r is row), None)
    if data_idx is None:
      return
    dlg = EditDialog(self, row, self.base_columns)
    if dlg.result:
      # Merge edited fields into a copy of the original row
      # so fields not shown in the dialog (e.g. "version") are preserved
      new_row = dict(row)
      new_row.update(_cast(dlg.result))
      target[data_idx] = new_row
      # Also update data_ref if it's a filtered sub-list (version tab)
      if self.master_data is not None:
        ref_idx = next((i for i, r in enumerate(self.data_ref) if r is row), None)
        if ref_idx is not None:
          self.data_ref[ref_idx] = new_row
      if self.on_data_change:
        self.on_data_change()
      else:
        self.refresh()

  def _sort(self, col):
    if self._sort_col == col:
      self._sort_reverse = not self._sort_reverse
    else:
      self._sort_col = col
      self._sort_reverse = False
    self.refresh()


# ── Rename entry ──────────────────────────────────────────────────────────────
class RenameEntry(tk.Entry):
  def __init__(self, nb, tab_id, current_text, on_rename):
    super().__init__(nb, font=("Segoe UI", 9), width=12)
    self._nb = nb
    self._tab_id = tab_id
    self._on_rename = on_rename
    self.insert(0, current_text.strip())
    self.select_range(0, "end")
    self.bind("<Return>", self._commit)
    self.bind("<Escape>", lambda e: self.destroy())
    self.bind("<FocusOut>", self._commit)
    try:
      x, y, w, h = nb.bbox(tab_id)
      self.place(in_=nb, x=x, y=y, width=max(w, 80), height=h)
    except Exception:
      self.destroy()
      return
    self.focus_set()

  def _commit(self, event=None):
    new_name = self.get().strip()
    if new_name:
      self._on_rename(self._tab_id, new_name)
    self.destroy()


# ── VersionTab ────────────────────────────────────────────────────────────────
class VersionTab(ttk.Frame):
  """One tab per version file (e.g. 20231.json). Loads lazily on first focus."""

  def __init__(self, parent, ver, player_id_tab_ref):
    super().__init__(parent)
    self.ver = ver                        # int or str version value
    self.label = str(ver)
    self.filepath = ver_file(ver)
    self.player_id_tab_ref = player_id_tab_ref  # callable returning PlayerIDTab
    self.data = None                      # None = not yet loaded
    self._tbl = None
    self._build_skeleton()

  # ── skeleton shown before first load ──────────────────────────────────────
  def _build_skeleton(self):
    self._top = ttk.Frame(self)
    self._top.pack(fill="x", padx=6, pady=4)
    ttk.Button(self._top, text="Add Row",    command=self._add_row).pack(side="left", padx=4)
    ttk.Button(self._top, text="Delete Row",  command=self._delete_row).pack(side="left", padx=4)
    ttk.Button(self._top, text="Save File",   command=self._save).pack(side="right", padx=4)
    self._table_frame = ttk.Frame(self)
    self._table_frame.pack(fill="both", expand=True, padx=4, pady=2)

  # ── lazy load ─────────────────────────────────────────────────────────────
  def ensure_loaded(self):
    if self.data is not None:
      return
    if os.path.exists(self.filepath):
      with open(self.filepath, encoding="utf-8") as f:
        self.data = json.load(f)
    else:
      self.data = []
    self._tbl = TreeTable(
      self._table_frame, DATA_COLS_VER, AUX_COLS_DATA, self.data,
      default_sort=True)
    self._tbl.pack(fill="both", expand=True)
    self._tbl.refresh()

  # ── helpers ───────────────────────────────────────────────────────────────
  def _pid_tab(self):
    return self.player_id_tab_ref()

  def _add_row(self):
    self.ensure_loaded()
    # Edit cols: DATA_COLS_VER minus status (auto-default 1)
    edit_cols = [c for c in DATA_COLS_VER if c != "status"]
    empty = {c: 0 if c in INT_FIELDS else "" for c in edit_cols}
    dlg = EditDialog(self, empty, edit_cols)
    if not dlg.result:
      return
    new_row = _cast(dlg.result)
    new_row.setdefault("status", 1)
    new_row["version"] = self.ver
    fname = new_row.get("fname", "").strip()
    lname = new_row.get("lname", "").strip()
    pid_tab = self._pid_tab()
    pid = pid_tab.lookup_id(fname, lname) if pid_tab else None
    if pid is None:
      ans = messagebox.askyesno(
        "Player not found",
        f'No ID found for "{fname} {lname}".\n\n'
        f'Register this player in the Player ID list?\n'
        f'(A new 4-digit ID will be assigned automatically.)'
      )
      if ans and pid_tab:
        pid = pid_tab.add_player(fname, lname)
      else:
        pid = 0
    new_row["id"] = pid
    self.data.append(new_row)
    self._tbl.refresh()

  def _delete_row(self):
    self.ensure_loaded()
    sel = self._tbl.tree.selection()
    if not sel:
      messagebox.showwarning("No selection", "Please select a row to delete.")
      return
    row = self._tbl.filtered[int(sel[0])]
    if messagebox.askyesno("Confirm", "Delete selected row?"):
      self.data.remove(row)
      self._tbl.refresh()

  def _save(self):
    self.ensure_loaded()
    pid_tab = self._pid_tab()
    if pid_tab:
      missing = [f"{r.get('fname','')} {r.get('lname','')}".strip()
            for r in self.data if not r.get("id")]
      if missing:
        names = "\n".join(f" • {n}" for n in missing[:10])
        if len(missing) > 10:
          names += f"\n ... and {len(missing)-10} more"
        if not messagebox.askyesno("Missing IDs",
            f"These players have no valid ID:\n{names}\n\nSave anyway?"):
          return
    EXCLUDE = {"pos_id", "price_id"}
    ordered = []
    for row in self.data:
      out = {}
      for col in DATA_SAVE_COLS:
        if col in EXCLUDE:
          continue
        if col == "prc":
          out["prc"] = get_price(row)   # always compute from price_map
        elif col in row:
          out[col] = row[col]
      for k, v in row.items():
        if k not in out and k not in EXCLUDE and k != "prc":
          out[k] = v
      ordered.append(out)
    with open(self.filepath, "w", encoding="utf-8") as f:
      json.dump(ordered, f, ensure_ascii=False, indent=4)
    messagebox.showinfo("Saved", f"Saved to {os.path.basename(self.filepath)}")


# ── DataTab ───────────────────────────────────────────────────────────────────
class DataTab(ttk.Frame):
  """Container tab that holds one VersionTab per version file found in BASE_DIR."""

  def __init__(self, parent):
    super().__init__(parent)
    self.player_id_tab = None   # set by App after construction
    self._ver_tabs = {}         # label -> VersionTab
    self._build()

  def _get_pid_tab(self):
    return self.player_id_tab

  def _build(self):
    self.nb = ttk.Notebook(self)
    self.nb.pack(fill="both", expand=True)
    self.nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    self._load_version_tabs()

  def _scan_versions(self):
    """Return sorted list of version values found as <ver>.json in BASE_DIR."""
    vers = []
    for fname in os.listdir(BASE_DIR):
      if fname.endswith(".json"):
        stem = fname[:-5]
        try:
          vers.append(int(stem))
        except ValueError:
          pass  # skip non-numeric filenames (special.json, player_id.json, etc.)
    return sorted(vers)

  def _load_version_tabs(self):
    for ver in self._scan_versions():
      label = str(ver)
      frame = VersionTab(self.nb, ver, self._get_pid_tab)
      self.nb.add(frame, text=f" {label} ")
      self._ver_tabs[label] = frame
    # Select last (most recent) tab
    tabs = self.nb.tabs()
    if tabs:
      self.nb.select(tabs[-1])

  def _active_ver_tab(self):
    try:
      tab_id = self.nb.select()
      label = self.nb.tab(tab_id, "text").strip()
      return self._ver_tabs.get(label)
    except Exception:
      return None

  def _on_tab_changed(self, event):
    """Lazy-load the version tab when it is first selected."""
    vt = self._active_ver_tab()
    if vt:
      vt.ensure_loaded()

  # Expose a flat list of all loaded data for PlayerIDTab compatibility
  @property
  def data(self):
    result = []
    for vt in self._ver_tabs.values():
      if vt.data is not None:
        result.extend(vt.data)
    return result


# ── SpecialTab ────────────────────────────────────────────────────────────────
class SpecialTab(ttk.Frame):
  def __init__(self, parent):
    super().__init__(parent)
    self.data = []
    with open(SPECIAL_FILE, encoding="utf-8") as f:
      self.data = json.load(f)
    self._build()

  def _build(self):
    top = ttk.Frame(self)
    top.pack(fill="x", padx=6, pady=4)
    ttk.Button(top, text="Add Row",  command=self._add_row).pack(side="left", padx=4)
    ttk.Button(top, text="Delete Row", command=self._delete_row).pack(side="left", padx=4)
    ttk.Button(top, text="Save File", command=self._save).pack(side="right", padx=4)

    self.tbl = TreeTable(self, SPECIAL_COLS, AUX_COLS_SPECIAL, self.data,
               default_sort=True)
    self.tbl.pack(fill="both", expand=True, padx=4, pady=2)
    self.tbl.refresh()

  def _add_row(self):
    empty = {c: 0 if c in INT_FIELDS else "" for c in SPECIAL_COLS}
    dlg = EditDialog(self, empty, SPECIAL_COLS)
    if dlg.result:
      self.data.append(_cast(dlg.result))
      self.tbl.refresh()

  def _delete_row(self):
    sel = self.tbl.tree.selection()
    if not sel:
      messagebox.showwarning("No selection", "Please select a row to delete.")
      return
    row = self.tbl.filtered[int(sel[0])]
    if messagebox.askyesno("Confirm", "Delete selected row?"):
      self.data.remove(row)
      self.tbl.refresh()

  def _save(self):
    with open(SPECIAL_FILE, "w", encoding="utf-8") as f:
      json.dump(self.data, f, ensure_ascii=False, indent=4)
    messagebox.showinfo("Saved", "Saved to special.json")


# ── PlayerIDTab ───────────────────────────────────────────────────────────────
class PlayerIDTab(ttk.Frame):
  def __init__(self, parent, data_source):
    super().__init__(parent)
    self.data_source = data_source
    self.data = []
    self._load()
    self._build()

  def _load(self):
    if os.path.exists(PLAYER_ID_FILE):
      with open(PLAYER_ID_FILE, encoding="utf-8") as f:
        loaded = json.load(f)
      self.data.clear()
      self.data.extend(loaded)
    else:
      self._rebuild_from_source()

  def _rebuild_from_source(self):
    """Rebuild player_id list by scanning all version JSON files directly."""
    import glob
    seen = {}
    for fpath in sorted(glob.glob(os.path.join(BASE_DIR, "*.json"))):
      stem = os.path.basename(fpath)[:-5]
      try:
        int(stem)
      except ValueError:
        continue  # skip special.json, player_id.json, etc.
      with open(fpath, encoding="utf-8") as f:
        rows = json.load(f)
      for row in rows:
        pid = row.get("id")
        if pid is not None and pid not in seen:
          seen[pid] = {"id": pid,
                 "fname": row.get("fname", ""),
                 "lname": row.get("lname", "")}
    self.data.clear()
    self.data.extend(sorted(seen.values(), key=lambda r: r["id"]))

  def _next_id(self):
    used = {r["id"] for r in self.data if isinstance(r.get("id"), int)}
    i = 1000
    while i in used:
      i += 1
    if i > 9999:
      raise ValueError("No available 4-digit IDs left.")
    return i

  def lookup_id(self, fname, lname):
    fname, lname = fname.strip(), lname.strip()
    for r in self.data:
      if r.get("fname", "").strip() == fname and r.get("lname", "").strip() == lname:
        return r["id"]
    return None

  def add_player(self, fname, lname):
    new_id = self._next_id()
    self.data.append({"id": new_id, "fname": fname.strip(), "lname": lname.strip()})
    self.tbl.refresh()
    return new_id

  def _build(self):
    top = ttk.Frame(self)
    top.pack(fill="x", padx=6, pady=4)
    ttk.Button(top, text="Add Player",    command=self._add_row).pack(side="left", padx=4)
    ttk.Button(top, text="Delete Row",    command=self._delete_row).pack(side="left", padx=4)
    ttk.Button(top, text="Rebuild from data", command=self._on_rebuild).pack(side="left", padx=4)
    ttk.Button(top, text="Save File",    command=self._save).pack(side="right", padx=4)

    self.tbl = TreeTable(self, PLAYER_ID_COLS, [], self.data)
    self.tbl.pack(fill="both", expand=True, padx=4, pady=2)
    self.tbl.refresh()

  def _on_rebuild(self):
    if messagebox.askyesno("Rebuild", "Rebuild player ID list from data.json?\nThis will overwrite current edits."):
      self._rebuild_from_source()
      self.tbl.refresh()

  def _add_row(self):
    dlg = EditDialog(self, {"fname": "", "lname": ""}, ["fname", "lname"])
    if dlg.result:
      fname = dlg.result.get("fname", "").strip()
      lname = dlg.result.get("lname", "").strip()
      if not lname:
        messagebox.showwarning("Missing name", "Last name (lname) is required.")
        return
      try:
        new_id = self._next_id()
      except ValueError as e:
        messagebox.showerror("Error", str(e))
        return
      self.data.append({"id": new_id, "fname": fname, "lname": lname})
      self.tbl.refresh()

  def _delete_row(self):
    sel = self.tbl.tree.selection()
    if not sel:
      messagebox.showwarning("No selection", "Please select a row to delete.")
      return
    row = self.tbl.filtered[int(sel[0])]
    if messagebox.askyesno("Confirm", "Delete selected row?"):
      self.data.remove(row)
      self.tbl.refresh()

  def _save(self):
    with open(PLAYER_ID_FILE, "w", encoding="utf-8") as f:
      json.dump(self.data, f, ensure_ascii=False, indent=4)
    messagebox.showinfo("Saved", "Saved to player_id.json")


# ── PriceMapTab ───────────────────────────────────────────────────────────────
class PriceMapTab(ttk.Frame):
  """Tab to view and edit price_map.json as a 2-column table (price_id, price)."""

  def __init__(self, parent):
    super().__init__(parent)
    self._data = []   # list of {"price_id": int, "price": int}
    self._load()
    self._build()

  def _load(self):
    with open(PRICE_MAP_FILE, encoding="utf-8") as f:
      raw = json.load(f)
    self._data = [{"price_id": int(k), "price": v}
            for k, v in sorted(raw.items(), key=lambda x: int(x[0]), reverse=True)]

  def _build(self):
    top = ttk.Frame(self)
    top.pack(fill="x", padx=6, pady=4)
    ttk.Button(top, text="Add Row",   command=self._add_row).pack(side="left", padx=4)
    ttk.Button(top, text="Delete Row", command=self._delete_row).pack(side="left", padx=4)
    ttk.Button(top, text="Save File",  command=self._save).pack(side="right", padx=4)

    container = ttk.Frame(self)
    container.pack(fill="both", expand=True, padx=6, pady=2)

    cols = ("price_id", "price")
    self._tree = ttk.Treeview(container, columns=cols, show="headings", selectmode="browse")
    self._tree.heading("price_id", text="price_id")
    self._tree.heading("price",    text="price")
    self._tree.column("price_id", width=120, anchor="center")
    self._tree.column("price",    width=120, anchor="center")

    vsb = ttk.Scrollbar(container, orient="vertical",   command=self._tree.yview)
    hsb = ttk.Scrollbar(container, orient="horizontal", command=self._tree.xview)
    self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    self._tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)

    self._tree.tag_configure("odd",  background="#e8e8e8")
    self._tree.tag_configure("even", background="#ffffff")
    self._tree.tag_configure("zero", background="#ffe0e0")  # highlight price=0

    self._tree.bind("<Double-Button-1>", self._on_double_click)
    self._repopulate()

  def _repopulate(self):
    self._tree.delete(*self._tree.get_children())
    for idx, row in enumerate(self._data):
      prc = row["price"]
      if prc == 0:
        tag = "zero"
      else:
        tag = "even" if idx % 2 == 0 else "odd"
      self._tree.insert("", "end", iid=str(idx),
                values=(row["price_id"], prc), tags=(tag,))

  def _on_double_click(self, event):
    sel = self._tree.selection()
    if not sel:
      return
    idx = int(sel[0])
    row = self._data[idx]
    dlg = EditDialog(self, row, ["price_id", "price"])
    if dlg.result:
      try:
        self._data[idx] = {
          "price_id": int(dlg.result["price_id"]),
          "price":    int(dlg.result["price"]),
        }
      except ValueError:
        messagebox.showerror("Invalid", "price_id and price must be integers.")
        return
      # Reload global price_map so prc preview in EditDialog stays in sync
      price_map.clear()
      price_map.update({r["price_id"]: r["price"] for r in self._data})
      self._repopulate()

  def _add_row(self):
    dlg = EditDialog(self, {"price_id": 0, "price": 0}, ["price_id", "price"])
    if dlg.result:
      try:
        entry = {
          "price_id": int(dlg.result["price_id"]),
          "price":    int(dlg.result["price"]),
        }
      except ValueError:
        messagebox.showerror("Invalid", "price_id and price must be integers.")
        return
      self._data.append(entry)
      self._data.sort(key=lambda r: r["price_id"], reverse=True)
      price_map[entry["price_id"]] = entry["price"]
      self._repopulate()

  def _delete_row(self):
    sel = self._tree.selection()
    if not sel:
      messagebox.showwarning("No selection", "Please select a row to delete.")
      return
    idx = int(sel[0])
    row = self._data[idx]
    if messagebox.askyesno("Confirm", f"Delete price_id {row['price_id']}?"):
      price_map.pop(row["price_id"], None)
      self._data.pop(idx)
      self._repopulate()

  def _save(self):
    out = {str(r["price_id"]): r["price"]
           for r in sorted(self._data, key=lambda r: r["price_id"], reverse=True)}
    with open(PRICE_MAP_FILE, "w", encoding="utf-8") as f:
      json.dump(out, f, ensure_ascii=False, indent=4)
    messagebox.showinfo("Saved", "Saved to price_map.json")


# ── App ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("DLS Stats Editor")
    self.state("zoomed")  # full screen (maximized) on startup
    setup_styles()

    nb = ttk.Notebook(self)
    nb.pack(fill="both", expand=True)
    data_tab = DataTab(nb)
    # Pass a callable so PlayerIDTab always sees the latest loaded data
    pid_tab = PlayerIDTab(nb, lambda: data_tab.data)
    data_tab.player_id_tab = pid_tab
    nb.add(data_tab,        text=" data.json ")
    nb.add(SpecialTab(nb),  text=" special.json ")
    nb.add(pid_tab,         text=" playerID ")
    nb.add(PriceMapTab(nb), text=" Price Map ")


if __name__ == "__main__":
  App().mainloop()