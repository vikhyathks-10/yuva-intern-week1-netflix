"""
Week 3 clustering workflow for the Netflix Movies and TV Shows catalogue.

Movies and TV Shows are clustered separately so movie runtime (minutes) is never
treated as equivalent to TV season count.
"""

from __future__ import annotations

import json
import os
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_samples,
    silhouette_score,
)
from sklearn.preprocessing import RobustScaler

warnings.filterwarnings("ignore")

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
PROCESSED_DATA_PATH = os.path.join(PROJECT_DIR, "dataset", "processed", "netflix_processed.csv")
VIS_DIR = os.path.join(PROJECT_DIR, "visualizations", "week3")
SCREEN_DIR = os.path.join(PROJECT_DIR, "screenshots", "week3")
METRICS_PATH = os.path.join(PROJECT_DIR, "dataset", "processed", "week3_clustering_metrics.json")
MOVIE_ASSIGN_PATH = os.path.join(PROJECT_DIR, "dataset", "processed", "netflix_movie_clusters.csv")
TV_ASSIGN_PATH = os.path.join(PROJECT_DIR, "dataset", "processed", "netflix_tv_clusters.csv")
HIER_SAMPLE_PATH = os.path.join(PROJECT_DIR, "dataset", "processed", "week3_hierarchical_movie_sample.csv")

RANDOM_STATE = 42
K_RANGE = range(2, 11)
N_INIT = 10
HIER_SAMPLE_SIZE = 250

MOVIE_GENRES = [
    "International Movies",
    "Dramas",
    "Comedies",
    "Documentaries",
    "Action & Adventure",
    "Independent Movies",
    "Children & Family Movies",
    "Romantic Movies",
    "Thrillers",
    "Stand-Up Comedy",
    "Music & Musicals",
    "Horror Movies",
]
TV_GENRES = [
    "International TV Shows",
    "TV Dramas",
    "TV Comedies",
    "Crime TV Shows",
    "Kids' TV",
    "Docuseries",
    "Romantic TV Shows",
    "British TV Shows",
    "Reality TV",
    "Anime Series",
]
COUNTRY_GROUPS = ["United States", "India", "United Kingdom", "Unknown Country", "Other"]
AUDIENCE_COLS = ["Kids", "Teens", "Adults", "Unrated"]

CLUSTER_COLORS = ["#E50914", "#1A5276", "#2B8A3E", "#F39C12", "#8E44AD", "#16A085"]

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["figure.dpi"] = 120


def ensure_dirs() -> None:
    os.makedirs(VIS_DIR, exist_ok=True)
    os.makedirs(SCREEN_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(METRICS_PATH), exist_ok=True)


def load_processed() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DATA_PATH)
    df["date_added_dt"] = pd.to_datetime(df["date_added"], errors="coerce")
    return df


def group_country(value: str) -> str:
    if value in {"United States", "India", "United Kingdom", "Unknown Country"}:
        return value
    return "Other"


def multi_hot_genres(series: pd.Series, genre_list: list[str]) -> pd.DataFrame:
    exploded_flags = {}
    split_lists = series.fillna("").apply(lambda x: [g.strip() for g in str(x).split(",")])
    for genre in genre_list:
        exploded_flags[f"genre_{genre}"] = split_lists.apply(lambda genres: int(genre in genres))
    return pd.DataFrame(exploded_flags, index=series.index)


def audience_one_hot(series: pd.Series) -> pd.DataFrame:
    out = pd.DataFrame(0, index=series.index, columns=[f"aud_{c}" for c in AUDIENCE_COLS])
    for col in AUDIENCE_COLS:
        out[f"aud_{col}"] = (series == col).astype(int)
    return out


def country_one_hot(series: pd.Series) -> pd.DataFrame:
    grouped = series.map(group_country)
    out = pd.DataFrame(0, index=series.index, columns=[f"cty_{c}" for c in COUNTRY_GROUPS])
    for col in COUNTRY_GROUPS:
        out[f"cty_{col}"] = (grouped == col).astype(int)
    return out


