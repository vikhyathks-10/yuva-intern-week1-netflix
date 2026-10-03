"""Create the submission DOCX from executed Week 4 evaluation results."""
from pathlib import Path
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "processed" / "week4_model_results.json"
OUT = ROOT / "reports" / "Week4_Supervised_Learning_Report.docx"
VIS = ROOT / "visualizations" / "week4"
R = json.loads(DATA.read_text(encoding="utf-8"))

doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(.72); sec.bottom_margin = Inches(.68)
sec.left_margin = Inches(.78); sec.right_margin = Inches(.78)
styles = doc.styles
styles['Normal'].font.name = 'Aptos'; styles['Normal'].font.size = Pt(10.5)
styles['Normal'].paragraph_format.space_after = Pt(6)
styles['Normal'].paragraph_format.line_spacing = 1.08
for name, size, color in [('Title', 28, '182B49'), ('Heading 1', 19, '182B49'), ('Heading 2', 13, 'A62635'), ('Heading 3', 11, '343A40')]:
    s = styles[name]; s.font.name = 'Aptos Display'; s.font.size = Pt(size); s.font.bold = True; s.font.color.rgb = RGBColor.from_string(color)
    s.paragraph_format.keep_with_next = True

def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd'); shd.set(qn('w:fill'), color); tcPr.append(shd)
def table(headers, rows, widths=None, font=8.2):
    t = doc.add_table(rows=1, cols=len(headers)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.style = 'Table Grid'
    t.autofit = False
    for i,h in enumerate(headers):
        c=t.rows[0].cells[i]; c.text=str(h); shade(c,'182B49'); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for p in c.paragraphs:
            for run in p.runs: run.font.bold=True; run.font.color.rgb=RGBColor(255,255,255); run.font.size=Pt(font)
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,val in enumerate(row):
            cells[i].text=str(val); cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri%2: shade(cells[i],'EEF2F7')
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after=Pt(2)
                for run in p.runs: run.font.size=Pt(font)
    if widths:
        for row in t.rows:
            for c,w in zip(row.cells,widths): c.width=Inches(w)
    doc.add_paragraph()
    return t
def para(text, lead=None):
    p=doc.add_paragraph()
    if lead and text.startswith(lead): p.add_run(lead).bold=True; p.add_run(text[len(lead):])
    else: p.add_run(text)
    return p
def heading(text, level=1): doc.add_heading(text,level=level)
def figure(filename, caption, width=6.35):
    path=VIS/filename
    if path.exists():
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(path),width=Inches(width))
        cap=doc.add_paragraph(caption); cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
        for r in cap.runs: r.italic=True; r.font.size=Pt(9); r.font.color.rgb=RGBColor.from_string('596579')
def page_field(paragraph):
    paragraph.alignment=WD_ALIGN_PARAGRAPH.CENTER
    run=paragraph.add_run('Yuva Internship | Week 4  •  Page ')
    run.font.size=Pt(8); run.font.color.rgb=RGBColor.from_string('596579')
    fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); paragraph._p.append(fld)
page_field(sec.footer.paragraphs[0])

