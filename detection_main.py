import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# define global variables
# filter_dates = ['10.05.2020.', ]  # list of dates we want to filer
# filter_dates = list(data.ffill().sort_values('Date')['Date'].unique()[1:])   # list of dates we want to filer, after change od 23:30 must try removing [1:]
autocorrelation_difference = 0.10   # 10% differene
autocorrelation_text = ' these towns have microclimates based on autocorrelation throughout day: '

# get data from csv files
def import_csv_file():
    df_data_pgz = pd.read_csv('data_pgz.csv')
    df_data_pgz['Date'] = pd.to_datetime(df_data_pgz['Date'], yearfirst=True, format='%d.%m.%Y.').dt.date
    df_data_pgz = df_data_pgz.sort_values(by=['Town', 'Date'])
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
def get_autocorrelation(data, filter_dates, names, autocorr_column):
    dict_autocorrelation = {}
    # 2 loops: filter all days and all towns
    for date in filter_dates:
        dict_temp = {}
        for name in names:
            by_name = data.loc[(data['Town'] == name) & (data['Date'] == date)].sort_values(by='Collected_at')  # filter dataFrame
            dict_temp[name] = by_name[autocorr_column].autocorr(lag=-1)
        dict_autocorrelation[date] = dict_temp

    return dict_autocorrelation

def daily_temp(data, filter_dates, names):
   # 2 loops: filter all days and all towns
    for date in filter_dates:
        for name in names:
            by_name = data.loc[(data['Town'] == name) & (data['Date'] == date)].sort_values(by='Collected_at') # filter dataFrame
            x_values = list(by_name['Collected_at']) # get x values: time
            y_values = list(by_name['Temperature']) # get y values: temperature
            plt.plot(x_values, y_values)

        # add title, legend and gird to every plot
        plt.title('Temperature for ' + str(date))
        plt.legend(list_title(list=names), loc='upper right')
        plt.grid()
        plt.show()

# print microclimates towns
def print_towns(data, message):
    for date in data:
        print('On ' + str(date) + message + str(data[date]).strip('[]'))
    # [print('On ' + date + message + str(data[date]).strip('[]')) for date in data]

# define function to check for microclimates
# difference is given argument - changes based on data we are checking
# default difference for height is 100m and for distance is 20km
def check_microclimates(data, filter_dates, names, allowed_difference , distance, altitude, diff_height=100, diff_dist=30, default_cnt=3):
    ret_dict = {}
    for date in filter_dates:
        tmp_list = []
        i = 0
        for name in names:
            tmp_cnt = 0
            i = i + 1
            altitude_value = altitude.loc[(altitude['Town'] == name)]['Elevation'].item()
            for name2 in names[i:]:
                abs_diff = np.abs(data[date][name] - data[date][name2]) / data[date][name]
                towns_distance = distance.loc[(distance['Town1'] == name) & (distance['Town2'] == name2)]['Distance'].item()
                town_altitude = altitude.loc[(altitude['Town'] == name2)]['Elevation'].item()
                if abs_diff > allowed_difference:
                    if towns_distance < diff_dist and np.abs(altitude_value - town_altitude) < diff_height:
                        tmp_cnt = tmp_cnt + 1
            if tmp_cnt > default_cnt:
                tmp_list.append(name)
        if tmp_list:
            ret_dict[date] = tmp_list

    return ret_dict

# define main funcion
def main():
    df_data_pgz, df_geolocation, df_distance, df_altitude = import_csv_file()   # call function to import data from files
    unique_towns = list(df_altitude.sort_values(by='Town')['Town'])     # get unique names of towns ordered by name
    filter_dates = list(df_data_pgz.ffill()['Date'].unique()[1:])  # list of dates we want to filer, after change od 23:30 - try removing [1:]
    daily_temp(data=df_data_pgz, filter_dates=filter_dates, names=unique_towns)  # call function to plot temperature by date for all places
    # autocorrelation = get_autocorrelation(data=df_data_pgz, filter_dates=filter_dates, names=unique_towns, autocorr_column='Temperature') # call function to get nested dict of autocorrelation for all places by date
    # microclimates_autocorrelation = check_microclimates(data=autocorrelation, filter_dates=filter_dates, names=unique_towns, allowed_difference=autocorrelation_difference, distance=df_distance, altitude=df_altitude)
    print_towns(microclimates_autocorrelation, autocorrelation_text)


# call main function
if __name__ == "__main__":
    main()