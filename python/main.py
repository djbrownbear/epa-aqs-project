import requests
import os
from dotenv import load_dotenv
from datetime import datetime as dt
from utils import save_json_to_file, load_json_to_dataframe, mask_api_key_and_email

# Load environment variables from .env file
load_dotenv()

# pollutants = {
#     "Carbon Monoxide": 42101,
#     "Lead PM10": 81102,
#     "PM2.5": 88101,
#     "Ozone": 44201,
#     "Nitrogen Dioxide": 42602,
#     "Sulfur Dioxide": 42401,
#     "PM10": 81101
# }

# Pollutant options for user selection (single source of truth)
pollutants = [
    ("Lead (TSP) LC", 14129),
    ("Carbon monoxide", 42101),
    ("Sulfur dioxide", 42401),
    ("Nitrogen dioxide (NO2)", 42602),
    ("Ozone", 44201),
    ("PM10 Total 0-10um STP", 81102),
    ("Lead PM10 LC FRM/FEM", 85129),
    ("PM2.5 - Local Conditions", 88101)
]

def get_air_quality_data(
    service="annualData",
    by="byCounty",
    email=None,
    api_key=None,
    param=None,
    state=None,
    county=None,
    bdate=None,
    edate=None,
    **kwargs
):
    """
    Generic function to call the EPA AQS API using the OpenAPI spec.
    """
    # Load credentials from environment if not provided
    email = email or os.getenv("API_EMAIL")
    api_key = api_key or os.getenv("API_KEY")
    if not email or not api_key:
        raise ValueError("API_EMAIL and API_KEY must be set.")

    # Validate required parameters
    if not param or not state or not bdate or not edate:
        raise ValueError("param, state, bdate, and edate are required.")
    if by in ("byCounty", "bySite") and not county:
        raise ValueError("county is required for byCounty or bySite endpoints.")

    # Format FIPS codes
    state = str(state).zfill(2)

    if county is not None:
        county = str(county).zfill(3)

    # Format parameter codes (comma-separated string)
    if isinstance(param, (list, tuple)):
        param = ",".join(str(p).zfill(5) for p in param)
    else:
        param = str(param).zfill(5)

    # Format dates (YYYYMMDD)
    bdate = str(bdate)
    edate = str(edate)

    # Build endpoint
    base_url = "https://aqs.epa.gov/data/api"
    endpoint = f"{base_url}/{service}/{by}"

    # Build query parameters
    params = {
        "email": email,
        "key": api_key,
        "param": param,
        "state": state,
        "bdate": bdate,
        "edate": edate,
    }

    if by in ("byCounty", "bySite"):
        params["county"] = county  # Include county only if required
    params.update(kwargs)  # Add any extra params

    response = requests.get(endpoint, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        print("HTTP error:", e)
        print("Response:", response.text)
        return None

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

    service = input("Enter service (e.g., annualData, dailyData, sampleData): ").strip() or "annualData"
    by = input("Enter 'by' (e.g., byCounty, byState, bySite): ").strip() or "byCounty"
    state = input("Enter state FIPS code (2 digits, e.g., 06): ").zfill(2)

    county = None
    if by in ("byCounty", "bySite"):
        county = input("Enter county FIPS code (3 digits, e.g., 001): ").zfill(3)

    print("Select pollutant(s) by number (comma-separated for multiple):")
    for idx, (name, code) in enumerate(pollutants, 1):
        print(f"  {idx}. {name} ({code})")
    selected = input("Enter your choice(s): ")
    selected_idxs = []
    for s in selected.split(","):
        stripped = s.strip()
        if stripped.isdigit():
            idx = int(stripped)
            if 1 <= idx <= len(pollutants):
                selected_idxs.append(idx)
    if not selected_idxs:
        print("Invalid selection. Exiting.")
        exit(1)
    param = ",".join(str(pollutants[i-1][1]) for i in selected_idxs)

    bdate = input("Enter begin date (YYYYMMDD): ")
    edate = input("Enter end date (YYYYMMDD): ")

    # Build argument dictionary
    aq_args = dict(service=service, by=by, state=state, param=param, bdate=bdate, edate=edate)
    if county is not None:
        aq_args["county"] = county

    air_quality_data = get_air_quality_data(**aq_args)

    filename = f"{service}_{by}_{param}_{bdate}_to_{edate}.json"

    if air_quality_data:
        air_quality_data = mask_api_key_and_email(air_quality_data)
        save_json_to_file(air_quality_data, filename=filename)
        df = load_json_to_dataframe(filename=filename, record_path="Data")
        print("DataFrame:")
        print(df.head())