import os
import shutil
import pandas as pd
import pytest
import satnogs_webscraper.observation_dataset as od
import satnogs_webscraper.constants as cnst


@pytest.fixture()
def get_obs_ids():
    obs_list = ["5738648", "5740805", "5740806"]
    cnst.verify_directories()

    for ob in obs_list:
        shutil.copy2(f'./tests/resources/{ob}.json', f'{cnst.directories["observations"]}')

    yield obs_list

    shutil.rmtree(cnst.directories['data'])


def test_get_dataset(get_obs_ids):
    df = od.get_dataset(get_obs_ids)
    assert df['Observation_id'].iloc[0] == "5738648"
    assert df['Observation_id'].iloc[1] == "5740805"
    assert df['Observation_id'].iloc[2] == "5740806"


def test_save_dataset(get_obs_ids):
    save_name = "saved_observations.csv"

    if os.path.exists(save_name):
        os.remove(save_name)

    od.save_dataset(get_obs_ids, save_name)

    assert os.path.exists(save_name)

    df = pd.read_csv(save_name)
    assert df['Observation_id'].iloc[0] == 5738648
    assert df['Observation_id'].iloc[1] == 5740805
    assert df['Observation_id'].iloc[2] == 5740806
