"""
Script cleans then extracts data from DESCRIPTION_RPA column. 
Then adds extracted data to columns: rule_type, day_of_week, time_of_day, date_period_active, resident_parking, special_conditions.

TODO:
 FIX in function find_time_of_day(description). 
 When time interval(s) is before date(s) a second time. Identify which time interval refers to which dates. 
 (Note: time interval can refers to many dates)
 DESIGN: How should output look for this case?
"""

import pandas as pd
import re
import unicodedata

from pathlib import Path

# Find the project root by navigating up from the current script's directory
project_root = Path(__file__).resolve().parents[1]  # Assumes 'Code' folder is one level deep within project

# Construct the path to the target file
          
# Load the GeoJSON file

## HELPER properties or functions ##

# Combine lists of French month and day abbreviations
exclude_list_for_special_conditions = [
    "JAN", "FEV", "MAR", "AVR", "MAI", "JUIN", 
    "JUIL", "AOU", "SEP", "OCT", "NOV", "DEC",
    "LUN", "MAR", "MER", "JEU", "VEN", "SAM", "DIM", "MIN"
]

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def extract_weekdays_and_words(text):
    "Extract the weekday and words between the weekdays."

    # Define a pattern to match weekdays and the words in between
    pattern = r'(?i)(LUN|MAR|MER|JEU|VEN|SAM|DIM)(.*?)(?=(LUN|MAR|MER|JEU|VEN|SAM|DIM)|$)'
    
    matches = re.findall(pattern, text, flags=re.DOTALL)
    
    # If no weekdays found, return an empty list
    if not matches:
        return []
    
    # If only one weekday is found, return just that weekday
    if len(matches) == 1:
        return [matches[0][0]]
    
    # Combine the matches for multiple weekdays, ensuring the first and last elements are weekdays
    result = []
    for i, match in enumerate(matches):
        result.append(match[0])  # Append the weekday
        if i < len(matches) - 1:  # If it's not the last match, append the words in between
            words = match[1].strip()
            if words:
                result.append(words)
    
    return result

def extract_weekdays(text_list):
    # Define a pattern to match weekdays
    pattern = r'(?i)\b(LUN|MAR|MER|JEU|VEN|SAM|DIM)\b'
    
    # Initialize an empty list to store the weekdays
    weekdays = []
    
    # Iterate through each element in the list of strings
    for text in text_list:
        # Find all matching weekdays in the current string
        matches = re.findall(pattern, text)
        # Extend the weekdays list with found matches
        weekdays.extend(matches)
    
    return weekdays

def identify_seperator_for_weekdays(schedule_list):
    "Given list of elements containing weekdays and words between. Return string of weekdays with proper seperator."

    day_pattern = re.compile(r'(?i)\b(LUN|MAR|MER|JEU|VEN|SAM|DIM)\b')
    time_pattern = re.compile(r'\b\d{1,2}[Hh](\d{2})? (a|au) \d{1,2}[Hh](\d{2})?\b', re.IGNORECASE)
    result = []
    i = 0

    # First iteration for date range
    while i < len(schedule_list):
        if i > 0 and i < len(schedule_list) - 1:
            prev_day = schedule_list[i-1].lower() if day_pattern.match(schedule_list[i-1]) else None
            next_day = schedule_list[i+1].lower() if day_pattern.match(schedule_list[i+1]) else None
            middle_content = schedule_list[i].lower()
            
            if prev_day and next_day:
                if ('a' in middle_content or 'au' in middle_content) and not time_pattern.search(middle_content) and not day_pattern.match(middle_content):
                    result.append(f"{schedule_list[i-1]}-{schedule_list[i+1]}")
                    i += 2  # Skip next element since it's already paired
        i += 1

    # Second iteration for remaining weekdays not added from list
    
    # Collect all weekdays in the original list
    all_weekdays = [day for day in schedule_list if day_pattern.match(day)]

    # Check if any weekdays are missing in the result
    for day in all_weekdays:
        if day not in ','.join(result) and day not in '-'.join(result):
            result.append(day)

    return ', '.join(result)


def add_prefix_to_months(text):
    # Define French months without accents, including their full names
    months_fr = [
        "jan", "janv", "janvier", "fev", "fevr", "fevrier", "mars", "avr", "avri", "avril", 
        "mai", "juin", "juil", "juillet", "aou", "aout", "sep", "sept", "septembre", 
        "oct", "octobre", "nov", "novembre", "dec", "decembre"
    ]

    # Create a regex pattern to match months not preceded by a number
    month_pattern = r'\b(?:' + '|'.join(months_fr) + r')\b'

    # Find all occurrences of months in the text
    matches = re.findall(month_pattern, text, flags=re.IGNORECASE)
    
    # If there are two different months, proceed
    if len(matches) >= 2:
        # Replace months not preceded by a number with "1 <month>"
        def replacer(match):
            # Check if the match is preceded by a number
            prefix_check = re.search(r'\d+\s*$', text[:match.start()])
            if not prefix_check:
                return "1 " + match.group(0)
            return match.group(0)
        
        # Substituting with correct prefixes
        text = re.sub(r'(?<!\d\s)\b(?:' + '|'.join(months_fr) + r')\b', replacer, text, flags=re.IGNORECASE)

    return text

