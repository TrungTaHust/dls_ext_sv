"""
editor_ocr.py — OCR tab dùng Qwen2.5-VL 7B qua Ollama.

Thay thế PaddleOCR bằng Vision-Language Model để đạt độ chính xác cao hơn.
Model trả về JSON có cấu trúc đúng schema cầu thủ, không cần regex parsing.

Yêu cầu:
  - Ollama đang chạy (ollama serve)
  - Model đã pull: ollama pull qwen2.5vl:7b
  - pip install ollama pillow
"""

import base64
import json
import os
import unicodedata
import tkinter as tk
from tkinter import ttk, messagebox

from editor_config import get_price, _cast
from editor_widgets import EditDialog
from editor_import import (
    PREVIEW_COLS, _validate_row, _populate_preview_tree, _commit_rows,
)

# ── Paths ─────────────────────────────────────────────────────────────────────
SCREENSHOT_MARKET = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "resources", "data", "screenshot", "market"
)

OLLAMA_MODEL = "qwen2.5vl:7b"

# Tọa độ grid 3×3 trên ảnh 1600×900
# Mỗi cell chứa 1 thẻ cầu thủ trong màn hình market DLS
COL_STARTS = [90,  435, 780]
ROW_STARTS = [185, 385, 585]
CELL_W, CELL_H = 280, 175

# ── Tự động tìm và khởi động Ollama server ───────────────────────────────────
import subprocess
import time

def _find_ollama_exe() -> str | None:
    """Tìm ollama.exe theo thứ tự ưu tiên."""
    import shutil
    # 1. Đã có trong PATH
    found = shutil.which("ollama")
    if found:
        return found
    # 2. Vị trí cài đặt mặc định trên Windows
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"),
        r"C:\Program Files\Ollama\ollama.exe",
        r"C:\Program Files (x86)\Ollama\ollama.exe",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _server_responding() -> bool:
    """Kiểm tra Ollama HTTP server đang lắng nghe tại localhost:11434."""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434", timeout=2)
        return True
    except Exception:
        return False


