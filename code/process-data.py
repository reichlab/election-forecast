from urllib.request import urlopen
from zipfile import ZipFile
from zoltpy import util
from zoltpy.connection import ZoltarConnection
from datetime import date
from pprint import pprint
from constants import *
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
        FTE: upload_to_zoltar_fte
    }

    if is_local_host:
        conn = ZoltarConnection(LOCAL_HOST)
        conn.authenticate(LOCAL_USERNAME, LOCAL_PASSWORD)
        helpers[site_key](conn, proj_config)
    else:
        conn = util.authenticate()
        helpers[site_key](conn, proj_config)


def upload_to_zoltar_fte(conn, proj_config):
    project = [p for p in filter(lambda p: p.name == proj_config['name'], conn.projects)][0]
    existing_timezeros = {timezero.timezero_date for timezero in project.timezeros}

    # fte_pres_nat = pd.read_csv(DOWNLOAD_PATHS[FTE]['pres-nat'])
    # fte_pres_state = pd.read_csv(DOWNLOAD_PATHS[FTE]['pres-state'])
    #
    # # calculate Dem share in two-party popular vote
    # # Dem share in two-party popular vote = (avg Dem share / (avg Dem share + avg Rep share)) * 100
    # # (multiplied by 100 for percentage)
    # # (subject to revision?)
    # fte_pres_nat['voteshare_dem_twoparty'] = \
    #     (fte_pres_nat['national_voteshare_chal'] / (fte_pres_nat['national_voteshare_inc'] +
    #                                                 fte_pres_nat['national_voteshare_chal'])) * 100
    #
    # fte_pres_state['voteshare_dem_twoparty'] = \
    #     (fte_pres_state['voteshare_chal'] / (fte_pres_state['voteshare_inc'] +
    #                                          fte_pres_state['voteshare_chal'])) * 100
    #
    # forecasts_by_timezero = {}
    # jobs = []
    #
    # # Presidential, national
    # for i in range(len(fte_pres_nat)):
    #     row = fte_pres_nat.iloc[i]
    #
    #     month, day, year = row.at['modeldate'].split('/')
    #     forecast = check_and_make_timezero(year, month, day, project, existing_timezeros, forecasts_by_timezero)
    #
    #     # each row in raw 538 csv has multiple targets for us
    #     for target in proj_config['targets']:
    #         target_name = target['name']
    #         if target_name == 'popvote_win_dem':
    #             forecast['predictions'].append({
    #                 'unit': 'US-pres',
    #                 'target': target_name,
    #                 'class': 'bin',
    #                 'prediction': {
    #                     'cat': [True, False],
    #                     'prob': list(row.loc[['popwin_chal', 'popwin_inc']])
    #                 }
    #             })
    #         elif target_name == 'ec_win_dem':
    #             forecast['predictions'].append({
    #                 'unit': 'US-pres',
    #                 'target': target_name,
    #                 'class': 'bin',
    #                 'prediction': {
    #                     'cat': ['Dem win', 'Rep win', 'tie'],
    #                     'prob': list(row.loc[['ecwin_chal', 'ecwin_inc', 'ec_nomajority']])
    #                 }
    #             })
    #         elif target_name == 'ev_won_dem':
    #             forecast['predictions'].extend([
    #                 {
    #                     'unit': 'US-pres',
    #                     'target': target_name,
    #                     'class': 'point',
    #                     'prediction': {
    #                         'value': row.at['ev_chal']
    #                     }
    #                 },
    #                 {
    #                     'unit': 'US-pres',
    #                     'target': target_name,
    #                     'class': 'quantile',
    #                     'prediction': {
    #                         'quantile': [0.1, 0.9],
    #                         'value': list(row.loc[['ev_chal_lo', 'ev_chal_hi']].astype('float64'))
    #                     }
    #                 }
    #             ])
    #         elif target_name == 'voteshare_dem_twoparty':
    #             forecast['predictions'].extend([
    #                 {
    #                     'unit': 'US-pres',
    #                     'target': target_name,
    #                     'class': 'point',
    #                     'prediction': {
    #                         'value': row.at['voteshare_dem_twoparty']
    #                     }
    #                 }
    #             ])
    #
    # # Presidential, state-level
    # for i in range(len(fte_pres_state)):
    #     row = fte_pres_state.iloc[i]
    #
    #     month, day, year = row.at['modeldate'].split('/')
    #     forecast = check_and_make_timezero(year, month, day, project, existing_timezeros, forecasts_by_timezero)
    #
    #     for target in proj_config['targets']:
    #         target_name = target['name']
    #         if target_name == 'popvote_win_dem':
    #             forecast['predictions'].append({
    #                 'unit': f'{LOCATION_CODES_REVERSE[row.at["state"]]}-pres',
    #                 'target': target_name,
    #                 'class': 'bin',
    #                 'prediction': {
    #                     'cat': [True, False],
    #                     'prob': list(row.loc[['winstate_chal', 'winstate_inc']])
    #                 }
    #             })
    #
    #         elif target_name == 'voteshare_dem_twoparty':
    #             forecast['predictions'].append({
    #                 'unit': f'{LOCATION_CODES_REVERSE[row.at["state"]]}-pres',
    #                 'target': target_name,
    #                 'class': 'point',
    #                 'prediction': {
    #                     'value': row.at['voteshare_dem_twoparty']
    #                 }
    #             })
    #
    # # 538_pp model ends here, senatorial forecasts are done by 3 different models
    # for timezero in forecasts_by_timezero:
    #     util.upload_forecast(
    #         conn=conn,
    #         json_io_dict=forecasts_by_timezero[timezero],
    #         forecast_filename='538-agg.csv',
    #         project_name=proj_config['name'],
    #         model_abbr='538_pp',
    #         timezero_date=timezero.isoformat(),
    #         overwrite=True
    #     )

    fte_senate_nat = pd.read_csv(DOWNLOAD_PATHS[FTE]['senate-nat'])
    fte_senate_state = pd.read_csv(DOWNLOAD_PATHS[FTE]['senate-state'])

    total_dem_voteshare = fte_senate_state.loc[:, ['voteshare_mean_D1', 'voteshare_mean_D2',
                                                   'voteshare_mean_D3', 'voteshare_mean_D4']].sum(axis=1)
    total_rep_voteshare = fte_senate_state.loc[:, ['voteshare_mean_R1', 'voteshare_mean_R2',
                                                   'voteshare_mean_R3', 'voteshare_mean_R4']].sum(axis=1)

    fte_senate_state['voteshare_dem_twoparty'] = total_dem_voteshare / (total_dem_voteshare + total_rep_voteshare)

    forecasts_by_timezero = {'_lite': {}, '_classic': {}, '_deluxe': {}}

    # Senate, national
    for i in range(len(fte_senate_nat)):
        row = fte_senate_nat.iloc[i]
        model = row.at['expression']

        month, day, year = row.at['forecastdate'].split('/')
        forecast = check_and_make_timezero('20' + year, month, day, project, existing_timezeros,
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
    for i in range(len(fte_senate_state)):
        row = fte_senate_state.iloc[i]
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
        forecast = check_and_make_timezero('20' + year, month, day, project, existing_timezeros,
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


# TODO: refactor this into two functions
def check_and_make_timezero(year, month, day, project, existing_timezeros, forecasts, model=None):
    timezero = date(int(year), int(month), int(day))
    if timezero not in existing_timezeros:
        project.create_timezero(timezero.isoformat())
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


# download_all()
upload_to_zoltar(FTE, is_local_host=False)
