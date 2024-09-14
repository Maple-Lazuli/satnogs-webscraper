import datetime
import json
import os
import pandas as pd
import re
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
    common_key = 0

    observations = []
    demod_dictionary = dict()
    demods = []

    for observation in observation_list:
        file_name = os.path.join(cnst.directories['observations'], f'{observation}.json')
        with open(file_name, "r") as file_in:
            observation_dictionary = json.load(file_in)
            observation_dictionary['demod_key'] = common_key if len(observation_dictionary['demods']) > 0 else -1

        for demod in observation_dictionary['demods']:
            with open(demod['location'], 'rb') as file_in:
                demods.append({
                    'timestamp': get_demod_time(demod['original_name']),
                    'bytes': file_in.read(),
                    'meta_key': common_key
                })
        del observation_dictionary['demods']
        observations.append(observation_dictionary)
        common_key += 1

    meta_df = pd.DataFrame(observations)

    for demod in demods:
        length_key = len(demod['bytes'])

        if length_key not in demod_dictionary.keys():
            demod_dictionary[length_key] = dict()
            demod_dictionary[length_key]['demods'] = []
            demod_dictionary[length_key]['demod_length'] = length_key
            demod_dictionary[length_key]['num_demods'] = 0

        for k, v in enumerate(demod['bytes']):
            demod[k] = v

        del demod['bytes']

        demod_dictionary[length_key]['demods'].append(demod)
        demod_dictionary[length_key]['num_demods'] += 1

    for key in demod_dictionary.keys():
        df = pd.DataFrame(demod_dictionary[key]['demods'])
        df.set_index(['timestamp'])
        df.sort_index()
        demod_dictionary[key]['dataframe'] = df
        del demod_dictionary[key]['demods']

    if len(demod_dictionary.keys()) != 0:
        demod_df = pd.DataFrame([demod_dictionary[key] for key in demod_dictionary.keys()])
        demod_df.set_index(['demod_length'], inplace=True)
        demod_df.sort_values(['num_demods'], ascending=False, inplace=True)
        return meta_df, demod_df
    else:
        return meta_df, None


def get_demod_time(demod_url):
    ts = demod_url.split("/")[-1].split("T")
    ts_date = ts[0].split("_")[-1]
    ts_time = ts[1].split("_")[0]
    time_parsed = datetime.datetime.strptime(f"{ts_date}T{ts_time}", "%Y-%m-%dT%H-%M-%S")
    if len(ts[1].split("_")) > 1:
        milliseconds = find_largest_number(ts[1].split("_")[1])
        time_parsed = datetime.timedelta(milliseconds=milliseconds)
    return time_parsed


def find_largest_number(string):
    numbers = re.findall(r'\d+', string)
    numbers = list(map(int, numbers))
    return max(numbers) if numbers else 0
