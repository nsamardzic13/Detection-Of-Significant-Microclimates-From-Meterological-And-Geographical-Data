import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def main():
    df = pd.read_csv('data_pgz.csv')
    for index, row in df.iterrows():
        if (row['Collected_at'] == '23:00' or row['Collected_at'] == '23:30'):
            date = datetime.strptime(row['Date'], "%d.%m.%Y.")
            ret_date = date - timedelta(days=1)
            df.at[index, 'Date'] = datetime.strftime(ret_date, "%d.%m.%Y.")
    df.to_csv('./data_pgz_fixed.csv', index=False)
if __name__ == '__main__':
    main()