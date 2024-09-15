import os
import shutil
from PIL import Image

import satnogs_webscraper.image_utils as iu
from satnogs_webscraper.observation_scraper import ObservationScraper
import satnogs_webscraper.constants as cnst
import pytest


@pytest.fixture()
def get_image_greyscale():
    cnst.verify_directories()
    scraper = ObservationScraper(grey_scale=False, delete_original_waterfall=False)
    scrape = scraper.scrape_observation('https://network.satnogs.org/observations/5025420/')
    original_name = scrape['Downloads']['waterfall_hash_name']+"_original"
    yield Image.open(original_name).convert('L')
    shutil.rmtree(cnst.directories['data'])



@pytest.fixture()
def get_image():
    cnst.verify_directories()
    scraper = ObservationScraper(grey_scale=False, delete_original_waterfall=False)
    scrape = scraper.scrape_observation('https://network.satnogs.org/observations/5025420/')
    original_name = scrape['Downloads']['waterfall_hash_name']+"_original"
    yield original_name
    shutil.rmtree(cnst.directories['data'])


def test_find_left_bound(get_image_greyscale):
    assert 65 == iu.find_left_bound(get_image_greyscale)


def test_find_bottom_bound(get_image_greyscale):
    assert 1551 == iu.find_bottom_bound(get_image_greyscale)


def test_find_right_bound(get_image_greyscale):
    assert 688 == iu.find_right_bound(get_image_greyscale)


def test_find_upper_bound(get_image_greyscale):
    assert 9 == iu.find_upper_bound(get_image_greyscale)


def test_crop_and_save_delete(get_image):
    assert os.path.exists(get_image), "Verify the base image exists before function call"
    _, name = iu.crop_and_save_psd(get_image)
    assert not os.path.exists(get_image), "Verify the base image is removed after function call"
    assert os.path.exists(name), "Verify the numpy image exists"


def test_crop_and_save_resize(get_image):
    default_size = (623, 1542)
    size, _ = iu.crop_and_save_psd(get_image, delete_original=False)
    assert size[0] == default_size[1], "Verify default resize"
    assert size[1] == default_size[0], "Verify default resize"

    resize_dimen = (5, 10)
    size, _ = iu.crop_and_save_psd(get_image, delete_original=False, resize=True, resize_dimen=resize_dimen)
    assert size[0] == resize_dimen[1], "Verify custom resize"
    assert size[1] == resize_dimen[0], "Verify custom resize"

    original_dimen = (623, 1542)
    size, _ = iu.crop_and_save_psd(get_image, delete_original=False, resize=False)
    assert size[0] == original_dimen[1], "Verify no resize"
    assert size[1] == original_dimen[0], "Verify no resize"
