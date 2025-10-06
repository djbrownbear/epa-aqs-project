import os
import json
import pandas as pd
from datetime import datetime as dt
import pandas.tseries.offsets as offsets

def read_flatten_json(filepath):
    """Read a JSON file and flatten header into each record."""
    with open(filepath, "r") as f:
        j = json.load(f)
    header = j["Header"][0] if isinstance(j["Header"], list) and len(j["Header"]) == 1 else j["Header"]
    records = []
    for record in j["Data"]:
        record_with_header = {**record, **header}
        records.append(record_with_header)
    return records

def combine_json_files(data_dir, pattern="quarterlysummary_by_state", flatten_header=True):
    """Combine all matching JSON files in a directory."""
    files = [f for f in os.listdir(data_dir) if f.startswith(pattern) and f.endswith(".json")]
    if not files:
        raise FileNotFoundError("No matching files found.")
    all_records = []
    for fname in files:
        all_records.extend(read_flatten_json(os.path.join(data_dir, fname)))
    df = pd.DataFrame(all_records)
    return df

def add_quarter_end_date(df, year_col="year", quarter_col="quarter", date_col="date"):
    """Add end-of-quarter date column."""
    df[year_col] = df[year_col].astype(int)
    df[quarter_col] = df[quarter_col].astype(int)
    df[date_col] = pd.to_datetime(df[year_col].astype(str) + 'Q' + df[quarter_col].astype(str)) + offsets.QuarterEnd()
    return df

def main(data_dir=None, output_file=None):
    if data_dir is None:
        data_dir = input("Enter the directory containing JSON files: ")
        data_dir = os.path.normpath(data_dir)
    if output_file is None:
        output_file = f"combined_data_{dt.now().strftime('%Y%m%d')}.csv"
    df = combine_json_files(data_dir)
    df = add_quarter_end_date(df)
    df.to_csv(output_file, index=False)
    print(f"Combined data saved to {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()