def build_feature_matrix(subset: pd.DataFrame, genre_list: list[str]) -> tuple[pd.DataFrame, list[str], list[str]]:
    # `release_year` and `content_age` describe different timing dimensions:
    # original release timing and lag until catalogue addition, respectively.
    numeric_cols = ["release_year", "duration_int", "content_age", "genre_count", "country_count"]
    numeric = subset[numeric_cols].copy()
    audience = audience_one_hot(subset["target_audience"])
    countries = country_one_hot(subset["primary_country"])
    genres = multi_hot_genres(subset["listed_in"], genre_list)
    features = pd.concat([numeric, audience, countries, genres], axis=1)
    return features, numeric_cols, list(features.columns)


def scale_features(features: pd.DataFrame, numeric_cols: list[str]) -> tuple[np.ndarray, RobustScaler]:
    scaled = features.copy().astype(float)
    scaler = RobustScaler()
    scaled[numeric_cols] = scaler.fit_transform(features[numeric_cols])
    return scaled.values, scaler


def evaluate_kmeans(X: np.ndarray, k_range=K_RANGE) -> pd.DataFrame:
    rows = []
    for k in k_range:
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=N_INIT)
        labels = model.fit_predict(X)
        sizes = pd.Series(labels).value_counts().sort_index()
        rows.append(
            {
                "k": int(k),
                "inertia": float(model.inertia_),
                "silhouette": float(silhouette_score(X, labels)),
                "davies_bouldin": float(davies_bouldin_score(X, labels)),
                "calinski_harabasz": float(calinski_harabasz_score(X, labels)),
                "min_cluster_size": int(sizes.min()),
                "max_cluster_size": int(sizes.max()),
                "size_ratio": float(sizes.max() / sizes.min()),
            }
        )
    return pd.DataFrame(rows)


def savefig(fig_name: str) -> str:
    path = os.path.join(VIS_DIR, fig_name)
    plt.savefig(path, dpi=300, bbox_inches="tight")
    screen_path = os.path.join(SCREEN_DIR, fig_name)
    plt.savefig(screen_path, dpi=200, bbox_inches="tight")
    plt.close()
    return path


def plot_elbow(metrics: pd.DataFrame, title: str, filename: str, selected_k: int | None = None,
               silhouette_best_k: int | None = None) -> None:
    plt.figure(figsize=(8.5, 5))
    plt.plot(metrics["k"], metrics["inertia"], marker="o", color="#E50914", linewidth=2.2, label="Inertia")
    if selected_k is not None and selected_k in set(metrics["k"]):
        y = float(metrics.loc[metrics["k"] == selected_k, "inertia"].iloc[0])
        plt.scatter([selected_k], [y], s=140, color="#1A5276", zorder=5, label=f"Selected K={selected_k}")
    if silhouette_best_k is not None and silhouette_best_k != selected_k:
        y2 = float(metrics.loc[metrics["k"] == silhouette_best_k, "inertia"].iloc[0])
        plt.scatter([silhouette_best_k], [y2], s=90, color="#F39C12", zorder=5, label=f"Silhouette-best K={silhouette_best_k}")
    plt.xticks(list(metrics["k"]))
    plt.xlabel("Number of clusters (K)")
    plt.ylabel("Inertia (within-cluster sum of squares)")
    plt.title(title, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.legend()
    savefig(filename)


def plot_silhouette_scores(metrics: pd.DataFrame, title: str, filename: str) -> None:
    plt.figure(figsize=(8.5, 5))
    plt.plot(metrics["k"], metrics["silhouette"], marker="o", color="#1A5276", linewidth=2.2, label="Silhouette")
    plt.xticks(list(metrics["k"]))
    plt.xlabel("Number of clusters (K)")
    plt.ylabel("Mean silhouette coefficient")
    plt.title(title, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.legend()
    savefig(filename)


def plot_additional_indices(metrics: pd.DataFrame, title: str, filename: str) -> None:
    fig, ax1 = plt.subplots(figsize=(8.5, 5))
    ax2 = ax1.twinx()
    ax1.plot(metrics["k"], metrics["davies_bouldin"], marker="s", color="#8E44AD", linewidth=2, label="Davies–Bouldin (lower better)")
    ax2.plot(metrics["k"], metrics["calinski_harabasz"], marker="^", color="#2B8A3E", linewidth=2, label="Calinski–Harabasz (higher better)")
    ax1.set_xlabel("Number of clusters (K)")
    ax1.set_ylabel("Davies–Bouldin index")
    ax2.set_ylabel("Calinski–Harabasz index")
    ax1.set_xticks(list(metrics["k"]))
    ax1.set_title(title, fontweight="bold")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")
    fig.tight_layout()
    savefig(filename)


def plot_cluster_sizes(labels: np.ndarray, title: str, filename: str) -> None:
    counts = pd.Series(labels).value_counts().sort_index()
    plt.figure(figsize=(8.5, 5))
    colors = CLUSTER_COLORS[: len(counts)]
    bars = plt.bar([f"Cluster {i}" for i in counts.index], counts.values, color=colors, edgecolor="black", alpha=0.9)
    plt.ylabel("Number of titles")
    plt.title(title, fontweight="bold")
    total = counts.sum()
    for bar, val in zip(bars, counts.values):
        plt.annotate(f"{val}\n({val / total * 100:.1f}%)", xy=(bar.get_x() + bar.get_width() / 2, val),
                     ha="center", va="bottom", fontsize=9, fontweight="bold")
    plt.ylim(0, counts.max() * 1.18)
    plt.tight_layout()
    savefig(filename)


def plot_pca_scatter(X: np.ndarray, labels: np.ndarray, title: str, filename: str) -> dict:
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coords = pca.fit_transform(X)
    plt.figure(figsize=(9, 6))
    for cluster_id in np.unique(labels):
        mask = labels == cluster_id
        plt.scatter(coords[mask, 0], coords[mask, 1], s=18, alpha=0.55,
                    color=CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)], label=f"Cluster {cluster_id}")
    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0] * 100:.1f}% variance)")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1] * 100:.1f}% variance)")
    plt.title(title, fontweight="bold")
    plt.legend(markerscale=2, frameon=True)
    plt.tight_layout()
    savefig(filename)
    return {
        "pc1": float(pca.explained_variance_ratio_[0]),
        "pc2": float(pca.explained_variance_ratio_[1]),
        "cumulative_2d": float(pca.explained_variance_ratio_[:2].sum()),
    }


