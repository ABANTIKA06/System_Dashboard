import pandas as pd
import matplotlib.pyplot as plt

CSV = "/home/abantika/disk_storage/data/disk_usage.csv"

# Read the CSV
df = pd.read_csv(CSV, names=["date", "usage"])
df["date"] = pd.to_datetime(df["date"])

# Simple date-range filter (last 7 days)
df = df[df["date"] >= (df["date"].max() - pd.Timedelta(days=7))]

# Moving average trend line
df["trend"] = df["usage"].rolling(window=3).mean()

# ----------- MAIN LINE PLOT --------------
plt.figure(figsize=(12, 6))
plt.plot(df["date"], df["usage"], marker="o", linewidth=2.5, label="Disk Usage")
plt.plot(df["date"], df["trend"], color="red", linewidth=2, label="Trend (Moving Avg)")

plt.xlabel("Date & Time", fontsize=16, fontweight='bold')
plt.ylabel("Disk Usage (%)", fontsize=16, fontweight='bold')
plt.title("Disk Usage Over Time", fontsize=18, fontweight='bold')
plt.xticks(rotation=45, fontsize=12, fontweight='bold')
plt.yticks(fontsize=12, fontweight='bold')
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend(fontsize=12)

plt.tight_layout()

# Save the figure as PNG
plt.savefig("/home/abantika/disk_storage/dashboard/disk_usage_plot.png")

plt.show()

# ----------- BAR CHART (LAST 10 ENTRIES) --------------
plt.figure(figsize=(10, 4))
last_10 = df.tail(10)
plt.bar(last_10["date"].dt.strftime("%H:%M:%S"), last_10["usage"])
plt.xlabel("Time", fontsize= 19,fontweight="bold")
plt.ylabel("Usage (%)", fontsize=19,fontweight="bold")
plt.title("Last 10 Disk Usage Entries", fontsize=16, fontweight='bold')
plt.xticks(rotation=45,fontweight ="bold")
plt.yticks(fontweight = "bold")
plt.tight_layout()
plt.savefig("/home/abantika/disk_storage/dashboard/disk_usage_barchart.png")
plt.show()

