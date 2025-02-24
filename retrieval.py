import requests
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Step 1: Gather Gold Price Data (Last 12 Months)
API_KEY = "8BJ63QT5NGP13RR8"  # Replace with your Alpha Vantage API key
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GLD&apikey={API_KEY}&outputsize=full"
response = requests.get(url)
data = response.json()

# Extract and structure gold price data
time_series = data["Time Series (Daily)"]
gold_df = pd.DataFrame.from_dict(time_series, orient="index")
gold_df = gold_df.rename(columns={"4. close": "price"})
gold_df.index = pd.to_datetime(gold_df.index)
gold_df["price"] = gold_df["price"].astype(float)

# Filter for the last 12 months
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
gold_df = gold_df[(gold_df.index >= start_date) & (gold_df.index <= end_date)]

# Step 2: Obtain Inflation Announcement Dates
cpi_dates = [
    "2024-03-12", "2024-04-10", "2024-05-15", "2024-06-12",
    "2024-07-11", "2024-08-14", "2024-09-11", "2024-10-10",
    "2024-11-13", "2024-12-11", "2025-01-15", "2025-02-12"
]
cpi_dates = pd.to_datetime(cpi_dates)
cpi_df = pd.DataFrame({"announcement_date": cpi_dates})

# Step 3: Preprocess Data
def get_window_data(df, date, days_before=3, days_after=3):
    start = date - timedelta(days=days_before)
    end = date + timedelta(days=days_after)
    return df[(df.index >= start) & (df.index <= end)].copy()

window_data = {}
for date in cpi_df["announcement_date"]:
    window_data[date] = get_window_data(gold_df, date)

# Step 4: Analyze Gold Price Reactions
analysis_results = []
for date, window in window_data.items():
    if not window.empty:
        price_change = window["price"].iloc[-1] - window["price"].iloc[0]
        volatility = window["price"].max() - window["price"].min()
        pct_change = (price_change / window["price"].iloc[0]) * 100
        analysis_results.append({
            "date": date,
            "price_change": price_change,
            "volatility": volatility,
            "pct_change": pct_change
        })
analysis_df = pd.DataFrame(analysis_results)

# Step 5: Visualize the Data
plt.figure(figsize=(12, 6))
for date, window in window_data.items():
    if not window.empty:
        plt.plot(window.index, window["price"], label=date.strftime("%Y-%m-%d"))
plt.title("Gold Price Movements Around CPI Announcements")
plt.xlabel("Date")
plt.ylabel("Gold Price (GLD)")
plt.legend(title="Announcement Dates", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("gold_price_visualization.png")  # Save plot
plt.show()

# Step 6: Summarize Findings
avg_price_change = analysis_df["price_change"].mean()
avg_volatility = analysis_df["volatility"].mean()
avg_pct_change = analysis_df["pct_change"].mean()

if avg_pct_change > 0:
    trend = "Gold prices tend to increase after CPI announcements."
elif avg_pct_change < 0:
    trend = "Gold prices tend to decrease after CPI announcements."
else:
    trend = "No consistent movement in gold prices around CPI announcements."

# Step 7: Generate Trade Ideas
if avg_pct_change > 1:
    trade_idea = "Buy gold (GLD) 3 days before CPI announcements and sell 3 days after, as prices tend to rise."
elif avg_pct_change < -1:
    trade_idea = "Sell gold (GLD) 3 days before CPI announcements and buy back 3 days after, as prices tend to fall."
else:
    trade_idea = "No clear trading opportunity based on historical data."

# Step 8: Document Results
report = f"""
### Gold Price Reaction to CPI Announcements (Last 12 Months)
- **Period**: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
- **Average Price Change**: {avg_price_change:.2f}
- **Average Volatility**: {avg_volatility:.2f}
- **Average Percentage Change**: {avg_pct_change:.2f}%
- **Trend**: {trend}
- **Trade Idea**: {trade_idea}

### Insights
The analysis shows how gold prices (via GLD) react to CPI announcements. Visualizations indicate individual event patterns, while aggregate stats provide a broader view. Traders can use these insights to anticipate movements.
"""

print(report)
with open("gold_cpi_analysis_report.txt", "w") as f:
    f.write(report)

# Display sample outputs
print("Gold Price Data (First 5 Rows):")
print(gold_df.head())
print("\nCPI Announcement Dates:")
print(cpi_df)
print("\nAnalysis Results:")
print(analysis_df)