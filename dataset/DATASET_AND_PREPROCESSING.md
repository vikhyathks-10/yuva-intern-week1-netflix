# Dataset and preprocessing notes

## Source file
- **Name:** Netflix Movies and TV Shows
- **Publisher/author:** Shivam Bansal (as credited by Kaggle)
- **Source:** https://www.kaggle.com/datasets/shivamb/netflix-shows
- **Access checked:** 3 October 2026
- **Local file:** `dataset/original/netflix_titles.csv` (existing repository snapshot, 7,787 rows × 12 fields)
- **Use:** educational analysis; verify Kaggle dataset terms before redistributing outside this repository.

## Analytical target
`catalogue_delay_years = calendar year(date_added) - release_year`. This integer difference is only a catalogue metadata proxy. It is not a license duration, a precise elapsed time, or an outcome directly caused by Netflix.

## Processing
The pipeline retains the raw CSV untouched. It parses `date_added` with invalid values coerced to missing; `release_year` is numeric; duration is converted to the leading integer; and first comma-delimited values define `primary_genre` and `primary_country`. Genre and country counts are derived from comma-delimited values. Duplicate source rows are counted and reported. Rows with missing target ingredients or negative target are excluded only from modeling; high nonnegative values remain.

Predictors: `type`, `rating`, `primary_genre`, `primary_country`, `genre_count`, `country_count`, `duration_value`. `year_added` and `release_year` are deliberately excluded from predictors because their difference defines the target. Imputation, encoding, and scaling are fit within the scikit-learn pipeline and cross-validation folds.

See `dataset/processed/week6_data_quality.json` and `dataset/processed/week6_model_results.json` for run-specific row counts and metrics.
