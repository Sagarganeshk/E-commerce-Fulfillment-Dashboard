import streamlit as st
import pandas as pd
import os
import sys
import plotly.express as px

# --- Fix for imports ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_preprocessing import prepare_processed_csv
from src.analysis import kpis, rate_by_group, avg_delay_by_group, monthly_trend
from src.visualization import (
    status_pie, courier_stack, delay_box_by_courier,
    regional_stack, monthly_orders_trend, cost_vs_delay
)

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="E-commerce Fulfillment Dashboard",
    page_icon="📦",
    layout="wide"
)

# -----------------------------
# Sidebar - Upload & Filters
# -----------------------------
st.sidebar.header("Upload & Filters")
uploaded_file = st.sidebar.file_uploader("Upload your orders CSV", type=["csv"])

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# -----------------------------
# Load / Process Data
# -----------------------------
if uploaded_file:
    raw_path = os.path.join(DATA_DIR, "uploaded_orders.csv")
    with open(raw_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    df = prepare_processed_csv(raw_path, os.path.join(DATA_DIR, "processed_orders.csv"))
else:
    processed_path = os.path.join(DATA_DIR, "processed_orders.csv")
    if os.path.exists(processed_path):
        df = pd.read_csv(
            processed_path,
            parse_dates=["OrderDate", "ShipDate", "DeliveryDate"],
            dayfirst=True
        )
    else:
        df = pd.DataFrame()
        st.warning("No dataset found. Upload a CSV to see the dashboard.")

if not df.empty:
    # -----------------------------
    # Preprocessing
    # -----------------------------
    df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors='coerce')
    df["ShipDate"] = pd.to_datetime(df["ShipDate"], errors='coerce')
    df["DeliveryDate"] = pd.to_datetime(df["DeliveryDate"], errors='coerce')
    df["OrderMonth"] = df["OrderDate"].dt.to_period("M").astype(str)

    # CustomerID handling
    if "Customer Id" in df.columns:
        df.rename(columns={"Customer Id": "CustomerID"}, inplace=True)
    elif "customer_id" in df.columns:
        df.rename(columns={"customer_id": "CustomerID"}, inplace=True)
    elif "CustomerID" not in df.columns:
        df["CustomerID"] = range(1, len(df)+1)

    # Auto-generate useful columns
    df["ProcessingDays"] = (df["ShipDate"] - df["OrderDate"]).dt.days
    df["DeliveryDays"] = (df["DeliveryDate"] - df["ShipDate"]).dt.days
    df["TotalFulfillmentDays"] = (df["DeliveryDate"] - df["OrderDate"]).dt.days
    df["LateDelivery"] = df["TotalFulfillmentDays"] > 7

    # -----------------------------
    # Sidebar Filters
    # -----------------------------
    min_date, max_date = df["OrderDate"].min(), df["OrderDate"].max()
    date_range = st.sidebar.date_input("Order Date Range", [min_date, max_date])

    courier_options = ["All"] + df["Courier"].dropna().unique().tolist()
    selected_courier = st.sidebar.selectbox("Select Courier", courier_options)

    region_options = ["All"] + df["Region"].dropna().unique().tolist()
    selected_region = st.sidebar.selectbox("Select Region", region_options)

    # Apply filters
    filtered_df = df.copy()
    if date_range:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_df = filtered_df[(filtered_df["OrderDate"] >= start) & (filtered_df["OrderDate"] <= end)]
    if selected_courier != "All":
        filtered_df = filtered_df[filtered_df["Courier"] == selected_courier]
    if selected_region != "All":
        filtered_df = filtered_df[filtered_df["Region"] == selected_region]
else:
    filtered_df = pd.DataFrame()

# -----------------------------
# Main Page - Dashboard Title
# -----------------------------
st.title("📊 E-commerce Fulfillment Dashboard")
st.markdown(
    """
    Welcome to your interactive dashboard! Explore delivery datasets, analyze performance by courier and region, 
    and visualize key metrics and trends.
    """
)

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Dataset", "KPIs & Trends", "Courier Analysis", "Regional Analysis"])

with tab1:
    st.markdown("## 📦 Dataset Preview")
    if not filtered_df.empty:
        st.markdown("Explore the first 20 rows of your uploaded/processed orders dataset.")
        st.dataframe(filtered_df.head(20))
        st.download_button(
            "Download Processed Data",
            filtered_df.to_csv(index=False),
            "processed_orders.csv"
        )
    else:
        st.info("Upload a dataset and apply filters to see it here.")

with tab2:
    st.markdown("## 📈 Key Performance Indicators")
    if not filtered_df.empty:
        for k, v in kpis(filtered_df).items():
            st.metric(k, v)

        st.plotly_chart(status_pie(filtered_df), use_container_width=True)

        monthly_summary = filtered_df.groupby("OrderMonth").agg(
            Orders=("CustomerID", "count"),
            AvgDeliveryDays=("TotalFulfillmentDays", "mean")
        ).reset_index()
        fig = px.line(
            monthly_summary,
            x="OrderMonth",
            y=["Orders", "AvgDeliveryDays"],
            markers=True,
            title="Monthly Orders & Avg Delivery Days"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(cost_vs_delay(filtered_df), use_container_width=True)
    else:
        st.info("Upload a dataset and apply filters to see KPIs.")

with tab3:
    st.markdown("## 🚚 Courier Analysis")
    if not filtered_df.empty:
        st.plotly_chart(courier_stack(filtered_df), use_container_width=True)
        fig_box = px.box(
            filtered_df,
            x="Courier",
            y="TotalFulfillmentDays",
            color="Courier",
            points="all",
            title="Total Fulfillment Days by Courier"
        )
        st.plotly_chart(fig_box, use_container_width=True)
        st.write(avg_delay_by_group(filtered_df, "Courier"))
    else:
        st.info("Upload a dataset to analyze courier performance.")

with tab4:
    st.markdown("## 🌍 Regional Analysis")
    if not filtered_df.empty:
        st.plotly_chart(regional_stack(filtered_df), use_container_width=True)
        st.write(rate_by_group(filtered_df, "Region"))
    else:
        st.info("Upload a dataset to analyze regional performance.")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit and Plotly")
