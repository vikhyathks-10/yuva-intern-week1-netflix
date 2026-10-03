import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for visualizations
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
ORIGINAL_DATA_PATH = os.path.join(PROJECT_DIR, 'dataset', 'original', 'netflix_titles.csv')
VIS_DIR = os.path.join(PROJECT_DIR, 'visualizations')
os.makedirs(VIS_DIR, exist_ok=True)

def explore_data():
    df = pd.read_csv(ORIGINAL_DATA_PATH)
    print("=== DATASET OVERVIEW ===")
    print(f"Dimensions: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\n--- Columns and Data Types ---")
    print(df.dtypes)
    
    print("\n--- First 5 Rows ---")
    print(df.head())
    
    print("\n--- Last 5 Rows ---")
    print(df.tail())
    
    print("\n--- Missing Values ---")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    missing_df = pd.DataFrame({'Missing Count': missing, 'Percentage (%)': missing_pct.round(2)})
    print(missing_df[missing_df['Missing Count'] > 0])
    
    print("\n--- Duplicate Rows ---")
    full_dups = df.duplicated().sum()
    title_dups = df['title'].str.lower().duplicated().sum()
    print(f"Full row duplicates: {full_dups}")
    print(f"Duplicate titles (case-insensitive): {title_dups}")
    
    print("\n--- Content Type Distribution ---")
    type_counts = df['type'].value_counts()
    print(type_counts)
    print(df['type'].value_counts(normalize=True) * 100)

    # 1. Type Distribution Chart
    plt.figure(figsize=(7, 5))
    ax = sns.barplot(x=type_counts.index, y=type_counts.values, palette=['#E50914', '#221F1F'])
    plt.title('Distribution of Content Type (Movies vs TV Shows)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Content Type', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}\n({p.get_height()/len(df)*100:.1f}%)', 
                    (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                    ha='center', va='center', fontsize=11, color='white', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, '01_content_type_distribution.png'), dpi=300)
    plt.close()

    # 2. Release Year Distribution
    plt.figure(figsize=(10, 5))
    sns.histplot(df['release_year'], bins=30, kde=True, color='#E50914')
    plt.title('Distribution of Content by Release Year', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Release Year', fontsize=12)
    plt.ylabel('Number of Titles', fontsize=12)
    plt.xlim(1940, 2022)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, '02_release_year_distribution.png'), dpi=300)
    plt.close()

    # 3. Missing Values Chart
    plt.figure(figsize=(9, 5))
    missing_active = missing_df[missing_df['Missing Count'] > 0].sort_values(by='Missing Count', ascending=False)
    ax = sns.barplot(x=missing_active['Missing Count'], y=missing_active.index, palette='Reds_r')
    plt.title('Missing Values by Feature (Original Dataset)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Missing Count', fontsize=12)
    plt.ylabel('Feature', fontsize=12)
    for p in ax.patches:
        width = p.get_width()
        pct = (width / len(df)) * 100
        ax.annotate(f'{int(width)} ({pct:.1f}%)', 
                    (width + 50, p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, '03_missing_values_original.png'), dpi=300)
    plt.close()

    # 4. Top 10 Countries
    plt.figure(figsize=(10, 5))
    # Handling multiple countries per row for accurate country count
    top_countries = df['country'].dropna().str.split(', ').explode().value_counts().head(10)
    ax = sns.barplot(x=top_countries.values, y=top_countries.index, palette='viridis')
    plt.title('Top 10 Content Producing Countries', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Number of Titles', fontsize=12)
    plt.ylabel('Country', fontsize=12)
    for p in ax.patches:
        ax.annotate(f'{int(p.get_width())}', (p.get_width() + 20, p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, '04_top_countries.png'), dpi=300)
    plt.close()

    # 5. Top Ratings
    plt.figure(figsize=(10, 5))
    rating_counts = df['rating'].value_counts().head(10)
    ax = sns.barplot(x=rating_counts.index, y=rating_counts.values, palette='Blues_r')
    plt.title('Top Content Ratings Distribution', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Rating Code', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.xticks(rotation=45)
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height() + 30),
                    ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, '05_ratings_distribution.png'), dpi=300)
    plt.close()

    print("Exploration complete. Initial visualizations saved to:", VIS_DIR)
    return df

if __name__ == '__main__':
    explore_data()
