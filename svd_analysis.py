#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Settings
csv_filename = 'data_pgz_fixed.csv'
field = 'Temperature'
dt_min = pd.to_datetime('2020-05-11 00:00:00')
dt_max = pd.to_datetime('2020-06-10 00:00:00')
k = 3

# Read CSV file
print(f'Reading raw data from CSV: {csv_filename}')
df_raw = pd.read_csv(csv_filename)
locations = df_raw['Town'].unique()
        
print(f'Time range: {dt_min} to {dt_max}')
# Temporary extending time range for later interpolation
df = pd.DataFrame(columns=locations, index=pd.date_range(start=pd.to_datetime('2020-01-01 00:00:00'),
                                                         end=pd.to_datetime('2021-01-01 00:00:00'),
                                                         freq='30min'),
                  dtype=float)


print(f'Preprocessing {field} data')
for index, row in df_raw.iterrows():
    try:
        dt = pd.to_datetime(row['Date'] + ' ' + row['Collected_at'], format='%d.%m.%Y. %H:%M')
        #if dt_min - pd.Timedelta('6 hours') <= dt <= dt_max + pd.Timedelta('6 hours'):
        df.at[dt, row['Town']] = row[field]
    except:
        #print(f' - Probably missing data at row {index}')
        continue

#plt.figure(figsize=(20,12))
#for iloc, location in enumerate(locations):
#    df[location].plot(ls='-', lw=0.5, marker='.', ms=0.5)
#plt.xlim(pd.to_datetime('2020-05-01 00:00:00'), pd.to_datetime('2020-08-15 00:00:00'))
#plt.savefig(f'raw_data_{field}.png', dpi=150)
#plt.close()

print('Filling missed entries by interpolation')
df = df.interpolate(method='linear')[dt_min:dt_max]
preprocesed_csv_filenmae = f'preprocessed_data_{field}.csv'
print(f'Saving preprocessed data to {preprocesed_csv_filenmae}')    
df.to_csv(preprocesed_csv_filenmae)

print('Doing SVD')
A = np.array(df)
#np.savetxt('A.txt', A) # For debugging
U, S, V = np.linalg.svd(A, full_matrices=False)
print(U.shape)
print(S.shape)
print(V.shape)

plt.figure(tight_layout=True)
plt.bar(np.arange(np.size(S)), np.cumsum(S / np.sum(S)), width=0.5)
plt.bar(np.arange(np.size(S)), S / np.sum(S), width=0.2)
for i in range(np.size(S)):
    plt.text(i, S[i] / np.sum(S) + 0.01, f'{100*S[i] / np.sum(S):.1f}%', 
             rotation=90, va='bottom', ha='center', fontsize=10)
plt.xlabel('Rang sustava')
plt.ylabel('Preciznost rekonstrukcije')
plt.grid(ls=':')

# dates to concept
plt.figure(tight_layout=True)
for i in range(k):
    plt.plot(df.index, U[:, i], label='k=' + str(i))


plt.title('Dates to concept for k = ' + str(k))
plt.legend()
plt.grid(ls=':')


# towns to concept
plt.figure(tight_layout=True)
xticks = np.arange(len(locations))
plt.xticks(xticks, labels=locations, rotation=90)
w = 1 / (3 + k)
for i in range(k):
    plt.bar(xticks + i * w - (k/2 - 0.5) * w, # centering bars to ticks
            V[i, :], 
            label='k=' + str(i),
            alpha=1,
            width=w)
plt.title('Towns to concept for k = ' + str(k))
plt.legend()
plt.grid(ls=':')


# lower rank reconstruction - matrix svd_Ar
Ar = np.dot(U[:,:k] * S[:k], V[:k, :])
svd_err = np.average(np.abs(A - Ar), axis=0)
axis_range = np.arange(0, len(locations))
plt.figure()
plt.xticks(axis_range, locations, rotation=90)
plt.bar(axis_range, svd_err) 
plt.xlabel('Lokacije')
plt.ylabel(f'Prosječno apsolutno odstupanje rekonstrukcije s rangom k={k} [°C]')


print('Making time series plots')

for iloc, location in enumerate(locations):
    print(f'Making SVD plot for {location}')
    fig = plt.figure(figsize=(20, 10), tight_layout=True)
    legend_handles = []
    legend_labels = []

    plt_orig, = plt.plot(df[location], marker='o', ls='', c='r', ms=1)    
    legend_handles.append(plt_orig)
    legend_labels.append('Original data')
    
    a_cum = np.zeros(A.shape[0])
    for i in range(k):
        a_k = np.dot(U[:,i] * S[i], V[i, iloc])
        flbtw_k = plt.fill_between(df.index, a_cum, a_cum + a_k, alpha=0.3, label=f'k={i}')
        legend_handles.append(flbtw_k)
        legend_labels.append(f'k={i}')
        a_cum += a_k
    
    plt_recon, = plt.plot(df.index, a_cum, marker='s', ls='--', c='b', lw=1, ms=1)    
    legend_handles.append(plt_recon)
    legend_labels.append('Reconstruction')
    
    plt.legend(legend_handles, legend_labels)
    plt.ylim(df[location].min() - 2, df[location].max() + 2)
    fig.savefig(f'svd_reconstruction_plot_{field.lower()}_{location}.png', dpi=90)
    plt.close(fig)