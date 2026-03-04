# -------------------------------
# APL Logistics – Delivery Dashboard
# -------------------------------

import streamlit as st
import pandas as pd
import numpy as np

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="APL Logistics Dashboard",
    layout="wide"
)

st.title("APL Logistics – Delivery Performance Dashboard")

# -------------------------------
# Load Dataset (Cached for performance)
# -------------------------------
@st.cache_data
def load_data():
    # Encoding adjusted due to earlier Unicode error
    df = pd.read_csv("APL_Logistics.zip", compression="zip", encoding="latin1")
    return df

df = load_data()

# -------------------------------
# Delivery Gap Engineering
# -------------------------------
# Calculate difference between actual and scheduled shipping days
df["delivery_gap"] = (
    df["Days for shipping (real)"] -
    df["Days for shipment (scheduled)"]
)

# Classify delivery status
df["delivery_status"] = np.where(
    df["delivery_gap"] > 0, "Delayed",
    np.where(df["delivery_gap"] == 0, "On-Time", "Early")
)

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filters")

shipping_mode_filter = st.sidebar.multiselect(
    "Select Shipping Mode",
    options=df["Shipping Mode"].unique(),
    default=df["Shipping Mode"].unique()
)

region_filter = st.sidebar.multiselect(
    "Select Region",
    options=df["Order Region"].unique(),
    default=df["Order Region"].unique()
)

# Apply filters
filtered_df = df[
    (df["Shipping Mode"].isin(shipping_mode_filter)) &
    (df["Order Region"].isin(region_filter))
]

# -------------------------------
# Executive Overview Section
# -------------------------------
st.markdown("---")
st.header("📊 Executive Overview")

total_orders = len(filtered_df)
delayed_orders = len(
    filtered_df[filtered_df["delivery_status"] == "Delayed"]
)

# Avoid division by zero
delay_rate = (
    (delayed_orders / total_orders) * 100
    if total_orders > 0 else 0
)

avg_gap = filtered_df["delivery_gap"].mean()

# Display KPI metrics in columns
col1, col2, col3 = st.columns(3)

col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Delay Rate (%)", f"{delay_rate:.2f}%")
col3.metric("Average Delivery Gap (Days)", f"{avg_gap:.2f}")

# -------------------------------
# Delivery Gap Distribution
# -------------------------------
st.subheader("Delivery Gap Distribution")

gap_counts = (
    filtered_df["delivery_gap"]
    .value_counts()
    .sort_index()
)

st.bar_chart(gap_counts)

# -------------------------------
# Shipping Mode Performance
# -------------------------------
st.markdown("---")
st.header("🚚 Shipping Mode Performance")

# Calculate delay rate by shipping mode
delay_by_mode = (
    filtered_df[filtered_df["delivery_status"] == "Delayed"]
    .groupby("Shipping Mode")
    .size()
    / filtered_df.groupby("Shipping Mode").size()
) * 100

st.subheader("Delay Rate by Shipping Mode (%)")
st.bar_chart(delay_by_mode)

# Compare Scheduled vs Actual Delivery Days
sla_comparison = filtered_df.groupby("Shipping Mode")[
    ["Days for shipment (scheduled)",
     "Days for shipping (real)"]
].mean()

st.subheader("Scheduled vs Actual Delivery Time (Average Days)")
st.dataframe(sla_comparison)

# -------------------------------
# Regional Delay Analysis
# -------------------------------
st.markdown("---")
st.header("🌍 Regional Delay Analysis")

region_delay_rate = (
    filtered_df[filtered_df["delivery_status"] == "Delayed"]
    .groupby("Order Region")
    .size()
    / filtered_df.groupby("Order Region").size()
) * 100

top_regions = (
    region_delay_rate
    .sort_values(ascending=False)
    .head(10)
)

st.subheader("Top 10 Regions by Delay Rate (%)")
st.bar_chart(top_regions)

# -------------------------------
# Financial Impact Section
# -------------------------------
st.markdown("---")
st.header("💰 Financial Impact Analysis")

# Average profit by delivery status
profit_analysis = (
    filtered_df
    .groupby("delivery_status")["Order Profit Per Order"]
    .mean()
)

st.subheader("Average Profit per Order by Delivery Status")
st.bar_chart(profit_analysis)

# Average sales by delivery status
sales_analysis = (
    filtered_df
    .groupby("delivery_status")["Sales"]
    .mean()
)

st.subheader("Average Sales per Order by Delivery Status")
st.bar_chart(sales_analysis)

# -------------------------------
# Key Insights Section (Narrative Layer)
# -------------------------------
st.markdown("---")
st.header("📌 Key Insights")

st.markdown("""
- Overall delay rate remains high, driven primarily by premium shipping modes.
- First Class and Second Class exhibit systematic SLA misalignment.
- Standard Class contributes the highest delayed volume due to shipment scale.
- Financial impact per order is moderate but accumulates at scale.

""")

