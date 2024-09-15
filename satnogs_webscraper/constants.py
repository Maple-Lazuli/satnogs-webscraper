import os

observations = 'observations/'
satellites = "satellites/"
web_address = "https://network.satnogs.org/"

observation_template = {
    'Observation_id': None,
    'Timeframe': None,
    'Satellite': None,
    'Station': None,
    'Status': None,
    'Status_Message': None,
    'Frequency': None,
    'Mode': None,
    'Metadata': None,
    'Downloads': None,
    'Waterfall_Status': None,
    'Polar_Plot': None,
    'demods': None
}

directories = dict()
directories['data'] = "./satnogs-data"
directories['satellites'] = directories['data'] + "/satellites/"
directories['observation_pages'] = directories['data'] + "/observation_pages/"
directories['observations'] = directories['data'] + "/observations/"
directories['waterfalls'] = directories['observations'] + "/waterfalls/"
directories['demods'] = directories['observations'] + "/demods/"
directories['logs'] = directories['data'] + "/logs/"

files = dict()
files['satellites_json'] = directories['satellites'] + "satellites.json"
files['observation_json'] = directories['observations'] + "observations.json"
files['log_file'] = directories['logs'] + "log.json"


def verify_directories():
    for key in directories.keys():
        if not os.path.exists(directories[key]):
            os.makedirs(directories[key])


if __name__ == '__main__':
    verify_directories()
    print(f'observation = {observations}')
    print(f'satellites = {satellites}')
    print(f'web_address = {web_address}')
    print(f'observation_template: {observation_template}')
