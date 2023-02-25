import os
import shutil
from PIL import Image

import satnogs_webscraper.image_utils as iu
import pytest


@pytest.fixture()
def get_image_greyscale():
    original_name = "./tests/resources/waterfall_7206380_2023-02-25T21-08-54.png"
    copy_name = "./tests/resources/base_copy.png"
    shutil.copy2(original_name, copy_name)
    yield Image.open(copy_name).convert('L')
    os.remove(copy_name)


@pytest.fixture()
def get_image():
    original_name = "./tests/resources/waterfall_7206380_2023-02-25T21-08-54.png"
    copy_name = "./tests/resources/base_copy.png"
    shutil.copy2(original_name, copy_name)
    yield copy_name
    if os.path.exists(copy_name):
        os.remove(copy_name)


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

