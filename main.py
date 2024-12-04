import streamlit as st
import pandas as pd
from io import StringIO
from functools import reduce

# Title and Description
st.title("Longitudinal Data Merger")
st.write("""
This app allows you to merge multiple longitudinal datasets either in a wide (horizontal) or long (vertical) format.
""")

# Sidebar for user inputs
st.sidebar.header("Upload Datasets")
uploaded_files = st.sidebar.file_uploader("Choose CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    data_frames = []
    file_names = []
    for uploaded_file in uploaded_files:
        try:
            df = pd.read_csv(uploaded_file)
            data_frames.append(df)
            file_names.append(uploaded_file.name)
            st.sidebar.success(f"Uploaded `{uploaded_file.name}` successfully.")
        except Exception as e:
            st.sidebar.error(f"Error loading `{uploaded_file.name}`: {e}")

    if data_frames:
        st.header("Uploaded Datasets")
        for i, df in enumerate(data_frames):
            st.subheader(f"Dataset {i+1}: {file_names[i]}")
            st.dataframe(df.head())

        # Select Primary Key
        st.sidebar.header("Merge Settings")
        primary_key = st.sidebar.selectbox(
            "Select Primary Key (Unique Case ID)",
            options=data_frames[0].columns.tolist()
        )

        # Select Merge Type
        merge_type = st.sidebar.selectbox(
            "Select Merge Type",
            options=["Wide (Horizontal Merge)", "Long (Vertical Merge)"]
        )

        if st.sidebar.button("Merge Datasets"):
            try:
                if merge_type == "Wide (Horizontal Merge)":
                    # Perform wide merge (inner join on primary key)
                    merged_df = reduce(lambda left, right: pd.merge(left, right, on=primary_key, how='inner', suffixes=('', '_dup')), data_frames)
                    
                    # Identify duplicate columns and rename them with prefix
                    cols = merged_df.columns.tolist()
                    new_cols = {}
                    for df_idx, col in enumerate(data_frames):
                        suffix = f"_w{df_idx+1}"
                        for column in col.columns:
                            if column != primary_key:
                                new_col = f"{column}{suffix}"
                                new_cols[column] = new_col
                    merged_df.rename(columns=new_cols, inplace=True)
                    
                    st.success("Datasets merged successfully (Wide format).")
                    st.dataframe(merged_df.head())

                else:
                    # Perform long merge (append) with a new wave identifier
                    merged_df = pd.DataFrame()
                    for idx, df in enumerate(data_frames):
                        temp_df = df.copy()
                        temp_df['wave'] = f"w{idx+1}"
                        merged_df = pd.concat([merged_df, temp_df], axis=0, ignore_index=True)
                    
                    # Perform inner join to keep only common primary keys
                    common_ids = set.intersection(*(set(df[primary_key]) for df in data_frames))
                    merged_df = merged_df[merged_df[primary_key].isin(common_ids)]
                    
                    st.success("Datasets merged successfully (Long format).")
                    st.dataframe(merged_df.head())

                # Option to download the merged dataset
                csv = merged_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Merged Dataset as CSV",
                    data=csv,
                    file_name='merged_dataset.csv',
                    mime='text/csv',
                )

            except Exception as e:
                st.error(f"An error occurred during merging: {e}")
else:
    st.info("Please upload one or more CSV files to begin.")

# Professional References
st.markdown("---")
st.markdown("### **Dr. Gabriele Di Cicco, PhD in Social Psychology**")
st.markdown("""
[GitHub](https://github.com/gdc0000) | 
[ORCID](https://orcid.org/0000-0002-1439-5790) | 
[LinkedIn](https://www.linkedin.com/in/gabriele-di-cicco-124067b0/)
""")
