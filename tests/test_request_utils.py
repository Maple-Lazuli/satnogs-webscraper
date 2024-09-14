import json
import os.path
import shutil
import satnogs_webscraper.constants as cnst
import satnogs_webscraper.request_utils as ru
import pytest


@pytest.fixture()
def prep_directories():

    if os.path.exists(cnst.directories['data']):
        shutil.rmtree(cnst.directories['data'])
    cnst.verify_directories()
    yield None
    shutil.rmtree(cnst.directories['data'])


def test_write_log(prep_directories):
    assert len(os.listdir(cnst.directories['logs'])) == 0

    url = "test/url"
    code = 123
    comment = "This is a comment"
    log_file = ru.write_log(url=url, code=code, comment=comment)

    assert len(os.listdir(cnst.directories['logs'])) == 1

    with open(log_file) as file_in:
        parsed_logs = json.load(file_in)

    assert parsed_logs['url'] == url
    assert parsed_logs['status'] == code
    assert parsed_logs['comment'] == comment


def test_get_request_logging(prep_directories):
    url = 'https://www.google.com/'

    assert len(os.listdir(cnst.directories['logs'])) == 0

    res = ru.get_request(url)

    assert len(os.listdir(cnst.directories['logs'])) == 1

    log_file = os.listdir(cnst.directories['logs'])[0]
    log_file = os.path.join(cnst.directories['logs'], log_file)

    with open(log_file) as file_in:
        parsed_logs = json.load(file_in)

    assert parsed_logs['url'] == url
    assert parsed_logs['status'] == res.status_code


def test_get_request_exception_handling(prep_directories):
    url = 'https://127.0.0.1/'

    assert len(os.listdir(cnst.directories['logs'])) == 0

    res = ru.get_request(url, max_count=2)

    assert len(os.listdir(cnst.directories['logs'])) == 1

    log_file = os.listdir(cnst.directories['logs'])[0]
    log_file = os.path.join(cnst.directories['logs'], log_file)

    with open(log_file) as file_in:
        parsed_logs = json.load(file_in)

    assert parsed_logs['url'] == url
    assert parsed_logs['status'] == -1
    assert parsed_logs['comment'].find("Exception") != -1
