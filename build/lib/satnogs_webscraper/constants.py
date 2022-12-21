import os

observations = 'observations/'
satellites = "satellites/"
web_address = "https://network.satnogs.org/"

observation_template = {
    'Observation_id': None,
    'Satellite': None,
    'Station': None,
    'Status': None,
    'Status_Message': None,
    'Transmitter': None,
    'Frequency': None,
    'Mode': None,
    'Metadata': None,
    'Downloads': None,
    'Waterfall_Status': None,
    'Polar_Plot': None,
    'demods':None
}

directories = {
    "data": "./satnogs-data",
    "satellites": "./satnogs-data/satellites/",
    "observation_pages": "./satnogs-data/observation_pages/",
    "observations": "./satnogs-data/observations/",
    "waterfalls": "./satnogs-data/observations/waterfalls/",
    "demods": "./satnogs-data/observations/demods/",
    "logs": "./satnogs-data/logs/"
}

files = {
    "satellites_json": "./satnogs-data/satellites/satellites.json",
    "observation_json": "./satnogs-data/observations/observations.json",
    "log_file": "./satnogs-data/logs/log.txt"
}


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
