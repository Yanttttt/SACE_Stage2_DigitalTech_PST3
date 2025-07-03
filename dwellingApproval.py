import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np

filePath = "Number of dwelling units approved, by sector, all series - Australia.xlsx"
sheetNameMedian = "Data1"
df = pd.read_excel(filePath, sheet_name=sheetNameMedian, skiprows=range(1,10), header=0)

timeCol = df.columns[0]
numCol = df.columns[1]

dfApproved = df[[timeCol, numCol]].dropna()
dfApproved.columns = ['Time', 'Number']
dfApproved['Time'] = pd.to_datetime(dfApproved['Time'], format='%Y-%m')

plt.figure(figsize=(12, 6))
plt.plot(dfApproved['Time'], dfApproved['Number'], label='Number of Dwelling Units Approved', color='blue', linewidth=2)
plt.title('Number of Dwelling Units Approved; Private Sector')
plt.xlabel('Year')
plt.ylabel('Number of Dwelling Units')
plt.grid(True)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("number_of_dwelling_units_approved.png", dpi=300, bbox_inches='tight')

from median_prices_pattern import dfNationalReal

dfApproved['Year'] = dfApproved['Time'].dt.year
dfApprovedYearly = dfApproved.groupby('Year')['Number'].sum().reset_index()

dfNationalReal['Year'] = dfNationalReal['Time'].dt.year
dfNationalRealYearly = dfNationalReal.groupby('Year')['RealPrice_QoQ_Change'].sum().reset_index()

dfCombined = pd.merge(dfNationalRealYearly[['Year', 'RealPrice_QoQ_Change']], dfApprovedYearly, on='Year', how='inner')

fig, ax1 = plt.subplots(figsize=(14, 6))
color = 'tab:red'
ax1.set_xlabel('Year')
ax1.set_ylabel('Real House Price Change ($)', color=color)
ax1.plot(dfCombined['Year'], dfCombined['RealPrice_QoQ_Change'], color=color, linewidth=2, label='Yearly House Price Change')
ax1.tick_params(axis='y', labelcolor=color)
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Number of Dwelling Units Approved', color=color)
ax2.plot(dfCombined['Year'], dfCombined['Number'], color=color, linewidth=2, label='Yearly Dwelling Units Approved')
ax2.tick_params(axis='y', labelcolor=color)
plt.title('Yearly Real House Price Change vs Number of Dwelling Units Approved')
fig.tight_layout()
plt.grid(True)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
plt.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
plt.savefig('price_vs_dwelling_units_approved.png', dpi=300, bbox_inches='tight')

x = dfCombined['RealPrice_QoQ_Change'].astype(float)
y = dfCombined['Number'].astype(float)
mask = x.notna() & y.notna()
x = x[mask]
y = y[mask]

# 回归分析
slope, intercept, r_value, p_value, std_err = linregress(x, y)
print(f"线性回归结果:")
print(f"斜率（slope）: {slope:.2f}")
print(f"截距（intercept）: {intercept:.2f}")
print(f"R²: {r_value**2:.3f}")
print(f"P值: {p_value:.3e}")

# 拟合图
plt.figure(figsize=(8, 6))
plt.scatter(x, y, color='steelblue', alpha=0.6, label='Data Points')
x_fit = np.linspace(x.min(), x.max(), 100)
plt.plot(x_fit, slope * x_fit + intercept, color='firebrick', label=f'Fit: y={slope:.1f}x + {intercept:.0f}')
plt.title(f'Housing Approval vs Real House Price Change\n$R^2$ = {r_value**2:.3f}')
plt.xlabel('Quarterly Real House Price Change ($)')
plt.ylabel('Number of Dwelling Units Approved')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('scatter_price_vs_dwelling_approval.png', dpi=300, bbox_inches='tight')

#-------------------- lag ------------------

from scipy.stats import linregress
max_lag = 5
correlations = []

# 计算每个滞后期的相关系数
for lag in range(max_lag + 1):
    dfLag = dfApprovedYearly.copy()
    dfLag['Year'] = dfLag['Year'] + lag  # 滞后：批准量滞后影响房价
    dfMerged = pd.merge(dfLag, dfNationalRealYearly, on='Year', how='inner')
    corr = dfMerged['Number'].corr(dfMerged['RealPrice_QoQ_Change'])
    correlations.append((lag, corr))

# 选择最强负相关
best_lag, best_corr = min(correlations, key=lambda x: x[1])
print(f"最强负相关滞后期：{best_lag} 年，相关系数：{best_corr:.3f}")

dfLag = dfApprovedYearly.copy()
dfLag['Year'] = dfLag['Year'] + best_lag
dfMerged = pd.merge(dfLag, dfNationalRealYearly, on='Year', how='inner')

# 线性回归（X: 房价变动, Y: 批准数量）
x = dfMerged['RealPrice_QoQ_Change']
y = dfMerged['Number']
slope, intercept, r_value, p_value, std_err = linregress(x, y)
line = slope * x + intercept

# 绘图
plt.figure(figsize=(10, 6))
plt.scatter(x, y, color='blue', label='Observed Data')
plt.plot(x, line, color='red', label=f'Fit: y = {slope:.2f}x + {intercept:.2f}')
plt.title(f'Lagged Effect (Lag = {best_lag} years)\n$R$ = {r_value:.3f}, $R^2$ = {r_value**2:.3f}')
plt.xlabel('Real House Price Change ($)')
plt.ylabel('Number of Dwelling Units Approved (Lagged)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(f'scatter_dwelling_vs_price_lag_{best_lag}.png', dpi=300)
plt.show()