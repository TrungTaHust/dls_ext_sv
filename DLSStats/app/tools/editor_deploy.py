# editor_deploy.py — DeployPanel: nut "Update to web" chay toan bo pipeline
# build + git push + vercel deploy ngam, khong block UI.
#
# Pipeline (tuan tu, chay trong background thread):
#   1. sencha app clean          (tai workspace goc DLSStats)
#   2. sencha app build
#   3. git add -A + commit + push  (repo DLSStats, branch hien tai)
#   4. robocopy build/production/DLSStats -> Desktop/dls-ext
#   5. git add -A + commit + push  (repo dls-ext, branch hien tai)
#   6. vercel --prod               (tai dls-ext)

import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────
WORKSPACE     = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILD_SRC     = os.path.join(WORKSPACE, "build", "production", "DLSStats")
DEPLOY_TARGET = os.path.join(os.path.expanduser("~"), "Desktop", "all", "dls-ext")


# ── Helpers ────────────────────────────────────────────────────────────────────
def _run(cmd: list[str], cwd: str, log_cb, ok_codes: set = None, shell: bool = False):
    """
    Chay lenh, stream tung dong output ve log_cb.
    shell=True: can thiet cho cac lenh la .cmd/.ps1 script tren Windows (vercel, sencha).
    ok_codes: tap exit code duoc coi la thanh cong (mac dinh {0}).
    """
    if ok_codes is None:
        ok_codes = {0}
    log_cb(f"$ {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd if not shell else " ".join(cmd),
        cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace",
        shell=shell,
        creationflags=0 if shell else subprocess.CREATE_NO_WINDOW,
    )
    for line in proc.stdout:
        line = line.rstrip()
        if line:
            log_cb(line)
    proc.wait()
    if proc.returncode not in ok_codes:
        raise RuntimeError(f"Command failed (exit {proc.returncode}): {' '.join(cmd)}")


def _git_push(cwd: str, message: str, log_cb) -> bool:
    """
    Kiem tra thay doi, neu co thi add + commit + push.
    Neu khong co gi thay doi thi skip toan bo, tra ve False.
    Tra ve True neu da push thanh cong.
    """
    # Lay branch hien tai
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=cwd, capture_output=True, text=True
    )
    branch = result.stdout.strip() or "main"
    log_cb(f"[git] branch: {branch}  |  cwd: {cwd}")

    # Kiem tra co thay doi khong (tracked + untracked)
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=cwd, capture_output=True, text=True
    )
    if not status.stdout.strip():
        log_cb("[git] No changes detected — skipping add/commit/push.")
        return False

    # Co thay doi — hien thi summary
    lines = status.stdout.strip().splitlines()
    log_cb(f"[git] {len(lines)} changed file(s):")
    for ln in lines[:10]:   # hien toi da 10 dong de khong spam log
        log_cb(f"       {ln}")
    if len(lines) > 10:
        log_cb(f"       ... and {len(lines)-10} more")

    _run(["git", "add", "-A"], cwd, log_cb)
    _run(["git", "commit", "-m", message], cwd, log_cb)
    _run(["git", "push", "origin", branch], cwd, log_cb)
    return True


# ── Deploy pipeline ────────────────────────────────────────────────────────────
STEPS = [
    "sencha app clean",
    "sencha app build",
    "git push (DLSStats)",
    "copy build → dls-ext",
    "git push (dls-ext)",
    "vercel --prod",
]


