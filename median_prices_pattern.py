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

#print("CPI Columns:", capitalCPICol);

cpiCols = [cpiTimeCol, nationalCPICol] + list(capitalCPICol.values())
dfCPISelected = dfCPI[cpiCols].copy()
dfCPISelected.columns = ['Time'] + ['CPI_Australia']+['CPI_' + col for col in list(capitalCPICol.keys())]
dfCPISelected['Time'] = pd.to_datetime(dfCPISelected['Time']).dt.strftime('%Y-%m')

dfNationalReal = pd.merge(dfNationalMedian, dfCPISelected, left_on=timeColMedian, right_on='Time', how='left')
dfNationalReal['RealPrice'] = dfNationalReal['Australia'] / dfNationalReal['CPI_Australia'] * dfCPISelected['CPI_Australia'].iloc[-1] # National CPI Mar 2025

print(dfCPISelected['CPI_Australia'].iloc[-1])

dfCityReal = pd.merge(dfSelectedMedian, dfCPISelected, left_on=timeColMedian, right_on='Time', how='left')

#print(dfCPISelected.columns)
#print(dfCityReal.columns)

for city in cityListMedian:
    cpi_col = 'CPI_' + city
    dfCityReal[city + '_Real'] = dfCityReal[city] / dfCityReal[cpi_col] * dfCPISelected[cpi_col].iloc[-1]

dfRealCityOnly = dfCityReal[[timeColMedian] + [c + '_Real' for c in cityListMedian]]
dfRealMelted = dfRealCityOnly.melt(id_vars=[timeColMedian], var_name='City', value_name='RealPrice')
dfRealMelted['City'] = dfRealMelted['City'].str.replace('_Real', '')

