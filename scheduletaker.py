import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
import json
import os
from datetime import datetime
from tkinter import ttk
import subprocess
import sys

# Default template schedules
default_weekday_schedule = ["09:00", "12:00", "15:00"]
default_sunday_schedule = ["10:00", "14:00"]

# Dictionary to hold the filenames for each day
file_dict = {}
schedule_dict = {}

BASE_DIR = "Sets"

available_folders = []
available_files = []

def cleanup_old_calendar_files():

    today = datetime.now()

    for filename in os.listdir():

        if (
            filename.startswith("calendar_files_")
            and filename.endswith(".json")
        ):

            try:

                # Aus Dateiname Jahr und Monat extrahieren
                parts = filename.replace(".json", "").split("_")

                year = int(parts[2])
                month = int(parts[3])

                # Alter in Monaten berechnen
                months_old = (
                    (today.year - year) * 12
                    + (today.month - month)
                )

                if months_old > 6:

                    os.remove(filename)

                    print(f"Gelöscht: {filename}")

            except Exception as e:

                print(
                    f"Fehler beim Verarbeiten von {filename}: {e}"
                )

# Function to load available JSON files in the current directory
def load_available_files():
    global available_files
    available_files = [f for f in os.listdir() if f.endswith('.json') and not f.startswith('calendar_files_')]
    if available_files:
        file_var.set(available_files[0])
    else:
        file_var.set('')

# Function to get the monthly JSON file name based on a given date
def get_monthly_filename(year, month):
    return f"calendar_files_{year}_{month:02d}.json"

# Function to load existing data from the monthly JSON file based on the selected date
def load_existing_data(selected_date):
    selected_year = selected_date.year
    selected_month = selected_date.month
    filename = get_monthly_filename(selected_year, selected_month)
    
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def update_calendar_marks():
    calendar.calevent_remove('all')

    for date_str in file_dict.keys():

        date_obj = datetime.strptime(
            date_str,
            "%Y-%m-%d"
        ).date()

        if date_obj.weekday() >= 5:  # Samstag oder Sonntag
            tag = "assigned_weekend"
        else:
            tag = "assigned_weekday"

        calendar.calevent_create(
            date_obj,
            "Plan vorhanden",
            tag
        )

# Function to set the schedule based on the day of the week
def set_default_schedule(date_str):
    parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = parsed_date.weekday()  # Monday is 0 and Sunday is 6
    if weekday == 6:  # Sunday
        return default_sunday_schedule
    elif weekday <= 5:  # Weekdays (Monday to Friday)
        return default_weekday_schedule
    return []

# Function to handle date selection in the calendar
def on_date_change(*args):
    selected_date = calendar.get_date()
    current_file = file_dict.get(selected_date, 'None')

    if current_file != 'None' and os.path.exists(os.path.join(BASE_DIR, current_file)):

        try:
            full_path = os.path.join(BASE_DIR,current_file)

            with open(full_path, "r", encoding="utf-8") as f:
                current_schedule = json.load(f)

        except Exception as e:
            current_schedule = [f"Fehler beim Laden: {e}"]

    else:
        current_schedule = set_default_schedule(selected_date)

    update_current_selection(
        selected_date,
        current_file,
        current_schedule
    )
# Function to update the current selection display
def update_current_selection(selected_date, current_file, current_schedule):

    current_selection_label.config(
        text=f"📅 {selected_date}\n📂 {current_file}"
    )

    if current_schedule:

        schedule_text = ("Läutzeiten:\n\n" + " • ".join(current_schedule))

    else:
        schedule_text = "Keine Läutzeiten vorhanden"

    schedule_label.config(text=schedule_text)

    status_var.set(f"Ausgewähltes Datum: {selected_date}")

# Function to handle file selection for a selected date
def select_file():
    cleanup_old_calendar_files()
    selected_date_str = calendar.get_date()
    selected_folder = folder_var.get()
    selected_file = file_var.get()

    selected_path = os.path.join(
        selected_folder,
        selected_file
    )

    if selected_file:
        file_dict[selected_date_str] = selected_path
        save_to_json()
        if calendar.get_date() == datetime.now().strftime("%Y-%m-%d"):
            trigger_bellringer_reload()
        update_calendar_marks()
        display_selected_files()

        # Datum neu auswerten
        on_date_change()

        status_var.set(
            f"Plan '{selected_file}' zugewiesen"
        )

