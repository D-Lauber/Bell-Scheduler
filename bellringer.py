import schedule
import time
import json
from datetime import datetime
import os

# Function to get the monthly JSON filename
def get_monthly_filename(year, month):
    return f"calendar_files_{year}_{month:02d}.json"

# Function to ring the alarm
def ring_alarm():
    print("Time to ring the alarm!")
    # Uncomment and replace 'alarm_sound.mp3' with the path to your sound file
    # playsound('alarm_sound.mp3')

# Function to read timestamps from the associated file
def read_timestamps(file_path):
    try:
        with open(file_path, 'r') as file:
            # Reading timestamps from the file and stripping quotes or spaces
            timestamps = [time.strip().strip('"').strip("'") for time in file.readlines()]
            return [time for time in timestamps if is_valid_time(time)]
    except Exception as e:
        print(f"Error reading timestamps from {file_path}: {e}")
        return []

# Function to validate time format
def is_valid_time(time_string):
    try:
        time.strptime(time_string, "%H:%M")
        return True
    except ValueError:
        return False

# Function to set up the schedule for the current day
def setup_schedule():
    # Get today's date and the current year and month
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    year = today.year
    month = today.month

    # Load the monthly JSON file with the file paths for each day
    json_file = get_monthly_filename(year, month)
    
    if not os.path.exists(json_file):
        print(f"JSON file {json_file} does not exist.")
        return
    
    with open(json_file, 'r') as file:
        calendar_data = json.load(file)

    # Check if there is a file associated with today's date
    if today_str in calendar_data:
        file_path = calendar_data[today_str]
        if os.path.exists(file_path):
            # Read timestamps from the associated file
            timestamps = read_timestamps(file_path)
            
            # Schedule alarms for each timestamp
            for alarm_time in timestamps:
                try:
                    schedule.every().day.at(alarm_time).do(ring_alarm)
                    print(f"Alarm scheduled for {alarm_time}")
                except Exception as e:
                    print(f"Invalid timestamp format in file {file_path}: {alarm_time}")
        else:
            print(f"File {file_path} for today's date does not exist.")
    else:
        print(f"No file associated with today's date: {today_str}")

# Main function to run the schedule
def main():
    setup_schedule()
    print("Scheduler is running...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
