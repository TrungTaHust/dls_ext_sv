import json
import copy
import re
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
    if col == "pos":
      result[col] = str(val).upper()
    elif col in INT_FIELDS:
      try:
        result[col] = int(val)
      except (ValueError, TypeError):
        result[col] = val
    else:
      result[col] = val
  return result


# ── Edit dialog ───────────────────────────────────────────────────────────────
class EditDialog(tk.Toplevel):
  def __init__(self, parent, row_data, columns, pid_lookup=None):
    """
    pid_lookup: callable(fname, lname) -> id | None  — for auto-mapping player ID
    """
    super().__init__(parent)
    self.title("Edit Row")
    self.result = None
    self.resizable(False, False)
    self._pid_lookup = pid_lookup

    # Validator: only allow printable ASCII (0x20–0x7E)
    vcmd = (self.register(lambda s: all(0x20 <= ord(c) <= 0x7E for c in s)), "%P")

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
      # id is read-only when pid_lookup is available (auto-mapped)
      if col == "id" and self._pid_lookup:
        lbl = ttk.Label(frame, textvariable=var,
                        foreground="#007700", font=("Segoe UI", 9, "bold"))
        lbl.grid(row=i, column=1, padx=4, pady=2, sticky="w")
        self._id_entry = lbl
        # still need a dummy widget for arrow-key nav slot
        self._entry_widgets.append(None)
      else:
        e = ttk.Entry(frame, textvariable=var, width=30,
                      validate="key", validatecommand=vcmd)
        e.grid(row=i, column=1, padx=4, pady=2)
        # Select all on focus for numeric fields so typing replaces old value
        if col in INT_FIELDS:
          e.bind("<FocusIn>", lambda ev, w=e: w.after(0, lambda: (w.selection_range(0, "end"), w.icursor("end"))))
        # Auto-uppercase pos on FocusOut and Return
        if col == "pos":
          def _upper_pos(ev, v=var): v.set(v.get().upper())
          e.bind("<FocusOut>", _upper_pos)
          e.bind("<Return>",   _upper_pos)
        if col == "id":
          self._id_entry = e
        self._entry_widgets.append(e)
      self.entries[col] = var

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

    # Arrow-key navigation (skip None slots for read-only fields)
    for idx, widget in enumerate(self._entry_widgets):
      if widget is None:
        continue
      widget.bind("<Up>",   lambda e, i=idx: self._nav(i - 1))
      widget.bind("<Down>", lambda e, i=idx: self._nav(i + 1))

    # Realtime prc preview — update when rate or pos changes
    for col in ("rate", "pos"):
      if col in self.entries:
        self.entries[col].trace_add("write", lambda *_: self._update_prc_preview())
    self._update_prc_preview()

    # Realtime id auto-map — update when fname or lname changes
    if self._pid_lookup and "id" in self.entries:
      for col in ("fname", "lname"):
        if col in self.entries:
          self.entries[col].trace_add("write", lambda *_: self._update_id_preview())
      self._update_id_preview()

    frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    self.geometry(f"320x{min(frame.winfo_reqheight()+20, 600)}")
    self.grab_set()
    self.wait_window()

  def _nav(self, idx):
    # Step over None slots (read-only fields) in the direction of travel
    direction = 1 if idx >= 0 else -1
    while 0 <= idx < len(self._entry_widgets):
      if self._entry_widgets[idx] is not None:
        self._entry_widgets[idx].focus_set()
        return
      idx += direction

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

  def _update_id_preview(self):
    """Auto-fill id field from player_id lookup based on current fname/lname."""
    if not self._pid_lookup or "id" not in self.entries:
      return
    fname = self.entries.get("fname", tk.StringVar()).get().strip()
    lname = self.entries.get("lname", tk.StringVar()).get().strip()
    pid = self._pid_lookup(fname, lname)
    if pid is not None:
      self.entries["id"].set(str(pid))
      if hasattr(self, "_id_entry"):
        self._id_entry.config(foreground="#007700")
    else:
      self.entries["id"].set("—")
      if hasattr(self, "_id_entry"):
        self._id_entry.config(foreground="#cc0000")

  def _save(self):
    vals = {col: var.get() for col, var in self.entries.items()}

    # ── status: only 0 or 1 ──────────────────────────────────────────────────
    if "status" in vals:
      if vals["status"] not in ("0", "1"):
        messagebox.showerror("Invalid", "status must be 0 or 1.")
        return

    # ── rate + 8 sub-stats <= 100 ────────────────────────────────────────────
    CAPPED = {"rate", "spe", "acc", "sta", "str", "con", "pas", "sho", "tac"}
    for col in CAPPED:
      if col not in vals:
        continue
      try:
        v = int(vals[col])
      except ValueError:
        messagebox.showerror("Invalid", f"'{col}' must be an integer.")
        return
      if v > 100:
        messagebox.showerror("Invalid", f"'{col}' must be ≤ 100 (got {v}).")
        return

    self.result = vals
    self.destroy()


