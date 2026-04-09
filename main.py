import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

DATA_FILE = "tasks.json"

BG       = "#1e1e2e"
SIDEBAR  = "#181825"
CARD     = "#313244"
CARD2    = "#45475a"
ACCENT   = "#cba6f7"
GREEN    = "#a6e3a1"
RED      = "#f38ba8"
YELLOW   = "#f9e2af"
BLUE     = "#89b4fa"
TEXT     = "#cdd6f4"
SUBTEXT  = "#a6adc8"

class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List — Rajesh Prajapat")
        self.geometry("720x580")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.tasks = []
        self.filter_var = tk.StringVar(value="All")
        self.load_tasks()
        self.build_ui()
        self.render_tasks()

    # ── Persistence ───────────────────────────────────────────────────────────
    def load_tasks(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE) as f:
                    self.tasks = json.load(f)
            except Exception:
                self.tasks = []

    def save_tasks(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.tasks, f, indent=2)

    # ── UI ────────────────────────────────────────────────────────────────────
    def build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=SIDEBAR, height=62)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="My To-Do List", bg=SIDEBAR, fg=ACCENT,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=20, pady=14)
        self.stats_lbl = tk.Label(hdr, text="", bg=SIDEBAR, fg=SUBTEXT,
                                   font=("Segoe UI", 9))
        self.stats_lbl.pack(side="right", padx=20)

        # Input row
        inp = tk.Frame(self, bg=BG, pady=14)
        inp.pack(fill="x", padx=20)
        self.task_var = tk.StringVar()
        self.entry = tk.Entry(inp, textvariable=self.task_var, bg=CARD, fg=TEXT,
                              insertbackground=TEXT, relief="flat",
                              font=("Segoe UI", 12), width=40)
        self.entry.pack(side="left", ipady=8, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.add_task())
        self.entry.focus()
        tk.Button(inp, text="+ Add Task", bg=ACCENT, fg=BG, font=("Segoe UI", 11, "bold"),
                  relief="flat", cursor="hand2", padx=16, pady=7,
                  command=self.add_task).pack(side="left")

        # Filter + clear row
        flt = tk.Frame(self, bg=BG)
        flt.pack(fill="x", padx=20, pady=(0, 10))
        for label in ["All", "Pending", "Completed"]:
            tk.Radiobutton(flt, text=label, variable=self.filter_var, value=label,
                           bg=BG, fg=SUBTEXT, selectcolor=BG, activebackground=BG,
                           activeforeground=ACCENT, font=("Segoe UI", 10),
                           cursor="hand2", command=self.render_tasks).pack(side="left", padx=6)
        tk.Button(flt, text="Clear Completed", bg=CARD, fg=RED, font=("Segoe UI", 9),
                  relief="flat", cursor="hand2", padx=10, pady=3,
                  command=self.clear_completed).pack(side="right")

        # Scrollable task list
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=BG)
        self.inner.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Mouse wheel scroll
        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ── Logic ─────────────────────────────────────────────────────────────────
    def add_task(self):
        text = self.task_var.get().strip()
        if not text:
            messagebox.showwarning("Empty", "Please enter a task!")
            return
        self.tasks.insert(0, {
            "id": int(datetime.now().timestamp() * 1000),
            "text": text,
            "done": False,
            "created": datetime.now().strftime("%d %b %Y, %I:%M %p")
        })
        self.save_tasks()
        self.task_var.set("")
        self.render_tasks()

    def toggle(self, tid):
        for t in self.tasks:
            if t["id"] == tid:
                t["done"] = not t["done"]
                break
        self.save_tasks()
        self.render_tasks()

    def delete_task(self, tid):
        self.tasks = [t for t in self.tasks if t["id"] != tid]
        self.save_tasks()
        self.render_tasks()

    def clear_completed(self):
        done = [t for t in self.tasks if t["done"]]
        if not done:
            messagebox.showinfo("Nothing", "No completed tasks.")
            return
        if messagebox.askyesno("Clear", f"Remove {len(done)} completed task(s)?"):
            self.tasks = [t for t in self.tasks if not t["done"]]
            self.save_tasks()
            self.render_tasks()

    # ── Render ────────────────────────────────────────────────────────────────
    def render_tasks(self):
        for w in self.inner.winfo_children():
            w.destroy()

        f = self.filter_var.get()
        shown = self.tasks
        if f == "Pending":
            shown = [t for t in self.tasks if not t["done"]]
        elif f == "Completed":
            shown = [t for t in self.tasks if t["done"]]

        total = len(self.tasks)
        done  = sum(1 for t in self.tasks if t["done"])
        self.stats_lbl.config(
            text=f"Done: {done}  |  Pending: {total-done}  |  Total: {total}")

        if not shown:
            tk.Label(self.inner, text="No tasks here!", bg=BG, fg=SUBTEXT,
                     font=("Segoe UI", 12)).pack(pady=40)
            return

        for task in shown:
            self.make_card(task)

    def make_card(self, task):
        card = tk.Frame(self.inner, bg=CARD, pady=10, padx=14)
        card.pack(fill="x", pady=4, padx=2)

        # Status dot
        dot_color = GREEN if task["done"] else YELLOW
        tk.Label(card, text="●", bg=CARD, fg=dot_color,
                 font=("Segoe UI", 14)).pack(side="left", padx=(0, 8))

        # Checkbox
        var = tk.BooleanVar(value=task["done"])
        tk.Checkbutton(card, variable=var, bg=CARD, activebackground=CARD,
                       selectcolor=CARD2, cursor="hand2",
                       command=lambda tid=task["id"]: self.toggle(tid)).pack(side="left")

        # Text + date
        mid = tk.Frame(card, bg=CARD)
        mid.pack(side="left", fill="x", expand=True)

        fg     = SUBTEXT if task["done"] else TEXT
        strike = "overstrike" if task["done"] else "normal"
        tk.Label(mid, text=task["text"], bg=CARD, fg=fg,
                 font=("Segoe UI", 11, strike), anchor="w").pack(fill="x")
        tk.Label(mid, text=f"Added: {task['created']}", bg=CARD, fg=SUBTEXT,
                 font=("Segoe UI", 8)).pack(anchor="w")

        # Delete
        tk.Button(card, text="X", bg=CARD, fg=RED, relief="flat",
                  font=("Segoe UI", 11, "bold"), cursor="hand2", bd=0,
                  command=lambda tid=task["id"]: self.delete_task(tid)).pack(side="right")

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
