import tkinter as tk
from tkinter import ttk, messagebox

from editor_config import (
  INT_FIELDS, POS_ID, price_map,
  get_pos_id, get_price_id, get_price, get_status,
  default_sort_key, _cast,
)

# Lazy-load danh sách club/nation từ checklist để tránh circular import
def _get_club_list():
    try:
        from editor_checklist import get_club_list
        return get_club_list()
    except Exception:
        return []

def _get_nation_list():
    try:
        from editor_checklist import get_nation_list
        return get_nation_list()
    except Exception:
        return []


# ── Edit dialog ───────────────────────────────────────────────────────────────
class EditDialog(tk.Toplevel):
  def __init__(self, parent, row_data, columns, pid_lookup=None):
    super().__init__(parent)
    self.title("Edit Row")
    self.result = None
    self.resizable(False, False)
    self._pid_lookup = pid_lookup

    vcmd = (self.register(lambda s: all(0x20 <= ord(c) <= 0x7E for c in s)), "%P")

    canvas = tk.Canvas(self)
    sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame = ttk.Frame(canvas, padding=10)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    self.entries = {}
    self._entry_widgets = []

    # Load danh sách dropdown một lần cho cả dialog
    _club_values   = _get_club_list()
    _nation_values = _get_nation_list()

    for i, col in enumerate(columns):
      ttk.Label(frame, text=col, width=10, anchor="e").grid(
        row=i, column=0, padx=4, pady=2, sticky="e")
      var = tk.StringVar(value=str(row_data.get(col, "")))
      if col == "id" and self._pid_lookup:
        lbl = ttk.Label(frame, textvariable=var,
                        foreground="#007700", font=("Segoe UI", 10, "bold"))
        lbl.grid(row=i, column=1, padx=4, pady=2, sticky="w")
        self._id_entry = lbl
        self._entry_widgets.append(None)
      elif col == "nat" and _nation_values:
        cb = ttk.Combobox(frame, textvariable=var, values=_nation_values,
                          width=28, state="normal")
        cb.grid(row=i, column=1, padx=4, pady=2)
        # Lọc dropdown khi gõ
        def _filter_cb(ev, w=cb, vals=_nation_values, v=var):
            typed = v.get().lower()
            filtered = [x for x in vals if typed in x.lower()]
            w["values"] = filtered if filtered else vals
        cb.bind("<KeyRelease>", _filter_cb)
        self._entry_widgets.append(cb)
      elif col == "club" and _club_values:
        cb = ttk.Combobox(frame, textvariable=var, values=_club_values,
                          width=28, state="normal")
        cb.grid(row=i, column=1, padx=4, pady=2)
        def _filter_cb(ev, w=cb, vals=_club_values, v=var):
            typed = v.get().lower()
            filtered = [x for x in vals if typed in x.lower()]
            w["values"] = filtered if filtered else vals
        cb.bind("<KeyRelease>", _filter_cb)
        self._entry_widgets.append(cb)
      else:
        e = ttk.Entry(frame, textvariable=var, width=30,
                      validate="key", validatecommand=vcmd)
        e.grid(row=i, column=1, padx=4, pady=2)
        if col in INT_FIELDS:
          e.bind("<FocusIn>", lambda ev, w=e: w.after(
            0, lambda: (w.selection_range(0, "end"), w.icursor("end"))))
        if col == "pos":
          def _upper_pos(ev, v=var): v.set(v.get().upper())
          e.bind("<FocusOut>", _upper_pos)
          e.bind("<Return>",   _upper_pos)
        if col == "id":
          self._id_entry = e
        self._entry_widgets.append(e)
      self.entries[col] = var

    prc_row = len(columns)
    ttk.Label(frame, text="prc", width=10, anchor="e",
              foreground="#888888").grid(row=prc_row, column=0, padx=4, pady=2, sticky="e")
    self._prc_var = tk.StringVar(value="")
    ttk.Label(frame, textvariable=self._prc_var,
              foreground="#0055cc", font=("Segoe UI", 10, "bold")).grid(
      row=prc_row, column=1, padx=4, pady=2, sticky="w")

    bf = ttk.Frame(frame)
    bf.grid(row=prc_row + 1, column=0, columnspan=2, pady=8)
    ttk.Button(bf, text="Save",   command=self._save).pack(side="left", padx=4)
    ttk.Button(bf, text="Cancel", command=self.destroy).pack(side="left", padx=4)

    for idx, widget in enumerate(self._entry_widgets):
      if widget is None:
        continue
      widget.bind("<Up>",   lambda e, i=idx: self._nav(i - 1))
      widget.bind("<Down>", lambda e, i=idx: self._nav(i + 1))

    for col in ("rate", "pos"):
      if col in self.entries:
        self.entries[col].trace_add("write", lambda *_: self._update_prc_preview())
    self._update_prc_preview()

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
      self._prc_var.set("—"); return
    pos    = self.entries.get("pos", tk.StringVar()).get().strip()
    pos_id = POS_ID.get(pos, 0)
    try:
      price_id = int(str(rate) + str(pos_id))
    except (ValueError, TypeError):
      self._prc_var.set("—"); return
    prc = price_map.get(price_id, 0)
    self._prc_var.set(str(prc) if prc else "0 (not in map)")

  def _update_id_preview(self):
    if not self._pid_lookup or "id" not in self.entries:
      return
    fname = self.entries.get("fname", tk.StringVar()).get().strip()
    lname = self.entries.get("lname", tk.StringVar()).get().strip()
    pid   = self._pid_lookup(fname, lname)
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
    if "status" in vals and vals["status"] not in ("0", "1"):
      messagebox.showerror("Invalid", "status must be 0 or 1."); return
    CAPPED = {"rate", "spe", "acc", "sta", "str", "con", "pas", "sho", "tac"}
    for col in CAPPED:
      if col not in vals:
        continue
      try:
        v = int(vals[col])
      except ValueError:
        messagebox.showerror("Invalid", f"'{col}' must be an integer."); return
      if v > 100:
        messagebox.showerror("Invalid", f"'{col}' must be ≤ 100 (got {v})."); return
    self.result = vals
    self.destroy()