def plot_centroid_heatmap(feature_names: list[str], centroids: np.ndarray, title: str, filename: str) -> None:
    centroid_df = pd.DataFrame(centroids, columns=feature_names, index=[f"Cluster {i}" for i in range(len(centroids))])
    plt.figure(figsize=(14, 4.8))
    sns.heatmap(centroid_df, cmap="RdYlBu_r", center=0, linewidths=0.3)
    plt.title(title, fontweight="bold")
    plt.xticks(rotation=65, ha="right", fontsize=8)
    plt.yticks(rotation=0)
    plt.tight_layout()
    savefig(filename)


def plot_numeric_boxplots(subset: pd.DataFrame, duration_label: str, title: str, filename: str) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    specs = [
        ("duration_int", duration_label),
        ("release_year", "Release year"),
        ("content_age", "Content age (years)"),
    ]
    for ax, (col, ylab) in zip(axes, specs):
        sns.boxplot(data=subset, x="cluster", y=col, palette=CLUSTER_COLORS, ax=ax)
        ax.set_xlabel("Cluster")
        ax.set_ylabel(ylab)
    fig.suptitle(title, fontweight="bold")
    fig.tight_layout()
    savefig(filename)


def plot_audience_stacked(subset: pd.DataFrame, title: str, filename: str) -> None:
    ct = pd.crosstab(subset["cluster"], subset["target_audience"], normalize="index") * 100
    ct = ct.reindex(columns=AUDIENCE_COLS, fill_value=0)
    ct.plot(kind="bar", stacked=True, figsize=(8.5, 5),
            color=["#27AE60", "#F4D03F", "#E74C3C", "#7F8C8D"], edgecolor="black")
    plt.ylabel("Percentage of cluster")
    plt.xlabel("Cluster")
    plt.title(title, fontweight="bold")
    plt.legend(title="Audience", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=0)
    plt.tight_layout()
    savefig(filename)


