# Netflix Movies and TV Shows — Data Analytics and Machine Learning

**Yuva Internship — Weeks 1, 2, 3, 4 & 5**
**Student Name:** Vikhyath Bharadwaj K S  
**Domain:** Data Analytics, Data Engineering, Data Visualization, Unsupervised and Supervised Learning
**Dataset:** Netflix Movies and TV Shows by Shivam Bansal (Kaggle)  

---

## Project Overview
This repository contains the Yuva Internship implementation for the **Netflix Movies and TV Shows** dataset.

- **Week 1:** Data acquisition, quality auditing, transparent missing-value imputation, feature engineering, and pipeline setup.
- **Week 2:** Exploratory data analysis, multi-country and genre unnesting, publication-quality visualisations, and inferential tests (chi-square and ANOVA / Kruskal–Wallis).
- **Week 3:** Unsupervised learning — type-separated K-Means clustering, multi-criteria selection of K, agglomerative hierarchical clustering on documented samples, PCA visualisations, and cluster interpretation of catalogue metadata.
- **Week 4:** Supervised learning — leakage-aware Movie/TV Show classification, reusable scikit-learn preprocessing pipelines, stratified cross-validation, model comparison, hyperparameter tuning, and held-out evaluation.

Weeks 1–4 deliverables are preserved. Week 5 adds a reproducible PyTorch CNN workflow, notebook, visualizations, and report.

---

## Internship Objectives

### Week 1
- Organised, reproducible project structure.
- Ingest the raw table (7,787 records × 12 columns) and keep original files.
- Clean without dropping rows.
- Engineer temporal, categorical, and numeric attributes.
- Fully executed notebook and DOCX report.

### Week 2
- EDA across type, year, country, genre, rating, and duration.
- Unnest multi-valued country and genre fields.
- Twelve Week 2 figures in `visualizations/week2/`.
- Hypothesis tests and a Week 2 notebook plus DOCX report.

### Week 3
- Cluster movies and TV shows **separately** so minutes and season counts are never treated as the same unit.
- Encode audience, grouped country, and frequent genres; Robust-scale numeric fields.
- Evaluate K-Means for K = 2…10 (inertia, silhouette, Davies–Bouldin, Calinski–Harabasz, size balance).
- Report **K = 4** as the interpretable primary model for each type, while documenting that **silhouette is highest at K = 2** (older catalogue vs contemporary majority).
- Compare Ward / average / complete linkage on a stratified sample of 250 titles per type.
- Characterise clusters with computed statistics and descriptive labels that do **not** claim recommender or viewer-preference insight.

---

### Week 4
- Predict the dataset's `type` label (Movie or TV Show) from catalog metadata.
- Exclude identifiers, free text, duration, and target-derived Week 1 fields; duration explicitly exposes minutes versus seasons and is leakage for this task.
- Use release year, rating, primary genre/country, genre/country counts, and parsed catalog addition year/month.
- Fit median imputation and scaling for numeric features and infrequent-aware one-hot encoding for categorical features inside a `ColumnTransformer` pipeline.
- Compare logistic regression, decision tree, random forest, KNN, and linear SVM with three-fold stratified CV; tune the best CV model family for macro F1.
- Keep a stratified 20% test set outside training CV and tuning. Random state: 42.
- Interpret coefficients and test errors as metadata associations only; no viewer preference, quality, or business outcome is available in the data.

### Week 5
- Classify handwritten digits (0–9) from 8×8 grayscale images using a two-block PyTorch CNN.
- Uses `sklearn.datasets.load_digits`, the bundled 1,797-example copy of the UCI Optical Recognition of Handwritten Digits dataset, so training needs no network download.
- Stratified train/validation/test split: 70/15/15, seed 42. Normalize pixel values from [0,16] to [0,1].
- CNN: 16- and 32-filter convolution blocks with ReLU and max-pooling; Dense(64), Dropout(0.20), 10 logits. Adam (0.001), cross-entropy, batch 64, 30 epochs, best validation-loss checkpoint.
- Test results: **95.19% accuracy**, **0.951 macro-F1**, **0.952 weighted-F1** on 270 examples. These are one split on a small, low-resolution benchmark, not evidence of writer-independent generalization.

