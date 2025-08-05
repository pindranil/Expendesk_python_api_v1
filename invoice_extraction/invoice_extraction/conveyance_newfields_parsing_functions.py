
## Libraries required
import warnings
warnings.filterwarnings("ignore")

import re

from datetime import datetime, timedelta
from invoice_extraction.configuration import *



## Required functions for conveyance bill's new fields extraction
##_________________________________________________________________________________________________________


# Compare if two dates are same or not
def compare_dates(date_str1, date_str2):
    date1 = ''
    date2 = ''
    try:
        # Attempt to parse the date strings as 'YYYY-MM-DD'
        date1 = datetime.strptime(date_str1, '%d-%m-%Y')
        date2 = datetime.strptime(date_str2, '%d-%m-%Y')
    except ValueError:
        # If parsing as 'YYYY-MM-DD' fails, try 'YYYY-MMM-DD'
        try:
            for full_month, abbreviation in month_abbreviations.items():
                date_str1 = date_str1.replace(full_month, abbreviation)
                date_str2 = date_str2.replace(full_month, abbreviation)
            # Parse the date strings into datetime objects
            date1 = datetime.strptime(date_str1, '%d-%b-%Y')
            date2 = datetime.strptime(date_str2, '%d-%b-%Y')
        except ValueError:
            return "Invalid date format"

    # Compare the dates
    if date1 > date2:
        return ("After")
    elif date1 < date2:
        return ("Before")
    else:
        return ("Same")



# Replace AM and PM string from time string
def replace_am_pm(input_string):
    try:
        # Check if the string contains "AM" or "PM"
        if "AM" in input_string or "PM" in input_string:
            # Remove "AM" and "PM" from the string
            input_string = input_string.replace("AM", "").replace("PM", "")
    except:
        pass
        
    return(input_string)



# Calculate total number of journey dates
def calculate_no_of_days(departure_date_str,arrival_date_str):
    days_difference=0
    try:
        date1 = datetime.strptime(departure_date_str, '%d-%m-%Y')
        date2 = datetime.strptime(arrival_date_str, '%d-%m-%Y')
        
    except:
        date1 = datetime.strptime(departure_date_str, '%d-%b-%Y')
        date2 = datetime.strptime(arrival_date_str, '%d-%b-%Y')

    try:
        date_difference = date2 - date1
        days_difference = date_difference.days
    except:
        pass
    
    return(days_difference)



# Calculate total number of journey hours
def calculate_no_of_hours(departure_time_str,arrival_time_str):
    hours = 0
    minutes=0

    try:
        # Convert time strings to datetime objects, assuming a fixed date (e.g., today's date)
        current_date = datetime.now().date()  # Use today's date
        departure_datetime = datetime.combine(current_date, datetime.strptime(departure_time_str, "%H:%M").time())
        arrival_datetime = datetime.combine(current_date, datetime.strptime(arrival_time_str, "%H:%M").time())

        # Calculate the journey time as a positive duration
        if arrival_datetime < departure_datetime:
            # If arrival is on the next day, add a day to the arrival datetime
            arrival_datetime += timedelta(days=1)

        journey_time = arrival_datetime - departure_datetime

        # Extract hours, minutes, and seconds
        hours, remainder = divmod(journey_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
    except:
        pass
    
    return (hours, minutes)



# Extract only time string from departure and arrival time string
# Example : 22 - Jun - 2022 00:05 -> 00:05

def extract_times(input_string):
    # Regular expression pattern to match time in the format "HH : MM" or "HH : MM : SS"
    time_pattern = r'(\d{2}:\d{2}(:\d{2})?)'

    # Search for the pattern in the input string
    matches = re.findall(time_pattern, input_string)

    # Extract all matched time values
    if matches:
        extracted_times = [match[0] for match in matches]
        return extracted_times[0]
    


## Final Function
def get_calculated_journey_time(list_item):
    departure_time_str = "Not Found"
    arrival_time_str = "Not Found"
    departure_date_str = "Not Found"
    arrival_date_str = "Not Found"

    #print("list item for jn time calc ****")
    #print(list_item)

    # try:
    departure_date_str = list_item['Departure Date']
    departure_time_str = list_item['Departure Time']
    arrival_date_str = list_item['Arrival Date']
    arrival_time_str = list_item['Arrival Time']

    # except:
    #     pass

    # for item in list_item:
    #     for line in item.split('\n'):
    #         if ':' in line:
    #             key, value = line.split(': ', 1)
    #             if key == "Departure Time":
    #                 departure_time_str = value
    #             if key == "Arrival Time":
    #                 arrival_time_str = value
    #             if key == "Departure Date":
    #                 departure_date_str = value
    #             if key == "Arrival Date":
    #                 arrival_date_str = value

    if departure_time_str == "Not Found" or arrival_time_str == "Not Found":
        print("Departure dt and tm not found!")
        calculated_journey_time = "Not Found"
    else:
        departure_time_str = replace_am_pm(departure_time_str)
        arrival_time_str = replace_am_pm(arrival_time_str)
        departure_time_str = departure_time_str.replace(" ", "")
        arrival_time_str = arrival_time_str.replace(" ", "")
        departure_time_str = extract_times(departure_time_str)
        arrival_time_str = extract_times(arrival_time_str)
        departure_time_str = departure_time_str[:5]
        arrival_time_str = arrival_time_str[:5]

        calculated_journey_time = calculate_no_of_hours(departure_time_str, arrival_time_str)
        #print(calculated_journey_time)
        hours = calculated_journey_time[0]
        #print(hours)
        minutes = calculated_journey_time[-1]
        #print(minutes)
        
        if departure_date_str and arrival_date_str:
            departure_date_str = departure_date_str.replace(" ", "")
            arrival_date_str = arrival_date_str.replace(" ", "")
            departure_date_str= departure_date_str.upper()
            arrival_date_str = arrival_date_str.upper()
            date = compare_dates(departure_date_str, arrival_date_str)
            #print(date)
            
            if date == "Before":
                calculated_journey_days = calculate_no_of_days(departure_date_str, arrival_date_str)
                #print(calculated_journey_days)
                
                hours = hours + (24 * calculated_journey_days)
                #print(calculated_journey_time)
                
                calculated_journey_time = (f"{hours} hours {minutes} minutes")
                
            elif date == "Same":
                calculated_journey_time = (f"{hours} hours {minutes} minutes")

            else:
                calculated_journey_time = "Not Found"

    return(calculated_journey_time)
