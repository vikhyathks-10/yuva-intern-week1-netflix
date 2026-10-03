# Netflix Movies and TV Shows — Data Acquisition, Cleaning, and Preprocessing

**Yuva Internship — Week 1 Project**  
**Student Name:** Vikhyath Bharadwaj K S  
**Domain:** Data Science & Data Engineering  

---

## 📌 Project Overview
This repository contains the complete end-to-end implementation for **Week 1 of the Yuva Internship program**. The project focuses on building a professional data engineering and exploratory data analysis pipeline using the popular **Netflix Movies and TV Shows** dataset curated by Shivam Bansal.

The pipeline covers raw data acquisition, comprehensive data quality auditing, transparent missing value imputation, feature engineering, statistical visual exploratory analysis, notebook execution, and professional report generation.

---

## 🎯 Assignment Objectives
- Establish an industry-standard directory structure for reproducible data analysis.
- Acquire raw dataset from reliable open-source repositories and preserve raw files without modification.
- Execute exploratory data analysis (EDA) to evaluate content distribution, missing values, duplicates, and release trends.
- Design a transparent data cleaning methodology that retains 100% of rows while imputing missing values.
- Engineer domain-specific features (temporal attributes, duration metrics, primary genres, target audience binning).
- Develop modular Python scripts and an interactive Jupyter Notebook.
- Generate a comprehensive DOCX project report suitable for academic and internship evaluation.
- Publish the verified project repository to GitHub.

---

## 📂 Repository Folder Structure
```text
yuva-intern-week1-netflix/
├── dataset/
│   ├── original/
│   │   └── netflix_titles.csv           # Preserved raw dataset (7,787 rows, 12 columns)
│   └── processed/
│       ├── netflix_cleaned.csv          # Cleaned dataset (missing values imputed)
│       └── netflix_processed.csv        # Analysis-ready dataset with 28 engineered features
├── notebooks/
│   └── netflix_data_analysis.ipynb      # Reproducible interactive Jupyter Notebook
├── src/
│   ├── data_loading.py                  # Module for fetching raw dataset
│   ├── data_exploration.py              # Module for EDA and initial chart generation
│   ├── data_cleaning.py                 # Module for data quality assessment & cleaning
│   ├── preprocessing.py                 # Module for feature engineering & preprocessing
│   ├── build_notebook.py                # Automation script building the Jupyter Notebook
│   └── generate_report.py               # Automation script creating the formatted DOCX report
├── visualizations/                      # High-resolution chart exports (.png)
├── reports/
│   └── Yuva_Internship_Week1_Report.docx # Formatted academic project report
├── README.md                            # Comprehensive project documentation
├── requirements.txt                     # Project python dependencies
└── .gitignore                           # Git exclusion rules
```

---

## 🛠️ Technologies Used
- **Python 3.13+**
- **Pandas**: Data manipulation, missing value imputation, and feature creation.
- **NumPy**: Vectorized data transformation and array processing.
- **Matplotlib & Seaborn**: High-resolution visual plotting and aesthetic chart styling.
- **Jupyter Notebook**: Interactive execution and document presentation.
- **Python-Docx**: Programmatic compilation of structured DOCX reports with custom styling.
- **Git & GitHub**: Version control and public repository hosting.

---

## 🚀 Setup & Execution Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/vikhyathbharadwaj/yuva-intern-week1-netflix.git
cd yuva-intern-week1-netflix
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Pipeline Modules
You can execute individual modular Python scripts sequentially:

```bash
# Step 1: Download & store raw dataset
python src/data_loading.py

# Step 2: Perform EDA & generate initial visualizations
python src/data_exploration.py

# Step 3: Run data cleaning & impute missing values
python src/data_cleaning.py

# Step 4: Run preprocessing & feature engineering
python src/preprocessing.py

# Step 5: Build Jupyter Notebook
python src/build_notebook.py

# Step 6: Build DOCX report
python src/generate_report.py
```

### 4. Execute Jupyter Notebook
To run the notebook interactively:
```bash
jupyter notebook notebooks/netflix_data_analysis.ipynb
```

---

## 📊 Summary of Main Findings
1. **Content Type Ratio**: 69.05% Movies (5,377 titles) vs 30.95% TV Shows (2,410 titles).
2. **Missingness Resolved**: Imputed `director` (2,389 missing), `cast` (718 missing), `country` (507 missing), `rating` (7 missing), and `date_added` (10 missing) with zero data loss.
3. **Top Content Producer**: United States (2,877 titles), followed by India (990 titles) and United Kingdom (576 titles).
4. **Primary Audience**: Over 45% of content is classified as Adult/Mature (`TV-MA`, `R`).
5. **Movie Duration Trend**: Median movie duration is **98 minutes**.

---

## 📄 Final Deliverables
- **Jupyter Notebook**: `notebooks/netflix_data_analysis.ipynb`
- **Cleaned Dataset**: `dataset/processed/netflix_cleaned.csv`
- **Processed Dataset**: `dataset/processed/netflix_processed.csv`
- **DOCX Report**: `reports/Yuva_Internship_Week1_Report.docx`
- **Visualizations**: `visualizations/`

---

## 📜 Dataset Licensing & Acknowledgments
- **Dataset Author**: Shivam Bansal
- **Dataset Sources**: Kaggle / Flixable / TidyTuesday
- **Licensing**: Public Domain CC0 / Educational use.
