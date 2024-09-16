import datetime
import json
import os
import pandas as pd
import re
import satnogs_webscraper.constants as cnst
import warnings


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


def get_datasets(observation_list, kaitai_interface=None):
    common_key = 0

    observations = []
    demod_dictionary = dict()
    demods = []

    for observation in observation_list:
        file_name = os.path.join(cnst.directories['observations'], f'{observation}.json')
        with open(file_name, "r") as file_in:
            observation_dictionary = json.load(file_in)
            observation_dictionary['meta_key'] = common_key if len(observation_dictionary['demods']) > 0 else -1

        for demod in observation_dictionary['demods']:
            with open(demod['location'], 'rb') as file_in:
                demod_data = file_in.read()
                demods.append({
                    'timestamp': get_demod_time(demod['original_name']),
                    'bytes': demod_data,
                    'meta_key': common_key
                })
                if kaitai_interface is not None:
                    from kaitaistruct import KaitaiStream, BytesIO
                    if 'kaitai' not in observation_dictionary.keys():
                        observation_dictionary['kaitai'] = []
                    try:
                        observation_dictionary['kaitai'].append(kaitai_interface(KaitaiStream(BytesIO(demod_data))))
                    except Exception as e:
                        warnings.warn(f"Error parsing demod. Error:{e}")
                        pass
        observations.append(observation_dictionary)
        common_key += 1

    meta_df = pd.DataFrame(observations)
    meta_df.set_index(['Observation_id'], inplace=True)
    meta_df.sort_index(inplace=True)

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
        df.set_index(['timestamp'], inplace=True)
        df.sort_index(inplace=True)
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

    pattern = r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}(?:_\d+)?"
    match = re.search(pattern, demod_url)
    time_string = match.group(0)

    if time_string.find("_") == -1:
        time_parsed = datetime.datetime.strptime(time_string, "%Y-%m-%dT%H-%M-%S")
    else:
        time_stamp_part = time_string.split("_")[0]
        extra_part = int(time_string.split("_")[1])
        time_parsed = datetime.datetime.strptime(time_stamp_part, "%Y-%m-%dT%H-%M-%S")
        time_parsed = time_parsed + datetime.timedelta(milliseconds=extra_part)
    return time_parsed


def find_largest_number(string):
    numbers = re.findall(r'\d+', string)
    numbers = list(map(int, numbers))
    return max(numbers) if numbers else 0
