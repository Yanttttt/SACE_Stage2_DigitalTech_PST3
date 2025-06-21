import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

filePath = "Median price and number of transfers (capital city and rest of state).xlsx"
sheetNameMedian = "Data1"
dfMedianPriceTransfers = pd.read_excel(filePath, sheet_name=sheetNameMedian, skiprows=range(1,10), header=0)
print("行数:", len(dfMedianPriceTransfers))

timeColMedian = dfMedianPriceTransfers.columns[0]
cityListMedian = ['Sydney', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin', 'Canberra']
cityColsMedian = {}
for city in cityListMedian:
    for col in dfMedianPriceTransfers.columns[1:]:
        if city in col and "Median Price of Established House Transfers (Unstratified)" in col:
            cityColsMedian[city] = col
            break

dfSelectedMedian = dfMedianPriceTransfers[[timeColMedian] + list(cityColsMedian.values())]
dfSelectedMedian.columns = [timeColMedian] + cityListMedian
dfSelectedMedian[timeColMedian] = pd.to_datetime(dfSelectedMedian[timeColMedian])
dfSelectedMedian[timeColMedian] = dfSelectedMedian[timeColMedian].dt.strftime('%Y-%m')

dfMeltedMedian = dfSelectedMedian.melt(id_vars=[timeColMedian], var_name='City', value_name='Price')

heatmapDataMedian = dfMeltedMedian.pivot(index=timeColMedian, columns='City', values='Price')
cityListMedianSort = ['Sydney', 'Canberra', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin']
heatmapDataMedian = heatmapDataMedian[cityListMedianSort]

# Median Price Heatmap
plt.figure(figsize=(14, 8))
sns.heatmap(heatmapDataMedian.transpose(), cmap='YlOrRd', linewidths=0.3, linecolor='gray')
plt.title('Median House Prices in Australian Capital Cities')
plt.xlabel('Quarter')
plt.ylabel('City')
plt.tight_layout()
#plt.show()
plt.savefig('median_house_prices_heatmap.png', dpi=300, bbox_inches='tight')

# Median Price Plot
plt.figure(figsize=(14, 6))
for city in cityListMedianSort:
    plt.plot(dfSelectedMedian[timeColMedian], dfSelectedMedian[city], label=city)

plt.title('Median House Prices Comparison Across Capital Cities')
plt.xlabel('Time')
plt.ylabel('Price ($\'000)')
plt.xticks(rotation=90)
plt.grid(True)
plt.legend(title="City", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
#plt.show()
plt.savefig('median_house_prices_plot.png', dpi=300, bbox_inches='tight')
