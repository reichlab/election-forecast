from urllib.request import urlopen
from zipfile import ZipFile
from zoltpy import util
from zoltpy.connection import ZoltarConnection
from datetime import date
from constants import *
from pprint import pprint
import pandas as pd
import os
import json


def download_all():
    download(FTE)
    download(ECONOMIST)
    download(JHK)
    download(OURPROGRESS)
    download(LEANTOSSUP)


def download(site_key):
    print(f'Downloading from {site_key}...')

    # get urls and local file locations
    site_urls = URLS[site_key]
    site_download_paths = DOWNLOAD_PATHS[site_key]

    # for each url
    for key in site_urls:

        # construct a request
        with urlopen(site_urls[key]) as resp:
            with open(site_download_paths[key], 'wb') as file:
                file.write(resp.read())
                file.close()

    if site_key == 'economist':
        process_economist_zipped_files()

    print('done!')


def process_economist_zipped_files():
    zipped_filename = DOWNLOAD_PATHS[ECONOMIST]['all-zip']
    subpath = '/'.join(zipped_filename.split('/')[:-1]) + '/'

    with ZipFile(zipped_filename, 'r') as zipped:
        for member in zipped.namelist():
            filename_wo_path = member.split('/')[-1]
            with zipped.open(member, 'r') as input_file:
                with open(subpath + filename_wo_path, 'wb') as output_file:
                    output_file.write(input_file.read())
                    output_file.close()
                input_file.close()
        zipped.close()

    os.remove(zipped_filename)


def read_config(path):
    with open(path, 'r') as config_json:
        config = json.load(config_json)

    return config


def upload_to_zoltar(site_key, is_local_host=False):
    proj_config = read_config(CONFIG_LOCAL_PATH)

    helpers = {
        FTE: upload_to_zoltar_fte,
        ECONOMIST: upload_to_zoltar_economist
    }

    if is_local_host:
        conn = ZoltarConnection(LOCAL_HOST)
        conn.authenticate(LOCAL_USERNAME, LOCAL_PASSWORD)
        helpers[site_key](conn, proj_config)
    else:
        conn = util.authenticate()
        helpers[site_key](conn, proj_config)


