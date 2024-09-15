import json
import os.path
import shutil
import re
import satnogs_webscraper.constants as cnst
from satnogs_webscraper.observation_scraper import ObservationScraper
import pytest

record_7206380 = {
    'Observation_id': '7206380',
    'Timeframe': ['2023-02-25 21:08:54', '2023-02-25 21:13:09'],
    'Satellite': '43880  - UWE-4',
    'Station': '2802 - geoscan-2',
    'Status': 'Good',
    'Status_Message': '100',
    'Frequency': '435,599,000Hz',
    'Mode': 'FSK 9600',
    'Metadata': {'radio': {'name': 'gr-satnogs',
                           'version': 'v2.3-compat-xxx-v2.3.3.0',
                           'parameters': {'soapy-rx-device': 'driver=airspy,biastee=false,bitpack=true',
                                          'samp-rate-rx': '6e6',
                                          'rx-freq': '435599000',
                                          'file-path': '/tmp/.satnogs/data/receiving_satnogs_7206380_2023-02-25T21-08-54.out',
                                          'waterfall-file-path': '/tmp/.satnogs/data/receiving_waterfall_7206380_2023-02-25T21-08-54.dat',
                                          'decoded-data-file-path': '/tmp/.satnogs/data/data_7206380',
                                          'doppler-correction-per-sec': None,
                                          'lo-offset': None,
                                          'ppm': None,
                                          'rigctl-port': '4532',
                                          'gain-mode': 'Settings Field',
                                          'gain': None,
                                          'antenna': 'RX',
                                          'dev-args': None,
                                          'stream-args': None,
                                          'tune-args': None,
                                          'other-settings': 'LNA=3,MIX=11,VGA=14',
                                          'dc-removal': None,
                                          'bb-freq': None,
                                          'bw': None,
                                          'enable-iq-dump': '1',
                                          'iq-file-path': '/tmp/.satnogs/iq.bin',
                                          'udp-dump-host': '127.0.0.1',
                                          'udp-dump-port': 57356,
                                          'wpm': None,
                                          'baudrate': '9600',
                                          'framing': 'ax25'}},
                 'latitude': 60.002677,
                 'longitude': 30.364098,
                 'elevation': 50,
                 'frequency': 435599000},
    'Downloads': {
        'audio': 'https://archive.org/download/satnogs-observations-007200001-007210000/satnogs-observations-007206001-007207000.zip/satnogs_7206380_2023-02-25T21-08-54.ogg',
        'waterfall': 'https://s3.eu-central-1.wasabisys.com/satnogs-network/data_obs/2023/2/25/21/7206380/waterfall_7206380_2023-02-25T21-08-54.png',
        'waterfall_hash_name': 'd4c1e87080299224b407920fc2ab56249b7961f28f4e57cfc565758f36250a6b',
        'waterfall_shape': (1542, 623, 3)},
    'Waterfall_Status': 'Unknown',
    'Polar_Plot': {'tle1': '1 43880U 18111E   23056.19343271  .00005878  00000+0  47147-3 0  9994',
                   'tle2': '2 43880  97.6498 323.1620 0014413 186.0212 174.0841 15.00395149227562',
                   'timeframe-start': '2023-02-25T21:08:54+00:00',
                   'timeframe-end': '2023-02-25T21:13:09+00:00',
                   'groundstation-lat': '60.002677',
                   'groundstation-lon': '30.364098',
                   'groundstation-alt': '50'},
    'demods': [{'original_name': 'data_obs/2023/2/25/21/7206380/data_7206380_2023-02-25T21-10-20_g0',
                'location': '74851f09608f5c7f10a1d71460484c399b599a70352a58b1a990e3a7df3d13f0.bin'},
               {'original_name': 'data_obs/2023/2/25/21/7206380/data_7206380_2023-02-25T21-10-28',
                'location': 'c1126bc65bcfe09bbc97e574a7323c6b5f28db978e35b48c93a8b5f1e26505bd.bin'},
               {'original_name': 'data_obs/2023/2/25/21/7206380/data_7206380_2023-02-25T21-10-47_g0',
                'location': '0501c350339d0689505f8bcdf16236b2e1a7ecc6df90b706505c0f5f591d9773.bin'}]}


@pytest.fixture()
def prep_directories():
    if os.path.exists(cnst.directories['data']):
        shutil.rmtree(cnst.directories['data'])
    cnst.verify_directories()
    yield None
    shutil.rmtree(cnst.directories['data'])


