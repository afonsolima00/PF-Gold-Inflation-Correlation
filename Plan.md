### Step-by-Step Plan to Execute the Task

1. **Gather Gold Price Data (Last 12 Months)**  
   - Use a free source
   - Extract the data into a structured format (e.g., CSV or directly into a Pandas DataFrame in Python).

2. **Obtain Inflation Announcement Dates**  
   - Refer to the CPI release schedule from sources like the Bureau of Labor Statistics or US Inflation Calculator. Collect monthly inflation announcement dates for the past 12 months.

3. **Preprocess Data**  
   - Ensure both datasets (gold prices and inflation dates) are in the same date format and time zone.
   - Filter gold price data to include only dates that are within a specified window around each inflation announcement (e.g., 3 days before and after).

4. **Analyze Gold Price Reactions**  
   - For each inflation announcement date:
     - Extract gold prices within the reaction window.
     - Calculate key metrics such as price changes, volatility (e.g., max-min difference), and percentage changes.

5. **Visualize the Data**  
   - Create a line plot for each inflation date showing gold price movements in the reaction window.
   - Use distinct colors for each inflation date to differentiate patterns.

6. **Summarize Findings**  
   - Identify trends or patterns in gold price reactions (e.g., consistent increases, decreases, or no significant movement).
   - Compute aggregate statistics, such as average price change across all announcements.

7. **Generate Trade Ideas**  
   - Based on findings, suggest potential trading strategies (e.g., buy gold before announcements if prices consistently rise).

8. **Document Results**  
   - Summarize results in a concise report with visualizations and key insights.
   - Highlight actionable insights for traders or investors.

