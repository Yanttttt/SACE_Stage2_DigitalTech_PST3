import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

from median_prices_pattern import dfNationalReal
from dwellingApproval import dfApproved
from population import dfPop

# ----------- Step 1: 收入数据 -----------
filePath = "Equivalised disposable household income at top of selected percentiles, 1994–95 to 2019–20(a).xlsx"
dfIncome = pd.read_excel(filePath, sheet_name="Sheet1", header=1)
dfIncome.columns = ['Time', 'Percentile 10', 'Percentile 20', 'Median', 'Percentile 80', 'Percentile 90']
dfIncome['Time'] = pd.to_datetime(dfIncome['Time'].astype(str).str[:4] + '-06')
dfIncome['Year'] = dfIncome['Time'].dt.year
dfIncomeYearly = dfIncome[['Year', 'Median']]

# ----------- Step 2: 房价增长与住房批准回归 -----------
dfApproved['Year'] = dfApproved['Time'].dt.year
dfApprovedYearly = dfApproved.groupby('Year')['Number'].sum().reset_index()

dfNationalReal['Year'] = dfNationalReal['Time'].dt.year
dfNationalRealYearly = dfNationalReal.groupby('Year')['RealPrice_QoQ_Change'].sum().reset_index()
dfNationalRealYearly['RealPrice'] = dfNationalReal.groupby('Year')['RealPrice'].mean().values

# 找滞后期
max_lag = 5
correlations = []
for lag in range(max_lag + 1):
    dfLag = dfApprovedYearly.copy()
    dfLag['Year'] += lag
    dfMerged = pd.merge(dfLag, dfNationalRealYearly, on='Year', how='inner')
    corr = dfMerged['Number'].corr(dfMerged['RealPrice_QoQ_Change'])
    correlations.append((lag, corr))

best_lag, best_corr = min(correlations, key=lambda x: x[1])
print(f"最强负相关滞后期：{best_lag} 年，相关系数：{best_corr:.3f}")

# 回归建模
dfLag = dfApprovedYearly.copy()
dfLag['Year'] += best_lag
dfMerged = pd.merge(dfLag, dfNationalRealYearly, on='Year', how='inner')

x = dfMerged['RealPrice_QoQ_Change']
y = dfMerged['Number']
slope, intercept, r_value, p_value, std_err = linregress(x, y)
print(f"\n线性回归: slope = {slope:.2f}, intercept = {intercept:.2f}, R² = {r_value**2:.3f}, P = {p_value:.2e}")

# 用回归反推房价变动贡献
dfMerged['Predicted_Change'] = slope * dfMerged['RealPrice_QoQ_Change'] + intercept
dfNationalRealYearly = pd.merge(dfNationalRealYearly, dfMerged[['Year', 'Predicted_Change']], on='Year', how='left')
dfNationalRealYearly['Predicted_Change'] = dfNationalRealYearly['Predicted_Change'].fillna(0)

# 累积成房价预测值
# 累积成房价预测值（确保初始值有效）
dfNationalRealYearly = dfNationalRealYearly.sort_values('Year').reset_index(drop=True)
initial_price = dfNationalRealYearly['RealPrice'].dropna().iloc[0]
dfNationalRealYearly['PredictedPrice'] = dfNationalRealYearly['Predicted_Change'].cumsum() + initial_price


# ----------- Step 3: 人口数据处理 -----------
dfPop['Year'] = dfPop['Time'].dt.year
dfPopYearly = dfPop.groupby('Year')['Population'].mean().reset_index()

# ----------- Step 4: 合并所有变量 -----------
dfFinal = dfNationalRealYearly[['Year', 'RealPrice', 'PredictedPrice']].merge(
    dfIncomeYearly, on='Year', how='inner'
).merge(
    dfPopYearly, on='Year', how='inner'
)

# ----------- Step 5: 标准化回归分析 -----------
def standardize(series):
    return (series - series.mean()) / series.std()

# 构造 X
X = pd.DataFrame({
    'Income': standardize(dfFinal['Median']),
    'Population': standardize(dfFinal['Population']),
    'HousingApproval': standardize(dfFinal['PredictedPrice'])
})

y = standardize(dfFinal['RealPrice'])

# 计算正规方程
X_np = np.column_stack([np.ones(len(X)), X.values])
y_np = y.values
beta = np.linalg.inv(X_np.T @ X_np) @ X_np.T @ y_np

# 提取标准化系数
beta_std = beta[1:]
abs_contrib = np.abs(beta_std)
contrib_ratio = abs_contrib / abs_contrib.sum()

# ----------- Step 6: 打印结果 -----------
factors = ['Income', 'Population', 'Housing Approval']
print("\n🏠 各变量对房价影响贡献（标准化线性回归）:")
for name, coef, ratio in zip(factors, beta_std, contrib_ratio):
    print(f"{name}: β = {coef:.3f}, 贡献比例 = {ratio * 100:.1f}%")

# Income: β = 0.095, 贡献比例 = 9.7%
# Population: β = 0.675, 贡献比例 = 68.7%
# Housing Approval: β = 0.213, 贡献比例 = 21.6%