def upload_to_zoltar_fte(conn, proj_config):
    project, existing_timezeros = get_project_and_timezeros(conn, proj_config)

    pres_nat = pd.read_csv(DOWNLOAD_PATHS[FTE]['pres-nat'])
    pres_state = pd.read_csv(DOWNLOAD_PATHS[FTE]['pres-state'])

    # calculate Dem share in two-party popular vote
    # Dem share in two-party popular vote = (avg Dem share / (avg Dem share + avg Rep share)) * 100
    # (multiplied by 100 for percentage)
    # (subject to revision?)
    pres_nat['voteshare_dem_twoparty'] = \
        (pres_nat['national_voteshare_chal'] / (pres_nat['national_voteshare_inc'] +
                                                pres_nat['national_voteshare_chal'])) * 100

    pres_state['voteshare_dem_twoparty'] = \
        (pres_state['voteshare_chal'] / (pres_state['voteshare_inc'] +
                                         pres_state['voteshare_chal'])) * 100

    forecasts_by_timezero = {}
    jobs = []

    # Presidential, national
    for i in range(len(pres_nat)):
        row = pres_nat.iloc[i]

        month, day, year = row.at['modeldate'].split('/')
        forecast = check_and_make_timezero_and_get_forecast_object(year, month, day, project,
                                                                   existing_timezeros, forecasts_by_timezero)

        # each row in raw 538 csv has multiple targets for us
        for target in proj_config['targets']:
            target_name = target['name']
            if target_name == 'popvote_win_dem':
                forecast['predictions'].append({
                    'unit': 'US-pres',
                    'target': target_name,
                    'class': 'bin',
                    'prediction': {
                        'cat': [True, False],
                        'prob': list(row.loc[['popwin_chal', 'popwin_inc']])
                    }
                })
            elif target_name == 'ec_win_dem':
                forecast['predictions'].append({
                    'unit': 'US-pres',
                    'target': target_name,
                    'class': 'bin',
                    'prediction': {
                        'cat': ['Dem win', 'Rep win', 'tie'],
                        'prob': list(row.loc[['ecwin_chal', 'ecwin_inc', 'ec_nomajority']])
                    }
                })
            elif target_name == 'ev_won_dem':
                forecast['predictions'].extend([
                    {
                        'unit': 'US-pres',
                        'target': target_name,
                        'class': 'point',
                        'prediction': {
                            'value': row.at['ev_chal']
                        }
                    },
                    {
                        'unit': 'US-pres',
                        'target': target_name,
                        'class': 'quantile',
                        'prediction': {
                            'quantile': [0.1, 0.9],
                            'value': list(row.loc[['ev_chal_lo', 'ev_chal_hi']].astype('float64'))
                        }
                    }
                ])
            elif target_name == 'voteshare_dem_twoparty':
                forecast['predictions'].extend([
                    {
                        'unit': 'US-pres',
                        'target': target_name,
                        'class': 'point',
                        'prediction': {
                            'value': row.at['voteshare_dem_twoparty']
                        }
                    }
                ])

    # Presidential, state-level
    for i in range(len(pres_state)):
        row = pres_state.iloc[i]

        month, day, year = row.at['modeldate'].split('/')
        forecast = check_and_make_timezero_and_get_forecast_object(year, month, day, project,
                                                                   existing_timezeros, forecasts_by_timezero)

        for target in proj_config['targets']:
            target_name = target['name']
            if target_name == 'popvote_win_dem':
                forecast['predictions'].append({
                    'unit': f'{LOCATION_CODES_REVERSE[row.at["state"]]}-pres',
                    'target': target_name,
                    'class': 'bin',
                    'prediction': {
                        'cat': [True, False],
                        'prob': list(row.loc[['winstate_chal', 'winstate_inc']])
                    }
                })

            elif target_name == 'voteshare_dem_twoparty':
                forecast['predictions'].append({
                    'unit': f'{LOCATION_CODES_REVERSE[row.at["state"]]}-pres',
                    'target': target_name,
                    'class': 'point',
                    'prediction': {
                        'value': row.at['voteshare_dem_twoparty']
                    }
                })

    # 538_pp model ends here, senatorial forecasts are done by 3 different models
    for timezero in forecasts_by_timezero:
        util.upload_forecast(
            conn=conn,
            json_io_dict=forecasts_by_timezero[timezero],
            forecast_filename='538-agg.csv',
            project_name=proj_config['name'],
            model_abbr='538_pp',
            timezero_date=timezero.isoformat(),
            overwrite=True
        )

    # senatorial elections
    senate_nat = pd.read_csv(DOWNLOAD_PATHS[FTE]['senate-nat'])
    senate_state = pd.read_csv(DOWNLOAD_PATHS[FTE]['senate-state'])

    total_dem_voteshare = senate_state.loc[:, ['voteshare_mean_D1', 'voteshare_mean_D2',
                                                   'voteshare_mean_D3', 'voteshare_mean_D4']].sum(axis=1)
    total_rep_voteshare = senate_state.loc[:, ['voteshare_mean_R1', 'voteshare_mean_R2',
                                                   'voteshare_mean_R3', 'voteshare_mean_R4']].sum(axis=1)

    senate_state['voteshare_dem_twoparty'] = total_dem_voteshare / (total_dem_voteshare + total_rep_voteshare)

    forecasts_by_timezero = {'_lite': {}, '_classic': {}, '_deluxe': {}}

    # Senate, national
    for i in range(len(senate_nat)):
        row = senate_nat.iloc[i]
        model = row.at['expression']

        month, day, year = row.at['forecastdate'].split('/')
        forecast = check_and_make_timezero_and_get_forecast_object('20' + year, month, day, project, existing_timezeros,
                                                                   forecasts_by_timezero, model=model)

        forecast['predictions'].extend([
            {
                'unit': 'US-sen',
                'target': 'senate_win_dem',
                'class': 'bin',
                'prediction': {
                    'cat': [True, False],
                    'prob': list(row.loc[['chamber_Dparty', 'chamber_Rparty']])
                }
            },
            {
                'unit': 'US-sen',
                'target': 'senate_seats_won_dem',
                'class': 'quantile',
                'prediction': {
                    'quantile': [0.1, 0.5, 0.9],
                    'value': list(row.loc[['p10_seats_Dparty',
                                           'median_seats_Dparty',
                                           'p90_seats_Dparty'
                                           ]].astype('int32'))
                }
            }
        ])

    # Senate, state-level
    for i in range(len(senate_state)):
        row = senate_state.iloc[i]
        model = row.at['expression']
        seat = row.at['district'].split('-')
        if seat[0] == 'GA':
            if seat[1] == 'S3':
                unit = 'GA-sen-sp'
            else:
                unit = 'GA-sen'
        else:
            unit = f'{seat[0]}-sen'

        month, day, year = row.at['forecastdate'].split('/')
        forecast = check_and_make_timezero_and_get_forecast_object('20' + year, month, day, project, existing_timezeros,
                                                                   forecasts_by_timezero, model=model)

        forecast['predictions'].extend([
            {
                'unit': unit,
                'target': 'popvote_win_dem',
                'class': 'bin',
                'prediction': {
                    'cat': [True, False],
                    'prob': list(row.loc[['winner_Dparty', 'winner_Rparty']])
                }
            },
            {
                'unit': unit,
                'target': 'voteshare_dem_twoparty',
                'class': 'point',
                'prediction': {
                    'value': row.at['voteshare_dem_twoparty']
                }
            }
        ])

    for model in forecasts_by_timezero:
        for timezero in forecasts_by_timezero[model]:
            util.upload_forecast(
                conn=conn,
                json_io_dict=forecasts_by_timezero[model][timezero],
                forecast_filename='538-agg.csv',
                project_name=proj_config['name'],
                model_abbr=f'538{model}',
                timezero_date=timezero.isoformat(),
                overwrite=True
            )