## Dataset
- **Author:** Shivam Bansal (Kaggle)
- **Source:** [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)
- **Raw file:** `dataset/original/netflix_titles.csv`
- **Cleaned:** `dataset/processed/netflix_cleaned.csv`
- **Processed (Week 1 features):** `dataset/processed/netflix_processed.csv`
- **Week 3 assignments:** `dataset/processed/netflix_movie_clusters.csv`, `dataset/processed/netflix_tv_clusters.csv`

---

## Technologies
- **Python 3.12+ (3.13 tested)**
- **Pandas / NumPy** — wrangling and matrices
- **Matplotlib / Seaborn** — charts
- **SciPy** — Week 2 tests; Week 3 hierarchical linkage / dendrograms
- **Scikit-learn** — preprocessing pipelines, classification, clustering, PCA, scaling, digits dataset, and evaluation metrics
- **PyTorch** — Week 5 CNN model, training, and inference
- **python-docx** — reports
- **Jupyter / nbformat / nbconvert** — notebooks

---

## Repository structure
```text
yuva-intern-week1-netflix/
├── dataset/
│   ├── original/netflix_titles.csv
│   └── processed/
│       ├── netflix_cleaned.csv
│       ├── netflix_processed.csv
│       ├── netflix_movie_clusters.csv
│       ├── netflix_tv_clusters.csv
│       └── week3_clustering_metrics.json
├── notebooks/
│   ├── netflix_data_analysis.ipynb          # Week 1
│   ├── week2_eda_visualization.ipynb        # Week 2
│   ├── week3_clustering_analysis.ipynb      # Week 3
│   ├── week4_supervised_learning.ipynb      # Week 4, executed
│   └── week5_deep_learning.ipynb             # Week 5
├── src/
│   ├── data_loading.py / data_cleaning.py / preprocessing.py
│   ├── eda_analysis.py
│   ├── clustering.py
│   └── week5/train.py                         # PyTorch CNN training and evaluation
│   ├── build_notebook.py / build_week2_notebook.py / build_week3_notebook.py
│   └── generate_report.py / generate_week2_report.py / generate_week3_report.py
├── visualizations/
│   ├── week2/
│   ├── week3/
│   └── week5/                               # learning curves, confusion matrix, architecture, errors
├── screenshots/week3/
├── reports/
│   ├── Yuva_Internship_Week1_Report.docx
│   ├── Week2_EDA_Visualization_Report.docx
│   ├── Week3_Clustering_Analysis_Report.docx
│   ├── Week4_Supervised_Learning_Report.docx
│   └── Week5_Deep_Learning_Report.docx
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Setup and how to run

Week 4 files are `notebooks/week4_supervised_learning.ipynb`, `src/week4_supervised_learning.py`, `src/build_week4_notebook.py`, and `src/generate_week4_report.py`. Its metrics are saved to `dataset/processed/week4_model_results.json`; figures are in `visualizations/week4/`.

```bash
git clone https://github.com/vikhyathks-10/yuva-intern-week1-netflix.git
cd yuva-intern-week1-netflix
pip install -r requirements.txt
```

### Week 1
```bash
python src/data_loading.py
python src/data_cleaning.py
python src/preprocessing.py
python src/build_notebook.py
python src/generate_report.py
```

### Week 2
```bash
python src/eda_analysis.py
python src/build_week2_notebook.py
jupyter nbconvert --to notebook --execute --inplace notebooks/week2_eda_visualization.ipynb
python src/generate_week2_report.py
```

### Week 3
```bash
python src/clustering.py
python src/build_week3_notebook.py
jupyter nbconvert --to notebook --execute --inplace notebooks/week3_clustering_analysis.ipynb
python src/generate_week3_report.py
```

### Week 4
```bash
python src/week4_supervised_learning.py
python src/build_week4_notebook.py
jupyter nbconvert --to notebook --execute --inplace notebooks/week4_supervised_learning.ipynb
python src/generate_week4_report.py
```

From the `notebooks/` folder, run `week3_clustering_analysis.ipynb` top to bottom. Paths are relative (`../dataset/...`, `../src`).

---

## Clustering methodology (Week 3)
1. **Split by `type`.** Movie runtime and TV season count are not interchangeable.
2. **Features.** `release_year`, type-specific `duration_int`, `content_age`, `genre_count`, `country_count`; one-hot `target_audience`; one-hot grouped `primary_country` (US, India, UK, Unknown, Other); multi-hot frequent `listed_in` tags. `release_year` and `content_age` capture original release timing and lag until catalogue addition.
3. **Excluded from the matrix.** `show_id`, `title`, description, director, cast (kept only to interpret rows).
4. **Scaling.** RobustScaler on numeric columns only (`random_state=42` for K-Means / PCA / sampling).
5. **K-Means.** `n_init=10`, K in 2…10.
6. **K selection.** Elbow + silhouette + Davies–Bouldin + Calinski–Harabasz + size balance + interpretability. Reported K = 4 for both types; silhouette-best K = 2.
7. **Hierarchical.** Ward (primary), average, and complete on **250 titles** stratified by audience. Sample results are **not** treated as the full-catalogue partition.
8. **Visualisation.** Elbow, silhouette, DB/CH, sizes, PCA, centroids, boxplots, audience stacks, genre heatmaps, dendrograms.

Figures: [`visualizations/week3/`](visualizations/week3/).

---

## Important findings

### Week 4
The selected target is catalog content type. All 7,787 rows have valid target labels in the local snapshot and were eligible after exact duplicate checks. The strongest cross-validation candidate was Linear SVM; its tuned pipeline uses `C=2.0` and balanced class weights. On the held-out 20% test set, tuned Linear SVM achieved **99.68% accuracy**, **0.996 macro F1**, and **0.997 weighted F1** (random state 42). These scores describe separation of this dataset's metadata labels only.

| Model | CV macro F1 | Test accuracy | Test macro F1 | Test weighted F1 |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.992 | 0.996 | 0.995 | 0.996 |
| Decision Tree | 0.992 | 0.995 | 0.994 | 0.995 |
| Random Forest | 0.993 | 0.994 | 0.993 | 0.994 |
| K-Nearest Neighbors | 0.955 | 0.960 | 0.952 | 0.960 |
| Linear SVM | 0.994 | 0.996 | 0.996 | 0.996 |
| Tuned Linear SVM | 0.994 | 0.997 | 0.996 | 0.997 |

The test support is 1,076 Movies and 482 TV Shows. `dataset/processed/week4_model_results.json` contains unrounded metrics, class-level scores, the confusion matrix, and top coefficient magnitudes.

### Week 1
- All 7,787 rows retained; 16 engineered fields including `content_age`, `duration_int`, `primary_genre`, `target_audience`.

### Week 2
- Movies 69.05% (5,377) vs TV Shows 30.95% (2,410).
- Unnested production leaders: United States, India, United Kingdom.
- Movie median runtime 98 minutes; 66.7% of TV shows have one season.

### Week 3 (primary K-Means, K = 4)
**Movies (n = 5,377; K=4 silhouette = 0.187; Davies–Bouldin = 1.519; K=2 silhouette = 0.511)**
| Cluster | Label | n | % | Distinctive observed traits |
|---:|---|---:|---:|---|
| 0 | Contemporary international feature films | 2,563 | 47.67% | Mean 109 min; 74.7% International Movies; non-US majority |
| 1 | Mid-catalogue licensed features | 791 | 14.71% | Mean year ~2003; mean addition lag 16 years; US/India features |
| 2 | Classic and vintage cinema | 188 | 3.50% | Mean year ~1974; mean lag 44 years |
| 3 | Short-form US docs, stand-up, and family titles | 1,835 | 34.13% | Mean 77 min; 68% US; docs / stand-up / family |

**TV Shows (n = 2,410; K=4 silhouette = 0.384; Davies–Bouldin = 0.994; K=2 silhouette = 0.665)**
| Cluster | Label | n | % | Distinctive observed traits |
|---:|---|---:|---:|---|
| 0 | Older acquired television catalogue | 278 | 11.54% | Mean year ~2008; mean lag 9.8 years |
| 1 | Contemporary mostly single-season series | 1,909 | 79.21% | Mean 1.36 seasons; mean year ~2018 |
| 2 | Legacy and vintage television | 27 | 1.12% | Mean year ~1981; small, geometrically distinct |
| 3 | Multi-season continuing series | 196 | 8.13% | Mean 5.71 seasons; 65% US |

**Algorithm comparison (K = 4)**
K-Means vs Ward ARI on samples: movies 0.495; TV 0.448. The K=4 models are practical descriptive partitions, not clear metric optima: K=2 has the best silhouette for both types. Average linkage can post higher *sample* silhouette by isolating compact groups; that is not treated as a better catalogue taxonomy. Full-data K-Means remains the primary reported partition.

These groups are **metadata co-occurrence patterns**. They are not Netflix’s recommendation system and they do not measure viewing behaviour.

---

## Reports and notebooks
- Week 1 report: `reports/Yuva_Internship_Week1_Report.docx`
- Week 2 report: `reports/Week2_EDA_Visualization_Report.docx`
- Week 3 report: `reports/Week3_Clustering_Analysis_Report.docx`
- Week 4 report: `reports/Week4_Supervised_Learning_Report.docx`
- Week 5 report: `reports/Week5_Deep_Learning_Report.docx`
- Week 1 notebook: `notebooks/netflix_data_analysis.ipynb`
- Week 2 notebook: `notebooks/week2_eda_visualization.ipynb`
- Week 3 notebook: `notebooks/week3_clustering_analysis.ipynb`
- Week 4 notebook: `notebooks/week4_supervised_learning.ipynb`
- Week 5 notebook: `notebooks/week5_deep_learning.ipynb`
- Week 5 visualizations: `visualizations/week5/` (training curves, confusion matrix, architecture, misclassified examples)
- Week 2 figures: `visualizations/week2/`
- Week 3 figures: `visualizations/week3/`
- Week 4 figures: `visualizations/week4/`

---

## Run Week 5
Install dependencies from `requirements.txt`, then from the repository root run `python src/week5/train.py` to train and generate plots. Run `notebooks/week5_deep_learning.ipynb` top-to-bottom for the documented exploration and full workflow. The UCI data are bundled through scikit-learn; no dataset download is required. Artifacts under `models/week5/` are ignored by Git and can be regenerated.

## Limitations and future improvements
- Week 3: mixed numeric/binary Euclidean space; silhouette is inflated by recency outliers at K = 2.
- Week 5: only 1,797 low-resolution examples; random partitions do not measure generalization to unseen writers. Consider larger data, repeated seeds, writer-aware splits, and augmentation experiments.
- Frequent-genre multi-hot is incomplete versus all 42 `listed_in` tags.
- Hierarchical analysis is sample-based.
- Two-dimensional PCA discards residual variance (movies ~36% not shown in 2D).
- Possible extensions: Gower mixed-type distance, HDBSCAN, description embeddings, bootstrap stability of K — still without claiming audience-preference results.

---

## Dataset licensing
Week 1–4 Netflix catalogue dataset: educational use as listed on the Kaggle dataset page. Week 5 UCI Optical Recognition of Handwritten Digits: CC BY 4.0; see the [UCI record](https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits).
