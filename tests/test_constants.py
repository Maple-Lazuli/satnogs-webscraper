import os
import shutil
import satnogs_webscraper.constants as cnst


def test_verify_directories():
    if os.path.exists(cnst.directories['data']):
        shutil.rmtree(cnst.directories['data'])

    cnst.verify_directories()

    for key in cnst.directories.keys():
        assert os.path.exists(cnst.directories[key]), f"Verify {key}:{cnst.directories[key]} exists"

    if os.path.exists(cnst.directories['data']):
        shutil.rmtree(cnst.directories['data'])
