import schedule
import time
import json
from datetime import datetime
import os
from gpiozero import LED
from time import sleep

# Default template schedules
default_weekday_schedule = ["09:00", "12:00", "15:00"]
default_sunday_schedule = ["10:00", "14:00"]


# Function to get the monthly JSON filename
def get_monthly_filename(year, month):
    return f"calendar_files_{year}_{month:02d}.json"


# Function to ring the alarm
def ring_alarm():
    print("Time to ring the alarm!")
    relay.on()
    sleep(20)
    relay.off()


# Function to read timestamps from the associated file
def read_timestamps(file_path):
    try:
        with open(file_path, 'r') as file:
            today_schedule = json.load(file)

            for timestamp in today_schedule:
                print(timestamp)

            return [timestamp for timestamp in today_schedule]

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

    # Remove only old gong schedules
    schedule.clear('alarms')

    print("Loading today's gong schedule...")

    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    year = today.year
    month = today.month

    json_file = get_monthly_filename(year, month)

    if not os.path.exists(json_file):
        print(f"JSON file {json_file} does not exist. Setting standard schedule")
        timestamps = set_default_schedule(today_str)
    else:    

        with open(json_file, 'r') as file:
            calendar_data = json.load(file)

        # Check if there is a file associated with today's date
        if today_str in calendar_data:

            file_path = calendar_data[today_str]

            if os.path.exists(file_path):
                timestamps = read_timestamps(file_path)
                print("Loaded timestamps:", timestamps)

            else:
                print(f"File {file_path} does not exist. Using default schedule.")
                timestamps = set_default_schedule(today_str)

        else:
            print(f"No file for {today_str}. Using default schedule.")
            timestamps = set_default_schedule(today_str)


    # Schedule alarms for each timestamp
    for alarm_time in timestamps:
        try:
            schedule.every().day.at(alarm_time).do(ring_alarm).tag('alarms')
            print(f"Alarm scheduled for {alarm_time}")

        except Exception as e:
            print(f"Invalid timestamp format: {alarm_time}")
            print(e)



# Function to set default schedule based on weekday
def set_default_schedule(date_str):

    parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = parsed_date.weekday()

    # Sunday
    if weekday == 6:
        return default_sunday_schedule

    # Monday-Friday
    elif weekday <= 5:
        return default_weekday_schedule

    return []



# Main function
def main():

    # Load today's schedule at startup
    setup_schedule()

    # Reload schedule every midnight
    schedule.every().day.at("00:00").do(setup_schedule)

    print("Scheduler is running...")

    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == "__main__":

    relay = LED(17)

    main()
