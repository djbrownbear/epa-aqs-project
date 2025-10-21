import json
import pandas as pd
import re
from datetime import datetime as dt
from difflib import SequenceMatcher
from constants import CONNECTION_TYPE, MAX_INPUT_LENGTH, BLOCKED_PATTERNS

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

def get_code_header_title(selected_language):
    return f'Here is the code to create the graph using {selected_language}:'

def get_param_options(param=None, add_all=True, dataframe=None):
    if dataframe is None:
        return []
    param_options = [{'label': str(p), 'value': p} for p in sorted(dataframe[str(param)].unique())]
    if add_all:
        param_options.insert(0, {'label': 'All', 'value': 'all'})
    return param_options

def get_fig_from_code(code, cleaned_df, px, go, pd):
    local_vars = {}
    exec(code, {"cleaned_df": cleaned_df, "px": px, "go": go, "pd": pd}, local_vars)
    return local_vars.get('fig', None)

def filter_df(df=None, pollutant=None, counties=None):
    if df is None:
        raise ValueError("DataFrame 'df' must be provided.")

    filtered = df
    if pollutant:
        filtered = filtered[filtered['parameter'] == pollutant]
    if counties and counties[0] != 'all':
        filtered = filtered[filtered['county'].isin(counties)]
    return filtered

def secure_user_input(user_input, system_prompt):
    if len(user_input) > MAX_INPUT_LENGTH:
        return False, "Input too long. Please shorten your request."
    if any(pat in user_input.lower() for pat in BLOCKED_PATTERNS):
        return False, "Input contains blocked phrases. Please rephrase."
    if is_similar(user_input, system_prompt):
        return False, "Input too similar to system prompt. Please rephrase."
    # Optionally sanitize
    sanitized = re.sub(r"```|system:|assistant:|user:", "", user_input, flags=re.IGNORECASE)
    return True, sanitized

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > threshold

def initialize_db_data(engine, inspect, table_name, data_path, connection_type):
    """
    Initialize the database with data from a CSV file if the table doesn't exist.
    """
    # If the table doesn't exist, upload the CSV
    if connection_type in ["mysql", "sqlite", "cloud_sql"]:
        with engine.begin() as conn:
            if not inspect(conn).has_table(table_name):
                csv_df = pd.read_csv(data_path)
                csv_df.to_sql(table_name, conn, index=False, if_exists="replace", chunksize=1000)
                print(f"Uploaded data to table '{table_name}'.")

def load_air_quality_df(connection_type, engine=None, table_name=None, download=None, cleaned_download=None):
    """
    Load the air quality dataframe based on the connection type.
    Supports: 'github_raw', 'mysql', 'sqlite', 'cloud_sql'.
    Returns: (df, cleaned_df)
    """
    import pandas as pd

    if connection_type == "github_raw":
        if download is None or cleaned_download is None:
            raise ValueError("Download bytes required for github_raw connection.")
        df = pd.read_csv(pd.compat.StringIO(download.decode('utf-8')), index_col=0)
        cleaned_df = pd.read_csv(pd.compat.StringIO(cleaned_download.decode('utf-8')))
    elif connection_type in ["mysql", "sqlite", "cloud_sql"]:
        if engine is None or table_name is None:
            raise ValueError("Engine and table_name required for SQL connections.")
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        cleaned_df = None  # You may want to add logic for cleaned_df if needed
    else:
        raise ValueError("Unsupported connection type specified.")
    return df, cleaned_df