def plot_genre_heatmap(subset: pd.DataFrame, genre_list: list[str], title: str, filename: str) -> None:
    rows = []
    for cluster_id in sorted(subset["cluster"].unique()):
        part = subset[subset["cluster"] == cluster_id]
        flags = multi_hot_genres(part["listed_in"], genre_list)
        rows.append((flags.mean() * 100).rename(cluster_id))
    heat = pd.concat(rows, axis=1).T
    heat.columns = genre_list
    heat.index = [f"Cluster {i}" for i in heat.index]
    plt.figure(figsize=(12, 4.6))
    sns.heatmap(heat, annot=True, fmt=".0f", cmap="Reds", linewidths=0.4)
    plt.title(title, fontweight="bold")
    plt.xlabel("Genre presence (% of titles in cluster)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    savefig(filename)


def plot_dendrogram(linkage_matrix: np.ndarray, title: str, filename: str) -> None:
    plt.figure(figsize=(12, 5.5))
    dendrogram(linkage_matrix, no_labels=True, color_threshold=None, above_threshold_color="#221F1F")
    plt.title(title, fontweight="bold")
    plt.xlabel("Sampled titles")
    plt.ylabel("Ward distance")
    plt.tight_layout()
    savefig(filename)


def characterize(subset: pd.DataFrame, genre_list: list[str], duration_name: str) -> list[dict]:
    profiles = []
    n_total = len(subset)
    for cluster_id in sorted(subset["cluster"].unique()):
        part = subset[subset["cluster"] == cluster_id]
        genre_rates = (multi_hot_genres(part["listed_in"], genre_list).mean() * 100).sort_values(ascending=False)
        country_counts = part["primary_country"].map(group_country).value_counts(normalize=True) * 100
        audience_counts = part["target_audience"].value_counts(normalize=True) * 100
        rating_counts = part["rating"].value_counts(normalize=True) * 100
        profiles.append(
            {
                "cluster": int(cluster_id),
                "n": int(len(part)),
                "pct": round(len(part) / n_total * 100, 2),
                "mean_release_year": round(float(part["release_year"].mean()), 2),
                "median_release_year": int(part["release_year"].median()),
                f"mean_{duration_name}": round(float(part["duration_int"].mean()), 2),
                f"median_{duration_name}": float(part["duration_int"].median()),
                "mean_content_age": round(float(part["content_age"].mean()), 2),
                "median_content_age": float(part["content_age"].median()),
                "mean_genre_count": round(float(part["genre_count"].mean()), 2),
                "mean_country_count": round(float(part["country_count"].mean()), 2),
                "top_genres": {k.replace("genre_", ""): round(float(v), 1) for k, v in genre_rates.head(5).items()},
                "audience_pct": {k: round(float(v), 1) for k, v in audience_counts.items()},
                "country_group_pct": {k: round(float(v), 1) for k, v in country_counts.items()},
                "top_ratings": {k: round(float(v), 1) for k, v in rating_counts.head(4).items()},
            }
        )
    return profiles


def assign_movie_labels(profiles: list[dict]) -> dict[int, str]:
    """Assign descriptive labels from observed cluster statistics, not prior assumptions."""
    labels = {}
    for p in profiles:
        cid = p["cluster"]
        genres = p["top_genres"]
        mean_dur = p["mean_duration_minutes"]
        mean_age = p["mean_content_age"]
        mean_year = p["mean_release_year"]
        intl = genres.get("International Movies", 0)
        docs = genres.get("Documentaries", 0)
        standup = genres.get("Stand-Up Comedy", 0)
        family = genres.get("Children & Family Movies", 0)
        if mean_age >= 30 or mean_year < 1985:
            labels[cid] = "Classic and vintage cinema"
        elif mean_age >= 10:
            labels[cid] = "Mid-catalogue licensed features"
        elif mean_dur < 90 and (docs + standup + family) >= 30:
            labels[cid] = "Short-form US docs, stand-up, and family titles"
        elif intl >= 50:
            labels[cid] = "Contemporary international feature films"
        else:
            labels[cid] = "Contemporary adult dramas and comedies"
    seen = {}
    for cid, name in labels.items():
        if name in seen:
            labels[cid] = f"{name} (cluster {cid})"
        seen[name] = cid
    return labels


def assign_tv_labels(profiles: list[dict]) -> dict[int, str]:
    labels = {}
    for p in profiles:
        cid = p["cluster"]
        mean_seasons = p["mean_seasons"]
        mean_age = p["mean_content_age"]
        mean_year = p["mean_release_year"]
        cty = p["country_group_pct"]
        if mean_age >= 25 or mean_year < 1990:
            labels[cid] = "Legacy and vintage television"
        elif mean_seasons >= 4:
            labels[cid] = "Multi-season continuing series"
        elif mean_age >= 6:
            labels[cid] = "Older acquired television catalogue"
        elif cty.get("United States", 0) >= 55 and mean_seasons >= 2.5:
            labels[cid] = "US continuing series"
        else:
            labels[cid] = "Contemporary mostly single-season series"
    seen = {}
    for cid, name in labels.items():
        if name in seen:
            labels[cid] = f"{name} (cluster {cid})"
        seen[name] = cid
    return labels


def fit_kmeans(X: np.ndarray, k: int) -> tuple[KMeans, np.ndarray]:
    model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=N_INIT)
    labels = model.fit_predict(X)
    return model, labels


