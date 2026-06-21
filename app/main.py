import streamlit as st
import pandas as pd

from app.config import (
    PAGE_TITLE,
    PAGE_LAYOUT,
    INITIAL_SIDEBAR_STATE,
    SUPPORTED_EXTENSIONS,
    AUTHOR_NAME,
    AUTHOR_GITHUB,
    AUTHOR_ORCID,
    AUTHOR_LINKEDIN,
    DEFAULT_FILL_VALUE,
)
from app.state import init_session_state
from app.file_loader import load_file
from app.processing import remove_duplicates, fill_missing_values
from app.merging import merge_wide, merge_long
from app.visualization import display_missing_values


def main() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE,
        layout=PAGE_LAYOUT,
        initial_sidebar_state=INITIAL_SIDEBAR_STATE,
    )

    init_session_state()

    st.title(PAGE_TITLE)
    st.markdown("""
Welcome to the **Longitudinal Data Merger** app! This tool is designed to help
researchers seamlessly merge multiple longitudinal datasets in both **Wide**
(horizontal) and **Long** (vertical) formats.

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

    st.sidebar.header("📁 Step 1: Upload Datasets")
    uploaded_files = st.sidebar.file_uploader(
        "Upload your datasets (CSV, Excel, or SPSS):",
        type=SUPPORTED_EXTENSIONS,
        accept_multiple_files=True,
    )

    if uploaded_files:
        with st.sidebar.expander("🗂 Step 2: Assign Wave Numbers"):
            wave_assignments = {}
            for i, file in enumerate(uploaded_files, start=1):
                wave_number = st.number_input(
                    f"🔢 Wave number for `{file.name}`:",
                    min_value=1,
                    step=1,
                    key=f"wave_{i}",
                )
                wave_assignments[i] = wave_number
            st.session_state["wave_assignments"] = wave_assignments

        with st.spinner("🔄 Loading datasets..."):
            data_frames = []
            file_names = []
            for file in uploaded_files:
                df = load_file(file)
                if df is not None:
                    data_frames.append(df)
                    file_names.append(file.name)
                    st.sidebar.success(f"✅ Loaded `{file.name}` successfully!")
            st.session_state["data_frames"] = data_frames
            st.session_state["file_names"] = file_names

        if data_frames:
            st.sidebar.info(f"📥 {len(data_frames)} dataset(s) uploaded.")
            with st.expander("🔍 Step 3: View Uploaded Datasets"):
                for i, df in enumerate(data_frames, start=1):
                    st.write(f"### 📄 Dataset {i}: `{file_names[i - 1]}`")
                    st.dataframe(df.head())
    else:
        st.sidebar.info("🚀 Begin by uploading your datasets here.")

    st.sidebar.header("🔑 Step 4: Select Primary Key")
    if st.session_state["data_frames"]:
        primary_key = st.sidebar.selectbox(
            "📝 Select Primary Key (Unique Case ID):",
            options=st.session_state["data_frames"][0].columns,
            help="Choose the column that uniquely identifies each case across all datasets.",
        )

        if primary_key:
            missing_pk = [
                i
                for i, df in enumerate(st.session_state["data_frames"], start=1)
                if primary_key not in df.columns
            ]
            if missing_pk:
                st.sidebar.error(
                    f"🚨 The primary key `{primary_key}` is missing in dataset(s): "
                    f"{missing_pk}. Please choose a different primary key."
                )
            else:
                pk_types = [
                    df[primary_key].dtype
                    for df in st.session_state["data_frames"]
                ]
                if len(set(pk_types)) > 1:
                    st.sidebar.error(
                        "🚨 Inconsistent data types for the primary key across "
                        "datasets. Please ensure all primary keys have the same data type."
                    )
                else:
                    st.session_state["data_frames"] = remove_duplicates(
                        st.session_state["data_frames"], primary_key
                    )

                    st.sidebar.header("🔀 Step 5: Configure Merge Options")
                    merge_type = st.sidebar.radio(
                        "🔍 Choose Merge Type:",
                        options=["Wide (Horizontal)", "Long (Vertical)"],
                        help="Select how you want to merge your datasets.",
                    )

                    if merge_type == "Wide (Horizontal)":
                        join_type = st.sidebar.selectbox(
                            "🔗 Select Join Type:",
                            options=["inner", "left", "right", "outer"],
                            index=0,
                            help="Choose the type of join operation for merging datasets.",
                        )
                    else:
                        join_type = None

                    st.sidebar.header("🧹 Step 6: Data Cleaning Options")
                    fill_missing = st.sidebar.checkbox("🛠 Fill Missing Values")
                    if fill_missing:
                        fill_value = st.sidebar.text_input(
                            "🔧 Fill with (e.g., 0, 'Unknown'):",
                            value=DEFAULT_FILL_VALUE,
                        )
                        if fill_value:
                            st.session_state["data_frames"] = fill_missing_values(
                                st.session_state["data_frames"], fill_value
                            )
                            st.sidebar.success("✅ Missing values filled successfully.")

                    st.sidebar.header("🚀 Step 7: Merge Datasets")
                    if st.sidebar.button("🚀 Merge Datasets"):
                        with st.spinner("🔄 Merging datasets..."):
                            try:
                                if merge_type == "Wide (Horizontal)":
                                    merged_df = merge_wide(
                                        st.session_state["data_frames"],
                                        primary_key,
                                        join_type,
                                        st.session_state["wave_assignments"],
                                    )
                                    st.session_state["merge_type"] = merge_type
                                    st.session_state["merged_df"] = merged_df

                                    st.success(
                                        f"✅ Datasets merged successfully "
                                        f"({merge_type} with `{join_type}` join)."
                                    )
                                    st.write("### 📈 Summary Statistics (Wide Merge)")
                                    st.write(f"**Number of Instances:** {merged_df.shape[0]}")

                                elif merge_type == "Long (Vertical)":
                                    merged_df, common_ids_count = merge_long(
                                        st.session_state["data_frames"],
                                        primary_key,
                                        st.session_state["wave_assignments"],
                                    )
                                    st.session_state["merge_type"] = merge_type
                                    st.session_state["merged_df"] = merged_df

                                    expected = (
                                        common_ids_count
                                        * len(st.session_state["data_frames"])
                                    )
                                    actual = merged_df.shape[0]
                                    if actual != expected:
                                        st.warning(
                                            f"⚠️ Expected {expected} rows "
                                            f"(for {common_ids_count} cases across "
                                            f"{len(st.session_state['data_frames'])} "
                                            f"waves), but got {actual} rows."
                                        )
                                    else:
                                        st.success(
                                            f"✅ Datasets merged successfully ({merge_type})."
                                        )

                                    st.write("### 📈 Summary Statistics (Long Merge)")
                                    st.write(f"**Total Number of Instances:** {merged_df.shape[0]}")
                                    st.write("**Number of Instances per Wave:**")
                                    st.write(merged_df["Wave"].value_counts())

                                st.write("### 📄 Merged Dataset Preview")
                                st.dataframe(st.session_state["merged_df"].head())

                                display_missing_values(st.session_state["merged_df"])

                                csv = (
                                    st.session_state["merged_df"]
                                    .to_csv(index=False)
                                    .encode("utf-8")
                                )
                                st.download_button(
                                    label="💾 Download Merged Dataset",
                                    data=csv,
                                    file_name="merged_dataset.csv",
                                    mime="text/csv",
                                )

                            except Exception as e:
                                st.error(f"❌ Error during merging: {e}")

    else:
        st.sidebar.info("🚀 Begin by uploading your datasets here.")

    st.markdown("---")
    st.markdown(f"### **{AUTHOR_NAME}**")
    st.markdown(
        f"[GitHub]({AUTHOR_GITHUB}) | "
        f"[ORCID]({AUTHOR_ORCID}) | "
        f"[LinkedIn]({AUTHOR_LINKEDIN})"
    )


if __name__ == "__main__":
    main()