def extract_date_period(text_with_prefix):
    # Define a regex pattern to match the date period with varying month lengths
    month_pattern = r'(?:jan(?:v(?:ier)?)?|fev(?:r(?:ier)?)?|mars|avr(?:il)?|mai|juin|juil(?:let)?|aou(?:t)?|sep(?:t(?:embre)?)?|oct(?:obre)?|nov(?:embre)?|dec(?:embre)?)'
    date_period_pattern = r'\d{1,2}\s*' + month_pattern + r'\s*[Aa][Uu]?\s*\d{1,2}\s*' + month_pattern
    
    # Extract the date period
    match = re.search(date_period_pattern, text_with_prefix, flags=re.IGNORECASE)
    
    # Return the matched date period if found, otherwise return None
    return match.group(0) if match else None


def normalize_month(month):
    # Dictionary mapping full French month names to their short forms
    month_mapping = {
        'janvier': 'jan', 'fevrier': 'fev', 'mars': 'mars', 'avril': 'avr',
        'mai': 'mai', 'juin': 'juin', 'juillet': 'juil', 'aout': 'aou',
        'septembre': 'sep', 'octobre': 'oct', 'novembre': 'nov', 'decembre': 'dec',
        'janv': 'jan', 'fevr': 'fev', 'avri': 'avr', 'juillet': 'juil',
        'sept': 'sep', 'dec': 'dec', 'oct': 'oct', 'nov': 'nov'
    }
    # Return the short form of the month, or the month itself if it's already short
    return month_mapping.get(month.lower(), month)

def extract_and_normalize_date_period(extracted_date_period):
    # Define a regex pattern to extract the day and month components
    pattern = r'(\d{1,2})\s*(jan(?:v(?:ier)?)?|fev(?:r(?:ier)?)?|mars|avr(?:il)?|mai|juin|juil(?:let)?|aou(?:t)?|sep(?:t(?:embre)?)?|oct(?:obre)?|nov(?:embre)?|dec(?:embre)?)'
    
    # Find all matches
    matches = re.findall(pattern, extracted_date_period, flags=re.IGNORECASE)
    
    # Normalize the months and prepare the final output
    if matches and len(matches) == 2:
        day1, month1 = matches[0]
        day2, month2 = matches[1]
        normalized_month1 = normalize_month(month1).lower()
        normalized_month2 = normalize_month(month2).lower()
        return f"{day1} {normalized_month1}-{day2} {normalized_month2}"
    
    return None  # or handle the case where the expected pattern isn't found


### ACTION FUNCTIONS ### ####################################################
def find_rule_type(description):
    "Given a row from DESCRIPTION_RPA. Return the parking type"

    # Check for each condition and classify accordingly
    if any(keyword in description for keyword in ["NO PARKING", "/P", "\\P", "\\A", "/A"]):
        return "No Parking"
    elif "P " in description:
        return "Parking Allowed"
    elif "PANONCEAU" in description:
        return "Impact sign directly above"
    else:
        return "Unknown"

def find_resident_parking(text):
    "Given a row from DESCRIPTION_RPA. Return whether sign relates to resident parking"

    if any(keyword in text for keyword in ["RESIDENTS ONLY", "S3R"]):
        find_resident_parking = "Yes"
    else:
        find_resident_parking = "No"
    return find_resident_parking

def find_day_of_week(description):
    "Given a row from DESCRIPTION_RPA. Return day(s) of the week sign applies. Identifying dashes as ranges and commas as individual days."

    found_days = []
    description_lower = description.lower()

    # Eliminate "MARS" month, due to it interfering with regrex
    if "mars" in description_lower:
        description_lower = description_lower.replace("mars", "")
        
    # Extract list of weekdays and words between them
    weekdays_and_words = extract_weekdays_and_words(description_lower)

    # Determine seperator to use (, or -), based on words between the weekdays.    
    found_days = identify_seperator_for_weekdays(weekdays_and_words)
   
    if found_days:
        return found_days
    else:
        return 'always'

