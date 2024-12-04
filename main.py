import streamlit as st
import pandas as pd
import pyreadstat
from functools import reduce

# Title and description
st.title("Longitudinal Data Merger")
st.write("""
This app allows you to merge multiple longitudinal datasets in **Wide** (horizontal) or **Long** (vertical) format. 
It supports **CSV**, **Excel**, and **SPSS (.sav)** files.
""")

# Sidebar for uploading datasets
st.sidebar.header("Upload Datasets")
uploaded_files = st.sidebar.file_uploader(
    "Upload your datasets (CSV, Excel, or SPSS):",
    type=["csv", "xlsx", "sav"],
    accept_multiple_files=True
)

# Function to read files based on their format
def read_file(file):
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            return pd.read_excel(file)
        elif file.name.endswith(".sav"):
            df, _ = pyreadstat.read_sav(file)
            return df
        else:
            raise ValueError("Unsupported file type")
    except Exception as e:
        st.error(f"Error reading file `{file.name}`: {e}")
        return None

# Process uploaded files
data_frames = []
if uploaded_files:
    for file in uploaded_files:
        df = read_file(file)
        if df is not None:
            data_frames.append(df)
            st.sidebar.success(f"File `{file.name}` loaded successfully!")

    if data_frames:
        st.sidebar.info(f"{len(data_frames)} datasets loaded.")
    else:
        st.sidebar.warning("No valid datasets uploaded.")

# If datasets are loaded, ask for further options
if data_frames:
    st.sidebar.header("Merge Options")

    # Select primary key
    primary_key = st.sidebar.selectbox(
        "Select Primary Key (Unique Case ID):",
        options=data_frames[0].columns
    )

    # Select merge type
    merge_type = st.sidebar.radio(
        "Choose Merge Type:",
        options=["Wide (Horizontal)", "Long (Vertical)"]
    )

    # Merge datasets button
    if st.sidebar.button("Merge Datasets"):
        try:
            # Wide merge
            if merge_type == "Wide (Horizontal)":
                merged_df = reduce(
                    lambda left, right: pd.merge(left, right, on=primary_key, how="inner"),
                    data_frames
                )
                # Rename columns with wave-specific suffixes
                for i, df in enumerate(data_frames, start=1):
                    suffix = f"_w{i}"
                    for col in df.columns:
                        if col != primary_key and col in merged_df.columns:
                            merged_df.rename(columns={col: f"{col}{suffix}"}, inplace=True)

            # Long merge
            elif merge_type == "Long (Vertical)":
                merged_df = pd.concat(
                    [df.assign(wave=f"w{i+1}") for i, df in enumerate(data_frames)],
                    ignore_index=True
                )
                # Retain only rows with common primary keys
                common_ids = set.intersection(*(set(df[primary_key]) for df in data_frames))
                merged_df = merged_df[merged_df[primary_key].isin(common_ids)]

            # Display merged dataset
            st.success(f"Datasets merged successfully ({merge_type}).")
            st.write("Preview of Merged Dataset:")
            st.dataframe(merged_df.head())

            # Allow user to download merged dataset
            csv = merged_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Merged Dataset",
                data=csv,
                file_name="merged_dataset.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error during merging: {e}")

# Footer with professional references
st.markdown("---")
st.markdown("### **Dr. Gabriele Di Cicco, PhD in Social Psychology**")
st.markdown("""
[GitHub](https://github.com/gdc0000) | 
[ORCID](https://orcid.org/0000-0002-1439-5790) | 
[LinkedIn](https://www.linkedin.com/in/gabriele-di-cicco-124067b0/)
""")
