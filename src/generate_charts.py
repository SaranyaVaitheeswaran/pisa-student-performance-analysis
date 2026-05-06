"""
PISA Student Performance Analysis - Chart Generation
=====================================================

Generates 8 publication-ready charts for the DAT 230 final project report.

Charts produced:
    1. country_performance.png  - Top 15 countries by average score (3 subjects)
    2. gender_gap_boxplots.png  - Gender boxplots faceted by subject
    3. escs_vs_math_2018_2022.png - ESCS vs Math, two-panel year comparison
    4. school_climate.png       - Teacher Support / Disciplinary Climate vs Math
    5. wellbeing_quadrant.png   - Math anxiety vs Math score with country labels
    6. correlation_heatmap.png  - Correlation matrix of drivers vs scores
    7. score_distribution.png   - KDE density plots of scores by subject
    8. world_map.png            - Choropleth world map of mean math scores

Usage:
    python src/generate_charts.py

Inputs (place in data/):
    - PISA_2022_WithMeanScore.csv
    - PISA_2018_WithMeanScore.csv

Outputs (saved to output/figures/):
    PNG (300 DPI) and PDF for each chart.
"""

import os
import sys
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from plot_config import (
    COLORS,
    SUBJECT_PALETTE,
    setup_style,
    save_figure,
    get_country_name,
    to_iso3,
)

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------
# Paths
# ---------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
FILE_2022 = os.path.join(DATA_DIR, "PISA_2022_WithMeanScore.csv")
FILE_2018 = os.path.join(DATA_DIR, "PISA_2018_WithMeanScore.csv")


# ---------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------
def load_data():
    """Load both PISA datasets and return as a dict."""
    print("Loading data...")
    if not os.path.exists(FILE_2022):
        sys.exit(f"ERROR: {FILE_2022} not found. Place CSVs in data/")
    if not os.path.exists(FILE_2018):
        sys.exit(f"ERROR: {FILE_2018} not found. Place CSVs in data/")

    df_2022 = pd.read_csv(FILE_2022)
    df_2018 = pd.read_csv(FILE_2018)
    print(f"  2022: {df_2022.shape}")
    print(f"  2018: {df_2018.shape}")
    return {"2022": df_2022, "2018": df_2018}


# ---------------------------------------------------------------
# Chart 1: Country Performance Overview
# ---------------------------------------------------------------
def chart_country_performance(df_2022):
    """Top 15 countries by average score across three subjects."""
    print("\n[1/6] Country performance overview...")

    country_scores = (
        df_2022.groupby("CNT")[
            ["Math_MeanScore", "Reading_MeanScore", "Science_MeanScore"]
        ]
        .mean()
        .reset_index()
    )

    # Rank by combined average
    country_scores["overall"] = country_scores[
        ["Math_MeanScore", "Reading_MeanScore", "Science_MeanScore"]
    ].mean(axis=1)
    top15 = country_scores.nlargest(15, "overall").copy()
    top15["Country"] = top15["CNT"].apply(get_country_name)

    # Reshape for grouped bar
    plot_df = top15.melt(
        id_vars=["Country"],
        value_vars=["Math_MeanScore", "Reading_MeanScore", "Science_MeanScore"],
        var_name="Subject",
        value_name="Score",
    )
    plot_df["Subject"] = plot_df["Subject"].str.replace("_MeanScore", "")

    fig, ax = plt.subplots(figsize=(11, 7))
    sns.barplot(
        data=plot_df,
        y="Country",
        x="Score",
        hue="Subject",
        palette=SUBJECT_PALETTE,
        ax=ax,
        order=top15["Country"].tolist(),
    )
    ax.set_title(
        "Top 15 Countries by Average PISA Score (2022)",
        fontweight="bold",
        pad=12,
    )
    ax.set_xlabel("Mean Score")
    ax.set_ylabel("")
    ax.set_xlim(350, 600)
    ax.legend(title="Subject", loc="lower right", framealpha=0.95)
    ax.grid(axis="x", alpha=0.3)

    save_figure(fig, "1_country_performance")
    plt.close(fig)