# ── TreeTable ─────────────────────────────────────────────────────────────────
class TreeTable(ttk.Frame):
  def __init__(self, parent, base_columns, aux_cols, data_ref,
         on_data_change=None, default_sort=False, master_data=None,
         pid_lookup=None):
    super().__init__(parent)
    self.base_columns = base_columns
    self.aux_cols   = aux_cols
    self.data_ref   = data_ref
    self.master_data  = master_data
    self.on_data_change = on_data_change
    self.default_sort = default_sort
    self.pid_lookup  = pid_lookup   # callable(fname, lname) -> id | None
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
    self._name_filter = None   # combined fname+lname filter

    # ASCII-only validator for filter entries
    vcmd = (self.tree.register(lambda s: all(0x20 <= ord(c) <= 0x7E for c in s)), "%P")

    for col in self._active_cols:
      var = tk.StringVar()
      var.trace_add("write", lambda *_, c=col: self.refresh())
      frame = tk.Frame(self._filter_frame, bg="#f5f5f5")
      frame.pack(side="left")

      if col == "fname":
        # Span fname+lname with a single "name" search box
        placeholder = "name"
        e = tk.Entry(frame, textvariable=var, font=("Segoe UI", 8, "italic"),
               fg="#aaaaaa", relief="flat", bd=1,
               highlightthickness=1, highlightbackground="#cccccc",
               validate="key", validatecommand=vcmd)
        e.pack(fill="both", expand=True)
        def on_focus_in(event, entry=e, var=var, ph=placeholder):
          if entry.cget("fg") == "#aaaaaa" and var.get() == ph:
            var.set("")
            entry.config(fg="#000000", font=("Segoe UI", 8))
        def on_focus_out(event, entry=e, var=var, ph=placeholder):
          if var.get() == "":
            var.set(ph)
            entry.config(fg="#aaaaaa", font=("Segoe UI", 8, "italic"))
        var.set(placeholder)
        e.bind("<FocusIn>", on_focus_in)
        e.bind("<FocusOut>", on_focus_out)
        self._name_filter = (var, e, placeholder)
        self._col_filters[col] = (var, e, placeholder)

      elif col == "lname":
        # lname column gets an invisible placeholder — filtered via _name_filter
        empty_var = tk.StringVar(value="")
        lbl = tk.Label(frame, bg="#f5f5f5")   # blank spacer
        lbl.pack(fill="both", expand=True)
        self._col_filters[col] = (empty_var, lbl, "")

      else:
        placeholder = col
        e = tk.Entry(frame, textvariable=var, font=("Segoe UI", 8, "italic"),
               fg="#aaaaaa", relief="flat", bd=1,
               highlightthickness=1, highlightbackground="#cccccc",
               validate="key", validatecommand=vcmd)
        e.pack(fill="both", expand=True)
        def on_focus_in(event, entry=e, var=var, ph=placeholder):
          if entry.cget("fg") == "#aaaaaa" and var.get() == ph:
            var.set("")
            entry.config(fg="#000000", font=("Segoe UI", 8))
        def on_focus_out(event, entry=e, var=var, ph=placeholder):
          if var.get() == "":
            var.set(ph)
            entry.config(fg="#aaaaaa", font=("Segoe UI", 8, "italic"))
        var.set(placeholder)
        e.bind("<FocusIn>", on_focus_in)
        e.bind("<FocusOut>", on_focus_out)
        self._col_filters[col] = (var, e, placeholder)

    self.after(50, self._sync_filter_widths)

  def _sync_filter_widths(self):
    fname_w = 0
    lname_w = 0
    for col, (var, entry, _) in self._col_filters.items():
      try:
        px = self.tree.column(col, "width")
      except Exception:
        continue
      if col == "fname":
        fname_w = px
      elif col == "lname":
        lname_w = px
      else:
        f = entry.master
        f.config(width=px, height=22)
        f.pack_propagate(False)
        entry.config(width=px)
    # name box spans fname + lname columns
    if self._name_filter and fname_w:
      var, entry, _ = self._name_filter
      total = fname_w + lname_w
      f = entry.master
      f.config(width=total, height=22)
      f.pack_propagate(False)
      entry.config(width=total)
    # blank lname spacer
    if "lname" in self._col_filters and lname_w:
      _, lbl, _ = self._col_filters["lname"]
      try:
        lbl.master.config(width=lname_w, height=22)
        lbl.master.pack_propagate(False)
      except Exception:
        pass

  def _clear_filters(self):
    if self._name_filter:
      var, entry, placeholder = self._name_filter
      var.set(placeholder)
      entry.config(fg="#aaaaaa", font=("Segoe UI", 8, "italic"))
    for col, (var, entry, placeholder) in self._col_filters.items():
      if col in ("fname", "lname"):
        continue
      var.set(placeholder)
      if isinstance(entry, tk.Entry):
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
    # Combined name filter (searches both fname and lname)
    if self._name_filter:
      var, _, placeholder = self._name_filter
      raw = var.get().strip()
      if raw and raw != placeholder:
        terms = [t.strip() for t in raw.split(";") if t.strip()]
        if terms:
          full_name = (str(row.get("fname", "")) + " " + str(row.get("lname", ""))).lower()
          if not any(t.lower() in full_name for t in terms):
            return False

    for col, (var, entry, placeholder) in self._col_filters.items():
      if col in ("fname", "lname"):
        continue   # handled above by _name_filter
      raw = var.get().strip()
      if not raw or raw == placeholder:
        continue
      terms = [t.strip() for t in raw.split(";") if t.strip()]
      if not terms:
        continue
      if col == "pos_id":   cell = str(get_pos_id(row))
      elif col == "price_id": cell = str(get_price_id(row))
      elif col == "prc":    cell = str(get_price(row))
      elif col == "status":  cell = str(get_status(row))
      else:          cell = str(row.get(col, ""))
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
    dlg = EditDialog(self, row, self.base_columns, pid_lookup=self.pid_lookup)
    if dlg.result:
      # Merge edited fields into a copy of the original row
      # so fields not shown in the dialog (e.g. "version") are preserved
      new_row = dict(row)
      new_row.update(_cast(dlg.result))
      # Auto-compute prc from price_map after edit
      new_row["prc"] = get_price(new_row)
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
      default_sort=True,
      pid_lookup=self.player_id_tab_ref().lookup_id if self.player_id_tab_ref() else None)
    self._tbl.pack(fill="both", expand=True)
    self._tbl.refresh()

  # ── helpers ───────────────────────────────────────────────────────────────
  def _pid_tab(self):
    return self.player_id_tab_ref()

  def _add_row(self):
    self.ensure_loaded()
    # Edit cols: DATA_COLS_VER minus status (auto-default 1)
    edit_cols = [c for c in DATA_COLS_VER if c != "status"]
    # Numeric fields default to empty string (not 0) so user types fresh values
    BLANK_FIELDS = {"rate", "hgt", "spe", "acc", "sta", "str", "con", "pas", "sho", "tac"}
    empty = {c: ("" if c in BLANK_FIELDS else (0 if c in INT_FIELDS else "")) for c in edit_cols}
    pid_tab = self._pid_tab()
    dlg = EditDialog(self, empty, edit_cols,
                     pid_lookup=pid_tab.lookup_id if pid_tab else None)
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


