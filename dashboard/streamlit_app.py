import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
from PIL import Image

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Disk Usage Monitoring Dashboard",
    page_icon="💽",
    layout="wide"
)

BASE_DIR = Path("/home/abantika/disk_storage")

DATA_FILE = BASE_DIR / "data" / "disk_usage.csv"
ALERT_LOG = BASE_DIR / "logs" / "disk_alert.log"

PNG_LINE = BASE_DIR / "dashboard" / "disk_usage_plot.png"
PNG_BAR = BASE_DIR / "dashboard" / "disk_usage_barchart.png"

THRESHOLD = 6

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data(ttl=30)
def load_csv():
    df = pd.read_csv(DATA_FILE, names=["timestamp", "usage"], header=None)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["usage"] = pd.to_numeric(df["usage"])
    return df.sort_values("timestamp")

df = load_csv()

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("💽 Disk Usage Monitoring Dashboard")
st.caption("Linux disk monitoring with alerts, trends and historical analysis")

if df.empty:
    st.warning("No disk usage data available")
    st.stop()

current_usage = df.iloc[-1]["usage"]

# -------------------------------------------------
# STATUS LOGIC
# -------------------------------------------------
if current_usage > THRESHOLD:
    status = "🔴 HIGH"
    color = "red"
elif current_usage == THRESHOLD:
    status = "🟡 WARNING"
    color = "yellow"
else:
    status = "🟢 NORMAL"
    color = "green"

# -------------------------------------------------
# METRICS
# -------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Usage", f"{current_usage}%")
c2.metric("Peak Usage", f"{df['usage'].max()}%")
c3.metric("Lowest Usage", f"{df['usage'].min()}%")
c4.metric("Alert Threshold", f"{THRESHOLD}%")

st.markdown(f"### System Status: {status}")

# -------------------------------------------------
# GAUGE (CURRENT ONLY)
# -------------------------------------------------
gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=current_usage,
    number={"suffix": "%"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": color},
        "steps": [
            {"range": [0, THRESHOLD], "color": "lightgreen"},
            {"range": [THRESHOLD, THRESHOLD], "color": "khaki"},
            {"range": [THRESHOLD, 100], "color": "lightcoral"},
        ],
        "threshold": {
            "line": {"color": "black", "width": 4},
            "value": THRESHOLD
        }
    }
))
gauge.update_layout(height=350)
st.plotly_chart(gauge, width="stretch")

# -------------------------------------------------
# ALERTS (FROM disk_alert.log)
# -------------------------------------------------
st.subheader("🚨 High Disk Usage Alerts")
st.markdown(
    "<span style='color:red; font-weight:bold;'>Red alerts indicate disk usage exceeded threshold</span>",
    unsafe_allow_html=True
)

alerts = []

if ALERT_LOG.exists():
    with open(ALERT_LOG) as f:
        for line in f:
            if "Disk usage is too high:" in line:
                ts, _, msg = line.partition(" Disk usage is too high:")
                alerts.append({
    "Status": "🔴 HIGH",
    "Timestamp": ts.strip(),
    "Usage (%)": msg.replace("%", "").strip()
})


st.metric("Total Alerts", len(alerts))

if alerts:
    st.dataframe(pd.DataFrame(alerts), height=300, width="stretch")
else:
    st.success("No alerts recorded")

# -------------------------------------------------
# PNG CHARTS
# -------------------------------------------------
st.subheader("📊 Disk Usage Visualizations")

c1, c2 = st.columns(2)

with c1:
    if PNG_LINE.exists():
        st.image(Image.open(PNG_LINE), caption="Disk Usage Trend (with moving average)")

with c2:
    if PNG_BAR.exists():
        st.image(Image.open(PNG_BAR), caption="Last 10 Disk Usage Entries")

# -------------------------------------------------
# RECENT RAW DATA
# -------------------------------------------------
st.subheader("📋 Recent Disk Usage Records")
st.dataframe(df.tail(15), height=300, width="stretch")
