import pandas as pd
from utils import load_data_section_to_dataframe

def analyze_air_quality_data(df):
    """Perform exploratory data analysis on the air quality DataFrame."""
    print("Descriptive Statistics:")
    print(df.describe())

    print("Missing Values:")
    print(df.isnull().sum())

    # Add more analysis as needed

if __name__ == "__main__":
    # Example usage
  df = load_data_section_to_dataframe()
  analyze_air_quality_data(df)