# ---------------------------------------------------------------
# Chart 2: Gender Gap Boxplots
# ---------------------------------------------------------------
def chart_gender_gap(df_2022):
    """Faceted boxplots by gender across three subjects."""
    print("\n[2/6] Gender gap boxplots...")

    df = df_2022[
        ["ST004D01T", "Math_MeanScore", "Reading_MeanScore", "Science_MeanScore"]
    ].dropna()
    df = df[df["ST004D01T"].isin([1.0, 2.0])].copy()
    df["Gender"] = df["ST004D01T"].map({1.0: "Female", 2.0: "Male"})

    plot_df = df.melt(
        id_vars=["Gender"],
        value_vars=["Math_MeanScore", "Reading_MeanScore", "Science_MeanScore"],
        var_name="Subject",
        value_name="Score",
    )
    plot_df["Subject"] = plot_df["Subject"].str.replace("_MeanScore", "")

    fig, axes = plt.subplots(1, 3, figsize=(13, 5), sharey=True)
    subjects = ["Math", "Reading", "Science"]

    for i, subj in enumerate(subjects):
        ax = axes[i]
        subset = plot_df[plot_df["Subject"] == subj]
        sns.boxplot(
            data=subset,
            x="Gender",
            y="Score",
            ax=ax,
            palette={"Female": COLORS["female"], "Male": COLORS["male"]},
            showfliers=False,
            width=0.55,
        )
        # Annotate means
        means = subset.groupby("Gender")["Score"].mean()
        diff = means["Female"] - means["Male"]
        ax.set_title(
            f"{subj}\n(F − M = {diff:+.1f})", fontweight="bold"
        )
        ax.set_xlabel("")
        if i == 0:
            ax.set_ylabel("Score")
        else:
            ax.set_ylabel("")
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle(
        "Gender Gap in PISA Performance by Subject (2022)",
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()
    save_figure(fig, "2_gender_gap_boxplots")
    plt.close(fig)


# ---------------------------------------------------------------
# Chart 3: ESCS vs Math (2018 vs 2022) - the headline chart
# ---------------------------------------------------------------
def chart_escs_comparison(df_2022, df_2018):
    """Two-panel scatter: ESCS vs Math at country level, 2018 and 2022."""
    print("\n[3/6] ESCS vs Math, 2018 vs 2022...")

    def country_summary(df):
        return (
            df.groupby("CNT")
            .agg(escs=("ESCS", "mean"), math=("Math_MeanScore", "mean"))
            .dropna()
            .reset_index()
        )

    s2018 = country_summary(df_2018)
    s2022 = country_summary(df_2022)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)

    for ax, data, year, color in [
        (axes[0], s2018, "2018", COLORS["year_2018"]),
        (axes[1], s2022, "2022", COLORS["year_2022"]),
    ]:
        sns.regplot(
            data=data,
            x="escs",
            y="math",
            ax=ax,
            scatter_kws={"alpha": 0.65, "s": 45, "color": color},
            line_kws={"color": COLORS["accent"], "lw": 2},
        )

        # Slope and R^2
        slope, intercept = np.polyfit(data["escs"], data["math"], 1)
        r = np.corrcoef(data["escs"], data["math"])[0, 1]

        ax.set_title(f"{year}", fontweight="bold")
        ax.set_xlabel("Mean ESCS (Country)")
        ax.set_ylabel("Mean Math Score" if year == "2018" else "")
        ax.text(
            0.04,
            0.96,
            f"slope = {slope:.1f}\nR² = {r**2:.2f}",
            transform=ax.transAxes,
            va="top",
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="grey", alpha=0.9),
        )
        ax.grid(alpha=0.3)

    fig.suptitle(
        "Socio-Economic Status vs Math Performance: 2018 vs 2022",
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()
    save_figure(fig, "3_escs_vs_math_2018_2022")
    plt.close(fig)


# ---------------------------------------------------------------
# Chart 4: School Climate vs Performance
# ---------------------------------------------------------------
def chart_school_climate(df_2022):
    """Teacher Support and Disciplinary Climate vs Math, country level."""
    print("\n[4/6] School climate vs performance...")

    summary = (
        df_2022.groupby("CNT")
        .agg(
            teach=("TEACHSUP", "mean"),
            disc=("DISCLIM", "mean"),
            math=("Math_MeanScore", "mean"),
        )
        .dropna()
        .reset_index()
    )

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    for ax, x_var, x_label in [
        (axes[0], "teach", "Teacher Support Index"),
        (axes[1], "disc", "Disciplinary Climate Index"),
    ]:
        sns.regplot(
            data=summary,
            x=x_var,
            y="math",
            ax=ax,
            scatter_kws={"alpha": 0.7, "s": 50, "color": COLORS["math"]},
            line_kws={"color": COLORS["accent"], "lw": 2},
        )
        r = np.corrcoef(summary[x_var], summary["math"])[0, 1]
        ax.set_title(f"{x_label} vs Math (r = {r:.2f})", fontweight="bold")
        ax.set_xlabel(x_label)
        ax.set_ylabel("Mean Math Score")
        ax.grid(alpha=0.3)

    fig.suptitle(
        "School Climate Indicators vs Math Performance (2022)",
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()
    save_figure(fig, "4_school_climate")
    plt.close(fig)


# ---------------------------------------------------------------
# Chart 5: Wellbeing Quadrant
# ---------------------------------------------------------------
def chart_wellbeing_quadrant(df_2022):
    """Math anxiety vs Math score, country labels, quadrants."""
    print("\n[5/6] Wellbeing quadrant...")

    summary = (
        df_2022.groupby("CNT")
        .agg(anxiety=("ANXMAT", "mean"), math=("Math_MeanScore", "mean"))
        .dropna()
        .reset_index()
    )
    summary["Country"] = summary["CNT"].apply(get_country_name)

    fig, ax = plt.subplots(figsize=(11, 8))

    ax.scatter(
        summary["anxiety"],
        summary["math"],
        s=70,
        alpha=0.75,
        color=COLORS["math"],
        edgecolor="white",
        linewidth=0.7,
    )

    # Quadrant lines at medians
    x_med = summary["anxiety"].median()
    y_med = summary["math"].median()
    ax.axvline(x_med, color="grey", linestyle="--", alpha=0.5)
    ax.axhline(y_med, color="grey", linestyle="--", alpha=0.5)

    # Label every country (small font)
    for _, row in summary.iterrows():
        ax.annotate(
            row["Country"],
            (row["anxiety"], row["math"]),
            fontsize=7,
            alpha=0.85,
            xytext=(3, 3),
            textcoords="offset points",
        )

    # Quadrant labels (4 corners, neutral descriptive)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    label_kwargs = dict(fontsize=9, alpha=0.6, style="italic")
    ax.text(
        xlim[0] + 0.02 * (xlim[1] - xlim[0]),
        ylim[1] - 0.04 * (ylim[1] - ylim[0]),
        "Low anxiety,\nHigh score",
        **label_kwargs,
    )
    ax.text(
        xlim[1] - 0.16 * (xlim[1] - xlim[0]),
        ylim[1] - 0.04 * (ylim[1] - ylim[0]),
        "High anxiety,\nHigh score",
        **label_kwargs,
    )
    ax.text(
        xlim[0] + 0.02 * (xlim[1] - xlim[0]),
        ylim[0] + 0.06 * (ylim[1] - ylim[0]),
        "Low anxiety,\nLow score",
        **label_kwargs,
    )
    ax.text(
        xlim[1] - 0.16 * (xlim[1] - xlim[0]),
        ylim[0] + 0.06 * (ylim[1] - ylim[0]),
        "High anxiety,\nLow score",
        **label_kwargs,
    )

    ax.set_xlabel("Math Anxiety Index (Country Mean)")
    ax.set_ylabel("Mean Math Score")
    ax.set_title(
        "Student Wellbeing vs Math Performance (2022)", fontweight="bold", pad=12
    )
    ax.grid(alpha=0.3)

    fig.tight_layout()
    save_figure(fig, "5_wellbeing_quadrant")
    plt.close(fig)


# ---------------------------------------------------------------
# Chart 6: Correlation Heatmap of Drivers
# ---------------------------------------------------------------
def chart_correlation_heatmap(df_2022):
    """Correlation matrix of school/student drivers vs scores."""
    print("\n[6/6] Correlation heatmap...")

    cols = {
        "MATHMOT": "Math Motivation",
        "BELONG": "Sense of Belonging",
        "DISCLIM": "Disciplinary Climate",
        "TEACHSUP": "Teacher Support",
        "ANXMAT": "Math Anxiety",
        "ESCS": "Socio-Economic Status",
        "Math_MeanScore": "Math Score",
        "Reading_MeanScore": "Reading Score",
        "Science_MeanScore": "Science Score",
    }
    available = [c for c in cols if c in df_2022.columns]
    df = df_2022[available].dropna()
    df = df.rename(columns=cols)

    corr = df.corr()

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.75, "label": "Pearson r"},
        ax=ax,
    )
    ax.set_title(
        "Correlation Between Drivers and Performance (2022)",
        fontweight="bold",
        pad=12,
    )
    plt.xticks(rotation=40, ha="right")
    plt.yticks(rotation=0)

    fig.tight_layout()
    save_figure(fig, "6_correlation_heatmap")
    plt.close(fig)


