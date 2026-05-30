"""
editor_checklist.py — ChecklistTab: two side-by-side tables for clubs and nations.

Each table has columns: checkbox (✓/blank), name, update (0/1), and for clubs: nation.
Rows with update=1 have a yellow background (matching the reference screenshot).
Users can add/delete rows and toggle the checkbox by clicking.
Data is persisted to resources/data/checklist.json.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ── Data file path ─────────────────────────────────────────────────────────────
CHECKLIST_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "resources", "data", "checklist.json"
)

# ── Default data ───────────────────────────────────────────────────────────────
DEFAULT_CLUBS = [
    {"club": "Arsenal",          "update": 1, "nation": "ENG"},
    {"club": "Aston Villa",      "update": 1, "nation": "ENG"},
    {"club": "Bournemouth",      "update": 1, "nation": "ENG"},
    {"club": "Brentford",        "update": 1, "nation": "ENG"},
    {"club": "Brighton",         "update": 1, "nation": "ENG"},
    {"club": "Burnley",          "update": 1, "nation": "ENG"},
    {"club": "Chelsea",          "update": 1, "nation": "ENG"},
    {"club": "Crystal Palace",   "update": 1, "nation": "ENG"},
    {"club": "Everton",          "update": 1, "nation": "ENG"},
    {"club": "Fulham",           "update": 1, "nation": "ENG"},
    {"club": "Leeds",            "update": 1, "nation": "ENG"},
    {"club": "Liverpool",        "update": 1, "nation": "ENG"},
    {"club": "Man City",         "update": 1, "nation": "ENG"},
    {"club": "Man United",       "update": 1, "nation": "ENG"},
    {"club": "Newcastle",        "update": 1, "nation": "ENG"},
    {"club": "Nottingham",       "update": 1, "nation": "ENG"},
    {"club": "Sunderland",       "update": 1, "nation": "ENG"},
    {"club": "Tottenham",        "update": 1, "nation": "ENG"},
    {"club": "West Ham",         "update": 1, "nation": "ENG"},
    {"club": "Wolves",           "update": 1, "nation": "ENG"},
    {"club": "Blackburn",        "update": 1, "nation": "ENG1"},
    {"club": "Bristol",          "update": 1, "nation": "ENG1"},
    {"club": "Charlton",         "update": 1, "nation": "ENG1"},
    {"club": "Coventry",         "update": 1, "nation": "ENG1"},
    {"club": "Derby",            "update": 1, "nation": "ENG1"},
    {"club": "Hull",             "update": 1, "nation": "ENG1"},
    {"club": "Ipswich",          "update": 1, "nation": "ENG1"},
    {"club": "Leicester",        "update": 1, "nation": "ENG1"},
    {"club": "Middlesbrough",    "update": 1, "nation": "ENG1"},
    {"club": "Oxford",           "update": 1, "nation": "ENG1"},
    {"club": "Portsmouth",       "update": 1, "nation": "ENG1"},
    {"club": "Sheffield United", "update": 1, "nation": "ENG1"},
    {"club": "Sheffield W",      "update": 1, "nation": "ENG1"},
    {"club": "Swansea",          "update": 1, "nation": "ENG1"},
    {"club": "Alaves",           "update": 1, "nation": "ESP"},
    {"club": "Athletic Bilbao",  "update": 1, "nation": "ESP"},
    {"club": "Atletico Madrid",  "update": 1, "nation": "ESP"},
    {"club": "Barcelona",        "update": 1, "nation": "ESP"},
    {"club": "Celta Vigo",       "update": 1, "nation": "ESP"},
    {"club": "Cornella",         "update": 1, "nation": "ESP"},
    {"club": "Elche",            "update": 1, "nation": "ESP"},
    {"club": "Getafe",           "update": 1, "nation": "ESP"},
    {"club": "Girona",           "update": 1, "nation": "ESP"},
    {"club": "Levante",          "update": 1, "nation": "ESP"},
    {"club": "Mallorca",         "update": 1, "nation": "ESP"},
    {"club": "Osasuna",          "update": 1, "nation": "ESP"},
    {"club": "Oviedo",           "update": 1, "nation": "ESP"},
    {"club": "Rayo Vallecano",   "update": 1, "nation": "ESP"},
    {"club": "Real Betis",       "update": 1, "nation": "ESP"},
    {"club": "Real Madrid",      "update": 1, "nation": "ESP"},
    {"club": "Real Sociedad",    "update": 1, "nation": "ESP"},
    {"club": "Sevilla",          "update": 1, "nation": "ESP"},
    {"club": "Valencia",         "update": 1, "nation": "ESP"},
    {"club": "Villareal",        "update": 1, "nation": "ESP"},
    {"club": "Angers",           "update": 1, "nation": "FRA"},
    {"club": "Auxerre",          "update": 1, "nation": "FRA"},
    {"club": "Brest",            "update": 1, "nation": "FRA"},
    {"club": "Le Havre",         "update": 1, "nation": "FRA"},
    {"club": "Lens",             "update": 1, "nation": "FRA"},
    {"club": "Lille",            "update": 1, "nation": "FRA"},
    {"club": "Lorient",          "update": 1, "nation": "FRA"},
    {"club": "Lyon",             "update": 1, "nation": "FRA"},
    {"club": "Marseille",        "update": 1, "nation": "FRA"},
    {"club": "Metz",             "update": 1, "nation": "FRA"},
    {"club": "Monaco",           "update": 1, "nation": "FRA"},
    {"club": "Nantes",           "update": 1, "nation": "FRA"},
    {"club": "Nice",             "update": 1, "nation": "FRA"},
    {"club": "Paris",            "update": 1, "nation": "FRA"},
    {"club": "Paris SG",         "update": 1, "nation": "FRA"},
    {"club": "Rennes",           "update": 1, "nation": "FRA"},
    {"club": "Strasbourg",       "update": 1, "nation": "FRA"},
    {"club": "Toulouse",         "update": 1, "nation": "FRA"},
    {"club": "AC Milan",         "update": 1, "nation": "ITA"},
    {"club": "Atalanta",         "update": 1, "nation": "ITA"},
    {"club": "Bologna",          "update": 1, "nation": "ITA"},
    {"club": "Cagliari",         "update": 1, "nation": "ITA"},
    {"club": "Como",             "update": 1, "nation": "ITA"},
    {"club": "Cremonese",        "update": 1, "nation": "ITA"},
    {"club": "Fiorentina",       "update": 1, "nation": "ITA"},
    {"club": "Genoa",            "update": 1, "nation": "ITA"},
    {"club": "Inter Milan",      "update": 1, "nation": "ITA"},
    {"club": "Juventus",         "update": 1, "nation": "ITA"},
    {"club": "Lazio",            "update": 1, "nation": "ITA"},
    {"club": "Lecce",            "update": 1, "nation": "ITA"},
    {"club": "Napoli",           "update": 1, "nation": "ITA"},
    {"club": "Parma",            "update": 1, "nation": "ITA"},
    {"club": "Pisa",             "update": 1, "nation": "ITA"},
    {"club": "Roma",             "update": 1, "nation": "ITA"},
    {"club": "Sassuolo",         "update": 1, "nation": "ITA"},
    {"club": "Torino",           "update": 1, "nation": "ITA"},
    {"club": "Udinese",          "update": 1, "nation": "ITA"},
    {"club": "Verona",           "update": 1, "nation": "ITA"},
    {"club": "PSV",              "update": 1, "nation": "NED"},
    {"club": "Benfica",          "update": 1, "nation": "POR"},
    {"club": "Porto",            "update": 1, "nation": "POR"},
    {"club": "S Lisbon",         "update": 1, "nation": "POR"},
    {"club": "Aberdeen",         "update": 1, "nation": "SCO"},
    {"club": "Celtic",           "update": 1, "nation": "SCO"},
    {"club": "Dundee",           "update": 1, "nation": "SCO"},
    {"club": "Dundee U",         "update": 1, "nation": "SCO"},
    {"club": "Glasgow R",        "update": 1, "nation": "SCO"},
    {"club": "Hearts",           "update": 1, "nation": "SCO"},
    {"club": "Hibernian",        "update": 1, "nation": "SCO"},
    {"club": "Kilmarnock",       "update": 1, "nation": "SCO"},
    {"club": "Livingston",       "update": 1, "nation": "SCO"},
    {"club": "Motherwell",       "update": 1, "nation": "SCO"},
    {"club": "S Mirren",         "update": 1, "nation": "SCO"},
    {"club": "Birmingham",       "update": 0, "nation": "ENG1"},
    {"club": "Cardiff",          "update": 0, "nation": "ENG1"},
    {"club": "Huddersfield",     "update": 0, "nation": "ENG1"},
    {"club": "Luton",            "update": 0, "nation": "ENG1"},
    {"club": "Millwall",         "update": 0, "nation": "ENG1"},
    {"club": "Norwich",          "update": 0, "nation": "ENG1"},
    {"club": "Plymouth",         "update": 0, "nation": "ENG1"},
    {"club": "Preston",          "update": 0, "nation": "ENG1"},
    {"club": "Queens Park R",    "update": 0, "nation": "ENG1"},
    {"club": "Rotherham",        "update": 0, "nation": "ENG1"},
    {"club": "Southampton",      "update": 0, "nation": "ENG1"},
    {"club": "Stoke",            "update": 0, "nation": "ENG1"},
    {"club": "Watford",          "update": 0, "nation": "ENG1"},
    {"club": "West Bromwich",    "update": 0, "nation": "ENG1"},
    {"club": "Wigan",            "update": 0, "nation": "ENG1"},
    {"club": "Wrexham",          "update": 0, "nation": "ENG1"},
    {"club": "Almeria",          "update": 0, "nation": "ESP"},
    {"club": "Cadiz",            "update": 0, "nation": "ESP"},
    {"club": "Eibar",            "update": 0, "nation": "ESP"},
    {"club": "Granada",          "update": 0, "nation": "ESP"},
    {"club": "Las Palmas",       "update": 0, "nation": "ESP"},
    {"club": "Leganes",          "update": 0, "nation": "ESP"},
    {"club": "Valladolid",       "update": 0, "nation": "ESP"},
    {"club": "Clermont-Ferrand", "update": 0, "nation": "FRA"},
    {"club": "Montpellier",      "update": 0, "nation": "FRA"},
    {"club": "Reims",            "update": 0, "nation": "FRA"},
    {"club": "Saint-Etienne",    "update": 0, "nation": "FRA"},
    {"club": "Empoli",           "update": 0, "nation": "ITA"},
    {"club": "Frosinone",        "update": 0, "nation": "ITA"},
    {"club": "Monza",            "update": 0, "nation": "ITA"},
    {"club": "Salernitana",      "update": 0, "nation": "ITA"},
    {"club": "Venezia",          "update": 0, "nation": "ITA"},
    {"club": "Ajax",             "update": 0, "nation": "NED"},
    {"club": "Alkmaar",          "update": 0, "nation": "NED"},
    {"club": "Breda",            "update": 0, "nation": "NED"},
    {"club": "Feyenoord",        "update": 1, "nation": "NED"},
    {"club": "GA Eagles",        "update": 0, "nation": "NED"},
    {"club": "Heerenveen",       "update": 0, "nation": "NED"},
    {"club": "Heracles Almelo",  "update": 0, "nation": "NED"},
    {"club": "Nijmegen",         "update": 0, "nation": "NED"},
    {"club": "Rotterdam",        "update": 0, "nation": "NED"},
    {"club": "Sittard",          "update": 0, "nation": "NED"},
    {"club": "Twente",           "update": 0, "nation": "NED"},
    {"club": "Utrecht",          "update": 0, "nation": "NED"},
    {"club": "V Arnhem",         "update": 0, "nation": "NED"},
    {"club": "Vizela",           "update": 0, "nation": "NED"},
    {"club": "Waalwijk",         "update": 0, "nation": "NED"},
    {"club": "Willem",           "update": 0, "nation": "NED"},
    {"club": "Zwolle",           "update": 0, "nation": "NED"},
    {"club": "Alverca",          "update": 0, "nation": "POR"},
    {"club": "Arouca",           "update": 0, "nation": "POR"},
    {"club": "Aves",             "update": 0, "nation": "POR"},
    {"club": "Azores",           "update": 0, "nation": "POR"},
    {"club": "Barcelos",         "update": 0, "nation": "POR"},
    {"club": "Boavista",         "update": 0, "nation": "POR"},
    {"club": "Braga",            "update": 1, "nation": "POR"},
    {"club": "Casa P",           "update": 0, "nation": "POR"},
    {"club": "Chaves",           "update": 0, "nation": "POR"},
    {"club": "E Amadora",        "update": 0, "nation": "POR"},
    {"club": "Estoril",          "update": 0, "nation": "POR"},
    {"club": "Famalicao",        "update": 0, "nation": "POR"},
    {"club": "Farense",          "update": 0, "nation": "POR"},
    {"club": "Guimaraes",        "update": 0, "nation": "POR"},
    {"club": "Moreirense",       "update": 0, "nation": "POR"},
    {"club": "N Funchal",        "update": 0, "nation": "POR"},
    {"club": "Portimao",         "update": 0, "nation": "POR"},
    {"club": "Rio Ave",          "update": 0, "nation": "POR"},
    {"club": "Tondela",          "update": 0, "nation": "POR"},
    {"club": "Vitoria",          "update": 0, "nation": "POR"},
    {"club": "Falkirk",          "update": 0, "nation": "SCO"},
    {"club": "Ross C",           "update": 0, "nation": "SCO"},
    {"club": "S Johnstone",      "update": 0, "nation": "SCO"},
]

DEFAULT_NATIONS = [
    {"nation": "Australia",     "updated": 1},
    {"nation": "Austria",       "updated": 1},
    {"nation": "Belgium",       "updated": 1},
    {"nation": "Cameroon",      "updated": 1},
    {"nation": "Colombia",      "updated": 1},
    {"nation": "Costa Rica",    "updated": 1},
    {"nation": "Croatia",       "updated": 1},
    {"nation": "Czech Republic","updated": 1},
    {"nation": "Denmark",       "updated": 1},
    {"nation": "DR Congo",      "updated": 1},
    {"nation": "Egypt",         "updated": 1},
    {"nation": "France",        "updated": 1},
    {"nation": "Ghana",         "updated": 1},
    {"nation": "Greece",        "updated": 1},
    {"nation": "Hungary",       "updated": 1},
    {"nation": "Ireland",       "updated": 1},
    {"nation": "Morocco",       "updated": 1},
    {"nation": "New Zealand",   "updated": 1},
    {"nation": "Panama",        "updated": 1},
    {"nation": "Paraguay",      "updated": 1},
    {"nation": "Peru",          "updated": 1},
    {"nation": "Romania",       "updated": 1},
    {"nation": "Scotland",      "updated": 1},
    {"nation": "Slovenia",      "updated": 1},
    {"nation": "South Africa",  "updated": 1},
    {"nation": "South Korea",   "updated": 1},
    {"nation": "Spain",         "updated": 1},
    {"nation": "Sweden",        "updated": 1},
    {"nation": "Switzerland",   "updated": 1},
    {"nation": "Ukraine",       "updated": 1},
    {"nation": "Uruguay",       "updated": 1},
    {"nation": "Argentina",     "updated": 0},
    {"nation": "Chile",         "updated": 0},
    {"nation": "England",       "updated": 0},
    {"nation": "Indonesia",     "updated": 0},
    {"nation": "Italy",         "updated": 0},
    {"nation": "Japan",         "updated": 0},
    {"nation": "Norway",        "updated": 0},
    {"nation": "Portugal",      "updated": 0},
]


# ── Load / Save ────────────────────────────────────────────────────────────────
def _load_checklist():
    if os.path.exists(CHECKLIST_FILE):
        try:
            with open(CHECKLIST_FILE, encoding="utf-8") as f:
                data = json.load(f)
            return data.get("clubs", DEFAULT_CLUBS), data.get("nations", DEFAULT_NATIONS)
        except Exception:
            pass
    return [dict(r) for r in DEFAULT_CLUBS], [dict(r) for r in DEFAULT_NATIONS]


def _save_checklist(clubs, nations):
    os.makedirs(os.path.dirname(CHECKLIST_FILE), exist_ok=True)
    with open(CHECKLIST_FILE, "w", encoding="utf-8") as f:
        json.dump({"clubs": clubs, "nations": nations}, f, ensure_ascii=False, indent=2)


def get_club_list() -> list[str]:
    """Trả về danh sách tên club sorted a-z, đọc từ checklist.json (hoặc default)."""
    clubs, _ = _load_checklist()
    return sorted({r["club"] for r in clubs if r.get("club")}, key=str.lower)


def get_nation_list() -> list[str]:
    """Trả về danh sách tên nation sorted a-z, đọc từ checklist.json (hoặc default)."""
    _, nations = _load_checklist()
    return sorted({r["nation"] for r in nations if r.get("nation")}, key=str.lower)


# ── ChecklistTable — reusable single-table widget ─────────────────────────────
class ChecklistTable(ttk.Frame):
    """
    A scrollable Treeview-based checklist table.
    columns: list of str — column names (first col is always the checkbox col)
    check_col: which column holds the 0/1 update flag
    Clicking a row toggles its checkbox and auto-saves.
    """

    CHECK_ON  = "✓"
    CHECK_OFF = ""
    COLOR_ON  = "#fffacd"   # light yellow — updated=1
    COLOR_OFF = "#ffffff"   # white        — updated=0

    def __init__(self, parent, data: list, name_col: str, check_col: str,
                 extra_cols: list = None, on_change=None):
        super().__init__(parent)
        self._data      = data
        self._name_col  = name_col
        self._check_col = check_col
        self._extra_cols = extra_cols or []
        self._on_change = on_change
        self._build()

    def _build(self):
        # Toolbar
        tb = ttk.Frame(self)
        tb.pack(fill="x", padx=4, pady=4)
        ttk.Button(tb, text="Add",    command=self._add_row).pack(side="left", padx=2)
        ttk.Button(tb, text="Delete", command=self._delete_row).pack(side="left", padx=2)
        ttk.Button(tb, text="Sort",   command=self._sort_data).pack(side="left", padx=2)
        self._count_lbl = ttk.Label(tb, text="")
        self._count_lbl.pack(side="left", padx=8)
        ttk.Label(tb, text="(click row to toggle ✓)",
                  foreground="#888888").pack(side="right", padx=4)

        # Treeview
        display_cols = ["check", self._name_col] + self._extra_cols + [self._check_col]
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        self._tree = ttk.Treeview(container, columns=display_cols,
                                   show="headings", selectmode="browse")

        # Column widths
        col_widths = {
            "check":    36,
            "club":    160,
            "nation":   60,
            "update":   60,
            "updated":  60,
        }
        col_heads = {
            "check":   "✓",
            "update":  "update",
            "updated": "updated",
        }
        for c in display_cols:
            w = col_widths.get(c, 120)
            h = col_heads.get(c, c)
            self._tree.heading(c, text=h)
            self._tree.column(c, width=w, minwidth=30,
                              anchor="center" if c in ("check", "update", "updated", "nation") else "w")

        vsb = ttk.Scrollbar(container, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self._tree.tag_configure("on",  background=self.COLOR_ON)
        self._tree.tag_configure("off", background=self.COLOR_OFF)

        self._tree.bind("<ButtonRelease-1>", self._on_click)
        self.refresh()

    def refresh(self):
        self._tree.delete(*self._tree.get_children())
        on_count = 0
        for idx, row in enumerate(self._data):
            flag = int(row.get(self._check_col, 0))
            if flag:
                on_count += 1
            check_sym = self.CHECK_ON if flag else self.CHECK_OFF
            tag = "on" if flag else "off"
            vals = [check_sym, row.get(self._name_col, "")]
            for ec in self._extra_cols:
                vals.append(row.get(ec, ""))
            vals.append(flag)
            self._tree.insert("", "end", iid=str(idx), values=vals, tags=(tag,))
        total = len(self._data)
        self._count_lbl.config(text=f"{on_count} / {total} updated")

    def _on_click(self, event):
        region = self._tree.identify_region(event.x, event.y)
        if region not in ("cell", "tree"):
            return
        sel = self._tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        row = self._data[idx]
        # Toggle
        row[self._check_col] = 0 if int(row.get(self._check_col, 0)) else 1
        self.refresh()
        # Re-select same row
        try:
            self._tree.selection_set(str(idx))
            self._tree.see(str(idx))
        except Exception:
            pass
        if self._on_change:
            self._on_change()

    def _sort_data(self):
        """
        Sort in-place theo quy tắc:
        - Nation table : update desc (1 trước) → nation a-z
        - Club table   : update desc (1 trước) → nation a-z → club a-z
        Sau đó refresh và auto-save.
        """
        if self._name_col == "nation":
            # sort: updated desc, nation a-z
            self._data.sort(key=lambda r: (
                -int(r.get(self._check_col, 0)),
                r.get(self._name_col, "").lower(),
            ))
        else:
            # sort: update desc, nation a-z, club a-z
            self._data.sort(key=lambda r: (
                -int(r.get(self._check_col, 0)),
                r.get("nation", "").lower(),
                r.get(self._name_col, "").lower(),
            ))
        self.refresh()
        if self._on_change:
            self._on_change()

    def _add_row(self):
        name = simpledialog.askstring(
            "Add", f"Enter {self._name_col} name:", parent=self
        )
        if not name or not name.strip():
            return
        name = name.strip()
        new_row = {self._name_col: name, self._check_col: 0}
        if self._extra_cols:
            for ec in self._extra_cols:
                val = simpledialog.askstring("Add", f"Enter {ec}:", parent=self) or ""
                new_row[ec] = val.strip()
        self._data.append(new_row)
        self.refresh()
        if self._on_change:
            self._on_change()

    def _delete_row(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select a row to delete.", parent=self)
            return
        idx = int(sel[0])
        name = self._data[idx].get(self._name_col, "")
        if messagebox.askyesno("Delete", f'Delete "{name}"?', parent=self):
            self._data.pop(idx)
            self.refresh()
            if self._on_change:
                self._on_change()


# ── ChecklistTab ───────────────────────────────────────────────────────────────
class ChecklistTab(ttk.Frame):
    """Main tab: two side-by-side checklist tables (clubs | nations)."""

    def __init__(self, parent):
        super().__init__(parent)
        self._clubs, self._nations = _load_checklist()
        self._build()

    def _build(self):
        # Top bar
        top = ttk.Frame(self)
        top.pack(fill="x", padx=6, pady=4)
        ttk.Button(top, text="Save", command=self._save).pack(side="right", padx=4)
        self._saved_lbl = ttk.Label(top, text="", foreground="#007700")
        self._saved_lbl.pack(side="right", padx=4)

        # Two-pane layout
        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        # Left: clubs
        left_frame = ttk.LabelFrame(panes, text=" Clubs ")
        self._club_tbl = ChecklistTable(
            left_frame,
            data=self._clubs,
            name_col="club",
            check_col="update",
            extra_cols=["nation"],
            on_change=self._on_change,
        )
        self._club_tbl.pack(fill="both", expand=True)
        panes.add(left_frame, weight=3)

        # Right: nations
        right_frame = ttk.LabelFrame(panes, text=" Nations ")
        self._nation_tbl = ChecklistTable(
            right_frame,
            data=self._nations,
            name_col="nation",
            check_col="updated",
            extra_cols=[],
            on_change=self._on_change,
        )
        self._nation_tbl.pack(fill="both", expand=True)
        panes.add(right_frame, weight=1)

    def _on_change(self):
        """Auto-save on every toggle."""
        _save_checklist(self._clubs, self._nations)
        self._saved_lbl.config(text="Saved ✓")
        self.after(2000, lambda: self._saved_lbl.config(text=""))

    def _save(self):
        _save_checklist(self._clubs, self._nations)
        self._saved_lbl.config(text="Saved ✓")
        self.after(2000, lambda: self._saved_lbl.config(text=""))