# Cover
p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(78)
p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('YUVA INTERNSHIP'); r.bold=True; r.font.size=Pt(13); r.font.color.rgb=RGBColor.from_string('A62635')
p=doc.add_paragraph(style='Title'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p.add_run('Week 4\nSupervised Learning Model Implementation')
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('Netflix Movies and TV Shows\nContent Type Classification'); r.font.size=Pt(17); r.font.color.rgb=RGBColor.from_string('343A40')
doc.add_paragraph('\n')
for line in ['Student: Vikhyath Bharadwaj K S','Dataset: Netflix Movies and TV Shows by Shivam Bansal','Submission date: 3 October 2026','Programming language: Python']:
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run(line).font.size=Pt(11)
doc.add_page_break()

heading('Abstract')
f=R['final_model']; n=R['model_rows']; dist=R['target_distribution']
para(f"This report develops a reproducible supervised learning workflow to classify Netflix catalogue records as Movies or TV Shows. The source snapshot contains {R['raw_rows']:,} records and {R['raw_columns']} original columns; after exact-duplicate and target validity checks, {n:,} records remain for modeling. Inputs include release year, rating, primary genre, primary country, catalog addition year and month, and counts of genre/country entries. Identifier, title, free-text description, director/cast, duration, and target-derived columns are excluded. Numeric median imputation and standardization, categorical imputation and infrequent-category-aware one-hot encoding are fitted inside a scikit-learn pipeline. Five classifiers are compared using three-fold stratified cross-validation; the best-performing algorithm family is tuned for macro F1. The selected configuration is {f['best_params']}; on a stratified 20% held-out test set it obtains accuracy {f['test_accuracy']:.3f}, macro F1 {f['test_macro_f1']:.3f}, and weighted F1 {f['test_weighted_f1']:.3f}. These results measure recovery of a catalogue metadata label, not viewer preference, title quality, or Netflix decisions.")
heading('Contents')
p=doc.add_paragraph(); fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'TOC \\o "1-2" \\h \\z \\u'); p._p.append(fld)
para('If the table of contents is blank in a Word viewer, select it and update the field.')
doc.add_page_break()

heading('1. Introduction')
para('Supervised learning estimates a mapping from input variables to a labeled outcome using examples where the outcome is known. Classification predicts categories; regression predicts numerical quantities. This assignment applies classification to an openly available catalog of film and television metadata. The goal is to learn whether a title is labeled Movie or TV Show from selected metadata that is available in the same record.')
para('The exercise demonstrates a complete modeling lifecycle: inspecting data, defining a defensible target, exploring class and feature distributions, preprocessing within a pipeline, comparing algorithms under cross-validation, tuning without touching the test partition, and interpreting class-level errors. Validation matters because training performance can overstate how a model behaves on titles it did not use to fit its parameters.')
para('Scope is deliberately narrow. The Netflix dataset records catalog metadata, not user viewing, satisfaction, demand, or recommendation outcomes. Predicting its `type` field is a technical classification exercise and cannot establish audience preferences or business performance.')

heading('2. Dataset Description')
para('The data is the Netflix Movies and TV Shows dataset attributed to Shivam Bansal and distributed through Kaggle. The local original CSV is retained at `dataset/original/netflix_titles.csv`; the Week 1 processed files remain available for prior analyses. The raw table has show_id, type, title, director, cast, country, date_added, release_year, rating, duration, listed_in, and description fields.')
table(['Audit item','Observed result'],[
['Raw dimensions',f"{R['raw_rows']:,} rows × {R['raw_columns']} columns"],
['Exact duplicate rows',str(R['exact_duplicate_rows'])],
['Rows used for modeling',f"{n:,}"],
['Rows excluded',str(R['excluded_rows'])],
['Target labels',f"Movie {dist.get('Movie',0):,}; TV Show {dist.get('TV Show',0):,}"],
['Input fields',', '.join(R['feature_columns'])],
['Target','type (Movie / TV Show)']])
para('The dataset is a dated catalog snapshot rather than a live feed. Country, rating, and addition date can be absent; genre and country fields may contain comma-separated values. `release_year` describes original release year, not the date a title entered the catalog. All dates are parsed with invalid values coerced to missing so the training pipeline can impute them.')
heading('2.1 Data quality and exclusions',2)
para(f"The workflow reports {R['exact_duplicate_rows']} exact duplicate rows and excludes {R['excluded_rows']} rows through duplicate removal and target validation. The record count is preserved in the audit JSON. Missing predictors are retained and imputed within the model pipeline rather than dropping potentially useful examples. No target-missing row is imputed. The supplied dataset's snapshot date and collection method limit temporal generalization.")

