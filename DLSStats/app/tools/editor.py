"""
DLS Stats Editor — entry point.

Module layout:
  editor_config.py   — paths, constants, price_map, helper functions
  editor_widgets.py  — EditDialog, TreeTable, RenameEntry
  editor_tabs.py     — VersionTab, DataTab, SpecialTab, PlayerIDTab, PriceMapTab
  editor_import.py   — ImportTab + shared preview/validation helpers
  editor_ocr.py      — OCRTab + PaddleOCR engine helpers (disabled, kept for future use)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk

from editor_config import setup_styles
from editor_tabs import DataTab, SpecialTab, PlayerIDTab, PriceMapTab
from editor_import import ImportTab
# OCR tab disabled — code kept in editor_ocr.py for future use
# from editor_ocr import OCRTab, _ocr_available, _get_paddle_engine


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

    nb.add(data_tab,                          text=" data.json ")
    nb.add(SpecialTab(nb),                    text=" special.json ")
    nb.add(pid_tab,                           text=" playerID ")
    nb.add(PriceMapTab(nb),                   text=" Price Map ")
    nb.add(ImportTab(nb, data_tab, pid_tab),  text=" Import ")
    # nb.add(OCRTab(nb, data_tab, pid_tab),   text=" OCR ")  # disabled


if __name__ == "__main__":
  App().mainloop()
