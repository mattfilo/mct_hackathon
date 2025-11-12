import pandas as pd
import matplotlib.pyplot as plt
import re
import io
from pathlib import Path

# ------------------------------------------------------------------
# 1. Load data once at import time – cache it for the session.
# ------------------------------------------------------------------
DATA_ROOT = Path(__file__).resolve().parents[0]

mapping = pd.read_csv(DATA_ROOT / "sortie_tracker_type_mapping.csv")
fixed   = pd.read_csv(DATA_ROOT / "fixedFences(in).csv")

# ------------------------------------------------------------------
# 2. Natural‑language filter parser
# ------------------------------------------------------------------
def parse_filters(nl_query: str) -> dict:
    nl = nl_query.lower()
    filters: dict[str, str] = {}

    if "orb" in nl:
        filters["Platform"] = "ORB"
    elif "uas" in nl:
        filters["Platform"] = "UAS"

    # altitude
    if re.search(r"\bhigh\b", nl):
        filters["Altitude"] = "High"
    elif re.search(r"\blow\b", nl):
        filters["Altitude"] = "Low"
    elif re.search(r"\bmedium\b", nl):
        filters["Altitude"] = "Medium"

    # speed
    if re.search(r"\bfast\b|high speed\b", nl):
        filters["Speed"] = "Fast"
    elif re.search(r"\slow\b|low speed\b", nl):
        filters["Speed"] = "Slow"
    elif re.search(r"medium speed\b", nl):
        filters["Speed"] = "Medium"

    return filters


# ------------------------------------------------------------------
# 3. Main chart builder
# ------------------------------------------------------------------
def draw_pcl_piechart(nl_query: str) -> tuple[io.BytesIO, dict]:
    """Return a PNG buffer *and* a summary dictionary."""
    filters = parse_filters(nl_query)
    df = mapping.copy()

    # Apply dynamic filtering (case‑insensitive)
    for col, val in filters.items():
        if col in df.columns:
            df = df[df[col].str.contains(val, case=False, na=False)]

    if df.empty:
        raise ValueError("No flights match the given natural‑language query.")

    merged  = fixed.merge(df, left_on="track_id", right_on="RID", how="inner")
    enter   = merged[merged["event_type"].str.lower() == "enter"]

    total_airtime   = float(enter["seconds_in_range"].sum())
    pcl_events      = enter[enter["c_uas"].str.contains("PCL", case=False, na=False)]
    detected_airtime= float(pcl_events["seconds_in_range"].sum())
    undetected      = max(total_airtime - detected_airtime, 0.0)

    # Pie chart
    labels   = ["Detected by PCL", "Not detected"]
    sizes    = [detected_airtime, undetected]
    colors   = ['#66b3ff', '#ff9999']

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%',
           startangle=90, colors=colors)
    ax.set_title(f'PCL Airtime Coverage for {nl_query.strip().capitalize()} Flights')
    plt.close(fig)                          # release memory

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    summary = {
        "flights": len(df),
        "total_airtime_sec": total_airtime,
        "detected_airtime_sec": detected_airtime,
        "coverage_pct": (detected_airtime / total_airtime) * 100 if total_airtime else 0.0
    }

    return buf, summary