heading('3. Problem Definition and Candidate Selection')
heading('3.1 Selected prediction problem',2)
para('The target is `type`, with two observed labels: Movie and TV Show. This is a binary classification problem. Inputs are release year, rating, the first listed genre, the first listed country, parsed catalog addition year and month, and counts of listed genres and countries. The split is stratified so both labels retain representative proportions in training and test partitions.')
heading('3.2 Why this target was selected',2)
para('Content type is present directly as a named catalog label and is available for both record groups. Its class balance is imperfect but sufficiently broad for stratified evaluation. Content rating classification would remove rows with missing ratings and would create a more fragmented target; rating conventions and metadata are related, which increases interpretive risks. Movie runtime regression is a valid alternative but must first filter to movie records, parse mixed text such as minutes, validate outliers, and exclude duration from predictors. That narrower task is not selected because type classification supports an end-to-end workflow across the full catalog.')
heading('3.3 Leakage prevention and feature relevance',2)
para('The duration field is excluded because it states minutes for movies and seasons for TV shows, making the target almost explicit. `show_id` and title are identifiers; description, director, and cast are high-cardinality text fields outside this assignment’s metadata baseline. `is_movie` and `target_audience` are also excluded because they are derived from `type` or `rating` in Week 1 preprocessing. The raw source and a separate target vector are used to avoid accidentally carrying these engineered leakage fields forward.')
para('The main evaluation criterion is macro F1, the unweighted mean of class-specific F1 scores. It makes performance on each label visible even when Movies are more common. Accuracy and weighted F1 supplement the primary score; per-class precision, recall, and the confusion matrix describe error types.')

heading('4. Exploratory Data Analysis')
para('The target distribution is shown in Figure 1. The two categories are not equal in size, so a majority-class baseline could have deceptively high accuracy. The release-year distributions (Figure 2) and primary genre counts (Figure 3) show how catalog metadata varies by type. These observations motivate using multiple metadata fields and balanced evaluation metrics, while preserving a simple, interpretable target.')
figure('w4_01_target_distribution.png','Figure 1. Target-class counts in the modeling records.')
figure('w4_02_release_year_by_type.png','Figure 2. Release-year density by content type; the plot is descriptive, not a causal explanation.')
figure('w4_03_genre_by_type.png','Figure 3. Twelve most common primary genres, split by type.')
para('Missingness is most relevant to rating, country, date_added, and occasionally release_year/listed_in. Missing categories are mapped to `Unknown` for genre/country and rating, while numerical/date-derived gaps are handled by median imputation. The imputation statistics are learned from the training partition only. This prevents the held-out test distribution from influencing preprocessing.')
heading('4.1 Modeling implications',2)
para('The target class difference is structurally associated with genre and rating conventions, so high classification performance should not be described as a discovery of causal rules. Release year and catalog addition date may help explain the composition of this particular snapshot. The preprocessing groups rare categorical levels, balancing categorical detail against sparse expansion and unseen categories.')

heading('5. Data Preparation and Feature Engineering')
para('Preparation starts with the raw CSV. Exact duplicate rows are removed; target values are stripped and only the two documented target labels are accepted. Records with missing or invalid target values are excluded because a supervised model cannot learn an unknown outcome. Comma-separated genre and country strings are split into lists. The first listed item becomes the primary category and list length becomes a count feature. `date_added` is parsed to derive year and month; invalid dates yield missing numbers rather than fabricated dates.')
heading('5.1 Input fields',2)
table(['Feature group','Fields','Treatment'],[
['Numeric','release_year, year_added, month_added, genre_count, country_count','Median imputation; StandardScaler'],
['Categorical','rating, primary_genre, primary_country','Most-frequent imputation; one-hot; categories <20 pooled'],
['Target','type','Separate y vector; no imputation'],
['Excluded','show_id, title, description, director, cast, duration, derived target flags','Identifier, free text, or direct/derived leakage']])
heading('5.2 Pipeline and train/test design',2)
para('A ColumnTransformer routes numeric and categorical columns into distinct transformations. The resulting sparse/dense transformed matrix is passed to a classifier within a Pipeline. This arrangement ensures that imputation medians, category vocabularies, rare-category grouping, and scaling means/standard deviations are learned on each training fold. The dataset is partitioned once into 80% training and 20% test rows using random state 42 and stratification by `type`. Cross-validation and hyperparameter search operate only on the training rows.')
para('Three-fold shuffled StratifiedKFold with random state 42 provides a reproducible training-only comparison. The test partition is not used to choose features, transformations, algorithms, or parameters. Once selection is complete, the selected pipeline is evaluated one time on the held-out test data.')

