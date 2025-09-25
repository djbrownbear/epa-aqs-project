import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_json_to_dataframe

def analyze_air_quality_data(df):
    """Perform exploratory data analysis on the air quality DataFrame."""
    print("Descriptive Statistics:")
    print(df.describe())

    print("Missing Values:")
    print(df.isnull().sum())

    # Add more analysis as needed

if __name__ == "__main__":
  # Example usage
  header_df = load_json_to_dataframe(record_path="Header")
  print("Header DataFrame:")
  print(header_df)

  df = load_json_to_dataframe(record_path="Data")
  analyze_air_quality_data(df)