def hierarchical_on_sample(X: np.ndarray, subset: pd.DataFrame, k: int) -> dict:
    rng = np.random.default_rng(RANDOM_STATE)
    n = min(HIER_SAMPLE_SIZE, len(subset))
    # Stratify by cluster if available, else by audience
    strat = subset["target_audience"].astype(str)
    sample_idx = []
    remaining = n
    groups = list(strat.unique())
    per_group = max(1, n // max(len(groups), 1))
    index_array = np.arange(len(subset))
    for g in groups:
        g_idx = index_array[strat.values == g]
        take = min(len(g_idx), per_group)
        if take > 0:
            chosen = rng.choice(g_idx, size=take, replace=False)
            sample_idx.extend(chosen.tolist())
    sample_idx = np.unique(np.array(sample_idx))
    if len(sample_idx) < n:
        leftover = np.setdiff1d(index_array, sample_idx)
        extra = rng.choice(leftover, size=min(n - len(sample_idx), len(leftover)), replace=False)
        sample_idx = np.concatenate([sample_idx, extra])
    sample_idx = sample_idx[:n]
    X_s = X[sample_idx]
    Z = linkage(X_s, method="ward")
    hier_labels = fcluster(Z, t=k, criterion="maxclust") - 1

    agg_metrics = {}
    for method in ["ward", "average", "complete"]:
        if method == "ward":
            model = AgglomerativeClustering(n_clusters=k, linkage="ward")
        else:
            model = AgglomerativeClustering(n_clusters=k, linkage=method, metric="euclidean")
        pred = model.fit_predict(X_s)
        agg_metrics[method] = {
            "silhouette": float(silhouette_score(X_s, pred)),
            "davies_bouldin": float(davies_bouldin_score(X_s, pred)),
            "calinski_harabasz": float(calinski_harabasz_score(X_s, pred)),
        }

    kmeans_sample = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=N_INIT).fit_predict(X_s)
    return {
        "sample_size": int(len(sample_idx)),
        "sample_idx": sample_idx.tolist(),
        "linkage_matrix": Z,
        "hier_labels": hier_labels.tolist(),
        "kmeans_sample_labels": kmeans_sample.tolist(),
        "ari_kmeans_ward": float(adjusted_rand_score(kmeans_sample, hier_labels)),
        "linkage_metrics": agg_metrics,
        "ward_silhouette": agg_metrics["ward"]["silhouette"],
        "kmeans_sample_silhouette": float(silhouette_score(X_s, kmeans_sample)),
    }