def upload_to_zoltar_economist(conn, proj_config):
    project, existing_timezeros = get_project_and_timezeros(conn, proj_config)

    ec_sims = pd.read_csv(f'{DOWNLOAD_PATHS[ECONOMIST]["root"]}electoral_college_simulations.csv')
    ec_prob = pd.read_csv(f'{DOWNLOAD_PATHS[ECONOMIST]["root"]}electoral_college_probability_over_time.csv')
    ec_votes = pd.read_csv(f'{DOWNLOAD_PATHS[ECONOMIST]["root"]}electoral_college_votes_over_time.csv')
    pres_nat = pd.read_csv(f'{DOWNLOAD_PATHS[ECONOMIST]["root"]}projected_eday_vote_over_time.csv')
    pres_nat_topline = pd.read_csv(f'{DOWNLOAD_PATHS[ECONOMIST]["root"]}national_ec_popvote_topline.csv')
    pres_state_topline = pd.read_csv(f'{DOWNLOAD_PATHS[ECONOMIST]["root"]}state_averages_and_predictions_topline.csv')

    for year, month, day in map(
        lambda date_str: date_str.split('-'),
        pres_nat['model_run_date']
    ):
        check_and_make_timezero(year, month, day, project, existing_timezeros)

    with open(f'{DOWNLOAD_PATHS[ECONOMIST]["root"]}timestamp.json', 'rb') as timestamp_file:
        model_most_recent_date = date.fromtimestamp(json.load(timestamp_file)['timestamp'])
        timestamp_file.close()

    forecasts = {}

    # process electoral college simulations
    # 1. sample 1000 out of 40000 simulations provided
    # 2. convert to Zoltar format
    # 3. save for upload
    ec_sims_sampled_1000 = ec_sims.sample(n=1000, random_state=SEED)
    forecast = get_forecast_object_of_timezero(model_most_recent_date, forecasts)
    ec_win_dem_samples, ev_won_dem_samples, popvote_win_dem_samples, voteshare_dem_twoparty_samples = [], [], [], []

    state_list = list(LOCATION_CODES.keys())[1:52]
    state_won_dem_samples, state_voteshare_samples = {k: [] for k in state_list}, {k: [] for k in state_list}
    for sample in ec_sims_sampled_1000.itertuples(name='Sample'):
        dem_ev = int(sample.dem_ev)
        if dem_ev > 270:
            ec_result = 'Dem win'
        elif dem_ev < 270:
            ec_result = 'Rep win'
        else:  # dev_ev == 270
            ec_result = 'tie'

        # extremely unlikely to be exactly 0.5 due to floating point value (and reality)
        voteshare_dem_twoparty = sample.natl_pop_vote
        popvote_win_dem = False if voteshare_dem_twoparty < 0.5 else True

        ec_win_dem_samples.append(ec_result)
        ev_won_dem_samples.append(dem_ev)
        popvote_win_dem_samples.append(popvote_win_dem)
        voteshare_dem_twoparty_samples.append(voteshare_dem_twoparty)

        # get the state popular voteshares
        state_list = list(LOCATION_CODES.keys())[1:52]
        for state, state_voteshare in zip(state_list, sample[4:]):
            state_won_dem = False if state_voteshare < 0.5 else True
            state_won_dem_samples[state].append(state_won_dem)
            state_voteshare_samples[state].append(state_voteshare)

    # converting to Zoltar format
    forecast['predictions'].extend([
        {
            'unit': 'US-pres',
            'target': 'ec_win_dem',
            'class': 'sample',
            'prediction': {
                'sample': ec_win_dem_samples
            }
        },
        {
            'unit': 'US-pres',
            'target': 'ev_won_dem',
            'class': 'sample',
            'prediction': {
                'sample': ev_won_dem_samples
            }
        },
        {
            'unit': 'US-pres',
            'target': 'popvote_win_dem',
            'class': 'sample',
            'prediction': {
                'sample': popvote_win_dem_samples
            }
        },
        {
            'unit': 'US-pres',
            'target': 'voteshare_dem_twoparty',
            'class': 'sample',
            'prediction': {
                'sample': voteshare_dem_twoparty_samples
            }
        },
    ])

    for state in state_list:
        forecast['predictions'].extend([
            {
                'unit': f'{state}-pres',
                'target': 'popvote_win_dem',
                'class': 'sample',
                'prediction': {
                    'sample': state_won_dem_samples[state]
                }
            },
            {
                'unit': f'{state}-pres',
                'target': 'voteshare_dem_twoparty',
                'class': 'sample',
                'prediction': {
                    'sample': state_voteshare_samples[state]
                }
            }
        ])

    # process electoral college win probabilities over time
    ec_prob_dem = ec_prob[ec_prob['party'] == 'Democratic']
    ec_prob_rep = ec_prob[ec_prob['party'] == 'Republican']
    for row_dem, row_rep in zip(ec_prob_dem.itertuples(name='Row'), ec_prob_rep.itertuples(name='Row')):
        year, month, day = row_dem.date.split('-')
        timezero = date(int(year), int(month), int(day))
        forecast = get_forecast_object_of_timezero(timezero, forecasts)
        tie_prob = 1 - row_dem.win_prob - row_rep.win_prob

        forecast['predictions'].append({
            'unit': 'US-pres',
            'target': 'ec_win_dem',
            'class': 'bin',
            'prediction': {
                'cat': ['Dem win', 'Rep win', 'tie'],
                'prob': [row_dem.win_prob, row_rep.win_prob, tie_prob]
            }
        })

    # process electoral college votes over time
    ec_votes_dem = ec_votes[ec_votes['party'] == 'Democratic']
    for row in ec_votes_dem.itertuples(name='Row'):
        year, month, day = row.date.split('-')
        timezero = date(int(year), int(month), int(day))
        forecast = get_forecast_object_of_timezero(timezero, forecasts)

        forecast['predictions'].append({
            'unit': 'US-pres',
            'target': 'ev_won_dem',
            'class': 'quantile',
            'prediction': {
                'quantile': [0.05, 0.4, 0.5, 0.6, 0.95],
                'value': [float(ev) for ev in row[2:]]
            }
        })

    # process national popular voteshare over time
    for row in pres_nat.itertuples(name='Row'):
        year, month, day = row.model_run_date.split('-')
        timezero = date(int(year), int(month), int(day))
        forecast = get_forecast_object_of_timezero(timezero, forecasts)

        forecast['predictions'].extend([
            {
                'unit': 'US-pres',
                'target': 'voteshare_dem_twoparty',
                'class': 'quantile',
                'prediction': {
                    'quantile': [0.05, 0.5, 0.95],
                    'value': [row.lower_95_dem_vote, row.mean_dem_vote, row.upper_95_dem_vote]
                }
            },
        ])

    # process national popular vote topline (for popular vote win probability)
    for row in pres_nat_topline.itertuples(name='Row'):
        year, month, day = row.date.split('-')
        timezero = date(int(year), int(month), int(day))
        forecast = get_forecast_object_of_timezero(timezero, forecasts)

        forecast['predictions'].append({
            'unit': 'US-pres',
            'target': 'popvote_win_dem',
            'class': 'bin',
            'prediction': {
                'cat': [True, False],
                'prob': [row.dem_vote_win_prob, row.rep_vote_win_prob]
            }
        })

    # process state popular vote topline:
    for row in pres_state_topline.itertuples(name='Row'):
        year, month, day = row.date.split('-')
        timezero = date(int(year), int(month), int(day))
        forecast = get_forecast_object_of_timezero(timezero, forecasts)

        forecast['predictions'].extend([
            {
                'unit': f'{row.state}-pres',
                'target': 'popvote_win_dem',
                'class': 'bin',
                'prediction': {
                    'cat': [True, False],
                    'prob': [row.projected_win_prob, 1 - row.projected_win_prob]
                }
            },
            {
                'unit': f'{row.state}-pres',
                'target': 'voteshare_dem_twoparty',
                'class': 'quantile',
                'prediction': {
                    'quantile': [0.05, 0.5, 0.95],
                    'value': [row.projected_vote_low, row.projected_vote_mean, row.projected_vote_high]
                }
            }
        ])

    # upload to Zoltar
    for timezero in forecasts:
        util.upload_forecast(
            conn=conn,
            json_io_dict=forecasts[timezero],
            forecast_filename='economist-agg.csv',
            project_name=proj_config['name'],
            model_abbr='economist',
            timezero_date=timezero.isoformat(),
            overwrite=True
        )


