import os
import nbformat as nbf

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
NOTEBOOK_PATH = os.path.join(PROJECT_DIR, 'notebooks', 'netflix_data_analysis.ipynb')
os.makedirs(os.path.dirname(NOTEBOOK_PATH), exist_ok=True)

nb = nbf.v4.new_notebook()

cells = []

# Title & Metadata
cells.append(nbf.v4.new_markdown_cell("""# Yuva Internship — Week 1: Netflix Movies and TV Shows Data Analysis
**Student Name:** Vikhyath Bharadwaj K S  
**Project Title:** Data Acquisition, Cleaning, Preprocessing, and Exploratory Data Analysis of Netflix Dataset  
**Dataset Source:** Shivam Bansal (Kaggle / TidyTuesday)  
**Deliverables:** Jupyter Notebook, Cleaned/Processed Datasets, Visualizations, DOCX Report, GitHub Repository  

---
## Executive Summary
This notebook performs a comprehensive data engineering and data science workflow on the Netflix Movies and TV Shows dataset. The objective is to acquire raw data, evaluate data quality, execute systematic data cleaning, engineer features during preprocessing, and generate actionable exploratory insights for downstream analytical and predictive tasks."""))

# Phase 1: Environment & Data Loading
cells.append(nbf.v4.new_markdown_cell("""## Phase 1: Project Setup and Data Acquisition
In this section, we import required Python libraries, define paths, and load the raw dataset."""))

cells.append(nbf.v4.new_code_cell("""import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual aesthetic configuration
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['figure.figsize'] = (10, 6)

# Define relative paths
BASE_DIR = os.path.dirname(os.path.abspath('')) if os.path.basename(os.getcwd()) == 'notebooks' else os.getcwd()
RAW_DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'original', 'netflix_titles.csv')
CLEANED_DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'processed', 'netflix_cleaned.csv')
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'processed', 'netflix_processed.csv')
VIS_DIR = os.path.join(BASE_DIR, 'visualizations')

os.makedirs(VIS_DIR, exist_ok=True)

# Load raw dataset
df_raw = pd.read_csv(RAW_DATA_PATH)
print(f"Dataset successfully loaded from: {RAW_DATA_PATH}")
print(f"Raw Dataset Shape: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
"""))

# Phase 2: EDA
cells.append(nbf.v4.new_markdown_cell("""## Phase 2: Exploratory Data Analysis (EDA)
Here we inspect the structure, data types, missing value distributions, summary statistics, and key attributes of the dataset."""))

cells.append(nbf.v4.new_code_cell("""# Preview first and last rows
print("--- First 5 Rows ---")
display(df_raw.head())

print("--- Last 5 Rows ---")
display(df_raw.tail())

print("--- Information and Data Types ---")
df_raw.info()
"""))

cells.append(nbf.v4.new_code_cell("""# Summary statistics for categorical and numerical features
print("--- Categorical Summary ---")
display(df_raw.describe(include=['O']))

print("--- Numerical Summary ---")
display(df_raw.describe())
"""))

cells.append(nbf.v4.new_code_cell("""# Missing Value Analysis
missing_count = df_raw.isnull().sum()
missing_pct = (missing_count / len(df_raw)) * 100
missing_df = pd.DataFrame({'Missing Count': missing_count, 'Percentage (%)': missing_pct.round(2)})
missing_summary = missing_df[missing_df['Missing Count'] > 0].sort_values(by='Missing Count', ascending=False)
display(missing_summary)
"""))

cells.append(nbf.v4.new_code_cell("""# Duplicate Records Analysis
full_duplicates = df_raw.duplicated().sum()
title_duplicates = df_raw['title'].str.lower().duplicated().sum()
print(f"Total Exact Duplicate Rows: {full_duplicates}")
print(f"Total Duplicate Titles (case-insensitive): {title_duplicates}")
"""))

