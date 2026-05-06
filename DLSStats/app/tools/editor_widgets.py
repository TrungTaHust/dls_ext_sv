import tkinter as tk
from tkinter import ttk, messagebox

from editor_config import (
  INT_FIELDS, POS_ID, price_map,
  get_pos_id, get_price_id, get_price, get_status,
  default_sort_key, _cast,
)


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
    self.aux_cols     = aux_cols
    self.data_ref     = data_ref
    self.master_data  = master_data
    self.on_data_change = on_data_change
    self.default_sort = default_sort
    self.pid_lookup   = pid_lookup   # callable(fname, lname) -> id | None
    self._show_aux    = False
    self._active_cols = list(base_columns)
    self.filtered     = []
    self._sort_col    = None
    self._sort_reverse = False
    self._col_filters = {}  # col -> StringVar
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

    self.tree.tag_configure("odd",         background="#e8e8e8")
    self.tree.tag_configure("even",        background="#ffffff")
    self.tree.tag_configure("odd_active",  background="#d0d0d0", font=("Segoe UI", 9, "bold"))
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
      if col == "pos_id":    cell = str(get_pos_id(row))
      elif col == "price_id": cell = str(get_price_id(row))
      elif col == "prc":     cell = str(get_price(row))
      elif col == "status":  cell = str(get_status(row))
      else:                  cell = str(row.get(col, ""))
      cell = cell.lower()
      if not any(t.lower() in cell for t in terms):
        return False
    return True

  # ── data helpers ──────────────────────────────────────────────────────────
  def _row_vals(self, row):
    vals = []
    for c in self._active_cols:
      if c == "pos_id":    vals.append(get_pos_id(row))
      elif c == "price_id": vals.append(get_price_id(row))
      elif c == "prc":     vals.append(get_price(row))
      elif c == "status":  vals.append(get_status(row))
      else:                vals.append(row.get(c, ""))
    return vals

  def refresh(self):
    self.filtered = [r for r in self.data_ref if self._matches(r)]
    # Only apply default sort if no manual sort has been set
    if self.default_sort and self._sort_col is None:
      self.filtered.sort(key=default_sort_key)
    elif self._sort_col is not None:
      col = self._sort_col
      def key(r):
        if col == "pos_id":   return get_pos_id(r)
        if col == "price_id": return get_price_id(r)
        if col == "prc":      return get_price(r)
        if col == "status":   return get_status(r)
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
