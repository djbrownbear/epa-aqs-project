import json
import pandas as pd
import re
from datetime import datetime as dt

def save_json_to_file(data, filename="../assets/air_quality_data.json"):
    """Save JSON data to a file."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def load_json_to_dataframe(filename="../assets/air_quality_data.json", record_path=None):
    """Load JSON data from a file into a Pandas DataFrame."""
    with open(filename, "r") as file:
        data = json.load(file)
    return pd.json_normalize(data, record_path=record_path)

def mask_api_key_and_email(data):
    """Mask the API key and email address in the 'url' field of the 'Header' section."""
    if "Header" in data:
        for header in data["Header"]:
            if "url" in header:
                # Mask the API key
                header["url"] = re.sub(r"(key=)[^&]+", r"\1*****", header["url"])
                # Mask the email address
                header["url"] = re.sub(r"(email=)[^&]+", r"\1*****", header["url"])
    return data

def format_date_to_yyyymmdd(date_str):
    """Convert a date string to the format 'YYYYMMDD'.
    Accepts formats like 'YYYY-MM-DD', 'MM-DD-YYYY', 'YYYY/MM/DD', or 'MM/DD/YYYY'.
    """
    try:
        # Replace '/' or '\\' with '-' for uniformity
        normalized_date_str = date_str.replace("/", "-").replace("\\", "-")

        # Try parsing as 'YYYY-MM-DD'
        date_obj = dt.strptime(normalized_date_str, "%Y-%m-%d")
    except ValueError:
        try:
            # Try parsing as 'MM-DD-YYYY'
            date_obj = dt.strptime(normalized_date_str, "%m-%d-%Y")
        except ValueError:
            raise ValueError("Date format must be 'YYYY-MM-DD', 'MM-DD-YYYY', 'YYYY/MM/DD', or 'MM/DD/YYYY'.")

    return date_obj.strftime("%Y%m%d")

def select_one_option(options, prompt="Select an option: "):
    """
    Display a list of options and prompt the user to select one.
    
    Args:
        options (list): List of tuples (display_name, value).
        prompt (str): Prompt message for user input.
    Returns:
        str: The value of the selected option.
    """
    print(prompt)
    for i, (display_name, value) in enumerate(options, start=1):
        print(f"{i}. {display_name}")
    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(options):
                return options[choice - 1][1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def select_multiple_options(options, prompt="Select options (comma-separated numbers): "):
    """
    Display a list of options and prompt the user to select multiple.
    
    Args:
        options (list): List of tuples (display_name, value).
        prompt (str): Prompt message for user input.
    Returns:
        list: List of values of the selected options.
    """
    print(prompt)
    for i, (display_name, value) in enumerate(options, start=1):
        print(f"{i}. {display_name}")
    while True:
        try:
            choices = input("Enter the numbers of your choices (comma-separated): ")
            selected = [options[int(c) - 1][1] for c in choices.split(",") if c.strip().isdigit()]
            if selected:
                return selected
            else:
                print("Invalid choice. Please try again.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter numbers corresponding to the options.")
