import streamlit as st
import pandas as pd
import pyreadstat
from functools import reduce

# Caching the file loading function to optimize performance
@st.cache_data
def load_file(file):
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file, engine="openpyxl")
        elif file.name.endswith(".sav"):
            df, _ = pyreadstat.read_sav(file)
        else:
            raise ValueError(f"Unsupported file format: {file.name}")
        
        # Strip leading/trailing spaces from column names
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading file `{file.name}`: {e}")
        return None

# Caching the merge function for wide merge
@st.cache_data
def merge_datasets_wide(data_frames, primary_key, join_type):
    renamed_dfs = []
    for i, df in enumerate(data_frames, start=1):
        df_renamed = df.copy()
        suffix = f"_w{i}"
        # Rename columns except primary key with wave-specific suffixes
        new_columns = {
            col: f"{col}{suffix}" if col != primary_key else col for col in df_renamed.columns
        }
        df_renamed.rename(columns=new_columns, inplace=True)
        renamed_dfs.append(df_renamed)
    
    # Perform inner join across all dataframes
    merged_df = reduce(
        lambda left, right: pd.merge(left, right, on=primary_key, how=join_type),
        renamed_dfs
    )
    return merged_df

# Caching the merge function for long merge
@st.cache_data
def merge_datasets_long(data_frames, primary_key):
    # Add 'Wave' identifier to each dataframe
    for i, df in enumerate(data_frames, start=1):
        df['Wave'] = f"w{i}"
    
    # Concatenate all dataframes vertically
    concatenated_df = pd.concat(data_frames, ignore_index=True)
    
    # Find common primary keys present in all datasets
    common_ids = set.intersection(*(set(df[primary_key]) for df in data_frames))
    
    # Filter to retain only common primary keys
    merged_df = concatenated_df[concatenated_df[primary_key].isin(common_ids)]
    
    return merged_df, len(common_ids)

# Function to remove duplicate primary keys within each dataset
def remove_duplicates(data_frames, primary_key):
    cleaned_dfs = []
    for i, df in enumerate(data_frames, start=1):
        if df.duplicated(subset=[primary_key]).any():
            st.warning(f"⚠️ Dataset {i} contains duplicate `{primary_key}` entries. Duplicates will be removed.")
            df = df.drop_duplicates(subset=[primary_key])
        cleaned_dfs.append(df)
    return cleaned_dfs

# App title and description
st.title("📊 Longitudinal Data Merger")
st.write("""
This app allows you to merge multiple longitudinal datasets in **Wide** (horizontal) or **Long** (vertical) format.  
Supported file formats: **CSV**, **Excel (.xlsx)**, and **SPSS (.sav)**.
""")

# Sidebar for file upload
st.sidebar.header("📁 Upload Datasets")
uploaded_files = st.sidebar.file_uploader(
    "Upload your datasets (CSV, Excel, or SPSS):",
    type=["csv", "xlsx", "sav"],
    accept_multiple_files=True
)

# Load datasets
data_frames = []
file_names = []
if uploaded_files:
    with st.spinner('Loading datasets...'):
        for file in uploaded_files:
            df = load_file(file)
            if df is not None:
                data_frames.append(df)
                file_names.append(file.name)
                st.sidebar.success(f"✅ Loaded `{file.name}` successfully!")
    
    # Remove duplicates within datasets
    data_frames = remove_duplicates(data_frames, 'PROLIFIC_PID')  # Assuming 'PROLIFIC_PID' is the primary key
    
    # Preview uploaded datasets
    if data_frames:
        st.sidebar.info(f"📥 {len(data_frames)} dataset(s) uploaded.")
        with st.expander("🔍 View Uploaded Datasets"):
            for i, df in enumerate(data_frames):
                st.write(f"### Dataset {i+1}: `{file_names[i]}`")
                st.dataframe(df.head())
else:
    st.sidebar.info("Please upload one or more datasets to begin.")

# If datasets are uploaded, show merge options
if data_frames:
    st.sidebar.header("🔧 Merge Options")
    
    # Select primary key
    primary_key = st.sidebar.selectbox(
        "🔑 Select Primary Key (Unique Case ID):",
        options=data_frames[0].columns
    )
    
    # Advanced Validation: Check if all datasets contain the primary key
    missing_pk = []
    for i, df in enumerate(data_frames, start=1):
        if primary_key not in df.columns:
            missing_pk.append(i)
    
    if missing_pk:
        st.sidebar.error(f"🚨 The primary key `{primary_key}` is missing in dataset(s): {missing_pk}. Please choose a different primary key or ensure all datasets contain it.")
    else:
        # Check data type consistency for primary key
        pk_types = [df[primary_key].dtype for df in data_frames]
        if len(set(pk_types)) > 1:
            st.sidebar.error("🚨 Inconsistent data types for the primary key across datasets. Please ensure all primary keys have the same data type.")
        else:
            # Choose merge type
            merge_type = st.sidebar.radio(
                "🔀 Choose Merge Type:",
                options=["Wide (Horizontal)", "Long (Vertical)"]
            )
            
            # For Wide merge, choose join type
            if merge_type == "Wide (Horizontal)":
                join_type = st.sidebar.selectbox(
                    "🔗 Select Join Type:",
                    options=["inner", "left", "right", "outer"],
                    index=0  # default to 'inner'
                )
            else:
                join_type = None  # Not applicable for long merge
            
            # Option for data cleaning (optional)
            st.sidebar.header("🧹 Data Cleaning Options")
            fill_missing = st.sidebar.checkbox("Fill Missing Values")
            if fill_missing:
                fill_value = st.sidebar.text_input("Fill with (e.g., 0, 'Unknown'):", value="0")
                for i in range(len(data_frames)):
                    data_frames[i] = data_frames[i].fillna(fill_value)
                st.sidebar.success("✅ Missing values filled successfully.")
            
            # Merge datasets button
            if st.sidebar.button("🚀 Merge Datasets"):
                with st.spinner('Merging datasets...'):
                    try:
                        if merge_type == "Wide (Horizontal)":
                            # Perform wide merge with selected join type
                            merged_df = merge_datasets_wide(data_frames, primary_key, join_type)
                            
                        elif merge_type == "Long (Vertical)":
                            merged_df, common_ids_count = merge_datasets_long(data_frames, primary_key)
                            
                        # Display merged dataset
                        if merge_type == "Long (Vertical)":
                            expected_rows = common_ids_count * len(data_frames)
                            actual_rows = len(merged_df)
                            if actual_rows != expected_rows:
                                st.warning(f"⚠️ Expected {expected_rows} rows (for {common_ids_count} cases across {len(data_frames)} waves), but got {actual_rows} rows.")
                            else:
                                st.success(f"✅ Datasets merged successfully ({merge_type}).")
                        else:
                            st.success(f"✅ Datasets merged successfully ({merge_type} with {join_type} join).")
                        
                        st.write("### 📄 Merged Dataset Preview")
                        st.dataframe(merged_df.head())
                        
                        # Allow user to download merged dataset
                        csv = merged_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="💾 Download Merged Dataset",
                            data=csv,
                            file_name="merged_dataset.csv",
                            mime="text/csv"
                        )
                    
                    except Exception as e:
                        st.error(f"❌ Error during merging: {e}")

# Footer with professional references
st.markdown("---")
st.markdown("### **Dr. Gabriele Di Cicco, PhD in Social Psychology**")
st.markdown("""
[GitHub](https://github.com/gdc0000) | 
[ORCID](https://orcid.org/0000-0002-1439-5790) | 
[LinkedIn](https://www.linkedin.com/in/gabriele-di-cicco-124067b0/)
""")
