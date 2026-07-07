"""Run the full Australian Grocery Loyalty CDP pipeline."""

from pathlib import Path
import pandas as pd

from src.config import DATA_DIR
from src.data_generator import GeneratorSettings, save_generated_data
from src.profile_builder import build_customer_profiles
from src.segmentation import assign_segments, explode_segments
from src.campaign_engine import create_campaign_triggers, simulate_campaign_results, campaign_summary


def main() -> None:
    Path(DATA_DIR).mkdir(exist_ok=True)

    print("[1/5] Generating synthetic Australian grocery loyalty data...")
    save_generated_data(GeneratorSettings())

    print("[2/5] Loading raw data...")
    customers = pd.read_csv(Path(DATA_DIR) / "customers.csv")
    events = pd.read_csv(Path(DATA_DIR) / "events.csv")
    orders = pd.read_csv(Path(DATA_DIR) / "orders.csv")

    print("[3/5] Building Customer 360 profiles...")
    profiles = build_customer_profiles(customers, events, orders)
    profiles.to_csv(Path(DATA_DIR) / "customer_360_profiles.csv", index=False)

    print("[4/5] Assigning CDP audience segments...")
    segmented = assign_segments(profiles)
    segment_membership = explode_segments(segmented)
    segmented.to_csv(Path(DATA_DIR) / "segmented_customers.csv", index=False)
    segment_membership.to_csv(Path(DATA_DIR) / "segment_membership.csv", index=False)

    print("[5/5] Triggering campaigns and calculating performance...")
    triggers = create_campaign_triggers(segmented)
    campaign_results = simulate_campaign_results(triggers)
    summary = campaign_summary(campaign_results)
    triggers.to_csv(Path(DATA_DIR) / "campaign_triggers.csv", index=False)
    campaign_results.to_csv(Path(DATA_DIR) / "campaign_results.csv", index=False)
    summary.to_csv(Path(DATA_DIR) / "campaign_summary.csv", index=False)

    print("\nPipeline complete.")
    print(f"Customers: {len(customers):,}")
    print(f"Events: {len(events):,}")
    print(f"Orders: {len(orders):,}")
    print(f"Campaign sends: {len(campaign_results):,}")
    print("\nTop campaigns by revenue:")
    print(summary.head().to_string(index=False))
    print("\nRun dashboard with: streamlit run streamlit_app.py")


if __name__ == "__main__":
    main()
