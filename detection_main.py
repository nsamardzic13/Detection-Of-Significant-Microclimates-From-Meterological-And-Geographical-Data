import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# define global variables
autocorrelation_text = ' these towns have microclimates based on autocorrelation throughout day: '
autocorrelation_weather_condition = ['vedro', 'kiša', 'malo oblačno']
autocorrelation_difference = 0.15   # x% differene
def_height = 100    # max height difference
def_dist = 50       # max distance difference
def_cnt = 13         # number of towns around

# get data from csv files
def import_csv_file():
    df_data_pgz = pd.read_csv('data_pgz_fixed.csv')
    df_data_pgz['Date'] = pd.to_datetime(df_data_pgz['Date'], yearfirst=True, format='%d.%m.%Y.').dt.date   #format date
    df_data_pgz = df_data_pgz.sort_values(by=['Town', 'Date'])
    df_geolocation = pd.read_csv('geolocation.csv').sort_values(by='Town')
    df_distance = pd.read_csv('distance.csv').sort_values(by=['Town1', 'Town2',])
    df_altitude = pd.read_csv('nadmorska_visina.csv').sort_values(by='Town')
    df_svd = pd.read_csv('data_svd.csv', index_col=0)
    df_svd.index = pd.to_datetime(df_svd.index)
    return df_data_pgz, df_geolocation, df_distance, df_altitude, df_svd

# format list to have first letter uppercase
def list_title(list):
    ret_list = []
    for row in list:
        ret_list.append(row.title())
    return ret_list

# get top n days with desired weather
def get_dates(data, value):
    tmp_ret_list = data.loc[data['Weather'] == value][['Date']]
    ret_list = tmp_ret_list['Date'].value_counts().nlargest(10).index.tolist()
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

def plot_temp(data_geo, data_temp, filter_dates, res_dict, plot_dict, weather):
   dimension = (data_geo['Lng'].min(), data_geo['Lng'].max(), data_geo['Lat'].min(), data_geo['Lat'].max())
   min_lng, max_lng, min_lat, max_lat = dimension[0], dimension[1], dimension[2], dimension[3]
   # 2 loops: filter all days and all towns
   for date in filter_dates:
       names = list(set(res_dict[date] + plot_dict[date]))
       img = plt.imread('./map.png')
       fig, ax = plt.subplots(figsize=(8, 7))
       fig2, ax2 = plt.subplots(figsize=(8, 7))
       for name in names:
           by_name = data_temp.loc[(data_temp['Town'] == name) & (data_temp['Date'] == date)].sort_values(by='Collected_at')  # filter dataFrame
           x_values = list(by_name['Collected_at'])  # get x values: time
           y_values = list(by_name['Temperature'])  # get y values: temperature
           current_lat = float(data_geo.loc[(data_geo['Town'] == name)]['Lat'])
           current_lng = float(data_geo.loc[(data_geo['Town'] == name)]['Lng'])
           if name in res_dict[date]:
               ax.scatter(current_lng, current_lat, zorder=1, alpha=1, c='b', s=20, label=name)
               ax2.plot(x_values, y_values, alpha=0.8, linewidth=4)

           elif name in plot_dict[date]:
               ax.scatter(current_lng, current_lat, zorder=1, alpha=1, c='r', s=20)
               ax2.plot(x_values, y_values, alpha=0.4)

       # add title, legend and gird to every plot
       ax2.set_title('Temperature for ' + str(date) + '(' + weather + ')')
       ax2.legend(list_title(list=names), loc='upper right')
       ax2.grid()
       ax.set_title('Microclimates on ' + str(date) + '( ' + weather + ' )')
       ax.set_xlim([min_lng, max_lng])
       ax.set_ylim([min_lat, max_lat])
       ax.legend(loc='upper right')
       ax.imshow(img, zorder=0, extent=dimension, aspect='equal')
       plt.show()

# print microclimates towns
def print_towns(data, message):
    for date in data:
        print('On ' + str(date) + message + str(data[date]).strip('[]'))