def test_Observation_Scraper_init():
    assert not os.path.exists(cnst.directories['data'])

    fetch_waterfalls = True
    fetch_logging = True
    prints = True
    check_disk = True
    cpus = 1
    grey_scale = True

    obs_scraper = ObservationScraper()

    assert os.path.exists(cnst.directories['data'])
    assert fetch_waterfalls == obs_scraper.fetch_waterfalls
    assert fetch_logging == obs_scraper.fetch_logging
    assert prints == obs_scraper.prints
    assert check_disk == obs_scraper.check_disk
    assert cpus == obs_scraper.cpus
    assert grey_scale == obs_scraper.grey_scale
    assert isinstance(obs_scraper.observations_list, list)
    assert cnst.files["observation_json"] == obs_scraper.json_file_loc
    assert cnst.directories['observations'] == obs_scraper.observation_save_dir
    assert cnst.files["log_file"] == obs_scraper.log_file_loc
    assert cnst.directories['waterfalls'] == obs_scraper.waterfall_path
    assert cnst.directories["demods"] == obs_scraper.demod_path

    fetch_waterfalls = False
    fetch_logging = False
    prints = False
    check_disk = False
    cpus = 2
    grey_scale = False

    obs_scraper2 = ObservationScraper(fetch_waterfalls=fetch_waterfalls, fetch_logging=fetch_logging, prints=prints,
                                      check_disk=check_disk, cpus=cpus, grey_scale=grey_scale)

    assert fetch_waterfalls == obs_scraper2.fetch_waterfalls
    assert fetch_logging == obs_scraper2.fetch_logging
    assert prints == obs_scraper2.prints
    assert check_disk == obs_scraper2.check_disk
    assert cpus == obs_scraper2.cpus
    assert grey_scale == obs_scraper2.grey_scale


def test_observation_scrape(prep_directories):
    observation_url = "https://network.satnogs.org/observations/7206380/"
    obs_scraper = ObservationScraper()

    scrape = obs_scraper.scrape_observation(url=observation_url)

    keys_to_skip = ['demods', 'Metadata', 'Polar_Plot', 'Downloads', 'Timeframe']

    # Test records that are in the table
    for key in scrape.keys():
        if key not in keys_to_skip:
            assert scrape[key] == record_7206380[key]

    # Test the timeframe record
    assert 2 == len(scrape['Timeframe'])
    assert scrape['Timeframe'][0] == record_7206380['Timeframe'][0]
    assert scrape['Timeframe'][1] == record_7206380['Timeframe'][1]

    # Test metadata
    assert scrape['Metadata'] is not None
    for key in record_7206380['Metadata'].keys():
        assert record_7206380['Metadata'][key] == scrape['Metadata'][key]

    # Test polar plot
    assert scrape['Polar_Plot'] is not None
    for key in record_7206380['Polar_Plot'].keys():
        assert record_7206380['Polar_Plot'][key] == scrape['Polar_Plot'][key]

    # Test the downloads
    assert record_7206380['Downloads']['audio'] == scrape['Downloads']['audio']
    assert record_7206380['Downloads']['waterfall'] == scrape['Downloads']['waterfall']
    assert len(scrape['Downloads']['waterfall_shape']) == 2
    assert scrape['Downloads']['waterfall_hash_name'].find(record_7206380['Downloads']['waterfall_hash_name']) != -1

    # Test the demods
    assert len(scrape['demods']) == len(record_7206380['demods'])
    for s_demod, r_demod in zip(scrape['demods'], record_7206380['demods']):
        assert s_demod['original_name'] == r_demod['original_name']
        assert s_demod['location'].find(r_demod['location']) != -1


def test_multi_process_observation_scrape(prep_directories):
    obs_ids = [7206380, 7206656]
    obs_names = [f'{obs_id}.json' for obs_id in obs_ids]
    obs_scraper = ObservationScraper()
    obs_scraper.multiprocess_scrape_observations(obs_ids)

    scraped_files = os.listdir(cnst.directories['observations'])
    for obs_name in obs_names:
        assert obs_name in scraped_files

    waterfall_files = [
        "042cae91b4da57f450dda7a3504503c4d293ea9cbb268b087d51f484bae465e1.bin",
        "d4c1e87080299224b407920fc2ab56249b7961f28f4e57cfc565758f36250a6b.bin"
    ]

    processed_waterfall_files = os.listdir(cnst.directories['waterfalls'])

    for file in waterfall_files:
        assert file in processed_waterfall_files

    demod_files = [
        "0501c350339d0689505f8bcdf16236b2e1a7ecc6df90b706505c0f5f591d9773.bin",
        "74851f09608f5c7f10a1d71460484c399b599a70352a58b1a990e3a7df3d13f0.bin",
        "830ecb5c37750234323882591ff8a0f3e5c3030a95a41e56c72c90eb64f5acec.bin",
        "99f4e4cc9364e7f704219ed05289b273a2df8136438f78ebb7aaf6a4349dd109.bin",
        "c1126bc65bcfe09bbc97e574a7323c6b5f28db978e35b48c93a8b5f1e26505bd.bin"
    ]

    processed_demod_files = os.listdir(cnst.directories['demods'])

    for file in demod_files:
        assert file in processed_demod_files
