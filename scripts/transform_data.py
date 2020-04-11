from tqdm import tqdm
import datetime as dt
import pandas as pd
import numpy as np
import json
import os

pd.options.mode.chained_assignment = None

########### Global Variables ###################################################

COVID_DIR = os.path.split(os.path.split(os.path.join(os.getcwd(), __file__))[0])[0]

DATA_DIR = os.path.join(COVID_DIR, 'data')

CONFIRMED_CSV = os.path.join(DATA_DIR, 'IRD/confirmed.csv')
RECOVERED_CSV = os.path.join(DATA_DIR, 'IRD/recovered.csv')
DEATHS_CSV = os.path.join(DATA_DIR, 'IRD/deaths.csv')

WEATHER_DIR = os.path.join(DATA_DIR, 'weather')

POPULATION_RAW_CSV = os.path.join('population', 'populations_raw.csv')
POPULATION_CSV = os.path.join('population', 'populations.csv')

################################################################################

def convert_date(date):

    date = dt.datetime.strptime(date, '%d %b')
    return f'{date.month}/{date.day}/20'

def initial_processing(df, threshold):

    for c in ['China', 'Diamond Princess']:
        if c in df.values:
            df.drop(index=df[c==df.values].index, inplace=True)

    df['Country/Region'].iloc[~df['Province/State'].isnull().values] += ' / '+df['Province/State']
    df.drop(columns=['Province/State', 'Lat', 'Long'], inplace=True)
    df.set_index(keys='Country/Region', inplace=True)
    df.drop(index=df[threshold>df.T.max()].index, inplace=True)

def intersect_dfs(dfs):
    keep = set(dfs[0].index)
    for i in dfs[1:]:
        keep = keep.intersection(set(i.index))

    for df in dfs:
        df.drop(index=set(df.index)-keep, inplace=True)

    return keep

def IRD(min_confirmed=100, min_recovered=10, min_deaths=5):

    IRD_df = [pd.read_csv(filename) for filename in
              [CONFIRMED_CSV, RECOVERED_CSV, DEATHS_CSV]]

    # Drop China, Iran, Italy and Diamond Princess
    # Drop data not meeting a minimum
    thresholds = [min_confirmed, min_recovered, min_deaths]
    for df, threshold in zip(IRD_df, thresholds):
        initial_processing(df, threshold)
    # Now we take the intersection of these DataFrames
    intersect_dfs(IRD_df)
    return IRD_df

def weather(update=True):

    if update:
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
                file_path = os.path.join(WEATHER_DIR, 'json',filename)
                date = dt.datetime.strptime(date, '%Y-%m-%dT12:00:00')
                date = f'{date.month}/{date.day}/20'
                exists = os.path.isfile(file_path)
                if exists:
                    data = json.load(open(file_path))

                    hours = len(data['hourly']['data'])
                    if hours<8:
                        print(filename, hours)

                    temps = np.array([x['temperature'] for x in data['hourly']['data']])
                    hums = 100*np.array([x['humidity'] for x in data['hourly']['data']])
                    winds = np.array([x['windSpeed'] for x in data['hourly']['data']])
                    t[date].iloc[i] = np.mean(temps)
                    h[date].iloc[i] = np.mean(hums)
                    w[date].iloc[i] = np.mean(winds)

        t.to_csv(os.path.join(WEATHER_DIR, 'temperature.csv'), index=False)
        h.to_csv(os.path.join(WEATHER_DIR, 'humidity.csv'), index=False)
        w.to_csv(os.path.join(WEATHER_DIR, 'wind_speed.csv'), index=False)

        print(f'Weather data saved @ {WEATHER_DIR}')
    else:
        t = pd.read_csv(os.path.join(WEATHER_DIR, 'temperature.csv'))
        h = pd.read_csv(os.path.join(WEATHER_DIR, 'humidity.csv'))
        w = pd.read_csv(os.path.join(WEATHER_DIR, 'wind_speed.csv'))
    # Drop China, Iran, Italy and Diamond Princess
    # Drop data not meeting a minimum
    min_temp, min_humid, min_wind = -50.0, 0.0, 0.0
    THW = [t, h, w]
    thresholds = [min_temp, min_humid, min_wind]
    for df, threshold in zip(THW, thresholds):
        initial_processing(df, threshold)
    return THW

