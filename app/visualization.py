import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


def display_missing_values(df: pd.DataFrame) -> None:
    st.write("### 🧩 Missing Values Summary")
    missing_summary = df.isnull().sum().sort_values(ascending=False)
    st.write(missing_summary)

    st.write("#### 📊 Missing Values Visualization")
    plt.figure(figsize=(12, 8))
    sns.heatmap(df.isnull(), cbar=False, cmap="viridis")
    st.pyplot(plt)
