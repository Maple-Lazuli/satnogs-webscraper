import satnogs_webscraper.observation_list_scraper as ols
import satnogs_webscraper.constants as cnst
import pytest
import os
import shutil
import re
import json
import requests


@pytest.fixture()
def prep_directories():
    if os.path.exists(cnst.directories['data']):
        shutil.rmtree(cnst.directories['data'])
    cnst.verify_directories()
    yield None
    shutil.rmtree(cnst.directories['data'])


def test_observation_list_scraper_init():
    url = 'some_url'
    save_name = "save_name"
    save_dir = "some_dir"
    page_limit = 2
    resume = False
    cpus = 2
    fetcher1 = ols.ObservationListFetch(url, save_name, save_dir)
    fetcher2 = ols.ObservationListFetch(url, save_name, save_dir, page_limit=page_limit, resume=resume, cpus=cpus)

    assert url == fetcher1.url
    assert save_name == fetcher1.save_name
    assert save_dir == fetcher1.save_dir
    assert fetcher1.page_limit is None
    assert fetcher1.cpus is None
    assert fetcher1.resume == True

    assert url == fetcher2.url
    assert save_name == fetcher2.save_name
    assert save_dir == fetcher2.save_dir
    assert page_limit == fetcher2.page_limit
    assert resume == fetcher2.resume
    assert cpus == fetcher2.cpus


def test_get_pages(prep_directories):
    test_url = "https://network.satnogs.org/observations/?future=0&bad=0&unknown=0&failed=0&norad=&observer=&station" \
               "=&start=&end=&transmitter_mode="

    fetcher1 = ols.ObservationListFetch(test_url, "", "", page_limit=2)

    pages = fetcher1.get_pages(test_url)

    assert len(pages) == 2

    for page in pages:
        assert 200 == requests.get(page).status_code


def test_get_page_observation_ids(prep_directories):
    test_url = "https://network.satnogs.org/observations/?future=0&bad=0&unknown=0&failed=0&norad=&observer=&station" \
               "=&start=&end=&transmitter_mode="

    fetcher1 = ols.ObservationListFetch(test_url, "", "", page_limit=2)
    pages = fetcher1.get_pages(test_url)

    ids_page0 = fetcher1.get_page_observation_ids(pages[0])
    assert len(ids_page0) == 20
    for id in ids_page0:
        assert id == re.search(r"\d+", id)[0]

    ids_page1 = fetcher1.get_page_observation_ids(pages[1])
    assert len(ids_page1) == 20
    for id in ids_page1:
        assert id == re.search(r"\d+", id)[0]


def test_multiprocess_id_fetch(prep_directories):
    test_url = "https://network.satnogs.org/observations/?future=0&bad=0&unknown=0&failed=0&norad=&observer=&station" \
               "=&start=&end=&transmitter_mode="
    json1 = cnst.directories['observation_pages'] + "1.json"
    json2 = cnst.directories['observation_pages'] + "2.json"

    fetcher1 = ols.ObservationListFetch(test_url, "", page_limit=2)
    fetcher1.multiprocess_id_fetch()

    assert os.path.exists(json1)
    assert os.path.exists(json2)

    with open(json1) as fin:
        json1_parsed = json.load(fin)

    assert len(json1_parsed['IDs']) == 20
    for id in json1_parsed['IDs']:
        assert id == re.search(r"\d+", id)[0]

    with open(json2) as fin:
        json2_parsed = json.load(fin)

    assert len(json2_parsed['IDs']) == 20
    for id in json2_parsed['IDs']:
        assert id == re.search(r"\d+", id)[0]


def test_fetch_ids(prep_directories):
    if os.path.exists("test.json"):
        os.remove("test.json")

    test_url = "https://network.satnogs.org/observations/?future=0&bad=0&unknown=0&failed=0&norad=&observer=&station" \
               "=&start=&end=&transmitter_mode="

    fetcher1 = ols.ObservationListFetch(test_url, "test.json", page_limit=2)

    assert not os.path.exists("test.json")

    ids = fetcher1.fetch_ids()

    assert os.path.exists("test.json")

    assert len(ids) == 40

    for id in ids:
        assert id == re.search(r"\d+", id)[0]
