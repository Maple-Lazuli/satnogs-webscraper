import os.path
import shutil
import satnogs_webscraper.constants as cnst
from satnogs_webscraper.scraper import Scraper
import pytest


@pytest.fixture()
def prep_directories():
    if os.path.exists(cnst.directories['data']):
        shutil.rmtree(cnst.directories['data'])
    cnst.verify_directories()
    yield None
    shutil.rmtree(cnst.directories['data'])


def test_scraper_init(prep_directories):
    expected_string = 'https://network.satnogs.org/observations/?future=0&bad=0&unknown=0&failed=0&norad=&observer=&' \
                      'station=&start=&end=&transmitter_mode='
    scraper = Scraper()
    assert scraper.generate_query_string() == expected_string

    expected_string2 = 'https://network.satnogs.org/observations/?future=0&bad=0&unknown=0&failed=0&norad=44352&' \
                       'observer=&station=&start=&end=&transmitter_mode='

    scraper2 = Scraper(norad="44352")
    assert scraper2.generate_query_string() == expected_string2


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
    assert meta_df.shape[1] == 12
    for expected_column in ['Timeframe', 'Satellite', 'Station', 'Status', 'Status_Message',
                            'Frequency', 'Mode', 'Metadata', 'Downloads', 'Waterfall_Status',
                            'Polar_Plot', 'demod_key']:
        assert expected_column in meta_df.columns

    for name in meta_df['Satellite']:
        assert name.find("ARMADILLO") != -1
        assert name.find("44352") != -1

    assert len(meta_df['Satellite'].unique()) == 1
    assert sum(meta_df['Status'] == 'Good') == page_limit * 20
    assert sum(meta_df['Status'] == 'Bad') == 0

    scraper2 = Scraper(good=False, bad=True, list_page_limit=page_limit+1)
    meta_df, demod_df = scraper2.scrape()
    assert len(meta_df['Satellite'].unique()) != 1
    assert sum(meta_df['Status'] == 'Bad') == page_limit * 20
    assert sum(meta_df['Status'] == 'Good') == 0