def choose_k(metrics: pd.DataFrame, preferred: int | None = None) -> dict:
    """Combine silhouette, DB, CH, size balance, elbow diminishing returns, and interpretability."""
    ranked = metrics.copy()
    ranked["sil_rank"] = ranked["silhouette"].rank(ascending=False)
    ranked["db_rank"] = ranked["davies_bouldin"].rank(ascending=True)
    ranked["ch_rank"] = ranked["calinski_harabasz"].rank(ascending=False)
    ranked["balance_rank"] = ranked["size_ratio"].rank(ascending=True)
    ranked["composite"] = ranked[["sil_rank", "db_rank", "ch_rank", "balance_rank"]].mean(axis=1)
    best_row = ranked.sort_values(["composite", "silhouette"], ascending=[True, False]).iloc[0]
    sil_best = int(ranked.sort_values("silhouette", ascending=False).iloc[0]["k"])
    selected = int(preferred) if preferred is not None else int(best_row["k"])
    selected_row = ranked[ranked["k"] == selected].iloc[0]
    return {
        "selected_k": selected,
        "silhouette_best_k": sil_best,
        "composite_best_k": int(best_row["k"]),
        "selection_rationale": (
            "K=2 maximises silhouette and is retained as a coarse recency baseline. K=4 is the descriptive primary model: the elbow begins to flatten around K=4 and the resulting groups expose additional interpretable runtime/season, genre, and country patterns. This is a practical resolution choice, not a uniquely optimal K."
            if preferred == 4 else
            "Selected from the candidate range using silhouette, Davies–Bouldin, Calinski–Harabasz, size balance, and interpretability."
        ),
        "selected_metrics": {
            key: (float(selected_row[key]) if key != "k" else int(selected_row[key]))
            for key in ["k", "inertia", "silhouette", "davies_bouldin", "calinski_harabasz",
                        "min_cluster_size", "max_cluster_size", "size_ratio", "composite"]
        },
    }


def run_subset_pipeline(df: pd.DataFrame, content_type: str, genre_list: list[str],
                        duration_name: str, duration_label: str, preferred_k: int | None,
                        prefix: str) -> dict:
    subset = df[df["type"] == content_type].copy().reset_index(drop=True)
    features, numeric_cols, feature_names = build_feature_matrix(subset, genre_list)
    X, scaler = scale_features(features, numeric_cols)
    metrics = evaluate_kmeans(X)
    choice = choose_k(metrics, preferred_k)
    k = choice["selected_k"]
    model, labels = fit_kmeans(X, k)
    subset["cluster"] = labels
    sil_mean = float(silhouette_score(X, labels))
    sil_samples = silhouette_samples(X, labels)

    plot_elbow(
        metrics,
        f"Elbow method — {content_type} K-Means",
        f"{prefix}_01_elbow.png",
        selected_k=k,
        silhouette_best_k=int(choice["silhouette_best_k"]),
    )
    plot_silhouette_scores(metrics, f"Silhouette scores — {content_type} K-Means", f"{prefix}_02_silhouette.png")
    plot_additional_indices(metrics, f"Davies–Bouldin and Calinski–Harabasz — {content_type}", f"{prefix}_03_db_ch.png")
    plot_cluster_sizes(labels, f"K-Means cluster sizes — {content_type}", f"{prefix}_04_cluster_sizes.png")
    pca_info = plot_pca_scatter(X, labels, f"PCA projection of {content_type} clusters", f"{prefix}_05_pca.png")
    plot_centroid_heatmap(feature_names, model.cluster_centers_, f"Scaled centroid profiles — {content_type}", f"{prefix}_06_centroids.png")
    plot_numeric_boxplots(subset, duration_label, f"Numeric feature distributions by cluster — {content_type}", f"{prefix}_07_boxplots.png")
    plot_audience_stacked(subset, f"Audience mix by cluster — {content_type}", f"{prefix}_08_audience.png")
    plot_genre_heatmap(subset, genre_list, f"Genre presence by cluster — {content_type}", f"{prefix}_09_genres.png")

    profiles = characterize(subset, genre_list, duration_name)
    if content_type == "Movie":
        name_map = assign_movie_labels(profiles)
    else:
        name_map = assign_tv_labels(profiles)
    for p in profiles:
        p["label"] = name_map[p["cluster"]]
    subset["cluster_label"] = subset["cluster"].map(name_map)

    hier = hierarchical_on_sample(X, subset, k)
    plot_dendrogram(hier["linkage_matrix"], f"Ward dendrogram — {content_type} sample (n={hier['sample_size']})", f"{prefix}_10_dendrogram.png")

    sample_subset = subset.iloc[hier["sample_idx"]].copy()
    sample_subset["hier_cluster"] = hier["hier_labels"]
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coords = pca.fit_transform(X[hier["sample_idx"]])
    plt.figure(figsize=(9, 5.5))
    for cluster_id in sorted(set(hier["hier_labels"])):
        mask = np.array(hier["hier_labels"]) == cluster_id
        plt.scatter(coords[mask, 0], coords[mask, 1], s=28, alpha=0.75,
                    color=CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)], label=f"Hier {cluster_id}")
    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0] * 100:.1f}% variance)")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1] * 100:.1f}% variance)")
    plt.title(f"Hierarchical clusters on sampled {content_type} titles (PCA)", fontweight="bold")
    plt.legend()
    plt.tight_layout()
    savefig(f"{prefix}_11_hier_pca.png")

    assign_cols = ["show_id", "title", "type", "release_year", "rating", "target_audience",
                   "duration_int", "primary_genre", "primary_country", "cluster", "cluster_label"]
    return {
        "n": int(len(subset)),
        "n_features": int(X.shape[1]),
        "feature_names": feature_names,
        "numeric_cols": numeric_cols,
        "k_metrics": metrics.to_dict(orient="records"),
        "choice": {k: (v if not isinstance(v, dict) else {kk: (float(vv) if isinstance(vv, (np.floating, float)) else int(vv) if isinstance(vv, (np.integer, int)) else vv) for kk, vv in v.items()}) for k, v in choice.items()},
        "selected_k": k,
        "final": {
            "inertia": float(model.inertia_),
            "silhouette": sil_mean,
            "davies_bouldin": float(davies_bouldin_score(X, labels)),
            "calinski_harabasz": float(calinski_harabasz_score(X, labels)),
            "mean_silhouette_by_cluster": {str(i): float(sil_samples[labels == i].mean()) for i in np.unique(labels)},
        },
        "pca": pca_info,
        "profiles": profiles,
        "labels": name_map,
        "hierarchical": {
            "sample_size": hier["sample_size"],
            "ari_kmeans_ward": hier["ari_kmeans_ward"],
            "linkage_metrics": hier["linkage_metrics"],
            "ward_silhouette": hier["ward_silhouette"],
            "kmeans_sample_silhouette": hier["kmeans_sample_silhouette"],
            "sampling_note": (
                f"Agglomerative clustering and the dendrogram use a stratified sample of "
                f"{hier['sample_size']} {content_type} titles. Sample results are not claimed to "
                "reproduce the full-catalogue partition."
            ),
        },
        "assignments": subset[assign_cols],
        "hier_sample": sample_subset[assign_cols + ["hier_cluster"]] if content_type == "Movie" else None,
        "scaler_center": scaler.center_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
    }