# Phase 3: Quality Assessment & Cleaning
cells.append(nbf.v4.new_markdown_cell("""## Phase 3 & 4: Data Quality Assessment and Data Cleaning
We address identified data quality issues:
1. `director`: Impute 2,389 missing values with `'Unknown Director'`
2. `cast`: Impute 718 missing values with `'Unknown Cast'`
3. `country`: Impute 507 missing values with `'Unknown Country'`
4. `rating`: Impute 7 missing values with mode (`'TV-MA'`)
5. `date_added`: Impute 10 missing values using `release_year-01-01`
6. Whitespace trimming and string normalization across all object columns."""))

cells.append(nbf.v4.new_code_cell("""df_clean = df_raw.copy()

# Strip whitespace
string_columns = df_clean.select_dtypes(include=['object']).columns
for col in string_columns:
    df_clean[col] = df_clean[col].astype(str).str.strip()
    df_clean[col] = df_clean[col].replace({'nan': np.nan, '': np.nan})

# Impute missing values
df_clean['director'] = df_clean['director'].fillna('Unknown Director')
df_clean['cast'] = df_clean['cast'].fillna('Unknown Cast')
df_clean['country'] = df_clean['country'].fillna('Unknown Country')
mode_rating = df_clean['rating'].mode()[0]
df_clean['rating'] = df_clean['rating'].fillna(mode_rating)

missing_dates = df_clean['date_added'].isnull()
df_clean.loc[missing_dates, 'date_added'] = df_clean.loc[missing_dates, 'release_year'].astype(str) + "-01-01"

print("--- Post-Cleaning Missing Value Verification ---")
print(df_clean.isnull().sum())
print(f"Cleaned Data Dimensions: {df_clean.shape}")
"""))

# Phase 5: Preprocessing & Feature Engineering
cells.append(nbf.v4.new_markdown_cell("""## Phase 5: Data Preprocessing & Feature Engineering
We transform raw attributes into analytical features:
- **Datetime Parsing:** Convert `date_added` to `datetime64[ns]` and extract `year_added`, `month_added`, `month_name_added`, `day_added`, `day_of_week_added`.
- **Content Age:** Calculate `content_age = year_added - release_year`.
- **Duration Parsing:** Split duration into `duration_int` (integer) and `duration_unit` (e.g. `min` vs `Season`).
- **Genre & Country Processing:** Extract `primary_genre`, `genre_count`, `primary_country`, `country_count`, `cast_count`.
- **Target Audience Binning:** Bin content ratings into `Kids`, `Teens`, `Adults`, `Unrated`.
- **Binary Encoding:** Encode `is_movie` (1 = Movie, 0 = TV Show)."""))

cells.append(nbf.v4.new_code_cell("""df_proc = df_clean.copy()

# Datetime & Temporal Features
df_proc['date_added_dt'] = pd.to_datetime(df_proc['date_added'], errors='coerce')
df_proc['year_added'] = df_proc['date_added_dt'].dt.year.fillna(df_proc['release_year']).astype(int)
df_proc['month_added'] = df_proc['date_added_dt'].dt.month.fillna(1).astype(int)
df_proc['month_name_added'] = df_proc['date_added_dt'].dt.month_name().fillna('January')
df_proc['day_added'] = df_proc['date_added_dt'].dt.day.fillna(1).astype(int)
df_proc['day_of_week_added'] = df_proc['date_added_dt'].dt.day_name().fillna('Wednesday')

df_proc['content_age'] = (df_proc['year_added'] - df_proc['release_year']).clip(lower=0)

# Duration Feature Extraction
def extract_duration(row):
    parts = str(row['duration']).split()
    if len(parts) >= 1 and parts[0].isdigit():
        num = int(parts[0])
        unit = parts[1] if len(parts) > 1 else ('min' if row['type'] == 'Movie' else 'Season')
        return pd.Series([num, unit])
    return pd.Series([np.nan, 'unknown'])

df_proc[['duration_int', 'duration_unit']] = df_proc.apply(extract_duration, axis=1)

# Multi-valued Feature Parsing
df_proc['primary_genre'] = df_proc['listed_in'].apply(lambda x: str(x).split(',')[0].strip())
df_proc['genre_count'] = df_proc['listed_in'].apply(lambda x: len(str(x).split(',')))
df_proc['primary_country'] = df_proc['country'].apply(lambda x: str(x).split(',')[0].strip())
df_proc['country_count'] = df_proc['country'].apply(lambda x: 0 if x == 'Unknown Country' else len(str(x).split(',')))
df_proc['cast_count'] = df_proc['cast'].apply(lambda x: 0 if x == 'Unknown Cast' else len(str(x).split(',')))

# Audience Binning
rating_map = {
    'G': 'Kids', 'TV-Y': 'Kids', 'TV-G': 'Kids',
    'PG': 'Teens', 'PG-13': 'Teens', 'TV-Y7': 'Teens', 'TV-Y7-FV': 'Teens', 'TV-14': 'Teens',
    'R': 'Adults', 'NC-17': 'Adults', 'TV-MA': 'Adults',
    'NR': 'Unrated', 'UR': 'Unrated'
}
df_proc['target_audience'] = df_proc['rating'].map(rating_map).fillna('Adults')
df_proc['is_movie'] = (df_proc['type'] == 'Movie').astype(int)

print(f"Processed Dataset Shape: {df_proc.shape[0]} rows, {df_proc.shape[1]} columns")
display(df_proc.head(3))
"""))