# ── helpers shared by Import & OCR ───────────────────────────────────────────
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
  if str(row.get("status", "1")) not in ("0", "1"):
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
  tree.tag_configure("ok",    background="#e8f5e9")
  tree.tag_configure("warn",  background="#fff9c4")
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
      if c == "prc":    vals.append(get_price(row))
      elif c == "errors": vals.append("; ".join(errs) if errs else "")
      else:          vals.append(row.get(c, ""))
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


# ── OCR helpers ───────────────────────────────────────────────────────────────
SCREENSHOT_MARKET = os.path.join(
  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
  "resources", "data", "screenshot", "market"
)

# Singleton PaddleOCR engine — initialised once on first use
_paddle_engine = None

def _ocr_available():
  try:
    from paddleocr import PaddleOCR  # noqa
    from PIL import Image             # noqa
    return True
  except ImportError:
    return False

def _get_paddle_engine():
  global _paddle_engine
  if _paddle_engine is None:
    import os as _os
    _os.environ["FLAGS_use_mkldnn"]      = "0"
    _os.environ["PADDLE_DISABLE_ONEDNN"] = "1"
    from paddleocr import PaddleOCR
    # PP-OCRv3 mobile: much faster than server, still accurate for game UI
    # use_angle_cls=False: game screenshots are never rotated → skip angle detection
    _paddle_engine = PaddleOCR(
      use_angle_cls=False,
      lang='en',
      enable_mkldnn=False,
      det_model_dir=None,   # use default mobile det
      rec_model_dir=None,   # use default mobile rec
    )
  return _paddle_engine

