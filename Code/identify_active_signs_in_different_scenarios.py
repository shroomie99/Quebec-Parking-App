"""
# Logic
Given user inputs {scenario_date, scenario_time}
For each sign_id {PANNEAU_ID_PAN},
   Determine if sign is currently applicable using {day_of_week,time_of_day,date_period_active,resident_parking}. 
-- If yes:
    - Output: number sign_id, boolean sign_active
-- If no, ignore sign.  

# Add output data into scenarios_sign_active.csv
"""


import pandas as pd
from datetime import datetime, timedelta, time

from pathlib import Path

# Find the project root by navigating up from the current script's directory
project_root = Path(__file__).resolve().parents[1] 


def is_sign_active(scenario_date, scenario_time, resident_parking, day_of_week, time_of_day, date_period_active):
    """
    Determine if a sign is active based on the given scenario date, time, and parking conditions.

    Parameters:
    scenario_date (str): Date in "YYYY-MM-DD" format
    scenario_time (str): Time in "HH:MM" format
    resident_parking (str): "No" or "Yes" indicating if resident parking is allowed
    day_of_week (str): Days of the week the sign is active
    time_of_day (str): Time of day the sign is active
    date_period_active (str): Date range the sign is active

    Returns:
    bool: True if the sign is active, False otherwise
    """

    # Implement logic to determine if a sign is active

    # Type1 (resident parking)
    if resident_parking == "Yes":
        return True
    
    # Type2 (date_period_active)  
    if is_date_in_period(scenario_date, date_period_active):
        return True

    # Type3 (values within both day of week && time of day intervals || within time of day interval & day of week="always" || within day of week interval & time of day="always")
    if check_day_of_week(scenario_date, day_of_week) and check_time_of_day(scenario_time, time_of_day):
        return True

    return False


def is_date_in_period(scenario_date, date_period):
    """
    Check if the scenario_date falls between date1 and date2 given in the format "15 MARS-15 NOVEMBRE".
    Return True if True, False otherwise.

    Parameters:
    scenario_date (str): Date in "YYYY-MM-DD" format
    date_period (str): Period in the format "15 MARS-15 NOVEMBRE"

    Returns:
    bool: True if scenario_date is within the period OR date_period is equal to "always". False otherwise
    """
    # Sign parameter always applies.
    if date_period == "always":
        return True
    

    # Define month mapping from French short-name to English full-name
    month_mapping = {
        "jan": "January", "fev": "February", "mars": "March",
        "avr": "April", "mai": "May", "juin": "June",
        "juil": "July", "aou": "August", "sep": "September",
        "oct": "October", "nov": "November", "dec": "December"
    }

    # Extract and convert date1 and date2
    date1_str, date2_str = date_period.split('-')
    day1, month1 = date1_str.strip().split(' ')
    day2, month2 = date2_str.strip().split(' ')

    month1 = month_mapping[month1.lower()]
    month2 = month_mapping[month2.lower()]

    # Get the year from scenario_date
    year = int(scenario_date[:4])
    
    # Create date1 and date2 in the current year
    date1 = datetime.strptime(f"{day1} {month1} {year}", "%d %B %Y")
    date2 = datetime.strptime(f"{day2} {month2} {year}", "%d %B %Y")
    
    # Parse scenario date
    scenario_datetime = datetime.strptime(scenario_date, "%Y-%m-%d")
    
    # Adjust year for periods spanning the end of the year
    if date1 > date2:
        if scenario_datetime < date1:
            date1 = date1.replace(year=year - 1)
        else:
            date2 = date2.replace(year=year + 1)
    
    # Check if scenario_date is between date1 and date2
    return date1 <= scenario_datetime <= date2



def parse_time(time_str):
    """
    Parse a time string in "HHhMM" or "HHh" format into a datetime.time object.

    Parameters:
    time_str (str): Time string in "HHhMM" or "HHh" format

    Returns:
    datetime.time: The corresponding time object
    """
    time_str = time_str.lower().strip()  # Strip any leading/trailing whitespace
   
    # Handle "24h" as "00h"
    if time_str.startswith("24h"):
        time_str = time_str.replace("24h", "00h")

    if 'h' in time_str:
        try:
            # Try to parse "HHhMM" format
            return datetime.strptime(time_str, "%Hh%M").time()
        except ValueError:
            # If it fails, try to parse "HHh" format
            return datetime.strptime(time_str, "%Hh").time()
    else:
        raise ValueError(f"Invalid time format: {time_str}")


def check_time_of_day(scenario_time, time_of_day):
    """
    Check if the scenario_time falls within any of the time ranges specified in time_of_day.

    Parameters:
    scenario_time (str): Time in "HH:MM" format
    time_of_day (str): Time ranges in the format "07h-09h30, 15h-18h" or "07h-09h30"

    Returns:
    bool: True if scenario_time is within any of the time ranges OR time_of_day is equal to "always". False otherwise.
    """ 
    # Sign parameter always applies.
    if time_of_day == "always":
        return True
    
    # Convert scenario_time to a datetime object
    scenario_time_dt = datetime.strptime(scenario_time, "%H:%M").time()

    # Split the time_of_day into individual time ranges
    time_ranges = time_of_day.split(',')

    for time_range in time_ranges:
        # Strip whitespace and split start and end times
        start_time_str, end_time_str = time_range.strip().split('-')

        # Convert times from "HHhMM" or "HHh" format to datetime objects
        start_time = parse_time(start_time_str)
        end_time = parse_time(end_time_str)

        # Check if scenario_time is within the current time range
        if start_time <= scenario_time_dt <= end_time:
            return True

    return False