def _ensure_ollama_server() -> bool:
    """
    Đảm bảo Ollama server đang chạy.
    - Nếu đã chạy → return True ngay.
    - Nếu chưa → tìm ollama.exe, spawn 'ollama serve' ẩn (không có cửa sổ),
      chờ tối đa 15 giây cho đến khi server sẵn sàng.
    - Return True nếu thành công, False nếu không tìm được exe.
    """
    if _server_responding():
        return True

    # Kiểm tra xem Ollama app/process đã chạy chưa (có thể đang start)
    # Nếu có process ollama đang chạy, chờ nó tự serve thay vì spawn thêm
    try:
        import psutil
        ollama_procs = [p for p in psutil.process_iter(['name'])
                        if 'ollama' in p.info['name'].lower()]
        if ollama_procs:
            # Ollama đang chạy nhưng server chưa respond — chờ nó sẵn sàng
            for _ in range(20):
                time.sleep(0.5)
                if _server_responding():
                    return True
            return False
    except ImportError:
        pass  # psutil không có — dùng fallback bên dưới

    exe = _find_ollama_exe()
    if not exe:
        return False

    # Spawn ngầm — DETACHED_PROCESS + CREATE_NO_WINDOW để không hiện cửa sổ cmd
    CREATE_NO_WINDOW  = 0x08000000
    DETACHED_PROCESS  = 0x00000008
    subprocess.Popen(
        [exe, "serve"],
        creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Chờ server sẵn sàng (tối đa 15 giây)
    for _ in range(30):
        time.sleep(0.5)
        if _server_responding():
            return True
    return False


def _ollama_available() -> bool:
    """Đảm bảo server chạy rồi mới check. Tự khởi động nếu cần."""
    return _ensure_ollama_server()


def _model_pulled() -> bool:
    """Kiểm tra qwen2.5vl:7b đã được pull về chưa.
    Dùng urllib trực tiếp thay vì ollama client để tránh connection pool issue."""
    import urllib.request, json as _json
    for attempt in range(3):
        try:
            with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as resp:
                data = _json.loads(resp.read())
                names = [m.get("name", "") for m in data.get("models", [])]
                if any(OLLAMA_MODEL in n for n in names):
                    return True
        except Exception:
            pass
        if attempt < 2:
            time.sleep(1)
    return False


# ── Chuẩn hoá tên cầu thủ ────────────────────────────────────────────────────
def _normalize_name(raw: str) -> str:
    """
    Chuẩn hoá tên cầu thủ theo quy tắc:
      - Bỏ dấu tiếng nước ngoài (à→a, ã→a, ö→o, ü→u, ñ→n, v.v.)
        NGOẠI TRỪ dấu nháy đơn (') và gạch ngang (-) được giữ nguyên
        vì chúng là một phần của tên (D'Ambrosio, Traoré→Traore nhưng D'Ambrosio giữ ')
      - Title-case từng từ (kể cả sau ' và -)
        Ví dụ: "d'ambrosio" → "D'Ambrosio", "van dijk" → "Van Dijk"
    """
    if not raw:
        return ""

    # Bước 1: Unicode normalize NFD → tách base char + combining marks
    # Sau đó bỏ combining marks (dấu) nhưng giữ lại ký tự ASCII cơ bản
    nfd = unicodedata.normalize("NFD", raw)
    # Giữ lại: ASCII printable + dấu nháy đơn + gạch ngang + khoảng trắng
    # Bỏ: combining diacritical marks (category Mn)
    stripped = "".join(
        ch for ch in nfd
        if unicodedata.category(ch) != "Mn"   # bỏ dấu
        or ch in ("'", "-")                    # nhưng giữ ' và - (chúng không phải Mn nên dòng này thực ra dự phòng)
    )

    # Bước 2: Title-case từng "từ", trong đó từ được phân tách bởi space, ' hoặc -
    # Dùng regex để split + rejoin giữ nguyên separator
    import re
    # Split theo (space | ' | -) nhưng giữ separator trong kết quả
    parts = re.split(r"([ '\-])", stripped)
    result = "".join(p.capitalize() if p and p not in (" ", "'", "-") else p for p in parts)

    return result.strip()


# ── Encode ảnh sang base64 để gửi cho Ollama ─────────────────────────────────
def _img_to_base64(pil_img):
    import io
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ── Prompt schema cho Qwen2.5-VL ─────────────────────────────────────────────
PLAYER_SCHEMA = {
    "type": "object",
    "properties": {
        "fname":  {"type": "string",  "description": "First name of player"},
        "lname":  {"type": "string",  "description": "Last name of player"},
        "pos":    {"type": "string",  "description": "Position: CF SS LW RW LM RM CM DM AM RWB LWB LB CB RB GK"},
        "foot":   {"type": "string",  "description": "Preferred foot: L or R"},
        "rate":   {"type": "integer", "description": "Overall rating 50-99"},
        "hgt":    {"type": "integer", "description": "Height in cm, e.g. 180"},
        "spe":    {"type": "integer", "description": "Speed stat 0-100"},
        "acc":    {"type": "integer", "description": "Acceleration stat 0-100"},
        "sta":    {"type": "integer", "description": "Stamina stat 0-100"},
        "str":    {"type": "integer", "description": "Strength stat 0-100"},
        "con":    {"type": "integer", "description": "Control stat 0-100"},
        "pas":    {"type": "integer", "description": "Passing stat 0-100"},
        "sho":    {"type": "integer", "description": "Shooting stat 0-100"},
        "tac":    {"type": "integer", "description": "Tackling stat 0-100"},
    },
    "required": ["fname", "lname", "pos", "foot", "rate", "hgt",
                 "spe", "acc", "sta", "str", "con", "pas", "sho", "tac"]
}

SYSTEM_PROMPT = """You are an OCR assistant for a football card game (Dream League Soccer).
Extract player information from the card image and return ONLY valid JSON.
No explanation, no markdown, no extra text — just the raw JSON object.

Field mapping in the card image:
- Player name (first line = fname, second line = lname). Return the name exactly as shown.
- Position code (CF/SS/LW/RW/LM/RM/CM/DM/AM/RWB/LWB/LB/CB/RB/GK)
- Overall rating (large number, usually 60-99)
- Height in cm (3-digit number like 175, 180, 185)
- Preferred foot (Left → "L", Right → "R")
- Stats in order: SPE ACC STA STR CON PAS SHO TAC (each 0-100)
- Do NOT extract price — leave it as 0.

Return exactly this JSON structure:
{"fname":"...","lname":"...","pos":"...","foot":"L or R","rate":0,"hgt":0,"spe":0,"acc":0,"sta":0,"str":0,"con":0,"pas":0,"sho":0,"tac":0}"""


def _ollama_api(payload: dict, timeout: int = 120) -> dict:
    """
    Gọi Ollama REST API trực tiếp bằng urllib — không dùng ollama Python client
    để tránh httpx connection pool issue trong môi trường multithread Tkinter.
    Dùng stream=False để nhận 1 JSON object duy nhất.
    """
    import urllib.request
    # Luôn dùng stream=False để response là 1 JSON object, không phải NDJSON
    payload = dict(payload)
    payload["stream"] = False
    body = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def _ocr_cell_with_vlm(cell_img):
    """
    Gửi ảnh cell cho Qwen2.5-VL qua REST API trực tiếp, nhận về dict cầu thủ.
    Trả về (dict, error_str) — dict=None nếu không parse được.
    """
    img_b64 = _img_to_base64(cell_img)

    payload = {
        "model": OLLAMA_MODEL,
        "stream": True,
        "format": PLAYER_SCHEMA,
        "options": {"temperature": 0, "num_predict": 256},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "Extract all player stats from this card image.",
                "images": [img_b64],
            },
        ],
    }

    try:
        result = _ollama_api(payload, timeout=120)
        raw = result.get("message", {}).get("content", "").strip()
    except Exception as e:
        return None, f"API error: {e}"

    if not raw:
        return None, "Empty response from model"

    # Parse JSON
    try:
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {e} | raw: {raw[:80]}"

    # Chuẩn hoá
    player = {
        "fname":  _normalize_name(str(data.get("fname", ""))),
        "lname":  _normalize_name(str(data.get("lname", ""))),
        "nat":    "",
        "club":   "",
        "pos":    str(data.get("pos",  "")).upper().strip(),
        "foot":   str(data.get("foot", "R")).upper().strip(),
        "rate":   int(data.get("rate", 0)),
        "hgt":    int(data.get("hgt",  0)),
        "spe":    int(data.get("spe",  0)),
        "acc":    int(data.get("acc",  0)),
        "sta":    int(data.get("sta",  0)),
        "str":    int(data.get("str",  0)),
        "con":    int(data.get("con",  0)),
        "pas":    int(data.get("pas",  0)),
        "sho":    int(data.get("sho",  0)),
        "tac":    int(data.get("tac",  0)),
        "prc":    0,   # sẽ tính lại sau khi có rate + pos
        "status": 1,
    }
    # Tính giá từ price_map dựa trên rate + pos (không lấy từ OCR)
    player["prc"] = get_price(player)
    return player, None


