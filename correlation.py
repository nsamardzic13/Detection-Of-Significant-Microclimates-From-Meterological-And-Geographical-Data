import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fields = ['Temperature',]

# get data from csv files
def import_csv_file():
    df_data_pgz = pd.read_csv('data_pgz_fixed.csv')
    df_data_pgz['Date'] = pd.to_datetime(df_data_pgz['Date'], yearfirst=True, format='%d.%m.%Y.').dt.date   #format date
    df_data_pgz = df_data_pgz.sort_values(by=['Town', 'Date'])
    df_geolocation = pd.read_csv('geolocation.csv').sort_values(by='Town')
    return df_data_pgz, df_geolocation

# format list to have first letter uppercase
def list_title(list):
    ret_list = []
    for row in list:
        ret_list.append(row.title())
    return ret_list

def get_correlation_matrix(data, towns, field):
    ret_matrix = np.zeros((len(towns), len(towns))) - 100
    for i, town1 in enumerate(towns):
        town1_values = np.array(data.loc[data['Town'] == town1][field])
        for j, town2 in enumerate(towns):
            town2_values = np.array(data.loc[data['Town'] == town2][field])
            ret_matrix[i,j] = np.correlate(town1_values, town2_values)[0]

        ret_matrix[i] -= ret_matrix[i,i]
    return ret_matrix

# define main funcion
def main():
    df_data_pgz, df_geolocation = import_csv_file()   # call function to import data from files
    unique_towns = list(df_geolocation.sort_values(by='Town')['Town'])     # get unique names of towns ordered by name

    for field in fields:
        corr_matrix = get_correlation_matrix(data=df_data_pgz, towns=unique_towns, field=field)
        print(corr_matrix)

# call main function
if __name__ == "__main__":
    main()