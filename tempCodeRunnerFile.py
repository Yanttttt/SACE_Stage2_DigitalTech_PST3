quarter_to_month = {'Q1': '03', 'Q2': '06', 'Q3': '09', 'Q4': '12'}
# dfPop['Time'] = pd.to_datetime(
#     dfPop['Time'].str.extract(r'(\d{4})-(Q[1-4])').apply(
#         lambda x: f"{x[0]}-{quarter_to_month[x[1]]}", axis=1
#     ),
#     format='%Y-%m'
# )