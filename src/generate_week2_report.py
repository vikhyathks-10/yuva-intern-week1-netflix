import os
import datetime
import pandas as pd
import numpy as np
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
REPORT_PATH = os.path.join(PROJECT_DIR, 'reports', 'Week2_EDA_Visualization_Report.docx')
VIS_DIR = os.path.join(PROJECT_DIR, 'visualizations', 'week2')

# Styling Colors
COLOR_PRIMARY = RGBColor(229, 9, 20)      # Netflix Crimson #E50914
COLOR_SECONDARY = RGBColor(34, 31, 31)    # Dark Charcoal #221F1F
COLOR_ACCENT = RGBColor(43, 138, 62)     # Forest Green #2B8A3E
COLOR_NAVY = RGBColor(26, 82, 118)       # Deep Blue #1A5276
COLOR_TEXT = RGBColor(51, 51, 51)        # Body Text #333333

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = COLOR_PRIMARY
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = COLOR_SECONDARY
    return p

def add_body_paragraph(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(11)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_TEXT
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(11)
    run.font.color.rgb = COLOR_TEXT
    return p

def add_bullet_point(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(11)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_TEXT
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(11)
    run.font.color.rgb = COLOR_TEXT
    return p

def add_callout_box(doc, title, text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F2F4F4")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border color primary
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="36" w:space="0" w:color="E50914"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    
    r_t = p.add_run(f"{title}\n")
    r_t.font.name = 'Calibri'
    r_t.font.size = Pt(11)
    r_t.font.bold = True
    r_t.font.color.rgb = COLOR_PRIMARY
    
    r_b = p.add_run(text)
    r_b.font.name = 'Calibri'
    r_b.font.size = Pt(10.5)
    r_b.font.color.rgb = COLOR_TEXT
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_figure_image(doc, img_filename, fig_num, title, caption):
    img_path = os.path.join(VIS_DIR, img_filename)
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.paragraph_format.keep_with_next = True
        run = p_img.add_run()
        run.add_picture(img_path, width=Inches(6.0))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        
        r_fig = p_cap.add_run(f"Figure {fig_num}: ")
        r_fig.font.name = 'Calibri'
        r_fig.font.size = Pt(9.5)
        r_fig.font.bold = True
        r_fig.font.color.rgb = COLOR_PRIMARY
        
        r_title = p_cap.add_run(f"{title} — ")
        r_title.font.name = 'Calibri'
        r_title.font.size = Pt(9.5)
        r_title.font.bold = True
        r_title.font.color.rgb = COLOR_SECONDARY
        
        r_desc = p_cap.add_run(caption)
        r_desc.font.name = 'Calibri'
        r_desc.font.size = Pt(9.5)
        r_desc.font.italic = True
        r_desc.font.color.rgb = COLOR_TEXT

def create_styled_table(doc, headers, data, col_widths=None):
    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Format Header Row
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1A5276")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = 'Calibri'
            run.font.size = Pt(10)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
    # Format Data Rows
    for r_idx, row_data in enumerate(data):
        row_cells = tbl.rows[r_idx + 1].cells
        bg_color = "F9FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
            p = row_cells[c_idx].paragraphs[0]
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(9.5)
                run.font.color.rgb = COLOR_TEXT

    # Apply column widths if specified
    if col_widths:
        for row in tbl.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def generate_report():
    doc = docx.Document()
    
    # Page Margins (1 inch)
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        
    print("Generating Cover Page...")
    # ==========================================
    # 1. COVER PAGE
    # ==========================================
    p_top_spacer = doc.add_paragraph()
    p_top_spacer.paragraph_format.space_before = Pt(40)

    p_org = doc.add_paragraph()
    p_org.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_org = p_org.add_run("YUVA INTERNSHIP PROGRAM — WEEK 2 DELIVERABLE")
    r_org.font.name = 'Calibri'
    r_org.font.size = Pt(13)
    r_org.font.bold = True
    r_org.font.color.rgb = COLOR_PRIMARY

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(20)
    p_title.paragraph_format.space_after = Pt(10)
    r_title = p_title.add_run("Exploratory Data Analysis and Visualization on the Netflix Catalog")
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(26)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(40)
    r_sub = p_sub.add_run("Comprehensive Technical Report on Catalog Trends, Global Distribution, Genre Patterns, Duration Metrics, and Statistical Hypothesis Testing")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_TEXT

    # Meta Table on Cover Page
    meta_headers = ["Metadata Field", "Details"]
    meta_data = [
        ["Student Name", "Vikhyath Bharadwaj K S"],
        ["Internship Track", "Data Analytics & Data Visualization (Yuva Internship)"],
        ["Project Title", "Netflix Movies and TV Shows — EDA & Visualization"],
        ["Dataset Source", "Netflix Movies and TV Shows by Shivam Bansal (Kaggle)"],
        ["Dataset Records Analyzed", "7,787 Title Records (5,377 Movies, 2,410 TV Shows)"],
        ["Programming Environment", "Python 3.13 | Pandas | NumPy | Matplotlib | Seaborn | SciPy"],
        ["Submission Date", datetime.date.today().strftime("%B %d, %Y")]
    ]
    create_styled_table(doc, meta_headers, meta_data, col_widths=[2.5, 4.0])

    doc.add_page_break()

    # Setup Header & Footer
    section = doc.sections[0]
    footer = section.footer
    f_p = footer.paragraphs[0]
    f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    f_run = f_p.add_run("Yuva Internship Week 2 | Vikhyath Bharadwaj K S | Page ")
    f_run.font.name = 'Calibri'
    f_run.font.size = Pt(9)
    f_run.font.color.rgb = COLOR_TEXT

    # ==========================================
    # 2. ABSTRACT
    # ==========================================
    add_heading_1(doc, "1. Abstract")
    add_body_paragraph(doc, "This technical report presents a comprehensive Exploratory Data Analysis (EDA) and data visualization study of the Netflix Movies and TV Shows dataset curated by Shivam Bansal from Kaggle. Building directly upon the Week 1 data cleaning and preprocessing pipeline, this investigation examines 7,787 title records (comprising 5,377 Movies and 2,410 TV Shows) to uncover catalog composition, temporal release patterns, geographic production hubs, content target audience ratings, duration distributions, and seasonal addition dynamics.")
    add_body_paragraph(doc, "Using Python analytical libraries (Pandas, NumPy, Matplotlib, Seaborn, and SciPy), 12 publication-quality visualizations were constructed alongside robust descriptive statistics and inferential hypothesis testing. Key empirical findings indicate that feature films constitute 69.05% of the platform's portfolio, though television series experienced exponential growth post-2016. Multi-country co-production unnesting highlights the United States (3,297 titles), India (990 titles), and the United Kingdom (723 titles) as top content contributors. Movie durations exhibit a normal distribution centered at a median of 98.0 minutes (mean: 99.3 min), whereas 66.7% of television series feature only a single season. Statistical tests confirm significant audience targeting differences between content formats (Chi-Square p = 1.79e-21) and significant duration variation across genres (ANOVA p = 3.91e-268).")

    # ==========================================
    # 3. INTRODUCTION
    # ==========================================
    add_heading_1(doc, "2. Introduction")
    add_body_paragraph(doc, "Exploratory Data Analysis (EDA) forms the bedrock of data science methodology. Developed by John Tukey, EDA emphasizes visual exploration, distribution assessment, relationship discovery, and hypothesis generation prior to formal statistical modeling. In modern corporate environments, streaming media platforms like Netflix rely heavily on exploratory analytics to optimize content licensing budgets, regional localization strategies, genre portfolio allocation, and user recommendation engines.")
    add_heading_2(doc, "2.1 Objectives of the Assignment")
    add_bullet_point(doc, "Quantify content type breakdown and analyze catalog expansion trends over time.", "1. Catalog Dynamics: ")
    add_bullet_point(doc, "Examine international content contributions while accounting for multi-country co-productions.", "2. Geographic Profiling: ")
    add_bullet_point(doc, "Identify top listed genres and evaluate primary content categories across Movies and TV Shows.", "3. Genre & Audience Taxonomy: ")
    add_bullet_point(doc, "Conduct empirical distribution analysis of movie runtimes and TV show season counts.", "4. Duration Metrics: ")
    add_bullet_point(doc, "Evaluate content age lag (release year vs Netflix addition date) and addition seasonality.", "5. Licensing & Release Patterns: ")
    add_bullet_point(doc, "Apply Chi-Square tests of independence and ANOVA/Kruskal-Wallis variance tests.", "6. Inferential Statistical Testing: ")

    # ==========================================
    # 4. DATASET DESCRIPTION
    # ==========================================
    add_heading_1(doc, "3. Dataset Description")
    add_body_paragraph(doc, "The primary dataset analyzed in this study is the Netflix Movies and TV Shows dataset sourced from Kaggle (contributed by Shivam Bansal). The original raw dataset contains 7,787 rows and 12 columns, capturing metadata for titles added to Netflix up to early 2021.")
    
    col_desc_headers = ["Column Name", "Data Type", "Role / Description", "Cleaned & Engineered State"]
    col_desc_data = [
        ["show_id", "Object / String", "Unique record identifier (e.g., s1, s2)", "Validated 100% unique primary key"],
        ["type", "Object / Category", "Content format: Movie or TV Show", "Standardized binary category"],
        ["title", "Object / String", "Official title of the movie or show", "Trimmed whitespace, normalized text"],
        ["director", "Object / String", "Director name(s)", "Missing values filled with 'Unknown Director'"],
        ["cast", "Object / String", "Main cast members (comma-separated)", "Missing values filled with 'Unknown Cast'"],
        ["country", "Object / String", "Production countries (comma-separated)", "Missing filled with 'Unknown Country'; unnested"],
        ["date_added", "Object / Datetime", "Date title was added to Netflix", "Parsed to datetime (`date_added_dt`) & year/month"],
        ["release_year", "Integer", "Original release year of title", "Numeric year (1925 to 2021)"],
        ["rating", "Object / Category", "Maturity rating (e.g., TV-MA, TV-14, R)", "Standardized; missing imputed with mode ('TV-MA')"],
        ["duration", "Object / String", "Raw runtime string ('90 min', '1 Season')", "Parsed into `duration_int` and `duration_unit`"],
        ["listed_in", "Object / String", "Genre classifications (comma-separated)", "Extracted `primary_genre` and unnested genres"],
        ["description", "Object / String", "Short textual summary of title", "Full text preserved"]
    ]
    create_styled_table(doc, col_desc_headers, col_desc_data, col_widths=[1.2, 1.2, 2.3, 1.8])

    # ==========================================
    # 5. TOOLS AND TECHNOLOGIES
    # ==========================================
    add_heading_1(doc, "4. Tools and Technologies")
    add_bullet_point(doc, "Core programming environment for data analysis and scripting.", "Python 3.13: ")
    add_bullet_point(doc, "DataFrame manipulation, string unnesting, crosstab aggregation, and datetime parsing.", "Pandas (v2.2+): ")
    add_bullet_point(doc, "High-performance vector operations, array computing, and descriptive stats.", "NumPy: ")
    add_bullet_point(doc, "Core plotting engine for multi-panel figures, annotations, and customized layouts.", "Matplotlib: ")
    add_bullet_point(doc, "Statistical visualization layer for distribution plots, boxplots, and heatmaps.", "Seaborn: ")
    add_bullet_point(doc, "Module `scipy.stats` for Chi-Square tests of independence, ANOVA, and Kruskal-Wallis tests.", "SciPy: ")
    add_bullet_point(doc, "Interactive notebook environment for reproducible code execution and inline rendering.", "Jupyter Notebook: ")

    # ==========================================
    # 6. METHODOLOGY
    # ==========================================
    add_heading_1(doc, "5. Methodology")
    add_body_paragraph(doc, "The exploratory analysis followed a structured 6-step analytical pipeline to guarantee reproducibility and rigorous insights:")
    add_bullet_point(doc, "Importing cleaned dataset (`netflix_cleaned.csv`) and processed dataset (`netflix_processed.csv`).", "Step 1: Data Ingestion — ")
    add_bullet_point(doc, "Checking dimensions (7,787 × 28), verifying non-null counts, and validating feature types.", "Step 2: Structural Verification — ")
    add_bullet_point(doc, "Computing central tendency, variance, skewness, and interquartile ranges.", "Step 3: Univariate Distribution Analysis — ")
    add_bullet_point(doc, "Exploding multi-valued fields (`country` and `listed_in`) to avoid multi-country and multi-genre count truncation.", "Step 4: Unnesting & Bivariate Crosstabs — ")
    add_bullet_point(doc, "Constructing 12 publication-quality visualizations using consistent color palettes.", "Step 5: Visual Feature Engineering — ")
    add_bullet_point(doc, "Executing Chi-Square tests of independence and ANOVA variance analysis.", "Step 6: Statistical Hypothesis Testing — ")

    # ==========================================
    # 7. INITIAL EXPLORATORY ANALYSIS
    # ==========================================
    add_heading_1(doc, "6. Initial Exploratory Analysis")
    add_body_paragraph(doc, "An initial quantitative summary of key numerical variables highlights significant structural differences across metadata fields:")
    
    num_summary_headers = ["Metric / Variable", "Release Year", "Movie Duration (min)", "Content Age Lag (yr)", "Cast Count", "Country Count"]
    num_summary_data = [
        ["Count (Non-Null)", "7,787", "5,377", "7,787", "7,787", "7,787"],
        ["Mean", "2013.93", "99.31", "5.28", "6.35", "1.13"],
        ["Standard Deviation", "8.76", "28.53", "8.76", "4.08", "0.78"],
        ["Minimum", "1925", "3.00", "0.00", "0", "0"],
        ["25th Percentile (Q1)", "2013", "86.00", "1.00", "3", "1"],
        ["50th Percentile (Median)", "2017", "98.00", "3.00", "6", "1"],
        ["75th Percentile (Q3)", "2018", "114.00", "6.00", "9", "1"],
        ["Maximum", "2021", "312.00", "95.00", "50", "12"],
        ["Skewness", "-3.63", "0.19", "3.59", "0.85", "3.21"]
    ]
    create_styled_table(doc, num_summary_headers, num_summary_data, col_widths=[1.8, 1.0, 1.2, 1.2, 0.9, 0.9])

    # ==========================================
    # 8. DETAILED EXPLORATORY DATA ANALYSIS
    # ==========================================
    add_heading_1(doc, "7. Detailed Exploratory Data Analysis")

    # A. Content Type
    add_heading_2(doc, "7.1 Content Type Distribution Analysis")
    add_body_paragraph(doc, "Netflix's catalog is partitioned into two primary content categories: Movies and TV Shows. Analysis reveals that Movies constitute 5,377 titles (69.05%), whereas TV Shows account for 2,410 titles (30.95%).")
    add_figure_image(doc, 'w2_01_content_type_distribution.png', 1, "Content Type Proportion & Volume", "Donut chart and bar plot illustrating the 69.05% vs 30.95% split between Movies and TV Shows.")
    add_body_paragraph(doc, "Observation & Insight: ", "Key Finding: ")
    add_body_paragraph(doc, "While feature films dominate total historical catalog acquisitions, television series have seen accelerated acquisition rates in recent years due to higher subscriber retention and binge-watching engagement metrics.")

    # B. Release Year
    add_heading_2(doc, "7.2 Release Year Evolution & Trends")
    add_body_paragraph(doc, "Content release years range from 1925 to 2021. Release volume remained low and flat throughout the 20th century before experiencing an exponential rise beginning in 2010.")
    add_figure_image(doc, 'w2_02_release_year_trends.png', 2, "Release Year Evolution (1925 - 2021)", "Line chart tracking release trends for Movies and TV Shows, highlighting peak movie releases in 2017 (767 titles) and TV show releases in 2020 (436 titles).")
    add_body_paragraph(doc, "The peak release year for movies was 2017 with 767 films, whereas TV show releases peaked in 2020 with 436 series. The sharp drop in 2021 reflects dataset right-censoring in early 2021.")

    # C. Country Analysis
    add_heading_2(doc, "7.3 International Content & Geographic Production Shares")
    add_body_paragraph(doc, "A common methodological error in EDA is counting multi-country entries (e.g., 'United States, India') as unique standalone strings, which undercounts country participation. By unnesting comma-separated values, true geographic representation was extracted:")
    add_figure_image(doc, 'w2_03_top_contributing_countries.png', 3, "Top 15 Content-Producing Countries", "Horizontal bar chart showing total titles produced or co-produced by country after unnesting multi-country entries.")
    
    country_table_headers = ["Rank", "Country Name", "Total Titles (Unnested)", "Primary Production Share (%)"]
    country_table_data = [
        ["1", "United States", "3,297", "42.34%"],
        ["2", "India", "990", "12.71%"],
        ["3", "United Kingdom", "723", "9.28%"],
        ["4", "Canada", "412", "5.29%"],
        ["5", "France", "349", "4.48%"],
        ["6", "Japan", "287", "3.69%"],
        ["7", "Spain", "215", "2.76%"],
        ["8", "South Korea", "212", "2.72%"],
        ["9", "Germany", "199", "2.56%"],
        ["10", "Mexico", "154", "1.98%"]
    ]
    create_styled_table(doc, country_table_headers, country_table_data, col_widths=[0.8, 2.2, 2.0, 2.0])

    add_figure_image(doc, 'w2_12_country_type_breakdown.png', 4, "Movie vs. TV Show Split for Top Countries", "Stacked bar chart illustrating content format preferences across top producing nations.")
    add_body_paragraph(doc, "Geographic Content Divergence: ", "Insight: ")
    add_body_paragraph(doc, "India exhibits an overwhelming bias toward feature films (over 90% Movies), whereas South Korea and Japan demonstrate strong structural preferences toward TV series (K-Dramas and Anime series).")

    # D. Genre Analysis
    add_heading_2(doc, "7.4 Genre Taxonomy & Distribution")
    add_body_paragraph(doc, "Unnesting listed genres reveals that 'International Movies' is the single most frequent classification (2,437 titles), followed by 'Dramas' (2,106 titles) and 'Comedies' (1,471 titles).")
    add_figure_image(doc, 'w2_04_top_listed_genres.png', 5, "Top 15 Listed Genres across Catalog", "Horizontal bar chart of top unnested listed genres across Netflix.")
    add_figure_image(doc, 'w2_08_genre_content_type_heatmap.png', 6, "Genre Frequency across Content Types", "Cross-tabulation heatmap comparing top 12 genres between Movies and TV Shows.")

    # E. Rating Analysis
    add_heading_2(doc, "7.5 Maturity Rating Classification")
    add_body_paragraph(doc, "Content maturity ratings reveal that Netflix focuses heavily on adult and mature audiences. The single largest rating category is `TV-MA` (2,870 titles, 36.86%), followed by `TV-14` (1,931 titles, 24.80%) and `R` (665 titles, 8.54%). Combined, mature adult content accounts for over 46% of all listings.")
    add_figure_image(doc, 'w2_05_content_ratings_by_type.png', 7, "Rating Distribution by Content Type", "Grouped bar chart comparing rating frequencies for Movies and TV Shows.")

    # F. Duration Analysis
    add_heading_2(doc, "7.6 Duration & Seasonality Analysis")
    add_body_paragraph(doc, "Movie runtimes and TV show season counts represent non-commensurable measurements and must be analyzed independently.")
    add_figure_image(doc, 'w2_06_movie_duration_histogram.png', 8, "Distribution of Movie Durations", "Histogram and KDE density curve of movie runtimes in minutes (Mean: 99.3 min, Median: 98 min).")
    add_figure_image(doc, 'w2_07_tv_show_seasons_distribution.png', 9, "TV Show Season Count Distribution", "Bar chart showing season counts for TV series, highlighting that 66.7% of shows have only 1 season.")
    add_figure_image(doc, 'w2_11_movie_duration_by_genre_boxplot.png', 10, "Movie Durations across Primary Genres", "Boxplot comparing runtime distributions for top 8 primary movie genres.")

    # G. Date Added Analysis
    add_heading_2(doc, "7.7 Content Addition Seasonality & Content Age Lag")
    add_body_paragraph(doc, "Analyzing addition dates (`date_added_dt`) demonstrates that Netflix additions peak during the fourth and first quarters of the year (December, October, and January).")
    add_figure_image(doc, 'w2_09_monthly_content_additions.png', 11, "Content Addition Heatmap (2015 - 2021)", "Yearly and monthly heatmap of title additions onto Netflix.")
    add_figure_image(doc, 'w2_10_content_age_lag_distribution.png', 12, "Content Age Lag Distribution", "Histogram of years elapsed between a title's original release year and its Netflix addition date (Median lag: 3 years).")

    # ==========================================
    # 9. STATISTICAL ANALYSIS & RELATIONSHIPS
    # ==========================================
    add_heading_1(doc, "8. Inferential Statistical Testing")
    add_body_paragraph(doc, "To go beyond descriptive visualization, formal statistical hypothesis tests were conducted to evaluate relationship significance:")

    add_callout_box(doc, "Test 1: Chi-Square Test of Independence (Content Type vs. Target Audience)", 
                    "• Null Hypothesis (H0): Target audience classification is independent of content type.\n"
                    "• Alternative Hypothesis (H1): Target audience classification depends significantly on content type.\n"
                    "• Results: Chi-Square Statistic = 99.7083, p-value = 1.7957e-21, Degrees of Freedom = 3.\n"
                    "• Effect Size: Cramer's V = 0.1132.\n"
                    "• Conclusion: Reject H0 with >99.9% confidence. Movies have a significantly higher proportion of R/PG-13 rated content, whereas TV shows lean more towards TV-MA and TV-14 ratings.")

    add_callout_box(doc, "Test 2: One-Way ANOVA & Kruskal-Wallis Test (Movie Duration across Top 5 Genres)", 
                    "• Null Hypothesis (H0): Mean movie runtime is equal across top primary movie genres.\n"
                    "• Alternative Hypothesis (H1): At least one genre has a significantly different mean runtime.\n"
                    "• Results (ANOVA): F-Statistic = 359.1099, p-value = 3.9173e-268.\n"
                    "• Results (Kruskal-Wallis): H-Statistic = 1165.9718, p-value = 3.7918e-251.\n"
                    "• Conclusion: Reject H0. Documentaries have significantly shorter runtimes (mean ~80 min), whereas Action & Dramas average significantly longer runtimes (~105-115 min).")

    # ==========================================
    # 10. TRANSFORMATIONS AND AGGREGATIONS
    # ==========================================
    add_heading_1(doc, "9. Transformations and Aggregations Summary")
    add_body_paragraph(doc, "All analytical transformations performed throughout Week 1 and Week 2 are documented below:")
    
    trans_headers = ["Transformation", "Original Format", "Transformed Output", "Analytical Justification"]
    trans_data = [
        ["Datetime Extraction", "String ('August 4, 2017')", "Datetime object (`date_added_dt`), year, month", "Enables time-series aggregation and seasonality analysis"],
        ["Country Unnesting", "Comma-string ('US, UK')", "Exploded individual rows per country", "Eliminates co-production undercounting"],
        ["Genre Unnesting", "Comma-string ('Dramas, Comedies')", "Exploded individual rows per genre", "Allows accurate cross-genre frequency counting"],
        ["Duration Parsing", "String ('90 min', '2 Seasons')", "`duration_int` (float) & `duration_unit`", "Enables numeric summary stats (mean, std, median)"],
        ["Audience Binning", "Rating codes ('TV-MA', 'PG')", "Target groups ('Adults', 'Teens', 'Kids')", "Simplifies demographic comparison across formats"],
        ["Content Lag Calculation", "Numeric year values", "`content_age` = `year_added` - `release_year`", "Measures platform licensing speed and content freshness"]
    ]
    create_styled_table(doc, trans_headers, trans_data, col_widths=[1.5, 1.5, 1.8, 2.2])

    # ==========================================
    # 11. KEY FINDINGS
    # ==========================================
    add_heading_1(doc, "10. Key Findings & Strategic Insights")
    add_bullet_point(doc, "Movies comprise 69.05% of the total catalog, but TV series additions grew at a faster relative rate post-2016.", "1. Catalog Composition: ")
    add_bullet_point(doc, "The US (3,297 titles), India (990 titles), and UK (723 titles) are top producers. India specializes in Movies, while South Korea/Japan specialize in TV series.", "2. Geographic Specialization: ")
    add_bullet_point(doc, "International Movies (2,437), Dramas (2,106), and Comedies (1,471) lead catalog offerings.", "3. Genre Hierarchy: ")
    add_bullet_point(doc, "Mature content (`TV-MA` + `R`) accounts for >46% of all content, aligning with subscriber demographic targeting.", "4. Mature Audience Orientation: ")
    add_bullet_point(doc, "Movie runtimes follow a tight normal distribution (median 98 min), while 66.7% of TV shows end after 1 season.", "5. Duration Metrics: ")
    add_bullet_point(doc, "Content additions peak in Q4 and Q1 (Dec/Jan), aligning with holiday viewing spikes.", "6. Addition Seasonality: ")

    # ==========================================
    # 12. CHALLENGES AND SOLUTIONS
    # ==========================================
    add_heading_1(doc, "11. Analytical Challenges & Solutions")
    add_bullet_point(doc, "Simple string matching double-counts or truncates co-productions. Solved by custom unnesting and exploding comma-separated lists.", "Challenge 1: Multi-Valued Fields — ")
    add_bullet_point(doc, "Duration strings mixed 'min' and 'Seasons'. Solved by regex parsing into numeric integer columns and categorical unit descriptors.", "Challenge 2: Non-Commensurable Durations — ")
    add_bullet_point(doc, "Missing dates and countries required careful imputation during Week 1 without distorting underlying distribution trends.", "Challenge 3: Imputation Artifacts — ")

    # ==========================================
    # 13. LIMITATIONS AND FUTURE SCOPE
    # ==========================================
    add_heading_1(doc, "12. Limitations & Future Scope")
    add_bullet_point(doc, "The dataset cuts off in early 2021 and lacks viewership numbers, watch completion rates, or subscriber ratings.", "1. Data Completeness: ")
    add_bullet_point(doc, "Future work could integrate external datasets (IMDb ratings, Box Office Mojo revenue, Rotten Tomatoes scores) for multi-variate predictive modeling.", "2. External Enrichment: ")
    add_bullet_point(doc, "Natural Language Processing (NLP) on title descriptions and sentiment analysis.", "3. Advanced NLP Scope: ")

    # ==========================================
    # 14. CONCLUSION
    # ==========================================
    add_heading_1(doc, "13. Conclusion")
    add_body_paragraph(doc, "This Week 2 Exploratory Data Analysis successfully delivers an exhaustive visual and quantitative exploration of the Netflix dataset. All 12 visualization figures, statistical hypothesis tests, and structured data summaries confirm significant structural patterns in Netflix's catalog strategy. The completed Jupyter Notebook (`week2_eda_visualization.ipynb`), Python scripts (`eda_analysis.py`), high-resolution PNG charts, and this DOCX report fulfill all requirements for Week 2 of the Yuva Internship.")

    # ==========================================
    # 15. REFERENCES
    # ==========================================
    add_heading_1(doc, "14. References")
    add_bullet_point(doc, "Shivam Bansal. Netflix Movies and TV Shows Dataset. Sourced from Kaggle: https://www.kaggle.com/datasets/shivamb/netflix-shows", "1. ")
    add_bullet_point(doc, "McKinney, W. (2010). Data Structures for Statistical Computing in Python. Proceedings of the 9th Python in Science Conference, 51-56.", "2. ")
    add_bullet_point(doc, "Waskom, M. L. (2021). Seaborn: statistical data visualization. Journal of Open Source Software, 6(60), 3021.", "3. ")
    add_bullet_point(doc, "Tukey, J. W. (1977). Exploratory Data Analysis. Addison-Wesley.", "4. ")

    # ==========================================
    # 16. APPENDIX
    # ==========================================
    add_heading_1(doc, "15. Appendix")
    add_body_paragraph(doc, "Selected Python code snippet for Chi-Square test execution and multi-country unnesting:")
    
    app_p = doc.add_paragraph()
    app_p.paragraph_format.space_before = Pt(4)
    app_p.paragraph_format.space_after = Pt(6)
    r_code = app_p.add_run(
        "# Unnesting Multi-Country Entries\n"
        "country_series = df_proc[df_proc['country'] != 'Unknown Country']['country'].dropna()\n"
        "exploded_countries = country_series.apply(lambda x: [c.strip() for c in str(x).split(',')]).explode()\n"
        "top_15_countries = exploded_countries.value_counts().head(15)\n\n"
        "# Chi-Square Test of Independence\n"
        "ct_aud = pd.crosstab(df_proc['type'], df_proc['target_audience'])\n"
        "chi2, p_val, dof, expected = stats.chi2_contingency(ct_aud)\n"
        "print(f'Chi2 = {chi2:.4f}, p-val = {p_val:.4e}')"
    )
    r_code.font.name = 'Courier New'
    r_code.font.size = Pt(9.5)
    r_code.font.color.rgb = COLOR_NAVY

    doc.save(REPORT_PATH)
    print(f"Professional DOCX Report generated at: {REPORT_PATH}")

if __name__ == '__main__':
    generate_report()