def _paddle_ocr_cell(cell_img):
  """Run PaddleOCR on a PIL image, return list of (text, conf)."""
  import numpy as np
  from PIL import Image
  SCALE = 2   # 2x sufficient for mobile model; 4x was overkill and slow
  w, h = cell_img.size
  arr = np.array(cell_img.resize((w * SCALE, h * SCALE), Image.LANCZOS))
  engine = _get_paddle_engine()
  result = engine.ocr(arr)
  lines = []
  if result:
    for item in result:
      if isinstance(item, dict):
        for t, s in zip(item.get('rec_texts', []), item.get('rec_scores', [])):
          if t.strip():
            lines.append((t.strip(), float(s)))
      elif isinstance(item, list):
        for ln in item:
          try:
            t, s = ln[1][0], ln[1][1]
            if t.strip():
              lines.append((t.strip(), float(s)))
          except (IndexError, TypeError):
            pass
  return lines

# Stat-label words to ignore when extracting names / pos
_STAT_LABELS = {
  'SPE','ACC','STA','STR','CON','PAS','SHO','TAC','GKR','GKH',
  'LEFT','RIGHT','LAST','CHANCE','LIVE','TOP','PICKS','TRANSFERS',
  'SCOUTS','AGENTS','MANAGE','PLAYERS','LOCKED',
}

