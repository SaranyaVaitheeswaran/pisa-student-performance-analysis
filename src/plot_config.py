"""
Shared plot configuration for PISA visualization project.
Ensures consistent styling across all charts.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import os

# Color palette (matches Power BI dashboard)
COLORS = {
    "math": "#1f77b4",      # blue
    "reading": "#2ca02c",   # green
    "science": "#ff7f0e",   # orange
    "female": "#e377c2",    # pink
    "male": "#1f77b4",      # blue
    "year_2018": "#888888", # grey
    "year_2022": "#1f77b4", # blue
    "accent": "#d62728",    # red for highlights
}

SUBJECT_PALETTE = {
    "Math": COLORS["math"],
    "Reading": COLORS["reading"],
    "Science": COLORS["science"],
}

# Figure settings
FIG_DPI = 300
FONT_FAMILY = "DejaVu Sans"
FONT_SIZE = 11

# Output directory (relative to project root)
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "output",
    "figures",
)


def setup_style():
    """Apply consistent styling to all plots."""
    sns.set_theme(style="whitegrid", context="paper")
    plt.rcParams.update(
        {
            "font.family": FONT_FAMILY,
            "font.size": FONT_SIZE,
            "axes.titlesize": FONT_SIZE + 1,
            "axes.labelsize": FONT_SIZE,
            "xtick.labelsize": FONT_SIZE - 1,
            "ytick.labelsize": FONT_SIZE - 1,
            "legend.fontsize": FONT_SIZE - 1,
            "figure.dpi": 100,  # screen
            "savefig.dpi": FIG_DPI,  # file
            "savefig.bbox": "tight",
            "savefig.facecolor": "white",
        }
    )


def save_figure(fig, name):
    """Save figure as PNG and PDF in the output directory."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    pdf_path = os.path.join(OUTPUT_DIR, f"{name}.pdf")
    fig.savefig(png_path, dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    print(f"  Saved: {name}.png and {name}.pdf")


# Country code to display name (top countries we will likely highlight)
COUNTRY_NAMES = {
    "SGP": "Singapore", "JPN": "Japan", "KOR": "S. Korea", "TAP": "Chinese Taipei",
    "EST": "Estonia", "MAC": "Macao", "HKG": "Hong Kong", "FIN": "Finland",
    "CAN": "Canada", "IRL": "Ireland", "POL": "Poland", "CHE": "Switzerland",
    "DNK": "Denmark", "AUS": "Australia", "NZL": "New Zealand", "GBR": "UK",
    "USA": "USA", "DEU": "Germany", "NLD": "Netherlands", "BEL": "Belgium",
    "FRA": "France", "ESP": "Spain", "ITA": "Italy", "PRT": "Portugal",
    "SWE": "Sweden", "NOR": "Norway", "AUT": "Austria", "CZE": "Czechia",
    "HUN": "Hungary", "ISR": "Israel", "TUR": "Turkey", "MEX": "Mexico",
    "CHL": "Chile", "BRA": "Brazil", "COL": "Colombia", "ARG": "Argentina",
    "IDN": "Indonesia", "THA": "Thailand", "MYS": "Malaysia", "PHL": "Philippines",
    "VNM": "Vietnam", "QAT": "Qatar", "ARE": "UAE", "SAU": "Saudi Arabia",
    "MAR": "Morocco", "JOR": "Jordan", "DOM": "Dom. Republic", "PAN": "Panama",
    "URY": "Uruguay", "PER": "Peru", "CRI": "Costa Rica", "ALB": "Albania",
    "BGR": "Bulgaria", "HRV": "Croatia", "GRC": "Greece", "LTU": "Lithuania",
    "LVA": "Latvia", "ROU": "Romania", "SVK": "Slovakia", "SVN": "Slovenia",
    "ISL": "Iceland", "LUX": "Luxembourg", "MLT": "Malta", "CYP": "Cyprus",
    "MNG": "Mongolia", "GEO": "Georgia", "KAZ": "Kazakhstan", "AZE": "Azerbaijan",
    "MDA": "Moldova", "MNE": "Montenegro", "MKD": "N. Macedonia", "SRB": "Serbia",
    "UKR": "Ukraine", "BIH": "Bosnia", "PSE": "Palestine", "KOS": "Kosovo",
    "JAM": "Jamaica", "PRY": "Paraguay", "SLV": "El Salvador", "GTM": "Guatemala",
    "BRN": "Brunei", "KHM": "Cambodia", "UZB": "Uzbekistan",
}


def get_country_name(code):
    """Return display name for country code, fallback to code."""
    return COUNTRY_NAMES.get(code, code)


# Mapping from PISA country codes to ISO-3 codes for choropleth maps.
# PISA mostly uses ISO-3 already, but a few special cases need translation.
PISA_TO_ISO3 = {
    # Most codes are identical — only handle PISA-specific exceptions
    "TAP": "TWN",   # Chinese Taipei -> Taiwan
    "QCH": "CHN",   # B-S-J-Z (China)
    "QAZ": "AZE",   # Baku
    "QUR": "UKR",   # Ukrainian regions
    "QMR": "MAR",   # Moroccan regional
    "KOS": "XKX",   # Kosovo (non-standard ISO)
    "KSV": "XKX",   # Kosovo alternative code
    "MAC": "MAC",   # Macao
    "HKG": "HKG",   # Hong Kong
}


def to_iso3(code):
    """Convert PISA country code to ISO-3 for choropleth maps."""
    return PISA_TO_ISO3.get(code, code)
