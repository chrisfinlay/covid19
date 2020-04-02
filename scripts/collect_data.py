from bs4 import BeautifulSoup
from tqdm import tqdm
import datetime as dt
import pandas as pd
import requests
import json
import os

########### Global Variables ###################################################

COVID_DIR = os.path.split(os.path.split(os.path.join(os.getcwd(), __file__))[0])[0]

DATA_DIR = os.path.join(COVID_DIR, 'data')

CONFIRMED_CSV = os.path.join(DATA_DIR, 'IRD/confirmed.csv')
RECOVERED_CSV = os.path.join(DATA_DIR, 'IRD/recovered.csv')
DEATHS_CSV = os.path.join(DATA_DIR, 'IRD/deaths.csv')

JH_DATA_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/' + \
              'master/csse_covid_19_data/csse_covid_19_time_series/'

CONFIRMED = JH_DATA_URL + 'time_series_covid19_confirmed_global.csv'
RECOVERED = JH_DATA_URL + 'time_series_covid19_recovered_global.csv'
DEATHS = JH_DATA_URL + 'time_series_covid19_deaths_global.csv'

API = 'https://api.darksky.net/forecast/'
API_KEY = open(os.path.join(COVID_DIR, 'API_KEY'), 'r').read().rstrip()

WOM_URL = 'https://www.worldometers.info/'
POPULATION = 'world-population/population-by-country/'
POPULATION_URL = os.path.join(WOM_URL, POPULATION)
POPULATION_RAW_CSV = os.path.join('population', 'populations_raw.csv')

TEST_URL = 'https://en.wikipedia.org/wiki/COVID-19_testing'

US_STATES = 'https://covidtracking.com/api/states/daily'
US_JSON = os.path.join(DATA_DIR, 'US_data/US_states.json')
US_CSV = os.path.join(DATA_DIR, 'US_data/US_states.csv')

################################################################################

def convert_date(date):

    date = dt.datetime.strptime(date, '%d %b')
    return f'{date.month}/{date.day}/20'

def IRD():

    files = [CONFIRMED_CSV, RECOVERED_CSV, DEATHS_CSV]
    urls = [CONFIRMED, RECOVERED, DEATHS]
    # Download and save data for each url
    for file, url in zip(files, urls):
        with open(file, 'w') as fp:
            fp.write(requests.get(url).text)
        # pd.read_csv(file).to_csv(file, index=False)
    fp = os.path.split(CONFIRMED_CSV)[0]
    print(f'Infection, Recovery and Death data saved @ {fp}')
    return fp

def weather():

    # Read in deaths data
    d = pd.read_csv(DEATHS_CSV)
    # Get latitudes and longitudes
    lats = d['Lat'].values
    lons = d['Long'].values
    # Drop unnecessary columns
    non_date_cols = ['Province/State', 'Country/Region', 'Lat', 'Long']
    deaths = d.drop(columns=non_date_cols).values
    # Get dates from DataFrame
    dates = d.drop(columns=non_date_cols).columns.values+'20'
    dates = [dt.datetime.strptime(date, '%m/%d/%Y') \
             .strftime('%Y-%m-%dT12:00:00') for date in dates]
    # Collect weather data for all locations and all days
    # Cleans up directory if limit was exceeded
    exceeded = False
    for i in tqdm(range(len(lats))):
        for date in dates:
            filename = f'{lats[i]:.6}_{lons[i]:.6}_{date}.json'
            file_path = os.path.join(DATA_DIR, 'weather/json', filename)
            exists = os.path.isfile(file_path)
            if exists:
                size = os.path.getsize(file_path)
                if size>100:
                    continue
                else:
                    os.remove(file_path)
            if exceeded:
                continue
            else:
                r = requests.get(os.path.join(API, API_KEY,
                                 f'{lats[i]:.6},{lons[i]:.6},{date}?units=si'))
                if '"code":403' in r.text:
                    exceeded = True
                    continue
                with open(file_path, 'w') as fp:
                    fp.write(r.text)

    fp = os.path.join(DATA_DIR, 'weather/json/')
    print(f'Weather data saved @ {fp}')
    return fp

def population():

    # Download webpage and grab table
    r = requests.get(POPULATION_URL)
    soup = BeautifulSoup(r.text, 'lxml') # Parse the HTML as a string
    html_table = soup.find_all('table')[0] # Grab the first table
    # Create DataFramewith columns and indices
    pop_cols = [x.text for x in html_table.find_all('tr')[0].find_all('th')]
    pop_index = range(len(html_table.find_all('tr'))-1)
    pops = pd.DataFrame(columns=pop_cols, index=pop_index)
    # Fill DataFrame with data
    for i, row in enumerate(html_table.find_all('tr')[1:]):
        columns = row.find_all('td')
        for j, column in enumerate(columns):
            pops.iat[i,j] = column.get_text()
    # Convert data to numeric
    pops['Population (2020)'] = pops['Population (2020)'] \
                                .apply(lambda x: int(''.join(x.split(','))))
    # Save data
    fp = os.path.join(DATA_DIR, POPULATION_RAW_CSV)
    pops.to_csv(fp, index=False)
    print(f'Population data saved @ {fp}')
    return fp

def testing():

    # Download webpage
    r = requests.get(TEST_URL)
    soup = BeautifulSoup(r.text, 'lxml') # Parse the HTML as a string
    # Find appropriate table
    N_t = None
    for i, table in enumerate(soup.find_all('table')):
        table_headings = [x.text for x in table.find_all('th') if
                          ('Tests\n' and 'Positive\n') in x.text]
        if len(table_headings)>0:
            N_t = i
    html_table = soup.find_all('table')[N_t]
    # Create DataFrame with columns and indices
    test_cols = [x.text.rstrip() for x in html_table.find_all('th')[1:7]]
    test_index = [x.text.rstrip()[1:] for x in html_table.find_all('th')[7:]]
    testing = pd.DataFrame(columns=test_cols, index=test_index)
    testing.index.name = 'Country/Region'
    # Fill DataFrame with data
    for i in range(len(testing)):
        row_data = html_table.find_all('tr')[i+1].find_all('td')
        testing.iloc[i] = [x.text.rstrip() for x in row_data]

    # Save data with today's date as data changes daily
    today = dt.datetime.now().strftime('%Y-%m-%d')
    fp = os.path.join(DATA_DIR, 'test_rate', f'test_rate_raw_{today}.csv')
    testing.to_csv(fp)
    print(f'Raw Testing data saved @ {fp}')
    return fp

def US():

    with open(US_JSON, 'w') as fp:
        fp.write(requests.get(US_STATES).text)

    data = json.load(open(US_JSON))
    states = []
    for i in range(len(data)):
        states.append(data[i]['state'])
    pd.DataFrame(data).to_csv(US_CSV)
    print(f'US state level data saved @ {US_CSV}')
    return US_CSV
