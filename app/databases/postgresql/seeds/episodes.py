from pathlib import Path

import numpy as np
import pandas as pd


def get_base_directory() -> Path:
    """Get the base directory of the package."""
    return Path(__file__).resolve().parent


def read_excel_file(file_path: str, sheet: int = 0) -> pd.DataFrame:
    """
    Read an Excel file and return a DataFrame
    """
    df = pd.read_excel(file_path, sheet_name=sheet, engine="openpyxl")
    return df

def rename_columns(df: pd.DataFrame, columns_map: dict) -> pd.DataFrame:
    """
    Rename columns in the dataframe based on the provided mapping.
    """
    return df.rename(columns=columns_map)

def filter_valid_episodes(
    df: pd.DataFrame, column: str, values: list[str]
) -> pd.DataFrame:
    """
    Filter the data with a specific column and values.
    """
    df_filtered = df[df[column].isin(values)]
    return df_filtered

def process_episode_data() -> pd.DataFrame:
	"""
	Process the episode data by cleaning and filling Episodes table
	"""
	file_path = get_base_directory() / "data" / "episodes_data.xlsx"
	df = read_excel_file(file_path, sheet=0)

	# Filter valid episodes
	valid_types = ["Type1", "Type2", "Type3"]
	df = df[df["episode_type"].isin(valid_types)]

	# Drop irrelevant columns
	columns_to_drop = ["unnecessary_col1", "unnecessary_col2"]
	df = df.drop(columns=columns_to_drop, errors="ignore")

	# Rename columns for consistency
	columns_map = {
		"old_name1": "new_name1",
		"old_name2": "new_name2",
	}
	df = df.rename(columns=columns_map)

	# Encode binary columns
	binary_columns = ["has_condition1", "has_condition2"]
	for col in binary_columns:
		if col in df.columns:
			df[col] = df[col].apply(lambda x: 1 if x == "Yes" else 0 if x == "No" else np.nan)

	# Fill missing values
	df.fillna({
		"new_name1": "Unknown",
		"new_name2": 0,
	}, inplace=True)

	return df

if __name__ == '__main__':

    print(get_base_directory()) 