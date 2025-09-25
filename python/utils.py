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