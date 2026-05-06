import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

from editor_config import get_price, _cast
from editor_widgets import EditDialog
from editor_import import (
  PREVIEW_COLS, _validate_row, _populate_preview_tree, _commit_rows,
)

# ── OCR paths ─────────────────────────────────────────────────────────────────
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
  'SPE', 'ACC', 'STA', 'STR', 'CON', 'PAS', 'SHO', 'TAC', 'GKR', 'GKH',
  'LEFT', 'RIGHT', 'LAST', 'CHANCE', 'LIVE', 'TOP', 'PICKS', 'TRANSFERS',
  'SCOUTS', 'AGENTS', 'MANAGE', 'PLAYERS', 'LOCKED',
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
  POSITIONS = {'CF', 'SS', 'LW', 'RW', 'LM', 'RM', 'RWB', 'LWB', 'CM', 'DM', 'AM',
               'LB', 'CB', 'RB', 'GK'}
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
  crop_dir = os.path.join(os.path.dirname(img_path), "crop")
  os.makedirs(crop_dir, exist_ok=True)
  img_stem = os.path.splitext(os.path.basename(img_path))[0]
  for ri in range(3):
    for ci in range(3):
      cell = img.crop((COL_STARTS[ci], ROW_STARTS[ri],
                       COL_STARTS[ci] + CELL_W, ROW_STARTS[ri] + CELL_H))
      cell.save(os.path.join(crop_dir, f"{img_stem}_r{ri}c{ci}.png"))

  # Detect banner row: check cell r0c0
  cell_r0   = img.crop((COL_STARTS[0], ROW_STARTS[0],
                        COL_STARTS[0] + CELL_W, ROW_STARTS[0] + CELL_H))
  lines_r0  = _paddle_ocr_cell(cell_r0)
  text_r0   = ' '.join(t for t, _ in lines_r0).upper()
  has_banner = any(k in text_r0 for k in ('TOP PICKS', 'LIVE TRANSFERS', 'LOCKED'))
  start_row  = 1 if has_banner else 0

  players = []
  for ri in range(start_row, 3):
    for ci in range(3):
      cell  = img.crop((COL_STARTS[ci], ROW_STARTS[ri],
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

    ttk.Button(top, text="Browse image...",    command=self._browse).pack(side="left", padx=4)
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
      initialdir=SCREENSHOT_MARKET if os.path.isdir(SCREENSHOT_MARKET) else None,
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
        if c == "prc":       vals.append(get_price(clean))
        elif c == "grid":    vals.append(row.get("_grid", ""))
        elif c == "raw_ocr": vals.append(row.get("_raw", "")[:80])
        elif c == "errors":  vals.append("; ".join(errs) if errs else "")
        else:                vals.append(clean.get(c, ""))
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