cityListMedianSort = ['Sydney', 'Canberra', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin']
heatmapDataReal = dfRealMelted.pivot(index=timeColMedian, columns='City', values='RealPrice')
heatmapDataReal = heatmapDataReal[cityListMedianSort]

dfNationalReal['Time'] = pd.to_datetime(dfNationalReal['Time'])

dfNationalReal = dfNationalReal.sort_values('Time')
dfNationalReal['YoY_Growth_Pct'] = dfNationalReal['RealPrice'].pct_change(periods=4) * 100  # four quarter is 1 year

plt.figure(figsize=(14, 6))
plt.plot(dfNationalReal['Time'], dfNationalReal['YoY_Growth_Pct'], color='darkgreen', linewidth=2)
plt.axhline(0, color='gray', linestyle='--', linewidth=1)
plt.title('National Real House Price YoY Growth (%)')
plt.xlabel('Time')
plt.ylabel('Year-over-Year Growth (%)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('national_yoy_growth_pct.png', dpi=300)

# 转换时间格式
dfCityGrowth = dfRealCityOnly.copy()
dfCityGrowth[timeColMedian] = pd.to_datetime(dfCityGrowth[timeColMedian])
dfCityGrowth = dfCityGrowth.sort_values(timeColMedian)

for city in cityListMedian:
    dfCityGrowth[city + '_YoY_Growth'] = dfCityGrowth[city + '_Real'].pct_change(periods=4) * 100

plt.figure(figsize=(14, 6))
for city in cityListMedianSort:
    plt.plot(dfCityGrowth[timeColMedian], dfCityGrowth[city + '_YoY_Growth'], label=city)

plt.axhline(0, color='gray', linestyle='--', linewidth=1)
plt.title('Year-over-Year Real House Price Growth (%) - Capital Cities')
plt.xlabel('Time')
plt.ylabel('YoY Growth (%)')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend(title="City", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('capital_cities_yoy_growth_pct.png', dpi=300)

city_yoy_growth_cols = [c + '_YoY_Growth' for c in cityListMedian]
dfHeatmap = dfCityGrowth[[timeColMedian] + city_yoy_growth_cols].copy()
dfHeatmap.set_index(timeColMedian, inplace=True)

dfHeatmap.columns = [col.replace('_YoY_Growth', '') for col in dfHeatmap.columns]

dfHeatmap = dfHeatmap[cityListMedianSort]

plt.figure(figsize=(14, 8))
sns.heatmap(
    dfHeatmap.T,  # 转置使城市为 y 轴，时间为 x 轴
    cmap='coolwarm',  # 蓝到红配色
    center=0,         # 使 0 为中性色（白）
    annot=False,      # 如需显示数字可设为 True
    fmt=".1f",        # 数字格式
    cbar_kws={'label': 'YoY Growth (%)'}
)

plt.title('YoY Real House Price Growth - Capital Cities Heatmap')
plt.xlabel('Time')
plt.ylabel('City')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('capital_cities_yoy_growth_heatmap.png', dpi=300)

#---------------- Population----------------

filePath="Australia Population 2002-2023.xlsx"
sheetName = "Table"

dfPop=pd.read_excel(filePath, sheet_name=sheetName, header=None).T
dfPop = dfPop[1:].reset_index(drop=True)

timeCol = dfPop.columns[0]
naturalIncreaseCol = dfPop.columns[3]
migrationCol = dfPop.columns[10]
populationCol = dfPop.columns[11]

dfPop=dfPop[[timeCol, naturalIncreaseCol, migrationCol, populationCol]]
dfPop.columns = ['Time', 'Natural Increase', 'Migration', 'Population']

quarter_to_month = {'Q1': '03', 'Q2': '06', 'Q3': '09', 'Q4': '12'}
dfPop['Time'] = pd.to_datetime(
    dfPop['Time'].str.extract(r'(\d{4})-(Q[1-4])').apply(
        lambda x: f"{x[0]}-{quarter_to_month[x[1]]}", axis=1
    ),
    format='%Y-%m'
)

for col in ['Natural Increase', 'Migration', 'Population']:
    dfPop[col] = pd.to_numeric(dfPop[col], errors='coerce')

dfNationalReal = dfNationalReal.sort_values('Time')
dfNationalReal['RealPrice_QoQ_Change'] = dfNationalReal['RealPrice'].diff() 

dfPop = dfPop.sort_values('Time')
dfPop['Population_QoQ_Change'] = dfPop['Population'].diff()

dfCombined = pd.merge(dfNationalReal[['Time', 'RealPrice_QoQ_Change']], dfPop, on='Time', how='inner')

fig, ax1 = plt.subplots(figsize=(14, 6))

ax1.plot(dfCombined['Time'], dfCombined['RealPrice_QoQ_Change'], color='firebrick', label='Quarterly House Price Change ($)', linewidth=2)
ax1.set_ylabel('Real House Price Change ($)', color='firebrick')
ax1.tick_params(axis='y', labelcolor='firebrick')

ax2 = ax1.twinx()
ax2.plot(dfCombined['Time'], dfCombined['Population_QoQ_Change'], color='steelblue', label='Quarterly Population Change', linewidth=2)
ax2.set_ylabel('Population Change', color='steelblue')
ax2.tick_params(axis='y', labelcolor='steelblue')

plt.title('Quarterly Real House Price vs Population Change')
ax1.set_xlabel('Time')
plt.xticks(rotation=45)
plt.grid(True)
fig.tight_layout()
plt.savefig('price_vs_population_change.png', dpi=300)

#---------------- Scatter --------------

dfLagged = dfCombined.copy()

dfLagged['Population_Lagged'] = dfLagged['Population_QoQ_Change'].shift(-4)

# 去除有缺失值的行
dfLagged = dfLagged.dropna(subset=['Population_Lagged', 'RealPrice_QoQ_Change'])

# 绘制散点图
plt.figure(figsize=(10, 6))
sns.regplot(
    data=dfLagged,
    x='Population_Lagged',
    y='RealPrice_QoQ_Change',
    scatter_kws={'alpha': 0.7},
    line_kws={'color': 'red'}
)
plt.title('Lagged Population Change (6 Quarters) vs Real House Price Change')
plt.xlabel('Population Change (6 Quarters Ago)')
plt.ylabel('Real House Price Change ($)')
plt.grid(True)
plt.tight_layout()
plt.savefig('scatter_lagged_population_vs_price.png', dpi=300)

