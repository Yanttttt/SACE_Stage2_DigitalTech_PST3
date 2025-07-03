import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np

from dwellingApproval import dfApproved # Time, Number

dfApproved['Quarter'] = dfApproved['Time'].dt.to_period('Q')  # 转为季度
dfApproved['QuarterEnd'] = dfApproved['Quarter'].dt.to_timestamp(how='end')  # 得到季度最后一天

dfApproved['QuarterMonth'] = dfApproved['QuarterEnd'].dt.to_period('M').dt.to_timestamp()

dfApproved = dfApproved.groupby('QuarterMonth')['Number'].sum().reset_index()
dfApproved.columns = ['Time', 'Number']

filePath = "Households; Housing finance; Total dwellings; By property purpose; New loan commitments; Values.xlsx"
sheetNameMedian = "Data1"
df = pd.read_excel(filePath, sheet_name=sheetNameMedian, skiprows=range(1,10), header=0)

timeCol = df.columns[0]
numCol = df.columns[5]

dfLoan = df[[timeCol, numCol]].dropna()
dfLoan.columns = ['Time', 'LoanNumber']
dfLoan['Time'] = pd.to_datetime(dfLoan['Time'], format='%Y-%m')
dfApproved['Time'] = pd.to_datetime(dfApproved['Time'], format='%Y-%m')

dfCombined = pd.merge(dfLoan, dfApproved, on='Time', how='inner')

print(dfCombined)

plt.figure(figsize=(12, 6))
plt.plot(dfCombined['Time'], dfCombined['LoanNumber'], label='Loan Number', color='blue')
plt.plot(dfCombined['Time'], dfCombined['Number'], label='Dwelling Approval Number', color='orange')
plt.xlabel('Time')
plt.ylabel('Value')
plt.title('Loan Number vs Dwelling Approvals Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("loan_vs_dwelling_approvals.png", dpi=300, bbox_inches='tight')

dfApproved['Time'] = dfApproved['Time'] + pd.DateOffset(months=12)

# ---- Step 4: 合并并计算差值 ----
dfCombined = pd.merge(dfLoan, dfApproved, on='Time', how='inner')
dfCombined['Diff'] = dfCombined['Number'] - dfCombined['LoanNumber']

print(dfCombined[['Time', 'LoanNumber', 'Number', 'Diff']].tail())

# ---- Step 5: 绘图 ----
plt.figure(figsize=(12, 6))
positive = dfCombined[dfCombined['Diff'] >= 0]
negative = dfCombined[dfCombined['Diff'] < 0]

plt.bar(positive['Time'], positive['Diff'], width=20, color='green', label='Loan > Approval')
plt.bar(negative['Time'], negative['Diff'], width=20, color='red', label='Loan < Approval')

plt.xlabel('Time')
plt.ylabel('Lagged Approval - Loan')
plt.title('Difference between Lagged Dwelling Approvals (1 Year) and Loan Numbers')
plt.grid(True, axis='y')
plt.tight_layout()
plt.xticks(rotation=45)
plt.savefig("loan_minus_lagged_approval.png", dpi=300, bbox_inches='tight')

dfCombined['CumulativeDiff'] = dfCombined['Diff'].cumsum()

# 绘制累积差值折线图
plt.figure(figsize=(12, 6))
plt.plot(dfCombined['Time'], dfCombined['CumulativeDiff'], color='purple', label='Cumulative Difference')
plt.xlabel('Time')
plt.ylabel('Cumulative Approval - Loan')
plt.title('Cumulative Difference: Lagged Approvals - Loan Numbers')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.xticks(rotation=45)
plt.savefig("cumulative_diff_line.png", dpi=300, bbox_inches='tight')