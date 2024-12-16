import schedule
import time
#from playsound import playsound

# Function to ring the alarm
def ring_alarm():
    print("Time to ring the alarm!")
    # Replace 'alarm_sound.mp3' with the path to your sound file
    print('alarm_sound.mp3')

# Function to set up a custom schedule with specific days and times
def set_custom_schedule():
    times = []
    days = []
    print("Enter up to 3 times for this schedule in 24-hour format (e.g., 09:00). Type 'done' to finish.")
    for i in range(1, 4):
        user_time = input(f"Enter time {i} (or type 'done' to finish): ")
        if user_time.lower() == 'done':
            break
        try:
            # Validate time format
            time.strptime(user_time, "%H:%M")
            times.append(user_time)
        except ValueError:
            print("Invalid time format. Please enter in HH:MM format.")
            continue
    
    print("Enter the days of the week you want this schedule to apply (e.g., Monday, Tuesday). Type 'done' to finish.")
    while True:
        user_day = input("Enter day (or type 'done' to finish): ").capitalize()
        if user_day.lower() == 'done':
            break
        elif user_day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            days.append(user_day)
        else:
            print("Invalid day. Please enter a valid day of the week (e.g., Monday).")
    
    return times, days

# Function to apply a schedule based on provided times and days
def apply_schedule(times, days):
    for day in days:
        for alarm_time in times:
            # Schedule alarms for the specific days and times
            getattr(schedule.every(), day.lower()).at(alarm_time).do(ring_alarm)
            print(f"Alarm set for {day} at {alarm_time}.")

# Function to choose the schedule and times
def choose_schedule():
    print("Choose your schedule:")
    print("1. Custom Schedule 1")
    print("2. Custom Schedule 2")
    choice = input("Enter 1 or 2: ")
    if choice == '1':
        print("Custom Schedule 1 selected.")
        schedule_one_times, schedule_one_days = set_custom_schedule()
        apply_schedule(schedule_one_times, schedule_one_days)
    elif choice == '2':
        print("Custom Schedule 2 selected.")
        schedule_two_times, schedule_two_days = set_custom_schedule()
        apply_schedule(schedule_two_times, schedule_two_days)
    else:
        print("Invalid choice. Please restart and select a valid option.")
        exit()

# Main function
def main():
    choose_schedule()
    # Main loop to keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
