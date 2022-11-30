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
}

directories = {
    "data": "./data",
    "satellites": "./data/satellites/",
    "observation_pages": "./data/observation_pages/",
    "observations": "./data/observations/",
    "waterfalls": "./data/observations/waterfalls/",
    "logs": "./data/logs/"
}

files = {
    "satellites_json": "./data/satellites/satellites.json",
    "observation_json": "./data/observations/observations.json",
    "log_file": "./data/logs/log.txt"
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
