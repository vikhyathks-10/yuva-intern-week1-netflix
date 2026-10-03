# Netflix Movies and TV Shows — Data Analytics Pipeline & EDA

**Yuva Internship — Weeks 1 & 2**  
**Student Name:** Vikhyath Bharadwaj K S  
**Domain:** Data Analytics, Data Engineering & Data Visualization  
**Dataset:** Netflix Movies and TV Shows by Shivam Bansal (Kaggle)  

---

## 📌 Project Overview
This repository contains the complete end-to-end implementation for **Week 1 and Week 2 of the Yuva Internship program**. The project focuses on building an industry-standard data engineering, exploratory analysis, and data visualization pipeline using the **Netflix Movies and TV Shows** dataset.

- **Week 1:** Data Acquisition, Quality Auditing, Transparent Missing Value Imputation, Feature Engineering, and Pipeline Setup.
- **Week 2:** In-Depth Exploratory Data Analysis (EDA), Multi-Country & Genre Unnesting, Content Seasonality, Duration Distribution Analysis, Publication-Quality Visualizations, and Inferential Statistical Testing (Chi-Square & ANOVA).

---

## 🎯 Internship Objectives

### Week 1 Objectives
- Establish an organized, reproducible project folder structure.
- Ingest raw dataset (`7,787` records × `12` columns) and preserve original raw files.
- Design transparent cleaning operations retaining 100% of data rows.
- Engineer 16 new temporal, categorical, and numeric analytical attributes.
- Compile fully executed Jupyter Notebook and formatted DOCX report (`Yuva_Internship_Week1_Report.docx`).

### Week 2 Objectives
- Perform comprehensive EDA across Content Types, Release Years, Countries, Genres, Ratings, and Durations.
- Address multi-valued country and genre entries via array unnesting/exploding to avoid co-production undercounting.
- Generate 12 publication-quality data visualizations using Matplotlib & Seaborn saved in `visualizations/week2/`.
- Execute formal hypothesis testing (Chi-Square Test of Independence & ANOVA/Kruskal-Wallis Variance Analysis).
- Develop fully executed Jupyter Notebook (`notebooks/week2_eda_visualization.ipynb`) and academic DOCX report (`reports/Week2_EDA_Visualization_Report.docx`).

---

## 📂 Repository Directory Structure
```text
yuva-intern-week1-netflix/
│
├── dataset/
│   ├── original/
│   │   └── netflix_titles.csv               # Raw dataset (7,787 rows, 12 columns)
│   └── processed/
│       ├── netflix_cleaned.csv              # Imputed dataset (100% row preservation)
│       └── netflix_processed.csv            # Analysis-ready dataset with 28 columns
│
├── notebooks/
│   ├── netflix_data_analysis.ipynb          # Week 1 Executed Jupyter Notebook
│   └── week2_eda_visualization.ipynb        # Week 2 Executed Jupyter Notebook
│
├── src/
│   ├── data_loading.py                      # Data ingestion module
│   ├── data_cleaning.py                     # Data cleaning & imputation module
│   ├── preprocessing.py                     # Feature engineering module
│   ├── eda_analysis.py                      # Week 2 EDA & visualization module
│   ├── build_notebook.py                    # Week 1 notebook builder
│   ├── build_week2_notebook.py              # Week 2 notebook builder
│   ├── generate_report.py                   # Week 1 report builder
│   └── generate_week2_report.py             # Week 2 report builder
│
├── visualizations/
│   ├── 01_content_type_distribution.png     # Week 1 Visualizations
│   ├── ...
│   └── week2/                               # Week 2 Visualizations (12 PNG Charts)
│       ├── w2_01_content_type_distribution.png
│       ├── w2_02_release_year_trends.png
│       ├── w2_03_top_contributing_countries.png
│       ├── w2_04_top_listed_genres.png
│       ├── w2_05_content_ratings_by_type.png
│       ├── w2_06_movie_duration_histogram.png
│       ├── w2_07_tv_show_seasons_distribution.png
│       ├── w2_08_genre_content_type_heatmap.png
│       ├── w2_09_monthly_content_additions.png
│       ├── w2_10_content_age_lag_distribution.png
│       ├── w2_11_movie_duration_by_genre_boxplot.png
│       └── w2_12_country_type_breakdown.png
│
├── reports/
│   ├── Yuva_Internship_Week1_Report.docx    # Week 1 DOCX Report
│   └── Week2_EDA_Visualization_Report.docx  # Week 2 Comprehensive DOCX Report
│
├── README.md                                # Comprehensive Project Documentation
├── requirements.txt                         # Python Library Dependencies
└── .gitignore                               # Version Control Exclusion Rules
```