def _parse_cell_lines(lines):
  """
  Parse (text, conf) lines from PaddleOCR into a player dict.
  Returns None if the cell looks like a banner.
  """
  texts = [t for t, _ in lines]
  full  = ' '.join(texts).upper()

  # Banner detection
  if any(k in full for k in ('TOP PICKS', 'LIVE TRANSFERS', 'LOCKED')):
    return None

  # Collect numbers
  nums = []
  for t, _ in lines:
    m = re.search(r'\b(\d{2,3})\b', t)
    if m:
      nums.append(int(m.group(1)))

  stat_nums = [n for n in nums if 10 <= n <= 100]
  if len(stat_nums) < 4:
    return None   # not enough stats → banner or empty

  # Stats: SPE ACC STA STR CON PAS SHO TAC (in order of appearance)
  vals = stat_nums[:8]
  while len(vals) < 8:
    vals.append(0)
  spe, acc, sta, str_, con, pas, sho, tac = vals

  # Rate: first 2-digit 50-99 that appears before stat labels
  rate = 0
  for t, _ in lines:
    m = re.search(r'\b([5-9]\d)\b', t)
    if m:
      rate = int(m.group(1))
      break

  # Height: 3-digit 150-220
  hgt = 0
  for t, _ in lines:
    m = re.search(r'\b(1[5-9]\d|2[0-2]\d)\b', t)
    if m:
      hgt = int(m.group(1))
      break

  # Foot
  foot = 'L' if re.search(r'\bLeft\b', full, re.IGNORECASE) else 'R'

  # Pos: known position codes
  POSITIONS = {'CF','SS','LW','RW','LM','RM','RWB','LWB','CM','DM','AM',
               'LB','CB','RB','GK'}
  pos = ''
  for t, _ in lines:
    if t.upper() in POSITIONS:
      pos = t.upper()
      break

  # Price: number followed by comma-format or standalone large number near end
  prc = 0
  for t, _ in lines:
    m = re.search(r'([\d,]+)', t)
    if m:
      try:
        v = int(m.group(1).replace(',', ''))
        if v >= 100:   # prices are always >= 100
          prc = v
      except ValueError:
        pass

  # Name: alphabetic tokens not in stat labels, not pos, not foot
  name_tokens = []
  for t, conf in lines:
    clean = re.sub(r'[^A-Za-z\-\']', '', t)
    if (len(clean) >= 2
        and clean.upper() not in _STAT_LABELS
        and clean.upper() not in POSITIONS
        and clean.upper() not in ('LEFT', 'RIGHT', 'CM', 'RIGHT')
        and conf >= 0.5):
      name_tokens.append(clean)

  fname, lname = '', ''
  if len(name_tokens) >= 2:
    fname = name_tokens[0]
    lname = name_tokens[1]
  elif len(name_tokens) == 1:
    fname = name_tokens[0]

  return {
    'fname': fname, 'lname': lname,
    'nat': '', 'club': '', 'pos': pos,
    'foot': foot, 'rate': rate, 'hgt': hgt,
    'spe': spe, 'acc': acc, 'sta': sta, 'str': str_,
    'con': con, 'pas': pas, 'sho': sho, 'tac': tac,
    'prc': prc, 'status': 1,
  }

def _parse_market_image(img_path):
  """
  Parse a DLS market screenshot using PaddleOCR.
  Grid: 3×3 cells at fixed coordinates.
  Row 0 may be banners (Top Picks) — auto-detected and skipped.
  """
  from PIL import Image

  COL_STARTS = [90, 435, 780]
  ROW_STARTS = [185, 385, 585]
  CELL_W, CELL_H = 280, 175

  img = Image.open(img_path).convert("RGB")

  # Save cropped cells to screenshot/market/crop/
  crop_dir  = os.path.join(os.path.dirname(img_path), "crop")
  os.makedirs(crop_dir, exist_ok=True)
  img_stem  = os.path.splitext(os.path.basename(img_path))[0]
  for ri in range(3):
    for ci in range(3):
      cell = img.crop((COL_STARTS[ci], ROW_STARTS[ri],
                       COL_STARTS[ci] + CELL_W, ROW_STARTS[ri] + CELL_H))
      cell.save(os.path.join(crop_dir, f"{img_stem}_r{ri}c{ci}.png"))

  # Detect banner row: check cell r0c0
  cell_r0 = img.crop((COL_STARTS[0], ROW_STARTS[0],
                      COL_STARTS[0] + CELL_W, ROW_STARTS[0] + CELL_H))
  lines_r0  = _paddle_ocr_cell(cell_r0)
  text_r0   = ' '.join(t for t, _ in lines_r0).upper()
  has_banner = any(k in text_r0 for k in ('TOP PICKS', 'LIVE TRANSFERS', 'LOCKED'))
  start_row  = 1 if has_banner else 0

  players = []
  for ri in range(start_row, 3):
    for ci in range(3):
      cell = img.crop((COL_STARTS[ci], ROW_STARTS[ri],
                       COL_STARTS[ci] + CELL_W, ROW_STARTS[ri] + CELL_H))
      lines = _paddle_ocr_cell(cell)
      p = _parse_cell_lines(lines)
      if p:
        p['_grid'] = f"r{ri}c{ci}"
        p['_raw']  = ' | '.join(t for t, _ in lines[:15])
        players.append(p)

  return players, start_row


