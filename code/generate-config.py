import json
from itertools import product

# TODO: make this into a CLI app using click

LOCATION_CODES = {
    'US': 'US National',
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
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
    'WY': 'Wyoming'
}

ELECTION_CODES = {
    'pres': 'Presidential',
    'sen': 'Senate',
}

TARGETS = [
    {
        'name': 'popular vote win for Democrats',
        'type': 'binary'
    },
    {
        'name': 'Electoral College win for Democrats',
        'type': 'binary'
    },
    {
        'name': 'electoral votes won by Democrats',
        'type': 'discrete',
        'is_step_ahead': False,
        'unit': 'votes',
        'range': [0, 538]
    },
    {
        'name': 'Share of two-party (D/R) popular vote for Democrats',
        'type': 'continuous',
        'is_step_ahead': False,
        'unit': 'percent',
        'range': [0, 100]
    }
]

CONFIG_LOCAL_PATH = 'code/Election_Forecasts-config.json'


def generate_units():
    units = list(map(lambda x: f'{x[0]}-{x[1]}', product(LOCATION_CODES.keys(), ELECTION_CODES.keys())))

    # there is a special election for a Georgia senate seat this year
    units.append('GA-sen-sp')
    return units


def generate_targets():
    return json.JSONEncoder().encode(TARGETS)


def read_config():
    with open(CONFIG_LOCAL_PATH, 'r') as f:
        config = json.loads(f.read())
        config['units'] = generate_units()
        print(json.dumps(config['units']))

    return "unimplemented"


read_config()
