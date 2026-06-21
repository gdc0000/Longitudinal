# Longitudinal Data Merger

**Longitudinal Data Merger** is a Streamlit-based application designed to help researchers merge multiple longitudinal datasets with ease. The tool supports both wide (horizontal) and long (vertical) merge formats, enabling you to combine datasets from different waves or time points with flexible join options and comprehensive data cleaning and analysis features.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

The **Longitudinal Data Merger** app allows you to:

- **Upload Datasets:** Supports CSV, Excel (.xlsx), and SPSS (.sav) files.
- **Assign Waves:** Easily assign a wave number to each dataset.
- **Select a Primary Key:** Choose a unique identifier (primary key) to ensure correct merging.
- **Merge in Two Formats:**
  - **Wide Merge:** Merge datasets horizontally with customizable join types (inner, left, right, outer).
  - **Long Merge:** Merge datasets vertically while retaining a 'Wave' identifier for each observation.
- **Data Cleaning:** Remove duplicate entries, fill missing values, and inspect missing data through summaries and visualizations.
- **Preview & Download:** View merged dataset previews, summary statistics, and download the final merged dataset.

---

## Features

- **Supported File Formats:**
  - CSV, Excel (.xlsx), and SPSS (.sav)
- **Wave Assignment:**
  - Assign wave numbers to datasets via the sidebar.
- **Primary Key Selection:**
  - Choose a unique identifier that exists across your datasets.
- **Merge Options:**
  - Wide (horizontal) merge with various join types.
  - Long (vertical) merge that retains a wave identifier.
- **Data Cleaning & Duplicate Removal:**
  - Automatically strips extra spaces from column names and filters datasets based on specific criteria (e.g., `Status` and `Finished` columns).
- **Missing Values Analysis:**
  - Get both a summary table and a heatmap visualization of missing data.
- **Session Persistence:**
  - Work is preserved throughout your session.
- **Downloadable Results:**
  - Easily download the merged dataset in CSV format.

---

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/longitudinal-data-merger.git
   cd longitudinal-data-merger
   ```
2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Required Dependencies**

   The dependencies are listed in the [`requirements.txt`](./requirements.txt) file. Install them using:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Run the Streamlit App**

   Launch the application with:

   ```bash
   streamlit run main.py
   ```
2. **Follow the On-Screen Instructions**

   - **Step 1: Upload Datasets**Use the sidebar to upload your datasets (CSV, Excel, or SPSS files).
   - **Step 2: Assign Wave Numbers**Assign a wave number to each dataset using the provided number inputs.
   - **Step 3: Preview Uploaded Datasets**Expand the "View Uploaded Datasets" section to see a preview of your data.
   - **Step 4: Select Primary Key**Choose a unique case identifier that is present in all datasets.
   - **Step 5: Configure Merge Options**

     - **Wide Merge:** Choose the join type (inner, left, right, outer) to merge datasets horizontally.
     - **Long Merge:** Merge datasets vertically while retaining wave information.
   - **Step 6: Data Cleaning Options**Optionally fill missing values across datasets.
   - **Step 7: Merge Datasets**
     Click the "Merge Datasets" button to perform the merge. The app will display summary statistics, a preview of the merged dataset, and a missing values analysis.
3. **Download the Merged Dataset**

   Once the merge is complete, download the merged dataset as a CSV file directly from the app.

---

## File Structure

```
.
├── main.py              # Entry point (streamlit run main.py)
├── app/
│   ├── __init__.py
│   ├── main.py          # Streamlit UI orchestration
│   ├── config.py        # App constants (page title, file types, column names)
│   ├── state.py         # Session state initialization
│   ├── file_loader.py   # File loading (CSV/XLSX/SAV) with caching
│   ├── processing.py    # Data cleaning: deduplicate, fill missing values
│   ├── merging.py       # Merge operations: wide (horizontal) and long (vertical)
│   └── visualization.py # Missing values summary and heatmap
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Shared test fixtures
│   ├── test_processing.py
│   └── test_merging.py
├── requirements.txt
└── README.md
```

---

## Contributing

Contributions are welcome! If you have suggestions, bug fixes, or improvements:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes.
4. Submit a pull request detailing your modifications.

---

## License

This project is open-source and available under the [MIT License](LICENSE).
