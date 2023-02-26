import json
import os.path
import shutil
import re
import satnogs_webscraper.constants as cnst
from satnogs_webscraper.observation_scraper import ObservationScraper
import pytest


@pytest.fixture()
def prep_directories():
    if os.path.exists(cnst.directories['data']):
        shutil.rmtree(cnst.directories['data'])
    cnst.verify_directories()
    yield None
    shutil.rmtree(cnst.directories['data'])


# def test_Observation_Scraper_init():
#     assert not os.path.exists(cnst.directories['data'])
#
#     fetch_waterfalls = True
#     fetch_logging = True
#     prints = True
#     check_disk = True
#     cpus = 1
#     grey_scale = True
#
#     obs_scraper = ObservationScraper()
#
#     assert os.path.exists(cnst.directories['data'])
#     assert fetch_waterfalls == obs_scraper.fetch_waterfalls
#     assert fetch_logging == obs_scraper.fetch_logging
#     assert prints == obs_scraper.prints
#     assert check_disk == obs_scraper.check_disk
#     assert cpus == obs_scraper.cpus
#     assert grey_scale == obs_scraper.grey_scale
#     assert isinstance(obs_scraper.observations_list, list)
#     assert cnst.files["observation_json"] == obs_scraper.json_file_loc
#     assert cnst.directories['observations'] == obs_scraper.observation_save_dir
#     assert cnst.files["log_file"] == obs_scraper.log_file_loc
#     assert cnst.directories['waterfalls'] == obs_scraper.waterfall_path
#     assert cnst.directories["demods"] == obs_scraper.demod_path
#
#     fetch_waterfalls = False
#     fetch_logging = False
#     prints = False
#     check_disk = False
#     cpus = 100
#     grey_scale = False
#
#     obs_scraper2 = ObservationScraper(fetch_waterfalls=fetch_waterfalls, fetch_logging=fetch_logging, prints=prints,
#                                       check_disk=check_disk, cpus=cpus, grey_scale=grey_scale)
#
#     assert fetch_waterfalls == obs_scraper2.fetch_waterfalls
#     assert fetch_logging == obs_scraper2.fetch_logging
#     assert prints == obs_scraper2.prints
#     assert check_disk == obs_scraper2.check_disk
#     assert cpus == obs_scraper2.cpus
#     assert grey_scale == obs_scraper2.grey_scale
#
#
# def test_observation_scrape(prep_directories):
#     observation_url = "https://network.satnogs.org/observations/7206380/"
#     obs_scraper = ObservationScraper()
#
#     scrape = obs_scraper.scrape_observation(url=observation_url)
#
#     with open("tests/resources/7206380.json") as file_in:
#         test_record = json.load(file_in)
#
#     keys_to_skip = ['Downloads', 'demods']
#
#     for key in test_record.keys():
#         if not key in keys_to_skip:
#             assert test_record[key] == scrape[key], key
#
#     assert scrape['Downloads']['audio'].find("satnogs_7206380_2023-02-25T21-08-54.ogg") != -1
#     assert scrape['Downloads']['waterfall'].find("waterfall_7206380_2023-02-25T21-08-54.png") != -1
#     assert scrape['Downloads']['waterfall_shape'] == (1542, 623)
#
#     waterfall_hash_str = scrape['Downloads']['waterfall_hash_name'].split("/")[-1]
#     assert len(waterfall_hash_str) == 64
#     assert re.search(r"[a-zA-Z\d]+", waterfall_hash_str)[0] == waterfall_hash_str
#
#     assert len(scrape['demods']) == 3
#
#     first_demod = scrape['demods'][0]
#     demod_hash_str = first_demod['location'].split("/")[-1][:-4]
#     assert first_demod['original_name'].split("/")[-1] == 'data_7206380_2023-02-25T21-10-20_g0'
#     assert len(demod_hash_str) == 64
#     assert re.search(r"[a-zA-Z\d]+", demod_hash_str)[0] == demod_hash_str
#     assert first_demod['location'].split("/")[-1][-4:] == '.bin'
#

def test_multi_process_observation_scrape(prep_directories):
    obs_ids = [7206380, 7206656]
    obs_names = [f'{obs_id}.json' for obs_id in obs_ids]
    obs_scraper = ObservationScraper()
    obs_scraper.multiprocess_scrape_observations(obs_ids)

    scraped_files = os.listdir(cnst.directories['observations'])

    assert obs_names[0] in scraped_files
    assert obs_names[1] in scraped_files
    assert 'demods' in scraped_files
    assert len(os.listdir(cnst.directories['demods'])) > 0
    assert 'waterfalls' in scraped_files
    assert len(os.listdir(cnst.directories['waterfalls'])) > 0

    keys_to_skip = ['Downloads', 'demods']
    for obs_name in obs_names:
        with open(f"tests/resources/{obs_name}") as file_in:
            test_record = json.load(file_in)
        with open(f"{cnst.directories['observations']}{obs_name}") as file_in:
            scraped = json.load(file_in)
        for key in test_record.keys():
            if not key in keys_to_skip:
                assert test_record[key] == scraped[key], key