---

## 🛠️ Technologies & Libraries
- **Python 3.13+**
- **Pandas**: Data manipulation, unnesting/exploding multi-valued fields, crosstabulation, and datetime feature extraction.
- **NumPy**: Numeric operations, statistical computations, and array transformations.
- **Matplotlib & Seaborn**: Multi-panel visualization, distribution estimation (KDE), boxplots, and visual styling.
- **SciPy (`scipy.stats`)**: Chi-Square Test of Independence, One-Way ANOVA, and Kruskal-Wallis non-parametric tests.
- **Python-Docx**: Automated formatting and compilation of professional DOCX academic reports.
- **Jupyter & NbConvert**: Notebook generation and programmatic execution.

---

## 🚀 Setup & Execution Instructions

### 1. Clone Repository & Install Dependencies
```bash
git clone https://github.com/vikhyathks-10/yuva-intern-week1-netflix.git
cd yuva-intern-week1-netflix
pip install -r requirements.txt
```

### 2. Execute Week 1 Pipeline
```bash
python src/data_loading.py
python src/data_cleaning.py
python src/preprocessing.py
python src/build_notebook.py
python src/generate_report.py
```

### 3. Execute Week 2 EDA & Visualization Pipeline
```bash
# Run EDA calculations and generate all 12 Week 2 charts
python src/eda_analysis.py

# Rebuild and execute the Week 2 Jupyter Notebook
python src/build_week2_notebook.py
jupyter nbconvert --to notebook --execute --inplace notebooks/week2_eda_visualization.ipynb

# Generate the Week 2 DOCX Technical Report
python src/generate_week2_report.py
```

---

## 📊 Summary of Main Findings

### Week 1 Data Engineering Summary
- **Data Integrity:** Retained all 7,787 original rows while resolving missing values in `director`, `cast`, `country`, `rating`, and `date_added`.
- **Feature Engineering:** Added 16 features including `date_added_dt`, `year_added`, `month_added`, `content_age`, `duration_int`, `primary_genre`, `target_audience`, and `country_count`.

### Week 2 Exploratory Data Analysis Summary
1. **Content Ratio:** Movies comprise **69.05%** (5,377 titles) while TV Shows account for **30.95%** (2,410 titles).
2. **Catalog Trends:** Movie releases peaked in 2017 (767 releases), whereas TV Show releases peaked in 2020 (436 releases).
3. **Geographic Distribution (Unnested):** The **United States** leads overall production (3,297 titles), followed by **India** (990 titles, overwhelmingly Movies) and the **United Kingdom** (723 titles).
4. **Genre Hierarchy:** **International Movies** (2,437), **Dramas** (2,106), and **Comedies** (1,471) represent the top content categories.
5. **Rating Concentration:** Mature content (`TV-MA` and `R`) constitutes **>46%** of total listings.
6. **Duration Statistics:** Movie runtimes follow a normal distribution centered at a median of **98.0 minutes** (mean: 99.3 min). Conversely, **66.7%** of TV Shows feature only 1 season.
7. **Addition Seasonality:** Content additions peak during Q4 and Q1 (October, December, January).
8. **Inferential Tests:**
   - **Chi-Square Test (Type vs Target Audience):** $\chi^2 = 99.71$, $p = 1.80 \times 10^{-21}$ (Significant difference in audience targeting).
   - **ANOVA Test (Movie Duration across Top 5 Genres):** $F = 359.11$, $p = 3.92 \times 10^{-268}$ (Significant runtime variance across genres).

---

## 📄 Final Deliverables
- **Week 1 Report:** `reports/Yuva_Internship_Week1_Report.docx`
- **Week 2 Report:** `reports/Week2_EDA_Visualization_Report.docx`
- **Week 1 Notebook:** `notebooks/netflix_data_analysis.ipynb`
- **Week 2 Notebook:** `notebooks/week2_eda_visualization.ipynb`
- **Cleaned Dataset:** `dataset/processed/netflix_cleaned.csv`
- **Processed Dataset:** `dataset/processed/netflix_processed.csv`
- **Visualizations Directory:** `visualizations/week2/` (12 PNG Figures)

---

## 📜 Dataset Licensing & Acknowledgments
- **Dataset Author:** Shivam Bansal (Kaggle)
- **Dataset Source:** [Kaggle - Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)
- **Licensing:** Public Domain CC0 / Educational use.