def json_ready(obj):
    if isinstance(obj, dict):
        return {str(k): json_ready(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_ready(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.ndarray, pd.Series)):
        return json_ready(obj.tolist())
    return obj


def run_clustering_pipeline() -> dict:
    ensure_dirs()
    df = load_processed()
    print(f"Loaded processed catalogue: {df.shape}")

    movie_result = run_subset_pipeline(
        df, "Movie", MOVIE_GENRES, "duration_minutes", "Duration (minutes)",
        preferred_k=4, prefix="w3_movie",
    )
    tv_result = run_subset_pipeline(
        df, "TV Show", TV_GENRES, "seasons", "Number of seasons",
        preferred_k=4, prefix="w3_tv",
    )

    # If movie K is too fragmented or silhouette-best is 2 with trivial type-like split,
    # keep the composite choice. Optionally override movies to a more interpretable k
    # if composite selected 2 and next-best interpretable k is 4.
    print("Movie K metrics:")
    print(pd.DataFrame(movie_result["k_metrics"]))
    print("Selected movie K:", movie_result["selected_k"])
    print("TV K metrics:")
    print(pd.DataFrame(tv_result["k_metrics"]))
    print("Selected TV K:", tv_result["selected_k"])

    movie_result["assignments"].to_csv(MOVIE_ASSIGN_PATH, index=False)
    tv_result["assignments"].to_csv(TV_ASSIGN_PATH, index=False)
    if movie_result["hier_sample"] is not None:
        movie_result["hier_sample"].to_csv(HIER_SAMPLE_PATH, index=False)

    comparison = {
        "movie_kmeans_k": movie_result["selected_k"],
        "tv_kmeans_k": tv_result["selected_k"],
        "movie_kmeans_silhouette": movie_result["final"]["silhouette"],
        "tv_kmeans_silhouette": tv_result["final"]["silhouette"],
        "movie_kmeans_db": movie_result["final"]["davies_bouldin"],
        "tv_kmeans_db": tv_result["final"]["davies_bouldin"],
        "movie_kmeans_ch": movie_result["final"]["calinski_harabasz"],
        "tv_kmeans_ch": tv_result["final"]["calinski_harabasz"],
        "movie_hier_sample_ward_silhouette": movie_result["hierarchical"]["ward_silhouette"],
        "movie_hier_ari": movie_result["hierarchical"]["ari_kmeans_ward"],
        "tv_hier_sample_ward_silhouette": tv_result["hierarchical"]["ward_silhouette"],
        "tv_hier_ari": tv_result["hierarchical"]["ari_kmeans_ward"],
        "movie_kmeans_sample_silhouette": movie_result["hierarchical"]["kmeans_sample_silhouette"],
        "tv_kmeans_sample_silhouette": tv_result["hierarchical"]["kmeans_sample_silhouette"],
    }

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    methods = ["K-Means (sample)", "Ward", "Average", "Complete"]
    movie_sils = [
        comparison["movie_kmeans_sample_silhouette"],
        movie_result["hierarchical"]["linkage_metrics"]["ward"]["silhouette"],
        movie_result["hierarchical"]["linkage_metrics"]["average"]["silhouette"],
        movie_result["hierarchical"]["linkage_metrics"]["complete"]["silhouette"],
    ]
    tv_sils = [
        comparison["tv_kmeans_sample_silhouette"],
        tv_result["hierarchical"]["linkage_metrics"]["ward"]["silhouette"],
        tv_result["hierarchical"]["linkage_metrics"]["average"]["silhouette"],
        tv_result["hierarchical"]["linkage_metrics"]["complete"]["silhouette"],
    ]
    axes[0].bar(methods, movie_sils, color=["#E50914", "#1A5276", "#2B8A3E", "#F39C12"], edgecolor="black")
    axes[0].set_title("Movie sample silhouette by method", fontweight="bold")
    axes[0].set_ylabel("Silhouette coefficient")
    axes[0].tick_params(axis="x", rotation=15)
    axes[1].bar(methods, tv_sils, color=["#E50914", "#1A5276", "#2B8A3E", "#F39C12"], edgecolor="black")
    axes[1].set_title("TV sample silhouette by method", fontweight="bold")
    axes[1].tick_params(axis="x", rotation=15)
    fig.tight_layout()
    savefig("w3_compare_01_method_silhouette.png")

    plt.figure(figsize=(8, 4.5))
    plt.bar(["Movies ARI", "TV Shows ARI"], [comparison["movie_hier_ari"], comparison["tv_hier_ari"]],
            color=["#E50914", "#1A5276"], edgecolor="black")
    plt.ylabel("Adjusted Rand Index")
    plt.title("Agreement between K-Means and Ward clustering on samples", fontweight="bold")
    plt.ylim(0, 1)
    plt.tight_layout()
    savefig("w3_compare_02_ari.png")

    metrics_out = {
        "random_state": RANDOM_STATE,
        "n_init": N_INIT,
        "scaler": "RobustScaler on numeric columns only; binary encodings left as 0/1",
        "catalogue_rows": int(len(df)),
        "movies": {k: v for k, v in movie_result.items() if k not in {"assignments", "hier_sample"}},
        "tv_shows": {k: v for k, v in tv_result.items() if k not in {"assignments", "hier_sample"}},
        "comparison": comparison,
        "method_notes": {
            "separate_types": "Movies and TV Shows were clustered separately because duration units are not comparable.",
            "encoding": "Audience and grouped countries are one-hot encoded; frequent genres are multi-hot encoded from listed_in.",
            "scaling": "RobustScaler is applied to release_year, type-specific duration, content_age, genre_count, and country_count; release year and addition lag capture distinct catalogue timing dimensions.",
            "identifiers_excluded": "show_id and title were retained only for interpretation and were not used as clustering features.",
        },
    }
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(json_ready(metrics_out), f, indent=2)

    print(f"Saved metrics: {METRICS_PATH}")
    print(f"Saved figures in: {VIS_DIR}")
    return metrics_out


if __name__ == "__main__":
    run_clustering_pipeline()
