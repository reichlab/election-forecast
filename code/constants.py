LOCATION_CODES = {
    'US': 'US National',
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
    'NE-1': 'NE-1',
    'NE-2': 'NE-2',
    'NE-3': 'NE-3',
    'ME-1': 'ME-1',
    'ME-2': 'ME-2',

}

LOCATION_CODES_REVERSE = {v: k for k, v in LOCATION_CODES.items()}


ELECTION_CODES = {
    'pres': 'Presidential',
    'sen': 'Senate',
}

LOCATIONS_WITH_SENATE_ELECTION = {
    'IA', 'ME', 'GA', 'NC', 'MT', 'KS', 'SC', 'GA', 'AZ', 'AL', 'MI', 'CO', 'AK', 'TN', 'IL', 'WY', 'RI', 'AR',
    'TX', 'MS', 'MN', 'KY', 'NM', 'LA', 'NH', 'VA', 'OR', 'OK', 'NJ', 'ID', 'WV', 'SD', 'DE', 'NE', 'MA', 'US'
}

TARGETS = [
    {
        'name': 'popvote_win_dem',
        'type': 'binary',
        'is_step_ahead': False,
        'description': 'popular vote win for Democrats'
    },
    {
        'name': 'ec_win_dem',
        'type': 'nominal',
        'cats': ['Dem win', 'Rep win', 'tie'],
        'is_step_ahead': False,
        'description': 'Electoral College win for Democrats'
    },
    {
        'name': 'ev_won_dem',
        'type': 'continuous',
        'unit': 'votes',
        'range': [0, 538],
        'is_step_ahead': False,
        'description': 'number of electoral votes won by Democrats',
    },
    {
        'name': 'voteshare_dem_twoparty',
        'type': 'continuous',
        'unit': 'percent',
        'range': [0, 100],
        'is_step_ahead': False,
        'description': 'Share of two-party (D/R) popular vote for Democrats'
    },
    {
        'name': 'senate_seats_won_dem',
        'type': 'discrete',
        'unit': 'seats',
        'range': [0, 100],
        'is_step_ahead': False,
        'description': 'Number of Senate seats won by Democrats'
    },
    {
        'name': 'senate_win_dem',
        'type': 'binary',
        'is_step_ahead': False,
        'description': 'Senate win (control) for Democrats'
    }
]

CONFIG_LOCAL_PATH = 'Election_Forecasts-config.json'
PROJECT_NAME = '2020 Election Forecasts'
LOCAL_HOST = 'http://localhost:8000'
LOCAL_USERNAME = 'yuxin'
LOCAL_PASSWORD = 'Pacman^3=216'

FTE = '538'
ECONOMIST = 'economist'
JHK = 'jhk'
OURPROGRESS = 'ourprogress'
LEANTOSSUP = 'leantossup'
SITE_KEYS = [FTE, ECONOMIST, JHK, OURPROGRESS, LEANTOSSUP]

URLS = {
    FTE: {
        'pres-nat': 'https://projects.fivethirtyeight.com/2020-general-data/presidential_national_toplines_2020.csv',
        'pres-state': 'https://projects.fivethirtyeight.com/2020-general-data/presidential_state_toplines_2020.csv',
        'senate-nat': 'https://projects.fivethirtyeight.com/2020-general-data/senate_national_toplines_2020.csv',
        'senate-state': 'https://projects.fivethirtyeight.com/2020-general-data/senate_state_toplines_2020.csv'
    },
    ECONOMIST: {
        'all-zip': 'https://cdn.economistdatateam.com/us-2020-forecast/data/president/economist_model_output.zip',
    },
    JHK: {
        'pres': 'https://data.jhkforecasts.com/2020-presidential.csv',
        'senate': 'https://data.jhkforecasts.com/2020-senate.csv'
    },
    OURPROGRESS: {
        'pres': 'https://becd085d-5f24-4974-b9b5-73518197155a.filesusr.com/ugd' +
                '/83fab9_eaf58f194c8f4b129f30625179a7a789.csv?dn=Winning%20Odds%20-%20Winning%20Odds%20(3).csv',
    },
    LEANTOSSUP: {
        'pres': 'http://www.leantossup.ca/US_Pres_2020/US_2020_Results.xlsx',
        'pres-sims': 'http://www.leantossup.ca/US_Pres_2020/US_State_Results.xlsx'
    }
}

DOWNLOAD_PATHS = {
    FTE: {
        'pres-nat': 'data/538/pres-nat.csv',
        'pres-state': 'data/538/pres-state.csv',
        'senate-nat': 'data/538/senate-nat.csv',
        'senate-state': 'data/538/senate-state.csv'
    },
    ECONOMIST: {
        'all-zip': 'data/economist/all.zip',
    },
    JHK: {
        'pres': 'data/jhk/pres.csv',
        'senate': 'data/jhk/senate.csv'
    },
    OURPROGRESS: {
        'pres': 'data/ourprogress/pres.csv',
    },
    LEANTOSSUP: {
        'pres': 'data/leantossup/pres.xlsx',
        'pres-sims': 'data/leantossup/pres-sims.xlsx'
    }
}