def _is_banner_cell(cell_img):
    """
    Kiểm tra nhanh cell có phải banner (Top Picks / Live Transfers) không
    bằng cách check màu sắc dominant — banner thường có màu nền khác hẳn thẻ cầu thủ.
    Dùng để skip trước khi gọi VLM (tiết kiệm thời gian).
    """
    import numpy as np
    from PIL import Image

    arr = np.array(cell_img.resize((28, 18)))
    # Banner thường rất tối hoặc có gradient đặc trưng
    # Thẻ cầu thủ thường có nền sáng hơn với text rõ
    # Heuristic đơn giản: nếu variance màu quá thấp → có thể là banner trống
    gray = arr.mean(axis=2)
    if gray.std() < 8:
        return True
    return False


def _parse_market_image_vlm(img_path, pid_tab=None, data_tab=None, progress_cb=None):
    """
    Parse toàn bộ ảnh market screenshot.
    Crop từng cell trong grid 3×3, gửi cho Qwen2.5-VL **song song** (ThreadPoolExecutor).
    Sau khi OCR xong mỗi cell:
      - Normalize tên (bỏ dấu, title-case)
      - Tính giá từ price_map
      - Auto-map ID: search pid_tab + toàn bộ version data (case-insensitive)
      - Nếu found → lấy nat/club từ version sau cùng
    progress_cb(current, total, msg) — callback cập nhật UI.
    Trả về (players, start_row).
    """
    from PIL import Image
    from concurrent.futures import ThreadPoolExecutor, as_completed

    img = Image.open(img_path).convert("RGB")

    # Lưu crop để debug
    crop_dir = os.path.join(os.path.dirname(img_path), "crop")
    os.makedirs(crop_dir, exist_ok=True)
    img_stem = os.path.splitext(os.path.basename(img_path))[0]

    # Detect banner row: kiểm tra cell r0c0
    cell_r0 = img.crop((COL_STARTS[0], ROW_STARTS[0],
                         COL_STARTS[0] + CELL_W, ROW_STARTS[0] + CELL_H))
    try:
        img_b64 = _img_to_base64(cell_r0)
        result = _ollama_api({
            "model": OLLAMA_MODEL,
            "stream": True,
            "options": {"temperature": 0, "num_predict": 10},
            "messages": [{
                "role": "user",
                "content": 'Is this a player card or a banner/header (like "Top Picks", "Live Transfers")? Reply with only one word: "player" or "banner".',
                "images": [img_b64],
            }],
        }, timeout=30)
        answer = result.get("message", {}).get("content", "").lower()
        is_banner = "banner" in answer
    except Exception:
        is_banner = False

    start_row = 1 if is_banner else 0

    # Chuẩn bị tất cả cells cần OCR
    cells_to_ocr = []
    for ri in range(start_row, 3):
        for ci in range(3):
            x0, y0 = COL_STARTS[ci], ROW_STARTS[ri]
            cell = img.crop((x0, y0, x0 + CELL_W, y0 + CELL_H))
            crop_path = os.path.join(crop_dir, f"{img_stem}_r{ri}c{ci}.png")
            cell.save(crop_path)
            cells_to_ocr.append((ri, ci, cell))

    total_cells = len(cells_to_ocr)
    done_count  = [0]  # list để mutate trong closure

    # Build index tra cứu nhanh từ toàn bộ version data
    latest_data_index = _build_latest_data_index(data_tab)

    # OCR song song — tối đa 3 threads
    results_map = {}  # (ri, ci) → (player, err)

    def ocr_one(ri, ci, cell):
        player, err = _ocr_cell_with_vlm(cell)
        done_count[0] += 1
        if progress_cb:
            progress_cb(done_count[0], total_cells,
                        f"OCR cell r{ri}c{ci} ({done_count[0]}/{total_cells})...")
        return (ri, ci), player, err

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(ocr_one, ri, ci, cell)
                   for ri, ci, cell in cells_to_ocr]
        for fut in as_completed(futures):
            key, player, err = fut.result()
            results_map[key] = (player, err)

    # Ghép kết quả theo thứ tự gốc
    players = []
    for ri, ci, _ in cells_to_ocr:
        player, err = results_map.get((ri, ci), (None, "missing"))
        if player:
            player["_grid"] = f"r{ri}c{ci}"
            player["_err"]  = err or ""

            # ── Auto-map ID: search pid_tab + toàn bộ version data ────────────
            pid, pid_status, existing_row = _resolve_player_id_full(
                player["fname"], player["lname"], pid_tab, latest_data_index
            )
            player["id"]          = pid
            player["_pid_status"] = pid_status

            # ── Lấy nat/club từ version sau cùng nếu đã tồn tại ──────────────
            if existing_row:
                player["nat"]  = existing_row.get("nat",  "") or ""
                player["club"] = existing_row.get("club", "") or ""

            players.append(player)

    return players, start_row


