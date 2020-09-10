import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

def plot_data(data, txt):
    town = 'opatija'
    start_date = '02.07.2020.'
    end_date = '03.07.2020.'
    new_data = data.loc[((data['Date'] == start_date) | (data['Date'] == end_date)) & (data['Town'] == town)]
    fig = plt.figure(figsize=(12.0, 8.0))
    x_asix_ticks = list(new_data['Collected_at'])
    x_len = len(x_asix_ticks)
    x_asix = np.arange(0, x_len)
    y_asix = list(new_data['Temperature'])


    plt.plot(x_asix, y_asix)
    plt.grid()
    plt.xlabel('Collected at')
    plt.ylabel('Temperature [°C]')
    plt.xticks(x_asix, x_asix_ticks, rotation=90)
    plt.title(f'{town.capitalize()} on {start_date} & {end_date} {txt} interpolation')
    fig.savefig(f'Data/{txt}_interpolation.png')

def fix_nan(data, index, col):
    step = 27
    ret_val = None
    if index - step >= 0:
        step = -27
        ret_val = data.iloc[index+step][col]
    if ret_val is None:
        step = 27
        ret_val = data.iloc[index+step][col]

    if col in ['Date', 'Collected_at']:
        cur_dt = data.iloc[index+step]['Date']
        cur_time = data.iloc[index+step]['Collected_at']
        if col == 'Collected_at':
            if cur_time == '23:30' and step < 0:
                ret_val = '01:30'
            elif cur_time == '01:30' and step > 0:
                ret_val = '23:30'
            elif step < 0:
                tmp_time = datetime.strptime(cur_time, "%H:%M")
                tmp_time = tmp_time + timedelta(hours=2)
                ret_val = datetime.strftime(tmp_time, "%H:%M")
            else:
                tmp_time = datetime.strptime(cur_time, "%H:%M")
                tmp_time - timedelta(hours=2)
                ret_val = datetime.strftime(tmp_time, "%H:%M")
        else:
            if step < 0:
                tmp_date = datetime.strptime(cur_dt, "%d.%m.%Y.")
                tmp_date = tmp_date + timedelta(days=1)
                ret_val = datetime.strftime(tmp_date, "%d.%m.%Y.")
            else:
                tmp_date = datetime.strptime(cur_dt, "%d.%m.%Y.")
                tmp_date = tmp_date - timedelta(days=1)
                ret_val = datetime.strftime(tmp_date, "%d.%m.%Y.")

    return ret_val

def main():
    df = pd.read_csv('data_pgz.csv')
    df = df[['Town', 'Date', 'Collected_at', 'Temperature', 'Weather', 'Real_feel', 'Humidity']]
    columns = list(df.columns)
    columns.remove('Temperature')
    columns.remove('Real_feel')
    columns.remove('Humidity')
    wrong_time_0 = ['01:00', '03:00', '05:00', '07:00', '09:00', '11:00', '13:00', '15:00', '17:00', '19:00', '21:00', '23:00']
    wrong_time_30 = ['00:30', '02:30', '04:30', '06:30', '08:30', '10:30', '12:30', '14:30', '16:30', '18:30', '20:30', '22:30']
    correct_time = ['01:30', '03:30', '05:30', '07:30', '09:30', '11:30', '13:30', '15:30', '17:30', '19:30', '21:30', '23:30']
    for index, row in df.iterrows():
        for col_name in columns:
            if pd.isna(row[col_name]):
                ret_val = fix_nan(data=df, index=index,col=col_name)
                row[col_name] = ret_val
                df.at[index, col_name] = ret_val

        if (row['Collected_at'] in wrong_time_0):
            pos = wrong_time_0.index(row['Collected_at'])
            df.at[index, 'Collected_at'] = correct_time[pos]

        elif (row['Collected_at'] in wrong_time_30):
            pos = wrong_time_30.index(row['Collected_at'])
            df.at[index, 'Collected_at'] = correct_time[pos]

        if (row['Collected_at'] == '23:00' or row['Collected_at'] == '23:30'):
            date = datetime.strptime(row['Date'], "%d.%m.%Y.")
            ret_date = date - timedelta(days=1)
            df.at[index, 'Date'] = datetime.strftime(ret_date, "%d.%m.%Y.")


    plot_data(df, 'before')
    df = df.interpolate(method='linear', asix='Temperature')
    df = df.interpolate(method='linear', asix='Real_feel')
    df = df.interpolate(method='linear', asix='Humidity')
    df.to_csv('./data_pgz_fixed.csv', index=False)
    plot_data(df, 'after')
    start_time = str(df.iloc[0]['Date']) + ' ' + str(df.iloc[0]['Collected_at'])
    end_time = str(df.iloc[-1]['Date']) + ' ' + str(df.iloc[-1]['Collected_at'])
    unique_towns = list(df.sort_values(by='Town')['Town'].unique())
    df_svd_temp = pd.DataFrame(columns=unique_towns, index=pd.date_range(start=pd.to_datetime(start_time),
                                                                    end=pd.to_datetime(end_time),
                                                                    freq='2h'), dtype=float)
    df_svd_realfeel = pd.DataFrame(columns=unique_towns, index=pd.date_range(start=pd.to_datetime(start_time),
                                                                    end=pd.to_datetime(end_time),
                                                                    freq='2h'), dtype=float)
    df_svd_humidity = pd.DataFrame(columns=unique_towns, index=pd.date_range(start=pd.to_datetime(start_time),
                                                                    end=pd.to_datetime(end_time),
                                                                    freq='2h'), dtype=float)

    for index, row in df.iterrows():
        try:
            dt = pd.to_datetime(str(row['Date']) + ' ' + str(row['Collected_at']), format='%d.%m.%Y. %H:%M', yearfirst=True)
            df_svd_temp.at[dt, row['Town']] = row['Temperature']
            df_svd_realfeel.at[dt, row['Town']] = row['Real_feel']
            df_svd_humidity.at[dt, row['Town']] = row['Humidity']
        except:
            continue
    df_svd_temp = df_svd_temp.interpolate(method='linear')
    df_svd_realfeel = df_svd_realfeel.interpolate(method='linear')
    df_svd_humidity = df_svd_humidity.interpolate(method='linear')

    df_svd_temp.to_csv('./data_svd_temp.csv')
    df_svd_realfeel.to_csv('./data_svd_realfeel.csv')
    df_svd_humidity.to_csv('./data_svd_humidity.csv')
if __name__ == '__main__':
    main()