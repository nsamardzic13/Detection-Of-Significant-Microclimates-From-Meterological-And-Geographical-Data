import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# get data from csv files
def import_csv_file():
    df_data_pgz = pd.read_csv('data_pgz.csv').sort_values(by='Town')
    df_geolocation = pd.read_csv('geolocation.csv').sort_values(by='Town')
    df_distance = pd.read_csv('distance.csv').sort_values(by=['Town1', 'Town2',])
    df_altitude = pd.read_csv('nadmorska_visina.csv').sort_values(by='Town')
    return df_data_pgz, df_geolocation, df_distance, df_altitude

# format list to have first letter uppercase
def list_title(list):
    ret_list = []
    for row in list:
        ret_list.append(row.title())
    return ret_list

# get autocorrelation
def get_autocorrelation(data, names, autocorr_column):
    filter_dates = ['10.05.2020.', ]  # list of dates we want to filer
    # filter_dates = list(data.ffill().sort_values('Date')['Date'].unique()[1:])   # list of dates we want to filer, after change od 23:30 must try removing [1:]
    dict_autocorrelation = {}
    # 2 loops: filter all days and all towns
    for date in filter_dates:
        dict_temp = {}
        for name in names:
            by_name = data.loc[(data['Town'] == name) & (data['Date'] == date)].sort_values(by='Collected_at')  # filter dataFrame
            dict_temp[name] = by_name[autocorr_column].autocorr(lag=-1)
        dict_autocorrelation[date] = dict_temp

    return dict_autocorrelation

def daily_temp(data, names):
    filter_dates = ['10.05.2020.', ]  # list of dates we want to filer
    # filter_dates = list(data.ffill().sort_values('Date')['Date'].unique()[1:])   # list of dates we want to filer, after change od 23:30 must try removing [1:]
    # 2 loops: filter all days and all towns
    for date in filter_dates:
        for name in names:
            by_name = data.loc[(data['Town'] == name) & (data['Date'] == date)].sort_values(by='Collected_at') # filter dataFrame
            x_values = list(by_name['Collected_at']) # get x values: time
            y_values = list(by_name['Temperature']) # get y values: temperature
            plt.plot(x_values, y_values)

        # add title, legend and gird to every plot
        plt.title('Temperature for ' + date)
        plt.legend(list_title(list=names), loc='upper right')
        plt.grid()
        plt.show()

# define main funcion
def main():
    df_data_pgz, df_geolocation, df_distance, df_altitude = import_csv_file()   # call function to import data from files
    unique_towns = list(df_altitude.sort_values(by='Town')['Town'])     # get unique names of towns ordered by name
    # daily_temp(data=df_data_pgz, names=unique_towns)  # call function to plot temperature by date for all places
    autocorrelation = get_autocorrelation(data=df_data_pgz, names=unique_towns, autocorr_column='Temperature') # call function to get nested dict of autocorrelation for all places by date
    print(autocorrelation)


# call main function
if __name__ == "__main__":
    main()