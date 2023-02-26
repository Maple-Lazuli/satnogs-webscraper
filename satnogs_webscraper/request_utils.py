import json
import os
import random
import requests
import time

import satnogs_webscraper.constants as cnst


def get_request(url):
    count = 1
    while True:
        res = requests.get(url)
        write_log(url, res.status_code)
        if res.status_code == 200:
            return res
        else:
            sleep_amount = count ** 2
            write_log(url,res.status_code, f"Timeout Count: {count}")
            time.sleep(sleep_amount)
        count += 1


def write_log(url, code, comment=""):
    log_name = f"{int(time.time())}-{''.join([str(random.randint(0, 9)) for _ in range(9)])}.json"
    with open(os.path.join(cnst.directories['logs'], log_name), "w") as log_out:
        json.dump({
            "time": str(time.time()),
            "url": url,
            "status": code,
            "comment": comment
        }, log_out)