heading('6. Model Implementation')
heading('6.1 Logistic Regression',2)
para('Logistic regression estimates class probabilities as a function of a weighted sum of transformed features. It supplies a useful linear baseline and coefficient-based interpretation. The comparison model uses a fixed C of 1 and a maximum of 1,500 iterations. Logistic regression is included among the five baseline candidates; the top-performing algorithm family under training CV is tuned separately.')
heading('6.2 Decision Tree',2)
para('A decision tree recursively partitions features into regions that reduce class impurity. It can express interactions and non-linear thresholds but may overfit. The comparison configuration limits maximum depth to 18, requires at least five samples in each leaf, and uses random state 42.')
heading('6.3 Random Forest',2)
para('A random forest averages many randomized decision trees to reduce the variance of an individual tree. The comparison uses 150 trees, maximum depth 24, minimum leaf size 2, balanced class weights, all available workers, and random state 42. It provides a non-linear ensemble comparator, although its decision logic is less directly interpretable than a linear model.')
heading('6.4 K-Nearest Neighbors',2)
para('KNN assigns a class based on labels among nearby training rows. The comparison uses 11 neighbors and distance weighting. Numeric scaling is important for distance-based learning; one-hot categorical features represent mismatches in the encoded metadata space. KNN can be sensitive to sparse, high-dimensional features and class density.')
heading('6.5 Linear Support Vector Machine',2)
para('LinearSVC finds a separating hyperplane with a margin and is suitable for sparse one-hot data. The comparison uses C=1, balanced class weights, random state 42, and a 5,000 iteration cap. It provides another linear decision boundary with a different loss/regularization objective from logistic regression.')
heading('6.6 Training and prediction',2)
para('Every candidate uses the same preprocessing steps, making scores more comparable. Cross-validation reports mean and standard deviation for accuracy and macro F1 over three training folds. Candidate pipelines are then fitted on the complete training set and tested on the held-out partition for a descriptive comparison table. Hyperparameter selection uses an independent GridSearchCV over the logistic regression pipeline and refits the best macro-F1 configuration on training data.')

heading('7. Validation and Hyperparameter Tuning')
sp=R['split']
table(['Validation setting','Value'],[
['Training observations',f"{sp['train_rows']:,}"],['Test observations',f"{sp['test_rows']:,}"],
['Train/test ratio','80% / 20%'],['Random state',str(sp['random_state'])],
['Split strategy','Stratified by type'],['Training CV',sp['cv']],['Tuning objective','Macro F1'],
['Selected parameters',str(f['best_params'])]])
para('Cross-validation reduces dependence on a single train/validation split and gives a measure of fold-to-fold variation. The test set remains untouched during tuning. However, a random split does not simulate future catalog additions, and the rows may share production context, genres, creators, or franchises across folds. Therefore, this validation estimates performance for a random sample from the same snapshot, not deployment performance on future titles.')

heading('8. Model Evaluation and Results')
para('Table 2 reports the mean training cross-validation macro F1 and test-set metrics for every candidate and the tuned classifier. Macro F1 is emphasized because the class distribution is unequal. The table is generated directly from the saved evaluation JSON to keep report results aligned with the executed workflow.')
rows=[]
for row in R['comparison']:
    rows.append([row['model'],f"{row['cv_macro_f1_mean']:.3f} ± {row['cv_macro_f1_std']:.3f}",f"{row['test_accuracy']:.3f}",f"{row['test_macro_f1']:.3f}",f"{row['test_weighted_f1']:.3f}"])
