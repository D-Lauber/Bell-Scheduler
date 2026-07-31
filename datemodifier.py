import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import json
import re
import os
import sys

# =====================================
# Daten
# =====================================

timestamps = []

BASE_DIR = "Sets"

os.makedirs(BASE_DIR, exist_ok=True)

# =====================================
# Funktionen
# =====================================

def is_valid_time(time_string):
    pattern = r"^\d{2}:\d{2}$"

    if re.match(pattern, time_string):
        try:
            hour, minute = map(int, time_string.split(":"))
            return 0 <= hour < 24 and 0 <= minute < 60
        except ValueError:
            return False

    return False


def get_subfolders():
    return [
        folder
        for folder in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, folder))
    ]


def refresh_tree():

    tree.delete(*tree.get_children())

    timestamps.sort()

    for index, timestamp in enumerate(timestamps):

        tag = "evenrow" if index % 2 == 0 else "oddrow"

        tree.insert(
            "",
            tk.END,
            values=(timestamp,),
            tags=(tag,)
        )


def update_file_list(event=None):

    folder = folder_var.get()

    if not folder:
        return

    folder_path = os.path.join(BASE_DIR, folder)

    files = [
        file
        for file in os.listdir(folder_path)
        if file.endswith(".json")
    ]

    file_select["values"] = files

    if files:
        file_select.current(0)


def load_set():

    global timestamps

    folder = folder_var.get()
    filename = file_var.get()

    if not folder or not filename:

        messagebox.showerror(
            "Fehler",
            "Bitte Ordner und Läut-Set auswählen."
        )
        return

    path = os.path.join(
        BASE_DIR,
        folder,
        filename
    )

    try:

        with open(path, "r", encoding="utf-8") as file:
            timestamps = json.load(file)

        refresh_tree()

        status_var.set(
            f"📂 Geladen: {filename}"
        )

    except Exception as e:

        messagebox.showerror(
            "Fehler",
            f"Datei konnte nicht geladen werden:\n\n{e}"
        )

def load_set_by_path(full_path):
    global timestamps

    try:

        with open(
            full_path,
            "r",
            encoding="utf-8"
        ) as file:

            timestamps = json.load(file)

        relative_path = os.path.relpath(
            full_path,
            BASE_DIR
        )

        folder = os.path.dirname(relative_path)
        filename = os.path.basename(relative_path)

        folder_var.set(folder)
        update_file_list()
        file_var.set(filename)

        refresh_tree()

        status_var.set(
            f"📂 Geladen: {filename}"
        )

    except Exception as e:

        messagebox.showerror(
            "Fehler",
            f"Datei konnte nicht geladen werden:\n\n{e}"
        )

def add_timestamp():

    timestamp = entry.get().strip()

    if not is_valid_time(timestamp):

        messagebox.showerror(
            "Ungültige Uhrzeit",
            "Bitte eine Uhrzeit im Format HH:MM eingeben."
        )
        return

    timestamps.append(timestamp)

    refresh_tree()
    autosave()

    entry.delete(0, tk.END)

    status_var.set(
        f"🔔 Läutzeit {timestamp} hinzugefügt"
    )


def remove_selected():

    selected = tree.selection()

    if not selected:
        return

    for item in selected:

        value = tree.item(item)["values"][0]

        if value in timestamps:
            timestamps.remove(value)

    refresh_tree()
    autosave()

    status_var.set(
        "🗑 Läutzeit entfernt"
    )


def edit_timestamp(event):

    selected = tree.selection()

    if not selected:
        return

    item = selected[0]

    old_time = tree.item(item)["values"][0]

    new_time = simpledialog.askstring(
        "Zeit bearbeiten",
        "Neue Uhrzeit:",
        initialvalue=old_time
    )

    if not new_time:
        return

    if not is_valid_time(new_time):

        messagebox.showerror(
            "Fehler",
            "Ungültiges Zeitformat."
        )
        return

    index = timestamps.index(old_time)

    timestamps[index] = new_time

    refresh_tree()
    autosave()

    status_var.set(
        f"✏️ Geändert: {old_time} → {new_time}"
    )


def save_changes():

    folder = folder_var.get()
    filename = file_var.get()

    if not folder or not filename:

        messagebox.showerror(
            "Fehler",
            "Kein Läut-Set ausgewählt."
        )
        return

    path = os.path.join(
        BASE_DIR,
        folder,
        filename
    )

    timestamps.sort()

    try:

        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                timestamps,
                file,
                indent=4
            )

        status_var.set(
            f"💾 Gespeichert: {filename}"
        )

        messagebox.showinfo(
            "Erfolg",
            "Die Änderungen wurden gespeichert."
        )

        with open("bellringer.reload","w") as f:
            f.write(str(datetime.now()))

    except Exception as e:

        messagebox.showerror(
            "Fehler",
            f"Speichern fehlgeschlagen:\n\n{e}"
        )

def autosave():
    folder = folder_var.get()
    filename = file_var.get()

    if not folder or not filename:
        return

    path = os.path.join(BASE_DIR, folder, filename)

    timestamps.sort()

    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                timestamps,
                file,
                indent=4
            )

        with open("bellringer.reload", "w") as f:
            f.write(str(datetime.now()))

        status_var.set(
            f"💾 AutoSave: {filename} ({datetime.now().strftime('%H:%M:%S')})"
        )

    except Exception as e:
        print(f"AutoSave Fehler: {e}")
    

