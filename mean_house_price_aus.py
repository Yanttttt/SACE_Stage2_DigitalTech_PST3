import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

filePath = "Total value of dwellings, all series.xlsx"
sheetNameMedian = "Data1"
dfMedianPriceTransfers = pd.read_excel(filePath, sheet_name=sheetNameMedian, skiprows=range(1,10), header=0)

timeCol = dfMedianPriceTransfers.columns[0]
priceCol = dfMedianPriceTransfers.columns[36]

dfSelectedMedian = dfMedianPriceTransfers[[timeCol] + [priceCol]]
dfSelectedMedian.columns = [timeCol, 'Mean price of residential dwellings ;  Australia']
dfSelectedMedian[timeCol] = pd.to_datetime(dfSelectedMedian[timeCol])
dfSelectedMedian[timeCol] = dfSelectedMedian[timeCol].dt.strftime('%Y-%m')

plt.figure(figsize=(12, 6))
plt.plot(dfSelectedMedian[timeCol], dfSelectedMedian['Mean price of residential dwellings ;  Australia'], color='blue', linewidth=2)

plt.title('Mean Price of Residential Dwellings in Australia', fontsize=14)
plt.xlabel('Time', fontsize=12)
plt.ylabel('Price ($)', fontsize=12)
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()

plt.savefig('mean_house_price_plot.png', dpi=300, bbox_inches='tight')