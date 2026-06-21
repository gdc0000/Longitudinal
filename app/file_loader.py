import pandas as pd
import streamlit as st
import pyreadstat

from app.config import STATUS_COL, FINISHED_COL


@st.cache_data
def load_file(file) -> pd.DataFrame | None:
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file, engine="openpyxl")
        elif file.name.endswith(".sav"):
            df, _ = pyreadstat.read_sav(file)
        else:
            raise ValueError(f"Unsupported file format: {file.name}")

        df.columns = df.columns.str.strip()

        if STATUS_COL in df.columns and FINISHED_COL in df.columns:
            df = df.query(f"{STATUS_COL} == 0 and {FINISHED_COL} == 1")

        return df
    except Exception as e:
        st.error(f"Error loading file `{file.name}`: {e}")
        return None