# define function to check for microclimates
# difference is given argument - changes based on data we are checking
# default difference for height is 100m and for distance is 20km
def check_microclimates(data, filter_dates, names, allowed_difference , distance, altitude,
                        diff_height=def_height, diff_dist=def_dist, default_cnt=def_cnt):
    ret_dict = {}
    plot_dict = {}
    for date in filter_dates:
        tmp_list = []
        tmp_plot_list = []
        for name in names:
            tmp_cnt = 0
            # altitude_value = altitude.loc[(altitude['Town'] == name)]['Elevation'].item()
            for name2 in names:
                if name == name2:
                    continue
                abs_diff = np.abs(data[date][name] - data[date][name2]) / data[date][name]
                # towns_distance = distance.loc[(distance['Town1'] == name) & (distance['Town2'] == name2)]['Distance'].item()
                # town_altitude = altitude.loc[(altitude['Town'] == name2)]['Elevation'].item()
                if abs_diff > allowed_difference:
                    # if towns_distance < diff_dist and np.abs(altitude_value - town_altitude) < diff_height:
                    #     tmp_cnt = tmp_cnt + 1
                    tmp_cnt = tmp_cnt + 1
                    if name2 not in tmp_plot_list:
                        tmp_plot_list.append(name2)
            if tmp_cnt > default_cnt:
                tmp_list.append(name)
        if tmp_list:
            ret_dict[date] = tmp_list
            plot_dict[date] = tmp_plot_list

    return ret_dict, plot_dict

# plot svd
def svd_plot(data, names, dates):
    for i, name in enumerate(names):
        plt.plot(dates, data[:, i], label=name)
    plt.grid()
    plt.legend()
    plt.show()

# define main funcion
def main():
    df_data_pgz, df_geolocation, df_distance, df_altitude, df_svd = import_csv_file()   # call function to import data from files
    unique_towns = list(df_altitude.sort_values(by='Town')['Town'])     # get unique names of towns ordered by name
    filter_dates = list(df_data_pgz.ffill()['Date'].unique())  # list of dates we want to filer, after change od 23:30 - try removing [1:]

    # call functions to get microclimates values based on autocorrelation
    for weather in autocorrelation_weather_condition:
        autocorrelation_days = get_dates(df_data_pgz, weather)
        autocorrelation = get_autocorrelation(data=df_data_pgz, filter_dates=autocorrelation_days, names=unique_towns, autocorr_column='Temperature') # call function to get nested dict of autocorrelation for all places by date
        microclimates_autocorrelation, plot_dict = check_microclimates(data=autocorrelation, filter_dates=autocorrelation_days, names=unique_towns,
                                                            allowed_difference=autocorrelation_difference, distance=df_distance, altitude=df_altitude) #check if we have microclimates
        # output of microclimates based on autocorrelation
        print('For days with weather description: ' + weather)
        if microclimates_autocorrelation:
            dates_microclimates = list(microclimates_autocorrelation.keys())    #get dates when we have towns with microclimates
            print_towns(microclimates_autocorrelation, autocorrelation_text)    #print towns and dates with microclimates
            # plot_temp(data_geo=df_geolocation, data_temp=df_data_pgz ,filter_dates=dates_microclimates, res_dict=microclimates_autocorrelation, plot_dict=plot_dict, weather=weather)  # call function to plot temperature by date for all places
        else:
            print('There are no towns with microclimates with current variables')

    # build 2d array having shape (filter_dates, unique_towns) and average temperatures

    svd_A = np.array(df_svd)

    # build matrix U, S, V
    svd_U, svd_S, svd_V = np.linalg.svd(svd_A, full_matrices=False)
    print(svd_S / np.sum(svd_S))

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

    svd_err = np.average(np.abs(svd_A - svd_Ar), axis=0)
    asix_range = np.arange(0, len(unique_towns))
    plt.plot(svd_err) 
    plt.xticks(asix_range, unique_towns, rotation=90)
    plt.xlabel('Lokacije')
    plt.ylabel(f'Prosječno apsolutno odstupanje rekonstrukcije s rangom k={k} [°C]')
    plt.show()

    print('Diff for k=' + str(k) + ': ' + str(np.mean(np.abs(svd_A-svd_Ar))))
    # svd_plot(data=svd_Ar, names=unique_towns, dates=filter_dates)

    # dates to concept
    for i in range(k):
        plt.plot(df_svd.index, svd_U[:, i], label='k=' + str(i))

    plt.title('Dates to concept for k = ' + str(k))
    plt.legend()
    plt.grid()
    plt.figure()

    # towns to concept
    asix_range = np.arange(0, len(unique_towns))
    for i in range(k):
        plt.xticks(asix_range, unique_towns, rotation=90)
        plt.bar(asix_range + i / (1 + k), svd_V[i, :], label='k=' + str(i), alpha=k*0.2, width=1 / (1 + k))
    plt.title('Towns to concept for k = ' + str(k))
    plt.legend()
    plt.show()

# call main function
if __name__ == "__main__":
    main()