# Function to display selected files in the listbox
def display_selected_files():
    tree.delete(*tree.get_children())

    weekday_names = [
        "Mo", "Di", "Mi",
        "Do", "Fr", "Sa", "So"
    ]

    for index, (date, file) in enumerate(sorted(file_dict.items())):

        date_obj = datetime.strptime(
            date,
            "%Y-%m-%d"
        )

        display_date = (
            f"{weekday_names[date_obj.weekday()]} "
            f"{date_obj.strftime('%d.%m.%Y')}"
        )

        tag = "evenrow" if index % 2 == 0 else "oddrow"

        tree.insert(
            "",
            tk.END,
            values=(display_date, file),
            tags=(tag,)
        )

# Function to save the filenames and schedules for each day to a monthly JSON file based on the selected date
def save_to_json():
    selected_date_str = calendar.get_date()
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")

    filename = get_monthly_filename(
        selected_date.year,
        selected_date.month
    )

    month_data = {}

    for date_str, assigned_file in file_dict.items():

        date_obj = datetime.strptime(date_str,"%Y-%m-%d")

        if (
            date_obj.year == selected_date.year
            and date_obj.month == selected_date.month
        ):
            month_data[date_str] = assigned_file

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            month_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    status_var.set(f"Gespeichert: {filename}")

# Function to refresh the data displayed
def refresh_data():
    global file_dict

    selected_date_str = calendar.get_date()
    selected_date = datetime.strptime(
        selected_date_str,
        "%Y-%m-%d"
    )

    file_dict = load_existing_data(selected_date)

    update_calendar_marks()
    display_selected_files()

    # Anzeige komplett neu laden
    on_date_change()

    status_var.set("Daten neu geladen")


def delete_assignment():
    selected_date = calendar.get_date()

    if selected_date in file_dict:
        del file_dict[selected_date]
        save_to_json()
        if selected_date == datetime.now().strftime("%Y-%m-%d"):
            trigger_bellringer_reload()
        update_calendar_marks()
        display_selected_files()
        on_date_change()

        status_var.set(f"Zuweisung für {selected_date} gelöscht")
    else:

        messagebox.showinfo(
            "Keine Zuweisung",
            f"Für {selected_date} existiert keine Zuweisung."
        )

def edit_selected_set():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Keine Auswahl",
            "Bitte zuerst einen Eintrag auswählen."
        )
        return

    values = tree.item(selected[0], "values")

    if len(values) < 2:
        return

    assigned_file = values[1]

    full_path = os.path.join(
        BASE_DIR,
        assigned_file
    )

    if not os.path.exists(full_path):
        messagebox.showerror(
            "Datei nicht gefunden",
            full_path
        )
        return

    try:
        subprocess.Popen(
            [
                sys.executable,
                "datemodifier.py",
                full_path
            ]
        )

    except Exception as e:
        messagebox.showerror(
            "Fehler",
            f"Editor konnte nicht gestartet werden:\n{e}"
        )

def delete_selected_assignment():

    selected = tree.selection()

    if not selected:
        return

    values = tree.item(
        selected[0],
        "values"
    )

    display_date = values[0]

    try:

        date_part = display_date.split(" ", 1)[1]

        date_obj = datetime.strptime(
            date_part,
            "%d.%m.%Y"
        )

        date_key = date_obj.strftime(
            "%Y-%m-%d"
        )

    except Exception:
        return

    if not messagebox.askyesno(
        "Zuweisung löschen",
        f"Soll die Zuweisung für\n{display_date}\nwirklich gelöscht werden?"
    ):
        return

    if date_key in file_dict:

        del file_dict[date_key]

        save_to_json()

        display_selected_files()

        update_calendar_marks()

        on_date_change()

        status_var.set(
            f"🗑 Zuweisung für {display_date} gelöscht"
        )

def show_context_menu(event):

    item = tree.identify_row(event.y)

    if item:

        tree.selection_set(item)

        context_menu.post(
            event.x_root,
            event.y_root
        )

def edit_current_day():
    selected_date = calendar.get_date()

    if selected_date not in file_dict:
        messagebox.showinfo(
            "Kein Set zugewiesen",
            "Für das ausgewählte Datum wurde kein Läutset zugewiesen."
        )
        return

    assigned_file = file_dict[selected_date]

    full_path = os.path.join(
        BASE_DIR,
        assigned_file
    )

    if not os.path.exists(full_path):
        messagebox.showerror(
            "Datei nicht gefunden",
            full_path
        )
        return

    try:
        subprocess.Popen(
            [
                sys.executable,
                "datemodifier.py",
                full_path
            ]
        )

    except Exception as e:
        messagebox.showerror(
            "Fehler",
            f"Editor konnte nicht gestartet werden:\n{e}"
        )

