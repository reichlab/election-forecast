from urllib.request import urlopen
from zipfile import ZipFile

FTE = '538'
ECONOMIST = 'economist'
JHK = 'jhk'
OURPROGRESS = 'ourprogress'
LEANTOSSUP = 'leantossup'

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


def download(site_key):

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


def process_economist_zipped_files():
    zipped_filename_length = len('all.zip')
    zipped_filename = DOWNLOAD_PATHS[ECONOMIST]['all-zip']
    subpath = zipped_filename[:-zipped_filename_length]
    with ZipFile(zipped_filename, 'r') as zipped:
        for member in zipped.namelist():
            filename_wo_path = member.split('/')[-1]
            with zipped.open(member, 'r') as input_file:
                with open(subpath + filename_wo_path, 'wb') as output_file:
                    output_file.write(input_file.read())
                    output_file.close()
                input_file.close()
        zipped.close()
        print('done!')


# download(FTE)
# download(ECONOMIST)
# download(JHK)
# download(OURPROGRESS)
# download(LEANTOSSUP)

process_economist_zipped_files()
