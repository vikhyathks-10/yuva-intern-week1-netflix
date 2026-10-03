import os
import pandas as pd

urls = [
    "https://raw.githubusercontent.com/jatin-code/Netflix-Movies-and-TV-Shows-Clustering/main/netflix_titles.csv",
    "https://raw.githubusercontent.com/datasets/netflix-shows/master/netflix_titles.csv",
    "https://raw.githubusercontent.com/Shivam-Bansal/Netflix-Movies-and-TV-Shows/master/netflix_titles.csv",
    "https://raw.githubusercontent.com/Subodh08-git/Netflix-Movies-and-TV-Shows-Data-Analysis/main/netflix_titles.csv",
    "https://raw.githubusercontent.com/Laxmi-Narayana-1/Netflix_Movies_and_TV_Shows_Analysis/main/netflix_titles.csv",
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-04-20/netflix_titles.csv"
]

ORIGINAL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'original', 'netflix_titles.csv')

for u in urls:
    try:
        df = pd.read_csv(u)
        print(f"Source {u} has shape {df.shape}")
        if df.shape[0] == 8807:
            print("Found 8807 row version! Overwriting original with latest Kaggle dataset release...")
            df.to_csv(ORIGINAL_PATH, index=False)
            break
    except Exception as e:
        pass
