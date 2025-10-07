import pandas as pd
from pathlib import Path
import re

# Set BASE_PATH to the directory containing the notebook/script
BASE_PATH = Path().resolve()
print(f"Base path set to: {BASE_PATH}")

REPORTS_PATH = BASE_PATH.parent / "my_reports" / "to_combine" # Default path for reports

if not REPORTS_PATH.exists():
    REPORTS_PATH = Path(input("Enter the path to the reports directory (default is current directory): ").strip())
    if not REPORTS_PATH:
      REPORTS_PATH = BASE_PATH
    else:
      REPORTS_PATH = REPORTS_PATH.resolve()
print(f"Reports path set to: {REPORTS_PATH}")

# Use rglob() with the pattern '*.csv' to find all CSV files recursively
csv_files = list(REPORTS_PATH.rglob('*.csv'))

def display_file_list(files):
    """Display the list of files found."""
    if not files:
        print("No CSV files found.")
    else:
        print(f"Found {len(files)} CSV files:")
        for i, f in enumerate(files):
            print(f"{i} - {f}\n")

def extract_year_from_filename(filename, pattern=r"(?!\_)(\d{4})(\d{4})?-?(\d{6})?\.csv"):
    """
    Extracts the pattern (i.e. 4-digit year) from a filename like 'Lead2019output.csv'.
    Returns the year as a string, or None if not found.
    """
    match = re.search(pattern, str(filename))
    if match:
        return match.group(1)
    return None

def combine_csv_files(file_list):
    """Combine multiple CSV files into a single DataFrame."""
    dataframes = []
    years = []
    for file in file_list:
        try:
            df = pd.read_csv(file)
            dataframes.append(df)
            if 'year' in df.columns:
               years.extend(df['year'].unique())
            else:
              year = extract_year_from_filename(file.name)
              if year:
                  years.append(year)
                  df['year'] = year
        except Exception as e:
          print(f"Error reading {file}: {e}")
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df, years
    else:
        return pd.DataFrame(), years
    
def save_combined_csv(df, years, filename=None):
  """
  Save the combined DataFrame to a CSV file.

  Args:
    df (pd.DataFrame): The DataFrame to save.
    years (list): List of years extracted from filenames.
    filename (str, optional): Base filename for output. Defaults to None.

  Returns:
    Path: Path to the saved CSV file.
  """
  filename = filename or "combined_output"
  if years:
    years_clean = sorted(set(years))
    year_range = f"{years_clean[0]}-{years_clean[-1]}"
    out_file = BASE_PATH / f"{filename}_{year_range}.csv"
  else:
    out_file = BASE_PATH / f"{filename}.csv"

  try:
    df.to_csv(out_file, index=False)
    print(f"Combined CSV saved to {out_file.resolve()}")
  except Exception as e:
    print(f"Error saving CSV: {e}")
    return None

  return out_file

def main():
    display_file_list(csv_files)
    
    if not csv_files:
        print("No CSV files to combine. Exiting.")
        return
    
    combined_df, years = combine_csv_files(csv_files)
    
    if combined_df.empty:
        print("No data found in the CSV files. Exiting.")
        return
    
    save_combined_csv(combined_df, years)

if __name__ == "__main__":
    main()
    print("Script executed successfully.")