def population():

    c_df = pd.read_csv(CONFIRMED_CSV)
    initial_processing(c_df, -1)
    pops = pd.read_csv(os.path.join(DATA_DIR, POPULATION_RAW_CSV)) \
                        .set_index('Country (or dependency)').drop('#', axis=1)

    populations = {}
    populations['Australia / New South Wales'] = 8117976
    populations['Australia / Queensland'] = 5115451
    populations['Australia / South Australia'] = 1756494
    populations['Australia / Victoria'] = 6629870
    populations['Australia / Western Australia'] = 2630557
    populations['Denmark / Faroe Islands'] = 51783
    populations['France / Guadeloupe'] = 395700
    populations['France / Reunion'] = 859959
    populations['United Kingdom / Channel Islands'] = 170499
    populations['West Bank and Gaza'] = 3340143
    popula_df_c = ['Brunei', 'Czechia', "Cote d'Ivoire", 'Korea, South',
                   'Taiwan*', 'US', 'Burma']
    corona_df_c = ['Brunei ', 'Czech Republic (Czechia)', "Côte d'Ivoire",
                   'South Korea', 'Taiwan', 'United States', 'Myanmar']
    for c_p, c_c in zip(popula_df_c, corona_df_c):
        populations[c_p] = pops.T[c_c]['Population (2020)']
    # Check for unmatched regions
    unmatched = []
    for c in c_df.index.values:
        if c not in pops.index.values:
            unmatched.append(c)
        else:
            populations[c] = pops.T[c].values[0]

    unmatched = set(unmatched) - set(populations.keys())
    print(f'Number of unmatched regions : {len(unmatched)}')

    fp = os.path.join(DATA_DIR, POPULATION_CSV)
    popula = pd.DataFrame(populations, index=['Population'])
    popula.to_csv(fp, index=False)
    print(f'Population data saved @ {fp}')
    return popula

def testing():

    today = dt.datetime.now().strftime('%Y-%m-%d')
    fp = os.path.join(DATA_DIR, 'test_rate', f'test_rate_raw_{today}.csv')
    test = pd.read_csv(fp, index_col='Country/Region')

    # Drop Countries with bad data or sub-regions
    # test.drop(['China:  Guangdong', 'Kazakhstan', 'Palestine'], inplace=True)
    test.drop([x for x in test.index if ':' in x], inplace=True)
    # Convert data to numeric and calculate test rate
    test['Tests'] = test['Tests'].apply(lambda x: int(str(x).replace('*', '') \
                                  .replace(',', '').replace('.', '')))
    test['Positive'] = test['Positive'].apply(lambda x: int(str(x).replace('*', '') \
                                  .replace(',', '').replace('.', '')))
    test['Test Rate'] = test['Tests\u2009/millionpeople'] \
                           .apply(lambda x: float(str(x).replace('*', '') \
                                                  .replace(',', '').replace('.', ''))/1.0e6)
    test['Positive Rate'] = test['Positive /thousandtests'] \
                               .apply(lambda x: float(str(x).replace('*', '') \
                                                      .replace(',', '').replace('.', ''))/1.0e3)
    # Convert date to match John's Hopkins Data
    test['As of'] = test['As of'].apply(convert_date)
    # Drop Unneeded columns
    unneeded_cols = ['Tests\u2009/millionpeople',
                     'Positive\u2009/thousandtests', 'Ref.']
    test.drop(unneeded_cols, axis=1, inplace=True)

    fp = os.path.join(DATA_DIR, 'test_rate', f'test_rate_{today}.csv')
    test.to_csv(fp)

    return test
