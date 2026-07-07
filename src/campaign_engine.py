"""Triggered campaign simulator.

This module decides which customers should receive which campaign based on their
segments, then simulates opens, clicks, conversions and revenue.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import CAMPAIGN_COSTS

CAMPAIGN_RULES = {
    "New Prospect": "Welcome Booster",
    "Cart Abandoner": "Cart Recovery",
    "Fresh Produce Buyer": "Fresh Produce Offer",
    "Dormant Loyalty Member": "Dormant Member Winback",
    "High Value Loyalty Member": "High Value Rewards",
    "High Basket Value Shopper": "Weekly Shop Booster",
    "Online Delivery Shopper": "Weekly Shop Booster",
}

PERFORMANCE_BY_CAMPAIGN = {
    "Welcome Booster": {"open": 0.52, "click": 0.18, "conversion": 0.08, "avg_revenue": 68},
    "Weekly Shop Booster": {"open": 0.48, "click": 0.16, "conversion": 0.10, "avg_revenue": 112},
    "Fresh Produce Offer": {"open": 0.46, "click": 0.14, "conversion": 0.09, "avg_revenue": 74},
    "Cart Recovery": {"open": 0.61, "click": 0.24, "conversion": 0.15, "avg_revenue": 96},
    "Dormant Member Winback": {"open": 0.24, "click": 0.07, "conversion": 0.03, "avg_revenue": 58},
    "High Value Rewards": {"open": 0.68, "click": 0.29, "conversion": 0.18, "avg_revenue": 145},
}


def create_campaign_triggers(segmented_profiles: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in segmented_profiles.iterrows():
        if not row["marketing_consent"]:
            continue
        for segment in row["segments"].split("|"):
            campaign = CAMPAIGN_RULES.get(segment)
            if campaign:
                rows.append(
                    {
                        "customer_id": row["customer_id"],
                        "segment": segment,
                        "campaign_name": campaign,
                        "loyalty_tier": row["loyalty_tier"],
                        "state": row["state"],
                        "preferred_category": row.get("preferred_category", "Unknown"),
                    }
                )
    return pd.DataFrame(rows).drop_duplicates(["customer_id", "campaign_name"])


def simulate_campaign_results(triggers: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for _, row in triggers.iterrows():
        p = PERFORMANCE_BY_CAMPAIGN[row["campaign_name"]]
        tier_boost = {"Bronze": 0.00, "Silver": 0.02, "Gold": 0.04, "Platinum": 0.06}.get(row["loyalty_tier"], 0)
        opened = rng.random() < min(0.95, p["open"] + tier_boost)
        clicked = opened and rng.random() < min(0.85, p["click"] + tier_boost / 2)
        converted = clicked and rng.random() < min(0.70, p["conversion"] + tier_boost / 2)
        revenue = round(float(rng.normal(p["avg_revenue"], p["avg_revenue"] * 0.22)), 2) if converted else 0.0
        revenue = max(revenue, 0.0)
        cost = CAMPAIGN_COSTS[row["campaign_name"]]

        rows.append(
            {
                **row.to_dict(),
                "sent": 1,
                "opened": int(opened),
                "clicked": int(clicked),
                "converted": int(converted),
                "campaign_cost": cost,
                "revenue": revenue,
            }
        )
    return pd.DataFrame(rows)


def campaign_summary(campaign_results: pd.DataFrame) -> pd.DataFrame:
    if campaign_results.empty:
        return pd.DataFrame()
    summary = (
        campaign_results.groupby("campaign_name")
        .agg(
            sent=("sent", "sum"),
            opens=("opened", "sum"),
            clicks=("clicked", "sum"),
            conversions=("converted", "sum"),
            campaign_cost=("campaign_cost", "sum"),
            revenue=("revenue", "sum"),
        )
        .reset_index()
    )
    summary["open_rate"] = (summary["opens"] / summary["sent"] * 100).round(1)
    summary["click_rate"] = (summary["clicks"] / summary["sent"] * 100).round(1)
    summary["conversion_rate"] = (summary["conversions"] / summary["sent"] * 100).round(1)
    summary["roi"] = ((summary["revenue"] - summary["campaign_cost"]) / summary["campaign_cost"]).round(2)
    summary["revenue"] = summary["revenue"].round(2)
    return summary.sort_values("revenue", ascending=False)