# ── OCRTab ────────────────────────────────────────────────────────────────────
class OCRTab(ttk.Frame):
  """OCR market screenshots → extract player cards → preview → add to version."""

  def __init__(self, parent, data_tab, pid_tab):
    super().__init__(parent)
    self._data_tab = data_tab
    self._pid_tab  = pid_tab
    self._rows     = []
    self._img_path = None
    self._build()

  def _build(self):
    # ── top bar ──────────────────────────────────────────────────────────────
    top = ttk.Frame(self)
    top.pack(fill="x", padx=6, pady=6)

    ttk.Button(top, text="Browse image...", command=self._browse).pack(side="left", padx=4)
    ttk.Button(top, text="Open market folder", command=self._open_folder).pack(side="left", padx=4)
    self._file_lbl = ttk.Label(top, text="No image selected", foreground="#888888")
    self._file_lbl.pack(side="left", padx=6)

    ttk.Label(top, text="Target version:").pack(side="left", padx=(20, 4))
    self._ver_var = tk.StringVar()
    self._ver_cb  = ttk.Combobox(top, textvariable=self._ver_var, width=10, state="readonly")
    self._ver_cb.pack(side="left")
    self._refresh_versions()

    ttk.Button(top, text="Run OCR", command=self._run_ocr,
               style="Accent.TButton").pack(side="left", padx=12)

    ttk.Button(top, text="Add selected",  command=self._add_selected).pack(side="right", padx=4)
    ttk.Button(top, text="Add all valid", command=self._add_all_valid).pack(side="right", padx=4)

    # ── image thumbnail + status ──────────────────────────────────────────────
    mid = ttk.Frame(self)
    mid.pack(fill="x", padx=6)
    self._thumb_lbl  = ttk.Label(mid)
    self._thumb_lbl.pack(side="left", padx=4, pady=4)
    self._status_lbl = ttk.Label(mid, text="", wraplength=900, justify="left")
    self._status_lbl.pack(side="left", padx=8, fill="x", expand=True)

    # ── grid cell preview (3x3 thumbnails shown after OCR) ───────────────────
    self._grid_frame = ttk.LabelFrame(self, text="Cell preview (3×3 grid)")
    self._grid_frame.pack(fill="x", padx=6, pady=(0, 4))
    self._cell_labels = []   # list of ttk.Label, populated in _show_grid_preview
    for r in range(3):
      row_frame = ttk.Frame(self._grid_frame)
      row_frame.pack(side="top", fill="x")
      row_labels = []
      for c in range(3):
        lbl = ttk.Label(row_frame, text=f"r{r}c{c}", relief="groove",
                        width=18, anchor="center")
        lbl.pack(side="left", padx=2, pady=2)
        row_labels.append(lbl)
      self._cell_labels.append(row_labels)

    # ── preview table ─────────────────────────────────────────────────────────
    self._preview_frame = ttk.Frame(self)
    self._preview_frame.pack(fill="both", expand=True, padx=4, pady=4)
    self._tree = None

    if not _ocr_available():
      ttk.Label(self._preview_frame,
                text="PaddleOCR not available.\n"
                     "Install with: pip install paddleocr pillow",
                foreground="red", justify="left").pack(pady=20, padx=10, anchor="w")

  def _refresh_versions(self):
    vers = list(self._data_tab._ver_tabs.keys())
    self._ver_cb["values"] = vers
    if vers:
      self._ver_var.set(vers[-1])

  def _open_folder(self):
    if os.path.isdir(SCREENSHOT_MARKET):
      os.startfile(SCREENSHOT_MARKET)
    else:
      messagebox.showwarning("Not found", f"Folder not found:\n{SCREENSHOT_MARKET}")

  def _browse(self):
    from tkinter import filedialog
    path = filedialog.askopenfilename(
      title="Select market screenshot",
      initialdir=SCREENSHOT_MARKET if os.path.isdir(SCREENSHOT_MARKET) else BASE_DIR,
      filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
    )
    if path:
      self._img_path = path
      self._file_lbl.config(text=os.path.basename(path), foreground="#000000")
      self._show_thumbnail(path)
      self._rows = []
      self._status_lbl.config(text="Image loaded. Click 'Run OCR' to extract players.")

  def _show_thumbnail(self, path):
    try:
      from PIL import Image, ImageTk
      img = Image.open(path)
      img.thumbnail((320, 180))
      self._tk_img = ImageTk.PhotoImage(img)
      self._thumb_lbl.config(image=self._tk_img)
    except Exception:
      self._thumb_lbl.config(image="", text="[preview unavailable]")

  def _show_grid_preview(self, img_path, start_row):
    """Crop and display the 3x3 grid cells as thumbnails."""
    try:
      from PIL import Image, ImageTk, ImageDraw
    except ImportError:
      return
    COL_STARTS = [90, 435, 780]
    ROW_STARTS = [185, 385, 585]
    CELL_W, CELL_H = 280, 175
    THUMB_W, THUMB_H = 200, 124   # thumbnail size per cell

    img = Image.open(img_path).convert("RGB")
    self._cell_tk_imgs = []   # keep refs to avoid GC

    for r in range(3):
      for c in range(3):
        x0 = COL_STARTS[c]
        y0 = ROW_STARTS[r]
        cell = img.crop((x0, y0, x0 + CELL_W, y0 + CELL_H))
        cell_thumb = cell.copy()
        cell_thumb.thumbnail((THUMB_W, THUMB_H))

        # Draw red border on banner rows, green on player rows
        draw = ImageDraw.Draw(cell_thumb)
        is_skip = (r < start_row)
        color = "#cc0000" if is_skip else "#00aa00"
        draw.rectangle([0, 0, cell_thumb.width-1, cell_thumb.height-1],
                       outline=color, width=3)

        tk_img = ImageTk.PhotoImage(cell_thumb)
        self._cell_tk_imgs.append(tk_img)
        lbl = self._cell_labels[r][c]
        lbl.config(image=tk_img, text="", width=THUMB_W)
    # Force geometry update
    self._grid_frame.update_idletasks()

  def _run_ocr(self):
    if not self._img_path:
      messagebox.showwarning("No image", "Browse to an image first.")
      return
    if not _ocr_available():
      messagebox.showerror("PaddleOCR missing",
                           "Install with: pip install paddleocr pillow")
      return
    self._status_lbl.config(text="Running OCR... please wait.")
    self.update_idletasks()
    try:
      self._rows, start_row = _parse_market_image(self._img_path)
    except Exception as e:
      messagebox.showerror("OCR Error", str(e))
      self._status_lbl.config(text=f"Error: {e}")
      return
    self._show_grid_preview(self._img_path, start_row)
    self._show_preview()

  def _show_preview(self):
    for w in self._preview_frame.winfo_children():
      w.destroy()
    if not self._rows:
      ttk.Label(self._preview_frame,
                text="No player cards detected. Try a different image.",
                foreground="#888888").pack(pady=20)
      self._status_lbl.config(text="No players found.")
      return

    # Build columns: all PREVIEW_COLS (prc last) + grid + raw_ocr + errors
    all_cols = ([c for c in PREVIEW_COLS if c != "prc"]
                + ["prc", "grid", "raw_ocr", "errors"])

    frame = ttk.Frame(self._preview_frame)
    self._tree = ttk.Treeview(frame, columns=all_cols,
                               show="headings", selectmode="extended")

    col_widths = {
      "fname": 80, "lname": 80, "nat": 60, "club": 70,
      "pos": 45, "foot": 40, "rate": 40, "hgt": 40,
      "spe": 40, "acc": 40, "sta": 40, "str": 40,
      "con": 40, "pas": 40, "sho": 40, "tac": 40,
      "prc": 50, "id": 50, "version": 55, "status": 45,
      "grid": 50, "raw_ocr": 220, "errors": 160,
    }
    for c in all_cols:
      self._tree.heading(c, text=c)
      self._tree.column(c, width=col_widths.get(c, 55),
                        minwidth=30, anchor="center")
    self._tree.column("raw_ocr", anchor="w")
    self._tree.column("errors",  anchor="w")

    vsb = ttk.Scrollbar(frame, orient="vertical",   command=self._tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=self._tree.xview)
    self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    self._tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    self._tree.tag_configure("ok",    background="#e8f5e9")
    self._tree.tag_configure("error", background="#ffebee")

    for idx, row in enumerate(self._rows):
      clean = {k: v for k, v in row.items() if not k.startswith("_")}
      errs  = _validate_row(clean)
      tag   = "error" if errs else "ok"
      vals  = []
      for c in all_cols:
        if c == "prc":      vals.append(get_price(clean))
        elif c == "grid":   vals.append(row.get("_grid", ""))
        elif c == "raw_ocr":vals.append(row.get("_raw", "")[:80])
        elif c == "errors": vals.append("; ".join(errs) if errs else "")
        else:               vals.append(clean.get(c, ""))
      self._tree.insert("", "end", iid=str(idx), values=vals, tags=(tag,))

    frame.pack(fill="both", expand=True)
    ok = sum(1 for r in self._rows
             if not _validate_row({k: v for k, v in r.items()
                                   if not k.startswith("_")}))
    self._status_lbl.config(
      text=f"Detected {len(self._rows)} player cards  |  {ok} valid  |  "
           f"Double-click a row to edit.  Ctrl+click to multi-select."
    )
    self._tree.bind("<Double-Button-1>", self._on_edit_row)

  def _on_edit_row(self, event):
    """Allow editing an OCR-extracted row before committing."""
    if not self._tree:
      return
    sel = self._tree.selection()
    if not sel:
      return
    idx = int(sel[0])
    row = {k: v for k, v in self._rows[idx].items() if not k.startswith("_")}
    edit_cols = [c for c in PREVIEW_COLS if c not in ("prc", "version")]
    dlg = EditDialog(self, row, edit_cols,
                     pid_lookup=self._pid_tab.lookup_id if self._pid_tab else None)
    if dlg.result:
      new_row = dict(self._rows[idx])
      new_row.update(_cast(dlg.result))
      new_row["prc"] = get_price(new_row)
      self._rows[idx] = new_row
      display_rows = [{k: v for k, v in r.items() if not k.startswith("_")}
                      for r in self._rows]
      _populate_preview_tree(self._tree, display_rows)

  def _selected_rows(self):
    if not self._tree:
      return []
    return [{k: v for k, v in self._rows[int(iid)].items() if not k.startswith("_")}
            for iid in self._tree.selection()]

  def _add_selected(self):
    rows = self._selected_rows()
    if not rows:
      messagebox.showwarning("Nothing selected", "Select rows in the preview table first.")
      return
    self._do_add(rows)

  def _add_all_valid(self):
    rows = [{k: v for k, v in r.items() if not k.startswith("_")}
            for r in self._rows if not _validate_row(r)]
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
    nb.add(ImportTab(nb, data_tab, pid_tab), text=" Import ")
    nb.add(OCRTab(nb, data_tab, pid_tab),    text=" OCR ")

    # Warm up PaddleOCR engine in background so first OCR run is fast
    if _ocr_available():
      import threading
      threading.Thread(target=_get_paddle_engine, daemon=True).start()


if __name__ == "__main__":
  App().mainloop()