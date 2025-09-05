import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
API_EMAIL = os.getenv('API_EMAIL', 'test@aqs.api')
API_KEY = os.getenv('API_KEY', 'test')

# Base URL for EPA AQS API
BASE_URL = "https://aqs.epa.gov/data/api"

def normalize_date(date_string):
    """
    Convert date string to YYYYMMDD format.
    Handles formats like YYYY-MM-DD, YYYY/MM/DD, MM-DD-YYYY, etc.
    
    Args:
        date_string (str): Date string in various formats
        
    Returns:
        str: Date string in YYYYMMDD format
        
    Raises:
        ValueError: If date format is invalid or cannot be parsed
    """
    if not date_string:
        raise ValueError("Date string cannot be empty")
    
    # Remove common separators and split into components
    for separator in ['-', '/', '\\']:
        if separator in date_string:
            parts = date_string.split(separator)
            break
    else:
        # No separators found, check if it's already in correct format
        if len(date_string) == 8 and date_string.isdigit():
            return date_string
        else:
            # Assume it's YYYYMMDD without separators
            parts = [date_string[i:i+2] for i in range(0, len(date_string), 2)]
            if len(parts) < 3:
                raise ValueError(f"Invalid date format: {date_string}")
    
    try:
        # Try different arrangements of year, month, day
        if len(parts[0]) == 4:  # Year first (YYYY-MM-DD)
            year, month, day = parts[0], parts[1], parts[2]
        elif len(parts[2]) == 4:  # Year last (MM-DD-YYYY)
            month, day, year = parts[0], parts[1], parts[2]
        else:
            raise ValueError(f"Cannot determine year position in: {date_string}")
        
        # Validate the date
        year_int = int(year)
        month_int = int(month)
        day_int = int(day)
        
        # Pad with zeros if necessary
        year_str = str(year_int).zfill(4)
        month_str = str(month_int).zfill(2)
        day_str = str(day_int).zfill(2)
        
        # Check if valid date
        datetime.strptime(f"{year_str}{month_str}{day_str}", "%Y%m%d")
        
        return f"{year_str}{month_str}{day_str}"
        
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid date format: {date_string}. Please use YYYY-MM-DD, YYYY/MM/DD, or MM-DD-YYYY")

