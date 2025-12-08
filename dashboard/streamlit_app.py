import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import os

# -----------------------------
# Configuration
# -----------------------------
st.set_page_config(page_title="Disk Usage Monitoring Dashboard", page_icon="💽", layout="wide")

DATA_FILE = Path("disk_usage.csv")  # default data file (change as needed)

# -----------------------------
# Helpers
# -----------------------------
@st.cache_data(ttl=30)
def load_disk_usage(path: Path):
    """Load disk usage CSV with two columns: timestamp, usage (percentage).

    Returns a dataframe with a datetime index and numeric 'usage' column.
    """
    if not path.exists():
        # return an empty dataframe with expected columns so rest of the app doesn't break
        df = pd.DataFrame(columns=["timestamp", "usage"])
        return df

    # read with flexible parsing
    df = pd.read_csv(path, names=["timestamp", "usage"], header=0)

    # try converting types
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception:
        # fallback if timestamps are unix seconds
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", errors="coerce")

    df["usage"] = pd.to_numeric(df["usage"], errors="coerce")

    df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    return df


def human_readable_time(dt: datetime):
    if pd.isna(dt):
        return "-"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# -----------------------------
# UI: Sidebar controls
# -----------------------------
st.sidebar.title("Controls")
st.sidebar.markdown("Upload a CSV or use the default `disk_usage.csv` file (two columns: timestamp, usage).")

uploaded_file = st.sidebar.file_uploader("Upload disk usage CSV", type=["csv", "txt"]) 
use_example = st.sidebar.checkbox("Use example sample data (if no file)", value=False)
refresh = st.sidebar.button("Refresh data")

# auto-refresh note: pressing Refresh reruns the app; streamlit caches TTL helps keep reasonable load

# -----------------------------
# Load data (uploaded > local file > example)
# -----------------------------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, names=["timestamp", "usage"], header=0)
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception:
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", errors="coerce")
    df["usage"] = pd.to_numeric(df["usage"], errors="coerce")
else:
    if DATA_FILE.exists() and not use_example:
        df = load_disk_usage(DATA_FILE)
    else:
        # create a small example dataframe
        now = pd.Timestamp.now()
        times = pd.date_range(now - pd.Timedelta(hours=12), now, freq="30min")
        import numpy as np

        usages = 50 + 20 * np.sin(np.linspace(0, 6.28, len(times))) + np.random.normal(0, 2, len(times))
        df = pd.DataFrame({"timestamp": times, "usage": usages.clip(0, 100)})

# -----------------------------
# Header
# -----------------------------
st.title("💽 Disk Usage Monitoring Dashboard")
st.write("Real-time-ish monitoring of disk usage. Upload a CSV or use the local `disk_usage.csv`.")

# -----------------------------
# Quick validation
# -----------------------------
if df.empty:
    st.warning("No data available yet. Upload a CSV or place a `disk_usage.csv` file in the app folder.")
    st.stop()

# -----------------------------
# Prepare metrics
# -----------------------------
current_usage = df["usage"].iloc[-1]
max_usage = df["usage"].max()
min_usage = df["usage"].min()
avg_usage = df["usage"].mean()
last_timestamp = df["timestamp"].iloc[-1]
first_timestamp = df["timestamp"].iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Usage", f"{current_usage:.2f}%", delta=f"{current_usage - avg_usage:+.2f}%")
col2.metric("Peak Usage", f"{max_usage:.2f}%")
col3.metric("Lowest Usage", f"{min_usage:.2f}%")
col4.metric("Average Usage", f"{avg_usage:.2f}%")

st.markdown(
    f"**Data range:** {human_readable_time(first_timestamp)} — {human_readable_time(last_timestamp)}  \
     **Points:** {len(df)}"
)

# -----------------------------
# Main chart: usage over time
# -----------------------------
st.subheader("📈 Disk Usage Trend")
fig = px.line(df, x="timestamp", y="usage", labels={"usage": "Usage (%)", "timestamp": "Time"},
              title="Disk usage over time", template="plotly_white")
fig.update_traces(mode="lines+markers", marker=dict(size=4, opacity=0.6))
fig.update_yaxes(range=[0, 105])

st.plotly_chart(fig, width='stretch')

# -----------------------------
# Distribution + recent points
# -----------------------------
left, right = st.columns((2, 1))
with left:
    st.subheader("📊 Usage Distribution")
    fig_hist = px.histogram(df, x="usage", nbins=25, labels={"usage": "Usage (%)"},
                            title="Histogram of usage values", template="plotly_white")
    st.plotly_chart(fig_hist, width='stretch')

with right:
    st.subheader("🔎 Recent samples")
    st.dataframe(df.tail(10).assign(timestamp=lambda x: x["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")), height=300)

# -----------------------------
# Gauge: show current utilization vs threshold
# -----------------------------
st.subheader("⚠️ Utilization Gauge")
threshold = st.slider("Alert threshold (%)", min_value=50, max_value=100, value=85, step=1)

gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=float(current_usage),
    domain={"x": [0, 1], "y": [0, 1]},
    title={"text": "Current Disk Usage"},
    delta={"reference": float(avg_usage), "increasing": {"color": "red"}},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "darkblue"},
        "steps": [
            {"range": [0, threshold * 0.6], "color": "lightgreen"},
            {"range": [threshold * 0.6, threshold], "color": "gold"},
            {"range": [threshold, 100], "color": "lightcoral"},
        ],
        "threshold": {
            "line": {"color": "red", "width": 4},
            "thickness": 0.75,
            "value": threshold,
        },
    }
))

gauge.update_layout(height=300, margin={"t": 30, "b": 0, "l": 0, "r": 0})
st.plotly_chart(gauge, width='stretch')

# -----------------------------
# Alerts (simple)
# -----------------------------
st.subheader("🔔 Alerts")
recent_exceed = df[df["usage"] >= threshold]
if len(recent_exceed) > 0:
    st.error(f"{len(recent_exceed)} samples exceed the threshold of {threshold}%.")
    st.dataframe(recent_exceed.tail(10).assign(timestamp=lambda x: x["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")))
else:
    st.success("No samples exceed the threshold.")

# -----------------------------
# Export filtered data and simple maintenance
# -----------------------------
st.subheader("Export / Maintenance")
if st.button("Download last 100 rows as CSV"):
    csv = df.tail(100).to_csv(index=False)
    st.download_button(label="Click to download", data=csv, file_name="disk_usage_recent.csv", mime="text/csv")

# small helper to save uploaded file to disk
if uploaded_file is not None:
    if st.button("Save uploaded file as disk_usage.csv"):
        with open(DATA_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Saved uploaded file to {DATA_FILE}")

# optional: manual refresh trigger
if refresh:
    st.experimental_rerun()



