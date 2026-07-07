"""Project configuration for the Australian Grocery Loyalty CDP simulator."""

DATA_DIR = "data"

STATES = ["VIC", "NSW", "QLD", "SA", "WA", "TAS", "ACT", "NT"]
CHANNELS = ["Organic Search", "Paid Search", "Email", "SMS", "App Push", "Social", "Direct"]
SHOPPING_MODES = ["Online Delivery", "Click & Collect", "In Store"]
CATEGORIES = [
    "Fresh Produce",
    "Bakery",
    "Dairy & Eggs",
    "Meat & Seafood",
    "Pantry",
    "Frozen",
    "Health & Beauty",
    "Baby",
    "Pet",
    "Household",
]

LOYALTY_TIERS = ["Bronze", "Silver", "Gold", "Platinum"]

CAMPAIGN_COSTS = {
    "Welcome Booster": 0.12,
    "Weekly Shop Booster": 0.15,
    "Fresh Produce Offer": 0.10,
    "Cart Recovery": 0.18,
    "Dormant Member Winback": 0.20,
    "High Value Rewards": 0.25,
}
