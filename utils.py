import json
import pandas as pd
import re

def save_json_to_file(data, filename="air_quality_data.json"):
    """Save JSON data to a file."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def load_json_to_dataframe(filename="air_quality_data.json", record_path=None):
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