# ── TreeTable ─────────────────────────────────────────────────────────────────
class TreeTable(ttk.Frame):
  """
  Layout (top → bottom):
    [toolbar: Show aux | Clear filters | row count]
    [filter_bar: one Entry per column, synced to column widths]
    [Treeview with headings + data rows]
    [horizontal scrollbar]
  """

  def __init__(self, parent, base_columns, aux_cols, data_ref,
               on_data_change=None, default_sort=False, master_data=None,
               pid_lookup=None):
    super().__init__(parent)
    self.base_columns   = base_columns
    self.aux_cols       = aux_cols
    self.data_ref       = data_ref
    self.master_data    = master_data
    self.on_data_change = on_data_change
    self.default_sort   = default_sort
    self.pid_lookup     = pid_lookup
    self._show_aux      = False
    self._active_cols   = list(base_columns)
    self.filtered       = []
    self._sort_col      = None
    self._sort_reverse  = False
    self._col_filters   = {}
    self._name_filter   = None
    self._filter_cells  = {}   # col -> tk.Frame inside filter_bar
    self._build()

  # ── build ─────────────────────────────────────────────────────────────────
  def _build(self):
    # toolbar
    top = ttk.Frame(self)
    top.pack(fill="x", padx=4, pady=3)
    self._aux_btn = ttk.Button(top, text="Show aux columns", command=self._toggle_aux)
    self._aux_btn.pack(side="left", padx=4)
    ttk.Button(top, text="Clear filters", command=self._clear_filters).pack(side="left", padx=4)
    self.status_lbl = ttk.Label(top, text="")
    self.status_lbl.pack(side="left", padx=8)

    # filter bar — fixed height frame, cells positioned by _sync_filter_widths
    self._filter_bar = tk.Frame(self, bg="#dcdcdc", height=24)
    self._filter_bar.pack(fill="x", padx=4)
    self._filter_bar.pack_propagate(False)

    # treeview + scrollbars
    tree_frame = ttk.Frame(self)
    tree_frame.pack(fill="both", expand=True, padx=4, pady=(0, 2))

    self.tree = ttk.Treeview(tree_frame, columns=self._active_cols,
                              show="headings", selectmode="browse")
    self._configure_columns()

    vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self._on_hscroll)
    self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=self._on_xscroll)
    self.tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)
    self._hsb = hsb

    self.tree.tag_configure("odd",         background="#e8e8e8")
    self.tree.tag_configure("even",        background="#ffffff")
    self.tree.tag_configure("odd_active",  background="#d0d0d0", font=("Segoe UI", 10, "bold"))
    self.tree.tag_configure("even_active", background="#f0f0f0", font=("Segoe UI", 10, "bold"))
    self.tree.bind("<Double-Button-1>", self._on_double_click)
    self.tree.bind("<Configure>",       lambda e: self.after(30, self._sync_filter_widths))
    self.tree.bind("<ButtonRelease-1>", lambda e: self.after(30, self._sync_filter_widths))

  def _on_xscroll(self, *args):
    self._hsb.set(*args)
    self.after(5, self._sync_filter_widths)

  def _on_hscroll(self, *args):
    self.tree.xview(*args)
    self.after(5, self._sync_filter_widths)

  # ── filter bar ────────────────────────────────────────────────────────────
  def _build_filter_row(self):
    for w in self._filter_bar.winfo_children():
      w.destroy()
    self._col_filters  = {}
    self._filter_cells = {}
    self._name_filter  = None

    vcmd = (self.tree.register(
      lambda s: all(0x20 <= ord(c) <= 0x7E for c in s)), "%P")

    for col in self._active_cols:
      var = tk.StringVar()
      var.trace_add("write", lambda *_, c=col: self.refresh())

      # Each column gets a fixed-size cell Frame inside the filter bar
      cell = tk.Frame(self._filter_bar, bg="#dcdcdc")
      # will be positioned by _sync_filter_widths
      self._filter_cells[col] = cell

      if col == "fname":
        placeholder = "name"
        e = tk.Entry(cell, textvariable=var, font=("Segoe UI", 9, "italic"),
                     fg="#999999", relief="flat", bd=0,
                     highlightthickness=1, highlightbackground="#aaaaaa",
                     bg="#f0f0f0", validate="key", validatecommand=vcmd)
        e.place(relx=0, rely=0, relwidth=1, relheight=1)
        def _fi(ev, w=e, v=var, ph=placeholder):
          if w.cget("fg") == "#999999" and v.get() == ph:
            v.set(""); w.config(fg="#000000", font=("Segoe UI", 9), bg="#ffffff")
        def _fo(ev, w=e, v=var, ph=placeholder):
          if v.get() == "":
            v.set(ph); w.config(fg="#999999", font=("Segoe UI", 9, "italic"), bg="#f0f0f0")
        var.set(placeholder)
        e.bind("<FocusIn>",  _fi)
        e.bind("<FocusOut>", _fo)
        self._name_filter      = (var, e, placeholder)
        self._col_filters[col] = (var, e, placeholder)

      elif col == "lname":
        # blank — covered by the combined fname+lname name box
        empty_var = tk.StringVar(value="")
        self._col_filters[col] = (empty_var, cell, "")

      else:
        placeholder = col
        e = tk.Entry(cell, textvariable=var, font=("Segoe UI", 9, "italic"),
                     fg="#999999", relief="flat", bd=0,
                     highlightthickness=1, highlightbackground="#aaaaaa",
                     bg="#f0f0f0", validate="key", validatecommand=vcmd)
        e.place(relx=0, rely=0, relwidth=1, relheight=1)
        def _fi(ev, w=e, v=var, ph=placeholder):
          if w.cget("fg") == "#999999" and v.get() == ph:
            v.set(""); w.config(fg="#000000", font=("Segoe UI", 9), bg="#ffffff")
        def _fo(ev, w=e, v=var, ph=placeholder):
          if v.get() == "":
            v.set(ph); w.config(fg="#999999", font=("Segoe UI", 9, "italic"), bg="#f0f0f0")
        var.set(placeholder)
        e.bind("<FocusIn>",  _fi)
        e.bind("<FocusOut>", _fo)
        self._col_filters[col] = (var, e, placeholder)

    self.after(60, self._sync_filter_widths)

  def _sync_filter_widths(self):
    """Position each filter cell to align with its tree column, accounting for scroll."""
    if not self._filter_cells:
      return

    total_virt = sum(self.tree.column(c, "width") for c in self._active_cols)
    if total_virt == 0:
      return

    try:
      xlo = self.tree.xview()[0]
    except Exception:
      xlo = 0.0
    scroll_px = int(xlo * total_virt)

    H = self._filter_bar.winfo_height() or 24

    x_cursor = 0
    fname_x = fname_w = lname_w = 0

    for col in self._active_cols:
      cw = self.tree.column(col, "width")
      sx = x_cursor - scroll_px   # screen x after scroll

      cell = self._filter_cells.get(col)
      if cell:
        if col == "fname":
          fname_x = sx
          fname_w = cw
          # placed after lname width is known
        elif col == "lname":
          lname_w = cw
          # hide lname cell — name box covers it
          cell.place_forget()
        else:
          cell.place(x=sx, y=0, width=cw, height=H)

      x_cursor += cw

    # fname cell spans fname + lname
    fname_cell = self._filter_cells.get("fname")
    if fname_cell is not None:
      fname_cell.place(x=fname_x, y=0, width=fname_w + lname_w, height=H)

  def _clear_filters(self):
    if self._name_filter:
      var, entry, ph = self._name_filter
      var.set(ph)
      entry.config(fg="#999999", font=("Segoe UI", 9, "italic"), bg="#f0f0f0")
    for col, (var, entry, ph) in self._col_filters.items():
      if col in ("fname", "lname"):
        continue
      var.set(ph)
      if isinstance(entry, tk.Entry):
        entry.config(fg="#999999", font=("Segoe UI", 9, "italic"), bg="#f0f0f0")
    self.refresh()

  # ── columns ───────────────────────────────────────────────────────────────
  def _toggle_aux(self):
    self._show_aux = not self._show_aux
    if self._show_aux:
      self._active_cols = self.base_columns + [
        c for c in self.aux_cols if c not in self.base_columns]
      self._aux_btn.config(text="Hide aux columns")
    else:
      self._active_cols = list(self.base_columns)
      self._aux_btn.config(text="Show aux columns")
    self._configure_columns()
    self._repopulate()

  def _configure_columns(self):
    self.tree.configure(columns=self._active_cols)
    for col in self._active_cols:
      w = 100 if col in ("fname", "lname", "nat", "club", "type") else 68
      self.tree.heading(col, text=col, command=lambda: None)
      self.tree.column(col, width=w, minwidth=40, anchor="center")
    self._build_filter_row()

  # ── events ────────────────────────────────────────────────────────────────
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
    if self._name_filter:
      var, _, ph = self._name_filter
      raw = var.get().strip()
      if raw and raw != ph:
        terms = [t.strip() for t in raw.split(";") if t.strip()]
        if terms:
          full = (str(row.get("fname", "")) + " " + str(row.get("lname", ""))).lower()
          if not any(t.lower() in full for t in terms):
            return False
    for col, (var, entry, ph) in self._col_filters.items():
      if col in ("fname", "lname"):
        continue
      raw = var.get().strip()
      if not raw or raw == ph:
        continue
      terms = [t.strip() for t in raw.split(";") if t.strip()]
      if not terms:
        continue
      if col == "pos_id":    cell = str(get_pos_id(row))
      elif col == "price_id": cell = str(get_price_id(row))
      elif col == "prc":     cell = str(get_price(row))
      elif col == "status":  cell = str(get_status(row))
      else:                  cell = str(row.get(col, ""))
      if not any(t.lower() in cell.lower() for t in terms):
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
    self._sort_col = None
    self._sort_reverse = False

  def _repopulate(self):
    self.tree.delete(*self.tree.get_children())
    for idx, row in enumerate(self.filtered):
      is_active = get_status(row) == 1
      tag = ("even_active" if idx % 2 == 0 else "odd_active") if is_active \
            else ("even"   if idx % 2 == 0 else "odd")
      self.tree.insert("", "end", iid=str(idx),
                       values=self._row_vals(row), tags=(tag,))
    self.status_lbl.config(
      text=f"{len(self.filtered)} / {len(self.data_ref)} rows")

  def _on_double_click_row(self, event):
    sel = self.tree.selection()
    if not sel:
      return
    row      = self.filtered[int(sel[0])]
    target   = self.master_data if self.master_data is not None else self.data_ref
    data_idx = next((i for i, r in enumerate(target) if r is row), None)
    if data_idx is None:
      return
    dlg = EditDialog(self, row, self.base_columns, pid_lookup=self.pid_lookup)
    if dlg.result:
      new_row = dict(row)
      new_row.update(_cast(dlg.result))
      new_row["prc"] = get_price(new_row)
      target[data_idx] = new_row
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
      self._sort_col    = col
      self._sort_reverse = False
    self.refresh()


# ── Rename entry ──────────────────────────────────────────────────────────────
class RenameEntry(tk.Entry):
  def __init__(self, nb, tab_id, current_text, on_rename):
    super().__init__(nb, font=("Segoe UI", 10), width=12)
    self._nb       = nb
    self._tab_id   = tab_id
    self._on_rename = on_rename
    self.insert(0, current_text.strip())
    self.select_range(0, "end")
    self.bind("<Return>",   self._commit)
    self.bind("<Escape>",   lambda e: self.destroy())
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