def _build_latest_data_index(data_tab) -> dict:
    """
    Xây dựng index từ toàn bộ version data (cả đã load lẫn chưa load).
    key: (fname_lower, lname_lower)
    value: row có version cao nhất (để lấy nat/club mới nhất)
    """
    if data_tab is None:
        return {}

    all_rows = []

    for vt in data_tab._ver_tabs.values():
        if vt.data is not None:
            # Tab đã load vào memory
            all_rows.extend(vt.data)
        elif os.path.exists(vt.filepath):
            # Tab chưa load — đọc trực tiếp từ file
            try:
                import json as _json
                with open(vt.filepath, encoding="utf-8") as f:
                    all_rows.extend(_json.load(f))
            except Exception:
                pass

    # Giữ row có version cao nhất cho mỗi (fname, lname)
    index = {}
    for row in all_rows:
        f = row.get("fname", "").strip().lower()
        l = row.get("lname", "").strip().lower()
        if not f and not l:
            continue
        key = (f, l)
        existing = index.get(key)
        if existing is None:
            index[key] = row
        else:
            try:
                if int(row.get("version", 0)) > int(existing.get("version", 0)):
                    index[key] = row
            except (ValueError, TypeError):
                pass

    return index


def _resolve_player_id_full(fname: str, lname: str, pid_tab, data_index: dict):
    """
    Tra cứu ID theo thứ tự ưu tiên:
    1. pid_tab.data — case-insensitive
    2. data_index (toàn bộ version data) — case-insensitive
    Nếu không tìm thấy → tạo ID mới.
    Trả về (id, status, existing_row_or_None).
    """
    f = fname.strip().lower()
    l = lname.strip().lower()

    # 1. Tìm trong pid_tab (case-insensitive)
    if pid_tab is not None:
        for r in pid_tab.data:
            if (r.get("fname", "").strip().lower() == f and
                    r.get("lname", "").strip().lower() == l):
                existing = data_index.get((f, l))
                return r["id"], "found", existing

    # 2. Tìm trong toàn bộ version data (pid_tab có thể chưa sync)
    existing = data_index.get((f, l))
    if existing is not None:
        pid = existing.get("id")
        if pid:
            # Sync ngược lại vào pid_tab nếu thiếu
            if pid_tab is not None:
                already = any(
                    r.get("fname", "").strip().lower() == f and
                    r.get("lname", "").strip().lower() == l
                    for r in pid_tab.data
                )
                if not already:
                    pid_tab.data.append({
                        "id":    pid,
                        "fname": existing.get("fname", fname),
                        "lname": existing.get("lname", lname),
                    })
                    try:
                        pid_tab.tbl.refresh()
                    except Exception:
                        pass
            return pid, "found", existing

    # 3. Không có → tạo mới
    if pid_tab is not None:
        new_id = pid_tab.add_player(fname, lname)
        return new_id, "new", None

    return 0, "new", None


