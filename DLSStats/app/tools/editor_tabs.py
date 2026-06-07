import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

from editor_config import (
  BASE_DIR, SPECIAL_FILE, PLAYER_ID_FILE, PRICE_MAP_FILE, price_map,
  ver_file, DATA_COLS_VER, DATA_SAVE_COLS, SPECIAL_COLS, PLAYER_ID_COLS,
  AUX_COLS_DATA, AUX_COLS_SPECIAL, INT_FIELDS,
  get_price, _cast,
)
from editor_widgets import EditDialog, TreeTable


# ── VersionTab ────────────────────────────────────────────────────────────────
class VersionTab(ttk.Frame):
  """One tab per version file (e.g. 20231.json). Loads lazily on first focus."""

  def __init__(self, parent, ver, player_id_tab_ref):
    super().__init__(parent)
    self.ver = ver                          # int or str version value
    self.label = str(ver)
    self.filepath = ver_file(ver)
    self.player_id_tab_ref = player_id_tab_ref  # callable returning PlayerIDTab
    self.data = None                        # None = not yet loaded
    self._tbl = None
    self._build_skeleton()

  # ── skeleton shown before first load ──────────────────────────────────────
  def _build_skeleton(self):
    self._top = ttk.Frame(self)
    self._top.pack(fill="x", padx=6, pady=4)
    ttk.Button(self._top, text="Add Row",   command=self._add_row).pack(side="left", padx=4)
    ttk.Button(self._top, text="Delete Row", command=self._delete_row).pack(side="left", padx=4)
    ttk.Button(self._top, text="Save File",  command=self._save).pack(side="right", padx=4)
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
    # Edit cols: bao gồm status để user chọn (0/1/2/3)
    edit_cols = list(DATA_COLS_VER)   # giữ nguyên status trong danh sách
    # Numeric fields default to empty string (not 0) so user types fresh values
    BLANK_FIELDS = {"rate", "hgt", "spe", "acc", "sta", "str", "con", "pas", "sho", "tac"}
    empty = {c: ("" if c in BLANK_FIELDS else (0 if c in INT_FIELDS else "")) for c in edit_cols}
    pid_tab = self._pid_tab()
    dlg = EditDialog(self, empty, edit_cols,
                     pid_lookup=pid_tab.lookup_id if pid_tab else None)
    if not dlg.result:
      return
    new_row = _cast(dlg.result)
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
    ttk.Button(top, text="Add Row",   command=self._add_row).pack(side="left", padx=4)
    ttk.Button(top, text="Delete Row", command=self._delete_row).pack(side="left", padx=4)
    ttk.Button(top, text="Save File",  command=self._save).pack(side="right", padx=4)

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
    # Lấy tất cả ID đang dùng từ self.data (player_id.json)
    used = {r["id"] for r in self.data if isinstance(r.get("id"), int)}
    # Tìm ID nhỏ nhất chưa dùng, bắt đầu từ max+1 để tránh scan toàn bộ
    if used:
      i = max(used) + 1
    else:
      i = 1000
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
    self._save_silent()
    self.tbl.refresh()
    return new_id

  def _save_silent(self):
    """Lưu player_id.json không hiện messagebox — dùng khi auto-save."""
    with open(PLAYER_ID_FILE, "w", encoding="utf-8") as f:
      json.dump(self.data, f, ensure_ascii=False, indent=4)

  def _build(self):
    top = ttk.Frame(self)
    top.pack(fill="x", padx=6, pady=4)
    ttk.Button(top, text="Add Player",       command=self._add_row).pack(side="left", padx=4)
    ttk.Button(top, text="Delete Row",       command=self._delete_row).pack(side="left", padx=4)
    ttk.Button(top, text="Rebuild from data", command=self._on_rebuild).pack(side="left", padx=4)
    ttk.Button(top, text="Save File",        command=self._save).pack(side="right", padx=4)

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
    ttk.Button(top, text="Add Row",    command=self._add_row).pack(side="left", padx=4)
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
