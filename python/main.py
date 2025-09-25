import requests
import os
from dotenv import load_dotenv
from datetime import datetime as dt
from utils import save_json_to_file, load_json_to_dataframe, mask_api_key_and_email

# Load environment variables from .env file
load_dotenv()

pollutants = {
    "Carbon Monoxide": 42101,
    "Lead PM10": 81102,
    "PM2.5": 88101,
    "Ozone": 44201,
    "Nitrogen Dioxide": 42602,
    "Sulfur Dioxide": 42401,
    "PM10": 81101
}

def get_air_quality_data(pollutant=None, start_date=None, end_date=None, args=None, **kwargs):
    """Retrieve air quality data from the EPA AQS API."""
    base_url = kwargs.get("base_url", "https://aqs.epa.gov/data/api/annualData/byCounty") # Replace with actual API endpoint
    email_address = os.getenv("API_EMAIL")  # Get email from environment variable
    api_key = os.getenv("API_KEY")  # Get API key from environment variable

    if not api_key:
        raise ValueError("API_KEY is not set in the environment variables.")

    params = {
        "email": email_address,
        "key": api_key,
        "param": pollutant,
        "bdate": format_date_to_yyyymmdd(start_date),
        "edate": format_date_to_yyyymmdd(end_date),
        "state": "06", # California
        "county": "001" # Alameda County
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

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

if __name__ == "__main__":

    # Select pollutant(s) to pull data for
    print("Available pollutants:")
    for name, code in pollutants.items():
        print(f"{name}: {code}")

    selected_name = input("Enter pollutant name from the list above: ")
    pollutant = pollutants.get(selected_name)
    if pollutant is None:
        print("Invalid pollutant name. Please choose from the list.")
        exit(1)

    start_date = input("Enter start date (YYYY-MM-DD or MM-DD-YYYY): ")
    end_date = input("Enter end date (YYYY-MM-DD or MM-DD-YYYY): ")

    base_url: str = "https://aqs.epa.gov/data/api/dailyData/byCounty"

    air_quality_data = get_air_quality_data(pollutant, start_date, end_date)

    filename = f"output_{pollutant}_{start_date}_to_{end_date}.json"

    if air_quality_data:
        air_quality_data = mask_api_key_and_email(air_quality_data)
        save_json_to_file(air_quality_data, filename=filename)
        df = load_json_to_dataframe(filename=filename, record_path="Data")
        print("DataFrame:")
        print(df.head())