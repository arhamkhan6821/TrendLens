import json
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from scipy.stats import theilslopes, kendalltau

st.set_page_config(page_title="TrendLens Lite", page_icon="🌍", layout="wide")
st.title("🌍 TrendLens Lite")
st.caption("A small Earth-system trend explorer using NASA POWER monthly data")

st.markdown("""
Explore how near-surface air temperature or precipitation has changed at a selected
location. Data are retrieved live from NASA POWER. Trend estimates describe the
selected data series; they do not establish causes.
""")

with st.sidebar:
    st.header("Investigation")
    location = st.selectbox("Location", ["Dhaka, Bangladesh", "Chattogram, Bangladesh", "Rajshahi, Bangladesh"])
    coords = {
        "Dhaka, Bangladesh": (23.8103, 90.4125),
        "Chattogram, Bangladesh": (22.3569, 91.7832),
        "Rajshahi, Bangladesh": (24.3745, 88.6042),
    }
    variable_label = st.selectbox("Earth-system variable", ["Air temperature", "Precipitation"])
    parameter = "T2M" if variable_label == "Air temperature" else "PRECTOTCORR"
    start_year = st.slider("Start year", 1981, 2020, 2001)
    end_year = st.slider("End year", max(1982, start_year + 1), 2025, 2025)
    fetch = st.button("Fetch NASA data", type="primary", use_container_width=True)

lat, lon = coords[location]
units = "°C" if parameter == "T2M" else "mm/day"
pretty = "2-m air temperature" if parameter == "T2M" else "corrected precipitation rate"

@st.cache_data(ttl=3600, show_spinner=False)
def get_power_data(param, latitude, longitude, first_year, last_year):
    url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
    params = {
        "parameters": param,
        "community": "AG",
        "longitude": longitude,
        "latitude": latitude,
        "start": first_year,
        "end": last_year,
        "format": "JSON",
    }
    response = requests.get(url, params=params, timeout=45)
    response.raise_for_status()
    payload = response.json()
    values = payload["properties"]["parameter"][param]
    rows = []
    for key, value in values.items():
        if key.endswith("13") or value is None:
            continue
        try:
            number = float(value)
            if number < -900:
                continue
            year = int(key[:4])
            month = int(key[4:6])
            rows.append({"date": pd.Timestamp(year=year, month=month, day=1), "value": number})
        except (ValueError, TypeError):
            continue
    df = pd.DataFrame(rows).sort_values("date")
    if df.empty:
        raise ValueError("NASA POWER returned no usable monthly observations.")
    return df

if "loaded_key" not in st.session_state:
    st.session_state.loaded_key = None
if fetch:
    st.session_state.loaded_key = (parameter, lat, lon, start_year, end_year)

key = st.session_state.loaded_key
if key is None:
    st.info("Choose an investigation in the sidebar and click **Fetch NASA data**.")
    st.markdown("**Data source:** NASA POWER monthly point API · **Location:** Dhaka is preselected.")
    st.stop()

try:
    with st.spinner("Retrieving monthly observations from NASA POWER..."):
        monthly = get_power_data(*key)
except Exception as exc:
    st.error(f"Could not retrieve NASA POWER data: {exc}")
    st.caption("Check your internet connection and try again. The app needs live access to the NASA POWER API.")
    st.stop()

annual = (monthly.assign(year=monthly["date"].dt.year)
          .groupby("year", as_index=False)["value"].mean())
if len(annual) < 5:
    st.error("Not enough annual observations to estimate a meaningful trend.")
    st.stop()

slope, intercept, low, high = theilslopes(annual["value"], annual["year"], 0.95)
tau, p_value = kendalltau(annual["year"], annual["value"])
first = annual.iloc[0]["value"]
last = annual.iloc[-1]["value"]
change = last - first

c1, c2, c3, c4 = st.columns(4)
c1.metric("Annual observations", f"{len(annual)}")
c2.metric("Estimated trend", f"{slope:+.4f} {units}/year")
c3.metric("95% slope interval", f"{low:+.4f} to {high:+.4f}")
c4.metric("Kendall trend p-value", f"{p_value:.4g}")

st.subheader(f"{variable_label} over time — {location}")
fig = px.line(annual, x="year", y="value", markers=True,
              labels={"year": "Year", "value": f"Annual mean ({units})"},
              title=f"Annual mean {pretty}")
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.subheader("What the analysis says")
direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "approximately flat"
if p_value < 0.05:
    significance = "The monotonic association is statistically significant at the 0.05 level."
else:
    significance = "The data do not provide sufficient evidence of a monotonic trend at the 0.05 level."
st.write(f"The Theil–Sen estimate indicates an **{direction}** trend of **{slope:+.4f} {units} per year**.")
st.write(significance)
st.write(f"Across the selected period, the first-to-last annual mean difference is **{change:+.3f} {units}**.")

with st.expander("Methods, data and limitations"):
    st.markdown(f"""
    - **Source:** NASA POWER monthly point API.
    - **Parameter:** `{parameter}` ({pretty}).
    - **Coordinates:** {lat:.4f}° N, {lon:.4f}° E.
    - **Period:** {int(annual.year.min())}–{int(annual.year.max())}.
    - **Aggregation:** arithmetic mean of available monthly values within each calendar year.
    - **Trend magnitude:** Theil–Sen median slope, with a 95% confidence interval.
    - **Trend evidence:** Kendall's tau rank association and its p-value (SciPy implementation).
    - **Missing values:** NASA POWER sentinel values are excluded; only returned valid monthly observations are used.

    **Important limitations:** This is a point-based gridded/reanalysis-informed product, not a direct
    thermometer or rain-gauge record. Annual averaging can hide seasonal changes. The basic
    Kendall test does not correct for serial autocorrelation or multiple testing. A p-value is
    not the probability that the trend is true, and statistical association does not prove causation.
    """)
st.download_button("Download annual results (CSV)", annual.to_csv(index=False).encode("utf-8"),
                   file_name="trendlens_annual_results.csv", mime="text/csv")
st.caption("Built for NASA Space Apps Challenge 2026 · TrendLens Lite")
