"""Streamlit dashboard for the Australian Grocery Loyalty CDP project."""

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

DATA_DIR = Path("data")

st.set_page_config(page_title="Australian Grocery Loyalty CDP", layout="wide")
st.title("Australian Grocery Loyalty CDP & Campaign Orchestrator")
st.caption("Synthetic Woolworths-style loyalty analytics project. No real customer or company data is used.")


def load_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        st.error("Data files not found. Run `python -m src.main` first.")
        st.stop()
    return pd.read_csv(path)

customers = load_csv("customers.csv")
events = load_csv("events.csv")
orders = load_csv("orders.csv")
profiles = load_csv("segmented_customers.csv")
segments = load_csv("segment_membership.csv")
campaign_results = load_csv("campaign_results.csv")
campaign_summary = load_csv("campaign_summary.csv")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", f"{len(customers):,}")
col2.metric("Events", f"{len(events):,}")
col3.metric("Orders", f"{len(orders):,}")
col4.metric("Campaign Sends", f"{len(campaign_results):,}")

st.divider()

st.subheader("Customer 360 Overview")
col1, col2 = st.columns(2)
with col1:
    tier_counts = profiles["loyalty_tier"].value_counts().reset_index()
    tier_counts.columns = ["loyalty_tier", "customers"]
    fig = px.bar(tier_counts, x="loyalty_tier", y="customers", title="Customers by Loyalty Tier")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    state_counts = profiles["state"].value_counts().reset_index()
    state_counts.columns = ["state", "customers"]
    fig = px.bar(state_counts, x="state", y="customers", title="Customers by Australian State")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("CDP Audience Segments")
segment_counts = segments["segment"].value_counts().reset_index()
segment_counts.columns = ["segment", "customers"]
fig = px.bar(segment_counts, x="customers", y="segment", orientation="h", title="Audience Segment Sizes")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Triggered Campaign Performance")
st.dataframe(campaign_summary, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    fig = px.bar(campaign_summary, x="campaign_name", y="revenue", title="Revenue by Campaign")
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.scatter(
        campaign_summary,
        x="open_rate",
        y="conversion_rate",
        size="revenue",
        hover_name="campaign_name",
        title="Open Rate vs Conversion Rate",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Orders by Shopping Mode")
mode_orders = orders.groupby("shopping_mode")["basket_value"].agg(["count", "sum", "mean"]).reset_index()
mode_orders.columns = ["shopping_mode", "orders", "revenue", "avg_basket"]
st.dataframe(mode_orders, use_container_width=True)

st.subheader("Sample Customer 360 Profiles")
st.dataframe(
    profiles[[
        "customer_id", "state", "loyalty_tier", "preferred_shopping_mode", "preferred_category",
        "total_orders", "lifetime_value", "avg_basket_value", "days_since_last_purchase", "segments"
    ]].head(50),
    use_container_width=True,
)
