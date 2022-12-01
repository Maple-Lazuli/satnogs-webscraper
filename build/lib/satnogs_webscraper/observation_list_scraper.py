import os.path

from bs4 import BeautifulSoup as bs
import bs4
import html5lib
import json
from multiprocessing import Pool

import satnogs_webscraper.constants as cnst
import satnogs_webscraper.request_utils as ru


class ObservationListFetch:
    def __init__(self, url, save_name, save_dir, page_limit=0, resume=True, cpus=None):
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
        if len(urls) > 0:
            pool = Pool(self.cpus)
            pool.map(self.get_page_observation_ids, urls)

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

    def get_page_observation_ids(self, url):
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
        return observation_ids


if __name__ == "__main__":
    bad_signals = "https://network.satnogs.org/observations/?future=0&failed=0&norad=&observer=&station=&start=&end=&rated=rw0&transmitter_mode="
    fetch_bad = ObservationListFetch(url=bad_signals, save_name="bad.json", save_dir=cnst.directories["bad"],
                                     resume=False, page_limit=5)
    fetch_bad.fetch_ids()