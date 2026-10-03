import os
import urllib.request
import pandas as pd

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'original')
OUTPUT_FILE = os.path.join(DATASET_DIR, 'netflix_titles.csv')

# Reliable public sources for Shivam Bansal's Netflix dataset
URL_SOURCES = [
    "https://raw.githubusercontent.com/amankharwal/Website-data/master/netflix_titles.csv",
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-04-20/netflix_titles.csv"
]

def download_dataset():
    os.makedirs(DATASET_DIR, exist_ok=True)
    if os.path.exists(OUTPUT_FILE):
        print(f"Dataset already exists at: {OUTPUT_FILE}")
        df = pd.read_csv(OUTPUT_FILE)
        print(f"Loaded shape: {df.shape}")
        return df

    for url in URL_SOURCES:
        try:
            print(f"Attempting download from: {url}")
            df = pd.read_csv(url)
            if df is not None and not df.empty and df.shape[0] > 5000:
                df.to_csv(OUTPUT_FILE, index=False)
                print(f"Successfully downloaded and saved dataset to {OUTPUT_FILE}")
                print(f"Dataset dimensions: {df.shape[0]} rows, {df.shape[1]} columns")
                return df
        except Exception as e:
            print(f"Failed to download from {url}: {e}")

    raise RuntimeError("Could not download Netflix dataset from available public sources.")

if __name__ == '__main__':
    download_dataset()
