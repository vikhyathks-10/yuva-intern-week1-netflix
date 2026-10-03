import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
CLEANED_DATA_PATH = os.path.join(PROJECT_DIR, 'dataset', 'processed', 'netflix_cleaned.csv')
PROCESSED_DATA_PATH = os.path.join(PROJECT_DIR, 'dataset', 'processed', 'netflix_processed.csv')
VIS_DIR = os.path.join(PROJECT_DIR, 'visualizations')

def preprocess_data():
    df = pd.read_csv(CLEANED_DATA_PATH)
    print(f"Loaded Cleaned Dataset Shape: {df.shape}")

    # 1. Datetime conversion and Feature Extraction
    df['date_added_dt'] = pd.to_datetime(df['date_added'], errors='coerce')
    
    df['year_added'] = df['date_added_dt'].dt.year.astype('Int64')
    df['month_added'] = df['date_added_dt'].dt.month.astype('Int64')
    df['month_name_added'] = df['date_added_dt'].dt.month_name()
    df['day_added'] = df['date_added_dt'].dt.day.astype('Int64')
    df['day_of_week_added'] = df['date_added_dt'].dt.day_name()
    
    # Fill any remaining date extraction NaNs with release year default
    df['year_added'] = df['year_added'].fillna(df['release_year']).astype(int)
    df['month_added'] = df['month_added'].fillna(1).astype(int)
    df['month_name_added'] = df['month_name_added'].fillna('January')
    df['day_added'] = df['day_added'].fillna(1).astype(int)
    df['day_of_week_added'] = df['day_of_week_added'].fillna('Wednesday')

    # Content Age feature (Years between release and addition to Netflix)
    df['content_age'] = df['year_added'] - df['release_year']
    # Correct any negative content age artifacts (if release_year > year_added due to date entry error)
    df['content_age'] = df['content_age'].apply(lambda x: max(0, x))

    # 2. Duration Parsing
    def parse_duration(row):
        val = str(row['duration'])
        parts = val.split()
        if len(parts) >= 1 and parts[0].isdigit():
            num = int(parts[0])
            unit = parts[1] if len(parts) > 1 else ('min' if row['type'] == 'Movie' else 'Season')
            return pd.Series([num, unit])
        return pd.Series([np.nan, 'unknown'])

    df[['duration_int', 'duration_unit']] = df.apply(parse_duration, axis=1)

    # 3. Genre & Country Feature Extraction
    df['primary_genre'] = df['listed_in'].apply(lambda x: str(x).split(',')[0].strip())
    df['genre_count'] = df['listed_in'].apply(lambda x: len(str(x).split(',')))
    
    df['primary_country'] = df['country'].apply(lambda x: str(x).split(',')[0].strip())
    df['country_count'] = df['country'].apply(lambda x: 0 if x == 'Unknown Country' else len(str(x).split(',')))
    
    df['cast_count'] = df['cast'].apply(lambda x: 0 if x == 'Unknown Cast' else len(str(x).split(',')))

    # 4. Audience Target Binning
    rating_map = {
        'G': 'Kids', 'TV-Y': 'Kids', 'TV-G': 'Kids',
        'PG': 'Teens', 'PG-13': 'Teens', 'TV-Y7': 'Teens', 'TV-Y7-FV': 'Teens', 'TV-14': 'Teens',
        'R': 'Adults', 'NC-17': 'Adults', 'TV-MA': 'Adults',
        'NR': 'Unrated', 'UR': 'Unrated'
    }
    df['target_audience'] = df['rating'].map(rating_map).fillna('Adults')

    # 5. Type Binary Encoding
    df['is_movie'] = (df['type'] == 'Movie').astype(int)

    # Save final processed dataset
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Processed Dataset Saved. Shape: {df.shape[0]} rows, {df.shape[1]} columns")

    # Generate Preprocessing Feature Visualizations

    # Chart 07: Addition Month Seasonality
    plt.figure(figsize=(10, 5))
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_counts = df['month_name_added'].value_counts().reindex(month_order)
    ax = sns.barplot(x=monthly_counts.index, y=monthly_counts.values, palette='plasma')
    plt.title('Content Addition Seasonality by Month', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Month Added', fontsize=12)
    plt.ylabel('Number of Titles Added', fontsize=12)
    plt.xticks(rotation=45)
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height() + 15),
                    ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, '07_addition_month_seasonality.png'), dpi=300)
    plt.close()

    # Chart 08: Content Age Distribution (Movie vs TV Show)
    plt.figure(figsize=(10, 5))
    sns.boxplot(x='type', y='content_age', data=df, palette=['#E50914', '#221F1F'])
    plt.title('Content Age Upon Addition to Netflix (Years)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Content Type', fontsize=12)
    plt.ylabel('Content Age (Years)', fontsize=12)
    plt.ylim(0, 50)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, '08_content_age_distribution.png'), dpi=300)
    plt.close()

    # Chart 09: Top Primary Genres
    plt.figure(figsize=(10, 6))
    top_genres = df['primary_genre'].value_counts().head(12)
    ax = sns.barplot(x=top_genres.values, y=top_genres.index, palette='magma')
    plt.title('Top 12 Primary Genres on Netflix', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Number of Titles', fontsize=12)
    plt.ylabel('Primary Genre', fontsize=12)
    for p in ax.patches:
        ax.annotate(f'{int(p.get_width())}', (p.get_width() + 15, p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, '09_top_primary_genres.png'), dpi=300)
    plt.close()

    # Chart 10: Target Audience Distribution
    plt.figure(figsize=(8, 5))
    audience_counts = df['target_audience'].value_counts()
    ax = sns.barplot(x=audience_counts.index, y=audience_counts.values, palette='Set2')
    plt.title('Target Audience Classification', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Audience Group', fontsize=12)
    plt.ylabel('Title Count', fontsize=12)
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}\n({p.get_height()/len(df)*100:.1f}%)', 
                    (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                    ha='center', va='center', fontsize=11, color='black', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, '10_target_audience_distribution.png'), dpi=300)
    plt.close()

    # Chart 11: Movie Duration Distribution (in Minutes)
    plt.figure(figsize=(10, 5))
    movie_durations = df[df['type'] == 'Movie']['duration_int'].dropna()
    sns.histplot(movie_durations, bins=30, kde=True, color='#E50914')
    plt.axvline(movie_durations.median(), color='black', linestyle='--', label=f'Median: {movie_durations.median():.0f} min')
    plt.title('Distribution of Movie Durations (Minutes)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Duration (Minutes)', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, '11_movie_duration_distribution.png'), dpi=300)
    plt.close()

    print("Preprocessing completed successfully!")

if __name__ == '__main__':
    preprocess_data()
