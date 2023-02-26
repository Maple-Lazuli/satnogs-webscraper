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


# def test_scraper_scrape_size(prep_directories):
#     page_limit = 1
#     scraper = Scraper(norad="44352", list_page_limit=page_limit)
#     df = scraper.scrape()
#     assert df.shape[0] == page_limit * 20
#     assert df.shape[1] == 13
#
#     page_limit = 2
#     scraper2 = Scraper(norad="44352", list_page_limit=page_limit)
#     df2 = scraper2.scrape()
#     assert df2.shape[0] == page_limit * 20
#     assert df2.shape[1] == 13


def test_scraper_scrape_contents(prep_directories):
    page_limit = 1
    scraper = Scraper(norad="44352", list_page_limit=page_limit)
    df = scraper.scrape()
    for name in df['Satellite']:
        assert name.find("ARMADILLO") != -1
        assert name.find("44352") != -1

    assert len(df['Satellite'].unique()) == 1
    assert sum(df['Status'] == 'Good') == page_limit * 20
    assert sum(df['Status'] == 'Bad') == 0

    scraper2 = Scraper(good=False, bad=True, list_page_limit=page_limit)
    df = scraper2.scrape()
    assert len(df['Satellite'].unique()) != 1
    assert sum(df['Status'] == 'Bad') == page_limit * 20
    assert sum(df['Status'] == 'Good') == 0
