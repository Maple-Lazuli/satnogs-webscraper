from dataclasses import dataclass
from enum import Enum
import multiprocessing
import os

import satnogs_webscraper.constants as cnst
import satnogs_webscraper.observation_scraper as obs
import satnogs_webscraper.observation_list_scraper as ols
from satnogs_webscraper.observation_dataset import get_dataset


class Results(Enum):
    IGNORE = -1
    ON = 1
    OFF = 0


class Artifacts(Enum):
    IGNORE = -1
    NON_RATED = 0
    WITH_SIGNAL = 1
    WITHOUT_SIGNAL = 2


@dataclass
class Scraper:
    norad: str = ""  # Norad number for the ISS
    future: bool = False
    good: bool = True
    bad: bool = False
    unknown: bool = False
    failed: bool = False
    observer: str = ''
    station_id: str = ''  # The numeric designator for a station
    waterfall: object = -1  # Results Enum
    audio: object = -1  # Results Enum
    data: object = -1  # Results Enum
    start: str = ''
    end: str = ''
    artifacts: object = -1
    # Items related to managing the data and scraping
    list_page_limit: int = 1
    save_name: str = "scrape"
    cpus: int = 0
    grey_scale: bool = True

    def __post_init__(self):
        self.waterfall = Results(self.waterfall)
        self.audio = Results(self.audio)
        self.data = Results(self.data)
        self.artifacts = Artifacts(self.artifacts)

        if self.cpus == 0:
            self.cpus = multiprocessing.cpu_count()

    def generate_query_string(self):
        url = ['https://network.satnogs.org/observations/?']

        if not self.future:
            url.append('future=0')

        if not self.good:
            url.append('good=0')

        if not self.bad:
            url.append('bad=0')

        if not self.unknown:
            url.append('unknown=0')

        if not self.failed:
            url.append('failed=0')

        url.append(f'norad={self.norad}')
        url.append(f'observer={self.observer}')

        url.append(f'station={self.station_id}')

        if self.waterfall != Results.IGNORE:
            if self.waterfall == Results.ON:
                url.append('results=w1')
            elif self.waterfall == Results.OFF:
                url.append('results=w0')

        if self.audio != Results.IGNORE:
            if self.audio == Results.ON:
                url.append('results=a1')
            elif self.audio == Results.OFF:
                url.append('results=a0')

        if self.data != Results.IGNORE:
            if self.data == Results.ON:
                url.append('results=d1')
            elif self.data == Results.OFF:
                url.append('results=d0')

        url.append(f'start={self.start}')
        url.append(f'end={self.end}')
        url.append(f'transmitter_mode=')

        complete_url = "&".join(url)
        complete_url = complete_url.replace("/?&", "/?")
        return complete_url

    def scrape(self, resume=False):
        url = self.generate_query_string()
        json_name = f"{self.save_name}.json"
        cnst.verify_directories()
        obs_list_temp_dir = os.path.join(cnst.directories['observation_pages'], self.save_name)
        save_name = os.path.join(cnst.directories['data'], json_name)
        if os.path.isdir(obs_list_temp_dir):
            print(f"List Storage Dir: {obs_list_temp_dir}")
        else:
            os.makedirs(obs_list_temp_dir)
            print(f"List Storage Dir: {obs_list_temp_dir}")

        print("Scraping List Pages...")
        obs_list_scraper = ols.ObservationListFetch(url=url, save_name=save_name,
                                                    save_dir=obs_list_temp_dir,
                                                    resume=resume,
                                                    cpus=self.cpus,
                                                    page_limit=self.list_page_limit)
        ids = obs_list_scraper.fetch_ids()
        print("Scraping Observation Pages...")
        obs_scraper = obs.ObservationScraper(cpus=self.cpus, grey_scale=self.grey_scale)
        obs_scraper.multiprocess_scrape_observations(ids)
        return get_dataset(ids)


if __name__ == '__main__':
    scraper = Scraper()
    print(scraper.generate_query_string())
