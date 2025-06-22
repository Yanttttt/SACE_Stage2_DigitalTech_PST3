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
sns.heatmap(heatmapDataMedian.transpose(), cmap='coolwarm', linewidths=0.3, linecolor='gray')
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

#-----------------National Weighted Median Price----------------------

capitalNumCol = {}
restNumCol = {}
for city in cityListMedian:
    for i in range(1, len(df.columns)):
        if city in df.columns[i] and "Number of Established House Transfers" in df.columns[i]:
            capitalNumCol[city] = df.columns[i]
            restNumCol[city] = df.columns[i + 1]
            break

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

nationalWeightedMedian = totalWeightedPrice / totalTransferCount
dfNationalMedian = pd.DataFrame({
    timeColMedian: pd.to_datetime(df[timeColMedian]),
    'Australia': nationalWeightedMedian
})
dfNationalMedian[timeColMedian] = dfNationalMedian[timeColMedian].dt.strftime('%Y-%m')

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

#----------------CPI Adjustment----------------------

filePath = "CPI All Groups, Index Numbers and Percentage Changes.xlsx"
sheetNameMedian = "Data1"
dfCPI = pd.read_excel(filePath, sheet_name=sheetNameMedian, skiprows=range(1,10), header=0)

cpiTimeCol = dfCPI.columns[0]
nationalCPICol = dfCPI.columns[9]

capitalCPICol = {}
for city in cityListMedian:
    for i in range(1, len(df.columns)):
        if city in dfCPI.columns[i] and "Index Numbers" in dfCPI.columns[i]:
            capitalCPICol[city] = dfCPI.columns[i]
            break

print("CPI Columns:", capitalCPICol);

cpiCols = [cpiTimeCol, nationalCPICol] + list(capitalCPICol.values())
dfCPISelected = dfCPI[cpiCols].copy()
dfCPISelected.columns = ['Time'] + ['CPI_Australia']+['CPI_' + col for col in list(capitalCPICol.keys())]
dfCPISelected['Time'] = pd.to_datetime(dfCPISelected['Time']).dt.strftime('%Y-%m')

dfNationalReal = pd.merge(dfNationalMedian, dfCPISelected, left_on=timeColMedian, right_on='Time', how='left')
dfNationalReal['RealPrice'] = dfNationalReal['Australia'] / dfNationalReal['CPI_Australia'] * dfCPISelected['CPI_Australia'].iloc[-1] # National CPI Mar 2025

print(dfCPISelected['CPI_Australia'].iloc[-1])

plt.figure(figsize=(14, 6))
plt.plot(dfNationalReal[timeColMedian], dfNationalReal['RealPrice'], color='darkgreen')
plt.title('Real (CPI-adjusted) National Weighted Median House Price')
plt.xlabel('Time')
plt.ylabel('Price ($\'000, real)')
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.savefig('national_real_median_price_plot.png', dpi=300, bbox_inches='tight')

dfCityReal = pd.merge(dfSelectedMedian, dfCPISelected, left_on=timeColMedian, right_on='Time', how='left')

print(dfCPISelected.columns)
print(dfCityReal.columns)

for city in cityListMedian:
    cpi_col = 'CPI_' + city
    dfCityReal[city + '_Real'] = dfCityReal[city] / dfCityReal[cpi_col] * dfCPISelected[cpi_col].iloc[-1]

dfRealCityOnly = dfCityReal[[timeColMedian] + [c + '_Real' for c in cityListMedian]]
dfRealMelted = dfRealCityOnly.melt(id_vars=[timeColMedian], var_name='City', value_name='RealPrice')
dfRealMelted['City'] = dfRealMelted['City'].str.replace('_Real', '')

cityListMedianSort = ['Sydney', 'Canberra', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin']
heatmapDataReal = dfRealMelted.pivot(index=timeColMedian, columns='City', values='RealPrice')
heatmapDataReal = heatmapDataReal[cityListMedianSort]

plt.figure(figsize=(14, 8))
sns.heatmap(heatmapDataReal.transpose(), cmap='coolwarm', linewidths=0.3, linecolor='gray')
plt.title('Real (CPI-adjusted) Median House Prices in Capital Cities')
plt.xlabel('Quarter')
plt.ylabel('City')
plt.tight_layout()
plt.savefig('real_median_house_prices_heatmap.png', dpi=300, bbox_inches='tight')

plt.figure(figsize=(14, 6))
for city in cityListMedianSort:
    plt.plot(dfRealCityOnly[timeColMedian], dfRealCityOnly[city + '_Real'], label=city)

plt.title('Real (CPI-adjusted) Median House Prices Comparison Across Capital Cities')
plt.xlabel('Time')
plt.ylabel('Real Price ($\'000)')
plt.xticks(rotation=90)
plt.grid(True)
plt.legend(title="City", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('real_median_house_prices_plot.png', dpi=300, bbox_inches='tight')

#--------------------campare with household income-------------------
filePath="Equivalised disposable household income at top of selected percentiles, 1994–95 to 2019–20(a).xlsx"
sheetNameIncome = "Sheet1"

dfIncome = pd.read_excel(filePath, sheet_name=sheetNameIncome, skiprows=0, header=1)
dfIncome.columns = ['Time', 'Percentile 90', 'Percentile 80', 'Median', 'Percentile 20', 'Percentile 10']

print(dfIncome)


