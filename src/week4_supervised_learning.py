"""Reproducible Week 4 supervised classification workflow.

Run from any directory with: python src/week4_supervised_learning.py
All learned preprocessing is inside the sklearn Pipeline and fit only on training folds.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score)
from sklearn.model_selection import (GridSearchCV, StratifiedKFold, cross_validate,
                                     train_test_split)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "dataset" / "original" / "netflix_titles.csv"
OUT = ROOT / "dataset" / "processed" / "week4_model_results.json"
VIS = ROOT / "visualizations" / "week4"
SEED = 42
TARGET = "type"
CATEGORICAL = ["rating", "primary_genre", "primary_country"]
NUMERIC = ["release_year", "year_added", "month_added", "genre_count", "country_count"]
FEATURES = CATEGORICAL + NUMERIC


def prepare_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, dict]:
    before = len(df)
    required = ["type", "release_year", "rating", "listed_in", "country", "date_added"]
    absent = sorted(set(required) - set(df.columns))
    if absent:
        raise ValueError(f"Required dataset columns are missing: {absent}")
    duplicates = int(df.duplicated().sum())
    valid_original_target = df[TARGET].astype("string").str.strip().isin(["Movie", "TV Show"])
    invalid_original_target = int((~valid_original_target).sum())
    work = df.drop_duplicates().copy()
    work[TARGET] = work[TARGET].astype("string").str.strip()
    work = work[work[TARGET].isin(["Movie", "TV Show"])].copy()
    dropped = before - len(work)

    def parts(value):
        if pd.isna(value) or not str(value).strip():
            return []
        return [p.strip() for p in str(value).split(",") if p.strip()]

    work["primary_genre"] = work["listed_in"].map(lambda x: (parts(x) or ["Unknown"])[0])
    work["genre_count"] = work["listed_in"].map(lambda x: len(parts(x)))
    work["primary_country"] = work["country"].map(lambda x: (parts(x) or ["Unknown"])[0])
    work["country_count"] = work["country"].map(lambda x: len(parts(x)))
    date = pd.to_datetime(work["date_added"], errors="coerce")
    work["year_added"] = date.dt.year
    work["month_added"] = date.dt.month
    work["release_year"] = pd.to_numeric(work["release_year"], errors="coerce")
    work["rating"] = work["rating"].fillna("Unknown").astype(str)
    X = work[FEATURES].copy()
    y = work[TARGET].astype(str).copy()
    summary = {
        "raw_rows": before, "raw_columns": len(df.columns), "raw_columns_list": list(df.columns),
        "exact_duplicate_rows": duplicates, "model_rows": len(work), "excluded_rows": dropped,
        "target_missing_or_invalid_excluded": invalid_original_target,
        "target_distribution": y.value_counts().to_dict(),
        "feature_missing_counts": X.isna().sum().to_dict(),
        "feature_columns": FEATURES, "target": TARGET,
        "candidate_regression_feasibility": "Not used: duration is observed only as mixed text and only movie rows carry minutes; identifying the target subset and parsing it narrows scope. Content type has complete, meaningful labels across the catalogue.",
        "content_rating_feasibility": "Not selected: rating labels are missing and unevenly distributed, and content type/genre metadata may encode rating conventions rather than independent audience suitability."
    }
    return X, y, summary


def build_pipeline(model):
    prep = ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")),
                              ("scale", StandardScaler())]), NUMERIC),
        ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                                  ("encode", OneHotEncoder(handle_unknown="infrequent_if_exist",
                                                           min_frequency=20))]), CATEGORICAL),
    ], remainder="drop")
    return Pipeline([("preprocess", prep), ("model", model)])


def run_analysis() -> dict:
    sns.set_theme(style="whitegrid", palette="deep")
    VIS.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(RAW)
    X, y, summary = prepare_frame(raw)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=SEED, stratify=y)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED)
    candidates = {
        "Logistic Regression": LogisticRegression(max_iter=1500, random_state=SEED),
        "Decision Tree": DecisionTreeClassifier(max_depth=18, min_samples_leaf=5, random_state=SEED),
        "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=24, min_samples_leaf=2,
                                                class_weight="balanced", n_jobs=-1, random_state=SEED),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=11, weights="distance", n_jobs=-1),
        "Linear SVM": LinearSVC(C=1.0, class_weight="balanced", random_state=SEED, max_iter=5000),
    }
    cv_rows = []
    for name, estimator in candidates.items():
        scores = cross_validate(build_pipeline(estimator), X_train, y_train, cv=cv,
                                scoring={"accuracy": "accuracy", "macro_f1": "f1_macro"},
                                n_jobs=1, return_train_score=False)
        cv_rows.append({"model": name, "cv_accuracy_mean": float(scores["test_accuracy"].mean()),
                        "cv_accuracy_std": float(scores["test_accuracy"].std()),
                        "cv_macro_f1_mean": float(scores["test_macro_f1"].mean()),
                        "cv_macro_f1_std": float(scores["test_macro_f1"].std()),
                        "estimator": estimator})

    tune = GridSearchCV(
        build_pipeline(LinearSVC(random_state=SEED, max_iter=5000)),
        {"model__C": [0.1, 0.5, 1.0, 2.0], "model__class_weight": [None, "balanced"]},
        scoring={"accuracy": "accuracy", "macro_f1": "f1_macro"}, cv=cv, n_jobs=1,
        refit="macro_f1", return_train_score=False)
    tune.fit(X_train, y_train)
    pred = tune.predict(X_test)
    labels = ["Movie", "TV Show"]
    comparison = []
    for row in cv_rows:
        fitted = build_pipeline(row["estimator"]).fit(X_train, y_train)
        p = fitted.predict(X_test)
        comparison.append({k: v for k, v in row.items() if k != "estimator"} | {
            "test_accuracy": float(accuracy_score(y_test, p)),
            "test_macro_f1": float(f1_score(y_test, p, average="macro")),
            "test_weighted_f1": float(f1_score(y_test, p, average="weighted"))})
    final_result = {"model": "Tuned Linear SVM",
                    "cv_accuracy_mean": float(tune.cv_results_["mean_test_accuracy"][tune.best_index_]),
                    "cv_accuracy_std": float(tune.cv_results_["std_test_accuracy"][tune.best_index_]),
                    "cv_macro_f1_mean": float(tune.best_score_), "cv_macro_f1_std": float(tune.cv_results_["std_test_macro_f1"][tune.best_index_]),
                    "test_accuracy": float(accuracy_score(y_test, pred)),
                    "test_macro_f1": float(f1_score(y_test, pred, average="macro")),
                    "test_weighted_f1": float(f1_score(y_test, pred, average="weighted")),
                    "test_precision_macro": float(precision_score(y_test, pred, average="macro")),
                    "test_recall_macro": float(recall_score(y_test, pred, average="macro")),
                    "best_params": tune.best_params_,
                    "classification_report": classification_report(y_test, pred, output_dict=True),
                    "confusion_matrix": confusion_matrix(y_test, pred, labels=labels).tolist(), "labels": labels}
    comparison.append(final_result)
    summary.update({"split": {"train_rows": len(X_train), "test_rows": len(X_test), "test_size": .2,
                               "random_state": SEED, "stratified": True, "cv": "3-fold shuffled stratified CV"},
                    "comparison": comparison, "final_model": final_result,
                    "interpretation": "The model predicts a catalogue metadata label. It does not predict viewer preference, popularity, quality, recommendations or future Netflix decisions."})

    # Target balance and modeling-focused feature relationships.
    fig, ax = plt.subplots(figsize=(7, 4.5)); sns.countplot(data=pd.DataFrame({"type": y}), x="type", ax=ax)
    ax.set(title="Target distribution: catalogue type", xlabel="Content type", ylabel="Titles")
    fig.tight_layout(); fig.savefig(VIS / "w4_01_target_distribution.png", dpi=180); plt.close(fig)
    rel = pd.DataFrame({"type": y, "release_year": X.release_year}).dropna()
    fig, ax = plt.subplots(figsize=(8, 4.5)); sns.histplot(data=rel, x="release_year", hue="type", bins=35, element="step", stat="density", common_norm=False, ax=ax)
    ax.set(title="Release-year distributions by content type", xlabel="Release year", ylabel="Density")
    fig.tight_layout(); fig.savefig(VIS / "w4_02_release_year_by_type.png", dpi=180); plt.close(fig)
    top = pd.DataFrame({"genre": X.primary_genre, "type": y}).groupby(["genre", "type"]).size().unstack(fill_value=0)
    top = top.loc[top.sum(axis=1).nlargest(12).index]
    fig, ax = plt.subplots(figsize=(9, 5.5)); top.plot(kind="barh", stacked=True, ax=ax, color=["#b51f2b", "#343a40"])
    ax.set(title="Most common primary genres by type", xlabel="Titles", ylabel="Primary genre"); ax.invert_yaxis()
    fig.tight_layout(); fig.savefig(VIS / "w4_03_genre_by_type.png", dpi=180); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 5)); sns.heatmap(final_result["confusion_matrix"], annot=True, fmt="d", cmap="Blues",
        xticklabels=labels, yticklabels=labels, ax=ax); ax.set(title="Held-out test confusion matrix", xlabel="Predicted", ylabel="Actual")
    fig.tight_layout(); fig.savefig(VIS / "w4_04_confusion_matrix.png", dpi=180); plt.close(fig)
    comp = pd.DataFrame(comparison).sort_values("test_macro_f1", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 5)); ax.barh(comp.model, comp.test_macro_f1, color="#b51f2b")
    ax.set(xlim=(0, 1), title="Held-out macro F1 by model", xlabel="Macro F1", ylabel="Model")
    fig.tight_layout(); fig.savefig(VIS / "w4_05_model_comparison.png", dpi=180); plt.close(fig)

    # Explain tuned model through signed standardized logistic coefficients.
    fitted = tune.best_estimator_
    names = fitted.named_steps["preprocess"].get_feature_names_out()
    coef = fitted.named_steps["model"].coef_
    if coef.shape[0] == 1:
        importance = np.abs(coef[0])
    else:
        importance = np.mean(np.abs(coef), axis=0)
    top_idx = np.argsort(importance)[-15:]
    summary["top_features_abs_coefficient"] = [{"feature": str(names[i]), "mean_absolute_coefficient": float(importance[i])} for i in top_idx[::-1]]
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=lambda o: float(o) if isinstance(o, np.floating) else str(o))
    print(f"Raw rows: {summary['raw_rows']}; modeling rows: {summary['model_rows']}; features: {len(FEATURES)}")
    print(pd.DataFrame(comparison)[["model", "cv_macro_f1_mean", "test_accuracy", "test_macro_f1", "test_weighted_f1"]].to_string(index=False))
    print("Best parameters:", tune.best_params_)
    print("Classification report:\n", classification_report(y_test, pred))
    print("Results:", OUT)
    return summary


if __name__ == "__main__":
    run_analysis()