def load_folders():

    global available_folders

    available_folders = [
        folder
        for folder in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, folder))
    ]

    available_folders.sort()

    folder_dropdown["values"] = available_folders

    if available_folders:
        folder_var.set(available_folders[0])
        load_files_for_folder()

def load_files_for_folder():

    selected_folder = folder_var.get()

    if not selected_folder:
        return

    folder_path = os.path.join(
        BASE_DIR,
        selected_folder
    )

    files = [
        file
        for file in os.listdir(folder_path)
        if file.endswith(".json")
    ]

    files.sort()

    file_dropdown["values"] = files

    if files:
        file_var.set(files[0])
    else:
        file_var.set("")

def on_folder_change(event=None):
    load_files_for_folder()

def trigger_bellringer_reload():

    try:

        with open(
            "bellringer.reload",
            "w"
        ) as f:

            f.write(
                str(datetime.now())
            )

    except Exception as e:

        print(
            f"Reload konnte nicht angefordert werden: {e}"
        )


# GUI Setup
app = tk.Tk()
app.title("🔔 Glockenplaner")
app.configure(bg="#f4f6f9")
app.geometry("1000x750")
app.minsize(900, 600)

style = ttk.Style()
style.theme_use("clam")

# Allgemein
style.configure(
    ".",
    background="#f4f6f9",
    foreground="#2c3e50",
    font=("Segoe UI", 10)
)

# LabelFrames
style.configure(
    "TLabelframe",
    background="#ffffff",
    borderwidth=1
)

style.configure(
    "TLabelframe.Label",
    font=("Segoe UI", 11, "bold"),
    foreground="#1f4e78"
)

# Labels
style.configure(
    "TLabel",
    background="#ffffff",
    foreground="#2c3e50"
)

# Buttons
style.configure(
    "Accent.TButton",
    font=("Segoe UI", 10, "bold")
)

style.configure(
    "Icon.TButton",
    padding=1
)

# Treeview
style.configure(
    "Treeview",
    rowheight=28,
    font=("Segoe UI", 10)
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 10, "bold")
)

# ==========================
# Root Layout
# ==========================

content_frame = ttk.Frame(app)
content_frame.pack(fill="both", expand=True)

main_frame = ttk.Frame(content_frame, padding=15)
main_frame.pack(fill="both", expand=True)

left_frame = ttk.Frame(main_frame)
left_frame.pack(side="left", fill="y", padx=(0, 15))

right_frame = ttk.Frame(main_frame)
right_frame.pack(side="right", fill="both", expand=True)

left_frame.configure(style="Card.TFrame")
right_frame.configure(style="Card.TFrame")

style.configure(
    "Card.TFrame",
    background="#f4f6f9"
)

# ==========================
# Calendar
# ==========================

calendar_label = ttk.Label(
    left_frame,
    text="📅 Kalender",
    font=("Arial", 12, "bold")
)
calendar_label.pack(anchor="w")

calendar = Calendar(
    left_frame,
    selectmode="day",
    date_pattern="yyyy-mm-dd",
    font=("Segoe UI", 10),

    background="#1f4e78",
    foreground="white",

    selectbackground="#0078d4",
    selectforeground="white",

    headersbackground="#1f4e78",
    headersforeground="white",

    normalbackground="white",
    normalforeground="#2c3e50",

    weekendbackground="#f5f5f5",
    weekendforeground="#d9534f",

    bordercolor="#d0d0d0"
)
calendar.pack(pady=10)

# Tage mit gespeichertem Plan markieren
calendar.tag_config(
    "assigned_weekday",
    background="#dff0d8",
    foreground="#2c3e50"
)

calendar.tag_config(
    "assigned_weekend",
    background="#dff0d8",
    foreground="#d9534f"
)

calendar.bind("<<CalendarSelected>>", lambda event: refresh_data())

# ==========================
# Load data
# ==========================

selected_date_str = calendar.get_date()
selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")

file_dict = load_existing_data(selected_date)

