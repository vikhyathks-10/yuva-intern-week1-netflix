import os
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))

raw_path = os.path.join(PROJECT_DIR, 'dataset', 'original', 'netflix_titles.csv')
clean_path = os.path.join(PROJECT_DIR, 'dataset', 'processed', 'netflix_cleaned.csv')
proc_path = os.path.join(PROJECT_DIR, 'dataset', 'processed', 'netflix_processed.csv')
nb_path = os.path.join(PROJECT_DIR, 'notebooks', 'netflix_data_analysis.ipynb')
report_path = os.path.join(PROJECT_DIR, 'reports', 'Yuva_Internship_Week1_Report.docx')
vis_dir = os.path.join(PROJECT_DIR, 'visualizations')

checklist = [
    ("Raw Dataset Exists", os.path.exists(raw_path)),
    ("Cleaned Dataset Exists", os.path.exists(clean_path)),
    ("Processed Dataset Exists", os.path.exists(proc_path)),
    ("Jupyter Notebook Exists", os.path.exists(nb_path)),
    ("DOCX Report Exists", os.path.exists(report_path)),
    ("Visualizations Folder Exists", os.path.exists(vis_dir) and len(os.listdir(vis_dir)) >= 10),
    ("README.md Exists", os.path.exists(os.path.join(PROJECT_DIR, 'README.md'))),
    ("requirements.txt Exists", os.path.exists(os.path.join(PROJECT_DIR, 'requirements.txt'))),
    (".gitignore Exists", os.path.exists(os.path.join(PROJECT_DIR, '.gitignore'))),
]

print("=== VALIDATION CHECKLIST ===")
all_passed = True
for task, passed in checklist:
    status = "PASSED [OK]" if passed else "FAILED [X]"
    if not passed:
        all_passed = False
    print(f"{task:<35}: {status}")

if all_passed:
    df_raw = pd.read_csv(raw_path)
    df_clean = pd.read_csv(clean_path)
    df_proc = pd.read_csv(proc_path)
    print("\n=== DATASET INTEGRITY METRICS ===")
    print(f"Raw Shape       : {df_raw.shape}")
    print(f"Cleaned Shape   : {df_clean.shape}")
    print(f"Processed Shape : {df_proc.shape}")
    print(f"Clean Nulls     : {df_clean.isnull().sum().sum()}")
    print(f"Processed Nulls : {df_proc.isnull().sum().sum()}")
    print("\nALL VALIDATION CHECKS PASSED SUCCESSFULLY!")