# ── OCRTab ────────────────────────────────────────────────────────────────────
class OCRTab(ttk.Frame):
    """OCR market screenshots dùng Qwen2.5-VL → extract player cards → preview → add to version."""

    def __init__(self, parent, data_tab, pid_tab):
        super().__init__(parent)
        self._data_tab = data_tab
        self._pid_tab  = pid_tab
        self._rows     = []
        self._img_path = None
        self._build()

    def _build(self):
        # ── top bar ──────────────────────────────────────────────────────────
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

        # ── model status bar ─────────────────────────────────────────────────
        status_bar = ttk.Frame(self)
        status_bar.pack(fill="x", padx=6, pady=(0, 2))
        self._model_lbl = ttk.Label(status_bar, text="⏳ Đang kiểm tra Ollama...", foreground="#888888")
        self._model_lbl.pack(side="left")
        ttk.Button(status_bar, text="Check model", command=self._check_model_async).pack(side="left", padx=8)
        # Chạy check sau khi UI render xong — không block mainloop
        self.after(500, self._check_model_async)

        # ── image thumbnail + status ──────────────────────────────────────────
        mid = ttk.Frame(self)
        mid.pack(fill="x", padx=6)
        self._thumb_lbl  = ttk.Label(mid)
        self._thumb_lbl.pack(side="left", padx=4, pady=4)
        self._status_lbl = ttk.Label(mid, text="", wraplength=900, justify="left")
        self._status_lbl.pack(side="left", padx=8, fill="x", expand=True)

        # ── progress bar ──────────────────────────────────────────────────────
        self._progress = ttk.Progressbar(self, mode="determinate")
        self._progress.pack(fill="x", padx=6, pady=(0, 2))

        # ── grid cell preview (3x3 thumbnails) ───────────────────────────────
        self._grid_frame = ttk.LabelFrame(self, text="Cell preview (3×3 grid)")
        self._grid_frame.pack(fill="x", padx=6, pady=(0, 4))
        self._cell_labels = []
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

        # ── preview table ─────────────────────────────────────────────────────
        self._preview_frame = ttk.Frame(self)
        self._preview_frame.pack(fill="both", expand=True, padx=4, pady=4)
        self._tree = None

    # ── model check ───────────────────────────────────────────────────────────
    def _check_model_async(self):
        """Chạy check trong thread riêng để không block UI."""
        import threading
        self._model_lbl.config(text="⏳ Đang kiểm tra Ollama...", foreground="#888888")
        threading.Thread(target=self._check_model_worker, daemon=True).start()

    def _check_model_worker(self):
        """Worker chạy trong background thread — update UI qua after()."""
        exe = _find_ollama_exe()
        if not exe:
            self.after(0, lambda: self._model_lbl.config(
                text="⚠ Không tìm thấy ollama.exe — cài Ollama từ https://ollama.com",
                foreground="#cc0000"
            ))
            return

        # Tự khởi động server nếu chưa chạy
        if not _server_responding():
            self.after(0, lambda: self._model_lbl.config(
                text="⏳ Đang khởi động Ollama server...", foreground="#cc6600"
            ))
            ok = _ensure_ollama_server()
            if not ok:
                self.after(0, lambda: self._model_lbl.config(
                    text="⚠ Không thể khởi động Ollama server tự động",
                    foreground="#cc0000"
                ))
                return

        # Check model
        if not _model_pulled():
            self.after(0, lambda: self._model_lbl.config(
                text=f"⚠ Model chưa pull — chạy: ollama pull {OLLAMA_MODEL}",
                foreground="#cc6600"
            ))
        else:
            self.after(0, lambda: self._model_lbl.config(
                text=f"✓ {OLLAMA_MODEL} sẵn sàng",
                foreground="#007700"
            ))

    def _check_model(self):
        """Alias để _run_ocr gọi được — delegate sang async version."""
        self._check_model_async()


    # ── helpers ───────────────────────────────────────────────────────────────
    def _refresh_versions(self):
        # Sắp xếp theo số version để đảm bảo sau cùng = lớn nhất
        vers = sorted(self._data_tab._ver_tabs.keys(), key=lambda v: int(v) if v.isdigit() else 0)
        self._ver_cb["values"] = vers
        if vers:
            self._ver_var.set(vers[-1])  # luôn chọn version sau cùng

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
        """Hiển thị 3×3 thumbnail với viền màu (đỏ=skip, xanh=processed)."""
        try:
            from PIL import Image, ImageTk, ImageDraw
        except ImportError:
            return

        THUMB_W, THUMB_H = 200, 124
        img = Image.open(img_path).convert("RGB")
        self._cell_tk_imgs = []

        for r in range(3):
            for c in range(3):
                x0, y0 = COL_STARTS[c], ROW_STARTS[r]
                cell = img.crop((x0, y0, x0 + CELL_W, y0 + CELL_H))
                cell.thumbnail((THUMB_W, THUMB_H))
                draw = ImageDraw.Draw(cell)
                color = "#cc0000" if r < start_row else "#00aa00"
                draw.rectangle([0, 0, cell.width - 1, cell.height - 1],
                               outline=color, width=3)
                tk_img = ImageTk.PhotoImage(cell)
                self._cell_tk_imgs.append(tk_img)
                self._cell_labels[r][c].config(image=tk_img, text="", width=THUMB_W)

        self._grid_frame.update_idletasks()

    # ── OCR ───────────────────────────────────────────────────────────────────
    def _run_ocr(self):
        if not self._img_path:
            messagebox.showwarning("No image", "Browse to an image first.")
            return

        if not _find_ollama_exe():
            messagebox.showerror(
                "Ollama không tìm thấy",
                "Cài Ollama từ https://ollama.com rồi thử lại."
            )
            return

        # Disable nút Run OCR để tránh double-click
        self._status_lbl.config(text="⏳ Chuẩn bị...")
        self._progress["value"] = 0
        self.update_idletasks()

        import threading
        threading.Thread(target=self._run_ocr_worker, daemon=True).start()

    def _run_ocr_worker(self):
        """Toàn bộ OCR chạy trong background thread — không block UI."""

        def ui(fn):
            """Gọi fn trên UI thread an toàn."""
            self.after(0, fn)

        # Bước 1: đảm bảo server chạy
        if not _server_responding():
            ui(lambda: self._status_lbl.config(text="⏳ Đang khởi động Ollama server..."))
            if not _ensure_ollama_server():
                ui(lambda: messagebox.showerror(
                    "Không thể khởi động Ollama",
                    "Ollama server không phản hồi sau 15 giây.\nThử mở Ollama thủ công."
                ))
                ui(lambda: self._status_lbl.config(text=""))
                return
            # Chờ thêm 1 giây sau khi server respond để API /api/tags sẵn sàng
            time.sleep(1)

        # Bước 2: kiểm tra model (có retry bên trong _model_pulled)
        ui(lambda: self._status_lbl.config(text="⏳ Đang kiểm tra model..."))
        if not _model_pulled():
            ui(lambda: messagebox.showerror(
                "Model chưa có",
                f"Chạy lệnh sau trong terminal:\n\n  ollama pull {OLLAMA_MODEL}\n\nSau đó thử lại."
            ))
            ui(lambda: self._status_lbl.config(text=""))
            return

        ui(lambda: self._status_lbl.config(text="Đang chạy OCR... vui lòng chờ."))

        # Bước 3: chạy OCR — progress_cb update UI qua after()
        def progress_cb(done, total, msg):
            def _update():
                self._progress["maximum"] = total
                self._progress["value"]   = done
                self._status_lbl.config(text=msg)
            ui(_update)

        try:
            rows, start_row = _parse_market_image_vlm(
                self._img_path, pid_tab=self._pid_tab,
                data_tab=self._data_tab, progress_cb=progress_cb
            )
        except Exception as e:
            ui(lambda: messagebox.showerror("OCR Error", str(e)))
            ui(lambda: self._status_lbl.config(text=f"Lỗi: {e}"))
            return

        # Bước 4: cập nhật kết quả lên UI thread
        def _finish():
            self._rows = rows
            self._progress["value"] = self._progress.cget("maximum") or len(rows)
            self._show_grid_preview(self._img_path, start_row)
            self._show_preview()
            # Cập nhật status model
            self._check_model_async()

        ui(_finish)

    def _show_preview(self):
        for w in self._preview_frame.winfo_children():
            w.destroy()

        if not self._rows:
            ttk.Label(self._preview_frame,
                      text="Không tìm thấy thẻ cầu thủ nào. Thử ảnh khác.",
                      foreground="#888888").pack(pady=20)
            self._status_lbl.config(text="Không tìm thấy cầu thủ.")
            return

        # Cột hiển thị: bỏ prc khỏi vị trí gốc, thêm vào cuối cùng với các cột phụ
        all_cols = ([c for c in PREVIEW_COLS if c != "prc"]
                    + ["prc", "pid_status", "grid", "ocr_err", "errors"])

        frame = ttk.Frame(self._preview_frame)
        self._tree = ttk.Treeview(frame, columns=all_cols,
                                   show="headings", selectmode="extended")

        col_widths = {
            "fname": 80, "lname": 80, "nat": 60, "club": 70,
            "pos": 45, "foot": 40, "rate": 40, "hgt": 40,
            "spe": 40, "acc": 40, "sta": 40, "str": 40,
            "con": 40, "pas": 40, "sho": 40, "tac": 40,
            "prc": 65, "id": 55, "version": 55, "status": 45,
            "pid_status": 65, "grid": 50, "ocr_err": 180, "errors": 160,
        }
        for c in all_cols:
            self._tree.heading(c, text=c)
            self._tree.column(c, width=col_widths.get(c, 55),
                              minwidth=30, anchor="center")
        self._tree.column("ocr_err", anchor="w")
        self._tree.column("errors",  anchor="w")

        vsb = ttk.Scrollbar(frame, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        # Màu nền: xanh lá = valid + ID found, xanh dương nhạt = valid + ID mới, đỏ = lỗi
        self._tree.tag_configure("ok_found", background="#e8f5e9")          # xanh lá — ID đã có
        self._tree.tag_configure("ok_new",   background="#e3f2fd")          # xanh dương — ID mới tạo
        self._tree.tag_configure("error",    background="#ffebee")          # đỏ — lỗi validate

        for idx, row in enumerate(self._rows):
            clean = {k: v for k, v in row.items() if not k.startswith("_")}
            errs  = _validate_row(clean)
            pid_status = row.get("_pid_status", "")
            if errs:
                tag = "error"
            elif pid_status == "new":
                tag = "ok_new"
            else:
                tag = "ok_found"

            vals = []
            for c in all_cols:
                if c == "prc":        vals.append(get_price(clean))
                elif c == "pid_status":
                    label = "✓ found" if pid_status == "found" else ("+ new" if pid_status == "new" else pid_status)
                    vals.append(label)
                elif c == "grid":     vals.append(row.get("_grid", ""))
                elif c == "ocr_err":  vals.append(row.get("_err", "")[:60])
                elif c == "errors":   vals.append("; ".join(errs) if errs else "")
                else:                 vals.append(clean.get(c, ""))
            self._tree.insert("", "end", iid=str(idx), values=vals, tags=(tag,))

        frame.pack(fill="both", expand=True)

        ok      = sum(1 for r in self._rows
                      if not _validate_row({k: v for k, v in r.items() if not k.startswith("_")}))
        n_new   = sum(1 for r in self._rows if r.get("_pid_status") == "new")
        n_found = sum(1 for r in self._rows if r.get("_pid_status") == "found")
        self._status_lbl.config(
            text=(f"Tìm thấy {len(self._rows)} thẻ  |  {ok} hợp lệ  |  "
                  f"ID: {n_found} found (xanh lá), {n_new} new (xanh dương)  |  "
                  f"Double-click để sửa  |  Ctrl+click để chọn nhiều")
        )
        self._tree.bind("<Double-Button-1>", self._on_edit_row)

    def _on_edit_row(self, event):
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
            # Tính lại giá từ price_map sau khi sửa rate/pos
            new_row["prc"] = get_price(new_row)
            # Re-resolve ID nếu tên thay đổi
            pid, pid_status = _resolve_player_id(
                new_row.get("fname", ""), new_row.get("lname", ""), self._pid_tab
            )
            new_row["id"]          = pid
            new_row["_pid_status"] = pid_status
            self._rows[idx] = new_row
            # Refresh preview
            self._show_preview()

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
                for r in self._rows
                if not _validate_row({k: v for k, v in r.items() if not k.startswith("_")})]
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
        messagebox.showinfo("Done", f"Đã thêm {n} cầu thủ vào version {label}.")
