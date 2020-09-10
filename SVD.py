import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# get data from csv files
def import_csv_file():
    df_geolocation = pd.read_csv('geolocation.csv').sort_values(by='Town')
    return df_geolocation

def plot_svd_map(unique_towns, vector, k, data_geo):
    color_map = plt.cm.seismic
    dimension = (data_geo['Lng'].min(), data_geo['Lng'].max(), data_geo['Lat'].min(), data_geo['Lat'].max())
    min_lng, max_lng, min_lat, max_lat = dimension[0], dimension[1], dimension[2], dimension[3]
    all_lat = []
    all_lng = []
    for town in unique_towns:
        current_lat = float(data_geo.loc[(data_geo['Town'] == town)]['Lat'])
        current_lng = float(data_geo.loc[(data_geo['Town'] == town)]['Lng'])
        all_lat.append(current_lat)
        all_lng.append(current_lng)

    img = plt.imread('./map2.png')
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.scatter(all_lng, all_lat, zorder=1, alpha=1, c=vector, s=40, cmap=color_map)

    ax.set_title(f'Towns for k = {k}')
    ax.set_xlim([min_lng, max_lng])
    ax.set_ylim([min_lat, max_lat])
    ax.imshow(img, zorder=0, extent=dimension, aspect='equal')

# reconstruct temperatures of unique towns using svd
def reconstruct_temperatures(unique_towns, df_svd, svd_A, svd_U, svd_S, svd_V, k, label):
    print('Making SVD plot for unique towns')
    for iloc, location in enumerate(unique_towns):
        fig = plt.figure(figsize=(20, 10), tight_layout=True)
        legend_handles = []
        legend_labels = []

        plt_orig, = plt.plot(df_svd[location], marker='o', ls='', c='r', ms=1)
        legend_handles.append(plt_orig)
        legend_labels.append('Original data')

        a_cum = np.zeros(svd_A.shape[0])
        for i in range(k):
            a_k = np.dot(svd_U[:, i] * svd_S[i], svd_V[i, iloc])
            flbtw_k = plt.fill_between(df_svd.index, a_cum, a_cum + a_k, alpha=0.3, label='k= ' + str(i))
            legend_handles.append(flbtw_k)
            legend_labels.append(f'k= {i}')
            a_cum += a_k

        plt_recon, = plt.plot(df_svd.index, a_cum, marker='s', ls='--', c='b', lw=1, ms=1)
        legend_handles.append(plt_recon)
        legend_labels.append('Reconstruction')

        plt.legend(legend_handles, legend_labels)
        plt.ylim(df_svd[location].min() - 2, df_svd[location].max() + 2)
        fig.savefig(f'./Reconstruct_temp/svd_reconstruction_plot_{label}_{location}.png', dpi=90)
        plt.close(fig)

def trunc_df(df):
    start = pd.to_datetime('2020-07-01 19:30:00')
    end = pd.to_datetime('2020-08-01 19:30:00')
    ret_df = df.loc[start:end]
    return ret_df

# define main funcion
def main():
    df_geolocation = import_csv_file()  # call function to import data from files
    unique_towns = list(df_geolocation.sort_values(by='Town')['Town'])  # get unique names of towns ordered by name

    # build 2d array having shape (unique_towns, date+collected_at) and average temperatures
    for svd_txt in ['temp', 'realfeel', 'humidity']:
        print(f'Doing analisys for {svd_txt}')
        if (svd_txt == 'humidity'):
            sign = '[%]'
        else:
            sign = '[°C]'
        df_svd = pd.read_csv('data_svd_' + svd_txt + '.csv', index_col=0)
        df_svd.index = pd.to_datetime(df_svd.index)

        # df_svd = trunc_df(df_svd)
        svd_A = np.array(df_svd)

        # build matrix U, S, V
        svd_U, svd_S, svd_V = np.linalg.svd(svd_A, full_matrices=False)
        # print(svd_S / np.sum(svd_S))

        plt.bar(np.arange(np.size(svd_S)), np.cumsum(svd_S / np.sum(svd_S)))
        plt.xlabel('Rang sustava')
        plt.ylabel('Preciznost rekonstrukcije')
        plt.show()

        # full reconstruction - matrix svd_Ar
        svd_Ar = np.dot(svd_U * svd_S, svd_V)
        print('Diff: ' + str(np.mean(np.abs(svd_A - svd_Ar))))
        # lower rank reconstruction - matrix svd_Ar
        k = 3
        svd_Ar = np.dot(svd_U[:,:k] * svd_S[:k], svd_V[:k, :])
        print('Diff reconstruction: ' + str(np.mean(np.abs(svd_A - svd_Ar))))
        svd_err = np.average(np.abs(svd_A - svd_Ar), axis=0)
        asix_range = np.arange(0, len(unique_towns))
        plt.plot(svd_err)
        plt.xticks(asix_range, unique_towns, rotation=90)
        plt.xlabel('Locations')
        plt.ylabel(f'Prosječno apsolutno odstupanje rekonstrukcije s rangom k={k} {sign}')
        plt.show()

        # dates to concept
        for i in range(k):
            plt.plot(df_svd.index, svd_U[:, i], label='k=' + str(i))

        plt.title(f'Dates to concept for k = {k}')
        plt.legend()
        plt.grid()
        plt.figure()

        # towns to concept
        asix_range = np.arange(0, len(unique_towns))
        for i in range(k):
            plt.xticks(asix_range, unique_towns, rotation=90)
            plt.bar(asix_range + i / (1 + k), svd_V[i, :], label='k=' + str(i), alpha=k*0.2, width=1 / (1 + k))
        plt.title(f'Towns to concept for k = {k}')
        plt.legend()
        plt.show()

        for i in range(k):
            plot_svd_map(unique_towns=unique_towns, vector=svd_V[i, :], k=i, data_geo=df_geolocation)
        plt.show()

        # SVD reconstruction temperature
        if (svd_txt == 'temp'):
            reconstruct_temperatures(unique_towns=unique_towns, df_svd=df_svd, svd_A=svd_A, svd_U=svd_U, svd_S=svd_S, svd_V=svd_V, k=k, label=svd_txt)


# call main function
if __name__ == "__main__":
    main()