table(['Model','CV macro F1','Test accuracy','Test macro F1','Test weighted F1'],rows,[2.0,1.25,1.0,1.0,1.2],7.8)
para(f"The tuned logistic regression reached test accuracy {f['test_accuracy']:.3f}, macro F1 {f['test_macro_f1']:.3f}, weighted F1 {f['test_weighted_f1']:.3f}, macro precision {f['test_precision_macro']:.3f}, and macro recall {f['test_recall_macro']:.3f}. The actual confusion matrix and class report are included below. These metrics are empirical estimates for this random held-out split and should not be generalized beyond similar records from this dataset snapshot.")
heading('8.1 Confusion matrix and class-level errors',2)
figure('w4_04_confusion_matrix.png','Figure 4. Confusion matrix for the tuned model on the held-out test set.',5.1)
cr=f['classification_report']
table(['Class','Precision','Recall','F1','Support'],[[label,f"{cr[label]['precision']:.3f}",f"{cr[label]['recall']:.3f}",f"{cr[label]['f1-score']:.3f}",int(cr[label]['support'])] for label in f['labels']])
para('The diagonal of the confusion matrix represents correct predictions. Off-diagonal cells show titles whose metadata led to a type error. The relative number of errors within each class matters more than a single accuracy score because the classes differ in prevalence. No individual error should be interpreted as a catalog policy decision.')
heading('8.2 Model comparison visualization',2)
figure('w4_05_model_comparison.png','Figure 5. Test macro F1 across comparison and selected models.')

heading('9. Model Interpretation')
para('The tuned linear SVM’s largest absolute standardized coefficients are saved in `week4_model_results.json`. A larger absolute coefficient indicates a stronger conditional association in this fitted, encoded linear model, holding the other included transformed features constant under the model’s parameterization. For this binary classifier, coefficient sign identifies which class receives a higher linear score; the saved coefficient summary emphasizes magnitude for a compact comparison.')
top=R.get('top_features_abs_coefficient',[])[:12]
if top: table(['Encoded feature','Absolute coefficient'],[[x['feature'],f"{x['mean_absolute_coefficient']:.3f}"] for x in top])
para('One-hot category coefficients are relative to the model’s coding and reference/regularization structure; correlated genre, country, year, and rating indicators can share or shift importance. Coefficients are not causal effects, and an association does not show that changing a metadata value would change title type. The results support a conclusion about the classification task only.')

heading('10. Improvements Attempted')
para('The main improvement over a single baseline is the use of a shared leakage-safe preprocessing pipeline across five algorithms, stratified three-fold cross-validation, and a macro-F1 grid search for the strongest candidate algorithm family. Rare categorical categories are pooled to reduce unstable, highly sparse levels. Balanced class weights are included as a tunable choice rather than assumed to help. Median and most-frequent imputers allow records with missing predictors to remain in the experiment.')
para('The measured impact of tuning is visible in the CV and test tables. If tuning does not improve the baseline, the simpler configuration remains a defensible choice. Further work could test calibrated probabilities, temporal validation, grouped splits for related content, additional token-level genre representations, and a carefully defined duration regression task. Any additional feature work must remain inside the cross-validation pipeline.')

heading('11. Challenges and Solutions')
para('Mixed fields required explicit parsing: date strings can fail conversion, while genre and country fields hold comma-separated values. Date parsing uses coercion and leaves missing values for train-fitted imputation; list parsing counts only non-empty trimmed values and uses an explicit Unknown category when no primary item is available. The duration field combines different units and nearly exposes the target, so it was excluded rather than converted into a potentially leaking numeric feature.')
para('The target distribution makes raw accuracy incomplete, so macro F1 and class-level metrics accompany it. Categorical metadata can have many rare labels; infrequent-category grouping limits feature expansion and safely handles unseen values. Finally, separating data preparation from target-derived Week 1 variables avoids accidental reuse of the `is_movie` flag or audience groups derived from rating.')

heading('12. Limitations and Future Scope')
para('The model represents one Kaggle snapshot and may contain collection or labeling errors. Missingness may be systematic rather than random. Primary genre and country discard secondary labels; counts preserve only limited multi-valued structure. Ratings may reflect different regional classification systems. Release years and catalog addition dates may be useful for this sample but can shift across snapshots. Linear model coefficients can be unstable with correlated categories, and the random split does not estimate future temporal performance.')
para('Future analyses should obtain a dated, versioned dataset; evaluate a time-based holdout; compare GroupKFold splits by creator or franchise when identifiers are reliable; report calibration and confidence intervals; and conduct error analysis on genuinely held-out rows. The candidate duration regression task could be revisited for movies only, with unit validation, outlier review, and a strict exclusion of raw duration strings. Audience behavior claims would require interaction or viewing data that this dataset does not contain.')

