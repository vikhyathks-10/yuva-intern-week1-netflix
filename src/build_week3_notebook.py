import os
import nbformat as nbf

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
NOTEBOOK_PATH = os.path.join(PROJECT_DIR, "notebooks", "week3_clustering_analysis.ipynb")


def md(cells, text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(cells, text):
    cells.append(nbf.v4.new_code_cell(text))


def build_notebook():
    nb = nbf.v4.new_notebook()
    cells = []

    md(cells, """# Yuva Internship — Week 3: Unsupervised Learning and Clustering Analysis
## Project: Netflix Movies and TV Shows
**Student Name:** Vikhyath Bharadwaj K S
**Dataset:** Netflix Movies and TV Shows by Shivam Bansal (Kaggle)
**Deliverable:** Reproducible Week 3 Jupyter Notebook
**Random state:** 42

---""")

    md(cells, """### 1. Project Introduction
Unsupervised learning discovers structure in unlabelled data. Clustering partitions observations so that titles in the same group are more similar to each other, in the chosen feature space, than to titles in other groups.

This notebook groups **Netflix catalogue metadata** — not viewer behaviour or Netflix's internal recommender. Movies and TV Shows are analysed **separately** because movie runtime (minutes) and TV season counts are not equivalent measurements.

The work builds on the Week 1 cleaned/processed tables and the Week 2 exploratory findings.""")

    md(cells, """### 2. Objectives
1. Select interpretable catalogue features and exclude identifiers (`show_id`, `title`).
2. Encode mixed-type fields and scale numeric variables for distance-based clustering.
3. Fit K-Means over a candidate range of cluster counts.
4. Use the elbow method, silhouette scores, Davies–Bouldin, Calinski–Harabasz, size balance, and interpretability to choose K.
5. Characterise each cluster with actual computed statistics and descriptive labels.
6. Compare agglomerative hierarchical clustering (Ward, average, complete) on a documented sample.
7. Visualise clusters with PCA projections while stating the limits of 2D views.""")

    md(cells, """### 3. Dataset Source and Description
- **Source:** [Kaggle — Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows) (Shivam Bansal)
- **Processed table:** `dataset/processed/netflix_processed.csv` (7,787 titles × 28 columns from Week 1)
- **Movies:** 5,377 titles
- **TV Shows:** 2,410 titles
- **Limitations:** categorical/sparse fields (`listed_in`, `country`), imputed unknowns from Week 1, and no audience-consumption metrics.""")

    md(cells, """### 4. Library Imports""")
    code(cells, """import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.metrics import (
    silhouette_score, davies_bouldin_score, calinski_harabasz_score, adjusted_rand_score
)
from sklearn.preprocessing import RobustScaler, StandardScaler, MinMaxScaler
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

warnings.filterwarnings('ignore')
sys.path.append('../src')
from clustering import (
    RANDOM_STATE, N_INIT, K_RANGE, MOVIE_GENRES, TV_GENRES, HIER_SAMPLE_SIZE,
    load_processed, build_feature_matrix, scale_features, evaluate_kmeans,
    fit_kmeans, characterize, assign_movie_labels, assign_tv_labels,
    hierarchical_on_sample, choose_k, VIS_DIR, SCREEN_DIR, ensure_dirs
)

ensure_dirs()
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.dpi'] = 120
print('Libraries imported. Random state =', RANDOM_STATE)""")

    md(cells, """### 5. Dataset Loading
Load the Week 1 processed catalogue and confirm row counts, types, and remaining missingness. Identifiers are kept for later interpretation only.""")
    code(cells, """df = load_processed()
print('Processed shape:', df.shape)
print(df['type'].value_counts())
display(pd.DataFrame({
    'dtype': df.dtypes.astype(str),
    'nulls': df.isnull().sum(),
    'nunique': df.nunique()
}).loc[['show_id','type','title','release_year','rating','duration_int','listed_in',
        'primary_country','content_age','target_audience','genre_count','country_count']])
df.head(3)""")

    md(cells, """### 6. Feature Selection
**Analytical objective:** group titles by observable catalogue characteristics (recency, format length within type, audience rating band, frequent genres, and grouped production country).

**Included**
- Numeric: `release_year`, type-specific `duration_int`, `content_age`, `genre_count`, `country_count`
- Categorical: `target_audience` (one-hot), grouped `primary_country` (US / India / UK / Unknown / Other)
- Multi-label: frequent genres from `listed_in` (multi-hot; top movie and TV genre lists are type-specific)

**Excluded:** `show_id`, `title`, free-text `description`, high-cardinality `director`/`cast`.

Movies and TV Shows are **not** placed in one matrix with a shared duration column.""")
    code(cells, """movies = df[df['type'] == 'Movie'].copy().reset_index(drop=True)
tv = df[df['type'] == 'TV Show'].copy().reset_index(drop=True)
print(f'Movies: {len(movies):,} | TV Shows: {len(tv):,}')
print('Movie duration unit sample:', movies['duration_unit'].value_counts().to_dict())
print('TV duration unit sample:', tv['duration_unit'].value_counts().to_dict())""")

    md(cells, """### 7. Data Preprocessing
Missing catalogue fields were already imputed in Week 1 (`Unknown Country`, modal rating, and related flags). Ten `date_added_dt` parse failures remain. `content_age` is the gap between release and catalogue addition year; it is distinct from `release_year` and is retained as a feature.

No additional row deletion is performed so cluster sizes remain comparable to the Week 1/2 catalogue.""")
    code(cells, """print('Movie numeric missing counts:')
print(movies[['release_year','duration_int','content_age','genre_count','country_count']].isnull().sum())
print('TV numeric missing counts:')
print(tv[['release_year','duration_int','content_age','genre_count','country_count']].isnull().sum())
print('Audience bands:', movies['target_audience'].value_counts().to_dict())""")

    md(cells, """### 8. Feature Encoding
- **One-hot:** `target_audience` and grouped production country.
- **Multi-hot:** selected genres from the comma-separated `listed_in` field (a title may belong to several genres).
- **Ordinal encoding is not used** for ratings: the Kids / Teens / Adults grouping is a convenience band from Week 1, and Unrated titles do not sit on that scale.

Sparse genre dummies for rare labels are omitted to keep the matrix interpretable.""")
    code(cells, """X_movies_df, movie_numeric_cols, movie_feature_names = build_feature_matrix(movies, MOVIE_GENRES)
X_tv_df, tv_numeric_cols, tv_feature_names = build_feature_matrix(tv, TV_GENRES)
print('Movie feature matrix:', X_movies_df.shape)
print('TV feature matrix:', X_tv_df.shape)
print('Movie columns:', movie_feature_names)""")

    md(cells, """### 9. Feature Scaling
K-Means and Ward hierarchical clustering use Euclidean distance, so numeric columns with different units must be scaled.

Content age and duration are skewed and have outliers. **RobustScaler** (median / IQR) is applied to the five numeric features. Binary encodings stay in \\{0, 1\\}.

A small scaler comparison is shown for K=4 on movies to justify the choice; it is not used to cherry-pick cluster labels after seeing interpretations.""")
    code(cells, """def scaled_copy(frame, numeric_cols, scaler):
    out = frame.copy().astype(float)
    out[numeric_cols] = scaler.fit_transform(frame[numeric_cols])
    return out.values

X_movies, movie_scaler = scale_features(X_movies_df, movie_numeric_cols)
X_tv, tv_scaler = scale_features(X_tv_df, tv_numeric_cols)

scaler_rows = []
for name, scaler in [('RobustScaler', RobustScaler()), ('StandardScaler', StandardScaler()), ('MinMaxScaler', MinMaxScaler())]:
    Xs = scaled_copy(X_movies_df, movie_numeric_cols, scaler)
    lab = KMeans(n_clusters=4, random_state=RANDOM_STATE, n_init=N_INIT).fit_predict(Xs)
    scaler_rows.append({
        'scaler': name,
        'silhouette': silhouette_score(Xs, lab),
        'davies_bouldin': davies_bouldin_score(Xs, lab),
        'calinski_harabasz': calinski_harabasz_score(Xs, lab)
    })
display(pd.DataFrame(scaler_rows).round(3))
print('Primary analysis uses RobustScaler on numeric columns.')
print('RobustScaler centres (median):', np.round(movie_scaler.center_, 3))
print('RobustScaler scales (IQR):', np.round(movie_scaler.scale_, 3))""")

    md(cells, """### 10. K-Means Implementation
**Unsupervised learning** estimates structure without a target label. **K-Means** randomly (or by k-means++) places K centroids, assigns each title to the nearest centroid, then updates centroids to the mean of assigned points until assignment stability or an iteration limit.

**Why scaling matters:** otherwise `release_year` (~2000) would dominate binary genre flags (0/1).

**Limitations:** spherical/equal-variance assumption, sensitivity to K and initialisation, and poor behaviour in very sparse high dimensions. `random_state=42` and `n_init=10` make the run reproducible and reduce unlucky initialisations.""")
    code(cells, """print('K-Means configuration: n_init=%s, random_state=%s, algorithm=lloyd (sklearn default)' % (N_INIT, RANDOM_STATE))
print('Candidate K:', list(K_RANGE))""")

    md(cells, """### 11. Elbow Method
Inertia is the within-cluster sum of squared Euclidean distances to centroids. An “elbow” is a K after which extra clusters buy little compactness. The elbow is a heuristic, not a proof of the true number of groups.""")
    code(cells, """movie_metrics = evaluate_kmeans(X_movies)
tv_metrics = evaluate_kmeans(X_tv)
print('--- Movies ---')
display(movie_metrics.round(3))
print('--- TV Shows ---')
display(tv_metrics.round(3))

fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
for ax, metrics, title, ksel in [
    (axes[0], movie_metrics, 'Movies', 4),
    (axes[1], tv_metrics, 'TV Shows', 4)
]:
    ax.plot(metrics['k'], metrics['inertia'], marker='o', color='#E50914', linewidth=2)
    y = float(metrics.loc[metrics['k']==ksel, 'inertia'].iloc[0])
    ax.scatter([ksel], [y], s=120, color='#1A5276', zorder=5, label=f'Selected K={ksel}')
    ax.set_title(f'Elbow method — {title}', fontweight='bold')
    ax.set_xlabel('K'); ax.set_ylabel('Inertia'); ax.legend(); ax.set_xticks(list(metrics['k']))
plt.tight_layout()
plt.savefig(os.path.join(VIS_DIR, 'w3_notebook_elbow.png'), dpi=300, bbox_inches='tight')
plt.show()""")

    md(cells, """### 12. Silhouette Analysis
The silhouette coefficient for a point is \\((b-a)/\\max(a,b)\\), where *a* is mean intra-cluster distance and *b* is mean distance to the nearest other cluster. Values near 1 indicate compact, well-separated clusters; values near 0 indicate overlap.

Silhouette can be **misleading** in mixed binary/numeric spaces: a small, far-away older-catalogue group inflates the mean score at K=2 even if that partition is too coarse for catalogue description.""")
    code(cells, """fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
for ax, metrics, title in [(axes[0], movie_metrics, 'Movies'), (axes[1], tv_metrics, 'TV Shows')]:
    ax.plot(metrics['k'], metrics['silhouette'], marker='o', color='#1A5276', linewidth=2)
    ax.set_title(f'Silhouette vs K — {title}', fontweight='bold')
    ax.set_xlabel('K'); ax.set_ylabel('Mean silhouette'); ax.set_xticks(list(metrics['k']))
plt.tight_layout()
plt.savefig(os.path.join(VIS_DIR, 'w3_notebook_silhouette.png'), dpi=300, bbox_inches='tight')
plt.show()""")

    md(cells, """### 13. Optimal Cluster Selection
K is **not** chosen from silhouette alone. For both subsets:
- K=2 maximises silhouette by isolating older titles from a large contemporary majority.
- Inertia reductions slow after **K=4**.
- K=4 yields interpretable duration / geography / recency structure.

**Reported models: K=4 for Movies and K=4 for TV Shows**, with K=2 retained as the silhouette-optimal contrast.""")
    code(cells, """movie_choice = choose_k(movie_metrics, preferred=4)
tv_choice = choose_k(tv_metrics, preferred=4)
print('Movies:', movie_choice['selection_rationale'])
print('Movie silhouette-best K =', movie_choice['silhouette_best_k'], '| selected K =', movie_choice['selected_k'])
print('TV silhouette-best K =', tv_choice['silhouette_best_k'], '| selected K =', tv_choice['selected_k'])
display(pd.DataFrame([
    {'subset': 'Movies', **{k: movie_choice['selected_metrics'][k] for k in ['k','inertia','silhouette','davies_bouldin','calinski_harabasz','size_ratio']}},
    {'subset': 'TV Shows', **{k: tv_choice['selected_metrics'][k] for k in ['k','inertia','silhouette','davies_bouldin','calinski_harabasz','size_ratio']}},
]).round(3))""")

    md(cells, """### 14. Final K-Means Model
Fit the selected models, attach cluster IDs to original `show_id` / `title` rows, and summarise sizes.""")
    code(cells, """K_MOVIE = 4
K_TV = 4
movie_model, movie_labels = fit_kmeans(X_movies, K_MOVIE)
tv_model, tv_labels = fit_kmeans(X_tv, K_TV)
movies['cluster'] = movie_labels
tv['cluster'] = tv_labels

def final_metrics(X, labels, inertia):
    return {
        'n': len(labels),
        'inertia': inertia,
        'silhouette': silhouette_score(X, labels),
        'davies_bouldin': davies_bouldin_score(X, labels),
        'calinski_harabasz': calinski_harabasz_score(X, labels)
    }

movie_final = final_metrics(X_movies, movie_labels, movie_model.inertia_)
tv_final = final_metrics(X_tv, tv_labels, tv_model.inertia_)
print('Movies K=4:', {k: round(v, 3) if isinstance(v, float) else v for k, v in movie_final.items()})
print('TV K=4:', {k: round(v, 3) if isinstance(v, float) else v for k, v in tv_final.items()})
print('Movie sizes:\\n', movies['cluster'].value_counts().sort_index())
print('TV sizes:\\n', tv['cluster'].value_counts().sort_index())""")

    md(cells, """### 15. PCA Visualization
PCA is used only for **display**. Two components cannot preserve all original distances. If the cumulative explained variance is moderate, overlapping clouds are expected even when original-space centroids differ.""")
    code(cells, """def pca_plot(X, labels, title, filename):
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coords = pca.fit_transform(X)
    colors = ['#E50914', '#1A5276', '#2B8A3E', '#F39C12']
    plt.figure(figsize=(8.5, 5.5))
    for cid in np.unique(labels):
        m = labels == cid
        plt.scatter(coords[m, 0], coords[m, 1], s=16, alpha=0.55, color=colors[cid % 4], label=f'Cluster {cid}')
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)')
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)')
    plt.title(title, fontweight='bold')
    plt.legend(markerscale=2)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, filename), dpi=300, bbox_inches='tight')
    plt.show()
    return pca.explained_variance_ratio_

print('Movie PCA 2D variance:', np.round(pca_plot(X_movies, movie_labels, 'PCA of movie K-Means clusters', 'w3_movie_05_pca.png')*100, 2))
print('TV PCA 2D variance:', np.round(pca_plot(X_tv, tv_labels, 'PCA of TV K-Means clusters', 'w3_tv_05_pca.png')*100, 2))""")

    md(cells, """### 16. Cluster Characterization
Statistics are computed from the original (unscaled) columns. Descriptive labels are assigned from those statistics, not from assumed Netflix business units.""")
    code(cells, """movie_profiles = characterize(movies, MOVIE_GENRES, 'duration_minutes')
movie_names = assign_movie_labels(movie_profiles)
for p in movie_profiles:
    p['label'] = movie_names[p['cluster']]
movies['cluster_label'] = movies['cluster'].map(movie_names)

tv_profiles = characterize(tv, TV_GENRES, 'seasons')
tv_names = assign_tv_labels(tv_profiles)
for p in tv_profiles:
    p['label'] = tv_names[p['cluster']]
tv['cluster_label'] = tv['cluster'].map(tv_names)

movie_summary = pd.DataFrame(movie_profiles)[['cluster','label','n','pct','mean_release_year','mean_duration_minutes','mean_content_age']]
tv_summary = pd.DataFrame(tv_profiles)[['cluster','label','n','pct','mean_release_year','mean_seasons','mean_content_age']]
print('Movie clusters')
display(movie_summary.round(2))
print('TV clusters')
display(tv_summary.round(2))
print('\\nMovie detail')
for p in movie_profiles:
    print('Cluster', p['cluster'], '|', p['label'], '| n=', p['n'], '(', p['pct'], '%)')
    print('  audience', p['audience_pct'])
    print('  genres', p['top_genres'])
    print('  countries', p['country_group_pct'])
print('\\nTV detail')
for p in tv_profiles:
    print('Cluster', p['cluster'], '|', p['label'], '| n=', p['n'], '(', p['pct'], '%)')
    print('  audience', p['audience_pct'])
    print('  genres', p['top_genres'])
    print('  countries', p['country_group_pct'])

os.makedirs('../dataset/processed', exist_ok=True)
movies[['show_id','title','type','release_year','rating','target_audience','duration_int',
        'primary_genre','primary_country','cluster','cluster_label']].to_csv(
    '../dataset/processed/netflix_movie_clusters.csv', index=False)
tv[['show_id','title','type','release_year','rating','target_audience','duration_int',
    'primary_genre','primary_country','cluster','cluster_label']].to_csv(
    '../dataset/processed/netflix_tv_clusters.csv', index=False)""")

    md(cells, """### 17. Hierarchical Clustering
Agglomerative clustering starts with each sample as its own cluster and merges the closest pair according to a **linkage**:
- **Ward:** minimises the increase in within-cluster variance (Euclidean).
- **Average:** mean pairwise distance between clusters.
- **Complete:** distance between farthest points.

The full movie matrix (5,377 × 26) produces an unreadable dendrogram and is slower to inspect. A **stratified sample of 250 titles** (by `target_audience`, `random_state=42`) is used for dendrograms and linkage comparison. **Sample results are not claimed to equal the full-catalogue K-Means partition.**""")
    code(cells, """movie_hier = hierarchical_on_sample(X_movies, movies, K_MOVIE)
tv_hier = hierarchical_on_sample(X_tv, tv, K_TV)
print('Movie sample n =', movie_hier['sample_size'], '| ARI vs K-Means =', round(movie_hier['ari_kmeans_ward'], 3))
print('TV sample n =', tv_hier['sample_size'], '| ARI vs K-Means =', round(tv_hier['ari_kmeans_ward'], 3))
display(pd.DataFrame(movie_hier['linkage_metrics']).T.add_prefix('movie_').join(
    pd.DataFrame(tv_hier['linkage_metrics']).T.add_prefix('tv_')
).round(3))""")

    md(cells, """### 18. Dendrogram and Cluster Visualization""")
    code(cells, """plt.figure(figsize=(12, 5))
dendrogram(movie_hier['linkage_matrix'], no_labels=True, above_threshold_color='#221F1F')
plt.title('Ward dendrogram — movie sample (n=%s)' % movie_hier['sample_size'], fontweight='bold')
plt.xlabel('Sampled titles'); plt.ylabel('Ward distance')
plt.tight_layout()
plt.savefig(os.path.join(VIS_DIR, 'w3_movie_10_dendrogram.png'), dpi=300, bbox_inches='tight')
plt.show()

plt.figure(figsize=(12, 5))
dendrogram(tv_hier['linkage_matrix'], no_labels=True, above_threshold_color='#221F1F')
plt.title('Ward dendrogram — TV sample (n=%s)' % tv_hier['sample_size'], fontweight='bold')
plt.xlabel('Sampled titles'); plt.ylabel('Ward distance')
plt.tight_layout()
plt.savefig(os.path.join(VIS_DIR, 'w3_tv_10_dendrogram.png'), dpi=300, bbox_inches='tight')
plt.show()""")

    md(cells, """### 19. Clustering Evaluation
Full-data K-Means metrics are the primary evaluation. Hierarchical metrics are reported **on the sample** only.""")
    code(cells, """eval_table = pd.DataFrame([
    {'model': 'K-Means movies (full, K=4)', **movie_final},
    {'model': 'K-Means TV (full, K=4)', **tv_final},
    {'model': 'Ward movies (sample, K=4)', 'n': movie_hier['sample_size'], 'inertia': np.nan,
     'silhouette': movie_hier['ward_silhouette'],
     'davies_bouldin': movie_hier['linkage_metrics']['ward']['davies_bouldin'],
     'calinski_harabasz': movie_hier['linkage_metrics']['ward']['calinski_harabasz']},
    {'model': 'Ward TV (sample, K=4)', 'n': tv_hier['sample_size'], 'inertia': np.nan,
     'silhouette': tv_hier['ward_silhouette'],
     'davies_bouldin': tv_hier['linkage_metrics']['ward']['davies_bouldin'],
     'calinski_harabasz': tv_hier['linkage_metrics']['ward']['calinski_harabasz']},
])
display(eval_table.round(3))
print('Davies–Bouldin: lower is better. Calinski–Harabasz: higher is better.')""")

    md(cells, """### 20. Algorithm Comparison
K-Means and Ward can disagree (ARI well below 1) because they optimise different criteria and because hierarchical clustering here sees only 250 titles. Average/complete linkage often post higher sample silhouette by forming small tight groups plus a large remainder — compact mathematically, weaker as a catalogue taxonomy.

Neither algorithm is universally superior on this dataset.""")
    code(cells, """compare = pd.DataFrame({
    'Movies': {
        'K-Means full silhouette': movie_final['silhouette'],
        'K-Means sample silhouette': movie_hier['kmeans_sample_silhouette'],
        'Ward sample silhouette': movie_hier['ward_silhouette'],
        'Average sample silhouette': movie_hier['linkage_metrics']['average']['silhouette'],
        'Complete sample silhouette': movie_hier['linkage_metrics']['complete']['silhouette'],
        'ARI K-Means vs Ward (sample)': movie_hier['ari_kmeans_ward'],
    },
    'TV Shows': {
        'K-Means full silhouette': tv_final['silhouette'],
        'K-Means sample silhouette': tv_hier['kmeans_sample_silhouette'],
        'Ward sample silhouette': tv_hier['ward_silhouette'],
        'Average sample silhouette': tv_hier['linkage_metrics']['average']['silhouette'],
        'Complete sample silhouette': tv_hier['linkage_metrics']['complete']['silhouette'],
        'ARI K-Means vs Ward (sample)': tv_hier['ari_kmeans_ward'],
    }
}).round(3)
display(compare)""")

    md(cells, """### 21. Business and Research Implications
Observed clusters describe **how titles sit together in metadata**, which can support catalogue tagging, QA of genre/country fields, or sampling for further qualitative review.

They do **not** measure watch time, ratings stars, or Netflix's recommendation system. Any “programming strategy” reading would be hypothetical and is not licensed by this dataset.""")

    md(cells, """### 22. Limitations
- Mixed numeric and binary features; Euclidean K-Means is a compromise, not a perfect mixed-type model.
- Multi-hot genres are still incomplete relative to all 42 listed categories.
- Unknown country / unknown director imputations from Week 1 can form artificial similarity.
- Cluster count is uncertain: silhouette favours K=2; interpretation favours K=4.
- TV Cluster of 27 legacy titles is real in feature space but small.
- Hierarchical results are sample-based.
- PCA scatter plots discard variance beyond two components.""")

    md(cells, """### 23. Conclusion
The Netflix catalogue was clustered separately for movies and TV shows using Robust-scaled numeric fields plus one-hot audience/country and multi-hot frequent genres. K-Means with K=4 provides an interpretable partition (international features vs short-form US titles vs licensed mid-catalogue vs vintage cinema; and contemporary single-season TV vs older acquisitions vs multi-season series vs a small vintage set), while K=2 is the silhouette-optimal recency split. Hierarchical Ward clustering on a 250-title sample shows moderate agreement with K-Means (ARI ≈ 0.45–0.50) and should be read with that sampling caveat.""")

    nb["cells"] = cells
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Notebook written: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    build_notebook()