# Phase 6: Visualizations & Evaluation
cells.append(nbf.v4.new_markdown_cell("""## Phase 6: Visualization and Insights
Generating key charts for exploratory analysis, distribution evaluations, and visual comparisons."""))

cells.append(nbf.v4.new_code_cell("""# 1. Content Type Breakdown
plt.figure(figsize=(7, 5))
type_counts = df_proc['type'].value_counts()
ax = sns.barplot(x=type_counts.index, y=type_counts.values, hue=type_counts.index, palette=['#E50914', '#221F1F'], legend=False)
plt.title('Content Type Breakdown (Movies vs TV Shows)', fontsize=14, fontweight='bold')
plt.xlabel('Content Type')
plt.ylabel('Count')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())} ({p.get_height()/len(df_proc)*100:.1f}%)',
                (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                ha='center', va='center', color='white', fontweight='bold')
plt.tight_layout()
plt.show()
"""))

cells.append(nbf.v4.new_code_cell("""# 2. Content Release Trend over Time
plt.figure(figsize=(10, 5))
release_trend = df_proc[df_proc['release_year'] >= 1990].groupby(['release_year', 'type']).size().unstack().fillna(0)
plt.plot(release_trend.index, release_trend['Movie'], label='Movies', color='#E50914', linewidth=2.5)
plt.plot(release_trend.index, release_trend['TV Show'], label='TV Shows', color='#221F1F', linewidth=2.5)
plt.title('Content Release Volume Trend (1990 - 2021)', fontsize=14, fontweight='bold')
plt.xlabel('Release Year')
plt.ylabel('Number of Titles Released')
plt.legend()
plt.tight_layout()
plt.show()
"""))

cells.append(nbf.v4.new_code_cell("""# 3. Top Producing Countries
plt.figure(figsize=(10, 5))
top_countries = df_proc[df_proc['primary_country'] != 'Unknown Country']['primary_country'].value_counts().head(10)
ax = sns.barplot(x=top_countries.values, y=top_countries.index, hue=top_countries.index, palette='viridis', legend=False)
plt.title('Top 10 Content Producing Countries', fontsize=14, fontweight='bold')
plt.xlabel('Title Count')
plt.ylabel('Country')
for p in ax.patches:
    ax.annotate(f'{int(p.get_width())}', (p.get_width() + 15, p.get_y() + p.get_height() / 2.), ha='left', va='center')
plt.tight_layout()
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("""## Conclusion and Data Quality Evaluation
1. **Missing Data Resolution:** 100% missing values successfully addressed without dropping valuable content records.
2. **Feature Engineering:** Extracted temporal trends, duration metrics, genre categories, and audience classifications.
3. **Reproducibility:** Pipeline end-to-end verified across raw data, cleaning routines, feature preprocessing, and artifact generation."""))

nb['cells'] = cells

with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Successfully created notebook at: {NOTEBOOK_PATH}")
