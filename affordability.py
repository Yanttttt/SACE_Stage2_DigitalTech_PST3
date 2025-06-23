import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#--------------------household income-------------------
filePath="Equivalised disposable household income at top of selected percentiles, 1994–95 to 2019–20(a).xlsx"
sheetName = "Sheet1"

dfIncome = pd.read_excel(filePath, sheet_name=sheetName, skiprows=0, header=1)
dfIncome.columns = ['Time', 'Percentile 10', 'Percentile 20', 'Median', 'Percentile 80', 'Percentile 90']
dfIncome['Time'] = pd.to_datetime(dfIncome['Time'].astype(str).str[:4] + '-06', format='%Y-%m')

#--------------------House cost-------------------
filePath="Housing occupancy and costs, Australia, 1994–95 to 2019–20 Edited.xlsx"
sheetName = "Sheet 1"

dfCost = pd.read_excel(filePath, header=None, skiprows=4, nrows=2)
dfCost=dfCost.T

dfCost.columns = ['Time', 'Cost']
dfCost['Time'] = pd.to_datetime(dfCost['Time'].astype(str).str[:4] + '-06', format='%Y-%m')

dfMerged = pd.merge(dfIncome, dfCost, on='Time', how='inner')
print(dfMerged)

ratio_data = {
    'Time': dfMerged['Time']
}

income_columns = ['Percentile 10', 'Percentile 20', 'Median', 'Percentile 80', 'Percentile 90']
for col in income_columns:
    ratio_data[col] = dfMerged['Cost'] / dfMerged[col] * 100 

dfRatio = pd.DataFrame(ratio_data)

colors = {
    'Percentile 90': '#a6cee3',
    'Percentile 80': '#1f78b4',
    'Median': '#33a02c',
    'Percentile 20': "#eff159",
    'Percentile 10': "#cb6e04"
}

plt.figure(figsize=(10, 6))

for col in ['Percentile 90', 'Percentile 80', 'Median', 'Percentile 20', 'Percentile 10']:
    plt.plot(dfRatio['Time'], dfRatio[col], label=col, color=colors[col], linewidth=2)

plt.axhline(y=30, color='red', linestyle='--', linewidth=1)
plt.text(dfRatio['Time'].iloc[1], 31.2, '30% Threshold', color='red')

plt.title('Mean Housing Cost as Percentage of Income by Percentile')
plt.xlabel('Time')
plt.ylabel('Cost as % of Income')
plt.legend(title="Income Percentile", loc='upper left')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

plt.savefig('housing_cost_ratio_by_percentile.png', dpi=300, bbox_inches='tight')
plt.show()
