"""Synthetic Australian grocery loyalty data generator.

This module creates fake customer, event, order and loyalty point data inspired by
Australian grocery loyalty programs. It does not use real Woolworths data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import random
import uuid

import numpy as np
import pandas as pd
from faker import Faker

from src.config import CATEGORIES, CHANNELS, DATA_DIR, SHOPPING_MODES, STATES

fake = Faker("en_AU")


@dataclass
class GeneratorSettings:
    n_customers: int = 1200
    start_date: str = "2025-01-01"
    end_date: str = "2025-06-30"
    seed: int = 42


def _tier_from_points(points: int) -> str:
    if points >= 12000:
        return "Platinum"
    if points >= 7000:
        return "Gold"
    if points >= 3000:
        return "Silver"
    return "Bronze"


def generate_customers(settings: GeneratorSettings) -> pd.DataFrame:
    random.seed(settings.seed)
    np.random.seed(settings.seed)

    rows = []
    for i in range(1, settings.n_customers + 1):
        state = random.choice(STATES)
        signup_date = fake.date_between(start_date="-3y", end_date="today")
        points_balance = max(0, int(np.random.gamma(shape=2.2, scale=1500)))
        rows.append(
            {
                "customer_id": f"C{i:05d}",
                "anonymous_id": str(uuid.uuid4()),
                "email": fake.email(),
                "first_name": fake.first_name(),
                "state": state,
                "postcode": fake.postcode(),
                "signup_date": signup_date,
                "loyalty_points_balance": points_balance,
                "loyalty_tier": _tier_from_points(points_balance),
                "marketing_consent": np.random.choice([True, False], p=[0.86, 0.14]),
                "preferred_shopping_mode": np.random.choice(SHOPPING_MODES, p=[0.32, 0.28, 0.40]),
            }
        )
    return pd.DataFrame(rows)


def generate_events_and_orders(customers: pd.DataFrame, settings: GeneratorSettings) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(settings.seed)
    start = datetime.strptime(settings.start_date, "%Y-%m-%d")
    end = datetime.strptime(settings.end_date, "%Y-%m-%d")
    days = (end - start).days

    events = []
    orders = []
    order_id_counter = 1

    for _, customer in customers.iterrows():
        # More active customers have more sessions.
        tier_multiplier = {"Bronze": 1.0, "Silver": 1.25, "Gold": 1.55, "Platinum": 1.9}[customer["loyalty_tier"]]
        n_sessions = max(1, int(rng.poisson(5 * tier_multiplier)))

        for _ in range(n_sessions):
            session_id = str(uuid.uuid4())
            session_start = start + timedelta(days=int(rng.integers(0, days)), hours=int(rng.integers(7, 22)))
            channel = rng.choice(CHANNELS, p=[0.18, 0.16, 0.20, 0.10, 0.12, 0.10, 0.14])
            shopping_mode = customer["preferred_shopping_mode"]
            category = rng.choice(CATEGORIES)

            event_sequence = ["session_start", "category_view", "product_view"]
            add_to_cart = rng.random() < 0.55
            checkout = rng.random() < 0.42 if add_to_cart else False
            purchase = rng.random() < 0.65 if checkout else False

            if add_to_cart:
                event_sequence.append("add_to_cart")
            if checkout:
                event_sequence.append("checkout_started")
            if purchase:
                event_sequence.append("purchase")

            for idx, event_name in enumerate(event_sequence):
                ts = session_start + timedelta(minutes=idx * int(rng.integers(2, 9)))
                events.append(
                    {
                        "event_id": str(uuid.uuid4()),
                        "customer_id": customer["customer_id"],
                        "anonymous_id": customer["anonymous_id"],
                        "session_id": session_id,
                        "timestamp": ts,
                        "event_name": event_name,
                        "channel": channel,
                        "utm_source": channel.lower().replace(" ", "_"),
                        "utm_campaign": rng.choice(["weekly_specials", "fresh_food", "bonus_points", "delivery_offer"]),
                        "category": category,
                        "shopping_mode": shopping_mode,
                        "state": customer["state"],
                    }
                )

            if purchase:
                basket_value = round(float(rng.gamma(shape=4.0, scale=18.0) + rng.uniform(10, 45)), 2)
                points_earned = int(basket_value)
                order_id = f"O{order_id_counter:06d}"
                order_id_counter += 1
                orders.append(
                    {
                        "order_id": order_id,
                        "customer_id": customer["customer_id"],
                        "session_id": session_id,
                        "order_date": session_start + timedelta(minutes=35),
                        "basket_value": basket_value,
                        "points_earned": points_earned,
                        "category": category,
                        "shopping_mode": shopping_mode,
                        "channel": channel,
                        "state": customer["state"],
                    }
                )

    return pd.DataFrame(events), pd.DataFrame(orders)


def save_generated_data(settings: GeneratorSettings | None = None) -> None:
    settings = settings or GeneratorSettings()
    Path(DATA_DIR).mkdir(exist_ok=True)
    customers = generate_customers(settings)
    events, orders = generate_events_and_orders(customers, settings)
    customers.to_csv(Path(DATA_DIR) / "customers.csv", index=False)
    events.to_csv(Path(DATA_DIR) / "events.csv", index=False)
    orders.to_csv(Path(DATA_DIR) / "orders.csv", index=False)
    print(f"Generated {len(customers):,} customers")
    print(f"Generated {len(events):,} events")
    print(f"Generated {len(orders):,} orders")


if __name__ == "__main__":
    save_generated_data()
