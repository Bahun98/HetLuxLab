import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# *** Before loading the data: *** 
# 1. remove prior columns from the excell file that are related to the algorithm
# 2. remove all words 'blauw' from color temp columns or from Ellen's spreadsheet

file_path = 'real_data.xlsx'
df = pd.read_excel(file_path, sheet_name='Main_data') # for testing add ,nrows=151

# transfrom lumen into lumen per square meter
df['LUMEN_SQM'] = df['LUMEN_LAMP'] / (((df['LPH_ARMATUUR'] / 100) **2) * 16)

# Missing/zero value handling:
cols = ['CK_IN_KELVIN', 'LUMEN_LAMP', 'LPH_ARMATUUR']

for i in cols:
    missing_or_zero = df[i].isna() | (df[i] == 0)
    print(f'Missing or zero values for {i} are: {missing_or_zero.sum()}')

# Create extra column that flags whether any of these 3 columns contain missing/zero values 
df['missing_zero_flag'] = ((df[cols].isna()) | (df[cols] == 0)).any(axis=1).astype(int)

# ALGORITHM CALCULATIONS: COLOR TEMPERATURE (note - code below could be made more efficient with loop)
ct_headers = [
    (df['CK_IN_KELVIN'] < 2000),
    (df['CK_IN_KELVIN'] >= 2000) & (df['CK_IN_KELVIN'] < 2700),
    (df['CK_IN_KELVIN'] >= 2700) & (df['CK_IN_KELVIN'] < 3000),
    (df['CK_IN_KELVIN'] >= 3000) & (df['CK_IN_KELVIN'] < 4000),
    (df['CK_IN_KELVIN'] >= 4000),
]

ct_nature_weights = [(5+5)/2, (4+4)/2, (3+3)/2, (2+2)/1, (1+1)/2]
ct_efficiency_weights = [2,3,3,4,5]
ct_humans_weights = [(5+4+4)/3, (4+4+5)/3, (3+4+5)/3, (2+5+3)/3, (1+5+1)/3]

df['ct_nature'] = np.select(ct_headers, ct_nature_weights, default=np.nan)
df['ct_efficiency'] = np.select(ct_headers, ct_efficiency_weights, default=np.nan)
df['ct_humans'] = np.select(ct_headers, ct_humans_weights, default=np.nan)
# note: treat as missing value if header category is invalid

# ALGORITHM CALCULATIONS: POLE HEIGHT

ph_headers = [
    (df['LPH_ARMATUUR'] < 1),
    (df['LPH_ARMATUUR'] >= 1) & (df['LPH_ARMATUUR'] < 2),
    (df['LPH_ARMATUUR'] >= 2) & (df['LPH_ARMATUUR'] < 4.2),
    (df['LPH_ARMATUUR'] >= 4.2) & (df['LPH_ARMATUUR'] <6),
    (df['LPH_ARMATUUR'] >= 6) & (df['LPH_ARMATUUR'] < 10),
    (df['LPH_ARMATUUR'] >= 10),
]

ph_nature_weights = [(5+5)/2, (4+4)/2, (3+3)/2, (2+2)/1, (1+1)/2, (1+1)/2]
ph_efficiency_weights = [1, 2, 3, 3, 4, 5]
ph_humans_weights = [(5+1+3)/3, (5+1+3)/3, (2+0+5)/3, (3+0+3)/3, (4+0+3)/3, (5+0+3)/3]

# ALGORITHM CALCULATIONS: LUMEN PER SQM

lm_headers = [
    (df['LUMEN_SQM'] < 1),
    (df['LUMEN_SQM'] >= 1) & (df['LUMEN_SQM'] < 5),
    (df['LUMEN_SQM'] >= 5) & (df['LUMEN_SQM'] < 10),
    (df['LUMEN_SQM'] >= 10) & (df['LUMEN_SQM'] < 20),
    (df['LUMEN_SQM'] >= 20) & (df['LUMEN_SQM'] < 50),
    (df['LUMEN_SQM'] >= 50),
]

lm_nature_weights = [(5+5)/2, (4+4)/2, (3+3)/2, (2+2)/1, (1+1)/2, (1+1)/2]
lm_efficiency_weights = [0, 0, 0, 0, 0 ,0]
lm_humans_weights = [0, 0, 0, 0, 0 ,0]

df['lm_nature'] = np.select(lm_headers, lm_nature_weights, default=np.nan)
df['lm_efficiency'] = np.select(lm_headers, lm_efficiency_weights, default=np.nan)
df['lm_humans'] = np.select(lm_headers, lm_humans_weights, default=np.nan)


df['ph_nature'] = np.select(ph_headers, ph_nature_weights, default=np.nan)
df['ph_efficiency'] = np.select(ph_headers, ph_efficiency_weights, default=np.nan)
df['ph_humans'] = np.select(ph_headers, ph_humans_weights, default=np.nan)

# CALCULATING THE COMPOSITE SCORES (using mean)
df['nature_composite'] = df[['ct_nature', 'ph_nature', 'lm_nature']].mean(axis=1)
df['efficiency_composite'] = df[['ct_efficiency', 'ph_efficiency', 'lm_efficiency']].mean(axis=1)
df['humans_composite'] = df[['ct_humans', 'ph_humans', 'lm_humans']].mean(axis=1) 


# split df: without missing/zero values vs with missing/zero values only
df_clean = df.dropna(subset=cols).copy()
df_missing = df[df[cols].isna().any(axis=1)].copy()

# export
df.to_excel("df.xlsx", index=False)
df_clean.to_excel("df_clean.xlsx", index=False)
df_missing.to_excel("df_missing.xlsx", index=False)
