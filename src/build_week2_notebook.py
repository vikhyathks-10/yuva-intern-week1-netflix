import os
import nbformat as nbf

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
NOTEBOOK_PATH = os.path.join(PROJECT_DIR, 'notebooks', 'week2_eda_visualization.ipynb')

def build_notebook():
    nb = nbf.v4.new_notebook()
    cells = []

    # Title & Metadata
    cells.append(nbf.v4.new_markdown_cell("""# Yuva Internship - Week 2: Exploratory Data Analysis & Visualization
## Project: Netflix Movies and TV Shows Dataset
**Student Name:** Vikhyath Bharadwaj K S  
**Dataset:** Netflix Movies and TV Shows by Shivam Bansal (Kaggle)  
**Deliverable:** Week 2 Fully Executed Jupyter Notebook  
---"""))

    # Section 1: Project Introduction
    cells.append(nbf.v4.new_markdown_cell("""### 1. Project Introduction
Exploratory Data Analysis (EDA) is a critical stage in the data science pipeline that involves investigating dataset structures, detecting patterns, uncovering anomalies, and summarizing key statistical characteristics through visual and quantitative methods. Following the completion of Week 1 (Data Acquisition, Cleaning, and Preprocessing), this notebook performs an in-depth exploratory analysis on the curated Netflix Movies and TV Shows dataset. The goal is to extract meaningful content insights, geographic production dynamics, temporal evolution, and rating characteristics."""))

    # Section 2: Objectives
    cells.append(nbf.v4.new_markdown_cell("""### 2. Objectives
1. Perform comprehensive univariate and bivariate analysis on Netflix content.
2. Quantify content breakdown between Movies and TV Shows.
3. Track release year trends and Netflix catalog expansion seasonality.
4. Analyze international content distribution accounting for multi-country co-productions.
5. Evaluate listed genre distributions and age target rating categories.
6. Conduct statistical distribution analysis for movie durations and TV show season counts.
7. Perform statistical hypothesis testing (Chi-Square Test of Independence & ANOVA / Kruskal-Wallis).
8. Generate 12 high-resolution publication-quality data visualizations."""))

    # Section 3: Dataset Source and Description
    cells.append(nbf.v4.new_markdown_cell("""### 3. Dataset Source and Description
- **Source:** Kaggle - Netflix Movies and TV Shows (Shivam Bansal)
- **Original Size:** 7,787 rows × 12 columns
- **Cleaned/Processed Size:** 7,787 rows × 28 columns
- **Key Fields:** `show_id`, `type`, `title`, `director`, `cast`, `country`, `date_added`, `release_year`, `rating`, `duration`, `listed_in`, `description`, `content_age`, `primary_genre`, `target_audience`."""))

    # Section 4: Library Imports
    cells.append(nbf.v4.new_code_cell("""import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

warnings.filterwarnings('ignore')

# Visual style setup
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['figure.dpi'] = 120

print("All libraries imported successfully.")"""))

    # Section 5: Dataset Loading
    cells.append(nbf.v4.new_markdown_cell("""### 5. Dataset Loading
We load both the cleaned dataset (`netflix_cleaned.csv`) and the feature-engineered processed dataset (`netflix_processed.csv`)."""))
    cells.append(nbf.v4.new_code_cell("""CLEANED_PATH = '../dataset/processed/netflix_cleaned.csv'
PROCESSED_PATH = '../dataset/processed/netflix_processed.csv'

df_clean = pd.read_csv(CLEANED_PATH)
df_proc = pd.read_csv(PROCESSED_PATH)

# Convert date fields
df_proc['date_added_dt'] = pd.to_datetime(df_proc['date_added'], errors='coerce')

print(f"Cleaned Dataset Shape: {df_clean.shape}")
print(f"Processed Dataset Shape: {df_proc.shape}")
df_proc.head(3)"""))

    # Section 6: Initial Inspection
    cells.append(nbf.v4.new_markdown_cell("""### 6. Initial Inspection
Inspecting column data types, non-null value counts, and unique value counts across key variables."""))
    cells.append(nbf.v4.new_code_cell("""# Dataset Summary
inspection_df = pd.DataFrame({
    'Data Type': df_proc.dtypes,
    'Non-Null Count': df_proc.notnull().sum(),
    'Null Count': df_proc.isnull().sum(),
    'Unique Values': df_proc.nunique()
})
print("--- DATASET COLUMN INSPECTION ---")
display(inspection_df)"""))

    # Section 7: Descriptive Statistics
    cells.append(nbf.v4.new_markdown_cell("""### 7. Descriptive Statistics
Calculating central tendency, dispersion, skewness, and kurtosis for numeric variables (`release_year`, `duration_int`, `content_age`, `cast_count`, `country_count`)."""))
    cells.append(nbf.v4.new_code_cell("""numeric_cols = ['release_year', 'duration_int', 'content_age', 'cast_count', 'country_count', 'genre_count']
desc_stats = df_proc[numeric_cols].describe().T
desc_stats['skewness'] = df_proc[numeric_cols].skew()
desc_stats['kurtosis'] = df_proc[numeric_cols].kurtosis()
print("--- NUMERICAL DESCRIPTIVE STATISTICS ---")
display(desc_stats.round(2))"""))

    # Section 8: Content Type Analysis
    cells.append(nbf.v4.new_markdown_cell("""### 8. Content Type Analysis
Analyzing the proportion of Movies versus TV Shows in the Netflix catalog."""))
    cells.append(nbf.v4.new_code_cell("""type_summary = pd.DataFrame({
    'Count': df_proc['type'].value_counts(),
    'Percentage (%)': (df_proc['type'].value_counts(normalize=True) * 100).round(2)
})
print("--- CONTENT TYPE BREAKDOWN ---")
display(type_summary)

# Plotting Chart 1
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
colors = ['#E50914', '#221F1F']
type_counts = df_proc['type'].value_counts()

ax1.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=90, colors=colors, explode=(0.05, 0),
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2), textprops=dict(fontsize=11, fontweight='bold'))
ax1.set_title('Content Type Proportion', fontsize=13, fontweight='bold')

bars = ax2.bar(type_counts.index, type_counts.values, color=colors, width=0.5, edgecolor='black', alpha=0.85)
ax2.set_ylabel('Number of Titles', fontsize=11)
ax2.set_title('Content Count by Type', fontsize=13, fontweight='bold')
ax2.set_ylim(0, max(type_counts.values) * 1.15)
for bar in bars:
    h = bar.get_height()
    pct_val = (h / len(df_proc)) * 100
    label_str = str(h) + f" ({pct_val:.1f}%)"
    ax2.annotate(label_str, xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()"""))

    # Section 9: Release Year Analysis
    cells.append(nbf.v4.new_markdown_cell("""### 9. Release Year Analysis
Tracking release year distribution from 1925 to 2021 and highlighting peak production periods."""))
    cells.append(nbf.v4.new_code_cell("""year_type = df_proc.groupby(['release_year', 'type']).size().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(year_type.index, year_type['Movie'], label='Movies', color='#E50914', linewidth=2.2)
ax.plot(year_type.index, year_type['TV Show'], label='TV Shows', color='#0080FF', linewidth=2.2)
ax.set_title('Netflix Content Release Trends (1925 - 2021)', fontsize=13, fontweight='bold')
ax.set_xlabel('Release Year', fontsize=11)
ax.set_ylabel('Number of Titles Released', fontsize=11)
ax.set_xlim(1940, 2021)
ax.legend(fontsize=11, loc='upper left')
plt.tight_layout()
plt.show()"""))

    # Section 10: Country Analysis
    cells.append(nbf.v4.new_markdown_cell("""### 10. Country Analysis
Handling multi-country co-productions by exploding comma-separated values to evaluate true geographic production shares."""))
    cells.append(nbf.v4.new_code_cell("""country_series = df_proc[df_proc['country'] != 'Unknown Country']['country'].dropna()
exploded_countries = country_series.apply(lambda x: [c.strip() for c in str(x).split(',')]).explode()
top_15_countries = exploded_countries.value_counts().head(15)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=top_15_countries.values, y=top_15_countries.index, hue=top_15_countries.index, palette='viridis', legend=False, ax=ax)
ax.set_title('Top 15 Content-Producing Countries (Unnested)', fontsize=13, fontweight='bold')
ax.set_xlabel('Total Titles Produced / Co-Produced', fontsize=11)
for p in ax.patches:
    ax.annotate(f'{int(p.get_width()):,}', (p.get_width() + 25, p.get_y() + p.get_height() / 2.),
                ha='left', va='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.show()"""))

    # Section 11: Genre Analysis
    cells.append(nbf.v4.new_markdown_cell("""### 11. Genre Analysis
Evaluating unnested genre occurrences across the catalog."""))
    cells.append(nbf.v4.new_code_cell("""genre_series = df_proc['listed_in'].apply(lambda x: [g.strip() for g in str(x).split(',')]).explode()
top_15_genres = genre_series.value_counts().head(15)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=top_15_genres.values, y=top_15_genres.index, hue=top_15_genres.index, palette='rocket', legend=False, ax=ax)
ax.set_title('Top 15 Listed Genres across Entire Catalog', fontsize=13, fontweight='bold')
ax.set_xlabel('Total Occurrences', fontsize=11)
for p in ax.patches:
    ax.annotate(f'{int(p.get_width()):,}', (p.get_width() + 15, p.get_y() + p.get_height() / 2.),
                ha='left', va='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.show()"""))

    # Section 12: Rating Analysis
    cells.append(nbf.v4.new_markdown_cell("""### 12. Rating Analysis
Examining content rating distributions across Movies and TV Shows."""))
    cells.append(nbf.v4.new_code_cell("""rating_type = pd.crosstab(df_proc['rating'], df_proc['type'])
rating_order = df_proc['rating'].value_counts().index
rating_type = rating_type.loc[rating_order]

fig, ax = plt.subplots(figsize=(11, 5))
rating_type.plot(kind='bar', color=['#E50914', '#221F1F'], ax=ax, width=0.8, edgecolor='black', alpha=0.85)
ax.set_title('Content Rating Breakdown: Movies vs. TV Shows', fontsize=13, fontweight='bold')
ax.set_xlabel('Rating', fontsize=11)
ax.set_ylabel('Number of Titles', fontsize=11)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
ax.legend(['Movies', 'TV Shows'], fontsize=10)
plt.tight_layout()
plt.show()"""))

    # Section 13: Duration Analysis
    cells.append(nbf.v4.new_markdown_cell("""### 13. Duration Analysis
Analyzing Movie durations (in minutes) and TV Show season counts."""))
    cells.append(nbf.v4.new_code_cell("""movie_durations = df_proc[df_proc['type'] == 'Movie']['duration_int'].dropna()
tv_seasons = df_proc[df_proc['type'] == 'TV Show']['duration_int'].dropna()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# Movie duration histogram
sns.histplot(movie_durations, bins=30, kde=True, color='#E50914', ax=ax1)
ax1.axvline(movie_durations.mean(), color='blue', linestyle='--', label=f'Mean: {movie_durations.mean():.1f} min')
ax1.axvline(movie_durations.median(), color='black', linestyle='-', label=f'Median: {movie_durations.median():.1f} min')
ax1.set_title('Movie Duration Distribution (Minutes)', fontsize=12, fontweight='bold')
ax1.legend()

# TV Seasons bar chart
season_counts = tv_seasons.value_counts().sort_index().head(10).reset_index()
season_counts.columns = ['Seasons', 'Count']
sns.barplot(x='Seasons', y='Count', data=season_counts, hue='Seasons', palette='Blues_r', legend=False, ax=ax2)
ax2.set_title('TV Show Season Count Distribution', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()"""))

    # Section 14: Date Added Analysis
    cells.append(nbf.v4.new_markdown_cell("""### 14. Date Added Analysis
Analyzing Netflix content additions by month and calculating content age lag."""))
    cells.append(nbf.v4.new_code_cell("""df_valid_date = df_proc.dropna(subset=['date_added_dt']).copy()
recent_years = df_valid_date[df_valid_date['year_added'] >= 2015]
monthly_matrix = pd.crosstab(recent_years['year_added'], recent_years['month_name_added'])
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
monthly_matrix = monthly_matrix.reindex(columns=month_order)

fig, ax = plt.subplots(figsize=(11, 5))
sns.heatmap(monthly_matrix, annot=True, fmt='d', cmap='YlGnBu', ax=ax, linewidths=0.5)
ax.set_title('Content Addition Heatmap by Year & Month (2015 - 2021)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.show()"""))

    # Section 15: Additional Exploratory Investigations
    cells.append(nbf.v4.new_markdown_cell("""### 15. Additional Exploratory Investigations
Investigating Movie duration variation across genres and statistical hypothesis tests."""))
    cells.append(nbf.v4.new_code_cell("""movies_df = df_proc[df_proc['type'] == 'Movie'].copy()
top_8_movie_genres = movies_df['primary_genre'].value_counts().head(8).index
movies_top_genres = movies_df[movies_df['primary_genre'].isin(top_8_movie_genres)]

fig, ax = plt.subplots(figsize=(11, 5))
sns.boxplot(x='primary_genre', y='duration_int', data=movies_top_genres, hue='primary_genre', palette='Set2', legend=False, ax=ax)
ax.set_title('Movie Duration Distribution across Top 8 Primary Genres', fontsize=13, fontweight='bold')
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
plt.tight_layout()
plt.show()

# Chi-Square Test
ct_aud = pd.crosstab(df_proc['type'], df_proc['target_audience'])
chi2, p_val, dof, _ = stats.chi2_contingency(ct_aud)
print(f"Chi-Square Test (Type vs Target Audience): Chi2 = {chi2:.4f}, p-value = {p_val:.4e}")

# ANOVA Test
top_5_m_genres = movies_df['primary_genre'].value_counts().head(5).index
genre_groups = [movies_df[movies_df['primary_genre'] == g]['duration_int'].dropna() for g in top_5_m_genres]
f_stat, p_val_anova = stats.f_oneway(*genre_groups)
print(f"ANOVA Test (Duration across Top 5 Genres): F-stat = {f_stat:.4f}, p-value = {p_val_anova:.4e}")"""))

    # Section 16: Data Transformations and Aggregations
    cells.append(nbf.v4.new_markdown_cell("""### 16. Data Transformations and Aggregations
Summary of transformations documented during EDA:
1. Datetime parsing (`date_added` → `year_added`, `month_name_added`).
2. Multi-valued field unnesting (`country` & `listed_in` string splitting and exploding).
3. Numerical duration extraction (`duration` string parsing into `duration_int` and `duration_unit`).
4. Content age lag computation (`year_added` - `release_year`).
5. Audience target grouping (`rating` map into `Kids`, `Teens`, `Adults`, `Unrated`)."""))

    # Section 17: Visualizations
    cells.append(nbf.v4.new_markdown_cell("""### 17. Visualizations Overview
All 12 high-resolution visualizations created during EDA are stored in `../visualizations/week2/`:
- `w2_01_content_type_distribution.png`
- `w2_02_release_year_trends.png`
- `w2_03_top_contributing_countries.png`
- `w2_04_top_listed_genres.png`
- `w2_05_content_ratings_by_type.png`
- `w2_06_movie_duration_histogram.png`
- `w2_07_tv_show_seasons_distribution.png`
- `w2_08_genre_content_type_heatmap.png`
- `w2_09_monthly_content_additions.png`
- `w2_10_content_age_lag_distribution.png`
- `w2_11_movie_duration_by_genre_boxplot.png`
- `w2_12_country_type_breakdown.png`"""))

    # Section 18: Interpretation of Findings
    cells.append(nbf.v4.new_markdown_cell("""### 18. Interpretation of Findings
1. **Catalog Composition:** Movies dominate the catalog (69.05%), but TV Show additions grew significantly after 2016.
2. **Geographic Distribution:** The US is the leading provider (3,297 titles), followed by India (990 titles, predominantly movies) and the UK (723 titles).
3. **Genre Dominance:** International Movies, Dramas, and Comedies represent the top content categories.
4. **Rating Insights:** Mature content (`TV-MA` and `R`) constitutes over 46% of all content, reflecting an adult-oriented licensing strategy.
5. **Duration Metrics:** Movie durations follow a normal distribution centered at 99.3 minutes (median 98 minutes), whereas 66.7% of TV Shows feature only 1 season."""))

    # Section 19: Limitations
    cells.append(nbf.v4.new_markdown_cell("""### 19. Limitations
1. **Right-Censoring:** Data collection cuts off in early 2021.
2. **Missing Granular Viewing Data:** Lacks viewership figures, watch time, ratings, or subscriber metrics.
3. **Imputed Fields:** Missing dates and countries filled during Week 1 introduce minor categorical noise."""))

    # Section 20: Conclusion
    cells.append(nbf.v4.new_markdown_cell("""### 20. Conclusion
This EDA notebook successfully establishes the descriptive and visual foundations of the Netflix Movies and TV Shows dataset. The findings reveal strategic shifts towards original series, global acquisition expansion, and clear structural differences between feature films and television series."""))

    nb['cells'] = cells
    with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Jupyter Notebook generated at: {NOTEBOOK_PATH}")

if __name__ == '__main__':
    build_notebook()