# =====================================
# GUI
# =====================================

app = tk.Tk()

app.title("🔧 Läut-Set bearbeiten")
app.geometry("750x650")
app.minsize(650, 500)

# =====================================
# Styling
# =====================================

app.configure(bg="#f4f6f9")

style = ttk.Style()
style.theme_use("clam")

style.configure(
    ".",
    background="#f4f6f9",
    foreground="#2c3e50",
    font=("Segoe UI", 10)
)

style.configure(
    "TLabelframe",
    background="#ffffff",
    borderwidth=1
)

style.configure(
    "TLabelframe.Label",
    background="#ffffff",
    foreground="#1f4e78",
    font=("Segoe UI", 11, "bold")
)

style.configure(
    "TLabel",
    background="#ffffff",
    foreground="#2c3e50"
)

style.configure(
    "Treeview",
    rowheight=26,
    font=("Segoe UI", 10)
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 10, "bold")
)

# =====================================
# Hauptbereich
# =====================================

main_frame = ttk.Frame(
    app,
    padding=15
)

main_frame.pack(
    fill="both",
    expand=True
)

title_label = ttk.Label(
    main_frame,
    text="🔧 Vorhandenes Läut-Set bearbeiten",
    font=("Segoe UI", 14, "bold")
)

title_label.pack(
    anchor="w",
    pady=(0, 15)
)

# =====================================
# Set auswählen
# =====================================

load_frame = ttk.LabelFrame(
    main_frame,
    text="📂 Läut-Set laden",
    padding=15
)

load_frame.pack(
    fill="x",
    pady=(0, 15)
)

load_row = ttk.Frame(load_frame)
load_row.pack(fill="x")

folder_var = tk.StringVar()
file_var = tk.StringVar()

folder_select = ttk.Combobox(
    load_row,
    textvariable=folder_var,
    state="readonly",
    width=20
)

folder_select["values"] = get_subfolders()

folder_select.pack(
    side="left",
    padx=(0, 10)
)

folder_select.bind(
    "<<ComboboxSelected>>",
    update_file_list
)

file_select = ttk.Combobox(
    load_row,
    textvariable=file_var,
    state="readonly",
    width=30
)

file_select.pack(
    side="left",
    padx=(0, 10)
)

load_button = ttk.Button(
    load_row,
    text="📂 Laden",
    command=load_set
)

load_button.pack(side="left")

# =====================================
# Zweispaltenbereich
# =====================================

top_frame = ttk.Frame(main_frame)
top_frame.pack(fill="both", expand=True)

left_frame = ttk.Frame(top_frame)
left_frame.pack(
    side="left",
    fill="y",
    padx=(0, 10)
)

right_frame = ttk.Frame(top_frame)
right_frame.pack(
    side="left",
    fill="both",
    expand=True
)

# =====================================
# Neue Zeit
# =====================================

input_frame = ttk.LabelFrame(
    left_frame,
    text="🔔 Läutzeit verwalten",
    padding=15
)

input_frame.pack(
    fill="x",
    anchor="n"
)

entry = ttk.Entry(
    input_frame,
    width=10,
    font=("Segoe UI", 12)
)

entry.pack(
    fill="x",
    pady=(0, 10)
)

add_button = ttk.Button(
    input_frame,
    text="➕ Hinzufügen",
    command=add_timestamp
)

add_button.pack(
    fill="x"
)

remove_button = ttk.Button(
    input_frame,
    text="🗑 Entfernen",
    command=remove_selected
)

remove_button.pack(
    fill="x",
    pady=(10, 0)
)

save_button = ttk.Button(
    input_frame,
    text="💾 Änderungen speichern",
    command=save_changes
)

save_button.pack(
    fill="x",
    pady=(10, 0)
)

# =====================================
# Tabelle
# =====================================

table_frame = ttk.LabelFrame(
    right_frame,
    text="📋 Läutzeiten",
    padding=10
)

table_frame.pack(
    fill="both",
    expand=True
)

tree = ttk.Treeview(
    table_frame,
    columns=("Zeit",),
    show="headings"
)

tree.heading(
    "Zeit",
    text="Zeit"
)

tree.column(
    "Zeit",
    width=100,
    anchor="center"
)

tree.tag_configure(
    "evenrow",
    background="#ffffff"
)

tree.tag_configure(
    "oddrow",
    background="#f8f9fa"
)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(
    yscrollcommand=scrollbar.set
)

tree.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)

tree.bind(
    "<Double-1>",
    edit_timestamp
)



# =====================================
# Statusleiste
# =====================================

status_var = tk.StringVar()

status_var.set("Bereit")

status_bar = tk.Label(
    app,
    textvariable=status_var,
    bg="#1f4e78",
    fg="white",
    anchor="w",
    padx=10,
    pady=4
)

status_bar.pack(
    side="bottom",
    fill="x"
)

# =====================================
# Start
# =====================================
if len(sys.argv) > 1:

    passed_file = sys.argv[1]

    if os.path.exists(passed_file):

        app.after(
            200,
            lambda: load_set_by_path(
                passed_file
            )
        )

app.mainloop()
