"""
Utility for building an airtime‑coverage pie chart based on a natural‑language query.

Designed to be imported from a Streamlit app (or any other Python script).

Example usage:

    import streamlit as st
    from utils.pcl_coverage import draw_sensor_piechart

    buf, stats = draw_sensor_piechart(
        "draw a pie chart for the percentage of airtime detected by pcl "
        "for high altitude slow speed orb flights"
    )
    st.image(buf)
"""

import io
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# ------------------------------------------------------------------
# 1. Load data (once – cached in memory for the lifetime of the process)
# ------------------------------------------------------------------
DATA_ROOT = Path(__file__).resolve().parents[0]

mapping = pd.read_csv(DATA_ROOT / "sortie_tracker_type_mapping.csv")
fixed   = pd.read_csv(DATA_ROOT / "fixedFences(in).csv")

# ------------------------------------------------------------------
# 2. Natural‑language filter parser
# ------------------------------------------------------------------
def parse_filters(nl_query: str) -> dict:
    """
    Extracts flight and sensor filters (Platform, Altitude, Speed, c_uas, etc.) from a natural language query.
    Example: "high altitude low speed orb flights detected by pcl"
    """
    nl = nl_query.lower()
    filters = {}

    # ---------- Platform ----------
    platform_keywords = [
        "orb", "kairos", "fiber", "afo", "parrot", "quantix",
        "neros", "sturnas", "boresight", "mavic", "blimp"
    ]
    for word in platform_keywords:
        if word in nl:
            filters["Platform"] = word.capitalize()
            break

    # ---------- Altitude ----------
    if re.search(r"\bhigh\b", nl):
        filters["Altitude"] = "High"
    elif re.search(r"\blow\b", nl):
        filters["Altitude"] = "Low"
    elif re.search(r"\bmedium\b", nl):
        filters["Altitude"] = "Medium"

    # ---------- Speed ----------
    if re.search(r"high speed|fast", nl):
        filters["Speed"] = "Fast"
    elif re.search(r"low speed|slow", nl):
        filters["Speed"] = "Slow"
    elif re.search(r"medium speed", nl):
        filters["Speed"] = "Medium"

    # ---------- Sensor ----------
    sensor_keywords = ["pcl", "gotcha", "ring_5", "stardust"]
    for sensor in sensor_keywords:
        if sensor.lower() in nl:
            filters["c_uas"] = sensor.upper()
            break

    # Default to PCL
    if "c_uas" not in filters:
        filters["c_uas"] = "PCL"

    return filters


# ------------------------------------------------------------------
# 3. Main pie‑chart builder – returns PNG buffer + summary dict
# ------------------------------------------------------------------
def draw_sensor_piechart(nl_query: str) -> tuple[io.BytesIO, dict]:
    """
    Parameters
    ----------
    nl_query : str
        Natural‑language query, e.g.
        "draw a pie chart for the percentage of airtime detected by pcl for high altitude slow speed orb flights"

    Returns
    -------
    buffer : BytesIO
        PNG image in memory – suitable for `st.image(buffer)` or download links.
    summary : dict
        Contains flight count, total airtime, sensor airtime, coverage %, and the applied filters.
    """
    # 1️⃣ Parse query
    filters = parse_filters(nl_query)
    sensor_name = filters.pop("c_uas", "PCL")
    applied_filters = {**filters}          # copy for output

    print(f"Applying filters: {applied_filters} | c_uas: {sensor_name}")

    df = mapping.copy()

    # 2️⃣ Apply column‑based filters (case‑insensitive)
    for col, val in applied_filters.items():
        if col in df.columns:
            df = df[df[col].str.contains(val, case=False, na=False)]

    if df.empty:
        warning = "⚠️ No flights match the given filters."
        print(warning)
        # Still return a blank buffer so Streamlit can handle it gracefully
        buf = io.BytesIO()
        plt.figure(figsize=(6, 6))
        plt.text(0.5, 0.5, warning, ha="center", va="center")
        plt.axis("off")
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        return buf, {
            "error": warning,
            "flights": 0,
            "total_airtime_sec": 0.0,
            "detected_airtime_sec": 0.0,
            "coverage_pct": 0.0,
            "filters_applied": applied_filters,
            "sensor": sensor_name,
        }

    # 3️⃣ Merge with fixed fences & filter for 'enter' events
    merged = fixed.merge(df, left_on="track_id", right_on="RID", how="inner")
    enter_events = merged[merged["event_type"].str.lower() == "enter"]

    total_airtime = float(enter_events["seconds_in_range"].sum())

    sensor_events = enter_events[
        enter_events["c_uas"].str.contains(sensor_name, case=False, na=False)
    ]
    detected_airtime = float(sensor_events["seconds_in_range"].sum())
    undetected_airtime = max(total_airtime - detected_airtime, 0.0)

    # 4️⃣ Draw pie chart (in memory only – no plt.show())
    labels = [f"Detected by {sensor_name}", "Not detected"]
    sizes = [detected_airtime, undetected_airtime]
    colors = ["#66b3ff", "#ff9999"]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
    )
    ax.set_title(f"{sensor_name} Airtime Coverage for {nl_query.strip().capitalize()}")
    plt.axis("equal")

    # Close the figure to free memory
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    # 5️⃣ Summary dictionary (for Streamlit / logs)
    summary = {
        "flights": len(df),
        "total_airtime_sec": total_airtime,
        "detected_airtime_sec": detected_airtime,
        "coverage_pct": (
            detected_airtime / total_airtime * 100 if total_airtime else 0.0
        ),
        "filters_applied": applied_filters,
        "sensor": sensor_name,
    }

    # Optional: print a console summary (kept for debugging)
    print("\n Summary ")
    print(f"Flights matching filters: {len(df)}")
    print(f"Total airtime: {total_airtime:.1f} sec")
    print(
        f"{sensor_name}-detected airtime: {detected_airtime:.1f} sec"
    )
    if total_airtime > 0:
        print(
            f"{sensor_name} Coverage: {(detected_airtime / total_airtime) * 100:.2f}%"
        )
    else:
        print("Coverage: 0.00% (no airtime found)")

    return buf, summary