def check_day_of_week(scenario_date, day_of_week):
    """
    Check if the scenario_date falls on the specified days or range of days.

    Parameters:
    scenario_date (str): Full date in "YYYY-MM-DD" format.
    day_of_week (str): Days or range of days in the format "mar-mer, jeu, sam-lun".

    Returns:
    bool: True if scenario_date is within any of the specified days, False otherwise.
    """
    # Return True for "always" case
    if day_of_week == "always":
        return True
    
    # Mapping of French day abbreviations to their weekday numbers
    day_mapping = {
        "lun": 0, "mar": 1, "mer": 2, "jeu": 3,
        "ven": 4, "sam": 5, "dim": 6, "sun": 6
    }

    # Convert the scenario_date string ("YYYY-MM-DD") to a datetime object
    scenario_datetime = datetime.strptime(scenario_date, "%Y-%m-%d")

    # Extract the weekday (0=Monday, 6=Sunday) from the datetime object
    scenario_weekday = scenario_datetime.weekday()

    # Split the day_of_week string by commas (indicating multiple day groups)
    day_ranges = day_of_week.split(',')

    # Iterate through each day or range of days
    for day_range in day_ranges:
        # Clean up and check if it's a single day or a range (using '-')
        days = day_range.strip().split('-')

        if len(days) == 1:
            # Single day
            day_start = day_mapping[days[0].strip()]
            day_end = day_start
        else:
            # Range of days
            day_start = day_mapping[days[0].strip()]
            day_end = day_mapping[days[1].strip()]

        # Handle wrapping around the week (e.g., "sam-lun")
        if day_start <= day_end:
            # No wrapping, check if scenario_weekday is in the range
            if day_start <= scenario_weekday <= day_end:
                return True
        else:
            # Wrapping case, check if scenario_weekday is before or after the wrap
            if scenario_weekday >= day_start or scenario_weekday <= day_end:
                return True

    return False
    

# Function to generate results for a single scenario
def generate_single_scenario(combined_datasets, scenario_date, scenario_time):
    # Placeholder for result storage
    results = []
    
    # Loop through all rows in csv, identifying if sign is active
    for _, row in combined_datasets.iterrows():
        PANNEAU_ID_PAN = row['PANNEAU_ID_PAN']
        resident_parking = row['resident_parking']  
        day_of_week = row['day_of_week']  
        time_of_day = row['time_of_day']  
        date_period_active = row['date_period_active']  

        # Determine if the sign is active
        active = is_sign_active(
            scenario_date,
            scenario_time,
            resident_parking,
            day_of_week,
            time_of_day,
            date_period_active
        )
        
        if active:
            results.append({
                "scenario_time": scenario_time,
                "scenario_date": scenario_date,
                "PANNEAU_ID_PAN": PANNEAU_ID_PAN,
            })

    # Convert results to DataFrame and return it
    return pd.DataFrame(results)
 

def generate_multiple_scenarios(combined_datasets):

    # Initialize an empty list for scenarios
    scenarios = []

    ## Generate multiple scenarios then obtain results for each scenario
    # Loop through each month in 2024
    for month in range(1, 13):  # Loop through each month
        for day in range(1, 8):  # Loop through the first 7 days of each month
            for hour in range(0, 24, 2):  # Loop through every 2 hours in a day
                # Create the date with the current month and day
                scenario_date = datetime(2024, month, day).strftime("%Y-%m-%d")
                # Format the time as HH:MM
                scenario_time = f"{hour:02d}:00"
                # Append both the date and time to the scenarios list
                scenarios.append((scenario_date, scenario_time))

                
                # Generate results for each scenario
                df = generate_single_scenario(combined_datasets, scenario_date, scenario_time)
                filename = project_root / "Datasets" / "scenarios" / f"scenarios_sign_active_{scenario_date}_{scenario_time.replace(':', '-')}.csv"
                df.to_csv(filename, index=False)
                print('1')
            print('2')    
        print('month')

    print(scenarios)
    return scenarios


def main():

    # Load sample_user_input
    combined_datasets_csv_path = project_root / "Datasets" / "combined_datasets.csv"

    # Load the data from CSV files into DataFrames
    combined_datasets = pd.read_csv(combined_datasets_csv_path)

    # TEST - SINGLE SCENARIO
    # scenario_date = "2024-01-02"
    # scenario_time = "23:30"
    # results_df = generate_single_scenario(combined_datasets, scenario_date, scenario_time)

    # output_csv_path = r'C:\Users\Benjamin\Desktop\Python Projects\Quebec Parking App\Datasets\scenarios_sign_active.csv'  
    # results_df.to_csv(output_csv_path, index=False)


    # TEST - MULTIPLE SCENARIOS
    # Generate scenarios and their associated csv for : Every 2 hours and every 1 to 8 day of each month
    generate_multiple_scenarios(combined_datasets)

    # Save the results to a CSV file
    print("Updated scenarios_sign_active.csv")

if __name__ == "__main__":
    main()