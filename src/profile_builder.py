"""Customer 360 profile builder.

Turns raw events and orders into one row per customer with marketing traits.
"""

from __future__ import annotations

import pandas as pd


def build_customer_profiles(customers: pd.DataFrame, events: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    events = events.copy()
    orders = orders.copy()
    events["timestamp"] = pd.to_datetime(events["timestamp"])

    if not orders.empty:
        orders["order_date"] = pd.to_datetime(orders["order_date"])
        order_agg = (
            orders.groupby("customer_id")
            .agg(
                total_orders=("order_id", "nunique"),
                lifetime_value=("basket_value", "sum"),
                avg_basket_value=("basket_value", "mean"),
                last_purchase_date=("order_date", "max"),
                total_points_earned=("points_earned", "sum"),
            )
            .reset_index()
        )

        preferred_category = (
            orders.groupby(["customer_id", "category"])
            .size()
            .reset_index(name="count")
            .sort_values(["customer_id", "count"], ascending=[True, False])
            .drop_duplicates("customer_id")[["customer_id", "category"]]
            .rename(columns={"category": "preferred_category"})
        )
    else:
        order_agg = pd.DataFrame(columns=["customer_id", "total_orders", "lifetime_value", "avg_basket_value", "last_purchase_date", "total_points_earned"])
        preferred_category = pd.DataFrame(columns=["customer_id", "preferred_category"])

    event_agg = (
        events.groupby("customer_id")
        .agg(
            total_events=("event_id", "count"),
            sessions=("session_id", "nunique"),
            first_seen=("timestamp", "min"),
            last_seen=("timestamp", "max"),
            cart_adds=("event_name", lambda x: (x == "add_to_cart").sum()),
            checkouts_started=("event_name", lambda x: (x == "checkout_started").sum()),
            purchases_from_events=("event_name", lambda x: (x == "purchase").sum()),
        )
        .reset_index()
    )

    favourite_channel = (
        events.groupby(["customer_id", "channel"])
        .size()
        .reset_index(name="count")
        .sort_values(["customer_id", "count"], ascending=[True, False])
        .drop_duplicates("customer_id")[["customer_id", "channel"]]
        .rename(columns={"channel": "favourite_channel"})
    )

    profiles = customers.merge(event_agg, on="customer_id", how="left")
    profiles = profiles.merge(order_agg, on="customer_id", how="left")
    profiles = profiles.merge(preferred_category, on="customer_id", how="left")
    profiles = profiles.merge(favourite_channel, on="customer_id", how="left")

    numeric_cols = ["total_events", "sessions", "cart_adds", "checkouts_started", "purchases_from_events", "total_orders", "lifetime_value", "avg_basket_value", "total_points_earned"]
    for col in numeric_cols:
        profiles[col] = profiles[col].fillna(0)

    latest_date = events["timestamp"].max()
    profiles["days_since_last_seen"] = (latest_date - pd.to_datetime(profiles["last_seen"])).dt.days.fillna(999).astype(int)
    profiles["days_since_last_purchase"] = (latest_date - pd.to_datetime(profiles["last_purchase_date"])).dt.days.fillna(999).astype(int)
    profiles["conversion_rate"] = (profiles["total_orders"] / profiles["sessions"].replace(0, 1)).round(3)
    profiles["email_engagement_score"] = (profiles["total_events"] * 0.03 + profiles["total_orders"] * 2 + profiles["cart_adds"] * 0.4).round(2)

    return profiles
