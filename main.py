import streamlit as st
import pandas as pd
import pyreadstat
from functools import reduce
import matplotlib.pyplot as plt
import seaborn as sns

# Set Streamlit page configuration
st.set_page_config(
    page_title="📊 Longitudinal Data Merger",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state variables
if 'data_frames' not in st.session_state:
    st.session_state['data_frames'] = []
if 'file_names' not in st.session_state:
    st.session_state['file_names'] = []
if 'wave_assignments' not in st.session_state:
    st.session_state['wave_assignments'] = {}
if 'merged_df' not in st.session_state:
    st.session_state['merged_df'] = None
if 'merge_type' not in st.session_state:
    st.session_state['merge_type'] = None

# Function to load files based on format
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
        
        # Apply filtering if 'Status' and 'Finished' columns exist
        if 'Status' in df.columns and 'Finished' in df.columns:
            df = df.query('Status == 0 and Finished == 1')
        
        return df
    except Exception as e:
        st.error(f"Error loading file `{file.name}`: {e}")
        return None

# Function to remove duplicate primary keys within each dataset
def remove_duplicates(data_frames, primary_key):
    cleaned_dfs = []
    for i, df in enumerate(data_frames, start=1):
        if primary_key and primary_key in df.columns:
            if df.duplicated(subset=[primary_key]).any():
                st.warning(f"⚠️ Dataset {i} contains duplicate `{primary_key}` entries. Duplicates will be removed.")
                df = df.drop_duplicates(subset=[primary_key])
        cleaned_dfs.append(df)
    return cleaned_dfs

# Function to merge datasets in wide format
@st.cache_data
def merge_datasets_wide(data_frames, primary_key, join_type, wave_assignments):
    renamed_dfs = []
    for i, df in enumerate(data_frames, start=1):
        df_renamed = df.copy()
        suffix = f"_w{wave_assignments[i]}"
        # Rename columns except primary key with wave-specific suffixes
        new_columns = {
            col: f"{col}{suffix}" if col != primary_key else col for col in df_renamed.columns
        }
        df_renamed.rename(columns=new_columns, inplace=True)
        renamed_dfs.append(df_renamed)
    
    # Perform the merge using the specified join type
    merged_df = reduce(
        lambda left, right: pd.merge(left, right, on=primary_key, how=join_type),
        renamed_dfs
    )
    return merged_df

# Function to merge datasets in long format
@st.cache_data
def merge_datasets_long(data_frames, primary_key, wave_assignments):
    # Add 'Wave' identifier to each dataframe
    for i, df in enumerate(data_frames, start=1):
        df['Wave'] = f"w{wave_assignments[i]}"
    
    # Concatenate all dataframes vertically
    concatenated_df = pd.concat(data_frames, ignore_index=True)
    
    # Find common primary keys present in all datasets
    common_ids = set.intersection(*(set(df[primary_key]) for df in data_frames))
    
    # Filter to retain only common primary keys
    merged_df = concatenated_df[concatenated_df[primary_key].isin(common_ids)]
    
    return merged_df, len(common_ids)

# Function to display missing values summary
def display_missing_values(df):
    st.write("### 🧩 Missing Values Summary")
    missing_summary = df.isnull().sum().sort_values(ascending=False)
    st.write(missing_summary)
    
    # Visualize missing values
    st.write("#### 📊 Missing Values Visualization")
    plt.figure(figsize=(12, 8))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
    st.pyplot(plt)

# App title and introduction
st.title("📊 Longitudinal Data Merger")
st.markdown("""
Welcome to the **Longitudinal Data Merger** app! This tool is designed to help researchers seamlessly merge multiple longitudinal datasets in both **Wide** (horizontal) and **Long** (vertical) formats. 

### **Key Features:**
- **Supported File Formats:** CSV, Excel (.xlsx), SPSS (.sav)
- **Wave Assignment:** Assign each dataset to a specific wave
- **Flexible Primary Key Selection:** Choose your primary key via a scrolling menu
- **Comprehensive Merge Options:** Inner, left, right, and outer joins for wide merges
- **Data Cleaning:** Option to fill missing values
- **Summary Statistics:** View detailed statistics post-merge
- **Missing Values Analysis:** Comprehensive summaries and visualizations
- **Session Persistence:** Preserves your work throughout the session

Let's get started!
""")

# Sidebar for file upload and wave assignment
st.sidebar.header("📁 Step 1: Upload Datasets")
uploaded_files = st.sidebar.file_uploader(
    "Upload your datasets (CSV, Excel, or SPSS):",
    type=["csv", "xlsx", "sav"],
    accept_multiple_files=True
)

# Handle file uploads
if uploaded_files:
    with st.sidebar.expander("🗂 Step 2: Assign Wave Numbers"):
        wave_assignments = {}
        for i, file in enumerate(uploaded_files, start=1):
            wave_number = st.number_input(
                f"🔢 Wave number for `{file.name}`:",
                min_value=1,
                step=1,
                key=f"wave_{i}"
            )
            wave_assignments[i] = wave_number
        st.session_state['wave_assignments'] = wave_assignments
    
    # Load datasets
    with st.spinner('🔄 Loading datasets...'):
        data_frames = []
        file_names = []
        for i, file in enumerate(uploaded_files, start=1):
            df = load_file(file)
            if df is not None:
                data_frames.append(df)
                file_names.append(file.name)
                st.sidebar.success(f"✅ Loaded `{file.name}` successfully!")
        st.session_state['data_frames'] = data_frames
        st.session_state['file_names'] = file_names
    
    # Preview uploaded datasets
    if data_frames:
        st.sidebar.info(f"📥 {len(data_frames)} dataset(s) uploaded.")
        with st.expander("🔍 Step 3: View Uploaded Datasets"):
            for i, df in enumerate(data_frames, start=1):
                st.write(f"### 📄 Dataset {i}: `{file_names[i-1]}`")
                st.dataframe(df.head())
else:
    st.sidebar.info("🚀 Begin by uploading your datasets here.")

# Primary Key Selection
st.sidebar.header("🔑 Step 4: Select Primary Key")
if st.session_state['data_frames']:
    # Scrollable selectbox for primary key selection
    primary_key = st.sidebar.selectbox(
        "📝 Select Primary Key (Unique Case ID):",
        options=st.session_state['data_frames'][0].columns,
        help="Choose the column that uniquely identifies each case across all datasets."
    )
    
    if primary_key:
        # Validate primary key presence in all datasets
        missing_pk = []
        for i, df in enumerate(st.session_state['data_frames'], start=1):
            if primary_key not in df.columns:
                missing_pk.append(i)
        if missing_pk:
            st.sidebar.error(f"🚨 The primary key `{primary_key}` is missing in dataset(s): {missing_pk}. Please choose a different primary key.")
        else:
            # Check data type consistency
            pk_types = [df[primary_key].dtype for df in st.session_state['data_frames']]
            if len(set(pk_types)) > 1:
                st.sidebar.error("🚨 Inconsistent data types for the primary key across datasets. Please ensure all primary keys have the same data type.")
            else:
                # Proceed with merging options
                st.session_state['data_frames'] = remove_duplicates(st.session_state['data_frames'], primary_key)
                
                # Merge Options
                st.sidebar.header("🔀 Step 5: Configure Merge Options")
                merge_type = st.sidebar.radio(
                    "🔍 Choose Merge Type:",
                    options=["Wide (Horizontal)", "Long (Vertical)"],
                    help="Select how you want to merge your datasets."
                )
                
                # For Wide merge, choose join type
                if merge_type == "Wide (Horizontal)":
                    join_type = st.sidebar.selectbox(
                        "🔗 Select Join Type:",
                        options=["inner", "left", "right", "outer"],
                        index=0,  # default to 'inner'
                        help="Choose the type of join operation for merging datasets."
                    )
                else:
                    join_type = None  # Not applicable for long merge
                
                # Optional Data Cleaning
                st.sidebar.header("🧹 Step 6: Data Cleaning Options")
                fill_missing = st.sidebar.checkbox("🛠 Fill Missing Values")
                if fill_missing:
                    fill_value = st.sidebar.text_input("🔧 Fill with (e.g., 0, 'Unknown'):", value="0")
                    if fill_value:
                        for i in range(len(st.session_state['data_frames'])):
                            st.session_state['data_frames'][i] = st.session_state['data_frames'][i].fillna(fill_value)
                        st.sidebar.success("✅ Missing values filled successfully.")
                
                # Merge Datasets Button
                st.sidebar.header("🚀 Step 7: Merge Datasets")
                if st.sidebar.button("🚀 Merge Datasets"):
                    with st.spinner('🔄 Merging datasets...'):
                        try:
                            if merge_type == "Wide (Horizontal)":
                                # Perform wide merge
                                merged_df = merge_datasets_wide(
                                    st.session_state['data_frames'],
                                    primary_key,
                                    join_type,
                                    st.session_state['wave_assignments']
                                )
                                st.session_state['merge_type'] = merge_type
                                st.session_state['merged_df'] = merged_df
                                
                                st.success(f"✅ Datasets merged successfully ({merge_type} with `{join_type}` join).")
                                
                                # Display summary statistics
                                st.write("### 📈 Summary Statistics (Wide Merge)")
                                st.write(f"**Number of Instances:** {merged_df.shape[0]}")
                            
                            elif merge_type == "Long (Vertical)":
                                # Perform long merge
                                merged_df, common_ids_count = merge_datasets_long(
                                    st.session_state['data_frames'],
                                    primary_key,
                                    st.session_state['wave_assignments']
                                )
                                st.session_state['merge_type'] = merge_type
                                st.session_state['merged_df'] = merged_df
                                
                                # Calculate expected and actual rows
                                expected_rows = common_ids_count * len(st.session_state['data_frames'])
                                actual_rows = merged_df.shape[0]
                                if actual_rows != expected_rows:
                                    st.warning(f"⚠️ Expected {expected_rows} rows (for {common_ids_count} cases across {len(st.session_state['data_frames'])} waves), but got {actual_rows} rows.")
                                else:
                                    st.success(f"✅ Datasets merged successfully ({merge_type}).")
                                
                                # Display summary statistics
                                st.write("### 📈 Summary Statistics (Long Merge)")
                                st.write(f"**Total Number of Instances:** {merged_df.shape[0]}")
                                st.write("**Number of Instances per Wave:**")
                                st.write(merged_df['Wave'].value_counts())
                            
                            # Display merged dataset preview
                            st.write("### 📄 Merged Dataset Preview")
                            st.dataframe(st.session_state['merged_df'].head())
                            
                            # Summary of Missing Values
                            display_missing_values(st.session_state['merged_df'])
                            
                            # Allow user to download merged dataset
                            csv = st.session_state['merged_df'].to_csv(index=False).encode("utf-8")
                            st.download_button(
                                label="💾 Download Merged Dataset",
                                data=csv,
                                file_name="merged_dataset.csv",
                                mime="text/csv"
                            )
                        
                        except Exception as e:
                            st.error(f"❌ Error during merging: {e}")

else:
    st.sidebar.info("🚀 Begin by uploading your datasets here.")

# Footer with professional references
st.markdown("---")
st.markdown("### **Gabriele Di Cicco, PhD in Social Psychology**")
st.markdown("""
[GitHub](https://github.com/gdc0000) | 
[ORCID](https://orcid.org/0000-0002-1439-5790) | 
[LinkedIn](https://www.linkedin.com/in/gabriele-di-cicco-124067b0/)
""")
