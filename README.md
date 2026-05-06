# PISA Student Performance Analysis

Final project for **DAT 230 — Data Visualization** at San Jose State University.

This project explores patterns in student performance, well-being, and school climate using the OECD Programme for International Student Assessment (PISA) datasets from 2018 and 2022. Visualizations are produced in both Python (static, publication-ready) and Power BI (interactive dashboard).

## Research Questions

The analysis is organized around six themes:

1. **Country-level performance** — Which countries lead in Math, Reading, and Science, and how do within-country subject gaps compare?
2. **Gender gaps** — How do male and female students differ across the three subjects?
3. **Socio-economic gradient** — How strongly does ESCS (Economic, Social and Cultural Status) predict math performance, and did this gradient change between 2018 and 2022?
4. **School climate** — How do Teacher Support and Disciplinary Climate relate to math outcomes?
5. **Student wellbeing** — How does math anxiety co-vary with math performance across countries?
6. **Drivers of performance** — Which student-level factors (motivation, belonging, climate, support, anxiety, ESCS) are most strongly associated with scores?

## Project Structure

```
pisa-student-performance-analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── data/                   # PISA CSV files (not tracked - too large)
├── src/
│   ├── plot_config.py      # Shared styling, colors, save helpers
│   └── generate_charts.py  # Main script - produces all 6 figures
├── output/
│   └── figures/            # Generated PNG and PDF charts
└── notebooks/
    └── EDA.ipynb           # Exploratory notebook
```

## Setup

### Requirements

- Python 3.9 or higher
- The two PISA cleaned CSV files (place in `data/`):
  - `PISA_2022_WithMeanScore.csv`
  - `PISA_2018_WithMeanScore.csv`

### Install

```bash
git clone https://github.com/<your-username>/pisa-student-performance-analysis.git
cd pisa-student-performance-analysis
pip install -r requirements.txt
```

### Run

Place the CSV files in `data/`, then:

```bash
python src/generate_charts.py
```

All 6 charts will be saved as PNG and PDF in `output/figures/`.

## Output Charts

| # | File | Description |
|---|---|---|
| 1 | `1_country_performance.png` | Top 15 countries by mean score across three subjects |
| 2 | `2_gender_gap_boxplots.png` | Faceted boxplots showing gender gap per subject |
| 3 | `3_escs_vs_math_2018_2022.png` | Two-panel ESCS vs Math regression, 2018 vs 2022 |
| 4 | `4_school_climate.png` | Teacher Support and Disciplinary Climate vs Math |
| 5 | `5_wellbeing_quadrant.png` | Math anxiety vs Math score with country labels |
| 6 | `6_correlation_heatmap.png` | Correlation matrix of student-level drivers vs scores |
| 7 | `7_score_distribution.png` | Density distribution of student scores by subject |
| 8 | `8_world_map.png` | Choropleth world map of mean math scores |

## Data Source

OECD PISA 2018 and 2022 Student Questionnaire datasets, available at:
https://www.oecd.org/pisa/data/

The `*_WithMeanScore` files in this project are pre-processed versions where the ten plausible values per subject are averaged into a single mean score column for ease of analysis.

## Tools Used

- **Python** — pandas, matplotlib, seaborn (static charts)
- **Power BI** — interactive dashboard
- **LaTeX (IEEE template)** — final report

## Team

DAT 230 — Spring 2026
