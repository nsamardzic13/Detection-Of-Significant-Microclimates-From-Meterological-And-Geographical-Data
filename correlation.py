import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fields = ['Temperature',]
corr_percent = 0.99

# get data from csv files
def import_csv_file():
    df_data_pgz = pd.read_csv('data_pgz_fixed.csv')
    df_data_pgz['Date'] = pd.to_datetime(df_data_pgz['Date'], yearfirst=True, format='%d.%m.%Y.').dt.date   #format date
    df_data_pgz = df_data_pgz.sort_values(by=['Town', 'Date'])
    df_geolocation = pd.read_csv('geolocation.csv').sort_values(by='Town')
    return df_data_pgz, df_geolocation

def get_correlation_matrix(data, towns, field):
    towns_cnt = len(towns)
    ret_matrix = np.zeros((towns_cnt, towns_cnt))
    for i, town1 in enumerate(towns):
        town1_values = np.array(data.loc[data['Town'] == town1][field])
        for j, town2 in enumerate(towns):
            town2_values = np.array(data.loc[data['Town'] == town2][field])
            ret_matrix[i,j] = np.correlate(town1_values, town2_values)[0]

    return ret_matrix

def plot_corr(cor, towns, field):
    dict = {}
    asix_range = np.arange(0, len(towns))
    for i, town in enumerate(towns):
        dict_list = []
        fig = plt.figure(figsize=(13.5,8.0))
        for j in range(len(towns)):
            if i == j:
                plt.bar(asix_range[j], cor[i][j], width=1)
            else:
                min_val = min([cor[i][i],cor[i][j]])
                max_val = max([cor[i][i],cor[i][j]])
                diff_res = min_val / max_val
                if (diff_res > corr_percent):
                    dict_list.append(towns[j])
                plt.bar(asix_range[j], cor[i][j], width=0.6)

        plt.axhline(y = cor[i,i], color='black', linewidth=2, alpha=0.4, label=str(cor[i,i]))
        # plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.xticks(asix_range, towns, rotation=90)
        plt.yticks([])
        plt.title(f'Correlation chart for {town.capitalize()}')
        fig.savefig(f'Correlation/{field}_correlation_chart_{town}.png')
        dict[town] = dict_list

    return dict
# define main funcion
def main():
    df_data_pgz, df_geolocation = import_csv_file()   # call function to import data from files
    unique_towns = list(df_geolocation.sort_values(by='Town')['Town'])     # get unique names of towns ordered by name

    for field in fields:
        corr_matrix = get_correlation_matrix(data=df_data_pgz, towns=unique_towns, field=field)
        corr_dict = plot_corr(cor=corr_matrix, towns=unique_towns, field=field)
        for town in unique_towns:
            print(f'{town}: {corr_dict[town]}')

# call main function
if __name__ == "__main__":
    main()