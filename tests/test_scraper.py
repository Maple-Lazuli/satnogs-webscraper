import kaitaistruct
import importlib
import os.path
import shutil
import satnogs_webscraper.constants as cnst
from satnogs_webscraper.scraper import Scraper
import pandas as pd
import pytest
import subprocess

@pytest.fixture()
def prep_directories():
    if os.path.exists(cnst.directories['data']):
        shutil.rmtree(cnst.directories['data'])
    cnst.verify_directories()
    yield None
    shutil.rmtree(cnst.directories['data'])

@pytest.fixture()
def get_kaitai_parser():

    if os.path.exists(cnst.directories['data']):
        shutil.rmtree(cnst.directories['data'])
    cnst.verify_directories()

    get_ksy = ["wget",
               "https://gitlab.com/librespacefoundation/satnogs/satnogs-decoders/-/raw/master/ksy/armadillo.ksy"]
    compile_ksy = ["kaitai-struct-compiler", "-t", "python", "armadillo.ksy"]

    try:
        result = subprocess.run(get_ksy, check=True, capture_output=True, text=True)
        print("Wget output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Wget failed with error: {e.stderr}")

    try:
        result = subprocess.run(compile_ksy, check=True, capture_output=True, text=True)
        print("Compile output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")

    yield importlib.import_module('armadillo').Armadillo

    shutil.rmtree(cnst.directories['data'])
    os.remove("armadillo.py")
    os.remove("armadillo.ksy")


def test_scraper_init(prep_directories):
    expected_string = 'https://network.satnogs.org/observations/?future=0&bad=0&unknown=0&failed=0&norad=&observer=&' \
                      'station=&start=&end=&transmitter_mode='
    scraper = Scraper()
    assert scraper.generate_query_string() == expected_string

    expected_string2 = 'https://network.satnogs.org/observations/?future=0&bad=0&unknown=0&failed=0&norad=44352&' \
                       'observer=&station=&start=&end=&transmitter_mode='

    scraper2 = Scraper(norad="44352")
    assert scraper2.generate_query_string() == expected_string2
    scraper3 = Scraper(norad="44352", kaitai_interface="Test")
    assert scraper3.kaitai_interface == "Test"


def test_scraper_scrape_contents(prep_directories):
    page_limit = 1
    scraper = Scraper(norad="44352", list_page_limit=page_limit)
    meta_df, demod_df = scraper.scrape()

    # Testing the demod df container
    assert demod_df.shape[0] == 6
    assert demod_df.shape[1] == 2
    assert 'num_demods' in demod_df.columns
    assert 'dataframe' in demod_df.columns
    assert 272 in demod_df.index
    # Testing the best demod df scraped
    demod_272 = demod_df.loc[272].dataframe
    assert demod_272.shape[0] == 20
    assert demod_272.shape[1] == 273
    assert 'meta_key' in demod_272.columns
    for i in range(0, 272):
        assert i in demod_272.columns

    # Testing meta df
    assert meta_df.shape[0] == 20
    assert meta_df.shape[1] == 13
    for expected_column in ['Timeframe', 'Satellite', 'Station', 'Status', 'Status_Message',
                            'Frequency', 'Mode', 'Metadata', 'Downloads', 'Waterfall_Status',
                            'Polar_Plot', 'meta_key']:
        assert expected_column in meta_df.columns

    # Testing right join

    df_merged = pd.merge(meta_df, demod_272, on='meta_key', how='right')
    assert df_merged.shape[0] == 20
    assert df_merged.shape[1] == 285

    for expected_column in ['Timeframe', 'Satellite', 'Station', 'Status', 'Status_Message',
                            'Frequency', 'Mode', 'Metadata', 'Downloads', 'Waterfall_Status',
                            'Polar_Plot', 'meta_key']:
        assert expected_column in df_merged.columns

    for i in range(0, 272):
        assert i in df_merged.columns

    for name in meta_df['Satellite']:
        assert name.find("ARMADILLO") != -1
        assert name.find("44352") != -1

    assert len(meta_df['Satellite'].unique()) == 1
    assert sum(meta_df['Status'] == 'Good') == page_limit * 20
    assert sum(meta_df['Status'] == 'Bad') == 0

    scraper2 = Scraper(good=False, bad=True, list_page_limit=2)
    meta_df, demod_df = scraper2.scrape()
    assert len(meta_df['Satellite'].unique()) != 1
    assert sum(meta_df['Status'] == 'Bad') == 2 * 20
    assert sum(meta_df['Status'] == 'Good') == 0


def test_kaitai_struct_interface(get_kaitai_parser):
    scraper = Scraper(norad="44352", data=1, save_name="Armadillo", list_page_limit=3,
                         kaitai_interface=get_kaitai_parser)

    meta_df, demod_df = scraper.scrape()

    assert meta_df.shape[1] == 14
    assert sum(meta_df['kaitai'].apply(len) > 0) > 10

    kaitai_obj = meta_df[meta_df['kaitai'].apply(len) > 0].kaitai[0][0]

    assert type(kaitai_obj._io) == kaitaistruct.KaitaiStream

    assert kaitai_obj.ax25_frame is not None

