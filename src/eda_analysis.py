import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

warnings.filterwarnings('ignore')

# Set style aesthetics
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
CLEANED_DATA_PATH = os.path.join(PROJECT_DIR, 'dataset', 'processed', 'netflix_cleaned.csv')
PROCESSED_DATA_PATH = os.path.join(PROJECT_DIR, 'dataset', 'processed', 'netflix_processed.csv')
VIS_DIR = os.path.join(PROJECT_DIR, 'visualizations', 'week2')
os.makedirs(VIS_DIR, exist_ok=True)

def run_eda_analysis():
    print("=" * 60)
    print("STARTING WEEK 2 EXPLORATORY DATA ANALYSIS (EDA)")
    print("=" * 60)
    
    # 1. Load Data
    df_clean = pd.read_csv(CLEANED_DATA_PATH)
    df_proc = pd.read_csv(PROCESSED_DATA_PATH)
    print(f"Loaded Cleaned Dataset Shape: {df_clean.shape}")
    print(f"Loaded Processed Dataset Shape: {df_proc.shape}")

    # Ensure datetime conversion for date_added
    df_proc['date_added_dt'] = pd.to_datetime(df_proc['date_added'], errors='coerce')
    
    results = {}

    # -------------------------------------------------------------
    # A. CONTENT TYPE ANALYSIS
    # -------------------------------------------------------------
    type_counts = df_proc['type'].value_counts()
    type_pct = df_proc['type'].value_counts(normalize=True) * 100
    results['content_type'] = pd.DataFrame({
        'Count': type_counts,
        'Percentage (%)': type_pct.round(2)
    })
    print("\n--- A. Content Type Breakdown ---")
    print(results['content_type'])

    # Chart 1: Content Type Distribution (Pie + Bar Hybrid)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    colors = ['#E50914', '#221F1F']
    
    # Donut Chart
    wedges, texts, autotexts = ax1.pie(
        type_counts, labels=type_counts.index, autopct='%1.1f%%',
        startangle=90, colors=colors, explode=(0.05, 0),
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
        textprops=dict(fontsize=12, fontweight='bold')
    )
    for autotext in autotexts:
        autotext.set_color('white')
    ax1.set_title('Content Type Proportion', fontsize=14, fontweight='bold', pad=15)

    # Bar Chart
    bars = ax2.bar(type_counts.index, type_counts.values, color=colors, width=0.5, edgecolor='black', alpha=0.85)
    ax2.set_ylabel('Number of Titles', fontsize=12)
    ax2.set_title('Content Count by Type', fontsize=14, fontweight='bold', pad=15)
    ax2.set_ylim(0, max(type_counts.values) * 1.15)
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'{height:,}\n({height/len(df_proc)*100:.1f}%)',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_01_content_type_distribution.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # B. RELEASE YEAR ANALYSIS
    # -------------------------------------------------------------
    rel_year_summary = df_proc['release_year'].describe()
    results['release_year_stats'] = rel_year_summary
    print("\n--- B. Release Year Descriptive Statistics ---")
    print(rel_year_summary)

    # Group by release year and type
    year_type = df_proc.groupby(['release_year', 'type']).size().unstack(fill_value=0)
    
    # Chart 2: Release Year Trends
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(year_type.index, year_type['Movie'], label='Movies', color='#E50914', linewidth=2.5)
    ax.plot(year_type.index, year_type['TV Show'], label='TV Shows', color='#0080FF', linewidth=2.5)
    ax.set_title('Evolution of Netflix Content Release Years (1925 - 2021)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Release Year', fontsize=12)
    ax.set_ylabel('Number of Titles Released', fontsize=12)
    ax.set_xlim(1940, 2021)
    ax.legend(fontsize=12, loc='upper left')
    
    # Annotate peak
    peak_movie_year = year_type['Movie'].idxmax()
    peak_movie_val = year_type['Movie'].max()
    ax.annotate(f'Movie Peak: {peak_movie_year} ({peak_movie_val})',
                xy=(peak_movie_year, peak_movie_val), xytext=(peak_movie_year - 20, peak_movie_val + 30),
                arrowprops=dict(facecolor='#E50914', shrink=0.05, width=1.5, headwidth=8),
                fontsize=10, fontweight='bold', color='#E50914')

    peak_tv_year = year_type['TV Show'].idxmax()
    peak_tv_val = year_type['TV Show'].max()
    ax.annotate(f'TV Show Peak: {peak_tv_year} ({peak_tv_val})',
                xy=(peak_tv_year, peak_tv_val), xytext=(peak_tv_year - 20, peak_tv_val + 50),
                arrowprops=dict(facecolor='#0080FF', shrink=0.05, width=1.5, headwidth=8),
                fontsize=10, fontweight='bold', color='#0080FF')

    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_02_release_year_trends.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # C. COUNTRY ANALYSIS (Unnested/Exploded)
    # -------------------------------------------------------------
    country_series = df_proc[df_proc['country'] != 'Unknown Country']['country'].dropna()
    exploded_countries = country_series.apply(lambda x: [c.strip() for c in str(x).split(',')]).explode()
    top_15_countries = exploded_countries.value_counts().head(15)
    
    results['top_countries'] = top_15_countries
    print("\n--- C. Top 15 Content-Producing Countries (Unnested) ---")
    print(top_15_countries)

    # Chart 3: Top Contributing Countries Bar Chart
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(x=top_15_countries.values, y=top_15_countries.index, hue=top_15_countries.index, palette='viridis', legend=False, ax=ax)
    ax.set_title('Top 15 Content-Producing Countries (Accounting for Multi-Country Co-Productions)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Total Number of Titles Produced / Co-Produced', fontsize=12)
    ax.set_ylabel('Country', fontsize=12)
    for p in ax.patches:
        ax.annotate(f'{int(p.get_width()):,}', (p.get_width() + 30, p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', fontsize=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_03_top_contributing_countries.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # D. GENRE ANALYSIS (Unnested/Exploded)
    # -------------------------------------------------------------
    genre_series = df_proc['listed_in'].apply(lambda x: [g.strip() for g in str(x).split(',')]).explode()
    top_15_genres = genre_series.value_counts().head(15)
    results['top_genres'] = top_15_genres
    print("\n--- D. Top 15 Genres (Unnested) ---")
    print(top_15_genres)

    # Chart 4: Top Genres Bar Chart
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(x=top_15_genres.values, y=top_15_genres.index, hue=top_15_genres.index, palette='rocket', legend=False, ax=ax)
    ax.set_title('Top 15 Listed Genres across Entire Netflix Catalog', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Total Occurrences across Titles', fontsize=12)
    ax.set_ylabel('Genre', fontsize=12)
    for p in ax.patches:
        ax.annotate(f'{int(p.get_width()):,}', (p.get_width() + 20, p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', fontsize=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_04_top_listed_genres.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # E. RATING ANALYSIS
    # -------------------------------------------------------------
    rating_type = pd.crosstab(df_proc['rating'], df_proc['type'])
    rating_order = df_proc['rating'].value_counts().index
    rating_type = rating_type.loc[rating_order]
    results['rating_type'] = rating_type
    print("\n--- E. Rating Distribution by Content Type ---")
    print(rating_type)

    # Chart 5: Content Ratings by Type
    fig, ax = plt.subplots(figsize=(12, 6))
    rating_type.plot(kind='bar', color=['#E50914', '#221F1F'], ax=ax, width=0.8, edgecolor='black', alpha=0.85)
    ax.set_title('Content Rating Distribution: Movies vs. TV Shows', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Content Rating', fontsize=12)
    ax.set_ylabel('Number of Titles', fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.legend(['Movies', 'TV Shows'], fontsize=11)
    for p in ax.patches:
        h = p.get_height()
        if h > 50:
            ax.annotate(f'{int(h)}', (p.get_x() + p.get_width() / 2., h + 15),
                        ha='center', va='bottom', fontsize=8, rotation=90)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_05_content_ratings_by_type.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # F. DURATION ANALYSIS
    # -------------------------------------------------------------
    movie_durations = df_proc[df_proc['type'] == 'Movie']['duration_int'].dropna()
    movie_stats = {
        'Count': len(movie_durations),
        'Mean': movie_durations.mean(),
        'Std': movie_durations.std(),
        'Median': movie_durations.median(),
        'IQR': movie_durations.quantile(0.75) - movie_durations.quantile(0.25),
        'Min': movie_durations.min(),
        'Max': movie_durations.max(),
        'Skewness': movie_durations.skew(),
        'Kurtosis': movie_durations.kurtosis()
    }
    results['movie_stats'] = pd.Series(movie_stats)
    print("\n--- F. Movie Duration Statistical Summary ---")
    print(results['movie_stats'])

    tv_seasons = df_proc[df_proc['type'] == 'TV Show']['duration_int'].dropna()
    tv_season_counts = tv_seasons.value_counts().sort_index()
    results['tv_seasons'] = tv_season_counts
    print("\n--- TV Show Season Counts ---")
    print(tv_season_counts.head(10))

    # Chart 6: Movie Duration Histogram & KDE
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.histplot(movie_durations, bins=35, kde=True, color='#E50914', ax=ax, stat='density', alpha=0.6)
    ax.axvline(movie_durations.mean(), color='blue', linestyle='--', linewidth=2, label=f'Mean: {movie_durations.mean():.1f} min')
    ax.axvline(movie_durations.median(), color='black', linestyle='-', linewidth=2, label=f'Median: {movie_durations.median():.1f} min')
    ax.set_title('Distribution of Movie Durations on Netflix (Minutes)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Duration (Minutes)', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.legend(fontsize=11)
    
    # Annotate stats
    stats_text = (f"Count: {len(movie_durations):,}\n"
                  f"Mean: {movie_durations.mean():.1f} min\n"
                  f"Std Dev: {movie_durations.std():.1f} min\n"
                  f"Median: {movie_durations.median():.1f} min\n"
                  f"IQR: {movie_stats['IQR']:.1f} min\n"
                  f"Skewness: {movie_stats['Skewness']:.2f}")
    ax.text(0.75, 0.65, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='#ccc'))

    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_06_movie_duration_histogram.png'), dpi=300)
    plt.close()

    # Chart 7: TV Show Seasons Distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    season_df = tv_season_counts.reset_index()
    season_df.columns = ['Seasons', 'Count']
    bars = sns.barplot(x='Seasons', y='Count', data=season_df, hue='Seasons', palette='Blues_r', legend=False, ax=ax)
    ax.set_title('TV Show Season Count Distribution', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Number of Seasons', fontsize=12)
    ax.set_ylabel('Number of TV Shows', fontsize=12)
    for bar in bars.patches:
        h = bar.get_height()
        if h > 0:
            pct = (h / len(tv_seasons)) * 100
            ax.annotate(f'{int(h)}\n({pct:.1f}%)', (bar.get_x() + bar.get_width() / 2., h + 15),
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_ylim(0, max(season_df['Count']) * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_07_tv_show_seasons_distribution.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # G. DATE ADDED & SEASONALITY ANALYSIS
    # -------------------------------------------------------------
    df_valid_date = df_proc.dropna(subset=['date_added_dt']).copy()
    
    # Monthly additions matrix (Year vs Month)
    recent_years = df_valid_date[df_valid_date['year_added'] >= 2015]
    monthly_matrix = pd.crosstab(recent_years['year_added'], recent_years['month_name_added'])
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_matrix = monthly_matrix.reindex(columns=month_order)
    results['monthly_matrix'] = monthly_matrix

    # Chart 9: Monthly Addition Heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(monthly_matrix, annot=True, fmt='d', cmap='YlGnBu', cbar_kws={'label': 'Titles Added'}, ax=ax, linewidths=0.5)
    ax.set_title('Netflix Content Addition Heatmap by Year & Month (2015 - 2021)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Month Added', fontsize=12)
    ax.set_ylabel('Year Added', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_09_monthly_content_additions.png'), dpi=300)
    plt.close()

    # Chart 10: Content Age Lag Distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df_proc['content_age'], bins=40, kde=True, color='#2B8A3E', ax=ax)
    ax.axvline(df_proc['content_age'].median(), color='red', linestyle='--', linewidth=2, 
               label=f"Median Lag: {df_proc['content_age'].median():.0f} years")
    ax.axvline(df_proc['content_age'].mean(), color='blue', linestyle=':', linewidth=2, 
               label=f"Mean Lag: {df_proc['content_age'].mean():.1f} years")
    ax.set_title('Content Age Lag: Years Between Release & Netflix Addition', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Content Age Lag (Years)', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_xlim(0, 50)
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_10_content_age_lag_distribution.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # H. ADDITIONAL CROSS-ANALYSIS & STATISTICAL TESTS
    # -------------------------------------------------------------
    # 1. Top 12 Genres vs Type Heatmap
    df_genre_type = []
    for idx, row in df_proc.iterrows():
        genres = [g.strip() for g in str(row['listed_in']).split(',')]
        for g in genres:
            df_genre_type.append({'type': row['type'], 'genre': g})
    df_genre_exploded = pd.DataFrame(df_genre_type)
    top_12_g_names = df_genre_exploded['genre'].value_counts().head(12).index
    df_filtered_g = df_genre_exploded[df_genre_exploded['genre'].isin(top_12_g_names)]
    gt_ct = df_filtered_g.groupby(['genre', 'type']).size().unstack(fill_value=0).loc[top_12_g_names]
    
    # Chart 8: Genre vs Content Type Heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(gt_ct, annot=True, fmt='d', cmap='OrRd', linewidths=0.5, ax=ax)
    ax.set_title('Top 12 Listed Genres Distribution across Movies & TV Shows', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Content Type', fontsize=12)
    ax.set_ylabel('Genre', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_08_genre_content_type_heatmap.png'), dpi=300)
    plt.close()

    # 2. Movie Duration by Primary Genre (Boxplot)
    movies_df = df_proc[df_proc['type'] == 'Movie'].copy()
    top_8_movie_genres = movies_df['primary_genre'].value_counts().head(8).index
    movies_top_genres = movies_df[movies_df['primary_genre'].isin(top_8_movie_genres)]
    
    # Chart 11: Movie Duration by Primary Genre Boxplot
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='primary_genre', y='duration_int', data=movies_top_genres, hue='primary_genre', palette='Set2', legend=False, ax=ax)
    ax.set_title('Movie Duration Distribution across Top 8 Primary Movie Genres', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Primary Genre', fontsize=12)
    ax.set_ylabel('Duration (Minutes)', fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_11_movie_duration_by_genre_boxplot.png'), dpi=300)
    plt.close()

    # 3. Country vs Content Type Stacked Bar
    df_country_type = []
    for idx, row in df_proc[df_proc['country'] != 'Unknown Country'].iterrows():
        countries = [c.strip() for c in str(row['country']).split(',')]
        for c in countries:
            df_country_type.append({'type': row['type'], 'country': c})
    df_country_exploded = pd.DataFrame(df_country_type)
    top_10_c_names = df_country_exploded['country'].value_counts().head(10).index
    c_type_ct = df_country_exploded[df_country_exploded['country'].isin(top_10_c_names)].groupby(['country', 'type']).size().unstack(fill_value=0).loc[top_10_c_names]

    # Chart 12: Country Type Breakdown Stacked Bar
    fig, ax = plt.subplots(figsize=(11, 6))
    c_type_ct.plot(kind='bar', stacked=True, color=['#E50914', '#0080FF'], ax=ax, edgecolor='black', alpha=0.85)
    ax.set_title('Movie vs. TV Show Breakdown for Top 10 Producing Countries', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Country', fontsize=12)
    ax.set_ylabel('Number of Titles', fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.legend(['Movies', 'TV Shows'], fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'w2_12_country_type_breakdown.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # STATISTICAL HYPOTHESIS TESTING
    # -------------------------------------------------------------
    print("\n--- STATISTICAL TESTS ---")
    
    # 1. Chi-Square Test of Independence: Content Type vs Target Audience
    ct_aud = pd.crosstab(df_proc['type'], df_proc['target_audience'])
    chi2, p_val, dof, expected = stats.chi2_contingency(ct_aud)
    n = ct_aud.sum().sum()
    cramers_v = np.sqrt(chi2 / (n * (min(ct_aud.shape) - 1)))
    
    results['chi2_test'] = {
        'Chi2 Statistic': chi2,
        'p-value': p_val,
        'Degrees of Freedom': dof,
        "Cramer's V": cramers_v
    }
    print(f"Chi-Square Test (Type vs Target Audience): Chi2 = {chi2:.4f}, p = {p_val:.4e}, Cramer's V = {cramers_v:.4f}")

    # 2. ANOVA Test: Movie Duration across Top 5 Primary Movie Genres
    top_5_m_genres = movies_df['primary_genre'].value_counts().head(5).index
    genre_groups = [movies_df[movies_df['primary_genre'] == g]['duration_int'].dropna() for g in top_5_m_genres]
    f_stat, p_val_anova = stats.f_oneway(*genre_groups)
    kw_stat, p_val_kw = stats.kruskal(*genre_groups)
    
    results['anova_test'] = {
        'F-Statistic': f_stat,
        'p-value (ANOVA)': p_val_anova,
        'Kruskal-Wallis H': kw_stat,
        'p-value (Kruskal-Wallis)': p_val_kw
    }
    print(f"ANOVA Test (Movie Duration across Top 5 Genres): F = {f_stat:.4f}, p = {p_val_anova:.4e}")
    print(f"Kruskal-Wallis Test: H = {kw_stat:.4f}, p = {p_val_kw:.4e}")

    print("\n" + "=" * 60)
    print("ALL WEEK 2 VISUALIZATIONS & STATISTICAL ANALYSES COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    return results

if __name__ == '__main__':
    run_eda_analysis()
