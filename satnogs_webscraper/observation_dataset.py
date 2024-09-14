import datetime
import json
import os
import pandas as pd
import satnogs_webscraper.constants as cnst


def save_dataset(observation_list, save_name):
    df = get_dataset(observation_list)
    df.to_csv(save_name, index=False)


def get_dataset(observation_list):
    observations = []
    for observation in observation_list:
        file_name = os.path.join(cnst.directories['observations'], f'{observation}.json')
        with open(file_name, "r") as file_in:
            observations.append(json.load(file_in))

    df = pd.DataFrame(observations)
    return df


def get_datasets(observation_list):
    observations = []
    for observation in observation_list:
        file_name = os.path.join(cnst.directories['observations'], f'{observation}.json')
        with open(file_name, "r") as file_in:
            observations.append(json.load(file_in))

    df = pd.DataFrame(observations)
    return df


def get_demod_time(demod_url):
    ts = demod_url.split("/")[-1].split("T")
    ts_date = ts[0].split("_")[-1]
    ts_time = ts[1].split("_")[0]
    return datetime.datetime.strptime(f"{ts_date}T{ts_time}", "%Y-%m-%dT%H-%M-%S")
