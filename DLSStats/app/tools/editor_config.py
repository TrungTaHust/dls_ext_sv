import json
import os
from tkinter import ttk

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
AUX_COLS_DATA    = ["prc", "pos_id", "price_id"]
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