def run_pipeline(log_cb, step_cb, done_cb):
    """
    Chạy toàn bộ pipeline. Gọi từ background thread.
    log_cb(str)       — append dòng log
    step_cb(int, str) — cập nhật bước hiện tại (index, tên)
    done_cb(bool, str)— kết thúc (success, message)
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_cb(f"\n{'='*60}")
    log_cb(f"Deploy started at {ts}")
    log_cb(f"{'='*60}")

    try:
        # ── Bước 1: sencha app clean ──────────────────────────────────────────
        step_cb(0, STEPS[0])
        _run(["sencha", "app", "clean"], WORKSPACE, log_cb, shell=True)

        # ── Bước 2: sencha app build ──────────────────────────────────────────
        step_cb(1, STEPS[1])
        _run(["sencha", "app", "build"], WORKSPACE, log_cb, shell=True)

        # ── Bước 3: git push DLSStats ─────────────────────────────────────────
        step_cb(2, STEPS[2])
        commit_msg = f"deploy: update {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        _git_push(WORKSPACE, commit_msg, log_cb)

        # ── Bước 4: copy build → dls-ext ─────────────────────────────────────
        step_cb(3, STEPS[3])
        if not os.path.isdir(BUILD_SRC):
            raise RuntimeError(f"Build output not found: {BUILD_SRC}")
        if not os.path.isdir(DEPLOY_TARGET):
            raise RuntimeError(f"Deploy target not found: {DEPLOY_TARGET}")
        log_cb(f"Copying {BUILD_SRC} -> {DEPLOY_TARGET}")
        _run([
            "robocopy", BUILD_SRC, DEPLOY_TARGET,
            "/E",          # copy subdirs including empty
            "/PURGE",      # xoa file cu trong dest khong con trong source
            "/XD", ".git", ".vercel", "node_modules",  # giu lai cac thu muc nay
            "/XF", ".gitignore", ".gitattributes", "vercel.json", "package.json",  # giu lai cac file config
            "/NFL",        # no file list
            "/NDL",        # no dir list
            "/NJH",        # no job header
            "/NJS",        # no job summary
        ], WORKSPACE, log_cb, ok_codes=set(range(8)))
        log_cb("Copy complete.")

        # ── Bước 5: git push dls-ext ──────────────────────────────────────────
        step_cb(4, STEPS[4])
        _git_push(DEPLOY_TARGET, commit_msg, log_cb)

        # ── Bước 6: vercel --prod ─────────────────────────────────────────────
        step_cb(5, STEPS[5])
        _run(["vercel", "--prod", "--yes"], DEPLOY_TARGET, log_cb, shell=True)

        done_cb(True, "Deploy completed successfully!")

    except RuntimeError as e:
        log_cb(f"\nERROR: {e}")
        done_cb(False, str(e))
    except Exception as e:
        log_cb(f"\nUNEXPECTED ERROR: {e}")
        done_cb(False, str(e))


# ── DeployPanel widget ─────────────────────────────────────────────────────────
class DeployPanel(ttk.Frame):
    """
    Một Frame nhỏ chứa nút 'Update to web' và log panel.
    Có thể nhúng vào bất kỳ tab nào.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._running = False
        self._build()

    def _build(self):
        # ── Top bar ───────────────────────────────────────────────────────────
        top = ttk.Frame(self)
        top.pack(fill="x", padx=6, pady=6)

        self._deploy_btn = ttk.Button(
            top, text="🚀  Update to web",
            command=self._start_deploy,
            style="Accent.TButton",
        )
        self._deploy_btn.pack(side="left", padx=4)

        self._status_lbl = ttk.Label(top, text="Ready", foreground="#555555")
        self._status_lbl.pack(side="left", padx=12)

        ttk.Button(top, text="Clear log", command=self._clear_log).pack(side="right", padx=4)

        # ── Step indicators ───────────────────────────────────────────────────
        steps_frame = ttk.LabelFrame(self, text=" Pipeline steps ")
        steps_frame.pack(fill="x", padx=6, pady=(0, 4))

        self._step_vars = []
        self._step_lbls = []
        for i, name in enumerate(STEPS):
            row = ttk.Frame(steps_frame)
            row.pack(fill="x", padx=8, pady=1)
            var = tk.StringVar(value="○")
            lbl_icon = ttk.Label(row, textvariable=var, width=2, font=("Segoe UI", 11))
            lbl_icon.pack(side="left")
            lbl_name = ttk.Label(row, text=name, foreground="#555555")
            lbl_name.pack(side="left", padx=4)
            self._step_vars.append(var)
            self._step_lbls.append(lbl_name)

        # ── Progress bar ──────────────────────────────────────────────────────
        self._progress = ttk.Progressbar(self, mode="determinate",
                                          maximum=len(STEPS))
        self._progress.pack(fill="x", padx=6, pady=(0, 4))

        # ── Log area ──────────────────────────────────────────────────────────
        log_frame = ttk.LabelFrame(self, text=" Log ")
        log_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self._log = tk.Text(log_frame, wrap="none", font=("Consolas", 9),
                            bg="#1e1e1e", fg="#d4d4d4",
                            insertbackground="white", state="disabled")
        vsb = ttk.Scrollbar(log_frame, orient="vertical",   command=self._log.yview)
        hsb = ttk.Scrollbar(log_frame, orient="horizontal", command=self._log.xview)
        self._log.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._log.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        # Tag màu cho log
        self._log.tag_configure("error",   foreground="#f48771")
        self._log.tag_configure("success", foreground="#89d185")
        self._log.tag_configure("step",    foreground="#4ec9b0", font=("Consolas", 9, "bold"))
        self._log.tag_configure("cmd",     foreground="#9cdcfe")

    # ── Log helpers ───────────────────────────────────────────────────────────
    def _append_log(self, text: str):
        """Thread-safe log append."""
        self.after(0, lambda t=text: self._do_append(t))

    def _do_append(self, text: str):
        self._log.configure(state="normal")
        # Chọn tag dựa trên nội dung
        if text.startswith("$"):
            tag = "cmd"
        elif "ERROR" in text.upper() or "FAILED" in text.upper():
            tag = "error"
        elif text.startswith("[step]"):
            tag = "step"
        else:
            tag = ""
        self._log.insert("end", text + "\n", tag)
        self._log.see("end")
        self._log.configure(state="disabled")

    def _clear_log(self):
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")

    # ── Step update ───────────────────────────────────────────────────────────
    def _update_step(self, idx: int, name: str):
        """Thread-safe step update."""
        self.after(0, lambda i=idx, n=name: self._do_update_step(i, n))

    def _do_update_step(self, idx: int, name: str):
        # Reset tất cả về pending
        for i, (var, lbl) in enumerate(zip(self._step_vars, self._step_lbls)):
            if i < idx:
                var.set("✓")
                lbl.config(foreground="#89d185")
            elif i == idx:
                var.set("▶")
                lbl.config(foreground="#4ec9b0", font=("Segoe UI", 10, "bold"))
            else:
                var.set("○")
                lbl.config(foreground="#555555", font=("Segoe UI", 10))
        self._progress["value"] = idx
        self._status_lbl.config(
            text=f"Step {idx+1}/{len(STEPS)}: {name}",
            foreground="#4ec9b0"
        )
        self._append_log(f"[step] ── {name} ──")

    def _mark_all_done(self, success: bool):
        for var, lbl in zip(self._step_vars, self._step_lbls):
            if success:
                var.set("✓")
                lbl.config(foreground="#89d185", font=("Segoe UI", 10))
            else:
                # Giữ nguyên trạng thái hiện tại, chỉ đổi icon bước đang chạy
                pass
        self._progress["value"] = len(STEPS) if success else self._progress["value"]

    # ── Deploy ────────────────────────────────────────────────────────────────
    def _start_deploy(self):
        if self._running:
            messagebox.showwarning("Busy", "Deploy đang chạy, vui lòng chờ.")
            return

        self._running = True
        self._deploy_btn.config(state="disabled")
        self._status_lbl.config(text="Running...", foreground="#4ec9b0")
        self._progress["value"] = 0

        # Reset step icons
        for var, lbl in zip(self._step_vars, self._step_lbls):
            var.set("○")
            lbl.config(foreground="#555555", font=("Segoe UI", 10))

        threading.Thread(
            target=run_pipeline,
            args=(self._append_log, self._update_step, self._on_done),
            daemon=True,
        ).start()

    def _on_done(self, success: bool, message: str):
        """Gọi từ background thread — schedule UI update về main thread."""
        self.after(0, lambda: self._do_done(success, message))

    def _do_done(self, success: bool, message: str):
        self._running = False
        self._deploy_btn.config(state="normal")
        self._mark_all_done(success)

        if success:
            self._status_lbl.config(text="✓ Done!", foreground="#89d185")
            self._append_log(f"\n✓ {message}")
        else:
            self._status_lbl.config(text="✗ Failed", foreground="#f48771")
            self._append_log(f"\n✗ {message}")
            messagebox.showerror("Deploy failed", message)
