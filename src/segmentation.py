"""Audience segmentation rules for the grocery loyalty CDP."""

from __future__ import annotations

import pandas as pd


def assign_segments(profiles: pd.DataFrame) -> pd.DataFrame:
    df = profiles.copy()
    segments = []

    for _, row in df.iterrows():
        customer_segments = []

        if row["marketing_consent"] is False:
            customer_segments.append("No Marketing Consent")

        if row["total_orders"] == 0 and row["sessions"] >= 2:
            customer_segments.append("New Prospect")

        if row["cart_adds"] > row["total_orders"] and row["days_since_last_seen"] <= 14:
            customer_segments.append("Cart Abandoner")

        if row["lifetime_value"] >= 700 or row["loyalty_tier"] in ["Gold", "Platinum"]:
            customer_segments.append("High Value Loyalty Member")

        if row["days_since_last_purchase"] >= 60 and row["total_orders"] > 0:
            customer_segments.append("Dormant Loyalty Member")

        if row["preferred_category"] == "Fresh Produce" and row["total_orders"] >= 2:
            customer_segments.append("Fresh Produce Buyer")

        if row["preferred_shopping_mode"] == "Online Delivery":
            customer_segments.append("Online Delivery Shopper")

        if row["avg_basket_value"] >= 120:
            customer_segments.append("High Basket Value Shopper")

        if not customer_segments:
            customer_segments.append("General Loyalty Member")

        segments.append("|".join(customer_segments))

    df["segments"] = segments
    return df


def explode_segments(segmented_profiles: pd.DataFrame) -> pd.DataFrame:
    return (
        segmented_profiles[["customer_id", "segments"]]
        .assign(segment=lambda d: d["segments"].str.split("|"))
        .explode("segment")
        .drop(columns=["segments"])
        .reset_index(drop=True)
    )
