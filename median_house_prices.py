import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

filePath = "Median price and number of transfers (capital city and rest of state).xlsx"
sheetNameMedian = "Data1"
df = pd.read_excel(filePath, sheet_name=sheetNameMedian, skiprows=range(1,10), header=0)

timeColMedian = df.columns[0]
cityListMedian = ['Sydney', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin', 'Canberra']
capitalCol = {}
restCol = {}
for city in cityListMedian:
    for i in range(1, len(df.columns)):
        if city in df.columns[i] and "Median Price of Established House Transfers (Unstratified)" in df.columns[i]:
            capitalCol[city] = df.columns[i]
            restCol[city] = df.columns[i + 1]
            break

dfSelectedMedian = df[[timeColMedian] + list(capitalCol.values())]
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


capitalNumCol = {}
restNumCol = {}
for city in cityListMedian:
    for i in range(1, len(df.columns)):
        if city in df.columns[i] and "Number of Established House Transfers" in df.columns[i]:
            capitalNumCol[city] = df.columns[i]
            restNumCol[city] = df.columns[i + 1]
            break

# 计算全国加权平均中位价格
totalWeightedPrice = 0
totalTransferCount = 0

for city in cityListMedian:
    capPriceCol = capitalCol[city]
    restPriceCol = restCol[city]
    capNum = capitalNumCol[city]
    restNum = restNumCol[city]

    weightedPrice = df[capPriceCol] * df[capNum] + df[restPriceCol] * df[restNum]
    totalTransfers = df[capNum] + df[restNum]

    totalWeightedPrice += weightedPrice
    totalTransferCount += totalTransfers

# 全国中位价格 = 总价格加权和 / 总交易数
nationalWeightedMedian = totalWeightedPrice / totalTransferCount

# 构建时间列和数据
dfNationalMedian = pd.DataFrame({
    timeColMedian: pd.to_datetime(df[timeColMedian]),
    'Australia': nationalWeightedMedian
})
dfNationalMedian[timeColMedian] = dfNationalMedian[timeColMedian].dt.strftime('%Y-%m')

# 绘制全国中位价格变化折线图
plt.figure(figsize=(14, 6))
plt.plot(dfNationalMedian[timeColMedian], dfNationalMedian['Australia'], color='darkblue')

plt.title('National Weighted Median House Price')
plt.xlabel('Time')
plt.ylabel('Price ($\'000)')
plt.xticks(rotation=90)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('national_median_price_plot.png', dpi=300, bbox_inches='tight')