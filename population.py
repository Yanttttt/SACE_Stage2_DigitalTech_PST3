import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress

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
plt.plot(dfPop['Time'], dfPop['Migration'], label='Net Oversea Migration', color='orange', linewidth=2)
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

# 提取数据
dfModel = dfPop[['Natural Increase', 'Migration', 'Population_QoQ_Change']].dropna()

# 手动标准化
X1 = dfModel['Natural Increase']
X2 = dfModel['Migration']
y = dfModel['Population_QoQ_Change']

X1_std = (X1 - X1.mean()) / X1.std()
X2_std = (X2 - X2.mean()) / X2.std()

# 构建标准化后的 X 矩阵（加上截距项）
X = np.column_stack([X1_std, X2_std, np.ones(len(X1_std))])

# 最小二乘回归（beta = (XᵀX)^-1 Xᵀy）
beta = np.linalg.inv(X.T @ X) @ X.T @ y

print(f"标准化回归系数（贡献）:")
print(f"自然增长: {beta[0]:.3f}")
print(f"移民:     {beta[1]:.3f}")

# 标准化回归系数（贡献）:
# 自然增长: 5.057
# 移民:     35.140

dfScatter = dfPop.dropna(subset=['Natural Increase', 'Migration', 'Population_QoQ_Change'])

slope_nat, intercept_nat, r_value_nat, _, _ = linregress(
    dfScatter['Natural Increase'], dfScatter['Population_QoQ_Change'])

slope_mig, intercept_mig, r_value_mig, _, _ = linregress(
    dfScatter['Migration'], dfScatter['Population_QoQ_Change'])

plt.figure(figsize=(6, 5))
plt.scatter(dfScatter['Natural Increase'], dfScatter['Population_QoQ_Change'], alpha=0.6, color='green', label='Data')
x = np.linspace(dfScatter['Natural Increase'].min(), dfScatter['Natural Increase'].max(), 100)
plt.plot(x, slope_nat * x + intercept_nat, color='black', label=f'Fit: y={slope_nat:.2f}x + {intercept_nat:.2f}')
plt.title(f'Population Change vs Natural Increase\n$R^2$ = {r_value_nat**2:.3f}')
plt.xlabel('Natural Increase')
plt.ylabel('Population QoQ Change')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('scatter_natural_vs_total.png', dpi=300)

plt.figure(figsize=(6, 5))
plt.scatter(dfScatter['Migration'], dfScatter['Population_QoQ_Change'], alpha=0.6, color='orange', label='Data')
x = np.linspace(dfScatter['Migration'].min(), dfScatter['Migration'].max(), 100)
plt.plot(x, slope_mig * x + intercept_mig, color='black', label=f'Fit: y={slope_mig:.2f}x + {intercept_mig:.2f}')
plt.title(f'Population Change vs Migration\n$R^2$ = {r_value_mig**2:.3f}')
plt.xlabel('Migration')
plt.ylabel('Population QoQ Change')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('scatter_migration_vs_total.png', dpi=300)

from median_house_prices import dfNationalReal

dfNationalReal['Time'] = pd.to_datetime(dfNationalReal['Time'], format='%Y-%m')
dfPop['Time'] = pd.to_datetime(dfPop['Time'])

# 合并两个数据集
dfMergedPricePop = pd.merge(dfNationalReal[['Time', 'RealPrice']], dfPop[['Time', 'Population']], on='Time', how='inner')

# 去除缺失数据
dfMergedPricePop = dfMergedPricePop.dropna(subset=['RealPrice', 'Population'])

# 执行线性回归
slope, intercept, r_value, p_value, std_err = linregress(dfMergedPricePop['Population'], dfMergedPricePop['RealPrice'])

# 绘图
plt.figure(figsize=(8, 6))
plt.scatter(dfMergedPricePop['Population'], dfMergedPricePop['RealPrice'], alpha=0.6, color='teal', label='Data')
x = np.linspace(dfMergedPricePop['Population'].min(), dfMergedPricePop['Population'].max(), 100)
plt.plot(x, slope * x + intercept, color='black', label=f'Fit: y = {slope:.2f}x + {intercept:.2f}')

plt.title(f'Real Median House Price vs Total Population\n$R^2$ = {r_value**2:.3f}')
plt.xlabel('Population')
plt.ylabel('Real Median House Price ($\'000)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('scatter_population_vs_real_price.png', dpi=300)






