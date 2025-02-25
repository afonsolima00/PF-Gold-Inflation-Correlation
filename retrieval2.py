import requests
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Step 1: Gather Gold Price Data (Last 12 Months)
API_KEY = "INSERT_YOUR_API_KEY"  # Replace with your Alpha Vantage API key
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

# Step 2: Obtain Inflation Announcement Dates and CPI Values
# BLS API Key (optional, unregistered requests allowed for limited data)
BLS_API_KEY = "YOUR_BLS_API_KEY_HERE"  # Optional: Register at https://data.bls.gov/registrationEngine/
series_id = "CUUR0000SA0"  # CPI-U, All Items, Not Seasonally Adjusted
url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
payload = {
    "seriesid": [series_id],
    "startyear": str(start_date.year),
    "endyear": str(end_date.year),
    "registrationkey": BLS_API_KEY if BLS_API_KEY else None
}
headers = {"Content-Type": "application/json"}
response = requests.post(url, json=payload, headers=headers)
cpi_data = response.json()

# Parse CPI data with error handling
cpi_values = []
if 'Results' in cpi_data and 'series' in cpi_data['Results']:
    for series in cpi_data["Results"]["series"]:
        for item in series["data"]:
            if item["periodName"] != "Annual":  # Exclude annual averages
                date = pd.to_datetime(f"{item['year']}-{item['period'][1:]}-01")
                value = float(item["value"])
                cpi_values.append({"date": date, "cpi": value})
else:
    print("Warning: Unable to fetch CPI data from BLS API. Using mock data for demonstration.")
    # Create mock CPI data for demonstration
    mock_dates = pd.date_range(start=start_date, end=end_date, freq='M')
    cpi_values = [
        {"date": date, "cpi": 300 + i * 0.2}  # Mock CPI values with slight increase
        for i, date in enumerate(mock_dates)
    ]

cpi_df = pd.DataFrame(cpi_values)
cpi_df = cpi_df.sort_values("date").drop_duplicates("date", keep="last")

# Manually align CPI announcement dates (approximate release dates for monthly data)
cpi_announcement_dates = [
    "2024-03-12", "2024-04-10", "2024-05-15", "2024-06-12",
    "2024-07-11", "2024-08-14", "2024-09-11", "2024-10-10",
    "2024-11-13", "2024-12-11", "2025-01-15", "2025-02-12"
]
cpi_df["announcement_date"] = pd.to_datetime(cpi_announcement_dates[:len(cpi_df)])  # Match to available data

# Step 3: Preprocess Data
def get_window_data(df, date, days_before=3, days_after=3):
    start = date - timedelta(days=days_before)
    end = date + timedelta(days=days_after)
    return df[(df.index >= start) & (df.index <= end)].copy()

window_data = {}
for date in cpi_df["announcement_date"]:
    window_data[date] = get_window_data(gold_df, date)

# Step 4: Analyze Gold Price Reactions with CPI Values
analysis_results = []
for i, row in cpi_df.iterrows():
    date = row["announcement_date"]
    cpi_value = row["cpi"]
    window = window_data.get(date)
    if window is not None and not window.empty:
        price_change = window["price"].iloc[-1] - window["price"].iloc[0]
        volatility = window["price"].max() - window["price"].min()
        pct_change = (price_change / window["price"].iloc[0]) * 100
        analysis_results.append({
            "date": date,
            "cpi": cpi_value,
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
plt.savefig("gold_price_visualization.png")
plt.show()

# Additional Visualization: Gold Price vs CPI
plt.figure(figsize=(12, 6))
plt.plot(analysis_df["date"], analysis_df["pct_change"], label="Gold % Change", marker="o")
plt.plot(analysis_df["date"], analysis_df["cpi"], label="CPI Value", marker="x")
plt.title("Gold Price % Change vs CPI Values")
plt.xlabel("Date")
plt.ylabel("Value")
plt.legend()
plt.tight_layout()
plt.savefig("gold_vs_cpi_visualization.png")
plt.show()

# Step 6: Summarize Findings
avg_price_change = analysis_df["price_change"].mean()
avg_volatility = analysis_df["volatility"].mean()
avg_pct_change = analysis_df["pct_change"].mean()
correlation = analysis_df["cpi"].corr(analysis_df["pct_change"])  # Correlation between CPI and gold price change

trend = f"Gold prices have a {correlation:.2f} correlation with CPI values. "
if correlation > 0.3:
    trend += "Higher CPI tends to increase gold prices."
elif correlation < -0.3:
    trend += "Higher CPI tends to decrease gold prices."
else:
    trend += "No strong relationship between CPI values and gold price movements."

# Step 7: Generate Trade Ideas
if correlation > 0.3 and avg_pct_change > 1:
    trade_idea = "Buy gold (GLD) before CPI announcements when high CPI is expected, sell after if prices rise."
elif correlation < -0.3 and avg_pct_change < -1:
    trade_idea = "Sell gold (GLD) before CPI announcements when high CPI is expected, buy back after if prices fall."
else:
    trade_idea = "No clear trading strategy based on CPI values and gold price movements."

# Step 8: Document Results
report = f"""
### Gold Price Reaction to CPI Announcements (Last 12 Months)
- **Period**: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
- **Average Price Change**: {avg_price_change:.2f}
- **Average Volatility**: {avg_volatility:.2f}
- **Average Percentage Change**: {avg_pct_change:.2f}%
- **CPI vs Gold Price Correlation**: {correlation:.2f}
- **Trend**: {trend}
- **Trade Idea**: {trade_idea}

### Insights
This analysis examines gold price (GLD) reactions to CPI announcements, incorporating actual CPI values. Visualizations show price movements and CPI correlations, offering insights into inflation-driven trends.
"""
print(report)
with open("gold_cpi_analysis_report.txt", "w") as f:
    f.write(report)

# Display sample outputs
print("Gold Price Data (First 5 Rows):")
print(gold_df.head())
print("\nCPI Data with Announcement Dates:")
print(cpi_df)
print("\nAnalysis Results:")
print(analysis_df)
