import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import signal

scheduler_process = None

PLANNER_SCRIPT = "scheduletaker.py"
SETS_SCRIPT = "datetaker.py"
SCHEDULER_SCRIPT = "bellringer.py"
MODIFIER_SCRIPT = "datemodifier.py"

PID_FILE = "scheduler.pid"


# =====================================================
# Anwendungen starten
# =====================================================

def open_planner():
    try:
        subprocess.Popen(
            [sys.executable, PLANNER_SCRIPT]
        )

        status_var.set(
            "Glockenplaner gestartet"
        )

    except Exception as e:
        messagebox.showerror(
            "Fehler",
            str(e)
        )


def open_sets():
    try:
        subprocess.Popen(
            [sys.executable, SETS_SCRIPT]
        )

        status_var.set(
            "Set-Erstellung gestartet"
        )

    except Exception as e:
        messagebox.showerror(
            "Fehler",
            str(e)
        )

def open_modifier():
    try:
        subprocess.Popen(
            [sys.executable, MODIFIER_SCRIPT]
        )

        status_var.set(
            "Set-Bearbeitung gestartet"
        )

    except Exception as e:
        messagebox.showerror(
            "Fehler",
            str(e)
        )

# =====================================================
# Scheduler
# =====================================================

def scheduler_running():

    if not os.path.exists(PID_FILE):
        return False

    try:

        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        os.kill(pid, 0)

        return True

    except Exception:
        return False


def start_scheduler():
    global scheduler_process

    if scheduler_process and scheduler_process.poll() is None:
        scheduler_status_var.set("🟢 Läuft bereits")
        return

    scheduler_process = subprocess.Popen(
        [sys.executable, SCHEDULER_SCRIPT]
    )

    scheduler_status_var.set("🟢 Läuft")


def stop_scheduler():

    global scheduler_process

    if scheduler_process and scheduler_process.poll() is None:

        scheduler_process.terminate()

        scheduler_status_var.set("🔴 Gestoppt")


def update_scheduler_status():

    if scheduler_process is not None:

        if scheduler_process.poll() is None:
            scheduler_status_var.set("🟢 Läuft")
        else:
            scheduler_status_var.set("🔴 Gestoppt")

    else:
        scheduler_status_var.set("🔴 Gestoppt")

    app.after(1000, update_scheduler_status)


# =====================================================
# GUI
# =====================================================

app = tk.Tk()

app.title("🔔 Glockenverwaltung")

app.geometry("650x500")

app.configure(bg="#f4f6f9")

# -------------------------

style = ttk.Style()

style.theme_use("clam")

style.configure(
    ".",
    background="#f4f6f9",
    foreground="#2c3e50",
    font=("Segoe UI", 10)
)

style.configure(
    "Card.TFrame",
    background="#ffffff"
)

style.configure(
    "Title.TLabel",
    background="#ffffff",
    foreground="#1f4e78",
    font=("Segoe UI", 18, "bold")
)

style.configure(
    "Info.TLabel",
    background="#ffffff",
    foreground="#2c3e50"
)

style.configure(
    "Launcher.TButton",
    font=("Segoe UI", 11, "bold")
)

# =====================================================
# Hauptbereich
# =====================================================

main_frame = ttk.Frame(
    app,
    padding=20,
    style="Card.TFrame"
)

main_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)

title_label = ttk.Label(
    main_frame,
    text="🔔 Glockenverwaltung",
    style="Title.TLabel"
)

title_label.pack(
    pady=(10, 20)
)

# =====================================================
# Tools
# =====================================================

tools_frame = ttk.LabelFrame(
    main_frame,
    text="Werkzeuge",
    padding=15
)

tools_frame.pack(
    fill="x",
    pady=(0, 20)
)

planner_button = ttk.Button(
    tools_frame,
    text="📅 Läut-Sets zuweisen",
    command=open_planner,
    width=30
)

planner_button.pack(
    pady=5
)

sets_button = ttk.Button(
    tools_frame,
    text="➕ Läut-Set erstellen",
    command=open_sets,
    width=30
)

sets_button.pack(
    pady=5
)

modifier_button = ttk.Button(
    tools_frame,
    text="🔧 Läut-Set bearbeiten",
    command=open_modifier,
    width=30
)

modifier_button.pack(
    pady=5
)

# =====================================================
# Scheduler
# =====================================================

scheduler_frame = ttk.LabelFrame(
    main_frame,
    text="Automatischer Scheduler",
    padding=15
)

scheduler_frame.pack(
    fill="x"
)

ttk.Label(
    scheduler_frame,
    text="Status:"
).pack()

scheduler_status_var = tk.StringVar()

scheduler_label = ttk.Label(
    scheduler_frame,
    textvariable=scheduler_status_var,
    font=("Segoe UI", 12, "bold")
)

scheduler_label.pack(
    pady=10
)

scheduler_button_frame = ttk.Frame(
    scheduler_frame
)

scheduler_button_frame.pack()

start_button = ttk.Button(
    scheduler_button_frame,
    text="▶ Starten",
    command=start_scheduler,
    width=15
)

start_button.pack(
    side="left",
    padx=5
)

stop_button = ttk.Button(
    scheduler_button_frame,
    text="⏹ Stoppen",
    command=stop_scheduler,
    width=15
)

stop_button.pack(
    side="left",
    padx=5
)

# =====================================================
# Statusleiste
# =====================================================

status_var = tk.StringVar()

status_var.set("Bereit")

status_bar = tk.Label(
    app,
    textvariable=status_var,
    bg="#1f4e78",
    fg="white",
    anchor="w",
    padx=10,
    pady=5
)

status_bar.pack(
    side="bottom",
    fill="x"
)

# =====================================================
# Statusüberwachung starten
# =====================================================

update_scheduler_status()

app.mainloop()