# ---------------------------------------------------------------
# Chart 7: Score Distribution Density
# ---------------------------------------------------------------
def chart_score_distribution(df_2022):
    """KDE plots of student-level score distributions by subject."""
    print("\n[7/8] Score distribution density...")

    df = df_2022[
        ["Math_MeanScore", "Reading_MeanScore", "Science_MeanScore"]
    ].dropna()

    fig, ax = plt.subplots(figsize=(10, 6))

    for subject, color in [
        ("Math", COLORS["math"]),
        ("Reading", COLORS["reading"]),
        ("Science", COLORS["science"]),
    ]:
        sns.kdeplot(
            df[f"{subject}_MeanScore"],
            label=subject,
            color=color,
            ax=ax,
            fill=True,
            alpha=0.25,
            linewidth=2,
        )

    ax.set_xlabel("Score")
    ax.set_ylabel("Density")
    ax.set_title(
        "Distribution of Student Scores by Subject (2022)",
        fontweight="bold",
        pad=12,
    )
    ax.legend(title="Subject", loc="upper right")
    ax.grid(alpha=0.3)
    ax.set_xlim(100, 800)

    fig.tight_layout()
    save_figure(fig, "7_score_distribution")
    plt.close(fig)


# ---------------------------------------------------------------
# Chart 8: World Map (Choropleth) of Math Scores
# ---------------------------------------------------------------
def chart_world_map(df_2022):
    """Choropleth world map of mean math scores by country.

    Tries plotly first (high quality). Falls back to a simple bar chart
    if plotly/kaleido cannot render PNG.
    """
    print("\n[8/8] World map of math scores...")

    summary = (
        df_2022.groupby("CNT")["Math_MeanScore"].mean().reset_index()
    )
    summary["iso_alpha"] = summary["CNT"].apply(to_iso3)
    summary["Country"] = summary["CNT"].apply(get_country_name)

    output_dir = os.path.join(PROJECT_ROOT, "output", "figures")
    os.makedirs(output_dir, exist_ok=True)
    png_path = os.path.join(output_dir, "8_world_map.png")
    pdf_path = os.path.join(output_dir, "8_world_map.pdf")

    # Try plotly first
    try:
        import plotly.express as px

        fig = px.choropleth(
            summary,
            locations="iso_alpha",
            color="Math_MeanScore",
            hover_name="Country",
            color_continuous_scale="RdYlBu",
            range_color=(330, 580),
            title="Mean Math Score by Country (PISA 2022)",
            labels={"Math_MeanScore": "Mean Math Score"},
        )
        fig.update_geos(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="grey",
            projection_type="natural earth",
        )
        fig.update_layout(
            title_font_size=16,
            title_x=0.5,
            margin=dict(l=10, r=10, t=60, b=10),
            coloraxis_colorbar=dict(title="Math Score", thickness=15, len=0.6),
        )
        fig.write_image(png_path, width=1400, height=800, scale=2)
        fig.write_image(pdf_path, width=1400, height=800)
        # Also save HTML for interactivity
        fig.write_html(os.path.join(output_dir, "8_world_map.html"))
        print("  Saved: 8_world_map.png, .pdf, and .html")
        return
    except Exception as e:
        print(f"  Plotly export failed ({type(e).__name__}). Trying matplotlib fallback.")

    # Matplotlib fallback: ranked country bar chart styled as a map alternative
    summary_sorted = summary.sort_values("Math_MeanScore", ascending=True).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(11, max(8, len(summary_sorted) * 0.18)))
    cmap = plt.cm.RdYlBu
    norm = plt.Normalize(vmin=330, vmax=580)
    colors = cmap(norm(summary_sorted["Math_MeanScore"]))

    ax.barh(
        summary_sorted["Country"],
        summary_sorted["Math_MeanScore"],
        color=colors,
        edgecolor="white",
        linewidth=0.5,
    )
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label("Math Score", rotation=270, labelpad=15)
    ax.set_xlabel("Mean Math Score")
    ax.set_title(
        "Mean Math Score by Country (PISA 2022)",
        fontweight="bold",
        pad=12,
    )
    ax.set_xlim(300, 600)
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    save_figure(fig, "8_world_map")
    plt.close(fig)


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
def main():
    setup_style()
    data = load_data()
    df_2022 = data["2022"]
    df_2018 = data["2018"]

    chart_country_performance(df_2022)
    chart_gender_gap(df_2022)
    chart_escs_comparison(df_2022, df_2018)
    chart_school_climate(df_2022)
    chart_wellbeing_quadrant(df_2022)
    chart_correlation_heatmap(df_2022)
    chart_score_distribution(df_2022)
    chart_world_map(df_2022)

    print("\n" + "=" * 50)
    print("All charts generated successfully.")
    print(f"Output: {os.path.join(PROJECT_ROOT, 'output', 'figures')}")
    print("=" * 50)


if __name__ == "__main__":
    main()
