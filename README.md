# 🏏 IPL Player & Team Performance Analytics Application (2008 – 2025)

An end-to-end, full-fledged Python analytical application and interactive Streamlit dashboard for analyzing 18 seasons of Indian Premier League (IPL) ball-by-ball and match dataset.

---

## 🌟 Features & Highlights

- **Complete 18-Season Coverage (2008–2025):** Processed **1,169 matches** and **278,205 deliveries**.
- **Data Engineering Pipeline:** Automatic entity resolution (franchise remapping, venue consolidation, legal delivery isolation, bowler runs & wicket categorization).
- **Multi-Dimensional Player Framework:**
  - **Batting:** Scoring volume, Strike Rate, Boundaries (4s & 6s), Boundary dependence %, Batting Average, and Consistency Coefficient of Variation ($CV = \sigma/\mu$).
  - **Bowling:** Wickets, Economy Rate, Bowling Average, Bowling Strike Rate, Dot Ball %, and Phase-wise containment.
- **Signature Phase-of-Play Analysis:** Over-by-over breakdown across **Powerplay (Overs 1-6)**, **Middle Overs (7-15)**, and **Death Overs (16-20)**.
- **Inferential Statistical Analysis:**
  - **Welch's Two-Sample t-Test:** Quantitative validation of IPL scoring escalation from Early Era (2008–2016) to Modern Era (2017–2025) ($p < 10^{-15}$, Cohen's $d = 0.49$).
  - **Chi-Square Test of Independence:** Evaluating the statistical significance of Toss Outcome on Match Outcome.
- **Interactive Streamlit Dashboard (`app.py`):**
  - Modern dark-theme glassmorphism UI styled with custom CSS (`styles.css`).
  - 7 Interactive Pages/Tabs with dynamic sliders, multiselect filters, Plotly charts, dataframes, and head-to-head radar chart comparisons.
- **Comprehensive Academic Project Report (`IPL_Analytics_Project_Report.md`):** Complete 10-chapter academic paper detailing dataset, methodology, empirical findings, and statistical outputs.

---

## 📁 Repository Structure

```
d:\ostf-ganesh\
├── app.md                          # Initial project specification document
├── app.py                          # Streamlit interactive web dashboard
├── styles.css                      # Custom CSS design system for dashboard UI
├── generate_report.py              # Script to process dataset & build markdown report
├── IPL_Analytics_Project_Report.md # Full 10-Chapter Academic/Project Report
├── data/                           # Raw datasets (2008-2025)
│   ├── matches_updated_ipl_upto_2025.csv
│   └── deliveries_updated_ipl_upto_2025.csv
├── processed_data/                 # Cleaned & cached pre-processed datasets
│   ├── matches_clean.csv
│   └── deliveries_clean.csv
├── src/                            # Modular Python source package
│   ├── __init__.py
│   ├── data_loader.py              # Ingestion, remapping, cleaning & caching
│   ├── analytics.py                # Batting, Bowling, Team, Venue & Phase metrics
│   ├── stats.py                    # Descriptive stats, correlation, t-tests, Chi-sq
│   └── utils.py                    # Chart formatting & KPI card HTML components
└── README.md                       # Documentation & execution instructions
```

---

## 🚀 Quick Start & How to Run

### 1. Requirements
Ensure Python 3.8+ is installed along with the required dependencies:
```bash
pip install pandas numpy matplotlib seaborn plotly scipy streamlit
```

### 2. Launch the Streamlit Web Application
To launch the interactive dashboard locally:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 3. Generate Project Analytics Report
To recalculate metrics and regenerate the 10-chapter academic report (`IPL_Analytics_Project_Report.md`):
```bash
python generate_report.py
```

---

## 📊 Key Findings Summary

1. **Scoring Rate Evolution:** 1st innings average scores increased significantly from **159.0 runs** (2008–2016) to **174.8 runs** (2017–2025), representing a statistically significant escalation of **+15.8 runs per match** ($t = 8.43, p = 1.01 \times 10^{-16}$).
2. **Toss Outcome Impact:** Winning the toss yields a **51.6% match win conversion rate**, proving that winning the toss does not confer a statistically significant advantage ($\chi^2 = 0.0, p = 1.0$).
3. **Phase-of-Play Dynamics:**
   - **Powerplay (1-6):** Highest boundary rate (66.2% of runs from boundaries).
   - **Middle Overs (7-15):** Lowest scoring rate (7.4 runs/over) and highest spin control.
   - **Death Overs (16-20):** Highest run rate (9.7+ runs/over) with 59.5% boundary contribution.

---
*Built as a Senior Data Analytics Application for IPL Performance Analysis (2008–2025).*
