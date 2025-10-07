import requests
import os
from dotenv import load_dotenv
from datetime import datetime as dt
from utils import save_json_to_file, load_json_to_dataframe, mask_api_key_and_email, select_one_option, select_multiple_options

# Load environment variables from .env file
load_dotenv()

services_list = [
  ("Monitors", "monitors"),
  ("Sample Data", "sampleData"),
  ("Daily Summary Data", "dailyData"),
  ("Annual Summary Data", "annualData"),
  ("Quarterly Summary Data", "quarterlyData"),
  ("Quality Assurance - Blanks Data", "qaBlanks"),
  ("Quality Assurance - Collocated Assessments", "qaCollocatedAssessments"),
  ("Quality Assurance - Flow Rate Verifications", "qaFlowRateVerifications"),
  ("Quality Assurance - Flow Rate Audits", "qaFlowRateAudits"),
  ("Quality Assurance - One Point Quality Control Raw Data", "qa_one_point_qc"),
  ("Quality Assurance - PEP Audits", "qaPepAudits"),
  ("Transaction Sample - AQS Submission data in transaction Format (RD)", "transactionsSample"),
  ("Quality Assurance - Annual Performance Evaluations", "qaAnnualPerformanceEvaluations"),
  ("Quality Assurance - Annual Performance Evaluations in the AQS Submission transaction format (RD)", "qaAnnualPerformanceEvaluationsTransaction"),
  ("List of valid values for data entry elsewhere", "list")
]

aggregation_list = [
    ("by site", "bySite"),
    ("by county", "byCounty"),
    ("by state", "byState"),
    ("by box", "byBox"),
    ("by monitoring agency", "byMA"),
    ("by quality assurance organization", "byPQAO"),
    ("by core statistical area", "byCBSA")
]

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

def main():
    service = select_one_option(services_list, prompt="Select a service:")
    aggregation = select_one_option(aggregation_list, prompt="Select an aggregation method:")
    state = input("Enter state FIPS code (2 digits, e.g., 06): ").zfill(2)

    county = None
    if aggregation in ("byCounty", "bySite"):
        county = input("Enter county FIPS code (3 digits, e.g., 001): ").zfill(3)

    param = ",".join(str(p) for p in select_multiple_options(pollutants, prompt="Select pollutant(s):"))

    bdate = input("Enter begin date (YYYYMMDD): ")
    edate = input("Enter end date (YYYYMMDD): ")

    # Build argument dictionary
    aq_args = dict(service=service, by=aggregation, state=state, param=param, bdate=bdate, edate=edate)
    if county is not None:
        aq_args["county"] = county

    print("Fetching data with parameters:")
    for k, v in aq_args.items():
        print(f"  {k}: {v}")
    air_quality_data = get_air_quality_data(**aq_args)

    filename = f"{service}_{aggregation}_{param}_{bdate}_to_{edate}.json"

    if air_quality_data:
        air_quality_data = mask_api_key_and_email(air_quality_data)
        save_json_to_file(air_quality_data, filename=filename)
        df = load_json_to_dataframe(filename=filename, record_path="Data")
        print("DataFrame:")
        print(df.head())
    else:
        print("No data retrieved.")

if __name__ == "__main__":
    main()