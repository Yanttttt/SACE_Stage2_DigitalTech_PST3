import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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

dfPop['Population_QoQ_Change'] = dfPop['Population'].diff()

# print(dfPop)

plt.figure(figsize=(12, 6))

plt.plot(dfPop['Time'], dfPop['Natural Increase'], label='Natural Increase (Birth - Death)', color='green', linewidth=2)
plt.plot(dfPop['Time'], dfPop['Migration'], label='Oversea Migration', color='orange', linewidth=2)
plt.plot(dfPop['Time'], dfPop['Population_QoQ_Change'], label='Quarterly Population Change', color='blue', linewidth=2)

plt.title('Australian Population Trends')
plt.xlabel('Year')
plt.ylabel('Number of People (Thousands)')
plt.grid(True)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("population_trends.png", dpi=300, bbox_inches='tight')

plt.figure(figsize=(12, 6))
plt.plot(dfPop['Time'], dfPop['Population'], label='Population', color='blue', linewidth=2)
plt.title('Australian Population')
plt.xlabel('Year')
plt.ylabel('Number of People (Thousands)')
plt.grid(True)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("population.png", dpi=300, bbox_inches='tight')