def upload_to_zoltar_jhk(conn, proj_config):
    pres = pd.read_csv(f'{DOWNLOAD_PATHS[JHK]["root"]}pres.csv')
    senate = pd.read_csv(f'{DOWNLOAD_PATHS[JHK]["root"]}senate.csv')

    replace_dict = {
        'Nebraska CD-1': 'NE-1',
        'Nebraska CD-2': 'NE-2',
        'Nebraska CD-3': 'NE-3',
        'Maine CD-1': 'ME-1',
        'Maine CD-2': 'ME-2'
    }

    pres.replace(to_replace=replace_dict, inplace=True)

    pres_dem = pres[pres['party'] == 'DEM']
    pres_rep = pres[pres['party'] == 'REP']

    print(pres)




def upload_to_zoltar_ourprogress(conn, proj_config):
    pass


def upload_to_zoltar_leantossup(conn, proj_config):
    pass


def get_project_and_timezeros(conn, proj_config):
    project = [p for p in filter(lambda p: p.name == proj_config['name'], conn.projects)][0]
    timezeros = {timezero.timezero_date for timezero in project.timezeros}

    return project, timezeros


def check_and_make_timezero_and_get_forecast_object(
        year, month, day,
        project, existing_timezeros, forecasts, model=None
):
    timezero = check_and_make_timezero(year, month, day, project, existing_timezeros)
    return get_forecast_object_of_timezero(timezero, forecasts, model)


def check_and_make_timezero(year, month, day, project, existing_timezeros):
    timezero = date(int(year), int(month), int(day))
    if timezero not in existing_timezeros:
        project.create_timezero(timezero.isoformat())

    return timezero


def get_forecast_object_of_timezero(timezero, forecasts, model=None):
    if model:
        if timezero not in forecasts[model]:
            forecast = {'meta': {}, 'predictions': []}
            forecasts[model][timezero] = forecast
        else:
            forecast = forecasts[model][timezero]
    else:
        if timezero not in forecasts:
            forecast = {'meta': {}, 'predictions': []}
            forecasts[timezero] = forecast
        else:
            forecast = forecasts[timezero]

    return forecast


def main(download_files=False):
    if download_files:
        download_all()
    # upload_to_zoltar(FTE, is_local_host=False)
    # upload_to_zoltar(ECONOMIST, is_local_host=False)
    upload_to_zoltar(JHK, is_local_host=True)



main(download_files=False)