def find_time_of_day(description):
    "Given a row from DESCRIPTION_RPA. Return when signs applies."

    # Define a regex pattern for the refined time format, allowing spaces around the separator
    time_pattern = r'\b\d{1,2}[hH]\d{0,2}\s*-\s*\d{1,2}[hH]\d{0,2}\b'

    # Standardize the description by replacing known separators with a hyphen
    standardized_description = re.sub(r'\s*(à|À|A|@)\s*', '-', description, flags=re.IGNORECASE)

    # Find all matches of the time pattern in the description
    matches = re.findall(time_pattern, standardized_description)


    #TODO: 
    # FIX when time interval(s) is before date(s) a second time. Identify which time interval refers to which dates. 
    # (Note: time interval can refers to many dates)
    # DESIGN: How should output look for this case?
  
    # if matched pattern
    if matches:
        # Join the extracted time intervals with a comma and remove spaces around hyphens
        intervals = [match.replace(' - ', '-') for match in matches]
        return ', '.join(intervals)
    
    else:
        # if no pattern match found
        return "always"

# Function to standardize, extract, convert and output the date period with French months
def find_date_period_active(text):
    "Given a row from DESCRIPTION_RPA. Return month range sign applies."

    # Clean data
    text = text.replace('.', '').replace('-', 'au').replace('er', '').replace('ER', '')
    text = text.replace('et', 'au').replace('ET', 'au').replace('À', 'au')
    
    # If month does not contain number before. Add a "1 " before it.
    text_with_prefix = add_prefix_to_months(text)

    # Given text_with_prefix, extract the data period from it. Format: "1 mai au 15 sep"
    extracted_date_period = extract_date_period(text_with_prefix)

    # Convert extract data (date_period) into an standardized output. 
    if extracted_date_period:
        result = extract_and_normalize_date_period(extracted_date_period)
        return result
    
    else:
        # set and return cell value as "always"
        return "always"

# Function to extract special conditions
def find_special_conditions(description):
    "Given a row from DESCRIPTION_RPA. Return the unclassified elements that is included in DESCRIPTION_RPA."

    description_no_accents = remove_accents(description)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', description_no_accents, re.IGNORECASE)  # Extract words
    special_conditions = []
    for word in words:
        if not any(exclude_word.lower() in word.lower() for exclude_word in exclude_list_for_special_conditions):
            special_conditions.append(word.upper())
    return ' '.join(special_conditions)


### MAIN ###
# Load the dataset
file_path = project_root / "Datasets" / "simplified_signalisation_stationnement.csv"  
# file_path = r'C:\Users\Benjamin\Desktop\Python Projects\Quebec Parking App\Datasets\signalisation-codification-rpa.csv' # for testing purposes
df = pd.read_csv(file_path, encoding='utf-8')

# Clean data. By replacing improper data with what it should be
df['DESCRIPTION_RPA'] = df['DESCRIPTION_RPA'].str.replace('MARSL', 'MARS', regex=False)
df['DESCRIPTION_RPA'] = df['DESCRIPTION_RPA'].str.replace('AVIL', 'AVRIL', regex=False)
df['DESCRIPTION_RPA'] = df['DESCRIPTION_RPA'].str.replace('AVRILS', 'AVRIL', regex=False)
df['DESCRIPTION_RPA'] = df['DESCRIPTION_RPA'].str.replace('MARS.', 'MARS', regex=False)
df['DESCRIPTION_RPA'] = df['DESCRIPTION_RPA'].str.replace('Ã€', 'AU', regex=False)
df['DESCRIPTION_RPA'] = df['DESCRIPTION_RPA'].str.replace('.', '', regex=False)
df['DESCRIPTION_RPA'] = df['DESCRIPTION_RPA'].str.replace('À', 'AU', regex=False)
df['DESCRIPTION_RPA'] = df['DESCRIPTION_RPA'].str.replace('É', 'E', regex=False)
df['DESCRIPTION_RPA'] = df['DESCRIPTION_RPA'].str.replace('é', 'e', regex=False)
df['DESCRIPTION_RPA'] = df['DESCRIPTION_RPA'].str.replace('à', 'A', regex=False)
df['DESCRIPTION_RPA'] = df['DESCRIPTION_RPA'].str.replace('1er', '1', regex=False)

# Extract various data from DESCRIPTION_RPA and add it to a new columns
df['rule_type'] = df['DESCRIPTION_RPA'].apply(find_rule_type)
df['day_of_week'] = df['DESCRIPTION_RPA'].apply(lambda x: find_day_of_week(str(x)))
df['time_of_day'] = df['DESCRIPTION_RPA'].apply(lambda x: find_time_of_day(str(x)))
df['date_period_active'] = df['DESCRIPTION_RPA'].apply(find_date_period_active)
df['resident_parking'] = df['DESCRIPTION_RPA'].apply(find_resident_parking)
df['special_conditions'] = df['DESCRIPTION_RPA'].apply(find_special_conditions)

# Save the updated dataframe to a new CSV file
updated_file_path = project_root / "Datasets" / "simplified_signalisation_stationnement.csv"  
# updated_file_path = r'C:\Users\Benjamin\Desktop\Python Projects\Quebec Parking App\Datasets\signalisation-codification-rpa.csv' # for testing purposes
df.to_csv(updated_file_path, index=False)


print(f"Sign rules has been updated in csv")
