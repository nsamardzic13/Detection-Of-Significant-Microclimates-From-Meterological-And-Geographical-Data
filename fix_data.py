import pandas as pd
from datetime import datetime, timedelta

def main():
    wrong_time = ['01:00', '03:00', '05:00', '07:00', '09:00', '11:00', '13:00', '15:00', '17:00', '19:00', '21:00', '23:00', '12:30', '10:30']
    correct_time = ['01:30', '03:30', '05:30', '07:30', '09:30', '11:30', '13:30', '15:30', '17:30', '19:30', '21:30', '23:30', '13:30', '11:30']
    df = pd.read_csv('data_pgz.csv')
    for index, row in df.iterrows():
        if (row['Collected_at'] in wrong_time):
            pos = wrong_time.index(row['Collected_at'])
            df.at[index, 'Collected_at'] = correct_time[pos]

        if (row['Collected_at'] == '23:00' or row['Collected_at'] == '23:30'):
            date = datetime.strptime(row['Date'], "%d.%m.%Y.")
            ret_date = date - timedelta(days=1)
            df.at[index, 'Date'] = datetime.strftime(ret_date, "%d.%m.%Y.")

    df.to_csv('./data_pgz_fixed.csv', index=False)
if __name__ == '__main__':
    main()