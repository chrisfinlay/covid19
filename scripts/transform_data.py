from tqdm import tqdm
import datetime as dt
import pandas as pd
import numpy as np
import json
import os

########### Global Variables ###################################################

COVID_DIR = os.path.split(os.path.split(os.path.join(os.getcwd(), __file__))[0])[0]

DATA_DIR = os.path.join(COVID_DIR, 'data')

CONFIRMED_CSV = os.path.join(DATA_DIR, 'IRD/confirmed.csv')

WEATHER_DIR = os.path.join(DATA_DIR, 'weather')

################################################################################

def weather():
    c = pd.read_csv(CONFIRMED_CSV)

    non_date_cols = ['Province/State', 'Country/Region', 'Lat', 'Long']
    cases = c.drop(columns=non_date_cols).values
    df_dates = c.drop(columns=non_date_cols).columns.values

    dates = [dt.datetime.strptime(date+'20', '%m/%d/%Y').strftime('%Y-%m-%dT12:00:00')
             for date in df_dates]

    lats = c['Lat'].values
    lons = c['Long'].values

    t, h, w = c.copy(), c.copy(), c.copy()

    t[df_dates] = np.nan
    h[df_dates] = np.nan
    w[df_dates] = np.nan

    for i in tqdm(range(len(lats))):
        for date in dates:
            filename = f'{lats[i]:.6}_{lons[i]:.6}_{date}.json'
            file_path = os.path.join(WEATHER_DIR, filename)
            date = dt.datetime.strptime(date, '%Y-%m-%dT12:00:00')
            date = f'{date.month}/{date.day}/20'
            exists = os.path.isfile(file_path)
            if exists:
                data = json.load(open(file_path))

                hours = len(data['hourly']['data'])
                if hours<24:
                    print(i, hours)

                temps = np.array([x['temperature'] for x in data['hourly']['data']])
                hums = np.array([x['humidity'] for x in data['hourly']['data']])
                winds = np.array([x['windSpeed'] for x in data['hourly']['data']])
                t[date].iloc[i] = np.mean(temps)
                h[date].iloc[i] = np.mean(hums)
                w[date].iloc[i] = np.mean(winds)

    t.to_csv(os.path.join(WEATHER_DIR, 'temperature.csv'), index=False)
    h.to_csv(os.path.join(WEATHER_DIR, 'humidity.csv'), index=False)
    w.to_csv(os.path.join(WEATHER_DIR, 'wind_speed.csv'), index=False)
    
    print(f'Weather data saved @ {WEATHER_DIR}')
