from typing import Any

import pandas as pd
import streamlit as st


def remove_duplicates(
    dataframes: list[pd.DataFrame], primary_key: str
) -> list[pd.DataFrame]:
    cleaned: list[pd.DataFrame] = []
    for i, df in enumerate(dataframes, start=1):
        if primary_key and primary_key in df.columns:
            if df.duplicated(subset=[primary_key]).any():
                st.warning(
                    f"⚠️ Dataset {i} contains duplicate `{primary_key}` entries. "
                    "Duplicates will be removed."
                )
                df = df.drop_duplicates(subset=[primary_key])
        cleaned.append(df)
    return cleaned


def fill_missing_values(
    dataframes: list[pd.DataFrame], fill_value: Any
) -> list[pd.DataFrame]:
    return [df.fillna(fill_value) for df in dataframes]