def make_api_request(endpoint, params=None):
    """
    Make a request to the EPA AQS API with error handling.
    
    Args:
        endpoint (str): API endpoint
        params (dict): Query parameters
        
    Returns:
        dict: JSON response from API
        
    Raises:
        requests.exceptions.RequestException: For network-related errors
        ValueError: For API response errors
    """
    url = f"{BASE_URL}/{endpoint}"
    default_params = {
        'email': API_EMAIL,
        'key': API_KEY
    }
    
    if params:
        default_params.update(params)
    
    try:
        response = requests.get(url, params=default_params, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Parse JSON response
        data = response.json()
        
        # Check if API returned an error
        if isinstance(data, dict) and data.get('Header', {}).get('status') == 'Failed':
            error_message = data.get('Header', {}).get('error', 'Unknown API error')
            raise ValueError(f"API Error: {error_message}")
            
        return data
        
    except requests.exceptions.Timeout:
        raise requests.exceptions.RequestException("Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise requests.exceptions.RequestException("Connection error. Please check your internet connection.")
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.RequestException(f"HTTP Error: {e}")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON response from API")
    except Exception as e:
        raise requests.exceptions.RequestException(f"Unexpected error: {e}")

def get_states():
    """Get list of all states."""
    try:
        return make_api_request('list/states')
    except Exception as e:
        print(f"Error fetching states: {e}")
        return None

def get_counties_by_state(state_code):
    """Get list of counties for a specific state."""
    try:
        return make_api_request('list/countiesByState', {'state': state_code})
    except Exception as e:
        print(f"Error fetching counties for state {state_code}: {e}")
        return None

def get_parameters_by_class(parameter_class='CRITERIA'):
    """Get list of parameters by class."""
    try:
        return make_api_request('list/parametersByClass', {'pc': parameter_class})
    except Exception as e:
        print(f"Error fetching parameters: {e}")
        return None

def get_air_quality_data(pollutant_param, bdate, edate, state, county=None):
    """
    Retrieve air quality data for a specific pollutant, date range, and location.
    
    Args:
        pollutant_param (str): Parameter code for the pollutant
        bdate (str): Start date in YYYYMMDD format
        edate (str): End date in YYYYMMDD format
        state (str): State code
        county (str, optional): County code
        
    Returns:
        dict: Air quality data
    """
    try:
        # Normalize dates
        normalized_bdate = normalize_date(bdate)
        normalized_edate = normalize_date(edate)
        
        if county:
            # Data by county
            endpoint = 'annualData/byCounty'
            params = {
                'param': pollutant_param,
                'bdate': normalized_bdate,
                'edate': normalized_edate,
                'state': state,
                'county': county
            }
        else:
            # Data by state
            endpoint = 'annualData/byState'
            params = {
                'param': pollutant_param,
                'bdate': normalized_bdate,
                'edate': normalized_edate,
                'state': state
            }
        
        return make_api_request(endpoint, params)
        
    except Exception as e:
        print(f"Error fetching air quality data: {e}")
        return None

def find_parameter_code(parameter_name, parameters_data):
    """
    Find parameter code for a given parameter name.
    
    Args:
        parameter_name (str): Name of the parameter to search for
        parameters_data (dict): Parameters data from API
        
    Returns:
        str: Parameter code if found, None otherwise
    """
    if not parameters_data or 'Data' not in parameters_data:
        return None
    
    for item in parameters_data['Data']:
        if parameter_name.lower() in item.get('parameter_desc', '').lower():
            return item.get('parameter_code')
        if parameter_name.lower() in item.get('parameter_name', '').lower():
            return item.get('parameter_code')
    
    return None

def display_available_pollutants(parameters_data):
    """Display available pollutants."""
    if not parameters_data or 'Data' not in parameters_data:
        print("No parameter data available")
        return
    
    print("\nAvailable Pollutants:")
    print("-" * 50)
    for i, item in enumerate(parameters_data['Data'][:20], 1):  # Show first 20
        print(f"{i:2d}. {item.get('parameter_desc', 'N/A')} "
              f"(Code: {item.get('parameter_code', 'N/A')})")
    
    if len(parameters_data['Data']) > 20:
        print(f"... and {len(parameters_data['Data']) - 20} more")

def main():
    """Main function to run the EPA AQS API client."""
    print("EPA AQS API Client")
    print("=" * 50)
    
    # Get available parameters
    print("Fetching available pollutants...")
    parameters_data = get_parameters_by_class()
    
    if not parameters_data:
        print("Could not fetch parameter list. Exiting.")
        return
    
    # Display some available options
    display_available_pollutants(parameters_data)
    
    # Get user input
    try:
        # Get pollutant
        pollutant_input = input("\nEnter pollutant name or code (e.g., 'PM2.5' or '88101'): ").strip()
        
        # Try to find parameter code
        if pollutant_input.isdigit():
            pollutant_code = pollutant_input
        else:
            pollutant_code = find_parameter_code(pollutant_input, parameters_data)
            if not pollutant_code:
                print(f"Pollutant '{pollutant_input}' not found.")
                print("Using default PM2.5 (code 88101)")
                pollutant_code = '88101'
            else:
                print(f"Found parameter code: {pollutant_code}")
        
        # Get date range
        bdate_input = input("Enter start date (YYYY-MM-DD, YYYY/MM/DD, or MM-DD-YYYY): ").strip()
        edate_input = input("Enter end date (YYYY-MM-DD, YYYY/MM/DD, or MM-DD-YYYY): ").strip()
        
        # Get location
        print("\nFetching states...")
        states_data = get_states()
        
        if states_data and 'Data' in states_data:
            print("\nAvailable States (first 10):")
            print("-" * 30)
            for i, state in enumerate(states_data['Data'][:10], 1):
                print(f"{state.get('state_code')}: {state.get('state_name')}")
            if len(states_data['Data']) > 10:
                print("... and more states available")
        
        state_code = input("\nEnter state code: ").strip()
        
        # Optional county
        county_code = input("Enter county code (optional, press Enter to skip): ").strip()
        if not county_code:
            county_code = None
            
        # Fetch data
        print(f"\nFetching air quality data for parameter {pollutant_code}...")
        data = get_air_quality_data(
            pollutant_param=pollutant_code,
            bdate=bdate_input,
            edate=edate_input,
            state=state_code,
            county=county_code
        )
        
        # Process and display results
        if data and 'Data' in data:
            print(f"\nSuccessfully retrieved {len(data['Data'])} records:")
            print("-" * 50)
            
            # Display header information
            header = data.get('Header', {})
            print(f"Status: {header.get('status', 'N/A')}")
            print(f"Number of Records: {len(data['Data'])}")
            print()
            
            # Display sample data
            for i, record in enumerate(data['Data'][:5]):  # Show first 5 records
                print(f"Record {i+1}:")
                print(f"  Site: {record.get('site_number', 'N/A')}")
                print(f"  Date: {record.get('year', 'N/A')}")
                print(f"  Value: {record.get(' arithmetic_mean', record.get('value', 'N/A'))}")
                print(f"  Units: {record.get('units_of_measure', 'N/A')}")
                print(f"  County: {record.get('county_name', 'N/A')}")
                print()
                
            if len(data['Data']) > 5:
                print(f"... and {len(data['Data']) - 5} more records")
                
            # Option to save data
            save_option = input("Save data to file? (y/n): ").strip().lower()
            if save_option == 'y':
                filename = f"aqs_data_{pollutant_code}_{bdate_input.replace('/', '-')}_{edate_input.replace('/', '-')}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"Data saved to {filename}")
        else:
            print("No data found or error occurred.")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()