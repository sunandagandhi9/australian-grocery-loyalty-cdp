# Australian Grocery Loyalty CDP & Campaign Orchestrator

A recruiter-friendly Martech portfolio project inspired by Australian grocery loyalty programs.

> This project uses fully synthetic data. It does not use real Woolworths, Everyday Rewards, or customer data.

## Business Problem

Australian grocery retailers collect large volumes of customer behaviour data across online delivery, click & collect, and in-store shopping. Marketing teams need to convert this data into useful customer profiles, loyalty segments, personalised campaigns, and measurable campaign outcomes.

This project simulates how a Customer Data Platform (CDP) and campaign orchestration layer can support loyalty marketing.

## What This Project Does

1. Generates synthetic Australian grocery loyalty customers.
2. Simulates ecommerce and grocery shopping events.
3. Builds Customer 360 profiles.
4. Creates rule-based audience segments.
5. Triggers personalised loyalty campaigns.
6. Simulates campaign outcomes such as opens, clicks, conversions, revenue, and ROI.
7. Displays results in a Streamlit dashboard.

## Martech Concepts Demonstrated

- Event tracking
- Customer Data Platform logic
- Customer 360 profile building
- Identity fields: customer ID and anonymous ID
- Loyalty tiers
- Audience segmentation
- Triggered campaign journeys
- Campaign analytics
- Revenue and ROI reporting

## Project Structure

```text
.
├── data/
├── src/
│   ├── config.py
│   ├── data_generator.py
│   ├── profile_builder.py
│   ├── segmentation.py
│   ├── campaign_engine.py
│   └── main.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

## How to Run

### 1. Clone or download the project

```bash
cd australian_grocery_loyalty_cdp
```

### 2. Create a virtual environment

Mac/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the data pipeline

```bash
python -m src.main
```

This creates CSV files inside the `data/` folder.

### 5. Launch the dashboard

```bash
streamlit run streamlit_app.py
```

## Campaigns Included

| Segment | Triggered Campaign |
|---|---|
| New Prospect | Welcome Booster |
| Cart Abandoner | Cart Recovery |
| Fresh Produce Buyer | Fresh Produce Offer |
| Dormant Loyalty Member | Dormant Member Winback |
| High Value Loyalty Member | High Value Rewards |
| Online Delivery Shopper | Weekly Shop Booster |

## Example Business Questions Answered

- Which loyalty segments are largest?
- Which campaigns generate the most revenue?
- Which campaign has the highest conversion rate?
- How do customer behaviours differ across loyalty tiers?
- Which states have the strongest loyalty customer base?
- Which shopping modes generate the most revenue?

## Resume Bullet

Built an Australian grocery loyalty CDP simulator using Python, pandas, and Streamlit to generate synthetic event-level customer data, create Customer 360 profiles, segment loyalty audiences, trigger personalised campaigns, and measure campaign ROI through an interactive dashboard.

## Disclaimer

This project is inspired by common Australian grocery loyalty concepts. It is not affiliated with Woolworths Group, Everyday Rewards, or any real retailer.
