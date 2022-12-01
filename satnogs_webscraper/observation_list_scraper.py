import datetime
import os.path
import tempfile
import time

from bs4 import BeautifulSoup as bs
import bs4
import html5lib
import json
from multiprocessing import Pool

import satnogs_webscraper.constants as cnst
import satnogs_webscraper.request_utils as ru


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def setup_temp_file(items_total, items_done):
    temp = tempfile.NamedTemporaryFile()
    setup = {
        'start_time': int(time.time()),
        'items_total': items_total,
        'items_done': items_done
    }
    with open(temp.name, 'w') as file_out:
        json.dump(setup, file_out)

    return temp


def check_progress(temp_file, items_completed):
    current_time = int(time.time())

    with open(temp_file.name, 'r') as file_in:
        setup = json.load(file_in)

    num_completed_since_start = abs(items_completed - setup['items_done'])

    if num_completed_since_start != 0:
        time_per_item = (current_time - setup['start_time']) / num_completed_since_start
    else:
        time_per_item = 0

    seconds_left = time_per_item * (setup['items_total'] - items_completed)

    iteration = items_completed

    start_time = datetime.datetime.fromtimestamp(setup['start_time'])

    prefix = datetime.datetime.strftime(start_time, "%d/%m/%y %H:%M:%S")

    end_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds_left)

    suffix = datetime.datetime.strftime(end_time, "%d/%m/%y %H:%M:%S.")

    printProgressBar(iteration, setup['items_total'], prefix=prefix, suffix=suffix)


class ObservationListFetch:
    def __init__(self, url, save_name, save_dir, page_limit=0, resume=True, cpus=None):
        self.temp_file = None
        self.url = url
        self.observation_list = []
        self.url_list = []
        self.save_name = save_name
        self.save_dir = save_dir
        self.page_limit = page_limit if page_limit != 0 else None
        self.resume = resume
        self.cpus = cpus

    def get_pages(self, url):
        res = ru.get_request(url)
        observation_list_page = bs(res.content, "html5lib")
        largest_page = 0
        nav_list = observation_list_page.find_all("ul", class_="pagination")[0]
        for child in nav_list.children:
            if child.name == "li":
                for c in child.children:
                    if c.name == "a":
                        if len(c.contents) == 1:
                            if type(c.contents[0]) == bs4.element.NavigableString:
                                if c.contents[0].isdigit():
                                    largest_page = max(largest_page, int(c.contents[0]))

        if self.page_limit is not None:
            return [f'{url}&page={page}' for page in range(1, largest_page + 1)][: self.page_limit]
        else:
            return [f'{url}&page={page}' for page in range(1, largest_page + 1)]

    def multiprocess_id_fetch(self):
        urls = self.get_pages(self.url)

        total_urls = len(urls)
        items_done = 0
        if self.resume:
            pages_completed = os.listdir(self.save_dir)
            pages_completed = [page.split(".")[0] for page in pages_completed]
            pages_completed = set([int(page) for page in pages_completed if page.isdigit()])
            urls_pages = set([int(url.split("=")[-1]) for url in urls])
            pages_remaining = list(urls_pages.difference(pages_completed))
            urls_remaining = []
            for url in urls:
                page_number = int(url.split("=")[-1])
                if page_number in pages_remaining:
                    urls_remaining.append(url)
            urls = urls_remaining
            items_done = total_urls - len(urls)

        self.temp_file = setup_temp_file(items_total=total_urls, items_done=items_done)

        if len(urls) > 0:
            pool = Pool(self.cpus)
            pool.map(self.get_page_observation_ids, urls, self.temp_file)

    def fetch_ids(self):
        self.multiprocess_id_fetch()
        ids = []
        for file in os.listdir(self.save_dir):
            if file == self.save_name:
                continue
            if file.find(".json") == -1:
                continue
            with open(os.path.join(self.save_dir, file), "r") as file_in:
                ids.append(json.load(file_in)['IDs'])
        ids = [idx for group in ids for idx in group]
        with open(self.save_name, "w") as file_out:
            json.dump({"observation_ids": ids}, file_out)
        print(f"Wrote {self.save_name} to disk")
        return ids

    def get_page_observation_ids(self, url, temp_file):
        res = ru.get_request(url)
        observation_list_page = bs(res.content, "html5lib")
        observation_table = observation_list_page.find_all("tbody")[0]
        observation_ids = []
        for child in observation_table:
            if child.name == "tr":
                first_td = child.find_all("td")[0]
                first_a = first_td.find_all("a")[0]
                first_span = first_a.find_all("span")[0]
                span_contents = first_span.contents[0].strip()
                observation_ids.append(span_contents)

        file_name = f"{url.split('=')[-1]}.json"
        full_name = os.path.join(self.save_dir, file_name)
        with open(full_name, "w") as file_out:
            json.dump({"IDs": observation_ids}, file_out)

        # print the progress of the scrape
        lists_scraped = 0
        for path in os.listdir(self.save_dir):
            if os.path.isfile(os.path.join(self.save_dir, path)):
                if str(path).find('.json') != -1:
                    lists_scraped += 1

        check_progress(self.temp_file, lists_scraped)

        return observation_ids


if __name__ == "__main__":
    bad_signals = "https://network.satnogs.org/observations/?future=0&failed=0&norad=&observer=&station=&start=&end=&rated=rw0&transmitter_mode="
    fetch_bad = ObservationListFetch(url=bad_signals, save_name="bad.json", save_dir=cnst.directories["bad"],
                                     resume=False, page_limit=5)
    fetch_bad.fetch_ids()
