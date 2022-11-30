import json
import os
import pandas as pd
import satnogs_webscraper.constants as cnst


def save_dataset(observation_list, save_name):
    observations = []
    for observation in observation_list:
        file_name = os.path.join(cnst.directories['observations'], f'{observation}.json')
        with open(file_name, "r") as file_in:
            observations.append(json.load(file_in))

    df = pd.DataFrame(observations)
    df.to_csv(save_name, index=False)


def get_dataset(observation_list):
    observations = []
    for observation in observation_list:
        file_name = os.path.join(cnst.directories['observations'], f'{observation}.json')
        with open(file_name, "r") as file_in:
            observations.append(json.load(file_in))

    df = pd.DataFrame(observations)
    return df
