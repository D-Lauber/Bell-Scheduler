import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
import json
import os
from datetime import datetime

# Default template schedules
default_weekday_schedule = ["09:00", "12:00", "15:00"]
default_sunday_schedule = ["10:00", "14:00"]

# Dictionary to hold the filenames for each day
file_dict = {}
schedule_dict = {}

# Function to load available JSON files in the current directory
def load_available_files():
    global available_files
    available_files = [f for f in os.listdir() if f.endswith('.json')]
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
    current_schedule = schedule_dict.get(selected_date, set_default_schedule(selected_date))
    update_current_selection(selected_date, current_file, current_schedule)

# Function to update the current selection display
def update_current_selection(selected_date, current_file, current_schedule):
    current_selection_label.config(text=f"Momentan gewähltes Set für {selected_date}: {current_file}")
    schedule_label.config(text=f"Momentane Läutzeiten: {', '.join(current_schedule)}")

# Function to handle file selection for a selected date
def select_file():
    selected_date_str = calendar.get_date()
    selected_file = file_var.get()
    if selected_file:
        file_dict[selected_date_str] = selected_file
        display_selected_files()
        update_current_selection(selected_date_str, selected_file, schedule_dict.get(selected_date_str, set_default_schedule(selected_date_str)))

# Function to display selected files in the listbox
def display_selected_files():
    listbox.delete(0, tk.END)
    for date, file in file_dict.items():
        listbox.insert(tk.END, f"{date}: {file}")

# Function to save the filenames and schedules for each day to a monthly JSON file based on the selected date
def save_to_json():
    # Parse the selected date from the calendar
    selected_date_str = calendar.get_date()
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
    
    # Get the filename based on the selected date
    filename = get_monthly_filename(selected_date.year, selected_date.month)
    
    # Load existing data from the corresponding JSON file
    existing_data = load_existing_data(selected_date)
    
    # Update the data with new entries from the file_dict
    existing_data.update(file_dict)
    
    # Save the updated data back to the JSON file
    with open(filename, 'w') as file:
        json.dump(existing_data, file, indent=4)
    
    messagebox.showinfo("Erfolg", f"Zuweisungen gespeichert in {filename}")

# Function to refresh the data displayed
def refresh_data():
    global file_dict, schedule_dict
    selected_date_str = calendar.get_date()
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
    
    file_dict = load_existing_data(selected_date)
    current_schedule = schedule_dict.get(selected_date_str, set_default_schedule(selected_date_str))
    update_current_selection(selected_date_str, file_dict.get(selected_date_str, 'None'), current_schedule)
    display_selected_files()

# GUI Setup
app = tk.Tk()
app.title("Kalender-Applikation")
app.geometry("600x400")

# Calendar widget
calendar = Calendar(app, selectmode='day', date_pattern='yyyy-mm-dd')
calendar.pack(pady=20)

# Load existing data and populate file_dict
selected_date_str = calendar.get_date()
selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
file_dict = load_existing_data(selected_date)

# Variable for dropdown selection
file_var = tk.StringVar()
load_available_files()

# Dropdown menu for file selection
file_dropdown = tk.OptionMenu(app, file_var, *available_files)
file_dropdown.pack(pady=10)

# Select file button
select_file_button = tk.Button(app, text="Set für das gewählte Datum festlegen", command=select_file)
select_file_button.pack(pady=10)

# Update button
update_button = tk.Button(app, text="Kalender updaten", command=refresh_data)
update_button.pack(pady=10)

# Label to display current file selection for the selected date
current_selection_label = tk.Label(app, text="Momentan eingetragenes Set für das gewählte Datum: None")
current_selection_label.pack(pady=10)

# Label to display current schedule for the selected date
schedule_label = tk.Label(app, text="Momentane Läutzeiten: None")
schedule_label.pack(pady=10)

# Listbox to display selected files
listbox_label = tk.Label(app, text="Gewählte Sets:")
listbox_label.pack(pady=5)

listbox = tk.Listbox(app, width=80, height=10)
listbox.pack(pady=10)

# Save button
save_button = tk.Button(app, text="Abspeichern", command=save_to_json)
save_button.pack(pady=10)

# Bind calendar date selection to update the current file display
calendar.bind("<<CalendarSelected>>", on_date_change)

# Run the GUI application
app.mainloop()
