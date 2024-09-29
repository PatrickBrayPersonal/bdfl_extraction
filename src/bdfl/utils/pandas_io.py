"""
Functions to generate pandas dataframes from file references
"""

from re import match

import pandas as pd
from datetime import datetime
import os
from inflection import underscore


def _snake_case_columns(df):
    # Convert column names to snake case using inflection.underscore
    new_columns = [underscore(col) for col in df.columns]

    # Create a new DataFrame with snake case column names
    new_df = df.copy()
    new_df.columns = new_columns

    # Check for duplicates
    if new_df.columns.duplicated().any():
        raise ValueError(
            f"Converting to snake case resulted in duplicate column names {new_df.columns.duplicated()}"
        )
    return new_df


def _insert_datetime_before_filetype(filepath: str) -> os.path:
    current_date = datetime.now().strftime("%Y%m%d-%H%M%S")
    dir_name, file_name = os.path.split(filepath)
    name, ext = os.path.splitext(file_name)
    new_file_name = f"{name}_{current_date}{ext}"
    new_filepath = os.path.join(dir_name, new_file_name)
    return new_filepath


def df_to_file(df: pd.DataFrame, path: str, add_datetime: bool = False, **kwargs):
    funcs = {
        r".*\.parquet": df.to_parquet,
        r".*\.p": df.to_pickle,
        r".*\.csv": df.to_csv,
        r".*\.xlsx": df.to_excel,
    }

    if add_datetime:
        path = _insert_datetime_before_filetype(path)

    for pattern, func in funcs.items():
        if match(pattern, path) is not None:
            func(path, **kwargs)
            return True
    raise ValueError(
        f"{path} does not match a known file pattern {', '.join(list(funcs.keys()))}"
    )


def file_to_df(path: str, snake_columns=True, **kwargs):
    """read a file to a DataFrame based on the file extension

    Raises:
        ValueError: value error if path does not include registered tag
    """

    funcs = {
        r".*\.parquet": pd.read_parquet,
        r".*\.p": pd.read_pickle,
        r".*\.csv": pd.read_csv,
        r".*\.xlsx": pd.read_excel,
    }
    for pattern, func in funcs.items():
        if match(pattern, path) is not None:
            df = func(path, **kwargs)
            if snake_columns:
                df = _snake_case_columns(df)
            return df
    raise ValueError(
        f"{path} does not match a known file pattern {', '.join(list(funcs.keys()))}"
    )
