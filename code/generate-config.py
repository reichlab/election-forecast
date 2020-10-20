import json
from constants import *


def generate_preamble():
    # initialize config object
    config = dict()

    # fields
    config['name'] = '2020 Election Forecasts'
    config['is_public'] = False
    config['description'] = 'This project stores forecasts from multiple election forecast sites, ' + \
                            'including FiveThirtyEight and the Economist, for ease of access and comparison.'
    config['home_url'] = 'https://reichlab.io'
    config['logo_url'] = 'http://reichlab.io/assets/images/logo/nav-logo.png'
    config['core_data'] = 'https://zoltardata.com/'
    config['time_interval_type'] = 'Week'
    config['visualization_y_label'] = 'Votes/voteshare (percent)'

    return config


def generate_units():
    # generate unit strings from encoded location and election types
    units = []
    for location in LOCATION_CODES:
        for election in ELECTION_CODES:
            if election == 'sen' and location not in LOCATIONS_WITH_SENATE_ELECTION:
                continue
            units.append({'name': f'{location}-{election}'})

    # there is a special election for a Georgia senate seat this year
    units.append({'name': 'GA-sen-sp'})

    return units


def generate_config():
    with open(CONFIG_LOCAL_PATH, 'w') as f:
        config = generate_preamble()
        config['units'] = generate_units()
        config['targets'] = TARGETS
        config['timezeros'] = []

        f.write(json.dumps(config))
        f.close()


generate_config()