folder_var = tk.StringVar()
file_var = tk.StringVar()
load_available_files()

# ==========================
# Information Card
# ==========================

info_frame = ttk.LabelFrame(
    right_frame,
    text="Ausgewähltes Datum",
    padding=15
)
info_frame.pack(fill="x", pady=(0, 15))

selection_frame = ttk.Frame(info_frame)

selection_frame.pack(
    fill="x",
    pady=5
)

current_selection_label = ttk.Label(
    selection_frame,
    text="Kein Plan ausgewählt",
    font=("Segoe UI", 13, "bold")
)

current_selection_label.pack(
    side="left",
    fill="x",
    expand=True
)

edit_day_button = ttk.Button(
    selection_frame,
    text="🖉",
    width=2,
    style="Icon.TButton",
    command=edit_current_day
)

edit_day_button.pack(
    side="right",
    padx=(10, 0)
)

schedule_label = ttk.Label(
    info_frame,
    text="Keine Läutzeiten vorhanden",
    justify="left",
    font=("Segoe UI", 11),
    wraplength=600
)
schedule_label.pack(anchor="w")


# ==========================
# Schedule assignment section
# ==========================

assign_frame = ttk.LabelFrame(
    right_frame,
    text="📂 Läutplan zuweisen",
    padding=15
)
assign_frame.pack(fill="x", pady=(0, 15))

folder_var = tk.StringVar()

folder_dropdown = ttk.Combobox(
    assign_frame,
    textvariable=folder_var,
    state="readonly"
)

folder_dropdown.pack(
    fill="x",
    pady=(5, 10)
)

folder_dropdown.bind(
    "<<ComboboxSelected>>",
    on_folder_change
)
file_var = tk.StringVar()

file_dropdown = ttk.Combobox(
    assign_frame,
    textvariable=file_var,
    state="readonly"
)

file_dropdown.pack(fill="x")
load_folders()

button_frame = ttk.Frame(assign_frame)
button_frame.pack(fill="x", pady=10)

select_file_button = ttk.Button(
    button_frame,
    text="Zuweisen",
    command=select_file
)
select_file_button.pack(side="left", padx=5)

delete_button = ttk.Button(
    button_frame,
    text="🗑 Zuweisung löschen",
    command=delete_assignment
)
delete_button.pack(side="left", padx=5)


save_button = ttk.Button(
    button_frame,
    text="💾 Speichern",
    command=save_to_json
)
save_button.pack(side="left", padx=5)


# ==========================
# Monthly Assignments
# ==========================

table_frame = ttk.LabelFrame(
    right_frame,
    text="📋 Zuweisungen für den angezeigten Monat",
    padding=10
)
table_frame.pack(fill="both", expand=True)

columns = ("Datum", "Plan")

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=6
)

tree.bind(
    "<Double-1>",
    lambda event: edit_selected_set()
)

tree.bind(
    "<Button-3>",
    show_context_menu
)

tree.tag_configure(
    "oddrow",
    background="#f8f9fa"
)

tree.tag_configure(
    "evenrow",
    background="#ffffff"
)


tree.heading("Datum", text="Datum")
tree.heading("Plan", text="Läutplan")

tree.column("Datum", width=180)
tree.column("Plan", width=500)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ==========================
# Status Bar
# ==========================

status_var = tk.StringVar()
status_var.set("Bereit")

status_bar = tk.Label(
    content_frame,
    textvariable=status_var,
    bg="#1f4e78",
    fg="white",
    anchor="w",
    padx=10,
    pady=5,
    font=("Segoe UI", 9)
)

status_bar.pack(
    side="bottom",
    fill="x"
)

# Run the GUI application
display_selected_files()
update_calendar_marks()
on_date_change()

app.update_idletasks()

required_width = app.winfo_reqwidth()
required_height = app.winfo_reqheight()

app.geometry(
    f"{max(required_width,1000)}x{max(required_height,700)}"
)

### context menu ###

context_menu = tk.Menu(
    app,
    tearoff=0
)

context_menu.add_command(
    label="✏️ Set bearbeiten",
    command=edit_selected_set
)

context_menu = tk.Menu(
    app,
    tearoff=0
)

context_menu.add_command(
    label="✏️ Set bearbeiten",
    command=edit_selected_set
)


context_menu.add_separator()

context_menu.add_command(
    label="🗑 Zuweisung löschen",
    command=delete_selected_assignment
)

app.mainloop()
