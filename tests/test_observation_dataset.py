import os
import shutil
import pandas as pd
import pytest
import satnogs_webscraper.observation_dataset as od
import satnogs_webscraper.constants as cnst
from satnogs_webscraper.observation_scraper import ObservationScraper


@pytest.fixture()
def get_obs_ids():
    if os.path.exists(cnst.directories['data']):
        shutil.rmtree(cnst.directories['data'])
    obs_list = ["5738648", "5740805", "5740806"]
    cnst.verify_directories()
    scraper = ObservationScraper(check_disk=False)
    scraper.multiprocess_scrape_observations(obs_list)
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


def test_get_datasets(get_obs_ids):
    meta_df, demod_df = od.get_datasets(get_obs_ids)

    assert demod_df is None
    assert meta_df.shape[0] == 3
    assert meta_df.shape[1] == 13
    assert '5740805' in meta_df.index
    assert '5738648' in meta_df.index
    assert '5740806' in meta_df.index

    for idx in range(0,3):
        assert meta_df.iloc[idx].meta_key == -1

    for expected_column in ['Timeframe', 'Satellite', 'Station', 'Status', 'Status_Message',
                            'Frequency', 'Mode', 'Metadata', 'Downloads', 'Waterfall_Status',
                            'Polar_Plot', 'meta_key']:
        assert expected_column in meta_df.columns