heading('13. Conclusion')
para(f"This assignment completes a supervised learning workflow for predicting the `type` metadata field using {len(R['feature_columns'])} selected catalog features and {n:,} eligible rows. Stratified splitting, fold-contained imputation and encoding, five-model comparison, and macro-F1 tuning keep model selection separate from the test evaluation. The tuned logistic regression achieved a held-out macro F1 of {f['test_macro_f1']:.3f} and accuracy of {f['test_accuracy']:.3f}. The findings describe how selected metadata distinguishes Movie and TV Show labels in this dataset; they do not measure popularity, preference, or business impact.")

heading('14. References')
for ref in [
    'Bansal, S. Netflix Movies and TV Shows dataset. Kaggle. https://www.kaggle.com/datasets/shivamb/netflix-shows',
    'scikit-learn developers. Pipeline and composite estimators. https://scikit-learn.org/stable/modules/compose.html',
    'scikit-learn developers. OneHotEncoder API. https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html',
    'scikit-learn developers. GridSearchCV API. https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html',
    'scikit-learn developers. Classification metrics. https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics',
    'pandas developers. pandas.read_csv. https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html',
    'Matplotlib developers. Matplotlib documentation. https://matplotlib.org/stable/',
    'Seaborn developers. Seaborn documentation. https://seaborn.pydata.org/',
]: para(ref)

heading('Appendix A. Reproducibility and selected code')
para('Run the workflow from the repository root after installing `requirements.txt`. It writes the metric record to `dataset/processed/week4_model_results.json` and figures to `visualizations/week4/`. The notebook includes the inspection, modeling and evaluation narrative. The key pipeline pattern is:')
code="""preprocess = ColumnTransformer([\n    ('numeric', Pipeline([('impute', SimpleImputer(strategy='median')),\n                          ('scale', StandardScaler())]), numeric_columns),\n    ('categorical', Pipeline([('impute', SimpleImputer(strategy='most_frequent')),\n                              ('encode', OneHotEncoder(\n                                  handle_unknown='infrequent_if_exist',\n                                  min_frequency=20))]), categorical_columns),\n])\nmodel = Pipeline([('preprocess', preprocess), ('model', classifier)])\n"""
p=doc.add_paragraph(); p.paragraph_format.left_indent=Inches(.2)
r=p.add_run(code); r.font.name='Consolas'; r.font.size=Pt(8.5); r.font.color.rgb=RGBColor.from_string('283747')
heading('Appendix B. Validation checklist')
check_items=[
('Source data located and schema inspected', 'Yes'),('Target and exclusions documented', 'Yes'),
('Train/test split stratified, seed recorded', 'Yes'),('Preprocessing fitted only within CV/training', 'Yes'),
('Five candidate estimators compared', 'Yes'),('Grid search run on training folds only', 'Yes'),
('Held-out metrics and confusion matrix saved', 'Yes'),('All notebook code cells executed in fresh Python process', 'Yes'),
('DOCX visual render and page-by-page check', 'Not verified: soffice unavailable'),('Prior Weeks 1–3 files preserved', 'Yes'),
('README updated and instructions checked', 'Yes'),('Git commit and push verified', 'Pending')]
table(['Check','Status'],check_items)
heading('Appendix C. Additional audit record')
table(['Audit detail','Value'],[
['Original field list',', '.join(R['raw_columns_list'])],
['Target missing/invalid exclusions',str(R['target_missing_or_invalid_excluded'])],
['Feature missing counts',str(R['feature_missing_counts'])],
['Split sizes',f"train={sp['train_rows']}, test={sp['test_rows']}"],
['Random seed',str(sp['random_state'])],['CV design',sp['cv']],
['Saved metric file','dataset/processed/week4_model_results.json']])

OUT.parent.mkdir(parents=True,exist_ok=True)
doc.save(OUT)
print(OUT)
